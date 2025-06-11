from django.db import models
from django.test import TestCase
from django.utils import timezone

from djinsight.models import (
    PageViewLog,
    PageViewStatisticsMixin,
    PageViewSummary,
    has_view_statistics,
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
        app_label = "djinsight"


class TestProduct(models.Model, PageViewStatisticsMixin):
    """Test model representing a product"""

    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def get_tracking_url(self):
        return f"/products/{self.id}/"

    def get_display_name(self):
        return f"Product: {self.name}"

    class Meta:
        app_label = "djinsight"


class TestCustomModel(models.Model, PageViewStatisticsMixin):
    """Test model without get_absolute_url"""

    name = models.CharField(max_length=100)

    class Meta:
        app_label = "djinsight"


# Regular model without mixin
class TestRegularModel(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        app_label = "djinsight"


class PageViewStatisticsMixinTest(TestCase):
    """Test the PageViewStatisticsMixin functionality"""

    def setUp(self):
        self.article = TestArticle.objects.create(
            title="Test Article", slug="test-article", content="Test content"
        )
        self.product = TestProduct.objects.create(name="Test Product", price=29.99)
        self.custom_model = TestCustomModel.objects.create(name="Test Custom")
        self.regular_model = TestRegularModel.objects.create(name="Regular Model")

    def test_mixin_fields_exist(self):
        """Test that mixin adds required fields"""
        self.assertTrue(hasattr(self.article, "total_views"))
        self.assertTrue(hasattr(self.article, "unique_views"))
        self.assertTrue(hasattr(self.article, "last_viewed_at"))
        self.assertTrue(hasattr(self.article, "first_viewed_at"))

    def test_initial_values(self):
        """Test initial field values"""
        self.assertEqual(self.article.total_views, 0)
        self.assertEqual(self.article.unique_views, 0)
        self.assertIsNone(self.article.last_viewed_at)
        self.assertIsNone(self.article.first_viewed_at)

    def test_increment_view_count(self):
        """Test incrementing view count"""
        original_time = timezone.now()

        # First view (unique)
        self.article.increment_view_count(unique=True)
        self.assertEqual(self.article.total_views, 1)
        self.assertEqual(self.article.unique_views, 1)
        self.assertIsNotNone(self.article.first_viewed_at)
        self.assertIsNotNone(self.article.last_viewed_at)

        first_viewed = self.article.first_viewed_at

        # Second view (not unique)
        self.article.increment_view_count(unique=False)
        self.assertEqual(self.article.total_views, 2)
        self.assertEqual(self.article.unique_views, 1)
        self.assertEqual(self.article.first_viewed_at, first_viewed)
        self.assertGreater(self.article.last_viewed_at, first_viewed)

    def test_get_content_type_label(self):
        """Test getting content type label"""
        self.assertEqual(self.article.get_content_type_label(), "djinsight.testarticle")
        self.assertEqual(self.product.get_content_type_label(), "djinsight.testproduct")

    def test_get_tracking_url_article(self):
        """Test getting tracking URL for article with get_absolute_url"""
        expected_url = "/articles/test-article/"
        self.assertEqual(self.article.get_tracking_url(), expected_url)

    def test_get_tracking_url_product(self):
        """Test getting tracking URL for product with custom get_tracking_url"""
        expected_url = f"/products/{self.product.id}/"
        self.assertEqual(self.product.get_tracking_url(), expected_url)

    def test_get_tracking_url_fallback(self):
        """Test fallback tracking URL for model without specific URL method"""
        expected_url = f"/testcustommodel/{self.custom_model.id}/"
        self.assertEqual(self.custom_model.get_tracking_url(), expected_url)

    def test_get_display_name_article(self):
        """Test display name for article (has title)"""
        self.assertEqual(self.article.get_display_name(), "Test Article")

    def test_get_display_name_product(self):
        """Test custom display name for product"""
        self.assertEqual(self.product.get_display_name(), "Product: Test Product")

    def test_get_display_name_custom(self):
        """Test display name for custom model (has name)"""
        self.assertEqual(self.custom_model.get_display_name(), "Test Custom")

    def test_get_views_today(self):
        """Test getting today's view count"""
        # Create some test logs
        today = timezone.now().date()
        yesterday = today - timezone.timedelta(days=1)

        PageViewLog.objects.create(
            page_id=self.article.id,
            content_type=self.article.get_content_type_label(),
            url=self.article.get_tracking_url(),
            timestamp=timezone.now(),
        )
        PageViewLog.objects.create(
            page_id=self.article.id,
            content_type=self.article.get_content_type_label(),
            url=self.article.get_tracking_url(),
            timestamp=timezone.datetime.combine(
                yesterday, timezone.datetime.min.time()
            ).replace(tzinfo=timezone.get_current_timezone()),
        )

        # Should only count today's views
        self.assertEqual(self.article.get_views_today(), 1)

    def test_get_views_this_week(self):
        """Test getting this week's view count"""
        # Create test logs for different time periods
        now = timezone.now()
        week_ago = now - timezone.timedelta(days=8)

        PageViewLog.objects.create(
            page_id=self.article.id,
            content_type=self.article.get_content_type_label(),
            url=self.article.get_tracking_url(),
            timestamp=now,
        )
        PageViewLog.objects.create(
            page_id=self.article.id,
            content_type=self.article.get_content_type_label(),
            url=self.article.get_tracking_url(),
            timestamp=week_ago,
        )

        # Should only count this week's views
        self.assertEqual(self.article.get_views_this_week(), 1)

    def test_get_views_this_month(self):
        """Test getting this month's view count"""
        # Create test logs
        now = timezone.now()
        last_month = now.replace(month=now.month - 1 if now.month > 1 else 12)

        PageViewLog.objects.create(
            page_id=self.article.id,
            content_type=self.article.get_content_type_label(),
            url=self.article.get_tracking_url(),
            timestamp=now,
        )
        PageViewLog.objects.create(
            page_id=self.article.id,
            content_type=self.article.get_content_type_label(),
            url=self.article.get_tracking_url(),
            timestamp=last_month,
        )

        # Should only count this month's views
        self.assertEqual(self.article.get_views_this_month(), 1)


class PageViewLogTest(TestCase):
    """Test PageViewLog model"""

    def setUp(self):
        self.article = TestArticle.objects.create(
            title="Test Article", slug="test-article", content="Test content"
        )

    def test_create_log(self):
        """Test creating a page view log"""
        log = PageViewLog.objects.create(
            page_id=self.article.id,
            content_type=self.article.get_content_type_label(),
            url=self.article.get_tracking_url(),
            session_key="test-session",
            ip_address="127.0.0.1",
            user_agent="Test Agent",
            referrer="https://example.com",
            is_unique=True,
        )

        self.assertEqual(log.page_id, self.article.id)
        self.assertEqual(log.content_type, "djinsight.testarticle")
        self.assertEqual(log.url, "/articles/test-article/")
        self.assertEqual(log.session_key, "test-session")
        self.assertEqual(log.ip_address, "127.0.0.1")
        self.assertEqual(log.user_agent, "Test Agent")
        self.assertEqual(log.referrer, "https://example.com")
        self.assertTrue(log.is_unique)

    def test_log_str(self):
        """Test string representation of log"""
        log = PageViewLog.objects.create(
            page_id=self.article.id,
            content_type=self.article.get_content_type_label(),
            url=self.article.get_tracking_url(),
        )

        expected_str = (
            f"View of djinsight.testarticle {self.article.id} at {log.timestamp}"
        )
        self.assertEqual(str(log), expected_str)


class PageViewSummaryTest(TestCase):
    """Test PageViewSummary model"""

    def setUp(self):
        self.article = TestArticle.objects.create(
            title="Test Article", slug="test-article", content="Test content"
        )

    def test_create_summary(self):
        """Test creating a page view summary"""
        today = timezone.now().date()

        summary = PageViewSummary.objects.create(
            page_id=self.article.id,
            content_type=self.article.get_content_type_label(),
            date=today,
            total_views=100,
            unique_views=75,
        )

        self.assertEqual(summary.page_id, self.article.id)
        self.assertEqual(summary.content_type, "djinsight.testarticle")
        self.assertEqual(summary.date, today)
        self.assertEqual(summary.total_views, 100)
        self.assertEqual(summary.unique_views, 75)

    def test_summary_str(self):
        """Test string representation of summary"""
        today = timezone.now().date()

        summary = PageViewSummary.objects.create(
            page_id=self.article.id,
            content_type=self.article.get_content_type_label(),
            date=today,
            total_views=100,
            unique_views=75,
        )

        expected_str = f"djinsight.testarticle {self.article.id} - {today}: 100 views"
        self.assertEqual(str(summary), expected_str)

    def test_unique_together_constraint(self):
        """Test that page_id and date must be unique together"""
        from django.db import IntegrityError

        today = timezone.now().date()

        # Create first summary
        PageViewSummary.objects.create(
            page_id=self.article.id,
            content_type=self.article.get_content_type_label(),
            date=today,
            total_views=100,
            unique_views=75,
        )

        # Try to create duplicate - should raise error
        with self.assertRaises(IntegrityError):
            PageViewSummary.objects.create(
                page_id=self.article.id,
                content_type=self.article.get_content_type_label(),
                date=today,
                total_views=50,
                unique_views=25,
            )


class HasViewStatisticsTest(TestCase):
    """Test the has_view_statistics helper function"""

    def setUp(self):
        self.article = TestArticle.objects.create(
            title="Test Article", slug="test-article", content="Test content"
        )
        self.regular_model = TestRegularModel.objects.create(name="Regular Model")

    def test_has_view_statistics_with_mixin(self):
        """Test has_view_statistics returns True for objects with mixin"""
        self.assertTrue(has_view_statistics(self.article))

    def test_has_view_statistics_without_mixin(self):
        """Test has_view_statistics returns False for objects without mixin"""
        self.assertFalse(has_view_statistics(self.regular_model))

    def test_has_view_statistics_with_none(self):
        """Test has_view_statistics returns False for None"""
        self.assertFalse(has_view_statistics(None))

    def test_has_view_statistics_with_string(self):
        """Test has_view_statistics returns False for non-model objects"""
        self.assertFalse(has_view_statistics("not a model"))
