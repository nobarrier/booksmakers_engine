from django.shortcuts import render


def login_view(request):
    return render(request, "accounts/login.html")


def signup(request):
    return render(request, "accounts/signup.html")


def mypage(request):
    return render(request, "accounts/mypage.html")


def order_history(request):
    return render(request, "accounts/order_history.html")


def support(request):
    return render(request, "accounts/support.html")
