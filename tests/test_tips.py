#!/usr/bin/env python3
"""
Comprehensive Unit and Integration Tests for Ars Arcanum Dynamic Tip Engine
(tests/test_tips.py)
================================================================================
Validates tip metadata database integrity, 51-engine coverage, intelligent ranking
and retrieval algorithms, configuration toggling, CLI commands, Studio Hub REST API,
and ecosystem integration.
"""

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from scripts.lib import cli
from scripts.lib import config
from scripts.lib import registry
from scripts.lib import story_canvas
from scripts.lib import studio_hub
from scripts.lib import tips
from scripts.lib import zen_studio


class TestTipModelAndDatabase(unittest.TestCase):
    """Validates Tip dataclass, Enum values, and TipDatabase internal structures."""

    def setUp(self) -> None:
        self.db = tips.get_tip_database()

    def test_database_not_empty_and_singleton(self) -> None:
        """Asserts database has loaded all tips and get_tip_database returns singleton."""
        self.assertGreaterEqual(len(self.db), 118)
        db2 = tips.get_tip_database()
        self.assertIs(self.db, db2)

    def test_engine_coverage_exactly_51(self) -> None:
        """Asserts that all domain engines (52 engines) are represented in the tips database."""
        engines = self.db.get_engines()
        self.assertGreaterEqual(len(engines), 51, f"Expected at least 51 engines, got {len(engines)}: {engines}")

    def test_unique_tip_ids(self) -> None:
        """Asserts that every tip in the database has a strictly unique identifier."""
        all_tips = self.db.get_all()
        ids = [t.id for t in all_tips]
        self.assertEqual(len(ids), len(set(ids)), "Found duplicate tip IDs in database!")

    def test_tip_metadata_completeness(self) -> None:
        """Validates that every tip contains all mandatory non-empty fields and valid types."""
        all_tips = self.db.get_all()
        for t in all_tips:
            self.assertTrue(t.id.startswith("tip_"), f"Tip ID must start with 'tip_': {t.id}")
            self.assertTrue(bool(t.engine.strip()), f"Empty engine in {t.id}")
            self.assertTrue(bool(t.feature.strip()), f"Empty feature in {t.id}")
            self.assertTrue(bool(t.subfeature.strip()), f"Empty subfeature in {t.id}")
            self.assertTrue(bool(t.title.strip()), f"Empty title in {t.id}")
            self.assertTrue(len(t.content.strip()) >= 30, f"Tip content too brief in {t.id}")
            self.assertTrue(len(t.rationale.strip()) >= 15, f"Tip rationale missing/brief in {t.id}")
            self.assertTrue(len(t.tags) >= 2, f"Tip must have at least 2 tags: {t.id}")
            self.assertTrue(len(t.contexts) >= 1, f"Tip must have at least 1 context: {t.id}")
            self.assertGreater(t.weight, 0.0, f"Weight must be positive: {t.id}")
            self.assertIsInstance(t.category, tips.TipCategory)
            self.assertIsInstance(t.pillar, tips.TipPillar)
            self.assertIsInstance(t.depth, tips.TipDepth)

    def test_tip_serialization_roundtrip(self) -> None:
        """Tests Tip.to_dict and Tip.from_dict roundtrip fidelity."""
        sample = self.db.get_all()[0]
        d = sample.to_dict()
        self.assertIsInstance(d, dict)
        self.assertEqual(d["id"], sample.id)
        self.assertEqual(d["category"], sample.category.value)
        self.assertEqual(d["pillar"], sample.pillar.value)
        self.assertEqual(d["depth"], sample.depth.value)

        reconstructed = tips.Tip.from_dict(d)
        self.assertEqual(reconstructed.id, sample.id)
        self.assertEqual(reconstructed.engine, sample.engine)
        self.assertEqual(reconstructed.subfeature, sample.subfeature)
        self.assertEqual(reconstructed.category, sample.category)
        self.assertEqual(reconstructed.pillar, sample.pillar)
        self.assertEqual(reconstructed.depth, sample.depth)

    def test_get_by_id(self) -> None:
        """Tests exact lookup by unique ID."""
        t = self.db.get_by_id("tip_astro_roche_limit_shattered_moons")
        self.assertIsNotNone(t)
        self.assertEqual(t.engine, "astrophysics")
        self.assertEqual(t.subfeature, "tidal_rings")

        missing = self.db.get_by_id("tip_nonexistent_xyz")
        self.assertIsNone(missing)


