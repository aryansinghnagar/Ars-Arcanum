#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Series Cross-Book Continuity Engine (scripts/lib/series_continuity.py).
Validates:
- WOR-103: Multi-volume discovery across series.
- Cross-book character mortality tracking (resurrected character alerts).
- Cross-book physical trait drift detection (contradictory eye/hair colors).
- HTML series ledger generation.
"""

import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.series_continuity import (
    scan_series_continuity,
    generate_series_html_report
)


class TestSeriesContinuityEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.series_dir = Path(self.temp_dir.name)
        self.b1_dir = self.series_dir / "Book-01" / "01_Act_I"
        self.b2_dir = self.series_dir / "Book-02" / "01_Act_I"
        self.b1_dir.mkdir(parents=True)
        self.b2_dir.mkdir(parents=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_mortality_invariant_detection(self):
        # Character Vance dies in Book 1, but appears active in Book 2
        (self.b1_dir / "01_Ch.md").write_text("Vance died on the battlefield protecting the gate.", encoding="utf-8")
        (self.b2_dir / "01_Ch.md").write_text("Vance had blue eyes and drew his blade once again.", encoding="utf-8")

        report = scan_series_continuity(self.series_dir)
        self.assertEqual(report["total_volumes"], 2)
        self.assertGreater(len(report["mortality_violations"]), 0)
        self.assertEqual(report["mortality_violations"][0]["character"], "Vance")

    def test_mortality_without_traits(self):
        # Character Marcus dies in Book 1, appears speaking in Book 2 without any eye/hair description
        (self.b1_dir / "02_Ch.md").write_text("Marcus was slain by the shadow beast.", encoding="utf-8")
        (self.b2_dir / "02_Ch.md").write_text("Marcus commanded the vanguard. \"Advance!\" he shouted.", encoding="utf-8")

        report = scan_series_continuity(self.series_dir)
        self.assertTrue(any(v["character"] == "Marcus" for v in report["mortality_violations"]))

    def test_physical_trait_drift_detection(self):
        # Character Lyra has green eyes in Book 1, but blue eyes in Book 2
        (self.b1_dir / "01_Ch.md").write_text("Lyra had green eyes as she observed the starfield.", encoding="utf-8")
        (self.b2_dir / "01_Ch.md").write_text("Lyra had blue eyes as she entered the bridge.", encoding="utf-8")

        report = scan_series_continuity(self.series_dir)
        self.assertGreater(len(report["contradictions"]), 0)
        self.assertEqual(report["contradictions"][0]["character"], "Lyra")
        self.assertEqual(report["contradictions"][0]["trait"], "Eye Color")

    def test_series_html_generation(self):
        (self.b1_dir / "01_Ch.md").write_text("Renée had golden hair.", encoding="utf-8")
        report = scan_series_continuity(self.series_dir)
        out_html = self.series_dir / "series_report.html"
        generate_series_html_report(report, out_html)
    def test_cli_main_and_options(self):
        import io
        import json
        from unittest.mock import patch
        from lib.series_continuity import main

        (self.b1_dir / "01_Ch.md").write_text("Vance died on the battlefield protecting the gate.", encoding="utf-8")
        (self.b2_dir / "01_Ch.md").write_text("Vance had blue eyes and drew his blade once again.", encoding="utf-8")

        # JSON mode
        with patch("sys.argv", ["series_continuity.py", str(self.series_dir), "--json"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                main()
                data = json.loads(mock_stdout.getvalue())
                self.assertEqual(data["total_volumes"], 2)

        # Human readable and HTML
        html_out = self.series_dir / "cli_series.html"
        with patch("sys.argv", ["series_continuity.py", str(self.series_dir), "--html", str(html_out)]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                main()
                self.assertIn("Series Cross-Book Continuity Ledger", mock_stdout.getvalue())
                self.assertIn("Mortality Invariant Violations", mock_stdout.getvalue())
                self.assertTrue(html_out.is_file())

    def test_hair_and_custom_trait_contradictions(self):
        (self.b1_dir / "03_Ch.md").write_text("Rowan had black hair and bore a silver scar across his brow.", encoding="utf-8")
        (self.b2_dir / "03_Ch.md").write_text("Rowan had golden hair and bore a burning rune across his brow.", encoding="utf-8")

        report = scan_series_continuity(self.series_dir)
        traits = [c["trait"] for c in report["contradictions"]]
        self.assertIn("Hair Color", traits)

    def test_perfect_continuity_cli(self):
        import io
        from unittest.mock import patch
        from lib.series_continuity import main

        (self.b1_dir / "01_Ch.md").write_text("Rowan had dark hair.", encoding="utf-8")
        (self.b2_dir / "01_Ch.md").write_text("Rowan had dark hair.", encoding="utf-8")

        with patch("sys.argv", ["series_continuity.py", str(self.series_dir)]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                main()
                self.assertIn("Perfect series continuity", mock_stdout.getvalue())

    def test_cli_error_path(self):
        import io
        from unittest.mock import patch
        from lib.series_continuity import main

        # Error path
        with patch("sys.argv", ["series_continuity.py", "nonexistent_dir_123"]):
            with patch("sys.stderr", new_callable=io.StringIO):
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 1)


if __name__ == "__main__":
    unittest.main()

