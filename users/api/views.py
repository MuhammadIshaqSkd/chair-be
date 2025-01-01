from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import (
    status,
    viewsets,
    permissions,
)
from rest_framework.response import Response
from rest_framework.generics import UpdateAPIView, ListAPIView

from auths.models import UserBusinessProfile
from users.api.serializers import (
    UserBusinessProfileSerializer,
    UserAccountTypeSerializer,
)


# Create your views here.
@extend_schema(tags=['User Profile'])
class UpdateUserAccountTypeView(UpdateAPIView, ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserAccountTypeSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        try:
            user = self.get_object()
            business_profile = UserBusinessProfile.objects.filter(user=user).exists()
            if not business_profile:
                return Response(
                    'User does not have a business profile.',
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.get_serializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            account_type = serializer.validated_data.get('account_type')
            return Response(
                f"Account shifted to {account_type} successfully.",
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(e, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(tags=['User-Rental Profile'])
class UserRentalProfileViewSet(viewsets.GenericViewSet):
    serializer_class = UserBusinessProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        user = request.user
        business_profile = UserBusinessProfile.objects.filter(user=user)
        if not business_profile.exists():
            return Response(
                "Business profile does not exist for this user.",
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(business_profile, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        user = request.user
        if UserBusinessProfile.objects.filter(user=user).exists():
            return Response(
                {"detail": "Business profile already exists for this user."},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)
        user = request.user
        user.account_type = "property_owner"
        user.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        user = request.user
        obj = get_object_or_404(UserBusinessProfile, user=user)
        serializer = self.get_serializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)