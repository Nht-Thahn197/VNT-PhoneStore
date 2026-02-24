from products.models import Category
from .cart import Cart

def categories_processor(request):
    return {
        'categories': Category.objects.all()
    }

def cart(request):
    return {
        'cart': Cart(request)
    }