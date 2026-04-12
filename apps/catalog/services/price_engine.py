from apps.catalog.models import SupplierProduct


def get_price_comparison(product):
    suppliers = SupplierProduct.objects.filter(product=product)

    data = []

    for sp in suppliers:
        data.append(
            {
                "supplier": sp.supplier.name,
                "price": sp.price,
                "stock": sp.stock,
                "url": sp.url,
            }
        )

    data.sort(key=lambda x: x["price"])

    if data:
        data[0]["best"] = True

    return data
