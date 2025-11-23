# chats/permissions.py
from rest_framework import permissions

class IsParticipant(permissions.BasePermission):
    """
    Allows access only to participants of the conversation
    """
    def has_object_permission(self, request, view, obj):
        return request.user in obj.participants.all()
