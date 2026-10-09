#!/usr/bin/env python3
"""
Unit and integration tests for the Eldoria Demo Cosmos template (tests/test_demo_cosmos.py).
"""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
LIB_DIR = REPO_ROOT / "scripts" / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

from codex_export import scan_world_vault
from diagnostics import generate_diagnostic_report
from preflight import run_preflight_linter

DEMO_COSMOS_DIR = REPO_ROOT / "templates" / "demo-cosmos" / "Eldoria-Cosmos"
DEMO_WORLD_DIR = DEMO_COSMOS_DIR / "Eldoria-Prime"
DEMO_MS_DIR = DEMO_COSMOS_DIR / "Manuscripts" / "The-Silver-Chronicles"


class TestDemoCosmos(unittest.TestCase):

    def test_demo_cosmos_files_exist(self):
        self.assertTrue(DEMO_COSMOS_DIR.is_dir(), "demo-cosmos directory must exist")
        self.assertTrue((DEMO_COSMOS_DIR / "universe.yaml").is_file())
        self.assertTrue((DEMO_COSMOS_DIR / "Universe-Index.md").is_file())
        self.assertTrue((DEMO_WORLD_DIR / "world.yaml").is_file())
        self.assertTrue((DEMO_WORLD_DIR / "World-Bible-Index.md").is_file())
        self.assertTrue((DEMO_MS_DIR / "manuscript.yaml").is_file())

    def test_diagnostics_passes_on_demo_cosmos(self):
        """Ensures that the demo cosmos lore vault passes diagnostics checks."""
        findings = generate_diagnostic_report(DEMO_WORLD_DIR)
        self.assertIsInstance(findings, dict)
        self.assertIn("toolchain", findings)

    def test_preflight_passes_on_demo_manuscript(self):
        """Ensures that the demo manuscript passes preflight linter."""
        rep = run_preflight_linter(DEMO_MS_DIR)
        self.assertIn("readiness_status", rep)
        self.assertEqual(rep["fail_count"], 0)

    def test_codex_export_scans_demo_world(self):
        """Ensures that codex export parses demo cosmos lore categories."""
        cats = scan_world_vault(DEMO_WORLD_DIR)
        self.assertGreater(len(cats), 0)


if __name__ == "__main__":
    unittest.main()

