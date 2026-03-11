"""Batch CLI for generating multiple proposal files from a CSV input."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
import json
from pathlib import Path

from agents.config import ProposalPolicy
from agents.env_loader import load_dotenv
from agents.llm_adapter import make_llm_adapter
from agents.pipeline import generate_proposal
from agents.proposal_generator import ClientBrief
from agents.renderer import render_outputs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Batch-generate marketing proposals from CSV.")
    parser.add_argument("--input-csv", required=True)
    parser.add_argument("--backend", default="mock", choices=["mock", "openai"])
    parser.add_argument("--output-dir", default="proposals/generated_batch")
    parser.add_argument("--table-policy", default="forbid", choices=["allow", "forbid"])
    parser.add_argument("--max-quality-retries", type=int, default=2)
    parser.add_argument("--strict-quality", action="store_true")
    parser.add_argument("--fail-fast", action="store_true")
    return parser.parse_args()


def main() -> int:
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    args = parse_args()
    in_path = Path(args.input_csv)
    if not in_path.exists():
        raise FileNotFoundError(f"input-csv not found: {in_path}")

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    policy = ProposalPolicy(
        allow_tables=(args.table_policy == "allow"),
        include_budget_and_calendar=True,
        max_quality_retries=max(0, args.max_quality_retries),
    )
    llm = make_llm_adapter(args.backend)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_rows: list[dict[str, object]] = []
    strict_failed = False

    with in_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, row in enumerate(reader, start=1):
            try:
                brief = _row_to_brief(row)
                context = (row.get("shared_context") or "").strip()
                result = generate_proposal(
                    brief=brief,
                    llm=llm,
                    shared_context=context,
                    policy=policy,
                )
                rendered = render_outputs(result.package, policy=policy)
                slug = _safe_slug(brief.client_name)
                prefix = f"{timestamp}_{idx:03d}_{slug}"
                md_path = out_dir / f"{prefix}.md"
                html_path = out_dir / f"{prefix}.html"
                report_path = out_dir / f"{prefix}.report.json"
                md_path.write_text(rendered.markdown, encoding="utf-8")
                html_path.write_text(rendered.html, encoding="utf-8")
                report_path.write_text(
                    json.dumps(
                        {
                            "client": {
                                "name": brief.client_name,
                                "industry": brief.industry,
                                "region": brief.region,
                                "budget_range": brief.budget_range,
                            },
                            "quality_results": [
                                {
                                    "gate": item.gate,
                                    "passed": item.passed,
                                    "details": item.details,
                                }
                                for item in result.quality_results
                            ],
                            "retries_used": result.retries_used,
                            "compliance_violation_count": result.compliance_violation_count,
                            "execution_log": result.execution_log,
                            "outputs": {
                                "markdown": str(md_path),
                                "html": str(html_path),
                            },
                        },
                        ensure_ascii=False,
                        indent=2,
                    ),
                    encoding="utf-8",
                )
                passed_count = sum(1 for item in result.quality_results if item.passed)
                total_count = len(result.quality_results)
                all_passed = passed_count == total_count
                strict_failed = strict_failed or (args.strict_quality and not all_passed)
                summary_rows.append(
                    {
                        "index": idx,
                        "client_name": brief.client_name,
                        "quality_passed": passed_count,
                        "quality_total": total_count,
                        "retries_used": result.retries_used,
                        "compliance_violation_count": result.compliance_violation_count,
                        "status": "ok" if all_passed else "quality_fail",
                        "markdown": str(md_path),
                        "html": str(html_path),
                        "report": str(report_path),
                    }
                )
                print(
                    f"[{idx}] {brief.client_name} "
                    f"quality={passed_count}/{total_count} retries={result.retries_used}"
                )
            except Exception as exc:
                summary_rows.append(
                    {
                        "index": idx,
                        "client_name": row.get("client_name", ""),
                        "quality_passed": 0,
                        "quality_total": 0,
                        "retries_used": 0,
                        "compliance_violation_count": 0,
                        "status": f"error:{exc}",
                        "markdown": "",
                        "html": "",
                        "report": "",
                    }
                )
                print(f"[{idx}] ERROR: {exc}")
                if args.fail_fast:
                    break

    summary_path = out_dir / f"{timestamp}_summary.csv"
    _write_summary_csv(summary_path, summary_rows)
    print(f"[saved] {summary_path}")

    if args.strict_quality and strict_failed:
        print("strict_quality=FAILED")
        return 2
    return 0


def _row_to_brief(row: dict[str, str]) -> ClientBrief:
    return ClientBrief(
        client_name=(row.get("client_name") or "").strip(),
        industry=(row.get("industry") or "").strip(),
        region=(row.get("region") or "").strip(),
        budget_range=(row.get("budget_range") or "").strip(),
        target_segments=_csv_to_list(row.get("target_segments", "")),
        constraints=_csv_to_list(row.get("constraints", "")),
    )


def _csv_to_list(raw: str) -> list[str]:
    return [item.strip() for item in (raw or "").split(",") if item.strip()]


def _safe_slug(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() else "_" for ch in value.strip())
    return cleaned.strip("_") or "proposal"


def _write_summary_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fields = [
        "index",
        "client_name",
        "quality_passed",
        "quality_total",
        "retries_used",
        "compliance_violation_count",
        "status",
        "markdown",
        "html",
        "report",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


if __name__ == "__main__":
    raise SystemExit(main())
