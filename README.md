# djInsight

A high-performance Django/Wagtail package for real-time page view analytics with Redis and Celery.

## Features

- **Universal Model Support**: Works with any Django model via mixin inheritance
- **Modular Template Tags**: Individual components for flexible UI design
- **Real-time Tracking**: JavaScript-based view counting with async Redis storage
- **High Performance**: Redis pipeline for fast data writes, Celery for background processing
- **Session-based Unique Visitors**: Accurate unique view counting using Django sessions
- **Template Tags**: Easy integration with simple template tags
- **Live Statistics**: Real-time stats display with auto-refresh
- **Automatic Data Processing**: Background tasks for Redis → Database sync
- **Data Cleanup**: Automatic cleanup of old tracking data
- **Admin Interface**: Django admin integration for viewing statistics

## Installation

```bash
pip install djInsight
```

## Quick Start

### 1. Add to Django Settings

```python
# settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Required dependencies
    'django_celery_beat',  # For periodic tasks
    
    # Your apps
    'djInsight',  # Add djInsight
    'myapp',  # Your app with models to track
]

# Redis Configuration (required)
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Celery Configuration (required for background processing)
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# djInsight Settings (optional)
DJINSIGHT_ENABLE_TRACKING = True  # Default: True
DJINSIGHT_REDIS_KEY_PREFIX = 'djinsight:'  # Default: 'djinsight:'
DJINSIGHT_CLEANUP_DAYS = 90  # Default: 90 (days to keep detailed logs)
```

### 2. Add to URLs

```python
# urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('djInsight/', include('djInsight.urls')),
    # ... your other URLs
]
```

### 3. Use with Your Models

djInsight works with **any Django model** through the `PageViewStatisticsMixin`:

#### Wagtail Pages

```python
# models.py
from wagtail.models import Page
from djInsight.models import PageViewStatisticsMixin

class BlogPage(Page, PageViewStatisticsMixin):
    introduction = models.TextField(blank=True)
    body = RichTextField(blank=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('introduction'),
        FieldPanel('body'),
    ]
```

#### Regular Django Models

```python
# models.py
from django.db import models
from django.urls import reverse
from djInsight.models import PageViewStatisticsMixin

class Article(models.Model, PageViewStatisticsMixin):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    published_at = models.DateTimeField(auto_now_add=True)
    
    def get_absolute_url(self):
        return reverse('article_detail', kwargs={'slug': self.slug})
    
    def __str__(self):
        return self.title

class Product(models.Model, PageViewStatisticsMixin):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    
    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})
    
    def __str__(self):
        return self.name

class Course(models.Model, PageViewStatisticsMixin):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    instructor = models.CharField(max_length=100)
    difficulty = models.CharField(max_length=50)
    
    def get_absolute_url(self):
        return reverse('course_detail', kwargs={'slug': self.slug})
    
    def get_display_name(self):
        return f"Course: {self.title} by {self.instructor}"

class Document(models.Model, PageViewStatisticsMixin):
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='documents/')
    category = models.CharField(max_length=100)
    
    def get_absolute_url(self):
        return reverse('document_view', kwargs={'pk': self.pk})
    
    def get_display_name(self):
        return f"Document: {self.title}"

# For models without get_absolute_url, override get_tracking_url:
class CustomModel(models.Model, PageViewStatisticsMixin):
    name = models.CharField(max_length=100)
    
    def get_tracking_url(self):
        return f'/custom/{self.id}/'
    
    def get_display_name(self):
        return f"Custom: {self.name}"

# E-commerce example
class Category(models.Model, PageViewStatisticsMixin):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    
    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})

# Real estate example  
class Property(models.Model, PageViewStatisticsMixin):
    address = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    bedrooms = models.IntegerField()
    
    def get_absolute_url(self):
        return reverse('property_detail', kwargs={'pk': self.pk})
    
    def get_display_name(self):
        return f"Property: {self.address}"
```

### 4. Template Tags Usage

djInsight now provides **modular template tags** for maximum flexibility:

#### Basic Tracking

```html
{% load djInsight_tags %}

<!-- Automatic object detection from context -->
{% page_view_tracker %}

<!-- Or specify the object explicitly -->
{% page_view_tracker obj=article %}
{% page_view_tracker obj=product debug=True async_load=False %}
```

#### Individual Statistics Components

```html
{% load djInsight_tags %}

<!-- Individual statistics - mix and match as needed -->
{% total_views_stat obj=article %}
{% unique_views_stat obj=article %}
{% last_viewed_stat obj=article %}
{% first_viewed_stat obj=article %}

<!-- Time-based statistics -->
{% views_today_stat obj=article %}
{% views_week_stat obj=article %}
{% views_month_stat obj=article %}

<!-- Live counter with auto-refresh -->
{% live_stats_counter obj=article show_unique=True refresh_interval=30 %}
```

