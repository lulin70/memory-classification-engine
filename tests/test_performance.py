"""Tests for performance monitoring functionality."""

import pytest
import tempfile
import os
from memory_classification_engine.utils.performance import PerformanceMonitor, PerformanceOptimizer


class TestPerformanceMonitor:
    """Test performance monitor functionality."""
    
    @pytest.fixture
    def monitor(self):
        """Create a performance monitor for testing."""
        return PerformanceMonitor(enabled=True, log_interval=1)
    
    def test_initialization(self, monitor):
        """Test monitor initialization."""
        assert monitor is not None
        assert monitor.enabled is True
    
    def test_record_metrics(self, monitor):
        """Test recording metrics."""
        monitor.record_metrics()
        metrics = monitor.get_metrics()
        assert 'memory' in metrics
        assert 'cpu' in metrics
        assert 'disk' in metrics
        assert metrics['memory']['usage'] >= 0
        assert metrics['cpu']['usage'] >= 0
        assert metrics['disk']['usage'] >= 0
    
    def test_record_response_time(self, monitor):
        """Test recording response time."""
        monitor.record_response_time('test_operation', 0.1)
        metrics = monitor.get_metrics()
        assert 'test_operation' in metrics['response_times']
        assert len(metrics['response_times']['test_operation']) == 1
        assert metrics['response_times']['test_operation'][0] == 0.1
    
    def test_increment_throughput(self, monitor):
        """Test incrementing throughput."""
        monitor.increment_throughput('messages_processed')
        metrics = monitor.get_metrics()
        assert metrics['throughput']['messages_processed'] == 1
    
    def test_get_summary(self, monitor):
        """Test getting performance summary."""
        monitor.record_metrics()
        summary = monitor.get_summary()
        assert 'memory' in summary
        assert 'cpu' in summary
        assert 'disk' in summary
        assert 'throughput' in summary
    
    def test_export_metrics(self, monitor):
        """Test exporting metrics."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            monitor.export_metrics(temp_file)
            assert os.path.exists(temp_file)
            assert os.path.getsize(temp_file) > 0
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


class TestPerformanceOptimizer:
    """Test performance optimizer functionality."""
    
    def test_optimize_query(self):
        """Test query optimization."""
        original_query = "   the quick brown fox jumps over the lazy dog   "
        optimized = PerformanceOptimizer.optimize_query(original_query)
        assert optimized == "quick brown fox jumps over lazy dog"
        assert "the" not in optimized
    
    def test_optimize_query_empty(self):
        """Test optimizing empty query."""
        optimized = PerformanceOptimizer.optimize_query("")
        assert optimized == ""
    
    def test_optimize_query_stop_words_only(self):
        """Test optimizing query with only stop words."""
        query = "the and or"
        optimized = PerformanceOptimizer.optimize_query(query)
        assert optimized == query  # Should return original if all are stop words
    
    def test_batch_process(self):
        """Test batch processing."""
        def square_batch(batch):
            return [x * x for x in batch]
        
        items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        result = PerformanceOptimizer.batch_process(square_batch, items, batch_size=3)
        expected = [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]
        assert result == expected
    
    def test_memory_efficient_iteration(self):
        """Test memory-efficient iteration."""
        items = list(range(10))
        batches = list(PerformanceOptimizer.memory_efficient_iteration(items, batch_size=3))
        assert len(batches) == 4  # 3 batches of 3, 1 batch of 1
        assert batches[0] == [0, 1, 2]
        assert batches[1] == [3, 4, 5]
        assert batches[2] == [6, 7, 8]
        assert batches[3] == [9]
    
    def test_cache_key_generator(self):
        """Test cache key generation."""
        key = PerformanceOptimizer.cache_key_generator('test', a=1, b='2', c=None)
        assert key == "test:a:1:b:2"
        assert "c:" not in key  # None values should be excluded
