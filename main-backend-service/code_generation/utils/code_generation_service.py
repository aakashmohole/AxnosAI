from typing import Optional
from openai import OpenAI  
from django.conf import settings

import logging  

logger = logging.getLogger(__name__)

AVAILABLE_MODELS = {
    "mistral": "mistralai/mistral-nemo",
    "deepseek": "deepseek/deepseek-chat",
    "llama": "meta-llama/llama-3.1-8b-instruct",
}


def generate_code_openrouter(data_preview: str, user_operation: str, chosen_model: str = "mistral") -> Optional[str]:
    model_id = AVAILABLE_MODELS.get(chosen_model, AVAILABLE_MODELS["mistral"])

    
    api_key = getattr(settings, "OPENROUTER_API_KEY", None)
    if not api_key:
        logger.error("OPENROUTER_API_KEY not found in Django settings.")
        return None

    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

    try:
        
        completion = client.chat.completions.create(
            model=model_id,
            max_tokens=3000,      
            temperature=0.7,      
            messages=[
                {
                    "role": "system",
                    "content": "You are a Python code generator using pandas. Respond only with clean, executable Python code without explanations."
                },
                {
                    "role": "user",
                    "content": f"Dataset sample:\n{data_preview}\n\nWrite Python code using pandas to: {user_operation}"
                }
            ]
        )
        # print(completion.choices[0].message.content)
        return completion.choices[0].message.content

    except Exception as exc:
        # Log the exact exception for troubleshooting (avoid printing)
        logger.exception("OpenRouter API call failed: %s", exc)
        return None
