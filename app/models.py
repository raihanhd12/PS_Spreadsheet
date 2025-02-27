"""
Data models for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class CredentialsModel(BaseModel):
    """Google Service Account credentials model"""
    type: str
    project_id: str
    private_key_id: str
    private_key: str
    client_email: str
    client_id: str
    auth_uri: str
    token_uri: str
    auth_provider_x509_cert_url: str
    client_x509_cert_url: str

    class Config:
        schema_extra = {
            "example": {
                "type": "service_account",
                "project_id": "your-project-id",
                "private_key_id": "your-private-key-id",
                "private_key": "-----BEGIN PRIVATE KEY-----\nYourPrivateKey\n-----END PRIVATE KEY-----\n",
                "client_email": "your-service-account@your-project-id.iam.gserviceaccount.com",
                "client_id": "your-client-id",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project-id.iam.gserviceaccount.com"
            }
        }


class DBConfigModel(BaseModel):
    """Database configuration model"""
    db_type: str
    host: str
    port: int
    user: str
    password: str
    database: str
    table_name: str

    class Config:
        schema_extra = {
            "example": {
                "db_type": "postgresql",
                "host": "localhost",
                "port": 5432,
                "user": "postgres",
                "password": "your_password",
                "database": "your_database",
                "table_name": "your_table"
            }
        }


class ConnectRequest(BaseModel):
    """Request model for connecting to Google Sheets"""
    spreadsheet_id: str
    credentials: CredentialsModel
    sheet_name: Optional[str] = Field(None, description="Name of the sheet to read")


class SyncRequest(BaseModel):
    """Request model for syncing data to database"""
    spreadsheet_id: str
    credentials: CredentialsModel
    db_config: DBConfigModel
    sheet_name: Optional[str] = Field(None, description="Name of the sheet to read")


class AutoSyncRequest(BaseModel):
    """Request model for auto-sync configuration"""
    spreadsheet_id: str
    credentials: CredentialsModel
    db_config: DBConfigModel
    interval_minutes: int = Field(5, ge=1, le=1440, description="Sync interval in minutes (1-1440)")
    sheet_name: Optional[str] = Field(None, description="Name of the sheet to read")


class ConnectResponse(BaseModel):
    """Response model for Google Sheets connection"""
    status: str
    rows: int
    columns: List[str]
    data: List[Dict[str, Any]]


class SyncResponse(BaseModel):
    """Response model for database sync"""
    status: str
    message: str
    rows_synced: int


class AutoSyncResponse(BaseModel):
    """Response model for auto-sync operations"""
    status: str
    message: str
    first_sync: Optional[Dict[str, Any]] = None


class StatusResponse(BaseModel):
    """Response model for sync status"""
    scheduler: str
    sync: Dict[str, Any]


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    timestamp: str
    scheduler: str
    last_sync: Optional[str] = None


class ErrorResponse(BaseModel):
    """Response model for errors"""
    status: str = "error"
    message: str
    detail: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
