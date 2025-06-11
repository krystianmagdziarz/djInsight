import json
import logging
import uuid

import redis
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from redis.exceptions import ConnectionError, TimeoutError

logger = logging.getLogger(__name__)


def check_stats_permission(user):
    """
    Check if user has permission to view statistics.

    If DJINSIGHT_ADMIN_ONLY is True, only staff users can view stats.
    Otherwise, any authenticated user can view stats.
    """
    admin_only = getattr(settings, "DJINSIGHT_ADMIN_ONLY", False)

    if admin_only:
        return user.is_authenticated and user.is_staff
    else:
        return True  # Allow all users when admin_only is False


# Initialize Redis connection with error handling
try:
    redis_client = redis.Redis(
        host=getattr(settings, "DJINSIGHT_REDIS_HOST", "localhost"),
        port=getattr(settings, "DJINSIGHT_REDIS_PORT", 6379),
        db=getattr(settings, "DJINSIGHT_REDIS_DB", 0),
        password=getattr(settings, "DJINSIGHT_REDIS_PASSWORD", None),
        socket_timeout=getattr(settings, "DJINSIGHT_REDIS_TIMEOUT", 5),
        socket_connect_timeout=getattr(settings, "DJINSIGHT_REDIS_CONNECT_TIMEOUT", 5),
        health_check_interval=30,
    )
    # Test the connection
    redis_client.ping()
    logger.info("Redis connection established successfully")
except (ConnectionError, TimeoutError) as e:
    logger.error(f"Redis connection failed: {e}")
    redis_client = None

# Redis key prefix for storing page views
REDIS_KEY_PREFIX = getattr(
    settings, "DJINSIGHT_REDIS_KEY_PREFIX", "djinsight:pageview:"
)


def get_client_ip(request):
    """Get the client IP address from request"""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR", "")
    return ip


def validate_page_data(data):
    """Validate the incoming page view data"""
    required_fields = ["page_id", "content_type", "url"]

    for field in required_fields:
        if not data.get(field):
            raise ValidationError(f"Field '{field}' is required")

    # Validate page_id is a positive integer
    try:
        page_id = int(data["page_id"])
        if page_id <= 0:
            raise ValidationError("page_id must be a positive integer")
    except (ValueError, TypeError):
        raise ValidationError("page_id must be a valid integer")

    # Validate content_type format
    content_type = data["content_type"]
    if "." not in content_type or content_type.count(".") != 1:
        raise ValidationError("content_type must be in format 'app.Model'")

    # Validate URL length
    url = data["url"]
    if len(url) > 500:
        raise ValidationError("URL is too long (max 500 characters)")

    return True


@csrf_exempt
@require_POST
@never_cache
def record_page_view(request):
    """
    Async endpoint to record a page view in Redis.

    Expected POST data:
    {
        "page_id": 123,
        "content_type": "myapp.MyPage",
        "url": "/some-page/",
        "referrer": "https://example.com/",
        "user_agent": "Mozilla/5.0 ..."
    }
    """
    if not redis_client:
        logger.error("Redis client not available")
        return JsonResponse(
            {"status": "error", "message": "Service temporarily unavailable"},
            status=503,
        )

    try:
        # Parse JSON data
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {"status": "error", "message": "Invalid JSON format"}, status=400
            )

        # Validate data
        try:
            validate_page_data(data)
        except ValidationError as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

        # Extract validated data
        page_id = int(data["page_id"])
        content_type = data["content_type"]
        url = data["url"]
        referrer = data.get("referrer", "")[:500]  # Limit referrer length
        user_agent = data.get("user_agent", "")[:1000]  # Limit user agent length

        # Get or create session key
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key or str(uuid.uuid4())

        # Get IP address
        ip_address = get_client_ip(request)

        # Create a unique view ID
        view_id = str(uuid.uuid4())

        # Get current timestamp
        timestamp = int(timezone.now().timestamp())

        # Check if this is a unique view for this session
        session_page_key = f"{REDIS_KEY_PREFIX}session:{session_key}:page:{page_id}"
        is_unique = not redis_client.exists(session_page_key)

        # Store the view data in Redis
        view_data = {
            "page_id": page_id,
            "content_type": content_type,
            "url": url,
            "session_key": session_key,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "referrer": referrer,
            "timestamp": timestamp,
            "is_unique": is_unique,
        }

        # Use pipeline for atomic operations
        pipe = redis_client.pipeline()

        # Store in Redis with expiration (default: 7 days)
        expiration = getattr(settings, "DJINSIGHT_REDIS_EXPIRATION", 60 * 60 * 24 * 7)

        # Store the view data
        pipe.setex(f"{REDIS_KEY_PREFIX}{view_id}", expiration, json.dumps(view_data))

        # Increment counters with content_type for better identification
        pipe.incr(f"{REDIS_KEY_PREFIX}counter:{content_type}:{page_id}")
        pipe.incr(f"{REDIS_KEY_PREFIX}counter:{page_id}")  # Keep backward compatibility

        # Mark session as having viewed this page
        if is_unique:
            pipe.setex(session_page_key, expiration, 1)
            pipe.incr(f"{REDIS_KEY_PREFIX}unique_counter:{content_type}:{page_id}")
            pipe.incr(
                f"{REDIS_KEY_PREFIX}unique_counter:{page_id}"
            )  # Keep backward compatibility

        # Execute pipeline
        pipe.execute()

        logger.info(
            f"Page view recorded: page_id={page_id}, view_id={view_id}, unique={is_unique}"
        )

        return JsonResponse(
            {"status": "success", "view_id": view_id, "is_unique": is_unique}
        )

    except (ConnectionError, TimeoutError) as e:
        logger.error(f"Redis error while recording page view: {e}")
        return JsonResponse(
            {"status": "error", "message": "Service temporarily unavailable"},
            status=503,
        )

    except Exception as e:
        logger.error(f"Unexpected error in record_page_view: {e}")
        return JsonResponse(
            {"status": "error", "message": "Internal server error"}, status=500
        )


