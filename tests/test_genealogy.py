#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Dynastic Genealogies & Succession Lineages (scripts/lib/genealogy.py).
Covers family tree graph construction, biological/chronological paradox detection,
succession ranking, Mermaid.js code generation, HTML reporting, terminal tree rendering, and CLI.
"""

import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.genealogy import (
    generate_genealogy_html_report,
    generate_mermaid_flowchart,
    get_house_lineage,
    load_characters_and_houses,
    matches_house_or_character,
    normalize_house_token,
    parse_year,
    print_terminal_tree,
    resolve_world_dir,
    validate_genealogy,
    main,
)


class TestGenealogyEngine(unittest.TestCase):

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.world_dir = Path(self.temp_dir.name) / "World"
        self.chars_dir = self.world_dir / "Characters"
        self.chars_dir.mkdir(parents=True)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_parse_year(self) -> None:
        self.assertEqual(parse_year("450 BCE"), -450.0)
        self.assertEqual(parse_year("-300 IE"), -300.0)
        self.assertEqual(parse_year("1200 AC"), 1200.0)
        self.assertEqual(parse_year(500), 500.0)
        self.assertIsNone(parse_year(None))
        self.assertIsNone(parse_year(""))

    def test_load_characters_relationships(self) -> None:
        (self.chars_dir / "King_Eldor.md").write_text("""---
name: "King Eldor I"
type: character
house: "House Vance"
title: "High King"
born: "100 AC"
died: "165 AC"
succession_order: 1
---
""", encoding="utf-8")

        (self.chars_dir / "Prince_Valen.md").write_text("""---
name: "Prince Valen"
type: character
house: "House Vance"
title: "Crown Prince"
parents: ["[[King Eldor I]]"]
born: "125 AC"
died: "180 AC"
succession_order: 2
---
""", encoding="utf-8")

        chars = load_characters_and_houses(self.world_dir)
        self.assertIn("King Eldor I", chars)
        self.assertIn("Prince Valen", chars)
        self.assertIn("Prince Valen", chars["King Eldor I"]["children"])
        self.assertIn("King Eldor I", chars["Prince Valen"]["parents"])

    def test_chronological_paradox_child_before_parent_gen101(self) -> None:
        (self.chars_dir / "Parent.md").write_text("""---
name: "Parent"
born: "150 AC"
---
""", encoding="utf-8")

        (self.chars_dir / "Child.md").write_text("""---
name: "Child"
parents: ["[[Parent]]"]
born: "120 AC"
---
""", encoding="utf-8")

        chars = load_characters_and_houses(self.world_dir)
        findings = validate_genealogy(chars)
        self.assertTrue(any(f["id"] == "GEN-101" and "before or same year" in f["message"] for f in findings))

    def test_chronological_paradox_child_after_parent_deceased_gen101(self) -> None:
        (self.chars_dir / "DeceasedFather.md").write_text("""---
name: "DeceasedFather"
born: "100 AC"
died: "140 AC"
---
""", encoding="utf-8")

        (self.chars_dir / "LateChild.md").write_text("""---
name: "LateChild"
parents: ["[[DeceasedFather]]"]
born: "145 AC"
---
""", encoding="utf-8")

        chars = load_characters_and_houses(self.world_dir)
        findings = validate_genealogy(chars)
        self.assertTrue(any(f["id"] == "GEN-101" and "deceased" in f["message"] for f in findings))

    def test_fuzzy_generational_builder_skips_chron_checks(self) -> None:
        (self.chars_dir / "AncientAncestor.md").write_text("""---
name: "AncientAncestor"
born: "100 AC"
died: "150 AC"
---
""", encoding="utf-8")

        (self.chars_dir / "LateDescendant.md").write_text("""---
name: "LateDescendant"
parents: ["direct descendant via ~4 unrecorded generations from [[AncientAncestor]]"]
born: "300 AC"
---
""", encoding="utf-8")

        chars = load_characters_and_houses(self.world_dir)
        self.assertIn("AncientAncestor", chars["LateDescendant"]["parents"])
        self.assertIn("AncientAncestor", chars["LateDescendant"]["fuzzy_parents"])

        findings = validate_genealogy(chars)
        self.assertFalse(any(f["id"] == "GEN-101" and f["character"] == "LateDescendant" for f in findings))

    def test_lifespan_sanity_died_before_born_gen101(self) -> None:
        (self.chars_dir / "TimeTraveler.md").write_text("""---
name: "TimeTraveler"
born: "200 AC"
died: "180 AC"
---
""", encoding="utf-8")

        chars = load_characters_and_houses(self.world_dir)
        findings = validate_genealogy(chars)
        self.assertTrue(any(f["id"] == "GEN-101" and "died" in f["message"] for f in findings))

    def test_circular_ancestry_paradox_gen101(self) -> None:
        (self.chars_dir / "Alpha.md").write_text("""---
