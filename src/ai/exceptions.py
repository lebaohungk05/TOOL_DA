class AIServiceError(Exception):
    """Base exception for AI generation errors."""
    pass

class AIServiceConnectionError(AIServiceError):
    """Raised when the AI provider cannot be reached."""
    pass
