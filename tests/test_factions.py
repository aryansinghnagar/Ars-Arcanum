#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Geopolitical Faction Matrix & Logistics (scripts/lib/factions.py).
Covers faction profiling, diplomatic paradoxes (FAC-101 to FAC-104), Mermaid generation,
Lanchester combat mathematics, campaign logistics, HTML reporting, and CLI subcommands.
"""

import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.factions import (
    audit_faction_diplomacy,
    calc_campaign_logistics,
    calc_lanchester_battle,
    extract_faction_profiles,
    generate_faction_html_report,
    generate_faction_mermaid,
    main,
)


class TestFactionsEngine(unittest.TestCase):

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.world_dir = Path(self.temp_dir.name) / "World"
        self.world_dir.mkdir(parents=True)
        (self.world_dir / "Factions").mkdir(parents=True)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_extract_and_audit_clean_factions(self) -> None:
        (self.world_dir / "Factions" / "Solar_Empire.md").write_text("""---
name: "Solar Empire"
type: faction
faction_type: "Empire"
leader: "[[Emperor Sol]]"
allies:
  - "[[Lunar Kingdom]]"
rivals:
  - "[[Void Syndicate]]"
military_strength: 50000
---
# Solar Empire
""", encoding="utf-8")

        (self.world_dir / "Factions" / "Lunar_Kingdom.md").write_text("""---
name: "Lunar Kingdom"
type: faction
faction_type: "Kingdom"
leader: "[[Queen Luna]]"
allies:
  - "[[Solar Empire]]"
rivals:
  - "[[Void Syndicate]]"
military_strength: 30000
---
# Lunar Kingdom
""", encoding="utf-8")

        factions = extract_faction_profiles(self.world_dir)
        self.assertIn("Solar Empire", factions)
        self.assertIn("Lunar Kingdom", factions)
        self.assertEqual(factions["Solar Empire"]["military_strength"], 50000.0)
        self.assertIn("Lunar Kingdom", factions["Solar Empire"]["allies"])

        findings = audit_faction_diplomacy(factions)
        self.assertEqual(len(findings), 0)

        mermaid = generate_faction_mermaid(factions)
        self.assertIn("flowchart LR", mermaid)
        self.assertIn("Solar Empire", mermaid)

    def test_diplomatic_asymmetric_alliance_fac101(self) -> None:
        (self.world_dir / "Factions" / "Faction_A.md").write_text("""---
name: "Faction A"
allies:
  - "Faction B"
---
""", encoding="utf-8")
        (self.world_dir / "Factions" / "Faction_B.md").write_text("""---
name: "Faction B"
allies: []
---
""", encoding="utf-8")

        factions = extract_faction_profiles(self.world_dir)
        findings = audit_faction_diplomacy(factions)
        self.assertTrue(any(f["id"] == "FAC-101" and f["severity"] == "WARNING" and "Asymmetric Alliance" in f["message"] for f in findings))

    def test_diplomatic_contradiction_fac101(self) -> None:
        (self.world_dir / "Factions" / "Faction_A.md").write_text("""---
name: "Faction A"
allies:
  - "Faction B"
---
""", encoding="utf-8")
        (self.world_dir / "Factions" / "Faction_B.md").write_text("""---
name: "Faction B"
rivals:
  - "Faction A"
---
""", encoding="utf-8")

        factions = extract_faction_profiles(self.world_dir)
        findings = audit_faction_diplomacy(factions)
        self.assertTrue(any(f["id"] == "FAC-101" and f["severity"] == "ERROR" and "Contradiction" in f["message"] for f in findings))

    def test_diplomatic_triad_tension_fac102(self) -> None:
        (self.world_dir / "Factions" / "Faction_A.md").write_text("""---
name: "Faction A"
allies:
  - "Faction B"
rivals:
  - "Faction C"
---
""", encoding="utf-8")
        (self.world_dir / "Factions" / "Faction_B.md").write_text("""---
name: "Faction B"
allies:
  - "Faction A"
  - "Faction C"
---
""", encoding="utf-8")
        (self.world_dir / "Factions" / "Faction_C.md").write_text("""---
name: "Faction C"
allies:
  - "Faction B"
rivals:
  - "Faction A"
