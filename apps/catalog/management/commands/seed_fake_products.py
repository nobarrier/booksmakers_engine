from django.core.management.base import BaseCommand
from apps.catalog.models import Product, Category
from django.utils.text import slugify
import random


class Command(BaseCommand):
    help = "Generate fake products for UI testing"

    def handle(self, *args, **kwargs):

        # 말단 카테고리(leaf)만 선택
        categories = Category.objects.filter(children__isnull=True)

        if not categories.exists():
            self.stdout.write(self.style.ERROR("No leaf categories found"))
            return

        for i in range(50):
            category = random.choice(categories)

            serial = f"BK-TEST-{1000 + i}"

            Product.objects.create(
                serial_number=serial,
                slug=slugify(serial, allow_unicode=True),
                category=category,
                name=f"테스트 상품 {i + 1}",
                brand="BOOKS",
                price=random.randint(1000, 20000),
                sale_price=None,
                stock=random.randint(1, 50),
                short_description="테스트 상품입니다.",
                detail_html="<p>상세 설명 테스트 데이터입니다.</p>",
                is_active=True,
            )

        self.stdout.write(self.style.SUCCESS("50 products created."))
