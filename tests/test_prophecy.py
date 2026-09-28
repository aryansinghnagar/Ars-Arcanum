#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Prophecy Resolution Matrix (scripts/lib/prophecy.py).
"""

import io
import tempfile
import unittest
from pathlib import Path
import sys
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.prophecy import (
    extract_prophecies,
    audit_prophecy_resolution,
    generate_prophecy_mermaid,
    generate_prophecy_html_report,
    main,
)


class TestProphecyEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.world_dir = Path(self.temp_dir.name) / "World"
        self.ms_dir = Path(self.temp_dir.name) / "Manuscript"
        self.world_dir.mkdir(parents=True)
        self.ms_dir.mkdir(parents=True)
        (self.world_dir / "Cosmology" / "Prophecies").mkdir(parents=True)
        (self.ms_dir / "Book-01" / "01_Act_I").mkdir(parents=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_extract_and_audit_prophecy(self):
        (self.world_dir / "Cosmology" / "Prophecies" / "The_Bleeding_Star.md").write_text("""---
name: "The Bleeding Star"
type: prophecy
oracle: "[[Pythia of Delphi]]"
target_entity: "[[Chosen King]]"
status: unfulfilled
clauses:
  - "When the red star bleeds across the dawn"
  - "The shattered crown shall be remade"
---
# The Bleeding Star
""", encoding="utf-8")

        (self.ms_dir / "Book-01" / "01_Act_I" / "01_Scene.md").write_text("""# Chapter 1
The priest recalled The Bleeding Star prophecy as the red meteor streaked overhead.
@prophecy: The Bleeding Star
""", encoding="utf-8")

        prophecies = extract_prophecies(self.world_dir)
        self.assertIn("The Bleeding Star", prophecies)
        self.assertEqual(prophecies["The Bleeding Star"]["oracle"], "Pythia of Delphi")
        self.assertEqual(len(prophecies["The Bleeding Star"]["clauses"]), 2)

        findings = audit_prophecy_resolution(prophecies, self.ms_dir)
        self.assertEqual(len(findings), 0)

        mermaid = generate_prophecy_mermaid(prophecies)
        self.assertIn("stateDiagram-v2", mermaid)

    def test_orphan_prophecy_prp101(self):
        (self.world_dir / "Cosmology" / "Prophecies" / "Forgotten_Fate.md").write_text("""---
name: "Forgotten Fate"
type: prophecy
status: unfulfilled
---
""", encoding="utf-8")

        (self.ms_dir / "Book-01" / "01_Act_I" / "01_Scene.md").write_text("""# Chapter 1
A quiet day at the bakery with fresh warm bread.
""", encoding="utf-8")

        prophecies = extract_prophecies(self.world_dir)
        findings = audit_prophecy_resolution(prophecies, self.ms_dir)

        ids = [f["id"] for f in findings]
        self.assertIn("PRP-101", ids)

    def test_dead_chosen_one_prp102(self):
        (self.world_dir / "Characters").mkdir(parents=True, exist_ok=True)
        (self.world_dir / "Characters" / "Chosen_One.md").write_text("""---
name: "Chosen One"
type: character
status: deceased
death_year: "450 AC"
---
""", encoding="utf-8")
        (self.world_dir / "Cosmology" / "Prophecies" / "Fate.md").write_text("""---
name: "Ancient Fate"
type: prophecy
target_entity: "[[Chosen One]]"
status: unfulfilled
---
""", encoding="utf-8")
        prophecies = extract_prophecies(self.world_dir)
        findings = audit_prophecy_resolution(prophecies, world_dir=self.world_dir)
        ids = [f["id"] for f in findings]
        self.assertIn("PRP-102", ids)

    def test_prp103_status_discrepancy(self):
        (self.world_dir / "Cosmology" / "Prophecies" / "Secret_Fate.md").write_text("""---
name: "Secret Fate"
type: prophecy
status: fulfilled
oracle: "Seer"
clauses: ["The door opens"]
---
""", encoding="utf-8")
        (self.ms_dir / "Book-01" / "01_Act_I" / "01_Scene.md").write_text("""# Chapter 1
A quiet day with no mention of anything special.
""", encoding="utf-8")
        prophecies = extract_prophecies(self.world_dir)
        findings = audit_prophecy_resolution(prophecies, self.ms_dir)
        ids = [f["id"] for f in findings]
        self.assertIn("PRP-103", ids)

    def test_subverted_and_broken_prophecies_mermaid(self):
        (self.world_dir / "Cosmology" / "Prophecies" / "Subverted.md").write_text("""---
name: "Subverted Fate"
type: prophecy
status: subverted
oracle: Oracle A
---
""", encoding="utf-8")
        (self.world_dir / "Cosmology" / "Prophecies" / "Broken.md").write_text("""---
name: "Broken Oath"
type: prophecy
status: broken
oracle: Oracle B
---
""", encoding="utf-8")
        prophecies = extract_prophecies(self.world_dir)
        mermaid = generate_prophecy_mermaid(prophecies)
        self.assertIn("Subverted", mermaid)
        self.assertIn("Broken", mermaid)

    def test_generate_prophecy_html_report_all_statuses(self):
        (self.world_dir / "Cosmology" / "Prophecies" / "Test_Prophecy.md").write_text("""---
