from django.views.generic import DetailView, ListView

from .models import Article, Course, Product


class HomeView(ListView):
    """Homepage with popular content"""

    model = Article
    template_name = "blog/home.html"
    context_object_name = "articles"
    paginate_by = 5

    def get_queryset(self):
        return Article.objects.order_by("-total_views", "-published_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["popular_products"] = Product.objects.order_by("-total_views")[:3]
        context["popular_courses"] = Course.objects.order_by("-total_views")[:3]
        return context


class ArticleListView(ListView):
    model = Article
    template_name = "blog/article_list.html"
    context_object_name = "articles"
    paginate_by = 10

    def get_queryset(self):
        return Article.objects.order_by("-published_at")


class ArticleDetailView(DetailView):
    model = Article
    template_name = "blog/article_detail.html"
    context_object_name = "article"


class ProductListView(ListView):
    model = Product
    template_name = "blog/product_list.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        return Product.objects.order_by("-created_at")


class ProductDetailView(DetailView):
    model = Product
    template_name = "blog/product_detail.html"
    context_object_name = "product"


class CourseListView(ListView):
    model = Course
    template_name = "blog/course_list.html"
    context_object_name = "courses"
    paginate_by = 8

    def get_queryset(self):
        return Course.objects.order_by("-created_at")


class CourseDetailView(DetailView):
    model = Course
    template_name = "blog/course_detail.html"
    context_object_name = "course"


class PopularContentView(ListView):
    """Dashboard showing popular content across all models"""

    model = Article
    template_name = "blog/popular.html"
    context_object_name = "popular_articles"

    def get_queryset(self):
        return Article.objects.filter(total_views__gt=0).order_by("-total_views")[:10]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["popular_products"] = Product.objects.filter(
            total_views__gt=0
        ).order_by("-total_views")[:5]
        context["popular_courses"] = Course.objects.filter(total_views__gt=0).order_by(
            "-total_views"
        )[:5]
        return context
