from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, Notification


class MessageNotificationSignalTest(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(username="alice", password="123")
        self.receiver = User.objects.create_user(username="bob", password="123")

    def test_notification_created_on_new_message(self):
        """A notification must be created when a new message is saved"""
        Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Hello Bob!"
        )

        self.assertEqual(Notification.objects.count(), 1)
        notification = Notification.objects.first()
        self.assertEqual(notification.user, self.receiver)
        self.assertIn(self.sender.username, notification.title)

    def test_no_notification_on_update(self):
        """Updating a message should NOT create another notification"""
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="First"
        )
        Notification.objects.all().delete()

        message.content = "Updated"
        message.save()

        self.assertEqual(Notification.objects.count(), 0)
