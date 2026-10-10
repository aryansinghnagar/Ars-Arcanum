#!/usr/bin/env python3
"""
Unit Test Suite for Ars Arcanum Manuscript Drafts, Redline Comparator, and Secure Backups
(tests/test_drafts_and_diff.py)
========================================================================================
Tests:
  1. Config engine (XDG persistence, backup-dest get/set/clear)
  2. Word tokenization and novelWriter metadata stripping
  3. Word-level diff sequence matcher (insertions, deletions, replacements)
  4. ManuscriptComparator on files and directory trees
  5. HTML Redline generator (accessible styles, WCAG contrast colors, chapter sidebar)
  6. JSON change metrics export
  7. ANSI terminal diff formatting
"""

import os
import sys
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# Add scripts/lib to Python path
TEST_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TEST_DIR.parent
SCRIPTS_LIB = PROJECT_ROOT / "scripts" / "lib"
sys.path.insert(0, str(SCRIPTS_LIB))

import config
import manuscript_diff


class TestConfigEngine(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="arcanum_test_config_")
        self.orig_xdg = os.environ.get("XDG_CONFIG_HOME")
        os.environ["XDG_CONFIG_HOME"] = self.tmp_dir

    def tearDown(self):
        if self.orig_xdg is not None:
            os.environ["XDG_CONFIG_HOME"] = self.orig_xdg
        else:
            os.environ.pop("XDG_CONFIG_HOME", None)
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_backup_dest_lifecycle(self):
        # Initial should be empty
        self.assertEqual(config.get_backup_dest(), "")

        # Set destination
        dest_path = str(Path(self.tmp_dir) / "secure_vault")
        self.assertTrue(config.set_backup_dest(dest_path))
        self.assertEqual(config.get_backup_dest(), str(Path(dest_path).resolve()))

        # Clear destination
        self.assertTrue(config.clear_backup_dest())
        self.assertEqual(config.get_backup_dest(), "")


