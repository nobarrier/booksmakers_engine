from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Product, Category
from django.db.models import Q
from django.shortcuts import render
from django.http import Http404
from django.db.models import Q
from django.core.paginator import Paginator

from django.db.models import Q
from django.core.paginator import Paginator
from .models import Product, Category
from apps.catalog.services.price_engine import get_price_comparison


def home(request):
    q = request.GET.get("q", "").strip()

    products = Product.objects.filter(is_active=True).select_related("category")

    # 🔥 검색 기능
    if q:
        products = products.filter(
            Q(name__icontains=q)
            | Q(category__name__icontains=q)
            | Q(brand__icontains=q)
            | Q(serial_number__icontains=q)
            | Q(mpn__icontains=q)  # 🔥 추가 (MPN 검색)
            | Q(manufacturer__icontains=q)  # 🔥 추가
        )

    products = products.order_by("-created_at")

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    # 🔥 1차 카테고리
    categories = Category.objects.filter(parent__isnull=True, is_active=True).order_by(
        "sort_order"
    )

    return render(
        request,
        "catalog/product_list.html",
        {
            "products": page_obj,
            "categories": categories,
            "q": q,
        },
    )


def category(request, category_slug):
    category = Category.objects.filter(slug=category_slug).first()

    if not category:
        raise Http404("Category not found")

    q = request.GET.get("q", "").strip()

    # 🔹 현재 카테고리의 최상위 찾기
    root = category
    while root.parent:
        root = root.parent

    # 🔹 1차 카테고리
    categories = Category.objects.filter(parent__isnull=True, is_active=True).order_by(
        "sort_order"
    )

    # 🔹 사이드바 (2차)
    sidebar_categories = root.children.filter(is_active=True).order_by("sort_order")

    # 🔹 현재 카테고리 + 하위 포함
    descendant_ids = category.get_descendant_ids()

    products = Product.objects.filter(
        category_id__in=descendant_ids, is_active=True
    ).select_related("category")

    # 🔹 검색
    if q:
        products = products.filter(
            Q(name__icontains=q) | Q(brand__icontains=q) | Q(serial_number__icontains=q)
        )

    products = products.order_by("-created_at")

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "catalog/product_list.html",
        {
            "category": category,
            "products": page_obj,
            "categories": categories,  # 1차
            "sidebar_categories": sidebar_categories,  # 2차
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


from django.http import JsonResponse
from apps.catalog.models import Product


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
