#!/usr/bin/env python3
"""
Tests for Ars Arcanum Typesetting & Publication Pipeline (tests/test_publisher.py)
"""

from __future__ import annotations

import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from lib.project_scaffold import scaffold_manuscript, scaffold_universe, scaffold_world
from lib.publisher import (
    collect_manuscript_content,
    compile_docx,
    compile_pandoc_epub,
    compile_typst_pdf,
    get_manuscript_metadata,
    main,
    publish_manuscript,
)


class TestPublisher(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp(prefix="arcanum_test_pub_"))
        self.univ_base = self.tmp_dir / "Universes"
        self.univ_base.mkdir(parents=True, exist_ok=True)

        scaffold_universe("Starlight", base_dir=self.univ_base)
        scaffold_world("Nova", universe_name="Starlight", base_dir=self.univ_base)
        res = scaffold_manuscript(
            "Starborne",
            universe="Starlight",
            world="Nova",
            base_dir=self.univ_base,
            target_words=60000,
        )
        self.ms_dir = Path(res["path"])

    def tearDown(self):
        if self.tmp_dir.exists():
            shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_get_manuscript_metadata(self):
        meta = get_manuscript_metadata(self.ms_dir)
        self.assertEqual(meta["title"], "Starborne")
        self.assertEqual(meta["author"], "Author")
        self.assertIn("language", meta)

    def test_collect_manuscript_content(self):
        chapters, _ = collect_manuscript_content(self.ms_dir)
        self.assertGreater(len(chapters), 0)
        self.assertEqual(chapters[0]["index"], 1)
        self.assertTrue(chapters[0]["body"])

    def test_compile_docx_standard_submission(self):
        chapters, _ = collect_manuscript_content(self.ms_dir)
        meta = get_manuscript_metadata(self.ms_dir)
        out_docx = self.ms_dir / "Exports" / "TestDocx.docx"
        out_docx.parent.mkdir(parents=True, exist_ok=True)

        res_path = compile_docx(self.ms_dir, out_docx, chapters, meta)
        self.assertTrue(res_path.is_file())
        self.assertGreater(res_path.stat().st_size, 0)

    def test_compile_typst_pdf_inspect(self):
        chapters, _ = collect_manuscript_content(self.ms_dir)
        meta = get_manuscript_metadata(self.ms_dir)
        out_pdf = self.ms_dir / "Exports" / "TestPdf.pdf"

        res = compile_typst_pdf(
            self.ms_dir,
            out_pdf,
            chapters,
            meta,
            typst_bin="typst",
            inspect_only=True,
        )
        self.assertEqual(res["status"], "inspected")
        self.assertEqual(res["format"], "pdf")
        self.assertIn("typ_source_path", res)
        self.assertTrue(Path(res["typ_source_path"]).is_file())

    def test_compile_pandoc_epub_inspect(self):
        chapters, _ = collect_manuscript_content(self.ms_dir)
        meta = get_manuscript_metadata(self.ms_dir)
        out_epub = self.ms_dir / "Exports" / "TestEpub.epub"

        res = compile_pandoc_epub(
            self.ms_dir,
            out_epub,
            chapters,
            meta,
            pandoc_bin="pandoc",
            inspect_only=True,
        )
        self.assertEqual(res["status"], "inspected")
        self.assertEqual(res["format"], "epub")
        self.assertIn("md_source_path", res)
        self.assertTrue(Path(res["md_source_path"]).is_file())

    def test_publish_manuscript_inspect_all(self):
        res = publish_manuscript(self.ms_dir, output_format="all", inspect_only=True)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["manuscript"], "Starborne")
        self.assertIn("docx", res["formats"])
        self.assertIn("pdf", res["formats"])
        self.assertIn("epub", res["formats"])
        self.assertEqual(res["formats"]["docx"]["status"], "inspected")
        self.assertEqual(res["formats"]["pdf"]["status"], "inspected")
        self.assertEqual(res["formats"]["epub"]["status"], "inspected")

    def test_publish_manuscript_docx_execution(self):
        res = publish_manuscript(self.ms_dir, output_format="docx", inspect_only=False)
        self.assertEqual(res["status"], "success")
        self.assertIn("docx", res["formats"])
        self.assertEqual(res["formats"]["docx"]["status"], "success")
        docx_file = Path(res["formats"]["docx"]["output_path"])
        self.assertTrue(docx_file.is_file())

    def test_publish_manuscript_missing_tool_skips_gracefully(self):
        with patch("lib.publisher.find_tool", return_value=None):
            res = publish_manuscript(self.ms_dir, output_format="pdf", inspect_only=False)
            self.assertEqual(res["formats"]["pdf"]["status"], "skipped")
            self.assertIn("not found", res["formats"]["pdf"]["reason"])

    def test_cli_publisher(self):
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            rc = main([str(self.ms_dir), "--inspect", "--json"])
            self.assertEqual(rc, 0)
            parsed = json.loads(mock_out.getvalue())
            self.assertEqual(parsed["title"], "Starborne")
            self.assertEqual(parsed["formats"]["docx"]["status"], "inspected")

        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            rc = main([str(self.ms_dir), "--format", "docx"])
            self.assertEqual(rc, 0)
            self.assertIn("Ars Arcanum Publication Pipeline", mock_out.getvalue())
            self.assertIn("[DOCX] Generated:", mock_out.getvalue())

        # Error case: Nonexistent manuscript
        with patch("sys.stderr", new_callable=io.StringIO) as mock_err:
            rc = main([str(self.tmp_dir / "NonexistentPubMS")])
            self.assertEqual(rc, 1)
            self.assertIn("Error:", mock_err.getvalue())


if __name__ == "__main__":
    unittest.main()
