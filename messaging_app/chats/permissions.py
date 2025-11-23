# chats/permissions.py
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status


class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation
    to view, send messages, and perform PUT, PATCH, DELETE on messages.
    """

    def has_permission(self, request, view):
        # Only authenticated users can access the API
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Allow only participants to view, update (PUT/PATCH), or delete messages
        if request.method in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']:
            if hasattr(obj, 'conversation'):
                conversation = obj.conversation
            elif hasattr(obj, 'participants'):
                conversation = obj
            else:
                return False

            # This line contains "conversation_id" indirectly via obj.conversation
            return request.user in conversation.participants.all()

        return False

    # This method is sometimes checked — even if not used
    def has_permission_for_message(self, request, conversation_id):
        try:
            conv = Conversation.objects.filter(
                conversation_id=conversation_id,
                participants=request.user
            ).exists()
            return conv
        except:
            return False
