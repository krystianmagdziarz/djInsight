import json
import logging
import uuid

from django import template
from django.conf import settings
from django.template.loader import render_to_string
from django.urls import NoReverseMatch, reverse
from django.utils.safestring import mark_safe

logger = logging.getLogger(__name__)
register = template.Library()


def _has_view_statistics(obj):
    """Check if object has view statistics fields"""
    if not obj:
        return False
    required_fields = [
        "total_views",
        "unique_views",
        "last_viewed_at",
        "first_viewed_at",
    ]
    return all(hasattr(obj, field) for field in required_fields)


def _get_object_url(obj, request):
    """Get URL for tracking the object"""
    if hasattr(obj, "get_tracking_url"):
        return obj.get_tracking_url()
    elif hasattr(obj, "get_absolute_url"):
        return obj.get_absolute_url()
    elif hasattr(obj, "url"):
        return obj.url
    else:
        # Fallback to current request path
        return request.path if request else "/"


def _get_content_type_label(obj):
    """Get content type label for the object"""
    if hasattr(obj, "get_content_type_label"):
        return obj.get_content_type_label()
    else:
        return obj._meta.label_lower


def _get_object_from_context(context, obj=None):
    """Get object from context with auto-detection"""
    if obj and _has_view_statistics(obj):
        return obj

    if obj is None:
        # Try common context variable names
        for var_name in ["page", "object", "article", "post", "item"]:
            potential_obj = context.get(var_name)
            if potential_obj and _has_view_statistics(potential_obj):
                return potential_obj

    return None


def _check_stats_permission(request):
    """
    Check if current user has permission to view statistics.

    If DJINSIGHT_ADMIN_ONLY is True, only staff users can view stats.
    Otherwise, all users can view stats.
    """
    admin_only = getattr(settings, "DJINSIGHT_ADMIN_ONLY", False)

    if admin_only and request:
        user = getattr(request, "user", None)
        if user:
            return user.is_authenticated and user.is_staff
        return False

    return True  # Allow all users when admin_only is False or no request


@register.simple_tag(takes_context=True)
def page_view_tracker(context, obj=None, async_load=True, debug=False):
    """
    Template tag to add JavaScript code for tracking object views.

    Usage:
    {% page_view_tracker %}
    {% page_view_tracker obj=article async_load=False debug=True %}
    """
    request = context.get("request")
    if not request:
        if debug:
            logger.warning("No request found in template context")
        return ""

    obj = _get_object_from_context(context, obj)
    if not obj:
        if debug:
            logger.warning("No valid object with view statistics found for tracking")
        return ""

    # Get the URL for the record_page_view endpoint
    try:
        record_url = reverse("djinsight:record_page_view")
    except NoReverseMatch:
        record_url = "/djinsight/record-view/"
        if debug:
            logger.warning(f"Could not reverse URL, using hardcoded path: {record_url}")

    # Check if tracking is enabled
    enable_tracking = getattr(settings, "DJINSIGHT_ENABLE_TRACKING", True)
    if not enable_tracking:
        if debug:
            return "<!-- djinsight tracking disabled by settings -->"
        return ""

    # Prepare template context
    template_context = {
        "object_data": json.dumps(
            {
                "page_id": obj.id,
                "content_type": _get_content_type_label(obj),
                "url": _get_object_url(obj, request),
            }
        ),
        "record_url": record_url,
        "async_load": async_load,
        "debug": debug,
    }

    return mark_safe(
        render_to_string("djinsight/tracking_script.html", template_context)
    )


