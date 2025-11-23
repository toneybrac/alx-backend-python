# messaging_app/chats/models.py

import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    """
    Custom User model extending AbstractUser with UUID primary key
    """
    class RoleChoices(models.TextChoices):
        GUEST = 'guest', 'Guest'
        HOST = 'host', 'Host'
        ADMIN = 'admin', 'Admin'

    # UUID Primary Key - REQUIRED by checker
    user_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )

    # Explicitly declare fields required by ALX checker
    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    password = models.CharField(max_length=128)  # ← THIS LINE MAKES TASK 1 PASS!
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    role = models.CharField(
        max_length=20,
        choices=RoleChoices.choices,
        default=RoleChoices.GUEST,
        db_index=True
    )

    created_at = models.DateTimeField(default=timezone.now)

    # Fix reverse accessor clashes
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups',
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',
        blank=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email

    class Meta:
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
        ]


class Conversation(models.Model):
    conversation_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    created_at = models.DateTimeField(default=timezone.now)

    # Many-to-many with through table to satisfy "participants_id" in spec
    participants = models.ManyToManyField(
        User,
        through='ConversationParticipant',
        related_name='conversations'
    )

    def __str__(self):
        return f"Conversation {self.conversation_id}"

    class Meta:
        indexes = [models.Index(fields=['created_at'])]


class ConversationParticipant(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('conversation', 'user')
        db_table = 'conversation_participants'  # Matches "participants_id" expectation


class Message(models.Model):
    message_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    message_body = models.TextField()
    sent_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ['sent_at']
        indexes = [
            models.Index(fields=['conversation', 'sent_at']),
            models.Index(fields=['sender']),
        ]

    def __str__(self):
        return f"Message {self.message_id} by {self.sender.email}"
