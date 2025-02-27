"""
Configuration settings for the application
"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings"""
    # App info
    APP_NAME: str = "Google Sheets to DB Sync API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = """
    This API allows you to synchronize data between Google Sheets and databases.
    
    ## Features
    
    * Connect to Google Sheets and retrieve data
    * Sync data to a database
    * Automatically sync data at specified intervals
    
    ## Security
    
    All API endpoints require an API key provided in the X-API-Key header.
    """

    # Environment
    DEBUG: bool = False

    # Security
    API_KEY: str = "your-secure-api-key"  # Default for development

    # CORS
    ALLOWED_ORIGINS: str = "*"

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 10

    # Database
    DATABASE_URL: Optional[str] = None

    # Google Sheets
    DEFAULT_SHEET_NAME: str = "Sheet1"

    # Scheduler
    DEFAULT_SYNC_INTERVAL: int = 5
    MAX_SYNC_INTERVAL: int = 1440  # 24 hours in minutes

    # Konfigurasi untuk pydantic-settings
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    def get_allowed_origins(self) -> List[str]:
        """Parse ALLOWED_ORIGINS string to list"""
        if self.ALLOWED_ORIGINS == "*":
            return ["*"]
        return self.ALLOWED_ORIGINS.split(",")


# Create a global settings object
settings = Settings()
