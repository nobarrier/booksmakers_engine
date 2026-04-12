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

    def handle(self, *args, **kwargs):

        # DigiKey 공급처 생성
        supplier, _ = Supplier.objects.get_or_create(
            code="DIGIKEY",
            defaults={
                "name": "DigiKey",
                "website": "https://www.digikey.com",
            },
        )

        raw = search_products("Raspberry Pi")

        products = normalize_products(raw)

        print("\n===== IMPORT START =====\n")

        count = 0

        for item in products:

            serial_number = item.get("dk_part") or item.get("mpn")

            if not serial_number:
                continue

            manufacturer = item.get("manufacturer") or ""
            mpn = item.get("mpn") or ""

            canonical = None

            # CanonicalProduct 자동 생성
            if manufacturer and mpn:
                canonical, _ = CanonicalProduct.objects.get_or_create(
                    manufacturer=manufacturer,
                    mpn=mpn,
                    defaults={
                        "name": item.get("description") or mpn,
                        "image_url": item.get("image") or "",  # ⭐ 이미지 저장
                    },
                )

            # 카테고리 자동 분류
            from apps.catalog.models import Category

            category = auto_assign_category(item)

            # fallback category
            if category is None:
                category, _ = Category.objects.get_or_create(
                    name="Uncategorized",
                    slug="uncategorized",
                )

            slug_value = ensure_unique_slug(
                item.get("description") or serial_number,
                serial_number,
            )

            # Product 생성 / 업데이트
            obj, created = Product.objects.update_or_create(
                serial_number=serial_number,
                defaults={
                    "product_code": item.get("dk_part") or "",
                    "name": item.get("description") or serial_number,
                    "slug": slug_value,
                    "price": item.get("price") or 0,
                    "short_description": item.get("description") or "",
                    "brand": manufacturer,
                    "manufacturer": manufacturer,
                    "mpn": mpn,
                    "source_url": item.get("url") or "",
                    "image_url": item.get("image") or "",  # ⭐ 이미지 저장
                    "category": category,
                    "canonical": canonical,
                },
            )

            # SupplierProduct 생성 (가격비교용)
            SupplierProduct.objects.update_or_create(
                supplier=supplier,
                supplier_part_number=serial_number,
                defaults={
                    "product": obj,
                    "price": item.get("price") or 0,
                    "stock": item.get("stock") or 0,
                    "url": item.get("url") or "",
                },
            )

            if created:
                print(f"✔ Created: {obj.name}")
            else:
                print(f"↻ Updated: {obj.name}")

            count += 1

        print(f"\n===== DONE ({count} items) =====\n")