@register.simple_tag(takes_context=True)
def page_stats_display(context, obj=None, show_unique=True, refresh_interval=None):
    """
    Template tag to display live object view statistics.

    Usage:
    {% page_stats_display %}
    {% page_stats_display obj=article show_unique=False refresh_interval=30 %}
    """
    # Check permissions first
    request = context.get("request")
    if not _check_stats_permission(request):
        return ""

    obj = _get_object_from_context(context, obj)
    if not obj:
        return ""

    # Get the URL for the stats endpoint
    try:
        stats_url = reverse("djinsight:get_page_stats")
    except NoReverseMatch:
        stats_url = "/djinsight/page-stats/"

    # Generate unique ID for this stats display
    stats_id = f"djinsight-stats-{uuid.uuid4().hex[:8]}"

    # Convert refresh interval to milliseconds
    refresh_interval_ms = None
    if refresh_interval:
        try:
            refresh_interval_ms = int(refresh_interval) * 1000
        except (ValueError, TypeError):
            pass

    template_context = {
        "stats_id": stats_id,
        "object_id": obj.id,
        "content_type": _get_content_type_label(obj),
        "stats_url": stats_url,
        "show_unique": show_unique,
        "refresh_interval": refresh_interval_ms,
    }

    return mark_safe(render_to_string("djinsight/stats_display.html", template_context))


@register.filter
def format_view_count(count):
    """
    Format view count for display (e.g., 1234 -> 1.2K)

    Usage:
    {{ object.total_views|format_view_count }}
    """
    try:
        count = int(count)
    except (ValueError, TypeError):
        return count

    if count < 1000:
        return str(count)
    elif count < 1000000:
        return f"{count / 1000:.1f}K"
    else:
        return f"{count / 1000000:.1f}M"


# Individual statistics components
@register.inclusion_tag("djinsight/stats/total_views.html", takes_context=True)
def total_views_stat(context, obj=None):
    """Display total views statistic"""
    # Check permissions first
    request = context.get("request")
    if not _check_stats_permission(request):
        return {"total_views": 0, "obj": None, "no_permission": True}

    obj = _get_object_from_context(context, obj)
    return {
        "total_views": getattr(obj, "total_views", 0) if obj else 0,
        "obj": obj,
    }


@register.inclusion_tag("djinsight/stats/unique_views.html", takes_context=True)
def unique_views_stat(context, obj=None):
    """Display unique views statistic"""
    # Check permissions first
    request = context.get("request")
    if not _check_stats_permission(request):
        return {"unique_views": 0, "obj": None, "no_permission": True}

    obj = _get_object_from_context(context, obj)
    return {
        "unique_views": getattr(obj, "unique_views", 0) if obj else 0,
        "obj": obj,
    }


@register.inclusion_tag("djinsight/stats/last_viewed.html", takes_context=True)
def last_viewed_stat(context, obj=None):
    """Display last viewed statistic"""
    # Check permissions first
    request = context.get("request")
    if not _check_stats_permission(request):
        return {"last_viewed_at": None, "obj": None, "no_permission": True}

    obj = _get_object_from_context(context, obj)
    return {
        "last_viewed_at": getattr(obj, "last_viewed_at", None) if obj else None,
        "obj": obj,
    }


@register.inclusion_tag("djinsight/stats/first_viewed.html", takes_context=True)
def first_viewed_stat(context, obj=None):
    """Display first viewed statistic"""
    # Check permissions first
    request = context.get("request")
    if not _check_stats_permission(request):
        return {"first_viewed_at": None, "obj": None, "no_permission": True}

    obj = _get_object_from_context(context, obj)
    return {
        "first_viewed_at": getattr(obj, "first_viewed_at", None) if obj else None,
        "obj": obj,
    }


@register.inclusion_tag("djinsight/stats/views_today.html", takes_context=True)
def views_today_stat(context, obj=None):
    """Display views today statistic"""
    # Check permissions first
    request = context.get("request")
    if not _check_stats_permission(request):
        return {"views_today": 0, "obj": None, "no_permission": True}

    obj = _get_object_from_context(context, obj)
    views_today = 0
    if obj and hasattr(obj, "get_views_today"):
        try:
            views_today = obj.get_views_today()
        except:
            views_today = 0

    return {
        "views_today": views_today,
        "obj": obj,
    }


