#!/usr/bin/env python3
"""
Comprehensive Unit Tests for Ars Arcanum Scope & Granular Target Resolution Engine
(tests/test_scope.py)
================================================================================
Validates range parsing, identifier parsing, manuscript/world resolution heuristics,
granular chapter/scene slicing, lore category filtering, CLI arguments, and serialization.
"""

import argparse
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib.scope import (
    EngineScope,
    parse_number_ranges,
    parse_identifier_list,
    extract_scenes_from_text,
    filter_manuscript_scope,
    filter_world_scope,
    resolve_scope,
    add_scope_arguments,
    parse_scope_args,
)


class TestRangeAndIdentifierParsers(unittest.TestCase):
    """Validates number range and identifier list parsing."""

    def test_parse_number_ranges_integers(self):
        self.assertEqual(parse_number_ranges(5), [5])
        self.assertEqual(parse_number_ranges(0), [])
        self.assertEqual(parse_number_ranges(-3), [])
        self.assertEqual(parse_number_ranges(None), [])

    def test_parse_number_ranges_comma_separated(self):
        self.assertEqual(parse_number_ranges("1,2,3"), [1, 2, 3])
        self.assertEqual(parse_number_ranges("1, 3, 5"), [1, 3, 5])
        self.assertEqual(parse_number_ranges("4,2,4,2,1"), [1, 2, 4])

    def test_parse_number_ranges_hyphen_and_dots(self):
        self.assertEqual(parse_number_ranges("1-5"), [1, 2, 3, 4, 5])
        self.assertEqual(parse_number_ranges("1..5"), [1, 2, 3, 4, 5])
        self.assertEqual(parse_number_ranges("01-05"), [1, 2, 3, 4, 5])
        self.assertEqual(parse_number_ranges("10-12"), [10, 11, 12])

    def test_parse_number_ranges_prefixed(self):
        self.assertEqual(parse_number_ranges("ch1-ch5"), [1, 2, 3, 4, 5])
        self.assertEqual(parse_number_ranges("Chapter 1 - Chapter 3"), [1, 2, 3])
        self.assertEqual(parse_number_ranges("sc1, sc3, sc5-sc7"), [1, 3, 5, 6, 7])
        self.assertEqual(parse_number_ranges("Scene 2..4"), [2, 3, 4])

    def test_parse_number_ranges_nested_sequence(self):
        self.assertEqual(parse_number_ranges(["1-3", 5, "7..9"]), [1, 2, 3, 5, 7, 8, 9])

    def test_parse_number_ranges_empty_and_invalid(self):
        self.assertEqual(parse_number_ranges(""), [])
        self.assertEqual(parse_number_ranges("abc"), [])
        self.assertEqual(parse_number_ranges("None"), [])

    def test_parse_identifier_list(self):
        self.assertEqual(parse_identifier_list("Book-01, Book-02"), ["Book-01", "Book-02"])
        self.assertEqual(parse_identifier_list(["Characters", "Locations"]), ["Characters", "Locations"])
        self.assertEqual(parse_identifier_list("SingleItem"), ["SingleItem"])
        self.assertEqual(parse_identifier_list(""), [])
        self.assertEqual(parse_identifier_list(None), [])


class TestEngineScopeDataClass(unittest.TestCase):
    """Validates EngineScope methods and serialization."""

    def test_is_scoped(self):
        s_empty = EngineScope()
        self.assertFalse(s_empty.is_scoped())

        s_ch = EngineScope(chapters=[1, 2])
        self.assertTrue(s_ch.is_scoped())
        self.assertTrue(s_ch.is_manuscript_scoped())
        self.assertFalse(s_ch.is_world_scoped())

        s_lore = EngineScope(lore_categories=["Characters"])
        self.assertTrue(s_lore.is_scoped())
        self.assertFalse(s_lore.is_manuscript_scoped())
        self.assertTrue(s_lore.is_world_scoped())

    def test_serialization_roundtrip(self):
        scope = EngineScope(
            manuscript="Novel",
            world="Eldoria",
            universe="Cosmere",
            books=["Book-01"],
            chapters=[1, 2, 3],
            scenes=[1, 2],
            lore_categories=["Factions", "MagicSystems"],
            raw_scope="ch1-ch3",
            all_targets=False,
        )
        d = scope.to_dict()
        reconstructed = EngineScope.from_dict(d)
        self.assertEqual(scope, reconstructed)
        self.assertIn("ch01-03", scope.summary)


