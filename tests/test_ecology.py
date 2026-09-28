#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Trophic Food Web & Ecology Simulator (scripts/lib/ecology.py).
"""

import io
import tempfile
import unittest
from pathlib import Path
import sys
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.ecology import (
    extract_species_profiles,
    audit_ecosystem,
    generate_ecology_mermaid,
    generate_ecology_html_report,
    resolve_world_dir,
    main,
)


class TestEcologyEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.world_dir = Path(self.temp_dir.name) / "World"
        self.world_dir.mkdir(parents=True)
        (self.world_dir / "Bestiary").mkdir(parents=True)
        (self.world_dir / "Flora").mkdir(parents=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_clean_self_sustaining_ecosystem(self):
        (self.world_dir / "Flora" / "Sun_Grass.md").write_text(
            """---
name: "Sun Grass"
trophic_level: 1
habitat: "Savanna"
biomass_kg: 10000
population_density: 500
---
""",
            encoding="utf-8",
        )

        (self.world_dir / "Bestiary" / "Gazelle.md").write_text(
            """---
name: "Sun Gazelle"
trophic_level: 2
habitat: "Savanna"
dietary_prey:
  - "[[Sun Grass]]"
biomass_kg: 40
population_density: 100
---
""",
            encoding="utf-8",
        )

        (self.world_dir / "Bestiary" / "Shadow_Lion.md").write_text(
            """---
name: "Shadow Lion"
trophic_level: 4
habitat: "Savanna"
dietary_prey:
  - "[[Sun Gazelle]]"
biomass_kg: 180
population_density: 0.5
---
""",
            encoding="utf-8",
        )

        species = extract_species_profiles(self.world_dir)
        self.assertIn("Sun Grass", species)
        self.assertIn("Sun Gazelle", species)
        self.assertIn("Shadow Lion", species)

        findings = audit_ecosystem(species)
        self.assertEqual(len(findings), 0)

        mermaid = generate_ecology_mermaid(species)
        self.assertIn("flowchart TD", mermaid)
        self.assertIn("Shadow Lion", mermaid)

    def test_trophic_anomalies_eco301_eco303_eco304(self):
        (self.world_dir / "Bestiary" / "Apex_Solitary.md").write_text(
            """---
name: "Apex Solitary"
trophic_level: 4
habitat: "Volcanic Ridge"
---
""",
            encoding="utf-8",
        )

        (self.world_dir / "Bestiary" / "Predator_A.md").write_text(
            """---
name: "Predator A"
trophic_level: 3
dietary_prey:
  - "Predator B"
habitat: "Jungle"
---
""",
            encoding="utf-8",
        )

        (self.world_dir / "Bestiary" / "Predator_B.md").write_text(
            """---
name: "Predator B"
trophic_level: 3
dietary_prey:
  - "Predator A"
habitat: "Jungle"
---
""",
            encoding="utf-8",
        )

        species = extract_species_profiles(self.world_dir)
        findings = audit_ecosystem(species)

        ids = [f["id"] for f in findings]
        self.assertIn("ECO-301", ids)
        self.assertIn("ECO-303", ids)
        self.assertIn("ECO-304", ids)

    def test_generate_ecology_html_report(self):
        (self.world_dir / "Bestiary" / "Wolf.md").write_text(
            """---
name: "Timber Wolf"
trophic_level: 3
habitat: "Forest"
---
""",
            encoding="utf-8",
        )
        species = extract_species_profiles(self.world_dir)
        html_out = Path(self.temp_dir.name) / "ecology.html"
        generate_ecology_html_report(
            {"world": "TestWorld", "species": species, "findings": []}, html_out
        )
        self.assertTrue(html_out.is_file())
        self.assertIn("Timber Wolf", html_out.read_text(encoding="utf-8"))

    def test_trophic_deficit_eco302(self):
        (self.world_dir / "Flora" / "Forest_Fern.md").write_text(
            """---
name: "Forest Fern"
trophic_level: 1
habitat: "Forest"
biomass_kg: 5000
population_density: 500
---
""",
            encoding="utf-8",
        )
        (self.world_dir / "Bestiary" / "Forest_Deer.md").write_text(
            """---
