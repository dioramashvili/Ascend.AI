"""Gemini LLM provider implementation."""
import json
import time
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from typing import Dict, Any

from .base_provider import LLMProvider, ProviderResponse, ProviderError


class GeminiProvider(LLMProvider):
    """Gemini provider using Google Generative AI SDK."""
    
    # Pricing per 1M tokens (approximate, update as needed)
    PRICING = {
        "gemini-2.5-flash": {"input": 0.075, "output": 0.30},  # $0.075/$0.30 per 1M tokens
        "gemini-2.0-flash-exp": {"input": 0.075, "output": 0.30},
    }
    
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash", temperature: float = 0.7, max_tokens: int = 2000):
        super().__init__(api_key, model)
        self.temperature = temperature
        self.max_tokens = max_tokens
        genai.configure(api_key=api_key)
        self.client = genai
    
    def generate(self, prompt: str, max_tokens: int = None, response_format: str = "text") -> ProviderResponse:
        """
        Generate completion from Gemini.
        
        Args:
            prompt: The prompt to send
            max_tokens: Override default max tokens
            response_format: "text" or "json"
        """
        start = time.time()
        
        if max_tokens is None:
            max_tokens = self.max_tokens
        
        try:
            model = self.client.GenerativeModel(self.model)
            
            generation_config = {
                "temperature": self.temperature,
                "max_output_tokens": max_tokens,
            }
            
            # Set JSON response format if requested
            if response_format == "json":
                generation_config["response_mime_type"] = "application/json"
            
            response = model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                }
            )
            
            latency = (time.time() - start) * 1000
            
            # Check for safety blocks
            if not response.candidates or len(response.candidates) == 0:
                raise ValueError("AI Safety Filter blocked this request. No response candidates available.")
            
            candidate = response.candidates[0]
            
            # Get response text
            try:
                response_text = response.text
            except (ValueError, AttributeError):
                # Text not available - likely blocked
                raise ValueError("Unable to retrieve response text from Gemini.")
            
            # Calculate cost
            pricing = self.PRICING.get(self.model, {"input": 0.075, "output": 0.30})
            input_tokens = response.usage_metadata.prompt_token_count if response.usage_metadata else 0
            output_tokens = response.usage_metadata.candidates_token_count if response.usage_metadata else 0
            total_tokens = input_tokens + output_tokens
            
            input_cost = (input_tokens / 1_000_000) * pricing["input"]
            output_cost = (output_tokens / 1_000_000) * pricing["output"]
            
            return ProviderResponse(
                content=response_text,
                model=self.model,
                tokens_used=total_tokens,
                cost=input_cost + output_cost,
                latency_ms=latency
            )
            
        except Exception as e:
            # Re-raise to be caught by router
            raise
    
    def classify_error(self, error: Exception) -> ProviderError:
        """Classify Gemini errors for fallback decisions."""
        error_msg = str(error).lower()
        
        if "rate_limit" in error_msg or "429" in error_msg or "quota" in error_msg:
            return ProviderError("rate_limit", str(error), 60)
        
        elif "timeout" in error_msg or "timed out" in error_msg:
            return ProviderError("timeout", str(error))
        
        elif "invalid" in error_msg or "400" in error_msg or "bad request" in error_msg:
            return ProviderError("invalid_request", str(error))
        
        elif "safety" in error_msg or "blocked" in error_msg:
            # Safety blocks are usually non-retryable
            return ProviderError("invalid_request", str(error))
        
        else:
            return ProviderError("api_error", str(error))

