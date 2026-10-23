
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("ResolveX Details", {"fields": ("role", "organization")}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("ResolveX Details", {"fields": ("role", "organization")}),
    )

    list_display = (
        "username",
        "email",
        "role",
        "organization",
        "is_staff",
        "is_active",
    )
