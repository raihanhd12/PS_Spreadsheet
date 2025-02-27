"""
Custom exceptions for the application
"""


class GSheetConnectionError(Exception):
    """Raised when connection to Google Sheets fails"""
    pass


class DBConnectionError(Exception):
    """Raised when database connection fails"""
    pass


class SchedulerError(Exception):
    """Raised when scheduler operations fail"""
    pass


class ValidationError(Exception):
    """Raised when input validation fails"""
    pass


class AuthenticationError(Exception):
    """Raised when authentication fails"""
    pass