class TestManuscriptDiffEngine(unittest.TestCase):
    def test_strip_nw_metadata(self):
        sample = (
            "@pov: Kaelen\n"
            "@char: Vance, Renée\n"
            "@location: The Citadel\n"
            "% This is a comment\n"
            "The rain fell silently against the ancient stone.\n"
            "@status: Draft\n"
            "He turned toward the gate.\n"
        )
        cleaned = manuscript_diff.strip_nw_metadata(sample)
        self.assertNotIn("@pov:", cleaned)
        self.assertNotIn("@char:", cleaned)
        self.assertNotIn("% This is a comment", cleaned)
        self.assertIn("The rain fell silently against the ancient stone.", cleaned)
        self.assertIn("He turned toward the gate.", cleaned)

    def test_word_diff_tokens(self):
        text_a = "The quick brown fox jumps over the lazy dog."
        text_b = "The swift brown fox leaps over a lazy sleeping dog."

        tokens_a = manuscript_diff.tokenize_words(text_a)
        tokens_b = manuscript_diff.tokenize_words(text_b)

        chunks, added, deleted = manuscript_diff.compute_word_diff(tokens_a, tokens_b)

        # "quick" cut, "swift" added; "jumps" cut, "leaps" added; "the" cut, "a" added; "sleeping" added
        self.assertGreater(added, 0)
        self.assertGreater(deleted, 0)

        # Check tag presence
        tags = [c["tag"] for c in chunks]
        self.assertIn("delete", tags)
        self.assertIn("insert", tags)
        self.assertIn("equal", tags)

    def test_single_file_comparator(self):
        tmp_dir = Path(tempfile.mkdtemp(prefix="arcanum_test_diff_"))
        try:
            file_a = tmp_dir / "draft1.md"
            file_b = tmp_dir / "draft2.md"

            file_a.write_text("# Chapter 1\n\nOld opening paragraph with five words.", encoding="utf-8")
            file_b.write_text("# Chapter 1\n\nNew opening paragraph with ten great and descriptive words.", encoding="utf-8")

            comp = manuscript_diff.ManuscriptComparator(file_a, file_b, "Draft-01", "Draft-02")
            summary = comp.compare()

            self.assertEqual(summary["chapter_count"], 1)
            self.assertGreater(summary["added_words"], 0)
            self.assertGreater(summary["deleted_words"], 0)
            self.assertGreater(summary["total_words_b"], summary["total_words_a"])
            self.assertTrue(0.0 <= summary["similarity_ratio"] <= 1.0)

            # Check JSON
            json_str = comp.to_json()
            data = json.loads(json_str)
            self.assertEqual(data["label_a"], "Draft-01")
            self.assertEqual(data["label_b"], "Draft-02")

            # Check HTML Redline
            html_out = comp.to_html()
            self.assertIn("<!DOCTYPE html>", html_out)
            self.assertIn("diff-ins", html_out)
            self.assertIn("diff-del", html_out)
            self.assertIn("Draft-01", html_out)
            self.assertIn("Draft-02", html_out)

            # Check Terminal ANSI
            ansi_out = comp.to_terminal_ansi()
            self.assertIn("Ars Arcanum Manuscript Revision Comparison", ansi_out)
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    def test_directory_tree_comparator(self):
        tmp_dir = Path(tempfile.mkdtemp(prefix="arcanum_test_tree_diff_"))
        try:
            dir_a = tmp_dir / "Draft-01"
            dir_b = tmp_dir / "Draft-02"

            (dir_a / "01_Act_I").mkdir(parents=True)
            (dir_a / "02_Act_II").mkdir(parents=True)
            (dir_b / "01_Act_I").mkdir(parents=True)
            (dir_b / "02_Act_II").mkdir(parents=True)

            (dir_a / "01_Act_I" / "01_Chapter_01.md").write_text("# Chapter 1\n\nInitial draft scene prose.", encoding="utf-8")
            (dir_a / "02_Act_II" / "01_Chapter_02.md").write_text("# Chapter 2\n\nSecond scene draft prose.", encoding="utf-8")

            (dir_b / "01_Act_I" / "01_Chapter_01.md").write_text("# Chapter 1\n\nInitial revised scene prose with extra details.", encoding="utf-8")
            (dir_b / "02_Act_II" / "01_Chapter_02.md").write_text("# Chapter 2\n\nSecond scene thoroughly expanded draft prose.", encoding="utf-8")

            comp = manuscript_diff.ManuscriptComparator(dir_a, dir_b, "Draft-01", "Draft-02")
            summary = comp.compare()

            self.assertEqual(summary["chapter_count"], 2)
            self.assertEqual(len(summary["chapters"]), 2)
            self.assertGreater(summary["total_words_b"], summary["total_words_a"])

            html_doc = comp.to_html()
            self.assertIn("Chapter 1", html_doc)
            self.assertIn("Chapter 2", html_doc)
            self.assertIn("Words Added", html_doc)
            self.assertIn("Words Cut", html_doc)
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    def test_open_in_libreoffice(self):
        tmp_dir = Path(tempfile.mkdtemp(prefix="arcanum_test_lo_"))
        try:
            file_a = tmp_dir / "draft1.md"
            file_b = tmp_dir / "draft2.md"
            file_a.write_text("# Scene A\nProse A", encoding="utf-8")
            file_b.write_text("# Scene B\nProse B", encoding="utf-8")

            comp = manuscript_diff.ManuscriptComparator(file_a, file_b)
            comp.compare()

            from unittest.mock import patch
            with patch("subprocess.run", side_effect=Exception("No pandoc")):
                res = comp.open_in_libreoffice()
                self.assertFalse(res)
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    def test_cli_interface(self):
        tmp_dir = Path(tempfile.mkdtemp(prefix="arcanum_test_cli_diff_"))
        try:
            file_a = tmp_dir / "draft1.md"
            file_b = tmp_dir / "draft2.md"
            file_a.write_text("# Scene 1\nOld scene prose.", encoding="utf-8")
            file_b.write_text("# Scene 1\nNew revised scene prose.", encoding="utf-8")

            import io
            from unittest.mock import patch

            # 1. json
            with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
                with patch("sys.argv", ["manuscript_diff.py", str(file_a), str(file_b), "--json"]):
                    manuscript_diff.main()
                    data = json.loads(mock_out.getvalue())
                    self.assertIn("added_words", data)

            # 2. html
            html_out = tmp_dir / "report.html"
            with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
                with patch("sys.argv", ["manuscript_diff.py", str(file_a), str(file_b), "--html", str(html_out)]):
                    manuscript_diff.main()
                    self.assertTrue(html_out.is_file())

            # 3. terminal default
            with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
                with patch("sys.argv", ["manuscript_diff.py", str(file_a), str(file_b)]):
                    manuscript_diff.main()
                    self.assertIn("Manuscript Revision Comparison", mock_out.getvalue())

            # 4. 1 arg error -> exit 2
            with patch("sys.stderr", new_callable=io.StringIO):
                with patch("sys.argv", ["manuscript_diff.py", str(file_a)]):
                    with self.assertRaises(SystemExit) as cm:
                        manuscript_diff.main()
                    self.assertEqual(cm.exception.code, 2)

            # 5. nonexistent file -> exit 2
            with patch("sys.stderr", new_callable=io.StringIO):
                with patch("sys.argv", ["manuscript_diff.py", str(file_a), str(tmp_dir / "nonexistent.md")]):
                    with self.assertRaises(SystemExit) as cm:
                        manuscript_diff.main()
                    self.assertEqual(cm.exception.code, 2)
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    def test_chapter_title_extraction_and_file_discovery(self):
        tmp_dir = Path(tempfile.mkdtemp(prefix="arcanum_test_title_"))
        try:
            f1 = tmp_dir / "01_h2_scene.md"
            f1.write_text("## Level 2 Scene Title\nBody text", encoding="utf-8")
            self.assertEqual(manuscript_diff.extract_chapter_title(f1, f1.read_text(encoding="utf-8")), "Level 2 Scene Title")

            f2 = tmp_dir / "02_no_heading.md"
            f2.write_text("Just plain body text without headers", encoding="utf-8")
            self.assertEqual(manuscript_diff.extract_chapter_title(f2, f2.read_text(encoding="utf-8")), "No Heading")

            # discover_draft_files on non-dir
            self.assertEqual(manuscript_diff.discover_draft_files(tmp_dir / "nonexistent"), [])
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    def test_open_in_libreoffice_success(self):
        tmp_dir = Path(tempfile.mkdtemp(prefix="arcanum_test_lo_success_"))
        try:
            file_a = tmp_dir / "draft1.md"
            file_b = tmp_dir / "draft2.md"
            file_a.write_text("# Scene A\nProse A", encoding="utf-8")
            file_b.write_text("# Scene B\nProse B", encoding="utf-8")

            comp = manuscript_diff.ManuscriptComparator(file_a, file_b)
            comp.compare()

            with patch("subprocess.run") as mock_run, patch("subprocess.Popen") as mock_popen:
                res = comp.open_in_libreoffice()
                self.assertTrue(res)
                self.assertEqual(mock_run.call_count, 2)
                mock_popen.assert_called_once()
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    def test_cli_3_args_and_libreoffice(self):
        tmp_dir = Path(tempfile.mkdtemp(prefix="arcanum_test_cli_3_"))
        try:
            ms_dir = tmp_dir / "MyNovel"
            d1 = ms_dir / "Draft-01"
            d2 = ms_dir / "Draft-02"
            d1.mkdir(parents=True)
            d2.mkdir(parents=True)
            (d1 / "01_Ch.md").write_text("# Ch 1\nDraft 1 content", encoding="utf-8")
            (d2 / "01_Ch.md").write_text("# Ch 1\nDraft 2 content", encoding="utf-8")

            # 1. 3 arguments: ms_dir, draft_b, draft_a
            import io
            with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
                with patch("sys.argv", ["manuscript_diff.py", str(ms_dir), "Draft-02", "Draft-01", "--json"]):
                    manuscript_diff.main()
                    data = json.loads(mock_out.getvalue())
                    self.assertEqual(data["chapter_count"], 1)

            # 2. --libreoffice flag in CLI
            with patch("manuscript_diff.ManuscriptComparator.open_in_libreoffice") as mock_lo:
                with patch("sys.argv", ["manuscript_diff.py", str(d1 / "01_Ch.md"), str(d2 / "01_Ch.md"), "--libreoffice"]):
                    manuscript_diff.main()
                    mock_lo.assert_called_once()
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    def test_moved_paragraph_detection(self):
        paras_a = [
            "This is the opening scene paragraph describing the quiet night sky with ancient glowing stars above the citadel.",
            "This is the middle paragraph that gets removed or changed in the second draft of the manuscript.",
            "This is the third paragraph concluding the scene with a long descriptive sentence about the ancient gates.",
        ]
        # In draft B, paragraph 0 and 2 are flipped
        paras_b = [
            "This is the third paragraph concluding the scene with a long descriptive sentence about the ancient gates.",
            "A completely new intermediate transition inserted in the middle.",
            "This is the opening scene paragraph describing the quiet night sky with ancient glowing stars above the citadel.",
        ]
        moved_a, moved_b, mapping = manuscript_diff.detect_moved_paragraphs(paras_a, paras_b, min_words=10)
        self.assertIn(0, moved_a)
        self.assertIn(2, moved_a)
        self.assertIn(0, moved_b)
        self.assertIn(2, moved_b)
        self.assertEqual(mapping[0], 2)
        self.assertEqual(mapping[2], 0)

    def test_scraps_vault_archiving(self):
        tmp_dir = Path(tempfile.mkdtemp(prefix="arcanum_test_scraps_"))
        try:
            ms_dir = tmp_dir / "ScrapsNovel"
            d1 = ms_dir / "Draft-01"
            d2 = ms_dir / "Draft-02"
            d1.mkdir(parents=True)
            d2.mkdir(parents=True)

            large_excised_prose = " ".join(["word"] * 60)
            (d1 / "01_Ch.md").write_text(f"# Chapter 1\n\n{large_excised_prose}\n\nRemaining prose.", encoding="utf-8")
            (d2 / "01_Ch.md").write_text("# Chapter 1\n\nRemaining prose.", encoding="utf-8")

            comp = manuscript_diff.ManuscriptComparator(
                d1, d2, "Draft-01", "Draft-02", ms_root=ms_dir, scrap_threshold=50, sync_scraps=True
            )
            summary = comp.compare()

            self.assertEqual(len(summary["scraps"]), 1)
            self.assertEqual(summary["scraps"][0]["word_count"], 60)

            scraps_dir = ms_dir / "Scraps"
            self.assertTrue(scraps_dir.is_dir())
            scraps_files = list(scraps_dir.glob("*.md"))
            self.assertEqual(len(scraps_files), 1)

            scrap_content = scraps_files[0].read_text(encoding="utf-8")
            self.assertIn("scrap_id:", scrap_content)
            self.assertIn("chapter: \"Chapter 1\"", scrap_content)
            self.assertIn("word_count: 60", scrap_content)
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    def test_smart_context_auto_discovery(self):
        tmp_dir = Path(tempfile.mkdtemp(prefix="arcanum_test_auto_disc_"))
        try:
            ms_dir = tmp_dir / "AutoNovel"
            d1 = ms_dir / "Draft-01"
            d2 = ms_dir / "Draft-02"
            d3 = ms_dir / "Draft-03"
            d1.mkdir(parents=True)
            d2.mkdir(parents=True)
            d3.mkdir(parents=True)

            (d1 / "01_Ch.md").write_text("# Ch 1\nDraft 1", encoding="utf-8")
            (d2 / "01_Ch.md").write_text("# Ch 1\nDraft 2", encoding="utf-8")
            (d3 / "01_Ch.md").write_text("# Ch 1\nDraft 3", encoding="utf-8")

            # Test resolving with 1 manuscript path
            pa, pb, la, lb, _ms = manuscript_diff.resolve_comparison_targets([str(ms_dir)])
            self.assertEqual(la, "Draft-02")
            self.assertEqual(lb, "Draft-03")
            self.assertEqual(pa, d2)
            self.assertEqual(pb, d3)

            # Test auto-discovery with 0 args via get_active_manuscript mock
            with patch("manuscript_diff.get_active_manuscript", return_value=ms_dir):
                _pa0, _pb0, la0, lb0, _ms0 = manuscript_diff.resolve_comparison_targets([])
                self.assertEqual(la0, "Draft-02")
                self.assertEqual(lb0, "Draft-03")
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    def test_advisory_telemetry_and_constitution(self):
        tmp_dir = Path(tempfile.mkdtemp(prefix="arcanum_test_adv_"))
        try:
            ms_dir = tmp_dir / "AdvisoryNovel"
            d1 = ms_dir / "Draft-01"
            d2 = ms_dir / "Draft-02"
            d1.mkdir(parents=True)
            d2.mkdir(parents=True)

            # Major cut (>30% and >500 words)
            big_text = " ".join(["story"] * 1000)
            (d1 / "01_Ch.md").write_text(f"# Ch 1\n{big_text}", encoding="utf-8")
            (d2 / "01_Ch.md").write_text("# Ch 1\nShort prose remaining.", encoding="utf-8")

            comp = manuscript_diff.ManuscriptComparator(d1, d2, "Draft-01", "Draft-02", ms_root=ms_dir)
            comp.compare()

            # Should trigger DIFF-301 massive cut observation
            self.assertTrue(any(a["rule_id"] == "DIFF-301" for a in comp.advisories))

            # Now test suppression with @intent: deliberate
            (d1 / "01_Ch.md").write_text(f"---\n@intent: deliberate\n---\n# Ch 1\n{big_text}", encoding="utf-8")
            comp2 = manuscript_diff.ManuscriptComparator(d1, d2, "Draft-01", "Draft-02", ms_root=ms_dir)
            comp2.compare()
            self.assertFalse(any(a["rule_id"] == "DIFF-301" for a in comp2.advisories))
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    def test_multi_tab_html_rendering(self):
        tmp_dir = Path(tempfile.mkdtemp(prefix="arcanum_test_html_tabs_"))
        try:
            f1 = tmp_dir / "d1.md"
            f2 = tmp_dir / "d2.md"
            f1.write_text("# Opening Scene\nHe said \"Hello there!\" and walked away.", encoding="utf-8")
            f2.write_text("# Opening Scene\nHe said \"Greetings, friend!\" and turned back.", encoding="utf-8")

            comp = manuscript_diff.ManuscriptComparator(f1, f2, "Draft-01", "Draft-02")
            html_out = comp.to_html()

            self.assertIn("tab-unified", html_out)
            self.assertIn("tab-split", html_out)
            self.assertIn("tab-scraps", html_out)
            self.assertIn("tab-churn", html_out)
            self.assertIn("Content-Security-Policy", html_out)
            self.assertIn("Editorial Studio", html_out)
            self.assertIn("data-dialogue=\"true\"", html_out)
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()

