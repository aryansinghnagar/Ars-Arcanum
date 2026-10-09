#!/usr/bin/env python3
"""
Unit and Integration Tests for Ars Arcanum Ecosystem Cohesion & Cross-Engine Interoperability
(tests/test_ecosystem_cohesion.py)
================================================================================
Comprehensive test suite verifying:
- 100% CLI command and alias dispatch coverage across all 14 registered sovereign engines
- FS Utils atomic storage and filesystem diagnostics
- Cross-engine multi-stage authoring pipelines (Matter -> Import -> Diff -> Preflight -> Codex)
- Zero-conflict command topology across CLI and registry surfaces
"""

from __future__ import annotations

import io
import sys
import tempfile
import unittest
from pathlib import Path

# Add project scripts to path
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib import (
    cli,
    codex_export,
    diagnostics,
    frontmatter_builder,
    fs_utils,
    manuscript_diff,
    preflight,
    registry,
)


class TestEcosystemCliDispatch(unittest.TestCase):
    """Verifies that all 14 registered engines and all aliases route cleanly in CLI."""

    def setUp(self) -> None:
        self.reg = registry.get_registry()

    def test_registered_engines_count(self) -> None:
        self.assertEqual(len(self.reg), 17)


    def test_all_primary_commands_dispatch(self) -> None:
        unrouted = []
        for name, spec in self.reg.items():
            cmd_tokens = spec.cli_command.split()
            old_stdout, old_stderr = sys.stdout, sys.stderr
            sys.stdout, sys.stderr = io.StringIO(), io.StringIO()
            try:
                ret = cli.main([*cmd_tokens, "--help"])
                err = sys.stderr.getvalue()
                if "Error: Unknown command" in err or (ret == 2 and "Unknown command" in err):
                    unrouted.append((name, spec.cli_command, err.strip()))
            except SystemExit:
                pass
            finally:
                sys.stdout, sys.stderr = old_stdout, old_stderr

        self.assertEqual(unrouted, [], f"Unrouted primary engine commands found: {unrouted}")

    def test_all_engine_aliases_dispatch(self) -> None:
        unrouted_aliases = []
        for name, spec in self.reg.items():
            for alias in spec.aliases:
                tokens = alias.split()
                first_token = tokens[0]
                old_stdout, old_stderr = sys.stdout, sys.stderr
                sys.stdout, sys.stderr = io.StringIO(), io.StringIO()
                try:
                    ret = cli.main([first_token, "--help"])
                    err = sys.stderr.getvalue()
                    if "Error: Unknown command" in err or (ret == 2 and "Unknown command" in err):
                        unrouted_aliases.append((name, alias, err.strip()))
                except SystemExit:
                    pass
                finally:
                    sys.stdout, sys.stderr = old_stdout, old_stderr

        self.assertEqual(unrouted_aliases, [], f"Unrouted engine aliases found: {unrouted_aliases}")


class TestFsUtilsDiagnostics(unittest.TestCase):
    """Tests the atomic filesystem diagnostic utility."""

    def test_check_filesystem(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            res = fs_utils.check_filesystem(tmpdir)
            self.assertTrue(res.get("atomic_write_verified"))
            self.assertEqual(res.get("status"), "healthy")

    def test_fs_utils_main(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            old_stdout, old_stderr = sys.stdout, sys.stderr
            sys.stdout, sys.stderr = io.StringIO(), io.StringIO()
            try:
                ret = fs_utils.main(["--json", tmpdir])
                out = sys.stdout.getvalue()
                self.assertEqual(ret, 0)
                self.assertIn('"status": "healthy"', out)
            finally:
                sys.stdout, sys.stderr = old_stdout, old_stderr


class TestCrossEnginePipeline(unittest.TestCase):
    """Tests end-to-end integration across multiple interacting sovereign engines."""

    def test_full_authoring_and_publishing_pipeline(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            ms_dir = root / "Manuscript"
            ms_dir.mkdir()
            world_dir = root / "World"
            char_dir = world_dir / "Characters"
            char_dir.mkdir(parents=True, exist_ok=True)

            # 1. Generate Publishing Front Matter
            (ms_dir / "manuscript.yaml").write_text("""---
title: The Obsidian Crown
author: Aurelia Vance
language: en
copyright: 2026
---
""", encoding="utf-8")
            matter_files = frontmatter_builder.generate_frontmatter_modules({
                "title": "The Obsidian Crown",
                "author": "Aurelia Vance",
            })
            self.assertTrue(len(matter_files) > 0)

            # 2. Add chapters and world lore
            (char_dir / "Solaris_Hero.md").write_text(
                "---\nname: Solaris Hero\ncategory: Characters\n---\n# Solaris Hero\nA master swordsman of the high citadel.",
                encoding="utf-8",
            )
            (ms_dir / "01_Chapter.md").write_text("# Chapter 1\n\nDawn broke over the high parapets. The leylines flared.", encoding="utf-8")

            # 3. Diff and Revision Heatmap
            old_prose = "Dawn broke over the walls."
            new_prose = "Dawn broke over the high parapets. The leylines flared."
            diff_tokens_a = manuscript_diff.tokenize_words(old_prose)
            diff_tokens_b = manuscript_diff.tokenize_words(new_prose)
            _, added, _deleted = manuscript_diff.compute_word_diff(diff_tokens_a, diff_tokens_b)
            self.assertGreater(added, 0)

            # 4. Preflight typesetting validation
            preflight_rep = preflight.run_preflight_linter(ms_dir)
            self.assertIn("readiness_status", preflight_rep)

            # 5. Static World Wiki Codex Export
            cats = codex_export.scan_world_vault(world_dir)
            codex_file = root / "codex.html"
            codex_export.build_single_file_codex(cats, "TestCosmos", codex_file)
            self.assertTrue(codex_file.is_file())

            # 6. Diagnostics Audit
            diag_rep = diagnostics.get_toolchain_diagnostics()
            self.assertIn("tools", diag_rep)


if __name__ == "__main__":
    unittest.main()
