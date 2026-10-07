#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum YAML Frontmatter Engine (scripts/lib/frontmatter.py).
Validates:
- Scalar coercion (booleans, nulls, integers, floats, quoted strings).
- Frontmatter parsing (YAML delimiters, nested lists, inline lists).
- Full YAML document parsing.
- Strict frontmatter parsing with success/failure flags.
- Frontmatter and body extraction.
"""

import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.frontmatter import (
    _coerce_scalar,
    _parse_yaml_lines,
    parse_yaml_frontmatter,
    parse_yaml_document,
    parse_frontmatter,
    extract_frontmatter_and_body,
)


class TestFrontmatter(unittest.TestCase):

    def test_coerce_scalar(self):
        # Quoted strings
        self.assertEqual(_coerce_scalar('"hello world"'), "hello world")
        self.assertEqual(_coerce_scalar("'single quoted'"), "single quoted")
        self.assertEqual(_coerce_scalar('"123"'), "123")

        # Booleans and Nulls
        self.assertIs(_coerce_scalar("true"), True)
        self.assertIs(_coerce_scalar("TRUE"), True)
        self.assertIs(_coerce_scalar("false"), False)
        self.assertIs(_coerce_scalar("FALSE"), False)
        self.assertIsNone(_coerce_scalar("none"))
        self.assertIsNone(_coerce_scalar("null"))
        self.assertIsNone(_coerce_scalar("~"))

        # Numbers
        self.assertEqual(_coerce_scalar("42"), 42)
        self.assertEqual(_coerce_scalar("-17"), -17)
        self.assertEqual(_coerce_scalar("+5"), 5)
        self.assertEqual(_coerce_scalar("3.14159"), 3.14159)
        self.assertEqual(_coerce_scalar("-0.05"), -0.05)
        self.assertEqual(_coerce_scalar("+2.5"), 2.5)

        # Plain text
        self.assertEqual(_coerce_scalar("Arcanum"), "Arcanum")
        self.assertEqual(_coerce_scalar("v1.0.0"), "v1.0.0")

    def test_parse_yaml_lines(self):
        lines = [
            "# Comment line",
            "",
            "title: The Sovereign Scribe",
            "count: 42",
            "tags:",
            "  - fantasy",
            "  - worldbuilding",
            "inline_tags: [magic, dragons, quest]",
            "empty_list: []",
            "empty_val:",
            "is_draft: false",
        ]
        res = _parse_yaml_lines(lines)
        self.assertEqual(res["title"], "The Sovereign Scribe")
        self.assertEqual(res["count"], 42)
        self.assertEqual(res["tags"], ["fantasy", "worldbuilding"])
        self.assertEqual(res["inline_tags"], ["magic", "dragons", "quest"])
        self.assertEqual(res["empty_list"], [])
        self.assertEqual(res["empty_val"], "")
        self.assertIs(res["is_draft"], False)

    def test_parse_yaml_lines_indent_variations(self):
        lines = [
            "items:",
            "    - four_spaces",
            "- root_dash",
        ]
        res = _parse_yaml_lines(lines)
        self.assertEqual(res["items"], ["four_spaces", "root_dash"])

    def test_parse_yaml_frontmatter(self):
        content = """---
title: Chapter 1
order: 1
draft: true
---
Chapter body starts here.
"""
        fm = parse_yaml_frontmatter(content)
        self.assertEqual(fm["title"], "Chapter 1")
        self.assertEqual(fm["order"], 1)
        self.assertIs(fm["draft"], True)

        # No frontmatter
        self.assertEqual(parse_yaml_frontmatter("No frontmatter here"), {})

    def test_parse_yaml_document(self):
        # Document with frontmatter delimiters
        doc1 = "---\nname: Eldoria\ntype: Realm\n---\n"
        res1 = parse_yaml_document(doc1)
        self.assertEqual(res1["name"], "Eldoria")
        self.assertEqual(res1["type"], "Realm")

        # Document without frontmatter delimiters
        doc2 = "name: Valen\nage: 28\nallies: [Aria, Kael]\n"
        res2 = parse_yaml_document(doc2)
        self.assertEqual(res2["name"], "Valen")
        self.assertEqual(res2["age"], 28)
        self.assertEqual(res2["allies"], ["Aria", "Kael"])

        # Document with loose delimiter lines
        doc3 = "---\nkey: value\n"
        res3 = parse_yaml_document(doc3)
        self.assertEqual(res3.get("key"), "value")

    def test_parse_frontmatter_strict(self):
        # Valid frontmatter with scalar, inline list, and bulleted list
        valid = """---
