import time
import pandas as pd

# Simple in-memory cache
# Structure: { "key": {"data": ..., "expires_at": timestamp} }
_cache = {}


def get_cache(key: str):
    """Get item from cache if not expired"""
    if key in _cache:
        item = _cache[key]
        if time.time() < item["expires_at"]:
            print(f"[CACHE HIT] {key}")
            return item["data"]
        else:
            # expired, delete it
            del _cache[key]
            print(f"[CACHE EXPIRED] {key}")
    return None


def set_cache(key: str, data, ttl_seconds: int = 300):
    """
    Store item in cache
    ttl_seconds: how long to keep it
    Default: 5 minutes (300 seconds)
    """
    _cache[key] = {
        "data": data,
        "expires_at": time.time() + ttl_seconds
    }
    
    # Better logging for DataFrames
    if isinstance(data, pd.DataFrame):
        print(f"[CACHE SET] {key} (DataFrame: {len(data)} rows) for {ttl_seconds}s")
    else:
        print(f"[CACHE SET] {key} for {ttl_seconds}s")


def clear_cache():
    """Clear all cache — for testing"""
    _cache.clear()
    print("[CACHE CLEARED]")