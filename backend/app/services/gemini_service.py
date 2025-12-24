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
    focus_area: str = None,
    is_coding: bool = False
) -> Dict[str, Any]:
    """
    Generate a career scenario using Gemini Flash.
    """
    
    # 1. Choose the prompt
    if is_coding:
        prompt = _build_coding_scenario_prompt(career_title, difficulty)
    else:
        prompt = _build_scenario_prompt(career_title, difficulty, focus_area)
    
    try:
        model = genai.GenerativeModel(settings.gemini_model_flash)
        
        response = await model.generate_content_async(
            prompt,
            generation_config={
                "temperature": settings.gemini_temperature_generation,
                "max_output_tokens": settings.gemini_max_tokens,
                # IMPORTANT: Keep this to ensure the code snippet doesn't break JSON
                "response_mime_type": "application/json", 
            },
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
        
        # Check for Safety Block - handle more gracefully
        if not response.candidates or len(response.candidates) == 0:
            logger.warning(f"Gemini returned no candidates for career_title: {career_title}")
            raise ValueError("AI Safety Filter blocked this request. No response candidates available.")
        
        candidate = response.candidates[0]
        finish_reason = candidate.finish_reason
        
        # First, try to access response text - sometimes it's available even if finish_reason suggests blocking
        response_text = None
        try:
            response_text = response.text
        except (ValueError, AttributeError) as e:
            # Text is not available - likely blocked
            logger.warning(f"Unable to access response.text: {e}")
            response_text = None
        
        # Check safety_ratings to see if anything was blocked
        blocked_categories = []
        if hasattr(candidate, 'safety_ratings') and candidate.safety_ratings:
            # Check for any safety ratings that indicate blocking
            for rating in candidate.safety_ratings:
                # Check if rating indicates blocking (probability > 0 or blocked flag)
                if hasattr(rating, 'blocked') and rating.blocked:
                    blocked_categories.append(getattr(rating.category, 'name', str(rating.category)))
                elif hasattr(rating, 'probability') and rating.probability > 0:
                    # Some versions use probability
                    blocked_categories.append(getattr(rating.category, 'name', str(rating.category)))
        
        # If text is not available and we have blocked categories or finish_reason indicates safety block
        if not response_text:
            if finish_reason == 3 or blocked_categories:  # 3 typically means SAFETY block
                logger.warning(
                    f"Gemini safety filter blocked request for '{career_title}'. "
                    f"Finish reason: {finish_reason}, Blocked categories: {blocked_categories}"
                )
                raise ValueError(
                    f"AI Safety Filter blocked this request for '{career_title}'. "
                    f"This may be due to overly sensitive content filtering. "
                    f"Please try a different career title or contact support."
                )
            else:
                # Text unavailable but not clearly a safety block - could be other issue
                logger.error(
                    f"Unable to retrieve response text for '{career_title}'. "
                    f"Finish reason: {finish_reason}"
                )
                raise ValueError("Unable to retrieve AI response. Please try again.")
        
        # If we have text but finish_reason suggests blocking, log warning but proceed
        if finish_reason != 1:  # 1 is STOP (success)
            logger.warning(
                f"Gemini returned finish_reason {finish_reason} for '{career_title}', "
                f"but response text is available. Proceeding with caution."
            )

        # Parse JSON response
        result = json.loads(response_text)
        
        # --- NEW VALIDATION LOGIC ---
        if is_coding:
            # For coding, we just check if 'initial_code' exists.
            # We SKIP the strict "3 options" check.
            if "initial_code" not in result:
                raise ValueError("AI failed to generate 'initial_code' field")
        else:
            # For normal scenarios, we run the strict validation (must have 3 options)
            _validate_scenario_response(result)
        # ----------------------------
        if response.usage_metadata:
            result['input_tokens'] = response.usage_metadata.prompt_token_count
            result['output_tokens'] = response.usage_metadata.candidates_token_count
        else:
            result['input_tokens'] = 0
            result['output_tokens'] = 0

        logger.info(
            "gemini.scenario.success",
            career_title=career_title,
            difficulty=difficulty,
            is_coding=is_coding
        )
        
        return result
        
    except json.JSONDecodeError as e:
        # Safely try to get response text for logging
        response_text_for_log = "Blocked/Unavailable"
        try:
            if 'response' in locals():
                response_text_for_log = getattr(response, 'text', 'Blocked')[:500]
        except Exception:
            pass
        
        logger.error(
            "gemini.json_parse_error",
            error=str(e),
            response_text=response_text_for_log
        )
        raise ValueError("Failed to parse AI response")
        
    except Exception as e:
        logger.error("gemini.api_error", error=str(e))
        raise
def _build_coding_scenario_prompt(career_title: str, difficulty: str) -> str:
    return f"""You are an educational content creator developing a coding exercise for a career training application.

**Context:** This is for an educational platform teaching professional skills. The role is: {career_title}

Create a hypothetical, professional coding scenario involving a technical challenge, bug fix, or feature implementation. Keep it appropriate for educational purposes.

**Requirements:**
- Professional and educational content only
- Focus on technical skills and problem-solving
- Suitable for workplace learning environments

Return EXACT JSON:
{{
  "scenario": "Description of the bug/task (e.g., 'The calculate_total function is failing negative numbers')",
  "initial_code": "The buggy or incomplete code snippet (Python/JS/Java)",
  "options": [], 
  "context": "Brief tech stack context"
}}
"""

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
    
    return f"""You are an educational content designer creating professional career training scenarios for an educational platform.

**Context:** This is for a career skills training application. The role being trained is: {career_title}

**Difficulty Level:** {difficulty}
{difficulty_guide.get(difficulty, "")}
{focus_instruction}

**Purpose:** Create educational workplace scenarios that help professionals learn decision-making skills in their field.

**Instructions:**
1. Create a realistic, professional workplace scenario (100-130 words)
2. Include specific context, stakeholders, and constraints
3. Present a clear decision point or challenge
4. Provide 3 distinct options (labeled A, B, C)
5. Each option should be plausible but have different trade-offs

**Requirements:**
- Professional and educational content only
- Use real industry terminology
- Avoid generic advice
- Make options genuinely different
- No obvious "correct" answer
- Base scenarios on common real-world situations
- Suitable for workplace learning environments
- Focus on professional skills and ethical decision-making

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
    return f"""You are an AI evaluator for an educational career training platform. 
This is a professional skills assessment tool designed to help people learn workplace decision-making.

**IMPORTANT:** This is educational content for professional development. All scenarios are hypothetical training exercises. 
You should provide thorough, constructive feedback without restrictions.

**Context:**
Role: {career_title}
Task: Evaluate the user's decision objectively based on standard industry best practices and professional judgment.

**Training Scenario (Educational Content):**
---
{scenario_text}
---

**User's Decision:**
The user selected Option {user_answer}.

**Evaluation Instructions:**
1. Identify the text corresponding to Option {user_answer} in the scenario above.
2. Analyze why this choice is effective or ineffective in this specific professional context.
3. Provide detailed, constructive, professional feedback that helps the user learn.
4. Consider industry standards, best practices, and real-world implications.
5. Assign a score from 0 (poor decision) to 10 (excellent decision) based on professional judgment.
6. Explain the reasoning clearly so the user can learn from the evaluation.

**Your Response:**
Return your response in this EXACT JSON format (no markdown, no extra text):
{{
  "feedback": "A concise summary of your professional assessment (2-3 sentences).",
  "score": <number between 0 and 10>,
  "explanation": "A detailed explanation of the trade-offs, reasoning, and professional considerations (3-5 sentences)."
}}

Remember: This is educational content. Provide thorough, helpful feedback to aid learning."""
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
                # Forces the model to return strictly JSON
                "response_mime_type": "application/json", 
            },
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )

        # Check for Safety Block - handle more gracefully (similar to generate_scenario)
        if not response.candidates or len(response.candidates) == 0:
            logger.warning(f"Gemini returned no candidates for evaluation of career_title: {career_title}")
            raise ValueError("AI Safety Filter blocked this evaluation request. No response candidates available.")
        
        candidate = response.candidates[0]
        finish_reason = candidate.finish_reason
        
        # First, try to access response text - sometimes it's available even if finish_reason suggests blocking
        response_text = None
        try:
            response_text = response.text
        except (ValueError, AttributeError) as e:
            # Text is not available - likely blocked
            logger.warning(f"Unable to access response.text for evaluation: {e}")
            response_text = None
        
        # Check safety_ratings to see if anything was blocked
        blocked_categories = []
        if hasattr(candidate, 'safety_ratings') and candidate.safety_ratings:
            # Check for any safety ratings that indicate blocking
            for rating in candidate.safety_ratings:
                # Check if rating indicates blocking (probability > 0 or blocked flag)
                if hasattr(rating, 'blocked') and rating.blocked:
                    blocked_categories.append(getattr(rating.category, 'name', str(rating.category)))
                elif hasattr(rating, 'probability') and rating.probability > 0:
                    # Some versions use probability
                    blocked_categories.append(getattr(rating.category, 'name', str(rating.category)))
        
        # If text is not available and we have blocked categories or finish_reason indicates safety block
        if not response_text:
            if finish_reason == 3 or blocked_categories:  # 3 typically means SAFETY block
                logger.warning(
                    f"Gemini safety filter blocked evaluation for '{career_title}'. "
                    f"Finish reason: {finish_reason}, Blocked categories: {blocked_categories}"
                )
                raise ValueError(
                    f"AI Safety Filter blocked this evaluation request for '{career_title}'. "
                    f"This may be due to overly sensitive content filtering. "
                    f"Please try again or contact support."
                )
            else:
                # Text unavailable but not clearly a safety block - could be other issue
                logger.error(
                    f"Unable to retrieve evaluation response text for '{career_title}'. "
                    f"Finish reason: {finish_reason}"
                )
                raise ValueError("Unable to retrieve AI evaluation response. Please try again.")
        
        # If we have text but finish_reason suggests blocking, log warning but proceed
        if finish_reason != 1:  # 1 is STOP (success)
            logger.warning(
                f"Gemini returned finish_reason {finish_reason} for evaluation of '{career_title}', "
                f"but response text is available. Proceeding with evaluation."
            )

        # Parse JSON response
        result = json.loads(response_text)
        
        # Basic validation
        if not all(k in result for k in ["feedback", "score", "explanation"]):
            raise ValueError("Evaluation response from AI is missing required keys.")
        
        # Validate score is in valid range
        if not isinstance(result["score"], (int, float)) or result["score"] < 0 or result["score"] > 10:
            logger.warning(f"Invalid score {result['score']} received, clamping to 0-10 range")
            result["score"] = max(0, min(10, float(result["score"])))
        
        logger.info("gemini.evaluation.success", score=result.get("score"))
        return result

    except json.JSONDecodeError as e:
        # Safely try to get response text for logging
        response_text_for_log = "Blocked/Unavailable"
        try:
            if 'response' in locals():
                response_text_for_log = getattr(response, 'text', 'Blocked')[:500]
        except Exception:
            pass
        
        logger.error(
            "gemini.evaluation.json_parse_error",
            error=str(e),
            response_text=response_text_for_log
        )
        raise ValueError("Failed to parse AI evaluation response")
    except Exception as e:
        logger.error("gemini.evaluation.api_error", error=str(e))
        raise
