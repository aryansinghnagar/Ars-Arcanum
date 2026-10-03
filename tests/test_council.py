#!/usr/bin/env python3
"""
Unit and Integration Tests for Ars Arcanum Multi-Perspective Editorial Council Engine
(tests/test_council.py)
================================================================================
"""

import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.lib.council import (
    evaluate_lore_auditor,
    evaluate_plot_doctor,
    evaluate_sensory_stylist,
    evaluate_voice_coach,
    main as council_main,
    render_council_html,
    render_council_markdown,
    run_editorial_council,
    score_to_grade,
)


class TestEditorialCouncilEngine(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

        self.sample_manuscript = self.root / "chapter_01.md"
        self.sample_manuscript.write_text(
            """# Chapter 1: The Broken Oath

Dawn broke over the high towers of Aethelgard. A cold, bitter wind wailed through the iron ramparts.
Elena felt the icy stone bite into her palms. She heard the distant roar of thunder. The air smelled of acrid ozone and burnt brimstone.

"Archon Valerius will not arrive before sunset," Marcus said quietly.

"He promised to bring the Aether crystal," Elena replied. "If the binding circle shatters, the abyss consumes us all."

Marcus turned toward the courtyard. He saw the crimson standard of the Sunfire Legion burning in the dark.
Could they survive until dawn?
""",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_score_to_grade(self) -> None:
        """Verifies grade classification boundaries."""
        self.assertEqual(score_to_grade(97.0), "A+")
        self.assertEqual(score_to_grade(90.0), "A")
        self.assertEqual(score_to_grade(82.0), "B+")
        self.assertEqual(score_to_grade(75.0), "B")
        self.assertEqual(score_to_grade(68.0), "C+")
        self.assertEqual(score_to_grade(58.0), "C")
        self.assertEqual(score_to_grade(48.0), "D")
        self.assertEqual(score_to_grade(30.0), "F")

    def test_evaluate_plot_doctor(self) -> None:
        """Verifies pacing waveform and hook evaluation."""
        text = self.sample_manuscript.read_text(encoding="utf-8")
        score = evaluate_plot_doctor(text)
        self.assertEqual(score.perspective_name, "Plot Doctor")
        self.assertGreater(score.score, 30.0)
        self.assertIn("sentence_std_dev", score.metrics)
        self.assertGreater(len(score.key_findings), 0)

    def test_evaluate_lore_auditor(self) -> None:
        """Verifies named entity recognition and magic/cosmic consistency checking."""
        text = self.sample_manuscript.read_text(encoding="utf-8")
        score = evaluate_lore_auditor(text)
        self.assertEqual(score.perspective_name, "Lore Auditor")
        self.assertGreater(score.score, 40.0)
        self.assertGreater(score.metrics["named_entities_count"], 0)

    def test_evaluate_voice_coach(self) -> None:
        """Verifies dialogue density and dialogue tag evaluation."""
        text = self.sample_manuscript.read_text(encoding="utf-8")
        score = evaluate_voice_coach(text)
        self.assertEqual(score.perspective_name, "Voice Coach")
        self.assertGreater(score.metrics["dialogue_ratio"], 0.0)
        self.assertGreater(score.metrics["utterance_count"], 0)

    def test_evaluate_sensory_stylist(self) -> None:
        """Verifies 8-channel sensory analysis and filter word tracking."""
        text = self.sample_manuscript.read_text(encoding="utf-8")
        score = evaluate_sensory_stylist(text)
        self.assertEqual(score.perspective_name, "Sensory Stylist")
        self.assertGreater(score.metrics["active_channels"], 2)
        self.assertIn("filter_word_count", score.metrics)

    def test_run_editorial_council(self) -> None:
        """Verifies end-to-end multi-agent council orchestration."""
        dossier = run_editorial_council(self.sample_manuscript)
        self.assertEqual(len(dossier.perspectives), 4)
        self.assertGreater(dossier.overall_score, 0.0)
        self.assertIn(dossier.overall_grade, ["A+", "A", "B+", "B", "C+", "C", "D", "F"])
        self.assertGreater(len(dossier.prioritized_action_items), 0)

    def test_render_council_markdown(self) -> None:
        """Generates clean markdown council dossier."""
        dossier = run_editorial_council(self.sample_manuscript)
        md = render_council_markdown(dossier)
        self.assertIn("# 🏛️ Ars Arcanum Editorial Council Dossier", md)
        self.assertIn("Plot Doctor", md)
        self.assertIn("Sensory Stylist", md)

    def test_render_council_html(self) -> None:
        """Generates offline HTML report with strict Content Security Policy."""
        dossier = run_editorial_council(self.sample_manuscript)
        out_html = self.root / "council_dossier.html"
        render_council_html(dossier, out_html)

        self.assertTrue(out_html.is_file())
        content = out_html.read_text(encoding="utf-8")
        self.assertIn("Content-Security-Policy", content)
        self.assertIn("default-src 'none'", content)
        self.assertIn("Editorial Council Dossier", content)

    def test_cli_execution(self) -> None:
        """Verifies CLI execution options (--json, --markdown)."""
        # JSON mode
        with patch("sys.argv", ["council.py", str(self.sample_manuscript), "--json"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                council_main()
                data = json.loads(mock_stdout.getvalue())
                self.assertIn("overall_score", data)
                self.assertEqual(len(data["perspectives"]), 4)

        # Markdown mode
        with patch("sys.argv", ["council.py", str(self.sample_manuscript), "--markdown"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                council_main()
                self.assertIn("Editorial Council Dossier", mock_stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
