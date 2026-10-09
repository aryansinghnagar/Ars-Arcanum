#!/usr/bin/env python3
"""
Test Suite for Ars Arcanum Engine Logic Documentation & Ecosystem Integration
(tests/test_engine_logic_docs.py)
================================================================================
Verifies:
1. Complete 14-engine registry metadata coverage (scientific_logic, why_this_way,
   subfeatures, extension_guide, advisory_guidance).
2. Doc formatting and fuzzy search indexation across sovereign engines.
3. CLI documentation command dispatch (`arcanum doc`).
4. HTML bundle generators (Codex Export, Revision Heatmap, Omnibus) embed valid logic
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
from lib.codex_export import build_single_file_codex, scan_world_vault
from lib.omnibus import (
    compile_omnibus_manuscript,
    discover_series_volumes,
    generate_omnibus_html_reader,
)
from lib.registry import (
    format_engine_doc,
    get_engine,
    get_engine_catalog,
    list_engines,
    search_engine_docs,
)
from lib.revision_heatmap import generate_revision_heatmap_html


class TestEngineLogicDocumentation(unittest.TestCase):
    """Verifies that all 14 sovereign core engines are documented thoroughly and systematically."""

    def test_engine_catalog_completeness(self):
        """Test that get_engine_catalog exports all engines with logic and subfeatures."""
        catalog = get_engine_catalog()
        self.assertEqual(len(catalog), 17)
        for entry in catalog:
            self.assertIn("scientific_logic", entry)
            self.assertIn("why_this_way", entry)
            self.assertIn("subfeatures", entry)
            self.assertIn("extension_guide", entry)
            self.assertIn("advisory_guidance", entry)

    def test_all_14_engines_have_exhaustive_documentation(self):
        """Ensure all engines contain non-empty scientific and architectural metadata."""
        engines = list_engines(enabled_only=False)
        self.assertEqual(len(engines), 17)


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

    def test_search_engine_docs(self):
        """Test fuzzy and keyword search across engine documentation."""
        # Search by revision term
        rev_results = search_engine_docs("churn")
        self.assertTrue(any(spec.name == "revision_heatmap" for spec in rev_results))

        # Search by wiki/codex term
        codex_results = search_engine_docs("encyclopedia")
        self.assertTrue(any(spec.name == "codex_export" for spec in codex_results))

        # Search by diff term
        diff_results = search_engine_docs("redline")
        self.assertTrue(any(spec.name == "manuscript_diff" for spec in diff_results))

    def test_format_engine_doc_modes(self):
        """Test formatting output for all supported modes."""
        spec = get_engine("revision_heatmap")
        self.assertIsNotNone(spec)
        assert spec is not None

        full_doc = format_engine_doc(spec, mode="full")
        self.assertIn("Word Churn Ratio", full_doc)
        self.assertIn("Why It Works This Way", full_doc)
        self.assertIn("How to Build Upon", full_doc)

        sources_doc = format_engine_doc(spec, mode="sources")
        self.assertIn("THEORETICAL FOUNDATIONS & REFERENCE SOURCES", sources_doc)

        math_doc = format_engine_doc(spec, mode="math")
        self.assertIn("Word Churn Ratio", math_doc)

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
            ret = handle_doc_command(["revision_heatmap", "--math"])
        self.assertEqual(ret, 0)
        self.assertIn("Churn", buf.getvalue())

        # Test specific engine doc sources
        buf = io.StringIO()
        with redirect_stdout(buf):
            ret = handle_doc_command(["revision_heatmap", "--sources"])
        self.assertEqual(ret, 0)
        self.assertIn("THEORETICAL FOUNDATIONS & REFERENCE SOURCES", buf.getvalue())

        # Test doc search
        buf = io.StringIO()
        with redirect_stdout(buf):
            ret = handle_doc_command(["--search", "churn"])
        self.assertEqual(ret, 0)
        self.assertIn("revision-heatmap", buf.getvalue().lower())

        # Test doc JSON output
        buf = io.StringIO()
        with redirect_stdout(buf):
            ret = handle_doc_command(["revision_heatmap", "--json"])
        self.assertEqual(ret, 0)
        parsed = json.loads(buf.getvalue())
        self.assertEqual(parsed["name"], "revision_heatmap")
        self.assertIn("scientific_logic", parsed)
        self.assertIn("theory_references", parsed)

    def test_html_bundles_csp_and_embedded_logic(self):
        """Test that generated HTML artifacts embed logic and have valid CSP."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            world_dir = tmppath / "World"
            char_dir = world_dir / "Characters"
            char_dir.mkdir(parents=True, exist_ok=True)
            (char_dir / "Aurelia.md").write_text("---\nname: Aurelia\ncategory: Characters\n---\n# Aurelia\nProtagonist.", encoding="utf-8")

            # 1. Codex Export HTML
            cats = scan_world_vault(world_dir)
            codex_path = tmppath / "codex.html"
            build_single_file_codex(cats, world_name="TestWorld", output_path=codex_path)
            codex_html = codex_path.read_text(encoding="utf-8")
            self.assertIn("default-src 'none'", codex_html)
            self.assertIn("Aurelia", codex_html)

            # 2. Revision Heatmap HTML
            from lib.revision_heatmap import ChapterRevisionStats
            heatmap_path = tmppath / "heatmap.html"
            sample_stats = [ChapterRevisionStats(
                chapter="01_Chapter.md",
                rel_path="01_Chapter.md",
                word_count=1200,
                insertions=50,
                deletions=20,
                churn_score=70,
                churn_ratio=0.058,
                has_snapshot=True,
                flag="REV-101",
            )]
            sample_data = {
                "manuscript": "TestManuscript",
                "total_words": 1200,
                "total_insertions": 50,
                "total_deletions": 20,
                "avg_churn_score": 70.0,
                "chapters": sample_stats,
            }
            generate_revision_heatmap_html(sample_data, heatmap_path)
            heatmap_html = heatmap_path.read_text(encoding="utf-8")
            self.assertIn("default-src 'none'", heatmap_html)

            # 3. Omnibus HTML
            ms1 = tmppath / "Manuscripts" / "Book-01" / "Draft-01"
            ms1.mkdir(parents=True, exist_ok=True)
            (tmppath / "Manuscripts" / "Book-01" / "manuscript.yaml").write_text("title: Book 1\nauthor: Author\n", encoding="utf-8")
            (ms1 / "01_Ch1.md").write_text("# Chapter 1\n\nContent here.", encoding="utf-8")
            vols = discover_series_volumes(tmppath / "Manuscripts")
            report = compile_omnibus_manuscript(vols, "Test Omnibus", "Author")
            omnibus_path = tmppath / "omnibus.html"
            generate_omnibus_html_reader(report, omnibus_path)
            self.assertTrue(omnibus_path.is_file())
            omnibus_html = omnibus_path.read_text(encoding="utf-8")
            self.assertIn("default-src 'none'", omnibus_html)


if __name__ == "__main__":
    unittest.main()
