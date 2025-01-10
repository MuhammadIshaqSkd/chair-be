from django.db.models import Q
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import (
    status,
    viewsets,
    permissions,
)
from rest_framework.response import Response
from rest_framework.generics import (
    ListAPIView,
    UpdateAPIView,
)

from ad_listing.helper import CustomPagination
from auths.models import (
    User,
    UserBusinessProfile,
)
from users.models import (
    Message,
    Conversation,
)
from users.api.serializers import (
    MessageSerializer,
    ConversationSerializer,
    UserAccountTypeSerializer,
    UserBusinessProfileSerializer,
)
from users.helper import mark_messages_as_read


# Create your views here.
@extend_schema(tags=['User Profile'])
class UpdateUserAccountTypeView(UpdateAPIView, ListAPIView):
    """
    Allows authenticated users to update their account type and view their account details.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserAccountTypeSerializer
    queryset = User.objects.all()

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(id=user.id)

    def update(self, request, *args, **kwargs):
        user = self.request.user

        # Check if the user has a business profile
        if not UserBusinessProfile.objects.filter(user=user).exists():
            return Response(
                "User does not have a business profile.",
                status=status.HTTP_400_BAD_REQUEST
            )

        # Partially update the user's account type
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Return success message with updated account type
        account_type = serializer.validated_data.get('account_type')
        return Response(
            f"Account shifted to {account_type} successfully.",
            status=status.HTTP_200_OK
        )

@extend_schema(tags=['User-Rental Profile'])
class UserRentalProfileViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserBusinessProfileSerializer

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
        user.account_type = "Owner"
        user.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        user = request.user
        obj = get_object_or_404(UserBusinessProfile, user=user)
        serializer = self.get_serializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(tags=['User Inbox Messages'])
class ConversationViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ConversationSerializer
    queryset = Conversation.objects.all()
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        return Conversation.objects.filter(Q(freelancer=user) | Q(owner=user)).order_by('-created')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(
            queryset,
            many=True,
            context={
                "request": request,
                "list": "conversation_list"
            })
        if page:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(tags=['User Inbox Messages'])
class MessageViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MessageSerializer
    queryset = Message.objects.all()
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        queryset = Message.objects.filter(
            Q(conversation__freelancer=user) | Q(conversation__owner=user)
        ).order_by('-created')
        return queryset

    def list(self, request, *args, **kwargs):
        conversation_id = request.query_params.get('conversation_id', None)
        if not conversation_id:
            return Response('conversation_id is required', status=status.HTTP_400_BAD_REQUEST)

        # Filter messages for the conversation
        message_query = self.queryset.filter(conversation__id=conversation_id)

        # Validate if the conversation exists and belongs to the user
        if self.queryset.exists() and not message_query.exists():
            return Response('Invalid Conversation ID', status=status.HTTP_404_NOT_FOUND)

        # Paginate the queryset
        page = self.paginate_queryset(message_query)
        serializer = self.get_serializer(
            page if page is not None else message_query,
            many=True,
            context={"request": request, "list": "message_list"}
        )

        # Mark messages as read
        mark_messages_as_read(message_query)

        if page:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)
