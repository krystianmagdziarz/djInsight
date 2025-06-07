from django.contrib import admin

from .models import Article, Course, Product


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "author",
        "published_at",
        "total_views",
        "unique_views",
        "last_viewed_at",
    ]
    list_filter = ["author", "published_at"]
    search_fields = ["title", "content"]
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = [
        "total_views",
        "unique_views",
        "first_viewed_at",
        "last_viewed_at",
    ]

    fieldsets = (
        ("Content", {"fields": ("title", "slug", "author", "content")}),
        ("Dates", {"fields": ("published_at", "updated_at"), "classes": ("collapse",)}),
        (
            "djInsight Analytics",
            {
                "fields": (
                    "total_views",
                    "unique_views",
                    "first_viewed_at",
                    "last_viewed_at",
                ),
                "classes": ("collapse",),
                "description": "View statistics are automatically tracked by djInsight",
            },
        ),
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "category",
        "price",
        "total_views",
        "unique_views",
        "created_at",
    ]
    list_filter = ["category", "created_at"]
    search_fields = ["name", "description"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = [
        "total_views",
        "unique_views",
        "first_viewed_at",
        "last_viewed_at",
    ]

    fieldsets = (
        (
            "Product Info",
            {"fields": ("name", "slug", "category", "price", "description")},
        ),
        (
            "djInsight Analytics",
            {
                "fields": (
                    "total_views",
                    "unique_views",
                    "first_viewed_at",
                    "last_viewed_at",
                ),
                "classes": ("collapse",),
                "description": "View statistics are automatically tracked by djInsight",
            },
        ),
    )


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "instructor",
        "difficulty",
        "total_views",
        "unique_views",
        "created_at",
    ]
    list_filter = ["difficulty", "instructor", "created_at"]
    search_fields = ["title", "description", "instructor"]
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = [
        "total_views",
        "unique_views",
        "first_viewed_at",
        "last_viewed_at",
    ]

    fieldsets = (
        (
            "Course Info",
            {"fields": ("title", "slug", "instructor", "difficulty", "description")},
        ),
        (
            "djInsight Analytics",
            {
                "fields": (
                    "total_views",
                    "unique_views",
                    "first_viewed_at",
                    "last_viewed_at",
                ),
                "classes": ("collapse",),
                "description": "View statistics are automatically tracked by djInsight",
            },
        ),
    )
