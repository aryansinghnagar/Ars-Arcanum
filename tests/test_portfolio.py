#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Portfolio Dashboard (scripts/lib/portfolio.py).
Validates:
- OPS-103: Multi-manuscript scanning, wordcount aggregation, editorial stage tracking,
  progress bar calculations, export detection, and standalone HTML dashboard generation.
"""

import io
import json
import tempfile
import unittest
from pathlib import Path
import sys
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.portfolio import (
    analyze_manuscript_project,
    generate_portfolio_html,
    scan_portfolio,
    main,
)


class TestPortfolioDashboard(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root_dir = Path(self.temp_dir.name)

        # Manuscript 1: Active In-Progress
        self.ms1 = self.root_dir / "Manuscript_A"
        self.ms1.mkdir()
        (self.ms1 / "manuscript.yaml").write_text('title: "Book Alpha"\nauthor: "Writer One"\ntarget_words: 50000\n', encoding="utf-8")
        (self.ms1 / "01_Act_I").mkdir()
        (self.ms1 / "01_Act_I" / "01_Ch1.md").write_text("# Ch 1\n\nWord " * 500, encoding="utf-8")

        # Manuscript 2: Completed with Exports
        self.ms2 = self.root_dir / "Manuscript_B"
        self.ms2.mkdir()
        (self.ms2 / "manuscript.yaml").write_text('title: "Book Beta"\nauthor: "Writer Two"\ntarget_words: 1000\n', encoding="utf-8")
        (self.ms2 / "01_Act_I").mkdir()
        (self.ms2 / "01_Act_I" / "01_Ch1.md").write_text("# Ch 1\n\nWord " * 1200, encoding="utf-8")
        exports_dir = self.ms2 / "Exports"
        exports_dir.mkdir()
        (exports_dir / "Book_Beta.pdf").write_bytes(b"%PDF-1.4 mock")

    def tearDown(self):
        self.temp_dir.cleanup()

    # ------------------------------------------------------------------ #
    # 1. Single Manuscript Analysis                                      #
    # ------------------------------------------------------------------ #
    def test_analyze_manuscript_project(self):
        """analyze_manuscript_project must extract title, author, word count, and progress."""
        data = analyze_manuscript_project(self.ms1)
        self.assertEqual(data["title"], "Book Alpha")
        self.assertEqual(data["author"], "Writer One")
        self.assertGreater(data["word_count"], 400)
        self.assertGreater(data["progress_pct"], 0.5)

    # ------------------------------------------------------------------ #
    # 2. Portfolio Scan and HTML Output                                  #
    # ------------------------------------------------------------------ #
    def test_scan_portfolio_and_html(self):
        """scan_portfolio and generate_portfolio_html must produce valid HTML dashboard."""
        report = scan_portfolio(self.root_dir)
        self.assertEqual(report["total_projects"], 2)
        self.assertGreater(report["total_words"], 1500)

        out_html = self.root_dir / "portfolio.html"
        generate_portfolio_html(report, out_html)
        self.assertTrue(out_html.is_file())
        self.assertIn("Author Portfolio & Catalog Dashboard", out_html.read_text(encoding="utf-8"))

    # ------------------------------------------------------------------ #
    # 3. Direct Manuscript Directory Scan                                #
    # ------------------------------------------------------------------ #
    def test_scan_portfolio_direct_manuscript_dir(self):
        """Passing manuscript directory directly should recognize it as 1 project."""
        report = scan_portfolio(self.ms1)
        self.assertEqual(report["total_projects"], 1)
        self.assertEqual(report["projects"][0]["title"], "Book Alpha")

    # ------------------------------------------------------------------ #
    # 4. Content Security Policy Compliance                              #
    # ------------------------------------------------------------------ #
    def test_portfolio_html_csp_compliance(self):
        """Portfolio dashboard HTML must declare Content-Security-Policy."""
        report = scan_portfolio(self.root_dir)
        out_html = self.root_dir / "csp_portfolio.html"
        generate_portfolio_html(report, out_html)
        content = out_html.read_text(encoding="utf-8")
        self.assertIn("default-src 'none'", content)
        self.assertIn("style-src 'unsafe-inline'", content)

    # ------------------------------------------------------------------ #
    # 5. Editorial Stage: Drafting Detection                             #
    # ------------------------------------------------------------------ #
    def test_stage_drafting_detection(self):
        """Manuscript under target words should be in Drafting stage."""
        data = analyze_manuscript_project(self.ms1)
        self.assertIn("Drafting", data["stage"])

    # ------------------------------------------------------------------ #
    # 6. Editorial Stage: Publication-Ready Detection                    #
    # ------------------------------------------------------------------ #
    def test_stage_publication_ready_detection(self):
        """Manuscript meeting target words with PDF exports should be Publication-Ready."""
        data = analyze_manuscript_project(self.ms2)
        self.assertEqual(data["stage"], "Publication-Ready")
        self.assertTrue(data["has_exports"])

    # ------------------------------------------------------------------ #
    # 7. Editorial Stage: Scaffolding Detection                          #
    # ------------------------------------------------------------------ #
    def test_stage_scaffolding_detection(self):
        """Empty manuscript with 0 words should be classified as Scaffolding."""
        ms3 = self.root_dir / "Manuscript_C"
        ms3.mkdir()
        data = analyze_manuscript_project(ms3)
        self.assertEqual(data["stage"], "Scaffolding")
        self.assertEqual(data["word_count"], 0)

    # ------------------------------------------------------------------ #
    # 8. Volume Directory Discovery                                      #
    # ------------------------------------------------------------------ #
    def test_volume_directory_discovery(self):
        """Multi-volume manuscript with Book-01 and Book-02 should discover both."""
        (self.ms1 / "Book-01").mkdir()
        (self.ms1 / "Book-02").mkdir()
        data = analyze_manuscript_project(self.ms1)
        self.assertEqual(data["volume_count"], 2)
        self.assertIn("Book-01", data["volumes"])
        self.assertIn("Book-02", data["volumes"])

    # ------------------------------------------------------------------ #
    # 9. Total Target Word Count Aggregation                             #
    # ------------------------------------------------------------------ #
    def test_total_target_words_aggregation(self):
        """scan_portfolio must aggregate total_target_words across all projects."""
        report = scan_portfolio(self.root_dir)
        self.assertIn("total_target_words", report)
        self.assertEqual(report["total_target_words"], 50000 + 1000)

    # ------------------------------------------------------------------ #
    # 10. Overall Catalog Progress Percentage                            #
    # ------------------------------------------------------------------ #
    def test_overall_catalog_progress(self):
        """scan_portfolio must calculate overall_progress_pct."""
        report = scan_portfolio(self.root_dir)
        self.assertIn("overall_progress_pct", report)
        self.assertGreater(report["overall_progress_pct"], 0.0)

    # ------------------------------------------------------------------ #
    # 11. Empty Directory Portfolio Scan                                 #
    # ------------------------------------------------------------------ #
    def test_empty_directory_portfolio_scan(self):
        """scan_portfolio on empty directory should return 0 projects cleanly."""
        empty_dir = self.root_dir / "Empty_Workspace"
        empty_dir.mkdir()
        report = scan_portfolio(empty_dir)
        self.assertEqual(report["total_projects"], 0)
        self.assertEqual(report["total_words"], 0)

    # ------------------------------------------------------------------ #
    # 12. Project Card Titles in Generated HTML                          #
    # ------------------------------------------------------------------ #
    def test_html_project_card_titles(self):
        """generate_portfolio_html must include title names of all projects."""
        report = scan_portfolio(self.root_dir)
        out_html = self.root_dir / "cards_portfolio.html"
        generate_portfolio_html(report, out_html)
        content = out_html.read_text(encoding="utf-8")
        self.assertIn("Book Alpha", content)
        self.assertIn("Book Beta", content)

    # ------------------------------------------------------------------ #
    # 13. CLI Main Execution                                             #
    # ------------------------------------------------------------------ #
    def test_cli_main_stdout_json_html(self):
        # Human-readable stdout
        out_html = self.root_dir / "cli_port.html"
        with patch.object(sys, "argv", ["portfolio.py", str(self.root_dir), "--html", str(out_html)]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                main()
                self.assertIn("Ars Arcanum Author Portfolio Dashboard", mock_stdout.getvalue())
                self.assertTrue(out_html.is_file())

        # JSON output
        with patch.object(sys, "argv", ["portfolio.py", str(self.root_dir), "--json"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                main()
                data = json.loads(mock_stdout.getvalue())
                self.assertEqual(data["total_projects"], 2)

    def test_scan_portfolio_with_scope(self):
        from lib.scope_models import EngineScope
        scope = EngineScope(manuscript=str(self.ms1))
        report = scan_portfolio(scope=scope)
        self.assertEqual(report["total_projects"], 1)
        self.assertEqual(report["projects"][0]["title"], "Book Alpha")

    def test_analyze_manuscript_multiple_drafts_isolation(self):
        """Word count must only reflect the latest active draft, not older drafts."""
        ms_multi = self.root_dir / "MultiDraft_MS"
        ms_multi.mkdir()
        (ms_multi / "manuscript.yaml").write_text('title: "Multi Book"\nauthor: "Writer Multi"\ntarget_words: 50000\n', encoding="utf-8")
        (ms_multi / "Book-01" / "Draft-01").mkdir(parents=True)
        (ms_multi / "Book-01" / "Draft-02").mkdir(parents=True)
        (ms_multi / "Book-01" / "Draft-01" / "01_Ch1.md").write_text("# Ch 1\n\n" + "OldWord " * 500, encoding="utf-8")
        (ms_multi / "Book-01" / "Draft-02" / "01_Ch1.md").write_text("# Ch 1\n\n" + "NewWord " * 600, encoding="utf-8")

        data = analyze_manuscript_project(ms_multi)
        self.assertEqual(data["chapter_count"], 1)
        self.assertEqual(data["word_count"], 602)

    def test_analyze_manuscript_nested_01_manuscript(self):
        """Manuscripts with 01-Manuscript subfolder must be analyzed properly without multi-draft overcounting."""
        ms_nested = self.root_dir / "Nested_MS"
        ms_nested.mkdir()
        (ms_nested / "manuscript.yaml").write_text('title: "Nested Book"\nauthor: "Writer Nested"\n', encoding="utf-8")
        (ms_nested / "01-Manuscript" / "Book-01" / "Draft-01").mkdir(parents=True)
        (ms_nested / "01-Manuscript" / "Book-01" / "Draft-02").mkdir(parents=True)
        (ms_nested / "01-Manuscript" / "Book-01" / "Draft-01" / "01_Ch1.md").write_text("# Ch 1\n\n" + "Draft1 " * 400, encoding="utf-8")
        (ms_nested / "01-Manuscript" / "Book-01" / "Draft-02" / "01_Ch1.md").write_text("# Ch 1\n\n" + "Draft2 " * 750, encoding="utf-8")

        data = analyze_manuscript_project(ms_nested)
        self.assertEqual(data["chapter_count"], 1)
        self.assertEqual(data["word_count"], 752)

    def test_analyze_manuscript_explicit_active_draft(self):
        """When manuscript.yaml specifies active_draft, portfolio metrics honor that selection over latest."""
        ms_draft = self.root_dir / "ExplicitDraft_MS"
        ms_draft.mkdir()
        (ms_draft / "manuscript.yaml").write_text('title: "Pinned Draft Book"\nactive_draft: "Draft-01"\n', encoding="utf-8")
        (ms_draft / "Book-01" / "Draft-01").mkdir(parents=True)
        (ms_draft / "Book-01" / "Draft-02").mkdir(parents=True)
        (ms_draft / "Book-01" / "Draft-01" / "01_Ch1.md").write_text("# Ch 1\n\n" + "PinnedWord " * 300, encoding="utf-8")
        (ms_draft / "Book-01" / "Draft-02" / "01_Ch1.md").write_text("# Ch 1\n\n" + "NewerWord " * 800, encoding="utf-8")

        data = analyze_manuscript_project(ms_draft)
        self.assertEqual(data["chapter_count"], 1)
        self.assertEqual(data["word_count"], 302)


if __name__ == "__main__":
    unittest.main()

