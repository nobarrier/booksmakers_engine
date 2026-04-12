from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError

from .models import Order, OrderItem
from apps.catalog.models import Product, ProductVariant
from .services.stock_service import confirm_order


def _get_default_variant(product: Product) -> ProductVariant:
    """
    옵션 없는 상품/단일 variant 상품 기준:
    - 기본 variant 1개를 가져온다.
    - 프로젝트에 맞게 기준을 하나로 고정해야 함.
    """
    # 1) is_default 필드가 있으면 이게 가장 깔끔
    if hasattr(ProductVariant, "is_default"):
        v = ProductVariant.objects.filter(product=product, is_default=True).first()
        if v:
            return v

    # 2) 없으면 그냥 첫 번째 variant
    v = ProductVariant.objects.filter(product=product).order_by("id").first()
    if not v:
        raise ValidationError(f"ProductVariant가 없습니다: product_id={product.id}")
    return v


def checkout(request):
    cart = request.session.get("cart", {})

    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        address = request.POST.get("address")

        # 주문 생성 (PENDING)
        order = Order.objects.create(
            name=name,
            phone=phone,
            address=address,
            total_price=0,
            status="PENDING",  # Order에 status 필드가 있으면 유지
        )

        total_price = 0

        for product_id, quantity in cart.items():
            product = Product.objects.get(id=product_id)

            variant = _get_default_variant(product)

            # 가격: product.price 쓰던 구조면 그대로, 아니면 variant 가격 쓰도록 조정
            unit_price = product.price
            line_price = unit_price * quantity
            total_price += line_price

            # ✅ 핵심: OrderItem은 variant로 저장
            OrderItem.objects.create(
                order=order,
                variant=variant,
                quantity=quantity,
                unit_price_snapshot=unit_price,  # orders 마이그레이션에 unit_price_snapshot 보임
            )

        order.total_price = total_price
        order.save(update_fields=["total_price"])

        # ✅ 재고 차감: 주문 확정(지금은 결제 없이 바로 확정으로 처리)
        # 결제 붙이면 여기 대신 결제 성공 콜백에서 confirm_order 호출
        confirm_order(order)

        request.session["cart"] = {}

        # ✅ order_id 넘겨서 complete에서 보여줄 수 있게
        return redirect("orders:complete", order_id=order.id)

    return render(request, "orders/checkout.html")


def complete(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "orders/complete.html", {"order": order})
