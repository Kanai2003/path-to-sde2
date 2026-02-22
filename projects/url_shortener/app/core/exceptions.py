"""Custom exceptions for the URL shortener application."""


class URLShortenerException(Exception):
    """Base exception for URL shortener."""
    pass


class URLAlreadyExistsError(URLShortenerException):
    """Raised when attempting to create a URL that already exists."""
    pass


class URLNotFoundError(URLShortenerException):
    """Raised when a URL is not found."""
    pass


class ShortCodeGenerationError(URLShortenerException):
    """Raised when unable to generate a unique short code."""
    pass
