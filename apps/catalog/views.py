from django.core.paginator import Paginator
from django.db.models import Case, IntegerField, Prefetch, Q, Value, When
from django.http import Http404, JsonResponse
from django.shortcuts import render

from apps.catalog.models import Product, Category
from apps.catalog.services.price_engine import get_price_comparison


def get_root_categories():
    children_qs = Category.objects.filter(is_active=True).order_by("sort_order", "name")

    return (
        Category.objects.filter(parent__isnull=True, is_active=True)
        .annotate(
            uncategorized_last=Case(
                When(name="Uncategorized", then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            )
        )
        .prefetch_related(Prefetch("children", queryset=children_qs))
        .order_by("uncategorized_last", "sort_order", "name")
    )


def home(request):
    q = request.GET.get("q", "").strip()

    products = Product.objects.filter(is_active=True).select_related("category")

    if q:
        products = products.filter(
            Q(name__icontains=q)
            | Q(category__name__icontains=q)
            | Q(brand__icontains=q)
            | Q(serial_number__icontains=q)
            | Q(mpn__icontains=q)
            | Q(manufacturer__icontains=q)
        )

    products = products.order_by("-created_at")

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "catalog/product_list.html",
        {
            "products": page_obj,
            "categories": get_root_categories(),
            "q": q,
        },
    )


def category(request, category_slug):
    current_category = Category.objects.filter(slug=category_slug).first()

    if not current_category:
        raise Http404("Category not found")

    q = request.GET.get("q", "").strip()

    root = current_category
    while root.parent:
        root = root.parent

    sidebar_categories = root.children.filter(is_active=True).order_by(
        "sort_order", "name"
    )

    descendant_ids = current_category.get_descendant_ids()

    products = Product.objects.filter(
        category_id__in=descendant_ids,
        is_active=True,
    ).select_related("category")

    if q:
        products = products.filter(
            Q(name__icontains=q)
            | Q(category__name__icontains=q)
            | Q(brand__icontains=q)
            | Q(serial_number__icontains=q)
            | Q(mpn__icontains=q)
            | Q(manufacturer__icontains=q)
        )

    products = products.order_by("-created_at")

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "catalog/product_list.html",
        {
            "category": current_category,
            "products": page_obj,
            "categories": get_root_categories(),
            "sidebar_categories": sidebar_categories,
            "q": q,
        },
    )


def product_detail(request, pk):
    product = Product.objects.prefetch_related("supplier_products__supplier").get(pk=pk)

    prices = product.supplier_products.all().order_by("price")

    return render(
        request,
        "catalog/product_detail.html",
        {
            "product": product,
            "prices": prices,
        },
    )


def product_price_compare(request, slug):
    try:
        product = Product.objects.get(slug=slug)
    except Product.DoesNotExist:
        return JsonResponse({"error": "Product not found"}, status=404)

    suppliers = []

    for sp in product.supplier_products.select_related("supplier"):
        suppliers.append(
            {
                "supplier": sp.supplier.name,
                "price": sp.price,
                "stock": sp.stock,
                "url": sp.url,
            }
        )

    return JsonResponse(
        {
            "product": product.name,
            "manufacturer": product.manufacturer,
            "mpn": product.mpn,
            "suppliers": suppliers,
        }
    )