name: "Alpha"
parents: ["[[Beta]]"]
---
""", encoding="utf-8")

        (self.chars_dir / "Beta.md").write_text("""---
name: "Beta"
parents: ["[[Alpha]]"]
---
""", encoding="utf-8")

        chars = load_characters_and_houses(self.world_dir)
        findings = validate_genealogy(chars)
        self.assertTrue(any(f["id"] == "GEN-101" and "Circular ancestry" in f["message"] for f in findings))

    def test_succession_order_conflict_gen102(self) -> None:
        (self.chars_dir / "Claimant1.md").write_text("""---
name: "Claimant1"
house: "House Corrino"
succession_order: 1
---
""", encoding="utf-8")

        (self.chars_dir / "Claimant2.md").write_text("""---
name: "Claimant2"
house: "House Corrino"
succession_order: 1
---
""", encoding="utf-8")

        chars = load_characters_and_houses(self.world_dir)
        findings = validate_genealogy(chars)
        self.assertTrue(any(f["id"] == "GEN-102" and "#1" in f["message"] for f in findings))

    def test_mermaid_generation(self) -> None:
        (self.chars_dir / "Lord_Stark.md").write_text("""---
name: "Lord Stark"
house: "House Stark"
title: "Warden of the North"
born: "250 AC"
succession_order: 1
---
""", encoding="utf-8")

        chars = load_characters_and_houses(self.world_dir)
        mermaid = generate_mermaid_flowchart(chars, "House Stark")
        self.assertIn("```mermaid", mermaid)
        self.assertIn("flowchart TD", mermaid)
        self.assertIn("Lord Stark", mermaid)
        self.assertIn("👑 <b>#1</b>", mermaid)

    def test_lineage_roster_sorting(self) -> None:
        (self.chars_dir / "Prince_B.md").write_text("""---
name: "Prince B"
house: "House Tudor"
succession_order: 2
born: "1500"
---
""", encoding="utf-8")

        (self.chars_dir / "King_A.md").write_text("""---
name: "King A"
house: "House Tudor"
succession_order: 1
born: "1480"
---
""", encoding="utf-8")

        chars = load_characters_and_houses(self.world_dir)
        lineage = get_house_lineage(chars, "House Tudor")
        self.assertEqual(len(lineage), 2)
        self.assertEqual(lineage[0]["name"], "King A")
        self.assertEqual(lineage[1]["name"], "Prince B")

    def test_house_name_normalization_matching(self) -> None:
        (self.chars_dir / "Eddard.md").write_text("""---
name: "Eddard"
house: "Stark"
succession_order: 1
---
""", encoding="utf-8")

        self.assertEqual(normalize_house_token("The House of Stark"), "stark")
        self.assertEqual(normalize_house_token("Clan Dragon"), "dragon")

        chars = load_characters_and_houses(self.world_dir)
        lineage = get_house_lineage(chars, "House Stark")
        self.assertEqual(len(lineage), 1)
        self.assertEqual(lineage[0]["name"], "Eddard")

        self.assertTrue(matches_house_or_character(chars["Eddard"], "Stark"))

    def test_html_report_generation(self) -> None:
        (self.chars_dir / "Noble.md").write_text("""---
name: "Noble"
house: "House Vance"
---
""", encoding="utf-8")
        chars = load_characters_and_houses(self.world_dir)
        mermaid = generate_mermaid_flowchart(chars, "House Vance")
        lineage = get_house_lineage(chars, "House Vance")
        out_html = self.world_dir / "genealogy.html"
        generate_genealogy_html_report("House Vance", mermaid, lineage, [], out_html)
        self.assertTrue(out_html.is_file())
        content = out_html.read_text(encoding="utf-8")
        self.assertIn("Dynastic Genealogy", content)
        self.assertIn("Content-Security-Policy", content)

    def test_terminal_tree_output(self) -> None:
        (self.chars_dir / "King.md").write_text("""---
name: "High King"
title: "Sovereign"
succession_order: 1
children: ["[[Prince]]"]
spouses: ["Queen"]
---
""", encoding="utf-8")
        (self.chars_dir / "Prince.md").write_text("""---
name: "Prince"
title: "Heir"
succession_order: 2
---
""", encoding="utf-8")

        chars = load_characters_and_houses(self.world_dir)
        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            print_terminal_tree(chars, "High King")
            output = mock_stdout.getvalue()
            self.assertIn("High King", output)
            self.assertIn("Prince", output)
            self.assertIn("Spouse", output)

    def test_resolve_world_dir(self) -> None:
        self.assertEqual(resolve_world_dir(str(self.world_dir)), str(self.world_dir.resolve()))

    def test_cli_main_tree_and_lineage(self) -> None:
        (self.chars_dir / "King.md").write_text("""---
