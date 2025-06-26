import json
import logging
from datetime import datetime, timedelta

import environ
from django.apps import apps
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from redis.exceptions import ConnectionError, TimeoutError

from .models import PageViewLog, PageViewSummary
from .views import REDIS_KEY_PREFIX, redis_client

logger = logging.getLogger(__name__)

# Initialize environment variables
env = environ.Env()

# Try to import Celery - if not available, tasks will be regular functions
try:
    from celery import shared_task

    HAS_CELERY = True
except ImportError:
    # Fallback decorator for when Celery is not available
    def shared_task(func):
        return func

    HAS_CELERY = False


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    task_time_limit=env.int(
        "DJINSIGHT_PROCESS_TASK_TIME_LIMIT", 1800
    ),  # 30 minutes hard limit
    task_soft_time_limit=env.int(
        "DJINSIGHT_PROCESS_TASK_SOFT_TIME_LIMIT", 1500
    ),  # 25 minutes soft limit
)
def process_page_views_task(
    self,
    batch_size=env.int("DJINSIGHT_BATCH_SIZE", 1000),
    max_records=env.int("DJINSIGHT_MAX_RECORDS", 10000),
):
    """
    Celery task to process page views from Redis and store them in the database.

    Args:
        batch_size (int): Number of records to process in a single transaction
                         (uses DJINSIGHT_BATCH_SIZE env var, defaults to 1000)
        max_records (int): Maximum number of records to process in a single run
                          (uses DJINSIGHT_MAX_RECORDS env var, defaults to 10000)

    Environment Variables:
        DJINSIGHT_PROCESS_TASK_TIME_LIMIT (int): Hard timeout in seconds (default: 1800 = 30 min)
        DJINSIGHT_PROCESS_TASK_SOFT_TIME_LIMIT (int): Soft timeout in seconds (default: 1500 = 25 min)

    Returns:
        int: Number of records processed
    """
    try:
        return process_page_views(batch_size, max_records)
    except Exception as exc:
        logger.error(f"Error processing page views: {exc}")
        if HAS_CELERY:
            raise self.retry(exc=exc)
        else:
            raise


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    task_time_limit=env.int(
        "DJINSIGHT_SUMMARY_TASK_TIME_LIMIT", 900
    ),  # 15 minutes hard limit
    task_soft_time_limit=env.int(
        "DJINSIGHT_SUMMARY_TASK_SOFT_TIME_LIMIT", 720
    ),  # 12 minutes soft limit
)
def generate_daily_summaries_task(
    self, days_back=env.int("DJINSIGHT_SUMMARY_DAYS_BACK", 1)
):
    """
    Celery task to generate daily page view summaries.

    Args:
        days_back (int): Number of days back to process
                        (uses DJINSIGHT_SUMMARY_DAYS_BACK env var, defaults to 1)

    Environment Variables:
        DJINSIGHT_SUMMARY_TASK_TIME_LIMIT (int): Hard timeout in seconds (default: 900 = 15 min)
        DJINSIGHT_SUMMARY_TASK_SOFT_TIME_LIMIT (int): Soft timeout in seconds (default: 720 = 12 min)

    Returns:
        int: Number of summaries generated
    """
    try:
        return generate_daily_summaries(days_back)
    except Exception as exc:
        logger.error(f"Error generating daily summaries: {exc}")
        if HAS_CELERY:
            raise self.retry(exc=exc)
        else:
            raise


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    task_time_limit=env.int(
        "DJINSIGHT_CLEANUP_TASK_TIME_LIMIT", 3600
    ),  # 60 minutes hard limit
    task_soft_time_limit=env.int(
        "DJINSIGHT_CLEANUP_TASK_SOFT_TIME_LIMIT", 3300
    ),  # 55 minutes soft limit
)
def cleanup_old_data_task(
    self, days_to_keep=env.int("DJINSIGHT_CLEANUP_DAYS_TO_KEEP", 90)
):
    """
    Celery task to cleanup old page view logs.

    Args:
        days_to_keep (int): Number of days of logs to keep
                           (uses DJINSIGHT_CLEANUP_DAYS_TO_KEEP env var, defaults to 90)

    Environment Variables:
        DJINSIGHT_CLEANUP_TASK_TIME_LIMIT (int): Hard timeout in seconds (default: 3600 = 60 min)
        DJINSIGHT_CLEANUP_TASK_SOFT_TIME_LIMIT (int): Soft timeout in seconds (default: 3300 = 55 min)

    Returns:
        int: Number of records deleted
    """
    try:
        return cleanup_old_data(days_to_keep)
    except Exception as exc:
        logger.error(f"Error cleaning up old data: {exc}")
        if HAS_CELERY:
            raise self.retry(exc=exc)
        else:
            raise


