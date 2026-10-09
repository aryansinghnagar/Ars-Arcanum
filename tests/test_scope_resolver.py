#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Scope & Context Resolver (scripts/lib/scope_resolver.py)
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.scope_models import EngineScope
from lib.scope_resolver import (
    get_active_manuscript,
    get_active_world,
    get_active_universe,
    resolve_manuscript_path,
    resolve_world_path,
    resolve_universe_path,
    resolve_manuscript_dir,
    resolve_world_dir,
    resolve_universe_dir,
)


class TestScopeResolver(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

        # Setup mock home directory structure
        self.home = self.root / "fake_home"
        self.home.mkdir()
        self.ms_root = self.home / "Manuscripts"
        self.ms_root.mkdir()
        self.univ_root = self.home / "Universes"
        self.univ_root.mkdir()
        self.worlds_root = self.home / "Worlds"
        self.worlds_root.mkdir()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_get_active_manuscript_from_home_single(self):
        ms1 = self.ms_root / "BookOne"
        ms1.mkdir()
        with patch("pathlib.Path.home", return_value=self.home):
            p = get_active_manuscript()
            self.assertEqual(p, ms1)

    def test_get_active_manuscript_from_config(self):
        ms1 = self.ms_root / "ConfiguredBook"
        ms1.mkdir()
        with patch("pathlib.Path.home", return_value=self.home), \
             patch("lib.config.load_config", return_value={"active_manuscript": "ConfiguredBook"}):
            p = get_active_manuscript()
            self.assertEqual(p, ms1)

    def test_get_active_world_from_home(self):
        univ = self.univ_root / "CosmosA" / "WorldOne"
        univ.mkdir(parents=True)
        with patch("pathlib.Path.home", return_value=self.home):
            p = get_active_world()
            self.assertEqual(p, univ)

    def test_get_active_universe_from_home(self):
        univ = self.univ_root / "CosmosA"
        univ.mkdir(parents=True)
        with patch("pathlib.Path.home", return_value=self.home):
            p = get_active_universe()
            self.assertEqual(p, univ)

    def test_resolve_manuscript_path_and_dir(self):
        ms1 = self.ms_root / "EpicFantasy"
        ms1.mkdir()
        with patch("pathlib.Path.home", return_value=self.home):
            # Exact match
            p = resolve_manuscript_path("EpicFantasy")
            self.assertEqual(p, ms1)
            self.assertEqual(resolve_manuscript_dir("EpicFantasy"), str(ms1))

            # Fuzzy match
            p_fuzzy = resolve_manuscript_path("fantasy")
            self.assertEqual(p_fuzzy, ms1)

            # Via scope object
            scope = EngineScope(manuscript="EpicFantasy")
            self.assertEqual(resolve_manuscript_path(scope=scope), ms1)

            # Non-existent
            self.assertIsNone(resolve_manuscript_path("NonExistent"))
            self.assertEqual(resolve_manuscript_dir("NonExistent"), "")

    def test_resolve_world_path_and_dir(self):
        w1 = self.worlds_root / "Aethelgard"
        w1.mkdir()
        with patch("pathlib.Path.home", return_value=self.home):
            p = resolve_world_path("Aethelgard")
            self.assertEqual(p, w1)
            self.assertEqual(resolve_world_dir("Aethelgard"), str(w1))

            scope = EngineScope(world="Aethelgard")
            self.assertEqual(resolve_world_path(scope=scope), w1)

            self.assertIsNone(resolve_world_path("UnknownWorld"))
            self.assertEqual(resolve_world_dir("UnknownWorld"), "")

    def test_resolve_universe_path_and_dir(self):
        u1 = self.univ_root / "ArcanumVerse"
        u1.mkdir()
        with patch("pathlib.Path.home", return_value=self.home):
            p = resolve_universe_path("ArcanumVerse")
            self.assertEqual(p, u1)
            self.assertEqual(resolve_universe_dir("ArcanumVerse"), str(u1))

            scope = EngineScope(universe="ArcanumVerse")
            self.assertEqual(resolve_universe_path(scope=scope), u1)

            self.assertIsNone(resolve_universe_path("UnknownVerse"))
            self.assertEqual(resolve_universe_dir("UnknownVerse"), "")

    def test_resolve_from_cwd(self):
        ms_local = self.root / "LocalMS"
        ms_local.mkdir()
        (ms_local / "manuscript.yaml").write_text("title: Local\n", encoding="utf-8")

        with patch("pathlib.Path.cwd", return_value=ms_local):
            self.assertEqual(get_active_manuscript(), ms_local)

        w_local = self.root / "LocalWorld"
        w_local.mkdir()
        (w_local / "world.yaml").write_text("name: LocalWorld\n", encoding="utf-8")

        with patch("pathlib.Path.cwd", return_value=w_local):
            self.assertEqual(get_active_world(), w_local)

        u_local = self.root / "LocalUniverse"
        u_local.mkdir()
        (u_local / "universe.yaml").write_text("name: LocalUniverse\n", encoding="utf-8")

        with patch("pathlib.Path.cwd", return_value=u_local):
            self.assertEqual(get_active_universe(), u_local)


if __name__ == "__main__":
    unittest.main()
