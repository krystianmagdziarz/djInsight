# Permission Control in djinsight

djinsight provides configurable access control for analytics data. By default, statistics are visible to all users, but you can restrict access to administrators only.

## Configuration

### Basic Setup

Add the following setting to your Django `settings.py`:

```python
# Allow all users to view statistics (default)
DJINSIGHT_ADMIN_ONLY = False

# Restrict statistics to admin users only
DJINSIGHT_ADMIN_ONLY = True
```

### Default Behavior

When `DJINSIGHT_ADMIN_ONLY` is not set or set to `False`:
- All users can view statistics
- Template tags render normally
- API endpoints are accessible to all users
- No permission checks are performed

### Admin-Only Mode

When `DJINSIGHT_ADMIN_ONLY = True`:
- Only authenticated staff users (`user.is_staff = True`) can view statistics
- Template tags return empty content for non-admin users
- API endpoints require staff permissions
- Non-admin users see "Access denied" messages in templates

## Implementation Details

### View-Level Protection

The `get_page_stats` API endpoint is protected using Django's `@user_passes_test` decorator:

```python
@user_passes_test(check_stats_permission, login_url=None)
def get_page_stats(request):
    # ... view logic
```

### Template-Level Protection

All template tags check permissions before rendering:

```python
def total_views_stat(context, obj=None):
    # Check permissions first
    request = context.get("request")
    if not _check_stats_permission(request):
        return {"total_views": 0, "obj": None, "no_permission": True}
    
    # ... render statistics
```

### Permission Check Function

The core permission logic:

```python
def check_stats_permission(user):
    """
    Check if user has permission to view statistics.
    
    If DJINSIGHT_ADMIN_ONLY is True, only staff users can view stats.
    Otherwise, all users can view stats.
    """
    admin_only = getattr(settings, 'DJINSIGHT_ADMIN_ONLY', False)
    
    if admin_only:
        return user.is_authenticated and user.is_staff
    else:
        return True
```

## Usage Examples

### Template Usage

```html
{% load djinsight_tags %}

<!-- These will respect permission settings -->
{% total_views_stat %}
{% unique_views_stat %}
{% page_analytics_widget %}

<!-- When permission is denied, templates show: -->
<!-- djinsight: Access denied -->
```

### Conditional Display

```html
{% load djinsight_tags %}

<!-- Check if user has permission before showing analytics section -->
{% if user.is_staff or not DJINSIGHT_ADMIN_ONLY %}
    <div class="analytics-section">
        {% page_analytics_widget %}
    </div>
{% else %}
    <p>Analytics are only available to administrators.</p>
{% endif %}
```

### JavaScript/AJAX Considerations

When using live counters or AJAX requests:

```javascript
// The get_page_stats endpoint will return 403 Forbidden for non-admin users
// when DJINSIGHT_ADMIN_ONLY = True

fetch('/djinsight/page-stats/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
    },
    body: JSON.stringify({
        page_id: 123,
        content_type: 'blog.article'
    })
})
.then(response => {
    if (response.status === 403) {
        console.log('Access denied: Admin privileges required');
        return;
    }
    return response.json();
})
.then(data => {
    // Handle successful response
});
```

## Security Considerations

### Staff User Requirement

The permission system checks for `user.is_staff = True`, not `user.is_superuser`. This means:

- Django admin users with staff status can view statistics
- Regular users cannot view statistics (when admin-only mode is enabled)
- Superusers can view statistics (since they typically have staff status)

### Anonymous Users

Anonymous (non-authenticated) users are always denied access when admin-only mode is enabled.

### Template Context

The permission check requires a `request` object in the template context. Ensure your views pass the request:

```python
def my_view(request):
    return render(request, 'template.html', {
        'object': my_object,
        # request is automatically available in template context
    })
```

## Migration Guide

### Upgrading from Previous Versions

If you're upgrading from a version without permission control:

1. **No action required** - The default behavior (`DJINSIGHT_ADMIN_ONLY = False`) maintains backward compatibility
2. **To enable admin-only mode** - Add `DJINSIGHT_ADMIN_ONLY = True` to your settings
3. **Template updates** - No template changes required; permission checks are automatic

### Testing Permission Changes

```python
# In your Django shell or tests
from django.conf import settings
from django.contrib.auth.models import User
from djinsight.views import check_stats_permission

# Test with different users
admin_user = User.objects.filter(is_staff=True).first()
regular_user = User.objects.filter(is_staff=False).first()

print(f"Admin can view stats: {check_stats_permission(admin_user)}")
print(f"Regular user can view stats: {check_stats_permission(regular_user)}")
```

## Troubleshooting

### Common Issues

1. **Statistics not showing for admin users**
   - Verify `user.is_staff = True` for the admin user
   - Check that `DJINSIGHT_ADMIN_ONLY = True` is set correctly

2. **Permission denied for all users**
   - Ensure the setting name is correct: `DJINSIGHT_ADMIN_ONLY`
   - Check that the request object is available in template context

3. **AJAX requests failing**
   - Verify CSRF token is included in requests
   - Check that the user has staff privileges when admin-only mode is enabled

### Debug Mode

Enable debug mode in template tags to see permission check results:

```html
{% load djinsight_tags %}
{% page_view_tracker debug=True %}
```

This will log permission check results to the Django logger.

## Related Settings

```python
# Complete djinsight configuration with permission control
DJINSIGHT_ADMIN_ONLY = True  # Restrict to admin users
DJINSIGHT_ENABLE_TRACKING = True  # Enable/disable tracking entirely
DJINSIGHT_REDIS_HOST = 'localhost'
DJINSIGHT_REDIS_PORT = 6379
DJINSIGHT_REDIS_DB = 0
```

Note: `DJINSIGHT_ENABLE_TRACKING` controls whether page views are recorded, while `DJINSIGHT_ADMIN_ONLY` controls who can view the recorded statistics. 