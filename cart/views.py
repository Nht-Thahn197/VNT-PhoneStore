from django.shortcuts import render, redirect
from .cart import Cart

def add_to_cart(request, product_id):
    cart = Cart(request)
    cart.add(product_id)
    return redirect('cart_detail')

def cart_detail(request):
    cart = Cart(request)
    products = cart.get_products()

    return render(request, 'cart/cart_detail.html', {
        'products': products,
        'cart': cart
    })