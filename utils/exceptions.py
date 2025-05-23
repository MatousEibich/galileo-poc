"""Custom exceptions for the municipal data chatbot."""

from typing import Optional


class ChatbotError(Exception):
    """Base exception for all chatbot-related errors."""
    
    def __init__(self, message: str, details: Optional[str] = None):
        self.message = message
        self.details = details
        super().__init__(self.message)


class ConfigurationError(ChatbotError):
    """Raised when there are configuration-related issues."""
    pass


class DataLoadError(ChatbotError):
    """Raised when data files cannot be loaded or processed."""
    pass


class AgentError(ChatbotError):
    """Raised when the LangChain agent encounters errors."""
    pass


class ValidationError(ChatbotError):
    """Raised when input validation fails."""
    pass 