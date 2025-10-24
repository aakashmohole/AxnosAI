from rest_framework import serializers
from .models import Chat

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = "__all__"

class ChatNameGenerateSerializer(serializers.Serializer):
    prompt = serializers.CharField()

class ChatNameUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
