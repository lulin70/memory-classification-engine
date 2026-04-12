"""Dynamic memory management system."""

import time
import psutil
import os
import gc
import threading
from typing import Dict, List, Optional, Any
from memory_classification_engine.utils.logger import logger
from memory_classification_engine.utils.config import ConfigManager


class MemoryManager:
    """Dynamic memory management system for Memory Classification Engine."""
    
    def __init__(self, config: ConfigManager):
        """Initialize the memory manager.
        
        Args:
            config: Configuration manager instance.
        """
        self.config = config
        self.process = psutil.Process(os.getpid())
        
        # Comment in Chinese removedsholds
        self.memory_thresholds = {
            'warning': self.config.get('memory.thresholds.warning', 70),  # Comment in Chinese removedmory
            'critical': self.config.get('memory.thresholds.critical', 85),  # Comment in Chinese removedmory
            'emergency': self.config.get('memory.thresholds.emergency', 95)  # Comment in Chinese removedmory
        }
        
        # Comment in Chinese removedmory limits
        self.memory_limits = {
            'working_memory': self.config.get('memory.limits.working_memory', 100),
            'cache': self.config.get('memory.limits.cache', 1000),
            'batch_size': self.config.get('memory.limits.batch_size', 100)
        }
        
        # Comment in Chinese removed history
        self.memory_history = []
        self.history_max_length = 100
        
        # Comment in Chinese removedttings
        self.optimization_enabled = self.config.get('memory.optimization.enabled', True)
        self.optimization_interval = self.config.get('memory.optimization.interval', 60)  # Comment in Chinese removedconds
        
        # Comment in Chinese removedttings
        self.gc_enabled = self.config.get('memory.gc.enabled', True)
        self.gc_threshold = self.config.get('memory.gc.threshold', 50)  # Comment in Chinese removed
        
        # Comment in Chinese removedrts
        self.alerts_enabled = self.config.get('memory.alerts.enabled', True)
        self.alert_history = []
        self.alert_cooldown = 300  # Comment in Chinese removeds
        
        # Comment in Chinese removedding
        self.running = False
        self.thread = None
        
        # Comment in Chinese removedtrics
        self.metrics = {
            'current_usage': 0,
            'available_memory': 0,
            'memory_percent': 0,
            'peak_usage': 0,
            'memory_fragments': 0,
            'collections': 0
        }
        
        logger.info("MemoryManager initialized")
    
    def start(self):
        """Start memory management thread."""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._memory_monitor_loop, daemon=True)
            self.thread.start()
            logger.info("Memory management started")
    
    def stop(self):
        """Stop memory management thread."""
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join()
            logger.info("Memory management stopped")
    
    def _memory_monitor_loop(self):
        """Main memory monitoring loop."""
        while self.running:
            try:
                # Comment in Chinese removedtrics
                self._update_memory_metrics()
                
                # Comment in Chinese removedctions
                self._check_memory_usage()
                
                # Comment in Chinese removedd
                self._run_garbage_collection()
                
                # Comment in Chinese removedl
                time.sleep(self.optimization_interval)
                
            except Exception as e:
                logger.error(f"Error in memory monitor loop: {e}")
                time.sleep(5)  # Comment in Chinese removedrror
    
    def _update_memory_metrics(self):
        """Update memory usage metrics."""
        try:
            # Comment in Chinese removedo
            memory_info = self.process.memory_info()
            virtual_memory = psutil.virtual_memory()
            
            # Comment in Chinese removedtrics
            current_usage = memory_info.rss / 1024 / 1024  # Comment in Chinese removed
            available_memory = virtual_memory.available / 1024 / 1024  # Comment in Chinese removed
            memory_percent = virtual_memory.percent
            
            # Comment in Chinese removedtrics
            self.metrics['current_usage'] = current_usage
            self.metrics['available_memory'] = available_memory
            self.metrics['memory_percent'] = memory_percent
            self.metrics['peak_usage'] = max(self.metrics['peak_usage'], current_usage)
            
            # Comment in Chinese removed history
            self.memory_history.append({
                'timestamp': time.time(),
                'usage': current_usage,
                'available': available_memory,
                'percent': memory_percent
            })
            
            # Comment in Chinese removedngth
            if len(self.memory_history) > self.history_max_length:
                self.memory_history = self.memory_history[-self.history_max_length:]
                
        except Exception as e:
            logger.error(f"Error updating memory metrics: {e}")
    
    def _check_memory_usage(self):
        """Check memory usage and trigger appropriate actions."""
        memory_percent = self.metrics['memory_percent']
        
        # Comment in Chinese removedsholds
        if memory_percent >= self.memory_thresholds['emergency']:
            self._handle_emergency_memory()
        elif memory_percent >= self.memory_thresholds['critical']:
            self._handle_critical_memory()
        elif memory_percent >= self.memory_thresholds['warning']:
            self._handle_warning_memory()
    
    def _handle_warning_memory(self):
        """Handle warning memory usage."""
        self._trigger_alert('warning', f"Memory usage warning: {self.metrics['memory_percent']:.2f}%")
        self._optimize_memory()
    
    def _handle_critical_memory(self):
        """Handle critical memory usage."""
        self._trigger_alert('critical', f"Memory usage critical: {self.metrics['memory_percent']:.2f}%")
        self._optimize_memory(aggressive=True)
    
    def _handle_emergency_memory(self):
        """Handle emergency memory usage."""
        self._trigger_alert('emergency', f"Memory usage emergency: {self.metrics['memory_percent']:.2f}%")
        self._optimize_memory(aggressive=True, emergency=True)
    
    def _optimize_memory(self, aggressive: bool = False, emergency: bool = False):
        """Optimize memory usage.
        
        Args:
            aggressive: Whether to use aggressive optimization.
            emergency: Whether to use emergency optimization.
        """
        if not self.optimization_enabled:
            return
        
        logger.info(f"Optimizing memory usage (aggressive: {aggressive}, emergency: {emergency})")
        
        # Comment in Chinese removedction
        self._force_garbage_collection()
        
        # Comment in Chinese removedmory
        self._adjust_memory_limits(aggressive, emergency)
    
    def _adjust_memory_limits(self, aggressive: bool = False, emergency: bool = False):
        """Adjust memory limits based on available memory."""
        available_memory = self.metrics['available_memory']
        
        # Comment in Chinese removedw limits
        if emergency:
            # Comment in Chinese removedm limits
            new_cache_limit = max(100, int(self.memory_limits['cache'] * 0.2))
            new_working_memory_limit = max(10, int(self.memory_limits['working_memory'] * 0.2))
            new_batch_size = max(10, int(self.memory_limits['batch_size'] * 0.2))
        elif aggressive:
            # Comment in Chinese removed limits
            new_cache_limit = max(500, int(self.memory_limits['cache'] * 0.5))
            new_working_memory_limit = max(50, int(self.memory_limits['working_memory'] * 0.5))
            new_batch_size = max(50, int(self.memory_limits['batch_size'] * 0.5))
        else:
            # Comment in Chinese removedmory
            memory_factor = min(1.0, available_memory / 1024)  # Comment in Chinese removed
            new_cache_limit = int(self.memory_limits['cache'] * memory_factor)
            new_working_memory_limit = int(self.memory_limits['working_memory'] * memory_factor)
            new_batch_size = int(self.memory_limits['batch_size'] * memory_factor)
        
        # Comment in Chinese removed limits
        self.memory_limits['cache'] = max(100, new_cache_limit)
        self.memory_limits['working_memory'] = max(10, new_working_memory_limit)
        self.memory_limits['batch_size'] = max(10, new_batch_size)
        
        logger.info(f"Adjusted memory limits: cache={self.memory_limits['cache']}, working_memory={self.memory_limits['working_memory']}, batch_size={self.memory_limits['batch_size']}")
    
    def _run_garbage_collection(self):
        """Run garbage collection if needed."""
        if not self.gc_enabled:
            return
        
        memory_percent = self.metrics['memory_percent']
        if memory_percent >= self.gc_threshold:
            self._force_garbage_collection()
    
    def _force_garbage_collection(self):
        """Force garbage collection."""
        try:
            logger.info("Running garbage collection...")
            before = self.metrics['current_usage']
            gc.collect()
            self._update_memory_metrics()  # Comment in Chinese removed
            after = self.metrics['current_usage']
            freed = before - after
            self.metrics['collections'] += 1
            logger.info(f"Garbage collection completed. Freed {freed:.2f} MB")
        except Exception as e:
            logger.error(f"Error during garbage collection: {e}")
    
    def _trigger_alert(self, level: str, message: str):
        """Trigger a memory alert.
        
        Args:
            level: Alert level (warning, critical, emergency).
            message: Alert message.
        """
        if not self.alerts_enabled:
            return
        
        # Comment in Chinese removedck cooldown
        current_time = time.time()
        if self.alert_history:
            last_alert = self.alert_history[-1]
            if current_time - last_alert['timestamp'] < self.alert_cooldown:
                return
        
        # Comment in Chinese removedrt history
        alert = {
            'timestamp': current_time,
            'level': level,
            'message': message,
            'memory_percent': self.metrics['memory_percent']
        }
        self.alert_history.append(alert)
        
        # Comment in Chinese removeds
        if len(self.alert_history) > 10:
            self.alert_history = self.alert_history[-10:]
        
        # Comment in Chinese removedrt
        if level == 'warning':
            logger.warning(message)
        elif level == 'critical':
            logger.critical(message)
        elif level == 'emergency':
            logger.critical(f"[EMERGENCY] {message}")
    
    def get_memory_limits(self) -> Dict[str, int]:
        """Get current memory limits.
        
        Returns:
            Memory limits.
        """
        return self.memory_limits
    
    def get_memory_metrics(self) -> Dict[str, Any]:
        """Get current memory metrics.
        
        Returns:
            Memory metrics.
        """
        self._update_memory_metrics()
        return self.metrics
    
    def get_memory_history(self) -> List[Dict[str, Any]]:
        """Get memory usage history.
        
        Returns:
            Memory usage history.
        """
        return self.memory_history
    
    def get_alert_history(self) -> List[Dict[str, Any]]:
        """Get alert history.
        
        Returns:
            Alert history.
        """
        return self.alert_history
    
    def calculate_memory_fragmentation(self) -> float:
        """Calculate memory fragmentation.
        
        Returns:
            Fragmentation ratio (0-1).
        """
        try:
            # Comment in Chinese removedrns
            if not self.memory_history:
                return 0.0
            
            # Comment in Chinese removed
            usages = [entry['usage'] for entry in self.memory_history]
            mean_usage = sum(usages) / len(usages)
            variance = sum((u - mean_usage) ** 2 for u in usages) / len(usages)
            std_dev = variance ** 0.5
            
            # Comment in Chinese removed
            fragmentation = min(1.0, std_dev / (mean_usage + 1))
            self.metrics['memory_fragments'] = fragmentation
            
            return fragmentation
        except Exception as e:
            logger.error(f"Error calculating memory fragmentation: {e}")
            return 0.0
    
    def optimize_memory_usage(self, target_usage: float = 0.5):
        """Optimize memory usage to target level.
        
        Args:
            target_usage: Target memory usage ratio (0-1).
        """
        current_percent = self.metrics['memory_percent'] / 100
        
        if current_percent > target_usage:
            # Comment in Chinese removed
            reduction_factor = target_usage / current_percent
            
            # Comment in Chinese removedst limits
            self.memory_limits['cache'] = int(self.memory_limits['cache'] * reduction_factor)
            self.memory_limits['working_memory'] = int(self.memory_limits['working_memory'] * reduction_factor)
            self.memory_limits['batch_size'] = int(self.memory_limits['batch_size'] * reduction_factor)
            
            # Comment in Chinese removedms
            self.memory_limits['cache'] = max(100, self.memory_limits['cache'])
            self.memory_limits['working_memory'] = max(10, self.memory_limits['working_memory'])
            self.memory_limits['batch_size'] = max(10, self.memory_limits['batch_size'])
            
            # Comment in Chinese removedction
            self._force_garbage_collection()
            
            logger.info(f"Optimized memory usage to target {target_usage * 100}%")
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get memory usage summary.
        
        Returns:
            Memory usage summary.
        """
        self._update_memory_metrics()
        fragmentation = self.calculate_memory_fragmentation()
        
        return {
            'current_usage': self.metrics['current_usage'],
            'available_memory': self.metrics['available_memory'],
            'memory_percent': self.metrics['memory_percent'],
            'peak_usage': self.metrics['peak_usage'],
            'memory_fragmentation': fragmentation,
            'collections': self.metrics['collections'],
            'limits': self.memory_limits,
            'alerts': len(self.alert_history),
            'last_alert': self.alert_history[-1] if self.alert_history else None
        }


class SmartCache:
    """Memory-efficient cache with dynamic sizing."""
    
    def __init__(self, initial_size: int = 1000, ttl: int = 3600):
        """Initialize the smart cache.
        
        Args:
            initial_size: Initial cache size.
            ttl: Time-to-live in seconds.
        """
        self.cache = {}
        self.initial_size = initial_size
        self.current_size = initial_size
        self.ttl = ttl
        self.hit_count = 0
        self.miss_count = 0
        self.expired_count = 0
        
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache.
        
        Args:
            key: Cache key.
            
        Returns:
            Cached value or None if not found or expired.
        """
        if key not in self.cache:
            self.miss_count += 1
            return None
        
        cached_item = self.cache[key]
        value = cached_item['value']
        timestamp = cached_item['timestamp']
        
        # Comment in Chinese removedd
        if time.time() - timestamp > self.ttl:
            del self.cache[key]
            self.expired_count += 1
            self.miss_count += 1
            return None
        
        self.hit_count += 1
        return value
    
    def set(self, key: str, value: Any):
        """Set value in cache.
        
        Args:
            key: Cache key.
            value: Value to cache.
        """
        # Comment in Chinese removedll
        while len(self.cache) >= self.current_size:
            # Comment in Chinese removedy
            oldest_key = None
            oldest_time = float('inf')
            for k, item in self.cache.items():
                if item['timestamp'] < oldest_time:
                    oldest_time = item['timestamp']
                    oldest_key = k
            if oldest_key:
                del self.cache[oldest_key]
        
        # Comment in Chinese removed
        self.cache[key] = {
            'value': value,
            'timestamp': time.time()
        }
    
    def clear(self):
        """Clear all cache."""
        self.cache = {}
    
    def set_size(self, size: int):
        """Set cache size.
        
        Args:
            size: New cache size.
        """
        # Comment in Chinese removed
        self.current_size = max(1, size)
        
        # Comment in Chinese removedry
        while len(self.cache) > self.current_size:
            # Comment in Chinese removedy
            oldest_key = None
            oldest_time = float('inf')
            for key, item in self.cache.items():
                if item['timestamp'] < oldest_time:
                    oldest_time = item['timestamp']
                    oldest_key = key
            if oldest_key:
                del self.cache[oldest_key]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Cache statistics.
        """
        total = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total * 100) if total > 0 else 0
        
        return {
            'size': len(self.cache),
            'max_size': self.current_size,
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'hit_rate': hit_rate,
            'expired_count': self.expired_count
        }
    
    def get_memory_usage(self) -> float:
        """Estimate memory usage of the cache.
        
        Returns:
            Estimated memory usage in MB.
        """
        # Comment in Chinese removedms
        # Comment in Chinese removed
        return len(self.cache) * 0.01  # Comment in Chinese removedm
