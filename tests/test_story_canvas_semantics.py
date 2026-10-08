#!/usr/bin/env python3
"""
Tests for Story Canvas Semantics & Framework-Free Narrative Alignment
(tests/test_story_canvas_semantics.py)
================================================================================
Validates mathematical calculations, cumulative offset measurements,
author-tagged beat overrides, and unconstrained framework-free mode.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.lib.story_canvas import extract_scene_cards, extract_single_card
from scripts.lib.story_canvas_template import render_story_canvas_page
from scripts.lib.structure import PARADIGMS, scan_manuscript_structure


class TestStoryCanvasSemantics(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_framework_free_paradigm_exists(self) -> None:
        self.assertIn("framework_free", PARADIGMS)
        ff = PARADIGMS["framework_free"]
        self.assertEqual(len(ff["beats"]), 4)
        self.assertEqual(ff["beats"][0]["target_pct"], 0.25)
        self.assertEqual(ff["beats"][3]["target_pct"], 1.00)

    def test_scan_manuscript_structure_framework_free_always_perfect_harmony(self) -> None:
        # Create 3 chapters of arbitrary lengths
        ch1 = self.root / "ch01.md"
        ch2 = self.root / "ch02.md"
        ch3 = self.root / "ch03.md"
        ch1.write_text("Chapter one with several words " * 50, encoding="utf-8")
        ch2.write_text("Chapter two with more words " * 100, encoding="utf-8")
        ch3.write_text("Chapter three with closing words " * 20, encoding="utf-8")

        res = scan_manuscript_structure(self.root, paradigm_key="framework_free")
        self.assertEqual(res["paradigm_key"], "framework_free")
        self.assertEqual(res["harmony_score"], 100.0)
        self.assertEqual(res["total_chapters"], 3)

    def test_author_tagged_beat_extraction(self) -> None:
        content = """---
title: The Awakening
beat: Inciting Incident
pov: Elenor
location: Obsidian Tower
---
@thread: Rebellion
@tension: 8.5
The citadel shuddered as the dark glyphs flared.
"""
        doc = self.root / "ch01.md"
        doc.write_text(content, encoding="utf-8")

        card = extract_single_card(content, doc, 1)
        self.assertEqual(card["title"], "The Awakening")
        self.assertEqual(card["author_beat"], "Inciting Incident")
        self.assertEqual(card["pov"], "Elenor")
        self.assertEqual(card["location"], "Obsidian Tower")
        self.assertEqual(card["thread"], "Rebellion")
        self.assertEqual(card["tension"], 8.5)

    def test_extract_scene_cards_preserves_author_beat(self) -> None:
        ch1 = self.root / "01_Prologue.md"
        ch1.write_text("---\npov: Alice\nbeat: Opening Movement\n---\nAlice saw the ship.", encoding="utf-8")
        ch2 = self.root / "02_Chapter.md"
        ch2.write_text("---\npov: Bob\n---\n@beat: Climax\nBob fought bravely.", encoding="utf-8")

        cards = extract_scene_cards(self.root)
        self.assertEqual(len(cards), 2)
        self.assertEqual(cards[0]["author_beat"], "Opening Movement")
        self.assertEqual(cards[1]["author_beat"], "Climax")

    def test_render_story_canvas_page_html_output(self) -> None:
        ch1 = self.root / "01_Prologue.md"
        ch1.write_text("Alice saw the ship on the stormy horizon.", encoding="utf-8")
        cards = extract_scene_cards(self.root)

        html_content = render_story_canvas_page(
            target_path=self.root,
            cards=cards,
            paradigm_key="framework_free",
            tips_data=[{"engine": "story_canvas", "subfeature": "flow", "title": "Pacing", "content": "Trust your flow"}],
            tips_enabled=True,
        )
        self.assertIn("<!DOCTYPE html>", html_content)
        self.assertIn("Content-Security-Policy", html_content)
        self.assertIn("framework_free", html_content)
        self.assertIn("Unconstrained Flow", html_content)


if __name__ == "__main__":
    unittest.main()
