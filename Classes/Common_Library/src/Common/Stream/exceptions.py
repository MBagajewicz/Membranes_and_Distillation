"""
Custom exceptions for the streams package.

Keeping them in a dedicated module makes it trivial to catch
stream-specific errors upstream without importing the entire
simulation layer.
"""


class StreamError(Exception):
    """Base exception for all stream-related errors."""
    pass


class CompositionError(StreamError):
    """Raised when the composition is invalid or contains unknown fluids."""
    pass


class FlowSpecificationError(StreamError):
    """
    Raised when flow is specified incorrectly (both, none, or inconsistent).
    """
    pass


class BackendError(StreamError):
    """Raised when CoolProp cannot instantiate the requested backend."""
    pass