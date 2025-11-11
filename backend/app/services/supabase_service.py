from supabase import create_client
from app.config import get_settings
from app.core.security import get_password_hash

settings = get_settings()
supabase = create_client(settings.supabase_url, settings.supabase_key)

# Create a new user
async def create_user(user):
    hashed_pw = get_password_hash(user.password)
    data = {
        "username": user.username,
        "hashed_password": hashed_pw
    }
    response = supabase.table("users").insert(data).execute()
    return response

# Get a user by username
async def get_user_by_username(username: str):
    response = supabase.table("users").select("*").eq("username", username).execute()
    return response.data[0] if response.data else None
