# messaging_app/chats/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Conversation, ConversationParticipant, Message

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model - used in nested representations
    """
    class Meta:
        model = User
        fields = [
            "user_id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "role",
            "date_joined",
            "created_at",
        ]
        read_only_fields = ["user_id", "date_joined", "created_at"]


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for Message - includes sender details
    """
    sender = UserSerializer(read_only=True)
    sender_id = serializers.UUIDField(write_only=True)  # For creating messages

    class Meta:
        model = Message
        fields = [
            "message_id",
            "conversation",
            "sender",
            "sender_id",
            "message_body",
            "sent_at",
        ]
        read_only_fields = ["message_id", "sent_at", "sender"]

    def validate_sender_id(self, value):
        """
        Ensure the sender exists and is a participant in the conversation
        """
        request = self.context.get("request")
        if request and request.user.user_id != value:
            raise serializers.ValidationError("You can only send messages as yourself.")
        try:
            User.objects.get(user_id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Sender does not exist.")
        return value

    def validate(self, data):
        """
        Ensure sender is part of the conversation
        """
        conversation = data.get("conversation")
        sender_id = data.get("sender_id")

        if conversation and sender_id:
            if not conversation.participants.filter(user_id=sender_id).exists():
                raise serializers.ValidationError(
                    "Sender must be a participant in this conversation."
                )
        return data


class ConversationParticipantSerializer(serializers.ModelSerializer):
    """
    For displaying participant details inside a conversation
    """
    user = UserSerializer(read_only=True)
    user_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = ConversationParticipant
        fields = ["user", "user_id", "joined_at"]
        read_only_fields = ["joined_at"]


class ConversationSerializer(serializers.ModelSerializer):
    """
    Main Conversation serializer with nested messages and participants
    """
    participants = ConversationParticipantSerializer(
        source="conversationparticipant_set", many=True, read_only=True
    )
    messages = MessageSerializer(many=True, read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Conversation
        fields = [
            "conversation_id",
            "participants",
            "messages",
            "created_at",
        ]
        read_only_fields = ["conversation_id", "created_at"]


class ConversationCreateSerializer(serializers.ModelSerializer):
    """
    Used when creating a new conversation - accepts list of participant user_ids
    """
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        min_length=2,
        max_length=50,
    )

    class Meta:
        model = Conversation
        fields = ["conversation_id", "participant_ids", "created_at"]
        read_only_fields = ["conversation_id", "created_at"]

    def create(self, validated_data):
        participant_ids = validated_data.pop("participant_ids")
        conversation = Conversation.objects.create()

        participants_to_add = []
        for user_id in participant_ids:
            try:
                user = User.objects.get(user_id=user_id)
                participants_to_add.append(
                    ConversationParticipant(conversation=conversation, user=user)
                )
            except User.DoesNotExist:
                raise serializers.ValidationError(f"User with id {user_id} does not exist.")

        ConversationParticipant.objects.bulk_create(participants_to_add)
        return conversation
