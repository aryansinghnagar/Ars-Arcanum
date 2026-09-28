#!/usr/bin/env python3
"""
Unit tests for the Project Migration Engine (scripts/lib/migrate.py).
Validates:
- Upgrades unversioned universes, worlds, and manuscripts to schema_version 1.0.
- Migrates legacy 05-Backups/ and 04-Publishing/ folders cleanly.
- Preserves existing lore and prose without data loss.
- Updates .gitignore with lock and cache entries.
- Traverses multi-project workspaces and nested universe world structures.
- CLI argument parsing and JSON output.
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

from lib.migrate import (
    ensure_gitignore_entries,
    migrate_universe,
    migrate_world,
    migrate_project,
    main,
    CURRENT_SCHEMA_VERSION,
)


class TestMigrateEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.work_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_ensure_gitignore_entries_no_file(self):
        actions = ensure_gitignore_entries(self.work_dir)
        self.assertEqual(actions, [])

    def test_ensure_gitignore_entries_adds_missing(self):
        gi = self.work_dir / ".gitignore"
        gi.write_text("*.tmp\n", encoding="utf-8")
        actions = ensure_gitignore_entries(self.work_dir)
        self.assertTrue(len(actions) > 0)
        content = gi.read_text(encoding="utf-8")
        self.assertIn(".arcanum_cache.json", content)
        self.assertIn(".sync_state.json", content)
        self.assertIn("*.lock", content)

        # Second call does nothing
        actions_second = ensure_gitignore_entries(self.work_dir)
        self.assertEqual(actions_second, [])

    def test_migrate_universe_new_and_existing(self):
        u_dir = self.work_dir / "CosmicUniverse"
        u_dir.mkdir()
        (u_dir / ".gitignore").write_text("*.bak\n", encoding="utf-8")

        # Case 1: Universe without universe.yaml
        actions = migrate_universe(u_dir)
        self.assertTrue(any("Created universe.yaml" in a for a in actions))
        u_yaml = (u_dir / "universe.yaml").read_text(encoding="utf-8")
        self.assertIn(f'schema_version: "{CURRENT_SCHEMA_VERSION}"', u_yaml)

        # Case 2: Universe with universe.yaml missing schema_version
        (u_dir / "universe.yaml").write_text('name: "CosmicUniverse"\n', encoding="utf-8")
        actions2 = migrate_universe(u_dir)
        self.assertTrue(any("Added schema_version" in a for a in actions2))

        # Case 3: Universe with universe.yaml already having schema_version
        actions3 = migrate_universe(u_dir)
        self.assertEqual(actions3, [])

    def test_migrate_legacy_world(self):
        world_dir = self.work_dir / "LegacyWorld"
        world_dir.mkdir()
        (world_dir / "Characters").mkdir()
        (world_dir / "05-Backups").mkdir()
        (world_dir / "scriptorium.yaml").write_text("name: LegacyWorld\nauthor: OldScribe\n", encoding="utf-8")

        res = migrate_project(world_dir)
        self.assertEqual(res["type"], "world")
        self.assertTrue((world_dir / "world.yaml").is_file())
        self.assertTrue((world_dir / "Backups").is_dir())
        self.assertFalse((world_dir / "05-Backups").exists())

        world_yaml = (world_dir / "world.yaml").read_text(encoding="utf-8")
        self.assertIn(f'schema_version: "{CURRENT_SCHEMA_VERSION}"', world_yaml)
        self.assertIn("OldScribe", world_yaml)

    def test_migrate_world_empty_or_existing_manifest(self):
        w_dir = self.work_dir / "CleanWorld"
        w_dir.mkdir()
        (w_dir / "Characters").mkdir()

        # World without world.yaml
        actions = migrate_world(w_dir)
        self.assertTrue(any("Created world.yaml" in a for a in actions))
        self.assertTrue((w_dir / "world.yaml").is_file())

        # World with world.yaml missing schema_version
        (w_dir / "world.yaml").write_text("name: CleanWorld\n", encoding="utf-8")
        actions2 = migrate_world(w_dir)
        self.assertTrue(any("Added schema_version" in a for a in actions2))

    def test_migrate_manuscript(self):
        ms_dir = self.work_dir / "LegacyManuscript"
        ms_dir.mkdir()
        (ms_dir / "Book-01").mkdir()
        (ms_dir / "04-Publishing").mkdir()
        (ms_dir / "05-Backups").mkdir()
        (ms_dir / "manuscript.yaml").write_text("title: Epic Novel\nauthor: Writer\n", encoding="utf-8")

        res = migrate_project(ms_dir)
        self.assertEqual(res["type"], "manuscript")
        self.assertTrue((ms_dir / "Exports").is_dir())
        self.assertFalse((ms_dir / "04-Publishing").exists())
        self.assertTrue((ms_dir / "Backups").is_dir())
        self.assertFalse((ms_dir / "05-Backups").exists())

        ms_yaml = (ms_dir / "manuscript.yaml").read_text(encoding="utf-8")
        self.assertIn(f'schema_version: "{CURRENT_SCHEMA_VERSION}"', ms_yaml)

    def test_migrate_manuscript_without_manifest(self):
        ms_dir = self.work_dir / "NewNovel"
        ms_dir.mkdir()
        (ms_dir / "nwProject.nwx").write_text("<project/>", encoding="utf-8")

        res = migrate_project(ms_dir)
        self.assertEqual(res["type"], "manuscript")
        self.assertTrue((ms_dir / "manuscript.yaml").is_file())

    def test_migrate_universe_with_child_worlds(self):
        u_dir = self.work_dir / "MyUniverse"
        u_dir.mkdir()
        (u_dir / "Universe-Index.md").write_text("# Universe Index", encoding="utf-8")

        w_child = u_dir / "PlanetA"
        w_child.mkdir()
        (w_child / "Characters").mkdir()

        res = migrate_project(u_dir)
        self.assertEqual(res["type"], "universe")
        self.assertTrue((u_dir / "universe.yaml").is_file())
        self.assertTrue((w_child / "world.yaml").is_file())

    def test_migrate_container_directory(self):
        container = self.work_dir / "Workspace"
        container.mkdir()

        sub_world = container / "WorldAlpha"
        sub_world.mkdir()
        (sub_world / "Characters").mkdir()

        res = migrate_project(container)
        self.assertEqual(res["type"], "unknown")
        self.assertTrue(any("WorldAlpha" in a for a in res["actions"]))

    def test_migrate_invalid_directory(self):
        not_a_dir = self.work_dir / "non_existent"
        with self.assertRaises(ValueError):
            migrate_project(not_a_dir)

    def test_cli_main_stdout_and_json(self):
        ms_dir = self.work_dir / "CLIManuscript"
        ms_dir.mkdir()
        (ms_dir / "manuscript.yaml").write_text("title: Test\n", encoding="utf-8")

        # Test human-readable CLI
        with patch.object(sys, "argv", ["migrate.py", str(ms_dir)]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                main()
                out = mock_stdout.getvalue()
                self.assertIn("Ars Arcanum Migration Engine", out)
                self.assertIn("Target:", out)

        # Test JSON CLI output
        with patch.object(sys, "argv", ["migrate.py", str(ms_dir), "--json"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                main()
                out = mock_stdout.getvalue()
                data = json.loads(out)
                self.assertEqual(data["type"], "manuscript")


if __name__ == "__main__":
    unittest.main()
