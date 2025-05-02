from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    # 1. Root redirect – handles “/” only
    path(
        "",
        lambda request: (
            redirect("app:admin_dashboard")
            if request.user.is_authenticated and request.user.is_admin
            else redirect("app:dashboard")
            if request.user.is_authenticated
            else redirect("app:auth_page")
        ),
    ),

    # 2. Your app URLs – must come BEFORE the built-in admin
    path("", include("app.urls")),

    # 3. Built-in Django admin – keep it last
    path("admin/", admin.site.urls),
]
