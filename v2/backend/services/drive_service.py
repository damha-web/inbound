"""
Google Drive service - upload and manage proposal files.
"""
import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from services.sheets_service import get_sheets_service

def upload_proposal_to_drive(file_path: str, company_name: str) -> str:
    """
    Uploads a generated HTML proposal to Google Drive.
    Returns the webViewLink of the uploaded file.
    """
    sheets_svc = get_sheets_service()
    creds = sheets_svc.get_drive_credentials()
    service = build("drive", "v3", credentials=creds)

    folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
    filename = os.path.basename(file_path)

    file_metadata = {"name": filename}
    if folder_id:
        file_metadata["parents"] = [folder_id]

    # MimeType for HTML
    media = MediaFileUpload(file_path, mimetype="text/html", resumable=True)

    try:
        # Upload file
        file = (
            service.files()
            .create(body=file_metadata, media_body=media, fields="id, webViewLink")
            .execute()
        )
        file_id = file.get("id")

        # Make file accessible to anyone with the link (read-only)
        # We need this to view it easily or send link. 
        # Alternatively, the folder it's in could be shared.
        service.permissions().create(
            fileId=file_id,
            body={"type": "anyone", "role": "reader"},
        ).execute()

        print(f"[Drive] Uploaded file: {file.get('webViewLink')}")
        return file.get("webViewLink")

    except Exception as e:
        print(f"[Drive] Failed to upload {filename}: {e}")
        # Return local path as fallback if Drive upload fails
        return file_path


def download_proposal_from_drive(file_url: str) -> str:
    """
    Downloads the HTML content of a proposal from a Google Drive URL.
    Returns the HTML string.
    """
    import re
    # Extract file ID from URL (e.g., https://drive.google.com/file/d/FILE_ID/view?usp=drivesdk)
    match = re.search(r"/d/([a-zA-Z0-9_-]+)", file_url)
    if not match:
        raise ValueError(f"Invalid Google Drive URL: {file_url}")
    file_id = match.group(1)

    sheets_svc = get_sheets_service()
    creds = sheets_svc.get_drive_credentials()
    service = build("drive", "v3", credentials=creds)

    request = service.files().get_media(fileId=file_id)
    # The proposal HTML is small, usually less than 1MB, so we can just download it all
    from io import BytesIO
    from googleapiclient.http import MediaIoBaseDownload

    fh = BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()

    return fh.getvalue().decode("utf-8")
