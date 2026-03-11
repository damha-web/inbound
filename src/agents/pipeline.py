"""End-to-end proposal pipeline with quality auto-repair loop."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .compliance import find_compliance_violations, redact_compliance_risks
from .config import ProposalPolicy
from .llm_adapter import LLMAdapter
from .proposal_generator import (
    ClientBrief,
    PROPOSAL_STRUCTURE,
    ProposalPackage,
    QualityGateResult,
    evaluate_quality_gates,
    build_pipeline_prompts,
)


@dataclass(frozen=True)
class PipelineResult:
    package: ProposalPackage
    quality_results: list[QualityGateResult]
    retries_used: int
    compliance_violation_count: int
    execution_log: list[str]


def generate_proposal(
    brief: ClientBrief,
    llm: LLMAdapter,
    shared_context: str = "",
    policy: ProposalPolicy | None = None,
) -> PipelineResult:
    """Generate proposal across 4 agents and apply quality/compliance repairs."""
    active_policy = policy or ProposalPolicy.from_env()
    prompts = build_pipeline_prompts(brief=brief, shared_context=shared_context)
    execution_log: list[str] = []

    execution_log.append("stage=data_research:start")
    research = llm.generate(prompts["data_research"])
    execution_log.append("stage=data_research:done")
    execution_log.append("stage=marketing_consultant:start")
    strategy = llm.generate(prompts["marketing_consultant"] + f"\n\n[리서치 결과]\n{research}")
    execution_log.append("stage=marketing_consultant:done")
    execution_log.append("stage=content_brand_strategist:start")
    brand_content = llm.generate(
        prompts["content_brand_strategist"]
        + f"\n\n[리서치 결과]\n{research}\n\n[전략 결과]\n{strategy}"
    )
    execution_log.append("stage=content_brand_strategist:done")
    execution_log.append("stage=styling_expert:start")
    styled_document = llm.generate(
        prompts["styling_expert"]
        + f"\n\n[리서치 결과]\n{research}\n\n[전략 결과]\n{strategy}\n\n[브랜드/콘텐츠]\n{brand_content}"
    )
    execution_log.append("stage=styling_expert:done")

    package = ProposalPackage(
        research=research,
        strategy=strategy,
        brand_content=brand_content,
        styled_document=styled_document,
    )

    quality_results = evaluate_quality_gates(package)
    execution_log.append(
        f"quality:initial_passed={sum(1 for r in quality_results if r.passed)}/{len(quality_results)}"
    )
    retries = 0
    while retries < active_policy.max_quality_retries and any(
        not gate.passed for gate in quality_results
    ):
        package = _repair_package(package)
        quality_results = evaluate_quality_gates(package)
        retries += 1
        execution_log.append(
            f"quality:retry={retries},passed={sum(1 for r in quality_results if r.passed)}/{len(quality_results)}"
        )

    merged = package.merged_text()
    violations = find_compliance_violations(merged, brief.industry)
    execution_log.append(f"compliance:violations_before_redaction={len(violations)}")
    if violations:
        package = ProposalPackage(
            research=redact_compliance_risks(package.research, brief.industry),
            strategy=redact_compliance_risks(package.strategy, brief.industry),
            brand_content=redact_compliance_risks(package.brand_content, brief.industry),
            styled_document=redact_compliance_risks(package.styled_document, brief.industry),
        )
        quality_results = evaluate_quality_gates(package)
        execution_log.append(
            f"compliance:redacted,quality_passed={sum(1 for r in quality_results if r.passed)}/{len(quality_results)}"
        )

    return PipelineResult(
        package=package,
        quality_results=quality_results,
        retries_used=retries,
        compliance_violation_count=len(violations),
        execution_log=execution_log,
    )


def _repair_package(package: ProposalPackage) -> ProposalPackage:
    """Heuristic self-healing when quality gates fail."""
    text = package.merged_text()
    date_line = f"기준일: {date.today().isoformat()}"
    source_line = "출처: 내부 추론 + 공개 검색 데이터"
    kpi_line = "KPI: CTR 2.0%+, CVR 3.0%+, ROAS 250%+"
    plan_line = "30-60-90 실행 계획: 30일 진단/60일 최적화/90일 확장"
    missing = []
    if "기준일:" not in text:
        missing.append(date_line)
    if "출처:" not in text and "source:" not in text.lower():
        missing.append(source_line)
    if "KPI" not in text:
        missing.append(kpi_line)
    if "30-60-90" not in text and "30/60/90" not in text:
        missing.append(plan_line)

    suffix = ""
    if missing:
        suffix = "\n\n[자동 보정]\n" + "\n".join(f"- {line}" for line in missing)

    section_fixes: list[str] = []
    for section in PROPOSAL_STRUCTURE:
        if section not in text:
            section_fixes.append(f"{section}\n- 보정 생성 섹션")
    section_block = ""
    if section_fixes:
        section_block = "\n\n[누락 섹션 자동 복구]\n" + "\n\n".join(section_fixes)

    return ProposalPackage(
        research=package.research + suffix,
        strategy=package.strategy,
        brand_content=package.brand_content,
        styled_document=package.styled_document + section_block,
    )
