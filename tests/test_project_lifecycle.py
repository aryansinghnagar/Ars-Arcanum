#!/usr/bin/env python3
"""
Tests for Ars Arcanum Project Lifecycle & Scaffolding Engine (tests/test_project_lifecycle.py)
=============================================================================================
Tests all 5 speculative fiction archetypes, Constitution presets, interactive wizard,
dry-run preview mode, and zero-dependency schema consistency.
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
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.project_scaffold import (
    CONSTITUTION_PRESETS,
    get_constitution_preset,
    get_manuscripts_base,
    get_universes_base,
    list_manuscripts,
    list_universes,
    list_worlds,
    main,
    run_interactive_wizard,
    scaffold_manuscript,
    scaffold_novella,
    scaffold_serial,
    scaffold_universe,
    scaffold_volume,
    scaffold_world,
)


class TestProjectLifecycle(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp(prefix="arcanum_test_scaffold_"))
        self.univ_base = self.tmp_dir / "Universes"
        self.ms_base = self.tmp_dir / "Manuscripts"
        self.univ_base.mkdir(parents=True, exist_ok=True)
        self.ms_base.mkdir(parents=True, exist_ok=True)

        self.env_patch = patch.dict(
            "os.environ",
            {
                "UNIVERSES_BASE": str(self.univ_base),
                "MANUSCRIPTS_BASE": str(self.ms_base),
            },
        )
        self.env_patch.start()

    def tearDown(self):
        self.env_patch.stop()
        if self.tmp_dir.exists():
            shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_get_base_directories_env_override(self):
        self.assertEqual(get_universes_base(), self.univ_base.resolve())
        self.assertEqual(get_manuscripts_base(), self.ms_base.resolve())

    def test_constitution_presets_and_omission_of_magic_timeline(self):
        expected_presets = ["epic-fantasy", "hard-scifi", "grimdark", "mystery-thriller", "literary-speculative", "unconstrained"]
        for p in expected_presets:
            self.assertIn(p, CONSTITUTION_PRESETS)
            preset_data = get_constitution_preset(p)
            self.assertIn("name", preset_data)
            self.assertIn("canon", preset_data)
            self.assertIn("style", preset_data)
            self.assertIn("structure", preset_data)
            # Invariant: magic modality and timeline strictness are deliberately omitted
            self.assertNotIn("magic", preset_data)
            self.assertNotIn("timeline", preset_data.get("continuity", {}))

    def test_scaffold_universe_creation(self):
        res = scaffold_universe("Aethelgard", base_dir=self.univ_base, author="Master Creator")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["type"], "universe")
        self.assertEqual(res["name"], "Aethelgard")

        u_dir = self.univ_base / "Aethelgard"
        self.assertTrue(u_dir.is_dir())
        self.assertTrue((u_dir / "universe.yaml").is_file())
        self.assertTrue((u_dir / ".gitignore").is_file())
        self.assertTrue((u_dir / "Manuscripts").is_dir())
        self.assertTrue((u_dir / "Worlds").is_dir())
        self.assertTrue((u_dir / "Art").is_dir())
        self.assertTrue((u_dir / "Audio").is_dir())

        # Duplicate should fail
        with self.assertRaises(FileExistsError):
            scaffold_universe("Aethelgard", base_dir=self.univ_base)

    def test_scaffold_world_standalone_and_in_universe(self):
        scaffold_universe("CosmosA", base_dir=self.univ_base)
        w_res = scaffold_world("Eldoria", universe_name="CosmosA", base_dir=self.univ_base, preset="epic-fantasy")
        self.assertEqual(w_res["status"], "success")
        self.assertEqual(w_res["universe"], "CosmosA")

        w_dir = self.univ_base / "CosmosA" / "Worlds" / "Eldoria"
        self.assertTrue(w_dir.is_dir())
        self.assertTrue((w_dir / "world.yaml").is_file())
        self.assertTrue((w_dir / "constitution.yaml").is_file())
        self.assertTrue((w_dir / "Locations").is_dir())
        self.assertTrue((w_dir / "Characters").is_dir())
        self.assertTrue((w_dir / "Cosmology").is_dir())
        self.assertTrue((w_dir / "Factions").is_dir())
        self.assertTrue((w_dir / "History").is_dir())

        # Duplicate should fail
        with self.assertRaises(FileExistsError):
            scaffold_world("Eldoria", universe_name="CosmosA", base_dir=self.univ_base)

        # Standalone / default universe
        w_def = scaffold_world("SolitaryWorld")
        self.assertEqual(w_def["status"], "success")
        self.assertTrue((self.univ_base / "Default-Universe" / "Worlds" / "SolitaryWorld").is_dir())

    def test_scaffold_novel_manuscript_and_volume(self):
        scaffold_universe("HighFantasy", base_dir=self.univ_base)
        scaffold_world("Valenor", universe_name="HighFantasy", base_dir=self.univ_base)

        m_res = scaffold_manuscript(
            "CrownOfShadows",
            archetype="novel",
            universe="HighFantasy",
            world="Valenor",
            base_dir=self.ms_base,
            target_words=100000,
            preset="epic-fantasy",
        )
        self.assertEqual(m_res["status"], "success")
        self.assertEqual(m_res["name"], "CrownOfShadows")

        m_dir = Path(m_res["path"])
        self.assertTrue(m_dir.is_dir())
        self.assertTrue((m_dir / "manuscript.yaml").is_file())
        self.assertTrue((m_dir / "constitution.yaml").is_file())
        self.assertTrue((m_dir / "nwProject.nwx").is_file())
        self.assertTrue((m_dir / "01-Manuscript" / "Book-01" / "Draft-01" / "01_Act_I" / "01_Chapter_01.md").is_file())
        self.assertTrue((m_dir / "01-Manuscript" / "Book-01" / "Draft-01" / "02_Act_II" / "01_Chapter_03.md").is_file())
        self.assertTrue((m_dir / "01-Manuscript" / "Book-01" / "Draft-01" / "03_Act_III" / "01_Chapter_04.md").is_file())
        self.assertTrue((m_dir / "Outlines" / "Master-Outline.md").is_file())

        # Duplicate manuscript should fail
        with self.assertRaises(FileExistsError):
            scaffold_manuscript(
                "CrownOfShadows",
                universe="HighFantasy",
                world="Valenor",
                base_dir=self.ms_base,
            )

        # Add Volume 2
        v_res = scaffold_volume(str(m_dir), "Book-02", title="The Sundered Throne")
        self.assertEqual(v_res["status"], "success")
        self.assertTrue((m_dir / "01-Manuscript" / "Book-02" / "Draft-01" / "01_Chapter_01.md").is_file())

        # Duplicate volume should fail
        with self.assertRaises(FileExistsError):
            scaffold_volume(str(m_dir), "Book-02")

    def test_scaffold_novella_archetype(self):
        nov_res = scaffold_novella(
            "WhisperingCaves",
            universe="HighFantasy",
            world="Valenor",
            base_dir=self.ms_base,
            target_words=25000,
            preset="mystery-thriller",
        )
        self.assertEqual(nov_res["status"], "success")
        self.assertEqual(nov_res["archetype"], "novella")

        n_dir = Path(nov_res["path"])
        self.assertTrue(n_dir.is_dir())
        self.assertTrue((n_dir / "manuscript.yaml").is_file())
        self.assertTrue((n_dir / "constitution.yaml").is_file())
        # Novellas use flat chapter layout
        self.assertTrue((n_dir / "01-Manuscript" / "Draft-01" / "01_Chapter_01.md").is_file())
        self.assertTrue((n_dir / "01-Manuscript" / "Draft-01" / "02_Chapter_02.md").is_file())
        self.assertTrue((n_dir / "01-Manuscript" / "Draft-01" / "03_Chapter_03.md").is_file())

    def test_scaffold_serial_archetype(self):
        ser_res = scaffold_serial(
            "StarlightChronicles",
            universe="SciFiCosmos",
            world="Hyperion",
            base_dir=self.ms_base,
            target_words=200000,
            cadence="weekly",
            preset="hard-scifi",
        )
        self.assertEqual(ser_res["status"], "success")
        self.assertEqual(ser_res["archetype"], "serial")

        s_dir = Path(ser_res["path"])
        self.assertTrue(s_dir.is_dir())
        self.assertTrue((s_dir / "manuscript.yaml").is_file())
        self.assertTrue((s_dir / "constitution.yaml").is_file())
        self.assertTrue((s_dir / "03-Backlog-Buffer").is_dir())
        # Serials use Arc & Episode layout
        self.assertTrue((s_dir / "01-Manuscript" / "Arc-01" / "Draft-01" / "01_Episode_01.md").is_file())
        self.assertTrue((s_dir / "01-Manuscript" / "Arc-01" / "Draft-01" / "02_Episode_02.md").is_file())
        self.assertTrue((s_dir / "01-Manuscript" / "Arc-02" / "Draft-01" / "01_Episode_01.md").is_file())

    def test_dry_run_mode(self):
        dry_target = self.tmp_dir / "DryRunTest"
        res = scaffold_manuscript("DryBook", base_dir=dry_target, dry_run=True)
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["dry_run"])
        self.assertGreater(len(res["created_files"]), 0)
        # Verify no directory was actually created on disk
        self.assertFalse((dry_target / "DryBook").exists())

    def test_list_functions(self):
        list_univ_base = self.tmp_dir / "ListUniverses"
        list_ms_base = self.tmp_dir / "ListManuscripts"
        list_univ_base.mkdir()
        list_ms_base.mkdir()

        scaffold_universe("UniverseOne", base_dir=list_univ_base)
        scaffold_universe("UniverseTwo", base_dir=list_univ_base)
        scaffold_world("WorldA", universe_name="UniverseOne", base_dir=list_univ_base)
        scaffold_world("WorldB", universe_name="UniverseTwo", base_dir=list_univ_base)
        scaffold_manuscript("NovelA", universe="UniverseOne", world="WorldA", base_dir=list_ms_base)

        univs = list_universes(base_dir=list_univ_base)
        self.assertEqual(len(univs), 2)
        names = [u["name"] for u in univs]
        self.assertIn("UniverseOne", names)
        self.assertIn("UniverseTwo", names)

        worlds = list_worlds(base_dir=list_univ_base)
        self.assertEqual(len(worlds), 2)

        worlds_filtered = list_worlds(universe_filter="UniverseOne", base_dir=list_univ_base)
        self.assertEqual(len(worlds_filtered), 1)
        self.assertEqual(worlds_filtered[0]["name"], "WorldA")

        mss = list_manuscripts(base_dir=list_ms_base)
        self.assertEqual(len(mss), 1)
        self.assertEqual(mss[0]["name"], "NovelA")

    def test_cli_interface_scaffold_all_commands(self):
        # 1. Presets command
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            rc = main(["presets"])
            self.assertEqual(rc, 0)
            self.assertIn("epic-fantasy", mock_out.getvalue())
            self.assertIn("hard-scifi", mock_out.getvalue())

        # 2. Universe
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            rc = main(["new", "universe", "CliUniverse", "--dir", str(self.univ_base)])
            self.assertEqual(rc, 0)
            self.assertIn("Created Universe: CliUniverse", mock_out.getvalue())

        # 3. World
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            rc = main(["new", "world", "CliWorld", "--universe", "CliUniverse", "--dir", str(self.univ_base / "CliUniverse" / "Worlds")])
            self.assertEqual(rc, 0)
            self.assertIn("Created World Lore Bible: CliWorld", mock_out.getvalue())

        # 4. Novel Manuscript
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            rc = main(["new", "novel", "CliBook", "--preset", "epic-fantasy", "--dir", str(self.ms_base)])
            self.assertEqual(rc, 0)
            self.assertIn("Created Novel Manuscript: CliBook", mock_out.getvalue())

        # 5. Novella
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            rc = main(["new", "novella", "CliNovella", "--preset", "mystery-thriller", "--dir", str(self.ms_base)])
            self.assertEqual(rc, 0)
            self.assertIn("Created Novella: CliNovella", mock_out.getvalue())

        # 6. Serial
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            rc = main(["new", "serial", "CliSerial", "--preset", "hard-scifi", "--dir", str(self.ms_base)])
            self.assertEqual(rc, 0)
            self.assertIn("Created Serial: CliSerial", mock_out.getvalue())

        # 7. JSON output flag
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            rc = main(["new", "novella", "JsonNovella", "--dir", str(self.ms_base), "--json"])
            self.assertEqual(rc, 0)
            data = json.loads(mock_out.getvalue())
            self.assertEqual(data["status"], "success")
            self.assertEqual(data["name"], "JsonNovella")

        # 8. Listing subcommands
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            rc = main(["universe", "--list"])
            self.assertEqual(rc, 0)
            self.assertIn("CliUniverse", mock_out.getvalue())

        # 9. Error case: duplicate creation via CLI returns code 1
        with patch("sys.stderr", new_callable=io.StringIO) as mock_err:
            rc = main(["new", "universe", "CliUniverse", "--dir", str(self.univ_base)])
            self.assertEqual(rc, 1)
            self.assertIn("already exists", mock_err.getvalue())

    def test_interactive_wizard_flow(self):
        # Mock inputs: [1: novel, Title, Author, Universe, World, Words, Preset (1: epic-fantasy), Dir]
        mock_inputs = [
            "1",
            "WizardNovel",
            "WizardAuthor",
            "WizardUniverse",
            "WizardWorld",
            "90000",
            "1",
            str(self.ms_base),
        ]
        with patch("builtins.input", side_effect=mock_inputs), patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            rc = run_interactive_wizard()
            self.assertEqual(rc, 0)
            self.assertIn("Successfully created", mock_out.getvalue())
            self.assertTrue((self.ms_base / "WizardNovel" / "manuscript.yaml").is_file())


if __name__ == "__main__":
    unittest.main()
