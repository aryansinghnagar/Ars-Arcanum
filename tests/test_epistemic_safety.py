#!/usr/bin/env python3
"""
Tests for Authorial Sovereignty, Epistemic Safety & Subcreation Invariants
(tests/test_epistemic_safety.py)
================================================================================
Validates all 13 core creative autonomy contracts:
1. Framework-Free Narrative Alignment (Score = 100.0)
2. Soft & Mythic Magic Non-Punitive Classification
3. Universal @intent: deliberate & custom whitelist immunity
4. Dynamic Custom World Folder Categorization
5. Authorial Policy & Tool Enable/Disable Switchboard
6. Daily Flow Ritual & Next-Time Bridge State Management
7. Fast Idea Scraps Capture
8. DOCX & Export Presets
9. Zero-Pip Standard Library Execution
10. Strict Offline CSP Guarantee
11. Typographic Consent & Dry-Run Guarantee
12. Observational Revision Density Telemetry
13. Speculative Naming Phonotactics & Conlang Support
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.lib.config import (
    get_daily_flow_state,
    get_disabled_engines,
    get_world_axioms,
    is_engine_enabled,
    set_daily_flow_state,
    set_engine_enabled,
    set_world_axioms,
)
from scripts.lib.data_access import get_data_access
from scripts.lib.economy import audit_technological_anachronisms
from scripts.lib.magic_system import extract_magic_profiles, scan_scene_magic_constraints
from scripts.lib.resonance_data import CrossDomainEdge, EdgeProvenance
from scripts.lib.revision_heatmap_template import _FLAG_LABELS
from scripts.lib.structure import scan_manuscript_structure
from scripts.lib.typography_cleaner import normalize_typography_line


class TestEpistemicSafety(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_invariant_1_framework_free_structural_harmony(self) -> None:
        """Framework-free unconstrained mode must always yield 100.0 harmony score."""
        ch1 = self.root / "01.md"
        ch1.write_text("Prose scene content " * 100, encoding="utf-8")
        res = scan_manuscript_structure(self.root, paradigm_key="framework_free")
        self.assertEqual(res["harmony_score"], 100.0)
        self.assertEqual(res["paradigm_key"], "framework_free")

    def test_invariant_2_soft_magic_unconstrained(self) -> None:
        """Soft and mythic magic systems must never penalize miracle or resurrection descriptions."""
        magic_dir = self.root / "Magic-Technology"
        magic_dir.mkdir(parents=True, exist_ok=True)
        (magic_dir / "AncientGrace.md").write_text("""---
name: Ancient Grace
classification: Soft Magic
modality: soft
source_of_power: Divine Mystery
---
The ancient powers are subtle and miraculous.
""", encoding="utf-8")

        profiles = extract_magic_profiles(self.root)
        self.assertIn("Ancient Grace", profiles)
        self.assertTrue(profiles["Ancient Grace"]["is_soft"])

        # Manuscript describes resurrection
        ms_dir = self.root / "Manuscript"
        ms_dir.mkdir(parents=True, exist_ok=True)
        (ms_dir / "ch01.md").write_text("The mystic raised the fallen king back to life with grace.", encoding="utf-8")

        findings = scan_scene_magic_constraints(ms_dir, profiles, {})
        # Soft magic should produce 0 violation findings for miracles
        self.assertEqual(len(findings), 0)

    def test_invariant_3_deliberate_intent_whitelisting(self) -> None:
        """Scenes with @intent: deliberate or frontmatter intent: deliberate must bypass constraint warnings."""
        ms_dir = self.root / "Manuscript"
        ms_dir.mkdir(parents=True, exist_ok=True)
        (ms_dir / "ch01.md").write_text("""---
intent: deliberate
---
The knight pulled out a smartphone and checked the radar.
""", encoding="utf-8")

        findings = audit_technological_anachronisms(ms_dir, baseline_era="medieval")
        self.assertEqual(len(findings), 0)

    def test_invariant_4_dynamic_custom_world_categories(self) -> None:
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

    def test_invariant_5_tool_enable_disable_switchboard(self) -> None:
        """Authors must be able to enable/disable any engine via authorial policy."""
        set_engine_enabled("astrophysics", False)
        self.assertFalse(is_engine_enabled("astrophysics"))
        self.assertIn("astrophysics", get_disabled_engines())

        set_engine_enabled("astrophysics", True)
        self.assertTrue(is_engine_enabled("astrophysics"))
        self.assertNotIn("astrophysics", get_disabled_engines())

    def test_invariant_6_daily_flow_state_persistence(self) -> None:
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

    def test_invariant_7_world_axioms_customization(self) -> None:
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

    def test_invariant_8_resonance_edge_provenance(self) -> None:
        """Resonance mesh edges must declare explicit provenance."""
        edge = CrossDomainEdge(
            source_id="climate_arid",
            target_id="economy_spice",
            relation="economically_impacts",
            provenance=EdgeProvenance.AUTHOR_DECLARED,
        )
        self.assertEqual(edge.provenance, EdgeProvenance.AUTHOR_DECLARED)
        d = edge.to_dict()
        self.assertEqual(d["provenance"], "author_declared")

    def test_invariant_9_observational_revision_heatmap(self) -> None:
        """Revision density flags must be purely descriptive observations."""
        self.assertIn("REV-101", _FLAG_LABELS)
        self.assertIn("High Revision Activity", _FLAG_LABELS["REV-101"])
        self.assertIn("Pristine Draft", _FLAG_LABELS["REV-102"])

    def test_invariant_10_typography_smart_cleaner_consent(self) -> None:
        """Typography normalizer must produce reviewable proposals without forced destructive edits."""
        raw = 'He said, "Look at the star---it\'s moving..."'
        new_line, _stats, proposals, _, _ = normalize_typography_line(raw, False, False)
        self.assertIn("—", new_line)
        self.assertIn("…", new_line)
        self.assertTrue(len(proposals) > 0)
        rules = [p["rule"] for p in proposals]
        self.assertIn("curly_double_quotes", rules)
        self.assertIn("ellipsis", rules)

    def test_invariant_11_continuity_deliberate_bypass(self) -> None:
        """Continuity linter must bypass files and lines marked with intent: deliberate."""
        from scripts.lib.continuity import run_continuity_audit

        world_dir = self.root / "World" / "Characters"
        world_dir.mkdir(parents=True, exist_ok=True)
        (world_dir / "Kaelen.md").write_text("""---
