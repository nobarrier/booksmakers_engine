from django.core.management.base import BaseCommand
from apps.catalog.services.importers.digikey_importer import (
    fetch_and_transform,
    save_products,
)
from apps.catalog.services.importers.digikey_importer import run_import


class Command(BaseCommand):
    help = "Import products from Digikey"

    def add_arguments(self, parser):
        parser.add_argument(
            "--keyword",
            type=str,
            default="arduino",
            help="Search keyword for Digikey",
        )

    def handle(self, *args, **options):
        keyword = options["keyword"]

        self.stdout.write(f"Searching Digikey for: {keyword}")

        products = fetch_and_transform(keyword)
        run_import(keyword)

        self.stdout.write(self.style.SUCCESS("Import completed."))
