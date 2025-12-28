from supabase import create_client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_image(file_path: str, file_name: str) -> str:
    with open(file_path, "rb") as f:
        supabase.storage.from_("plots").upload(
            file_name,
            f,
            {"content-type": "image/png"},
        )

    return supabase.storage.from_("plots").get_public_url(file_name)