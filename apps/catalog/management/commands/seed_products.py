from django.core.management.base import BaseCommand
from apps.catalog.models import Category, Product
from django.utils.text import slugify
import random


class Command(BaseCommand):
    help = "Create dummy products for leaf categories only"

    def handle(self, *args, **kwargs):

        leaf_categories = Category.objects.filter(children__isnull=True)

        if not leaf_categories.exists():
            self.stdout.write(self.style.ERROR("No leaf categories found"))
            return

        for category in leaf_categories:
            for i in range(1, 6):
                serial = f"TEST-{category.id}-{i}"

                Product.objects.create(
                    serial_number=serial,  # 🔥 핵심 추가
                    slug=slugify(serial),
                    category=category,
                    name=f"{category.name} 상품 {i}",
                    price=random.randint(10000, 150000),
                    is_active=True,
                )

        self.stdout.write(
            self.style.SUCCESS("Leaf dummy products created successfully")
        )
