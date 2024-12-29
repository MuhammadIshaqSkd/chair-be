from django.shortcuts import get_object_or_404
from rest_framework import (
    status,
    viewsets,
    permissions,
)
from rest_framework.response import Response

from auths.models import UserBusinessProfile
from users.api.serializers import UserBusinessProfileSerializer


# Create your views here.

class UserBusinessProfileViewSet(viewsets.GenericViewSet):
    serializer_class = UserBusinessProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        user = request.user
        business_profile = UserBusinessProfile.objects.filter(user=user)
        if not business_profile.exists():
            return Response(
                {"detail": "Business profile does not exist for this user."},
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
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        user = request.user
        obj = get_object_or_404(UserBusinessProfile, user=user)
        serializer = self.get_serializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)