#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Diagnostics Engine (scripts/lib/diagnostics.py)
"""

import io
import json
import logging
import os
import tempfile
import unittest
from pathlib import Path
import sys
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.diagnostics import (
    get_state_dir,
    setup_logging,
    redact_sensitive_paths,
    get_toolchain_diagnostics,
    generate_diagnostic_report,
    format_diagnostic_report_markdown,
    run_doctor_report,
    main,
)


class TestDiagnostics(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.work_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_get_state_dir(self):
        state_dir = get_state_dir()
        self.assertTrue(state_dir.is_dir())
        self.assertIn("ars-arcanum", str(state_dir))

    def test_setup_logging(self):
        logger = setup_logging()
        self.assertIsInstance(logger, logging.Logger)
        logger.info("Test diagnostics log entry")

    def test_redact_sensitive_paths(self):
        home_path = str(Path.home())
        sensitive_text = f"Error in file: {home_path}/Documents/SecretNovel.md"
        redacted = redact_sensitive_paths(sensitive_text)
        self.assertNotIn(home_path, redacted)
        self.assertIn("~/Documents/SecretNovel.md", redacted)

    def test_get_toolchain_diagnostics(self):
        tc = get_toolchain_diagnostics()
        self.assertIn("tools", tc)
        self.assertIn("python", tc["tools"])
        self.assertTrue(tc["tools"]["python"]["available"])
        self.assertIn("gui", tc)

    def test_generate_diagnostic_report_with_project(self):
        proj = self.work_dir / "SampleProject"
        proj.mkdir()
        (proj / "Characters").mkdir()
        (proj / "01_Chapters").mkdir()
        (proj / "manuscript.yaml").write_text("title: Test\n", encoding="utf-8")

        # Write dummy log to state dir to test recent_logs branch
        log_file = get_state_dir() / "arcanum.log"
        log_file.write_text("INFO: Test log line\n", encoding="utf-8")

        report = generate_diagnostic_report(project_path=str(proj))
        self.assertIn("version", report)
        self.assertIn("system", report)
        self.assertIn("toolchain", report)
        self.assertIn("project", report)
        self.assertTrue(report["project"]["has_world_bible"])
        self.assertTrue(report["project"]["has_manuscript"])
        self.assertTrue(report["project"]["manifest_found"])
        self.assertIn("recent_logs", report)

        md = format_diagnostic_report_markdown(report)
        self.assertIn("Ars Arcanum Diagnostic Triage Report", md)
        self.assertIn("Toolchain & Dependencies", md)
        self.assertIn("Target Project Inspection", md)
        self.assertIn("Recent Log Output", md)

    def test_run_doctor_report_world_filter(self):
        w_dir = self.work_dir / "DoctorWorld"
        w_dir.mkdir()
        (w_dir / "world.yaml").write_text('schema_version: "1.0"\nname: "DoctorWorld"\n', encoding="utf-8")
        (w_dir / "00-World-Bible").mkdir()

        rc = run_doctor_report(world_filter=str(w_dir), as_json=False)
        self.assertIn(rc, (0, 1))

        rc_json = run_doctor_report(world_filter=str(w_dir), as_json=True)
        self.assertIn(rc_json, (0, 1))

    def test_run_doctor_report_all_worlds(self):
        u_base = self.work_dir / "Universes"
        u_base.mkdir()
        u1 = u_base / "CosmosA"
        u1.mkdir()
        w1 = u1 / "WorldOne"
        w1.mkdir()
        (w1 / "world.yaml").write_text('schema_version: "1.0"\nname: "WorldOne"\n', encoding="utf-8")

        with patch.dict(os.environ, {"UNIVERSES_BASE": str(u_base)}):
            rc = run_doctor_report(all_worlds=True, as_json=False)
            self.assertIn(rc, (0, 1))

    def test_cli_main_report_and_doctor(self):
        # CLI --report
        with patch.object(sys, "argv", ["diagnostics.py", "--report"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                rc = main()
                self.assertEqual(rc, 0)
                self.assertIn("Ars Arcanum Diagnostic Triage Report", mock_stdout.getvalue())

        # CLI --json
        with patch.object(sys, "argv", ["diagnostics.py", "--json"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                rc = main()
                self.assertIn(rc, (0, 1))
                data = json.loads(mock_stdout.getvalue())
                self.assertIn("system", data)

        # CLI --all-worlds
        with patch.object(sys, "argv", ["diagnostics.py", "--all-worlds"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                rc = main()
                self.assertIn(rc, (0, 1))


if __name__ == "__main__":
    unittest.main()