#### Complete Analytics Widget

```html
{% load djInsight_tags %}

<!-- All-in-one analytics widget -->
{% page_analytics_widget obj=article period='month' %}
```

#### Format Numbers

```html
{% load djInsight_tags %}

<!-- Format large numbers (1234 -> 1.2K) -->
{{ article.total_views|format_view_count }}
{{ product.unique_views|format_view_count }}
```

### 5. Template Examples

#### Article Detail with Modular Stats

```html
<!-- templates/articles/article_detail.html -->
{% extends 'base.html' %}
{% load djInsight_tags %}

{% block content %}
    <article>
        <h1>{{ article.title }}</h1>
        <div class="article-meta">
            <span>Published: {{ article.published_at|date:"M d, Y" }}</span>
            <span>{% total_views_stat obj=article %}</span>
        </div>
        
        <div class="content">
            {{ article.content|linebreaks }}
        </div>
        
        <!-- Custom stats layout -->
        <div class="article-stats">
            <div class="main-stats">
                {% total_views_stat obj=article %}
                {% unique_views_stat obj=article %}
            </div>
            
            <div class="time-stats">
                {% views_today_stat obj=article %}
                {% views_week_stat obj=article %}
                {% views_month_stat obj=article %}
            </div>
            
            <div class="meta-stats">
                {% first_viewed_stat obj=article %}
                {% last_viewed_stat obj=article %}
            </div>
        </div>
        
        <!-- Live counter -->
        {% live_stats_counter obj=article refresh_interval=15 %}
    </article>
    
    <!-- Track this page view -->
    {% page_view_tracker obj=article %}
{% endblock %}
```

#### Product Page with Conditional Stats

```html
<!-- templates/shop/product_detail.html -->
{% extends 'base.html' %}
{% load djInsight_tags %}

{% block content %}
    <div class="product">
        <h1>{{ product.name }}</h1>
        <p class="price">${{ product.price }}</p>
        
        <!-- Show popularity if product has views -->
        {% if product.total_views > 0 %}
        <div class="popularity-badge">
            🔥 Popular: {{ product.total_views|format_view_count }} views
        </div>
        {% endif %}
        
        <div class="description">
            {{ product.description|linebreaks }}
        </div>
        
        <!-- Minimal stats display -->
        <div class="product-stats">
            {% total_views_stat obj=product %}
            {% unique_views_stat obj=product %}
            {% views_today_stat obj=product %}
        </div>
        
        <!-- Live tracking for high-value products -->
        {% if product.price >= 100 %}
            {% live_stats_counter obj=product show_unique=True refresh_interval=10 %}
        {% endif %}
    </div>
    
    {% page_view_tracker obj=product %}
{% endblock %}
```

#### Dashboard with Multiple Objects

```html
<!-- templates/dashboard.html -->
{% extends 'base.html' %}
{% load djInsight_tags %}

{% block content %}
    <div class="dashboard">
        <h1>Content Dashboard</h1>
        
        {% for article in popular_articles %}
        <div class="content-card">
            <h3><a href="{{ article.get_absolute_url }}">{{ article.title }}</a></h3>
            
            <div class="stats-row">
                {% total_views_stat obj=article %}
                {% unique_views_stat obj=article %}
                {% views_today_stat obj=article %}
            </div>
            
            {% if article.total_views > 1000 %}
                <span class="badge trending">🔥 Trending</span>
            {% endif %}
        </div>
        {% endfor %}
        
        <!-- Admin-only detailed analytics -->
        {% if user.is_staff %}
        <div class="admin-section">
            <h2>📊 Admin Analytics</h2>
            {% for item in recent_content %}
                <div class="admin-stats">
                    <strong>{{ item.title }}</strong>
                    <div class="detailed-stats">
                        {% total_views_stat obj=item %}
                        {% unique_views_stat obj=item %}
                        {% first_viewed_stat obj=item %}
                        {% last_viewed_stat obj=item %}
                        {% views_week_stat obj=item %}
                    </div>
                </div>
            {% endfor %}
        </div>
        {% endif %}
    </div>
{% endblock %}
```

#### Mobile-Optimized Stats

