from django.core.management.base import BaseCommand
import requests
from bs4 import BeautifulSoup
from apps.catalog.models import Product, Category
import time


class Command(BaseCommand):
    help = "Import products from ICBanQ URLs"

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str)

    def handle(self, *args, **options):
        file_path = options["file_path"]

        with open(file_path, "r") as f:
            urls = f.read().splitlines()

        for url in urls:
            self.stdout.write(f"Processing: {url}")

            try:
                response = requests.get(url, timeout=10)
                soup = BeautifulSoup(response.text, "html.parser")

                # 🔹 상품명 (예시 selector — 나중에 실제 구조 맞춰 수정)
                name = soup.find("h3").get_text(strip=True)

                # 🔹 가격 (예시)
                price_tag = soup.find(class_="price")
                price = price_tag.get_text(strip=True) if price_tag else "0"

                # 🔹 기본 카테고리 (임시)
                category, _ = Category.objects.get_or_create(name="임시카테고리")

                # 🔹 상품 생성
                Product.objects.create(
                    name=name, price=price, category=category, source_url=url
                )

                time.sleep(1)  # 서버 부담 방지

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error: {e}"))
