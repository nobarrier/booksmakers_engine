from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path
from django.utils.html import format_html

from .models import Order, OrderItem
from .services.stock_service import cancel_order


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    readonly_fields = ("variant", "quantity", "unit_price_snapshot", "fulfillment_type")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "phone",
        "status",
        "total_price",
        "created_at",
        "cancel_button",
    )
    list_filter = ("status",)
    search_fields = ("id", "name", "phone")
    inlines = [OrderItemInline]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:order_id>/cancel/",
                self.admin_site.admin_view(self.cancel_view),
                name="orders_order_cancel",
            ),
        ]
        return custom_urls + urls

    def cancel_button(self, obj: Order):
        # ✅ PAID인 주문만 취소 가능(재고복원)
        if obj.status != "PAID":
            return "-"
        return format_html(
            '<a class="button" href="{}">취소(재고복원)</a>', f"{obj.id}/cancel/"
        )

    cancel_button.short_description = "취소"

    def cancel_view(self, request, order_id: int):
        order = Order.objects.get(id=order_id)

        # ✅ 서비스 레이어 한 곳에서만 재고/원장 처리
        cancel_order(order)

        self.message_user(request, f"주문 #{order.id} 취소 완료 (재고 복원)")
        return redirect("../..")
