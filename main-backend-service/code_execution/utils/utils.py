import os
import subprocess
from typing import Dict, Optional


def execute_in_docker(code_to_execute: str, timeout_seconds: int = 60) -> Dict[str, Optional[str]]:
    os.makedirs("/tmp/docker_outputs", exist_ok=True)
    image_name = "data-sci-executor"

    # 1️⃣ Build image (only if not exists)
    build_cmd = ["docker", "image", "inspect", image_name]

    try:
        subprocess.run(build_cmd, capture_output=True, check=True)
        print("[DOCKER]: Image found, skipping build.")
    except subprocess.CalledProcessError:
        # image not found → build it
        subprocess.run(
            ["docker", "build", "-t", image_name, "."],
            capture_output=True,
            text=True,
            check=True,
        )
        print("[DOCKER]: Image built successfully.")

    # 2️⃣ Run container
    docker_command = [
        "docker",
        "run",
        "--rm",
        "--network", "none",
        "--memory", "2g",
        "--cpus", "1",
        "--read-only",

        "--env", "MPLCONFIGDIR=/outputs",
        "-v", "/tmp/docker_outputs:/outputs",
        image_name,
        "python",
        "-c",
        code_to_execute,
    ]

    try:
        result = subprocess.run(
            docker_command,
            capture_output=True,
            text=True,
            check=True,
            timeout=timeout_seconds + 5,
        )
        return {"output": result.stdout, "error": None, "files": os.listdir("/tmp/docker_outputs/")}

    except subprocess.CalledProcessError as e:
        return {"output": None, "error": e.stderr, "files": []}

    except subprocess.TimeoutExpired:
        return {"output": None, "error": "Execution timed out.", "files": []}

