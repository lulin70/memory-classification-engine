"""Memory Classification Engine SDK exceptions."""


class MemoryClassificationError(Exception):
    """Base exception for Memory Classification Engine SDK."""
    pass


class APIError(MemoryClassificationError):
    """API error exception."""
    pass


class ConnectionError(MemoryClassificationError):
    """Connection error exception."""
    pass


class TimeoutError(MemoryClassificationError):
    """Timeout error exception."""
    pass


class ValidationError(MemoryClassificationError):
    """Validation error exception."""
    pass
