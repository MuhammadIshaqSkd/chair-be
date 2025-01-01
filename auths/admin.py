from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from auths.models import (
    User,
    UserBusinessProfile,
)

# Register your models here.

from django.contrib.admin import AdminSite

AdminSite.site_title = 'Admin Panel'

AdminSite.site_header = 'Chair Administration'

AdminSite.index_title = 'Chair Admin Panel'

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {"fields": ("email", "password", "normalized_email", "account_type")}),
        ("Personal info", {"fields": ("username", "full_name", "profile_photo", "phone_number")}),
        ("Forget token", {"fields": ( "token", "token_expiry")}),
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
        "full_name",
        "account_type",
        "is_active",
        "is_superuser",
    )

    list_filter = (
        "is_active",
        "is_superuser",
        "account_type",
    )
    readonly_fields = ("normalized_email", "token")

    search_fields = [
        "email",
        "username",
        "full_name",
        "normalized_email",
    ]


@admin.register(UserBusinessProfile)
class UserBusinessProfileAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'business_name',
        'created'
    ]
    list_filter = [
        'created',
        'modified'
    ]
    search_fields = [
        'user__email',
        'user__username',
        'business_name'
    ]
    readonly_fields = [
        'created',
        'modified',
        'id',
    ]