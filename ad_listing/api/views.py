import ast

from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ad_listing.helper import process_media
from auths.models import UserBusinessProfile
from ad_listing.models import (
    AdListing,
    AdListImage,
)
from ad_listing.api.serializers import (
    AdListingSerializer,
    AdListImageSerializer,
)


# Create your views here.

@extend_schema(tags=['Ad Listings'])
class AdListingViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AdListingSerializer
    queryset = AdListing.objects.all()

    def list(self, request, *args, **kwargs):
        user = request.user
        if user.account_type == "property_owner":
            business_profile = UserBusinessProfile.objects.filter(user=user).first()
            if not business_profile:
                return Response(
                    "Business profile does not exist for this user.",
                    status=status.HTTP_404_NOT_FOUND
                )
            ad_list_query = self.queryset.filter(user__id=business_profile.id)
        else:
            ad_list_query = self.queryset.order_by('-created')
        serializer = self.get_serializer(ad_list_query, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        instance = self.get_object()

        if user.account_type == "property_owner":
            business_profile = UserBusinessProfile.objects.filter(user=user).first()
            if not business_profile:
                return Response(
                    "Business profile does not exist for this user.",
                    status=status.HTTP_404_NOT_FOUND
                )

            # Ensure the requesting user owns the ad listing
            if instance.user.id != business_profile.id:
                return Response(
                    "You are not authorized to view this ad listing.",
                    status=status.HTTP_403_FORBIDDEN
                )

        # For other user types, no ownership check is applied
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        try:
            user = request.user
            business_profile = UserBusinessProfile.objects.filter(user=user)
            if not business_profile.exists():
                return Response(
                    "Business profile does not exist for this user.",
                    status=status.HTTP_400_BAD_REQUEST
                )
            new_data = request.data.copy()
            new_data.pop("ad_images", "[]")
            new_data['user'] = business_profile.first().id
            ad_list_serializer = self.get_serializer(data=new_data)
            ad_list_serializer.is_valid(raise_exception=True)
            ad_list__ins = ad_list_serializer.save()

            images = request.data.getlist("ad_images")
            img_ids = []
            for image in images:
                data = {"image": image}
                post_ser = AdListImageSerializer(data=data)
                post_ser.is_valid(raise_exception=True)
                post_ins = post_ser.save()
                img_ids.append(post_ins.id)
                ad_list__ins.ad_images.set(img_ids)
            ad_list__ins.save()
            return Response(ad_list_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(e, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        try:
            user = request.user
            business_profile = UserBusinessProfile.objects.filter(user=user)
            if not business_profile.exists():
                return Response(
                    "Business profile does not exist for this user.",
                    status=status.HTTP_400_BAD_REQUEST
                )
            partial = kwargs.pop('partial', True)
            delete_media = request.data.get("delete_media_ids")
            instance = self.get_object()

            # Ensure the requesting user owns the ad listing
            if instance.user.user.id != request.user.id:
                return Response(
                    "You are not authorized to update this ad listing.",
                    status=status.HTTP_403_FORBIDDEN
                )
            data = request.data
            ad_images = request.FILES.getlist("ad_images", [])
            if ad_images:
                data.pop('ad_images')
            serializer = self.get_serializer(instance, data=data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            img_ids = process_media(ad_images)
            # Append new media IDs to the existing Many-to-Many field
            instance.ad_images.add(*img_ids)
            instance.save()

            if delete_media:
                delete_media_list = ast.literal_eval(delete_media)
                delete_social_media = AdListImage.objects.filter(id__in=delete_media_list)
                for social_media in delete_social_media:
                    social_media.delete()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Ensure the requesting user owns the ad listing
        if instance.user.user.id != request.user.id:
            return Response(
                "You are not authorized to delete this ad listing.",
                status=status.HTTP_403_FORBIDDEN
            )

        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)