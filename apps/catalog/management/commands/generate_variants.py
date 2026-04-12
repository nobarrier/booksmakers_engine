from django.core.management.base import BaseCommand
from apps.catalog.models import Product, ProductVariant


class Command(BaseCommand):
    help = "Generate ProductVariant from existing Product data"

    def handle(self, *args, **kwargs):

        created_count = 0

        for p in Product.objects.all():

            # product_code 자동 생성
            if not p.product_code:
                parts = p.serial_number.split("-")
                if len(parts) >= 2:
                    p.product_code = "-".join(parts[:2])
                else:
                    p.product_code = p.serial_number
                p.save()

            # Variant 생성
            if not ProductVariant.objects.filter(sku=p.serial_number).exists():
                ProductVariant.objects.create(
                    product=p,
                    sku=p.serial_number,
                    selling_price=p.sale_price if p.sale_price else p.price,
                    cost_price=0,
                    stock=p.stock,
                )
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f"완료: {created_count}개 생성"))
