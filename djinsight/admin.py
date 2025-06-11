from django.contrib import admin
from django.utils.html import format_html

from .models import PageViewLog, PageViewSummary


@admin.register(PageViewLog)
class PageViewLogAdmin(admin.ModelAdmin):
    list_display = [
        "page_id",
        "content_type",
        "timestamp",
        "is_unique",
        "session_key_short",
        "ip_address",
        "referrer_short",
    ]
    list_filter = [
        "content_type",
        "is_unique",
        "timestamp",
        ("timestamp", admin.DateFieldListFilter),
    ]
    search_fields = ["page_id", "url", "ip_address", "session_key"]
    readonly_fields = [
        "page_id",
        "content_type",
        "url",
        "session_key",
        "ip_address",
        "user_agent",
        "referrer",
        "timestamp",
        "is_unique",
    ]
    date_hierarchy = "timestamp"
    ordering = ["-timestamp"]

    def session_key_short(self, obj):
        if obj.session_key:
            return f"{obj.session_key[:8]}..."
        return "-"

    session_key_short.short_description = "Session"

    def referrer_short(self, obj):
        if obj.referrer:
            return f"{obj.referrer[:50]}..." if len(obj.referrer) > 50 else obj.referrer
        return "-"

    referrer_short.short_description = "Referrer"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(PageViewSummary)
class PageViewSummaryAdmin(admin.ModelAdmin):
    list_display = [
        "page_id",
        "content_type",
        "date",
        "total_views",
        "unique_views",
        "view_ratio",
    ]
    list_filter = ["content_type", "date", ("date", admin.DateFieldListFilter)]
    search_fields = ["page_id", "content_type"]
    readonly_fields = ["page_id", "content_type", "date", "total_views", "unique_views"]
    date_hierarchy = "date"
    ordering = ["-date", "-total_views"]

    def view_ratio(self, obj):
        if obj.total_views > 0:
            ratio = (obj.unique_views / obj.total_views) * 100
            color = "green" if ratio > 50 else "orange" if ratio > 25 else "red"
            return format_html('<span style="color: {};">{:.1f}%</span>', color, ratio)
        return "-"

    view_ratio.short_description = "Unique Ratio"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


# Custom admin views for statistics
class PageViewStatsAdmin(admin.ModelAdmin):
    """
    A custom admin view for displaying page view statistics.
    This doesn't correspond to a real model but provides a dashboard.
    """

    def changelist_view(self, request, extra_context=None):
        from datetime import timedelta

        from django.db.models import Sum
        from django.utils import timezone

        # Calculate some basic statistics
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        stats = {
            "total_views_today": PageViewLog.objects.filter(
                timestamp__date=today
            ).count(),
            "total_views_week": PageViewLog.objects.filter(
                timestamp__date__gte=week_ago
            ).count(),
            "total_views_month": PageViewLog.objects.filter(
                timestamp__date__gte=month_ago
            ).count(),
            "unique_sessions_today": PageViewLog.objects.filter(timestamp__date=today)
            .values("session_key")
            .distinct()
            .count(),
            "unique_sessions_week": PageViewLog.objects.filter(
                timestamp__date__gte=week_ago
            )
            .values("session_key")
            .distinct()
            .count(),
            "unique_sessions_month": PageViewLog.objects.filter(
                timestamp__date__gte=month_ago
            )
            .values("session_key")
            .distinct()
            .count(),
        }

        # Top pages by views
        top_pages = (
            PageViewSummary.objects.filter(date__gte=week_ago)
            .values("page_id", "content_type")
            .annotate(total=Sum("total_views"), unique=Sum("unique_views"))
            .order_by("-total")[:10]
        )

        extra_context = extra_context or {}
        extra_context.update(
            {
                "stats": stats,
                "top_pages": top_pages,
                "title": "Page View Statistics Dashboard",
            }
        )

        return super().changelist_view(request, extra_context)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# Register the stats dashboard
# admin.site.register(PageViewStatsAdmin)  # Uncomment if you want the dashboard
