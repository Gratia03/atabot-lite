import hashlib
import json
import time
from typing import Optional, Any, Dict

class MemoryCache:
    def __init__(self, default_ttl: int = 3600):  # 1 hour default
        self.cache: Dict[str, dict] = {}
        self.default_ttl = default_ttl
    
    def _generate_key(self, prefix: str, data: Any) -> str:
        """Generate cache key from data"""
        data_str = json.dumps(data, sort_keys=True) if isinstance(data, (dict, list)) else str(data)
        return f"{prefix}:{hashlib.md5(data_str.encode()).hexdigest()}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self.cache:
            entry = self.cache[key]
            if time.time() < entry['expires_at']:
                entry['access_count'] += 1
                entry['last_accessed'] = time.time()
                return entry['value']
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache"""
        ttl = ttl or self.default_ttl
        self.cache[key] = {
            'value': value,
            'expires_at': time.time() + ttl,
            'created_at': time.time(),
            'last_accessed': time.time(),
            'access_count': 1
        }
    
    def delete(self, key: str) -> None:
        """Delete key from cache"""
        self.cache.pop(key, None)
    
    def clear(self) -> None:
        """Clear all cache"""
        self.cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        now = time.time()
        active_entries = sum(1 for entry in self.cache.values() if entry['expires_at'] > now)
        
        return {
            "total_entries": len(self.cache),
            "active_entries": active_entries,
            "expired_entries": len(self.cache) - active_entries,
            "memory_usage_estimate": len(str(self.cache)),  # Rough estimate
        }

# Global cache instance
cache_service = MemoryCache()
