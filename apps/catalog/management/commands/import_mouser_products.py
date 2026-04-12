from django.core.management.base import BaseCommand

from apps.catalog.models import (
    Product,
    CanonicalProduct,
    Supplier,
    SupplierProduct,
)

from apps.catalog.services.external_api.mouser_api import (
    search_mouser_products,
    normalize_mouser_products,
)

from apps.catalog.services.category_engine import auto_assign_category


class Command(BaseCommand):
    help = "Import products from Mouser"

    def handle(self, *args, **kwargs):

        supplier, _ = Supplier.objects.get_or_create(
            code="MOUSER",
            defaults={
                "name": "Mouser Electronics",
                "website": "https://www.mouser.com",
            },
        )

        raw = search_mouser_products("Raspberry Pi")

        products = normalize_mouser_products(raw)

        print("\n===== MOUSER IMPORT START =====\n")

        for item in products:

            serial_number = item.get("mpn")

            if not serial_number:
                continue

            manufacturer = item.get("manufacturer")
            mpn = item.get("mpn")

            canonical = None

            if manufacturer and mpn:
                canonical, _ = CanonicalProduct.objects.get_or_create(
                    manufacturer=manufacturer,
                    mpn=mpn,
                    defaults={
                        "name": item.get("description") or mpn,
                        "image_url": item.get("image") or "",
                    },
                )

            category = auto_assign_category(item)

            obj, created = Product.objects.update_or_create(
                serial_number=serial_number,
                defaults={
                    "name": item.get("description") or serial_number,
                    "manufacturer": manufacturer,
                    "mpn": mpn,
                    "brand": manufacturer,
                    "price": 0,
                    "image_url": item.get("image") or "",
                    "source_url": item.get("url") or "",
                    "category": category,
                    "canonical": canonical,
                },
            )

            SupplierProduct.objects.update_or_create(
                supplier=supplier,
                supplier_part_number=serial_number,
                defaults={
                    "product": obj,
                    "price": 0,
                    "stock": 0,
                    "url": item.get("url") or "",
                },
            )

            if created:
                print(f"✔ Created: {obj.name}")
            else:
                print(f"↻ Updated: {obj.name}")

        print("\n===== MOUSER IMPORT DONE =====\n")
