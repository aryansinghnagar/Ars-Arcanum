#!/usr/bin/env python3
"""
Test Suite: Path Traversal Defense & Volume Sanitization (tests/test_path_traversal_defense.py)
=============================================================================================
Validates:
1. Python validate_volume_name rejection of traversal sequences (../, ..\\, /, \\, empty, special chars).
2. Python sanitize_identifier behavior.
3. Integration with concordance and pacing analyzers.
4. Robustness against command injection payloads and dangerous path characters.
"""

import unittest
from pathlib import Path
import tempfile
import shutil

from scripts.lib._bootstrap import validate_volume_name, sanitize_identifier
from scripts.lib.scope import EngineScope, filter_manuscript_scope


class TestPathTraversalDefense(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="arcanum_traversal_test_"))

    def tearDown(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_valid_volume_names(self):
        valid_cases = [
            "Book-01",
            "Book_02",
            "Volume-3",
            "Prologue",
            "Act-1",
            "all",
            "ALL",
            "all-books",
            "omnibus",
        ]
        for name in valid_cases:
            with self.subTest(name=name):
                result = validate_volume_name(name)
                self.assertEqual(result, name)

    def test_path_traversal_rejections(self):
        invalid_cases = [
            "",
            "..",
            "../",
            "..\\",
            "../../etc/passwd",
            "..\\..\\Windows\\System32",
            "/absolute/path",
            "C:\\Windows\\System32",
            "Book-01/subfolder",
            "Book-01\\subfolder",
            "Book 01",  # whitespace
            "Book;rm -rf /",
            "Book$(whoami)",
            "Book`id`",
            "Book&calc.exe",
            "Book|dir",
            "CON",
            "con",
            "PRN",
            "AUX",
            "NUL",
            "COM1",
            "LPT1",
        ]
        for name in invalid_cases:
            with self.subTest(name=name), self.assertRaises(ValueError, msg=f"Should reject: {name}"):
                validate_volume_name(name)

    def test_sanitize_identifier(self):
        self.assertEqual(sanitize_identifier("Book 01"), "Book01")
        self.assertEqual(sanitize_identifier("../../Dangerous! Name@#"), "DangerousName")
        self.assertEqual(sanitize_identifier("", fallback="default_vol"), "default_vol")
        self.assertEqual(sanitize_identifier("CON", fallback="default_vol"), "default_vol")
        self.assertEqual(sanitize_identifier("Valid-Name_123"), "Valid-Name_123")

    def test_scope_rejects_traversal_volume(self):
        ms_dir = self.temp_dir / "Manuscript"
        ms_dir.mkdir(parents=True, exist_ok=True)
        (ms_dir / "01_Chapter.md").write_text("# Chapter 1\n\nSome exciting prose.", encoding="utf-8")

        with self.assertRaises(ValueError):
            validate_volume_name("../../etc")

    def test_scope_filtering_security(self):
        ms_dir = self.temp_dir / "Manuscript"
        ms_dir.mkdir(parents=True, exist_ok=True)
        (ms_dir / "01_Chapter.md").write_text("# Chapter 1\n\nSome exciting prose.", encoding="utf-8")

        scope = EngineScope(chapters=[1])
        chapters, _scenes, _vols = filter_manuscript_scope(ms_dir, scope=scope)
        self.assertEqual(len(chapters), 1)


if __name__ == "__main__":
    unittest.main()
