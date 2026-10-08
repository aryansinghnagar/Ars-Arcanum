#!/usr/bin/env python3
"""
Tests for Unified Craft Library Master Bibliography (tests/test_unified_bibliography.py)
========================================================================================
Verifies cross-engine bibliography aggregation, deduplication, formatting (text, markdown, JSON),
category filtering, and CLI integration.
"""

import json
import unittest

from scripts.lib.cli import handle_doc_command
from scripts.lib.registry import (
    format_unified_bibliography,
    get_unified_bibliography,
)


class TestUnifiedBibliography(unittest.TestCase):
    """Verifies that the unified master bibliography indexes references across all engines."""

    def test_bibliography_aggregation_not_empty(self) -> None:
        bib = get_unified_bibliography()
        self.assertGreater(len(bib), 100, "Master bibliography should index hundreds of scholarly/craft sources.")

    def test_bibliography_entry_structure(self) -> None:
        bib = get_unified_bibliography()
        sample = bib[0]
        self.assertIn("title", sample)
        self.assertIn("citation", sample)
        self.assertIn("description", sample)
        self.assertIn("engines", sample)
        self.assertIn("categories", sample)
        self.assertIsInstance(sample["engines"], list)
        self.assertGreater(len(sample["engines"]), 0)

    def test_bibliography_category_filtering(self) -> None:
        craft_bib = get_unified_bibliography(category="craft")
        core_bib = get_unified_bibliography(category="core")
        total_bib = get_unified_bibliography()

        self.assertGreater(len(craft_bib), 0)
        self.assertGreater(len(core_bib), 0)
        self.assertGreaterEqual(len(total_bib), len(craft_bib))
        for item in craft_bib:
            self.assertIn("craft", item["categories"])

    def test_bibliography_format_json(self) -> None:
        json_str = format_unified_bibliography(format_type="json")
        data = json.loads(json_str)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 100)

    def test_bibliography_format_markdown(self) -> None:
        md_str = format_unified_bibliography(format_type="markdown")
        self.assertIn("# Ars Arcanum Sovereign Craft Library — Unified Master Bibliography", md_str)
        self.assertIn("Associated Engines", md_str)

    def test_bibliography_format_text(self) -> None:
        text_str = format_unified_bibliography(format_type="text")
        self.assertIn("ARS ARCANUM CRAFT LIBRARY — UNIFIED MASTER BIBLIOGRAPHY", text_str)
        self.assertIn("Indexed Works", text_str)

    def test_cli_doc_bibliography_routing(self) -> None:
        # Test that CLI returns 0 on bib subcommands
        self.assertEqual(handle_doc_command(["bib"]), 0)
        self.assertEqual(handle_doc_command(["bibliography", "--json"]), 0)
        self.assertEqual(handle_doc_command(["citations", "--markdown"]), 0)
        self.assertEqual(handle_doc_command(["sources", "--craft"]), 0)


if __name__ == "__main__":
    unittest.main()
