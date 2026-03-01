from decimal import Decimal
from urllib.parse import urlencode, quote

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from orders.models import Order, OrderItem
from products.models import Product, Category

from .cart import Cart

def home(request):
    products = Product.objects.filter(is_active=True, is_featured=True)
    return render(request, 'core/home.html', {'products': products})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, 'core/product_detail.html', {'product': product})

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, is_active=True)

    return render(request, 'core/category_detail.html', {
        'category': category,
        'products': products
    })

def search(request):
    query = request.GET.get('q')
    products = []

    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query),
            is_active=True
        )

    return render(request, 'core/search.html', {
        'products': products,
        'query': query
    })


def _get_cart_totals(cart):
    subtotal = cart.get_total_price() or Decimal("0")
    discount = Decimal("0")
    shipping = Decimal("0")
    total = subtotal - discount + shipping
    if total < 0:
        total = Decimal("0")
    return subtotal, discount, shipping, total


def _build_address_display(data):
    parts = [data.get("address"), data.get("ward_name") or data.get("ward"), data.get("city_name") or data.get("city")]
    return ", ".join([part for part in parts if part])


def _build_vietqr_url(total):
    bank_id = getattr(settings, "VIETQR_BANK_ID", "")
    account_no = getattr(settings, "VIETQR_ACCOUNT_NO", "")
    account_name = getattr(settings, "VIETQR_ACCOUNT_NAME", "")
    template = getattr(settings, "VIETQR_TEMPLATE", "compact2") or "compact2"
    if not (bank_id and account_no and account_name):
        return ""

    amount = int(total or 0)
    params = {"amount": amount, "accountName": account_name}
    add_info = getattr(settings, "VIETQR_ADD_INFO", "")
    if add_info:
        params["addInfo"] = add_info
    query = urlencode(params, quote_via=quote)
    return f"https://img.vietqr.io/image/{bank_id}-{account_no}-{template}.png?{query}"


@login_required
def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart.html', {'cart': cart})


@login_required
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.add(product)
    return redirect('cart')


