# 📊 djInsight

A high-performance Django/Wagtail package for real-time page view analytics with Redis and Celery.

## 🚀 Live Demo Screenshots

See djInsight in action with our comprehensive example application:

### Articles List
![djInsight Dashboard](docs/images/1.png)
*Main articles list with counters*

### Article Analytics 
![Article Detail View](docs/images/2.png)
*Individual article page with live view counters and modular statistics components*

### Analytics Demo
![Analytics Components](docs/images/3.png)
*Demonstration of djInsight's modular template tags and live statistics counter*

### E-commerce Integration
![Product Analytics](docs/images/4.png)
*Product pages with analytics tracking showing cross-content type support*

### Popular Content Overview
![Popular Content](docs/images/5.png)
*Dashboard showing most popular articles, products, and courses with real-time view counts*

---

## 🔧 How It Works

djInsight implements a **two-tier architecture** for maximum performance and reliability:

### 🚀 Tier 1: Real-time Data Collection (Redis)
- **Instant Tracking**: When a user visits a page, JavaScript sends an async request to djInsight's API
- **Redis Storage**: View data is immediately stored in Redis with sub-millisecond write times
- **Session Management**: Unique visitors are tracked using Django's session framework
- **Smart Key Structure**: Uses content-type specific Redis keys (`djinsight:counter:blog.article:123`)
- **No Database Blocking**: Zero impact on page load times - all writes go to Redis first

### 🔄 Tier 2: Background Processing (Celery)
- **Batch Processing**: Celery tasks periodically move data from Redis to PostgreSQL/MySQL
- **Data Aggregation**: Daily summaries are generated for efficient historical queries  
- **Automatic Cleanup**: Old detailed logs are cleaned up while preserving summaries
- **Fault Tolerance**: If database is down, data accumulates safely in Redis

### 🛡️ Reliability Features
- **Backward Compatibility**: Supports both new and legacy Redis key formats
- **Graceful Degradation**: Works even if Celery workers are temporarily down
- **Error Recovery**: Failed batch processing can be retried without data loss
- **Conflict Resolution**: Content-type separation prevents ID conflicts between models

## ✨ Features

- **🌐 Universal Model Support**: Works with any Django model via mixin inheritance
- **🧩 Modular Template Tags**: Individual components for flexible UI design
- **⚡ Real-time Tracking**: JavaScript-based view counting with async Redis storage
- **🚄 High Performance**: Redis pipeline for fast data writes, Celery for background processing
- **👥 Session-based Unique Visitors**: Accurate unique view counting using Django sessions
- **🔒 Permission Control**: Configurable access restrictions for statistics
- **🏷️ Template Tags**: Easy integration with simple template tags
- **📈 Live Statistics**: Real-time stats display with auto-refresh
- **🔄 Automatic Data Processing**: Background tasks for Redis → Database sync
- **🧹 Data Cleanup**: Automatic cleanup of old tracking data
- **🔧 Admin Interface**: Django admin integration for viewing statistics

## 📋 Metrics & Functions

### 📊 Core Metrics Collected
- **📈 Total Views**: Complete view count across all time
- **👥 Unique Views**: Session-based unique visitor tracking
- **📅 Time-based Views**: Today, this week, this month counters
- **⏰ Timestamps**: First view and last view tracking
- **🔗 URL Tracking**: Full request path and referrer information
- **📱 User Agent**: Browser and device information
- **🌍 IP Address**: Geographic tracking (privacy-compliant)

### 🛠️ Key Functions
- **⚡ Live Counters**: Real-time updating statistics with configurable refresh rates
- **📊 Historical Analysis**: Daily/weekly/monthly trend analysis
- **🔍 Content Performance**: Compare performance across different content types
- **📈 Popular Content**: Identify trending and top-performing pages
- **👥 Visitor Patterns**: Unique vs returning visitor analysis
- **🕐 Time Series Data**: View patterns over time with granular control
- **🔄 Data Export**: Export analytics data for external analysis
- **📱 API Access**: REST API for custom integrations and dashboards

### 🏷️ Template Components
- **📊 `total_views_stat`**: Display total view counts
- **👥 `unique_views_stat`**: Show unique visitor numbers  
- **⏰ `last_viewed_stat`**: Last visit timestamp
- **🎯 `first_viewed_stat`**: First view tracking
- **📅 `views_today_stat`**: Today's view count
- **📆 `views_week_stat`**: Weekly view statistics
- **📊 `views_month_stat`**: Monthly performance
- **🔄 `live_stats_counter`**: Auto-refreshing live counter

