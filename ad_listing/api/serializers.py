from rest_framework import serializers

from ad_listing.models import AdListing, AdListImage


class AdListingSerializer(serializers.ModelSerializer):
    rating = serializers.FloatField(read_only=True)

    class Meta:
        model = AdListing
        fields = '__all__'
        read_only_fields = [
            'id',
            'rating',
        ]

class AdListImageSerializer(serializers.ModelSerializer):

    class Meta:
            model = AdListImage
            fields = '__all__'