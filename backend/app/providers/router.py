"""Router for managing multi-vendor fallback chain."""
import time
from typing import List, Optional

from .base_provider import LLMProvider, ProviderResponse, ProviderError


class SimpleRouter:
    """Dead-simple fallback chain: try each provider until one works"""
    
    def __init__(self, providers: List[LLMProvider], max_retries: int = 3):
        self.providers = providers
        self.max_retries = max_retries
    
    def generate(self, prompt: str, max_tokens: int = 500, response_format: str = "text") -> ProviderResponse:
        """
        Try each provider in order until one succeeds.
        
        Args:
            prompt: The prompt to send
            max_tokens: Maximum tokens to generate
            response_format: "text" or "json"
        
        Returns:
            ProviderResponse from the first successful provider
        
        Raises:
            Exception: If all providers fail
        """
        last_error = None
        
        for attempt, provider in enumerate(self.providers):
            for retry in range(self.max_retries):
                try:
                    response = provider.generate(prompt, max_tokens=max_tokens, response_format=response_format)
                    return response
                
                except Exception as e:
                    error = provider.classify_error(e)
                    last_error = error
                    
                    # If rate limited, wait and retry same provider
                    if error.error_type == "rate_limit" and retry < self.max_retries - 1:
                        wait_time = 2 ** retry  # Exponential backoff: 1s, 2s, 4s
                        time.sleep(wait_time)
                        continue
                    
                    # If invalid request, don't retry - fail immediately
                    if error.error_type == "invalid_request":
                        raise Exception(f"Invalid request: {error.message}")
                    
                    # Otherwise, try next provider
                    break
        
        # All providers failed
        error_msg = f"All providers failed. Last error: {last_error.message if last_error else 'Unknown error'}"
        raise Exception(error_msg)

