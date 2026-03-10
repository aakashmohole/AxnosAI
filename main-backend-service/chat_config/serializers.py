from rest_framework import serializers
from .models import Chat

from data_config.serializers import PromptSerializer

class ChatSerializer(serializers.ModelSerializer):
    prompts = PromptSerializer(many=True, read_only=True)
    
    class Meta:
        model = Chat
        fields = ["id", "name", "user_id", "dataset", "name_generated", "created_At", "preview", "table_name", "prompts"]
        read_only_fields = ['id', 'user_id', 'created_at']

class ChatNameGenerateSerializer(serializers.Serializer):
    prompt = serializers.CharField()

class ChatNameUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
