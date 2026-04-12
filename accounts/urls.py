from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup, name="signup"),
    path("mypage/", views.mypage, name="mypage"),
    path("orders/", views.order_history, name="order_history"),
    path("support/", views.support, name="support"),
]
