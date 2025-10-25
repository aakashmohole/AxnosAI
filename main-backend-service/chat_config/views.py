from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from django.shortcuts import get_object_or_404
from .models import Chat
from .serializers import ChatSerializer, ChatNameGenerateSerializer, ChatNameUpdateSerializer

from collections import Counter
from .utils.auto_generate_chat_name import generate_chat_name

# ✅ API to auto-generate chat name
class GenerateChatNameView(APIView):
    def post(self, request, pk):
        chat = get_object_or_404(Chat, pk=pk)
        serializer = ChatNameGenerateSerializer(data=request.data)

        if serializer.is_valid():
            if not chat.name_generated:  # Only generate if not already generated
                prompt = serializer.validated_data["prompt"]
                chat.name = generate_chat_name(prompt)
                chat.name_generated = True
                chat.save()
            return Response({"chat_id": chat.id, "name": chat.name}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ✅ API to manually update chat name
class UpdateChatNameView(APIView):
    def put(self, request, pk):
        chat = get_object_or_404(Chat, pk=pk)
        serializer = ChatNameUpdateSerializer(data=request.data)

        if serializer.is_valid():
            chat.name = serializer.validated_data["name"]
            chat.name_generated = True  # Mark true since name is set manually
            chat.save()
            return Response({"chat_id": chat.id, "name": chat.name}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ✅ Optional: CRUD for Chat (list/create/delete)
class ChatListCreateView(generics.ListCreateAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer

class ChatDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
