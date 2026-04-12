from django.utils.text import slugify

from apps.catalog.services.external_api.digikey_api import (
    search_products,
    normalize_products,
)

from apps.catalog.models import (
    Product,
    Category,
    ProductVariant,
    Warehouse,
    StockLedger,
    Mall,
    Supplier,
    SupplierProduct,
)

from apps.catalog.services.base_importer import NormalizedItem

category_cache = {}


def fetch_and_transform(keyword):
    raw_json = search_products(keyword)
    normalized = normalize_products(raw_json)

    items = []

    for item in normalized:
        data = NormalizedItem(
            supplier_code="digikey",
            supplier_part_number=item["dk_part"],
            manufacturer=item.get("manufacturer"),
            mpn=item.get("mpn") or item["dk_part"],
            name=item.get("description") or "Unknown",
            price=item.get("price") or 0,
            stock=item.get("stock") or 0,
            url=item.get("url") or "",
            category_path=item.get("category_path") or ["Digikey"],
            image_url=item.get("image"),
        )

        items.append(data)

    return items


def run_import(keyword):
    items = fetch_and_transform(keyword)

    print("items count:", len(items))

    for item in items:
        print("importing:", item.name)
        save_products([item])


def ensure_default_warehouse():
    warehouse, _ = Warehouse.objects.get_or_create(
        code="DIGIKEY_MAIN",
        defaults={"name": "Digikey Warehouse"},
    )

    return warehouse


def map_to_root_category(category_path):
    if not category_path:
        return "전자/전기 부품"

    first = category_path[0].lower()

    if "sensor" in first:
        return "전자/전기 부품"

    if "development" in first or "board" in first:
        return "MCU/개발보드"

    if "power" in first:
        return "전원/배터리"

    if "robot" in first:
        return "로봇/기계/모터"

    return "전자/전기 부품"


def ensure_category_tree(category_path):
    parent = None
    path_key = " > ".join(category_path)

    if path_key in category_cache:
        return category_cache[path_key]

    for level_name in category_path:
        slug_base = slugify(level_name)[:50]

        category, _ = Category.objects.get_or_create(
            name=level_name,
            parent=parent,
            defaults={"slug": slug_base},
        )

        parent = category

    category_cache[path_key] = parent

    return parent


def save_products(products):
    electronics_mall, _ = Mall.objects.get_or_create(
        code="electronics",
        defaults={"name": "Electronics Mall"},
    )

    supplier = Supplier.objects.get(code="digikey")

    for p in products:

        if not p.supplier_part_number:
            continue

        root_name = map_to_root_category(p.category_path)

        full_path = [root_name] + (p.category_path or [])

        category = ensure_category_tree(full_path)

        slug_base = slugify(p.name or "product")[:40]

        slug = f"{slug_base}-{p.supplier_part_number[:6]}"

        # 🔥 Product 생성 (이미지 URL 포함)
        product, created = Product.objects.update_or_create(
            manufacturer=p.manufacturer,
            mpn=p.mpn,
            defaults={
                "name": p.name or "No Name",
                "slug": slug,
                "serial_number": p.supplier_part_number,
                "category": category,
                "brand": p.manufacturer or "",
                "price": int(p.price or 0),
                "short_description": "",
                "source_url": p.url or "",
                "image_url": p.image_url or "",  # ⭐ 이미지 저장
                "is_active": True,
                "source_supplier": "digikey",
                "source_category_path": p.category_path,
                "mall": electronics_mall,
            },
        )

        # 🔥 가격 비교 데이터 저장
        SupplierProduct.objects.update_or_create(
            supplier=supplier,
            supplier_part_number=p.supplier_part_number,
            defaults={
                "product": product,
                "price": float(p.price or 0),
                "stock": int(p.stock or 0),
                "url": p.url or "",
            },
        )

        variant, v_created = ProductVariant.objects.get_or_create(
            product=product,
            sku=p.supplier_part_number,
            defaults={
                "cost_price": int(p.price or 0),
                "selling_price": int(p.price or 0),
                "is_active": True,
            },
        )

        warehouse = ensure_default_warehouse()

        if v_created and p.stock and p.stock > 0:
            StockLedger.objects.create(
                warehouse=warehouse,
                variant=variant,
                qty_change=int(p.stock),
                type="PURCHASE_IN",
                reference_type="DIGIKEY_IMPORT",
                reference_id=None,
            )

        print(
            ("CREATED" if created else "UPDATED"),
            product.name,
            "| Variant:",
            "NEW" if v_created else "EXISTS",
        )
