#!/usr/bin/env python3
"""
Integration Tests for Ars Arcanum Engine Granular Scoping (CLI & GUI Hub)
(tests/test_engine_scope_integration.py)
========================================================================
Validates that narrative, worldbuilding, and system engines correctly respect
manuscript, chapter, scene, and lore category scopes across direct API, CLI,
and Studio Hub HTTP endpoints.
"""

import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib.scope import EngineScope, parse_unified_scope_string, filter_manuscript_scope
from lib.structure import scan_manuscript_structure, main as structure_main
from lib.plot_matrix import scan_manuscript_plot_matrix, main as plot_matrix_main
from lib.story_canvas import extract_scene_cards, main as story_canvas_main
from lib.timeline_sync import extract_timeline_events, main as timeline_sync_main
from lib.zen_studio import build_zen_studio_bundle, main as zen_studio_main
from lib.studio_hub import SovereignStudioHandler, collect_studio_hub_data


class TestEngineScopeIntegration(unittest.TestCase):
    """Integration test suite for granular target scoping across engines."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

        # Setup mock manuscript
        self.ms_dir = self.root / "Manuscripts" / "TestManuscript"
        self.ms_dir.mkdir(parents=True, exist_ok=True)

        # Chapter 1: 3 scenes
        ch1_text = """---
title: Chapter 1 - The Departure
pov: Lyra
---
# Chapter 1: The Departure
Lyra tightened the leather straps of her pack. The morning sun broke through the damp canopy.

---

Across the river, the Silver Order cavalry assembled in gleaming armor. Their steel clinked softly.

***

"We move at dawn," Master Kenneth whispered, extinguishing the small campfire with moist loam.
"""
        (self.ms_dir / "01_Chapter_One.md").write_text(ch1_text, encoding="utf-8")

        # Chapter 2: 2 scenes
        ch2_text = """---
title: Chapter 2 - The Crossing
pov: Kenneth
---
# Chapter 2: The Crossing
The bridge was narrow and slick with moss. Kenneth tested the timber with his iron-shod staff.

---

A sudden wind howled from the northern crags, smelling of sulfur and ozone.
"""
        (self.ms_dir / "02_Chapter_Two.md").write_text(ch2_text, encoding="utf-8")

        # Chapter 3: 1 scene
        ch3_text = """---