class TestIntelligentRetrieval(unittest.TestCase):
    """Tests search algorithms, ranking, subfeature filtering, and history cycle suppression."""

    def setUp(self) -> None:
        self.db = tips.TipDatabase()  # isolated instance for history testing

    def test_get_by_engine(self) -> None:
        """Tests retrieval by engine name and case-insensitivity."""
        astro_tips = self.db.get_by_engine("astrophysics")
        self.assertGreaterEqual(len(astro_tips), 4)

        climate_tips = self.db.get_by_engine("CLIMATE")
        self.assertGreaterEqual(len(climate_tips), 3)

        # Subfeature filtering
        roche_tips = self.db.get_by_engine("astrophysics", subfeature="tidal_rings")
        self.assertEqual(len(roche_tips), 1)
        self.assertEqual(roche_tips[0].subfeature, "tidal_rings")

    def test_get_by_context(self) -> None:
        """Tests retrieval by workflow context."""
        drafting_tips = self.db.get_by_context("drafting")
        self.assertGreater(len(drafting_tips), 10)

        worldbuilding_tips = self.db.get_by_context("worldbuilding")
        self.assertGreater(len(worldbuilding_tips), 20)

    def test_keyword_search(self) -> None:
        """Tests search query matching title, content, rationale, tags, and engine."""
        results = self.db.search("roche limit tidal forces")
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0].engine, "astrophysics")

        # Search for conlang phonotactics
        conlang_results = self.db.search("phonotactics sonority syllables")
        self.assertGreater(len(conlang_results), 0)
        self.assertEqual(conlang_results[0].engine, "conlang")

    def test_contextual_retrieval_history_cycling(self) -> None:
        """Tests that get_contextual_tip cycles through unseen tips before repeating."""
        climate_tips = self.db.get_by_engine("climate")
        total_climate = len(climate_tips)
        seen_ids = set()

        for _ in range(total_climate):
            tip = self.db.get_contextual_tip(engine="climate", exclude_seen=True)
            self.assertIsNotNone(tip)
            self.assertEqual(tip.engine, "climate")
            self.assertNotIn(tip.id, seen_ids)
            seen_ids.add(tip.id)

        self.assertEqual(len(seen_ids), total_climate)

        # After exhausting all climate tips, history should reset and continue returning valid tips
        next_tip = self.db.get_contextual_tip(engine="climate", exclude_seen=True)
        self.assertIsNotNone(next_tip)
        self.assertIn(next_tip.id, seen_ids)