## 🆚 djInsight vs Google Analytics

### 🏆 **djInsight Advantages**

| Feature | 📊 djInsight | 📈 Google Analytics |
|---------|-------------|-------------------|
| **🚀 Performance** | Sub-millisecond Redis writes | ~100-500ms external requests |
| **🔒 Privacy** | Your servers, full control | Google's servers, limited control |
| **📱 Real-time** | Instant live counters | 24-48h delay for reports |
| **🎨 Customization** | Full template control | Limited widget customization |
| **💾 Data Ownership** | Your database, permanent | Google's data, subject to changes |
| **🛡️ GDPR Compliance** | Built-in privacy controls | Requires complex cookie consent |
| **📊 Granular Control** | Per-model, per-object tracking | Page-level only |
| **🔧 Integration** | Native Django/Wagtail | JavaScript embed only |
| **💰 Cost** | Open source, free | Free tier limitations |

### 📈 **Google Analytics Advantages**

| Feature | 📈 Google Analytics | 📊 djInsight |
|---------|-------------------|-------------|
| **🌍 External Traffic Analysis** | Full referrer tracking | Basic referrer only |
| **🎯 Advanced Segmentation** | Extensive user segments | Session-based only |
| **📊 E-commerce Tracking** | Built-in funnel analysis | Manual implementation |
| **🔍 Search Console Integration** | SEO data integration | No SEO features |
| **📱 Mobile App Tracking** | Native mobile support | Web-only focus |
| **🤖 Machine Learning** | AI-powered insights | Manual analysis |

### 🤝 **Best Practice: Use Both**

Many sites use **djInsight + Google Analytics** together:

- **📊 djInsight**: Internal dashboards, real-time stats, GDPR-compliant tracking
- **📈 Google Analytics**: Marketing analysis, SEO insights, external traffic sources
- **🔄 Hybrid Approach**: djInsight for app performance, GA for marketing metrics

## 📦 Quick Installation

```bash
pip install djInsight
```

Add to your Django settings and URLs:

```python
# settings.py
INSTALLED_APPS = [
    # ... other apps
    'djInsight',
]

# urls.py  
urlpatterns = [
    # ... other URLs
    path('djInsight/', include('djInsight.urls')),
]
```

Add analytics to your models:

```python
from djInsight.models import PageViewStatisticsMixin

class Article(models.Model, PageViewStatisticsMixin):
    title = models.CharField(max_length=200)
    # ... your fields
```

Add tracking to your templates:

```html
{% load djInsight_tags %}
{% page_view_tracker obj=article %}
<p>Views: {% total_views_stat obj=article %}</p>
```

## 📚 Documentation

- **📖 [Complete Documentation](docs/README.md)** - Full documentation index
- **📦 [Installation Guide](docs/installation.md)** - Step-by-step setup
- **⚡ [Quick Start](docs/quick-start.md)** - Get running in 5 minutes
- **🔒 [Permission Control](docs/permission-control.md)** - Access control and security
- **🏷️ [Template Tags](docs/template-tags.md)** - Complete reference
- **🎨 [Template Examples](docs/template-examples.md)** - Implementation examples
- **🔧 [Configuration](docs/configuration.md)** - Advanced settings
- **📊 [Analytics Usage](docs/analytics.md)** - Advanced features
- **🚄 [Performance](docs/performance.md)** - Optimization tips
- **🔑 [Redis Structure](docs/redis-structure.md)** - Understanding Redis keys
- **⚙️ [Management Commands](docs/management-commands.md)** - CLI tools

## 👨‍💻 Development

- **🤝 [Contributing Guide](docs/contributing.md)** - How to contribute
- **📄 [License](docs/license.md)** - MIT License details
- **🔄 [Changelog](CHANGELOG.md)** - Version history
- **🖼️ [Demo Gallery](docs/demo-gallery.md)** - Visual showcase

## 📋 Requirements

- 🐍 Python 3.8+
- 🎯 Django 3.2+
- 🚀 Redis 4.0+
- 🔄 Celery 5.0+
- 📦 django-redis
- 🌐 Optional: Wagtail 3.0+ (for Wagtail integration)

## 🔗 Links

- **📦 [PyPI Package](https://pypi.org/project/djInsight/)**
- **🐙 [GitHub Repository](https://github.com/krystianmagdziarz/djInsight)**
- **🐛 [Issue Tracker](https://github.com/krystianmagdziarz/djInsight/issues)**
- **💬 [Discussions](https://github.com/krystianmagdziarz/djInsight/discussions)**

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.