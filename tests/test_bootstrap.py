#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Bootstrap Utilities (scripts/lib/_bootstrap.py).
"""

import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib._bootstrap import (
    validate_volume_name,
    sanitize_identifier,
    atomic_write,
    LIB_DIR,
    PROJECT_ROOT,
    SCRIPTS_DIR,
)


class TestBootstrap(unittest.TestCase):

    def test_paths_resolved(self):
        self.assertTrue(LIB_DIR.is_dir())
        self.assertTrue(SCRIPTS_DIR.is_dir())
        self.assertTrue(PROJECT_ROOT.is_dir())

    def test_validate_volume_name(self):
        self.assertEqual(validate_volume_name("Book-01"), "Book-01")
        self.assertEqual(validate_volume_name("Volume_02"), "Volume_02")
        self.assertEqual(validate_volume_name("all"), "all")
        self.assertEqual(validate_volume_name("omnibus"), "omnibus")

        # Empty
        with self.assertRaises(ValueError):
            validate_volume_name("")

        # Path traversal
        with self.assertRaises(ValueError):
            validate_volume_name("../secrets")
        with self.assertRaises(ValueError):
            validate_volume_name("foo/bar")
        with self.assertRaises(ValueError):
            validate_volume_name("foo\\bar")

        # Invalid characters
        with self.assertRaises(ValueError):
            validate_volume_name("Vol:1*")

    def test_sanitize_identifier(self):
        self.assertEqual(sanitize_identifier("Lord Valen!"), "LordValen")
        self.assertEqual(sanitize_identifier("House-of_Stark"), "House-of_Stark")
        self.assertEqual(sanitize_identifier("???", fallback="unknown"), "unknown")
        self.assertEqual(sanitize_identifier(None, fallback="item"), "item")

    def test_atomic_write_export(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "test.txt"
            atomic_write(f, "test content")
            self.assertTrue(f.is_file())
            self.assertEqual(f.read_text(encoding="utf-8"), "test content")


if __name__ == "__main__":
    unittest.main()