```html
<!-- templates/mobile/article_detail.html -->
{% extends 'base.html' %}
{% load djInsight_tags %}

{% block content %}
    <article class="mobile-article">
        <h1>{{ article.title }}</h1>
        
        <!-- Compact stats for mobile -->
        <div class="mobile-stats">
            <span class="stat-item">
                {{ article.total_views|format_view_count }} views
            </span>
            <span class="stat-item">
                {{ article.unique_views|format_view_count }} readers
            </span>
        </div>
        
        <div class="content">
            {{ article.content|linebreaks }}
        </div>
        
        <!-- Optional: Show more stats on tap -->
        <details class="expandable-stats">
            <summary>📊 More Statistics</summary>
            <div class="expanded-stats">
                {% views_today_stat obj=article %}
                {% views_week_stat obj=article %}
                {% first_viewed_stat obj=article %}
                {% last_viewed_stat obj=article %}
            </div>
        </details>
        
        <!-- Live counter for mobile -->
        {% live_stats_counter obj=article show_unique=False refresh_interval=60 %}
    </article>
    
    {% page_view_tracker obj=article async_load=True %}
{% endblock %}
```

### 6. Available Template Tags

#### Core Tags

- `{% page_view_tracker %}` - JavaScript tracking code
- `{% page_stats_display %}` - Live statistics with auto-refresh
- `{% page_analytics_widget %}` - Complete analytics widget
- `{{ count|format_view_count }}` - Number formatting filter

#### Individual Statistics Components

- `{% total_views_stat %}` - Total page views
- `{% unique_views_stat %}` - Unique visitors count
- `{% last_viewed_stat %}` - Last view timestamp
- `{% first_viewed_stat %}` - First view timestamp
- `{% views_today_stat %}` - Today's views
- `{% views_week_stat %}` - This week's views
- `{% views_month_stat %}` - This month's views
- `{% live_stats_counter %}` - Live counter with auto-refresh

#### All tags support:
- **Automatic object detection** from template context
- **Explicit object parameter**: `obj=article`
- **Flexible styling** through CSS classes

### 7. Styling Your Statistics

Each component includes CSS classes for easy customization:

```css
/* Individual stat items */
.djinsight-stat-item {
    background: white;
    padding: 0.75rem;
    border-radius: 4px;
    border-left: 4px solid #007bff;
    margin-bottom: 0.5rem;
}

.djinsight-stat-value {
    color: #007bff;
    font-size: 1.1rem;
    font-weight: 600;
}

/* Live counter */
.djinsight-live-counter {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 6px;
    padding: 1rem;
    margin: 1rem 0;
}

/* Complete analytics widget */
.djinsight-analytics-widget {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 1rem;
    margin: 1rem 0;
}
```

### 8. Run Migrations

```bash
python manage.py migrate djInsight
```

### 9. Start Background Services

Start Redis:
```bash
redis-server
```

Start Celery worker:
```bash
celery -A your_project worker -l info
```

Start Celery Beat (for periodic tasks):
```bash
celery -A your_project beat -l info
```

## Advanced Usage

### Custom Layouts

Create your own layouts by combining individual components:

```html
{% load djInsight_tags %}

<!-- Horizontal stats bar -->
<div class="stats-bar">
    {% total_views_stat obj=post %}
    {% unique_views_stat obj=post %}
    {% views_today_stat obj=post %}
</div>

<!-- Vertical stats sidebar -->
<aside class="stats-sidebar">
    <h4>📊 Statistics</h4>
    {% total_views_stat obj=article %}
    {% unique_views_stat obj=article %}
    {% last_viewed_stat obj=article %}
    {% live_stats_counter obj=article refresh_interval=30 %}
</aside>

<!-- Grid layout -->
<div class="stats-grid">
    {% total_views_stat obj=product %}
    {% unique_views_stat obj=product %}
    {% views_week_stat obj=product %}
    {% views_month_stat obj=product %}
</div>
```

### Conditional Display

```html
{% load djInsight_tags %}

<!-- Show different stats based on content type -->
{% if article.total_views > 100 %}
    <div class="popular-content">
        {% total_views_stat obj=article %}
        {% unique_views_stat obj=article %}
        {% views_today_stat obj=article %}
    </div>
{% else %}
    <div class="new-content">
        <p>📝 New article - be the first to read!</p>
        {% total_views_stat obj=article %}
    </div>
{% endif %}

<!-- Admin-only detailed stats -->
{% if user.is_staff %}
    <div class="admin-analytics">
        {% page_analytics_widget obj=article period='month' %}
    </div>
{% endif %}
```

### Analytics Queries

