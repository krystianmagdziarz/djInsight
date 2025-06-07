from django.urls import path

from . import views

urlpatterns = [
    # Home
    path("", views.HomeView.as_view(), name="home"),
    path("popular/", views.PopularContentView.as_view(), name="popular"),
    # Articles
    path("articles/", views.ArticleListView.as_view(), name="article_list"),
    path(
        "articles/<slug:slug>/",
        views.ArticleDetailView.as_view(),
        name="article_detail",
    ),
    # Products
    path("products/", views.ProductListView.as_view(), name="product_list"),
    path(
        "products/<slug:slug>/",
        views.ProductDetailView.as_view(),
        name="product_detail",
    ),
    # Courses
    path("courses/", views.CourseListView.as_view(), name="course_list"),
    path(
        "courses/<slug:slug>/", views.CourseDetailView.as_view(), name="course_detail"
    ),
]
