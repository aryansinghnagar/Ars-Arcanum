#!/usr/bin/env python3
"""
Unit Tests for Ars Arcanum Unified Python CLI Dispatcher (tests/test_cli_dispatch.py)
===================================================================================
Validates command routing, alias dispatch, plugin listing, and error handling.
"""

from io import StringIO
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.cli import (
    VERSION,
    dispatch_script,
    dispatch_subcommand,
    handle_engines_command,
    main,
)


class TestCliDispatch(unittest.TestCase):
    """Unit tests for lib.cli command routing."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.work_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_version_flag(self):
        with patch("sys.stdout", new_callable=StringIO) as mock_out:
            rc = main(["--version"])
            self.assertEqual(rc, 0)
            self.assertIn(f"Ars Arcanum v{VERSION}", mock_out.getvalue())

    def test_help_flag(self):
        with patch("sys.stdout", new_callable=StringIO) as mock_out:
            rc = main(["--help"])
            self.assertEqual(rc, 0)
            self.assertIn("Ars Arcanum Unified CLI", mock_out.getvalue())
            self.assertIn("Core Authoring & Editorial Craft:", mock_out.getvalue())

    def test_empty_argv_shows_banner(self):
        with patch("sys.stdout", new_callable=StringIO) as mock_out:
            rc = main([])
            self.assertEqual(rc, 0)
            self.assertIn("Ars Arcanum Unified CLI", mock_out.getvalue())

    def test_engines_list_command(self):
        with patch("sys.stdout", new_callable=StringIO) as mock_out:
            rc = main(["engines"])
            self.assertEqual(rc, 0)
            output = mock_out.getvalue()
            self.assertIn("Ars Arcanum Registered Plugins & Engines", output)
            self.assertIn("astrophysics", output)
            self.assertIn("cartography", output)

    def test_engines_filtered_flags(self):
        with patch("sys.stdout", new_callable=StringIO) as mock_out:
            rc_core = handle_engines_command(["--core"])
            self.assertEqual(rc_core, 0)
            self.assertIn("[CORE]", mock_out.getvalue())

        with patch("sys.stdout", new_callable=StringIO) as mock_out:
            rc_craft = handle_engines_command(["--craft"])
            self.assertEqual(rc_craft, 0)
            self.assertIn("[CRAFT]", mock_out.getvalue())

    def test_calc_subcommands_route_help(self):
        calc_targets = [
            "transit", "time-dilation", "orbit", "comms",
            "journey", "battle", "climate", "trade", "logistics"
        ]
        for sub in calc_targets:
            with patch("sys.stdout", new_callable=StringIO):
                rc = main(["calc", sub, "--help"])
                self.assertIn(rc, (0, None))

    def test_calc_without_subcommand_shows_usage(self):
        with patch("sys.stderr", new_callable=StringIO) as mock_err:
            rc = main(["calc"])
            self.assertEqual(rc, 2)
            self.assertIn("Usage: arcanum calc", mock_err.getvalue())

    def test_calc_unknown_subcommand(self):
        with patch("sys.stderr", new_callable=StringIO) as mock_err:
            rc = main(["calc", "unknown_calc_mode"])
            self.assertEqual(rc, 2)
            self.assertIn("Unknown calc mode", mock_err.getvalue())

    def test_audit_subcommands_route_help(self):
        audit_targets = [
            "voice", "style", "dialogue", "echoes",
            "scenes", "structure", "idioms", "senses", "tech"
        ]
        for sub in audit_targets:
            with patch("sys.stdout", new_callable=StringIO):
                rc = main(["audit", sub, "--help"])
                self.assertIn(rc, (0, None))

    def test_audit_without_args_routes_doctor_script(self):
        with patch("lib.cli.dispatch_script", return_value=0) as mock_ds:
            rc = main(["audit"])
            self.assertEqual(rc, 0)
            mock_ds.assert_called_once()

    def test_speculative_craft_subcommands_route_help(self):
        subcmds = [
            ["magic-check", "--help"],
            ["magic-report", "--help"],
            ["genealogy", "--help"],
            ["lineage", "--help"],
            ["conlang", "--help"],
            ["family-tree", "--help"],
            ["calendar", "--help"],
            ["concordance", "--help"],
            ["series", "--help"],
            ["causality", "--help"],
            ["economy", "--help"],
            ["ecology", "--help"],
            ["faction", "--help"],
            ["plot", "--help"],
            ["structure", "--help"],
            ["ambient", "--help"],
            ["portfolio", "--help"],
            ["matter", "--help"],
            ["polish", "typography", "--help"],
            ["preflight", "--help"],
            ["docx", "--help"],
            ["pace", "--help"],
            ["tension", "--help"],
            ["sim", "--help"],
            ["mesh", "--help"],
            ["cascade", "--help"],
            ["spark", "--help"],
            ["bridge", "--help"],
        ]
        for sub in subcmds:
            with patch("sys.stdout", new_callable=StringIO):
                rc = main(sub)
                self.assertIn(rc, (0, None))

    def test_doc_and_guide_commands(self):
        with patch("sys.stdout", new_callable=StringIO) as mock_out:
            rc = main(["doc"])
            self.assertEqual(rc, 0)
            self.assertIn("Author Craft Guide & Advisory Matrix", mock_out.getvalue())

        with patch("sys.stdout", new_callable=StringIO) as mock_out:
            rc = main(["doc", "astrophysics"])
            self.assertEqual(rc, 0)
            val = mock_out.getvalue()
            self.assertIn("ASTROPHYSICS & ORBITAL MECHANICS", val)
            self.assertIn("Engine Logic & Scientific / Structural Foundations:", val)
            self.assertIn("Advisory Mechanics & Creative Freedom Resolution Pathways:", val)

        # Multi-word command doc lookup
        with patch("sys.stdout", new_callable=StringIO) as mock_out:
            rc = main(["doc", "calc", "astro"])
            self.assertEqual(rc, 0)
            self.assertIn("ASTROPHYSICS & ORBITAL MECHANICS", mock_out.getvalue())

        # Hyphenated engine name lookup
        with patch("sys.stdout", new_callable=StringIO) as mock_out:
            rc = main(["doc", "magic-system"])
            self.assertEqual(rc, 0)
            self.assertIn("MAGIC SYSTEM CONSTRAINTS", mock_out.getvalue())

        # Modes: math, why, examples, subfeatures, advisory, json
        for mode_flag in ["--math", "--why", "--examples", "--subfeatures", "--advisory", "--json"]:
            with patch("sys.stdout", new_callable=StringIO) as mock_out:
                rc = main(["doc", "climate", mode_flag])
                self.assertEqual(rc, 0)

        # Doc search query
        with patch("sys.stdout", new_callable=StringIO) as mock_out:
            rc = main(["doc", "--search", "orbital"])
            self.assertEqual(rc, 0)
            self.assertIn("Search results", mock_out.getvalue())

        # Doc search query with --json
        with patch("sys.stdout", new_callable=StringIO) as mock_out:
            rc = main(["doc", "--search", "orbital", "--json"])
            self.assertEqual(rc, 0)

        with patch("sys.stdout", new_callable=StringIO) as mock_out:
            rc = main(["guide", "climate"])
            self.assertEqual(rc, 0)
            self.assertIn("PLANETARY CLIMATE & KÖPPEN BIOMES", mock_out.getvalue())

        with patch("sys.stdout", new_callable=StringIO) as mock_out:
            rc = main(["explain", "magic_system"])
            self.assertEqual(rc, 0)
            self.assertIn("MAGIC SYSTEM CONSTRAINTS", mock_out.getvalue())

    def test_doc_unknown_engine(self):
        with patch("sys.stderr", new_callable=StringIO) as mock_err:
            rc = main(["doc", "totally_fake_engine"])
            self.assertEqual(rc, 1)
            self.assertIn("No documentation found for engine: 'totally_fake_engine'", mock_err.getvalue())

    def test_unknown_command_suggests_close_match(self):
        with patch("sys.stderr", new_callable=StringIO) as mock_err:
            rc = main(["prefligt"])
            self.assertEqual(rc, 2)
            self.assertIn("Did you mean 'preflight'?", mock_err.getvalue())

    def test_unknown_command_generic_error(self):
        with patch("sys.stderr", new_callable=StringIO) as mock_err:
            rc = main(["xyzabc123nonexistent"])
            self.assertEqual(rc, 2)
            self.assertIn("Error: Unknown command 'xyzabc123nonexistent'", mock_err.getvalue())

    def test_handle_new_dispatches(self):
        with patch("sys.stderr", new_callable=StringIO) as mock_err:
            rc_empty = main(["new"])
            self.assertEqual(rc_empty, 2)
            self.assertIn("Usage: arcanum new", mock_err.getvalue())

        with patch("lib.cli.dispatch_script", return_value=0) as mock_ds:
            rc = main(["new", "manuscript", "TestBook"])
            self.assertEqual(rc, 0)
            mock_ds.assert_called_once()

        with patch("sys.stderr", new_callable=StringIO) as mock_err:
            rc_unk = main(["new", "invalid_type", "TestBook"])
            self.assertEqual(rc_unk, 2)
            self.assertIn("Unknown project type", mock_err.getvalue())

    def test_handle_doctor_with_directory(self):
        test_dir = self.work_dir / "world_lore"
        test_dir.mkdir()
        with patch("lib.cli.dispatch_subcommand", return_value=0) as mock_sub:
            rc = main(["doctor", str(test_dir)])
            self.assertEqual(rc, 0)
            mock_sub.assert_called_once_with("lib.world_doctor", [str(test_dir)])

    def test_dispatch_subcommand_errors(self):
        with patch("sys.stderr", new_callable=StringIO) as mock_err:
            rc_missing = dispatch_subcommand("nonexistent.module", [])
            self.assertEqual(rc_missing, 1)
            self.assertIn("Error executing 'nonexistent.module'", mock_err.getvalue())

    def test_dispatch_script_not_found(self):
        with patch("sys.stderr", new_callable=StringIO) as mock_err:
            rc_missing = dispatch_script("nonexistent_script.sh", [])
            self.assertEqual(rc_missing, 1)
            self.assertIn("Error: Script 'nonexistent_script.sh' not found.", mock_err.getvalue())


if __name__ == "__main__":
    unittest.main()
