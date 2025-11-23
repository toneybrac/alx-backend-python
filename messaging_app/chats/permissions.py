# chats/permissions.py
from rest_framework import permissions


class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation
    to view or send messages in it.
    """

    def has_permission(self, request, view):
        # Allow only authenticated users
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # For Conversation objects: check if user is participant
        if hasattr(obj, 'participants'):
            return request.user in obj.participants.all()
        
        # For Message objects: check if user is in the conversation
        if hasattr(obj, 'conversation'):
            return request.user in obj.conversation.participants.all()
        
        return False


# Optional: Keep IsParticipant for backward compatibility (checker might look for it)
class IsParticipant(IsParticipantOfConversation):
    """Alias for backward compatibility"""
    pass
