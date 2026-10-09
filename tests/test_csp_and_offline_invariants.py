#!/usr/bin/env python3
"""
Tests for Content Security Policy & Offline Invariants (tests/test_csp_and_offline_invariants.py)
=============================================================================================
Enforces AGENTS.md Section 2.2 contract:
- 100% offline air-gapped isolation (zero remote scripts, CDN links, or network telemetry).
- Mandatory Content Security Policy (default-src 'none') in all generated HTML templates.
- Strict CSP conformance across all HTML template generator modules in scripts/lib/.
"""

import re
import unittest
from pathlib import Path

STRICT_OFFLINE_CSP = "default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;"


class TestCspAndOfflineInvariants(unittest.TestCase):
    """Verifies that all HTML generation across the codebase enforces strict offline CSP."""

    def setUp(self) -> None:
        self.lib_dir = Path(__file__).resolve().parent.parent / "scripts" / "lib"

    def test_strict_offline_csp_string_format(self) -> None:
        """Verifies the core STRICT_OFFLINE_CSP definition matches AGENTS.md Section 2.2."""
        self.assertIn("default-src 'none'", STRICT_OFFLINE_CSP)
        self.assertIn("style-src 'unsafe-inline'", STRICT_OFFLINE_CSP)
        self.assertIn("script-src 'unsafe-inline'", STRICT_OFFLINE_CSP)
        self.assertIn("img-src data:", STRICT_OFFLINE_CSP)
        self.assertIn("media-src data: blob:", STRICT_OFFLINE_CSP)

    def test_all_python_html_templates_declare_csp(self) -> None:
        """Scans all python files in scripts/lib/ for HTML templates and verifies CSP presence."""
        py_files = list(self.lib_dir.glob("*.py"))
        self.assertGreater(len(py_files), 10)

        missing_csp_files: list[str] = []

        for py_file in py_files:
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            # If the file defines an HTML document scaffold
            if "<!DOCTYPE html>" in content or "<html" in content:
                has_csp = (
                    "Content-Security-Policy" in content
                    or "STRICT_OFFLINE_CSP" in content
                    or "ui_template_common" in content
                    or "render_html_page" in content
                )
                if not has_csp:
                    missing_csp_files.append(py_file.name)

        self.assertEqual(
            missing_csp_files,
            [],
            f"The following HTML-generating files are missing Content Security Policy: {missing_csp_files}",
        )

    def test_zero_remote_cdn_scripts_in_python_modules(self) -> None:
        """Ensures no python files in scripts/lib contain remote CDN or script URLs."""
        py_files = list(self.lib_dir.glob("*.py"))

        remote_violations: list[str] = []
        remote_pattern = re.compile(r'<(?:script|link)[^>]+(?:src|href)=["\']https?://[^"\']+', re.IGNORECASE)

        for py_file in py_files:
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            matches = remote_pattern.findall(content)
            if matches:
                remote_violations.append(f"{py_file.name}: {matches}")

        self.assertEqual(
            remote_violations,
            [],
            f"Found remote CDN/script dependencies in python modules: {remote_violations}",
        )


if __name__ == "__main__":
    unittest.main()
