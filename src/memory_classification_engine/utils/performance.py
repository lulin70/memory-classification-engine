"""Performance monitoring utilities for CarryMem.

Provides decorators and utilities to track operation performance,
identify bottlenecks, and log timing information.

v0.4.1: Initial implementation
"""

import functools
import time
from typing import Any, Callable, Optional

from .logger import logger


def track_performance(operation_name: str, log_level: str = "info"):
    """Decorator to track and log performance of a function.
    
    Args:
        operation_name: Name of the operation for logging
        log_level: Log level to use ('debug', 'info', 'warning')
        
    Example:
        @track_performance("classify_message")
        def classify_message(self, message):
            # ... implementation
            pass
            
        # Output: classify_message completed in 0.123s
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            error_occurred = False
            result = None
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                error_occurred = True
                duration = time.time() - start_time
                logger.error(
                    f"{operation_name} failed after {duration:.3f}s: {e}",
                    exc_info=True
                )
                raise
            finally:
                if not error_occurred:
                    duration = time.time() - start_time
                    log_message = f"{operation_name} completed in {duration:.3f}s"
                    
                    if log_level == "debug":
                        logger.debug(log_message)
                    elif log_level == "info":
                        logger.info(log_message)
                    elif log_level == "warning":
                        logger.warning(log_message)
                    
        return wrapper
    return decorator


def track_performance_async(operation_name: str, log_level: str = "info"):
    """Decorator to track and log performance of an async function.
    
    Args:
        operation_name: Name of the operation for logging
        log_level: Log level to use ('debug', 'info', 'warning')
        
    Example:
        @track_performance_async("async_operation")
        async def async_operation(self):
            # ... implementation
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            error_occurred = False
            result = None
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                error_occurred = True
                duration = time.time() - start_time
                logger.error(
                    f"{operation_name} failed after {duration:.3f}s: {e}",
                    exc_info=True
                )
                raise
            finally:
                if not error_occurred:
                    duration = time.time() - start_time
                    log_message = f"{operation_name} completed in {duration:.3f}s"
                    
                    if log_level == "debug":
                        logger.debug(log_message)
                    elif log_level == "info":
                        logger.info(log_message)
                    elif log_level == "warning":
                        logger.warning(log_message)
                    
        return wrapper
    return decorator


class PerformanceTimer:
    """Context manager for timing code blocks.
    
    Example:
        with PerformanceTimer("database_query") as timer:
            # ... perform operation
            pass
        print(f"Operation took {timer.duration:.3f}s")
    """
    
    def __init__(self, operation_name: str, log: bool = True, log_level: str = "info"):
        """Initialize the timer.
        
        Args:
            operation_name: Name of the operation
            log: Whether to log the duration automatically
            log_level: Log level to use if logging
        """
        self.operation_name = operation_name
        self.log = log
        self.log_level = log_level
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.duration: Optional[float] = None
        
    def __enter__(self):
        """Start the timer."""
        self.start_time = time.time()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop the timer and optionally log."""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        
        if self.log:
            if exc_type is not None:
                logger.error(
                    f"{self.operation_name} failed after {self.duration:.3f}s: {exc_val}"
                )
            else:
                log_message = f"{self.operation_name} completed in {self.duration:.3f}s"
                
                if self.log_level == "debug":
                    logger.debug(log_message)
                elif self.log_level == "info":
                    logger.info(log_message)
                elif self.log_level == "warning":
                    logger.warning(log_message)
        
        return False  # Don't suppress exceptions


class PerformanceStats:
    """Collect and aggregate performance statistics.
    
    Example:
        stats = PerformanceStats()
        
        for i in range(100):
            with stats.measure("operation"):
                # ... perform operation
                pass
        
        print(stats.get_summary("operation"))
        # Output: {'count': 100, 'total': 12.5, 'avg': 0.125, 'min': 0.1, 'max': 0.2}
    """
    
    def __init__(self):
        """Initialize the stats collector."""
        self._stats = {}
        
    def measure(self, operation_name: str):
        """Context manager to measure an operation.
        
        Args:
            operation_name: Name of the operation
            
        Returns:
            Context manager that records timing
        """
        return _PerformanceMeasurement(self, operation_name)
        
    def record(self, operation_name: str, duration: float):
        """Record a duration for an operation.
        
        Args:
            operation_name: Name of the operation
            duration: Duration in seconds
        """
        if operation_name not in self._stats:
            self._stats[operation_name] = {
                'count': 0,
                'total': 0.0,
                'min': float('inf'),
                'max': 0.0,
                'durations': []
            }
        
        stats = self._stats[operation_name]
        stats['count'] += 1
        stats['total'] += duration
        stats['min'] = min(stats['min'], duration)
        stats['max'] = max(stats['max'], duration)
        stats['durations'].append(duration)
        
    def get_summary(self, operation_name: str) -> dict:
        """Get summary statistics for an operation.
        
        Args:
            operation_name: Name of the operation
            
        Returns:
            Dictionary with count, total, avg, min, max
        """
        if operation_name not in self._stats:
            return {
                'count': 0,
                'total': 0.0,
                'avg': 0.0,
                'min': 0.0,
                'max': 0.0
            }
        
        stats = self._stats[operation_name]
        return {
            'count': stats['count'],
            'total': round(stats['total'], 3),
            'avg': round(stats['total'] / stats['count'], 3),
            'min': round(stats['min'], 3),
            'max': round(stats['max'], 3)
        }
        
    def get_all_summaries(self) -> dict:
        """Get summaries for all operations.
        
        Returns:
            Dictionary mapping operation names to their summaries
        """
        return {
            name: self.get_summary(name)
            for name in self._stats.keys()
        }
        
    def reset(self, operation_name: Optional[str] = None):
        """Reset statistics.
        
        Args:
            operation_name: If provided, reset only this operation.
                          If None, reset all operations.
        """
        if operation_name:
            if operation_name in self._stats:
                del self._stats[operation_name]
        else:
            self._stats.clear()


class _PerformanceMeasurement:
    """Internal context manager for PerformanceStats."""
    
    def __init__(self, stats: PerformanceStats, operation_name: str):
        self.stats = stats
        self.operation_name = operation_name
        self.start_time: Optional[float] = None
        
    def __enter__(self):
        self.start_time = time.time()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        self.stats.record(self.operation_name, duration)
        return False


# Global performance stats instance
_global_stats = PerformanceStats()


def get_global_stats() -> PerformanceStats:
    """Get the global performance stats instance.
    
    Returns:
        The global PerformanceStats instance
    """
    return _global_stats


def reset_global_stats():
    """Reset all global performance statistics."""
    _global_stats.reset()
