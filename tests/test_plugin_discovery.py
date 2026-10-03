#!/usr/bin/env python3
"""
Unit and Integration Tests for Ars Arcanum Dynamic User Plugin Discovery & Typst Presets
(tests/test_plugin_discovery.py)
================================================================================
"""

import tempfile
import unittest
from pathlib import Path

from scripts.lib.registry import (
    BaseCraftEngine,
    EngineCategory,
    EngineSpec,
    discover_craft_plugins,
    discover_user_plugins,
    load_user_plugin,
    register_user_engine,
)


class SampleCustomEngine(BaseCraftEngine):
    name = "chronomancy"
    title = "Chronomancy & Temporal Weaving"
    description = "Time loops, paradox metrics, and retrocausal divination"
    cli_command = "craft chronomancy"
    aliases = ["time-magic", "temporal"]
    studio_tab = "Magic"

    def execute(self, argv: list[str]) -> int:
        return 0


class TestPluginDiscovery(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_base_craft_engine_subclass(self) -> None:
        """Verifies BaseCraftEngine subclassing and spec extraction."""
        engine = SampleCustomEngine()
        spec = engine.get_spec()
        self.assertEqual(spec.name, "chronomancy")
        self.assertEqual(spec.title, "Chronomancy & Temporal Weaving")
        self.assertEqual(spec.category, EngineCategory.CRAFT)
        self.assertIn("time-magic", spec.aliases)
        self.assertEqual(spec.studio_tab, "Magic")
        self.assertEqual(engine.execute([]), 0)

    def test_register_user_engine(self) -> None:
        """Verifies dynamic registration of user engine spec."""
        spec = EngineSpec(
            name="pyromancy_test",
            category=EngineCategory.CRAFT,
            title="Pyromancy Testing Engine",
            description="Thermal energy calculations",
            module_name="test.pyromancy",
            cli_command="craft pyro",
        )
        register_user_engine(spec)
        from scripts.lib.registry import get_engine
        retrieved = get_engine("pyromancy_test")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.title, "Pyromancy Testing Engine")  # type: ignore

    def test_load_user_plugin_from_file_class(self) -> None:
        """Verifies loading a dynamic plugin file subclassing BaseCraftEngine."""
        plugin_file = self.root / "alchemical_synthesis.py"
        plugin_code = '''
from scripts.lib.registry import BaseCraftEngine, EngineCategory

class AlchemyPlugin(BaseCraftEngine):
    name = "alchemy_synth"
    title = "Alchemical Transmutation & Crucible Reactions"
    description = "Elemental reagent balancing and philosopher stone catalytic chains"
    cli_command = "craft alchemy"
    aliases = ["alchemy", "crucible"]
    studio_tab = "Worldbuilding"

    def execute(self, argv):
        return 42
'''
        plugin_file.write_text(plugin_code, encoding="utf-8")

        spec = load_user_plugin(plugin_file)
        self.assertIsNotNone(spec)
        self.assertEqual(spec.name, "alchemy_synth")  # type: ignore
        self.assertEqual(spec.title, "Alchemical Transmutation & Crucible Reactions")  # type: ignore

    def test_load_user_plugin_register_function(self) -> None:
        """Verifies loading a dynamic plugin file declaring register_engine()."""
        plugin_file = self.root / "astral_cartography.py"
        plugin_code = '''
from scripts.lib.registry import EngineSpec, EngineCategory

def register_engine():
    return EngineSpec(
        name="astral_map",
        category=EngineCategory.CRAFT,
        title="Astral Sea Cartography",
        description="Planar navigation and planar conjunctions",
        module_name="astral_cartography",
        cli_command="map astral",
    )
'''
        plugin_file.write_text(plugin_code, encoding="utf-8")

        spec = load_user_plugin(plugin_file)
        self.assertIsNotNone(spec)
        self.assertEqual(spec.name, "astral_map")  # type: ignore
        self.assertEqual(spec.title, "Astral Sea Cartography")  # type: ignore

    def test_discover_user_plugins_in_extra_dirs(self) -> None:
        """Verifies discovering plugins across multiple directory paths."""
        plugins_dir = self.root / ".plugins"
        plugins_dir.mkdir(parents=True, exist_ok=True)

        (plugins_dir / "plugin_one.py").write_text('''
from scripts.lib.registry import BaseCraftEngine
class EngineOne(BaseCraftEngine):
    name = "plugin_one"
    title = "Plugin One"
''', encoding="utf-8")

        (plugins_dir / "plugin_two.py").write_text('''
from scripts.lib.registry import BaseCraftEngine
class EngineTwo(BaseCraftEngine):
    name = "plugin_two"
    title = "Plugin Two"
''', encoding="utf-8")

        # Hidden or underscore file (should be ignored)
        (plugins_dir / "_ignored.py").write_text("invalid python code", encoding="utf-8")

        discovered = discover_user_plugins(extra_dirs=[plugins_dir])
        self.assertEqual(len(discovered), 2)
        names = [s.name for s in discovered]
        self.assertIn("plugin_one", names)
        self.assertIn("plugin_two", names)

        # Also verify alias discover_craft_plugins
        discovered_alias = discover_craft_plugins(extra_dirs=[plugins_dir])
        self.assertEqual(len(discovered_alias), 2)

    def test_typst_publication_presets_exist_and_valid(self) -> None:
        """Verifies that all 3 genre Typst publication presets exist with expected layouts."""
        typst_dir = Path(__file__).resolve().parent.parent / "templates" / "typst"
        self.assertTrue(typst_dir.is_dir(), f"Typst directory missing: {typst_dir}")

        expected_templates = [
            "epic_fantasy.typ",
            "hard_scifi.typ",
            "literary_trade.typ",
        ]

        for tmpl in expected_templates:
            tmpl_path = typst_dir / tmpl
            self.assertTrue(tmpl_path.is_file(), f"Typst template missing: {tmpl_path}")
            content = tmpl_path.read_text(encoding="utf-8")
            self.assertIn("#let", content)
            self.assertIn("set document", content)
            self.assertIn("set page", content)
            self.assertIn("body", content)


if __name__ == "__main__":
    unittest.main()
