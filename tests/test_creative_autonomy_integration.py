#!/usr/bin/env python3
"""
Integration Tests for Sovereign Creative Autonomy & Epistemic Decoupling
(tests/test_creative_autonomy_integration.py)
========================================================================
Validates the 6 Intent Preservation Contracts and Epistemic Decoupling across:
1. Deliberate Repetition & Stylostatistical Observations
2. Deliberate Passive Voice / Bureaucratic Voice
3. Static & Atmospheric Scenes (Zero Polarity Shift)
4. Mythic & Impossible Magic Modality
5. Geopolitical Intrigue & Asymmetric Alliances (Exit 0 default)
6. Non-Linear Manuscript Discourse & Flashbacks (Exit 0 default)
7. Prophecy Open Arcs & Subversion (Exit 0 default)
8. World Doctor Lore Stubs vs Hard Syntax Errors
9. Authorial Constitution Schema & Suppression Filtering
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.lib.causality import audit_causality, extract_causal_nodes
from scripts.lib.config import (
    get_authorial_constitution,
    is_rule_suppressed,
)
from scripts.lib.factions import audit_faction_diplomacy, extract_faction_profiles
from scripts.lib.magic_system import extract_magic_profiles, scan_scene_magic_constraints
from scripts.lib.preflight import run_preflight_linter
from scripts.lib.prophecy import audit_prophecy_resolution, extract_prophecies
from scripts.lib.registry_base import DiagnosticSeverity
from scripts.lib.structure import analyze_character_arc_geometry, scan_manuscript_structure
from scripts.lib.world_doctor import check_world


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

    def test_autonomy_1_deliberate_repetition(self) -> None:
        """Intentional repetition in prose must not trigger blocking failures."""
        ch = self.ms_dir / "ch01.md"
        ch.write_text("""---
title: Litany of the Deep
intent: deliberate
---
The bells rang for the lost.
The bells rang for the forgotten.
The bells rang for the sea.
The bells rang until dawn.
""", encoding="utf-8")
        res = scan_manuscript_structure(self.ms_dir, paradigm_key="framework_free")
        self.assertEqual(res["harmony_score"], 100.0)

    def test_autonomy_2_deliberate_passive_voice(self) -> None:
        """Bureaucratic / passive narration must pass preflight and structural evaluation."""
        (self.ms_dir / "manuscript.yaml").write_text("""---
