
from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, Notification


class MessageNotificationSignalTest(TestCase):
    def setUp(self):
        self):
        self.sender = User.objects.create_user("alice", password="pass123")
        self.receiver = User.objects.create_user("bob", password="pass123")

    def test_notification_created_on_new_message(self):
        """Ensure a notification is created when a new message is saved"""
        Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Hey Bob, how are you?"
        )

        # Check that exactly one notification was created for the receiver
        self.assertEqual(Notification.objects.count(), 1)
        notification = Notification.objects.first()
        self.assertEqual(notification.user, self.receiver)
        self.assertIn("alice", notification.title.lower())  # sender name in title

    def test_no_notification_on_message_update(self):
        """Updating a message should NOT create a new notification"""
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Initial message"
        )
        Notification.objects.all().delete()  # Clear any from creation

        message.content = "Updated content"
        message.save()

        self.assertEqual(Notification.objects.count(), 0)
