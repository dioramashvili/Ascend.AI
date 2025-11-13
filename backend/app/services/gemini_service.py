"""Gemini API integration."""
import json
from typing import Dict, Any
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential
from google.generativeai.types import HarmCategory, HarmBlockThreshold 

from app.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)

genai.configure(api_key=settings.gemini_api_key)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def generate_scenario(
    career_title: str,
    difficulty: str = "intermediate",
    focus_area: str = None
) -> Dict[str, Any]:
    """
    Generate a career scenario using Gemini Flash (faster, cheaper).
    
    Returns:
        Dict with keys:
        - scenario: Full scenario text (200-300 words)
        - options: List of 3 choices (A, B, C)
        - context: Additional background info
        - correct_option: Optional "best" answer
    """
    
    prompt = _build_scenario_prompt(career_title, difficulty, focus_area)
    
    try:
        # Use Flash model for scenario generation (cheaper)
        model = genai.GenerativeModel(settings.gemini_model_flash)
        
        response = await model.generate_content_async(
            prompt,
            generation_config={
                "temperature": settings.gemini_temperature_generation,
                "max_output_tokens": settings.gemini_max_tokens,
            },
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
        
        # Parse JSON response
        result = json.loads(response.text)
        
        # Validate response structure
        _validate_scenario_response(result)
        
        logger.info(
            "gemini.scenario.success",
            career_title=career_title,
            difficulty=difficulty
        )
        
        return result
        
    except json.JSONDecodeError as e:
        logger.error(
            "gemini.json_parse_error",
            error=str(e),
            response_text=response.text[:500]  # Log first 500 chars
        )
        raise ValueError("Failed to parse AI response")
        
    except Exception as e:
        logger.error("gemini.api_error", error=str(e))
        raise


def _build_scenario_prompt(
    career_title: str,
    difficulty: str,
    focus_area: str = None
) -> str:
    """Build the scenario generation prompt."""
    
    difficulty_guide = {
        "beginner": "Focus on fundamental concepts and common situations. Avoid jargon.",
        "intermediate": "Include realistic challenges requiring some experience and judgment.",
        "advanced": "Present complex situations requiring deep expertise and strategic thinking."
    }
    
    focus_instruction = ""
    if focus_area:
        focus_instruction = f"\nFocus specifically on: {focus_area}"
    
    return f"""You are a simulation designer creating realistic career scenarios for {career_title}.

**Difficulty Level:** {difficulty}
{difficulty_guide.get(difficulty, "")}
{focus_instruction}

**Instructions:**
1. Create a realistic workplace scenario (100-130 words)
2. Include specific context, stakeholders, and constraints
3. Present a clear decision point or challenge
4. Provide 3 distinct options (labeled A, B, C)
5. Each option should be plausible but have different trade-offs

**Requirements:**
- Use real industry terminology
- Avoid generic advice
- Make options genuinely different
- No obvious "correct" answer
- Base scenarios on common real-world situations

Return your response in this EXACT JSON format (no markdown, no extra text):
{{
  "scenario": "Full scenario text describing the situation, context, and challenge",
  "context": "Brief additional context or background (50-100 words)",
  "options": [
    "Option A: [Detailed description of first approach]",
    "Option B: [Detailed description of second approach]",
    "Option C: [Detailed description of third approach]"
  ],
  "correct_option": "A or B or C (which option demonstrates best practice, or null if subjective)"
}}

Remember: Return ONLY valid JSON, no markdown formatting or extra text."""


def _validate_scenario_response(result: Dict[str, Any]) -> None:
    """Validate the structure of Gemini's scenario response."""
    required_fields = ["scenario", "options"]
    
    for field in required_fields:
        if field not in result:
            raise ValueError(f"Missing required field: {field}")
    
    if not isinstance(result["options"], list):
        raise ValueError("Options must be a list")
    
    if len(result["options"]) != 3:
        raise ValueError(f"Must have exactly 3 options, got {len(result['options'])}")
    
    if len(result["scenario"]) < 100:
        raise ValueError("Scenario text is too short (minimum 100 characters)")
    
    if len(result["scenario"]) > 2000:
        raise ValueError("Scenario text is too long (maximum 2000 characters)")



def _build_evaluation_prompt(
    career_title: str,
    scenario_text: str,
    user_answer: str
) -> str:
    """Build the prompt for evaluating a user's answer."""
    return f"""You are an expert career coach for the role of a {career_title}.
A user was presented with the following scenario and made a choice.

**Scenario:**
---
{scenario_text}
---

**User's Answer:**
They chose option '{user_answer}'.

**Your Task:**
Evaluate the user's choice. Provide constructive feedback in 1-2 sentences, a  explanation, and a score.
The score should be from 0 (very poor choice) to 10 (excellent choice).
Your tone should be encouraging and professional.

Return your response in this EXACT JSON format (no markdown or extra text):
{{
  "feedback": "A concise summary of the feedback for the user's choice.",
  "score": <a number from 0 to 10>,
  "explanation": "A more detailed explanation  in 10 or more words of why the choice was good or bad, and what the trade-offs were."
}}
"""
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def generate_evaluation(
    career_title: str,
    scenario_text: str,
    user_answer: str
) -> Dict[str, Any]:
    """
    Evaluates a user's answer using Gemini and returns feedback and a score.
    """
    prompt = _build_evaluation_prompt(career_title, scenario_text, user_answer)
    try:
        # Use a more capable model for nuanced evaluation if needed, but flash is fine for testing.
        model = genai.GenerativeModel(settings.gemini_model_flash)
        response = await model.generate_content_async(
            prompt,
            generation_config={
                "temperature": settings.gemini_temperature_evaluation,
                "max_output_tokens": 1000,
            },
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
        result = json.loads(response.text)
        
        # Basic validation
        if not all(k in result for k in ["feedback", "score", "explanation"]):
            raise ValueError("Evaluation response from AI is missing required keys.")
        
        logger.info("gemini.evaluation.success", score=result.get("score"))
        return result

    except json.JSONDecodeError as e:
        logger.error(
            "gemini.evaluation.json_parse_error",
            error=str(e),
            response_text=response.text[:500]
        )
        raise ValueError("Failed to parse AI evaluation response")
    except Exception as e:
        logger.error("gemini.evaluation.api_error", error=str(e))
        raise