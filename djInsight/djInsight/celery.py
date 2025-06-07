"""
Celery configuration for djInsight.

This module provides Celery configuration and periodic tasks for processing
page view statistics.
"""

import os

from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "your_project.settings")

app = Celery("djInsight")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Periodic tasks configuration
app.conf.beat_schedule = {
    "process-page-views": {
        "task": "djInsight.tasks.process_page_views_task",
        "schedule": crontab(minute="*/5"),  # Every 5 minutes
        "kwargs": {
            "batch_size": getattr(settings, "DJINSIGHT_BATCH_SIZE", 1000),
            "max_records": getattr(settings, "DJINSIGHT_MAX_RECORDS", 10000),
        },
    },
    "generate-daily-summaries": {
        "task": "djInsight.tasks.generate_daily_summaries_task",
        "schedule": crontab(hour=1, minute=0),  # Daily at 1:00 AM
        "kwargs": {
            "days_back": getattr(settings, "DJINSIGHT_SUMMARY_DAYS_BACK", 7),
        },
    },
    "cleanup-old-data": {
        "task": "djInsight.tasks.cleanup_old_data_task",
        "schedule": crontab(
            hour=2, minute=0, day_of_week=0
        ),  # Weekly on Sunday at 2:00 AM
        "kwargs": {
            "days_to_keep": getattr(settings, "DJINSIGHT_DAYS_TO_KEEP", 90),
        },
    },
}

# Timezone configuration
app.conf.timezone = getattr(settings, "TIME_ZONE", "UTC")

# Additional Celery configuration
app.conf.update(
    # Task serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    # Task routing
    task_routes={
        "djInsight.tasks.*": {"queue": "djinsight"},
    },
    # Task execution
    task_always_eager=getattr(settings, "CELERY_TASK_ALWAYS_EAGER", False),
    task_eager_propagates=True,
    # Worker configuration
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    # Result backend (optional)
    result_backend=getattr(settings, "CELERY_RESULT_BACKEND", None),
    result_expires=3600,  # 1 hour
)


@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery configuration."""
    print(f"Request: {self.request!r}")
    return "Debug task completed"


# Example of how to configure Celery in your Django settings:
"""
# Celery Configuration
CELERY_BROKER_URL = 'redis://localhost:6379/1'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'

# djInsight specific settings
DJINSIGHT_BATCH_SIZE = 1000
DJINSIGHT_MAX_RECORDS = 10000
DJINSIGHT_SUMMARY_DAYS_BACK = 7
DJINSIGHT_DAYS_TO_KEEP = 90

# Redis settings for djInsight
DJINSIGHT_REDIS_HOST = 'localhost'
DJINSIGHT_REDIS_PORT = 6379
DJINSIGHT_REDIS_DB = 0
DJINSIGHT_REDIS_PASSWORD = None
DJINSIGHT_REDIS_KEY_PREFIX = 'djInsight:pageview:'
DJINSIGHT_REDIS_EXPIRATION = 60 * 60 * 24 * 7  # 7 days

# Enable/disable tracking
DJINSIGHT_ENABLE_TRACKING = True
"""
