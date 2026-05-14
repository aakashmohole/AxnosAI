from typing import Optional
from openai import OpenAI  
from django.conf import settings

import logging  

logger = logging.getLogger(__name__)

AVAILABLE_MODELS = {
    "mistral": "mistralai/mistral-nemo",
    "deepseek": "deepseek/deepseek-chat",
    "llama": "meta-llama/llama-3.1-8b-instruct",
    "openai/gpt-4o-mini": "openai/gpt-4o-mini",
}


def generate_code_openrouter(data_preview: str, user_operation: str, chosen_model: str = "mistral", stream: bool = False):
    model_id = AVAILABLE_MODELS.get(chosen_model, AVAILABLE_MODELS["mistral"])
    api_key = getattr(settings, "OPENROUTER_API_KEY", None)
    
    if not api_key:
        logger.error("OPENROUTER_API_KEY not found in Django settings.")
        return None

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1", 
        api_key=api_key,
        timeout=60.0
    )

    try:
        completion = client.chat.completions.create(
            model=model_id,
            max_tokens=2000,      
            temperature=0.7,
            stream=stream,
            messages=[
                {
                    "role": "system",
                    "content": "You are a Python code generator using pandas. Respond only with clean, executable Python code without explanations. If the user wants normal conversation, respond normally."
                },
                {
                    "role": "user",
                    "content": f"Dataset sample:\n{data_preview}\n\nTask: {user_operation}"
                }
            ]
        )
        
        if stream:
            return completion
        
        return completion.choices[0].message.content

    except Exception as exc:
        print(f"[OPENROUTER ERR]: {str(exc)}")
        logger.exception("OpenRouter API call failed")
        return None
