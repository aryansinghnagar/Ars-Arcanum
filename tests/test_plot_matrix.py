#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Multi-Track Plot Grid & Subplot Matrix Engine
(scripts/lib/plot_matrix.py).
Validates:
- PLT-101: Plot and thread tag extraction (@plot:, @thread:, @arc:).
- Pacing gap & dormant thread alerts.
- Dangling subplot identification.
- Track density histogram.
- SVG/HTML multi-lane matrix generation with CSP compliance.
"""

import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.plot_matrix import (
    extract_chapter_plot_metadata,
    scan_manuscript_plot_matrix,
    generate_plot_html_report,
)


class TestPlotMatrixEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.target_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    # ------------------------------------------------------------------ #
    # Original 4 tests                                                     #
    # ------------------------------------------------------------------ #

    def test_extract_chapter_plot_tags(self):
        """@plot:, @thread:, @arc: tags must all be extracted correctly."""
        ch = self.target_dir / "01_Ch1.md"
        ch.write_text(
            "# Chapter 1\n@pov: Vance\n@plot: The Heist\n@thread: Romance\n@arc: Vance Redemption\n\nVance climbed the wall.\n",
            encoding="utf-8",
        )
        meta = extract_chapter_plot_metadata(ch, 1)
        self.assertEqual(meta["pov"], "Vance")
        self.assertIn("The Heist", meta["plots"])
        self.assertIn("Romance", meta["threads"])
        self.assertIn("Vance Redemption", meta["arcs"])
        self.assertEqual(meta["track_count"], 3)

    def test_extract_comma_separated_tags(self):
        """Comma-separated @plot: and @thread: values must each be split into separate tracks."""
        ch = self.target_dir / "02_Ch2.md"
        ch.write_text(
            "# Chapter 2\n@plot: The Heist, The Betrayal\n@thread: Subplot A, Subplot B\n\nText.\n",
            encoding="utf-8",
        )
        meta = extract_chapter_plot_metadata(ch, 2)
        self.assertIn("The Heist", meta["plots"])
        self.assertIn("The Betrayal", meta["plots"])
        self.assertIn("Subplot A", meta["threads"])
        self.assertIn("Subplot B", meta["threads"])
        self.assertEqual(meta["track_count"], 4)

    def test_dormant_and_dangling_thread_detection(self):
        """Gap Thread absent for 5 chapters must appear in abandoned_tracks."""
        (self.target_dir / "01_Ch1.md").write_text("@plot: Main Heist\n@plot: Forgotten Clue\n@plot: Gap Thread\nText.", encoding="utf-8")
        (self.target_dir / "02_Ch2.md").write_text("@plot: Main Heist\nText.", encoding="utf-8")
        (self.target_dir / "03_Ch3.md").write_text("@plot: Main Heist\nText.", encoding="utf-8")
        (self.target_dir / "04_Ch4.md").write_text("@plot: Main Heist\nText.", encoding="utf-8")
        (self.target_dir / "05_Ch5.md").write_text("@plot: Main Heist\nText.", encoding="utf-8")
        (self.target_dir / "06_Ch6.md").write_text("@plot: Main Heist\n@plot: Gap Thread\nText.", encoding="utf-8")

        report = scan_manuscript_plot_matrix(self.target_dir, max_gap_threshold=4)
        self.assertEqual(report["total_chapters"], 6)
        self.assertIn("Main Heist", report["tracks"])
        self.assertEqual(report["tracks"]["Main Heist"]["occurrences"], 6)
        self.assertGreater(len(report["abandoned_tracks"]), 0)
        abandoned_names = [a["track"] for a in report["abandoned_tracks"]]
        self.assertIn("Gap Thread", abandoned_names)

    def test_plot_matrix_html_generation(self):
        """generate_plot_html_report must create an HTML file with the report title."""
        (self.target_dir / "01_Ch1.md").write_text("@plot: Odyssey\nText.", encoding="utf-8")
        report = scan_manuscript_plot_matrix(self.target_dir)
        out_html = self.target_dir / "plot_report.html"
        generate_plot_html_report(report, out_html)
        self.assertTrue(out_html.is_file())
        self.assertIn("Multi-Track Plot Grid", out_html.read_text(encoding="utf-8"))

    # ------------------------------------------------------------------ #
    # New tests 5–12                                                       #
    # ------------------------------------------------------------------ #

    def test_extract_arc_tag_only(self):
        """@arc: tag alone must populate the arcs list and be included in all_tracks."""
        ch = self.target_dir / "arc_only.md"
        ch.write_text("@arc: HeroRedemption\nText.", encoding="utf-8")
        meta = extract_chapter_plot_metadata(ch, 1)
        self.assertIn("HeroRedemption", meta["arcs"])
        self.assertIn("HeroRedemption", meta["all_tracks"])

    def test_no_tags_chapter_zero_count(self):
        """A chapter with no @plot:, @thread:, or @arc: tags must have track_count == 0."""
        ch = self.target_dir / "no_tags.md"
        ch.write_text("# Chapter with no tags\nJust prose here.", encoding="utf-8")
        meta = extract_chapter_plot_metadata(ch, 1)
        self.assertEqual(meta["track_count"], 0)
        self.assertEqual(meta["all_tracks"], [])

    def test_scan_single_file_total_chapters(self):
        """scan_manuscript_plot_matrix on a dir with one file must return total_chapters == 1."""
        (self.target_dir / "01_only.md").write_text("@plot: Solo\nText.", encoding="utf-8")
        report = scan_manuscript_plot_matrix(self.target_dir)
        self.assertEqual(report["total_chapters"], 1)

    def test_total_unique_tracks_count(self):
        """3 unique tracks across 3 chapters must yield total_tracks == 3."""
        (self.target_dir / "01.md").write_text("@plot: Track-A\nText.", encoding="utf-8")
        (self.target_dir / "02.md").write_text("@plot: Track-B\nText.", encoding="utf-8")
        (self.target_dir / "03.md").write_text("@plot: Track-C\nText.", encoding="utf-8")
        report = scan_manuscript_plot_matrix(self.target_dir)
        self.assertEqual(report["total_tracks"], 3)

    def test_density_histogram_present(self):
        """scan result must contain a density_histogram dict."""
        (self.target_dir / "01.md").write_text("@plot: Main\nText.", encoding="utf-8")
        report = scan_manuscript_plot_matrix(self.target_dir)
        self.assertIn("density_histogram", report)
        self.assertIsInstance(report["density_histogram"], dict)

    def test_track_occurrences_counted(self):
        """A track appearing in 3 of 3 chapters must have occurrences == 3."""
        for i in range(1, 4):
            (self.target_dir / f"0{i}_Ch.md").write_text("@plot: Recurring\nText.", encoding="utf-8")
        report = scan_manuscript_plot_matrix(self.target_dir)
        self.assertEqual(report["tracks"]["Recurring"]["occurrences"], 3)

    def test_html_report_csp_compliant(self):
        """generate_plot_html_report output must contain Content-Security-Policy meta tag."""
        (self.target_dir / "01.md").write_text("@plot: Main\nText.", encoding="utf-8")
        report = scan_manuscript_plot_matrix(self.target_dir)
        out_html = self.target_dir / "csp_plot.html"
        generate_plot_html_report(report, out_html)
        content = out_html.read_text(encoding="utf-8")
        self.assertIn(
            "default-src",
            content,
            msg="Plot matrix HTML is missing Content-Security-Policy meta tag",
        )

    def test_extract_chapter_yaml_frontmatter(self):
        ch = self.target_dir / "fm_chapter.md"
        ch.write_text("""# The Heist Begins
