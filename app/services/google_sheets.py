"""
Google Sheets service for connecting and retrieving data
"""
import pandas as pd
import tempfile
import json
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

from app.exceptions import GSheetConnectionError
from app.utils.logging import logger
from app.config import settings


def connect_to_gsheets(spreadsheet_id, credentials_dict, sheet_name=None):
    """
    Connect to a Google Spreadsheet and return its data as a DataFrame.

    Args:
        spreadsheet_id (str): The ID of the Google Spreadsheet (from the URL)
        credentials_dict (dict): Dictionary containing Google Service Account credentials
        sheet_name (str, optional): The name of the sheet to read. Defaults to settings.DEFAULT_SHEET_NAME.

    Returns:
        pandas.DataFrame: DataFrame containing the sheet data

    Raises:
        GSheetConnectionError: If connection or data retrieval fails
    """
    if sheet_name is None:
        sheet_name = settings.DEFAULT_SHEET_NAME

    logger.info("Starting connection to Google Sheets",
                spreadsheet_id=spreadsheet_id,
                sheet=sheet_name)

    credentials_path = None
    try:
        logger.debug("Writing credentials to temporary file")
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as temp:
            temp.write(json.dumps(credentials_dict).encode())
            credentials_path = temp.name

        logger.debug("Authenticating with Google Sheets")
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        sheets_service = build('sheets', 'v4', credentials=credentials)
        logger.info("Authentication successful")

        logger.debug("Reading data from sheet",
                     spreadsheet_id=spreadsheet_id,
                     sheet=sheet_name)
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=sheet_name
        ).execute()

        values = result.get('values', [])
        if not values:
            logger.error("No data found in sheet",
                         spreadsheet_id=spreadsheet_id,
                         sheet=sheet_name)
            raise GSheetConnectionError("No data found in the specified sheet")

        headers = values[0]
        data = values[1:]
        google_spreadsheet_df = pd.DataFrame(data, columns=headers)
        logger.info("Successfully read data from sheet",
                    rows=len(google_spreadsheet_df),
                    columns=list(google_spreadsheet_df.columns))

        # Cleanup temp file
        if credentials_path:
            os.unlink(credentials_path)
            logger.debug("Temporary credentials file cleaned up")

        return google_spreadsheet_df

    except Exception as e:
        error_msg = f"Error connecting to Google Sheets: {str(e)}"
        logger.error(error_msg,
                     spreadsheet_id=spreadsheet_id,
                     sheet=sheet_name,
                     error=str(e),
                     exc_info=True)

        # Cleanup temp file if exists
        if credentials_path and os.path.exists(credentials_path):
            os.unlink(credentials_path)
            logger.debug("Temporary credentials file cleaned up after error")

        raise GSheetConnectionError(error_msg)
