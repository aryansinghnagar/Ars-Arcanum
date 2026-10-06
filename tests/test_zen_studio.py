#!/usr/bin/env python3
"""
Test Suite: Standalone Offline Zen Drafting Studio
(tests/test_zen_studio.py)
================================================================================
Validates manuscript, lore, and outline scanning, single-file HTML5 bundle creation,
Content Security Policy compliance, in-situ metadata inspector, real-time two-way
frontmatter sync, multi-tier outline drawer (Floating, Book, Series), theme styling,
ergonomic controls, and CLI telemetry export methods.
"""

import tempfile
import unittest
from pathlib import Path

from scripts.lib.zen_studio import (
    build_zen_studio_bundle,
    scan_lore_entities,
    scan_outlines,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestZenStudio(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

        # Mock World Lore
        self.world_dir = self.root / "Eldoria-Prime"
        self.chars_dir = self.world_dir / "Characters"
        self.locs_dir = self.world_dir / "Locations"
        self.chars_dir.mkdir(parents=True)
        self.locs_dir.mkdir(parents=True)

        (self.chars_dir / "Aeloria.md").write_text(
            """---
name: "Aeloria Vael"
type: "character"
---
# Aeloria Vael
Master of the crystal greatsword.
""",
            encoding="utf-8",
        )

        (self.locs_dir / "Sanctuary.md").write_text(
            """---
name: "High Sanctuary"
type: "location"
---
# High Sanctuary
The floating citadel.
""",
            encoding="utf-8",
        )

        # Mock Manuscript & Outlines
        self.ms_dir = self.root / "Book-01" / "Draft-01"
        self.outlines_dir = self.root / "Book-01" / "Outlines"
        self.ms_dir.mkdir(parents=True)
        self.outlines_dir.mkdir(parents=True)

        (self.outlines_dir / "Master-Outline.md").write_text(
            """# Master Story Outline & Structural Blueprint

## 1. High Concept
- **Logline**: A disgraced inquisitor must stop a rogue sun conduit.

## 2. Multi-Act Milestone Matrix
- **ACT I**: Hook & Inciting Incident
- **ACT II**: Midpoint Turn
- **ACT III**: Climax Showdown
""",
            encoding="utf-8",
        )

        (self.outlines_dir / "Series-Outline.md").write_text(
            """# Series Chronicle

### 📖 Book 1: The Spark
Origin of the fire.

### 📖 Book 2: The Conflagration
War of the high peaks.
""",
            encoding="utf-8",
        )

        (self.ms_dir / "01_Ch1.md").write_text(
            """---
title: "The Fractured Spire"
chapter: 1
pov: "Kaelen"
location: "High Sanctuary"
characters: ["Kaelen", "Master Vance"]
plot_thread: "A-Plot: Treaty Seal"
time_marker: "Day 1 - Dawn"
status: "Draft"
target_words: 3000
synopsis: "Kaelen discovers the broken seal in the archives."
tags: ["intro", "mystery"]
---
# The Fractured Spire

Dawn broke over the high parapets.
""",
            encoding="utf-8",
        )
        (self.ms_dir / "02_Ch2.md").write_text(
            """---
title: "Shadows in the Deep"
chapter: 2
pov: "Aeloria"
status: "Revision"
---
# Shadows in the Deep

A cold mist rolled across the valley floor.
""",
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    # ------------------------------------------------------------------ #
    # 1. Lore Entity Scanning                                            #
    # ------------------------------------------------------------------ #
    def test_scan_lore_entities(self):
        """scan_lore_entities must discover characters and locations with correct metadata."""
        entities = scan_lore_entities(self.world_dir)
        self.assertEqual(len(entities), 2)
        names = {e["name"] for e in entities}
        self.assertIn("Aeloria Vael", names)
        self.assertIn("High Sanctuary", names)

    # ------------------------------------------------------------------ #
    # 2. Outline Discovery and Scanning                                  #
    # ------------------------------------------------------------------ #
    def test_scan_outlines(self):
        """scan_outlines must discover master outline, series outline, and floating templates."""
        outlines = scan_outlines(self.ms_dir, world_path=self.world_dir)
        self.assertIn("book_outline", outlines)
        self.assertIn("series_outline", outlines)
        self.assertIn("floating_templates", outlines)
        self.assertIn("discovered_files", outlines)

        self.assertIn("Master Story Outline", outlines["book_outline"]["raw"])
        self.assertIn("Series Chronicle", outlines["series_outline"]["raw"])
        self.assertGreaterEqual(len(outlines["floating_templates"]), 4)

    # ------------------------------------------------------------------ #
    # 3. Multi-Chapter Bundle Verification                               #
    # ------------------------------------------------------------------ #
    def test_multi_chapter_bundle_content(self):
        """build_zen_studio_bundle must embed all chapters in the manuscript with metadata."""
        out_html = self.root / "zen_multi.html"
        bundle_path = build_zen_studio_bundle(self.ms_dir, world_path=self.world_dir, output_path=out_html)
        self.assertTrue(bundle_path.exists())
        content = bundle_path.read_text(encoding="utf-8")
        self.assertIn("The Fractured Spire", content)
        self.assertIn("Shadows in the Deep", content)
        self.assertIn("Kaelen", content)
        self.assertIn("High Sanctuary", content)

    # ------------------------------------------------------------------ #
    # 4. In-Situ Document Metadata Inspector & Real-Time Sync             #
    # ------------------------------------------------------------------ #
    def test_zen_studio_metadata_inspector(self):
        """Bundle must contain metadata panel elements, two-way sync functions, and inputs."""
        out_html = self.root / "zen_meta.html"
        build_zen_studio_bundle(self.ms_dir, world_path=self.world_dir, output_path=out_html)
        content = out_html.read_text(encoding="utf-8")

        # Side panel container & header controls
        self.assertIn('id="metaPanel"', content)
        self.assertIn("Document Metadata", content)
        self.assertIn("btnMetaExpand", content)
        self.assertIn("btnMetaCollapse", content)

        # Form fields
        self.assertIn('id="metaTitle"', content)
        self.assertIn('id="metaPov"', content)
        self.assertIn('id="metaLocation"', content)
        self.assertIn('id="metaCast"', content)
        self.assertIn('id="metaThread"', content)
        self.assertIn('id="metaTime"', content)
        self.assertIn('id="metaStatus"', content)
        self.assertIn('id="metaTargetWords"', content)
        self.assertIn('id="metaSynopsis"', content)
        self.assertIn('id="metaTags"', content)

        # Two-way sync & helper logic
        self.assertIn("syncFrontmatterToEditor", content)
        self.assertIn("syncMetadataFromEditorText", content)
        self.assertIn("handleMetadataInput", content)
        self.assertIn("parseSimpleYaml", content)
        self.assertIn("serializeYaml", content)

    # ------------------------------------------------------------------ #
    # 5. Multi-Tier Narrative Outline Drawer                             #
    # ------------------------------------------------------------------ #
    def test_zen_studio_outline_drawer(self):
        """Bundle must include Floating, Book, and Series outline panels and actions."""
        out_html = self.root / "zen_outline.html"
        build_zen_studio_bundle(self.ms_dir, world_path=self.world_dir, output_path=out_html)
        content = out_html.read_text(encoding="utf-8")

        # Outline panel structure
        self.assertIn('id="outlinePanel"', content)
        self.assertIn("Narrative Outlines", content)
        self.assertIn("tabBtnFloating", content)
        self.assertIn("tabBtnBook", content)
        self.assertIn("tabBtnSeries", content)

        # Floating scratchpad
        self.assertIn('id="floatingOutlineText"', content)
        self.assertIn("floatingTemplateSelect", content)
        self.assertIn("insertFloatingBeatToEditor", content)
        self.assertIn("applyFloatingTemplate", content)

        # Book & Series renderers
        self.assertIn("renderBookOutline", content)
        self.assertIn("renderSeriesOutline", content)
        self.assertIn('id="bookOutlineContent"', content)
        self.assertIn('id="seriesOutlineContent"', content)

    # ------------------------------------------------------------------ #
    # 6. Ergonomic Expand / Collapse / Close & Shortcuts                #
    # ------------------------------------------------------------------ #
    def test_zen_studio_ergonomics_and_shortcuts(self):
        """Bundle must include expand/collapse/close toggle logic and keyboard shortcuts."""
        out_html = self.root / "zen_ergo.html"
        build_zen_studio_bundle(self.ms_dir, world_path=self.world_dir, output_path=out_html)
        content = out_html.read_text(encoding="utf-8")

        self.assertIn("togglePanelExpand", content)
        self.assertIn("togglePanelCollapse", content)
        self.assertIn("closePanel", content)
        self.assertIn("saveUIState", content)
        self.assertIn("loadUIState", content)

        # Keyboard shortcuts handlers in handleKeyDown
        self.assertIn('event.key.toLowerCase() === "m"', content)
        self.assertIn('event.key.toLowerCase() === "o"', content)
        self.assertIn('event.key.toLowerCase() === "b"', content)
        self.assertIn('event.key.toLowerCase() === "l"', content)

    # ------------------------------------------------------------------ #
    # 7. Strict Content Security Policy                                  #
    # ------------------------------------------------------------------ #
    def test_zen_studio_csp_compliance(self):
        """Zen studio HTML must declare default-src 'none' and offline privacy isolation."""
        out_html = self.root / "zen_csp.html"
        build_zen_studio_bundle(self.ms_dir, world_path=self.world_dir, output_path=out_html)
        content = out_html.read_text(encoding="utf-8")
        self.assertIn("default-src 'none'", content)
        self.assertIn("style-src 'unsafe-inline'", content)
        self.assertIn("script-src 'unsafe-inline'", content)

    # ------------------------------------------------------------------ #
    # 8. Zen Editor Textarea Workspace                                   #
    # ------------------------------------------------------------------ #
    def test_zen_studio_editor_area(self):
        """Bundle must include textarea.zen-editor with Georgia/serif styling."""
        out_html = self.root / "zen_editor.html"
        build_zen_studio_bundle(self.ms_dir, world_path=self.world_dir, output_path=out_html)
        content = out_html.read_text(encoding="utf-8")
        self.assertIn("zen-editor", content)
        self.assertIn("editor-area", content)

    # ------------------------------------------------------------------ #
    # 9. Theme CSS Variables                                             #
    # ------------------------------------------------------------------ #
    def test_zen_studio_css_variables(self):
        """Bundle must define CSS root variables for themes and high contrast."""
        out_html = self.root / "zen_themes.html"
        build_zen_studio_bundle(self.ms_dir, world_path=self.world_dir, output_path=out_html)
        content = out_html.read_text(encoding="utf-8")
        self.assertIn("--bg:", content)
        self.assertIn("--text:", content)
        self.assertIn("--accent:", content)

    # ------------------------------------------------------------------ #
    # 10. Lore Drawer Search and Entity Filtering                        #
    # ------------------------------------------------------------------ #
    def test_zen_studio_lore_search_filter(self):
        """Bundle JavaScript must include filterLore / query filtering logic."""
        out_html = self.root / "zen_lore_filter.html"
        build_zen_studio_bundle(self.ms_dir, world_path=self.world_dir, output_path=out_html)
        content = out_html.read_text(encoding="utf-8")
        self.assertIn("loreQuery", content)
        self.assertIn("filterDrawer", content)
        self.assertIn("lore-drawer", content)

    # ------------------------------------------------------------------ #
    # 11. Word Count and Reading Time Telemetry                          #
    # ------------------------------------------------------------------ #
    def test_zen_studio_telemetry_elements(self):
        """Bundle must include telWords, telChars, and telReadTime telemetry spans."""
        out_html = self.root / "zen_telemetry.html"
        build_zen_studio_bundle(self.ms_dir, world_path=self.world_dir, output_path=out_html)
        content = out_html.read_text(encoding="utf-8")
        self.assertIn("telWords", content)
        self.assertIn("telChars", content)
        self.assertIn("telReadTime", content)

    # ------------------------------------------------------------------ #
    # 12. Sidebar Chapter Navigation Controls                            #
    # ------------------------------------------------------------------ #
    def test_zen_studio_sidebar_navigation(self):
        """Bundle must include chapter sidebar list and toggleSidebar function."""
        out_html = self.root / "zen_sidebar.html"
        build_zen_studio_bundle(self.ms_dir, world_path=self.world_dir, output_path=out_html)
        content = out_html.read_text(encoding="utf-8")
        self.assertIn("sidebar", content)
        self.assertIn("chapList", content)
        self.assertIn("toggleSidebar", content)

    # ------------------------------------------------------------------ #
    # 13. Standalone Studio Without World Lore                           #
    # ------------------------------------------------------------------ #
    def test_build_zen_studio_without_world(self):
        """build_zen_studio_bundle must function cleanly when world_path is None."""
        out_html = self.root / "zen_no_world.html"
        bundle_path = build_zen_studio_bundle(self.ms_dir, world_path=None, output_path=out_html)
        self.assertTrue(bundle_path.exists())
        content = bundle_path.read_text(encoding="utf-8")
        self.assertIn("The Fractured Spire", content)

    # ------------------------------------------------------------------ #
    # 14. Empty Manuscript Default Initialization                        #
    # ------------------------------------------------------------------ #
    def test_build_zen_studio_empty_manuscript(self):
        """Empty manuscript directory should compile clean empty studio HTML."""
        empty_ms = self.root / "Empty_Manuscript"
        empty_ms.mkdir()
        out_html = self.root / "zen_empty.html"
        bundle_path = build_zen_studio_bundle(empty_ms, world_path=None, output_path=out_html)
        self.assertTrue(bundle_path.exists())
        content = bundle_path.read_text(encoding="utf-8")
        self.assertIn("Ars Arcanum Zen Studio", content)

    # ------------------------------------------------------------------ #
    # 15. CLI Options & Main Execution                                   #
    # ------------------------------------------------------------------ #
    def test_cli_main_and_options(self):
        import io
        import json
        from unittest.mock import patch
        from lib.zen_studio import main

        out_html = self.root / "cli_zen.html"

        # JSON mode
        with patch("sys.argv", ["zen_studio.py", str(self.ms_dir), "--world", str(self.world_dir), "--output", str(out_html), "--json"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                main()
                data = json.loads(mock_stdout.getvalue())
                self.assertEqual(data["status"], "ready")
                self.assertTrue(out_html.is_file())

        # Human readable
        with patch("sys.argv", ["zen_studio.py", str(self.ms_dir), "--world", str(self.world_dir)]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                main()
                self.assertIn("Sovereign Zen Studio", mock_stdout.getvalue())

        # Error path
        with patch("sys.argv", ["zen_studio.py", "nonexistent_dir_123"]):
            with patch("sys.stderr", new_callable=io.StringIO):
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
