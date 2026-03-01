from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    readonly_fields = ("product", "product_name", "price", "quantity", "total")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "phone", "total", "status", "payment_method", "created_at")
    list_filter = ("status", "payment_method", "delivery_method", "created_at")
    search_fields = ("id", "full_name", "phone", "email")
    ordering = ("-created_at",)
    inlines = [OrderItemInline]
