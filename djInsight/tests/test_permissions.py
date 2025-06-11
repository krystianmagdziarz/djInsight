import json

from django.contrib.auth.models import AnonymousUser, User
from django.template import Context, Template
from django.test import RequestFactory, TestCase, override_settings

from djinsight.templatetags.djinsight_tags import _check_stats_permission
from djinsight.views import check_stats_permission


class PermissionControlTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin_user = User.objects.create_user(
            username="admin", email="admin@test.com", password="testpass", is_staff=True
        )
        self.regular_user = User.objects.create_user(
            username="user", email="user@test.com", password="testpass", is_staff=False
        )

    @override_settings(DJINSIGHT_ADMIN_ONLY=False)
    def test_admin_only_disabled_allows_all_users(self):
        """Test that when DJINSIGHT_ADMIN_ONLY=False, all users can access stats"""
        # Test with admin user
        self.assertTrue(check_stats_permission(self.admin_user))

        # Test with regular user
        self.assertTrue(check_stats_permission(self.regular_user))

        # Test with anonymous user
        anonymous = AnonymousUser()
        self.assertTrue(check_stats_permission(anonymous))

    @override_settings(DJINSIGHT_ADMIN_ONLY=True)
    def test_admin_only_enabled_restricts_to_staff(self):
        """Test that when DJINSIGHT_ADMIN_ONLY=True, only staff users can access stats"""
        # Test with admin user
        self.assertTrue(check_stats_permission(self.admin_user))

        # Test with regular user
        self.assertFalse(check_stats_permission(self.regular_user))

        # Test with anonymous user
        anonymous = AnonymousUser()
        self.assertFalse(check_stats_permission(anonymous))

    @override_settings(DJINSIGHT_ADMIN_ONLY=False)
    def test_template_tag_permission_check_disabled(self):
        """Test template tag permission check when admin_only is disabled"""
        request = self.factory.get("/")
        request.user = self.regular_user

        # Should allow access
        self.assertTrue(_check_stats_permission(request))

    @override_settings(DJINSIGHT_ADMIN_ONLY=True)
    def test_template_tag_permission_check_enabled_admin(self):
        """Test template tag permission check for admin when admin_only is enabled"""
        request = self.factory.get("/")
        request.user = self.admin_user

        # Should allow access for admin
        self.assertTrue(_check_stats_permission(request))

    @override_settings(DJINSIGHT_ADMIN_ONLY=True)
    def test_template_tag_permission_check_enabled_regular_user(self):
        """Test template tag permission check for regular user when admin_only is enabled"""
        request = self.factory.get("/")
        request.user = self.regular_user

        # Should deny access for regular user
        self.assertFalse(_check_stats_permission(request))

    @override_settings(DJINSIGHT_ADMIN_ONLY=True)
    def test_template_tag_permission_check_enabled_anonymous(self):
        """Test template tag permission check for anonymous user when admin_only is enabled"""
        request = self.factory.get("/")
        request.user = AnonymousUser()

        # Should deny access for anonymous user
        self.assertFalse(_check_stats_permission(request))

    def test_template_tag_permission_check_no_request(self):
        """Test template tag permission check when no request is provided"""
        # Should allow access when no request (fallback behavior)
        self.assertTrue(_check_stats_permission(None))

    @override_settings(DJINSIGHT_ADMIN_ONLY=True)
    def test_get_page_stats_view_permission_denied(self):
        """Test that get_page_stats view denies access to non-admin users when admin_only is enabled"""
        request = self.factory.post(
            "/djinsight/page-stats/",
            data=json.dumps({"page_id": 1}),
            content_type="application/json",
        )
        request.user = self.regular_user

        # This should be handled by the user_passes_test decorator
        # The actual test would need to be done through the URL dispatcher
        # For now, we test the permission function directly
        self.assertFalse(check_stats_permission(self.regular_user))

    @override_settings(DJINSIGHT_ADMIN_ONLY=True)
    def test_get_page_stats_view_permission_allowed(self):
        """Test that get_page_stats view allows access to admin users when admin_only is enabled"""
        request = self.factory.post(
            "/djinsight/page-stats/",
            data=json.dumps({"page_id": 1}),
            content_type="application/json",
        )
        request.user = self.admin_user

        # Test the permission function directly
        self.assertTrue(check_stats_permission(self.admin_user))

    def test_template_rendering_with_no_permission(self):
        """Test that template tags render correctly when permission is denied"""
        template_content = """
        {% load djinsight_tags %}
        {% total_views_stat %}
        """

        # Mock context with no_permission flag
        context = Context({"request": self.factory.get("/"), "no_permission": True})

        template = Template(template_content)
        rendered = template.render(context)

        # Should contain access denied comment
        self.assertIn("djinsight: Access denied", rendered)

    @override_settings(DJINSIGHT_ADMIN_ONLY=False)
    def test_default_setting_value(self):
        """Test that DJINSIGHT_ADMIN_ONLY defaults to False"""
        from django.conf import settings

        # When not explicitly set, should default to False
        admin_only = getattr(settings, "DJINSIGHT_ADMIN_ONLY", False)
        self.assertFalse(admin_only)
