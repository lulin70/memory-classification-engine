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
    
    def __init__(self, enabled: bool = True, log_interval: int = 60, alert_thresholds: Optional[Dict[str, Any]] = None):
        """Initialize the performance monitor.
        
        Args:
            enabled: Whether performance monitoring is enabled.
            log_interval: Logging interval in seconds.
            alert_thresholds: Thresholds for performance alerts.
        """
        self.enabled = enabled
        self.log_interval = log_interval
        self.alert_thresholds = alert_thresholds or {
            'memory': 80,
            'cpu': 90,
            'disk': 90,
            'response_time': 1.0,
            'cache_hit_rate': 70
        }
        self.metrics = {
            'memory': {
                'usage': 0,
                'peak': 0,
                'trend': [],
                'alerts': []
            },
            'cpu': {
                'usage': 0,
                'peak': 0,
                'trend': [],
                'alerts': []
            },
            'disk': {
                'usage': 0,
                'peak': 0,
                'trend': [],
                'alerts': []
            },
            'response_times': {
                'process_message': [],
                'retrieve_memories': [],
                'store_memory': [],
                'alerts': []
            },
            'throughput': {
                'messages_processed': 0,
                'memories_stored': 0,
                'queries_processed': 0,
                'rate': 0  # Comment in Chinese removedcond
            },
            'cache': {
                'hit_count': 0,
                'miss_count': 0,
                'hit_rate': 0,
                'size': 0,
                'expired_count': 0,
                'alerts': []
            },
            'storage': {
                'read_operations': 0,
                'write_operations': 0,
                'read_time': 0,
                'write_time': 0
            },
            'last_log_time': time.time(),
            'last_throughput_time': time.time(),
            'last_throughput_count': 0
        }
        
        # Comment in Chinese removedo
        self.process = psutil.Process(os.getpid())
        
        # Comment in Chinese removedd
        self.monitoring_thread = None
        self.running = False
        
        logger.info("PerformanceMonitor initialized")
    
    def start(self):
        """Start performance monitoring."""
        if self.enabled:
            logger.info("Starting performance monitoring")
            self.running = True
            # Comment in Chinese removedd
            import threading
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitoring_thread.start()
    
    def stop(self):
        """Stop performance monitoring."""
        if self.enabled:
            logger.info("Stopping performance monitoring")
            self.running = False
            if self.monitoring_thread:
                self.monitoring_thread.join(timeout=5)
    
    def _monitoring_loop(self):
        """Background monitoring loop."""
        while self.running:
            try:
                self.record_metrics()
                self._check_alerts()
                self.log_metrics()
                # Comment in Chinese removedl
                time.sleep(self.log_interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(1)  # Comment in Chinese removedtrying
    
    def _check_alerts(self):
        """Check for performance alerts."""
        if not self.enabled:
            return
        
        alerts = []
        
        # Comment in Chinese removed
        memory_usage_percent = psutil.virtual_memory().percent
        if memory_usage_percent > self.alert_thresholds['memory']:
            alert = {
                'timestamp': datetime.now().isoformat(),
                'type': 'memory',
                'message': f"Memory usage high: {memory_usage_percent:.2f}%",
                'severity': 'warning' if memory_usage_percent < 95 else 'critical'
            }
            self.metrics['memory']['alerts'].append(alert)
            alerts.append(alert)
        
        # Comment in Chinese removed
        cpu_usage = psutil.cpu_percent(interval=0.1)
        if cpu_usage > self.alert_thresholds['cpu']:
            alert = {
                'timestamp': datetime.now().isoformat(),
                'type': 'cpu',
                'message': f"CPU usage high: {cpu_usage:.2f}%",
                'severity': 'warning' if cpu_usage < 98 else 'critical'
            }
            self.metrics['cpu']['alerts'].append(alert)
            alerts.append(alert)
        
        # Comment in Chinese removed
        disk_usage_percent = psutil.disk_usage('.').percent
        if disk_usage_percent > self.alert_thresholds['disk']:
            alert = {
                'timestamp': datetime.now().isoformat(),
                'type': 'disk',
                'message': f"Disk usage high: {disk_usage_percent:.2f}%",
                'severity': 'warning' if disk_usage_percent < 98 else 'critical'
            }
            self.metrics['disk']['alerts'].append(alert)
            alerts.append(alert)
        
        # Comment in Chinese removeds
        for operation, times in self.metrics['response_times'].items():
            if times and operation != 'alerts':
                avg_time = sum(times) / len(times)
                if avg_time > self.alert_thresholds['response_time']:
                    alert = {
                        'timestamp': datetime.now().isoformat(),
                        'type': 'response_time',
                        'message': f"{operation} response time high: {avg_time:.4f}s",
                        'severity': 'warning'
                    }
                    self.metrics['response_times']['alerts'].append(alert)
                    alerts.append(alert)
        
        # Comment in Chinese removed
        if self.metrics['cache']['hit_rate'] < self.alert_thresholds['cache_hit_rate']:
            # 只在有实际缓存操作时才告警
            if self.metrics['cache']['hit_count'] + self.metrics['cache']['miss_count'] > 0:
                alert = {
                    'timestamp': datetime.now().isoformat(),
                    'type': 'cache',
                    'message': f"Cache hit rate low: {self.metrics['cache']['hit_rate']:.2f}%",
                    'severity': 'warning'
                }
                self.metrics['cache']['alerts'].append(alert)
                alerts.append(alert)
        
        # Comment in Chinese removedrts
        for alert in alerts:
            if alert['severity'] == 'critical':
                logger.critical(f"[PERFORMANCE ALERT] {alert['message']}")
            else:
                logger.warning(f"[PERFORMANCE ALERT] {alert['message']}")
        
        # Comment in Chinese removeds
        for key in ['memory', 'cpu', 'disk', 'response_times', 'cache']:
            if 'alerts' in self.metrics[key]:
                if len(self.metrics[key]['alerts']) > 50:
                    self.metrics[key]['alerts'] = self.metrics[key]['alerts'][-50:]
    
    def record_metrics(self):
        """Record current performance metrics."""
        if not self.enabled:
            return
        
        try:
            # Comment in Chinese removed
            memory_info = self.process.memory_info()
            memory_usage = memory_info.rss / 1024 / 1024  # Comment in Chinese removed
            memory_usage_percent = psutil.virtual_memory().percent
            
            # Comment in Chinese removed
            cpu_usage = self.process.cpu_percent(interval=0.1)
            
            # Comment in Chinese removed
            disk_usage = psutil.disk_usage('.')
            disk_usage_percent = disk_usage.percent
            
            # Comment in Chinese removedtrics
            self.metrics['memory']['usage'] = memory_usage
            self.metrics['memory']['peak'] = max(self.metrics['memory']['peak'], memory_usage)
            self.metrics['memory']['trend'].append(memory_usage)
            
            self.metrics['cpu']['usage'] = cpu_usage
            self.metrics['cpu']['peak'] = max(self.metrics['cpu']['peak'], cpu_usage)
            self.metrics['cpu']['trend'].append(cpu_usage)
            
            self.metrics['disk']['usage'] = disk_usage_percent
            self.metrics['disk']['peak'] = max(self.metrics['disk']['peak'], disk_usage_percent)
            self.metrics['disk']['trend'].append(disk_usage_percent)
            
            # Comment in Chinese removed
            current_time = time.time()
            elapsed_time = current_time - self.metrics['last_throughput_time']
            if elapsed_time > 0:
                current_count = self.metrics['throughput']['messages_processed']
                message_rate = (current_count - self.metrics['last_throughput_count']) / elapsed_time
                self.metrics['throughput']['rate'] = message_rate
                self.metrics['last_throughput_time'] = current_time
                self.metrics['last_throughput_count'] = current_count
            
            # Comment in Chinese removeds
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
            
            # Comment in Chinese removeds
            for operation, times in self.metrics['response_times'].items():
                if times and operation != 'alerts':
                    avg_time = sum(times) / len(times)
                    logger.info(f"{operation}: {avg_time:.4f}s average")
            
            # Comment in Chinese removedtrics
            logger.info(f"Throughput: {self.metrics['throughput']['messages_processed']} messages, {self.metrics['throughput']['memories_stored']} memories, {self.metrics['throughput']['queries_processed']} queries")
            logger.info(f"Throughput Rate: {self.metrics['throughput']['rate']:.2f} messages/second")
            
            # Comment in Chinese removedtrics
            logger.info(f"Cache: Hit Rate {self.metrics['cache']['hit_rate']:.2f}%, {self.metrics['cache']['hit_count']} hits, {self.metrics['cache']['miss_count']} misses")
            logger.info(f"Cache Size: {self.metrics['cache']['size']} items, {self.metrics['cache']['expired_count']} expired")
            
            # Comment in Chinese removedtrics
            storage = self.metrics['storage']
            logger.info(f"Storage: {storage['read_operations']} reads, {storage['write_operations']} writes")
            if storage['read_operations'] > 0:
                avg_read_time = storage['read_time'] / storage['read_operations']
                logger.info(f"Average Read Time: {avg_read_time:.4f}s")
            if storage['write_operations'] > 0:
                avg_write_time = storage['write_time'] / storage['write_operations']
                logger.info(f"Average Write Time: {avg_write_time:.4f}s")
            
            # Comment in Chinese removedry
            total_alerts = 0
            for key in ['memory', 'cpu', 'disk', 'response_times', 'cache']:
                if 'alerts' in self.metrics[key]:
                    total_alerts += len(self.metrics[key]['alerts'])
            if total_alerts > 0:
                logger.warning(f"Performance Alerts: {total_alerts} recent alerts")
            
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
        
        # Comment in Chinese removedxist
        if operation not in self.metrics['response_times']:
            self.metrics['response_times'][operation] = []
        
        self.metrics['response_times'][operation].append(duration)
        # Comment in Chinese removeds
        if len(self.metrics['response_times'][operation]) > 100:
            self.metrics['response_times'][operation] = self.metrics['response_times'][operation][-100:]
    
    def increment_throughput(self, operation: str):
        """Increment throughput counter for an operation.
        
        Args:
            operation: Operation name.
        """
        if not self.enabled:
            return
        
        # Comment in Chinese removedxist
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
        
        # Comment in Chinese removedtrics
        self.metrics['cache']['hit_count'] = cache_stats.get('hit_count', 0)
        self.metrics['cache']['miss_count'] = cache_stats.get('miss_count', 0)
        self.metrics['cache']['hit_rate'] = cache_stats.get('hit_rate', 0)
        self.metrics['cache']['size'] = cache_stats.get('size', 0)
        self.metrics['cache']['expired_count'] = cache_stats.get('expired_count', 0)
    
    def record_storage_operation(self, operation_type: str, duration: float):
        """Record storage operation metrics.
        
        Args:
            operation_type: Type of storage operation ('read' or 'write').
            duration: Duration in seconds.
        """
        if not self.enabled:
            return
        
        if operation_type == 'read':
            self.metrics['storage']['read_operations'] += 1
            self.metrics['storage']['read_time'] += duration
        elif operation_type == 'write':
            self.metrics['storage']['write_operations'] += 1
            self.metrics['storage']['write_time'] += duration
    
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
                'average': sum(self.metrics['memory']['trend']) / len(self.metrics['memory']['trend']) if self.metrics['memory']['trend'] else 0,
                'alerts': len(self.metrics['memory'].get('alerts', []))
            },
            'cpu': {
                'current': self.metrics['cpu']['usage'],
                'peak': self.metrics['cpu']['peak'],
                'average': sum(self.metrics['cpu']['trend']) / len(self.metrics['cpu']['trend']) if self.metrics['cpu']['trend'] else 0,
                'alerts': len(self.metrics['cpu'].get('alerts', []))
            },
            'disk': {
                'current': self.metrics['disk']['usage'],
                'peak': self.metrics['disk']['peak'],
                'average': sum(self.metrics['disk']['trend']) / len(self.metrics['disk']['trend']) if self.metrics['disk']['trend'] else 0,
                'alerts': len(self.metrics['disk'].get('alerts', []))
            },
            'throughput': self.metrics['throughput'],
            'cache': self.metrics['cache'],
            'storage': self.metrics['storage']
        }
        
        # Comment in Chinese removeds
        for operation, times in self.metrics['response_times'].items():
            if times and operation != 'alerts':
                summary['response_times'] = summary.get('response_times', {})
                summary['response_times'][operation] = {
                    'average': sum(times) / len(times),
                    'count': len(times)
                }
        
        # Comment in Chinese removedry
        total_alerts = 0
        for key in ['memory', 'cpu', 'disk', 'response_times', 'cache']:
            if 'alerts' in self.metrics[key]:
                total_alerts += len(self.metrics[key]['alerts'])
        summary['alerts'] = total_alerts
        
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
        # Comment in Chinese removed
        query = ' '.join(query.split())
        
        # Comment in Chinese removed common stop words
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
