import csv
import os

from django import forms
from django.contrib import admin
from django.shortcuts import render, redirect
from django.urls import path
from django.utils.text import slugify

from .models import (
    Product,
    Category,
    CategoryRule,
    ProductImage,
    ProductVariant,
    Warehouse,
    Inventory,
    StockLedger,
)


class CsvImportForm(forms.Form):
    csv_file = forms.FileField()


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "price", "brand", "is_active")
    list_filter = ("is_active", "category", "brand")
    search_fields = ("name", "serial_number", "mpn", "manufacturer")
    list_select_related = ("category",)
    inlines = [ProductImageInline]

    change_list_template = "admin/products_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("import-csv/", self.import_csv),
        ]
        return custom_urls + urls

    def _resolve_image_path(self, image_base: str):
        image_base = (image_base or "").strip()

        if not image_base:
            return None

        candidates = [
            f"{image_base}.jpg",
            f"{image_base}.png",
            f"{image_base}.jpeg",
        ]

        for filename in candidates:
            return os.path.join("product_images", filename)

        return None

    def import_csv(self, request):

        if request.method == "POST":

            csv_file = request.FILES["csv_file"]

            decoded_file = csv_file.read().decode("utf-8-sig").splitlines()

            reader = csv.DictReader(decoded_file)

            for row in reader:

                category_name = (row.get("category") or "").strip()

                if not category_name:
                    continue

                category, _ = Category.objects.get_or_create(
                    name=category_name,
                    defaults={"slug": slugify(category_name, allow_unicode=True)},
                )

                name = (row.get("name") or "").strip()

                if not name:
                    continue

                product, _created = Product.objects.update_or_create(
                    name=name,
                    defaults={
                        "category": category,
                        "price": int(row.get("price") or 0),
                        "detail_html": row.get("description", ""),
                        "is_active": True,
                    },
                )

                image_base = (row.get("product_image_name") or "").strip()

                image_path = self._resolve_image_path(image_base)

                if image_path:
                    ProductImage.objects.filter(product=product).delete()

                    ProductImage.objects.create(
                        product=product,
                        image=image_path,
                    )

            self.message_user(request, "CSV 업로드 완료")

            return redirect("..")

        form = CsvImportForm()

        return render(request, "admin/csv_form.html", {"form": form})


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "parent",
        "sort_order",
        "is_active",
        "created_at",
    )

    list_filter = ("is_active", "parent")

    search_fields = ("name", "slug")

    ordering = ("parent__id", "sort_order", "name")

    prepopulated_fields = {"slug": ("name",)}


@admin.register(CategoryRule)
class CategoryRuleAdmin(admin.ModelAdmin):
    list_display = ("keyword", "category_name", "level", "priority")

    list_filter = ("level",)

    search_fields = ("keyword", "category_name")

    ordering = ("level", "priority", "keyword")


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("id", "sku", "product", "selling_price", "is_active")

    list_filter = ("is_active",)

    search_fields = ("sku", "product__name")

    list_select_related = ("product",)


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name", "is_active", "created_at")

    list_filter = ("is_active",)

    search_fields = ("code", "name")


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ("id", "warehouse", "variant", "quantity")

    list_filter = ("warehouse",)

    search_fields = ("variant__sku", "warehouse__name", "warehouse__code")

    list_select_related = ("warehouse", "variant")


@admin.register(StockLedger)
class StockLedgerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "warehouse",
        "variant",
        "qty_change",
        "type",
        "reference_type",
        "reference_id",
        "created_at",
    )

    list_filter = ("warehouse", "type", "reference_type")

    search_fields = ("variant__sku", "reference_id")

    list_select_related = ("warehouse", "variant")
