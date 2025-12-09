"""Scenario generation and management business logic."""
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from app.services import gemini_service, cache_service
from app.services.supabase_service import (
    save_scenario,
    get_scenarios_by_career as db_get_scenarios,
    get_scenario_by_id as db_get_scenario,
    track_scenario_view as db_track_view
)
from app.core.logging import get_logger
from app.config import get_settings

settings = get_settings()
logger = get_logger(__name__)


# List of supported careers (could move to database later)
SUPPORTED_CAREERS = [
    "software engineer",
    "product manager",
    "ux designer",
    "data scientist",
    "marketing manager",
    "financial analyst",
    "teacher",
    "nurse",
    "sales representative",
    "hr manager"
]


async def generate_career_scenario(
    career_title: str,
    difficulty: str = "intermediate",
    focus_area: Optional[str] = None,
    is_coding: bool = False
) -> Dict[str, Any]:
    """
    Generate a new career scenario with intelligent caching.
    
    Flow:
    1. Validate and normalize input
    2. Check cache for similar scenario
    3. Generate new scenario via Gemini if cache miss
    4. Save to database
    5. Cache the result
    6. Return formatted scenario
    
    Args:
        career_title: The career to simulate (e.g., "software engineer")
        difficulty: beginner, intermediate, or advanced
        focus_area: Optional specific area to focus on
        
    Returns:
        Complete scenario with ID, text, options, and metadata
    """
    
    # 1. Validate and normalize
    career_title = _normalize_career_title(career_title)
    _validate_career_title(career_title)
    _validate_difficulty(difficulty)
    
    # 2. Generate cache key
    cache_key = _generate_scenario_cache_key(
        career_title=career_title,
        difficulty=difficulty,
        focus_area=focus_area
    )
    
    # 3. Check cache (scenarios are expensive to generate)
    if cached_scenario := await cache_service.get_cached(cache_key):
        logger.info(
            "scenario.cache_hit",
            cache_key=cache_key,
            career_title=career_title
        )
        return cached_scenario
    
    logger.info(
        "scenario.cache_miss",
        cache_key=cache_key,
        career_title=career_title
    )
    
    # 4. Generate new scenario via Gemini
    try:
        gemini_response = await gemini_service.generate_scenario(
            career_title=career_title,
            difficulty=difficulty,
            focus_area=focus_area,
            is_coding=is_coding
        )
    except Exception as e:
        logger.error("scenario.gemini_failed", error=str(e))
        
        # Fallback to pre-written scenario if available
        if fallback := await _get_fallback_scenario(career_title, difficulty):
            logger.warning("scenario.using_fallback", career_title=career_title)
            return fallback
        
        raise ValueError(f"Failed to generate scenario for {career_title}")
    
    # 5. Enrich with metadata
    scenario_id = str(uuid.uuid4())
    scenario = {
        "id": scenario_id,
        "career_title": career_title,
        "difficulty": difficulty,
        "focus_area": focus_area,
        "scenario_text": gemini_response["scenario"],
        "options": gemini_response.get("options", []), 
        "initial_code": gemini_response.get("initial_code"), 
        "correct_option": gemini_response.get("correct_option"),  # Optional
        "context": gemini_response.get("context", ""),
        "created_at": datetime.utcnow().isoformat(),
        "cached": False
    }
    
    # 6. Save to database (non-blocking, best effort)
    try:
        await save_scenario(scenario)
    except Exception as e:
        # Don't fail the request if DB save fails
        logger.error("scenario.db_save_failed", error=str(e))
    
    # 7. Cache the result
    await cache_service.set_cached(
        key=cache_key,
        value=scenario,
        ttl=settings.cache_ttl_scenario  # 1 hour default
    )
    
    logger.info(
        "scenario.generated",
        scenario_id=scenario_id,
        career_title=career_title,
        difficulty=difficulty
    )
    
    return scenario


async def get_scenarios_by_career(
    career_title: str,
    limit: int = 10,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """
    Retrieve previously generated scenarios for a career.
    
    This allows users to:
    - Browse available scenarios
    - Retry previous scenarios
    - See what challenges exist for a career
    """
    career_title = _normalize_career_title(career_title)
    
    try:
        scenarios = await db_get_scenarios(
            career_title=career_title,
            limit=limit,
            offset=offset
        )
        
        logger.info(
            "scenario.list_fetched",
            career_title=career_title,
            count=len(scenarios)
        )
        
        return scenarios
        
    except Exception as e:
        logger.error("scenario.list_fetch_failed", error=str(e))
        return []


async def get_scenario_by_id(scenario_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a specific scenario by ID.
    
    Uses cache-aside pattern:
    1. Check cache first
    2. Query database if cache miss
    3. Update cache with result
    """
    
    # Check cache
    cache_key = f"scenario:id:{scenario_id}"
    if cached := await cache_service.get_cached(cache_key):
        logger.info("scenario.cache_hit_by_id", scenario_id=scenario_id)
        return cached
    
    # Query database
    scenario = await db_get_scenario(scenario_id)
    
    if scenario:
        # Cache for future requests
        await cache_service.set_cached(
            key=cache_key,
            value=scenario,
            ttl=3600  # 1 hour
        )
    
    return scenario


async def track_scenario_view(
    scenario_id: str,
    user_id: Optional[str] = None
) -> None:
    """
    Track scenario views for analytics.
    
    This is fire-and-forget - failures don't affect user experience.
    """
    try:
        await db_track_view(scenario_id, user_id)
        logger.info("scenario.view_tracked", scenario_id=scenario_id)
    except Exception as e:
        logger.warning("scenario.view_tracking_failed", error=str(e))


# ==================== Helper Functions ====================

def _normalize_career_title(career_title: str) -> str:
    """Normalize career title for consistency."""
    return career_title.lower().strip()


def _validate_career_title(career_title: str) -> None:
    """Validate that career title is supported."""
    if not career_title:
        raise ValueError("Career title cannot be empty")
    
    if len(career_title) < 3:
        raise ValueError("Career title too short")
    
    if len(career_title) > 100:
        raise ValueError("Career title too long")
    
    # Optional: Check against supported list
    # if career_title not in SUPPORTED_CAREERS:
    #     raise ValueError(f"Career '{career_title}' is not supported yet")


def _validate_difficulty(difficulty: str) -> None:
    """Validate difficulty level."""
    valid_difficulties = ["beginner", "intermediate", "advanced"]
    
    if difficulty not in valid_difficulties:
        raise ValueError(
            f"Invalid difficulty '{difficulty}'. "
            f"Must be one of: {', '.join(valid_difficulties)}"
        )


def _generate_scenario_cache_key(
    career_title: str,
    difficulty: str,
    focus_area: Optional[str]
) -> str:
    """Generate cache key for scenario."""
    base_key = f"scenario:{career_title}:{difficulty}"
    
    if focus_area:
        import hashlib
        focus_hash = hashlib.md5(focus_area.encode()).hexdigest()[:8]
        base_key += f":{focus_hash}"
    
    return base_key


async def _get_fallback_scenario(
    career_title: str,
    difficulty: str
) -> Optional[Dict[str, Any]]:
    """
    Get a fallback scenario when AI generation fails.
    
    In production, these would be pre-written scenarios
    stored in the database or a JSON file.
    """
    # For now, return None
    # TODO: Implement fallback scenario system
    return None