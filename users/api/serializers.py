from rest_framework import serializers

from auths.models import User, UserBusinessProfile

class UserBusinessProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBusinessProfile
        fields = [
            'id',
            'user',
            'business_name',
            'business_logo',
            'business_website',
            'business_location',
            'business_description',
        ]
        read_only_fields = ['id', 'user']

    @staticmethod
    def validate_business_name(value):
        if len(value) < 3:
            raise serializers.ValidationError(
                {"business_name" : "Business name must be at least 3 characters long."}
            )
        return value

class UserSerializer(serializers.ModelSerializer):
    business_account = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "full_name",
            "is_active",
            "account_type",
            "sign_up_with",
            "profile_photo",
            "business_account",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        business_account = UserBusinessProfile.objects.filter(user=instance).exists()
        data['business_account'] = business_account
        return data

class UserAccountTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "id",
            "account_type",
        ]
        read_only_fields = ['id']

