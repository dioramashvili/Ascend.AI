from pydantic import BaseModel, Field, constr
import uuid
from typing import List, Literal, Optional

# User & Auth Models
class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)

class UserResponse(BaseModel):
    id: int
    username: str
    class Config: orm_mode = True # For SQLAlchemy compatibility

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# API Endpoint Models from your docs
class ScenarioRequest(BaseModel):
    career_title: constr(strip_whitespace=True, to_lower=True, min_length=3, max_length=100) # type: ignore
    
class ScenarioResponse(BaseModel):
    scenario: str
    options: List[str]

class EvaluationRequest(BaseModel):
    career_title: constr(strip_whitespace=True, to_lower=True, min_length=3, max_length=100) # type: ignore
    user_answer: constr(strip_whitespace=True, min_length=1, max_length=500) # type: ignore

class EvaluationResponse(BaseModel):
    task_id: str
    status: str = "pending"