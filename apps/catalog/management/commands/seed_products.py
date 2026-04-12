from django.core.management.base import BaseCommand
from apps.catalog.models import Category, Product
import random


class Command(BaseCommand):
    help = "Create dummy products for leaf categories only"

    def handle(self, *args, **kwargs):

        # 🔥 children이 없는 카테고리만 가져오기
        leaf_categories = Category.objects.filter(children__isnull=True)

        if not leaf_categories.exists():
            self.stdout.write(self.style.ERROR("No leaf categories found"))
            return

        for category in leaf_categories:
            for i in range(1, 6):
                Product.objects.create(
                    category=category,
                    name=f"{category.name} 상품 {i}",
                    price=random.randint(10000, 150000),
                    description=f"{category.name} 관련 데모 상품입니다.",
                    is_active=True,
                )

        self.stdout.write(
            self.style.SUCCESS("Leaf dummy products created successfully")
        )
