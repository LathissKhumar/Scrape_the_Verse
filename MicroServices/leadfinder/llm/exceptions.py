class LLMError(Exception):
    """Base exception for all LLM errors."""
    pass


class LLMConnectionError(LLMError):
    """Raised when the LLM provider service cannot be reached."""
    pass


class LLMModelNotFoundError(LLMError):
    """Raised when the requested LLM model is not available on the provider."""
    pass


class LLMTimeoutError(LLMError):
    """Raised when an LLM request exceeds the configured timeout."""
    pass


class LLMInvocationError(LLMError):
    """Raised when the LLM provider returns an error response during generation."""
    pass
