from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Partner(models.Model):
    TYPE_CHOICES = [
        ("supplier", "Supplier"),
        ("customer", "Customer"),
    ]

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    mpn = models.CharField(max_length=100, unique=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_bom_requirements(self, qty):
        requirements = {}
        for bom in self.bom_parent.all():
            requirements[bom.component.name] = bom.quantity * qty
        return requirements

    def generate_purchase_list(self, qty):
        purchase_list = []
        for bom in self.bom_parent.all():
            item = {"product": bom.component.name, "qty": bom.quantity * qty}
            purchase_list.append(item)
        return purchase_list

    def create_purchase_order(self, company, partner, qty):
        # 1. 발주서 생성
        doc = Document.objects.create(doc_type="PO", company=company, partner=partner)

        # 2. BOM 기준으로 품목 추가
        for bom in self.bom_parent.all():
            DocumentItem.objects.create(
                document=doc, product=bom.component, qty=bom.quantity * qty, price=0
            )

        return doc


class BOMGroup(models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class BOM(models.Model):
    group = models.ForeignKey(
        BOMGroup,
        on_delete=models.CASCADE,
        related_name="boms",
        null=True,  # 추가
        blank=True,  # 추가
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="bom_parent"
    )
    component = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="bom_component"
    )
    quantity = models.FloatField()

    def __str__(self):
        return f"[{self.group}] {self.product} -> {self.component} ({self.quantity})"


class Document(models.Model):
    DOC_TYPE = [
        ("PR", "Purchase Requisition"),
        ("PO", "Purchase Order"),
        ("QUOTE", "Quotation"),
    ]

    doc_type = models.CharField(max_length=20, choices=DOC_TYPE)

    doc_no = models.CharField(max_length=50, blank=True)
    q_code = models.CharField(max_length=50, blank=True)

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    partner = models.ForeignKey(
        Partner, on_delete=models.CASCADE, null=True, blank=True
    )

    date = models.DateField(null=True, blank=True)
    usage = models.CharField(max_length=200, blank=True)

    total_amount = models.FloatField(default=0)
    remark = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.doc_no if self.doc_no else f"{self.doc_type} - {self.id}"


class DocumentItem(models.Model):
    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name="items"
    )

    row_no = models.IntegerField(null=True, blank=True)

    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, blank=True
    )

    name = models.CharField(max_length=200, blank=True)
    spec = models.CharField(max_length=200, blank=True)
    unit = models.CharField(max_length=50, blank=True)

    qty = models.FloatField(null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    amount = models.FloatField(null=True, blank=True)

    remark = models.TextField(blank=True)


class BOMLine(models.Model):
    group = models.ForeignKey(BOMGroup, on_delete=models.CASCADE)

    row_no = models.IntegerField()
    mpn = models.CharField(max_length=100, blank=True)

    category = models.CharField(max_length=100, blank=True)
    maker = models.CharField(max_length=100, blank=True)

    item_name = models.CharField(max_length=200)
    spec = models.CharField(max_length=200, blank=True)
    unit = models.CharField(max_length=50, blank=True)

    qty = models.FloatField(null=True, blank=True)
    unit_price = models.FloatField(null=True, blank=True)
    amount = models.FloatField(null=True, blank=True)
    supply_amount = models.FloatField(null=True, blank=True)

    supplier = models.CharField(max_length=100, blank=True)

    draft = models.BooleanField(default=False)
    rfq = models.BooleanField(default=False)
    quoted = models.BooleanField(default=False)
    confirmed = models.BooleanField(default=False)
    ordered = models.BooleanField(default=False)
    delivered = models.BooleanField(default=False)

    remark = models.TextField(blank=True)

    def __str__(self):
        return f"{self.group.name} - {self.row_no}"
