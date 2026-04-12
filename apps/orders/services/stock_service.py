from django.db import transaction
from django.db.models import F
from django.core.exceptions import ValidationError

from apps.catalog.models import Inventory, StockLedger, Warehouse


def _get_default_warehouse():
    """
    단일창고 운영:
    - code가 YYCOM_MAIN/MAIN 중 하나면 우선 선택
    - 없으면 가장 첫 창고 사용
    """
    wh = (
        Warehouse.objects.filter(code__in=["YYCOM_MAIN", "MAIN"]).order_by("id").first()
    )
    if wh:
        return wh

    wh = Warehouse.objects.order_by("id").first()
    if not wh:
        raise ValidationError("Warehouse가 없습니다. 먼저 창고를 1개 생성하세요.")
    return wh


@transaction.atomic
def confirm_order(order):
    """
    주문 확정(PENDING -> PAID)
    - Inventory 차감
    - StockLedger 기록: qty_change = -수량, type=SALE_OUT
    - order.status = PAID
    """
    print("🔥 confirm_order 실행됨:", order.id)

    if order.status in ("PAID", "CANCELLED"):
        raise ValidationError("이미 처리된 주문입니다.")

    wh = _get_default_warehouse()

    for item in order.items.select_related("variant"):
        if not item.variant:
            raise ValidationError("주문 아이템에 variant가 없습니다.")

        inv = (
            Inventory.objects.select_for_update()
            .filter(warehouse=wh, variant=item.variant)
            .first()
        )
        if not inv:
            raise ValidationError(
                f"Inventory row가 없습니다: warehouse={wh.id}, variant={item.variant_id}"
            )

        if inv.quantity < item.quantity:
            raise ValidationError(f"재고 부족: {item.variant.sku}")

        # 재고 차감
        inv.quantity = F("quantity") - item.quantity
        inv.save(update_fields=["quantity"])

        # 원장 기록(출고)
        StockLedger.objects.create(
            warehouse=wh,
            variant=item.variant,
            qty_change=-item.quantity,
            type="SALE_OUT",
            reference_type="order",
            reference_id=order.id,
        )

    order.status = "PAID"
    order.save(update_fields=["status"])


@transaction.atomic
def cancel_order(order):
    """
    주문 취소(PAID -> CANCELLED)
    - Inventory 복원
    - StockLedger 기록: qty_change = +수량, type=RETURN
    - order.status = CANCELLED
    """
    if order.status != "PAID":
        raise ValidationError("확정된(PAID) 주문만 취소 가능합니다.")

    wh = _get_default_warehouse()

    for item in order.items.select_related("variant"):
        if not item.variant:
            raise ValidationError("주문 아이템에 variant가 없습니다.")

        inv = (
            Inventory.objects.select_for_update()
            .filter(warehouse=wh, variant=item.variant)
            .first()
        )
        if not inv:
            raise ValidationError(
                f"Inventory row가 없습니다: warehouse={wh.id}, variant={item.variant_id}"
            )

        # 재고 복원
        inv.quantity = F("quantity") + item.quantity
        inv.save(update_fields=["quantity"])

        # 원장 기록(반품/복원)
        StockLedger.objects.create(
            warehouse=wh,
            variant=item.variant,
            qty_change=item.quantity,
            type="RETURN",
            reference_type="cancel",
            reference_id=order.id,
        )

    order.status = "CANCELLED"
    order.save(update_fields=["status"])
