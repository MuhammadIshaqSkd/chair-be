from rest_framework import serializers
from django.contrib.auth import password_validation
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.api.serializers import (
    UserSerializer,
)
from auths.models import User
from auths.helper import get_normalized_email



class SignupSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "username",
            "full_name",
            "profession",
            "phone_number",
        ]
        extra_kwargs = {"password": {"write_only": True}}
        read_only_fields = ["id", "username"]

    def validate_password(self, value):
        password_validation.validate_password(value, self.instance)
        return value

    @staticmethod
    def validate_email(value):
        # Check if a user with the same email (case-insensitive) already exists
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value


    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class TokenObtainOverridePairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        username_or_email = attrs.get(self.username_field)
        normalized_email = get_normalized_email(username_or_email)
        # Fetch the user, case-insensitive
        user = User.objects.filter(normalized_email__iexact=normalized_email).first()

        if not user:
            # If email is not found
            raise serializers.ValidationError({"detail": "Invalid email or password"})

        # Validate using the parent class
        data = super().validate(attrs)

        serializer = UserSerializer(self.user)
        data = {
            **serializer.data,
            "token": data['access']
        }
        return data
