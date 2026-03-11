"""
Google Sheets service - read/write submission data.
"""
import os
from typing import List, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import json

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/drive.file",
]

# Actual sheet structure (damhaDB):
# Row 1: dummy header (A1, B1, C1...)
# Row 2: real header (타임스탬프, 병원명, 위치, 타겟, 이메일, IP주소)
# Row 3+: data
# Columns A-F are from damhaDB, G-I are added by V2
SHEET_COLUMNS = {
    "timestamp": 0,      # A - 타임스탬프
    "company_name": 1,   # B - 병원명
    "location": 2,       # C - 위치
    "targets": 3,        # D - 타겟
    "email": 4,          # E - 이메일
    "ip_address": 5,     # F - IP주소 (damhaDB original)
    "status": 6,         # G - 처리상태 (v2 added)
    "sent_at": 7,        # H - 발송일시 (v2 added)
    "proposal_path": 8,  # I - 제안서경로 (v2 added)
}
DATA_START_ROW = 3  # Data starts at row 3 (row 1=dummy, row 2=header)
TOTAL_COLUMNS = 9  # A through I


class SheetsService:
    def __init__(self):
        self.creds = None
        self.sheet_id = os.getenv("GOOGLE_SHEET_ID", "")
        self.sheet_name = os.getenv("GOOGLE_SHEET_NAME", "설문지 응답 시트1")
        self.credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials/credentials.json")
        self.token_path = os.getenv("GOOGLE_TOKEN_PATH", "credentials/token.json")

    def _get_credentials(self) -> Credentials:
        """Get or refresh Google API credentials prioritize environment token."""
        creds = None
        refresh_token = os.getenv("GOOGLE_REFRESH_TOKEN")
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

        if refresh_token and client_id and client_secret:
            # Build credentials from environment (Production Server usage)
            info = {
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token,
                "token_uri": "https://oauth2.googleapis.com/token",
            }
            creds = Credentials.from_authorized_user_info(info, SCOPES)
            
        elif os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"Google credentials not found at {self.credentials_path}. "
                        "Please download from Google Cloud Console or provide ENV tokens."
                    )
                # When scopes change or run first time locally
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save the new token back to JSON if it's not purely from ENV
            if not refresh_token:
                with open(self.token_path, "w") as f:
                    f.write(creds.to_json())

        return creds

    def _get_service(self):
        creds = self._get_credentials()
        return build("sheets", "v4", credentials=creds)

    def _detect_sheet_name(self, service) -> str:
        """Auto-detect the first sheet tab name from the spreadsheet."""
        try:
            meta = service.spreadsheets().get(spreadsheetId=self.sheet_id).execute()
            sheets = meta.get("sheets", [])
            if sheets:
                actual_name = sheets[0]["properties"]["title"]
                print(f"[SheetsService] Auto-detected sheet name: '{actual_name}'")
                return actual_name
        except Exception as e:
            print(f"[SheetsService] Failed to detect sheet name: {e}")
        return self.sheet_name

    def get_all_submissions(self) -> List[dict]:
        """Read all rows from Google Sheets."""
        service = self._get_service()
        range_name = f"{self.sheet_name}!A{DATA_START_ROW}:I"  # Skip 2 header rows

        try:
            result = (
                service.spreadsheets()
                .values()
                .get(spreadsheetId=self.sheet_id, range=range_name)
                .execute()
            )
        except Exception as e:
            print(f"[SheetsService] Failed with sheet name '{self.sheet_name}': {e}")
            # Fallback: auto-detect actual sheet name and retry
            actual_name = self._detect_sheet_name(service)
            if actual_name != self.sheet_name:
                self.sheet_name = actual_name
                print(f"[SheetsService] Retrying with detected name: '{actual_name}'")
                range_name = f"{actual_name}!A{DATA_START_ROW}:I"
                result = (
                    service.spreadsheets()
                    .values()
                    .get(spreadsheetId=self.sheet_id, range=range_name)
                    .execute()
                )
            else:
                raise

        rows = result.get("values", [])
        print(f"[SheetsService] Fetched {len(rows)} rows from '{self.sheet_name}'")

        submissions = []
        for i, row in enumerate(rows):
            # Pad row to ensure all columns exist
            while len(row) < TOTAL_COLUMNS:
                row.append("")

            submissions.append({
                "row_index": i + DATA_START_ROW,  # actual sheet row number
                "receipt_id": str(i + 1).zfill(3),
                "timestamp": row[SHEET_COLUMNS["timestamp"]],
                "company_name": row[SHEET_COLUMNS["company_name"]],
                "location": row[SHEET_COLUMNS["location"]],
                "targets": row[SHEET_COLUMNS["targets"]],
                "email": row[SHEET_COLUMNS["email"]],
                "status": row[SHEET_COLUMNS["status"]] or "대기",
                "sent_at": row[SHEET_COLUMNS["sent_at"]],
                "proposal_path": row[SHEET_COLUMNS["proposal_path"]],
            })

        return submissions

    def update_status(self, row_index: int, status: str, sent_at: str = "", proposal_path: str = ""):
        """Update status columns for a specific row."""
        service = self._get_service()

        # Update columns G, H, I (status, sent_at, proposal_path)
        range_name = f"{self.sheet_name}!G{row_index}:I{row_index}"
        values = [[status, sent_at, proposal_path]]

        service.spreadsheets().values().update(
            spreadsheetId=self.sheet_id,
            range=range_name,
            valueInputOption="RAW",
            body={"values": values},
        ).execute()

    def get_gmail_credentials(self) -> Credentials:
        """Return credentials for Gmail API usage."""
        return self._get_credentials()

    def get_drive_credentials(self) -> Credentials:
        """Return credentials for Drive API usage."""
        return self._get_credentials()


# Singleton instance
_sheets_service: Optional[SheetsService] = None


def get_sheets_service() -> SheetsService:
    global _sheets_service
    if _sheets_service is None:
        _sheets_service = SheetsService()
    return _sheets_service