name: "Solar Prophecy"
type: prophecy
status: partially_fulfilled
clauses:
  - "The sun rises"
---
""", encoding="utf-8")
        (self.world_dir / "Cosmology" / "Prophecies" / "Broken_Prophecy.md").write_text("""---
name: "Lunar Prophecy"
type: prophecy
status: broken
---
""", encoding="utf-8")
        prophecies = extract_prophecies(self.world_dir)
        html_out = Path(self.temp_dir.name) / "prophecy.html"
        generate_prophecy_html_report({
            "world": "TestWorld",
            "prophecies": prophecies,
            "findings": [{"id": "PRP-101", "severity": "WARNING", "message": "Orphan", "file": "test.md"}]
        }, html_out)
        self.assertTrue(html_out.is_file())
        content = html_out.read_text(encoding="utf-8")
        self.assertIn("Solar Prophecy", content)
        self.assertIn("Lunar Prophecy", content)
        self.assertIn("badge-warning", content)

    def test_cli_json_and_options(self):
        (self.world_dir / "Cosmology" / "Prophecies" / "Fate.md").write_text("""---
name: "Ancient Fate"
type: prophecy
oracle: "Seer"
target_entity: "Chosen"
clauses: "The bell shall toll"
status: unfulfilled
---
""", encoding="utf-8")
        (self.ms_dir / "Book-01" / "01_Act_I" / "01_Chapter.md").write_text("""# Chapter 1
@prophecy: Ancient Fate
The bell tolled.
""", encoding="utf-8")
        note_out = Path(self.temp_dir.name) / "lifecycle.md"
        html_out = Path(self.temp_dir.name) / "out.html"

        # 1. Test JSON output
        with patch.object(sys, "argv", ["prophecy.py", "report", "-w", str(self.world_dir), "-m", str(self.ms_dir), "--json"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 0)
                import json
                parsed = json.loads(mock_stdout.getvalue())
                self.assertEqual(parsed["world"], self.world_dir.name)
                self.assertEqual(parsed["prophecies_count"], 1)

        # 2. Test file writes
        with patch.object(sys, "argv", ["prophecy.py", "report", "-w", str(self.world_dir), "-m", str(self.ms_dir), "--write-note", str(note_out), "--html", str(html_out)]):
            with patch("sys.stdout", new_callable=io.StringIO):
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 0)
                self.assertTrue(note_out.is_file())
                self.assertTrue(html_out.is_file())

    def test_cli_human_readable_check_and_report(self):
        (self.world_dir / "Cosmology" / "Prophecies" / "Fate.md").write_text("""---
name: "Ancient Fate"
type: prophecy
oracle: "Seer"
target_entity: "Chosen"
clauses: "The bell shall toll"
status: unfulfilled
---
""", encoding="utf-8")
        (self.ms_dir / "Book-01" / "01_Act_I" / "01_Chapter.md").write_text("# Chapter 1\nNo prophecies mentioned.\n", encoding="utf-8")
        # Check with stdout
        with patch.object(sys, "argv", ["prophecy.py", str(self.world_dir), str(self.ms_dir)]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 1)
                self.assertIn("Prophecy Resolution Matrix", mock_stdout.getvalue())
                self.assertIn("Ancient Fate", mock_stdout.getvalue())

    def test_cli_errors_and_path_resolution(self):
        # Invalid world dir
        with patch.object(sys, "argv", ["prophecy.py", "check", "nonexistent_world_123"]):
            with patch("sys.stderr", new_callable=io.StringIO):
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 2)

        from lib.prophecy import resolve_manuscript_dir, resolve_world_dir, clean_link_name
        self.assertEqual(clean_link_name(""), "")
        self.assertEqual(clean_link_name("[[Oracle of Delphi]]"), "Oracle of Delphi")
        self.assertEqual(resolve_manuscript_dir(str(self.ms_dir)), str(self.ms_dir.resolve()))
        self.assertEqual(resolve_manuscript_dir(""), "")

        # Test resolving world from Universe / World fallback
        temp_home = Path(self.temp_dir.name) / "home"
        (temp_home / "Universes" / "Cosmos" / "Aethelgard").mkdir(parents=True)
        with patch("pathlib.Path.home", return_value=temp_home):
            res = resolve_world_dir("Aethelgard")
            self.assertTrue(res.endswith("Aethelgard"))
            # Test default single universe
            res2 = resolve_world_dir(None)
            self.assertTrue(res2.endswith("Aethelgard"))

            # Test multiple worlds
            (temp_home / "Universes" / "Cosmos" / "Valendor").mkdir(parents=True)
            with patch("sys.stderr", new_callable=io.StringIO):
                with self.assertRaises(SystemExit) as cm:
                    resolve_world_dir(None)
                self.assertEqual(cm.exception.code, 2)


if __name__ == "__main__":
    unittest.main()

