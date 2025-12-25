"""Multi-vendor LLM provider abstraction layer with fallback support."""

from .base_provider import LLMProvider, ProviderResponse, ProviderError
from .gemini_provider import GeminiProvider
from .deepseek_provider import DeepSeekProvider
from .router import SimpleRouter

__all__ = [
    "LLMProvider",
    "ProviderResponse",
    "ProviderError",
    "GeminiProvider",
    "DeepSeekProvider",
    "SimpleRouter",
]


def get_llm_router(max_retries: int = 3, temperature: float = None):
    """
    Factory function to create LLM router with fallback chain.
    
    Provider order: Gemini -> DeepSeek
    
    Args:
        max_retries: Maximum retries per provider before falling back
        temperature: Optional temperature override (defaults to generation temperature)
        
    Returns:
        SimpleRouter instance configured with available providers
    """
    from app.config import get_settings
    
    settings = get_settings()
    providers = []
    
    # Use provided temperature or default to generation temperature
    gemini_temp = temperature if temperature is not None else settings.gemini_temperature_generation
    
    # Add Gemini provider (always primary)
    gemini_provider = GeminiProvider(
        api_key=settings.gemini_api_key,
        model=settings.gemini_model_flash,
        temperature=gemini_temp,
        max_tokens=settings.gemini_max_tokens
    )
    providers.append(gemini_provider)
    
    # Add DeepSeek provider if API key is configured
    if settings.deepseek_api_key:
        deepseek_provider = DeepSeekProvider(
            api_key=settings.deepseek_api_key,
            model=settings.deepseek_model,
            temperature=gemini_temp  # Use same temperature as Gemini
        )
        providers.append(deepseek_provider)
    
    return SimpleRouter(providers=providers, max_retries=max_retries)
