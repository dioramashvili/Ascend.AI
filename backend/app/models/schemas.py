from pydantic import BaseModel, Field, constr, validator
import uuid
from typing import List, Literal, Optional

# User & Auth Models
class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)

class UserResponse(BaseModel):
    id: int
    username: str
    class Config: orm_mode = True 

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ScenarioRequest(BaseModel):
    """Request to generate a career scenario."""
    career_title: constr(strip_whitespace=True, to_lower=True, min_length=3, max_length=100) # type: ignore
    difficulty: Literal["beginner", "intermediate", "advanced"] = "intermediate"
    focus_area: Optional[constr(max_length=200)] = None # type: ignore
    
    @validator('career_title')
    def validate_career_title(cls, v):
        """Ensure career title has no special characters."""
        if not v.replace(" ", "").replace("-", "").isalnum():
            raise ValueError('Career title can only contain letters, numbers, spaces, and hyphens')
        return v


class ScenarioResponse(BaseModel):
    """Response containing a generated scenario."""
    id: str
    career_title: str
    difficulty: str
    focus_area: Optional[str] = None
    scenario_text: str
    options: List[str] = Field(..., min_items=3, max_items=3)
    correct_option: Optional[str] = None
    context: Optional[str] = None
    created_at: str
    cached: bool = False

class ScenarioListResponse(BaseModel):
    """Response containing multiple scenarios."""
    scenarios: List[ScenarioResponse]
    total: int
    career_title: str



class EvaluationRequest(BaseModel):
    """Request to evaluate a user's answer."""
    career_title: constr(strip_whitespace=True, to_lower=True, min_length=3, max_length=100) # type: ignore
    scenario_id: str
    scenario_text: str
    user_answer: constr(strip_whitespace=True, min_length=1, max_length=500) # type: ignore
    
    @validator('user_answer')
    def validate_answer(cls, v):
        """Ensure answer is one of A, B, or C."""
        if v.upper() not in ['A', 'B', 'C', 'OPTION A', 'OPTION B', 'OPTION C']:
            raise ValueError('Answer must be A, B, or C')
        return v.upper()[0]  # Normalize to just 'A', 'B', or 'C'


class EvaluationResponse(BaseModel):
    """Response containing evaluation feedback."""
    scenario_id: str
    career_title: str
    feedback: str
    score: int = Field(..., ge=0, le=10)
    explanation: str
    cached: bool = False
