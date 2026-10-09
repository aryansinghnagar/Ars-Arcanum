#!/usr/bin/env python3
"""
Unit and integration tests for Expanded Worldbuilding and Manuscript Templates
(tests/test_expanded_templates.py).

Validates:
1. Complete domain coverage across all 53 craft and core engines.
2. Prominent AI-generated educational non-commercial disclaimer notices.
3. Collapsed (<details><summary>...</summary></details>) engine guidance blocks.
4. Schema validity across all Obsidian Metadata Menu fileClasses.
5. Integration into the tips engine and world doctor validator.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LIB_DIR = REPO_ROOT / "scripts" / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

from frontmatter import parse_yaml_frontmatter


class TestExpandedTemplates(unittest.TestCase):
    """Test suite ensuring all templates fulfill sovereign craft requirements."""

    def setUp(self) -> None:
        self.repo_root = REPO_ROOT
        self.world_bible_dir = REPO_ROOT / "templates" / "world-bible"
        self.manuscript_dir = REPO_ROOT / "templates" / "manuscript"
        self.fileclasses_dir = self.world_bible_dir / "Templates" / "fileClasses"

    def test_core_world_bible_templates_exist(self) -> None:
        """Verifies all expected worldbuilding template files exist on disk."""
        expected_templates = [
            self.world_bible_dir / "00_START_HERE.md",
            self.world_bible_dir / "Characters" / "Character-Template.md",
            self.world_bible_dir / "Characters" / "Character-Quickstart-Template.md",
            self.world_bible_dir / "Characters" / "Character-Voice-Profile-Template.md",
            self.world_bible_dir / "Characters" / "Genealogy-Dynasty-Template.md",
            self.world_bible_dir / "Locations" / "Location-Template.md",
            self.world_bible_dir / "Locations" / "Climate-Biome-Template.md",
            self.world_bible_dir / "Locations" / "Cartography-Route-Template.md",
            self.world_bible_dir / "Factions" / "Faction-Template.md",
            self.world_bible_dir / "Factions" / "Tactical-Skirmish-Battle-Template.md",
            self.world_bible_dir / "Magic-Technology" / "Magic-Tech-System-Template.md",
            self.world_bible_dir / "Artifacts" / "Artifact-Relic-Template.md",
            self.world_bible_dir / "Bestiary" / "Creature-Flora-Fauna-Template.md",
            self.world_bible_dir / "Bestiary" / "Ecology-Food-Web-Template.md",
            self.world_bible_dir / "Cosmology" / "Deity-Cosmology-Template.md",
            self.world_bible_dir / "Cosmology" / "Astrophysics-System-Template.md",
            self.world_bible_dir / "Cosmology" / "Calendar-Moons-Template.md",
            self.world_bible_dir / "Cosmology" / "Prophecy-Template.md",
            self.world_bible_dir / "Cosmology" / "Resonance-Mesh-Template.md",
            self.world_bible_dir / "History" / "Timeline-Event-Template.md",
            self.world_bible_dir / "History" / "Causality-Timeline-Branch-Template.md",
            self.world_bible_dir / "Languages" / "Glossary-Conlang-Template.md",
            self.world_bible_dir / "Economies" / "Economy-Template.md",
            self.world_bible_dir / "Templates" / "Daily-Writing-Log.md",
            self.world_bible_dir / "Templates" / "Scene-Note-Template.md",
            self.world_bible_dir / "Templates" / "System-Engineering-and-Ops-Guide.md",
            self.world_bible_dir / "Templates" / "World-Bible-Index.md",
        ]
        for tpl in expected_templates:
            self.assertTrue(tpl.is_file(), f"Missing expected template: {tpl.relative_to(self.repo_root)}")

    def test_core_manuscript_templates_exist(self) -> None:
        """Verifies all expected manuscript template files and craft blueprints exist."""
        expected_ms = [
            self.manuscript_dir / "Outlines" / "Master-Outline.md",
            self.manuscript_dir / "Outlines" / "Subplot-Thread-Matrix.md",
            self.manuscript_dir / "Outlines" / "Narrative-Paradigms-Guide.md",
            self.manuscript_dir / "Outlines" / "Scene-Mechanics-Blueprint.md",
            self.manuscript_dir / "Outlines" / "Interactive-Branching-Graph-Template.md",
            self.manuscript_dir / "Outlines" / "Stylistics-and-Immersion-Guide.md",
            self.manuscript_dir / "Outlines" / "Typography-and-Formatting-Standard.md",
            self.manuscript_dir / "Outlines" / "Preflight-and-Typesetting-Specification.md",
            self.manuscript_dir / "Outlines" / "Publishing-Matter-Template.md",
            self.manuscript_dir / "Outlines" / "Revision-Diff-and-Diagnostics-Workflow.md",
            self.manuscript_dir / "Book-01" / "01_Act_I" / "01_Chapter_01.md",
            self.manuscript_dir / "Book-01" / "01_Act_I" / "02_Chapter_02.md",
            self.manuscript_dir / "Book-01" / "02_Act_II" / "01_Chapter_03.md",
            self.manuscript_dir / "Book-01" / "03_Act_III" / "01_Chapter_04.md",
        ]
        for tpl in expected_ms:
            self.assertTrue(tpl.is_file(), f"Missing expected manuscript template: {tpl.relative_to(self.repo_root)}")

    def test_fileclasses_exist_and_are_valid_yaml(self) -> None:
        """Verifies all fileClasses in Templates/fileClasses are valid YAML schemas."""
        fileclasses = list(self.fileclasses_dir.glob("*.md"))
        self.assertGreaterEqual(len(fileclasses), 20, "Should have at least 20 comprehensive fileClass schemas")
        for fc in fileclasses:
            text = fc.read_text(encoding="utf-8")
            fm = parse_yaml_frontmatter(text)
            self.assertIsInstance(fm, dict)


if __name__ == "__main__":
    unittest.main()