name: Lyra
role: Protagonist
aliases: ["The Shadow", "Starborn"]
skills:
  - Stealth
  - Astral Weaving
---
# Lyra's Profile
"""
        fm, success = parse_frontmatter(valid)
        self.assertTrue(success)
        self.assertEqual(fm["name"], "Lyra")
        self.assertEqual(fm["role"], "Protagonist")
        self.assertEqual(fm["aliases"], ["The Shadow", "Starborn"])
        self.assertEqual(fm["skills"], ["Stealth", "Astral Weaving"])

        # Empty text
        self.assertEqual(parse_frontmatter(""), ({}, True))

        # No frontmatter delimiter
        self.assertEqual(parse_frontmatter("# Heading\nBody text"), ({}, True))

        # Empty key value without bullets
        empty_key = "---\nnotes:\nsummary: Quick overview\n---\n"
        fm2, s2 = parse_frontmatter(empty_key)
        self.assertTrue(s2)
        self.assertEqual(fm2["notes"], "")
        self.assertEqual(fm2["summary"], "Quick overview")

        # Unclosed frontmatter
        unclosed = "---\nname: Unclosed\ntitle: Broken"
        _fm3, s3 = parse_frontmatter(unclosed)
        self.assertFalse(s3)

        # Invalid line syntax
        invalid = "---\nvalid_key: 1\nINVALID LINE WITHOUT COLON\n---\n"
        _fm4, s4 = parse_frontmatter(invalid)
        self.assertFalse(s4)

    def test_extract_frontmatter_and_body(self):
        content = """---
title: Act I
status: complete
---
# Act I: The Gathering Storm

It was a dark and tempestuous night.
"""
        fm, body = extract_frontmatter_and_body(content)
        self.assertEqual(fm["title"], "Act I")
        self.assertEqual(fm["status"], "complete")
        self.assertIn("# Act I: The Gathering Storm", body)
        self.assertIn("dark and tempestuous night", body)

        # No frontmatter
        no_fm = "# Just a header\nContent line"
        fm_none, body_none = extract_frontmatter_and_body(no_fm)
        self.assertEqual(fm_none, {})
        self.assertEqual(body_none, no_fm)

    def test_parse_nested_dictionaries_and_block_scalars(self):
        content = """---
name: Eldoria Prime
astrophysics:
  mass_solar: 1.25
  radius_km: 7200.5
  atmosphere:
    pressure_atm: 1.05
    habitable: true
currencies:
  - name: Sovereign
    rate: 1.0
  - name: Shilling
    rate: 0.1
synopsis: |
  Line 1 of synopsis.
  Line 2 of synopsis.
---
# Body content
"""
        fm, body = extract_frontmatter_and_body(content)
        self.assertEqual(fm["name"], "Eldoria Prime")
        self.assertIsInstance(fm["astrophysics"], dict)
        self.assertEqual(fm["astrophysics"]["mass_solar"], 1.25)
        self.assertEqual(fm["astrophysics"]["radius_km"], 7200.5)
        self.assertIs(fm["astrophysics"]["atmosphere"]["habitable"], True)
        self.assertEqual(fm["astrophysics"]["atmosphere"]["pressure_atm"], 1.05)
        self.assertIsInstance(fm["currencies"], list)
        self.assertEqual(len(fm["currencies"]), 2)
        self.assertEqual(fm["currencies"][0]["name"], "Sovereign")
        self.assertEqual(fm["currencies"][0]["rate"], 1.0)
        self.assertEqual(fm["currencies"][1]["name"], "Shilling")
        self.assertEqual(fm["currencies"][1]["rate"], 0.1)
        self.assertEqual(fm["synopsis"], "Line 1 of synopsis.\nLine 2 of synopsis.")
        self.assertIn("# Body content", body)


if __name__ == "__main__":
    unittest.main()
