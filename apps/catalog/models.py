import os
from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.db.models import Sum


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(allow_unicode=True)

    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.CASCADE,
    )

    class Meta:
        unique_together = ("parent", "slug")

    def save(self, *args, **kwargs):
        self.clean()

        if not self.slug:
            base_slug = slugify(self.name, allow_unicode=True)

            if self.parent:
                base_slug = f"{self.parent.slug}-{base_slug}"

            slug_candidate = base_slug
            counter = 2

            while (
                Category.objects.filter(slug=slug_candidate)
                .exclude(pk=self.pk)
                .exists()
            ):
                slug_candidate = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug_candidate

        super().save(*args, **kwargs)

    def get_ancestors(self):
        nodes = []
        cur = self.parent
        while cur:
            nodes.append(cur)
            cur = cur.parent
        return list(reversed(nodes))

    def get_descendant_ids(self):
        ids = []
        stack = [self]
        while stack:
            node = stack.pop()
            ids.append(node.id)
            stack.extend(list(node.children.all()))
        return ids

    def get_depth(self):
        depth = 0
        parent = self.parent
        while parent:
            depth += 1
            parent = parent.parent
        return depth

    def __str__(self):
        return "—" * self.get_depth() + self.name

    def clean(self):
        if self.parent and self.parent.get_depth() >= 4:
            raise ValidationError("카테고리는 최대 5단계까지만 허용됩니다.")


def product_image_path(instance, filename):
    serial = instance.product.serial_number
    parts = serial.split("-")
    category_code = parts[1] if len(parts) > 1 else "ETC"
    return f"product_images/{category_code}/{serial}/{filename}"


class Mall(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    product_code = models.CharField(max_length=50, blank=True)

    # 🔥 외부 API 연동용 ID
    external_id = models.CharField(
        max_length=120,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
    )

    # 🔥 공급처 정보
    source_supplier = models.CharField(max_length=50, blank=True, db_index=True)

    source_category_path = models.JSONField(blank=True, null=True)

    # 🔥 가격비교 핵심 키
    manufacturer = models.CharField(max_length=200, blank=True, db_index=True)

    mpn = models.CharField(max_length=200, blank=True, db_index=True)

    # 🔥 supplier part number
    serial_number = models.CharField(max_length=120, unique=True)

    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    mall = models.ForeignKey("Mall", null=True, blank=True, on_delete=models.SET_NULL)

    category = models.ForeignKey(
        Category,
        related_name="products",
        on_delete=models.PROTECT,
    )

    name = models.CharField(max_length=300, db_index=True)

    brand = models.CharField(max_length=120, blank=True, db_index=True)

    price = models.IntegerField(db_index=True)

    sale_price = models.IntegerField(blank=True, null=True)

    short_description = models.CharField(max_length=500, blank=True)

    detail_html = models.TextField(blank=True)

    source_url = models.URLField(blank=True)

    image_url = models.URLField(blank=True)

    is_active = models.BooleanField(default=True)

    is_reviewed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["category"]),
            models.Index(fields=["price"]),
            models.Index(fields=["external_id"]),
            models.Index(fields=["manufacturer", "mpn"]),  # 🔥 MPN 통합 핵심
        ]

    def __str__(self):
        return self.name

    @property
    def lowest_price(self):
        prices = self.supplier_products.values_list("price", flat=True)

        if prices:
            return min(prices)

        return None

    canonical = models.ForeignKey(
        "CanonicalProduct",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="products",
    )


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to=product_image_path)
    is_thumbnail = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.product.name} Image"


class ProductVariant(models.Model):
    product = models.ForeignKey(
        Product,
        related_name="variants",
        on_delete=models.CASCADE,
    )

    sku = models.CharField(max_length=100, unique=True)

    cost_price = models.IntegerField(default=0)
    selling_price = models.IntegerField()

    spec_json = models.JSONField(blank=True, null=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["sku"]),
        ]

    def __str__(self):
        return self.sku

    @property
    def current_stock(self):
        total = self.ledger_entries.aggregate(total=Sum("qty_change"))["total"]
        return total or 0


class Warehouse(models.Model):
    code = models.CharField(max_length=50, unique=True, default="YYCOM_MAIN")
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class StockLedger(models.Model):
    TYPE_CHOICES = [
        ("PURCHASE_IN", "Purchase In"),
        ("SALE_OUT", "Sale Out"),
        ("ADJUST", "Adjust"),
        ("RESERVE", "Reserve"),
        ("RELEASE", "Release"),
        ("RETURN", "Return"),
    ]

    warehouse = models.ForeignKey(
        Warehouse,
        related_name="ledger_entries",
        on_delete=models.CASCADE,
    )

    variant = models.ForeignKey(
        ProductVariant,
        related_name="ledger_entries",
        on_delete=models.CASCADE,
    )

    qty_change = models.IntegerField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    reference_type = models.CharField(max_length=50, blank=True)
    reference_id = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.variant.sku} ({self.qty_change})"


class Inventory(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["warehouse", "variant"],
                name="uniq_inventory_warehouse_variant",
            )
        ]


class CategoryRule(models.Model):
    LEVEL_CHOICES = (
        (1, "1차"),
        (2, "2차"),
        (3, "3차"),
    )

    keyword = models.CharField(max_length=100)
    category_name = models.CharField(max_length=100)
    level = models.IntegerField(choices=LEVEL_CHOICES)

    priority = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.keyword} → {self.category_name} ({self.level})"


class Supplier(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    website = models.URLField(blank=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class SupplierProduct(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="supplier_products"
    )

    supplier_part_number = models.CharField(max_length=200)

    price = models.FloatField()
    stock = models.IntegerField(default=0)

    url = models.URLField()

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("supplier", "supplier_part_number")

        indexes = [
            models.Index(fields=["product"]),
            models.Index(fields=["price"]),
            models.Index(fields=["supplier"]),
        ]


class CanonicalProduct(models.Model):
    manufacturer = models.CharField(max_length=200, db_index=True)

    mpn = models.CharField(max_length=200, db_index=True)

    name = models.CharField(max_length=300)

    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, null=True, blank=True
    )

    image_url = models.URLField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("manufacturer", "mpn")

    def __str__(self):
        return f"{self.manufacturer} {self.mpn}"
