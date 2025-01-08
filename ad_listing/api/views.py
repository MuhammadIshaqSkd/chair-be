import ast

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from drf_spectacular.utils import extend_schema

from ad_listing.filters import AdListingFilter
from auths.models import UserBusinessProfile
from ad_listing.models import (
    AdReview,
    AdListing,
    AdListImage,
    RentalRequest,
)
from ad_listing.api.serializers import (
    AdReviewSerializer,
    AdListingSerializer,
    AdListImageSerializer,
    RentalRequestSerializer,
    UpdateRentalRequestSerializer,
)
from ad_listing.helper import (
    process_media,
    CustomPagination
)

# Create your views here.

@extend_schema(tags=['Ad Listings'])
class AdListingViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AdListingSerializer
    queryset = AdListing.objects.all()
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = AdListingFilter
    search_fields = ['title', 'location', 'space_type', 'availability']


    def list(self, request, *args, **kwargs):
        user = request.user
        if user.account_type == "Owner":
            business_profile = UserBusinessProfile.objects.filter(user=user).first()
            if not business_profile:
                return Response(
                    "Business profile does not exist for this user.",
                    status=status.HTTP_404_NOT_FOUND
                )
            ad_list_query = self.queryset.filter(user__id=business_profile.id)
        else:
            ad_list_query = self.queryset.order_by('-created')
        # Apply filtering and searching
        ad_list_query = self.filter_queryset(ad_list_query)
        page = self.paginate_queryset(ad_list_query)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(ad_list_query, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        instance = self.get_object()

        if user.account_type == "Owner":
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


@extend_schema(tags=['Rental Request'])
class RentalRequestView(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = RentalRequestSerializer
    queryset = RentalRequest.objects.all()
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']

    def get_queryset(self):
        """
        Return rental requests based on the user's account type.
        - Property owners: See requests for their own ads.
        - Freelancers: See their own rental requests.
        """
        user = self.request.user
        if user.account_type == "Owner":
            return self.queryset.filter(ad_list__user__user__id=user.id)
        else:
            return self.queryset.filter(rental_user=user)

    def create(self, request, *args, **kwargs):
        """
        Allow only Freelancer users to create rental requests.
        Automatically associate the request with the logged-in user.
        Prevent status field modification during creation.
        """
        user = request.user
        if user.account_type == "Owner":
            return Response(
                {"detail": "Only Freelancer users can request for rental."},
                status=status.HTTP_403_FORBIDDEN,
            )

        data = request.data.copy()
        data.pop("status", None)  # Prevent status updates during creation
        data["rental_user"] = user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        """
        Allow partial updates and validate permissions.
        Ad owners can update only the status field.
        """
        rental_request = self.get_object()
        serializer_class = UpdateRentalRequestSerializer
        serializer = serializer_class(
            rental_request,
            data=request.data,
            partial=True,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        update_status = serializer.validated_data.get("status")
        return Response(
            f'Request {update_status} successfully', status=status.HTTP_200_OK
        )

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific rental request.
        """
        rental_request = self.get_object()
        serializer = self.get_serializer(rental_request)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        """
        List rental requests for the authenticated user based on account type.
        """
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

@extend_schema(tags=['Request Review'])
class RequestReviewView(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AdReviewSerializer
    queryset = AdReview.objects.all()
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        if user.account_type == "Owner":
            return self.queryset.filter(user_request__ad_list__user__user__id=user.id)
        else:
            return self.queryset.filter(review_user__id=user.id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        user = request.user
        new_data = request.data.copy()
        new_data['review_user'] = user.id
        ad_review_serializer = self.get_serializer(data=new_data)
        ad_review_serializer.is_valid(raise_exception=True)
        ad_review_serializer.save()
        return Response(ad_review_serializer.data, status=status.HTTP_201_CREATED)