from django.db import transaction
from django.utils.text import slugify

from apps.catalog.models import (
    Product,
    Supplier,
    SupplierProduct,
    Category,
    Mall,
)


def ensure_supplier(code: str):
    supplier, _ = Supplier.objects.get_or_create(code=code, defaults={"name": code})

    return supplier


def ensure_default_category():
    category, _ = Category.objects.get_or_create(
        name="미분류", parent=None, defaults={"slug": "uncategorized"}
    )

    return category


@transaction.atomic
def upsert_product(item):
    supplier = ensure_supplier(item.supplier_code)

    category = ensure_default_category()

    slug_base = slugify(item.name or "product")[:40]

    slug = f"{slug_base}-{item.supplier_part_number.lower()}"

    product, _ = Product.objects.update_or_create(
        serial_number=item.supplier_part_number,
        defaults={
            "manufacturer": item.manufacturer or "",
            "mpn": item.mpn or item.supplier_part_number,
            "name": item.name or "No Name",
            "slug": slug,
            "category": category,
            "brand": item.manufacturer or "",
            "price": int(item.price or 0),
            "short_description": "",
            "is_active": True,
        },
    )

    SupplierProduct.objects.update_or_create(
        supplier=supplier,
        supplier_part_number=item.supplier_part_number,
        defaults={
            "product": product,
            "price": float(item.price or 0),
            "stock": int(item.stock or 0),
            "url": item.url or "",
        },
    )

    return product