---
""", encoding="utf-8")

        factions = extract_faction_profiles(self.world_dir)
        findings = audit_faction_diplomacy(factions)
        self.assertTrue(any(f["id"] == "FAC-102" for f in findings))

    def test_diplomatic_vassal_allegiance_conflict_fac103(self) -> None:
        (self.world_dir / "Factions" / "Overlord.md").write_text("""---
name: "Overlord"
rivals:
  - "Enemy"
vassals:
  - "Vassal"
---
""", encoding="utf-8")
        (self.world_dir / "Factions" / "Enemy.md").write_text("""---
name: "Enemy"
rivals:
  - "Overlord"
---
""", encoding="utf-8")
        (self.world_dir / "Factions" / "Vassal.md").write_text("""---
name: "Vassal"
overlord: "Overlord"
allies:
  - "Enemy"
---
""", encoding="utf-8")

        factions = extract_faction_profiles(self.world_dir)
        findings = audit_faction_diplomacy(factions)
        self.assertTrue(any(f["id"] == "FAC-103" and f["severity"] == "ERROR" for f in findings))

    def test_diplomatic_self_reference_fac104(self) -> None:
        (self.world_dir / "Factions" / "House_Solo.md").write_text("""---
name: "House Solo"
allies:
  - "House Solo"
rivals:
  - "House Solo"
---
""", encoding="utf-8")

        factions = extract_faction_profiles(self.world_dir)
        findings = audit_faction_diplomacy(factions)
        self.assertTrue(any(f["id"] == "FAC-104" for f in findings))

    def test_lanchester_square_law_combat(self) -> None:
        res = calc_lanchester_battle(attacker_force=10000, defender_force=5000, law="square")
        self.assertEqual(res["victor"], "Attacker")
        self.assertGreater(res["final_attacker"], 7000)
        self.assertEqual(res["law"], "square")

    def test_lanchester_fortification_bonus_turnaround(self) -> None:
        res_no_fort = calc_lanchester_battle(attacker_force=10000, defender_force=6000, fort_bonus=1.0)
        self.assertEqual(res_no_fort["victor"], "Attacker")

        res_fort = calc_lanchester_battle(attacker_force=10000, defender_force=6000, fort_bonus=5.0)
        self.assertEqual(res_fort["victor"], "Defender")

    def test_lanchester_linear_melee_combat(self) -> None:
        res_linear = calc_lanchester_battle(attacker_force=5000, defender_force=5000, law="linear")
        self.assertIn("victor", res_linear)
        self.assertEqual(res_linear["law"], "linear")

    def test_campaign_logistics_within_wagon_radius(self) -> None:
        log = calc_campaign_logistics(infantry=5000, cavalry=1000, support=500, distance_km=100.0, march_speed_km_day=20.0)
        self.assertGreater(log["daily_consumption"]["total_daily_supply_tons"], 0)
        self.assertGreater(log["logistics_requirements"]["wagons_required"], 0)
        self.assertTrue(log["logistics_requirements"]["is_within_wagon_radius"])
        self.assertIn("Feasible", log["logistics_requirements"]["logistics_verdict"])

    def test_campaign_logistics_exceeds_wagon_radius_failure(self) -> None:
        log_far = calc_campaign_logistics(infantry=5000, cavalry=1000, distance_km=5000.0, march_speed_km_day=15.0)
        self.assertFalse(log_far["logistics_requirements"]["is_within_wagon_radius"])
        self.assertIn("SUPPLY FAILURE", log_far["logistics_requirements"]["logistics_verdict"])

    def test_generate_faction_html_report_and_csp(self) -> None:
        (self.world_dir / "Factions" / "Guild.md").write_text("""---
name: "Merchants Guild"
type: faction
---
""", encoding="utf-8")
        factions = extract_faction_profiles(self.world_dir)
        findings = audit_faction_diplomacy(factions)
        html_out = Path(self.temp_dir.name) / "factions.html"
        generate_faction_html_report({"world": "TestWorld", "factions": factions, "findings": findings}, html_out)
        self.assertTrue(html_out.is_file())
        content = html_out.read_text(encoding="utf-8")
        self.assertIn("Merchants Guild", content)
        self.assertIn("Content-Security-Policy", content)

    def test_extract_and_mermaid_edges(self) -> None:
        (self.world_dir / "Factions" / "Overlord.md").write_text("""---
