from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Conversation, Message, User
from .serializers import ConversationSerializer, MessageSerializer, UserSerializer


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer

    @action(detail=False, methods=['post'], url_path='create-with-participants')
    def create_with_participants(self, request):
        """
        Body: { "participant_ids": [uuid1, uuid2, ...] }
        """
        participant_ids = request.data.get('participant_ids', [])
        if len(participant_ids) < 2:
            return Response({"detail": "At least two participants required."},
                            status=status.HTTP_400_BAD_REQUEST)

        participants = User.objects.filter(user_id__in=participant_ids)
        if participants.count() != len(participant_ids):
            return Response({"detail": "One or more participant IDs invalid."},
                            status=status.HTTP_400_BAD_REQUEST)

        conversation = Conversation.objects.create()
        conversation.participants.set(participants)
        return Response(ConversationSerializer(conversation).data,
                        status=status.HTTP_201_CREATED)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def perform_create(self, serializer):
        """Inject the authenticated user as sender"""
        serializer.save(sender=self.request.user)

    @action(detail=False, methods=['post'], url_path='send-to-conversation')
    def send_to_conversation(self, request):
        """
        Body: { "conversation_id": uuid, "message_body": "text" }
        """
        conv_id = request.data.get('conversation_id')
        body = request.data.get('message_body')
        if not conv_id or not body:
            return Response({"detail": "conversation_id and message_body required."},
                            status=status.HTTP_400_BAD_REQUEST)

        conversation = get_object_or_404(Conversation, conversation_id=conv_id)
        # optional: verify user is participant
        if request.user not in conversation.participants.all():
            return Response({"detail": "You are not a participant of this conversation."},
                            status=status.HTTP_403_FORBIDDEN)

        message = Message.objects.create(
            sender=request.user,
            conversation=conversation,
            message_body=body
        )
        return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)