@pov: Elena
@plot: Infiltration
@thread: Betrayal
@arc: Elena Arc

Prose here.
""", encoding="utf-8")
        meta = extract_chapter_plot_metadata(ch, 1)
        self.assertEqual(meta["pov"], "Elena")
        self.assertIn("Infiltration", meta["plots"])
        self.assertIn("Betrayal", meta["threads"])
        self.assertIn("Elena Arc", meta["arcs"])

    def test_cli_main_and_matrix_render(self):
        import io
        import json
        from unittest.mock import patch
        from lib.plot_matrix import main

        (self.target_dir / "01_Ch1.md").write_text("@plot: Track1\nText.", encoding="utf-8")
        (self.target_dir / "02_Ch2.md").write_text("@plot: Track1\nText.", encoding="utf-8")
        (self.target_dir / "03_Ch3.md").write_text("@plot: Track2\nText.", encoding="utf-8")

        # JSON mode
        with patch("sys.argv", ["plot_matrix.py", str(self.target_dir), "--json"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                main()
                data = json.loads(mock_stdout.getvalue())
                self.assertEqual(data["total_chapters"], 3)

        # Matrix and HTML
        html_out = self.target_dir / "cli_plot.html"
        with patch("sys.argv", ["plot_matrix.py", str(self.target_dir), "--matrix", "--html", str(html_out)]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                main()
                self.assertIn("Multi-Track Plot Grid", mock_stdout.getvalue())
                self.assertIn("Narrative Track ASCII Grid", mock_stdout.getvalue())
                self.assertTrue(html_out.is_file())

        # Error path
        with patch("sys.argv", ["plot_matrix.py", "nonexistent_dir_123"]):
            with patch("sys.stderr", new_callable=io.StringIO):
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 1)


if __name__ == "__main__":
    unittest.main()