name: "Overlord"
military_strength: "invalid_str"
rivals: "Enemy"
vassals: "SubF"
allies: "AllyF"
---
""", encoding="utf-8")
        (self.world_dir / "Factions" / "SubF.md").write_text("""---
name: "SubF"
---
""", encoding="utf-8")
        (self.world_dir / "Factions" / "AllyF.md").write_text("""---
name: "AllyF"
allies: "Overlord"
---
""", encoding="utf-8")
        (self.world_dir / "Factions" / "Enemy.md").write_text("""---
name: "Enemy"
rivals: "Overlord"
---
""", encoding="utf-8")
        factions = extract_faction_profiles(self.world_dir)
        self.assertEqual(factions["Overlord"]["military_strength"], 1000.0)
        mermaid = generate_faction_mermaid(factions)
        self.assertIn("<==>|Ally|", mermaid)
        self.assertIn("-.->|Rival|", mermaid)
        self.assertIn("==>|Vassal|", mermaid)

    def test_cli_human_readable_check_battle_logistics(self) -> None:
        (self.world_dir / "Factions" / "Guild.md").write_text("""---
name: "Merchants Guild"
type: faction
allies: ["Merchants Guild"]
---
""", encoding="utf-8")

        # 1. Check with stdout
        with patch.object(sys, "argv", ["factions.py", "check", str(self.world_dir)]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 1)
                self.assertIn("Geopolitical Faction Matrix", mock_stdout.getvalue())
                self.assertIn("FAC-104", mock_stdout.getvalue())

        # 2. Battle with stdout
        with patch.object(sys, "argv", ["factions.py", "battle", "-a", "5000", "-d", "3000"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 0)
                self.assertIn("Lanchester Combat Simulation", mock_stdout.getvalue())

        # 3. Logistics with stdout
        with patch.object(sys, "argv", ["factions.py", "logistics", "--infantry", "1000"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 0)
                self.assertIn("Military Campaign Logistics", mock_stdout.getvalue())

    def test_cli_json_and_file_exports(self) -> None:
        (self.world_dir / "Factions" / "Solar.md").write_text("""---
name: "Solar"
type: faction
allies: ["Solar"]
---
""", encoding="utf-8")
        note_out = Path(self.temp_dir.name) / "factions.md"
        html_out = Path(self.temp_dir.name) / "factions_out.html"

        # 1. matrix --json
        with patch.object(sys, "argv", ["factions.py", "matrix", str(self.world_dir), "--json"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 1)
                import json
                res = json.loads(mock_stdout.getvalue())
                self.assertEqual(res["world"], self.world_dir.name)

        # 1b. matrix --write-note --html
        with patch.object(sys, "argv", ["factions.py", "matrix", str(self.world_dir), "--write-note", str(note_out), "--html", str(html_out)]):
            with patch("sys.stdout", new_callable=io.StringIO):
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 1)
                self.assertTrue(note_out.is_file())
                self.assertTrue(html_out.is_file())

        # 2. battle --json
        with patch.object(sys, "argv", ["factions.py", "battle", "-a", "1000", "-d", "500", "--json"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 0)
                import json
                res = json.loads(mock_stdout.getvalue())
                self.assertEqual(res["victor"], "Attacker")

        # 3. logistics --json
        with patch.object(sys, "argv", ["factions.py", "logistics", "--infantry", "1000", "--json"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 0)
                import json
                res = json.loads(mock_stdout.getvalue())
                self.assertIn("logistics_requirements", res)

    def test_world_resolution_and_edge_cases(self) -> None:
        from lib.factions import resolve_world_dir
        temp_home = Path(self.temp_dir.name) / "home"
        (temp_home / "Universes" / "Cosmos" / "Aethelgard").mkdir(parents=True)

        with patch("pathlib.Path.home", return_value=temp_home):
            # Resolve universe
            res_w = resolve_world_dir("Aethelgard")
            self.assertTrue(res_w.endswith("Aethelgard"))
            # Default world fallback
            res_single = resolve_world_dir(None)
            self.assertTrue(res_single.endswith("Aethelgard"))

            # Multiple worlds
            (temp_home / "Universes" / "Cosmos" / "Valendor").mkdir(parents=True)
            with patch("sys.stderr", new_callable=io.StringIO):
                with self.assertRaises(SystemExit) as cm:
                    resolve_world_dir(None)
                self.assertEqual(cm.exception.code, 2)


if __name__ == "__main__":
    unittest.main()

