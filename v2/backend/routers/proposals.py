"""
Proposals router - generate and preview proposals.
"""
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse
from models.schemas import ProposalGenerateRequest, ProposalStatusResponse
from services.proposal_service import generate_proposal, get_task_status, get_proposal_html
from services.sheets_service import get_sheets_service
from services.auth_service import get_current_user

router = APIRouter(prefix="/api/proposals", tags=["proposals"])


async def _run_generation(req: ProposalGenerateRequest):
    """Background task to generate a proposal."""
    import traceback
    sheets = get_sheets_service()
    try:
        sheets.update_status(req.row_index, "생성중")
        html_path = await generate_proposal(
            row_index=req.row_index,
            company_name=req.company_name,
            industry=req.industry,
            region=req.location,
            target_segments=req.targets,
            budget_range=req.budget_range,
            constraints=req.constraints,
        )
        sheets.update_status(req.row_index, "검토대기", proposal_path=html_path)
    except Exception as e:
        print(f"[proposals] Generation FAILED for row {req.row_index}: {e}")
        traceback.print_exc()
        sheets.update_status(req.row_index, "오류")


@router.post("/generate")
async def start_generation(
    req: ProposalGenerateRequest,
    background_tasks: BackgroundTasks,
    _user: str = Depends(get_current_user),
):
    """Start async proposal generation."""
    background_tasks.add_task(_run_generation, req)
    return {
        "success": True,
        "message": f"제안서 생성을 시작합니다: {req.company_name}",
        "row_index": req.row_index,
    }


@router.get("/{row_index}/status", response_model=ProposalStatusResponse)
async def check_status(
    row_index: int,
    _user: str = Depends(get_current_user),
):
    """Poll generation progress."""
    task = get_task_status(row_index)
    if not task:
        return ProposalStatusResponse(
            row_index=row_index,
            status="unknown",
            message="진행 중인 작업 없음",
        )
    return ProposalStatusResponse(
        row_index=row_index,
        status=task.get("status", "unknown"),
        progress=task.get("progress", 0),
        message=task.get("message", ""),
        proposal_path=task.get("proposal_path"),
    )


@router.get("/{row_index}/html", response_class=HTMLResponse)
async def get_html(
    row_index: int,
    _user: str = Depends(get_current_user),
):
    """Return generated proposal HTML for preview."""
    task = get_task_status(row_index)
    if not task or "proposal_path" not in task:
        # Try to get from sheets
        sheets = get_sheets_service()
        items = sheets.get_all_submissions()
        found = next((i for i in items if i["row_index"] == row_index), None)
        if found and found.get("proposal_path"):
            html = get_proposal_html(found["proposal_path"])
            return HTMLResponse(content=html)
        raise HTTPException(status_code=404, detail="제안서를 찾을 수 없습니다")

    html = get_proposal_html(task["proposal_path"])
    return HTMLResponse(content=html)
