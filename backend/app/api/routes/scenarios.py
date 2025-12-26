"""Scenario generation API endpoints."""
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse
from typing import Optional
import asyncio
import json
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


@router.post("/generate-stream")
async def generate_scenario_stream(request: ScenarioRequest):
    """
    Generate a scenario with streaming response for word-by-word display.
    
    Uses Server-Sent Events (SSE) to stream the scenario text word-by-word,
    then sends the complete scenario data including options.
    """
    async def generate():
        try:
            logger.info(
                "scenario.generation.stream.request",
                career_title=request.career_title,
                difficulty=request.difficulty
            )
            
            # Generate the full scenario first
            scenario = await scenario_service.generate_career_scenario(
                career_title=request.career_title,
                difficulty=request.difficulty,
                focus_area=request.focus_area,
                is_coding=request.is_coding
            )
            
            scenario_text = scenario.get("scenario_text", "")
            
            # Stream the scenario text word-by-word
            words = scenario_text.split()
            accumulated_text = ""
            
            for i, word in enumerate(words):
                # Add word to accumulated text
                if i > 0:
                    accumulated_text += " "
                accumulated_text += word
                
                # Send word as SSE event
                event_data = {
                    "type": "word",
                    "word": word,
                    "text": accumulated_text,
                    "is_complete": False
                }
                yield f"data: {json.dumps(event_data)}\n\n"
                
                # Small delay for typing effect (adjustable)
                await asyncio.sleep(0.05)  # 50ms delay per word
            
            # Send completion event with full scenario data
            completion_data = {
                "type": "complete",
                "scenario": {
                    "id": scenario["id"],
                    "career_title": scenario["career_title"],
                    "scenario_text": scenario["scenario_text"],
                    "options": scenario.get("options", []),
                    "initial_code": scenario.get("initial_code"),
                    "difficulty": scenario.get("difficulty"),
                    "focus_area": scenario.get("focus_area"),
                    "correct_option": scenario.get("correct_option"),
                    "context": scenario.get("context"),
                    "created_at": scenario.get("created_at"),
                    "cached": scenario.get("cached", False),
                    "input_tokens": scenario.get("input_tokens", 0),
                    "output_tokens": scenario.get("output_tokens", 0),
                },
                "is_complete": True
            }
            yield f"data: {json.dumps(completion_data)}\n\n"
            
            logger.info(
                "scenario.generation.stream.success",
                scenario_id=scenario["id"],
                career_title=request.career_title
            )
            
        except ValueError as e:
            # Business validation errors
            logger.warning("scenario.stream.validation_error", error=str(e))
            error_data = {"type": "error", "message": str(e)}
            yield f"data: {json.dumps(error_data)}\n\n"
            
        except Exception as e:
            # Unexpected errors
            logger.error("scenario.generation.stream.failed", error=str(e), exc_info=True)
            error_data = {
                "type": "error",
                "message": "Failed to generate scenario. Please try again."
            }
            yield f"data: {json.dumps(error_data)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
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