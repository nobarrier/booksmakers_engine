from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("checkout/", views.checkout, name="checkout"),
    path("complete/<int:order_id>/", views.complete, name="complete"),
]
