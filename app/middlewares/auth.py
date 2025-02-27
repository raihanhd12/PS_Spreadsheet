"""
Authentication middleware for API security
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from app.config import settings
from app.utils.logging import logger

# API key security
api_key_header = APIKeyHeader(name="X-API-Key")


def verify_api_key(api_key: str = Depends(api_key_header)):
    """
    Verify that the provided API key is valid

    Args:
        api_key (str): API key from request header

    Returns:
        str: Validated API key

    Raises:
        HTTPException: If API key is invalid
    """
    if api_key != settings.API_KEY:
        logger.error("Unauthorized access attempt", api_key_provided=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    return api_key
