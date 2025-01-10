from django.db import models
from django.core.exceptions import ValidationError
from django_extensions.db.models import TimeStampedModel

from auths.models import User


class Conversation(TimeStampedModel):
    """
    Represents a conversation between two users.
    """
    freelancer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="freelancer_conversations",
        help_text="The freelancer user in the conversation."
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="owner_conversations",
        help_text="The owner user in the conversation."
    )

    class Meta:
        unique_together = ('freelancer', 'owner')
        verbose_name = "Conversation"
        verbose_name_plural = "Conversations"
        ordering = ['-modified']

    def clean(self):
        """
        Custom validation to ensure freelancer and owner are not the same.
        """
        if self.freelancer == self.owner:
            raise ValidationError("Freelancer and Owner cannot be the same user.")

    def save(self, *args, **kwargs):
        self.clean()  # Ensure validation is run before saving
        super().save( **kwargs)

    def __str__(self):
        return f"{self.freelancer.full_name} - {self.owner.full_name}"


class Message(TimeStampedModel):
    """
    Represents a message in a conversation.
    """
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
        help_text="The conversation to which this message belongs."
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_messages",
        help_text="The user who sent the message."
    )
    content = models.TextField(help_text="The content of the message.")
    is_read = models.BooleanField(default=False, help_text="Whether the message has been read.")

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        ordering = ['-created']

    def clean(self):
        """
        Custom validation to ensure the sender is part of the conversation.
        """
        if self.sender not in [self.conversation.freelancer, self.conversation.owner]:
            raise ValidationError("Message sender must be either the freelancer or the owner of the conversation.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(**kwargs)

    def __str__(self):
        return f"Message from {self.sender} at {self.created}"

