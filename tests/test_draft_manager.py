#!/usr/bin/env python3
"""
Tests for Ars Arcanum Draft Management & Versioning Engine (tests/test_draft_manager.py)
"""

from __future__ import annotations

import io
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

TEST_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TEST_DIR.parent
SCRIPTS_LIB = PROJECT_ROOT / "scripts" / "lib"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
sys.path.insert(0, str(SCRIPTS_LIB))

from lib.draft_manager import (
    DraftManager,
    activate_draft,
    fork_draft,
    list_drafts,
    lock_draft,
    main,
    set_milestone,
    unlock_draft,
)
from lib.project_scaffold import scaffold_manuscript, scaffold_universe, scaffold_world



class TestDraftManager(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp(prefix="arcanum_test_drafts_"))
        self.univ_base = self.tmp_dir / "Universes"
        self.univ_base.mkdir(parents=True, exist_ok=True)

        scaffold_universe("Chronicles", base_dir=self.univ_base)
        scaffold_world("Terra", universe_name="Chronicles", base_dir=self.univ_base)
        res = scaffold_manuscript(
            "Starfall",
            universe="Chronicles",
            world="Terra",
            base_dir=self.univ_base,
            target_words=90000,
        )
        self.ms_dir = Path(res["path"])

    def tearDown(self):
        if self.tmp_dir.exists():
            shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_list_initial_draft(self):
        drafts = list_drafts(self.ms_dir)
        self.assertEqual(len(drafts), 1)
        self.assertEqual(drafts[0]["name"], "Draft-01")
        self.assertTrue(drafts[0]["is_active"])
        self.assertFalse(drafts[0]["locked"])

    def test_fork_draft_basic(self):
        res = fork_draft(
            self.ms_dir,
            new_draft_name="Draft-02",
            source_draft_name="Draft-01",
            milestone="Beta",
            notes="Second developmental draft",
        )
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["draft"], "Draft-02")
        self.assertEqual(res["milestone"], "Beta")

        d2_dir = Path(res["path"])
        self.assertTrue(d2_dir.is_dir())

        mgr = DraftManager(self.ms_dir)
        drafts = mgr.list_drafts()
        self.assertEqual(len(drafts), 2)

        d2 = mgr.get_draft("Draft-02")
        self.assertIsNotNone(d2)
        if d2:
            self.assertEqual(d2.parent_draft, "Draft-01")
            self.assertEqual(d2.milestone, "Beta")
            self.assertEqual(d2.notes, "Second developmental draft")
            self.assertTrue(d2.is_active)

    def test_fork_draft_auto_increment(self):
        res = fork_draft(self.ms_dir)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["draft"], "Draft-02")

        res3 = fork_draft(self.ms_dir)
        self.assertEqual(res3["status"], "success")
        self.assertEqual(res3["draft"], "Draft-03")

        drafts = list_drafts(self.ms_dir)
        self.assertEqual(len(drafts), 3)

    def test_fork_draft_with_chapter_scoping(self):
        # Create multiple chapters in Draft-01
        mgr = DraftManager(self.ms_dir)
        d1 = mgr.get_draft("Draft-01")
        self.assertIsNotNone(d1)
        d1_path = Path(d1.path)  # type: ignore[union-attr]

        for child in list(d1_path.iterdir()):
            if child.is_dir():
                shutil.rmtree(child)
            elif child.is_file():
                child.unlink()

        (d1_path / "01_Chapter_01.md").write_text("# Chapter 1\nProse 1", encoding="utf-8")
        (d1_path / "02_Chapter_02.md").write_text("# Chapter 2\nProse 2", encoding="utf-8")
        (d1_path / "03_Chapter_03.md").write_text("# Chapter 3\nProse 3", encoding="utf-8")
        (d1_path / "04_Chapter_04.md").write_text("# Chapter 4\nProse 4", encoding="utf-8")

        # Fork including only chapters 1 and 3
        res = fork_draft(
            self.ms_dir,
            new_draft_name="Draft-02-slice",
            source_draft_name="Draft-01",
            chapters="1,3",
        )
        self.assertEqual(res["chapters_copied"], 2)

        d2_slice = mgr.get_draft("Draft-02-slice")
        self.assertIsNotNone(d2_slice)
        if d2_slice:
            ch_names = [ch["filename"] for ch in d2_slice.chapters]
            self.assertIn("01_Chapter_01.md", ch_names)
            self.assertIn("03_Chapter_03.md", ch_names)
            self.assertNotIn("02_Chapter_02.md", ch_names)

        # Fork with exclusion
        res_ex = fork_draft(
            self.ms_dir,
            new_draft_name="Draft-03-ex",
            source_draft_name="Draft-01",
            exclude="2,4",
        )
        self.assertEqual(res_ex["chapters_copied"], 2)

    def test_activate_draft(self):
        fork_draft(self.ms_dir, new_draft_name="Draft-02", activate=False)
        mgr = DraftManager(self.ms_dir)
        d2 = mgr.get_draft("Draft-02")
        self.assertIsNotNone(d2)
        self.assertFalse(d2.is_active)  # type: ignore[union-attr]

        res = activate_draft(self.ms_dir, "Draft-02")
        self.assertEqual(res["status"], "success")

        # Re-check active state
        d2_after = mgr.get_draft("Draft-02")
        self.assertIsNotNone(d2_after)
        self.assertTrue(d2_after.is_active)  # type: ignore[union-attr]

    def test_lock_and_unlock_draft(self):
        res_lock = lock_draft(self.ms_dir, "Draft-01", notes="Freezing v1")
        self.assertEqual(res_lock["status"], "success")
        self.assertTrue(res_lock["locked"])

        mgr = DraftManager(self.ms_dir)
        d1 = mgr.get_draft("Draft-01")
        self.assertIsNotNone(d1)
        self.assertTrue(d1.locked)  # type: ignore[union-attr]
        self.assertEqual(d1.notes, "Freezing v1")  # type: ignore[union-attr]

        res_unlock = unlock_draft(self.ms_dir, "Draft-01")
        self.assertEqual(res_unlock["status"], "success")
        self.assertFalse(res_unlock["locked"])

        d1_unlocked = mgr.get_draft("Draft-01")
        self.assertIsNotNone(d1_unlocked)
        self.assertFalse(d1_unlocked.locked)  # type: ignore[union-attr]

    def test_set_milestone(self):
        res = set_milestone(self.ms_dir, "Draft-01", "Line-Edit")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["milestone"], "Line-Edit")

        mgr = DraftManager(self.ms_dir)
        d1 = mgr.get_draft("Draft-01")
        self.assertIsNotNone(d1)
        self.assertEqual(d1.milestone, "Line-Edit")  # type: ignore[union-attr]

    def test_lineage_graph_and_status(self):
        fork_draft(self.ms_dir, new_draft_name="Draft-02", source_draft_name="Draft-01")
        fork_draft(self.ms_dir, new_draft_name="Draft-02-alt", source_draft_name="Draft-02")

        mgr = DraftManager(self.ms_dir)
        lineage = mgr.get_lineage_graph()
        self.assertTrue(len(lineage) >= 1)
        self.assertEqual(lineage[0]["name"], "Draft-01")
        self.assertTrue(len(lineage[0]["children"]) >= 1)

        stat = mgr.get_draft_status("Draft-02-alt")
        self.assertEqual(stat["parent_draft"], "Draft-02")

    def test_ansi_tree_rendering(self):
        mgr = DraftManager(self.ms_dir)
        tree_str = mgr.render_ansi_tree()
        self.assertIn("Draft Lineage Tree", tree_str)
        self.assertIn("Draft-01", tree_str)
        self.assertIn("ACTIVE", tree_str)

    def test_html_visual_dashboard_generation(self):
        mgr = DraftManager(self.ms_dir)
        out_html = self.ms_dir / "drafts_dashboard.html"
        html_str = mgr.render_html(output_path=out_html)

        self.assertTrue(out_html.is_file())
        self.assertIn("<!DOCTYPE html>", html_str)
        self.assertIn("Content-Security-Policy", html_str)
        self.assertIn("Draft-01", html_str)
        self.assertIn("ACTIVE WORKSTREAM", html_str)
        self.assertIn("Version Lineage DAG", html_str)

    def test_cli_draft_manager_suite(self):
        # 1. list
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            rc = main([str(self.ms_dir), "list"])
            self.assertEqual(rc, 0)
            self.assertIn("Draft-01", mock_out.getvalue())

        # 2. tree
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            rc = main([str(self.ms_dir), "tree"])
            self.assertEqual(rc, 0)
            self.assertIn("Draft-01", mock_out.getvalue())

        # 3. fork
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            rc = main([str(self.ms_dir), "fork", "Draft-02", "--tag", "Beta"])
            self.assertEqual(rc, 0)
            self.assertIn("Created new draft: 'Draft-02'", mock_out.getvalue())

        # 4. lock
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            rc = main([str(self.ms_dir), "lock", "Draft-01"])
            self.assertEqual(rc, 0)
            self.assertIn("LOCKED", mock_out.getvalue())

        # 5. unlock
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            rc = main([str(self.ms_dir), "unlock", "Draft-01"])
            self.assertEqual(rc, 0)
            self.assertIn("UNLOCKED", mock_out.getvalue())

        # 6. switch
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            rc = main([str(self.ms_dir), "switch", "Draft-01"])
            self.assertEqual(rc, 0)
            self.assertIn("Active draft switched", mock_out.getvalue())

        # 7. tag
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            rc = main([str(self.ms_dir), "tag", "Draft-02", "Proof-Final"])
            self.assertEqual(rc, 0)
            self.assertIn("milestone set to: Proof-Final", mock_out.getvalue())

        # 8. status
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            rc = main([str(self.ms_dir), "status", "Draft-02"])
            self.assertEqual(rc, 0)
            self.assertIn("Draft Status: 'Draft-02'", mock_out.getvalue())

        # 9. html export
        html_export = self.tmp_dir / "exported_drafts.html"
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            rc = main([str(self.ms_dir), "--html", str(html_export)])
            self.assertEqual(rc, 0)
            self.assertTrue(html_export.is_file())

        # 10. open flag
        with patch("webbrowser.open") as mock_open:
            rc = main([str(self.ms_dir), "--html", str(html_export), "--open"])
            self.assertEqual(rc, 0)
            mock_open.assert_called_once()

        # Error case: Nonexistent manuscript
        with patch("sys.stderr", new_callable=io.StringIO) as mock_err:
            rc = main([str(self.tmp_dir / "FakeManuscript")])
            self.assertEqual(rc, 1)
            self.assertIn("Error:", mock_err.getvalue())

    def test_nested_folder_structure_preservation_and_forking(self):
        """Test that any custom nested directory structure is preserved across list and fork operations."""
        custom_ms_dir = self.univ_base / "CustomStructureMS"
        draft1_dir = custom_ms_dir / "01-Manuscript" / "Book-01" / "Draft-01"
        draft1_dir.mkdir(parents=True, exist_ok=True)

        # Create nested folders: 4-act, kishotenketsu, custom parts
        act1 = draft1_dir / "01_Act_I" / "Part_A"
        act2 = draft1_dir / "02_Act_II" / "Part_B"
        deep = draft1_dir / "Deep" / "Custom" / "Branch"
        act1.mkdir(parents=True, exist_ok=True)
        act2.mkdir(parents=True, exist_ok=True)
        deep.mkdir(parents=True, exist_ok=True)

        (act1 / "01_Chapter_01.md").write_text("# Chapter 1\nProse in act 1 part A.\n", encoding="utf-8")
        (act2 / "02_Chapter_02.md").write_text("# Chapter 2\nProse in act 2 part B.\n", encoding="utf-8")
        (deep / "03_Chapter_03.md").write_text("# Chapter 3\nDeeply nested custom prose.\n", encoding="utf-8")

        mgr = DraftManager(custom_ms_dir)
        drafts = mgr.list_drafts()
        self.assertEqual(len(drafts), 1)
        d1 = drafts[0]
        self.assertEqual(d1.chapter_count, 3)
        self.assertGreater(d1.word_count, 0)

        # Verify relative paths are captured
        rel_paths = [ch.get("rel_path") for ch in d1.chapters]
        self.assertTrue(any("Part_A" in p for p in rel_paths if p))
        self.assertTrue(any("Deep" in p for p in rel_paths if p))

        # Fork to Draft-02
        res = mgr.fork_draft(new_draft_name="Draft-02", milestone="Alpha-2")
        self.assertEqual(res["status"], "success")

        draft2_dir = custom_ms_dir / "01-Manuscript" / "Book-01" / "Draft-02"
        self.assertTrue((draft2_dir / "01_Act_I" / "Part_A" / "01_Chapter_01.md").is_file())
        self.assertTrue((draft2_dir / "02_Act_II" / "Part_B" / "02_Chapter_02.md").is_file())
        self.assertTrue((draft2_dir / "Deep" / "Custom" / "Branch" / "03_Chapter_03.md").is_file())

        drafts2 = mgr.list_drafts()
        self.assertEqual(len(drafts2), 2)
        d2 = mgr.get_draft("Draft-02")
        self.assertIsNotNone(d2)
        if d2:
            self.assertEqual(d2.chapter_count, 3)

    def test_draft_notes_and_status_defaults(self):
        """Test setting notes on drafts and querying status without explicit draft name."""
        mgr = DraftManager(self.ms_dir)
        res = mgr.set_notes("Draft-01", "Initial draft complete.")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["notes"], "Initial draft complete.")

        stat = mgr.get_draft_status()
        self.assertEqual(stat["draft"], "Draft-01")
        self.assertEqual(stat["notes"], "Initial draft complete.")

    def test_multi_act_chapter_sorting_and_scoping(self):
        """Test that multi-act hierarchical chapters (01_Act_I/01_Chapter_01.md, 01_Act_I/02_Chapter_02.md, 02_Act_II/01_Chapter_03.md) are ordered 1,2,3,4 and sliced correctly."""
        act_ms_dir = self.univ_base / "MultiActMS"
        d1_dir = act_ms_dir / "01-Manuscript" / "Book-01" / "Draft-01"
        (d1_dir / "01_Act_I").mkdir(parents=True, exist_ok=True)
        (d1_dir / "02_Act_II").mkdir(parents=True, exist_ok=True)
        (d1_dir / "03_Act_III").mkdir(parents=True, exist_ok=True)

        (d1_dir / "01_Act_I" / "01_Chapter_01.md").write_text("# Chapter 1\nAct 1 Chapter 1\n", encoding="utf-8")
        (d1_dir / "01_Act_I" / "02_Chapter_02.md").write_text("# Chapter 2\nAct 1 Chapter 2\n", encoding="utf-8")
        (d1_dir / "02_Act_II" / "01_Chapter_03.md").write_text("# Chapter 3\nAct 2 Chapter 3\n", encoding="utf-8")
        (d1_dir / "03_Act_III" / "01_Chapter_04.md").write_text("# Chapter 4\nAct 3 Chapter 4\n", encoding="utf-8")

        mgr = DraftManager(act_ms_dir)
        drafts = mgr.list_drafts()
        self.assertEqual(len(drafts), 1)
        ch_list = drafts[0].chapters
        self.assertEqual(len(ch_list), 4)

        # Confirm sequential ordering across acts: 1, 2, 3, 4
        ch_titles = [c["title"] for c in ch_list]
        self.assertEqual(ch_titles, ["Chapter 1", "Chapter 2", "Chapter 3", "Chapter 4"])
        ch_nums = [c["number"] for c in ch_list]
        self.assertEqual(ch_nums, [1, 2, 3, 4])

        # Fork with chapter slicing for chapter 3 specifically
        res_fork = mgr.fork_draft(new_draft_name="Draft-02-ch3", chapters="3")
        self.assertEqual(res_fork["chapters_copied"], 1)

        d2_slice = mgr.get_draft("Draft-02-ch3")
        self.assertIsNotNone(d2_slice)
        if d2_slice:
            self.assertEqual(len(d2_slice.chapters), 1)
            self.assertEqual(d2_slice.chapters[0]["title"], "Chapter 3")
            self.assertEqual(d2_slice.chapters[0]["rel_path"], "02_Act_II/01_Chapter_03.md")

    def test_non_numeric_chapter_slicing(self):
        """Test that unnumbered chapter files (Prologue, Interlude, Epilogue) are naturally sorted and index-sliceable."""
        named_ms_dir = self.univ_base / "NamedChaptersMS"
        d1_dir = named_ms_dir / "01-Manuscript" / "Book-01" / "Draft-01"
        d1_dir.mkdir(parents=True, exist_ok=True)

        (d1_dir / "01_Prologue.md").write_text("# Prologue\nThe origin.\n", encoding="utf-8")
        (d1_dir / "02_Interlude.md").write_text("# Interlude\nThe quiet.\n", encoding="utf-8")
        (d1_dir / "03_Epilogue.md").write_text("# Epilogue\nThe resolution.\n", encoding="utf-8")

        mgr = DraftManager(named_ms_dir)
        drafts = mgr.list_drafts()
        self.assertEqual(len(drafts), 1)
        titles = [c["title"] for c in drafts[0].chapters]
        self.assertEqual(titles, ["Prologue", "Interlude", "Epilogue"])

        # Slice 1st and 3rd files by index
        res = mgr.fork_draft(new_draft_name="Draft-02-ends", chapters="1,3")
        self.assertEqual(res["chapters_copied"], 2)

        d2 = mgr.get_draft("Draft-02-ends")
        self.assertIsNotNone(d2)
        if d2:
            self.assertEqual([c["title"] for c in d2.chapters], ["Prologue", "Epilogue"])


if __name__ == "__main__":
    unittest.main()

