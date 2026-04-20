import os
import json
import logging
from datetime import datetime
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_INSTALLED = True
except ImportError:
    GSPREAD_INSTALLED = False

logger = logging.getLogger(__name__)

class GoogleSheetsService:
    def __init__(self):
        self.scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        self.credentials_file = os.getenv('GOOGLE_SHEETS_CREDENTIALS_FILE', 'credentials.json')
        self.sheet_id = os.getenv('GOOGLE_SHEET_ID')
        self.worksheet_name = os.getenv('GOOGLE_SHEET_WORKSHEET_NAME', 'Sheet1')
        self.client = None

    def _authenticate(self):
        if not GSPREAD_INSTALLED:
            logger.warning("gspread or google-auth not installed. Skipping Google Sheets integration.")
            return False

        if not self.sheet_id:
            logger.warning("GOOGLE_SHEET_ID is not set in environment. Skipping Google Sheets integration.")
            return False

        if not os.path.exists(self.credentials_file):
            logger.warning(f"Google Sheets credentials file '{self.credentials_file}' not found. Skipping Google Sheets integration.")
            return False

        try:
            credentials = Credentials.from_service_account_file(self.credentials_file, scopes=self.scopes)
            self.client = gspread.authorize(credentials)
            return True
        except Exception as e:
            logger.error(f"Failed to authenticate with Google Sheets: {str(e)}")
            return False

    def append_subscriber(self, subscriber_data):
        """
        Expects a dictionary containing subscriber info matching the sheet columns.
        Silently fails and logs error to preserve UX.
        """
        if not self._authenticate():
            return

        try:
            spreadsheet = self.client.open_by_key(self.sheet_id)
            worksheet = spreadsheet.worksheet(self.worksheet_name)
            
            # Formatting timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Expected order of columns matching the MD requirement:
            # - timestamp
            # - email
            # - first_name
            # - source
            # - utm_source
            # - utm_medium
            # - utm_campaign
            # - utm_content
            # - utm_term
            # - landing_page
            # - consent_status
            
            row = [
                timestamp,
                subscriber_data.get('email', ''),
                subscriber_data.get('first_name', ''),
                subscriber_data.get('source', ''),
                subscriber_data.get('utm_source', ''),
                subscriber_data.get('utm_medium', ''),
                subscriber_data.get('utm_campaign', ''),
                subscriber_data.get('utm_content', ''),
                subscriber_data.get('utm_term', ''),
                subscriber_data.get('landing_page', ''),
                str(subscriber_data.get('consent_status', True))
            ]
            
            worksheet.append_row(row)
            logger.info(f"Successfully appended {subscriber_data.get('email')} to Google Sheets.")
            
        except Exception as e:
            logger.error(f"Failed to append row to Google Sheets: {str(e)}")
            # Intentionally pass so the user doesn't see an error if Sheets fails
            pass
