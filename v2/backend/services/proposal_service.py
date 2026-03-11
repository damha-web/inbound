"""
Proposal service - wraps V1 AI pipeline for proposal generation.
"""
import os
import sys
import subprocess
import asyncio
import glob
from datetime import datetime
from typing import Optional, Dict
from pathlib import Path

from services.drive_service import upload_proposal_to_drive, download_proposal_from_drive


def _get_config():
    """Read configuration at runtime (after dotenv is loaded)."""
    return {
        "v1_src": os.getenv("V1_SRC_PATH", "H:/inbound/src"),
        "output_dir": os.getenv("PROPOSAL_OUTPUT_DIR", "H:/inbound/proposals/generated"),
        "table_policy": os.getenv("PROPOSAL_TABLE_POLICY", "forbid"),
    }

# In-memory task tracking
_tasks: Dict[int, dict] = {}


def get_task_status(row_index: int) -> Optional[dict]:
    return _tasks.get(row_index)


async def generate_proposal(
    row_index: int,
    company_name: str,
    industry: str,
    region: str,
    target_segments: str,
    budget_range: str = "미정",
    constraints: str = "의료광고 심의 준수,과장표현 금지",
) -> str:
    """
    Run V1 pipeline to generate a proposal.
    Returns the path to the generated HTML file.
    """
    _tasks[row_index] = {
        "status": "생성중",
        "progress": 10,
        "message": "AI 파이프라인 시작...",
    }

    cfg = _get_config()

    try:
        # Ensure output directory exists
        Path(cfg["output_dir"]).mkdir(parents=True, exist_ok=True)

        # Build command to invoke V1 pipeline
        cmd = [
            sys.executable,
            os.path.join(cfg["v1_src"], "run_proposal.py"),
            "--client-name", company_name,
            "--industry", industry,
            "--region", region,
            "--target-segments", target_segments,
            "--budget-range", budget_range,
            "--constraints", constraints,
            "--backend", "openai",
            "--output-format", "html",
            "--output-dir", cfg["output_dir"],
            "--table-policy", cfg["table_policy"],
        ]

        _tasks[row_index]["progress"] = 20
        _tasks[row_index]["message"] = "V1 파이프라인 호출 중..."

        # Run subprocess asynchronously
        env = os.environ.copy()
        env["PYTHONPATH"] = cfg["v1_src"]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
            cwd=Path(cfg["v1_src"]).parent,  # H:/inbound so .env is found
        )

        _tasks[row_index]["progress"] = 50
        _tasks[row_index]["message"] = "AI 에이전트 제안서 생성 중..."

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            error_msg = stderr.decode("utf-8", errors="replace")
            _tasks[row_index] = {
                "status": "오류",
                "progress": 0,
                "message": f"생성 실패: {error_msg[:200]}",
            }
            raise RuntimeError(f"Pipeline failed: {error_msg}")

        _tasks[row_index]["progress"] = 90
        _tasks[row_index]["message"] = "Google Drive 업로드 중..."

        # Find the generated HTML file
        local_html_path = _find_latest_html(company_name, cfg["output_dir"])
        if not local_html_path:
            raise FileNotFoundError(f"Generated HTML not found for {company_name}")

        drive_url = upload_proposal_to_drive(local_html_path, company_name)
        
        _tasks[row_index] = {
            "status": "검토대기",
            "progress": 100,
            "message": "제안서 생성 완료",
            "proposal_path": drive_url,
        }

        return drive_url

    except Exception as e:
        if row_index in _tasks and _tasks[row_index]["status"] != "오류":
            _tasks[row_index] = {
                "status": "오류",
                "progress": 0,
                "message": str(e)[:200],
            }
        raise


def _find_latest_html(company_name: str, output_dir: str = "") -> Optional[str]:
    """Find the most recently generated HTML file for a company."""
    out = output_dir or _get_config()["output_dir"]
    # V1 naming: {timestamp}_{slug}.html where slug = safe chars of company_name
    slug = "".join(ch if ch.isalnum() else "_" for ch in company_name.strip()).strip("_")

    # Try slug-based match first
    pattern = os.path.join(out, f"*{slug}*.html")
    files = glob.glob(pattern)
    if not files:
        # Broader fallback: any HTML
        pattern = os.path.join(out, "*.html")
        files = glob.glob(pattern)

    if files:
        return max(files, key=os.path.getmtime)
    return None


def get_proposal_html(proposal_path: str) -> str:
    """Read and return the HTML content of a proposal (local or from Drive)."""
    if proposal_path.startswith("http"):
        return download_proposal_from_drive(proposal_path)
        
    if not os.path.exists(proposal_path):
        raise FileNotFoundError(f"Proposal file not found: {proposal_path}")

    with open(proposal_path, "r", encoding="utf-8") as f:
        return f.read()
