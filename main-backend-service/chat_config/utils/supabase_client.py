from supabase import create_client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
# Use service role key for storage operations (has admin privileges)
# If SUPABASE_SERVICE_ROLE_KEY is not set, fall back to SUPABASE_KEY
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY (or SUPABASE_SERVICE_ROLE_KEY) must be set in environment variables")

print(f"[SUPABASE] URL: {SUPABASE_URL}")
print(f"[SUPABASE] Key configured: {'Yes' if SUPABASE_KEY else 'No'}")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
