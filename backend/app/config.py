from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "CareerSim"
    DEBUG: bool = False
    
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    SUPABASE_URL: str
    SUPABASE_KEY: str  
    SUPABASE_SERVICE_KEY: str 
    
    REDIS_URL: str
    REDIS_CACHE_TTL: int = 3600
    
    GEMINI_API_KEY: str
    GEMINI_MODEL_FLASH: str = "gemini-2.0-flash-exp"
    GEMINI_MODEL_PRO: str = "gemini-1.5-pro-latest"
    GEMINI_TEMPERATURE: float = 0.4
    GEMINI_MAX_TOKENS: int = 1000
    
    RATE_LIMIT_PER_MINUTE: int = 10
    
    SENTRY_DSN: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()