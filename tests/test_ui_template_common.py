#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Shared UI Template Common Module (tests/test_ui_template_common.py)
"""

from __future__ import annotations

import unittest
from scripts.lib.ui_template_common import (
    COMMON_ACCESSIBILITY_JS,
    COMMON_CSS_VARIABLES,
    STRICT_OFFLINE_CSP,
    render_html_page,
)


class TestUiTemplateCommon(unittest.TestCase):
    """Verifies common design system primitives, accessibility tokens, and strict CSP."""

    def test_strict_offline_csp_invariants(self) -> None:
        self.assertIn("default-src 'none'", STRICT_OFFLINE_CSP)
        self.assertIn("style-src 'unsafe-inline'", STRICT_OFFLINE_CSP)
        self.assertIn("script-src 'unsafe-inline'", STRICT_OFFLINE_CSP)
        self.assertIn("img-src data:", STRICT_OFFLINE_CSP)
        self.assertIn("media-src data: blob:", STRICT_OFFLINE_CSP)
        self.assertNotIn("http://", STRICT_OFFLINE_CSP)
        self.assertNotIn("https://", STRICT_OFFLINE_CSP)

    def test_common_css_theme_variables(self) -> None:
        self.assertIn("--bg-primary", COMMON_CSS_VARIABLES)
        self.assertIn("--text-primary", COMMON_CSS_VARIABLES)
        self.assertIn('body[data-theme="sepia"]', COMMON_CSS_VARIABLES)
        self.assertIn('body[data-theme="light"]', COMMON_CSS_VARIABLES)
        self.assertIn('body[data-font="opendyslexic"]', COMMON_CSS_VARIABLES)
        self.assertIn('body[data-font="atkinson"]', COMMON_CSS_VARIABLES)

    def test_accessibility_javascript_announcers(self) -> None:
        self.assertIn("arcanum-live-announcer", COMMON_ACCESSIBILITY_JS)
        self.assertIn("aria-live", COMMON_ACCESSIBILITY_JS)
        self.assertIn("Escape", COMMON_ACCESSIBILITY_JS)
        self.assertIn("initThemeAndFont", COMMON_ACCESSIBILITY_JS)

    def test_render_html_page(self) -> None:
        page = render_html_page(
            title="World Bible <Overview>",
            body_html="<main role='main'><h1>Content</h1></main>",
            extra_css=".custom { color: red; }",
            extra_js="console.log('test');",
            subtitle="Cosmic Codex & Encyclopedia",
        )
        self.assertIn("<!DOCTYPE html>", page)
        self.assertIn("<meta http-equiv=\"Content-Security-Policy\"", page)
        self.assertIn("World Bible &lt;Overview&gt; — Cosmic Codex &amp; Encyclopedia", page)
        self.assertIn("<main role='main'><h1>Content</h1></main>", page)
        self.assertIn(".custom { color: red; }", page)
        self.assertIn("console.log('test');", page)
        self.assertIn("arcanum-live-announcer", page)


if __name__ == "__main__":
    unittest.main()
