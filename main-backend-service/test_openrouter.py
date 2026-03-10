import requests

api_key = "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"

try:
    response = requests.get(
        url="https://openrouter.ai/api/v1/models",
        headers={"Authorization": f"Bearer {api_key}"}
    )
    if response.ok:
        models = response.json()['data']
        openai_models = [m['id'] for m in models if 'openai' in m['id'].lower()]
        print(f"OpenAI models ({len(openai_models)}): {openai_models}")
    else:
        print(f"Failed to fetch models: {response.text}")

except Exception as e:
    print(f"Error: {str(e)}")
