import unittest

from agents.config import ProposalPolicy
from agents.llm_adapter import MockLLMAdapter
from agents.pipeline import generate_proposal
from agents.proposal_generator import ClientBrief
from agents.renderer import render_outputs


class PipelineTests(unittest.TestCase):
    def test_generate_proposal_and_render_outputs(self) -> None:
        brief = ClientBrief(
            client_name="테스트의원",
            industry="의료",
            region="부산",
            budget_range="월 500~800만원",
            target_segments=["20대", "30대"],
            constraints=["의료광고 준수"],
        )
        policy = ProposalPolicy(allow_tables=False, max_quality_retries=1)
        result = generate_proposal(
            brief=brief, llm=MockLLMAdapter(), shared_context="초기 진단", policy=policy
        )
        self.assertGreaterEqual(len(result.quality_results), 1)
        self.assertGreaterEqual(len(result.execution_log), 1)
        rendered = render_outputs(result.package, policy)
        self.assertIn("AI 맞춤형 마케팅 제안서", rendered.markdown)
        self.assertIn("<html", rendered.html.lower())


if __name__ == "__main__":
    unittest.main()
