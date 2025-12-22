"""Evaluation business logic and orchestration."""
from typing import Dict, Any
import asyncio
import hashlib
from app.services import gemini_service, cache_service
from app.services.supabase_service import save_evaluation
from app.core.logging import get_logger

logger = get_logger(__name__)


async def evaluate_user_answer(
    career_title: str,
    scenario_text: str,
    user_answer: str,
    scenario_id: str,
    user_id: str = None
) -> Dict[str, Any]:
    """
    Evaluate a user's answer with caching and persistence.
    
    This function:
    1. Checks cache for existing evaluation
    2. Calls Gemini API if cache miss
    3. Saves result to database
    4. Returns formatted evaluation
    
    Args:
        career_title: The career being simulated
        scenario_text: The full scenario text
        user_answer: User's selected answer
        scenario_id: ID of the scenario
        user_id: Optional user ID for tracking
        
    Returns:
        Dict with feedback, score, and explanation
    """
    
    # 1. Generate cache key
    cache_key = _generate_cache_key(
        career_title=career_title,
        scenario_id=scenario_id,
        user_answer=user_answer
    )
    
    # 2. Check cache
    if cached_result := await cache_service.get_cached(cache_key):
        logger.info("evaluation.cache_hit", cache_key=cache_key)
        return cached_result
    
    logger.info("evaluation.cache_miss", cache_key=cache_key)
    
    # 3. Call Gemini API through gemini_service
    try:
        evaluation = await gemini_service.generate_evaluation(
            career_title=career_title,
            scenario_text=scenario_text,
            user_answer=user_answer
        )
    except Exception as e:
        logger.error("evaluation.gemini_failed", error=str(e))
        raise
    
    # 4. Add metadata
    result = {
        **evaluation,
        "scenario_id": scenario_id,
        "career_title": career_title,
        "cached": False
    }
    
    # 5. Cache the result (do this first for faster response)
    await cache_service.set_cached(
        key=cache_key,
        value=result,
        ttl=1800  # 30 minutes
    )
    
    # 6. Save to database (truly non-blocking fire-and-forget using background task)
    # This doesn't block the response - returns immediately after caching
    if user_id:
        async def _save_evaluation_background():
            """Background task to save evaluation without blocking response."""
            try:
                await save_evaluation(
                    user_id=user_id,
                    scenario_id=scenario_id,
                    user_answer=user_answer,
                    score=evaluation["score"],
                    feedback=evaluation["feedback"]
                )
                logger.info("evaluation.db_saved_background", scenario_id=scenario_id)
            except Exception as e:
                # Don't fail the request if DB save fails
                logger.error("evaluation.db_save_failed", error=str(e), scenario_id=scenario_id)
        
        # Create background task - doesn't block, runs independently
        asyncio.create_task(_save_evaluation_background())
    
    return result


def _generate_cache_key(career_title: str, scenario_id: str, user_answer: str) -> str:
    """Generate a unique cache key for an evaluation.
    
    Optimized: hashlib imported at module level to avoid repeated imports.
    """
    # Hash the answer to keep key length reasonable
    # Use module-level hashlib import (optimization)
    answer_hash = hashlib.md5(user_answer.encode()).hexdigest()[:8]
    
    return f"eval:{career_title}:{scenario_id}:{answer_hash}"


async def get_user_evaluation_history(user_id: str, limit: int = 10) -> list:
    """
    Get a user's evaluation history.
    
    This is another business logic function that might aggregate
    data from multiple sources.
    """
    from app.services.supabase_service import get_user_evaluations
    
    evaluations = await get_user_evaluations(user_id, limit)
    
    return evaluations