
***

# AI Tool Use Log
**Lab 6: Function Calling & Structured Outputs**

| Tool | Used For | Description |
|------|-----------|--------------|
| **Google AI Studio** |helping in  Code Generation (Schemas) | Asked: "fix my Pydantic models for a career scenario with a list of options and a strict string validator for career titles." |
| **Gemini 1.5 Flash API** | Runtime Logic (Backend) | Integrated into `gemini_service.py` to dynamically generate simulation text and evaluate user answers based on function arguments. |
| **clauideai** | Prompt Engineering for better results| Asked: "How do I improve my   system prompt that forces an LLM to return **only** raw JSON without markdown formatting?" for `_build_scenario_prompt`. |

### Notes
*   **Code Generation vs. Runtime:** AI Studio was used to help write the Python code (specifically the Pydantic data models), while the Gemini Flash API is called programmatically by the application to generate content for the user.
*   **Verification:** All AI-generated Pydantic validators (e.g., `validate_career_title`) were manually tested with invalid inputs to ensure they raise the correct 400 errors.
*   **Understanding:** I reviewed the `gemini_service.py` logic to ensure I understood how the JSON parsing and error handling work before submitting.