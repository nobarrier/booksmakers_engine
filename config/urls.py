from django.contrib import admin
from django.urls import include, path
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from erp.views import export_po_view, po_list_view
from erp.views import export_po_view, po_list_view, create_po_view
from erp.views import bom_input_view
from erp.views import upload_bom_view
from erp.views import bom_list_view
from django.views.generic import TemplateView
from django.shortcuts import render


def pay_success(request):
    return render(request, "orders/pay_success.html")


def pay_fail(request):
    return render(request, "orders/pay_fail.html")


urlpatterns = [
    path("", RedirectView.as_view(url="/catalog/", permanent=False)),
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/custom/", include("accounts.urls")),
    path("users/", include("users.urls")),
    path("catalog/", include("apps.catalog.urls")),
    path("cart/", include("apps.cart.urls")),
    path("order/", include("apps.orders.urls")),
    path("export-po/<int:doc_id>/", export_po_view),
    path("po-list/", po_list_view),
    path("create-po/", create_po_view),
    path("bom-input/", bom_input_view),
    path("upload-bom/", upload_bom_view),
    path("bom-list/<int:group_id>/", bom_list_view),
    path("erp/", include("erp.urls")),
    path(
        "company/",
        TemplateView.as_view(template_name="policy/company.html"),
        name="company",
    ),
    path("pay/success/", pay_success, name="pay_success"),
    path("pay/fail/", pay_fail, name="pay_fail"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