title: Inquisition Records
author: Inquisitor General
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

    def test_autonomy_3_static_atmospheric_scene(self) -> None:
        """Static atmospheric scenes (low polarity shift) must emit telemetry without flagging defects."""
        ch = self.ms_dir / "ch01.md"
        ch.write_text("""---
title: Twilight on the Steppe
@arc: Atmospheric Prelude
---
The wind moved through the tall grasses. Saffron light touched the edge of the dunes.
A hawk circled above the quiet riverbank, drifting on the thermal currents.
Night fell softly over the ancient stone markers.
""", encoding="utf-8")
        arc_report = analyze_character_arc_geometry(self.ms_dir, world_path=self.world_dir)
        self.assertEqual(len(arc_report["chapter_progression"]), 1)
        self.assertIn("Author-Declared", arc_report["chapter_progression"][0]["arc_stage"])

    def test_autonomy_4_mythic_magic(self) -> None:
        """Mythic / unconstrained magic descriptions must not trigger thermodynamic cost errors."""
        magic_dir = self.world_dir / "Magic-Technology"
        magic_dir.mkdir(parents=True, exist_ok=True)
        (magic_dir / "CreationSong.md").write_text("""---
name: Creation Song
modality: mythic
classification: Mythic Magic
---
A primal melody that weaves stars into being from void.
""", encoding="utf-8")

        ch = self.ms_dir / "ch01.md"
        ch.write_text("The goddess sang, and an island of pure pearl coalesced from nothingness.", encoding="utf-8")

        profiles = extract_magic_profiles(self.world_dir)
        findings = scan_scene_magic_constraints(self.ms_dir, profiles, {})
        self.assertEqual(len(findings), 0)

    def test_autonomy_5_geopolitical_intrigue_observations(self) -> None:
        """Asymmetric alliances and vassal conflicts must be categorized as OBSERVATION."""
        f_dir = self.world_dir / "Factions"
        f_dir.mkdir(parents=True, exist_ok=True)

        (f_dir / "Empire.md").write_text("""---
name: Solaris Empire
faction_type: Empire
military_strength: 50000
allies: [Vanguard Guild]
rivals: [Shadow Syndicate]
vassals: [Northern Duchy]
---
""", encoding="utf-8")

        (f_dir / "Vanguard.md").write_text("""---
name: Vanguard Guild
faction_type: Guild
military_strength: 15000
allies: []
rivals: []
---
""", encoding="utf-8")

        (f_dir / "Syndicate.md").write_text("""---
name: Shadow Syndicate
faction_type: Guild
military_strength: 10000
allies: [Northern Duchy]
rivals: [Solaris Empire]
---
""", encoding="utf-8")

        (f_dir / "NorthernDuchy.md").write_text("""---
name: Northern Duchy
faction_type: Duchy
military_strength: 5000
allies: [Shadow Syndicate]
overlord: Solaris Empire
---
""", encoding="utf-8")

        factions = extract_faction_profiles(self.world_dir)
        findings = audit_faction_diplomacy(factions)

        self.assertGreater(len(findings), 0)
        for fd in findings:
            self.assertEqual(fd["severity"], "OBSERVATION")

    def test_autonomy_6_nonlinear_flashback(self) -> None:
        """Non-linear narrative chapters (flashbacks) must be classified as OBSERVATION."""
        (self.ms_dir / "01_present.md").write_text("""---
title: The Battle of Red Ridge
@time-coord: Year 1050
---
The army clashed at the ridge.
""", encoding="utf-8")

        (self.ms_dir / "02_flashback.md").write_text("""---
title: Ten Years Earlier
@time-coord: Year 1040
@causes: [the battle of red ridge]
---
Ten years earlier, the oath was sworn.
""", encoding="utf-8")

        events, timelines = extract_causal_nodes(self.world_dir, self.ms_dir)
        findings = audit_causality(events, timelines)

        for fd in findings:
            if fd["id"] == "CAU-106":
                self.assertEqual(fd["severity"], "OBSERVATION")
                self.assertIn("Non-Linear Discourse", fd["message"])

    def test_autonomy_7_prophecy_open_arcs(self) -> None:
        """Unreferenced lore prophecies must be classified as OBSERVATION."""
        p_dir = self.world_dir / "Prophecies"
        p_dir.mkdir(parents=True, exist_ok=True)
        (p_dir / "AncientScroll.md").write_text("""---
name: Prophecy of the Twin Moons
type: prophecy
oracle: High Seer
status: active
target_entity: Chosen Child
clauses:
  - "When the two moons align"
---
""", encoding="utf-8")

        (self.ms_dir / "ch01.md").write_text("The boy walked down the village road.", encoding="utf-8")

        prophecies = extract_prophecies(self.world_dir)
        findings = audit_prophecy_resolution(prophecies, self.ms_dir, self.world_dir)

        self.assertGreater(len(findings), 0)
        for fd in findings:
            if fd["id"] == "PRP-101":
                self.assertEqual(fd["severity"], "OBSERVATION")
                self.assertIn("Unreferenced Prophecy", fd["message"])

    def test_autonomy_8_world_doctor_lore_stubs(self) -> None:
        """World Doctor should differentiate orphan notes (lore stubs) from parse errors."""
        c_dir = self.world_dir / "Characters"
        c_dir.mkdir(parents=True, exist_ok=True)
        (c_dir / "OrphanHero.md").write_text("""---
name: Orphan Hero
role: Explorer
---
An isolated explorer with no cross-links.
""", encoding="utf-8")

        findings = check_world(self.world_dir, self.ms_dir)
        orphan_files = [x.get("file", "") for x in findings["orphans"]]
        self.assertTrue(any("OrphanHero.md" in f for f in orphan_files))
        self.assertEqual(len(findings["frontmatter_parse_errors"]), 0)


if __name__ == "__main__":
    unittest.main()
