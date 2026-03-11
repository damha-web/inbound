import unittest

from agents.proposal_generator import (
    ClientBrief,
    ProposalPackage,
    build_pipeline_prompts,
    evaluate_quality_gates,
)


class ProposalGeneratorTests(unittest.TestCase):
    def test_build_pipeline_prompts_returns_all_agents(self) -> None:
        brief = ClientBrief(
            client_name="테스트의원",
            industry="의료",
            region="부산",
            budget_range="월 500~800만원",
        )
        prompts = build_pipeline_prompts(brief, shared_context="테스트")
        self.assertEqual(
            list(prompts.keys()),
            [
                "data_research",
                "marketing_consultant",
                "content_brand_strategist",
                "styling_expert",
            ],
        )
        self.assertIn("고객사명: 테스트의원", prompts["data_research"])

    def test_quality_gates_pass_with_complete_text(self) -> None:
        package = ProposalPackage(
            research=(
                "1. 정밀 상권 및 포지션 분석\n"
                "2. 동종업 시장조사 (Top 4)\n"
                "기준일: 2026-03-09\n"
                "출처: 네이버"
            ),
            strategy=(
                "3. 브랜딩 및 마케팅 추천 전략\n"
                "4. 마케팅 채널 진단 및 개선\n"
                "KPI: CTR 2.1%, CVR 3.0%\n"
                "30-60-90 실행 계획"
            ),
            brand_content="5. 브랜드 방향성 (Tone & Manner)",
            styled_document="6. 실행 예산안 및 4주 콘텐츠 로드맵\nROAS 목표",
        )
        results = evaluate_quality_gates(package)
        self.assertTrue(all(r.passed for r in results), msg=[r.details for r in results])


if __name__ == "__main__":
    unittest.main()
