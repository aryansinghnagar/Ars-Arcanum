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

from tips import get_tip_database
from world_doctor import check_world, parse_frontmatter


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

    def test_educational_disclaimer_present_in_templates(self) -> None:
        """Verifies that all templates explicitly state they are AI-generated and for educational/non-commercial use."""
        all_templates = list(self.world_bible_dir.rglob("*.md")) + list(self.manuscript_dir.rglob("*.md"))
        for tpl in all_templates:
            if "fileClasses" in tpl.parts:
                continue
            text = tpl.read_text(encoding="utf-8")
            self.assertTrue(
                "EDUCATIONAL TEMPLATE (AI-GENERATED)" in text or "educational" in text.lower(),
                f"Template {tpl.relative_to(self.repo_root)} missing educational AI notice",
            )
            self.assertTrue(
                "non-commercial" in text.lower() or "educational purposes" in text.lower(),
                f"Template {tpl.relative_to(self.repo_root)} missing non-commercial disclaimer",
            )

    def test_collapsed_engine_guidance_present_in_templates(self) -> None:
        """Verifies that templates contain collapsed <details><summary> engine guidance sections."""
        all_templates = list(self.world_bible_dir.rglob("*.md")) + list(self.manuscript_dir.rglob("*.md"))
        for tpl in all_templates:
            if "fileClasses" in tpl.parts:
                continue
            text = tpl.read_text(encoding="utf-8")
            self.assertTrue(
                "<details>" in text and "</details>" in text,
                f"Template {tpl.relative_to(self.repo_root)} missing <details> collapsed guidance",
            )
            self.assertTrue(
                "<summary>" in text and "</summary>" in text,
                f"Template {tpl.relative_to(self.repo_root)} missing <summary> tag",
            )

    def test_fileclasses_exist_and_are_valid_yaml(self) -> None:
        """Verifies all fileClasses in Templates/fileClasses are valid YAML schemas."""
        fileclasses = list(self.fileclasses_dir.glob("*.md"))
        self.assertGreaterEqual(len(fileclasses), 20, "Should have at least 20 comprehensive fileClass schemas")
        for fc in fileclasses:
            text = fc.read_text(encoding="utf-8")
            fm, ok = parse_frontmatter(text)
            self.assertTrue(ok, f"FileClass {fc.name} failed frontmatter parsing")
            self.assertIn("fileClass", fm, f"FileClass {fc.name} missing 'fileClass' attribute")

    def test_all_53_engines_demonstrated_in_templates(self) -> None:
        """Verifies all 53 registered engines are mentioned and demonstrated across the templates."""
        from registry import _ENGINES
        all_templates = list(self.world_bible_dir.rglob("*.md")) + list(self.manuscript_dir.rglob("*.md"))
        template_texts = [
            tpl.read_text(encoding="utf-8")
            for tpl in all_templates
            if "fileClasses" not in tpl.parts
        ]
        combined_text = "\n".join(template_texts)

        for name, spec in _ENGINES.items():
            found = (
                name in combined_text
                or spec.cli_command in combined_text
                or any(alias in combined_text for alias in spec.aliases)
            )
            self.assertTrue(found, f"Engine '{name}' is not demonstrated in any template.")

    def test_all_subfeatures_covered_in_templates(self) -> None:
        """Verifies 100% of all registered engine subfeatures are covered across templates."""
        from registry import _ENGINES
        all_templates = list(self.world_bible_dir.rglob("*.md")) + list(self.manuscript_dir.rglob("*.md"))
        template_texts = [
            tpl.read_text(encoding="utf-8").lower()
            for tpl in all_templates
            if "fileClasses" not in tpl.parts
        ]
        combined_text_lower = "\n".join(template_texts)

        missing = []
        for name, spec in _ENGINES.items():
            for sf in spec.subfeatures:
                sf_name = sf.get("name", "")
                if sf_name.lower() not in combined_text_lower:
                    missing.append((name, sf_name))

        self.assertEqual(len(missing), 0, f"Missing subfeatures in templates: {missing}")

    def test_tip_engine_integration_for_templates(self) -> None:
        """Verifies that the tips engine provides specialized guidance for educational templates."""
        db = get_tip_database()
        
        # Test direct query search
        results = db.search("educational templates")
        self.assertTrue(len(results) > 0, "Should find tips matching 'educational templates'")
        
        # Test domain coverage tip exists
        tip_cov = db.get_by_id("tip_templates_comprehensive_domain_coverage")
        self.assertIsNotNone(tip_cov, "Missing tip_templates_comprehensive_domain_coverage in tip DB")
        self.assertIn("53-Engine", tip_cov.title)

        # Test alias resolution
        self.assertEqual(db.resolve_engine("templates"), "manuscript_scaffold")
        self.assertEqual(db.resolve_engine("world-bible"), "world_doctor")

    def test_world_doctor_validates_templates_without_fatal_errors(self) -> None:
        """Verifies that world_doctor indexes the expanded template vault safely."""
        findings = check_world(str(self.world_bible_dir))
        self.assertEqual(len(findings["frontmatter_parse_errors"]), 0, f"FM errors: {findings['frontmatter_parse_errors']}")
        self.assertEqual(len(findings["timeline_errors"]), 0, f"Timeline errors: {findings['timeline_errors']}")


if __name__ == "__main__":
    unittest.main()
