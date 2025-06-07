# Generated migration for flexible model support

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("djInsight", "0001_initial"),
    ]

    operations = [
        # This migration is informational - it documents the change to flexible model support
        # No actual database changes are needed as the mixin is abstract
        migrations.RunSQL(
            sql="-- Updated djInsight to support any Django model via PageViewStatisticsMixin",
            reverse_sql="-- Reverting to Wagtail-only support",
            state_operations=[],
        ),
    ]
