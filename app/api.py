"""
FastAPI application and endpoints
"""
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from datetime import datetime

from app.config import settings
from app.utils.logging import logger
from app.middlewares.auth import verify_api_key
from app.middlewares.rate_limit import limiter, setup_rate_limiter
from app.models import (
    ConnectRequest, SyncRequest, AutoSyncRequest,
    ConnectResponse, SyncResponse, AutoSyncResponse,
    StatusResponse, HealthResponse, ErrorResponse
)
from app.exceptions import GSheetConnectionError, DBConnectionError, SchedulerError
from app.services.google_sheets import connect_to_gsheets
from app.services.database import sync_to_db
from app.services.scheduler import (
    start_auto_sync, stop_auto_sync, get_sync_status,
    last_sync_time, scheduler_running
)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DEBUG else None,  # Only show docs in debug mode
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json",
    openapi_tags=[
        {
            "name": "Root",
            "description": "Root endpoint to check if the API is running"
        },
        {
            "name": "Health",
            "description": "Health check endpoints to monitor API status"
        },
        {
            "name": "Connect to Google Sheets",
            "description": "Connect to Google Sheets and return its data as a DataFrame"
        },
        {
            "name": "Sync to Database",
            "description": "Synchronize data from Google Sheets to a database"
        },
        {
            "name": "Auto-sync",
            "description": "Automatically sync data at specified intervals"
        }
    ]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up rate limiter
setup_rate_limiter(app)

# Set up Prometheus metrics - penting: ini harus sebelum event handlers
# Dan akan dikomentari jika terjadi masalah
try:
    Instrumentator().instrument(app).expose(app)
except Exception as e:
    logger.error(f"Failed to initialize Prometheus Instrumentator: {e}")


# Event handlers
@app.on_event("startup")
async def startup_event():
    logger.info("API started", version=settings.APP_VERSION)


@app.on_event("shutdown")
async def shutdown_event():
    # Stop scheduler if running
    if scheduler_running:
        stop_auto_sync()
    logger.info("API shutdown")


# API Endpoints
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint to check if the API is running.

    Returns:
        dict: A simple message with API info
    """
    return {
        "message": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Check if the API is healthy.

    Returns:
        HealthResponse: Health status information
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        scheduler="running" if scheduler_running else "idle",
        last_sync=last_sync_time
    )


@app.get("/sync-status", tags=["Auto-sync"], dependencies=[Depends(verify_api_key)])
async def sync_status_endpoint():
    """
    Get the current status of the auto-sync process.

    Returns:
        StatusResponse: Current sync status
    """
    status = get_sync_status()
    return StatusResponse(**status)


@app.post("/connect-gsheets/", tags=["Connect to Google Sheets"], dependencies=[Depends(verify_api_key)])
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def connect_gsheets_endpoint(
        request: Request,
        connect_request: ConnectRequest
):
    """
    Connect to a Google Spreadsheet and return its data.

    Args:
        connect_request (ConnectRequest): Connection parameters

    Returns:
        ConnectResponse: DataFrame data in JSON format

    Raises:
        HTTPException: If connection fails
    """
    try:
        df = connect_to_gsheets(
            connect_request.spreadsheet_id,
            connect_request.credentials.dict(),
            connect_request.sheet_name
        )

        return ConnectResponse(
            status="success",
            rows=len(df),
            columns=list(df.columns),
            data=df.to_dict(orient="records")
        )

    except GSheetConnectionError as e:
        logger.error("Google Sheets connection error",
                     error=str(e),
                     spreadsheet_id=connect_request.spreadsheet_id)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Google Sheets connection error: {str(e)}"
        )

    except Exception as e:
        logger.error("Unexpected error in connect-gsheets",
                     error=str(e),
                     exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@app.post("/sync-db/", tags=["Sync to Database"], dependencies=[Depends(verify_api_key)])
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def sync_db_endpoint(
        request: Request,
        sync_request: SyncRequest
):
    """
    Sync data from Google Spreadsheet to database.

    Args:
        sync_request (SyncRequest): Sync parameters

    Returns:
        SyncResponse: Sync result

    Raises:
        HTTPException: If sync fails
    """
    try:
        df = connect_to_gsheets(
            sync_request.spreadsheet_id,
            sync_request.credentials.dict(),
            sync_request.sheet_name
        )

        sync_result = sync_to_db(df, sync_request.db_config.dict())

        return SyncResponse(
            status="success",
            message=f"Data synced to {sync_request.db_config.database}.{sync_request.db_config.table_name}",
            rows_synced=len(df)
        )

    except GSheetConnectionError as e:
        logger.error("Google Sheets connection error",
                     error=str(e),
                     spreadsheet_id=sync_request.spreadsheet_id)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Google Sheets connection error: {str(e)}"
        )

    except DBConnectionError as e:
        logger.error("Database connection error",
                     error=str(e),
                     database=sync_request.db_config.database)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Database connection error: {str(e)}"
        )

    except Exception as e:
        logger.error("Unexpected error in sync-db",
                     error=str(e),
                     exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@app.post("/start-auto-sync/", tags=["Auto-sync"], dependencies=[Depends(verify_api_key)])
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def start_auto_sync_endpoint(
        request: Request,
        auto_sync_request: AutoSyncRequest
):
    """
    Start auto-sync process with a given interval.

    Args:
        auto_sync_request (AutoSyncRequest): Auto-sync parameters

    Returns:
        AutoSyncResponse: Auto-sync result

    Raises:
        HTTPException: If auto-sync fails to start
    """
    try:
        result = start_auto_sync(
            auto_sync_request.spreadsheet_id,
            auto_sync_request.credentials.dict(),
            auto_sync_request.db_config.dict(),
            auto_sync_request.interval_minutes,
            auto_sync_request.sheet_name
        )

        return AutoSyncResponse(**result)

    except SchedulerError as e:
        logger.error("Scheduler error",
                     error=str(e))
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Scheduler error: {str(e)}"
        )

    except Exception as e:
        logger.error("Unexpected error in start-auto-sync",
                     error=str(e),
                     exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@app.post("/stop-auto-sync/", tags=["Auto-sync"], dependencies=[Depends(verify_api_key)])
async def stop_auto_sync_endpoint():
    """
    Stop the auto-sync process.

    Returns:
        dict: Status message
    """
    return stop_auto_sync()