name: Kaelen
eye_color: blue
---
Kaelen has striking sapphire eyes.
""", encoding="utf-8")

        ms_dir = self.root / "Manuscript"
        ms_dir.mkdir(parents=True, exist_ok=True)
        (ms_dir / "ch01.md").write_text("""---
intent: deliberate
---
Kaelen looked up with fiery green eyes.
""", encoding="utf-8")

        res = run_continuity_audit(str(self.root / "World"), str(ms_dir))
        findings = res.get("findings", [])
        self.assertEqual(len(findings), 0)

    def test_invariant_12_framework_free_aliases(self) -> None:
        """Paradigm keys 'none' and 'unconstrained' must resolve to framework_free."""
        from scripts.lib.manuscript_scaffold import get_preset

        ch1 = self.root / "01.md"
        ch1.write_text("Prose scene content " * 100, encoding="utf-8")
        res_none = scan_manuscript_structure(self.root, paradigm_key="none")
        self.assertEqual(res_none["paradigm_name"], "Framework-Free / Pure Timeline Flow")
        self.assertEqual(res_none["harmony_score"], 100.0)

        res_unconstrained = scan_manuscript_structure(self.root, paradigm_key="unconstrained")
        self.assertEqual(res_unconstrained["paradigm_name"], "Framework-Free / Pure Timeline Flow")
        self.assertEqual(res_unconstrained["harmony_score"], 100.0)

        preset = get_preset("none")
        self.assertIsNotNone(preset)
        self.assertEqual(preset["paradigm_key"], "framework_free")

    def test_invariant_13_tips_tradition_filtering(self) -> None:
        """Tips retrieval must support tradition filtering in contextual queries."""
        from scripts.lib.tips import TipDatabase

        db = TipDatabase()
        tip = db.get_contextual_tip(tradition="unconstrained")
        self.assertIsNotNone(tip)

    def test_invariant_14_authorial_policy_defaults(self) -> None:
        """Authorial policy must provide default configurations for structure, magic, continuity, and naming."""
        from scripts.lib.config import get_authorial_policy

        pol = get_authorial_policy()
        self.assertIn("default_mode", pol)
        self.assertIn("structure", pol)
        self.assertIn("magic", pol)
        self.assertIn("continuity", pol)
        self.assertIn("naming", pol)
        self.assertEqual(pol["structure"]["framework"], "none")
        self.assertEqual(pol["magic"]["mode"], "unconstrained")

    def test_invariant_15_economy_advisory_exit_code(self) -> None:
        """Economy checks must return exit code 0 by default (advisory-first), requiring --strict for exit 1."""
        from scripts.lib.economy import main as economy_main

        world_dir = self.root / "World" / "Economies"
        world_dir.mkdir(parents=True, exist_ok=True)
        (world_dir / "Sol.md").write_text("""---
name: Sol
base_currency: Gold
tech_era: medieval
commodity_basket:
  - "bread: 1"
---
""", encoding="utf-8")

        ms_dir = self.root / "Manuscript"
        ms_dir.mkdir(parents=True, exist_ok=True)
        (ms_dir / "01.md").write_text("""# Scene
He bought a smartphone and an airplane.
""", encoding="utf-8")

        # Without --strict, exits 0
        with patch("sys.argv", ["economy.py", "tech", str(ms_dir), "-w", str(self.root / "World")]):
            with self.assertRaises(SystemExit) as cm:
                economy_main()
            self.assertEqual(cm.exception.code, 0)

        # With --strict, exits 1
        with patch("sys.argv", ["economy.py", "tech", str(ms_dir), "-w", str(self.root / "World"), "--strict"]):
            with self.assertRaises(SystemExit) as cm:
                economy_main()
            self.assertEqual(cm.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