@login_required
def cart_decrease(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.decrease(product)
    return redirect('cart')


@login_required
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart')


@login_required
def checkout_info(request):
    cart = Cart(request)
    if cart.get_total_quantity() <= 0:
        return redirect("cart")

    errors = {}
    session_data = request.session.get("checkout_info")
    if not isinstance(session_data, dict):
        session_data = {}
    form_data = {
        "full_name": request.user.get_full_name() or request.user.username,
        "phone": getattr(request.user, "phone", "") or "",
        "email": request.user.email or "",
        "delivery_method": "delivery",
        "city": "",
        "city_name": "",
        "ward": "",
        "ward_name": "",
        "address": "",
        "delivery_time": "",
        "note": "",
        "invoice_required": False,
    }
    form_data.update(session_data)

    if request.method == "POST":
        form_data = {
            "full_name": request.POST.get("full_name", "").strip(),
            "phone": request.POST.get("phone", "").strip(),
            "email": request.POST.get("email", "").strip(),
            "delivery_method": request.POST.get("delivery", "delivery").strip() or "delivery",
            "city": request.POST.get("city", "").strip(),
            "city_name": request.POST.get("city_name", "").strip(),
            "ward": request.POST.get("ward", "").strip(),
            "ward_name": request.POST.get("ward_name", "").strip(),
            "address": request.POST.get("address", "").strip(),
            "delivery_time": request.POST.get("delivery_time", "").strip(),
            "note": request.POST.get("note", "").strip(),
            "invoice_required": request.POST.get("invoice") == "yes",
        }

        if form_data["delivery_method"] == "pickup":
            form_data["city"] = ""
            form_data["city_name"] = ""
            form_data["ward"] = ""
            form_data["ward_name"] = ""
            form_data["address"] = ""

        if not form_data["full_name"]:
            errors["full_name"] = "Vui lòng nhập họ và tên."
        if not form_data["phone"]:
            errors["phone"] = "Vui lòng nhập số điện thoại."
        if form_data["delivery_method"] == "delivery":
            if not form_data["city"]:
                errors["city"] = "Vui lòng chọn Tỉnh/Thành phố."
            if not form_data["ward"]:
                errors["ward"] = "Vui lòng chọn Phường/Xã."
            if not form_data["address"]:
                errors["address"] = "Vui lòng nhập địa chỉ nhận hàng."

        if not errors:
            request.session["checkout_info"] = form_data
            request.session.modified = True
            return redirect("checkout_payment")

    subtotal, discount, shipping, total = _get_cart_totals(cart)

    context = {
        "cart": cart,
        "subtotal": subtotal,
        "discount": discount,
        "shipping": shipping,
        "total": total,
        "today": timezone.localdate(),
        "form": form_data,
        "errors": errors,
    }
    return render(request, "core/checkout_info.html", context)


@login_required
def checkout_payment(request):
    cart = Cart(request)
    if cart.get_total_quantity() <= 0:
        return redirect("cart")

    checkout_info = request.session.get("checkout_info")
    if not isinstance(checkout_info, dict):
        checkout_info = None
    if not checkout_info:
        return redirect("checkout_info")

    subtotal, discount, shipping, total = _get_cart_totals(cart)
    bank_qr_url = _build_vietqr_url(total)
    errors = {}
    payment_method = "cod"
    coupon_code = ""

    if request.method == "POST":
        payment_method = request.POST.get("payment_method", "cod").strip() or "cod"
        coupon_code = request.POST.get("coupon", "").strip()

        if payment_method not in {"cod", "wallet", "bank"}:
            errors["payment_method"] = "Vui lòng chọn phương thức thanh toán hợp lệ."

        for item in cart:
            if item["product"].stock < item["quantity"]:
                errors["stock"] = f"Sản phẩm {item['product'].name} không đủ số lượng."
                break

        if not errors:
            with transaction.atomic():
                order = Order.objects.create(
                    user=request.user,
                    full_name=checkout_info.get("full_name") or request.user.get_full_name() or request.user.username,
                    phone=checkout_info.get("phone") or "",
                    email=checkout_info.get("email") or "",
                    delivery_method=checkout_info.get("delivery_method") or "delivery",
                    city=checkout_info.get("city_name") or checkout_info.get("city") or "",
                    ward=checkout_info.get("ward_name") or checkout_info.get("ward") or "",
                    address=checkout_info.get("address") or "",
                    delivery_time=checkout_info.get("delivery_time") or "",
                    note=checkout_info.get("note") or "",
                    invoice_required=bool(checkout_info.get("invoice_required")),
                    payment_method=payment_method,
                    coupon_code=coupon_code,
                    subtotal=subtotal,
                    discount=discount,
                    shipping=shipping,
                    total=total,
                    status="pending",
                )

                for item in cart:
                    product = item["product"]
                    quantity = item["quantity"]
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        product_name=product.name,
                        price=product.price,
                        quantity=quantity,
                        total=product.price * quantity,
                    )
                    product.stock = max(product.stock - quantity, 0)
                    product.save(update_fields=["stock"])

                cart.clear()
                request.session.pop("checkout_info", None)
                request.session.modified = True

            return redirect("checkout_success", order_id=order.id)

    context = {
        "cart": cart,
        "subtotal": subtotal,
        "discount": discount,
        "shipping": shipping,
        "total": total,
        "today": timezone.localdate(),
        "checkout": checkout_info,
        "address_display": _build_address_display(checkout_info),
        "errors": errors,
        "payment_method": payment_method,
        "coupon_code": coupon_code,
        "bank_qr_url": bank_qr_url,
    }
    return render(request, "core/checkout_payment.html", context)


@login_required
def checkout_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "core/checkout_success.html", {"order": order, "items": order.items.all()})
