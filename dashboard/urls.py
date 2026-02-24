from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.admin_login, name="admin_login"),
    path("", views.dashboard_home, name="dashboard_home"),
    path("categories/", views.category_list, name="category_list"),
    path("categories/create/", views.category_create, name="category_create"),
    path("categories/delete/<int:id>/", views.category_delete, name="category_delete"),
]