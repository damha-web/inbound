"""CLI entrypoint for proposal generation pipeline."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path

from agents.config import ProposalPolicy
from agents.env_loader import load_dotenv
from agents.llm_adapter import make_llm_adapter
from agents.pipeline import generate_proposal
from agents.proposal_generator import ClientBrief, summarize_quality_results
from agents.renderer import render_outputs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate marketing proposal package.")
    parser.add_argument("--client-name", required=True)
    parser.add_argument("--industry", required=True)
    parser.add_argument("--region", required=True)
    parser.add_argument("--budget-range", required=True)
    parser.add_argument("--target-segments", default="")
    parser.add_argument("--constraints", default="")
    parser.add_argument("--shared-context", default="")
    parser.add_argument("--context-file", default="")
    parser.add_argument("--backend", default="mock", choices=["mock", "openai"])
    parser.add_argument("--output-dir", default="proposals/generated")
    parser.add_argument("--output-format", default="both", choices=["both", "html", "markdown"])
    parser.add_argument("--table-policy", default="forbid", choices=["allow", "forbid"])
    parser.add_argument("--max-quality-retries", type=int, default=2)
    parser.add_argument("--save-json-report", action="store_true")
    parser.add_argument("--strict-quality", action="store_true")
    parser.add_argument("--print-execution-log", action="store_true")
    return parser.parse_args()


def main() -> int:
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    args = parse_args()
    context = (args.shared_context or "").strip()
    if args.context_file:
        context_path = Path(args.context_file)
        if context_path.exists():
            context = context + "\n\n" + context_path.read_text(encoding="utf-8")
        else:
            raise FileNotFoundError(f"context-file not found: {context_path}")

    brief = ClientBrief(
        client_name=args.client_name.strip(),
        industry=args.industry.strip(),
        region=args.region.strip(),
        budget_range=args.budget_range.strip(),
        target_segments=_csv_to_list(args.target_segments),
        constraints=_csv_to_list(args.constraints),
    )

    policy = ProposalPolicy(
        allow_tables=(args.table_policy == "allow"),
        include_budget_and_calendar=True,
        max_quality_retries=max(0, args.max_quality_retries),
    )
    llm = make_llm_adapter(args.backend)
    result = generate_proposal(brief=brief, llm=llm, shared_context=context, policy=policy)

    rendered = render_outputs(result.package, policy=policy)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = _safe_slug(brief.client_name)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    md_path = out_dir / f"{timestamp}_{slug}.md"
    html_path = out_dir / f"{timestamp}_{slug}.html"

    if args.output_format in {"both", "markdown"}:
        md_path.write_text(rendered.markdown, encoding="utf-8")
        print(f"[saved] {md_path}")
    if args.output_format in {"both", "html"}:
        html_path.write_text(rendered.html, encoding="utf-8")
        print(f"[saved] {html_path}")

    if args.save_json_report:
        report_path = out_dir / f"{timestamp}_{slug}.report.json"
        report = {
            "client": {
                "name": brief.client_name,
                "industry": brief.industry,
                "region": brief.region,
                "budget_range": brief.budget_range,
            },
            "policy": {
                "allow_tables": policy.allow_tables,
                "max_quality_retries": policy.max_quality_retries,
            },
            "quality_results": [
                {"gate": item.gate, "passed": item.passed, "details": item.details}
                for item in result.quality_results
            ],
            "retries_used": result.retries_used,
            "compliance_violation_count": result.compliance_violation_count,
            "execution_log": result.execution_log,
            "outputs": {
                "markdown": str(md_path) if args.output_format in {"both", "markdown"} else None,
                "html": str(html_path) if args.output_format in {"both", "html"} else None,
            },
        }
        report_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"[saved] {report_path}")

    print(summarize_quality_results(result.quality_results))
    print(
        f"retries_used={result.retries_used}, "
        f"compliance_violation_count={result.compliance_violation_count}"
    )
    if args.print_execution_log:
        print("[execution_log]")
        for item in result.execution_log:
            print(f"- {item}")

    if args.strict_quality and any(not item.passed for item in result.quality_results):
        print("strict_quality=FAILED")
        return 2
    return 0


def _csv_to_list(raw: str) -> list[str]:
    return [item.strip() for item in (raw or "").split(",") if item.strip()]


def _safe_slug(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() else "_" for ch in value.strip())
    return cleaned.strip("_") or "proposal"


if __name__ == "__main__":
    raise SystemExit(main())
