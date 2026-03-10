from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import requests
import os
import tempfile
import logging

logger = logging.getLogger(__name__)

class TranscriptionView(APIView):
    """
    API endpoint to transcribe audio to text using Hugging Face Inference API.
    """

    def post(self, request):
        logger.info("[Transcription] Received transcription request (Hugging Face)")
        
        if 'audio' not in request.FILES:
            logger.warning("[Transcription] No audio file in request")
            return Response({"error": "No audio file provided"}, status=status.HTTP_400_BAD_REQUEST)

        audio_file = request.FILES['audio']
        user_id = request.headers.get('X-User-ID', 'unknown')
        logger.info(f"[Transcription] Processing audio for user: {user_id}")

        hf_token = settings.HUGGINGFACE_API_TOKEN
        model_id = settings.HF_TRANSCRIPTION_MODEL
        # New Hugging Face router URL (api-inference.huggingface.co is deprecated)
        api_url = f"https://router.huggingface.co/hf-inference/models/{model_id}"

        if not hf_token or hf_token == "hf_your_token_here":
             logger.warning("[Transcription] Hugging Face API token is missing or invalid")
             return Response({"error": "Hugging Face API token is not configured. Please add HUGGINGFACE_API_TOKEN to your .env file."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            audio_data = audio_file.read()
            headers = {
                "Authorization": f"Bearer {hf_token}",
                "Content-Type": "audio/webm", # Explicitly set content type
                "Accept": "application/json"
            }
            
            logger.info(f"[Transcription] Sending audio to Hugging Face via Router ({model_id})...")
            response = requests.post(api_url, headers=headers, data=audio_data)
            
            if response.status_code == 403 or (response.status_code == 400 and "permissions" in response.text):
                logger.error(f"[Transcription] Permission error: {response.text}")
                return Response({
                    "error": "Hugging Face token has insufficient permissions. Please ensure your token has 'Make calls to Inference Providers' scope enabled in Hugging Face settings.",
                    "details": response.json() if response.headers.get('Content-Type') == 'application/json' else response.text
                }, status=status.HTTP_403_FORBIDDEN)

            if response.status_code != 200:
                logger.error(f"[Transcription] HF API error: {response.status_code} - {response.text}")
                return Response({"error": f"Hugging Face API error: {response.text}"}, status=response.status_code)

            result = response.json()
            transcript_text = result.get("text", "")
            
            if not transcript_text:
                logger.warning(f"[Transcription] Empty transcript received: {result}")
                return Response({"error": "No transcription text received from model"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            logger.info(f"[Transcription] Transcription successful: {transcript_text[:50]}...")
            return Response({"text": transcript_text}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"[Transcription] Error during transcription: {str(e)}")
            return Response({"error": f"Transcription failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)