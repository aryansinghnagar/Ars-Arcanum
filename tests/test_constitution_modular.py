#!/usr/bin/env python3
"""
Tests for Ars Arcanum Modularized Configuration, Constitution, Presets & State
(tests/test_constitution_modular.py)
"""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from lib.config_store import (
    get_config_path,
    load_config,
    save_config,
)
from lib.constitution import (
    deep_merge_constitution,
    get_disabled_engines,
    get_suppressed_rules,
    is_rule_suppressed,
    load_authorial_constitution,
    set_engine_enabled,
)
from lib.docx_presets import (
    get_docx_config,
    get_docx_preset_names,
)
from lib.state import (
    clear_active_manuscript,
    clear_active_universe,
    clear_active_world,
    get_active_manuscript,
    get_active_universe,
    get_active_world,
    get_daily_flow_state,
    set_active_manuscript,
    set_active_universe,
    set_active_world,
    set_daily_flow_state,
)


class TestConstitutionModular(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp(prefix="arcanum_test_cfg_"))
        self.config_dir = self.tmp_dir / ".config" / "arcanum"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.env_patch = patch.dict(
            "os.environ",
            {"ARCANUM_CONFIG_DIR": str(self.config_dir)},
        )
        self.env_patch.start()

    def tearDown(self):
        self.env_patch.stop()
        if self.tmp_dir.exists():
            shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_config_store_load_save(self):
        cfg_path = get_config_path()
        self.assertEqual(cfg_path.parent, self.config_dir.resolve())

        cfg = load_config()
        self.assertIsInstance(cfg, dict)

        cfg["author"] = "J. R. R. Tolkien"
        save_config(cfg)

        cfg2 = load_config()
        self.assertEqual(cfg2["author"], "J. R. R. Tolkien")

    def test_docx_presets(self):
        preset_names = get_docx_preset_names()
        self.assertIn("standard-submission", preset_names)
        self.assertIn("modern-manuscript", preset_names)
        self.assertIn("classic-trade", preset_names)

        cfg = get_docx_config("standard-submission")
        self.assertEqual(cfg["font_family"], "Times New Roman")
        self.assertEqual(cfg["line_spacing"], 2.0)

    def test_state_management(self):
        self.assertEqual(get_active_manuscript(), "")
        set_active_manuscript("/path/to/MyBook")
        self.assertEqual(get_active_manuscript(), "/path/to/MyBook")
        clear_active_manuscript()
        self.assertEqual(get_active_manuscript(), "")

        set_active_world("Eldoria")
        self.assertEqual(get_active_world(), "Eldoria")
        clear_active_world()
        self.assertEqual(get_active_world(), "")

        set_active_universe("CosmosX")
        self.assertEqual(get_active_universe(), "CosmosX")
        clear_active_universe()
        self.assertEqual(get_active_universe(), "")

        # Daily flow state
        flow = get_daily_flow_state()
        self.assertIn("last_cursor_line", flow)
        set_daily_flow_state({"last_cursor_line": 42, "next_time_bridge": "Scene 2"})
        flow2 = get_daily_flow_state()
        self.assertEqual(flow2["last_cursor_line"], 42)
        self.assertEqual(flow2["next_time_bridge"], "Scene 2")

    def test_constitution_deep_merge_and_rule_suppression(self):
        base = {
            "authorial_policy": "advisory",
            "suppressed_rules": ["RULE-001", "PAC-101"],
            "editorial": {"strict": False, "target": 80000},
        }
        override = {
            "suppressed_rules": ["RULE-001", "FAC-202"],
            "editorial": {"target": 95000},
            "new_key": "custom_val",
        }
        merged = deep_merge_constitution(base, override)
        self.assertEqual(merged["authorial_policy"], "advisory")
        self.assertEqual(merged["editorial"]["target"], 95000)
        self.assertEqual(merged["editorial"]["strict"], False)
        self.assertEqual(merged["new_key"], "custom_val")
        # List deduplication
        self.assertIn("RULE-001", merged["suppressed_rules"])
        self.assertIn("PAC-101", merged["suppressed_rules"])
        self.assertIn("FAC-202", merged["suppressed_rules"])
        self.assertEqual(len(merged["suppressed_rules"]), 3)

    def test_constitution_loading_and_policy(self):
        proj_dir = self.tmp_dir / "TestProject"
        proj_dir.mkdir(parents=True, exist_ok=True)
        const_file = proj_dir / "constitution.yaml"
        const_file.write_text(
            "authorial_policy: strict\nsuppressed_rules:\n  - PAC-101\n",
            encoding="utf-8",
        )

        c = load_authorial_constitution(proj_dir)
        self.assertEqual(c.get("authorial_policy"), "strict")
        self.assertTrue(is_rule_suppressed("PAC-101", proj_dir))
        self.assertFalse(is_rule_suppressed("RULE-999", proj_dir))
        self.assertIn("PAC-101", get_suppressed_rules(proj_dir))

    def test_switchboard_engine_toggling(self):
        set_engine_enabled("revision_heatmap", False)
        disabled = get_disabled_engines()
        self.assertIn("revision_heatmap", disabled)

        set_engine_enabled("revision_heatmap", True)
        disabled2 = get_disabled_engines()
        self.assertNotIn("revision_heatmap", disabled2)


if __name__ == "__main__":
    unittest.main()
