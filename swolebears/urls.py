from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('landing.urls')), # Route specific custom routes (e.g. admin/qr-analytics/) first
    path('admin/', admin.site.urls),
]

