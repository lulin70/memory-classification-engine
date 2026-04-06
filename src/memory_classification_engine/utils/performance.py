"""Performance monitoring and optimization utilities."""

import time
import psutil
import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from memory_classification_engine.utils.logger import logger


class PerformanceMonitor:
    """Performance monitoring system for Memory Classification Engine."""
    
    def __init__(self, enabled: bool = True, log_interval: int = 60):
        """Initialize the performance monitor.
        
        Args:
            enabled: Whether performance monitoring is enabled.
            log_interval: Logging interval in seconds.
        """
        self.enabled = enabled
        self.log_interval = log_interval
        self.metrics = {
            'memory': {
                'usage': 0,
                'peak': 0,
                'trend': []
            },
            'cpu': {
                'usage': 0,
                'peak': 0,
                'trend': []
            },
            'disk': {
                'usage': 0,
                'peak': 0,
                'trend': []
            },
            'response_times': {
                'process_message': [],
                'retrieve_memories': [],
                'store_memory': []
            },
            'throughput': {
                'messages_processed': 0,
                'memories_stored': 0,
                'queries_processed': 0
            },
            'cache': {
                'hit_count': 0,
                'miss_count': 0,
                'hit_rate': 0,
                'size': 0,
                'expired_count': 0
            },
            'last_log_time': time.time()
        }
        
        # Process info
        self.process = psutil.Process(os.getpid())
        
        logger.info("PerformanceMonitor initialized")
    
    def start(self):
        """Start performance monitoring."""
        if self.enabled:
            logger.info("Starting performance monitoring")
    
    def stop(self):
        """Stop performance monitoring."""
        if self.enabled:
            logger.info("Stopping performance monitoring")
    
    def record_metrics(self):
        """Record current performance metrics."""
        if not self.enabled:
            return
        
        try:
            # Memory usage
            memory_info = self.process.memory_info()
            memory_usage = memory_info.rss / 1024 / 1024  # MB
            
            # CPU usage
            cpu_usage = self.process.cpu_percent(interval=0.1)
            
            # Disk usage
            disk_usage = psutil.disk_usage('.')
            disk_usage_percent = disk_usage.percent
            
            # Update metrics
            self.metrics['memory']['usage'] = memory_usage
            self.metrics['memory']['peak'] = max(self.metrics['memory']['peak'], memory_usage)
            self.metrics['memory']['trend'].append(memory_usage)
            
            self.metrics['cpu']['usage'] = cpu_usage
            self.metrics['cpu']['peak'] = max(self.metrics['cpu']['peak'], cpu_usage)
            self.metrics['cpu']['trend'].append(cpu_usage)
            
            self.metrics['disk']['usage'] = disk_usage_percent
            self.metrics['disk']['peak'] = max(self.metrics['disk']['peak'], disk_usage_percent)
            self.metrics['disk']['trend'].append(disk_usage_percent)
            
            # Keep trends to last 100 entries
            for key in ['memory', 'cpu', 'disk']:
                if len(self.metrics[key]['trend']) > 100:
                    self.metrics[key]['trend'] = self.metrics[key]['trend'][-100:]
            
        except Exception as e:
            logger.error(f"Error recording metrics: {e}")
    
    def log_metrics(self):
        """Log performance metrics."""
        if not self.enabled:
            return
        
        current_time = time.time()
        if current_time - self.metrics['last_log_time'] >= self.log_interval:
            self.record_metrics()
            
            logger.info(f"\n=== Performance Metrics ===")
            logger.info(f"Memory: {self.metrics['memory']['usage']:.2f} MB (Peak: {self.metrics['memory']['peak']:.2f} MB)")
            logger.info(f"CPU: {self.metrics['cpu']['usage']:.2f}% (Peak: {self.metrics['cpu']['peak']:.2f}%)")
            logger.info(f"Disk: {self.metrics['disk']['usage']:.2f}% (Peak: {self.metrics['disk']['peak']:.2f}%)")
            
            # Calculate response time averages
            if self.metrics['response_times']['process_message']:
                avg_time = sum(self.metrics['response_times']['process_message']) / len(self.metrics['response_times']['process_message'])
                logger.info(f"Process Message: {avg_time:.4f}s average")
            
            if self.metrics['response_times']['retrieve_memories']:
                avg_time = sum(self.metrics['response_times']['retrieve_memories']) / len(self.metrics['response_times']['retrieve_memories'])
                logger.info(f"Retrieve Memories: {avg_time:.4f}s average")
            
            if self.metrics['response_times']['store_memory']:
                avg_time = sum(self.metrics['response_times']['store_memory']) / len(self.metrics['response_times']['store_memory'])
                logger.info(f"Store Memory: {avg_time:.4f}s average")
            
            logger.info(f"Throughput: {self.metrics['throughput']['messages_processed']} messages, {self.metrics['throughput']['memories_stored']} memories, {self.metrics['throughput']['queries_processed']} queries")
            
            # Cache metrics
            logger.info(f"Cache: Hit Rate {self.metrics['cache']['hit_rate']:.2f}%, {self.metrics['cache']['hit_count']} hits, {self.metrics['cache']['miss_count']} misses")
            logger.info(f"Cache Size: {self.metrics['cache']['size']} items, {self.metrics['cache']['expired_count']} expired")
            
            logger.info(f"=========================\n")
            
            self.metrics['last_log_time'] = current_time
    
    def record_response_time(self, operation: str, duration: float):
        """Record response time for an operation.
        
        Args:
            operation: Operation name.
            duration: Duration in seconds.
        """
        if not self.enabled:
            return
        
        # Add operation to response_times if it doesn't exist
        if operation not in self.metrics['response_times']:
            self.metrics['response_times'][operation] = []
        
        self.metrics['response_times'][operation].append(duration)
        # Keep only last 100 entries
        if len(self.metrics['response_times'][operation]) > 100:
            self.metrics['response_times'][operation] = self.metrics['response_times'][operation][-100:]
    
    def increment_throughput(self, operation: str):
        """Increment throughput counter for an operation.
        
        Args:
            operation: Operation name.
        """
        if not self.enabled:
            return
        
        # Add operation to throughput if it doesn't exist
        if operation not in self.metrics['throughput']:
            self.metrics['throughput'][operation] = 0
        
        self.metrics['throughput'][operation] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics.
        
        Returns:
            Performance metrics.
        """
        self.record_metrics()
        return self.metrics
    
    def record_cache_metrics(self, cache_stats: Dict[str, Any]):
        """Record cache performance metrics.
        
        Args:
            cache_stats: Cache statistics from SmartCache.
        """
        if not self.enabled:
            return
        
        # Update cache metrics
        self.metrics['cache']['hit_count'] = cache_stats.get('hit_count', 0)
        self.metrics['cache']['miss_count'] = cache_stats.get('miss_count', 0)
        self.metrics['cache']['hit_rate'] = cache_stats.get('hit_rate', 0)
        self.metrics['cache']['size'] = cache_stats.get('size', 0)
        self.metrics['cache']['expired_count'] = cache_stats.get('expired_count', 0)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary.
        
        Returns:
            Performance summary.
        """
        self.record_metrics()
        
        summary = {
            'memory': {
                'current': self.metrics['memory']['usage'],
                'peak': self.metrics['memory']['peak'],
                'average': sum(self.metrics['memory']['trend']) / len(self.metrics['memory']['trend']) if self.metrics['memory']['trend'] else 0
            },
            'cpu': {
                'current': self.metrics['cpu']['usage'],
                'peak': self.metrics['cpu']['peak'],
                'average': sum(self.metrics['cpu']['trend']) / len(self.metrics['cpu']['trend']) if self.metrics['cpu']['trend'] else 0
            },
            'disk': {
                'current': self.metrics['disk']['usage'],
                'peak': self.metrics['disk']['peak'],
                'average': sum(self.metrics['disk']['trend']) / len(self.metrics['disk']['trend']) if self.metrics['disk']['trend'] else 0
            },
            'throughput': self.metrics['throughput'],
            'cache': self.metrics['cache']
        }
        
        # Add response time averages
        for operation, times in self.metrics['response_times'].items():
            if times:
                summary['response_times'] = summary.get('response_times', {})
                summary['response_times'][operation] = {
                    'average': sum(times) / len(times),
                    'count': len(times)
                }
        
        return summary
    
    def export_metrics(self, filename: str):
        """Export metrics to a file.
        
        Args:
            filename: Filename to export to.
        """
        if not self.enabled:
            return
        
        try:
            metrics = self.get_metrics()
            metrics['export_time'] = datetime.now().isoformat()
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(metrics, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Metrics exported to {filename}")
        except Exception as e:
            logger.error(f"Error exporting metrics: {e}")


class PerformanceOptimizer:
    """Performance optimization utilities."""
    
    @staticmethod
    def optimize_query(query: str) -> str:
        """Optimize a search query.
        
        Args:
            query: Original query.
            
        Returns:
            Optimized query.
        """
        # Remove redundant whitespace
        query = ' '.join(query.split())
        
        # Remove common stop words
        stop_words = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'with', 'by']
        words = query.split()
        optimized_words = [word for word in words if word.lower() not in stop_words]
        
        if not optimized_words:
            return query
        
        return ' '.join(optimized_words)
    
    @staticmethod
    def batch_process(func, items: List[Any], batch_size: int = 100):
        """Process items in batches to reduce memory usage.
        
        Args:
            func: Function to apply to each batch.
            items: List of items to process.
            batch_size: Batch size.
            
        Returns:
            List of results.
        """
        results = []
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_results = func(batch)
            results.extend(batch_results)
        
        return results
    
    @staticmethod
    def memory_efficient_iteration(iterable, batch_size: int = 1000):
        """Memory-efficient iteration over large iterables.
        
        Args:
            iterable: Iterable to process.
            batch_size: Batch size.
            
        Yields:
            Batches of items.
        """
        batch = []
        for item in iterable:
            batch.append(item)
            if len(batch) >= batch_size:
                yield batch
                batch = []
        
        if batch:
            yield batch
    
    @staticmethod
    def cache_key_generator(prefix: str, **kwargs) -> str:
        """Generate a cache key from parameters.
        
        Args:
            prefix: Cache key prefix.
            **kwargs: Parameters to include in the key.
            
        Returns:
            Cache key.
        """
        key_parts = [prefix]
        
        for k, v in sorted(kwargs.items()):
            if v is not None:
                key_parts.append(f"{k}:{v}")
        
        return ':'.join(key_parts)
