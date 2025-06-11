# ⚡ Quick Start Guide

Get djinsight up and running in your Django project in just 5 minutes!

## 🚀 Prerequisites

Before starting, make sure you have completed the [Installation Guide](installation.md).

## 📝 Step 1: Add Analytics to Your Models

djinsight works with **any Django model** through the `PageViewStatisticsMixin`.

### For Wagtail Pages

```python
# models.py
from wagtail.models import Page
from djinsight.models import PageViewStatisticsMixin

class BlogPage(Page, PageViewStatisticsMixin):
    introduction = models.TextField(blank=True)
    body = RichTextField(blank=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('introduction'),
        FieldPanel('body'),
    ]
```

### For Regular Django Models

```python
# models.py
from django.db import models
from django.urls import reverse
from djinsight.models import PageViewStatisticsMixin

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
```

## 🎨 Step 2: Add Template Tags

Add analytics tracking to your templates:

### Basic Tracking (Required)

```html
<!-- In your detail template (e.g., article_detail.html) -->
{% load djinsight_tags %}

<!-- Add tracking script - automatically detects 'article' from context -->
{% page_view_tracker %}

<!-- Or specify explicitly -->
{% page_view_tracker obj=article %}
```

### Display Statistics (Optional)

```html
{% load djinsight_tags %}

<div class="article-stats">
    <h3>📊 Article Statistics</h3>
    
    <!-- Individual components -->
    <p>Total Views: {% total_views_stat obj=article %}</p>
    <p>Unique Views: {% unique_views_stat obj=article %}</p>
    <p>Last Viewed: {% last_viewed_stat obj=article %}</p>
    
    <!-- Time-based stats -->
    <p>Today: {% views_today_stat obj=article %}</p>
    <p>This Week: {% views_week_stat obj=article %}</p>
    <p>This Month: {% views_month_stat obj=article %}</p>
</div>
```

### Live Counter (Optional)

```html
{% load djinsight_tags %}

<!-- Auto-refreshing live counter -->
<div class="live-stats">
    {% live_stats_counter obj=article refresh_interval=30 %}
</div>
```

## 🔄 Step 3: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

## 🚀 Step 4: Start Services

### Start Redis (if not running)
```bash
# macOS
brew services start redis

# Ubuntu/Debian  
sudo systemctl start redis-server
```

### Start Celery Workers
```bash
# Terminal 1: Start worker
celery -A your_project worker --loglevel=info

# Terminal 2: Start beat scheduler  
celery -A your_project beat --loglevel=info
```

### ⏰ Optional: Configure Task Schedules

By default, djinsight runs background tasks with these schedules:
- **Process views**: Every 10 seconds
- **Generate summaries**: Every 10 minutes  
- **Cleanup old data**: Daily at 1:00 AM

To customize schedules, set environment variables:

```bash
# Custom schedule examples
export DJINSIGHT_PROCESS_SCHEDULE="30"        # Every 30 seconds
export DJINSIGHT_SUMMARIES_SCHEDULE="*/5"     # Every 5 minutes
export DJINSIGHT_CLEANUP_SCHEDULE="0 2 * * *"   # Daily at 2:00 AM

# Then restart Celery beat
celery -A your_project beat --loglevel=info
```

📖 **See:** [Configuration Guide](configuration.md#celery-schedule-settings) for more schedule options.

## ✅ Step 5: Test It Works

1. **Visit your page** - Go to a page with djinsight tracking
2. **Check Redis** - Verify data is being stored:
   ```bash
   redis-cli
   keys djinsight:*
   ```
3. **Check admin** - Visit `/admin/djinsight/` to see logged views
4. **View live stats** - Refresh the page to see counters update

## 🎯 Quick Examples

### Minimal Article Template

```html
<!-- templates/blog/article_detail.html -->
{% extends 'base.html' %}
{% load djinsight_tags %}

{% block content %}
    <!-- Add tracking (required) -->
    {% page_view_tracker obj=article %}
    
    <article>
        <h1>{{ article.title }}</h1>
        
        <!-- Show view count -->
        <div class="meta">
            👁️ {% total_views_stat obj=article %} views
        </div>
        
        <div class="content">
            {{ article.content }}
        </div>
    </article>
{% endblock %}
```

### E-commerce Product Template

```html
<!-- templates/shop/product_detail.html -->
{% extends 'base.html' %}
{% load djinsight_tags %}

{% block content %}
    {% page_view_tracker obj=product %}
    
    <div class="product">
        <h1>{{ product.name }}</h1>
        <p class="price">${{ product.price }}</p>
        
        <!-- Popular product indicator -->
        {% total_views_stat obj=product as views %}
        {% if views > 100 %}
            <span class="badge">🔥 Popular!</span>
        {% endif %}
        
        <div class="stats">
            📊 {{ views }} views • 
            👥 {% unique_views_stat obj=product %} visitors
        </div>
    </div>
{% endblock %}
```

### Dashboard Overview

```html
<!-- templates/dashboard.html -->
{% load djinsight_tags %}

<div class="analytics-dashboard">
    <h2>📈 Site Analytics</h2>
    
    {% for article in popular_articles %}
        <div class="article-card">
            <h3>{{ article.title }}</h3>
            <div class="stats">
                👁️ {% total_views_stat obj=article %} •
                📅 {% views_today_stat obj=article %} today •
                {% live_stats_counter obj=article show_unique=True %}
            </div>
        </div>
    {% endfor %}
</div>
```

## 🔧 Common Customizations

### Custom Object Detection

If your template uses different variable names:

```html
<!-- For templates using 'post' instead of 'article' -->
{% page_view_tracker obj=post %}
{% total_views_stat obj=post %}

<!-- For generic views using 'object' -->
{% page_view_tracker obj=object %}
{% total_views_stat obj=object %}
```

### Debug Mode

Enable debug logging in development:

```html
{% page_view_tracker obj=article debug=True %}
```

Check browser console for tracking information.

### Custom Display Names

Override display names in your models:

```python
class Course(models.Model, PageViewStatisticsMixin):
    title = models.CharField(max_length=200)
    instructor = models.CharField(max_length=100)
    
    def get_display_name(self):
        return f"Course: {self.title} by {self.instructor}"
```

## 🚨 Troubleshooting

### Views Not Being Tracked

1. **Check JavaScript errors** in browser console
2. **Verify URLs** - ensure `djinsight.urls` is included
3. **Check Redis** - ensure Redis is running and accessible
4. **Test API endpoint**:
   ```bash
   curl -X POST http://localhost:8000/djinsight/record-view/ \
        -H "Content-Type: application/json" \
        -d '{"page_id": 1, "content_type": "blog.article"}'
   ```

### Celery Not Processing

1. **Check Celery workers** are running
2. **Verify Redis connection** in Celery
3. **Manual processing**:
   ```bash
   python manage.py process_pageviews
   ```

### Template Tags Not Working

1. **Load template tags** - ensure `{% load djinsight_tags %}`
2. **Check object context** - verify object is available in template
3. **Debug mode** - add `debug=True` to see console output

## ⚡ Next Steps

- 📖 [Template Tags Reference](template-tags.md) - Complete template tags documentation
- 🎨 [Template Examples](template-examples.md) - More implementation examples  
- 🔒 [Permission Control](permission-control.md) - Access control and security
- 🔧 [Configuration](configuration.md) - Advanced configuration options
- 📊 [Analytics Usage](analytics.md) - Advanced analytics features 