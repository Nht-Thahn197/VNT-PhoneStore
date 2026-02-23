from django.shortcuts import render
from products.models import Product
from django.shortcuts import get_object_or_404

def home(request):
    products = Product.objects.filter(is_active=True, is_featured=True)
    return render(request, 'core/home.html', {'products': products})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, 'core/product_detail.html', {'product': product})