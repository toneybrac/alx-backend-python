from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Message, Notification, MessageHistory


# Task 1: Notification on new message
@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.receiver,
            message=instance,
            title=f"New message from {instance.sender.get_full_name() or instance.sender.username}"
        )


# Task 2: Log message edits
@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = Message.objects.get(pk=instance.pk)
        if old.content != instance.content:
            MessageHistory.objects.create(message=instance, old_content=old.content)
            instance.edited = True
            instance.edited_by = instance.sender
    except Message.DoesNotExist:
        pass


# Task 3: Clean up all user data when account is deleted
@receiver(post_delete, sender=User)
def delete_user_related_data(sender, instance, **kwargs):
    """
    Automatically delete:
    - Messages sent/received
    - Notifications
    - MessageHistory entries
    This runs AFTER the User is deleted (post_delete)
    """
    # These will cascade if you used on_delete=CASCADE, but we do it explicitly for safety
    Message.objects.filter(sender=instance).delete()
    Message.objects.filter(receiver=instance).delete()
    Notification.objects.filter(user=instance).delete()
    MessageHistory.objects.filter(message__sender=instance).delete()
    MessageHistory.objects.filter(message__receiver=instance).delete()
