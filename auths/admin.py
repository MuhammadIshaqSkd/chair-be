from django.contrib import admin
from django import forms as form
from django.contrib.admin import forms
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from auths.models import (
    User,
    UserBusinessProfile,
)

class CustomAdminSite(admin.AdminSite):
    def index(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}

        # Add your custom context
        extra_context['total_users'] = User.objects.count()
        extra_context['active_users'] = User.objects.filter(is_active=True).count()
        extra_context['total_owner_profiles'] = UserBusinessProfile.objects.count()

        return super().index(request, extra_context=extra_context)

# Instantiate the custom admin site
custom_admin_site = CustomAdminSite(name="custom_admin")

class UserAdmin(BaseUserAdmin):
    def image_preview(self, obj):
        if obj.profile_photo:
            return format_html(
                '<image style="height:30px;border-radius:30px" src="{}" />'.format(
                    obj.profile_photo.url
                )
            )
        else:
            return None

    fieldsets = (
        (None, {"fields": (
            "email",
            "password",
            "sign_up_with",
            "account_type",
            "profession",
        )}),
        (_("Personal Information"), {"fields": (
            "username",
            "full_name",
            "profile_photo",
            "image_preview",
            "phone_number"
        )}),
        # (_("Password Reset"), {"fields": ("token", "token_expiry")}),
        (_("Permissions"), {"fields": ("is_active", )}),
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
        "image_preview",
    )

    # list_filter = (
    #     "is_active",
    #     "account_type",
    #       "sign_up_with"
    # )
    list_filter =  []
    readonly_fields = (
        "token",
        "last_login",
        "date_joined",
        "normalized_email",
        "sign_up_with",
        "image_preview",
    )

    search_fields = [
        "email",
        "username",
        "full_name",
        "profession",
        "normalized_email",
    ]


class UserBusinessProfileAdminForm(form.ModelForm):
    class Meta:
        model = UserBusinessProfile
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove "Add" and "View" buttons for the user field
        self.fields['user'].widget.can_add_related = False
        self.fields['user'].widget.can_change_related = False
        self.fields['user'].widget.can_view_related = False  # Hide the "View" button


class UserBusinessProfileAdmin(admin.ModelAdmin):
    form = UserBusinessProfileAdminForm

    list_display = [
        'id',
        'user',
        'business_name',
        'rating',
        'created'
    ]
    fieldsets = (
        (None, {"fields": (
            "user",
            "rating",
            "business_name",
            "location",
            "description",
            "business_logo",
        )}),
        (_("Contact Information"), {"fields": ("business_email", "phone_number", "business_website")}),
        (_("Important Dates"), {"fields": ("created", "modified")}),
    )
    # list_filter = [
    #     'created',
    #     'modified'
    # ]
    # search_fields = [
    #     'user__email',
    #     'user__username',
    #     'business_name',
    #     'user__full_name',
    #     'user__profession',
    #     'workspace',
    # ]
    readonly_fields = [
        'created',
        'modified',
        'rating',
        'total_ratings',
        'total_reviews',
        'id',
    ]


custom_admin_site.register(UserBusinessProfile, UserBusinessProfileAdmin)
custom_admin_site.register(User, UserAdmin)