from django.core.management.base import BaseCommand
from apps.catalog.services.external_api.mouser_api import (
    search_mouser_products,
    normalize_mouser_products,
)


class Command(BaseCommand):
    help = "Test Mouser search"

    def handle(self, *args, **kwargs):
        raw = search_mouser_products("Raspberry Pi")

        print("\n===== RAW RESPONSE =====\n")
        print(raw)

        products = normalize_mouser_products(raw)
        print("\n===== RESULT =====\n")

        for p in products:
            print(p)

        print("\n===== DONE =====\n")
