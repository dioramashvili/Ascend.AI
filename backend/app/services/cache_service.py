"""
Mock Cache Service
This file provides placeholder functions for caching to allow the application
to run without a real Redis server. It simulates a cache that is always empty.
"""
from typing import Optional, Any

async def get_cached(key: str) -> Optional[Any]:
    """
    Mock function to simulate a cache miss. It always returns None.
    This forces the application to proceed with the actual logic (e.g., calling Gemini).
    """
    print(f"MOCK CACHE: Checking for key '{key}' -> Always a Miss")
    return None


async def set_cached(key: str, value: Any, ttl: int):
    """
    Mock function to simulate setting a value in the cache. It does nothing.
    """
    print(f"MOCK CACHE: Pretending to set key '{key}' with TTL {ttl}s.")
    pass