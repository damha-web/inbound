import unittest

from agents.config import ProposalPolicy
from agents.proposal_generator import ProposalPackage
from agents.renderer import render_html, render_markdown


class RendererTests(unittest.TestCase):
    def setUp(self) -> None:
        self.package = ProposalPackage(
            research="리서치 본문",
            strategy="전략 본문",
            brand_content="브랜드 본문",
            styled_document="스타일링 본문",
        )

    def test_markdown_has_title(self) -> None:
        text = render_markdown(self.package)
        self.assertIn("# AI 맞춤형 마케팅 제안서", text)

    def test_html_reflects_table_policy(self) -> None:
        allow = render_html(self.package, ProposalPolicy(allow_tables=True))
        forbid = render_html(self.package, ProposalPolicy(allow_tables=False))
        self.assertIn("표 정책: 허용", allow)
        self.assertIn("표 정책: 금지", forbid)


if __name__ == "__main__":
    unittest.main()
