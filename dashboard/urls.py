from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.admin_login, name="admin_login"),
    path("", views.dashboard_home, name="dashboard_home"),
    path("categories/", views.category_list, name="category_list"),
    path("categories/create/", views.category_create, name="category_create"),
    path("categories/delete/<int:id>/", views.category_delete, name="category_delete"),
    path("brands/", views.brand_list, name="brand_list"),
    path("brands/create/", views.brand_create, name="brand_create"),
    path("brands/delete/<int:id>/", views.brand_delete, name="brand_delete"),
    path("products/", views.product_list, name="product_list"),
    path("products/create/", views.product_create, name="product_create"),
    path("products/delete/<int:id>/", views.product_delete, name="product_delete"),
    path("customers/", views.customer_list, name="customer_list"),
]
