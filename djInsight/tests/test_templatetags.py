from django.contrib.sessions.middleware import SessionMiddleware
from django.db import models
from django.template import Context, Template
from django.test import RequestFactory, TestCase

from djInsight.models import PageViewStatisticsMixin
from djInsight.templatetags.djInsight_tags import (
    _get_content_type_label,
    _get_object_url,
    _has_view_statistics,
    format_view_count,
    page_analytics_widget,
    page_stats_display,
    page_view_tracker,
)


# Test models for testing
class TestArticle(models.Model, PageViewStatisticsMixin):
    """Test model representing a blog article"""

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()

    def get_absolute_url(self):
        return f"/articles/{self.slug}/"

    def __str__(self):
        return self.title

    class Meta:
        app_label = "djInsight"


class TestProduct(models.Model, PageViewStatisticsMixin):
    """Test model representing a product"""

    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def get_tracking_url(self):
        return f"/products/{self.id}/"

    def get_display_name(self):
        return f"Product: {self.name}"

    class Meta:
        app_label = "djInsight"


class TestRegularModel(models.Model):
    """Test model without PageViewStatisticsMixin"""

    name = models.CharField(max_length=100)

    class Meta:
        app_label = "djInsight"


class TemplateTagsTest(TestCase):
    """Test djInsight template tags"""

    def setUp(self):
        self.factory = RequestFactory()
        self.article = TestArticle.objects.create(
            title="Test Article", slug="test-article", content="Test content"
        )
        self.product = TestProduct.objects.create(name="Test Product", price=29.99)
        self.regular_model = TestRegularModel.objects.create(name="Regular Model")

    def _get_request_context(self, obj=None, context_var="object"):
        """Helper to create request context"""
        request = self.factory.get("/")
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

        context = Context({"request": request})
        if obj:
            context[context_var] = obj
        return context

    def test_has_view_statistics_helper(self):
        """Test _has_view_statistics helper function"""
        self.assertTrue(_has_view_statistics(self.article))
        self.assertTrue(_has_view_statistics(self.product))
        self.assertFalse(_has_view_statistics(self.regular_model))
        self.assertFalse(_has_view_statistics(None))
        self.assertFalse(_has_view_statistics("not a model"))

    def test_get_object_url_helper(self):
        """Test _get_object_url helper function"""
        request = self.factory.get("/current-path/")

        # Test with get_absolute_url
        url = _get_object_url(self.article, request)
        self.assertEqual(url, "/articles/test-article/")

        # Test with custom get_tracking_url
        url = _get_object_url(self.product, request)
        self.assertEqual(url, f"/products/{self.product.id}/")

        # Test fallback to request path
        url = _get_object_url(self.regular_model, request)
        self.assertEqual(url, "/current-path/")

    def test_get_content_type_label_helper(self):
        """Test _get_content_type_label helper function"""
        label = _get_content_type_label(self.article)
        self.assertEqual(label, "djinsight.testarticle")

        label = _get_content_type_label(self.product)
        self.assertEqual(label, "djinsight.testproduct")

    def test_page_view_tracker_with_article(self):
        """Test page_view_tracker tag with article object"""
        context = self._get_request_context(self.article, "article")
        result = page_view_tracker(context)

        # Check that JavaScript is returned
        self.assertIn("<script>", result)
        self.assertIn("trackObjectView", result)
        self.assertIn("djInsight/record-view/", result)
        self.assertIn(str(self.article.id), result)
        self.assertIn("djinsight.testarticle", result)

    def test_page_view_tracker_with_explicit_obj(self):
        """Test page_view_tracker tag with explicitly passed object"""
        context = self._get_request_context()
        result = page_view_tracker(context, obj=self.product)

        self.assertIn("<script>", result)
        self.assertIn(str(self.product.id), result)
        self.assertIn("djinsight.testproduct", result)

    def test_page_view_tracker_auto_detection(self):
        """Test page_view_tracker auto-detection from context"""
        # Test with 'page' context variable
        context = self._get_request_context(self.article, "page")
        result = page_view_tracker(context)
        self.assertIn(str(self.article.id), result)

        # Test with 'object' context variable
        context = self._get_request_context(self.product, "object")
        result = page_view_tracker(context)
        self.assertIn(str(self.product.id), result)

    def test_page_view_tracker_no_valid_object(self):
        """Test page_view_tracker with no valid object"""
        context = self._get_request_context(self.regular_model)
        result = page_view_tracker(context)

        # Should return empty string
        self.assertEqual(result, "")

    def test_page_view_tracker_no_request(self):
        """Test page_view_tracker with no request in context"""
        context = Context({"object": self.article})
        result = page_view_tracker(context)

        # Should return empty string
        self.assertEqual(result, "")

    def test_page_view_tracker_options(self):
        """Test page_view_tracker with various options"""
        context = self._get_request_context(self.article)

        # Test with debug enabled
        result = page_view_tracker(context, obj=self.article, debug=True)
        self.assertIn("console.log", result)

        # Test with async_load disabled
        result = page_view_tracker(context, obj=self.article, async_load=False)
        self.assertNotIn("window.addEventListener('load'", result)

    def test_page_stats_display_with_article(self):
        """Test page_stats_display tag with article"""
        context = self._get_request_context(self.article)
        result = page_stats_display(context, obj=self.article)

        self.assertIn("djinsight-page-stats", result)
        self.assertIn("loadStats", result)
        self.assertIn(str(self.article.id), result)

    def test_page_stats_display_auto_detection(self):
        """Test page_stats_display auto-detection"""
        context = self._get_request_context(self.product, "product")
        # This should not find the product since 'product' is not in auto-detection list
        result = page_stats_display(context)
        self.assertEqual(result, "")

        # But 'object' should work
        context = self._get_request_context(self.product, "object")
        result = page_stats_display(context)
        self.assertIn(str(self.product.id), result)

    def test_page_stats_display_options(self):
        """Test page_stats_display with options"""
        context = self._get_request_context(self.article)

        # Test with unique views hidden
        result = page_stats_display(context, obj=self.article, show_unique=False)
        self.assertNotIn("djinsight-unique-views", result)

        # Test with refresh interval
        result = page_stats_display(context, obj=self.article, refresh_interval=30)
        self.assertIn("setInterval(loadStats, 30000)", result)

    def test_format_view_count_filter(self):
        """Test format_view_count filter"""
        # Test small numbers
        self.assertEqual(format_view_count(5), "5")
        self.assertEqual(format_view_count(999), "999")

        # Test thousands
        self.assertEqual(format_view_count(1000), "1.0K")
        self.assertEqual(format_view_count(1234), "1.2K")
        self.assertEqual(format_view_count(999999), "1000.0K")

        # Test millions
        self.assertEqual(format_view_count(1000000), "1.0M")
        self.assertEqual(format_view_count(1234567), "1.2M")

        # Test invalid input
        self.assertEqual(format_view_count("invalid"), "invalid")
        self.assertEqual(format_view_count(None), None)

    def test_page_analytics_widget_with_article(self):
        """Test page_analytics_widget with article"""
        context = self._get_request_context(self.article)
        result = page_analytics_widget(context, obj=self.article)

        self.assertIn("obj", result)
        self.assertEqual(result["obj"], self.article)
        self.assertTrue(result["has_stats"])
        self.assertEqual(result["display_name"], "Test Article")
        self.assertEqual(result["total_views"], 0)
        self.assertEqual(result["unique_views"], 0)

    def test_page_analytics_widget_with_product(self):
        """Test page_analytics_widget with product (custom display name)"""
        context = self._get_request_context(self.product)
        result = page_analytics_widget(context, obj=self.product, period="month")

        self.assertEqual(result["obj"], self.product)
        self.assertTrue(result["has_stats"])
        self.assertEqual(result["display_name"], "Product: Test Product")
        self.assertEqual(result["period"], "month")

    def test_page_analytics_widget_auto_detection(self):
        """Test page_analytics_widget auto-detection"""
        context = self._get_request_context(self.article, "article")
        result = page_analytics_widget(context)

        self.assertEqual(result["obj"], self.article)
        self.assertTrue(result["has_stats"])

    def test_page_analytics_widget_no_valid_object(self):
        """Test page_analytics_widget with no valid object"""
        context = self._get_request_context(self.regular_model)
        result = page_analytics_widget(context)

        self.assertIsNone(result["obj"])
        self.assertFalse(result["has_stats"])

    def test_page_analytics_widget_with_stats_data(self):
        """Test page_analytics_widget includes view statistics methods"""
        # Set some data on the article
        self.article.total_views = 100
        self.article.unique_views = 75
        self.article.save()

        context = self._get_request_context(self.article)
        result = page_analytics_widget(context, obj=self.article)

        self.assertEqual(result["total_views"], 100)
        self.assertEqual(result["unique_views"], 75)

        # Test that it includes period-specific data if methods exist
        self.assertIn("views_today", result)
        self.assertIn("views_this_week", result)
        self.assertIn("views_this_month", result)


