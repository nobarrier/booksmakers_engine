from django.core.management.base import BaseCommand
from apps.catalog.services.importers.digikey_importer import run_import


class Command(BaseCommand):
    help = "Import products from DigiKey"

    def add_arguments(self, parser):
        parser.add_argument(
            "--keyword",
            type=str,
            default="arduino",
            help="Search keyword for DigiKey",
        )

    def handle(self, *args, **options):
        keyword = options["keyword"]

        self.stdout.write(f"Searching DigiKey for: {keyword}")

        imported_count = run_import(keyword)

        self.stdout.write(
            self.style.SUCCESS(f"Import completed. Imported: {imported_count}")
        )
