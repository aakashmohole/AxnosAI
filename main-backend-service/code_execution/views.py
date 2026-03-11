import os
import re
import uuid
import pandas as pd
import requests
from io import StringIO
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from data_config.models import Prompt
from .utils.utils  import execute_in_docker
from .utils.supabase_client import upload_to_supabase
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

            # 🔹 Inject and Clean generated code
            import re
            
            # Clean output fencing
            cleaned_code = (
                generated_code.replace("```python", "")
                .replace("```", "")
                .strip()
            )

            # Prepend essential imports and initial data loading
            # This ensures 'df' is available even if not assigned in the generated code
            data_injection = "import pandas as pd\nimport matplotlib.pyplot as plt\n"
            data_injection += "df = pd.read_csv('/outputs/data.csv')\n\n"
            
            # Patterns to replace common data loading/mocking (e.g., df = pd.read_csv('sample.csv'))
            # We want to replace assignments to typical variable names like 'df', 'data', 'dataset'
            patterns = [
                r'^(\s*)(df|data|dataset)\s*=\s*pd\.read_\w+\(.*\)',
                r'^(\s*)(df|data|dataset)\s*=\s*pd\.DataFrame\(.*\)',
            ]
            
            lines = cleaned_code.split('\n')
            final_processed_lines = []
            
            for line in lines:
                matched = False
                for pattern in patterns:
                    if re.match(pattern, line.strip()):
                        m = re.match(pattern, line.strip())
                        indent = m.group(1)
                        var_name = m.group(2)
                        # Comment out the old line and inject our loading
                        final_processed_lines.append(f"{indent}# Replaced by system: {line.strip()}")
                        final_processed_lines.append(f"{indent}{var_name} = pd.read_csv('/outputs/data.csv')")
                        matched = True
                        break
                
                if not matched:
                    final_processed_lines.append(line)

            # Prepare code with non-interactive backend and plot saving replacements
            code_lines = "\n".join(final_processed_lines)
            
            # Inject matplotlib setup at the very top
            data_injection = "import matplotlib\nmatplotlib.use('Agg')\nimport matplotlib.pyplot as plt\n" + data_injection
            
            # Replace plt.show() with plt.savefig logic
            # Use a regex to find plt.show() and replace it with a unique savefig call
            import re
            def replace_show(match):
                plot_id = f"plot_{uuid.uuid4().hex}"
                return f"plt.savefig(f'/outputs/{plot_id}.png'); plt.close()"
            
            processed_code_body = re.sub(r'plt\.show\(\)', replace_show, code_lines)
            
            final_code = data_injection + "\n" + processed_code_body
            
            # Append result saving logic to ensure we always have a downloadable file if data was processed
            # We iterate through locals in reverse to find the most recently created DataFrame
            final_code += "\n\n# System: Save final result if exists\n"
            final_code += "import pandas as pd\n"
            final_code += "import os\n"
            final_code += "result_found = False\n"
            final_code += "for var_name in reversed(list(locals().keys())):\n"
            final_code += "    if var_name.startswith('_'): continue\n"
            final_code += "    val = locals()[var_name]\n"
            final_code += "    if isinstance(val, pd.DataFrame):\n"
            final_code += "        val.to_csv('/outputs/result.csv', index=False)\n"
            final_code += "        print('\\n--- RESULT DATAFRAME ---')\n"
            final_code += "        print(val)\n"
            final_code += "        result_found = True\n"
            final_code += "        break\n"
            final_code += "\nif not result_found:\n"
            final_code += "    if any(f.endswith('.png') for f in os.listdir('/outputs')):\n"
            final_code += "        print('\\n[INFO] Result plot available in Charts tab')\n"

            print("--- FINAL CODE TO EXECUTE ---")
            print(final_code)
            print("-----------------------------")

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
            download_url = None
            output_dir = "/tmp/docker_outputs/"
            for file_name in os.listdir(output_dir):
                file_path = os.path.join(output_dir, file_name)
                if file_name.endswith(".png"):
                    url = upload_to_supabase(file_path, f"{pk}/{file_name}", bucket_name="plots", content_type="image/png")
                    image_urls.append(url)
                elif file_name == "result.csv":
                    download_url = upload_to_supabase(file_path, f"{pk}/result.csv", bucket_name="results", content_type="text/csv")

            return Response(
                {
                    "output": execution_result.get("output", ""), 
                    "image_urls": image_urls,
                    "download_url": download_url
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateGeneratedCodeView(APIView):
    """
    Update the generated code stored on the Prompt model.

    URL: PATCH /code-execution/update/<prompt_id>/
    Body:
      - code: the updated python code string.
    """

    def patch(self, request, pk):
        try:
            prompt = get_object_or_404(Prompt, pk=pk)
            new_code = request.data.get("code")
            
            if new_code is None:
                return Response(
                    {"error": "Code field is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            prompt.generated_code = new_code
            prompt.save()
            
            return Response(
                {"message": "Code updated successfully", "code": prompt.generated_code},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

