from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework import status
from django.shortcuts import get_object_or_404
from chat_config.models import Chat
from .utils.supabase_client import supabase


class UploadDatasetView(APIView):
from django.shortcuts import render
# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser,JSONParser
from django.conf import settings
from .utils.supabase_client import supabase
from rest_framework import status
from django.shortcuts import get_object_or_404
from chat_config.models import Chat
from chat_config.serializers import ChatSerializer
import uuid
import pandas as pd


class UploadDatasetView(APIView):
    parser_classes = [MultiPartParser, FormParser,JSONParser]

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES['file']
        bucket_name = "dataset_files"

        # Upload to Supabase Storage
        res = supabase.storage.from_(bucket_name).upload(file_obj.name, file_obj.read(), {
            "content-type": file_obj.content_type
        })
        print(res)

        # Get public URL
        public_url = supabase.storage.from_(bucket_name).get_public_url(file_obj.name)

        return Response({
            "message": "File uploaded successfully",
            "public_url": public_url
        })
        
class UploadDatasetToChatView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request, pk):
        chat = get_object_or_404(Chat, pk=pk)
        bucket_name = "dataset_files"

        source_type = request.data.get("source_type")
        if not source_type:
            return Response(
                {"error": "source_type is required (file or database_url)"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ FILE UPLOAD
        if source_type == "file":
            if "file" not in request.FILES:
                return Response(
                    {"error": "file is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if not source_type:
            return Response({"error": "source_type is required (file or database_url)"},
                            status=status.HTTP_400_BAD_REQUEST)

        # 🔹 Case 1: File upload
        if source_type == "file":
            if "file" not in request.FILES:
                return Response({"error": "No file uploaded"},
                                status=status.HTTP_400_BAD_REQUEST)

            file_obj = request.FILES["file"]
            file_path = f"{pk}_{file_obj.name}"

            try:
                supabase.storage.from_(bucket_name).upload(
                    file_path,
                    file_obj.read(),
                    {"content-type": file_obj.content_type}
                )
            except Exception:
                supabase.storage.from_(bucket_name).update(
                    file_path,
                    file_obj.read(),
                    {"content-type": file_obj.content_type}
                )

            public_url = supabase.storage.from_(bucket_name).get_public_url(file_path)

            chat.dataset = public_url
            chat.source_type = "file"
            chat.save()

            return Response({
                "message": "File uploaded and dataset updated successfully",
                "chat_id": chat.id,
                "dataset_url": public_url
            }, status=status.HTTP_200_OK)

        # ✅ DATABASE URL
        if source_type == "database_url":
            database_url = request.data.get("database_url")
            if not database_url:
                return Response(
                    {"error": "database_url is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            chat.dataset = database_url
            chat.source_type = "database_url"
            chat.save()

            return Response({
                "message": "Database URL saved successfully",
                "chat_id": chat.id,
                "dataset_url": database_url
            }, status=status.HTTP_200_OK)

        return Response(
            {"error": "Invalid source_type"},
            status=status.HTTP_400_BAD_REQUEST
        )
            chat.dataset = public_url
            chat.source_type = "file"

        # 🔹 Case 2: Database URL
        elif source_type == "database_url":
            database_url = request.data.get("database_url")
            if not database_url:
                return Response({"error": "database_url is required when source_type=database_url"},
                                status=status.HTTP_400_BAD_REQUEST)

            chat.dataset = database_url
            chat.source_type = "database_url"

        else:
            return Response({"error": "Invalid source_type (choose 'file' or 'database_url')"},
                            status=status.HTTP_400_BAD_REQUEST)

        chat.save()

        if source_type == "file":
            message = "Dataset added successfully."
        else:
            message = "Database url added successfully."

        return Response({
            "chat_id": chat.id,
            "source_type": chat.source_type,
            "dataset_url": chat.dataset,
            "message": message
        }, status=status.HTTP_200_OK)
