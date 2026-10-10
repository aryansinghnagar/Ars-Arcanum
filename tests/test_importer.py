#!/usr/bin/env python3
"""
Unit tests for the Manuscript Importer Engine & Visual Migration Studio (tests/test_importer.py).
"""

import io
import json
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

from importer import (
    EpubImporter,
    convert_html_to_markdown,
    extract_docx_text,
    import_manuscript_batch,
    main,
    resolve_sequential_draft,
    rtf_to_text,
    split_monolithic_by_headings,
)
from importer_template import render_import_studio_html


class TestManuscriptImporter(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.work_path = Path(self.tmp_dir.name)

    def tearDown(self):
        self.tmp_dir.cleanup()

    # --------------------------------------------------------------------------
    # 1. Pure Python HTML to Markdown & RTF Parsing Tests
    # --------------------------------------------------------------------------

    def test_html_to_markdown_converter(self):
        raw_html = """
        <html>
        <head><title>Test Title</title><style>body { color: red; }</style></head>
        <body>
            <h1>Chapter 1: The Gathering</h1>
            <p>It was a <strong>dark</strong> and <em>stormy</em> night.</p>
            <blockquote>"Speak, friend, and enter."</blockquote>
            <hr/>
            <ul>
                <li>Sword</li>
                <li>Shield</li>
            </ul>
            <pre>code block</pre>
            <p>Inline `code` and entities &amp; &lt; &gt; &#160; text.</p>
        </body>
        </html>
        """
        md = convert_html_to_markdown(raw_html)
        self.assertIn("# Chapter 1: The Gathering", md)
        self.assertIn("**dark**", md)
        self.assertIn("*stormy*", md)
        self.assertIn("> \"Speak, friend, and enter.\"", md)
        self.assertIn("***", md)
        self.assertIn("- Sword", md)
        self.assertIn("- Shield", md)
        self.assertIn("```\ncode block\n```", md)
        self.assertNotIn("<style>", md)
        self.assertNotIn("body { color: red; }", md)

    def test_rtf_to_text(self):
        raw_rtf = (
            r"{\rtf1\ansi\ansicpg1252\deff0\nouicompat\deflang1033"
            r"{\fonttbl{\f0\fnil\fcharset0 Calibri;}}"
            r"{\colortbl ;\red0\green0\blue0;}"
            r"\viewkind4\uc1 "
            r"\pard\sa200\sl276\slmult1\b\f0\fs22 Chapter One\b0\par"
            r"The ancient dragon \i slept\i0  peacefully.\par"
            r"Unicode test: \u8212? em-dash and \'a9 copyright.\par}"
        )
        text = rtf_to_text(raw_rtf)
        self.assertIn("Chapter One", text)
        self.assertIn("The ancient dragon", text)
        self.assertIn("slept", text)
        self.assertIn("—", text)  # \u8212 is em-dash
        self.assertIn("©", text)  # \'a9 is copyright sign
        self.assertNotIn(r"\fonttbl", text)
        self.assertNotIn(r"\colortbl", text)

    # --------------------------------------------------------------------------
    # 2. Strict Heading Splitting Tests
    # --------------------------------------------------------------------------

    def test_split_monolithic_by_headings(self):
        content = """Introductory poem before the journey starts.

# Chapter 1: The Departure
The ship set sail at dawn.

# Chapter 2: The Open Sea
Waves crashed against the hull.
"""
        chapters = split_monolithic_by_headings(content, default_title="Book")
        self.assertEqual(len(chapters), 3)
        self.assertEqual(chapters[0]["title"], "Prologue")
        self.assertIn("Introductory poem", chapters[0]["content"])

        self.assertEqual(chapters[1]["title"], "Chapter 1: The Departure")
        self.assertIn("The ship set sail at dawn.", chapters[1]["content"])

        self.assertEqual(chapters[2]["title"], "Chapter 2: The Open Sea")
        self.assertIn("Waves crashed against the hull.", chapters[2]["content"])

    def test_split_monolithic_fallback_when_no_headings(self):
        content = "This is a single continuous prose piece without any heading tags at all."
        chapters = split_monolithic_by_headings(content, default_title="Single_Draft")
        self.assertEqual(len(chapters), 1)
        self.assertEqual(chapters[0]["title"], "Single_Draft")
        self.assertEqual(chapters[0]["content"], content)

    # --------------------------------------------------------------------------
    # 3. EPUB Ingestion Engine Tests
    # --------------------------------------------------------------------------

    def test_epub_importer(self):
        epub_file = self.work_path / "test_book.epub"
        with zipfile.ZipFile(epub_file, "w") as zf:
            container_xml = """<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>"""
            zf.writestr("META-INF/container.xml", container_xml)

            opf_xml = """<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="pub-id">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:title>Eldoria Rising</dc:title>
    <dc:creator>Brandon Sanderson</dc:creator>
  </metadata>
  <manifest>
    <item id="ch1" href="ch01.xhtml" media-type="application/xhtml+xml"/>
    <item id="ch2" href="ch02.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine>
    <itemref idref="ch1"/>
    <itemref idref="ch2"/>
  </spine>
</package>"""
            zf.writestr("OEBPS/content.opf", opf_xml)

            ch1_html = "<html><body><h1>Prologue: The Fall</h1><p>The city burned.</p></body></html>"
            ch2_html = "<html><body><h1>Chapter 1: The Ashes</h1><p>Kael walked through the ruins.</p></body></html>"
            zf.writestr("OEBPS/ch01.xhtml", ch1_html)
            zf.writestr("OEBPS/ch02.xhtml", ch2_html)

        importer = EpubImporter(epub_file)
        res = importer.parse()
        self.assertEqual(res["title"], "Eldoria Rising")
        self.assertEqual(res["author"], "Brandon Sanderson")
        self.assertEqual(len(res["chapters"]), 2)
        self.assertIn("Prologue: The Fall", res["chapters"][0]["title"])
        self.assertIn("The city burned.", res["chapters"][0]["content"])

    # --------------------------------------------------------------------------
    # 4. Scrivener Ingestion & Dual-Vault Routing Tests
    # --------------------------------------------------------------------------

    def test_scrivener_importer(self):
        scriv_dir = self.work_path / "MyNovel.scriv"
        scriv_dir.mkdir()
        (scriv_dir / "Files" / "Data" / "101").mkdir(parents=True)
        (scriv_dir / "Files" / "Data" / "201").mkdir(parents=True)
        (scriv_dir / "Files" / "Data" / "301").mkdir(parents=True)

        scrivx_xml = """<?xml version="1.0" encoding="utf-8"?>
<ScrivenerProject Version="2.0">
  <ProjectTitle>The Silver Citadel</ProjectTitle>
  <Binder>
    <BinderItem ID="100" Type="DraftFolder">
      <Title>Manuscript</Title>
      <Children>
        <BinderItem ID="101" Type="Text">
          <Title>The Awakening</Title>
          <MetaData><Synopsis>Hero discovers magic sword in the crypt.</Synopsis></MetaData>
        </BinderItem>
      </Children>
    </BinderItem>
    <BinderItem ID="200" Type="Folder">
      <Title>Characters</Title>
      <Children>
        <BinderItem ID="201" Type="Text">
          <Title>Elandra Swift</Title>
          <MetaData><Synopsis>Lead ranger and archer.</Synopsis></MetaData>
        </BinderItem>
      </Children>
    </BinderItem>
    <BinderItem ID="300" Type="Folder">
      <Title>Places</Title>
      <Children>
        <BinderItem ID="301" Type="Text">
          <Title>Oakhaven Fortress</Title>
          <MetaData><Synopsis>Northern bastion guarding the river.</Synopsis></MetaData>
        </BinderItem>
      </Children>
    </BinderItem>
  </Binder>
</ScrivenerProject>"""
        (scriv_dir / "project.scrivx").write_text(scrivx_xml, encoding="utf-8")

        (scriv_dir / "Files" / "Data" / "101" / "content.txt").write_text("Light pierced the stained glass window.", encoding="utf-8")
        (scriv_dir / "Files" / "Data" / "201" / "content.txt").write_text("Born in the high canopy of the Greenwood.", encoding="utf-8")
        (scriv_dir / "Files" / "Data" / "301" / "content.txt").write_text("Constructed during the Third Dynasty of Stone.", encoding="utf-8")

        dest_dir = self.work_path / "Target_Scriv_Manuscript"
        res = import_manuscript_batch(
            scriv_dir,
            dest_dir,
            universe="Aethelgard",
            world="Eldoria",
        )

        self.assertEqual(res["title"], "The Silver Citadel")
        self.assertEqual(res["chapters_imported"], 1)
        self.assertEqual(len(res["lore_entities"]), 2)

        # Check Manuscript Chapter
        chap_file = dest_dir / "Book-01" / "Draft-01" / "01_The_Awakening.md"
        self.assertTrue(chap_file.is_file())
        chap_text = chap_file.read_text(encoding="utf-8")
        self.assertIn("synopsis: Hero discovers magic sword in the crypt.", chap_text)
        self.assertIn("# Chapter 1: The Awakening", chap_text)
        self.assertIn("Light pierced the stained glass window.", chap_text)

        # Check World Lore Dossiers
        world_dir = dest_dir.parent / "World"
        char_file = world_dir / "Characters" / "Elandra_Swift.md"
        loc_file = world_dir / "Locations" / "Oakhaven_Fortress.md"
        self.assertTrue(char_file.is_file())
        self.assertTrue(loc_file.is_file())

        char_text = char_file.read_text(encoding="utf-8")
        self.assertIn("name: Elandra Swift", char_text)
        self.assertIn("Born in the high canopy", char_text)

    # --------------------------------------------------------------------------
    # 5. Collision Avoidance & Draft Resolution Tests
    # --------------------------------------------------------------------------

    def test_resolve_sequential_draft(self):
        vault = self.work_path / "Vault_Test"
        book_dir = vault / "Book-01"
        book_dir.mkdir(parents=True)
        (book_dir / "Draft-01").mkdir()
        (book_dir / "Draft-02").mkdir()

        next_d = resolve_sequential_draft(vault, "Book-01", "Draft-01")
        self.assertEqual(next_d, "Draft-03")

    def test_import_manuscript_collision_increments_draft(self):
        dest_dir = self.work_path / "Collision_Vault"
        (dest_dir / "Book-01" / "Draft-01").mkdir(parents=True)
        (dest_dir / "Book-01" / "Draft-01" / "01_Old.md").write_text("Old draft content", encoding="utf-8")

        src_dir = self.work_path / "src_batch"
        src_dir.mkdir()
        (src_dir / "01_New.md").write_text("# Chapter 1\nNew draft content", encoding="utf-8")

        res = import_manuscript_batch(src_dir, dest_dir, title="My Book", overwrite=False)
        self.assertEqual(res["draft"], "Draft-02")
        self.assertTrue((dest_dir / "Book-01" / "Draft-02" / "01_New.md").is_file())
        self.assertTrue((dest_dir / "Book-01" / "Draft-01" / "01_Old.md").is_file())

    def test_import_manuscript_dry_run(self):
        dest_dir = self.work_path / "DryRun_Vault"
        src_dir = self.work_path / "src_dry"
        src_dir.mkdir()
        (src_dir / "01_Ch1.md").write_text("# Chapter 1\nContent text", encoding="utf-8")

        res = import_manuscript_batch(src_dir, dest_dir, title="Dry Book", dry_run=True)
        self.assertTrue(res["dry_run"])
        self.assertEqual(res["chapters_imported"], 1)
        self.assertFalse((dest_dir / "Book-01").exists())

    # --------------------------------------------------------------------------
    # 6. Visual Studio Template & CSP Compliance Tests
    # --------------------------------------------------------------------------

    def test_render_import_studio_html_csp_and_content(self):
        report = {
            "title": "Visual Studio Test",
            "author": "Tester",
            "source_format": "scrivener",
            "source_path": "/path/to/novel.scriv",
            "dest_path": "/path/to/vault",
            "book": "Book-01",
            "draft": "Draft-01",
            "chapters_imported": 2,
            "total_words": 5000,
            "collision_resolution": "Sequential (Non-Destructive)",
            "dry_run": False,
            "lore_entities": [
                {"name": "Valerius", "type": "character", "category": "Characters", "rel_path": "Valerius.md", "synopsis": "Knight Commander."}
            ],
            "chapters": [
                {"index": 1, "title": "The Oath", "filename": "01_The_Oath.md", "word_count": 2500, "synopsis": "Taking the vow."},
                {"index": 2, "title": "The Breach", "filename": "02_The_Breach.md", "word_count": 2500, "synopsis": "Castle falls."},
            ]
        }
        out_html = self.work_path / "test_studio.html"
        render_import_studio_html(report, out_html)

        self.assertTrue(out_html.is_file())
        content = out_html.read_text(encoding="utf-8")
        self.assertIn("Visual Studio Test", content)
        self.assertIn("The Oath", content)
        self.assertIn("Valerius", content)
        self.assertIn("<meta http-equiv=\"Content-Security-Policy\"", content)
        self.assertIn("default-src 'none'", content)

    # --------------------------------------------------------------------------
    # 7. DOCX & Existing Tests
    # --------------------------------------------------------------------------

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
      <w:r><w:t>The cold wind howled across the plains.</w:t></w:r>
    </w:p>
  </w:body>
</w:document>"""
        with zipfile.ZipFile(docx_file, "w") as zf:
            zf.writestr("word/document.xml", doc_xml)

        text = extract_docx_text(docx_file)
        self.assertIn("# The Beginning", text)
        self.assertIn("The cold wind howled across the plains.", text)

    def test_cli_main_with_json_and_dry_run(self):
        source_dir = self.work_path / "cli_src"
        source_dir.mkdir()
        (source_dir / "01_Ch1.md").write_text("# Chapter 1\nContent.", encoding="utf-8")
        dest_dir = self.work_path / "cli_dest"

        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            code = main([str(source_dir), "--dest", str(dest_dir), "--title", "CLI Book", "--json"])
            self.assertEqual(code, 0)
            data = json.loads(mock_out.getvalue())
            self.assertEqual(data["title"], "CLI Book")
            self.assertEqual(data["chapters_imported"], 1)


if __name__ == "__main__":
    unittest.main()
