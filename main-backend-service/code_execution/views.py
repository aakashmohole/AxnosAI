import os
import pandas as pd
import requests
from io import StringIO
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from data_config.models import Prompt
from .utils.utils  import execute_in_docker
from .utils.supabase_client import upload_image
from db_connection.utils.pool import get_connection_pool

class ExecuteGeneratedCodeView(APIView):
    """
    Execute previously generated code (stored on the Prompt model) inside Docker.

    URL: POST /code-execution/execute/<prompt_id>/
    Body (optional):
      - timeout_seconds: max seconds to allow execution (default 60).
    """

    def post(self, request, pk):
        try:
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
            chat = prompt.chat_id
            
            generated_code = (prompt.generated_code or "").strip()
            if not generated_code:
                return Response(
                    {"[MAIN ERROR]": "No generated_code found for this prompt"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 🔹 Prepare data for execution
            os.makedirs("/tmp/docker_outputs/", exist_ok=True)
            # Clean previous outputs
            for f in os.listdir("/tmp/docker_outputs/"):
                if os.path.isfile(os.path.join("/tmp/docker_outputs/", f)):
                    os.remove(os.path.join("/tmp/docker_outputs/", f))

            try:
                if chat.source_type == "database_url":
                    table_name = chat.table_name or chat.name
                    pool = get_connection_pool(str(chat.id), chat.dataset)
                    conn = pool.getconn()
                    try:
                        query = f'SELECT * FROM "{table_name}"'
                        df_all = pd.read_sql(query, conn)
                        df_all.to_csv("/tmp/docker_outputs/data.csv", index=False)
                    finally:
                        pool.putconn(conn)
                else:
                    response = requests.get(chat.dataset)
                    response.raise_for_status()
                    df_all = pd.read_csv(StringIO(response.text))
                    df_all.to_csv("/tmp/docker_outputs/data.csv", index=False)

            except Exception as e:
                return Response(
                    {"[MAIN ERROR]": f"Failed to prepare data for execution: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            # 🔹 Inject data loading code
            # We prepend code to load the csv we just created
            data_injection = "import pandas as pd\nimport matplotlib.pyplot as plt\n"
            data_injection += "df = pd.read_csv('/outputs/data.csv')\n"
            
            # Clean output fencing
            cleaned_code = (
                generated_code.replace("```python", "")
                .replace("```", "")
                .strip()
            )
            
            final_code = data_injection + cleaned_code

            execution_result = execute_in_docker(
                code_to_execute=final_code,
                timeout_seconds=timeout_seconds,
            )

            if execution_result.get("error"):
                return Response(
                    {"[MAIN ERROR]": execution_result["error"]},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            image_urls = []
            output_dir = "/tmp/docker_outputs/"
            for file_name in os.listdir(output_dir):
                if file_name.endswith(".png"):
                    file_path = os.path.join(output_dir, file_name)
                    url = upload_image(file_path, f"{pk}/{file_name}")
                    image_urls.append(url)

            return Response(
                {"output": execution_result.get("output", ""), "image_urls": image_urls},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