class TemplateRenderingTest(TestCase):
    """Test template rendering with djInsight tags"""

    def setUp(self):
        self.factory = RequestFactory()
        self.article = TestArticle.objects.create(
            title="Test Article", slug="test-article", content="Test content"
        )

    def test_page_view_tracker_in_template(self):
        """Test page_view_tracker tag in template"""
        template = Template(
            "{% load djInsight_tags %}{% page_view_tracker obj=article %}"
        )

        request = self.factory.get("/")
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

        context = Context({"request": request, "article": self.article})
        result = template.render(context)

        self.assertIn("<script>", result)
        self.assertIn("trackObjectView", result)

    def test_page_stats_display_in_template(self):
        """Test page_stats_display tag in template"""
        template = Template(
            "{% load djInsight_tags %}{% page_stats_display obj=article %}"
        )

        request = self.factory.get("/")
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

        context = Context({"request": request, "article": self.article})
        result = template.render(context)

        self.assertIn("djinsight-page-stats", result)

    def test_format_view_count_in_template(self):
        """Test format_view_count filter in template"""
        template = Template("{% load djInsight_tags %}{{ count|format_view_count }}")

        context = Context({"count": 1234})
        result = template.render(context)

        self.assertEqual(result, "1.2K")

    def test_backward_compatibility_aliases(self):
        """Test backward compatibility aliases for Wagtail"""
        # Test wagtail_page_view_tracker
        template = Template(
            "{% load djInsight_tags %}{% wagtail_page_view_tracker page=article %}"
        )

        request = self.factory.get("/")
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

        context = Context({"request": request, "article": self.article})
        result = template.render(context)

        self.assertIn("<script>", result)
        self.assertIn("trackObjectView", result)
