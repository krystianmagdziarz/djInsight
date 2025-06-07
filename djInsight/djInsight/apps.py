from django.apps import AppConfig


class DjInsightConfig(AppConfig):
    name = 'djInsight'
    verbose_name = 'djInsight'
    
    def ready(self):
        # Import signal handlers
        pass