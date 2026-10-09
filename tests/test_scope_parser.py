#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Scope Parser (scripts/lib/scope_parser.py)
"""

import argparse
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.scope_parser import (
    add_scope_arguments,
    parse_identifier_list,
    parse_number_ranges,
    parse_scope_args,
    parse_unified_scope_string,
)


class TestScopeParser(unittest.TestCase):

    def test_parse_number_ranges_edge_cases(self):
        self.assertEqual(parse_number_ranges(None), [])
        self.assertEqual(parse_number_ranges(0), [])
        self.assertEqual(parse_number_ranges(-10), [])
        self.assertEqual(parse_number_ranges(42), [42])
        self.assertEqual(parse_number_ranges("all"), [])
        self.assertEqual(parse_number_ranges("none"), [])
        self.assertEqual(parse_number_ranges("*"), [])
        self.assertEqual(parse_number_ranges(""), [])
        self.assertEqual(parse_number_ranges("   "), [])

        # Test ranges descending
        self.assertEqual(parse_number_ranges("5-1"), [1, 2, 3, 4, 5])
        self.assertEqual(parse_number_ranges("5 to 1"), [1, 2, 3, 4, 5])

        # Test messy tokens
        self.assertEqual(parse_number_ranges("chapter 1 to 3; ch 5..7"), [1, 2, 3, 5, 6, 7])
        self.assertEqual(parse_number_ranges("act 2, scenes 3-5, vol 1"), [1, 2, 3, 4, 5])
        self.assertEqual(parse_number_ranges("part 1-3"), [1, 2, 3])

    def test_parse_identifier_list(self):
        self.assertEqual(parse_identifier_list(None), [])
        self.assertEqual(parse_identifier_list(""), [])
        self.assertEqual(parse_identifier_list("all"), [])
        self.assertEqual(parse_identifier_list("none"), [])
        self.assertEqual(parse_identifier_list("*"), [])
        self.assertEqual(parse_identifier_list("A, B, 'C', \"D\""), ["A", "B", "C", "D"])
        self.assertEqual(parse_identifier_list(["A, B", "C", ["D"]]), ["A", "B", "C", "D"])

    def test_parse_unified_scope_string_shorthands(self):
        # Empty
        self.assertEqual(parse_unified_scope_string(""), {
            "manuscript": None, "world": None, "universe": None,
            "series": [], "books": [], "chapters": [], "scenes": [], "lore_categories": []
        })

        # Number shorthand
        res = parse_unified_scope_string("1-5")
        self.assertEqual(res["chapters"], [1, 2, 3, 4, 5])

        res_sc = parse_unified_scope_string("sc1..3")
        self.assertEqual(res_sc["scenes"], [1, 2, 3])

    def test_parse_unified_scope_string_key_values(self):
        # Key:value combinations
        res = parse_unified_scope_string("ms:BookOne, world:Cosmos, cat:Characters, ch:1-3, sc:1-2")
        self.assertEqual(res["manuscript"], "BookOne")
        self.assertEqual(res["world"], "Cosmos")
        self.assertEqual(res["lore_categories"], ["Characters"])
        self.assertEqual(res["chapters"], [1, 2, 3])
        self.assertEqual(res["scenes"], [1, 2])

        # Universe and series
        res2 = parse_unified_scope_string("universe:Arcana, series:Trilogy, books:Book-01,Book-02")
        self.assertEqual(res2["universe"], "Arcana")
        self.assertEqual(res2["series"], ["Trilogy"])
        self.assertEqual(res2["books"], ["Book-01", "Book-02"])

    def test_parse_unified_scope_string_path_segments(self):
        res = parse_unified_scope_string("Book-01/ch1-3/sc1-2")
        self.assertEqual(res["books"], ["Book-01"])
        self.assertEqual(res["chapters"], [1, 2, 3])
        self.assertEqual(res["scenes"], [1, 2])

        res_plain = parse_unified_scope_string("manuscript:MyNovel")
        self.assertEqual(res_plain["manuscript"], "MyNovel")

        res_book = parse_unified_scope_string("MyNovel")
        self.assertEqual(res_book["books"], ["MyNovel"])


    def test_add_scope_arguments_and_parse(self):
        parser = argparse.ArgumentParser()
        add_scope_arguments(parser, target_pos_arg=True)

        args = parser.parse_args([
            "MyManuscript",
            "--world", "MyWorld",
            "--universe", "MyUniverse",
            "--series", "Series1",
            "--books", "Book1,Book2",
            "--chapters", "1-4",
            "--scenes", "1,2",
            "--lore-categories", "Magic,Factions",
            "--all",
        ])
        scope = parse_scope_args(args)
        self.assertEqual(scope.manuscript, "MyManuscript")
        self.assertEqual(scope.world, "MyWorld")
        self.assertEqual(scope.universe, "MyUniverse")
        self.assertEqual(scope.series, ["Series1"])
        self.assertEqual(scope.books, ["Book1", "Book2"])
        self.assertEqual(scope.chapters, [1, 2, 3, 4])
        self.assertEqual(scope.scenes, [1, 2])
        self.assertEqual(scope.lore_categories, ["Magic", "Factions"])
        self.assertTrue(scope.all_targets)


if __name__ == "__main__":
    unittest.main()
