from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Project": "CareerSim API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}


class ScenarioRequest(BaseModel):
    career_title: str

@app.post("/api/v1/simulations/generate")
def generate_mock_scenario(request: ScenarioRequest):
    return {
        "scenario": f"This is a mock scenario for a {request.career_title}. What do you do?",
        "options": ["Option A", "Option B", "Option C"]
    }