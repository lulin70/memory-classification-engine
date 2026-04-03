import time
from collections import OrderedDict
from typing import Dict, Optional, Any

class LRUCache:
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.max_size = max_size
        self.ttl = ttl
        self.cache = OrderedDict()
        self.expiry_times = {}
    
    def get(self, key: str) -> Optional[Any]:
        if key not in self.cache:
            return None
        
        if self._is_expired(key):
            self._remove_expired(key)
            return None
        
        self.cache.move_to_end(key)
        return self.cache[key]
    
    def set(self, key: str, value: Any) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        elif len(self.cache) >= self.max_size:
            oldest_key = next(iter(self.cache))
            self._remove_key(oldest_key)
        
        self.cache[key] = value
        self.expiry_times[key] = time.time() + self.ttl
    
    def delete(self, key: str) -> None:
        if key in self.cache:
            self._remove_key(key)
    
    def clear(self) -> None:
        self.cache.clear()
        self.expiry_times.clear()
    
    def exists(self, key: str) -> bool:
        if key not in self.cache:
            return False
        
        if self._is_expired(key):
            self._remove_expired(key)
            return False
        
        return True
    
    def size(self) -> int:
        self._remove_all_expired()
        return len(self.cache)
    
    def _is_expired(self, key: str) -> bool:
        return time.time() > self.expiry_times.get(key, 0)
    
    def _remove_expired(self, key: str) -> None:
        if key in self.cache:
            self._remove_key(key)
    
    def _remove_all_expired(self) -> None:
        expired_keys = [key for key in self.cache if self._is_expired(key)]
        for key in expired_keys:
            self._remove_key(key)
    
    def _remove_key(self, key: str) -> None:
        del self.cache[key]
        del self.expiry_times[key]

class MemoryCache:
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.cache = LRUCache(max_size, ttl)
        self.expired_count = 0
    
    def get(self, key: str) -> Optional[Any]:
        value = self.cache.get(key)
        if value is None and key in self.cache.cache:
            self.expired_count += 1
        return value
    
    def set(self, key: str, value: Any) -> None:
        self.cache.set(key, value)
    
    def delete(self, key: str) -> None:
        self.cache.delete(key)
    
    def clear(self) -> None:
        self.cache.clear()
        self.expired_count = 0
    
    def exists(self, key: str) -> bool:
        return self.cache.exists(key)
    
    def size(self) -> int:
        return self.cache.size()
    
    @property
    def max_size(self) -> int:
        return self.cache.max_size
    
    @property
    def ttl(self) -> int:
        return self.cache.ttl
