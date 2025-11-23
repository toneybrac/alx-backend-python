# messaging_app/chats/models.py

import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    """
    Custom User model extending AbstractUser
    Uses email as the unique identifier (USERNAME_FIELD)
    Uses UUID as primary key
    """
    class RoleChoices(models.TextChoices):
        GUEST = "guest", "Guest"
        HOST = "host", "Host"
        ADMIN = "admin", "Admin"

    # Primary key as UUID
    user_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True,
    )

    # Make email the unique login field
    email = models.EmailField(
        unique=True,
        db_index=True,
        null=False,
        blank=False,
        error_messages={"unique": "A user with that email already exists."},
    )

    first_name = models.CharField(max_length=150, null=False, blank=False)
    last_name = models.CharField(max_length=150, null=False, blank=False)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    role = models.CharField(
        max_length=20,
        choices=RoleChoices.choices,
        default=RoleChoices.GUEST,
        db_index=True,
    )

    created_at = models.DateTimeField(default=timezone.now, editable=False)

    # === CRITICAL FIX: Avoid reverse accessor clashes with built-in User ===
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="custom_user_groups",  # Avoid clash
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )

    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="custom_user_permissions",  # Avoid clash
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

    # Use email as the login field instead of username
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    def __str__(self):
        return self.get_full_name() or self.email

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["role"]),
            models.Index(fields=["created_at"]),
        ]


class Conversation(models.Model):
    """
    Represents a conversation (1-1 or group chat)
    Participants linked via ManyToMany through ConversationParticipant
    """
    conversation_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True,
    )
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    # Participants in this conversation
    participants = models.ManyToManyField(
        User,
        related_name="conversations",
        through="ConversationParticipant",
    )

    def __str__(self):
        names = ", ".join(
            [user.get_full_name() or user.email for user in self.participants.all()[:3]]
        )
        return f"Conversation ({names})"

    class Meta:
        indexes = [
            models.Index(fields=["created_at"]),
        ]
        verbose_name = "Conversation"
        verbose_name_plural = "Conversations"


class ConversationParticipant(models.Model):
    """
    Through model for Conversation ↔ User relationship
    Allows extra data like joined_at in the future
    """
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("conversation", "user")
        indexes = [
            models.Index(fields=["conversation", "user"]),
        ]
        verbose_name = "Conversation Participant"
        verbose_name_plural = "Conversation Participants"


class Message(models.Model):
    """
    Individual message in a conversation
    """
    message_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True,
    )

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_messages",
    )
    message_body = models.TextField(null=False, blank=False)
    sent_at = models.DateTimeField(default=timezone.now, db_index=True, editable=False)

    class Meta:
        ordering = ["sent_at"]
        indexes = [
            models.Index(fields=["conversation", "sent_at"]),
            models.Index(fields=["sender"]),
            models.Index(fields=["sent_at"]),
        ]
        verbose_name = "Message"
        verbose_name_plural = "Messages"

    def __str__(self):
        return f"{self.sender.email}: {self.message_body[:50]}..."