class TestConfigAndPreferenceToggling(unittest.TestCase):
    """Tests enabling, disabling, and persisting tips preferences."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.orig_xdg = os.environ.get("XDG_CONFIG_HOME")
        os.environ["XDG_CONFIG_HOME"] = self.temp_dir.name

    def tearDown(self) -> None:
        if self.orig_xdg is not None:
            os.environ["XDG_CONFIG_HOME"] = self.orig_xdg
        else:
            os.environ.pop("XDG_CONFIG_HOME", None)
        self.temp_dir.cleanup()

    def test_default_tips_enabled(self) -> None:
        """Asserts that tips are enabled by default on clean installations."""
        self.assertTrue(tips.are_tips_enabled())
        self.assertTrue(config.get_tips_enabled())

    def test_set_and_get_tips_enabled(self) -> None:
        """Tests setting tips to disabled and persisting to config file."""
        config.set_tips_enabled(False)
        self.assertFalse(config.get_tips_enabled())
        self.assertFalse(tips.are_tips_enabled())

        config.set_tips_enabled(True)
        self.assertTrue(config.get_tips_enabled())
        self.assertTrue(tips.are_tips_enabled())

    def test_toggle_tips(self) -> None:
        """Tests toggling tips enabled status back and forth."""
        self.assertTrue(tips.are_tips_enabled())
        new_state = tips.toggle_tips()
        self.assertFalse(new_state)
        self.assertFalse(tips.are_tips_enabled())

        new_state2 = tips.toggle_tips()
        self.assertTrue(new_state2)
        self.assertTrue(tips.are_tips_enabled())


class TestRegistryIntegration(unittest.TestCase):
    """Validates integration with scripts/lib/registry.py."""

    def test_get_engine_tips_from_registry(self) -> None:
        """Tests registry.get_engine_tips returns accurate tips for registered engines."""
        astrophysics_tips = registry.get_engine_tips("astrophysics")
        self.assertGreaterEqual(len(astrophysics_tips), 4)
        for t in astrophysics_tips:
            self.assertEqual(t["engine"], "astrophysics")

    def test_engine_catalog_contains_tips(self) -> None:
        """Tests that registry.get_engine_catalog metadata includes tips count and payloads."""
        catalog = registry.get_engine_catalog()
        self.assertIsInstance(catalog, list)
        astro_meta = next((e for e in catalog if e["id"] == "astrophysics"), None)
        self.assertIsNotNone(astro_meta)
        assert astro_meta is not None
        self.assertIn("tips", astro_meta)
        self.assertGreaterEqual(len(astro_meta["tips"]), 4)


class TestCliCommands(unittest.TestCase):
    """Tests CLI entry points, subcommands, and flag parsing."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.orig_xdg = os.environ.get("XDG_CONFIG_HOME")
        os.environ["XDG_CONFIG_HOME"] = self.temp_dir.name

    def tearDown(self) -> None:
        if self.orig_xdg is not None:
            os.environ["XDG_CONFIG_HOME"] = self.orig_xdg
        else:
            os.environ.pop("XDG_CONFIG_HOME", None)
        self.temp_dir.cleanup()

    def test_cli_tip_list_engines(self) -> None:
        """Tests 'arcanum tip --list-engines' output."""
        buf = io.StringIO()
        with redirect_stdout(buf):
            ret = tips.main(["--list-engines"])
        self.assertEqual(ret, 0)
        out = buf.getvalue()
        self.assertIn("engines", out)
        self.assertIn("astrophysics", out)
        self.assertIn("pacing", out)

    def test_cli_tip_by_engine_and_json(self) -> None:
        """Tests 'arcanum tip --engine pacing --json' returns valid JSON."""
        buf = io.StringIO()
        with redirect_stdout(buf):
            ret = tips.main(["--engine", "pacing", "--json"])
        self.assertEqual(ret, 0)
        data = json.loads(buf.getvalue())
        self.assertEqual(data["engine"], "pacing")
        self.assertIn("title", data)
        self.assertIn("content", data)

    def test_cli_tip_all_json(self) -> None:
        """Tests 'arcanum tip --all --json' returns all tips in JSON list."""
        buf = io.StringIO()
        with redirect_stdout(buf):
            ret = tips.main(["--all", "--json"])
        self.assertEqual(ret, 0)
        data = json.loads(buf.getvalue())
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 118)

    def test_cli_tip_enable_disable_status(self) -> None:
        """Tests toggling tips via CLI flags."""
        buf = io.StringIO()
        with redirect_stdout(buf):
            tips.main(["--disable"])
        self.assertFalse(tips.are_tips_enabled())

        buf = io.StringIO()
        with redirect_stdout(buf):
            tips.main(["--status"])
        self.assertIn("DISABLED", buf.getvalue())

        buf = io.StringIO()
        with redirect_stdout(buf):
            tips.main(["--enable"])
        self.assertTrue(tips.are_tips_enabled())

    def test_config_cli_subcommand(self) -> None:
        """Tests 'arcanum config tips disable' and 'arcanum config tips enable'."""
        buf = io.StringIO()
        with redirect_stdout(buf):
            config.main(["tips", "disable"])
        self.assertFalse(config.get_tips_enabled())

        buf = io.StringIO()
        with redirect_stdout(buf):
            config.main(["tips", "get"])
        self.assertIn("tips_enabled: False", buf.getvalue())

        buf = io.StringIO()
        with redirect_stdout(buf):
            config.main(["tips", "enable"])
        self.assertTrue(config.get_tips_enabled())

    def test_unified_cli_dispatcher_aliases(self) -> None:
        """Tests that aliases ('tip', 'tips', 'craft-tip', 'wisdom', 'hint') route cleanly."""
        for alias in ["tip", "tips", "craft-tip", "wisdom", "hint", "hints"]:
            buf = io.StringIO()
            with redirect_stdout(buf):
                ret = cli.main([alias, "--status"])
            self.assertEqual(ret, 0, f"Alias {alias} failed with returncode {ret}")
            self.assertIn("Dynamic tips:", buf.getvalue())


