#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum 6D Sensory Palette & White Room Engine (scripts/lib/senses.py).
"""

import io
import json
import tempfile
import unittest
from pathlib import Path
import sys
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.senses import (
    analyze_text_senses,
    audit_manuscript_senses,
    generate_senses_html_report,
    resolve_manuscript_dir,
    main,
)


class TestSensesEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.ms_dir = Path(self.temp_dir.name) / "Manuscript"
        self.ms_dir.mkdir(parents=True)
        (self.ms_dir / "Book-01" / "01_Act_I").mkdir(parents=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_analyze_text_senses(self):
        sample = """
        The crimson banner fluttered in the darkness. A deafening roar echoed through the stone hall.
        The pungent aroma of sulfur and burning smoke filled his nostrils, while the bitter taste of ash
        lingered on his tongue. Freezing rain struck his rough skin as vertigo made him stumble with dizziness.
        """
        res = analyze_text_senses(sample)
        self.assertGreater(res["counts"]["visual"], 0)
        self.assertGreater(res["counts"]["auditory"], 0)
        self.assertGreater(res["counts"]["olfactory"], 0)
        self.assertGreater(res["counts"]["gustatory"], 0)
        self.assertGreater(res["counts"]["tactile_thermal"], 0)
        self.assertGreater(res["counts"]["kinesthetic_vestibular"], 0)

    def test_white_room_and_monotony_detection(self):
        white_room_text = "The room was large and rectangular with white walls and a grey ceiling. " * 20
        (self.ms_dir / "Book-01" / "01_Act_I" / "01_WhiteRoom.md").write_text(white_room_text, encoding="utf-8")

        audit = audit_manuscript_senses(self.ms_dir)
        findings = audit["findings"]
        ids = [f["id"] for f in findings]

        self.assertIn("SNS-101", ids)

    def test_sensory_monotony_sns102(self):
        visual_phrase = (
            "The crimson shadow gleamed across the azure gloom. "
            "Scarlet silhouettes shimmered in the amber darkness. "
            "An ivory pallor bathed the ebony emerald edifice. "
            "The vivid golden radiance flickered in translucent murk. "
            "Cobalt and indigo gleam sparkled in the brilliant glare. "
        )
        long_visual_scene = visual_phrase * 12
        (self.ms_dir / "Book-01" / "01_Act_I" / "02_Monotony.md").write_text(
            long_visual_scene, encoding="utf-8"
        )
        audit = audit_manuscript_senses(self.ms_dir)
        ids = [f["id"] for f in audit["findings"]]
        self.assertIn("SNS-102", ids)

    def test_generate_senses_html_report(self):
        (self.ms_dir / "Book-01" / "01_Act_I" / "01_Scene.md").write_text("""# Scene
The scarlet sun sank in silence. The icy wind howled.
""", encoding="utf-8")
        audit = audit_manuscript_senses(self.ms_dir)
        html_out = Path(self.temp_dir.name) / "senses.html"
        generate_senses_html_report(audit, html_out)
        self.assertTrue(html_out.is_file())
        self.assertIn("Sensory Palette", html_out.read_text(encoding="utf-8"))

    def test_resolve_manuscript_dir(self):
        self.assertEqual(resolve_manuscript_dir(str(self.ms_dir)), str(self.ms_dir.resolve()))
        # Empty string handling
        res_empty = resolve_manuscript_dir(None)
        self.assertIsInstance(res_empty, str)

    def test_cli_main(self):
        (self.ms_dir / "Book-01" / "01_Act_I" / "01_Scene.md").write_text("""# Scene
The scarlet sun sank in silence. The icy wind howled. The aroma of pine filled the air.
The bitter taste of ash was on his lips as rough stone scratched him and vertigo struck.
""", encoding="utf-8")

        html_out = Path(self.temp_dir.name) / "cli_senses.html"
        # CLI JSON
        with patch.object(sys, "argv", ["senses.py", str(self.ms_dir), "--json"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertIn(cm.exception.code, (0, 1))
                data = json.loads(mock_stdout.getvalue())
                self.assertIn("overall_percentages", data)

        # CLI HTML & Human readable
        with patch.object(sys, "argv", ["senses.py", str(self.ms_dir), "--html", str(html_out)]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertIn(cm.exception.code, (0, 1))
                self.assertTrue(html_out.is_file())
                self.assertIn("Sensory Distribution", mock_stdout.getvalue())

    def test_resolve_manuscript_dir_edge_cases(self):
        # 1. Single manuscript in home/Manuscripts
        fake_home = Path(self.temp_dir.name) / "FakeHome"
        (fake_home / "Manuscripts" / "BookAlpha").mkdir(parents=True)
        with patch("pathlib.Path.home", return_value=fake_home):
            res_single = resolve_manuscript_dir(None)
            self.assertIn("BookAlpha", res_single)

            # Match by name in home/Manuscripts
            res_name = resolve_manuscript_dir("bookalpha")
            self.assertIn("BookAlpha", res_name)

            # Multiple manuscripts error
            (fake_home / "Manuscripts" / "BookBeta").mkdir(parents=True)
            with patch("sys.stderr", new_callable=io.StringIO) as mock_err:
                with self.assertRaises(SystemExit) as cm:
                    resolve_manuscript_dir(None)
                self.assertEqual(cm.exception.code, 2)
                self.assertIn("Multiple manuscripts discovered", mock_err.getvalue())

    def test_cli_clean_scene_ok_output(self):
        clean_ms = Path(self.temp_dir.name) / "CleanMs"
        (clean_ms / "Book-01").mkdir(parents=True)
        (clean_ms / "Book-01" / "01_Scene.md").write_text("""# Scene 1
The red flame danced brightly. The sweet honey tasted delicious.
The sulfur aroma filled the hall as a thunderous roar resonated.
Rough granite bit into his fingers as dizziness spun the world.
""", encoding="utf-8")
        with patch.object(sys, "argv", ["senses.py", str(clean_ms)]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 0)
                self.assertIn("[OK] Multi-sensory grounding is well-balanced", mock_stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
