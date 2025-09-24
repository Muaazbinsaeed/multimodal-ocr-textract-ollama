from fastapi import HTTPException
from typing import Optional


class OllamaError(Exception):
    """Base exception for Ollama-related errors"""
    def __init__(self, message: str, status_code: int = 503):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class OllamaConnectionError(OllamaError):
    """Raised when cannot connect to Ollama"""
    def __init__(self, message: str = "Cannot connect to Ollama. Make sure Ollama is running at the configured host."):
        super().__init__(message, 503)


class OllamaTimeoutError(OllamaError):
    """Raised when Ollama request times out"""
    def __init__(self, message: str = "Request to Ollama timed out. The image processing is taking too long."):
        super().__init__(message, 504)


class OllamaModelError(OllamaError):
    """Raised when model is not available"""
    def __init__(self, model: str, message: Optional[str] = None):
        if message is None:
            message = f"Model '{model}' not found. Try running: ollama pull {model}"
        super().__init__(message, 503)


class ImageValidationError(HTTPException):
    """Raised when image validation fails"""
    def __init__(self, message: str):
        super().__init__(status_code=400, detail=message)


def create_error_response(error: Exception) -> dict:
    """Create standardized error response"""
    if isinstance(error, OllamaError):
        return {
            "error": type(error).__name__,
            "message": error.message,
            "code": error.status_code
        }
    elif isinstance(error, HTTPException):
        return {
            "error": "ValidationError",
            "message": error.detail,
            "code": error.status_code
        }
    else:
        return {
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "code": 500
        }