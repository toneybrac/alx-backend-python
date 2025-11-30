from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Message, Notification, MessageHistory


@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.receiver,
            message=instance,
            title=f"New message from {instance.sender.get_full_name() or instance.sender.username}"
        )


@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    """Save old content to history if message is being updated and content changed"""
    if not instance.pk:  # New message → nothing to log
        return

    try:
        old_message = Message.objects.get(pk=instance.pk)
    except Message.DoesNotExist:
        return

    if old_message.content != instance.content:
        MessageHistory.objects.create(
            message=instance,
            old_content=old_message.content
        )
        instance.edited = True  # Mark as edited
        instance.edited_by = instance.sender
