#!/usr/bin/env python3
"""
Unit tests for Typography Cleaner scene break / horizontal rule preservation (DATA-01)
(scripts/lib/typography_cleaner.py)
"""

import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.typography_cleaner import normalize_typography_text


class TestSceneBreakPreservation(unittest.TestCase):

    def test_horizontal_rules_preservation(self):
        sample_md = """# Chapter 1

The hero stood upon the precipice.

---

Meanwhile, in the valley below:

***

The battle raged on.

* * *

Night fell across the realm.

- - -

Silence followed.

___

The end of the chapter.
"""
        cleaned, _stats = normalize_typography_text(sample_md)

        # Standalone scene breaks must remain intact as Markdown thematic breaks
        self.assertIn("\n---\n", cleaned)
        self.assertIn("\n***\n", cleaned)
        self.assertIn("\n* * *\n", cleaned)
        self.assertIn("\n- - -\n", cleaned)
        self.assertIn("\n___\n", cleaned)

        # Make sure they weren't converted to em-dashes
        self.assertNotIn("\n—\n", cleaned)

    def test_inline_em_dash_conversion_preserved(self):
        sample = "He paused---wondering if the door was locked--and turned back."
        cleaned, stats = normalize_typography_text(sample)
        self.assertEqual(cleaned, "He paused—wondering if the door was locked—and turned back.")
        self.assertEqual(stats["em_dashes"], 2)


if __name__ == "__main__":
    unittest.main()
