import unittest

from agents.compliance import (
    find_compliance_violations,
    normalize_industry,
    redact_compliance_risks,
)


class ComplianceTests(unittest.TestCase):
    def test_medical_industry_detection(self) -> None:
        self.assertEqual(normalize_industry("의료"), "medical")
        self.assertEqual(normalize_industry("Plastic Surgery Clinic"), "medical")
        self.assertEqual(normalize_industry("카페"), "default")

    def test_medical_banned_terms_detected(self) -> None:
        text = "우리 병원은 최고 수준이며 완치 사례를 강조합니다."
        violations = find_compliance_violations(text, "의료")
        self.assertTrue(any(v.term.lower() in {"최고", "완치"} for v in violations))

    def test_redaction_replaces_risky_terms(self) -> None:
        text = "최고 의료진이 100% 완치를 약속합니다."
        redacted = redact_compliance_risks(text, "의료")
        self.assertNotIn("최고", redacted)
        self.assertNotIn("100%", redacted)
        self.assertNotIn("완치", redacted)


if __name__ == "__main__":
    unittest.main()
