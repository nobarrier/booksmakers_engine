from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.catalog.models import Warehouse, StockLedger
from apps.orders.models import Order


def _get_main_warehouse():
    # code 필드 추가했으니 여기서는 MAIN/YYCOM_MAIN 중 하나를 우선 찾고, 없으면 첫 창고 사용
    wh = Warehouse.objects.filter(
        is_active=True, code__in=["YYCOM_MAIN", "MAIN"]
    ).first()
    return wh or Warehouse.objects.filter(is_active=True).first()


def _ledger_exists(
    *, warehouse, variant, qty_change, type, reference_type, reference_id
):
    return StockLedger.objects.filter(
        warehouse=warehouse,
        variant=variant,
        qty_change=qty_change,
        type=type,
        reference_type=reference_type,
        reference_id=reference_id,
    ).exists()


def reserve_for_order(order: Order):
    """
    주문이 PENDING일 때 예약(RESERVE) 생성
    """
    wh = _get_main_warehouse()
    if not wh:
        raise RuntimeError("Warehouse가 없습니다. 먼저 창고(YYCOM_MAIN)를 생성하세요.")

    for item in order.items.select_related("variant").all():
        if item.fulfillment_type != "WAREHOUSE":
            continue
        if item.variant is None:
            continue

        qty = item.quantity

        # 이미 예약 기록이 있으면 스킵(중복 방지)
        if _ledger_exists(
            warehouse=wh,
            variant=item.variant,
            qty_change=-qty,
            type="RESERVE",
            reference_type="ORDER_RESERVE",
            reference_id=order.id,
        ):
            continue

        # 재고 부족 체크(선택사항: 부족하면 예약 실패)
        if item.variant.current_stock < qty:
            raise RuntimeError(
                f"재고 부족: {item.variant.sku} (현재 {item.variant.current_stock}, 요청 {qty})"
            )

        StockLedger.objects.create(
            warehouse=wh,
            variant=item.variant,
            qty_change=-qty,
            type="RESERVE",
            reference_type="ORDER_RESERVE",
            reference_id=order.id,
        )


def release_reservation(order: Order, *, reason: str):
    """
    예약 복구(RELEASE)
    reason: ORDER_CANCEL / ORDER_SHIP
    """
    wh = _get_main_warehouse()
    if not wh:
        raise RuntimeError("Warehouse가 없습니다. 먼저 창고(YYCOM_MAIN)를 생성하세요.")

    for item in order.items.select_related("variant").all():
        if item.fulfillment_type != "WAREHOUSE":
            continue
        if item.variant is None:
            continue

        qty = item.quantity

        if _ledger_exists(
            warehouse=wh,
            variant=item.variant,
            qty_change=qty,
            type="RELEASE",
            reference_type=reason,
            reference_id=order.id,
        ):
            continue

        StockLedger.objects.create(
            warehouse=wh,
            variant=item.variant,
            qty_change=qty,
            type="RELEASE",
            reference_type=reason,
            reference_id=order.id,
        )


def mark_sale_out(order: Order):
    """
    발송 기록(SALE_OUT)
    (예약을 RELEASE로 되돌린 뒤, 다시 SALE_OUT을 찍어서 발송 이력 남김)
    """
    wh = _get_main_warehouse()
    if not wh:
        raise RuntimeError("Warehouse가 없습니다. 먼저 창고(YYCOM_MAIN)를 생성하세요.")

    for item in order.items.select_related("variant").all():
        if item.fulfillment_type != "WAREHOUSE":
            continue
        if item.variant is None:
            continue

        qty = item.quantity

        if _ledger_exists(
            warehouse=wh,
            variant=item.variant,
            qty_change=-qty,
            type="SALE_OUT",
            reference_type="ORDER_SHIP",
            reference_id=order.id,
        ):
            continue

        StockLedger.objects.create(
            warehouse=wh,
            variant=item.variant,
            qty_change=-qty,
            type="SALE_OUT",
            reference_type="ORDER_SHIP",
            reference_id=order.id,
        )


@receiver(post_save, sender=Order)
def order_status_flow(sender, instance: Order, created: bool, **kwargs):
    """
    주문 상태 변화에 따라 재고 원장 자동 기록
    - created(PENDING): 예약
    - CANCELLED: 예약 복구
    - SHIPPED: RELEASE(+qty) 후 SALE_OUT(-qty)
    """
    # DB에서 이전 상태 조회 (created면 이전 없음)
    old_status = None
    if not created:
        old_status = (
            Order.objects.filter(pk=instance.pk)
            .values_list("status", flat=True)
            .first()
        )

    # created 시점: PENDING이면 예약
    if created and instance.status == "PENDING":
        with transaction.atomic():
            reserve_for_order(instance)
        return

    # 상태 변화가 없으면 종료
    if old_status == instance.status:
        return

    # 취소: 예약 복구
    if instance.status == "CANCELLED":
        with transaction.atomic():
            release_reservation(instance, reason="ORDER_CANCEL")
        return

    # 발송: 예약을 RELEASE로 되돌리고 SALE_OUT으로 발송 이력 남김
    if instance.status == "SHIPPED":
        with transaction.atomic():
            release_reservation(instance, reason="ORDER_SHIP")
            mark_sale_out(instance)
        return
