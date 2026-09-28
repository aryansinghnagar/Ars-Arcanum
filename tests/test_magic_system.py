#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Hard Magic Systems & Arcane Constraint Matrix (scripts/lib/magic_system.py).
Covers magic profile extraction, character tier limits, catalyst validation, fatigue tracking,
hard limitation enforcement, HTML report generation, and CLI subcommands.
"""

import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.magic_system import (
    extract_character_magic_profiles,
    extract_magic_profiles,
    generate_magic_html_report,
    resolve_manuscript_dir,
    resolve_world_dir,
    run_magic_audit,
    main,
)


class TestMagicSystemEngine(unittest.TestCase):

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.world_dir = Path(self.temp_dir.name) / "World"
        self.ms_dir = Path(self.temp_dir.name) / "Manuscript"
        self.world_dir.mkdir(parents=True)
        self.ms_dir.mkdir(parents=True)

        (self.world_dir / "Magic-Technology").mkdir(parents=True)
        (self.world_dir / "Characters").mkdir(parents=True)
        (self.ms_dir / "Book-01" / "01_Act_I").mkdir(parents=True)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_extract_magic_profiles(self) -> None:
        magic_file = self.world_dir / "Magic-Technology" / "Aether_Weaving.md"
        magic_file.write_text("""---
name: "Aether Weaving"
type: magic_tech_system
classification: "Hard Magic"
source_of_power: "Atmospheric Aether"
danger_cost: "High"
max_tier: 5
disciplines:
  - "Pyromancy"
  - "Chronomancy"
catalysts:
  - "Ruby Focus"
  - "Silver Thread"
hard_limitations:
  - "Cannot resurrect the dead"
  - "Cannot create matter from nothing"
---
# Aether Weaving
## 3. Power Source, Costs & Limitations
- It is impossible to reverse total brain death.
- Hard bound by conservation of energy.
## 4. Disciplines, Branches or Schools
- **Aeromancy**: Control over wind currents.
## 5. Other Notes
""", encoding="utf-8")

        profiles = extract_magic_profiles(self.world_dir)
        self.assertIn("Aether Weaving", profiles)
        data = profiles["Aether Weaving"]
        self.assertEqual(data["classification"], "Hard Magic")
        self.assertEqual(data["max_tier"], 5)
        self.assertIn("Pyromancy", data["disciplines"])
        self.assertIn("Aeromancy", data["disciplines"])
        self.assertIn("ruby focus", data["catalysts"])
        self.assertTrue(any("resurrect" in lim for lim in data["hard_limitations"]))

    def test_extract_character_magic_profiles(self) -> None:
        char_file = self.world_dir / "Characters" / "Valen.md"
        char_file.write_text("""---
name: "Valen Vance"
type: character
role: Protagonist
magic_tier: 2
magic_ability: "Pyromancy"
catalyst: "Ruby Focus"
max_fatigue: 80
---
# Valen Vance
A promising initiate.
""", encoding="utf-8")

        chars = extract_character_magic_profiles(self.world_dir)
        self.assertIn("Valen Vance", chars)
        self.assertEqual(chars["Valen Vance"]["magic_tier"], 2)
        self.assertIn("pyromancy", chars["Valen Vance"]["affinity"])
        self.assertIn("ruby focus", chars["Valen Vance"]["catalysts"])
        self.assertEqual(chars["Valen Vance"]["max_fatigue"], 80)

    def test_detect_tier_overflow_mag101(self) -> None:
        (self.world_dir / "Characters" / "Valen.md").write_text("""---
name: "Valen Vance"
magic_tier: 1
---
""", encoding="utf-8")

        scene = self.ms_dir / "Book-01" / "01_Act_I" / "01_Scene.md"
        scene.write_text("""# Scene 1
@pov: Valen Vance
@cast: Valen Vance, Cataclysm, tier=4

The sky shattered.
""", encoding="utf-8")

        audit = run_magic_audit(str(self.world_dir), str(self.ms_dir))
        self.assertTrue(any(f["id"] == "MAG-101" for f in audit["findings"]))

    def test_detect_fatigue_overflow_mag104(self) -> None:
        (self.world_dir / "Characters" / "Valen.md").write_text("""---
name: "Valen Vance"
magic_tier: 3
max_fatigue: 50
---
""", encoding="utf-8")

        scene = self.ms_dir / "Book-01" / "01_Act_I" / "01_Scene.md"
        scene.write_text("""# Scene 1
@pov: Valen Vance
@cast: Valen Vance, Fireball, cost=30
@cast: Valen Vance, Fireball, cost=30

