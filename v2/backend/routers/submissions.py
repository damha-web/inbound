"""
Submissions router - read data from Google Sheets.
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional
import traceback
from models.schemas import SubmissionListResponse, SubmissionRow, StatsResponse
from services.sheets_service import get_sheets_service
from services.auth_service import get_current_user

router = APIRouter(prefix="/api/submissions", tags=["submissions"])


@router.get("", response_model=SubmissionListResponse)
async def list_submissions(
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search by company name or location"),
    sort_by: Optional[str] = Query("timestamp", description="Sort field"),
    sort_order: Optional[str] = Query("desc", description="asc or desc"),
    _user: str = Depends(get_current_user),
):
    """Get all submissions from Google Sheets."""
    sheets = get_sheets_service()
    try:
        items = sheets.get_all_submissions()
    except Exception as e:
        err_msg = str(e)
        print(f"[submissions] Error fetching data: {err_msg}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Google Sheets 연동 오류: {err_msg[:200]}")

    # Filter by status
    if status and status != "전체":
        items = [i for i in items if i["status"] == status]

    # Search
    if search:
        search_lower = search.lower()
        items = [
            i for i in items
            if search_lower in i["company_name"].lower()
            or search_lower in i["location"].lower()
        ]

    # Sort
    reverse = sort_order == "desc"
    if sort_by in ("timestamp", "company_name", "location", "status"):
        items.sort(key=lambda x: x.get(sort_by, ""), reverse=reverse)

    return SubmissionListResponse(
        total=len(items),
        items=[SubmissionRow(**i) for i in items],
    )


@router.get("/stats", response_model=StatsResponse)
async def get_stats(_user: str = Depends(get_current_user)):
    """Get dashboard statistics."""
    sheets = get_sheets_service()
    items = sheets.get_all_submissions()

    stats = StatsResponse(total=len(items))
    for item in items:
        s = item.get("status", "대기")
        if s == "대기":
            stats.pending += 1
        elif s == "생성중":
            stats.generating += 1
        elif s in ("검토대기", "승인"):
            stats.review += 1
        elif s == "발송완료":
            stats.sent += 1
        elif s == "오류":
            stats.error += 1
        else:
            stats.pending += 1

    return stats


@router.patch("/{row_index}/status")
async def update_submission_status(
    row_index: int,
    status: str = Query(...),
    _user: str = Depends(get_current_user),
):
    """Manually update a submission's status."""
    sheets = get_sheets_service()
    sheets.update_status(row_index, status)
    return {"success": True, "row_index": row_index, "status": status}
