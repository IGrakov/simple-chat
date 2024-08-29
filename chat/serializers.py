from rest_framework import serializers

from chat.models import Message, Thread
from user.serializers import UserSerializer


class ThreadReadSerializer(serializers.ModelSerializer):
    participant_one = UserSerializer(read_only=True)
    participant_two = UserSerializer(read_only=True)

    class Meta:
        model = Thread
        fields = [
            'id',
            'participant_one',
            'participant_two',
            'created_at',
            'updated_at',
        ]


class ThreadWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thread
        fields = [
            'participant_one',
            'participant_two',
            'created_at',
            'updated_at',
        ]

    def to_representation(self, data):
        return ThreadReadSerializer(context=self.context).to_representation(data)


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = [
            'id',
            'sender',
            'text',
            'thread',
            'created_at',
            'is_read',
        ]


class SwaggerCreateMessageSerializer(MessageSerializer):
    class Meta:
        model = Message
        fields = [
            'id',
            'sender',
            'text',
            'thread',
            'created_at',
        ]