Valen collapsed from exhaustion.
""", encoding="utf-8")

        audit = run_magic_audit(str(self.world_dir), str(self.ms_dir))
        self.assertTrue(any(f["id"] == "MAG-104" for f in audit["findings"]))

    def test_detect_missing_catalyst_mag102(self) -> None:
        (self.world_dir / "Characters" / "Valen.md").write_text("""---
name: "Valen Vance"
magic_tier: 3
catalyst: "Ruby Focus"
---
""", encoding="utf-8")

        scene = self.ms_dir / "Book-01" / "01_Act_I" / "02_Scene.md"
        scene.write_text("""# Scene 2
@pov: Valen Vance
@cast: Valen Vance, Diamond Shield, tier=2, catalyst=Diamond

The light shone through the prism.
""", encoding="utf-8")

        audit = run_magic_audit(str(self.world_dir), str(self.ms_dir))
        self.assertTrue(any(f["id"] == "MAG-102" for f in audit["findings"]))

    def test_detect_hard_limitation_breach_resurrection_mag103(self) -> None:
        (self.world_dir / "Magic-Technology" / "Necromancy.md").write_text("""---
name: "Necromancy"
type: magic_tech_system
hard_limitations:
  - "Cannot resurrect the dead"
---
""", encoding="utf-8")

        scene = self.ms_dir / "Book-01" / "01_Act_I" / "03_Scene.md"
        scene.write_text("""# Scene 3
@pov: Elena

With a gasp, the fallen king was resurrected before their eyes.
""", encoding="utf-8")

        audit = run_magic_audit(str(self.world_dir), str(self.ms_dir))
        self.assertTrue(any(f["id"] == "MAG-103" for f in audit["findings"]))

    def test_detect_hard_limitation_breach_matter_creation_mag103(self) -> None:
        (self.world_dir / "Magic-Technology" / "Elementalism.md").write_text("""---
name: "Elementalism"
type: magic_tech_system
hard_limitations:
  - "Cannot create matter from nothing"
---
""", encoding="utf-8")

        scene = self.ms_dir / "Book-01" / "01_Act_I" / "04_Scene.md"
        scene.write_text("""# Scene 4
@pov: Valen

With a wave of his hand, he created water from nothing to quench their thirst.
""", encoding="utf-8")

        audit = run_magic_audit(str(self.world_dir), str(self.ms_dir))
        self.assertTrue(any(f["id"] == "MAG-103" for f in audit["findings"]))

    def test_clean_scene_compliant_cast_no_findings(self) -> None:
        (self.world_dir / "Magic-Technology" / "Aether.md").write_text("""---
name: "Aether"
type: magic_tech_system
---
""", encoding="utf-8")

        (self.world_dir / "Characters" / "Valen.md").write_text("""---
name: "Valen"
magic_tier: 3
catalyst: "Opal Focus"
max_fatigue: 100
---
""", encoding="utf-8")

        scene = self.ms_dir / "Book-01" / "01_Act_I" / "06_Scene.md"
        scene.write_text("""# Scene 6
@pov: Valen
@reagent: Opal Focus
@cast: Valen, Spark, tier=1, catalyst=Opal Focus, cost=10

A single bright spark flickered to life.
""", encoding="utf-8")

        audit = run_magic_audit(str(self.world_dir), str(self.ms_dir))
        self.assertEqual(audit["total_findings"], 0)

    def test_html_report_generation_and_csp(self) -> None:
        (self.world_dir / "Magic-Technology" / "Alchemy.md").write_text("""---
name: "Alchemy"
type: magic_tech_system
classification: "Potioncraft"
---
""", encoding="utf-8")
        audit = run_magic_audit(str(self.world_dir), str(self.ms_dir))
        out_html = self.ms_dir / "magic_report.html"
        generate_magic_html_report(audit, out_html)
        self.assertTrue(out_html.is_file())
        content = out_html.read_text(encoding="utf-8")
        self.assertIn("Arcane Constraint Matrix", content)
    def test_resolve_world_and_manuscript_dir(self) -> None:
        self.assertEqual(resolve_world_dir(str(self.world_dir)), str(self.world_dir.resolve()))
        self.assertEqual(resolve_manuscript_dir(str(self.ms_dir)), str(self.ms_dir.resolve()))
        self.assertEqual(resolve_world_dir(""), "")
        self.assertEqual(resolve_manuscript_dir(""), "")

    def test_extract_magic_profiles_alternative_fields(self) -> None:
        (self.world_dir / "Magic-Technology" / "Rune.md").write_text("""---
