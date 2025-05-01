# app/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Course, Module, Section, Exercise, Completion

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'points', 'is_admin')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('points', 'is_admin')}),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(Course)
admin.site.register(Module)
admin.site.register(Section)
admin.site.register(Exercise)
admin.site.register(Completion)