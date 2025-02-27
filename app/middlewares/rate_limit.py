"""
Rate limiting middleware to prevent API abuse
"""
from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.config import settings

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


def setup_rate_limiter(app):
    """
    Configure rate limiting for the application

    Args:
        app: FastAPI application
    """
    from slowapi import _rate_limit_exceeded_handler
    from slowapi.errors import RateLimitExceeded

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
