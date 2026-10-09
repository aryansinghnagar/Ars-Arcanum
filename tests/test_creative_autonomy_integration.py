#!/usr/bin/env python3
"""
Integration Tests for Sovereign Creative Autonomy & Epistemic Decoupling
(tests/test_creative_autonomy_integration.py)
========================================================================
Validates the Intent Preservation Contracts and Epistemic Decoupling across:
1. 6-Tier Diagnostic Severity Taxonomy
2. Authorial Constitution Schema & Local Override
3. Rule Suppression Filtering
4. Preflight Typesetting and Intent-Preserving Linting
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.lib.config import (
    get_authorial_constitution,
    is_rule_suppressed,
)
from scripts.lib.preflight import run_preflight_linter
from scripts.lib.registry_base import DiagnosticSeverity


class TestCreativeAutonomyIntegration(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.world_dir = self.root / "00-World-Bible"
        self.ms_dir = self.root / "01-Manuscript"
        self.world_dir.mkdir(parents=True, exist_ok=True)
        self.ms_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_diagnostic_severity_enum(self) -> None:
        """Verify the 6-tier diagnostic severity taxonomy."""
        self.assertEqual(DiagnosticSeverity.CANON_ERROR.value, "canon_error")
        self.assertEqual(DiagnosticSeverity.RULE_CONFLICT.value, "rule_conflict")
        self.assertEqual(DiagnosticSeverity.OBSERVATION.value, "observation")
        self.assertEqual(DiagnosticSeverity.LENS_NOTE.value, "lens_note")
        self.assertEqual(DiagnosticSeverity.SUGGESTION.value, "suggestion")
        self.assertEqual(DiagnosticSeverity.EXPERIMENT.value, "experiment")

    def test_authorial_constitution_defaults_and_override(self) -> None:
        """Verify Authorial Constitution schema defaults and local file overrides."""
        # Test default constitution
        const = get_authorial_constitution()
        self.assertEqual(const["canon"]["authority"], "author")
        self.assertEqual(const["style"]["passive_voice"], "observe")
        self.assertEqual(const["magic"]["modality"], "unconstrained")

        # Test local world constitution override
        w_const_file = self.world_dir / "constitution.json"
        w_const_file.write_text(json.dumps({
            "magic": {"modality": "mythic"},
            "diagnostics": {"suppressed_rules": ["FAC-101", "PRP-101"]}
        }), encoding="utf-8")

        resolved = get_authorial_constitution(world_path=self.world_dir)
        self.assertEqual(resolved["magic"]["modality"], "mythic")
        self.assertTrue(is_rule_suppressed("FAC-101", resolved))
        self.assertTrue(is_rule_suppressed("PRP-101", resolved))
        self.assertFalse(is_rule_suppressed("WLD-106", resolved))

    def test_autonomy_deliberate_passive_voice(self) -> None:
        """Bureaucratic / passive narration must pass preflight evaluation."""
        (self.ms_dir / "manuscript.yaml").write_text("""---
title: Inquisition Records
author: Inquisitor General
language: en
---
""", encoding="utf-8")
        ch = self.ms_dir / "ch01.md"
        ch.write_text("""---
title: Official Inquisition Inquest
---
The decrees were issued by the Ministry of Protocol during the third lunar cycle of the year.
The petitions were received in triplicate and systematically filed in the high registry.
The prisoners were brought before the grand magistrate under armed guard at sunrise.
Sentences were read aloud in the central courtyard before the gathered citizenry.
No resistance was offered by the condemned during the formal recitation of charges.
All official records were sealed by direct order of the high crown council.
The classified documents were subsequently stored in reinforced subterranean vaults beneath the capitol archives.
Each leather-bound ledger was catalogued with meticulous care by the senior scribes.
No procedural exceptions were granted under imperial tribunal regulations.
The execution of the decrees was completed before dusk with complete administrative compliance.
""", encoding="utf-8")
        report = run_preflight_linter(self.ms_dir)
        self.assertEqual(report["fail_count"], 0)
        self.assertEqual(report["readiness_status"], "READY")


if __name__ == "__main__":
    unittest.main()
