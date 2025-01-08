from django_filters import rest_framework as filters
from ad_listing.models import AdListing


# Custom FilterSet for AdListing
class AdListingFilter(filters.FilterSet):
    location = filters.CharFilter(field_name='location', lookup_expr='icontains')
    space_type = filters.CharFilter(field_name='space_type', lookup_expr='icontains')

    class Meta:
        model = AdListing
        fields = ['location', 'space_type']