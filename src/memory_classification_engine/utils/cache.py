import time
from typing import Dict, Optional, Any

class MemoryCache:
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.ttl = ttl
        self.expired_count = 0
    
    def set(self, key: str, value: Any):
        if len(self.cache) >= self.max_size:
            self._evict_oldest()
        
        self.cache[key] = {
            'value': value,
            'timestamp': time.time()
        }
    
    def get(self, key: str) -> Optional[Any]:
        if key not in self.cache:
            return None
        
        if self._is_expired(key):
            self._remove_expired(key)
            return None
        
        # Move to end (most recently used)
        self.cache.move_to_end(key)
        return self.cache[key]['value']
    
    def exists(self, key: str) -> bool:
        if key not in self.cache:
            return False
        
        if self._is_expired(key):
            self._remove_expired(key)
            return False
        
        return True
    
    def delete(self, key: str):
        if key in self.cache:
            del self.cache[key]
    
    def clear(self):
        self.cache.clear()
        self.expired_count = 0
    
    def size(self) -> int:
        self._clean_expired()
        return len(self.cache)
    
    def _is_expired(self, key: str) -> bool:
        if key not in self.cache:
            return True
        
        timestamp = self.cache[key]['timestamp']
        return time.time() - timestamp > self.ttl
    
    def _remove_expired(self, key: str):
        if key in self.cache:
            del self.cache[key]
            self.expired_count += 1
    
    def _clean_expired(self):
        expired_keys = [key for key in self.cache if self._is_expired(key)]
        for key in expired_keys:
            self._remove_expired(key)
    
    def _evict_oldest(self):
        if not self.cache:
            return
        
        # Remove expired items first
        self._clean_expired()
        
        if len(self.cache) >= self.max_size:
            # Remove the first item (oldest)
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]