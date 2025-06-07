from django.core.management.base import BaseCommand, CommandError

from djInsight.tasks import run_generate_summaries


class Command(BaseCommand):
    help = "Generate daily page view summaries from detailed logs"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days-back",
            type=int,
            default=7,
            help="Number of days back to process (default: 7)",
        )

    def handle(self, *args, **options):
        days_back = options["days_back"]
        verbosity = options["verbosity"]

        if verbosity >= 1:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Starting to generate daily summaries for the last {days_back} days"
                )
            )

        try:
            generated = run_generate_summaries(verbosity=verbosity, days_back=days_back)

            if verbosity >= 1:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully generated {generated} daily summaries"
                    )
                )

        except Exception as e:
            raise CommandError(f"Error generating summaries: {e}")
