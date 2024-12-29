from rest_framework import serializers

from auths.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "full_name",
            "business_name",
            "profile_photo",
            "is_active",
            "sign_up_with",
        ]
