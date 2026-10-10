#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Manuscript Revision Density & Churn Heatmap Engine
(scripts/lib/revision_heatmap.py & scripts/lib/revision_heatmap_template.py).
"""

import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.revision_heatmap import (
    ChapterRevisionStats,
    analyze_revision_churn,
    count_words,
    diff_line_counts,
    diff_word_counts,
    extract_dialogue_and_prose,
    extract_sub_scenes,
    generate_revision_heatmap_html,
    main,
    scan_manuscript_snapshots,
)


class TestRevisionHeatmapEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.ms_dir = Path(self.temp_dir.name) / "Manuscript"
        self.snapshot_dir = Path(self.temp_dir.name) / "Snapshots"
        self.draft01_dir = Path(self.temp_dir.name) / "Draft-01"
        self.draft02_dir = Path(self.temp_dir.name) / "Draft-02"

        self.ms_dir.mkdir(parents=True)
        self.snapshot_dir.mkdir(parents=True)
        self.draft01_dir.mkdir(parents=True)
        self.draft02_dir.mkdir(parents=True)

        (self.ms_dir / "Book-01" / "Draft-01").mkdir(parents=True)
        (self.snapshot_dir / "Book-01" / "Draft-01").mkdir(parents=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _write(self, base_dir: Path, rel_path: str, content: str) -> Path:
        target = base_dir / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return target

    def test_count_words(self):
        """Headers and @tags are excluded from word count."""
        text = """# Chapter 1
@pov: Kaelen
@location: Obsidian Citadel

The silver blade hummed in the dark.
@thread: main
"""
        wc = count_words(text)
        self.assertEqual(wc, 7)

    def test_extract_dialogue_and_prose(self):
        """Separates spoken quotes from narrative exposition."""
        text = """# Chapter 1