name: "Forest Deer"
trophic_level: 2
habitat: "Forest"
dietary_prey:
  - "[[Forest Fern]]"
biomass_kg: 50
population_density: 2
---
""",
            encoding="utf-8",
        )
        (self.world_dir / "Bestiary" / "Shadow_Wolf.md").write_text(
            """---
name: "Shadow Wolf"
trophic_level: 3
habitat: "Forest"
dietary_prey:
  - "[[Forest Deer]]"
biomass_kg: 80
population_density: 1
---
""",
            encoding="utf-8",
        )
        species = extract_species_profiles(self.world_dir)
        findings = audit_ecosystem(species)
        ids = [f["id"] for f in findings]
        self.assertIn("ECO-302", ids)

    def test_resolve_world_dir(self):
        self.assertEqual(resolve_world_dir(str(self.world_dir)), str(self.world_dir.resolve()))
        self.assertEqual(resolve_world_dir(""), "")

    def test_extract_species_trophic_string_aliases(self):
        (self.world_dir / "Bestiary" / "Herb.md").write_text("""---
name: "Herbivore Creature"
trophic_level: "herbivore"
prey: "Sun Grass"
habitat: "Plains"
---
""", encoding="utf-8")
        species = extract_species_profiles(self.world_dir)
        self.assertIn("Herbivore Creature", species)
        self.assertEqual(species["Herbivore Creature"]["trophic_level"], 2)
        self.assertIn("Sun Grass", species["Herbivore Creature"]["dietary_prey"])

    def test_cli_human_readable_check_and_report(self):
        (self.world_dir / "Bestiary" / "Pred.md").write_text("""---
name: "Lone Wolf"
trophic_level: 3
dietary_prey: ["Sun Deer"]
habitat: "Woods"
---
""", encoding="utf-8")
        # Check with stdout
        with patch.object(sys, "argv", ["ecology.py", "check", str(self.world_dir)]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 1)
                self.assertIn("Trophic Food Web", mock_stdout.getvalue())
                self.assertIn("Lone Wolf", mock_stdout.getvalue())

    def test_cli_json_html_and_write_note(self):
        (self.world_dir / "Bestiary" / "Pred.md").write_text("""---
name: "Lone Wolf"
trophic_level: 3
dietary_prey: ["Sun Deer"]
habitat: "Woods"
---
""", encoding="utf-8")
        note_out = Path(self.temp_dir.name) / "food_web.md"
        html_out = Path(self.temp_dir.name) / "web.html"

        # 1. report --json
        with patch.object(sys, "argv", ["ecology.py", "report", "-w", str(self.world_dir), "--json"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 1)
                import json
                res = json.loads(mock_stdout.getvalue())
                self.assertEqual(res["world"], self.world_dir.name)
                self.assertEqual(res["species_count"], 1)

        # 2. report --write-note --html
        with patch.object(sys, "argv", ["ecology.py", "report", "-w", str(self.world_dir), "--write-note", str(note_out), "--html", str(html_out)]):
            with patch("sys.stdout", new_callable=io.StringIO):
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 1)
                self.assertTrue(note_out.is_file())
                self.assertTrue(html_out.is_file())

    def test_world_resolution_and_edge_cases(self):
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

    def test_parsing_invalid_numeric_fields(self):
        (self.world_dir / "Bestiary" / "Malformed.md").write_text("""---
name: "Malformed Beast"
trophic_level: "invalid"
biomass_kg: "invalid"
daily_caloric_demand: "invalid"
population_density: "invalid"
---
""", encoding="utf-8")
        species = extract_species_profiles(self.world_dir)
        self.assertIn("Malformed Beast", species)
        m = species["Malformed Beast"]
        self.assertEqual(m["trophic_level"], 2)
        self.assertEqual(m["biomass_kg"], 50.0)
        self.assertEqual(m["daily_caloric_demand"], 2500.0)
        self.assertEqual(m["population_density"], 10.0)


if __name__ == "__main__":
    unittest.main()

