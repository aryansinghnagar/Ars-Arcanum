#!/usr/bin/env python3
"""
Unit and Integration tests for Ars Arcanum Manuscript Structure Scaffolder
(scripts/lib/manuscript_scaffold.py)
"""

import io
import json
import re
import tempfile
import unittest
from pathlib import Path
import sys
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.manuscript_scaffold import (
    STRUCTURE_PRESETS,
    generate_manuscript_manifest,
    get_paradigm_key,
    get_preset,
    list_presets,
    main,
    read_manifest_structure,
    scaffold_volume,
    validate_division_name,
)
from lib.structure import PARADIGMS, scan_manuscript_structure
from tests.helpers import create_test_manuscript, create_test_volume


class TestManuscriptScaffold(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_all_16_presets_registered(self):
        """Verify all 16 narrative framework presets are registered."""
        expected_keys = [
            "three_act", "freytags_pyramid", "heros_journey", "save_the_cat",
            "story_circle", "kishotenketsu", "seven_point", "fichtean_curve",
            "eight_sequence", "mice_quotient", "romancing_the_beat", "virgins_promise",
            "snowflake", "parallel", "episodic", "nonlinear", "none", "framework_free"
        ]
        self.assertEqual(len(STRUCTURE_PRESETS), len(expected_keys))
        for key in expected_keys:
            self.assertIn(key, STRUCTURE_PRESETS, f"Preset '{key}' missing from STRUCTURE_PRESETS")

    def test_preset_data_integrity(self):
        """Verify every preset has valid structure, labels, and paradigm mappings."""
        for key, preset in STRUCTURE_PRESETS.items():
            self.assertIn("name", preset, f"Preset '{key}' missing 'name'")
            self.assertIsInstance(preset["name"], str)
            self.assertIn("divisions", preset, f"Preset '{key}' missing 'divisions'")
            self.assertIsInstance(preset["divisions"], list)
            self.assertGreater(len(preset["divisions"]), 0, f"Preset '{key}' has empty divisions")

            for div in preset["divisions"]:
                self.assertIn("label", div)
                self.assertIn("desc", div)
                self.assertTrue(bool(re.match(r"^[A-Za-z0-9_-]+$", div["label"])),
                                f"Preset '{key}' has invalid label '{div['label']}'")
                self.assertIsInstance(div["desc"], str)
                self.assertGreater(len(div["desc"]), 0)

            paradigm_key = preset.get("paradigm_key")
            if paradigm_key is not None:
                self.assertIn(paradigm_key, PARADIGMS,
                              f"Preset '{key}' links to unknown paradigm '{paradigm_key}' in structure.py")

    def test_division_name_validation_valid(self):
        """Verify valid division identifiers pass validation."""
        valid_names = [
            "Act_I", "Act_II", "Departure", "Initiation", "Return",
            "Ki-Introduction", "Seq_A-Status_Quo", "Part-01", "Epilogue_2",
            "Thread_A", "Episode-01", "Fragment-99"
        ]
        for name in valid_names:
            validated = validate_division_name(name)
            self.assertEqual(validated, name)

    def test_division_name_validation_invalid(self):
        """Verify path traversal, injection, and invalid tokens are rejected."""
        invalid_names = [
            "", "   ", "Act/I", "Act\\II", "../Act_I", "Act..I",
            "Act*I", "Act?I", "Act I", "@Act_I", "Act#I", "Act;rm"
        ]
        for name in invalid_names:
            with self.assertRaises(ValueError, msg=f"Should reject: {name!r}"):
                validate_division_name(name)

    def test_scaffold_three_act_default(self):
        """Verify default three_act scaffold matches canonical 01_Act_I layout."""
        vol_dir = self.root / "Book-01"
        created = scaffold_volume(vol_dir, structure_key="three_act")

        self.assertEqual(len(created), 3)
        self.assertEqual(created[0].name, "01_Act_I")
        self.assertEqual(created[1].name, "02_Act_II")
        self.assertEqual(created[2].name, "03_Act_III")

        for d in created:
            self.assertTrue(d.is_dir())

        starter_file = created[0] / "01_Chapter_01.md"
        self.assertTrue(starter_file.is_file())
        content = starter_file.read_text(encoding="utf-8")
        self.assertIn("# Chapter 1", content)
        self.assertIn("Begin writing Book-01 here", content)

    def test_scaffold_all_16_presets(self):
        """Verify scaffolding for all 16 presets produces expected folder layouts."""
        for key, preset in STRUCTURE_PRESETS.items():
            vol_dir = self.root / f"Volume_{key}"
            created = scaffold_volume(vol_dir, structure_key=key)

            expected_divs = preset["divisions"]
            self.assertEqual(len(created), len(expected_divs), f"Mismatch for preset '{key}'")

            for idx, (dir_path, div_def) in enumerate(zip(created, expected_divs, strict=False), 1):
                expected_name = f"{idx:02d}_{div_def['label']}"
                self.assertEqual(dir_path.name, expected_name)
                self.assertTrue(dir_path.is_dir())

            # First division should have starter chapter
            starter = created[0] / "01_Chapter_01.md"
            self.assertTrue(starter.is_file())

    def test_scaffold_custom_divisions(self):
        """Verify user-defined custom divisions scaffold correctly."""
        vol_dir = self.root / "CustomVol"
        custom_divs = ["Prologue", "Part-I", "Part-II", "Epilogue"]
        created = scaffold_volume(vol_dir, structure_key="custom", custom_divisions=custom_divs)

        self.assertEqual(len(created), 4)
        self.assertEqual(created[0].name, "01_Prologue")
        self.assertEqual(created[1].name, "02_Part-I")
        self.assertEqual(created[2].name, "03_Part-II")
        self.assertEqual(created[3].name, "04_Epilogue")

        for d in created:
            self.assertTrue(d.is_dir())
        self.assertTrue((created[0] / "01_Chapter_01.md").is_file())

    def test_scaffold_empty_custom_divisions_rejected(self):
        """Verify custom structure without division list raises ValueError."""
        vol_dir = self.root / "EmptyCustom"
        with self.assertRaises(ValueError):
            scaffold_volume(vol_dir, structure_key="custom", custom_divisions=[])
        with self.assertRaises(ValueError):
            scaffold_volume(vol_dir, structure_key="custom", custom_divisions=None)

    def test_scaffold_unknown_preset_rejected(self):
        """Verify unknown preset key raises ValueError."""
        vol_dir = self.root / "UnknownPreset"
        with self.assertRaises(ValueError) as ctx:
            scaffold_volume(vol_dir, structure_key="invalid_unknown_preset")
        self.assertIn("Unknown structure preset", str(ctx.exception))

    def test_scaffold_idempotency_collision(self):
        """Verify attempting to scaffold onto existing division directories raises FileExistsError."""
        vol_dir = self.root / "CollideVol"
        scaffold_volume(vol_dir, structure_key="three_act")

        with self.assertRaises(FileExistsError):
            scaffold_volume(vol_dir, structure_key="three_act")

    def test_scaffold_no_starter_option(self):
        """Verify create_starter_chapter=False skips starter file."""
        vol_dir = self.root / "NoStarterVol"
        created = scaffold_volume(vol_dir, structure_key="three_act", create_starter_chapter=False)
        self.assertFalse((created[0] / "01_Chapter_01.md").exists())

    def test_list_presets_output(self):
        """Verify list_presets formats all 16 presets."""
        output = list_presets()
        self.assertIn("Ars Arcanum — Manuscript Structure Presets", output)
        for key in STRUCTURE_PRESETS:
            self.assertIn(f"* {key}:", output)
        self.assertIn("* custom:", output)

    def test_get_paradigm_key_mapping(self):
        """Verify mapping of presets to structure.py paradigms."""
        self.assertEqual(get_paradigm_key("three_act"), "three_act")
        self.assertEqual(get_paradigm_key("heros_journey"), "heros_journey")
        self.assertEqual(get_paradigm_key("save_the_cat"), "save_the_cat")
        self.assertEqual(get_paradigm_key("kishotenketsu"), "kishotenketsu")
        self.assertIsNone(get_paradigm_key("mice_quotient"))
        self.assertIsNone(get_paradigm_key("snowflake"))
        self.assertIsNone(get_paradigm_key("nonexistent_preset"))

    def test_get_preset_lookup(self):
        """Verify get_preset case-insensitivity and None fallback."""
        preset = get_preset("Three_Act")
        self.assertIsNotNone(preset)
        self.assertEqual(preset["name"], "Classic Three-Act Structure")  # type: ignore[index]
        self.assertIsNone(get_preset("nonexistent"))

    def test_generate_and_read_manifest_preset(self):
        """Verify manuscript.yaml manifest generation and roundtrip reading."""
        ms_dir = self.root / "ManifestTest"
        ms_dir.mkdir(parents=True, exist_ok=True)
        manifest = generate_manuscript_manifest(
            title="Sovereign Arc",
            author="Arcanist",
            universe="Elder-Cosmos",
            world="Aethelgard",
            structure="heros_journey",
        )
        (ms_dir / "manuscript.yaml").write_text(manifest, encoding="utf-8")

        structure_key, custom_divs = read_manifest_structure(ms_dir)
        self.assertEqual(structure_key, "heros_journey")
        self.assertIsNone(custom_divs)

    def test_generate_and_read_manifest_custom(self):
        """Verify manuscript.yaml with custom divisions roundtrips correctly."""
        ms_dir = self.root / "CustomManifestTest"
        ms_dir.mkdir(parents=True, exist_ok=True)
        manifest = generate_manuscript_manifest(
            title="Custom Arc",
            structure="custom",
            custom_divisions=["Prelude", "Act_One", "Interlude", "Coda"],
        )
        (ms_dir / "manuscript.yaml").write_text(manifest, encoding="utf-8")

        structure_key, custom_divs = read_manifest_structure(ms_dir)
        self.assertEqual(structure_key, "custom")
        self.assertEqual(custom_divs, ["Prelude", "Act_One", "Interlude", "Coda"])

    def test_read_manifest_structure_deep_traversal(self):
        """Verify read_manifest_structure traverses parent directories from nested files/folders."""
        ms_dir = create_test_manuscript(
            self.root,
            name="DeepManuscript",
            structure="seven_point",
            volumes=("Book-01",),
            chapters_per_division=1,
        )
        vol_path = ms_dir / "Book-01"
        div_path = vol_path / "01_Hook_and_Turn"
        ch_path = div_path / "01_Chapter_01.md"

        # Traversal from volume dir
        struct_vol, _ = read_manifest_structure(vol_path)
        self.assertEqual(struct_vol, "seven_point")

        # Traversal from division dir
        struct_div, _ = read_manifest_structure(div_path)
        self.assertEqual(struct_div, "seven_point")

        # Traversal from chapter file path
        struct_ch, _ = read_manifest_structure(ch_path)
        self.assertEqual(struct_ch, "seven_point")

        # Fallback for non-existent path
        struct_none, divs_none = read_manifest_structure(self.root / "NonExistentDir")
        self.assertEqual(struct_none, "three_act")
        self.assertIsNone(divs_none)

    def test_integration_test_fixture_helper(self):
        """Verify create_test_manuscript creates valid directory structure."""
        ms_dir = create_test_manuscript(
            self.root,
            name="Epic-Saga",
            structure="kishotenketsu",
            volumes=("Book-01", "Book-02"),
            chapters_per_division=2,
            words_per_chapter=150,
        )

        self.assertTrue((ms_dir / "manuscript.yaml").is_file())
        for vol in ("Book-01", "Book-02"):
            vol_path = ms_dir / vol
            self.assertTrue(vol_path.is_dir())
            self.assertTrue((vol_path / "01_Ki-Introduction").is_dir())
            self.assertTrue((vol_path / "02_Sho-Development").is_dir())
            self.assertTrue((vol_path / "03_Ten-Twist").is_dir())
            self.assertTrue((vol_path / "04_Ketsu-Reconciliation").is_dir())
            self.assertTrue((vol_path / "01_Ki-Introduction" / "01_Chapter_01.md").is_file())
            self.assertTrue((vol_path / "01_Ki-Introduction" / "02_Chapter_02.md").is_file())

    def test_create_test_volume_helper(self):
        """Verify create_test_volume scaffolds discrete volume."""
        ms_dir = self.root / "SingleVolMs"
        ms_dir.mkdir(parents=True, exist_ok=True)
        vol_path = create_test_volume(
            ms_dir=ms_dir,
            vol_name="Book-01",
            structure="three_act",
            chapters_per_division=1,
            words_per_chapter=50,
        )
        self.assertTrue((vol_path / "01_Act_I" / "01_Chapter_01.md").is_file())
        self.assertTrue((vol_path / "02_Act_II" / "01_Chapter_01.md").is_file())
        self.assertTrue((vol_path / "03_Act_III" / "01_Chapter_01.md").is_file())
        self.assertTrue((vol_path / "04_Back_Matter").is_dir())

    def test_integration_scaffold_then_analyze(self):
        """Verify scaffolding a preset and scanning with structure.py analysis."""
        ms_dir = create_test_manuscript(
            self.root,
            name="HeroNovel",
            structure="heros_journey",
            volumes=("Book-01",),
            chapters_per_division=4,
            words_per_chapter=200,
        )
        vol_path = ms_dir / "Book-01"

        paradigm = get_paradigm_key("heros_journey")
        self.assertIsNotNone(paradigm)
        report = scan_manuscript_structure(vol_path, paradigm_key=paradigm)  # type: ignore[arg-type]

        self.assertEqual(report["total_chapters"], 12)  # 3 divisions * 4 chapters
        self.assertGreater(report["total_words"], 2000)
        self.assertEqual(report["paradigm_key"], "heros_journey")
        self.assertEqual(len(report["beats"]), 12)

    def test_cli_scaffold_subcommand(self):
        """Verify CLI scaffold subcommand execution."""
        vol_dir = self.root / "CliVol"
        rc = main(["scaffold", str(vol_dir), "--structure", "story_circle"])
        self.assertEqual(rc, 0)
        self.assertTrue((vol_dir / "01_Comfort_Zone").is_dir())
        self.assertTrue((vol_dir / "04_Transformation").is_dir())

    def test_cli_scaffold_custom_subcommand(self):
        """Verify CLI custom division scaffolding."""
        vol_dir = self.root / "CliCustomVol"
        rc = main(["scaffold", str(vol_dir), "--structure", "custom", "--divisions", "Intro,Body,Outro"])
        self.assertEqual(rc, 0)
        self.assertTrue((vol_dir / "01_Intro").is_dir())
        self.assertTrue((vol_dir / "02_Body").is_dir())
        self.assertTrue((vol_dir / "03_Outro").is_dir())

    def test_cli_list_subcommand(self):
        """Verify CLI list subcommand and JSON output."""
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            rc = main(["list"])
            self.assertEqual(rc, 0)
            self.assertIn("Ars Arcanum — Manuscript Structure Presets", mock_out.getvalue())

        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            rc = main(["list", "--json"])
            self.assertEqual(rc, 0)
            data = json.loads(mock_out.getvalue())
            self.assertEqual(len(data), len(STRUCTURE_PRESETS))
            self.assertIn("three_act", data)

    def test_cli_info_subcommand(self):
        """Verify CLI info subcommand displays preset details."""
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            rc = main(["info", "kishotenketsu"])
            self.assertEqual(rc, 0)
            val = mock_out.getvalue()
            self.assertIn("Kishōtenketsu", val)
            self.assertIn("Ki-Introduction", val)
            self.assertIn("Ten-Twist", val)

    def test_cli_scaffold_error_handling(self):
        """Verify CLI returns error code on invalid scaffold parameters."""
        vol_dir = self.root / "ErrorVol"
        with patch("sys.stderr", new_callable=io.StringIO) as mock_err:
            rc = main(["scaffold", str(vol_dir), "--structure", "invalid_preset_xyz"])
            self.assertEqual(rc, 1)
            self.assertIn("Error:", mock_err.getvalue())

    def test_cli_empty_args_shows_help(self):
        """Verify CLI with no arguments shows help and exits cleanly."""
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            rc = main([])
            self.assertEqual(rc, 0)
            self.assertIn("usage:", mock_out.getvalue())


if __name__ == "__main__":
    unittest.main()
