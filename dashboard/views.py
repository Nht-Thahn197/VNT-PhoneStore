from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.text import slugify

from accounts.models import User
from products.models import Category, Brand, Product

def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("dashboard_home")

    next_url = request.GET.get("next") or request.POST.get("next") or ""
    error = None
    identifier = ""

    if request.method == "POST":
        identifier = request.POST.get("identifier", "").strip()
        password = request.POST.get("password", "")
        user = None

        if identifier:
            lookup_phone = identifier
            if "@" not in identifier:
                normalized = "".join(ch for ch in identifier if ch.isdigit() or ch == "+")
                if normalized:
                    lookup_phone = normalized
            user_model = get_user_model()
            candidate = user_model.objects.filter(
                Q(email__iexact=identifier) | Q(phone=lookup_phone) | Q(username__iexact=identifier)
            ).first()
            if candidate:
                user = authenticate(request, username=candidate.username, password=password)

        if user is None and identifier:
            user = authenticate(request, username=identifier, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            return redirect(next_url or "dashboard_home")

        error = "Thông tin đăng nhập không đúng hoặc tài khoản không có quyền quản trị."

    return render(
        request,
        "dashboard/login.html",
        {"error": error, "next": next_url, "identifier": identifier},
    )


def admin_logout(request):
    logout(request)
    return redirect("admin_login")

def staff_required(view_func):
    return user_passes_test(lambda u: u.is_staff, login_url="admin_login")(view_func)

@staff_required
def dashboard_home(request):
    return render(request, "dashboard/home.html")

@staff_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, "dashboard/category_list.html", {"categories": categories})


@staff_required
def category_create(request):
    if request.method == "POST":
        name = request.POST.get("name")
        slug = slugify(name)
        if name:
            Category.objects.create(name=name, slug=slug)
        return redirect("category_list")

    return render(request, "dashboard/category_form.html")


@staff_required
def category_edit(request, id):
    category = get_object_or_404(Category, id=id)

    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            category.name = name
            category.slug = slugify(name)
            category.save()
            return redirect("category_list")

    return render(
        request,
        "dashboard/category_form.html",
        {"category": category, "is_edit": True},
    )


@staff_required
def category_delete(request, id):
    category = get_object_or_404(Category, id=id)
    category.delete()
    return redirect("category_list")


@staff_required
def brand_list(request):
    brands = Brand.objects.select_related("category").all()
    categories = Category.objects.all()
    return render(request, "dashboard/brand_list.html", {"brands": brands, "categories": categories})


@staff_required
def brand_create(request):
    categories = Category.objects.all()
    if request.method == "POST":
        name = request.POST.get("name")
        category_id = request.POST.get("category_id")
        if name and category_id:
            category = get_object_or_404(Category, id=category_id)
            Brand.objects.create(name=name, category=category)
            return redirect("brand_list")

    return render(request, "dashboard/brand_form.html", {"categories": categories})


@staff_required
def brand_edit(request, id):
    brand = get_object_or_404(Brand, id=id)
    categories = Category.objects.all()

    if request.method == "POST":
        name = request.POST.get("name")
        category_id = request.POST.get("category_id")
        if name and category_id:
            category = get_object_or_404(Category, id=category_id)
            brand.name = name
            brand.category = category
            brand.save()
            return redirect("brand_list")

    return render(
        request,
        "dashboard/brand_form.html",
        {"categories": categories, "brand": brand, "is_edit": True},
    )


@staff_required
def brand_delete(request, id):
    brand = get_object_or_404(Brand, id=id)
    brand.delete()
    return redirect("brand_list")


@staff_required
def product_list(request):
    products = Product.objects.select_related("brand", "category").all()
    categories = Category.objects.all()
    brands = Brand.objects.all()
    return render(
        request,
        "dashboard/product_list.html",
        {"products": products, "categories": categories, "brands": brands},
    )


@staff_required
def product_create(request):
    categories = Category.objects.all()
    brands = Brand.objects.all()

    if request.method == "POST":
        name = request.POST.get("name")
        slug = request.POST.get("slug") or slugify(name or "")
        category_id = request.POST.get("category_id")
        brand_id = request.POST.get("brand_id")
        price = request.POST.get("price") or 0
        old_price = request.POST.get("old_price") or None
        stock = request.POST.get("stock") or 0
        description = request.POST.get("description") or ""
        specifications = request.POST.get("specifications") or ""
        is_active = request.POST.get("is_active") == "on"
        is_featured = request.POST.get("is_featured") == "on"
        image = request.FILES.get("image")

        if name and category_id and brand_id and image:
            category = get_object_or_404(Category, id=category_id)
            brand = get_object_or_404(Brand, id=brand_id)
            Product.objects.create(
                name=name,
                slug=slug,
                category=category,
                brand=brand,
                price=price,
                old_price=old_price or None,
                stock=stock,
                description=description,
                specifications=specifications,
                image=image,
                is_active=is_active,
                is_featured=is_featured,
            )
            return redirect("product_list")

    return render(
        request,
        "dashboard/product_form.html",
        {"categories": categories, "brands": brands},
    )


@staff_required
def product_edit(request, id):
    product = get_object_or_404(Product, id=id)
    categories = Category.objects.all()
    brands = Brand.objects.all()

    if request.method == "POST":
        name = request.POST.get("name")
        slug = request.POST.get("slug") or slugify(name or "")
        category_id = request.POST.get("category_id")
        brand_id = request.POST.get("brand_id")
        price = request.POST.get("price") or 0
        old_price = request.POST.get("old_price") or None
        stock = request.POST.get("stock") or 0
        description = request.POST.get("description") or ""
        specifications = request.POST.get("specifications") or ""
        is_active = request.POST.get("is_active") == "on"
        is_featured = request.POST.get("is_featured") == "on"
        image = request.FILES.get("image")

        if name and category_id and brand_id:
            category = get_object_or_404(Category, id=category_id)
            brand = get_object_or_404(Brand, id=brand_id)
            product.name = name
            product.slug = slug
            product.category = category
            product.brand = brand
            product.price = price
            product.old_price = old_price or None
            product.stock = stock
            product.description = description
            product.specifications = specifications
            product.is_active = is_active
            product.is_featured = is_featured
            if image:
                product.image = image
            product.save()
            return redirect("product_list")

    return render(
        request,
        "dashboard/product_form.html",
        {"categories": categories, "brands": brands, "product": product, "is_edit": True},
    )


@staff_required
def product_delete(request, id):
    product = get_object_or_404(Product, id=id)
    product.delete()
    return redirect("product_list")


@staff_required
def customer_list(request):
    customers = User.objects.filter(role="customer").order_by("-date_joined")
    return render(request, "dashboard/customer_list.html", {"customers": customers})


@staff_required
def customer_detail(request, id):
    customer = get_object_or_404(User, id=id, role="customer")
    return render(request, "dashboard/customer_detail.html", {"customer": customer})
