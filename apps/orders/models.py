from django.db import models


class Order(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PAID", "Paid"),
        ("SHIPPED", "Shipped"),
        ("CANCELLED", "Cancelled"),
    ]

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.TextField()

    total_price = models.IntegerField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.name}"


class OrderItem(models.Model):
    FULFILLMENT_CHOICES = [
        ("WAREHOUSE", "Warehouse"),
        ("DROPSHIP", "Dropship"),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")

    variant = models.ForeignKey(
        "catalog.ProductVariant",  # ✅ 문자열 FK로 순환참조 제거
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    quantity = models.IntegerField()
    unit_price_snapshot = models.IntegerField()

    fulfillment_type = models.CharField(
        max_length=20,
        choices=FULFILLMENT_CHOICES,
        default="WAREHOUSE",
    )

    def __str__(self):
        return (
            f"{self.variant.sku} x {self.quantity}"
            if self.variant
            else f"Item x {self.quantity}"
        )
