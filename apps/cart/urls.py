from django.urls import path
from . import views

app_name = "cart"
urlpatterns = [
    path("add/<int:product_id>/", views.add_to_cart, name="cart_add"),
    path("increase/<int:product_id>/", views.increase_quantity, name="cart_increase"),
    path("decrease/<int:product_id>/", views.decrease_quantity, name="cart_decrease"),
    path("remove/<int:product_id>/", views.remove_from_cart, name="cart_remove"),
    path("", views.cart_view, name="cart_view"),
]
