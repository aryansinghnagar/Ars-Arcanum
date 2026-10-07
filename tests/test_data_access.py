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

    def test_lru_eviction_and_evict_hook(self) -> None:
        small_dal = DataAccessLayer(max_entries=3)
        with tempfile.TemporaryDirectory() as td:
            f1 = Path(td) / "f1.md"
            f2 = Path(td) / "f2.md"
            f3 = Path(td) / "f3.md"
            f4 = Path(td) / "f4.md"

            f1.write_text("content 1", encoding="utf-8")
            f2.write_text("content 2", encoding="utf-8")
            f3.write_text("content 3", encoding="utf-8")
            f4.write_text("content 4", encoding="utf-8")

            small_dal.read_file(f1)
            small_dal.read_file(f2)
            small_dal.read_file(f3)
            self.assertEqual(small_dal.get_stats()["cached_files"], 3)

            # Access f1 to promote it in LRU
            small_dal.read_file(f1)

            # Read f4 -> should evict f2 (since f1 was promoted)
            small_dal.read_file(f4)
            self.assertEqual(small_dal.get_stats()["cached_files"], 3)

            # Explicit evict single file
            self.assertEqual(small_dal.evict(f1), 1)
            self.assertEqual(small_dal.get_stats()["cached_files"], 2)
            self.assertEqual(small_dal.evict(f1), 0)

    def test_get_word_count_and_prefix_eviction(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            dir_a = Path(td) / "project_a"
            dir_a.mkdir()
            f1 = dir_a / "chap1.md"
            f2 = dir_a / "chap2.md"
            f1.write_text("# Chapter 1\nOne two three four five.", encoding="utf-8")
            f2.write_text("# Chapter 2\nSix seven eight nine ten.", encoding="utf-8")

            # Word count cached test
            wc1 = self.dal.get_word_count(f1)
            self.assertEqual(wc1, 7)  # "Chapter 1 One two three four five" = 7 words
            wc2 = self.dal.get_word_count(f2)
            self.assertEqual(wc2, 7)

            _fm, body = self.dal.parse_frontmatter_and_body(f1)
            self.assertIn("Chapter 1", body)

            # Prefix eviction test
            evicted_count = self.dal.evict(dir_a)
            self.assertEqual(evicted_count, 2)
            self.assertEqual(self.dal.evict(dir_a), 0)


if __name__ == "__main__":
    unittest.main()

