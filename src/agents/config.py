"""Configuration and policy definitions for proposal generation."""

from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class ProposalPolicy:
    """Global policy flags that resolve document-rule conflicts."""

    allow_tables: bool = False
    include_budget_and_calendar: bool = True
    max_quality_retries: int = 2

    @staticmethod
    def from_env() -> "ProposalPolicy":
        table_policy = os.getenv("PROPOSAL_TABLE_POLICY", "forbid").strip().lower()
        allow_tables = table_policy in {"allow", "true", "1", "yes"}
        include_budget = os.getenv("PROPOSAL_INCLUDE_BUDGET_CALENDAR", "true").lower()
        max_retries_str = os.getenv("PROPOSAL_MAX_QUALITY_RETRIES", "2")
        try:
            max_retries = max(0, int(max_retries_str))
        except ValueError:
            max_retries = 2
        return ProposalPolicy(
            allow_tables=allow_tables,
            include_budget_and_calendar=include_budget in {"true", "1", "yes"},
            max_quality_retries=max_retries,
        )
