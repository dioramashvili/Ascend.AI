
# Safety and Privacy Checklist
**Lab 6: Function Calling & Structured Outputs**

| Check | Status | Notes |
|-------|--------|-------|
| **Removed all API keys from code** | ✅ | Keys are loaded via `.env` and `app/config.py`; `.env` is git-ignored. |
| **No private or personal data used** | ✅ | Only simulation data (career titles, choices) is sent to AI; no PII. |
| **Function handles bad inputs safely** | ✅ | Pydantic validators restrict special characters in career titles. |
| **Function returns friendly error messages** | ✅ | FastAPI exception handlers return clear JSON error details. |
| **User consent not required** | ✅ | No tracking or rigorous data collection implemented yet. |

### Example Safety Handling

**Scenario:**
A user tries to inject special characters or potential prompt injection scripts into the career title field (e.g., `"Software Engineer <script>alert('hack')</script>"` or `"!!!Delete DB!!!"`).

**Code Logic (`backend/app/models/schemas.py`):**
```python
@validator('career_title')
def validate_career_title(cls, v):
    """Ensure career title has no special characters."""
    if not v.replace(" ", "").replace("-", "").isalnum():
        raise ValueError('Career title can only contain letters, numbers, spaces, and hyphens')
    return v
```

**System Response:**
The API intercepts the request before it reaches the AI model and returns a 400 Bad Request:
```json
{
  "detail": [
    {
      "loc": ["body", "career_title"],
      "msg": "Career title can only contain letters, numbers, spaces, and hyphens",
      "type": "value_error"
    }
  ]
}
```

### Plan to Improve

1.  **Re-enable Gemini Safety Filters:** Currently, `backend/app/services/gemini_service.py` sets `HarmBlockThreshold.BLOCK_NONE`. In Week 7, we will adjust this to `BLOCK_MEDIUM_AND_ABOVE` to prevent the AI from generating inappropriate workplace scenarios.
2.  **Rate Limiting:** Ensure the rate limiting configured in `config.py` (`RATE_LIMIT_PER_MINUTE=10`) is actively enforced on the `/generate` endpoint to prevent API cost abuse.
3.  **Output Sanitization:** Add a post-processing step to scan AI-generated JSON for potential bias before sending it to the frontend.