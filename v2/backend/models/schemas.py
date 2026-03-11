"""
Pydantic schemas for the Automation V2 API.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime


class SubmissionStatus(str, Enum):
    PENDING = "대기"
    GENERATING = "생성중"
    REVIEW = "검토대기"
    APPROVED = "승인"
    SENDING = "발송중"
    SENT = "발송완료"
    ERROR = "오류"


class SubmissionRow(BaseModel):
    """Single row from Google Sheets."""
    row_index: int
    receipt_id: str = ""
    timestamp: str = ""
    company_name: str = ""
    location: str = ""
    targets: str = ""
    email: str = ""
    status: str = "대기"
    sent_at: str = ""
    proposal_path: str = ""


class SubmissionListResponse(BaseModel):
    total: int
    items: List[SubmissionRow]


class ProposalGenerateRequest(BaseModel):
    row_index: int
    company_name: str
    location: str
    targets: str
    email: str
    industry: str = "의료"
    budget_range: str = "미정"
    constraints: str = "의료광고 심의 준수,과장표현 금지"


class ProposalStatusResponse(BaseModel):
    row_index: int
    status: str
    progress: int = 0  # 0-100
    message: str = ""
    proposal_path: Optional[str] = None


class EmailSendRequest(BaseModel):
    row_index: int
    to_email: str
    company_name: str
    proposal_path: str
    subject: Optional[str] = None


class EmailSendResponse(BaseModel):
    success: bool
    message: str
    sent_at: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class StatsResponse(BaseModel):
    total: int = 0
    pending: int = 0
    generating: int = 0
    review: int = 0
    sent: int = 0
    error: int = 0
