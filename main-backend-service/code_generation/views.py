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
            dataset_url = chat.dataset
            
            if dataset_url.endswith("?"):
                dataset_url = dataset_url[:-1]  # remove trailing '?' if present
                
        except Chat.DoesNotExist:
            return Response(
                {
                    "error": f"No Chat found with id {chat_id}"
                },status=status.HTTP_404_NOT_FOUND,
            )

        # Fetch dataset from the given URL
        try:
            response = requests.get(dataset_url)
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

        # Save generated code linked to the Chat
        try:
            Prompt.objects.create(
                generated_code=generated_code,
                chat_id=chat 
            )
            
        except Exception as e:
            return Response(
                {
                    "error": f"Failed to save generated code: {str(e)}"
                },status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Return the generated code in response
        return Response(
            {
                "generated_code": generated_code
            },status=status.HTTP_200_OK,
        )
