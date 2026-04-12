from django.contrib import admin
from .models import (
    Company,
    Partner,
    Product,
    BOM,
    Document,
    DocumentItem,
    BOMGroup,
    BOMLine,
)

admin.site.register(Company)
admin.site.register(Partner)
admin.site.register(Product)
admin.site.register(BOM)
admin.site.register(Document)
admin.site.register(DocumentItem)


class BOMLineInline(admin.TabularInline):
    model = BOMLine
    extra = 0


@admin.register(BOMGroup)
class BOMGroupAdmin(admin.ModelAdmin):
    inlines = [BOMLineInline]
