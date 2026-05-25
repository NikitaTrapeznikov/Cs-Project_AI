import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def register_user(email, password):
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        return {"success": True, "data": response}
    except Exception as e:
        return {"success": False, "error": str(e)}

def login_user(email, password):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        return {"success": True, "data": response}
    except Exception as e:
        return {"success": False, "error": str(e)}