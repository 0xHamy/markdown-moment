# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('app:dashboard') if request.user.is_authenticated else redirect('app:auth_page')),
    path('app/', include('app.urls')),
]
