#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Configuration Engine (scripts/lib/config.py).
Validates:
- Config path resolution (standard XDG and legacy fallback).
- Config load/save safety and error handling.
- Backup destination management.
- DOCX presets and custom override configuration.
- Dynamic tips toggle and persistence.
- Full CLI command dispatch and error branches.
"""

import io
import json
import os
import tempfile
import unittest
from pathlib import Path
import sys
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.config import (
    get_config_dir,
    get_config_file_path,
    load_config,
    save_config,
    get_backup_dest,
    set_backup_dest,
    clear_backup_dest,
    get_active_docx_preset_name,
    get_docx_config,
    set_docx_preset,
    set_docx_option,
    list_docx_presets,
    get_tips_enabled,
    set_tips_enabled,
    toggle_tips,
    main,
)


class TestConfig(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.work_dir = Path(self.temp_dir.name)
        # Mock XDG_CONFIG_HOME
        self.env_patch = patch.dict(os.environ, {"XDG_CONFIG_HOME": str(self.work_dir)})
        self.env_patch.start()

    def tearDown(self):
        self.env_patch.stop()
        self.temp_dir.cleanup()

    def test_config_paths_and_legacy_fallback(self):
        cfg_dir = get_config_dir()
        self.assertEqual(cfg_dir, self.work_dir / "ars-arcanum")

        cfg_file = get_config_file_path()
        self.assertEqual(cfg_file, self.work_dir / "ars-arcanum" / "config.json")

        # Legacy fallback when legacy exists and modern does not
        legacy_dir = self.work_dir / "arcanum"
        legacy_dir.mkdir(parents=True, exist_ok=True)
        legacy_file = legacy_dir / "config.json"
        legacy_file.write_text('{"legacy": true}', encoding="utf-8")

        self.assertEqual(get_config_file_path(), legacy_file)

    def test_load_save_config(self):
        # Initial empty
        self.assertEqual(load_config(), {})

        data = {"author": "Valen", "active": True, "count": 10}
        self.assertTrue(save_config(data))

        loaded = load_config()
        self.assertEqual(loaded, data)

        # Corrupt file handling
        cfg_file = get_config_file_path()
        cfg_file.write_text("INVALID_JSON", encoding="utf-8")
        self.assertEqual(load_config(), {})

    def test_backup_dest_operations(self):
        self.assertEqual(get_backup_dest(), "")

        dest_path = str(self.work_dir / "backups")
        self.assertTrue(set_backup_dest(dest_path))
        self.assertEqual(get_backup_dest(), str(Path(dest_path).resolve()))

        self.assertTrue(clear_backup_dest())
        self.assertEqual(get_backup_dest(), "")

    def test_docx_presets_and_options(self):
        presets = list_docx_presets()
        self.assertIn("standard-submission", presets)
        self.assertIn("modern-manuscript", presets)

        self.assertEqual(get_active_docx_preset_name(), "standard-submission")
        cfg = get_docx_config()
        self.assertEqual(cfg["font_family"], "Times New Roman")

        # Change preset
        self.assertTrue(set_docx_preset("modern-manuscript"))
        self.assertEqual(get_active_docx_preset_name(), "modern-manuscript")
        cfg_modern = get_docx_config()
        self.assertEqual(cfg_modern["font_family"], "Georgia")

        # Invalid preset
        self.assertFalse(set_docx_preset("non-existent-preset"))

        # Custom option override
        self.assertTrue(set_docx_option("font_size_pt", 14.0))
        self.assertEqual(get_active_docx_preset_name(), "custom")
        cfg_custom = get_docx_config()
        self.assertEqual(cfg_custom["font_size_pt"], 14.0)

    def test_tips_toggle(self):
        self.assertTrue(get_tips_enabled())
        self.assertFalse(toggle_tips())
        self.assertFalse(get_tips_enabled())
        self.assertTrue(toggle_tips())
        self.assertTrue(get_tips_enabled())
        set_tips_enabled(False)
        self.assertFalse(get_tips_enabled())

    def test_cli_backup_dest(self):
        # Set
        target = str(self.work_dir / "safe_backups")
        with patch.object(sys, "argv", ["config.py", "backup-dest", "set", target]):
            with patch("sys.stdout", new_callable=io.StringIO):
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 0)

        # Get
        with patch.object(sys, "argv", ["config.py", "backup-dest", "get"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 0)
                self.assertIn("safe_backups", mock_stdout.getvalue())

        # Clear
        with patch.object(sys, "argv", ["config.py", "backup-dest", "clear"]):
            with patch("sys.stdout", new_callable=io.StringIO):
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 0)

    def test_cli_docx_commands(self):
        # Presets list
        with patch.object(sys, "argv", ["config.py", "docx-presets"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 0)
                self.assertIn("standard-submission", mock_stdout.getvalue())

        # Set preset
        with patch.object(sys, "argv", ["config.py", "docx-preset", "classic-trade"]):
            with patch("sys.stdout", new_callable=io.StringIO):
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 0)

        # Get active preset
        with patch.object(sys, "argv", ["config.py", "docx-preset"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 0)
                self.assertEqual(mock_stdout.getvalue().strip(), "classic-trade")

        # Set option
        with patch.object(sys, "argv", ["config.py", "docx-config", "line_spacing", "1.75"]):
            with patch("sys.stdout", new_callable=io.StringIO):
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 0)

        # Get option
        with patch.object(sys, "argv", ["config.py", "docx-config", "line_spacing"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 0)
                self.assertEqual(mock_stdout.getvalue().strip(), "1.75")

        # Dump full config
        with patch.object(sys, "argv", ["config.py", "docx-config"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 0)
                data = json.loads(mock_stdout.getvalue())
                self.assertEqual(data["line_spacing"], 1.75)

    def test_cli_tips_commands(self):
        for cmd_action in [["enable"], ["disable"], ["toggle"], ["get"], ["set", "true"], ["set", "false"]]:
            with patch.object(sys, "argv", ["config.py", "tips", *cmd_action]):
                with patch("sys.stdout", new_callable=io.StringIO):
                    rc = main()
                    self.assertEqual(rc, 0)

    def test_active_targets_get_set(self):
        from lib.config import (
            get_active_manuscript_name, set_active_manuscript, clear_active_manuscript,
            get_active_world_name, set_active_world, clear_active_world,
            get_active_universe_name, set_active_universe, clear_active_universe,
            get_default_scope, set_default_scope,
        )
        self.assertEqual(get_active_manuscript_name(), "")
        set_active_manuscript("NovelA")
        self.assertEqual(get_active_manuscript_name(), "NovelA")
        clear_active_manuscript()
        self.assertEqual(get_active_manuscript_name(), "")

        set_active_world("WorldB")
        self.assertEqual(get_active_world_name(), "WorldB")
        clear_active_world()
        self.assertEqual(get_active_world_name(), "")

        set_active_universe("UnivC")
        self.assertEqual(get_active_universe_name(), "UnivC")
        clear_active_universe()
        self.assertEqual(get_active_universe_name(), "")

        self.assertEqual(get_default_scope(), {})
        set_default_scope({"chapters": [1, 2]})
        self.assertEqual(get_default_scope(), {"chapters": [1, 2]})

    def test_authorial_constitution(self):
        from lib.config import (
            get_authorial_constitution,
            is_rule_suppressed,
            get_authorial_policy,
        )
        # Empty dir defaults
        const = get_authorial_constitution(self.work_dir)
        self.assertIn("canon", const)

        # Suppressed rule
        self.assertFalse(is_rule_suppressed("RULE-001", const))
        self.assertFalse(is_rule_suppressed("RULE-001"))

        # Authorial policy
        pol = get_authorial_policy()
        self.assertEqual(pol.get("default_mode"), "observational")



if __name__ == "__main__":
    unittest.main()

