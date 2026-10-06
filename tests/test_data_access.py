#!/usr/bin/env python3
"""
Tests for Ars Arcanum Centralized Data Access Layer (tests/test_data_access.py)
"""

from __future__ import annotations

import tempfile
import time
import unittest
from pathlib import Path

from scripts.lib.data_access import DataAccessLayer, get_data_access


class TestDataAccessLayer(unittest.TestCase):
    """Unit and caching invariant tests for DataAccessLayer."""

    def setUp(self) -> None:
        self.dal = DataAccessLayer()

    def test_singleton_accessor(self) -> None:
        dal1 = get_data_access()
        dal2 = get_data_access()
        self.assertIs(dal1, dal2)

    def test_read_file_and_cache_hits(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "note.md"
            f.write_text("# Chapter 1\nProse content here.", encoding="utf-8")

            # First read: cache miss
            content1 = self.dal.read_file(f)
            self.assertEqual(content1, "# Chapter 1\nProse content here.")
            stats1 = self.dal.get_stats()
            self.assertEqual(stats1["cache_hits"], 0)
            self.assertEqual(stats1["cache_misses"], 1)

            # Second read: cache hit
            content2 = self.dal.read_file(f)
            self.assertEqual(content2, content1)
            stats2 = self.dal.get_stats()
            self.assertEqual(stats2["cache_hits"], 1)
            self.assertEqual(stats2["cache_misses"], 1)

    def test_mtime_invalidation(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "draft.md"
            f.write_text("Original text", encoding="utf-8")

            self.assertEqual(self.dal.read_file(f), "Original text")

            # Sleep slightly to guarantee different mtime
            time.sleep(0.05)
            f.write_text("Updated text", encoding="utf-8")

            # Must read updated text on mtime modification
            updated = self.dal.read_file(f)
            self.assertEqual(updated, "Updated text")
            stats = self.dal.get_stats()
            self.assertEqual(stats["cache_misses"], 2)

    def test_parse_frontmatter(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "hero.md"
            f.write_text(
                "---\nname: Lyra Vael\nrole: Protagonist\nalive: true\nage: 24\n---\n# Dossier\nLyra is an aetherist.",
                encoding="utf-8",
            )

            fm, body = self.dal.parse_frontmatter(f)
            self.assertEqual(fm["name"], "Lyra Vael")
            self.assertEqual(fm["role"], "Protagonist")
            self.assertEqual(fm["alive"], True)
            self.assertEqual(fm["age"], 24)
            self.assertIn("# Dossier", body)

    def test_get_manuscript_chapters_and_lore_entities(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            # Create world
            world_dir = root / "Aethelgard"
            char_dir = world_dir / "Characters"
            char_dir.mkdir(parents=True)
            (char_dir / "Lyra.md").write_text("---\nname: Lyra\ntags: mage, hero\n---\nLyra body", encoding="utf-8")

            # Create manuscript
            ms_dir = root / "Manuscript"
            draft_dir = ms_dir / "Book-01" / "Draft-01"
            draft_dir.mkdir(parents=True)
            (draft_dir / "01_Chapter.md").write_text("---\ntitle: The Opening\n---\nFive hundred words here.", encoding="utf-8")

            entities = self.dal.get_lore_entities(world_dir)
            self.assertEqual(len(entities), 1)
            self.assertEqual(entities[0]["name"], "Lyra")
            self.assertEqual(entities[0]["category"], "Characters")

            chapters = self.dal.get_manuscript_chapters(ms_dir)
            self.assertEqual(len(chapters), 1)
            self.assertEqual(chapters[0]["title"], "The Opening")
            self.assertGreater(chapters[0]["words"], 0)

    def test_nonexistent_files_and_clear(self) -> None:
        self.assertEqual(self.dal.read_file("/non/existent/path/never.md"), "")
        fm, body = self.dal.parse_frontmatter("/non/existent/path/never.md")
        self.assertEqual(fm, {})
        self.assertEqual(body, "")
        self.assertEqual(self.dal.list_files("/non/existent/dir"), [])

        self.dal.clear()
        stats = self.dal.get_stats()
        self.assertEqual(stats["cached_files"], 0)


if __name__ == "__main__":
    unittest.main()
