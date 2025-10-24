from rest_framework import serializers 
from .models import Prompt  

class PromptSerializer(serializers.ModelSerializer):
    # To display chat_id as its ID (default behavior), we don't need extra config.
    # But if we want more details from Chat model, we can use depth or nested serializers.

    class Meta:
        model = Prompt  
        fields = '__all__' 
    