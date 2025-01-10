from django.contrib import admin
from users.models import Conversation, Message
# Register your models here.

@admin.register(Conversation)
class ConversationAdminView(admin.ModelAdmin):
    list_display = [
        "id",
        "freelancer",
        "owner",
    ]
    list_filter = [
        "created",
        "modified",
    ]
    search_fields = [
        "owner__email",
        "freelancer__email",
    ]
    readonly_fields = [
        "id",
        "created",
        "modified",
    ]

@admin.register(Message)
class MessageAdminView(admin.ModelAdmin):
    list_display = [
        "id",
        "conversation",
        "sender",
        "is_read",
        "created"
    ]

    list_filter = [
        "is_read",
        "created",
    ]
    search_fields = [
        "sender__email",
        "conversation__owner__email",
        "conversation__freelancer__email",
    ]
    readonly_fields = [
        "id",
        "created",
        "modified",
        # "conversation",
    ]