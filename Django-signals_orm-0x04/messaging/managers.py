from django.db import models


class UnreadMessagesManager(models.Manager):
    def unread_for_user(self, user):
        """Return only unread messages for the given user with .only() optimization"""
        return self.get_queryset().filter(
            receiver=user,
            is_read=False
        ).only('id', 'sender', 'content', 'timestamp', 'parent_message')
