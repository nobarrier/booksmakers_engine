from django.core.management.base import BaseCommand
from apps.catalog.models import Category
from django.utils.text import slugify

TOP_LEVEL_CATEGORIES = [
    "아두이노",
    "라즈베리파이",
    "MCU/개발보드",
    "센서",
    "모터/구동부",
    "전원/배터리",
    "통신/네트워크",
    "전자부품",
    "로봇플랫폼",
    "AI/비전",
    "교육/키트",
    "공구/계측",
    "출판/도서",
]


class Command(BaseCommand):
    help = "Seed only top-level categories safely"

    def handle(self, *args, **kwargs):
        self.stdout.write("\n===== TOP CATEGORY SEED START =====\n")

        for order, name in enumerate(TOP_LEVEL_CATEGORIES, start=1):
            Category.objects.update_or_create(
                parent=None,
                name=name,
                defaults={
                    "slug": slugify(name, allow_unicode=True),
                    "sort_order": order,
                    "is_active": True,
                },
            )

        self.stdout.write(self.style.SUCCESS("1차 카테고리 정리 완료"))
