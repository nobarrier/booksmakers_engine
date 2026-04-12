from django.core.management.base import BaseCommand
from apps.catalog.models import ProductVariant, Inventory, Warehouse


class Command(BaseCommand):
    help = "모든 ProductVariant에 대해 Inventory row를 생성합니다."

    def handle(self, *args, **options):
        warehouse = Warehouse.objects.order_by("id").first()

        if not warehouse:
            self.stdout.write(
                self.style.ERROR("Warehouse가 없습니다. 먼저 창고를 생성하세요.")
            )
            return

        created_count = 0

        for variant in ProductVariant.objects.all():
            obj, created = Inventory.objects.get_or_create(
                warehouse=warehouse,
                variant=variant,
                defaults={"quantity": 0},  # 초기 재고는 0
            )

            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"Inventory 초기화 완료. 생성된 row 수: {created_count}")
        )