name: "High King"
house: "House Vance"
succession_order: 1
---
""", encoding="utf-8")
        self.world_dir / "cli_tree.html"

    def test_load_characters_father_mother_and_strings(self) -> None:
        (self.chars_dir / "Lady_Aria.md").write_text("""---
name: "Lady Aria"
father: "Lord Corvo"
mother: "Lady Beatrix"
spouse: "Lord Dan"
child: "Little Leo"
succession_order: "invalid_order"
---
""", encoding="utf-8")
        chars = load_characters_and_houses(self.world_dir)
        self.assertIn("Lady Aria", chars)
        self.assertIn("Lord Corvo", chars["Lady Aria"]["parents"])
        self.assertIn("Lady Beatrix", chars["Lady Aria"]["parents"])
        self.assertIn("Lord Dan", chars["Lady Aria"]["spouses"])
        self.assertIn("Little Leo", chars["Lady Aria"]["children"])
        self.assertIsNone(chars["Lady Aria"]["succession_order"])

    def test_cli_mermaid_and_human_readable(self) -> None:
        (self.chars_dir / "King.md").write_text("""---
name: "High King"
house: "House Vance"
succession_order: 1
---
""", encoding="utf-8")
        # Mermaid flag
        with patch.object(sys, "argv", ["genealogy.py", "tree", "House Vance", "-w", str(self.world_dir), "--mermaid"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                main()
                self.assertIn("flowchart TD", mock_stdout.getvalue())

        # Human readable tree output
        with patch.object(sys, "argv", ["genealogy.py", "tree", "High King", "-w", str(self.world_dir)]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                main()
                self.assertIn("High King", mock_stdout.getvalue())

        # Human readable lineage output
        with patch.object(sys, "argv", ["genealogy.py", "lineage", "House Vance", "-w", str(self.world_dir)]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                main()
                self.assertIn("High King", mock_stdout.getvalue())

        # Lineage with unknown house
        with patch.object(sys, "argv", ["genealogy.py", "lineage", "House Nonexistent", "-w", str(self.world_dir)]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                main()
                self.assertIn("No characters found", mock_stdout.getvalue())

    def test_cli_no_args_and_errors(self) -> None:
        # No subcommand -> help
        with patch.object(sys, "argv", ["genealogy.py"]):
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 0)

        # Invalid world dir
        with patch.object(sys, "argv", ["genealogy.py", "tree", "House Vance", "-w", "nonexistent_world_123"]):
            with patch("sys.stderr", new_callable=io.StringIO):
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 2)

    def test_cli_json_and_html_modes(self) -> None:
        (self.chars_dir / "King.md").write_text("""---
name: "High King"
house: "House Vance"
succession_order: 1
---
""", encoding="utf-8")
        html_out = self.world_dir / "tree.html"

        # 1. tree --json
        with patch.object(sys, "argv", ["genealogy.py", "tree", "House Vance", "-w", str(self.world_dir), "--json"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                main()
                import json
                res = json.loads(mock_stdout.getvalue())
                self.assertEqual(res["target"], "House Vance")
                self.assertEqual(res["lineage_count"], 1)

        # 1b. tree --html
        with patch.object(sys, "argv", ["genealogy.py", "tree", "House Vance", "-w", str(self.world_dir), "--html", str(html_out)]):
            with patch("sys.stdout", new_callable=io.StringIO):
                main()
                self.assertTrue(html_out.is_file())

        # 2. lineage --json
        with patch.object(sys, "argv", ["genealogy.py", "lineage", "House Vance", "-w", str(self.world_dir), "--json"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                main()
                import json
                res = json.loads(mock_stdout.getvalue())
                self.assertEqual(res["house"], "House Vance")
                self.assertEqual(len(res["members"]), 1)

        # 3. tree for house without direct name match (prints House Members)
        with patch.object(sys, "argv", ["genealogy.py", "tree", "House Vance", "-w", str(self.world_dir)]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                main()
                self.assertIn("House Members", mock_stdout.getvalue())

    def test_world_resolution_and_edge_cases(self) -> None:
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

    def test_html_report_with_findings(self) -> None:
        out_html = self.world_dir / "findings_genealogy.html"
        findings = [{"severity": "FATAL", "id": "GEN-101", "message": "Paradox detected", "file": "King.md"}]
        generate_genealogy_html_report("House Vance", "flowchart TD\nA-->B", [], findings, out_html)
        self.assertTrue(out_html.is_file())
        self.assertIn("Genealogy Paradox Findings", out_html.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

