
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message, Notification


@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    """
    Create a notification for the receiver whenever a new Message is created.
    """
    if created:  # Only trigger on new messages, not updates
        Notification.objects.create(
            user=instance.receiver,
            message=instance,
            title=f"New message from {instance.sender.get_full_name() or instance.sender.username}"
        )
