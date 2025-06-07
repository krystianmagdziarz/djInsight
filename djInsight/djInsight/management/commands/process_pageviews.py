from django.core.management.base import BaseCommand, CommandError

from djInsight.tasks import run_process_page_views


class Command(BaseCommand):
    help = "Process page views from Redis and store them in the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--batch-size",
            type=int,
            default=1000,
            help="Number of records to process in a single transaction (default: 1000)",
        )
        parser.add_argument(
            "--max-records",
            type=int,
            default=10000,
            help="Maximum number of records to process in a single run (default: 10000)",
        )

    def handle(self, *args, **options):
        batch_size = options["batch_size"]
        max_records = options["max_records"]
        verbosity = options["verbosity"]

        if verbosity >= 1:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Starting to process page views with batch_size={batch_size}, max_records={max_records}"
                )
            )

        try:
            processed = run_process_page_views(
                verbosity=verbosity, batch_size=batch_size, max_records=max_records
            )

            if verbosity >= 1:
                self.stdout.write(
                    self.style.SUCCESS(f"Successfully processed {processed} page views")
                )

        except Exception as e:
            raise CommandError(f"Error processing page views: {e}")
