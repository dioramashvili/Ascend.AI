"""Evaluation API endpoints."""
from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import EvaluationRequest, EvaluationResponse
from app.services import evaluation_service
from app.core.logging import get_logger

router = APIRouter(prefix="/evaluations", tags=["evaluations"])
logger = get_logger(__name__)


@router.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_answer(request: EvaluationRequest):
    """
    Evaluate a user's answer to a career scenario.
    
    This endpoint:
    1. Validates the request
    2. Calls the evaluation service
    3. Returns formatted response
    """
    try:
        logger.info(
            "evaluation.request",
            career_title=request.career_title,
            answer_length=len(request.user_answer)
        )
        
        # Call the service layer
        result = await evaluation_service.evaluate_user_answer(
            career_title=request.career_title,
            scenario_text=request.scenario_text,
            user_answer=request.user_answer,
            scenario_id=request.scenario_id
        )
        
        logger.info("evaluation.success", score=result["score"])
        return result
        
    except ValueError as e:
        # Business logic errors (e.g., invalid input)
        logger.warning("evaluation.validation_error", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
        
    except Exception as e:
        # Unexpected errors
        logger.error("evaluation.failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to evaluate answer. Please try again."
        )