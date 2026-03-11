from supabase import create_client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_to_supabase(file_path: str, file_name: str, bucket_name: str = "plots", content_type: str = "image/png") -> str:
    """
    Directly upload a file to Supabase storage.
    Expects buckets like 'plots' and 'results' to exist.
    """
    with open(file_path, "rb") as f:
        try:
            supabase.storage.from_(bucket_name).upload(
                file_name,
                f,
                {"content-type": content_type, "upsert": "true"},
            )
        except Exception as e:
            print(f"Failed to upload '{file_name}' to '{bucket_name}': {e}")
            print(f"Error Detail: Please verify that bucket '{bucket_name}' exists and has Public/Insert policies.")

    return supabase.storage.from_(bucket_name).get_public_url(file_name)