@user_passes_test(check_stats_permission, login_url=None)
@csrf_exempt
@require_POST
@never_cache
def get_page_stats(request):
    """
    Get basic statistics for a page from Redis counters.

    Expected POST data:
    {
        "page_id": 123,
        "content_type": "blog.article"  # Optional, for more specific stats
    }
    """
    if not redis_client:
        return JsonResponse(
            {"status": "error", "message": "Service temporarily unavailable"},
            status=503,
        )

    try:
        data = json.loads(request.body)
        page_id = data.get("page_id")
        content_type = data.get("content_type")  # Optional

        if not page_id:
            return JsonResponse(
                {"status": "error", "message": "page_id is required"}, status=400
            )

        try:
            page_id = int(page_id)
        except (ValueError, TypeError):
            return JsonResponse(
                {"status": "error", "message": "page_id must be a valid integer"},
                status=400,
            )

        # Get counters from Redis
        if content_type:
            # Use specific content_type keys if provided
            total_views = redis_client.get(
                f"{REDIS_KEY_PREFIX}counter:{content_type}:{page_id}"
            )
            unique_views = redis_client.get(
                f"{REDIS_KEY_PREFIX}unique_counter:{content_type}:{page_id}"
            )

            # Fallback to legacy keys and add them together for total count
            if not total_views:
                total_views = redis_client.get(f"{REDIS_KEY_PREFIX}counter:{page_id}")

            # For unique views, check both new and old keys and take maximum
            # (since unique visits might be split between old and new format)
            legacy_unique_views = redis_client.get(
                f"{REDIS_KEY_PREFIX}unique_counter:{page_id}"
            )

            unique_views_new = int(unique_views) if unique_views else 0
            unique_views_legacy = int(legacy_unique_views) if legacy_unique_views else 0
            unique_views = max(unique_views_new, unique_views_legacy)

        else:
            # Fallback to generic keys for backward compatibility
            total_views = redis_client.get(f"{REDIS_KEY_PREFIX}counter:{page_id}")
            unique_views = redis_client.get(
                f"{REDIS_KEY_PREFIX}unique_counter:{page_id}"
            )
            unique_views = int(unique_views) if unique_views else 0

        # Convert total_views to integer
        total_views = int(total_views) if total_views else 0

        return JsonResponse(
            {
                "status": "success",
                "page_id": page_id,
                "content_type": content_type,
                "total_views": total_views,
                "unique_views": unique_views,
            }
        )

    except json.JSONDecodeError:
        return JsonResponse(
            {"status": "error", "message": "Invalid JSON format"}, status=400
        )

    except Exception as e:
        logger.error(f"Error getting page stats: {e}")
        return JsonResponse(
            {"status": "error", "message": "Internal server error"}, status=500
        )
