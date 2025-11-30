from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Message(models.Model):
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_messages"
    )
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_messages"
    )
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    edited = models.BooleanField(default=False)
    edited_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="edited_messages"
    )
    is_read = models.BooleanField(default=False)

    # Threading support
    parent_message = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies'
    )

    class Meta:
        ordering = ["timestamp"]
        indexes = [
            models.Index(fields=["receiver", "-timestamp"]),
            models.Index(fields=["parent_message"]),
        ]

    def __str__(self):
        return f"{self.sender} → {self.receiver}: {self.content[:50]}"

    # Recursive method to get all replies (for UI display)
    def get_thread(self):
        """Return all replies in threaded order"""
        thread = [self]
        for reply in self.replies.all():
            thread.extend(reply.get_thread())
        return thread


class MessageHistory(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="history")
    old_content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=255, default="New Message")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "message"]
