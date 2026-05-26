import json
import hashlib
from typing import Any, Optional
from django.core.cache import cache

def get_cache_key(prefix: str, data: Any) -> str:
    """Generate a stable cache key based on a prefix and a data payload."""
    serialized_data = json.dumps(data, sort_keys=True)
    hash_val = hashlib.md5(serialized_data.encode()).hexdigest()
    return f"planner:{prefix}:{hash_val}"

class ProviderCache:
    """
    Simple wrapper around Django's cache framework to handle 
    provider response caching.
    """
    
    def __init__(self, prefix: str, ttl: int = 3600 * 24): # Default 24 hours
        self.prefix = prefix
        self.ttl = ttl

    def get(self, query_data: Any) -> Optional[Any]:
        key = get_cache_key(self.prefix, query_data)
        return cache.get(key)

    def set(self, query_data: Any, value: Any):
        key = get_cache_key(self.prefix, query_data)
        cache.set(key, value, self.ttl)
