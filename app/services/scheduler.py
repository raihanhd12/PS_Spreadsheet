"""
Scheduler service for auto-sync functionality
"""
import schedule
import time
import threading
from datetime import datetime

from app.exceptions import SchedulerError, GSheetConnectionError, DBConnectionError
from app.utils.logging import logger
from app.services.google_sheets import connect_to_gsheets
from app.services.database import sync_to_db
from app.config import settings

# Global scheduler state
scheduler_running = False
scheduler_thread = None
last_sync_time = None
sync_status = {"status": "idle", "last_run": None, "error": None}


def start_auto_sync(spreadsheet_id, credentials_dict, db_config, interval_minutes=None, sheet_name=None):
    """
    Start auto-sync process with a given interval.

    Args:
        spreadsheet_id (str): The ID of the Google Spreadsheet
        credentials_dict (dict): Dictionary containing Google Service Account credentials
        db_config (dict): Dictionary containing database configuration
        interval_minutes (int, optional): Sync interval in minutes. Defaults to settings.DEFAULT_SYNC_INTERVAL.
        sheet_name (str, optional): The name of the sheet to read. Defaults to settings.DEFAULT_SHEET_NAME.

    Returns:
        dict: Status message

    Raises:
        SchedulerError: If scheduler operations fail
    """
    global scheduler_running, scheduler_thread, sync_status

    if interval_minutes is None:
        interval_minutes = settings.DEFAULT_SYNC_INTERVAL

    if sheet_name is None:
        sheet_name = settings.DEFAULT_SHEET_NAME

    if scheduler_running:
        logger.warning("Auto-sync already running", interval_minutes=interval_minutes)
        raise SchedulerError("Auto-sync is already running")

    try:
        def auto_sync_job():
            global last_sync_time, sync_status

            logger.info("Auto-sync job triggered")
            sync_status = {"status": "running", "last_run": datetime.now().isoformat(), "error": None}

            try:
                df = connect_to_gsheets(spreadsheet_id, credentials_dict, sheet_name)
                sync_result = sync_to_db(df, db_config)
                last_sync_time = datetime.now().isoformat()
                sync_status = {
                    "status": "completed",
                    "last_run": last_sync_time,
                    "rows_synced": len(df),
                    "error": None
                }
                logger.info("Auto-sync completed successfully", rows_synced=len(df))
            except (GSheetConnectionError, DBConnectionError) as e:
                error_msg = f"Error in auto-sync job: {str(e)}"
                sync_status = {
                    "status": "failed",
                    "last_run": datetime.now().isoformat(),
                    "error": str(e)
                }
                logger.error(error_msg, exc_info=True)
            except Exception as e:
                error_msg = f"Unexpected error in auto-sync job: {str(e)}"
                sync_status = {
                    "status": "failed",
                    "last_run": datetime.now().isoformat(),
                    "error": str(e)
                }
                logger.error(error_msg, exc_info=True)

        # Schedule the job
        schedule.clear()  # Clear any existing schedules
        schedule.every(interval_minutes).minutes.do(auto_sync_job)
        scheduler_running = True

        logger.info("Auto-sync scheduled",
                    interval_minutes=interval_minutes,
                    spreadsheet_id=spreadsheet_id,
                    sheet_name=sheet_name)

        # Start the scheduler in a background thread
        def run_scheduler():
            global scheduler_running
            logger.info("Scheduler thread started")
            while scheduler_running:
                schedule.run_pending()
                time.sleep(1)
            logger.info("Scheduler thread stopped")

        # Stop existing thread if it exists
        if scheduler_thread and scheduler_thread.is_alive():
            scheduler_running = False
            scheduler_thread.join(timeout=5)

        # Create and start new thread
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()

        # Run the job immediately for the first time
        auto_sync_job()

        return {
            "status": "success",
            "message": f"Auto-sync started every {interval_minutes} minutes",
            "first_sync": sync_status
        }

    except Exception as e:
        error_msg = f"Error starting auto-sync: {str(e)}"
        logger.error(error_msg,
                     spreadsheet_id=spreadsheet_id,
                     interval_minutes=interval_minutes,
                     exc_info=True)
        raise SchedulerError(error_msg)


def stop_auto_sync():
    """
    Stop the auto-sync process.

    Returns:
        dict: Status message
    """
    global scheduler_running, scheduler_thread

    if not scheduler_running:
        return {"status": "warning", "message": "Auto-sync is not running"}

    try:
        schedule.clear()
        scheduler_running = False

        # Wait for thread to terminate
        if scheduler_thread and scheduler_thread.is_alive():
            scheduler_thread.join(timeout=5)

        logger.info("Auto-sync stopped")
        return {"status": "success", "message": "Auto-sync stopped"}
    except Exception as e:
        error_msg = f"Error stopping auto-sync: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {"status": "error", "message": error_msg}


def get_sync_status():
    """
    Get the current status of the auto-sync process.

    Returns:
        dict: Current sync status
    """
    global sync_status
    return {
        "scheduler": "running" if scheduler_running else "idle",
        "sync": sync_status
    }
