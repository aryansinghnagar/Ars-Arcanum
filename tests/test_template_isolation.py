#!/usr/bin/env python3
"""
Tests for Ars Arcanum Isolated Presentation Templates (tests/test_template_isolation.py)
Validates 100% offline isolation, strict CSP declarations, and no remote dependencies.
"""

from __future__ import annotations

import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

TEST_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TEST_DIR.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.codex_export_template import render_codex_html
from lib.docx_sync_template import render_docx_studio_html
from lib.draft_manager_template import generate_draft_dashboard_html
from lib.importer_template import render_import_studio_html
from lib.manuscript_diff_template import render_manuscript_diff_html
from lib.omnibus_template import render_omnibus_html
from lib.portfolio_template import render_portfolio_html
from lib.preflight_template import render_preflight_html
from lib.revision_heatmap_template import generate_revision_heatmap_html
from lib.velocity_template import render_velocity_html


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

    def test_manuscript_diff_template_rendering_and_csp(self):
        summary = {
            "label_a": "Draft-01",
            "label_b": "Draft-02",
            "total_words_a": 5000,
            "total_words_b": 5200,
            "added_words": 400,
            "deleted_words": 200,
            "moved_words": 150,
            "net_change": 200,
            "similarity_ratio": 0.88,
        }
        chapters = [
            {
                "title": "Chapter 1: The Gathering",
                "rel_path": "01_Act_I/01_Chapter_01.md",
                "words_a": 2500,
                "words_b": 2600,
                "added_words": 200,
                "deleted_words": 100,
                "moved_words": 50,
                "net_change": 100,
                "similarity": 0.90,
                "chunks": [
                    {"tag": "equal", "text": "The wind howled across the plains."},
                    {"tag": "insert", "text": " A single cloaked figure appeared."},
                ],
                "split_pairs": [
                    {"tag": "equal", "text_a": "The wind howled.", "text_b": "The wind howled."},
                ],
            }
        ]
        html_out = render_manuscript_diff_html(summary, chapters, "Draft-01", "Draft-02")
        self._assert_strict_csp(html_out)
        self.assertIn("Editorial Studio", html_out)
        self.assertIn("The Gathering", html_out)
        self.assertIn("tab-unified", html_out)
        self.assertIn("tab-split", html_out)

    def test_docx_studio_template_rendering_and_csp(self):
        out_file = self.tmp_dir / "docx_studio.html"
        report = {
            "manuscript": "The Silver Citadel",
            "draft": "Draft-01",
            "active_preset": "chicago-manual",
            "presets": {
                "chicago-manual": {
                    "name": "Chicago Manual of Style (CMOS)",
                    "description": "CMOS formatting",
                    "font_family": "Times New Roman",
                    "font_size_pt": 12.0,
                    "line_spacing": 2.0,
                    "first_line_indent_inches": 0.5,
                    "scene_break_symbol": "#",
                }
            },
            "chapters": [
                {
                    "stem": "01_Chapter_01",
                    "title": "Chapter 1: The Inciting Spark",
                    "rel_path": "01_Chapter_01.md",
                    "status": "docx_newer",
                    "md_words": 1500,
                    "docx_words": 1550,
                    "delta": 50,
                    "has_comments": True,
                }
            ],
            "comments": [
                {
                    "id": "1",
                    "author": "Editor",
                    "chapter": "Chapter 1",
                    "date": "2026-10-09",
                    "text": "Check pacing here.",
                }
            ],
            "summary": {
                "total": 1,
                "synced": 0,
                "docx_newer": 1,
                "md_newer": 0,
                "conflicts": 0,
            },
        }
        html_out = render_docx_studio_html(report, out_file)
        self.assertTrue(out_file.is_file())
        self._assert_strict_csp(html_out)
        self.assertIn("DOCX Studio", html_out)
        self.assertIn("The Silver Citadel", html_out)
        self.assertIn("The Inciting Spark", html_out)
        self.assertIn("Chicago Manual of Style", html_out)
        self.assertIn("Check pacing here.", html_out)

    def test_draft_manager_template_rendering_and_csp(self):
        out_file = self.tmp_dir / "draft_tree.html"
        drafts_data = [
            {
                "name": "Draft-01",
                "volume": "Volume-1",
                "milestone": "Alpha",
                "word_count": 45000,
                "chapter_count": 12,
                "is_active": False,
                "is_locked": False,
                "created_at": "2026-10-01",
            },
            {
                "name": "Draft-02",
                "volume": "Volume-1",
                "milestone": "Beta",
                "word_count": 52000,
                "chapter_count": 14,
                "is_active": True,
                "is_locked": False,
                "created_at": "2026-10-05",
            },
        ]
        html_out = generate_draft_dashboard_html(
            manuscript_title="The Astral Archive",
            drafts_data=drafts_data,
            active_draft_name="Draft-02",
            output_path=out_file,
        )
        self.assertTrue(out_file.is_file())
        self._assert_strict_csp(html_out)
        self.assertIn("The Astral Archive", html_out)
        self.assertIn("Draft-01", html_out)
        self.assertIn("Draft-02", html_out)

    def test_importer_template_rendering_and_csp(self):
        out_file = self.tmp_dir / "import_studio.html"
        report = {
            "title": "Imported Chronicles",
            "author": "Test Scribe",
            "source_format": "Scrivener",
            "source_path": "/path/to/archive.scriv",
            "dest_path": "/path/to/vault",
            "book": "Book-01",
            "draft": "Draft-01",
            "total_words": 65000,
            "chapters_imported": 15,
            "lore_entities": [
                {
                    "name": "Eldoria",
                    "type": "location",
                    "category": "Locations",
                    "rel_path": "Locations/Eldoria.md",
                    "synopsis": "Capital city of the realm.",
                }
            ],
            "chapters": [
                {
                    "index": 1,
                    "title": "Prologue: The Shattered Gate",
                    "filename": "01_Prologue.md",
                    "word_count": 3500,
                    "synopsis": "The ancient gate is breached.",
                    "pov": "Valen",
                }
            ],
        }
        res_path = render_import_studio_html(report, out_file)
        self.assertTrue(res_path.is_file())
        html = res_path.read_text(encoding="utf-8")
        self._assert_strict_csp(html)
        self.assertIn("Batch Importer", html)
        self.assertIn("Imported Chronicles", html)
        self.assertIn("Eldoria", html)
        self.assertIn("The Shattered Gate", html)

    def test_revision_heatmap_template_rendering_and_csp(self):
        out_file = self.tmp_dir / "heatmap.html"
        report_data = {
            "manuscript": "Crown of Ash",
            "baseline_source": "Snapshot v0.1",
            "total_chapters": 1,
            "total_words": 5000,
            "total_baseline_words": 4800,
            "avg_churn_score": 750.0,
            "max_churn_score": 750,
            "avg_churn_ratio": 0.15,
            "dialogue_churn_percentage": 25.0,
            "chapters": [
                {
                    "chapter_number": 1,
                    "title": "The Embers",
                    "rel_path": "01_The_Embers.md",
                    "word_count": 5000,
                    "baseline_word_count": 4800,
                    "churn_score": 750,
                    "churn_ratio": 0.15,
                    "added_lines": 45,
                    "deleted_lines": 20,
                    "modified_lines": 10,
                    "flag": "REV-101",
                    "flag_desc": "High Revision Activity",
                    "dialogue_churn_score": 180,
                    "scenes": [],
                }
            ],
            "findings": [],
        }
        res_path = generate_revision_heatmap_html(report_data, out_file)
        self.assertTrue(res_path.is_file())
        html = res_path.read_text(encoding="utf-8")
        self._assert_strict_csp(html)
        self.assertIn("Crown of Ash", html)
        self.assertIn("The Embers", html)

    def test_velocity_template_rendering_and_csp(self):
        out_file = self.tmp_dir / "velocity.html"
        word_data = {
            "title": "The Velocity Chronicle",
            "author": "Test Author",
            "total_words": 15000,
            "target_words": 80000,
            "percent_complete": 18.75,
            "estimated_pages": 60,
            "reading_time_minutes": 66.7,
            "audiobook_hours": 1.7,
            "dialogue_percentage": 35.0,
            "chapters": [],
            "pov_distribution": {},
        }
        velocity_data = {
            "rolling_7d_daily_words": 1200,
            "rolling_7d_wpm": 28.5,
            "current_streak_days": 12,
            "best_streak_days": 15,
            "sprint_history": [
                {
                    "date": "2026-10-09",
                    "words": 1500,
                    "duration_minutes": 50,
                    "wpm": 30.0,
                }
            ],
        }
        res_path = render_velocity_html(word_data, velocity_data, out_file)
        self.assertTrue(res_path.is_file())
        html = res_path.read_text(encoding="utf-8")
        self._assert_strict_csp(html)
        self.assertIn("Velocity", html)


if __name__ == "__main__":
    unittest.main()

