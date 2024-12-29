from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from auths.models import User

# Register your models here.

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {"fields": ("email", "password",)}),
        ("Personal info", {"fields": ("username", "full_name", "profile_photo", "phone_number")}),
        ("Forget token", {"fields": ( "token", "token_expiry")}),
        ("business info", {"fields": ("business_name", "business_description")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "full_name"),
        }),
    )

    list_display = (
        "id",
        "email",
        "business_name",
        "full_name",
        "is_active",
        "is_superuser",
    )

    list_filter = (
        "is_staff",
        "is_active",
        "is_superuser",
    )

    search_fields = ["email", "username", "full_name", "business_name"]
