#!/usr/bin/env python3
"""
Tests for Ars Arcanum Unicode Prose Word Count & Analytics (tests/test_word_counter.py)
"""

from __future__ import annotations

import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.project_scaffold import scaffold_manuscript, scaffold_universe, scaffold_world
from lib.word_counter import (
    analyze_manuscript_words,
    count_prose_words_advanced,
    format_ansi_velocity,
    format_words_markdown,
    format_words_table,
    main,
)


class TestWordCounter(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp(prefix="arcanum_test_words_"))
        self.univ_base = self.tmp_dir / "Universes"
        self.univ_base.mkdir(parents=True, exist_ok=True)

        scaffold_universe("Saga", base_dir=self.univ_base)
        scaffold_world("Avalon", universe_name="Saga", base_dir=self.univ_base)
        res = scaffold_manuscript(
            "DragonSong",
            universe="Saga",
            world="Avalon",
            base_dir=self.univ_base,
            target_words=50000,
        )
        self.ms_dir = Path(res["path"])

    def tearDown(self):
        if self.tmp_dir.exists():
            shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_ansi_velocity_formatting(self):
        # Non-interactive returns text unmodified
        with patch("lib.word_counter._is_interactive_tty", return_value=False):
            self.assertEqual(format_ansi_velocity(85.0, "85.0%"), "85.0%")

        # Interactive returns ANSI escape color sequences
        with patch("lib.word_counter._is_interactive_tty", return_value=True):
            self.assertIn("\033[1;32m", format_ansi_velocity(105.0, "105.0%"))
            self.assertIn("\033[32m", format_ansi_velocity(80.0, "80.0%"))
            self.assertIn("\033[33m", format_ansi_velocity(60.0, "60.0%"))
            self.assertIn("\033[38;5;208m", format_ansi_velocity(35.0, "35.0%"))
            self.assertIn("\033[31m", format_ansi_velocity(10.0, "10.0%"))

    def test_count_prose_words_advanced(self):
        # Test basic text
        res = count_prose_words_advanced("The quick brown fox jumps over the lazy dog.")
        self.assertEqual(res["total_words"], 9)
        self.assertEqual(res["dialogue_words"], 0)
        self.assertEqual(res["dialogue_percentage"], 0.0)

        # Test CriticMarkup stripping
        text_critic = 'The {--slow red--}{++quick brown++} fox {==jumped==} "Run away!" {>>comment<<} yelled the badger.'
        res2 = count_prose_words_advanced(text_critic)
        self.assertGreater(res2["total_words"], 0)
        self.assertGreater(res2["dialogue_words"], 0)
        self.assertEqual(res2["dialogue_percentage"] > 0, True)

        # Test CJK ideographs
        text_cjk = "Hello world 这是一个测试 こんにちは"
        res3 = count_prose_words_advanced(text_cjk)
        self.assertGreater(res3["cjk_characters"], 0)

        # Test empty
        res_empty = count_prose_words_advanced("")
        self.assertEqual(res_empty["total_words"], 0)

    def test_analyze_manuscript_words(self):
        data = analyze_manuscript_words(self.ms_dir)
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["title"], "DragonSong")
        self.assertEqual(data["target_words"], 50000)
        self.assertGreater(data["chapter_count"], 0)
        self.assertIn("chapters", data)
        self.assertIn("pov_distribution", data)
        self.assertIn("reading_time_minutes", data)
        self.assertIn("audiobook_hours", data)
        self.assertIn("dialogue_percentage", data)

        # Write additional text with specific POV frontmatter and dialogue
        ch1 = self.ms_dir / "01-Manuscript" / "Book-01" / "Draft-01" / "01_Chapter_01.md"
        ch1.write_text(
            "---\ntitle: The Dragon Awakens\npov: Lyra\n---\n\n"
            '"Look at the sky!" Lyra whispered. The ancient dragon opened its golden eyes and roared across the valley.',
            encoding="utf-8",
        )

        data2 = analyze_manuscript_words(self.ms_dir)
        self.assertIn("Lyra", data2["pov_distribution"])
        self.assertGreater(data2["pov_distribution"]["Lyra"], 0)
        self.assertGreater(data2["dialogue_percentage"], 0.0)

    def test_format_words_table_and_markdown(self):
        data = analyze_manuscript_words(self.ms_dir)
        tbl = format_words_table(data, show_pov=True, show_dialogue=True)
        self.assertIn("DragonSong — Manuscript Word Count", tbl)
        self.assertIn("Total Words:", tbl)
        self.assertIn("Reading Time:", tbl)
        self.assertIn("Dialogue Ratio:", tbl)

        md = format_words_markdown(data)
        self.assertIn("# DragonSong — Word Count Analytics", md)
        self.assertIn("| Index | Title | POV | Words |", md)
        self.assertIn("Reading Time", md)

    def test_cli_word_counter(self):
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            rc = main([str(self.ms_dir), "--json"])
            self.assertEqual(rc, 0)
            parsed = json.loads(mock_out.getvalue())
            self.assertEqual(parsed["title"], "DragonSong")

        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            rc = main([str(self.ms_dir), "--md"])
            self.assertEqual(rc, 0)
            self.assertIn("# DragonSong", mock_out.getvalue())

        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            rc = main([str(self.ms_dir), "--pov", "--dialogue"])
            self.assertEqual(rc, 0)
            self.assertIn("DragonSong", mock_out.getvalue())

        # Test HTML export flag
        html_out = self.tmp_dir / "test_velocity.html"
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            rc = main([str(self.ms_dir), "--html", str(html_out)])
            self.assertEqual(rc, 0)
            self.assertTrue(html_out.is_file())
            content = html_out.read_text(encoding="utf-8")
            self.assertIn("DragonSong", content)
            self.assertIn("Content-Security-Policy", content)
            self.assertIn("Pomodoro", content)

        # Error case: Nonexistent manuscript
        with patch("sys.stderr", new_callable=io.StringIO) as mock_err:
            rc = main([str(self.tmp_dir / "NonexistentMS")])
            self.assertEqual(rc, 1)
            self.assertIn("Error:", mock_err.getvalue())


if __name__ == "__main__":
    unittest.main()
