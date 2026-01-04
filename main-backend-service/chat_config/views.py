from django.core.exceptions import PermissionDenied, ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from django.shortcuts import get_object_or_404
from .models import Chat
from .serializers import ChatSerializer, ChatNameGenerateSerializer, ChatNameUpdateSerializer
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from collections import Counter
from .utils.auto_generate_chat_name import generate_chat_name
from db_connection.utils.pool import get_connection_pool
from chat_config.utils.supabase_client import supabase
import pandas as pd
import numpy as np


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


class CreateChatWithDatasetView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def post(self, request):
        user_id = request.META.get("HTTP_X_USER_ID")
        if not user_id:
            return Response({"[MAIN ERR]": "User not authenticated"}, status=401)
        
        source_type = request.data.get("source_type")
        if not source_type:
            return Response({"[MAIN ERR]": "Source type not provided"}, status=400)
        
        # create chat first
        chat = Chat.objects.create(user_id=user_id, source_type=source_type)

        preview = None
        bucket_name = "dataset_files"

        # file upload flow
        if source_type == "file":
            file_object = request.FILES.get("file")
            if not file_object: 
                return Response({"[MAIN ERR]": "File not provided"}, status=400)
            
            file_path = f"{chat.id}_{file_object.name}"
            supabase.storage.from_(bucket_name).upload(
                file_path,
                file_object.read(),
                {"content-type": file_object.content_type}
            )

            public_url = supabase.storage.from_(bucket_name).get_public_url(file_path)
            chat.dataset = public_url
            chat.save()

             # 🔹 Preview (CSV example)
            file_object.seek(0)
            df = pd.read_csv(file_object)
            df = df.fillna("")  # Handle missing values
            preview = df.head(5).to_dict(orient="records")

        elif source_type == "database_url":
            database_url = request.data.get("database_url")
            if not database_url:
                return Response({"[MAIN ERR]": "URL not provided"}, status=400)
            
            chat.dataset = database_url
            chat.save()
            
            # 🔹 Fetch tables preview
            pool = get_connection_pool(chat.id, database_url)
            conn = pool.getconn()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
            )
            tables = [row[0] for row in cursor.fetchall()]

            preview = {"tables": tables}

            cursor.close()
            pool.putconn(conn)
        else:
            return Response({"[MAIN ERR]": "Invalid source type"}, status=400)
        
        return Response({
            "message": "Chat created successfully",
            "chat": ChatSerializer(chat).data,
            "preview": preview
        }, status = status.HTTP_201_CREATED) 

            
class FetchTablePreviewAPIView(APIView):
    """
    Fetch preview data for selected tables
    (No chat_id needed)
    """

    def post(self, request):
        database_url = request.data.get("database_url")
        tables = request.data.get("tables")

        if not database_url:
            return Response(
                {"[MAIN ERR]": "database_url is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not tables or not isinstance(tables, list):
            return Response(
                {"[MAIN ERR]": "tables must be a list"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            pool = get_connection_pool("preview", database_url)
            conn = pool.getconn()

            preview = {}

            for table in tables:
                query = f'SELECT * FROM "{table}" LIMIT 20'
                df = pd.read_sql(query, conn)

                # JSON safe
                df = df.replace({np.nan: None})

                preview[table] = {
                    "columns": list(df.columns),
                    "rows": df.to_dict(orient="records")
                }

                if(preview[table]["rows"] == []):
                    preview[table]["rows"] = "Table is empty"
                    

            pool.putconn(conn)

            return Response({
                "preview": preview
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ListUserChatsView(generics.ListAPIView):
    serializer_class = ChatSerializer

    def get_queryset(self):
        user_id = self.request.META.get("HTTP_X_USER_ID")
        if not user_id:
            raise PermissionDenied("User not authenticated")
        return Chat.objects.filter(user_id=user_id).order_by('-created_At')

class ChatDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    
    def get_object(self):
        obj = super().get_object()
        user_id = self.request.META.get("HTTP_X_USER_ID")
        if not user_id or str(user_id) != str(obj.user_id):
            raise PermissionDenied("Not allowed")
        return obj
