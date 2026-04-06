"""Test memory management functionality."""

import unittest
import time
from memory_classification_engine.utils.config import ConfigManager
from memory_classification_engine.utils.memory_manager import MemoryManager, SmartCache


class TestMemoryManager(unittest.TestCase):
    """Test memory manager functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = ConfigManager()
        self.memory_manager = MemoryManager(self.config)
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.memory_manager.stop()
    
    def test_initialization(self):
        """Test memory manager initialization."""
        self.assertIsNotNone(self.memory_manager)
        self.assertEqual(self.memory_manager.metrics['current_usage'], 0)
    
    def test_memory_metrics(self):
        """Test memory metrics collection."""
        self.memory_manager._update_memory_metrics()
        metrics = self.memory_manager.get_memory_metrics()
        
        self.assertIn('current_usage', metrics)
        self.assertIn('available_memory', metrics)
        self.assertIn('memory_percent', metrics)
        self.assertGreaterEqual(metrics['current_usage'], 0)
        self.assertGreaterEqual(metrics['available_memory'], 0)
        self.assertGreaterEqual(metrics['memory_percent'], 0)
        self.assertLessEqual(metrics['memory_percent'], 100)
    
    def test_memory_history(self):
        """Test memory usage history."""
        self.memory_manager._update_memory_metrics()
        history = self.memory_manager.get_memory_history()
        
        self.assertGreater(len(history), 0)
        self.assertIn('timestamp', history[0])
        self.assertIn('usage', history[0])
        self.assertIn('available', history[0])
        self.assertIn('percent', history[0])
    
    def test_memory_fragmentation(self):
        """Test memory fragmentation calculation."""
        # Generate some memory usage history
        for _ in range(10):
            self.memory_manager._update_memory_metrics()
            time.sleep(0.1)
        
        fragmentation = self.memory_manager.calculate_memory_fragmentation()
        self.assertGreaterEqual(fragmentation, 0)
        self.assertLessEqual(fragmentation, 1)
    
    def test_garbage_collection(self):
        """Test garbage collection functionality."""
        initial_collections = self.memory_manager.metrics['collections']
        self.memory_manager._force_garbage_collection()
        
        self.assertGreater(self.memory_manager.metrics['collections'], initial_collections)
    
    def test_memory_summary(self):
        """Test memory usage summary."""
        summary = self.memory_manager.get_memory_summary()
        
        self.assertIn('current_usage', summary)
        self.assertIn('available_memory', summary)
        self.assertIn('memory_percent', summary)
        self.assertIn('peak_usage', summary)
        self.assertIn('memory_fragmentation', summary)
        self.assertIn('collections', summary)
        self.assertIn('limits', summary)
        self.assertIn('alerts', summary)
    
    def test_alert_triggering(self):
        """Test alert triggering functionality."""
        initial_alerts = len(self.memory_manager.get_alert_history())
        
        # Trigger a warning alert
        self.memory_manager._trigger_alert('warning', 'Test warning alert')
        alerts = self.memory_manager.get_alert_history()
        
        self.assertGreater(len(alerts), initial_alerts)
        self.assertEqual(alerts[-1]['level'], 'warning')
        self.assertEqual(alerts[-1]['message'], 'Test warning alert')
    
    def test_memory_limits_adjustment(self):
        """Test memory limits adjustment."""
        initial_limits = self.memory_manager.get_memory_limits().copy()
        
        # Test normal adjustment
        self.memory_manager._adjust_memory_limits()
        new_limits = self.memory_manager.get_memory_limits()
        
        # Create a new memory manager for aggressive test
        aggressive_manager = MemoryManager(self.config)
        aggressive_manager._adjust_memory_limits(aggressive=True)
        aggressive_limits = aggressive_manager.get_memory_limits()
        
        # Create a new memory manager for emergency test
        emergency_manager = MemoryManager(self.config)
        emergency_manager._adjust_memory_limits(emergency=True)
        emergency_limits = emergency_manager.get_memory_limits()
        
        # Clean up
        aggressive_manager.stop()
        emergency_manager.stop()
        
        # Emergency limits should be smaller than aggressive limits
        self.assertLess(emergency_limits['cache'], aggressive_limits['cache'])
        self.assertLess(emergency_limits['working_memory'], aggressive_limits['working_memory'])
        self.assertLess(emergency_limits['batch_size'], aggressive_limits['batch_size'])


class TestSmartCache(unittest.TestCase):
    """Test smart cache functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.cache = SmartCache(initial_size=10, ttl=1)
    
    def test_cache_operations(self):
        """Test basic cache operations."""
        # Test set and get
        self.cache.set('key1', 'value1')
        self.assertEqual(self.cache.get('key1'), 'value1')
        
        # Test miss
        self.assertIsNone(self.cache.get('non_existent_key'))
        
        # Test cache size limit
        for i in range(15):
            self.cache.set(f'key{i}', f'value{i}')
        
        # Should only have 10 items
        stats = self.cache.get_stats()
        self.assertEqual(stats['size'], 10)
    
    def test_cache_expiration(self):
        """Test cache expiration."""
        self.cache.set('key1', 'value1')
        self.assertEqual(self.cache.get('key1'), 'value1')
        
        # Wait for TTL to expire
        time.sleep(1.1)
        
        # Should return None after expiration
        self.assertIsNone(self.cache.get('key1'))
    
    def test_cache_stats(self):
        """Test cache statistics."""
        # Test hits and misses
        self.cache.set('key1', 'value1')
        self.cache.get('key1')  # Hit
        self.cache.get('non_existent')  # Miss
        
        stats = self.cache.get_stats()
        self.assertEqual(stats['hit_count'], 1)
        self.assertEqual(stats['miss_count'], 1)
        self.assertGreater(stats['hit_rate'], 0)
    
    def test_cache_resizing(self):
        """Test cache resizing."""
        # Set initial size
        self.cache.set_size(5)
        
        # Add items
        for i in range(10):
            self.cache.set(f'key{i}', f'value{i}')
        
        stats = self.cache.get_stats()
        self.assertEqual(stats['size'], 5)
        self.assertEqual(stats['max_size'], 5)
    
    def test_cache_clear(self):
        """Test cache clearing."""
        self.cache.set('key1', 'value1')
        self.cache.set('key2', 'value2')
        
        stats = self.cache.get_stats()
        self.assertEqual(stats['size'], 2)
        
        self.cache.clear()
        stats = self.cache.get_stats()
        self.assertEqual(stats['size'], 0)
    
    def test_memory_usage_estimate(self):
        """Test memory usage estimation."""
        for i in range(100):
            self.cache.set(f'key{i}', f'value{i}')
        
        memory_usage = self.cache.get_memory_usage()
        self.assertGreater(memory_usage, 0)


if __name__ == '__main__':
    unittest.main()
