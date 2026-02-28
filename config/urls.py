from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.templatetags.static import static as static_url
from django.views.generic.base import RedirectView
from cart.views import add_to_cart, cart_detail
from core import views
from core.views import home
from core.views import home, product_detail
from core.views import home, product_detail, category_detail, search



urlpatterns = [
    path(
        "favicon.ico",
        RedirectView.as_view(url=static_url("tech-one.ico"), permanent=True),
    ),
    path('admin/', admin.site.urls),
    path('account/', include('accounts.urls')),
    path('', home, name='home'),
    path('product/<slug:slug>/', product_detail, name='product_detail'),
    path('search/', search, name='search'),
    path('', cart_detail, name='cart_detail'),
    path('add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('checkout/', views.checkout_info, name='checkout_info'),
    path('checkout/payment/', views.checkout_payment, name='checkout_payment'),
    path('cart/', include('cart.urls')),
    path('cart/', views.cart_detail, name='cart'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/decrease/<int:product_id>/', views.cart_decrease, name='cart_decrease'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path("dashboard/", include("dashboard.urls")),
    path('<slug:slug>/', category_detail, name='category_detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
