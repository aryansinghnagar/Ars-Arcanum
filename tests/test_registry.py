#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Engine & Plugin Registry (scripts/lib/registry.py)
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib.registry import (
    EngineCategory,
    disable_engine,
    enable_engine,
    format_engine_doc,
    get_all_engine_docs,
    get_core_engines,
    get_craft_engines,
    get_engine,
    get_engine_docs,
    get_registry,
    is_engine_enabled,
    load_engine_module,
)


class TestRegistry(unittest.TestCase):

    def test_registry_contains_core_and_craft_engines(self):
        reg = get_registry()
        self.assertEqual(len(reg), 14)

        # Check core engines present
        core = get_core_engines()
        core_names = {e.name for e in core}
        self.assertIn("config", core_names)
        self.assertIn("cache", core_names)
        self.assertIn("fs_utils", core_names)
        self.assertIn("migrate", core_names)
        self.assertIn("docx_sync", core_names)
        self.assertIn("diagnostics", core_names)
        self.assertIn("manuscript_diff", core_names)
        self.assertIn("portfolio", core_names)
        self.assertIn("importer", core_names)
        self.assertIn("preflight", core_names)
        self.assertIn("frontmatter_builder", core_names)
        self.assertIn("omnibus", core_names)

        # Check craft engines present
        craft = get_craft_engines()
        craft_names = {e.name for e in craft}
        self.assertIn("revision_heatmap", craft_names)
        self.assertIn("codex_export", craft_names)

    def test_get_engine_by_name_and_alias(self):
        # By primary name
        eng = get_engine("docx_sync")
        self.assertIsNotNone(eng)
        self.assertEqual(eng.category, EngineCategory.CORE)
        self.assertEqual(eng.cli_command, "sync-docx")

        # By alias
        eng_alias = get_engine("diff")
        self.assertIsNotNone(eng_alias)
        self.assertEqual(eng_alias.name, "manuscript_diff")

        # Unknown
        self.assertIsNone(get_engine("non_existent_engine_xyz"))

    def test_enable_disable_engine(self):
        self.assertTrue(is_engine_enabled("codex_export"))
        disable_engine("codex_export")
        self.assertFalse(is_engine_enabled("codex_export"))

        # list_engines with enabled_only=True should exclude it
        enabled_craft = get_craft_engines(enabled_only=True)
        self.assertNotIn("codex_export", {e.name for e in enabled_craft})

        # Re-enable
        enable_engine("codex_export")
        self.assertTrue(is_engine_enabled("codex_export"))
        enabled_craft_after = get_craft_engines(enabled_only=True)
        self.assertIn("codex_export", {e.name for e in enabled_craft_after})

    def test_load_engine_module(self):
        mod = load_engine_module("fs_utils")
        self.assertTrue(hasattr(mod, "atomic_write"))

    def test_get_engine_lookups_and_aliases(self):
        # Hyphenated vs underscore
        self.assertIsNotNone(get_engine("docx-sync"))
        self.assertIsNotNone(get_engine("manuscript-diff"))
        self.assertIsNotNone(get_engine("revision-heatmap"))
        self.assertIsNotNone(get_engine("codex-export"))
        self.assertIsNotNone(get_engine("frontmatter-builder"))

        # Aliases and CLI commands
        self.assertIsNotNone(get_engine("compare"))
        self.assertIsNotNone(get_engine("redline"))
        self.assertIsNotNone(get_engine("portfolio"))
        self.assertIsNotNone(get_engine("diff"))

    def test_get_engine_docs(self):
        doc = get_engine_docs("codex_export")
        self.assertIsNotNone(doc)
        assert doc is not None
        self.assertEqual(doc["name"], "codex_export")
        self.assertEqual(doc["studio_tab"], "Publishing")
        self.assertTrue(len(doc["logic_documentation"]) > 10)
        self.assertTrue(len(doc["worldbuilding_relevance"]) > 10)
        self.assertTrue(len(doc["storytelling_relevance"]) > 10)
        self.assertTrue(len(doc["writing_relevance"]) > 10)
        self.assertGreaterEqual(len(doc["advisory_guidance"]), 1)
        self.assertIn("theory_references", doc)
        self.assertGreaterEqual(len(doc["theory_references"]), 1)

        # Hyphenated lookup in get_engine_docs
        doc_hyphen = get_engine_docs("codex-export")
        self.assertIsNotNone(doc_hyphen)
        assert doc_hyphen is not None
        self.assertEqual(doc_hyphen["name"], "codex_export")
        self.assertGreaterEqual(len(doc_hyphen["theory_references"]), 1)

        # Non-existent
        self.assertIsNone(get_engine_docs("non_existent_fake"))

    def test_get_all_engine_docs(self):
        all_docs = get_all_engine_docs()
        self.assertEqual(len(all_docs), 14)
        for d in all_docs:
            self.assertIn("name", d)
            self.assertIn("title", d)
            self.assertIn("category", d)
            self.assertIn("studio_tab", d)
            self.assertIn("logic_documentation", d)
            self.assertIn("worldbuilding_relevance", d)
            self.assertIn("storytelling_relevance", d)
            self.assertIn("writing_relevance", d)
            self.assertIn("advisory_guidance", d)
            self.assertIn("theory_references", d)
            for adv in d["advisory_guidance"]:
                self.assertIn("pattern", adv)
                self.assertIn("option_a", adv)
                self.assertIn("option_b", adv)
                self.assertIn("option_c", adv)

    def test_format_engine_doc(self):
        formatted = format_engine_doc("codex_export")
        self.assertIn("WORLD WIKI CODEX EXPORT", formatted)
        self.assertIn("Engine Logic & Scientific / Structural Foundations:", formatted)
        self.assertIn("Advisory Mechanics & Creative Freedom Resolution Pathways:", formatted)
        self.assertIn("Theoretical Foundations & Reference Sources:", formatted)

        # Sources mode
        sources_fmt = format_engine_doc("codex_export", mode="sources")
        self.assertIn("THEORETICAL FOUNDATIONS & REFERENCE SOURCES", sources_fmt)
        self.assertIn("Citation:", sources_fmt)

        # Formatted via hyphenated string
        formatted_hyphen = format_engine_doc("codex-export")
        self.assertIn("WORLD WIKI CODEX EXPORT", formatted_hyphen)

        # Unknown
        unknown_fmt = format_engine_doc("fake_xyz")
        self.assertIn("No documentation available", unknown_fmt)


if __name__ == "__main__":
    unittest.main()
