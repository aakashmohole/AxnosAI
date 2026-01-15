import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from data_config.models import Prompt
from .utils.utils  import execute_in_docker
from .utils.supabase_client import upload_image

class ExecuteGeneratedCodeView(APIView):
    """
    Execute previously generated code (stored on the Prompt model) inside Docker.

    URL: POST /code-execution/execute/<prompt_id>/
    Body (optional):
      - timeout_seconds: max seconds to allow execution (default 60).
    """

    def post(self, request, pk):
        prompt_id = pk  # Get prompt_id from URL parameter
        timeout_seconds = request.data.get("timeout_seconds", 60)

        try:
            timeout_seconds = int(timeout_seconds)
        except (TypeError, ValueError):
            return Response(
                {"[MAIN ERROR]": "timeout_seconds must be an integer"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        prompt = get_object_or_404(Prompt, id=prompt_id)

        generated_code = (prompt.generated_code or "").strip()
        if not generated_code:
            return Response(
                {"[MAIN ERROR]": "No generated_code found for this prompt"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Optional: clean any leftover markdown fencing if present
        cleaned_code = (
            generated_code.replace("```python", "")
            .replace("```", "")
            .strip()
        )

        execution_result = execute_in_docker(
            code_to_execute=cleaned_code,
            timeout_seconds=timeout_seconds,
        )

        if execution_result.get("error"):
            return Response(
                {"[MAIN ERROR]": execution_result["error"]},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        image_urls = []

        for file_name in execution_result["files"]:
            if file_name.endswith(".png"):
                file_path = os.path.join("/tmp/docker_outputs/", file_name)
                url = upload_image(file_path, f"{pk}/{file_name}")
                image_urls.append(url)

        return Response(
            {"output": execution_result.get("output", ""), "image_urls": image_urls},
            status=status.HTTP_200_OK,
        )

