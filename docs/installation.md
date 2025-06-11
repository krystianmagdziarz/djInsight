# 📦 Installation Guide

This guide will walk you through installing and setting up djinsight in your Django/Wagtail project.

## 🚀 Quick Installation

```bash
pip install djinsight
```

## 📋 Prerequisites

Before installing djinsight, ensure you have:

- 🐍 **Python 3.8+**
- 🎯 **Django 3.2+** 
- 🚀 **Redis 4.0+** (running and accessible)
- 🔄 **Celery 5.0+** (for background processing)

## 🔧 System Dependencies

### Redis Installation

**macOS (using Homebrew):**
```bash
brew install redis
brew services start redis
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

**Windows:**
Download Redis from [official website](https://redis.io/download) or use WSL.

### Verify Redis Installation
```bash
redis-cli ping
# Should return: PONG
```

## ⚙️ Python Dependencies

djinsight automatically installs these dependencies:

```bash
# Core dependencies (installed automatically)
Django>=3.2
wagtail>=3.0
redis>=4.0.0
celery>=5.0.0
django-redis>=5.0.0
```

## 🎯 Django Project Setup

### 1. Install djinsight
```bash
pip install djinsight
```

### 2. Add to INSTALLED_APPS
```python
# settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Required for Celery periodic tasks
    'django_celery_beat',
    
    # Add djinsight
    'djinsight',
    
    # Your apps
    'myapp',
]
```

### 3. Configure Redis Cache
```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

### 4. Configure Celery
```python
# settings.py
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
```

### 5. Add URLs
```python
# urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('djinsight/', include('djinsight.urls')),
    # ... your other URLs
]
```

### 6. Run Migrations
```bash
python manage.py migrate
```

## 🔄 Celery Setup

### Create Celery Configuration
Create `celery.py` in your project directory:

```python
# your_project/celery.py
import os
from celery import Celery

# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')

app = Celery('your_project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

### Update __init__.py
```python
# your_project/__init__.py
from .celery import app as celery_app

__all__ = ('celery_app',)
```

### Start Celery Workers
```bash
# In separate terminal windows:

# Start worker
celery -A your_project worker --loglevel=info

# Start beat scheduler (for periodic tasks)
celery -A your_project beat --loglevel=info
```

### ⏰ Optional: Configure Task Schedules

djinsight uses these default schedules:
- **Process page views**: Every 10 seconds
- **Generate summaries**: Every 10 minutes
- **Cleanup old data**: Daily at 1:00 AM

To customize, set environment variables before starting Celery:

```bash
# Example custom schedules
DJINSIGHT_PROCESS_SCHEDULE="30"        # Every 30 seconds
DJINSIGHT_SUMMARIES_SCHEDULE="*/15"    # Every 15 minutes
DJINSIGHT_CLEANUP_SCHEDULE="0 2 * * *"   # Daily at 2:00 AM

# Then start Celery beat
celery -A your_project beat --loglevel=info
```

📖 **See:** [Configuration Guide](configuration.md#celery-schedule-settings) for detailed schedule options.

## ✅ Verify Installation

### 1. Check Django Admin
Visit `/admin/` and verify djinsight models are available.

### 2. Test Redis Connection
```python
# In Django shell
python manage.py shell

from django.core.cache import cache
cache.set('test', 'Hello djinsight!')
print(cache.get('test'))  # Should print: Hello djinsight!
```

### 3. Test Celery Tasks
```python
# In Django shell
from djinsight.tasks import process_page_views_task
result = process_page_views_task.delay()
print(result.status)  # Should print: SUCCESS or PENDING
```

## 🚨 Troubleshooting

### Redis Connection Issues
```bash
# Check if Redis is running
redis-cli ping

# Check Redis logs
redis-cli monitor

# Test connection with specific host/port
redis-cli -h localhost -p 6379 ping
```

### Celery Issues
```bash
# Check if Celery can connect to Redis
celery -A your_project inspect ping

# Check active tasks
celery -A your_project inspect active

# Restart Celery workers
pkill -f "celery worker"
celery -A your_project worker --loglevel=info
```

### Django Issues
```bash
# Check for migration issues
python manage.py showmigrations djinsight

# Re-run migrations
python manage.py migrate djinsight

# Check URL configuration
python manage.py shell
from django.urls import reverse
print(reverse('djinsight:record_view'))
```

## 🔧 Optional Configuration

See [Configuration Guide](configuration.md) for advanced settings and customization options.

## ⚡ Next Steps

1. Follow the [Quick Start Guide](quick-start.md) to add analytics to your models
2. Explore [Template Tags](template-tags.md) for UI integration
3. Check [Template Examples](template-examples.md) for implementation ideas 