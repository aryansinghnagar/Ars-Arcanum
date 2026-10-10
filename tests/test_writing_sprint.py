#!/usr/bin/env python3
"""
Tests for Ars Arcanum Writing Sprint & Cognitive Velocity Engine (tests/test_writing_sprint.py)
"""

from __future__ import annotations

import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.project_scaffold import scaffold_manuscript, scaffold_universe, scaffold_world
from lib.writing_sprint import (
    cancel_sprint,
    format_stats_markdown,
    format_stats_table,
    get_velocity_metrics,
    log_manual_sprint,
    main,
    start_sprint,
    status_sprint,
    stop_sprint,
)


class TestWritingSprint(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp(prefix="arcanum_test_sprint_"))
        self.univ_base = self.tmp_dir / "Universes"
        self.univ_base.mkdir(parents=True, exist_ok=True)

        scaffold_universe("Chronicles", base_dir=self.univ_base)
        scaffold_world("Eldoria", universe_name="Chronicles", base_dir=self.univ_base)
        res = scaffold_manuscript(
            "Starfall",
            universe="Chronicles",
            world="Eldoria",
            base_dir=self.univ_base,
            target_words=60000,
        )
        self.ms_dir = Path(res["path"])

    def tearDown(self):
        if self.tmp_dir.exists():
            shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_sprint_lifecycle(self):
        # 1. Start sprint
        res_start = start_sprint(
            self.ms_dir,
            target_words=500,
            minutes=25,
            interactive=False,
        )
        self.assertEqual(res_start["status"], "started")
        self.assertEqual(res_start["target_words"], 500)
        self.assertEqual(res_start["duration_minutes"], 25)

        # 2. Starting again without force raises RuntimeError
        with self.assertRaises(RuntimeError):
            start_sprint(self.ms_dir, target_words=750, minutes=30, interactive=False)

        # Force start overwrites
        res_force = start_sprint(
            self.ms_dir,
            target_words=750,
            minutes=30,
            interactive=False,
            force=True,
        )
        self.assertEqual(res_force["status"], "started")
        self.assertEqual(res_force["target_words"], 750)

        # 3. Status
        res_status = status_sprint(self.ms_dir)
        self.assertEqual(res_status["status"], "active")
        self.assertEqual(res_status["target_words"], 750)

        # 4. Stop sprint with manual words
        res_stop = stop_sprint(self.ms_dir, manual_words=600)
        self.assertEqual(res_stop["status"], "completed")
        self.assertEqual(res_stop["words_written"], 600)
        self.assertGreater(res_stop["wpm"], 0.0)
        self.assertEqual(res_stop["completion_percentage"], 80.0)

        # 5. Status after stop is inactive
        res_inactive = status_sprint(self.ms_dir)
        self.assertEqual(res_inactive["status"], "inactive")

        # 6. Stopping when inactive raises RuntimeError
        with self.assertRaises(RuntimeError):
            stop_sprint(self.ms_dir)

    def test_cancel_sprint(self):
        start_sprint(self.ms_dir, target_words=400, minutes=20, interactive=False)
        self.assertEqual(status_sprint(self.ms_dir)["status"], "active")

        res_cancel = cancel_sprint(self.ms_dir)
        self.assertEqual(res_cancel["status"], "cancelled")
        self.assertEqual(status_sprint(self.ms_dir)["status"], "inactive")

        # Second cancel when inactive
        res_cancel2 = cancel_sprint(self.ms_dir)
        self.assertEqual(res_cancel2["status"], "inactive")

    def test_log_manual_sprint_and_metrics(self):
        res_log = log_manual_sprint(
            self.ms_dir,
            words=750,
            minutes=25.0,
            target_words=500,
            chapter="Chapter_01.md",
        )
        self.assertEqual(res_log["status"], "logged")
        self.assertEqual(res_log["record"]["words_written"], 750)
        self.assertEqual(res_log["record"]["wpm"], 30.0)

        # Add Obsidian style Daily-Writing-Log note
        dwl_file = self.ms_dir / "Daily-Writing-Log-Test.md"
        dwl_file.write_text(
            "---\nfileClass: WritingLog\ntype: daily_writing_log\ndate: '2026-10-09'\n"
            "words_written: 1000\nwriting_time_minutes: 40\nwpm_velocity: 25.0\ngoal: 1000\n---\n# Notes",
            encoding="utf-8",
        )

        metrics = get_velocity_metrics(self.ms_dir)
        self.assertEqual(metrics["total_sprint_sessions"], 2)
        self.assertEqual(metrics["total_sprint_words"], 1750)
        self.assertGreater(metrics["overall_average_wpm"], 0.0)
        self.assertIn("Morning (6-12)", metrics["time_of_day_distribution"])

    def test_format_stats_table_and_markdown(self):
        log_manual_sprint(self.ms_dir, words=500, minutes=20.0)
        metrics = get_velocity_metrics(self.ms_dir)

        tbl = format_stats_table(metrics, title="Starfall")
        self.assertIn("Starfall — Drafting Velocity & Sprint Telemetry", tbl)
        self.assertIn("Total Sprints:", tbl)

        md = format_stats_markdown(metrics, title="Starfall")
        self.assertIn("# Starfall — Drafting Velocity & Sprint Telemetry", md)
        self.assertIn("Recent Sprint Sessions", md)

    def test_cli_sprint(self):
        # CLI start
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            rc = main(["start", str(self.ms_dir), "--target", "300", "--minutes", "15", "--no-interactive", "--json"])
            self.assertEqual(rc, 0)
            parsed = json.loads(mock_out.getvalue())
            self.assertEqual(parsed["status"], "started")

        # CLI status
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            rc = main(["status", str(self.ms_dir), "--json"])
            self.assertEqual(rc, 0)
            parsed = json.loads(mock_out.getvalue())
            self.assertEqual(parsed["status"], "active")

        # CLI stop
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            rc = main(["stop", str(self.ms_dir), "--words", "350", "--json"])
            self.assertEqual(rc, 0)
            parsed = json.loads(mock_out.getvalue())
            self.assertEqual(parsed["status"], "completed")
            self.assertEqual(parsed["words_written"], 350)

        # CLI log
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            rc = main(["log", str(self.ms_dir), "--words", "800", "--minutes", "30", "--json"])
            self.assertEqual(rc, 0)
            parsed = json.loads(mock_out.getvalue())
            self.assertEqual(parsed["status"], "logged")

        # CLI stats with --html and --open
        stats_html = self.tmp_dir / "stats_hub.html"
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            with patch("webbrowser.open") as mock_open:
                rc = main(["stats", str(self.ms_dir), "--html", str(stats_html), "--open"])
                self.assertEqual(rc, 0)
                self.assertTrue(stats_html.is_file())
                mock_open.assert_called_once()

        # CLI report --html with --open
        html_file = self.tmp_dir / "sprint_hub.html"
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            with patch("webbrowser.open") as mock_open:
                rc = main(["report", str(self.ms_dir), "--html", str(html_file), "--open"])
                self.assertEqual(rc, 0)
                self.assertTrue(html_file.is_file())
                content = html_file.read_text(encoding="utf-8")
                self.assertIn("Starfall", content)
                self.assertIn("Content-Security-Policy", content)
                mock_open.assert_called_once()

        # CLI cancel
        start_sprint(self.ms_dir, target_words=200, minutes=10, interactive=False)
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            rc = main(["cancel", str(self.ms_dir), "--json"])
            self.assertEqual(rc, 0)
            parsed = json.loads(mock_out.getvalue())
            self.assertEqual(parsed["status"], "cancelled")


if __name__ == "__main__":
    unittest.main()