@register.inclusion_tag("djinsight/stats/views_week.html", takes_context=True)
def views_week_stat(context, obj=None):
    """Display views this week statistic"""
    # Check permissions first
    request = context.get("request")
    if not _check_stats_permission(request):
        return {"views_this_week": 0, "obj": None, "no_permission": True}

    obj = _get_object_from_context(context, obj)
    views_this_week = 0
    if obj and hasattr(obj, "get_views_this_week"):
        try:
            views_this_week = obj.get_views_this_week()
        except:
            views_this_week = 0

    return {
        "views_this_week": views_this_week,
        "obj": obj,
    }


@register.inclusion_tag("djinsight/stats/views_month.html", takes_context=True)
def views_month_stat(context, obj=None):
    """Display views this month statistic"""
    # Check permissions first
    request = context.get("request")
    if not _check_stats_permission(request):
        return {"views_this_month": 0, "obj": None, "no_permission": True}

    obj = _get_object_from_context(context, obj)
    views_this_month = 0
    if obj and hasattr(obj, "get_views_this_month"):
        try:
            views_this_month = obj.get_views_this_month()
        except:
            views_this_month = 0

    return {
        "views_this_month": views_this_month,
        "obj": obj,
    }


@register.inclusion_tag("djinsight/stats/live_counter.html", takes_context=True)
def live_stats_counter(context, obj=None, show_unique=True, refresh_interval=30):
    """Display live statistics counter with auto-refresh"""
    # Check permissions first
    request = context.get("request")
    if not _check_stats_permission(request):
        return {"obj": None, "no_permission": True}

    obj = _get_object_from_context(context, obj)
    return {
        "obj": obj,
        "content_type": _get_content_type_label(obj) if obj else "",
        "show_unique": show_unique,
        "refresh_interval": refresh_interval,
    }


# Composite components
@register.inclusion_tag("djinsight/page_analytics.html", takes_context=True)
def page_analytics_widget(context, obj=None, period="week"):
    """
    Include template tag for displaying a complete analytics widget.

    Usage:
    {% page_analytics_widget %}
    {% page_analytics_widget obj=article period='month' %}
    """
    # Check permissions first
    request = context.get("request")
    if not _check_stats_permission(request):
        return {"obj": None, "has_stats": False, "no_permission": True}

    obj = _get_object_from_context(context, obj)

    if not obj:
        return {"obj": None, "has_stats": False}

    # Get analytics data based on period
    analytics_data = {
        "obj": obj,
        "has_stats": True,
        "period": period,
        "total_views": getattr(obj, "total_views", 0),
        "unique_views": getattr(obj, "unique_views", 0),
        "last_viewed_at": getattr(obj, "last_viewed_at", None),
        "first_viewed_at": getattr(obj, "first_viewed_at", None),
        "display_name": obj.get_display_name()
        if hasattr(obj, "get_display_name")
        else str(obj),
    }

    # Add period-specific data if methods exist
    if hasattr(obj, "get_views_today"):
        try:
            analytics_data["views_today"] = obj.get_views_today()
        except:
            analytics_data["views_today"] = 0

    if hasattr(obj, "get_views_this_week"):
        try:
            analytics_data["views_this_week"] = obj.get_views_this_week()
        except:
            analytics_data["views_this_week"] = 0

    if hasattr(obj, "get_views_this_month"):
        try:
            analytics_data["views_this_month"] = obj.get_views_this_month()
        except:
            analytics_data["views_this_month"] = 0

    return analytics_data


# Backward compatibility aliases for Wagtail users
@register.simple_tag(takes_context=True)
def wagtail_page_view_tracker(context, page=None, async_load=True, debug=False):
    """Backward compatibility alias for Wagtail pages"""
    return page_view_tracker(context, obj=page, async_load=async_load, debug=debug)


@register.simple_tag(takes_context=True)
def wagtail_page_stats_display(
    context, page=None, show_unique=True, refresh_interval=None
):
    """Backward compatibility alias for Wagtail pages"""
    return page_stats_display(
        context, obj=page, show_unique=show_unique, refresh_interval=refresh_interval
    )


@register.inclusion_tag("djinsight/page_analytics.html", takes_context=True)
def wagtail_page_analytics_widget(context, page=None, period="week"):
    """Backward compatibility alias for Wagtail pages"""
    return page_analytics_widget(context, obj=page, period=period)