def process_page_views(
    batch_size=env.int("DJINSIGHT_BATCH_SIZE", 1000),
    max_records=env.int("DJINSIGHT_MAX_RECORDS", 10000),
):
    """
    Process page views from Redis and store them in the database.

    Args:
        batch_size (int): Number of records to process in a single transaction
                         (uses DJINSIGHT_BATCH_SIZE env var, defaults to 1000)
        max_records (int): Maximum number of records to process in a single run
                          (uses DJINSIGHT_MAX_RECORDS env var, defaults to 10000)

    Returns:
        int: Number of records processed
    """
    if not redis_client:
        logger.error("Redis client not available")
        return 0

    logger.info("Starting to process page views from Redis")

    try:
        # Get all keys matching the page view pattern, excluding counters and sessions
        pattern = f"{REDIS_KEY_PREFIX}*"
        exclude_patterns = [
            f"{REDIS_KEY_PREFIX}counter:",
            f"{REDIS_KEY_PREFIX}unique_counter:",
            f"{REDIS_KEY_PREFIX}session:",
        ]

        # Get all keys
        all_keys = redis_client.keys(pattern)
        # Filter out counter and session keys
        keys = [
            key.decode("utf-8")
            for key in all_keys
            if not any(
                key.decode("utf-8").startswith(exclude) for exclude in exclude_patterns
            )
        ]

        # Limit the number of keys to process
        keys = keys[:max_records]

        if not keys:
            logger.info("No page views to process")
            return 0

        logger.info(f"Found {len(keys)} page views to process")

        # Process in batches
        processed_count = 0
        for i in range(0, len(keys), batch_size):
            batch_keys = keys[i : i + batch_size]
            batch_processed = process_batch(batch_keys)
            processed_count += batch_processed

            # Log progress
            if i % (batch_size * 10) == 0:
                logger.info(f"Processed {processed_count} / {len(keys)} page views")

        logger.info(f"Completed processing {processed_count} page views")
        return processed_count

    except (ConnectionError, TimeoutError) as e:
        logger.error(f"Redis connection error: {e}")
        raise
    except Exception as e:
        logger.error(f"Error processing page views: {e}")
        raise


def process_batch(keys):
    """
    Process a batch of page views.

    Args:
        keys (list): List of Redis keys to process

    Returns:
        int: Number of records processed in this batch
    """
    if not redis_client:
        return 0

    # Get all values in a single call using pipeline
    pipe = redis_client.pipeline()
    for key in keys:
        pipe.get(key)
    values = pipe.execute()

    # Create PageViewLog objects and collect statistics
    page_view_logs = []
    page_view_counters = {}  # {(page_id, content_type): (total, unique)}
    unique_sessions = set()  # Track unique sessions per page

    processed_count = 0

    for key, value in zip(keys, values):
        if value is None:
            continue

        try:
            data = json.loads(value.decode("utf-8"))

            # Extract data with validation
            page_id = data.get("page_id")
            content_type = data.get("content_type")
            url = data.get("url")
            session_key = data.get("session_key")
            ip_address = data.get("ip_address")
            user_agent = data.get("user_agent")
            referrer = data.get("referrer")
            timestamp_value = data.get("timestamp")
            is_unique = data.get("is_unique", False)

            # Skip if missing essential data
            if not all([page_id, content_type, url]):
                logger.warning(f"Skipping incomplete page view data in key {key}")
                continue

            # Convert timestamp
            if timestamp_value:
                if isinstance(timestamp_value, str):
                    timestamp = datetime.fromtimestamp(
                        int(timestamp_value), tz=timezone.get_current_timezone()
                    )
                else:
                    timestamp = datetime.fromtimestamp(
                        timestamp_value, tz=timezone.get_current_timezone()
                    )
            else:
                timestamp = timezone.now()

            # Create PageViewLog
            page_view_logs.append(
                PageViewLog(
                    page_id=page_id,
                    content_type=content_type,
                    url=url,
                    session_key=session_key,
                    ip_address=ip_address,
                    user_agent=user_agent[:1000] if user_agent else "",  # Limit length
                    referrer=referrer[:500] if referrer else "",  # Limit length
                    timestamp=timestamp,
                    is_unique=is_unique,
                )
            )

            # Update counters
            counter_key = (page_id, content_type)
            if counter_key not in page_view_counters:
                page_view_counters[counter_key] = (1, 1 if is_unique else 0)
            else:
                total, unique = page_view_counters[counter_key]
                page_view_counters[counter_key] = (
                    total + 1,
                    unique + (1 if is_unique else 0),
                )

            processed_count += 1

        except (json.JSONDecodeError, ValueError, TypeError) as e:
            logger.error(f"Error processing page view {key}: {e}")
            continue
        except Exception as e:
            logger.error(f"Unexpected error processing page view {key}: {e}")
            continue

    # Save to database in a transaction
    if page_view_logs or page_view_counters:
        with transaction.atomic():
            # Save PageViewLog objects
            if page_view_logs:
                PageViewLog.objects.bulk_create(page_view_logs, batch_size=500)

            # Update page statistics
            for (page_id, content_type), (total, unique) in page_view_counters.items():
                try:
                    # Get the model class from the content type
                    app_label, model = content_type.split(".")
                    model_class = apps.get_model(app_label, model)

                    # Update the page statistics using F expressions for thread safety
                    updated = model_class.objects.filter(id=page_id).update(
                        total_views=F("total_views") + total,
                        unique_views=F("unique_views") + unique,
                        last_viewed_at=timezone.now(),
                    )

                    # If page wasn't updated (doesn't exist), log warning
                    if updated == 0:
                        logger.warning(
                            f"Page {content_type} with id {page_id} not found for statistics update"
                        )

                except Exception as e:
                    logger.error(
                        f"Error updating page statistics for {content_type} {page_id}: {e}"
                    )

    # Delete processed keys from Redis
    if keys:
        try:
            redis_client.delete(*keys)
        except Exception as e:
            logger.error(f"Error deleting processed keys from Redis: {e}")

    return processed_count