```python
# Find most popular content
from django.db.models import Q, F
from myapp.models import Article, Product

# Most viewed articles this month
popular_articles = Article.objects.filter(
    last_viewed_at__month=timezone.now().month
).order_by('-total_views')[:10]

# Products with high unique view ratio
interesting_products = Product.objects.annotate(
    unique_ratio=F('unique_views') * 100.0 / F('total_views')
).filter(
    total_views__gte=100,
    unique_ratio__gte=70.0
).order_by('-unique_ratio')
```

### Template Tag Options

#### page_view_tracker
```html
{% page_view_tracker obj=article async_load=False debug=True %}
```
- `obj`: Object to track (auto-detected if not provided)
- `async_load`: Load after page load (default: True)
- `debug`: Enable JavaScript console logging (default: False)

#### live_stats_counter
```html
{% live_stats_counter obj=article show_unique=True refresh_interval=30 %}
```
- `obj`: Object to show stats for (auto-detected if not provided)
- `show_unique`: Show unique view count (default: True)
- `refresh_interval`: Auto-refresh in seconds (default: 30)

#### page_analytics_widget
```html
{% page_analytics_widget obj=article period='month' %}
```
- `obj`: Object to show analytics for (auto-detected if not provided)
- `period`: Time period for statistics ('week' or 'month')

### Management Commands

```bash
# Process Redis data to database manually
python manage.py process_pageviews --batch-size 100

# Generate daily summaries
python manage.py generate_summaries

# Cleanup old data
python manage.py cleanup_pageviews --days 30 --yes
```

### Custom Context Detection

The system automatically looks for objects in template context using these variable names:
- `page` (Wagtail pages)
- `object` (Django generic views)
- `article` (custom articles)
- `post` (blog posts)
- `item` (general items)

### Backward Compatibility

For existing Wagtail users, these aliases are provided:

```html
<!-- Old Wagtail-specific tags still work -->
{% wagtail_page_view_tracker page=page %}
{% wagtail_page_stats_display page=page %}
{% wagtail_page_analytics_widget page=page %}
```

## Performance

- **Redis Pipeline**: Batches multiple Redis operations for better performance
- **Template Caching**: Individual components can be cached separately
- **Async JavaScript**: Non-blocking page view tracking
- **Celery Tasks**: Background processing prevents database bottlenecks
- **Data Aggregation**: Daily summaries reduce query complexity
- **Automatic Cleanup**: Keeps database size manageable

## Redis Key Structure

djInsight uses Redis for high-performance real-time analytics with the following key structure:

### View Data Keys
Individual page view records with complete metadata:
```
djinsight:12345678-abcd-1234-5678-abcdef123456
```
Each key contains JSON data with page_id, content_type, session, IP, timestamp, etc.

### Counter Keys
For tracking total views with content type identification:
```
djinsight:counter:blog.article:5        # New format (recommended)
djinsight:counter:5                      # Legacy format (backward compatibility)
```

### Unique Counter Keys
For tracking unique visitors per content:
```
djinsight:unique_counter:blog.article:5  # New format (recommended)
djinsight:unique_counter:5               # Legacy format (backward compatibility)
```

### Session Tracking Keys
To prevent double-counting views from the same session:
```
djinsight:session:abc123:page:5
```

### Analysis Commands

Use the included management command to analyze your Redis keys:

```bash
# Analyze Redis key structure and identify object types
python manage.py analyze_redis

# Sample output:
# Redis Key Analysis:
# Object ID 5: blog.article - "Article Title" (15 total views)
# Object ID 12: shop.product - "Product Name" (8 total views)
```

### Key Migration

The system automatically creates both new content-type-specific keys and maintains backward compatibility:

- **New implementations**: Use content-type keys for better object identification
- **Existing systems**: Continue working with legacy keys seamlessly
- **Analytics queries**: Can distinguish between different model types

### Key Expiration

All Redis keys have configurable expiration times:

```python
# settings.py
DJINSIGHT_REDIS_EXPIRATION = 60 * 60 * 24 * 7  # 7 days (default)
```

## Configuration Options

```python
# settings.py

# Enable/disable tracking
DJINSIGHT_ENABLE_TRACKING = True

# Redis key prefix
DJINSIGHT_REDIS_KEY_PREFIX = 'djinsight:'

# How long to keep detailed view logs (days)
DJINSIGHT_CLEANUP_DAYS = 90

# Batch size for processing Redis data
DJINSIGHT_BATCH_SIZE = 1000

# Redis connection timeout
DJINSIGHT_REDIS_TIMEOUT = 5
```

## Requirements

- Python 3.8+
- Django 3.2+
- Redis 4.0+
- Celery 5.0+
- django-redis
- Optional: Wagtail 3.0+ (for Wagtail integration)

## License

MIT License