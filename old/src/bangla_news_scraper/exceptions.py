"""
Custom exceptions for the Bangla News Scraper
"""


class ScraperException(Exception):
    """Base exception for all scraper-related errors"""
    pass


class NetworkException(ScraperException):
    """Exception raised for network-related errors"""
    def __init__(self, message: str, url: str = None, status_code: int = None):
        self.url = url
        self.status_code = status_code
        super().__init__(message)


class ParseException(ScraperException):
    """Exception raised when content parsing fails"""
    def __init__(self, message: str, url: str = None, element: str = None):
        self.url = url
        self.element = element
        super().__init__(message)


class ValidationException(ScraperException):
    """Exception raised when data validation fails"""
    def __init__(self, message: str, field: str = None, value: str = None):
        self.field = field
        self.value = value
        super().__init__(message)


class ConfigurationException(ScraperException):
    """Exception raised for configuration-related errors"""
    pass


class CacheException(ScraperException):
    """Exception raised for cache-related operations"""
    pass


class RateLimitException(ScraperException):
    """Exception raised when rate limiting is triggered"""
    def __init__(self, message: str, retry_after: int = None):
        self.retry_after = retry_after
        super().__init__(message)