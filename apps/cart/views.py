from django.shortcuts import render, redirect
from apps.catalog.models import Product


def add_to_cart(request, product_id):
    cart = request.session.get("cart", {})

    if str(product_id) in cart:
        cart[str(product_id)] += 1
    else:
        cart[str(product_id)] = 1

    request.session["cart"] = cart

    return redirect("catalog:home")


def cart_view(request):
    cart = request.session.get("cart", {})
    products = []
    total_price = 0

    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        product.total_quantity = quantity
        product.total_price = product.price * quantity
        total_price += product.total_price
        products.append(product)

    return render(
        request,
        "cart/cart_list.html",
        {
            "products": products,
            "total_price": total_price,
        },
    )


def increase_quantity(request, product_id):
    cart = request.session.get("cart", {})
    if str(product_id) in cart:
        cart[str(product_id)] += 1
        request.session["cart"] = cart
    return redirect("cart:cart_view")


def decrease_quantity(request, product_id):
    cart = request.session.get("cart", {})
    if str(product_id) in cart:
        cart[str(product_id)] -= 1
        if cart[str(product_id)] <= 0:
            del cart[str(product_id)]
        request.session["cart"] = cart
    return redirect("cart:cart_view")


def remove_from_cart(request, product_id):
    cart = request.session.get("cart", {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session["cart"] = cart
    return redirect("cart:cart_view")
