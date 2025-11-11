from supabase import create_client
from app.config import get_settings
from app.core.security import get_password_hash
from typing import Dict, Any

settings = get_settings()
supabase = create_client(settings.supabase_url, settings.supabase)

# Create a new user
async def create_user(user):
    hashed_pw = get_password_hash(user.password)
    data = {
        "username": user.username,
        "hashed_password": hashed_pw
    }
    response = supabase.table("users").insert(data).execute()
    return response
async def save_scenario(scenario: Dict[str, Any]) -> None:
    response = supabase.table("scenarios").insert(scenario).execute()
    
    if response.get("error"):
        raise RuntimeError(f"Failed to save scenario: {response['error']}")
    
# Get a user by username
async def get_user_by_username(username: str):
    response = supabase.table("users").select("*").eq("username", username).execute()
    return response.data[0] if response.data else None
