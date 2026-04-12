from apps.catalog.models import Product, CanonicalProduct


def unify_products_by_mpn():
    products = (
        Product.objects.exclude(mpn="")
        .exclude(manufacturer="")
        .select_related("category")
    )

    for p in products:

        manufacturer = p.manufacturer.lower().strip()
        mpn = p.mpn.lower().strip()

        canonical, created = CanonicalProduct.objects.get_or_create(
            manufacturer=manufacturer,
            mpn=mpn,
            defaults={
                "name": p.name,
                "category": p.category,
                "image_url": p.image_url,
            },
        )

        if p.canonical_id != canonical.id:
            p.canonical = canonical
            p.save(update_fields=["canonical"])
