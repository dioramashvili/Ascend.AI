"""Scenario generation API endpoints."""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from app.models.schemas import (
    ScenarioRequest, 
    ScenarioResponse,
    ScenarioListResponse
)
from app.services import scenario_service
from app.core.logging import get_logger
from app.dependencies import get_current_user  # For protected routes

router = APIRouter(prefix="/scenarios", tags=["scenarios"])
logger = get_logger(__name__)


@router.post("/generate", response_model=ScenarioResponse)
async def generate_scenario(request: ScenarioRequest):
    """
    Generate a new career scenario.
    
    This endpoint:
    1. Validates the career title
    2. Generates a realistic scenario with options
    3. Returns the scenario with metadata
    
    Example request:
```json
    {
        "career_title": "software engineer",
        "difficulty": "intermediate",
        "focus_area": "technical decision making"
    }
```
    """
    try:
        logger.info(
            "scenario.generation.request",
            career_title=request.career_title,
            difficulty=request.difficulty
        )
        
        # Call service layer
        scenario = await scenario_service.generate_career_scenario(
            career_title=request.career_title,
            difficulty=request.difficulty,
            focus_area=request.focus_area,
            is_coding=request.is_coding
        )
        
        logger.info(
            "scenario.generation.success",
            scenario_id=scenario["id"],
            career_title=request.career_title
        )
        
        return scenario
        
    except ValueError as e:
        # Business validation errors
        logger.warning("scenario.validation_error", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
        
    except Exception as e:
        # Unexpected errors
        logger.error("scenario.generation.failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to generate scenario. Please try again."
        )


@router.get("/career/{career_title}", response_model=ScenarioListResponse)
async def get_scenarios_by_career(
    career_title: str,
    limit: int = Query(default=10, ge=1, le=50),
    offset: int = Query(default=0, ge=0)
):
    """
    Get previously generated scenarios for a specific career.
    
    Useful for:
    - Showing users what scenarios are available
    - Allowing replay of previous scenarios
    - Building a scenario library
    """
    try:
        scenarios = await scenario_service.get_scenarios_by_career(
            career_title=career_title,
            limit=limit,
            offset=offset
        )
        
        return {
            "scenarios": scenarios,
            "total": len(scenarios),
            "career_title": career_title
        }
        
    except Exception as e:
        logger.error("scenario.fetch.failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch scenarios")



@router.get("/{scenario_id}", response_model=ScenarioResponse)
async def get_scenario_by_id(scenario_id: str):
    """
    Get a specific scenario by ID.
    
    Useful for:
    - Retrieving a scenario to display
    - Re-attempting a scenario
    - Sharing scenarios between users
    """
    try:
        scenario = await scenario_service.get_scenario_by_id(scenario_id)
        
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")
        
        return scenario
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("scenario.fetch.failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch scenario")


@router.post("/{scenario_id}/track-view")
async def track_scenario_view(
    scenario_id: str,
    user_id: Optional[str] = None
):
    """
    Track when a user views a scenario (analytics).
    
    This is a fire-and-forget endpoint - even if it fails,
    we don't want to break the user experience.
    """
    try:
        await scenario_service.track_scenario_view(scenario_id, user_id)
        return {"status": "tracked"}
    except Exception as e:
        logger.warning("scenario.tracking.failed", error=str(e))
        # Return success anyway - tracking is non-critical
        return {"status": "tracking_failed"}