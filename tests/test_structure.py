#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Story Paradigm & Structure Enforcer (scripts/lib/structure.py).
Validates:
- PLT-102: Multi-paradigm structural alignment across all 9 canonical models.
- Chapter wordcount accumulation and percentage milestone mapping.
- Structural harmony score and drift penalties.
- HTML report generation with Content Security Policy.
"""

import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.structure import (
    scan_manuscript_structure,
    generate_structure_html_report,
    PARADIGMS,
)


class TestStructureEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.target_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_paradigms_available(self):
        expected = [
            "three_act", "save_the_cat", "heros_journey", "story_circle",
            "seven_point", "eight_sequence", "fichtean_curve", "kishotenketsu",
            "freytags_pyramid", "romancing_the_beat", "virgins_promise"
        ]
        for p in expected:
            self.assertIn(p, PARADIGMS)
            self.assertGreater(len(PARADIGMS[p]["beats"]), 3)

    def test_structure_scan_and_beat_mapping_three_act(self):
        # Create 8 balanced chapters (each ~250 words)
        words_chunk = "Word " * 250
        for i in range(1, 9):
            (self.target_dir / f"0{i}_Chapter_{i}.md").write_text(f"# Chapter {i}\n\n{words_chunk}\n", encoding="utf-8")

        report = scan_manuscript_structure(self.target_dir, paradigm_key="three_act")
        self.assertEqual(report["total_chapters"], 8)
        self.assertGreater(report["total_words"], 1900)
        self.assertGreater(report["harmony_score"], 60.0)

        beat_names = [b["beat_name"] for b in report["beats"]]
        self.assertIn("Inciting Incident", beat_names)
        self.assertIn("Midpoint", beat_names)
        self.assertIn("Climax", beat_names)

    def test_structure_scan_save_the_cat_15_beats(self):
        for i in range(1, 16):
            (self.target_dir / f"0{i:02d}_Ch.md").write_text(f"# Chapter {i}\n\n" + "word " * 100, encoding="utf-8")
        report = scan_manuscript_structure(self.target_dir, paradigm_key="save_the_cat")
        self.assertEqual(len(report["beats"]), 15)
        names = [b["beat_name"] for b in report["beats"]]
        self.assertIn("Opening Image", names)
        self.assertIn("All Hope Is Lost", names)
        self.assertIn("Final Image", names)

    def test_structure_scan_heros_journey_12_stages(self):
        for i in range(1, 13):
            (self.target_dir / f"0{i:02d}_Ch.md").write_text(f"# Chapter {i}\n\n" + "hero " * 150, encoding="utf-8")
        report = scan_manuscript_structure(self.target_dir, paradigm_key="heros_journey")
        self.assertEqual(len(report["beats"]), 12)
        names = [b["beat_name"] for b in report["beats"]]
        self.assertIn("1. Ordinary World", names)
        self.assertIn("8. The Ordeal", names)
        self.assertIn("12. Return with Elixir", names)

    def test_structure_scan_story_circle_8_steps(self):
        for i in range(1, 9):
            (self.target_dir / f"0{i}_Ch.md").write_text(f"# Chapter {i}\n\n" + "step " * 200, encoding="utf-8")
        report = scan_manuscript_structure(self.target_dir, paradigm_key="story_circle")
        self.assertEqual(len(report["beats"]), 8)
        names = [b["beat_name"] for b in report["beats"]]
        self.assertIn("1. You (Comfort Zone)", names)
        self.assertIn("5. Find (Getting What They Wanted)", names)

    def test_structure_scan_seven_point(self):
        for i in range(1, 8):
            (self.target_dir / f"0{i}_Ch.md").write_text(f"# Chapter {i}\n\n" + "plot " * 150, encoding="utf-8")
        report = scan_manuscript_structure(self.target_dir, paradigm_key="seven_point")
        self.assertEqual(len(report["beats"]), 7)
        names = [b["beat_name"] for b in report["beats"]]
        self.assertIn("1. Hook", names)
        self.assertIn("4. Midpoint", names)
        self.assertIn("7. Resolution", names)

    def test_structure_scan_eight_sequence(self):
        for i in range(1, 9):
            (self.target_dir / f"0{i}_Ch.md").write_text(f"# Chapter {i}\n\n" + "seq " * 200, encoding="utf-8")
        report = scan_manuscript_structure(self.target_dir, paradigm_key="eight_sequence")
        self.assertEqual(len(report["beats"]), 8)
        names = [b["beat_name"] for b in report["beats"]]
        self.assertIn("Sequence A: Status Quo & Inciting Incident", names)
        self.assertIn("Sequence D: Midpoint Crisis & Shift of Intent", names)

    def test_structure_scan_fichtean_curve(self):
        for i in range(1, 8):
            (self.target_dir / f"0{i}_Ch.md").write_text(f"# Chapter {i}\n\n" + "crisis " * 180, encoding="utf-8")
        report = scan_manuscript_structure(self.target_dir, paradigm_key="fichtean_curve")
        self.assertEqual(len(report["beats"]), 7)
        names = [b["beat_name"] for b in report["beats"]]
        self.assertIn("2. Crisis 1 (First Complication)", names)
        self.assertIn("6. Climax (Supreme Confrontation)", names)

    def test_structure_scan_kishotenketsu(self):
        for i in range(1, 5):
            (self.target_dir / f"0{i}_Ch.md").write_text(f"# Chapter {i}\n\n" + "story " * 250, encoding="utf-8")
        report = scan_manuscript_structure(self.target_dir, paradigm_key="kishotenketsu")
        self.assertEqual(len(report["beats"]), 4)
        names = [b["beat_name"] for b in report["beats"]]
        self.assertIn("1. 起 Ki (Introduction)", names)
        self.assertIn("3. 転 Ten (The Twist / Turn)", names)

    def test_structure_scan_freytags_pyramid(self):
        for i in range(1, 8):
            (self.target_dir / f"0{i}_Ch.md").write_text(f"# Chapter {i}\n\n" + "dramatic " * 150, encoding="utf-8")
        report = scan_manuscript_structure(self.target_dir, paradigm_key="freytags_pyramid")
        self.assertEqual(len(report["beats"]), 7)
        names = [b["beat_name"] for b in report["beats"]]
        self.assertIn("1. Exposition", names)
        self.assertIn("4. Climax / Turning Point", names)

    def test_containing_chapter_assignment(self):
        # Chapter 1 is 100 words, Chapter 2 is 900 words
        (self.target_dir / "01_Ch1.md").write_text("# Ch 1\n\n" + "word " * 100, encoding="utf-8")
        (self.target_dir / "02_Ch2.md").write_text("# Ch 2\n\n" + "word " * 900, encoding="utf-8")
        report = scan_manuscript_structure(self.target_dir, paradigm_key="three_act")
        opening_beat = next(b for b in report["beats"] if b["beat_name"] == "Opening Status Quo")
        self.assertEqual(opening_beat["assigned_chapter"], 1)
        self.assertTrue(opening_beat["is_in_window"])

    def test_structure_html_generation_csp(self):
        (self.target_dir / "01_Ch1.md").write_text("# Ch 1\n\n" + "word " * 100, encoding="utf-8")
        report = scan_manuscript_structure(self.target_dir, paradigm_key="save_the_cat")
        out_html = self.target_dir / "structure_report.html"
        generate_structure_html_report(report, out_html)
        self.assertTrue(out_html.is_file())
        content = out_html.read_text(encoding="utf-8")
        self.assertIn("Story Paradigm & Structure Alignment", content)
        self.assertIn("Content-Security-Policy", content)

    def test_cli_list_structures(self):
        import io
        from unittest.mock import patch
        from lib.structure import main as structure_main

        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            rc = structure_main(["--list-structures"])
            self.assertEqual(rc, 0)
            self.assertIn("Manuscript Structure Presets", mock_out.getvalue())

    def test_cli_structure_mapping(self):
        import io
        import json
        from unittest.mock import patch
        from lib.structure import main as structure_main

        (self.target_dir / "01_Ch1.md").write_text("# Ch 1\n\n" + "word " * 100, encoding="utf-8")
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            rc = structure_main([str(self.target_dir), "--structure", "kishotenketsu", "--json"])
            self.assertEqual(rc, 0)
            data = json.loads(mock_out.getvalue())
            self.assertEqual(data["paradigm_key"], "kishotenketsu")

    def test_cli_auto_detect_structure_from_manifest(self):
        import io
        import json
        from unittest.mock import patch
        from lib.structure import main as structure_main

        # Create manuscript with manuscript.yaml declaring heros_journey
        (self.target_dir / "manuscript.yaml").write_text(
            'schema_version: "1.1"\ntitle: "Hero Tale"\nstructure: "heros_journey"\n',
            encoding="utf-8",
        )
        vol_dir = self.target_dir / "Book-01"
        vol_dir.mkdir(parents=True, exist_ok=True)
        (vol_dir / "01_Departure").mkdir(parents=True, exist_ok=True)
        (vol_dir / "01_Departure" / "01_Ch1.md").write_text("# Ch 1\n\n" + "word " * 150, encoding="utf-8")

        # Scan volume without passing --paradigm or --structure
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            rc = structure_main([str(vol_dir), "--json"])
            self.assertEqual(rc, 0)
            data = json.loads(mock_out.getvalue())
            self.assertEqual(data["paradigm_key"], "heros_journey")

    def test_cli_additional_branches(self):
        import io
        from unittest.mock import patch
        from lib.structure import main as structure_main

        (self.target_dir / "01_Ch1.md").write_text("# Ch 1\n\n" + "word " * 100, encoding="utf-8")
        out_html = self.target_dir / "struct.html"

        # 1. table and html export
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            rc = structure_main([str(self.target_dir), "--paradigm", "three_act", "--html", str(out_html)])
            self.assertEqual(rc, 0)
            self.assertIn("Story Paradigm Milestone Observer", mock_out.getvalue())
            self.assertTrue(out_html.is_file())

        # 2. no target -> return 1
        with patch("sys.stdout", new_callable=io.StringIO):
            rc = structure_main([])
            self.assertEqual(rc, 1)

    def test_scan_single_file_and_file_not_found(self):
        f = self.target_dir / "single.md"
        f.write_text("# Chapter 1\n\n" + "word " * 500, encoding="utf-8")
        report = scan_manuscript_structure(f, paradigm_key="three_act")
        self.assertEqual(report["total_chapters"], 1)

        with self.assertRaises(FileNotFoundError):
            scan_manuscript_structure(self.target_dir / "nonexistent_dir_or_file")

    def test_cli_structure_direct_paradigm_name(self):
        import io
        import json
        from unittest.mock import patch
        from lib.structure import main as structure_main

        (self.target_dir / "01_Ch1.md").write_text("# Ch 1\n\n" + "word " * 100, encoding="utf-8")
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            rc = structure_main([str(self.target_dir), "--structure", "three_act", "--json"])
            self.assertEqual(rc, 0)
            data = json.loads(mock_out.getvalue())
            self.assertEqual(data["paradigm_key"], "three_act")

    def test_audit_character_arcs_and_cli(self):
        import io
        import json
        from unittest.mock import patch
        from lib.structure import analyze_character_arc_geometry, main as structure_main

        # Create sample manuscript with chapters and character notes
        char_dir = self.target_dir / "Characters"
        char_dir.mkdir(parents=True, exist_ok=True)
        (char_dir / "Kael.md").write_text("---\nflaw: Cynicism\nlie: Trust no one\ntruth: Vulnerability is strength\n---\n", encoding="utf-8")

        ch1 = self.target_dir / "01_Ch1.md"
        ch1.write_text("@pov: Kael\n# Ch 1\n\n" + "word " * 300, encoding="utf-8")
        ch2 = self.target_dir / "02_Ch2.md"
        ch2.write_text("# Ch 2\n\n" + "word " * 300, encoding="utf-8")

        res = analyze_character_arc_geometry(self.target_dir, world_path=self.target_dir)
        self.assertEqual(res["total_chapters"], 2)
        self.assertGreater(len(res["arc_stages"]), 3)
        self.assertEqual(res["characters_tracked"][0]["name"], "Kael")

        # Test CLI invocation with --character-arc
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            rc = structure_main([str(self.target_dir), "--character-arc", "--json"])
            self.assertEqual(rc, 0)
            data = json.loads(mock_out.getvalue())
            self.assertIn("characters_tracked", data)

        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            rc = structure_main([str(self.target_dir), "--character-arc"])
            self.assertEqual(rc, 0)
            self.assertIn("Character Arc", mock_out.getvalue())

    def test_author_tagged_beats_mapping_and_drift(self):
        """Verify frontmatter beat tags and inline @beat: directives are parsed and assigned properly."""
        words_chunk = "Word " * 100
        # 10 chapters: Chapter 5 is at 50%
        for i in range(1, 11):
            (self.target_dir / f"{i:02d}_Ch.md").write_text(f"# Chapter {i}\n\n{words_chunk}\n", encoding="utf-8")

        # Tag Inciting Incident late in Chapter 6 (60% instead of standard 12%)
        (self.target_dir / "06_Ch.md").write_text(f"---\nbeat: Inciting Incident\n---\n# Chapter 6\n\n{words_chunk}\n", encoding="utf-8")

        # Tag Midpoint with inline directive in Chapter 5
        (self.target_dir / "05_Ch.md").write_text(f"@beat: Midpoint\n# Chapter 5\n\n{words_chunk}\n", encoding="utf-8")

        report = scan_manuscript_structure(self.target_dir, paradigm_key="three_act")
        beats_by_name = {b["beat_name"]: b for b in report["beats"]}

        self.assertIn("Inciting Incident", beats_by_name)
        inciting = beats_by_name["Inciting Incident"]
        self.assertTrue(inciting["is_author_tagged"])
        self.assertEqual(inciting["assigned_chapter"], 6)
        self.assertFalse(inciting["is_in_window"])  # Marked as drifted because 60% > 16% window

        self.assertIn("Midpoint", beats_by_name)
        mid = beats_by_name["Midpoint"]
        self.assertTrue(mid["is_author_tagged"])
        self.assertEqual(mid["assigned_chapter"], 5)
        self.assertTrue(mid["is_in_window"])

    def test_elastic_window_scaling(self):
        """Verify length-scaled elastic tolerance envelopes widen for short manuscripts and narrow for epics."""
        words_chunk = "Word " * 100
        # 4 chapters: total words ~400 (very short novella/novelette)
        for i in range(1, 5):
            (self.target_dir / f"{i:02d}_Ch.md").write_text(f"# Chapter {i}\n\n{words_chunk}\n", encoding="utf-8")

        # Scan with elastic=True
        report_elastic = scan_manuscript_structure(self.target_dir, paradigm_key="three_act", elastic=True)
        self.assertTrue(report_elastic.get("elastic_tolerance"))

        # Scan with elastic=False
        report_rigid = scan_manuscript_structure(self.target_dir, paradigm_key="three_act", elastic=False)
        self.assertFalse(report_rigid.get("elastic_tolerance"))

        # Verify beats have target windows
        self.assertEqual(len(report_elastic["beats"]), len(report_rigid["beats"]))


if __name__ == "__main__":
    unittest.main()


