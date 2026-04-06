import time
import unittest
from memory_classification_engine.utils.cache import LRUCache, FileCache, SmartCache

class TestCache(unittest.TestCase):
    def test_lru_cache(self):
        """测试LRU缓存基本功能"""
        cache = LRUCache(max_size=3, ttl=1)
        
        # 测试设置和获取
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')
        cache.set('key3', 'value3')
        
        self.assertEqual(cache.get('key1'), 'value1')
        self.assertEqual(cache.get('key2'), 'value2')
        self.assertEqual(cache.get('key3'), 'value3')
        
        # 测试LRU驱逐
        cache.set('key4', 'value4')
        self.assertIsNone(cache.get('key1'))  # key1应该被驱逐
        self.assertEqual(cache.get('key2'), 'value2')
        self.assertEqual(cache.get('key3'), 'value3')
        self.assertEqual(cache.get('key4'), 'value4')
        
        # 测试过期
        time.sleep(1.1)
        self.assertIsNone(cache.get('key2'))
        
        # 测试统计
        stats = cache.get_stats()
        self.assertIn('hit_count', stats)
        self.assertIn('miss_count', stats)
        self.assertIn('hit_rate', stats)
    
    def test_file_cache(self):
        """测试文件缓存基本功能"""
        cache = FileCache(cache_dir=".test_cache", ttl=1)
        
        # 测试设置和获取
        cache.set('file_key1', 'file_value1')
        self.assertEqual(cache.get('file_key1'), 'file_value1')
        
        # 测试过期
        time.sleep(1.1)
        self.assertIsNone(cache.get('file_key1'))
        
        # 清理
        cache.clear()
    
    def test_smart_cache(self):
        """测试智能多级缓存"""
        cache = SmartCache({
            'tier1': {
                'max_size': 2,
                'ttl': 1
            },
            'tier2': {
                'cache_dir': ".test_smart_cache",
                'ttl': 2
            }
        })
        
        # 测试设置和获取
        cache.set('smart_key1', 'smart_value1')
        cache.set('smart_key2', 'smart_value2')
        
        # 一级缓存命中
        self.assertEqual(cache.get('smart_key1'), 'smart_value1')
        
        # 测试LRU驱逐
        cache.set('smart_key3', 'smart_value3')
        
        # 测试key1仍然存在于一级缓存
        self.assertEqual(cache.get('smart_key1'), 'smart_value1')
        
        # 测试key2可以从二级缓存获取
        self.assertEqual(cache.get('smart_key2'), 'smart_value2')
        
        # 清理
        cache.clear()
    
    def test_cache_performance(self):
        """测试缓存性能"""
        cache = SmartCache()
        
        # 测试设置性能
        start_time = time.time()
        for i in range(1000):
            cache.set(f'key{i}', f'value{i}')
        set_time = time.time() - start_time
        print(f"Set 1000 items: {set_time:.4f}s")
        
        # 测试获取性能
        start_time = time.time()
        hits = 0
        for i in range(1000):
            if cache.get(f'key{i}') is not None:
                hits += 1
        get_time = time.time() - start_time
        print(f"Get 1000 items: {get_time:.4f}s, Hits: {hits}")
        
        # 测试命中率
        stats = cache.get_stats()
        print(f"Hit rate: {stats['total_hit_rate']:.2f}%")
        
        # 清理
        cache.clear()
    
    def test_cache_warmup(self):
        """测试缓存预热"""
        cache = SmartCache()
        
        # 定义数据源
        def data_source(key):
            return f'value_{key}'
        
        # 预热缓存
        keys = ['warmup1', 'warmup2', 'warmup3']
        cache.warmup(keys, data_source)
        
        # 验证预热结果
        for key in keys:
            self.assertEqual(cache.get(key), f'value_{key}')
        
        # 清理
        cache.clear()

if __name__ == '__main__':
    unittest.main()