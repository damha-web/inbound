"""Industry-aware compliance rules for proposal copy."""

from __future__ import annotations

from dataclasses import dataclass
import re


COMMON_BANNED = [
    r"\b100%\b",
    r"\b절대\b",
]

INDUSTRY_BANNED: dict[str, list[str]] = {
    "medical": [
        r"\b최고\b",
        r"\b유일\b",
        r"\b완치\b",
        r"\b부작용\s*0\b",
        r"\b기적\b",
    ],
    "default": [
        r"\b업계\s*1위\b",
        r"\b무조건\b",
    ],
}


@dataclass(frozen=True)
class ComplianceViolation:
    term: str
    start: int
    end: int
    rule: str


def normalize_industry(industry: str) -> str:
    value = (industry or "").strip().lower()
    if any(token in value for token in ["의료", "병원", "clinic", "medical"]):
        return "medical"
    return "default"


def get_patterns(industry: str) -> list[str]:
    group = normalize_industry(industry)
    return COMMON_BANNED + INDUSTRY_BANNED.get(group, INDUSTRY_BANNED["default"])


def find_compliance_violations(text: str, industry: str) -> list[ComplianceViolation]:
    violations: list[ComplianceViolation] = []
    for pattern in get_patterns(industry):
        regex = re.compile(pattern, re.IGNORECASE)
        for match in regex.finditer(text):
            violations.append(
                ComplianceViolation(
                    term=match.group(0), start=match.start(), end=match.end(), rule=pattern
                )
            )
    return violations


def redact_compliance_risks(text: str, industry: str) -> str:
    """Replace banned expressions with safer alternatives."""
    output = text
    replacements = {
        "최고": "우수한",
        "유일": "차별화된",
        "완치": "개선",
        "기적": "기대 가능한 변화",
        "업계 1위": "선도권 경쟁",
        "100%": "높은 수준의",
        "절대": "가급적",
        "무조건": "상황에 따라",
    }
    for raw, safe in replacements.items():
        output = re.sub(raw, safe, output, flags=re.IGNORECASE)
    output = re.sub(r"부작용\s*0", "부작용 가능성 최소화", output, flags=re.IGNORECASE)
    return output
