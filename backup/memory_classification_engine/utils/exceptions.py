class MemoryEngineError(Exception):
    """Base exception class for Memory Classification Engine"""
    pass

class StorageError(MemoryEngineError):
    """Base exception for storage-related errors"""
    pass

class MemoryNotFoundError(StorageError):
    """Raised when a memory is not found"""
    pass

class MemoryAlreadyExistsError(StorageError):
    """Raised when trying to create a memory that already exists"""
    pass

class DatabaseError(StorageError):
    """Raised when there's a database-related error"""
    pass

class FTS5Error(StorageError):
    """Raised when there's an FTS5-related error"""
    pass

class CacheError(MemoryEngineError):
    """Raised when there's a cache-related error"""
    pass

class ConfigurationError(MemoryEngineError):
    """Raised when there's a configuration error"""
    pass

class PluginError(MemoryEngineError):
    """Raised when there's a plugin-related error"""
    pass
