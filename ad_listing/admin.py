from django.contrib import admin
from django.utils.html import format_html

from ad_listing.models import (
    AdReview,
    AdListing,
    AdListImage,
    RentalRequest,
)
# Register your models here.

@admin.register(AdListImage)
class AdListImageAdminView(admin.ModelAdmin):

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<image style="height:30px;border-radius:30px" src="{}" />'.format(
                    obj.image.url
                )
            )
        else:
            return None

    list_display = [
        'id',
        'image_preview',
        'created'
    ]
    list_filter = ['created', 'modified']

@admin.register(AdListing)
class AdListingAdminView(admin.ModelAdmin):
    filter_horizontal = ('ad_list_images',)

    list_display = [
        'id',
        'title',
        'user',
        'rental_rate',
        'location',
        'created',
    ]
    list_filter = [
        'created',
        'modified',
        'space_type'
    ]
    search_fields = [
        'title',
        'location',
        'space_type',
        'user__business_name',
        'user__user__email',
    ]
    readonly_fields = [
        'id',
        'total_ratings',
        'total_reviews',
        'created',
        'modified'
    ]


@admin.register(RentalRequest)
class RentalRequestAdminView(admin.ModelAdmin):
    list_display = [
        'rental_user',
        'ad_list',
        'status',
        'created',
        'id',
    ]

    list_filter = ['status', 'created', 'is_review']
    search_fields = [
        'rental_user__email',
        'ad_list__title',
        'status',
    ]
    readonly_fields = ['id', 'is_review']

@admin.register(AdReview)
class AdReviewAdminView(admin.ModelAdmin):

    list_display = [
        'id',
        'user_request',
        'rating',
    ]
