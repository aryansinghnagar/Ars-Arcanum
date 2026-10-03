#!/usr/bin/env python3
"""
Unit and Integration Tests for Ars Arcanum Cosmology & Pantheon Validator
(tests/test_cosmology.py)
================================================================================
"""

import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.lib.cosmology import (
    audit_cosmology,
    extract_deity_profiles,
    generate_cosmology_html_report,
    generate_cosmology_svg,
    main as cosmology_main,
)


class TestCosmologyEngine(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

        # Create sample cosmology vault
        self.cosmology_dir = self.root / "Pantheon"
        self.cosmology_dir.mkdir(parents=True, exist_ok=True)

        # Deity 1: Solas (Sun God)
        (self.cosmology_dir / "Solas.md").write_text(
            """---
name: Solas, The Radiant Dawn
type: deity
domains: [sun, light, order, justice]
alignment: Lawful Radiant
hierarchy: Supreme Deity
ritual_catalysts: [Solar Ash, Gold, Dawn Lily]
commandments: [Never strike in the dark, Protect the mortal faithful, Honor oaths]
worship_base: 500000
---
# Solas
The High Deity of the Solar Sphere.
""",
            encoding="utf-8",
        )

        # Deity 2: Umbra (Shadow God - Domain Conflict with Solas on Sun/Order)
        (self.cosmology_dir / "Umbra.md").write_text(
            """---
name: Umbra, Sovereign of the Eclipse
type: deity
domains: [night, darkness, sun, justice]
alignment: Lawful Radiant
hierarchy: Major Deity
ritual_catalysts: [Solar Ash, Obsidian]
commandments: [Silence is Power, Guard the Deep Secrets]
worship_base: 120000
---
# Umbra
Deity of hidden stars and cosmic balance.
""",
            encoding="utf-8",
        )

        # Deity 3: Malakor (Contradictory Ritual Catalysts: Lawful Radiant demanding blood tithe)
        (self.cosmology_dir / "Malakor.md").write_text(
            """---
name: Malakor the Pure
type: deity
domains: [fire, purification]
alignment: Lawful Radiant
hierarchy: Major Deity
ritual_catalysts: [blood_tithes, human_sacrifice]
commandments: [Ash cleanses all, Destroy the mortal flesh]
worship_base: 80000
---
# Malakor
The Flame Lord.
""",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_extract_deity_profiles(self) -> None:
        """Verifies parsing of deity frontmatter markdown."""
        deities = extract_deity_profiles(self.root)
        self.assertEqual(len(deities), 3)
        self.assertIn("Solas", deities)
        self.assertEqual(deities["Solas"]["name"], "Solas, The Radiant Dawn")
        self.assertIn("sun", deities["Solas"]["domains"])
        self.assertEqual(deities["Solas"]["worship_base"], 500000)

    def test_domain_overlap_conflict_cos101(self) -> None:
        """COS-101: Detects domain overlap conflict between multiple major deities (Solas vs Umbra on sun)."""
        audit = audit_cosmology(self.root)
        findings = audit["findings"]
        cos_101 = [f for f in findings if f["id"] == "COS-101"]

        self.assertTrue(len(cos_101) > 0)
        domains = [f["domain"] for f in cos_101]
        self.assertTrue("sun" in domains or "justice" in domains)

    def test_ritual_catalyst_contradiction_cos102(self) -> None:
        """COS-102: Detects profane catalyst demanded by Lawful Radiant deity (Malakor demanding blood_tithes)."""
        audit = audit_cosmology(self.root)
        findings = audit["findings"]
        cos_102 = [f for f in findings if f["id"] == "COS-102"]

        self.assertTrue(len(cos_102) > 0)
        self.assertTrue(any("Malakor" in f["deity"] for f in cos_102))

    def test_theological_schisms_cos103(self) -> None:
        """COS-103: Detects contradictory commandments between deities (Protect vs Destroy)."""
        audit = audit_cosmology(self.root)
        findings = audit["findings"]
        cos_103 = [f for f in findings if f["id"] == "COS-103"]
        self.assertTrue(len(cos_103) > 0)

    def test_generate_svg_pantheon(self) -> None:
        """Generates valid offline SVG pantheon diagram."""
        deities = extract_deity_profiles(self.root)
        svg = generate_cosmology_svg(deities)
        self.assertIn("<svg", svg)
        self.assertIn("Solas", svg)
        self.assertIn("</svg>", svg)

    def test_generate_html_report(self) -> None:
        """Generates valid offline HTML report with strict Content Security Policy."""
        audit = audit_cosmology(self.root)
        out_html = self.root / "cosmology_report.html"
        generate_cosmology_html_report(audit, out_html)
        self.assertTrue(out_html.is_file())
        content = out_html.read_text(encoding="utf-8")
        self.assertIn("Content-Security-Policy", content)
        self.assertIn("Solas", content)

    def test_cli_invocation(self) -> None:
        """Tests CLI execution in JSON and human-readable mode."""
        with patch("sys.argv", ["cosmology.py", str(self.root), "--json"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                with self.assertRaises(SystemExit) as cm:
                    cosmology_main()
                self.assertEqual(cm.exception.code, 1)
                data = json.loads(mock_stdout.getvalue())
                self.assertEqual(data["deities_count"], 3)
                self.assertGreater(len(data["findings"]), 0)


if __name__ == "__main__":
    unittest.main()
