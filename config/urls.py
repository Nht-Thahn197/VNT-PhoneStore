from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from core.views import home
from core.views import home, product_detail

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('product/<slug:slug>/', product_detail, name='product_detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)