import unittest

from run_batch_proposals import _csv_to_list, _row_to_brief, _safe_slug


class BatchRunnerTests(unittest.TestCase):
    def test_csv_to_list(self) -> None:
        self.assertEqual(_csv_to_list("a, b , ,c"), ["a", "b", "c"])

    def test_row_to_brief(self) -> None:
        row = {
            "client_name": "Clinic",
            "industry": "medical",
            "region": "Busan",
            "budget_range": "500",
            "target_segments": "x,y",
            "constraints": "c1,c2",
        }
        brief = _row_to_brief(row)
        self.assertEqual(brief.client_name, "Clinic")
        self.assertEqual(brief.target_segments, ["x", "y"])

    def test_safe_slug(self) -> None:
        self.assertEqual(_safe_slug("A B"), "A_B")
        self.assertEqual(_safe_slug(""), "proposal")


if __name__ == "__main__":
    unittest.main()
