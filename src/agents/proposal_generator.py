"""Proposal generator utilities for the marketing agent pipeline.

This module focuses on two responsibilities:
1) Build execution-ready prompts per agent from shared context.
2) Run quality-gate checks against generated proposal artifacts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Iterable

from .prompts import AGENT_PROMPTS, PROPOSAL_STRUCTURE, QUALITY_GATES


DATE_PATTERN = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
SOURCE_PATTERN = re.compile(r"(출처|source)\s*[:：]", re.IGNORECASE)
KPI_PATTERN = re.compile(r"\b(KPI|CTR|CVR|CPA|ROAS|리드|전환율)\b", re.IGNORECASE)
ACTION_30_60_90_PATTERN = re.compile(r"\b(30-60-90|30/60/90|30일|60일|90일)\b")
COMPLIANCE_RISK_PATTERN = re.compile(
    r"\b(최고|유일|완치|부작용\s*0|100%|절대)\b", re.IGNORECASE
)


@dataclass(frozen=True)
class ClientBrief:
    client_name: str
    industry: str
    region: str
    budget_range: str
    target_segments: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ProposalPackage:
    """Container for generated proposal artifacts."""

    research: str
    strategy: str
    brand_content: str
    styled_document: str

    def merged_text(self) -> str:
        return "\n\n".join(
            [self.research, self.strategy, self.brand_content, self.styled_document]
        ).strip()


@dataclass(frozen=True)
class QualityGateResult:
    gate: str
    passed: bool
    details: str


def _join_lines(values: Iterable[str], fallback: str = "-") -> str:
    cleaned = [v.strip() for v in values if v and v.strip()]
    if not cleaned:
        return fallback
    return "\n".join(f"- {item}" for item in cleaned)


def build_agent_prompt(agent_key: str, brief: ClientBrief, shared_context: str = "") -> str:
    """Build a concrete prompt for one agent."""
    if agent_key not in AGENT_PROMPTS:
        available = ", ".join(sorted(AGENT_PROMPTS.keys()))
        raise KeyError(f"Unknown agent_key={agent_key}. Available: {available}")

    base = AGENT_PROMPTS[agent_key].prompt
    return (
        f"{base}\n\n"
        "[입력 컨텍스트]\n"
        f"- 고객사명: {brief.client_name}\n"
        f"- 업종: {brief.industry}\n"
        f"- 지역: {brief.region}\n"
        f"- 예산 범위: {brief.budget_range}\n"
        f"- 타겟 세그먼트:\n{_join_lines(brief.target_segments)}\n"
        f"- 운영 제약사항:\n{_join_lines(brief.constraints)}\n"
        f"- 추가 컨텍스트:\n{shared_context.strip() or '-'}\n"
    )


def build_pipeline_prompts(brief: ClientBrief, shared_context: str = "") -> dict[str, str]:
    """Build prompts for all agents in execution order."""
    order = [
        "data_research",
        "marketing_consultant",
        "content_brand_strategist",
        "styling_expert",
    ]
    return {
        key: build_agent_prompt(key, brief=brief, shared_context=shared_context)
        for key in order
    }


def evaluate_quality_gates(package: ProposalPackage) -> list[QualityGateResult]:
    """Evaluate proposal outputs against quality gates defined in prompts.py."""
    text = package.merged_text()
    results: list[QualityGateResult] = []

    # Gate 1: Data freshness marker (date).
    has_date = bool(DATE_PATTERN.search(text))
    results.append(
        QualityGateResult(
            gate=QUALITY_GATES[0],
            passed=has_date,
            details="기준일(YYYY-MM-DD) 발견" if has_date else "기준일 표기가 없습니다.",
        )
    )

    # Gate 2: Traceable evidence (source marker).
    has_source = bool(SOURCE_PATTERN.search(text))
    results.append(
        QualityGateResult(
            gate=QUALITY_GATES[1],
            passed=has_source,
            details="출처 표기 발견" if has_source else "출처 표기(출처:, source:)가 없습니다.",
        )
    )

    # Gate 3: KPI linkage presence.
    has_kpi = bool(KPI_PATTERN.search(text))
    results.append(
        QualityGateResult(
            gate=QUALITY_GATES[2],
            passed=has_kpi,
            details="KPI/성과지표 용어 발견" if has_kpi else "KPI 또는 성과지표 표기가 없습니다.",
        )
    )

    # Gate 4: 30-60-90 execution cadence.
    has_action_plan = bool(ACTION_30_60_90_PATTERN.search(text))
    results.append(
        QualityGateResult(
            gate=QUALITY_GATES[3],
            passed=has_action_plan,
            details="30-60-90 실행 계획 표현 발견"
            if has_action_plan
            else "30-60-90(또는 30/60/90) 실행 계획이 없습니다.",
        )
    )

    # Gate 5: Compliance risk check.
    risky = sorted(set(COMPLIANCE_RISK_PATTERN.findall(text)))
    results.append(
        QualityGateResult(
            gate=QUALITY_GATES[4],
            passed=len(risky) == 0,
            details="금지 표현 없음" if not risky else f"금지 표현 감지: {', '.join(risky)}",
        )
    )

    # Gate 6: Performance measurement terms.
    has_perf_terms = bool(re.search(r"\b(CTR|CVR|CPA|ROAS|매출|리드)\b", text, re.IGNORECASE))
    results.append(
        QualityGateResult(
            gate=QUALITY_GATES[5],
            passed=has_perf_terms,
            details="선행/결과 지표 용어 발견"
            if has_perf_terms
            else "성과 측정 지표 용어(CTR/CVR/CPA/ROAS/매출/리드)가 부족합니다.",
        )
    )

    # Gate 7: Section completeness.
    missing_sections = [section for section in PROPOSAL_STRUCTURE if section not in text]
    results.append(
        QualityGateResult(
            gate=QUALITY_GATES[6],
            passed=len(missing_sections) == 0,
            details="모든 필수 섹션 포함"
            if not missing_sections
            else f"누락 섹션: {', '.join(missing_sections)}",
        )
    )

    return results


def summarize_quality_results(results: list[QualityGateResult]) -> str:
    passed = [r for r in results if r.passed]
    failed = [r for r in results if not r.passed]
    lines = [
        f"Quality Gates: {len(passed)}/{len(results)} 통과",
        "",
        "[PASS]",
    ]
    if passed:
        lines.extend(f"- {r.gate}" for r in passed)
    else:
        lines.append("- 없음")

    lines.extend(["", "[FAIL]"])
    if failed:
        lines.extend(f"- {r.gate} | {r.details}" for r in failed)
    else:
        lines.append("- 없음")

    return "\n".join(lines).strip()
