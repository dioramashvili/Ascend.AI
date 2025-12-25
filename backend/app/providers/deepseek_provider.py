"""DeepSeek LLM provider implementation."""
import time
from openai import OpenAI
from typing import Optional

from .base_provider import LLMProvider, ProviderResponse, ProviderError


class DeepSeekProvider(LLMProvider):
    """DeepSeek provider using OpenAI-compatible API."""
    
    # Pricing per 1M tokens (approximate DeepSeek pricing, update as needed)
    PRICING = {
        "deepseek-chat": {"input": 0.14, "output": 0.28},  # $0.14/$0.28 per 1M tokens
        "deepseek-coder": {"input": 0.14, "output": 0.28},
    }
    
    def __init__(self, api_key: str, model: str = "deepseek-chat", base_url: str = "https://api.deepseek.com/v1", temperature: float = 0.7):
        super().__init__(api_key, model)
        self.base_url = base_url
        self.temperature = temperature
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
    
    def generate(self, prompt: str, max_tokens: int = 500, response_format: str = "text") -> ProviderResponse:
        """
        Generate completion from DeepSeek.
        
        Args:
            prompt: The prompt to send
            max_tokens: Maximum tokens to generate
            response_format: "text" or "json"
        """
        start = time.time()
        
        try:
            # Build messages
            messages = [{"role": "user", "content": prompt}]
            
            # For JSON format, add system message to ensure JSON output
            if response_format == "json":
                messages.insert(0, {"role": "system", "content": "You are a helpful assistant that returns responses in valid JSON format."})
            
            # Build request parameters
            request_params = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": self.temperature,
            }
            
            # Add JSON response format if requested
            if response_format == "json":
                request_params["response_format"] = {"type": "json_object"}
            
            response = self.client.chat.completions.create(**request_params)
            
            latency = (time.time() - start) * 1000
            
            # Extract response
            content = response.choices[0].message.content
            
            if not content:
                raise ValueError("Empty response from DeepSeek")
            
            # Calculate cost
            pricing = self.PRICING.get(self.model, {"input": 0.14, "output": 0.28})
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            total_tokens = response.usage.total_tokens
            
            input_cost = (input_tokens / 1_000_000) * pricing["input"]
            output_cost = (output_tokens / 1_000_000) * pricing["output"]
            
            return ProviderResponse(
                content=content,
                model=self.model,
                tokens_used=total_tokens,
                cost=input_cost + output_cost,
                latency_ms=latency
            )
            
        except Exception as e:
            # Re-raise to be caught by router
            raise
    
    def classify_error(self, error: Exception) -> ProviderError:
        """Classify DeepSeek errors for fallback decisions."""
        error_msg = str(error).lower()
        error_type = type(error).__name__
        
        if "rate_limit" in error_msg or "429" in error_msg or error_type == "RateLimitError":
            # Extract retry-after if available
            retry_after = 60  # Default
            return ProviderError("rate_limit", str(error), retry_after)
        
        elif "timeout" in error_msg or "timed out" in error_msg or error_type == "Timeout":
            return ProviderError("timeout", str(error))
        
        elif "invalid" in error_msg or "400" in error_msg or error_type == "InvalidRequestError":
            return ProviderError("invalid_request", str(error))
        
        else:
            return ProviderError("api_error", str(error))

