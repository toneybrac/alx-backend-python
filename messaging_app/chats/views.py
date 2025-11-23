# messaging_app/chats/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Conversation, Message, ConversationParticipant
from .serializers import (
    ConversationSerializer,
    ConversationCreateSerializer,
    MessageSerializer,
    UserSerializer,
)


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for:
    - Listing all conversations the authenticated user is part of
    - Creating a new conversation
    - Retrieving a single conversation (with messages & participants)
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only return conversations where the user is a participant
        return Conversation.objects.filter(participants=self.request.user).distinct()

    def get_serializer_class(self):
        if self.action == "create":
            return ConversationCreateSerializer
        return ConversationSerializer

    def perform_create(self, serializer):
        # Automatically handled by ConversationCreateSerializer
        serializer.save()

    @action(detail=True, methods=["post"], url_path="send-message")
    def send_message(self, request, pk=None):
        """
        Custom action: POST /api/conversations/{id}/send-message/
        Send a message in this conversation
        """
        conversation = self.get_object()  # 404 if not found or not participant

        serializer = MessageSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            # Set sender to current user and save
            message = serializer.save(
                conversation=conversation,
                sender=request.user
            )
            read_serializer = MessageSerializer(message, context={"request": request})
            return Response(read_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MessageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only ViewSet for listing messages
    Only messages from conversations the user participates in are shown
    """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        conversation_id = self.kwargs.get("conversation_id")
        if conversation_id:
            # Used when nested under conversation (optional future route)
            conversation = get_object_or_404(
                Conversation,
                conversation_id=conversation_id,
                participants=self.request.user
            )
            return Message.objects.filter(conversation=conversation)
        
        # Fallback: all messages from user's conversations
        return Message.objects.filter(
            conversation__participants=self.request.user
        ).select_related("sender").order_by("sent_at")
