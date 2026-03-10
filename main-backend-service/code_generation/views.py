from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import pandas as pd
import requests
from io import StringIO
import uuid

from .utils.code_generation_service import generate_code_openrouter  

from data_config.models import Prompt
from chat_config.models import Chat

from chat_config.utils.auto_generate_chat_name import generate_chat_name
from db_connection.utils.pool import get_connection_pool

class GenerateCodeView(APIView):
    def post(self, request):
        # Extract required fields from request
        prompt_text = request.data.get("prompt")
        model_name = request.data.get("model")
        chat_id = request.data.get("chat_id") 

        if not prompt_text or not model_name or not chat_id:
            return Response(
                {"error": "All fields are required: prompt, model, and chat_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

       
        try:
            chat = Chat.objects.get(id=chat_id)
            dataset_location = chat.dataset # This could be a URL or a DB Connection String
            source_type = chat.source_type
            
            if dataset_location.endswith("?"):
                dataset_location = dataset_location[:-1]  # remove trailing '?' if present
                
        except Chat.DoesNotExist:
            return Response(
                {
                    "error": f"No Chat found with id {chat_id}"
                },status=status.HTTP_404_NOT_FOUND,
            )

        # Fetch dataset preview based on source type
        try:
            if source_type == "database_url":
                # For DB, fetch preview from the connected pool and specific table
                table_name = chat.table_name or chat.name # Prefer table_name, fallback to name
                pool = get_connection_pool(str(chat.id), dataset_location)
                conn = pool.getconn()
                try:
                    query = f'SELECT * FROM "{table_name}" LIMIT 5'
                    df = pd.read_sql(query, conn)
                    data_preview = df.to_string()
                finally:
                    pool.putconn(conn)
            else:
                # Standard file-based URL fetch
                response = requests.get(dataset_location)
                response.raise_for_status()
            
                csv_data = StringIO(response.text)
                df = pd.read_csv(csv_data)
                data_preview = df.head(5).to_string()
        
        except Exception as e:
            return Response(
                {
                    "error": f"Failed to read dataset: {str(e)}"
                    },status=status.HTTP_400_BAD_REQUEST,
            )
            
        # Generate Python code using model
        generated_code = generate_code_openrouter(
            data_preview=data_preview,
            user_operation=prompt_text,
            chosen_model=model_name,
        )

        if not generated_code:
            return Response(
                {"error": "Failed to generate code from model."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Clean output (remove formatting)
        generated_code = generated_code.replace("```python", "").replace("```", "").strip()

        # Automatic Chat Renaming on first prompt
        new_chat_name = None
        if not chat.name_generated:
            try:
                new_chat_name = generate_chat_name(prompt_text)
                chat.name = new_chat_name
                chat.name_generated = True
                chat.save()
            except Exception as e:
                print(f"[RENAME ERR] Failed to auto-generate chat name: {str(e)}")

        # Save generated code linked to the Chat
        try:
            prompt_obj = Prompt.objects.create(
                prompt=prompt_text,
                generated_code=generated_code,
                chat_id=chat 
            )
            
        except Exception as e:
            return Response(
                {
                    "error": f"Failed to save generated code: {str(e)}"
                },status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Return the generated code and prompt_id in response
        return Response(
            {
                "generated_code": generated_code,
                "prompt_id": prompt_obj.id,
                "updated_chat_name": new_chat_name
            },status=status.HTTP_200_OK,
        )
