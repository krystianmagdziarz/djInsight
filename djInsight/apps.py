from django.apps import AppConfig


class DjInsightConfig(AppConfig):
    name = "djinsight"
    verbose_name = "djinsight"

    def ready(self):
        # Import signal handlers
        pass
