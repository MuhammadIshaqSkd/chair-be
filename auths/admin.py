from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from auths.models import (
    User,
    UserBusinessProfile,
)

# Register your models here.
admin.site.site_title = _('Admin Panel')
admin.site.site_header = _('Chair Administration')
admin.site.index_title = _('Chair Admin Panel')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {"fields": ("email", "password", "normalized_email", "account_type", "profession")}),
        (_("Personal Information"), {"fields": ("username", "full_name", "profile_photo", "phone_number")}),
        (_("Password Reset"), {"fields": ("token", "token_expiry")}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser")}),
        (_("Important Dates"), {"fields": ("date_joined", "last_login")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "full_name", "profession"),
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
    readonly_fields = (
        "token",
        "last_login",
        "date_joined",
        "normalized_email",
    )

    search_fields = [
        "email",
        "username",
        "full_name",
        "profession",
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
        'business_name',
        'user__full_name',
        'user__profession',
        'workspace',
    ]
    readonly_fields = [
        'created',
        'modified',
        'id',
    ]