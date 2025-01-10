from rest_framework import serializers

from ad_listing.models import (
    AdReview,
    AdListing,
    AdListImage,
    RentalRequest,
)

class AdReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdReview
        fields = '__all__'
        read_only_fields = ['id']

    def validate(self, data):
        # Ensure user_request is present
        user_request = data.get('user_request')
        if not user_request:
            raise serializers.ValidationError({"user_request": "This field is required."})

        # Check if the rental request status is 'approved'
        if user_request.status != 'approved':
            raise serializers.ValidationError(
                {"user_request": "This rental request has not been approved."}
            )

        # Check if the request is already reviewed
        if user_request.is_review:
            raise serializers.ValidationError(
                {"user_request": "You have already reviewed this request."}
            )

        return data


class AdListingSerializer(serializers.ModelSerializer):
    rating = serializers.FloatField(read_only=True)

    class Meta:
        model = AdListing
        fields = '__all__'
        read_only_fields = [
            'id',
            'rating',
            'total_ratings',
            'total_reviews',
        ]
    def to_representation(self, instance):
        data = super().to_representation(instance)
        ad_list_reviews = AdReview.objects.filter(user_request__ad_list__id=instance.id)
        data['ad_list_reviews'] = ad_list_reviews
        return data

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