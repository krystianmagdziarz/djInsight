from django.core.management.base import BaseCommand, CommandError

from djInsight.tasks import run_cleanup_old_data


class Command(BaseCommand):
    help = "Cleanup old page view logs older than specified days"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days-to-keep",
            type=int,
            default=90,
            help="Number of days of logs to keep (default: 90)",
        )
        parser.add_argument(
            "--confirm", action="store_true", help="Confirm deletion without prompting"
        )

    def handle(self, *args, **options):
        days_to_keep = options["days_to_keep"]
        verbosity = options["verbosity"]
        confirm = options["confirm"]

        if not confirm:
            response = input(
                f"This will delete page view logs older than {days_to_keep} days. "
                "Are you sure you want to continue? [y/N]: "
            )
            if response.lower() not in ["y", "yes"]:
                self.stdout.write(self.style.WARNING("Operation cancelled."))
                return

        if verbosity >= 1:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Starting to cleanup page view logs older than {days_to_keep} days"
                )
            )

        try:
            deleted = run_cleanup_old_data(
                verbosity=verbosity, days_to_keep=days_to_keep
            )

            if verbosity >= 1:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully deleted {deleted} old page view logs"
                    )
                )

        except Exception as e:
            raise CommandError(f"Error cleaning up old data: {e}")
