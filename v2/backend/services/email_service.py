"""
Email service - send proposals via Gmail API.
"""
import os
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from typing import Optional

from googleapiclient.discovery import build
from services.sheets_service import get_sheets_service

def send_proposal_email(
    to_email: str,
    company_name: str,
    html_content: str,
    subject: Optional[str] = None,
) -> dict:
    """
    Send proposal HTML as email body via Gmail API.
    Returns dict with success status and sent timestamp.
    """
    gmail_from = os.getenv("GMAIL_FROM", "contact@damha.co.kr")

    sheets_svc = get_sheets_service()
    creds = sheets_svc.get_gmail_credentials()
    service = build("gmail", "v1", credentials=creds)

    if not subject:
        subject = f"[담하 마케팅 제안서] {company_name} 맞춤 마케팅 전략 제안"


    # Build email
    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = gmail_from
    msg["To"] = to_email

    # HTML body (inline)
    html_part = MIMEText(html_content, "html", "utf-8")
    msg.attach(html_part)

    # Attach original HTML file
    attachment = MIMEBase("application", "octet-stream")
    attachment.set_payload(html_content.encode("utf-8"))
    encoders.encode_base64(attachment)
    
    import re
    safe_name = re.sub(r'[\/:*?"<>|]', "", company_name)
    filename = f"{safe_name}_proposal.html"
    attachment.add_header("Content-Disposition", f'attachment; filename="{filename}"')
    msg.attach(attachment)

    # Send via Gmail API
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
    result = (
        service.users()
        .messages()
        .send(userId="me", body={"raw": raw})
        .execute()
    )

    sent_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "success": True,
        "message_id": result.get("id", ""),
        "sent_at": sent_at,
    }