title: Chapter 3 - The Citadel
pov: Kenneth
---
# Chapter 3: The Citadel
They reached the basalt gates of the Sunspire Citadel at dusk. The ancient gates groaned.
"""
        (self.ms_dir / "03_Chapter_Three.md").write_text(ch3_text, encoding="utf-8")

        # Setup mock world
        self.world_dir = self.root / "Worlds" / "TestWorld"
        (self.world_dir / "Characters").mkdir(parents=True, exist_ok=True)
        (self.world_dir / "Factions").mkdir(parents=True, exist_ok=True)
        (self.world_dir / "MagicSystems").mkdir(parents=True, exist_ok=True)

        (self.world_dir / "Characters" / "Lyra.md").write_text("# Lyra\nHeroine and scout.", encoding="utf-8")
        (self.world_dir / "Characters" / "Kenneth.md").write_text("# Kenneth\nVeteran mage mentor.", encoding="utf-8")
        (self.world_dir / "Factions" / "SilverOrder.md").write_text("# Silver Order\nMilitarized arcane knightly order.", encoding="utf-8")
        (self.world_dir / "MagicSystems" / "GlyphMagic.md").write_text("# Glyph Magic\nHard arcane rune system.", encoding="utf-8")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_filter_manuscript_scope(self):
        """Validates filter_manuscript_scope core primitive."""
        scope_ch1 = EngineScope(chapters=[1])
        chapters, _scenes, _vols = filter_manuscript_scope(self.ms_dir, scope=scope_ch1)
        self.assertEqual(len(chapters), 1)
        self.assertEqual(chapters[0].chapter_num, 1)

        scope_ch1_2 = EngineScope(chapters=[1, 2])
        chapters2, _scenes2, _vols2 = filter_manuscript_scope(self.ms_dir, scope=scope_ch1_2)
        self.assertEqual(len(chapters2), 2)

    def test_structure_engine_scoped(self):
        """Validates narrative structure paradigm engine operates on selected scope."""
        scope_ch1 = EngineScope(chapters=[1])
        rep_ch1 = scan_manuscript_structure(self.ms_dir, scope=scope_ch1)
        self.assertEqual(rep_ch1.get("total_chapters", 0), 1)

        buf = io.StringIO()
        with patch("sys.stdout", buf):
            code = structure_main([str(self.ms_dir), "--chapters", "1-2", "--json"])
        self.assertEqual(code, 0)
        output = json.loads(buf.getvalue())
        self.assertEqual(len(output["chapters"]), 2)

    def test_plot_matrix_engine_scoped(self):
        """Validates plot matrix engine respects chapter scope."""
        scope = EngineScope(chapters=[1])
        rep = scan_manuscript_plot_matrix(self.ms_dir, scope=scope)
        self.assertEqual(rep.get("total_chapters", 0), 1)

        buf_plot = io.StringIO()
        with patch("sys.stdout", buf_plot):
            code_plot = plot_matrix_main([str(self.ms_dir), "--chapters", "1", "--json"])
        self.assertEqual(code_plot, 0)

    def test_story_canvas_engine_scoped(self):
        """Validates visual story canvas card extraction with scope."""
        scope = EngineScope(chapters=[1])
        cards = extract_scene_cards(self.ms_dir, scope=scope)
        self.assertTrue(len(cards) >= 1)

        buf = io.StringIO()
        with patch("sys.stdout", buf):
            code = story_canvas_main([str(self.ms_dir), "--chapters", "1", "--json"])
        self.assertEqual(code, 0)

    def test_timeline_sync_engine_scoped(self):
        """Validates dual-track timeline event extraction with scope."""
        scope = EngineScope(chapters=[1])
        events = extract_timeline_events(self.ms_dir, scope=scope)
        self.assertTrue(len(events) >= 1)

        buf = io.StringIO()
        with patch("sys.stdout", buf):
            code = timeline_sync_main([str(self.ms_dir), "--chapters", "2", "--json"])
        self.assertEqual(code, 0)

    def test_zen_studio_bundle_scoped(self):
        """Validates Zen Drafting Studio generates bundle with scoped chapters and lore."""
        out_html = self.root / "dist" / "zen_scoped.html"
        scope = EngineScope(chapters=[1, 2], lore_categories=["Characters"])
        bundle_path = build_zen_studio_bundle(self.ms_dir, world_path=self.world_dir, output_path=out_html, scope=scope)
        self.assertTrue(bundle_path.is_file())
        html_text = bundle_path.read_text(encoding="utf-8")
        self.assertIn("Chapter 1", html_text)
        self.assertIn("Chapter 2", html_text)
        self.assertNotIn("Chapter 3 - The Citadel", html_text)

        # Test CLI invocation
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            code = zen_studio_main([str(self.ms_dir), "-w", str(self.world_dir), "--chapters", "1", "--json"])
        self.assertEqual(code, 0)

    def test_studio_hub_scope_execution(self):
        """Validates Studio Hub handler scoped engine execution method."""
        handler = SovereignStudioHandler
        handler.project_dir = self.root
        handler.data = collect_studio_hub_data(self.root)
        handler.active_scope = EngineScope()

        scope = EngineScope(manuscript=str(self.ms_dir), chapters=[1])
        exec_res = handler._execute_scoped_engine(handler, "structure", scope, {})
        self.assertEqual(exec_res["status"], "success")
        self.assertEqual(exec_res["scope_applied"]["chapters"], [1])

    def test_unified_scope_string_parsing(self):
        """Validates complex unified scope string expressions."""
        d1 = parse_unified_scope_string("ch01..ch05:sc01..sc03")
        scope1 = EngineScope.from_dict(d1)
        self.assertEqual(scope1.chapters, [1, 2, 3, 4, 5])
        self.assertEqual(scope1.scenes, [1, 2, 3])

        d2 = parse_unified_scope_string("Book1:ch1,3,7-10:sc1-2")
        scope2 = EngineScope.from_dict(d2)
        self.assertEqual(scope2.book, "Book1")
        self.assertEqual(scope2.chapters, [1, 3, 7, 8, 9, 10])
        self.assertEqual(scope2.scenes, [1, 2])

        d3 = parse_unified_scope_string("world:Eldoria:lore:Characters,MagicSystems")
        scope3 = EngineScope.from_dict(d3)
        self.assertEqual(scope3.world, "Eldoria")
        self.assertEqual(scope3.lore_categories, ["Characters", "MagicSystems"])


if __name__ == "__main__":
    unittest.main()
