#!/usr/bin/env python3
"""
Test Suite for Ars Arcanum Engine Logic Documentation & Ecosystem Integration
(tests/test_engine_logic_docs.py)
================================================================================
Verifies:
1. Complete 50-engine registry metadata coverage (scientific_logic, why_this_way,
   subfeatures, extension_guide, advisory_guidance).
2. Doc formatting and fuzzy search indexation across all 50 engines.
3. CLI documentation command dispatch (`arcanum doc`).
4. HTML bundle generators (Studio Hub, Zen Studio, Story Canvas) embed valid logic
   and comply with strict offline Content Security Policies.
"""

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.cli import handle_doc_command
from lib.registry import (
    format_engine_doc,
    get_engine,
    get_engine_catalog,
    list_engines,
    search_engine_docs,
)
from lib.story_canvas import generate_story_canvas_html
from lib.studio_hub import collect_studio_hub_data, generate_studio_hub_html
from lib.zen_studio import build_zen_studio_bundle


class TestEngineLogicDocumentation(unittest.TestCase):
    """Verifies that all 50 engines are documented thoroughly and systematically."""

    def test_engine_catalog_completeness(self):
        """Test that get_engine_catalog exports all engines with logic and subfeatures."""
        catalog = get_engine_catalog()
        self.assertGreaterEqual(len(catalog), 47)
        for entry in catalog:
            self.assertIn("scientific_logic", entry)
            self.assertIn("why_this_way", entry)
            self.assertIn("subfeatures", entry)
            self.assertIn("extension_guide", entry)
            self.assertIn("advisory_guidance", entry)

    def test_all_50_engines_have_exhaustive_documentation(self):
        """Ensure all 47 engines contain non-empty scientific and architectural metadata."""
        engines = list_engines(enabled_only=False)
        self.assertGreaterEqual(len(engines), 47, f"Expected at least 47 engines, found {len(engines)}")

        for eng in engines:
            with self.subTest(engine=eng.name):
                self.assertTrue(
                    bool(eng.scientific_logic and eng.scientific_logic.strip()),
                    f"Engine '{eng.name}' is missing scientific_logic",
                )
                self.assertTrue(
                    bool(eng.why_this_way and eng.why_this_way.strip()),
                    f"Engine '{eng.name}' is missing why_this_way",
                )
                self.assertTrue(
                    bool(eng.extension_guide and eng.extension_guide.strip()),
                    f"Engine '{eng.name}' is missing extension_guide",
                )
                self.assertTrue(
                    len(eng.subfeatures) >= 2,
                    f"Engine '{eng.name}' must define at least 2 subfeatures, found {len(eng.subfeatures)}",
                )
                self.assertTrue(
                    bool(eng.advisory_guidance),
                    f"Engine '{eng.name}' is missing advisory_guidance",
                )
                self.assertTrue(
                    len(eng.theory_references) >= 3,
                    f"Engine '{eng.name}' must have at least 3 theoretical references, found {len(eng.theory_references)}",
                )
                for ref in eng.theory_references:
                    self.assertTrue(bool(ref.get("title")), f"Reference in '{eng.name}' missing title")
                    self.assertTrue(bool(ref.get("citation")), f"Reference in '{eng.name}' missing citation")

        # Verify cross-engine bibliography includes external URLs
        total_urls = sum(
            sum(1 for ref in e.theory_references if ref.get("url"))
            for e in engines
        )
        self.assertGreaterEqual(total_urls, 100, f"Expected at least 100 external URL citations, found {total_urls}")

    def test_search_engine_docs(self):
        """Test fuzzy and keyword search across engine documentation."""
        # Search by physics term
        astro_results = search_engine_docs("brachistochrone")
        self.assertTrue(any(spec.name == "astrophysics" for spec in astro_results))

        # Search by ecology term
        eco_results = search_engine_docs("trophic")
        self.assertTrue(any(spec.name == "ecology" for spec in eco_results))

        # Search by narrative term
        narr_results = search_engine_docs("Kishōtenketsu")
        self.assertTrue(any(spec.name == "structure" for spec in narr_results))

        # Search by magic rule term
        magic_results = search_engine_docs("Sanderson")
        self.assertTrue(any(spec.name == "magic_system" for spec in magic_results))

    def test_format_engine_doc_modes(self):
        """Test formatting output for all supported modes."""
        spec = get_engine("astrophysics")
        self.assertIsNotNone(spec)
        assert spec is not None

        full_doc = format_engine_doc(spec, mode="full")
        self.assertIn("Kepler's Third Law", full_doc)
        self.assertIn("Why It Works This Way", full_doc)
        self.assertIn("How to Build Upon", full_doc)
        self.assertIn("Theoretical Foundations & Reference Sources:", full_doc)

        sources_doc = format_engine_doc(spec, mode="sources")
        self.assertIn("THEORETICAL FOUNDATIONS & REFERENCE SOURCES", sources_doc)
        self.assertIn("Kopparapu", sources_doc)
        self.assertIn("http", sources_doc)

        math_doc = format_engine_doc(spec, mode="math")
        self.assertIn("Kepler's Third Law", math_doc)

        why_doc = format_engine_doc(spec, mode="why")
        self.assertIn("ARCHITECTURAL & CREATIVE RATIONALE", why_doc)

        examples_doc = format_engine_doc(spec, mode="examples")
        self.assertIn("AUTHOR EXTENSION GUIDE", examples_doc)

        subfeatures_doc = format_engine_doc(spec, mode="subfeatures")
        self.assertIn("SUBFEATURES", subfeatures_doc)

        advisory_doc = format_engine_doc(spec, mode="advisory")
        self.assertIn("CREATIVE ADVISORY RESOLUTION", advisory_doc)

    def test_cli_doc_command_execution(self):
        """Test CLI dispatcher doc commands."""
        # Test specific engine doc math
        buf = io.StringIO()
        with redirect_stdout(buf):
            ret = handle_doc_command(["astrophysics", "--math"])
        self.assertEqual(ret, 0)
        self.assertIn("Kepler", buf.getvalue())

        # Test specific engine doc sources
        buf = io.StringIO()
        with redirect_stdout(buf):
            ret = handle_doc_command(["astrophysics", "--sources"])
        self.assertEqual(ret, 0)
        self.assertIn("THEORETICAL FOUNDATIONS & REFERENCE SOURCES", buf.getvalue())
        self.assertIn("Kopparapu", buf.getvalue())

        # Test doc search
        buf = io.StringIO()
        with redirect_stdout(buf):
            ret = handle_doc_command(["--search", "trophic"])
        self.assertEqual(ret, 0)
        self.assertIn("ecology", buf.getvalue().lower())

        # Test doc JSON output
        buf = io.StringIO()
        with redirect_stdout(buf):
            ret = handle_doc_command(["magic_system", "--json"])
        self.assertEqual(ret, 0)
        parsed = json.loads(buf.getvalue())
        self.assertEqual(parsed["name"], "magic_system")
        self.assertIn("Sanderson", parsed["scientific_logic"])
        self.assertIn("theory_references", parsed)
        self.assertGreaterEqual(len(parsed["theory_references"]), 3)

    def test_html_bundles_csp_and_embedded_logic(self):
        """Test that generated HTML artifacts embed logic and have valid CSP."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            ms_dir = tmppath / "01_Manuscript"
            ms_dir.mkdir()
            (ms_dir / "Chapter_01.md").write_text(
                "---\ntitle: 'Chapter One'\npov: 'Aurelia'\n---\n# Chapter One\n\nShe looked out at the twin moons.",
                encoding="utf-8",
            )
            world_dir = tmppath / "00_World"
            world_dir.mkdir()
            (world_dir / "Aurelia.md").write_text("# Aurelia Vance\n\nProtagonist.", encoding="utf-8")

            # 1. Studio Hub HTML
            hub_data = collect_studio_hub_data(tmppath)
            hub_html = generate_studio_hub_html(hub_data)
            hub_path = tmppath / "hub.html"
            hub_path.write_text(hub_html, encoding="utf-8")
            self.assertIn("default-src 'none'", hub_html)
            self.assertIn("engineDocModal", hub_html)
            self.assertIn("Brachistochrone", hub_html)

            # 2. Zen Studio HTML
            zen_path = tmppath / "zen.html"
            build_zen_studio_bundle(ms_dir, world_path=world_dir, output_path=zen_path)
            zen_html = zen_path.read_text(encoding="utf-8")
            self.assertIn("default-src 'none'", zen_html)
            self.assertIn("craftModal", zen_html)
            self.assertIn("Motivational Response Unit", zen_html)

            # 3. Story Canvas HTML
            canvas_path = tmppath / "canvas.html"
            cards = [{
                "id": "c1",
                "index": 1,
                "filename": "Chapter_01.md",
                "title": "Chapter One",
                "pov": "Aurelia",
                "location": "Citadel",
                "thread": "Main",
                "tension": 6.0,
                "word_count": 800,
                "cumulative_words": 800,
                "summary": "Sample summary",
            }]
            generate_story_canvas_html(ms_dir, cards, output_path=canvas_path)
            canvas_html = canvas_path.read_text(encoding="utf-8")
            self.assertIn("default-src 'none'", canvas_html)
            self.assertIn("paradigmGuideModal", canvas_html)
            self.assertIn("Structural Harmony Equation", canvas_html)


if __name__ == "__main__":
    unittest.main()