def generate_daily_summaries(days_back=env.int("DJINSIGHT_SUMMARY_DAYS_BACK", 7)):
    """
    Generate daily page view summaries from detailed logs.

    Args:
        days_back (int): Number of days back to process
                        (uses DJINSIGHT_SUMMARY_DAYS_BACK env var, defaults to 7)

    Returns:
        int: Number of summaries generated
    """
    logger.info(f"Generating daily summaries for the last {days_back} days")

    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days_back)

    summaries_created = 0

    # Get all page IDs that have views in the time period
    page_views = (
        PageViewLog.objects.filter(
            timestamp__date__gte=start_date, timestamp__date__lte=end_date
        )
        .values("page_id", "content_type", "timestamp__date")
        .distinct()
    )

    for view_data in page_views:
        page_id = view_data["page_id"]
        content_type = view_data["content_type"]
        date = view_data["timestamp__date"]

        # Calculate statistics for this page on this date
        date_views = PageViewLog.objects.filter(page_id=page_id, timestamp__date=date)

        total_views = date_views.count()
        unique_views = date_views.values("session_key").distinct().count()

        # Create or update summary
        summary, created = PageViewSummary.objects.update_or_create(
            page_id=page_id,
            date=date,
            defaults={
                "content_type": content_type,
                "total_views": total_views,
                "unique_views": unique_views,
            },
        )

        if created:
            summaries_created += 1

    logger.info(f"Generated {summaries_created} daily summaries")
    return summaries_created


def cleanup_old_data(days_to_keep=env.int("DJINSIGHT_CLEANUP_DAYS_TO_KEEP", 90)):
    """
    Cleanup old page view logs older than specified days.

    Args:
        days_to_keep (int): Number of days of logs to keep
                           (uses DJINSIGHT_CLEANUP_DAYS_TO_KEEP env var, defaults to 90)

    Returns:
        int: Number of records deleted
    """
    cutoff_date = timezone.now() - timedelta(days=days_to_keep)

    logger.info(f"Cleaning up page view logs older than {cutoff_date}")

    # Delete old logs
    deleted_count, _ = PageViewLog.objects.filter(timestamp__lt=cutoff_date).delete()

    logger.info(f"Deleted {deleted_count} old page view logs")

    # Also cleanup old Redis session keys (this is optional)
    if redis_client:
        try:
            # Clean up session keys older than days_to_keep
            session_pattern = f"{REDIS_KEY_PREFIX}session:*"
            session_keys = redis_client.keys(session_pattern)

            # Check TTL and delete expired keys manually
            # (Redis should handle this automatically, but just in case)
            deleted_sessions = 0
            for key in session_keys:
                ttl = redis_client.ttl(key)
                if ttl == -1:  # Key exists but has no expiration
                    redis_client.delete(key)
                    deleted_sessions += 1

            if deleted_sessions > 0:
                logger.info(
                    f"Cleaned up {deleted_sessions} orphaned session keys from Redis"
                )

        except Exception as e:
            logger.error(f"Error cleaning up Redis session keys: {e}")

    return deleted_count


# Management command functions (for manual execution)
def run_process_page_views(verbosity=1, **options):
    """Function that can be called from management command"""
    batch_size = options.get("batch_size", env.int("DJINSIGHT_BATCH_SIZE", 1000))
    max_records = options.get("max_records", env.int("DJINSIGHT_MAX_RECORDS", 10000))

    if verbosity >= 1:
        print(
            f"Processing page views with batch_size={batch_size}, max_records={max_records}"
        )

    processed = process_page_views(batch_size, max_records)

    if verbosity >= 1:
        print(f"Processed {processed} page views")

    return processed


def run_generate_summaries(verbosity=1, **options):
    """Function that can be called from management command"""
    days_back = options.get("days_back", env.int("DJINSIGHT_SUMMARY_DAYS_BACK", 7))

    if verbosity >= 1:
        print(f"Generating daily summaries for the last {days_back} days")

    generated = generate_daily_summaries(days_back)

    if verbosity >= 1:
        print(f"Generated {generated} daily summaries")

    return generated


def run_cleanup_old_data(verbosity=1, **options):
    """Function that can be called from management command"""
    days_to_keep = options.get(
        "days_to_keep", env.int("DJINSIGHT_CLEANUP_DAYS_TO_KEEP", 90)
    )

    if verbosity >= 1:
        print(f"Cleaning up data older than {days_to_keep} days")

    deleted = cleanup_old_data(days_to_keep)

    if verbosity >= 1:
        print(f"Deleted {deleted} old records")

    return deleted
