from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.admin_login, name="admin_login"),
    path("logout/", views.admin_logout, name="admin_logout"),
    path("", views.dashboard_home, name="dashboard_home"),
    path("categories/", views.category_list, name="category_list"),
    path("categories/create/", views.category_create, name="category_create"),
    path("categories/edit/<int:id>/", views.category_edit, name="category_edit"),
    path("categories/delete/<int:id>/", views.category_delete, name="category_delete"),
    path("brands/", views.brand_list, name="brand_list"),
    path("brands/create/", views.brand_create, name="brand_create"),
    path("brands/edit/<int:id>/", views.brand_edit, name="brand_edit"),
    path("brands/delete/<int:id>/", views.brand_delete, name="brand_delete"),
    path("products/", views.product_list, name="product_list"),
    path("products/create/", views.product_create, name="product_create"),
    path("products/edit/<int:id>/", views.product_edit, name="product_edit"),
    path("products/delete/<int:id>/", views.product_delete, name="product_delete"),
    path("customers/", views.customer_list, name="customer_list"),
    path("customers/<int:id>/", views.customer_detail, name="customer_detail"),
    path("orders/", views.order_list, name="order_list"),
    path("orders/<int:id>/", views.order_detail, name="order_detail"),
    path("orders/notifications/", views.order_notifications, name="order_notifications"),
]
