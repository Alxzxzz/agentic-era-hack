import time
from typing import Any, Dict

_cache: Dict[str, Any] = {}
_cache_ttl: Dict[str, float] = {}

def get_from_cache(key: str) -> Any:
    if key in _cache and time.time() < _cache_ttl[key]:
        return _cache[key]
    return None

def set_in_cache(key: str, value: Any, ttl_seconds: int = 300):
    _cache[key] = value
    _cache_ttl[key] = time.time() + ttl_seconds
