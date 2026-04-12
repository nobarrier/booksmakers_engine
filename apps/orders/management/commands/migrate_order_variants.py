from django.core.management.base import BaseCommand
from apps.orders.models import OrderItem
from apps.catalog.models import ProductVariant


class Command(BaseCommand):
    help = "Migrate existing OrderItem.product to OrderItem.variant"

    def handle(self, *args, **kwargs):

        updated = 0

        for item in OrderItem.objects.all():

            if item.variant is None and item.product:

                try:
                    variant = ProductVariant.objects.get(sku=item.product.serial_number)
                    item.variant = variant
                    item.save()
                    updated += 1

                except ProductVariant.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Variant not found for product {item.product.serial_number}"
                        )
                    )

        self.stdout.write(self.style.SUCCESS(f"{updated}개 OrderItem 이전 완료"))