The captain stood at the helm. "Lower the sails!" he shouted.
“We cannot hold the line,” Lyra whispered.
"""
        d_text, p_text, d_wc, p_wc = extract_dialogue_and_prose(text)
        self.assertIn("Lower the sails", d_text)
        self.assertIn("We cannot hold the line", d_text)
        self.assertIn("captain stood at the helm", p_text)
        self.assertGreater(d_wc, 0)
        self.assertGreater(p_wc, 0)

    def test_diff_word_counts_identical(self):
        """Identical text produces zero word additions and deletions."""
        text = "The ancient tower watched over the silent valley."
        w_add, w_del, _d_add, _d_del, _p_add, _p_del = diff_word_counts(text, text)
        self.assertEqual(w_add, 0)
        self.assertEqual(w_del, 0)

    def test_diff_word_counts_additions_and_deletions(self):
        """Computes true word additions and deletions."""
        snap = "The ancient stone gates stood silent."
        curr = "The ancient iron gates stood silent in the mist."
        w_add, w_del, _, _, _, _ = diff_word_counts(curr, snap)
        self.assertGreater(w_add, 0)
        self.assertGreater(w_del, 0)

    def test_diff_word_counts_dialogue_breakdown(self):
        """Distinguishes dialogue rewrites from narrative changes."""
        snap = 'The guard nodded. "Halt there, traveler."'
        curr = 'The guard nodded. "Turn back immediately, stranger."'
        _w_add, _w_del, d_add, d_del, p_add, p_del = diff_word_counts(curr, snap)
        self.assertGreater(d_add, 0)
        self.assertGreater(d_del, 0)
        self.assertEqual(p_add, 0)
        self.assertEqual(p_del, 0)

    def test_diff_line_counts_identical(self):
        """Identical text produces zero line insertions and deletions."""
        text = "Line 1\nLine 2\nLine 3\n"
        ins, dels = diff_line_counts(text, text)
        self.assertEqual(ins, 0)
        self.assertEqual(dels, 0)

    def test_diff_line_counts_modifications(self):
        snap = "Line 1\nLine 2\nLine 3\n"
        curr = "Line 1\nLine 2 modified\nLine 3\nLine 4\n"
        ins, dels = diff_line_counts(curr, snap)
        self.assertEqual(ins, 2)
        self.assertEqual(dels, 1)

    def test_sub_scenes_extraction(self):
        """Extracts and calculates sub-scene breakdowns when dividers are present."""
        snap = "Scene one text.\n---\nScene two old text."
        curr = "Scene one text.\n---\nScene two rewritten brand new text."
        sub_scenes = extract_sub_scenes(curr, snap)
        self.assertEqual(len(sub_scenes), 2)
        self.assertEqual(sub_scenes[0]["name"], "Scene 1")
        self.assertEqual(sub_scenes[1]["name"], "Scene 2")
        self.assertGreater(sub_scenes[1]["churn_score"], 0)

    def test_scan_no_snapshots(self):
        """When no snapshot exists, chapter has has_snapshot=False."""
        self._write(
            self.ms_dir,
            "Book-01/Draft-01/01_Chapter.md",
            "# Chapter 1\nThe wind howled over the jagged stones.",
        )
        stats = scan_manuscript_snapshots(self.ms_dir, snapshot_dir=None)
        self.assertEqual(len(stats), 1)
        self.assertFalse(stats[0].has_snapshot)
        self.assertGreater(stats[0].word_count, 0)

    def test_scan_with_snapshot_identical(self):
        """Identical snapshot gives 0 insertions, 0 deletions, and 0 churn_score."""
        content = "# Chapter 1\nThe wind howled over the jagged stones."
        self._write(self.ms_dir, "Book-01/Draft-01/01_Chapter.md", content)
        self._write(self.snapshot_dir, "Book-01/Draft-01/01_Chapter.md", content)

        stats = scan_manuscript_snapshots(self.ms_dir, snapshot_dir=self.snapshot_dir)
        self.assertEqual(len(stats), 1)
        self.assertTrue(stats[0].has_snapshot)
        self.assertEqual(stats[0].insertions, 0)
        self.assertEqual(stats[0].deletions, 0)
        self.assertEqual(stats[0].churn_score, 0)

    def test_scan_two_directories_pair(self):
        """Supports explicit dual-directory comparison (Draft-02 vs Draft-01)."""
        self._write(self.draft01_dir, "01_Chapter.md", "Old chapter content here.")
        self._write(self.draft02_dir, "01_Chapter.md", "New chapter content rewritten completely.")

        stats = scan_manuscript_snapshots(self.draft02_dir, baseline_target=self.draft01_dir)
        self.assertEqual(len(stats), 1)
        self.assertTrue(stats[0].has_snapshot)
        self.assertGreater(stats[0].churn_score, 0)

    def test_analyze_churn_rev101_over_revised(self):
        """Chapter with extreme churn ratio is flagged with REV-101."""
        stats = [
            ChapterRevisionStats("ch1.md", "ch1.md", 500, 5, 5, 10, 0.02, True, "", [], 500),
            ChapterRevisionStats("ch2.md", "ch2.md", 500, 5, 5, 10, 0.02, True, "", [], 500),
            ChapterRevisionStats("ch3.md", "ch3.md", 500, 5, 5, 10, 0.02, True, "", [], 500),
            ChapterRevisionStats("ch4.md", "ch4.md", 500, 5, 5, 10, 0.02, True, "", [], 500),
            ChapterRevisionStats("ch5.md", "ch5.md", 500, 5, 5, 10, 0.02, True, "", [], 500),
            ChapterRevisionStats("ch6.md", "ch6.md", 500, 300, 200, 500, 1.00, True, "", [], 500),
        ]
        result = analyze_revision_churn(stats)
        findings = result["findings"]
        ids = [f["id"] for f in findings]
        self.assertIn("REV-101", ids)
        self.assertIn("REV-101", stats[5].flags)

    def test_analyze_churn_rev102_pristine(self):
        """Substantial chapter with snapshot and zero churn is flagged with REV-102."""
        stats = [
            ChapterRevisionStats("ch1.md", "ch1.md", 500, 20, 10, 30, 0.06, True, "", [], 500),
            ChapterRevisionStats("ch2.md", "ch2.md", 250, 0, 0, 0, 0.0, True, "", [], 250),
        ]
        result = analyze_revision_churn(stats)
        findings = result["findings"]
        ids = [f["id"] for f in findings]
        self.assertIn("REV-102", ids)
        self.assertIn("REV-102", stats[1].flags)

    def test_analyze_churn_rev103_heavy_cut(self):
        """Chapter with >40% baseline deletions is flagged with REV-103."""
        stats = [
            ChapterRevisionStats("ch1.md", "ch1.md", 450, 10, 360, 370, 0.46, True, "", [], 800),
        ]
        result = analyze_revision_churn(stats)
        findings = result["findings"]
        ids = [f["id"] for f in findings]
        self.assertIn("REV-103", ids)

    def test_analyze_churn_rev104_expansion(self):
        """Chapter with >50% additions over baseline is flagged with REV-104."""
        stats = [
            ChapterRevisionStats("ch1.md", "ch1.md", 1200, 600, 20, 620, 0.52, True, "", [], 600),
        ]
        result = analyze_revision_churn(stats)
        findings = result["findings"]
        ids = [f["id"] for f in findings]
        self.assertIn("REV-104", ids)

    def test_analyze_churn_rev105_dialogue_skew(self):
        """Chapter with >75% churn in dialogue is flagged with REV-105."""
        stats = [
            ChapterRevisionStats(
                chapter="ch1.md",
                rel_path="ch1.md",
                word_count=600,
                insertions=80,
                deletions=20,
                churn_score=100,
                churn_ratio=0.16,
                has_snapshot=True,
                baseline_word_count=600,
                dialogue_churn_score=85,
                prose_churn_score=15,
            ),
        ]
        result = analyze_revision_churn(stats)
        findings = result["findings"]
        ids = [f["id"] for f in findings]
        self.assertIn("REV-105", ids)

    def test_analyze_churn_rev106_front_loading(self):
        """When opening chapters have >2.5x churn of later chapters, REV-106 is raised."""
        stats = [
            ChapterRevisionStats("ch1.md", "ch1.md", 500, 150, 150, 300, 0.60, True, "", [], 500),
            ChapterRevisionStats("ch2.md", "ch2.md", 500, 140, 140, 280, 0.56, True, "", [], 500),
            ChapterRevisionStats("ch3.md", "ch3.md", 500, 130, 130, 260, 0.52, True, "", [], 500),
            ChapterRevisionStats("ch4.md", "ch4.md", 500, 10, 10, 20, 0.04, True, "", [], 500),
            ChapterRevisionStats("ch5.md", "ch5.md", 500, 10, 10, 20, 0.04, True, "", [], 500),
            ChapterRevisionStats("ch6.md", "ch6.md", 500, 10, 10, 20, 0.04, True, "", [], 500),
        ]
        result = analyze_revision_churn(stats)
        findings = result["findings"]
        ids = [f["id"] for f in findings]
        self.assertIn("REV-106", ids)

    def test_intent_tag_suppression(self):
        """Chapter with @intent: deliberate suppresses outlier warnings."""
        stats = [
            ChapterRevisionStats(
                chapter="ch1.md",
                rel_path="ch1.md",
                word_count=500,
                insertions=400,
                deletions=400,
                churn_score=800,
                churn_ratio=1.60,
                has_snapshot=True,
                baseline_word_count=500,
                intent="deliberate",
            ),
        ]
        result = analyze_revision_churn(stats)
        self.assertEqual(len(result["findings"]), 0)

    def test_constitution_rule_suppression(self):
        """Rules listed in suppressed_rules are not reported."""
        stats = [
            ChapterRevisionStats("ch1.md", "ch1.md", 500, 0, 0, 0, 0.0, True, "", [], 500),
        ]
        result = analyze_revision_churn(stats, suppressed_rules=["REV-102"])
        self.assertEqual(len(result["findings"]), 0)

    def test_generate_heatmap_html_and_csp(self):
        """generate_revision_heatmap_html creates an offline CSP-compliant interactive dashboard."""
        stats = [
            ChapterRevisionStats(
                chapter="01_Chapter.md",
                rel_path="01_Chapter.md",
                word_count=450,
                insertions=30,
                deletions=10,
                churn_score=40,
                churn_ratio=0.089,
                has_snapshot=True,
                baseline_word_count=430,
                dialogue_word_count=150,
                dialogue_churn_score=20,
                prose_word_count=300,
                prose_churn_score=20,
                sub_scenes=[
                    {"name": "Scene 1", "word_count": 200, "churn_score": 10, "churn_ratio": 0.05, "insertions": 10, "deletions": 0},
                    {"name": "Scene 2", "word_count": 250, "churn_score": 30, "churn_ratio": 0.12, "insertions": 20, "deletions": 10},
                ],
            )
        ]
        churn_data = analyze_revision_churn(stats)
        churn_data["chapters"] = stats
        churn_data["manuscript"] = "Test Manuscript"
        churn_data["baseline_source"] = "Draft-01"

        html_out = Path(self.temp_dir.name) / "studio_heatmap.html"
        generate_revision_heatmap_html(churn_data, html_out)
        self.assertTrue(html_out.is_file())

        content = html_out.read_text(encoding="utf-8")
        self.assertIn("Content-Security-Policy", content)
        self.assertIn("default-src 'none'", content)
        self.assertIn("Revision Heatmap Studio", content)
        self.assertIn("01_Chapter.md", content)
        self.assertIn("Scene 1", content)
        self.assertIn("Scene 2", content)
        self.assertIn("arcanumThemeLauncher", content)

    def test_cli_json_and_html(self):
        """CLI supports JSON and HTML exports."""
        self._write(self.ms_dir, "Book-01/Draft-01/01_Chapter.md", "# Chapter 1\nNew lines here.")
        self._write(self.snapshot_dir, "Book-01/Draft-01/01_Chapter.md", "# Chapter 1\nOld line.")

        # 1. JSON output
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            with patch("sys.argv", ["revision_heatmap.py", str(self.ms_dir), "--snapshot-dir", str(self.snapshot_dir), "--json"]):
                main()
                data = json.loads(mock_out.getvalue())
                self.assertIn("chapters", data)
                self.assertIn("dialogue_churn_percentage", data)

        # 2. HTML output
        out_html = self.ms_dir / "cli_studio.html"
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            with patch("sys.argv", ["revision_heatmap.py", str(self.ms_dir), "--snapshot-dir", str(self.snapshot_dir), "--html", str(out_html)]):
                main()
                self.assertTrue(out_html.is_file())

    def test_cli_dual_positional_drafts(self):
        """CLI supports positional baseline argument (arcanum revision-heatmap Draft-02 Draft-01)."""
        self._write(self.draft01_dir, "01_Chap.md", "First draft.")
        self._write(self.draft02_dir, "01_Chap.md", "Second draft expanded.")

        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            with patch("sys.argv", ["revision_heatmap.py", str(self.draft02_dir), str(self.draft01_dir)]):
                main()
                out = mock_out.getvalue()
                self.assertIn("Revision Heatmap Studio", out)
                self.assertIn("01_Chap.md", out)

    def test_scan_single_file(self):
        f = self._write(self.ms_dir, "SingleChap.md", "# Chapter Single\nLine 1\nLine 2\n")
        stats = scan_manuscript_snapshots(f)
        self.assertEqual(len(stats), 1)
        self.assertEqual(stats[0].chapter, "SingleChap.md")


if __name__ == "__main__":
    unittest.main()
