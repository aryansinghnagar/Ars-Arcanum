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
    count_prose_words,
    count_words,
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
        self.assertEqual(validate_volume_name("ALL"), "ALL")
        self.assertEqual(validate_volume_name("all-books"), "all-books")
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

        # Windows reserved names
        for res_name in ["CON", "PRN", "AUX", "NUL", "COM1", "LPT1"]:
            with self.assertRaises(ValueError):
                validate_volume_name(res_name)
            with self.assertRaises(ValueError):
                validate_volume_name(f"{res_name}.txt")

    def test_sanitize_identifier(self):
        self.assertEqual(sanitize_identifier("Lord Valen!"), "LordValen")
        self.assertEqual(sanitize_identifier("House-of_Stark"), "House-of_Stark")
        self.assertEqual(sanitize_identifier("???", fallback="unknown"), "unknown")
        self.assertEqual(sanitize_identifier(None, fallback="item"), "item")
        self.assertEqual(sanitize_identifier("", fallback="fallback_id"), "fallback_id")
        self.assertEqual(sanitize_identifier("CON", fallback="safe_name"), "safe_name")
        self.assertEqual(sanitize_identifier("NUL.txt", fallback="safe_name"), "safe_name")

    def test_count_prose_words(self):
        self.assertEqual(count_prose_words(""), 0)
        self.assertEqual(count_prose_words(None), 0)
        self.assertEqual(count_prose_words("The quick brown fox jumps over the lazy dog."), 9)

        # Frontmatter stripping
        text_with_fm = """---
title: Chapter One
draft: true
---
In the beginning was the Word.
"""
        self.assertEqual(count_prose_words(text_with_fm), 6)

        # Codeblock and HTML comment stripping
        text_with_code = """
```python
def foo():
    return 42
```
<!-- This is an editorial note -->
Here is the real manuscript prose.
"""
        self.assertEqual(count_prose_words(text_with_code), 6)

        # NovelCrafter tags and Typst comments
        text_with_tags = """
@pov: Valen
@status: draft
% Typst margin note
The ancient gate opened slowly with a grinding roar.
"""
        self.assertEqual(count_prose_words(text_with_tags), 9)
        self.assertEqual(count_words(text_with_tags), 9)

    def test_atomic_write_export(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "sub" / "test.txt"
            atomic_write(f, "test content")
            self.assertTrue(f.is_file())
            self.assertEqual(f.read_text(encoding="utf-8"), "test content")

            # Binary write
            fb = Path(td) / "sub" / "test.bin"
            atomic_write(fb, b"\x00\x01\x02\x03")
            self.assertTrue(fb.is_file())
            self.assertEqual(fb.read_bytes(), b"\x00\x01\x02\x03")


if __name__ == "__main__":
    unittest.main()
