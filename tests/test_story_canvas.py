#!/usr/bin/env python3
"""
Test Suite: Interactive Visual Story Canvas & Corkboard Engine
(tests/test_story_canvas.py)
================================================================================
Validates scene card extraction, metadata parsing, paradigm mapping, drag-and-drop
corkboard generation, thread/POV filtering, and Content Security Policy compliance.
"""

import io
import json
import tempfile
import unittest
from pathlib import Path
import sys
from unittest.mock import patch

from scripts.lib.story_canvas import (
    extract_scene_cards,
    extract_single_card,
    generate_story_canvas_html,
    main,
)
from scripts.lib.story_canvas_template import render_story_canvas_page
from scripts.lib.structure import PARADIGMS, scan_manuscript_structure

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestStoryCanvas(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

        # Create mock chapters with metadata
        (self.root / "01_Chapter_01.md").write_text(
            "---\ntitle: Opening Scene\npov: Kaelen\nlocation: Sun-Tower\nthread: Core\ntension: 7.0\n---\nKaelen stood upon the high tower overlooking the city.",
            encoding="utf-8",
        )
        (self.root / "02_Chapter_02.md").write_text(
            "@pov: Lysandra\n@location: Shadow-Alley\n@thread: Subplot\n@tension: 4.5\nLysandra slipped into the damp alleyway silently.",
            encoding="utf-8",
        )
        (self.root / "03_Chapter_03.md").write_text(
            "# The Convergence\n\nBoth heroes met at the central plaza under the eclipse.",
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    # ------------------------------------------------------------------ #
    # 1. Card Extraction Count & Fields                                  #
    # ------------------------------------------------------------------ #
    def test_extract_scene_cards(self):
        """extract_scene_cards must return structured metadata cards for all chapters."""
        cards = extract_scene_cards(self.root)
        self.assertEqual(len(cards), 3)

        # Card 1
        c1 = cards[0]
        self.assertEqual(c1["title"], "Opening Scene")
        self.assertEqual(c1["pov"], "Kaelen")
        self.assertEqual(c1["location"], "Sun-Tower")
        self.assertEqual(c1["thread"], "Core")
        self.assertEqual(c1["tension"], 7.0)
        self.assertGreater(c1["word_count"], 0)

        # Card 2 (inline @tags)
        c2 = cards[1]
        self.assertEqual(c2["pov"], "Lysandra")
        self.assertEqual(c2["location"], "Shadow-Alley")
        self.assertEqual(c2["thread"], "Subplot")
        self.assertEqual(c2["tension"], 4.5)

        # Card 3 (defaults)
        c3 = cards[2]
        self.assertEqual(c3["title"], "The Convergence")
        self.assertEqual(c3["pov"], "Omniscient")

    # ------------------------------------------------------------------ #
    # 2. HTML Canvas Generation & Components                             #
    # ------------------------------------------------------------------ #
    def test_generate_story_canvas_html(self):
        """generate_story_canvas_html must produce interactive HTML with paradigm lanes."""
        cards = extract_scene_cards(self.root)
        out_html = self.root / "test_canvas.html"
        html_str = generate_story_canvas_html(self.root, cards, paradigm_key="eight_sequence", output_path=out_html)

        self.assertTrue(out_html.is_file())
        self.assertIn("Ars Arcanum Story Canvas", html_str)
        self.assertIn("Content-Security-Policy", html_str)
        self.assertIn("Kaelen", html_str)
        self.assertIn("Lysandra", html_str)
        self.assertIn("8-Sequence Method", html_str)

    # ------------------------------------------------------------------ #
    # 3. Content Security Policy Isolation                               #
    # ------------------------------------------------------------------ #
    def test_story_canvas_csp_compliance(self):
        """Story Canvas HTML must enforce strict offline Content-Security-Policy."""
        cards = extract_scene_cards(self.root)
        out_html = self.root / "canvas_csp.html"
        html_str = generate_story_canvas_html(self.root, cards, output_path=out_html)
        self.assertIn("default-src 'none'", html_str)
        self.assertIn("style-src 'unsafe-inline'", html_str)
        self.assertIn("script-src 'unsafe-inline'", html_str)

    # ------------------------------------------------------------------ #
    # 4. Canonical Paradigm Support (Save the Cat)                       #
    # ------------------------------------------------------------------ #
    def test_story_canvas_save_the_cat_paradigm(self):
        """generate_story_canvas_html must render Save the Cat beat definitions."""
        cards = extract_scene_cards(self.root)
        out_html = self.root / "canvas_stc.html"
        html_str = generate_story_canvas_html(self.root, cards, paradigm_key="save_the_cat", output_path=out_html)
        self.assertIn("save_the_cat", html_str)
        self.assertIn("Opening Image", html_str)
        self.assertIn("Catalyst", html_str)

    # ------------------------------------------------------------------ #
    # 5. Canonical Paradigm Support (Hero's Journey)                     #
    # ------------------------------------------------------------------ #
    def test_story_canvas_heros_journey_paradigm(self):
        """generate_story_canvas_html must render Hero's Journey monomyth definitions."""
        cards = extract_scene_cards(self.root)
        out_html = self.root / "canvas_hero.html"
        html_str = generate_story_canvas_html(self.root, cards, paradigm_key="heros_journey", output_path=out_html)
        self.assertIn("heros_journey", html_str)
        self.assertIn("Ordinary World", html_str)
        self.assertIn("Call to Adventure", html_str)

    # ------------------------------------------------------------------ #
    # 6. Canonical Paradigm Support (Kishōtenketsu)                       #
    # ------------------------------------------------------------------ #
    def test_story_canvas_kishotenketsu_paradigm(self):
        """generate_story_canvas_html must render Kishōtenketsu structural definitions."""
        cards = extract_scene_cards(self.root)
        out_html = self.root / "canvas_kisho.html"
        html_str = generate_story_canvas_html(self.root, cards, paradigm_key="kishotenketsu", output_path=out_html)
        self.assertIn("kishotenketsu", html_str)
        self.assertIn("Ki (Introduction)", html_str)

    # ------------------------------------------------------------------ #
    # 7. Drag and Drop JavaScript Handlers                               #
    # ------------------------------------------------------------------ #
    def test_story_canvas_drag_drop_script(self):
        """HTML must include handleDragStart, handleDragOver, and handleDrop handlers."""
        cards = extract_scene_cards(self.root)
        out_html = self.root / "canvas_dnd.html"
        html_str = generate_story_canvas_html(self.root, cards, output_path=out_html)
        self.assertIn("handleDragStart", html_str)
        self.assertIn("handleDragOver", html_str)
        self.assertIn("handleDrop", html_str)

    # ------------------------------------------------------------------ #
    # 8. POV Filtering Controls in HTML UI                               #
    # ------------------------------------------------------------------ #
    def test_story_canvas_pov_filters(self):
        """HTML must include povFilter select element and filterCards logic."""
        cards = extract_scene_cards(self.root)
        out_html = self.root / "canvas_pov.html"
        html_str = generate_story_canvas_html(self.root, cards, output_path=out_html)
        self.assertIn("povFilter", html_str)
        self.assertIn("filterCards", html_str)

    # ------------------------------------------------------------------ #
    # 9. Badges and Metadata Rendering                                   #
    # ------------------------------------------------------------------ #
    def test_story_canvas_badges(self):
        """HTML must include badge-pov, badge-loc, and badge-thread classes."""
        cards = extract_scene_cards(self.root)
        out_html = self.root / "canvas_badges.html"
        html_str = generate_story_canvas_html(self.root, cards, output_path=out_html)
        self.assertIn("badge-pov", html_str)
        self.assertIn("badge-loc", html_str)
        self.assertIn("badge-thread", html_str)

    # ------------------------------------------------------------------ #
    # 10. Manifest Export Logic                                          #
    # ------------------------------------------------------------------ #
    def test_story_canvas_manifest_export(self):
        """HTML must include exportManifest function for saving reordered cards."""
        cards = extract_scene_cards(self.root)
        out_html = self.root / "canvas_manifest.html"
        html_str = generate_story_canvas_html(self.root, cards, output_path=out_html)
        self.assertIn("exportManifest", html_str)
        self.assertIn("story_canvas_manifest.json", html_str)

    # ------------------------------------------------------------------ #
    # 11. Single File Extraction Behavior                                #
    # ------------------------------------------------------------------ #
    def test_extract_scene_cards_single_file(self):
        """extract_scene_cards pointing to a single file should return 1 card."""
        single_file = self.root / "01_Chapter_01.md"
        cards = extract_scene_cards(single_file)
        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0]["title"], "Opening Scene")

    # ------------------------------------------------------------------ #
    # 12. Nonexistent Path Error Handling                                #
    # ------------------------------------------------------------------ #
    def test_extract_scene_cards_nonexistent_path(self):
        """extract_scene_cards on missing directory must raise FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            extract_scene_cards(self.root / "Nonexistent_Dir")

    # ------------------------------------------------------------------ #
    # 13. CLI Main Routine                                               #
    # ------------------------------------------------------------------ #
    def test_cli_main(self):
        # JSON output
        with patch.object(sys, "argv", ["story_canvas.py", str(self.root), "--json"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                main()
                data = json.loads(mock_stdout.getvalue())
                self.assertEqual(len(data), 3)

        # HTML generation via CLI
        out_html = self.root / "cli_canvas.html"
        with patch.object(sys, "argv", ["story_canvas.py", str(self.root), "--html", str(out_html), "--paradigm", "save_the_cat"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                main()
                self.assertIn("Ars Arcanum Story Canvas", mock_stdout.getvalue())
                self.assertTrue(out_html.is_file())

        # Error nonexistent
        with patch.object(sys, "argv", ["story_canvas.py", str(self.root / "nonexistent")]):
            with patch("sys.stderr", new_callable=io.StringIO) as mock_stderr:
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 1)
                self.assertIn("Target path does not exist", mock_stderr.getvalue())

    # ------------------------------------------------------------------ #
    # 14. Framework-Free Narrative & Author-Tagged Beat Extraction       #
    # ------------------------------------------------------------------ #
    def test_framework_free_paradigm_exists(self):
        self.assertIn("framework_free", PARADIGMS)
        ff = PARADIGMS["framework_free"]
        self.assertEqual(len(ff["beats"]), 4)
        self.assertEqual(ff["beats"][0]["target_pct"], 0.25)
        self.assertEqual(ff["beats"][3]["target_pct"], 1.00)

    def test_scan_manuscript_structure_framework_free_always_perfect_harmony(self):
        ch1 = self.root / "ch01_ff.md"
        ch2 = self.root / "ch02_ff.md"
        ch3 = self.root / "ch03_ff.md"
        ch1.write_text("Chapter one with several words " * 50, encoding="utf-8")
        ch2.write_text("Chapter two with more words " * 100, encoding="utf-8")
        ch3.write_text("Chapter three with closing words " * 20, encoding="utf-8")

        res = scan_manuscript_structure(self.root, paradigm_key="framework_free")
        self.assertEqual(res["paradigm_key"], "framework_free")
        self.assertEqual(res["harmony_score"], 100.0)

    def test_author_tagged_beat_extraction(self):
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
        doc = self.root / "ch_tagged.md"
        doc.write_text(content, encoding="utf-8")

        card = extract_single_card(content, doc, 1)
        self.assertEqual(card["title"], "The Awakening")
        self.assertEqual(card["author_beat"], "Inciting Incident")
        self.assertEqual(card["pov"], "Elenor")
        self.assertEqual(card["location"], "Obsidian Tower")
        self.assertEqual(card["thread"], "Rebellion")
        self.assertEqual(card["tension"], 8.5)

    def test_extract_scene_cards_preserves_author_beat(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            ch1 = td_path / "01_Prologue.md"
            ch1.write_text("---\npov: Alice\nbeat: Opening Movement\n---\nAlice saw the ship.", encoding="utf-8")
            ch2 = td_path / "02_Chapter.md"
            ch2.write_text("---\npov: Bob\n---\n@beat: Climax\nBob fought bravely.", encoding="utf-8")

            cards = extract_scene_cards(td_path)
            self.assertEqual(len(cards), 2)
            self.assertEqual(cards[0]["author_beat"], "Opening Movement")
            self.assertEqual(cards[1]["author_beat"], "Climax")

    def test_render_story_canvas_page_html_output(self):
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

