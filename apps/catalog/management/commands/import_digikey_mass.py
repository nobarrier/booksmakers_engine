from django.core.management.base import BaseCommand
from apps.catalog.services.importers.digikey_importer import run_import

KEYWORDS = [
    "arduino",
    "esp32",
    "stm32",
    "sensor",
    "imu sensor",
    "dc dc converter",
    "voltage regulator",
    "wifi module",
    "bluetooth module",
    "stepper motor",
    "servo motor",
]


class Command(BaseCommand):
    help = "Mass import Digikey products"

    def handle(self, *args, **options):
        for keyword in KEYWORDS:
            print("\n============================")
            print("IMPORT:", keyword)
            print("============================\n")

            run_import(keyword)

        print("\nImport completed.")
