from django.conf import settings
from django.db import models

from products.models import Product


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Chờ xử lý"),
        ("confirmed", "Đã xác nhận"),
        ("shipping", "Đang giao"),
        ("completed", "Hoàn thành"),
        ("canceled", "Đã hủy"),
    ]
    PAYMENT_CHOICES = [
        ("cod", "Thanh toán khi nhận hàng"),
        ("wallet", "Thẻ ATM / Ví điện tử"),
        ("bank", "Chuyển khoản ngân hàng"),
    ]
    DELIVERY_CHOICES = [
        ("delivery", "Giao hàng tận nơi"),
        ("pickup", "Nhận tại cửa hàng"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="orders",
        null=True,
        blank=True,
    )
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)

    delivery_method = models.CharField(max_length=20, choices=DELIVERY_CHOICES, default="delivery")
    city = models.CharField(max_length=100, blank=True)
    ward = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=255, blank=True)
    delivery_time = models.CharField(max_length=100, blank=True)
    note = models.TextField(blank=True)
    invoice_required = models.BooleanField(default=False)

    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default="cod")
    coupon_code = models.CharField(max_length=50, blank=True)

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.full_name}"

    @property
    def address_display(self):
        parts = [self.address, self.ward, self.city]
        return ", ".join([part for part in parts if part])


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="order_items")
    product_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order_id} - {self.product_name} x{self.quantity}"
