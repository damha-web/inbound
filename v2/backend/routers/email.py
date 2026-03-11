"""
Email router - send proposals via Gmail.
"""
from fastapi import APIRouter, Depends, HTTPException
from models.schemas import EmailSendRequest, EmailSendResponse
from services.email_service import send_proposal_email
from services.proposal_service import get_proposal_html
from services.sheets_service import get_sheets_service
from services.auth_service import get_current_user

router = APIRouter(prefix="/api/email", tags=["email"])


@router.post("/send", response_model=EmailSendResponse)
async def send_email(
    req: EmailSendRequest,
    _user: str = Depends(get_current_user),
):
    """Send a proposal email via Gmail API."""
    try:
        sheets = get_sheets_service()
        sheets.update_status(req.row_index, "발송중")

        html_content = get_proposal_html(req.proposal_path)
        result = send_proposal_email(
            to_email=req.to_email,
            company_name=req.company_name,
            html_content=html_content,
            subject=req.subject,
        )

        # Update sheet with sent status
        sheets.update_status(
            req.row_index,
            "발송완료",
            sent_at=result["sent_at"],
            proposal_path=req.proposal_path,
        )

        return EmailSendResponse(
            success=True,
            message=f"{req.company_name} 제안서를 {req.to_email}로 발송 완료",
            sent_at=result["sent_at"],
        )

    except Exception as e:
        sheets = get_sheets_service()
        sheets.update_status(req.row_index, "오류")
        raise HTTPException(status_code=500, detail=f"이메일 발송 실패: {str(e)}")