class TestSceneExtractionAndFiltering(unittest.TestCase):
    """Validates scene extraction from chapter content and manuscript scope filtering."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

        # Create manuscript fixture
        self.ms_dir = self.root / "TestNovel"
        self.book1_dir = self.ms_dir / "Book-01"
        self.book1_dir.mkdir(parents=True, exist_ok=True)

        (self.book1_dir / "01_Prologue.md").write_text(
            "---\ntitle: Prologue\npov: Lyra\n---\n# Prologue\n\nFirst scene text.\n\n---\n\nSecond scene text.\n\n***\n\nThird scene text.",
            encoding="utf-8",
        )
        (self.book1_dir / "02_Chapter_One.md").write_text(
            "# Chapter 1: The Gathering\n\nScene A text.\n\n@scene: Escape\nScene B text.",
            encoding="utf-8",
        )
        (self.book1_dir / "03_Chapter_Two.md").write_text(
            "# Chapter 2: The Journey\n\nFull chapter continuous text.",
            encoding="utf-8",
        )

        # Create world fixture
        self.world_dir = self.root / "TestWorld"
        (self.world_dir / "Characters").mkdir(parents=True, exist_ok=True)
        (self.world_dir / "Factions").mkdir(parents=True, exist_ok=True)
        (self.world_dir / "Locations").mkdir(parents=True, exist_ok=True)

        (self.world_dir / "Characters" / "Lyra.md").write_text("# Lyra\nHeroine", encoding="utf-8")
        (self.world_dir / "Factions" / "SilverOrder.md").write_text("# Silver Order\nKnights", encoding="utf-8")
        (self.world_dir / "Locations" / "Sunspire.md").write_text("# Sunspire\nCapital", encoding="utf-8")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_extract_scenes_from_chapter(self):
        p = self.book1_dir / "01_Prologue.md"
        content = p.read_text(encoding="utf-8")
        scenes = extract_scenes_from_text(content, p, 1)
        self.assertEqual(len(scenes), 3)
        self.assertEqual(scenes[0].scene_idx, 1)
        self.assertEqual(scenes[1].scene_idx, 2)
        self.assertEqual(scenes[2].scene_idx, 3)
        self.assertIn("First scene text", scenes[0].content)
        self.assertIn("Second scene text", scenes[1].content)
        self.assertIn("Third scene text", scenes[2].content)

    def test_filter_manuscript_scope_all(self):
        scope = EngineScope()
        chapters, _scenes, _volumes = filter_manuscript_scope(self.ms_dir, scope)
        self.assertEqual(len(chapters), 3)

    def test_filter_manuscript_scope_chapters_subset(self):
        scope = EngineScope(chapters=[1, 3])
        chapters, _scenes, _volumes = filter_manuscript_scope(self.ms_dir, scope)
        self.assertEqual(len(chapters), 2)
        self.assertEqual([c.chapter_num for c in chapters], [1, 3])

    def test_filter_manuscript_scope_scenes_subset(self):
        scope = EngineScope(chapters=[1], scenes=[2])
        chapters, _scenes, _volumes = filter_manuscript_scope(self.ms_dir, scope)
        self.assertEqual(len(chapters), 1)
        self.assertEqual(len(chapters[0].scenes), 1)
        self.assertEqual(chapters[0].scenes[0].scene_idx, 2)

    def test_filter_world_scope_categories(self):
        scope = EngineScope(lore_categories=["Characters", "Factions"])
        lore_items = filter_world_scope(self.world_dir, scope)
        self.assertEqual(len(lore_items), 2)
        filenames = {item.file_path.name for item in lore_items}
        self.assertIn("Lyra.md", filenames)
        self.assertIn("SilverOrder.md", filenames)
        self.assertNotIn("Sunspire.md", filenames)


class TestScopeResolutionAndArgparse(unittest.TestCase):
    """Validates CLI argument parsing and full scope resolution."""

    def test_add_and_parse_scope_arguments(self):
        parser = argparse.ArgumentParser()
        add_scope_arguments(parser, target_pos_arg=True)
        args = parser.parse_args([
            "MyNovel",
            "--chapters", "1-3,5",
            "--scenes", "1-2",
            "--world", "Eldoria",
            "--lore-categories", "Bestiary,Characters"
        ])
        scope = parse_scope_args(args)
        self.assertEqual(scope.manuscript, "MyNovel")
        self.assertEqual(scope.world, "Eldoria")
        self.assertEqual(scope.chapters, [1, 2, 3, 5])
        self.assertEqual(scope.scenes, [1, 2])
        self.assertEqual(scope.lore_categories, ["Bestiary", "Characters"])

    def test_resolve_scope_with_fixtures(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ms = root / "NovelA"
            ms.mkdir()
            (ms / "01_Ch1.md").write_text("# Chapter 1\n\nScene 1 text.\n\n---\n\nScene 2 text.", encoding="utf-8")
            (ms / "02_Ch2.md").write_text("# Chapter 2\n\nScene 1 text.", encoding="utf-8")

            scope = EngineScope(manuscript=str(ms), chapters=[1])
            res = resolve_scope(scope)
            self.assertEqual(len(res.chapters), 1)
            self.assertEqual(res.chapters[0].chapter_num, 1)
            self.assertEqual(res.get_total_chapter_count(), 1)
            self.assertEqual(res.get_total_scene_count(), 2)


if __name__ == "__main__":
    unittest.main()