name: "Runic Arcana"
type: magic_tech_system
disciplines: "Inscription"
catalysts: "Chalk"
hard_limitations: "Requires physical substrate"
---
""", encoding="utf-8")
        profiles = extract_magic_profiles(self.world_dir)
        self.assertIn("Runic Arcana", profiles)
        self.assertIn("Inscription", profiles["Runic Arcana"]["disciplines"])
        self.assertIn("chalk", profiles["Runic Arcana"]["catalysts"])

    def test_cli_human_readable_check_and_report(self) -> None:
        (self.world_dir / "Magic-Technology" / "Aether.md").write_text("""---
name: "Aether"
type: magic_tech_system
classification: "Hard"
danger_cost: "High"
disciplines: ["Light"]
catalysts: ["Prism"]
hard_limitations: ["No time travel"]
---
""", encoding="utf-8")
        (self.world_dir / "Characters" / "Valen.md").write_text("""---
name: "Valen"
magic_tier: 1
---
""", encoding="utf-8")
        (self.ms_dir / "Book-01" / "01_Act_I" / "01_Scene.md").write_text("""# Scene
@cast: Valen, Nova, tier=5
""", encoding="utf-8")

        # Check with stdout
        with patch.object(sys, "argv", ["magic_system.py", "check", str(self.world_dir), "-m", str(self.ms_dir)]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 1)
                self.assertIn("Arcane Constraint Matrix", mock_stdout.getvalue())
                self.assertIn("MAG-101", mock_stdout.getvalue())

    def test_cli_report_json_and_html(self) -> None:
        (self.world_dir / "Magic-Technology" / "Aether.md").write_text("""---
name: "Aether"
type: magic_tech_system
classification: "Hard"
danger_cost: "High"
disciplines: ["Light"]
catalysts: ["Prism"]
hard_limitations: ["No time travel"]
---
""", encoding="utf-8")
        (self.world_dir / "Characters" / "Valen.md").write_text("""---
name: "Valen"
magic_tier: 1
---
""", encoding="utf-8")
        (self.ms_dir / "Book-01" / "01_Act_I" / "01_Scene.md").write_text("""# Scene
@pov: Valen
@char: Valen, Elena
@cast: Valen, Nova, tier=5
""", encoding="utf-8")
        html_out = Path(self.temp_dir.name) / "report.html"

        # 1. report --json
        with patch.object(sys, "argv", ["magic_system.py", "report", str(self.world_dir), "-m", str(self.ms_dir), "--json"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 1)
                import json
                res = json.loads(mock_stdout.getvalue())
                self.assertEqual(res["world"], self.world_dir.name)
                self.assertGreater(res["total_findings"], 0)

        # 2. report --html
        with patch.object(sys, "argv", ["magic_system.py", "report", str(self.world_dir), "-m", str(self.ms_dir), "--html", str(html_out)]):
            with patch("sys.stdout", new_callable=io.StringIO):
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 1)
                self.assertTrue(html_out.is_file())

        # 3. check --json
        with patch.object(sys, "argv", ["magic_system.py", "check", str(self.world_dir), "-m", str(self.ms_dir), "--json"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 1)

    def test_world_and_ms_directory_resolution_and_edge_cases(self) -> None:
        temp_home = Path(self.temp_dir.name) / "home"
        (temp_home / "Universes" / "Cosmos" / "Aethelgard").mkdir(parents=True)
        (temp_home / "Manuscripts" / "Novel").mkdir(parents=True)

        with patch("pathlib.Path.home", return_value=temp_home):
            # Resolve universe
            res_w = resolve_world_dir("Aethelgard")
            self.assertTrue(res_w.endswith("Aethelgard"))
            # Resolve manuscript
            res_m = resolve_manuscript_dir("Novel")
            self.assertTrue(res_m.endswith("Novel"))
            # Default world fallback
            res_single = resolve_world_dir(None)
            self.assertTrue(res_single.endswith("Aethelgard"))

            # Multiple worlds
            (temp_home / "Universes" / "Cosmos" / "Valendor").mkdir(parents=True)
            with patch("sys.stderr", new_callable=io.StringIO):
                with self.assertRaises(SystemExit) as cm:
                    resolve_world_dir(None)
                self.assertEqual(cm.exception.code, 2)

    def test_cli_no_args_and_error(self) -> None:
        # No args
        with patch.object(sys, "argv", ["magic_system.py"]):
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 0)

        # Invalid world dir
        with patch.object(sys, "argv", ["magic_system.py", "check", "nonexistent_world_123"]):
            with patch("sys.stderr", new_callable=io.StringIO):
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 2)


if __name__ == "__main__":
    unittest.main()

