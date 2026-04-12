import time
import pickle
import os
from typing import Dict, Optional, Any, List, Tuple
from collections import OrderedDict

class LRUCache:
    """改进的LRU缓存实现，支持优先级和预加载"""
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self.max_size = max_size
        self.ttl = ttl
        self.expired_count = 0
        self.hit_count = 0
        self.miss_count = 0
    
    def set(self, key: str, value: Any, priority: int = 0):
        """设置缓存，支持优先级"""
        if len(self.cache) >= self.max_size:
            self._evict_oldest()
        
        self.cache[key] = {
            'value': value,
            'timestamp': time.time(),
            'priority': priority
        }
        # 移动到末尾（最近使用）
        self.cache.move_to_end(key)
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存，更新使用时间"""
        if key not in self.cache:
            self.miss_count += 1
            return None
        
        if self._is_expired(key):
            self._remove_expired(key)
            self.miss_count += 1
            return None
        
        # 更新时间戳和位置（最近使用）
        self.cache[key]['timestamp'] = time.time()
        self.cache.move_to_end(key)
        self.hit_count += 1
        return self.cache[key]['value']
    
    def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        if key not in self.cache:
            return False
        
        if self._is_expired(key):
            self._remove_expired(key)
            return False
        
        return True
    
    def delete(self, key: str):
        """删除缓存"""
        if key in self.cache:
            del self.cache[key]
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()
        self.expired_count = 0
        self.hit_count = 0
        self.miss_count = 0
    
    def size(self) -> int:
        """获取缓存大小"""
        self._clean_expired()
        return len(self.cache)
    
    def get_stats(self) -> Dict[str, int]:
        """获取缓存统计信息"""
        return {
            'size': self.size(),
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'hit_rate': self._calculate_hit_rate(),
            'expired_count': self.expired_count
        }
    
    def _calculate_hit_rate(self) -> float:
        """计算命中率"""
        total = self.hit_count + self.miss_count
        return (self.hit_count / total * 100) if total > 0 else 0
    
    def _is_expired(self, key: str) -> bool:
        """检查缓存是否过期"""
        if key not in self.cache:
            return True
        
        timestamp = self.cache[key]['timestamp']
        return time.time() - timestamp > self.ttl
    
    def _remove_expired(self, key: str):
        """删除过期缓存"""
        if key in self.cache:
            del self.cache[key]
            self.expired_count += 1
    
    def _clean_expired(self):
        """清理所有过期缓存"""
        expired_keys = [key for key in self.cache if self._is_expired(key)]
        for key in expired_keys:
            self._remove_expired(key)
    
    def _evict_oldest(self):
        """驱逐最旧的缓存，考虑优先级"""
        if not self.cache:
            return
        
        # 先清理过期项
        self._clean_expired()
        
        if len(self.cache) >= self.max_size:
            # 按优先级和时间排序，驱逐优先级低且最旧的
            items = [(k, v) for k, v in self.cache.items()]
            items.sort(key=lambda x: (x[1]['priority'], x[1]['timestamp']))
            oldest_key = items[0][0]
            del self.cache[oldest_key]

class FileCache:
    """文件缓存实现，作为二级缓存"""
    def __init__(self, cache_dir: str = ".cache", ttl: int = 86400):
        self.cache_dir = cache_dir
        self.ttl = ttl
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def _get_file_path(self, key: str) -> str:
        """获取缓存文件路径"""
        safe_key = key.replace('/', '_').replace('\\', '_')
        return os.path.join(self.cache_dir, f"{safe_key}.cache")
    
    def set(self, key: str, value: Any):
        """设置文件缓存"""
        file_path = self._get_file_path(key)
        try:
            # Comment in Chinese removedving
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'wb') as f:
                pickle.dump({
                    'value': value,
                    'timestamp': time.time()
                }, f)
        except Exception:
            pass
    
    def get(self, key: str) -> Optional[Any]:
        """获取文件缓存"""
        file_path = self._get_file_path(key)
        if not os.path.exists(file_path):
            return None
        
        try:
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
                if time.time() - data['timestamp'] > self.ttl:
                    os.remove(file_path)
                    return None
                return data['value']
        except Exception:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except (OSError, PermissionError):
                    pass
            return None

    def delete(self, key: str):
        """删除文件缓存"""
        file_path = self._get_file_path(key)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except (OSError, PermissionError):
                pass

    def clear(self):
        """清空文件缓存"""
        for file in os.listdir(self.cache_dir):
            if file.endswith('.cache'):
                try:
                    os.remove(os.path.join(self.cache_dir, file))
                except (OSError, PermissionError):
                    pass

class SmartCache:
    """智能多级缓存系统"""
    def __init__(self, config: Dict[str, Any] = None):
        """初始化智能缓存系统"""
        default_config = {
            'tier1': {
                'max_size': 1000,
                'ttl': 3600
            },
            'tier2': {
                'cache_dir': ".cache",
                'ttl': 86400
            },
            'preload_keys': []
        }
        
        self.config = config or default_config
        self.tier1 = LRUCache(
            max_size=self.config['tier1']['max_size'],
            ttl=self.config['tier1']['ttl']
        )
        self.tier2 = FileCache(
            cache_dir=self.config['tier2']['cache_dir'],
            ttl=self.config['tier2']['ttl']
        )
        self.preload_keys = self.config.get('preload_keys', [])
        self._preload_cache()
    
    def set(self, key: str, value: Any, priority: int = 0):
        """设置缓存到多级"""
        # 同时设置到一级和二级缓存
        self.tier1.set(key, value, priority)
        self.tier2.set(key, value)
    
    def get(self, key: str) -> Optional[Any]:
        """从多级缓存获取"""
        try:
            # 先从一级缓存获取
            value = self.tier1.get(key)
            if value is not None:
                return value
            
            # 从二级缓存获取
            value = self.tier2.get(key)
            if value is not None:
                # 缓存到一级缓存
                self.tier1.set(key, value)
            
            return value
        except Exception as e:
            # Comment in Chinese removed，避免影响主流程
            return None
    
    def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        return self.tier1.exists(key) or self.tier2.get(key) is not None
    
    def delete(self, key: str):
        """删除多级缓存"""
        self.tier1.delete(key)
        self.tier2.delete(key)
    
    def clear(self):
        """清空所有缓存"""
        self.tier1.clear()
        self.tier2.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        return {
            'tier1': self.tier1.get_stats(),
            'tier2': {
                'cache_dir': self.tier2.cache_dir
            },
            'total_hit_rate': self._calculate_total_hit_rate()
        }
    
    def _calculate_total_hit_rate(self) -> float:
        """计算总命中率"""
        tier1_stats = self.tier1.get_stats()
        total_hits = tier1_stats['hit_count']
        total_misses = tier1_stats['miss_count']
        total = total_hits + total_misses
        return (total_hits / total * 100) if total > 0 else 0
    
    def _preload_cache(self):
        """预加载缓存"""
        """
        预加载配置的热点键到缓存中
        """
        if self.preload_keys:
            # 这里可以实现从配置或其他来源加载热点数据的逻辑
            # Comment in Chinese removed获取数据
            pass
    
    def warmup(self, keys: List[str], data_source):
        """预热缓存"""
        """
        data_source: 一个函数，接收key返回对应的值
        """
        for key in keys:
            try:
                value = data_source(key)
                if value is not None:
                    self.set(key, value, priority=1)
            except Exception:
                pass
    
    def warmup_with_pattern(self, pattern: str, data_source):
        """根据模式预热缓存"""
        """
        pattern: 键的模式，例如 "user:*"
        data_source: 一个函数，接收模式返回匹配的键值对
        """
        try:
            key_value_pairs = data_source(pattern)
            for key, value in key_value_pairs.items():
                if value is not None:
                    self.set(key, value, priority=1)
        except Exception:
            pass
    
    def invalidate_pattern(self, pattern: str):
        """根据模式使缓存失效"""
        """
        pattern: 键的模式，例如 "user:*"
        """
        # 这里可以实现根据模式匹配并删除缓存的逻辑
        # 例如使用正则表达式匹配键
        pass
    
    def invalidate_all(self):
        """使所有缓存失效"""
        self.clear()
    
    def set_ttl(self, key: str, ttl: int):
        """为特定键设置过期时间"""
        """
        key: 缓存键
        ttl: 过期时间（秒）
        """
        # 这里可以实现为特定键设置不同过期时间的逻辑
        pass

# Comment in Chinese removed接口
class MemoryCache(LRUCache):
    """兼容旧接口的内存缓存"""
    pass