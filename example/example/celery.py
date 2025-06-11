"""
Celery configuration for example project with djinsight.
"""

import os

from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "example.settings")

app = Celery("example")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# djinsight periodic tasks - z nowymi częstotliwościami
app.conf.beat_schedule = {
    "process-page-views-every-10-seconds": {
        "task": "djinsight.tasks.process_page_views_task",
        "schedule": 10.0,  # Co 10 sekund
        "kwargs": {
            "batch_size": 1000,
            "max_records": 5000,
        },
    },
    "generate-daily-summaries-every-10-minutes": {
        "task": "djinsight.tasks.generate_daily_summaries_task",
        "schedule": crontab(minute="*/10"),  # Co 10 minut
        "kwargs": {
            "days_back": 7,
        },
    },
    "cleanup-old-data-daily-at-1am": {
        "task": "djinsight.tasks.cleanup_old_data_task",
        "schedule": crontab(hour=1, minute=0),  # Codziennie o 1:00
        "kwargs": {
            "days_to_keep": 30,  # Krócej dla example
        },
    },
}

app.conf.timezone = "UTC"


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
    return "Debug task completed"
