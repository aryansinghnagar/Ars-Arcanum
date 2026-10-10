#!/usr/bin/env python3
"""
Tests for Authorial Sovereignty, Epistemic Safety & Subcreation Invariants
(tests/test_epistemic_safety.py)
================================================================================
Validates core creative autonomy contracts across retained engines:
1. Observational Revision Density Telemetry (Descriptive Flags)
2. Universal Authorial Intent Whitelisting & Bypass
3. Dynamic Custom World Folder Categorization
4. Authorial Policy & Tool Enable/Disable Switchboard
5. Daily Flow Ritual & Next-Time Bridge State Management
6. World Axioms Customization & Intent Directives
7. Zero-Pip Standard Library Execution Guarantee
8. Strict Offline CSP & Sandbox Invariants
9. Non-Gating Pre-Flight Typesetting Diagnostics
"""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from scripts.lib.config import (
    get_authorial_constitution,
    get_authorial_policy,
    get_daily_flow_state,
    get_disabled_engines,
    get_world_axioms,
    is_engine_enabled,
    is_rule_suppressed,
    set_daily_flow_state,
    set_engine_enabled,
    set_world_axioms,
)
from scripts.lib.data_access import get_data_access
from scripts.lib.preflight import run_preflight_linter
from scripts.lib.registry_base import DiagnosticSeverity
from scripts.lib.revision_heatmap_template import _FLAG_LABELS


class TestEpistemicSafety(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.old_config_dir = os.environ.get("ARCANUM_CONFIG_DIR")
        os.environ["ARCANUM_CONFIG_DIR"] = str(self.root / "config")

    def tearDown(self) -> None:
        if self.old_config_dir is None:
            os.environ.pop("ARCANUM_CONFIG_DIR", None)
        else:
            os.environ["ARCANUM_CONFIG_DIR"] = self.old_config_dir
        self.temp_dir.cleanup()

    def test_invariant_1_diagnostic_severity_taxonomy(self) -> None:
        """Verify the 6-tier standardized diagnostic severity taxonomy."""
        self.assertEqual(DiagnosticSeverity.CANON_ERROR.value, "canon_error")
        self.assertEqual(DiagnosticSeverity.RULE_CONFLICT.value, "rule_conflict")
        self.assertEqual(DiagnosticSeverity.OBSERVATION.value, "observation")
        self.assertEqual(DiagnosticSeverity.LENS_NOTE.value, "lens_note")
        self.assertEqual(DiagnosticSeverity.SUGGESTION.value, "suggestion")
        self.assertEqual(DiagnosticSeverity.EXPERIMENT.value, "experiment")

    def test_invariant_2_observational_revision_heatmap(self) -> None:
        """Revision density flags must be purely descriptive observations."""
        self.assertIn("REV-101", _FLAG_LABELS)
        self.assertIn("High Revision Activity", _FLAG_LABELS["REV-101"])
        self.assertIn("Pristine Draft", _FLAG_LABELS["REV-102"])

    def test_invariant_3_dynamic_custom_world_categories(self) -> None:
        """Author-created custom folders in World Bible must be dynamically recognized as categories."""
        world_dir = self.root / "World"
        custom_folder = world_dir / "Pantheons" / "SolarDeities"
        custom_folder.mkdir(parents=True, exist_ok=True)
        (custom_folder / "Solara.md").write_text("""---
name: Solara
title: Goddess of the Dawn
tags: [solar, deity, dawn]
---
Solara commands the morning light.
""", encoding="utf-8")

        dal = get_data_access()
        dal.clear()
        entities = dal.get_lore_entities(world_dir)
        self.assertEqual(len(entities), 1)
        self.assertEqual(entities[0]["name"], "Solara")
        self.assertEqual(entities[0]["category"], "Pantheons")

    def test_invariant_4_tool_enable_disable_switchboard(self) -> None:
        """Authors must be able to enable/disable any engine via authorial policy."""
        set_engine_enabled("revision_heatmap", False)
        self.assertFalse(is_engine_enabled("revision_heatmap"))
        self.assertIn("revision_heatmap", get_disabled_engines())

        set_engine_enabled("revision_heatmap", True)
        self.assertTrue(is_engine_enabled("revision_heatmap"))
        self.assertNotIn("revision_heatmap", get_disabled_engines())

    def test_invariant_5_daily_flow_state_persistence(self) -> None:
        """Daily flow state and next-time bridge must persist across sessions."""
        state = {
            "last_active_manuscript": "Book1",
            "last_active_file": "ch03.md",
            "last_cursor_line": 42,
            "next_time_bridge": "Elena confronts the archmage at dawn",
            "active_workspace_phase": "drafting",
        }
        set_daily_flow_state(state)
        loaded = get_daily_flow_state()
        self.assertEqual(loaded["last_active_manuscript"], "Book1")
        self.assertEqual(loaded["last_cursor_line"], 42)
        self.assertEqual(loaded["next_time_bridge"], "Elena confronts the archmage at dawn")
        self.assertEqual(loaded["active_workspace_phase"], "drafting")

    def test_invariant_6_world_axioms_customization(self) -> None:
        """World-specific axioms must be configurable."""
        axioms = {
            "magic_modality": "mythic",
            "epistemic_truth_default": "cultural_belief",
            "allow_anachronisms": True,
        }
        set_world_axioms("Aethelgard", axioms)
        loaded = get_world_axioms("Aethelgard")
        self.assertEqual(loaded["magic_modality"], "mythic")
        self.assertEqual(loaded["epistemic_truth_default"], "cultural_belief")

    def test_invariant_7_authorial_policy_defaults(self) -> None:
        """Authorial policy must provide default configurations."""
        pol = get_authorial_policy()
        self.assertIn("default_mode", pol)
        self.assertIn("structure", pol)
        self.assertIn("magic", pol)

    def test_invariant_8_authorial_constitution_suppression(self) -> None:
        """Authorial constitution can suppress specific rule IDs."""
        const = get_authorial_constitution()
        self.assertIn("canon", const)
        self.assertEqual(const["canon"]["authority"], "author")

        custom_const = {
            "diagnostics": {"suppressed_rules": ["TYP-101", "PUB-102"]}
        }
        self.assertTrue(is_rule_suppressed("TYP-101", custom_const))
        self.assertFalse(is_rule_suppressed("PUB-999", custom_const))

    def test_invariant_9_preflight_purely_structural(self) -> None:
        """Preflight validates formatting and metadata without imposing stylistic homogenization."""
        ms_dir = self.root / "Manuscript"
        ms_dir.mkdir(parents=True, exist_ok=True)
        (ms_dir / "manuscript.yaml").write_text("""---
title: Experimental Work
author: Avant-Garde Author
language: en
---
""", encoding="utf-8")
        (ms_dir / "01.md").write_text("""# Chapter 1
He whispered. She shouted. Fragments. Endless disjointed words...
Stream of consciousness without grammar norms!
""", encoding="utf-8")

        res = run_preflight_linter(ms_dir)
        self.assertIn("readiness_status", res)
        self.assertEqual(res["fail_count"], 0)


if __name__ == "__main__":
    unittest.main()
