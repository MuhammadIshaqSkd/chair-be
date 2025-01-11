from django.db.models import Q
from rest_framework import serializers

from auths.models import (
    User,
    UserBusinessProfile,
)
from users.models import (
    Message,
    Conversation,
)
class UserBusinessProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBusinessProfile
        fields = [
            'id',
            'user',
            'rating',
            'workspace',
            "phone_number",
            "business_email",
            'business_name',
            'business_logo',
            'business_website',
            'location',
            'description',
        ]
        read_only_fields = ['id', 'user', 'rating']

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
            "profession",
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

class MessageSerializer(serializers.ModelSerializer):
    message_type = serializers.SerializerMethodField()
    sender_name = serializers.SerializerMethodField()
    sender_profile_img = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            'id',
            'conversation',
            'sender',
            'content',
            'is_read',
            'created',
            'modified',
            'message_type',
            'sender_name',
            'sender_profile_img'
        ]
        read_only_fields = [
            'id',
            'created',
            'modified'
        ]

    def get_message_type(self, obj):
        request_user = self.context.get('request').user
        return "sent" if obj.sender == request_user else "received"

    @staticmethod
    def get_sender_name(obj):
        return obj.sender.full_name

    @staticmethod
    def get_sender_profile_img(obj):
        return obj.sender.profile_photo.url if obj.sender.profile_photo else None


class SendMessageSerializer(serializers.ModelSerializer):
    receiver_user = serializers.IntegerField()
    content = serializers.CharField(max_length=255)

    class Meta:
        model = Message
        fields = ['receiver_user', 'content']

    @staticmethod
    def validate_receiver_user(receiver_user):
        """
        Validate that the receiver user exists in the system.
        """
        try:
            user = User.objects.get(id=receiver_user)
        except User.DoesNotExist:
            raise serializers.ValidationError("Receiver user does not exist.")
        return user

    def validate(self, attrs):
        """
        Perform any additional cross-field validations here.
        """
        user = self.context['request'].user
        if user.id == attrs['receiver_user'].id:
            raise serializers.ValidationError("You cannot send a message to yourself.")
        return attrs

    def create(self, validated_data):
        """
        Create a new message and handle conversation creation if it doesn't already exist.
        """
        user = self.context['request'].user
        receiver_user = validated_data['receiver_user']
        content = validated_data['content']

        # Check if a conversation exists
        conversation = Conversation.objects.filter(
            Q(freelancer=user) | Q(owner=user),
            Q(freelancer=receiver_user) | Q(owner=receiver_user)
        ).first()

        if not conversation:
            # Create a new conversation
            conversation = Conversation.objects.create(
                freelancer=user,
                owner=receiver_user
            )

        # Create the message
        message = Message.objects.create(
            conversation=conversation,
            sender=user,
            content=content
        )

        return message

class ConversationSerializer(serializers.ModelSerializer):
    unread_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    user_profile_img = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'id',
            'freelancer',
            'owner',
            'created',
            'modified',
            'unread_count',
            'last_message',
            'user_name',
            'user_profile_img'
        ]
        read_only_fields = ['id', 'created', 'modified']

    @staticmethod
    def get_unread_count(obj):
        return Message.objects.filter(conversation=obj, is_read=False).count()

    def get_last_message(self, obj):
        last_message = Message.objects.filter(conversation=obj).order_by('-created').first()
        if last_message:
            serializer = MessageSerializer(last_message, context=self.context)
            return {
                "message_type": serializer.data['message_type'],
                "content": last_message.content,
                "created": last_message.created,
            }
        return None

    def get_user_name(self, obj):
        request_user = self.context.get('request').user
        other_user = obj.freelancer if obj.owner == request_user else obj.owner
        return other_user.full_name

    def get_user_profile_img(self, obj):
        request_user = self.context.get('request').user
        other_user = obj.freelancer if obj.owner == request_user else obj.owner
        return other_user.profile_photo.url if other_user.profile_photo else None

    def to_representation(self, instance):
        is_list_view = self.context.get('list', False)
        data = super().to_representation(instance)

        # Exclude messages for list view
        if not is_list_view:
            messages_query = Message.objects.filter(conversation=instance).order_by('-created')
            data['messages'] = MessageSerializer(messages_query, many=True, context=self.context).data

        # Remove unnecessary fields for list view
        if is_list_view:
            data.pop('freelancer', None)
            data.pop('owner', None)

        return data


