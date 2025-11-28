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
    return f"""You are an AI evaluator for a **fictional educational career simulation**. 
The following is a hypothetical workplace scenario designed for training purposes only. 
It involves professional challenges and simulated workplace conflicts.

**Context:**
Role: {career_title}
Task: Evaluate the user's decision objectively based on standard industry best practices.

**Hypothetical Scenario:**
---
{scenario_text}
---


**User's Decision:**
The user selected Option {user_answer}.

**Instructions:**
1. Identify the text corresponding to Option {user_answer} in the scenario above.
2. Analyze why this choice is effective or ineffective in this specific context.
3. Provide constructive, professional feedback.
4. Assign a score from 0 (poor) to 10 (excellent).

Return your response in this EXACT JSON format (no markdown):
{{
  "feedback": "A concise summary of the feedback.",
  "score": <number>,
  "explanation": "A detailed explanation of the trade-offs and reasoning."
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
        model = genai.GenerativeModel(settings.gemini_model_flash)
        
        response = await model.generate_content_async(
            prompt,
            generation_config={
                "temperature": settings.gemini_temperature_evaluation,
                "max_output_tokens": 1000,
                # ADD THIS LINE: Forces the model to return strictly JSON
                "response_mime_type": "application/json", 
            },
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )

        # CHECK FOR SAFETY BLOCK BEFORE ACCESSING .text
        if response.candidates and response.candidates[0].finish_reason != 1: # 1 is STOP (Success)
             logger.warning(f"Gemini blocked response. Finish reason: {response.candidates[0].finish_reason}")
             # Return a fallback response instead of crashing
             return {
                 "feedback": "Unable to evaluate detailed feedback due to content safety filters. However, your answer has been recorded.",
                 "score": 5,
                 "explanation": "The AI model flagged the scenario context as sensitive and could not generate a detailed critique."
             }

        # Parse JSON
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
            # Add safe access to response.text in logging
            response_text=getattr(response, 'text', 'Blocked/Empty')[:500] 
        )
        raise ValueError("Failed to parse AI evaluation response")
    except Exception as e:
        logger.error("gemini.evaluation.api_error", error=str(e))
        raise