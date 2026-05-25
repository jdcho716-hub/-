class QuantKorError(Exception):
    """Base exception for quant_kor project."""


class ConfigurationError(QuantKorError):
    """Raised when config/env loading fails."""


class DatabaseError(QuantKorError):
    """Raised when SQLite operations fail."""
