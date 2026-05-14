from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import pandas as pd
import requests
from io import StringIO
import uuid

from .utils.code_generation_service import generate_code_openrouter, AVAILABLE_MODELS

from data_config.models import Prompt
from chat_config.models import Chat

from chat_config.utils.auto_generate_chat_name import generate_chat_name
from db_connection.utils.pool import get_connection_pool

class ModelListView(APIView):
    def get(self, request):
        # Return a list of available models with metadata
        models = [
            {"id": "mistral", "name": "Mistral Nemo", "description": "Fast and efficient"},
            {"id": "deepseek", "name": "DeepSeek Chat", "description": "High reasoning capabilities"},
            {"id": "llama", "name": "Llama 3.1 8B", "description": "Meta's latest powerful model"},
            {"id": "openai/gpt-4o-mini", "name": "GPT-4o Mini", "description": "OpenAI's efficient mini model"},
        ]
        return Response(models, status=status.HTTP_200_OK)

from django.http import StreamingHttpResponse
import json

class GenerateCodeView(APIView):
    def post(self, request):
        prompt_text = request.data.get("prompt")
        model_name = request.data.get("model")
        chat_id = request.data.get("chat_id") 
        is_stream = request.data.get("stream", True) # Default to streaming for speed

        if not prompt_text or not model_name or not chat_id:
            return Response({"error": "Fields required: prompt, model, chat_id"}, status=400)

        try:
            chat = Chat.objects.get(id=chat_id)
            dataset_location = chat.dataset
            source_type = chat.source_type
            if dataset_location.endswith("?"): dataset_location = dataset_location[:-1]
        except Chat.DoesNotExist:
            return Response({"error": "Chat not found"}, status=404)

        # Fetch preview (cached logic simplified here for speed)
        try:
            if source_type == "database_url":
                pool = get_connection_pool(str(chat.id), dataset_location)
                conn = pool.getconn()
                try:
                    df = pd.read_sql(f'SELECT * FROM "{chat.table_name or chat.name}" LIMIT 5', conn)
                    data_preview = df.to_string()
                finally: pool.putconn(conn)
            else:
                resp = requests.get(dataset_location, timeout=10)
                resp.raise_for_status()
                df = pd.read_csv(StringIO(resp.text), nrows=5)
                data_preview = df.to_string()
        except Exception as e:
            return Response({"error": f"Dataset error: {str(e)}"}, status=400)
            
        # Call with streaming
        stream_resp = generate_code_openrouter(
            data_preview=data_preview,
            user_operation=prompt_text,
            chosen_model=model_name,
            stream=is_stream
        )

        if not stream_resp:
            return Response({"error": "Model failed"}, status=500)

        if not is_stream:
            return Response({"generated_code": stream_resp}, status=200)

        def stream_generator():
            full_content = ""
            # yield metadata first
            yield f"data: {json.dumps({'type': 'start', 'chat_id': chat.id})}\n\n"
            
            for chunk in stream_resp:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_content += content
                    yield f"data: {json.dumps({'type': 'chunk', 'content': content})}\n\n"
            
            # Auto-rename and save at the end
            if not chat.name_generated:
                try:
                    new_name = generate_chat_name(prompt_text)
                    chat.name = new_name
                    chat.name_generated = True
                    chat.save()
                    yield f"data: {json.dumps({'type': 'rename', 'name': new_name})}\n\n"
                except: pass

            # Save to DB
            clean_code = full_content.replace("```python", "").replace("```", "").strip()
            prompt_obj = Prompt.objects.create(
                prompt=prompt_text,
                generated_code=clean_code,
                chat_id=chat 
            )
            yield f"data: {json.dumps({'type': 'end', 'prompt_id': prompt_obj.id, 'full_code': clean_code})}\n\n"

        return StreamingHttpResponse(stream_generator(), content_type="text/event-stream")
