from supabase import create_client
from app.config import get_settings
from app.core.security import get_password_hash
from typing import Dict, Any, List, Optional

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
async def save_scenario(scenario: Dict[str, Any]) -> None:
    response = supabase.table("scenarios").insert(scenario).execute()
    
    if response.get("error"):
        raise RuntimeError(f"Failed to save scenario: {response['error']}")
    
# Get a user by username
async def get_user_by_username(username: str):
    response = supabase.table("users").select("*").eq("username", username).execute()
    return response.data[0] if response.data else None
async def get_scenarios_by_career(career_title: str, limit: int, offset: int) -> List[Dict[str, Any]]:
    """Placeholder for fetching scenarios. Returns an empty list."""
    print(f"MOCK: Getting scenarios for '{career_title}'")
    return []

async def get_scenario_by_id(scenario_id: str) -> Optional[Dict[str, Any]]:
    """Placeholder for fetching a single scenario. Returns None."""
    print(f"MOCK: Getting scenario by ID '{scenario_id}'")
    return None

async def track_scenario_view(scenario_id: str, user_id: Optional[str] = None):
    """Placeholder for tracking analytics."""
    print(f"MOCK: Tracking view for scenario '{scenario_id}'")
    pass
async def save_evaluation(
    user_id: str,
    scenario_id: str,
    user_answer: str,
    score: int,
    feedback: str
):
    """Save an evaluation to the Supabase 'evaluations' table."""
    try:
        data = {
            "user_id": user_id,
            "scenario_id": scenario_id,
            "user_answer": user_answer,
            "score": score,
            "feedback": feedback
        }

        response = supabase.table("evaluations").insert(data).execute()

        if response.data:
            print(f"✅ Saved evaluation for user {user_id} and scenario {scenario_id}")
        else:
            print(f"⚠️ Failed to save evaluation: {response.error}")
        
        return response.data

    except Exception as e:
        print(f"❌ Error saving evaluation: {e}")
        return None