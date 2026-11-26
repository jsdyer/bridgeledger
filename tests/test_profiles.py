from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from profiles import comparable


class ProfileTests(unittest.TestCase):
    def test_comparison_excludes_unfinished_errors_and_conflicts(self):
        def row(day, value, level="1", final=True, error=False):
            return dict(date=day, level=level, rating=value, finalised=final, evidence=[dict(inError=error)])
        visits = [row("2019-01-01", 2), row("2020-01-01", 1), row("2020-01-01", 2),
                  row("2021-01-01", 1, error=True), row("2022-01-01", 1, final=False),
                  row("2023-01-01", 0, level="2"), row("2024-01-01", None)]
        self.assertEqual([r["date"] for r in comparable(visits, "1")], ["2019-01-01"])
        self.assertEqual(comparable(visits, "2")[0]["rating"], 0)
