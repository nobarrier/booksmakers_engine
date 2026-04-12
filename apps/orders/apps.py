from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.orders"

    def ready(self):
        # ✅ signals 비활성화: 재고 로직은 services/stock_service.py에서만 처리
        return
