#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Modular Front & Back Matter Builder (scripts/lib/frontmatter_builder.py).
Validates:
- PUB-103: Standard front matter (Half-Title, Title, Copyright, Dedication, Epigraph).
- Standard back matter (Acknowledgments, About Author, Also By, Reading Group Questions, CTA).
- Scaffolding to manuscript directory with force overwrite and skip behaviors.
- CLI argument parsing, custom flags, manifest loading, and JSON output mode.
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

from lib.frontmatter_builder import (
    generate_frontmatter_modules,
    generate_backmatter_modules,
    scaffold_matter,
    main,
)


class TestFrontmatterBuilder(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.target_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_frontmatter_generation(self):
        meta = {
            "title": "The Starborn Gate",
            "subtitle": "Chronicles of the Void",
            "author": "Valen Vance",
            "publisher": "Aether Press",
            "copyright_year": "2026",
            "isbn": "978-1-234567-89-0",
            "edition": "Special Illustrated Edition",
            "dedication": "To the navigators.",
            "epigraph": "Look up at the stars.",
            "epigraph_author": "The Navigator",
        }
        modules = generate_frontmatter_modules(meta)
        self.assertIn("01_Half_Title.md", modules)
        self.assertIn("02_Title_Page.md", modules)
        self.assertIn("03_Copyright.md", modules)
        self.assertIn("04_Dedication.md", modules)
        self.assertIn("05_Epigraph.md", modules)

        self.assertIn("The Starborn Gate", modules["01_Half_Title.md"])
        self.assertIn("### Chronicles of the Void", modules["02_Title_Page.md"])
        self.assertIn("Copyright © 2026", modules["03_Copyright.md"])
        self.assertIn("Special Illustrated Edition", modules["03_Copyright.md"])
        self.assertIn("To the navigators.", modules["04_Dedication.md"])
        self.assertIn("The Navigator", modules["05_Epigraph.md"])

    def test_backmatter_generation(self):
        meta = {
            "title": "The Starborn Gate",
            "author": "Valen Vance",
            "newsletter_url": "https://valenvance.com/join",
            "website_url": "https://valenvance.com",
        }
        modules = generate_backmatter_modules(meta)
        self.assertIn("01_Acknowledgments.md", modules)
        self.assertIn("02_About_the_Author.md", modules)
        self.assertIn("03_Also_By.md", modules)
        self.assertIn("04_Discussion_Questions.md", modules)
        self.assertIn("05_Reader_CTA.md", modules)

        self.assertIn("Valen Vance", modules["02_About_the_Author.md"])
        self.assertIn("https://valenvance.com/join", modules["05_Reader_CTA.md"])

    def test_scaffold_matter_skip_and_force(self):
        meta = {"title": "The Starborn Gate", "author": "Valen Vance"}

        # Initial scaffold
        res1 = scaffold_matter(self.target_dir, meta, force=False)
        self.assertEqual(res1["created_count"], 10)
        self.assertEqual(res1["skipped_count"], 0)

        # Second scaffold without force (should skip all 10)
        res2 = scaffold_matter(self.target_dir, meta, force=False)
        self.assertEqual(res2["created_count"], 0)
        self.assertEqual(res2["skipped_count"], 10)

        # Third scaffold with force (should rewrite all 10)
        res3 = scaffold_matter(self.target_dir, meta, force=True)
        self.assertEqual(res3["created_count"], 10)
        self.assertEqual(res3["skipped_count"], 0)

    def test_cli_main_build_command(self):
        (self.target_dir / "manuscript.yaml").write_text("title: Manifest Title\nauthor: Manifest Author\n", encoding="utf-8")

        # Test CLI build with arguments
        test_args = [
            "frontmatter_builder.py",
            "build",
            str(self.target_dir),
            "--title", "Override Title",
            "--author", "Override Author",
            "--isbn", "978-0-123456-78-9",
            "--year", "2030",
            "--publisher", "Custom Press",
            "-f",
        ]
        with patch.object(sys, "argv", test_args), patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            main()
            out = mock_stdout.getvalue()
            self.assertIn("Modular Front & Back Matter Scaffolder", out)
            self.assertIn("Created: 10 files", out)

        # Test JSON CLI output
        test_args_json = [
            "frontmatter_builder.py",
            "build",
            str(self.target_dir),
            "--json",
        ]
        with patch.object(sys, "argv", test_args_json):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                main()
                out = mock_stdout.getvalue()
                data = json.loads(out)
                self.assertEqual(data["created_count"], 0)
                self.assertEqual(data["skipped_count"], 10)

    def test_cli_main_invalid_args_and_missing_target(self):
        # Missing command
        with patch.object(sys, "argv", ["frontmatter_builder.py"]):
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 0)

        # Target does not exist
        fake_path = self.target_dir / "does_not_exist"
        with patch.object(sys, "argv", ["frontmatter_builder.py", "build", str(fake_path)]):
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