class TestStudioHubAndRestApi(unittest.TestCase):
    """Tests Studio Hub HTTP endpoints for tip retrieval and preference toggling."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.orig_xdg = os.environ.get("XDG_CONFIG_HOME")
        os.environ["XDG_CONFIG_HOME"] = self.temp_dir.name

    def tearDown(self) -> None:
        if self.orig_xdg is not None:
            os.environ["XDG_CONFIG_HOME"] = self.orig_xdg
        else:
            os.environ.pop("XDG_CONFIG_HOME", None)
        self.temp_dir.cleanup()

    def test_studio_hub_data_contains_tips(self) -> None:
        """Tests that collect_studio_hub_data includes tips catalog and tips_enabled state."""
        data = studio_hub.collect_studio_hub_data()
        self.assertIn("tips", data)
        self.assertTrue(data["tips"]["enabled"])
        self.assertGreaterEqual(len(data["tips"]["tips"]), 118)

    def test_studio_hub_html_generation(self) -> None:
        """Tests that Studio Hub HTML contains tip bar and dynamic tip switcher script."""
        data = studio_hub.collect_studio_hub_data()
        html_code = studio_hub.generate_studio_hub_html(data)
        self.assertIn('id="dynamic-tip-bar"', html_code)
        self.assertIn("cycleNextTip", html_code)
        self.assertIn("toggleTipsBar", html_code)


class TestZenStudioAndStoryCanvasIntegration(unittest.TestCase):
    """Validates tips integration inside Zen Studio and Story Canvas."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.manuscript = self.root / "Test_Novel"
        self.manuscript.mkdir(parents=True, exist_ok=True)
        (self.manuscript / "01_Prologue.md").write_text(
            "# Chapter 1: The Gathering\n\nIt was a dark and stormy dawn in the high mountains.\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_zen_studio_bundle_has_tips(self) -> None:
        """Tests that Zen Studio bundle includes tips tab and footer tip ticker."""
        bundle_path = zen_studio.build_zen_studio_bundle(self.manuscript)
        self.assertTrue(bundle_path.exists())
        html_out = bundle_path.read_text(encoding="utf-8")
        self.assertIn("zenTipBar", html_out)
        self.assertIn("💡 Tips", html_out)

    def test_story_canvas_html_has_tips(self) -> None:
        """Tests that Story Canvas HTML output contains non-intrusive tip ticker."""
        cards = story_canvas.extract_scene_cards(self.manuscript)
        out_html = self.root / "canvas.html"
        html_str = story_canvas.generate_story_canvas_html(self.manuscript, cards, output_path=out_html)
        self.assertIn('id="tipBar"', html_str)
        self.assertIn("cycleCanvasTip", html_str)
        self.assertTrue(out_html.exists())


class TestExhaustiveSubfeatureCoverage(unittest.TestCase):
    """Deep verification that all 117 subfeatures across all 51 engines resolve properly."""

    def setUp(self) -> None:
        self.db = tips.get_tip_database()

    def test_all_117_registry_subfeatures_resolve_tips(self) -> None:
        """Asserts that every subfeature in registry._ENGINES retrieves matching tips."""
        total_subfeatures = 0
        for eng_name, spec in registry._ENGINES.items():
            for sf in spec.subfeatures:
                total_subfeatures += 1
                sf_name = sf["name"]
                matched_tips = self.db.get_by_engine(eng_name, sf_name)
                self.assertGreater(
                    len(matched_tips),
                    0,
                    f"Subfeature '{sf_name}' in engine '{eng_name}' returned no tips!",
                )
                contextual_tip = self.db.get_contextual_tip(engine=eng_name, subfeature=sf_name)
                self.assertIsNotNone(
                    contextual_tip,
                    f"get_contextual_tip failed for subfeature '{sf_name}' in engine '{eng_name}'",
                )
        self.assertGreaterEqual(total_subfeatures, 117, f"Expected at least 117 subfeatures in registry, found {total_subfeatures}")

    def test_engine_alias_resolution(self) -> None:
        """Asserts that all common aliases and commands resolve to canonical engine keys."""
        test_cases = [
            ("astro", "astrophysics"),
            ("orbital", "astrophysics"),
            ("weather", "climate"),
            ("biomes", "climate"),
            ("lunar", "calendar"),
            ("trophic", "ecology"),
            ("corkboard", "story_canvas"),
            ("canvas", "story_canvas"),
            ("time-travel", "causality"),
            ("cast", "dramatis_personae"),
            ("dialogue-voice", "voice"),
            ("linguistics", "conlang"),
            ("lineage", "genealogy"),
            ("diplomacy", "factions"),
            ("battle", "tactical_sim"),
            ("arcane", "magic_system"),
            ("spells", "magic_system"),
            ("quotes", "typography_cleaner"),
            ("redline", "manuscript_diff"),
            ("churn", "revision_heatmap"),
            ("binaural", "ambient"),
            ("rag", "local_rag"),
            ("scrivener", "importer"),
            ("word", "docx_sync"),
            ("prepress", "preflight"),
            ("glossary", "concordance"),
            ("wiki", "codex_export"),
            ("mesh", "resonance"),
            ("synergy", "resonance"),
        ]
        for alias, expected in test_cases:
            resolved = self.db.resolve_engine(alias)
            self.assertEqual(resolved, expected, f"Alias '{alias}' resolved to '{resolved}', expected '{expected}'")

    def test_edge_cases_and_corrupted_config_resilience(self) -> None:
        """Tests unknown engines, empty queries, and corrupted config JSON files."""
        # Unknown engine falls back gracefully
        unknown = self.db.get_by_engine("completely_unknown_xyz123")
        self.assertEqual(unknown, [])

        # Empty queries
        empty_search = self.db.search("")
        self.assertGreater(len(empty_search), 0)

        # Non-existent contextual tip query falls back to universal database
        tip = self.db.get_contextual_tip(engine="unknown_engine_123")
        self.assertIsNotNone(tip)

        # Corrupted config file recovery
        with tempfile.TemporaryDirectory() as tmp:
            cfg_file = Path(tmp) / "config.json"
            cfg_file.write_text("{corrupted_json_invalid", encoding="utf-8")
            orig_xdg = os.environ.get("XDG_CONFIG_HOME")
            try:
                os.environ["XDG_CONFIG_HOME"] = tmp
                # Should not raise, falls back to True
                self.assertTrue(tips.are_tips_enabled())
            finally:
                if orig_xdg:
                    os.environ["XDG_CONFIG_HOME"] = orig_xdg
                else:
                    os.environ.pop("XDG_CONFIG_HOME", None)


if __name__ == "__main__":
    unittest.main()

