from django.core.management.base import BaseCommand
from apps.catalog.services.external_api.digikey_api import (
    search_products,
    normalize_products,
)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        raw = search_products("Raspberry Pi")
        products = normalize_products(raw)

        print("\n===== RESULT =====\n")
        for p in products:
            print(p)
        print("\n===== DONE =====\n")
