from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.catalog.models import (
    Product,
    CanonicalProduct,
    Supplier,
    SupplierProduct,
)

from apps.catalog.services.external_api.digikey_api import (
    search_products,
    normalize_products,
)

from apps.catalog.services.category_engine import auto_assign_category


def ensure_unique_slug(base_slug, serial_number):
    slug = slugify(base_slug) or "item"

    candidate = slug
    suffix = 2

    while (
        Product.objects.filter(slug=candidate)
        .exclude(serial_number=serial_number)
        .exists()
    ):
        candidate = f"{slug}-{suffix}"
        suffix += 1

    return candidate


class Command(BaseCommand):
    help = "Import products from DigiKey and save to DB"

    def add_arguments(self, parser):
        parser.add_argument(
            "--keyword",
            type=str,
            default="Raspberry Pi",
            help="DigiKey search keyword",
        )

    def handle(self, *args, **kwargs):
        keyword = kwargs["keyword"]

        supplier, _ = Supplier.objects.get_or_create(
            code="DIGIKEY",
            defaults={
                "name": "DigiKey",
                "website": "https://www.digikey.com",
            },
        )

        raw = search_products(keyword)
        products = normalize_products(raw)

        print(f"\n===== IMPORT START: {keyword} =====\n")

        count = 0

        for item in products:
            serial_number = item.get("dk_part") or item.get("mpn")

            if not serial_number:
                continue

            manufacturer = item.get("manufacturer") or ""
            mpn = item.get("mpn") or ""
            image_url = item.get("image") or ""

            canonical = None

            if manufacturer and mpn:
                canonical, _ = CanonicalProduct.objects.get_or_create(
                    manufacturer=manufacturer,
                    mpn=mpn,
                    defaults={
                        "name": item.get("description") or mpn,
                        "image_url": image_url,
                    },
                )

            from apps.catalog.models import Category

            category = auto_assign_category(item)

            if category is None:
                category, _ = Category.objects.get_or_create(
                    name="Uncategorized",
                    slug="uncategorized",
                )

            slug_value = ensure_unique_slug(
                item.get("description") or serial_number,
                serial_number,
            )

            obj, created = Product.objects.update_or_create(
                serial_number=serial_number,
                defaults={
                    "product_code": item.get("dk_part") or "",
                    "name": item.get("description") or serial_number,
                    "slug": slug_value,
                    "price": int(item.get("price") or 0),
                    "short_description": item.get("description") or "",
                    "brand": manufacturer,
                    "manufacturer": manufacturer,
                    "mpn": mpn,
                    "source_url": item.get("url") or "",
                    "image_url": image_url,
                    "source_supplier": "digikey",
                    "source_category_path": item.get("category_path") or [],
                    "category": category,
                    "canonical": canonical,
                    "is_active": True,
                },
            )

            SupplierProduct.objects.update_or_create(
                supplier=supplier,
                supplier_part_number=serial_number,
                defaults={
                    "product": obj,
                    "price": float(item.get("price") or 0),
                    "stock": int(item.get("stock") or 0),
                    "url": item.get("url") or "",
                },
            )

            if created:
                print(f"✔ Created: {obj.name}")
            else:
                print(f"↻ Updated: {obj.name}")

            count += 1

        print(f"\n===== DONE ({count} items) =====\n")
