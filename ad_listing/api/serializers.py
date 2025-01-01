from rest_framework import serializers

from ad_listing.models import AdListing, AdListImage, RentalRequest


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


class RentalRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RentalRequest
        fields = "__all__"
        read_only_fields = [
            'id',
            'status',
            'is_review'
        ]

    def validate(self, data):
        # Ensure users cannot create a rental request for their own ad
        request = self.context['request']
        if request.method == "POST" and data['ad_list'].user.user == request.user:
            raise serializers.ValidationError(
                "You cannot create a rental request for your own ad."
            )
        return data

class UpdateRentalRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RentalRequest
        fields = "__all__"
        read_only_fields = [
            'id',
            'ad_list',
            'is_review',
            'rental_user',
        ]


    def update(self, instance, validated_data):
        # Allow only the ad_list owner to update the status
        if instance.status == 'approved':
            raise serializers.ValidationError(
                "This rental request has already been approved."
            )
        if not 'status' in validated_data:
            raise serializers.ValidationError('status field is required')
        request = self.context['request']
        if 'status' in validated_data and instance.ad_list.user.user != request.user:
            raise serializers.ValidationError(
                "You do not have permission to update the status of this rental request."
            )
        # Allow other fields to be updated if necessary
        return super().update(instance, validated_data)