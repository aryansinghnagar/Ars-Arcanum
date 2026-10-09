#!/usr/bin/env python3
"""
Tests for Ars Arcanum Isolated Presentation Templates (tests/test_template_isolation.py)
Validates 100% offline isolation, strict CSP declarations, and no remote dependencies.
"""

from __future__ import annotations

import re
import shutil
import tempfile
import unittest
from pathlib import Path

from lib.codex_export_template import render_codex_html
from lib.omnibus_template import render_omnibus_html
from lib.portfolio_template import render_portfolio_html
from lib.preflight_template import render_preflight_html


class TestTemplateIsolation(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp(prefix="arcanum_test_templates_"))

    def tearDown(self):
        if self.tmp_dir.exists():
            shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def _assert_strict_csp(self, html: str):
        """Validates that strict Content Security Policy is present and disallows remote scripts/styles."""
        self.assertIn("<meta http-equiv=\"Content-Security-Policy\"", html)
        self.assertIn("default-src 'none'", html)
        # Check no external CDN or http/https links
        self.assertFalse(re.search(r'https?://[^\s"\'<>]+(?:\.js|\.css|\.woff|\.ttf)', html, re.IGNORECASE))
        self.assertNotIn("unpkg.com", html)
        self.assertNotIn("cdn.", html)
        self.assertNotIn("cdnjs.", html)
        self.assertNotIn("googleapis.", html)

    def test_omnibus_template_rendering_and_csp(self):
        out_file = self.tmp_dir / "omnibus.html"
        report = {
            "title": "The Grand Omnibus",
            "author": "Test Author",
            "volumes": [
                {
                    "title": "The Awakening",
                    "index": 1,
                    "word_count": 50000,
                    "chapters": [
                        {"title": "Prologue", "pov": "Lyra", "words": 2500, "body": "First chapter text."},
                    ],
                }
            ],
            "total_words": 50000,
        }
        res_path = render_omnibus_html(report, out_file)
        self.assertTrue(res_path.is_file())
        html = res_path.read_text(encoding="utf-8")
        self._assert_strict_csp(html)
        self.assertIn("The Grand Omnibus", html)
        self.assertIn("The Awakening", html)
        self.assertIn("First chapter text.", html)

    def test_codex_export_template_rendering_and_csp(self):
        out_file = self.tmp_dir / "codex.html"
        categories = {
            "Locations": [
                {
                    "clean_id": "citadel",
                    "title": "Citadel of Light",
                    "category": "Locations",
                    "body_html": "<p>A grand citadel upon the mountain.</p>",
                    "frontmatter": {"climate": "Alpine", "elevation": "3000m"},
                }
            ]
        }
        res_path = render_codex_html(categories, "Aethelgard", out_file)
        self.assertTrue(res_path.is_file())
        html = res_path.read_text(encoding="utf-8")
        self._assert_strict_csp(html)
        self.assertIn("Aethelgard", html)
        self.assertIn("Citadel of Light", html)

    def test_preflight_template_rendering_and_csp(self):
        out_file = self.tmp_dir / "preflight.html"
        report = {
            "manuscript": "Crown of Shadows",
            "title": "Crown of Shadows",
            "total_words": 75000,
            "chapter_count": 12,
            "fail_count": 0,
            "warn_count": 1,
            "issues": [
                {
                    "code": "CHK-002",
                    "level": "WARN",
                    "file": "02_Chapter_01.md",
                    "line": 15,
                    "message": "Duplicate scene heading observed.",
                }
            ],
        }
        res_path = render_preflight_html(report, out_file)
        self.assertTrue(res_path.is_file())
        html = res_path.read_text(encoding="utf-8")
        self._assert_strict_csp(html)
        self.assertIn("Crown of Shadows", html)
        self.assertIn("CHK-002", html)

    def test_portfolio_template_rendering_and_csp(self):
        out_file = self.tmp_dir / "portfolio.html"
        report = {
            "total_manuscripts": 1,
            "total_words": 80000,
            "target_words": 80000,
            "overall_progress_pct": 100.0,
            "projects": [
                {
                    "title": "Crown of Shadows",
                    "path": "/path/to/ms1",
                    "stage": "Drafting",
                    "word_count": 80000,
                    "target_words": 80000,
                    "progress_pct": 100.0,
                    "volume_count": 1,
                    "chapter_count": 12,
                }
            ],
        }
        res_path = render_portfolio_html(report, out_file)
        self.assertTrue(res_path.is_file())
        html = res_path.read_text(encoding="utf-8")
        self._assert_strict_csp(html)
        self.assertIn("Author Portfolio", html)
        self.assertIn("Crown of Shadows", html)


if __name__ == "__main__":
    unittest.main()
