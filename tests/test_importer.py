#!/usr/bin/env python3
"""
Unit tests for the Manuscript Importer Engine (tests/test_importer.py).
"""

import io
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).parent.parent
LIB_DIR = REPO_ROOT / "scripts" / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

from importer import extract_docx_text, import_manuscript_batch, main


class TestManuscriptImporter(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.work_path = Path(self.tmp_dir.name)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_extract_docx_text(self):
        docx_file = self.work_path / "sample.docx"
        doc_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading 1"/></w:pPr>
      <w:r><w:t>The Beginning</w:t></w:r>
    </w:p>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading 2"/></w:pPr>
      <w:r><w:t>Act One</w:t></w:r>
    </w:p>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading 3"/></w:pPr>
      <w:r><w:t>Scene Alpha</w:t></w:r>
    </w:p>
    <w:p>
      <w:r><w:t>The cold wind howled across the plains.</w:t></w:r>
    </w:p>
    <w:p>
    </w:p>
  </w:body>
</w:document>"""
        with zipfile.ZipFile(docx_file, "w") as zf:
            zf.writestr("word/document.xml", doc_xml)

        text = extract_docx_text(docx_file)
        self.assertIn("# The Beginning", text)
        self.assertIn("## Act One", text)
        self.assertIn("### Scene Alpha", text)
        self.assertIn("The cold wind howled across the plains.", text)

    def test_extract_docx_text_errors(self):
        not_zip = self.work_path / "fake.docx"
        not_zip.write_text("not a zip file", encoding="utf-8")
        with self.assertRaises(ValueError):
            extract_docx_text(not_zip)

        missing_xml = self.work_path / "missing_xml.docx"
        with zipfile.ZipFile(missing_xml, "w") as zf:
            zf.writestr("something_else.xml", "<root/>")
        with self.assertRaises(ValueError):
            extract_docx_text(missing_xml)

        unsafe_xml = self.work_path / "unsafe.docx"
        with zipfile.ZipFile(unsafe_xml, "w") as zf:
            zf.writestr("word/document.xml", "<!DOCTYPE doc [ <!ENTITY xxe SYSTEM 'test'> ]><w:document></w:document>")
        with self.assertRaises(ValueError):
            extract_docx_text(unsafe_xml)

    def test_import_manuscript_batch_from_md_folder(self):
        source_dir = self.work_path / "scrivener_export"
        source_dir.mkdir()
        (source_dir / "01_Prologue.md").write_text("Long ago in the first age.", encoding="utf-8")
        (source_dir / "02_The_Call.md").write_text("# Chapter 2\n\nA hero stood by the gate.", encoding="utf-8")

        dest_dir = self.work_path / "Target_Manuscript"
        res = import_manuscript_batch(
            source_dir,
            dest_dir,
            title="The Chronicles of Eldoria",
            author="Test Author",
        )

        self.assertEqual(res["chapters_imported"], 2)
        self.assertTrue((dest_dir / "manuscript.yaml").is_file())
        self.assertTrue((dest_dir / "nwProject.nwx").is_file())
        self.assertTrue((dest_dir / ".gitignore").is_file())
        self.assertTrue((dest_dir / "Book-01" / "Draft-01" / "01_Prologue.md").is_file())
        self.assertTrue((dest_dir / "Book-01" / "Draft-01" / "02_The_Call.md").is_file())

        yaml_content = (dest_dir / "manuscript.yaml").read_text(encoding="utf-8")
        self.assertIn('title: "The Chronicles of Eldoria"', yaml_content)
        self.assertIn('author: "Test Author"', yaml_content)

    def test_import_manuscript_batch_single_file_and_errors(self):
        # Nonexistent path
        with self.assertRaises(FileNotFoundError):
            import_manuscript_batch(self.work_path / "nonexistent", self.work_path / "dest")

        # Empty folder
        empty_dir = self.work_path / "empty_src"
        empty_dir.mkdir()
        with self.assertRaises(ValueError):
            import_manuscript_batch(empty_dir, self.work_path / "dest_empty")

        # Single file import
        single_doc = self.work_path / "01_Solo.md"
        single_doc.write_text("Solo text content.", encoding="utf-8")
        dest_solo = self.work_path / "dest_solo"
        res = import_manuscript_batch(single_doc, dest_solo, title="Solo Manuscript")
        self.assertEqual(res["chapters_imported"], 1)

    def test_import_manuscript_preserves_frontmatter_at_line_zero(self):
        source_dir = self.work_path / "frontmatter_src"
        source_dir.mkdir()
        doc_content = "---\ntitle: \"Existing Note\"\npov: \"Kaelen\"\n---\n\nProse begins here without header."
        (source_dir / "01_Story.md").write_text(doc_content, encoding="utf-8")

        dest_dir = self.work_path / "Target_FM_Manuscript"
        res = import_manuscript_batch(source_dir, dest_dir, title="FM Book")
        self.assertEqual(res["chapters_imported"], 1)

        target_file = dest_dir / "Book-01" / "Draft-01" / "01_Story.md"
        result_text = target_file.read_text(encoding="utf-8")
        self.assertTrue(result_text.startswith("---\n"))
        self.assertIn("# Chapter 1: Story", result_text)
        # Ensure frontmatter is at line 0 before the header
        lines = result_text.splitlines()
        self.assertEqual(lines[0], "---")
        self.assertEqual(lines[1], 'title: "Existing Note"')
        self.assertEqual(lines[2], 'pov: "Kaelen"')
        self.assertEqual(lines[3], "---")
        self.assertEqual(lines[4], "")
        self.assertEqual(lines[5], "# Chapter 1: Story")

    def test_extract_docx_track_changes_and_formatting(self):
        docx_file = self.work_path / "formatted.docx"
        doc_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:r><w:rPr><w:b/></w:rPr><w:t>Bold Text</w:t></w:r>
      <w:r><w:t> </w:t></w:r>
      <w:r><w:rPr><w:i/></w:rPr><w:t>Italic Text</w:t></w:r>
      <w:del><w:r><w:t> Deleted Text</w:t></w:r></w:del>
    </w:p>
  </w:body>
</w:document>"""
        with zipfile.ZipFile(docx_file, "w") as zf:
            zf.writestr("word/document.xml", doc_xml)

        text = extract_docx_text(docx_file)
        self.assertIn("**Bold Text**", text)
        self.assertIn("*Italic Text*", text)
        self.assertNotIn("Deleted Text", text)

    def test_cli_main(self):
        source_dir = self.work_path / "cli_src"
        source_dir.mkdir()
        (source_dir / "01_Ch1.md").write_text("# Chapter 1\nContent.", encoding="utf-8")
        dest_dir = self.work_path / "cli_dest"

        # Successful CLI run
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            code = main([str(source_dir), "--dest", str(dest_dir), "--title", "CLI Book", "--author", "Tester"])
            self.assertEqual(code, 0)
            self.assertIn("Successfully imported manuscript 'CLI Book'", mock_out.getvalue())

        # Error CLI run
        with patch("sys.stderr", new_callable=io.StringIO) as mock_err:
            code_err = main([str(self.work_path / "nonexistent_source")])
            self.assertEqual(code_err, 1)
            self.assertIn("Error importing manuscript", mock_err.getvalue())


if __name__ == "__main__":
    unittest.main()
