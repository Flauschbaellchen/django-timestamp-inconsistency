from django.core.management import BaseCommand
from django.utils import timezone
from timestamps.models import MyModel
from django.db import connection

class Command(BaseCommand):
    help = "Reproduces the timestamp inconsistency"

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--times",
            "-t",
            dest="times",
            type=int,
            default=20,
            help="How many times should the check run, defaults to 20.",
        )

    def handle(self, *args, **options):
        self._check(options["times"])

    def _check(self, times):
        c = MyModel.objects.first()
        if not c:
            c = MyModel.objects.create(timestamp=timezone.now())

        old_timestamp = c.timestamp
        try:
            for idx in range(times):
                # force-reset the connection to the database
                # Can be left out, but then it depends on which node is accessed first (writer or reader)
                connection.connect()

                c.refresh_from_db()
                # or use: c = MyModel.objects.get(pk=c.pk)

                if idx > 0 and c.timestamp != old_timestamp:
                    print(f"\n /!\ Failed iteration {idx}: {old_timestamp} != {c.timestamp}")
                    exit(1)

                c.timestamp = old_timestamp
                c.save(update_fields=["timestamp"])
                print(".", end="")
        finally:
            print()
            MyModel.objects.filter(pk=c.pk).update(timestamp=old_timestamp)
