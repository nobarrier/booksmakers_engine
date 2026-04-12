from django.urls import path
from . import views

urlpatterns = [
    path("create-pr/<int:group_id>/", views.create_pr_from_bom_view, name="create_pr"),
    path("create-rfq/<int:group_id>/", views.create_rfq_from_bom_view),
    path("create-po/<int:group_id>/", views.create_po_from_bom_view),
]
