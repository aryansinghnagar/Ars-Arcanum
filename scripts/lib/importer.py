#!/usr/bin/env python3
"""
Ars Arcanum Manuscript Batch Importer & Migration Engine (scripts/lib/importer.py)
==================================================================================
Converts Scrivener projects (.scriv binder XML), Microsoft Word (.docx), EPUB ebooks,
and unstructured Markdown directories into sovereign, publication-ready Ars Arcanum
manuscript vaults with dual-vault lore routing and visual migration studios.

Zero external dependencies required (Pure Python standard library with optional Pandoc boost).
"""

from __future__ import annotations

import argparse
import html
import json
import logging
import os
import re
import sys
import xml.etree.ElementTree as ET
import xml.sax.saxutils as saxutils
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

try:
    from lib._bootstrap import atomic_write, sanitize_identifier
    from lib.docx_sync import convert_docx_to_markdown
    from lib.frontmatter import (
        extract_frontmatter_and_body,
        serialize_yaml_frontmatter,
    )
    from lib.importer_template import render_import_studio_html
    from lib.word_counter import count_words_prose
except ImportError:
    from _bootstrap import atomic_write, sanitize_identifier  # type: ignore[no-redef]
    from docx_sync import convert_docx_to_markdown  # type: ignore[no-redef]
    from frontmatter import (  # type: ignore[no-redef]
        extract_frontmatter_and_body,
        serialize_yaml_frontmatter,
    )
    from importer_template import render_import_studio_html  # type: ignore[no-redef]
    from word_counter import count_words_prose  # type: ignore[no-redef]

try:
    from lib.backup import create_backup
except ImportError:
    try:
        from backup import create_backup  # type: ignore[no-redef]
    except ImportError:
        create_backup = None  # type: ignore[assignment]

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("arcanum.importer")

NWX_TEMPLATE = """<?xml version="1.0" encoding="utf-8"?>
<novelWriterXML appVersion="2.0" fileVersion="1.5">
  <project>
    <title>{title}</title>
    <author>{author}</author>
  </project>
</novelWriterXML>
"""


# ==============================================================================
# Pure Python HTML to Markdown Converter (Zero-Pip)
# ==============================================================================

class HtmlToMarkdownConverter(HTMLParser):
    """
    Zero-dependency pure standard library HTML to Markdown converter.
    Translates headings, paragraphs, lists, bold, italics, blockquotes, and hr tags.
    """

    def __init__(self) -> None:
        super().__init__()
        self.output: list[str] = []
        self.tags_stack: list[str] = []
        self.in_pre = False
        self.in_script = False
        self.in_style = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        self.tags_stack.append(tag)

        if tag in ("script", "style", "head", "title"):
            if tag == "script":
                self.in_script = True
            elif tag == "style":
                self.in_style = True
            return

        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            level = int(tag[1])
            self.output.append("\n\n" + "#" * level + " ")
        elif tag == "p":
            self.output.append("\n\n")
        elif tag == "br":
            self.output.append("\n")
        elif tag in ("strong", "b"):
            self.output.append("**")
        elif tag in ("em", "i"):
            self.output.append("*")
        elif tag == "blockquote":
            self.output.append("\n\n> ")
        elif tag == "hr":
            self.output.append("\n\n***\n\n")
        elif tag == "li":
            self.output.append("\n- ")
        elif tag == "pre":
            self.in_pre = True
            self.output.append("\n\n```\n")
        elif tag == "code" and not self.in_pre:
            self.output.append("`")

    def handle_endtag(self, tag: str, attrs: Any = None) -> None:
        tag = tag.lower()
        if self.tags_stack and self.tags_stack[-1] == tag:
            self.tags_stack.pop()

        if tag == "script":
            self.in_script = False
        elif tag == "style":
            self.in_style = False
        elif tag in ("strong", "b"):
            self.output.append("**")
        elif tag in ("em", "i"):
            self.output.append("*")
        elif tag == "code" and not self.in_pre:
            self.output.append("`")
        elif tag == "pre":
            self.in_pre = False
            self.output.append("\n```\n\n")
        elif tag in ("p", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote"):
            self.output.append("\n\n")

    def handle_data(self, data: str) -> None:
        if self.in_script or self.in_style:
            return
        if not self.in_pre:
            # Normalize whitespace outside pre blocks
            data = re.sub(r"[ \t]+", " ", data)
        self.output.append(data)

    def handle_entityref(self, name: str) -> None:
        if self.in_script or self.in_style:
            return
        self.output.append(html.unescape(f"&{name};"))

    def handle_charref(self, name: str) -> None:
        if self.in_script or self.in_style:
            return
        self.output.append(html.unescape(f"&#{name};"))

    def get_markdown(self) -> str:
        text = "".join(self.output)
        # Collapse 3+ consecutive newlines to 2
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()


def convert_html_to_markdown(html_str: str) -> str:
    """Converts an HTML string to clean Markdown."""
    converter = HtmlToMarkdownConverter()
    converter.feed(html_str)
    return converter.get_markdown()


# ==============================================================================
# Pure Python RTF to Text Converter (Zero-Pip)
# ==============================================================================

def rtf_to_text(rtf_content: str | bytes) -> str:
    """
    Pure Python zero-pip RTF (Rich Text Format) text extractor.
    Strips control words, skips stylesheet/font tables, and preserves paragraph breaks.
    """
    text = rtf_content.decode("utf-8", errors="ignore") if isinstance(rtf_content, bytes) else str(rtf_content)

    if not text.startswith("{\\rtf"):
        return text

    # Remove font tables, color tables, stylesheet groups, file tables
    text = re.sub(r"\{\\(?:fonttbl|colortbl|stylesheet|info|\*\\[a-z0-9_-]+)[^}]*\}", "", text, flags=re.DOTALL)

    # Convert RTF paragraph breaks and line breaks
    text = re.sub(r"\\par(?:\r?\n| )?", "\n\n", text)
    text = re.sub(r"\\line(?:\r?\n| )?", "\n", text)
    text = re.sub(r"\\tab(?:\r?\n| )?", "\t", text)

    # Handle unicode escapes: \uN? (followed by optional fallback character)
    def _replace_unicode(m: re.Match[str]) -> str:
        val = int(m.group(1))
        if val < 0:
            val += 65536
        return chr(val)

    text = re.sub(r"\\u(-?\d+)\??", _replace_unicode, text)

    # Handle hex character escapes: \'hh
    def _replace_hex(m: re.Match[str]) -> str:
        try:
            return bytes.fromhex(m.group(1)).decode("cp1252", errors="replace")
        except Exception:
            return ""

    text = re.sub(r"\\\'([0-9a-fA-F]{2})", _replace_hex, text)

    # Remove bold, italic, underline and remaining control words
    text = re.sub(r"\\[a-zA-Z]+-?\d* ?", "", text)

    # Remove remaining braces
    text = text.replace("{", "").replace("}", "")

    # Clean up whitespace
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ==============================================================================
# Format Parsers & Ingestion Strategies
# ==============================================================================

def extract_docx_text(docx_path: Path) -> str:
    """Extracts clean markdown paragraphs from an OpenXML .docx file using docx_sync."""
    return convert_docx_to_markdown(docx_path)


def split_monolithic_by_headings(content: str, default_title: str = "Monolithic") -> list[dict[str, str]]:
    """
    Strict Heading & Structure Splitting:
    Splits markdown content on explicit `# Heading 1` boundaries.
    If no Heading 1 is found, preserves entire content as a single chapter.
    """
    lines = content.splitlines()
    h1_indices: list[tuple[int, str]] = []

    for idx, line in enumerate(lines):
        m = re.match(r"^#\s+(.+)$", line.strip())
        if m:
            h1_indices.append((idx, m.group(1).strip()))

    if not h1_indices:
        logger.info("[OBSERVATION] No Heading 1 (#) detected; importing as single monolithic chapter.")
        return [{"title": default_title, "content": content.strip()}]

    chapters: list[dict[str, str]] = []

    # If there is prose before the first Heading 1 (e.g. prologue or teaser)
    first_idx, _first_title = h1_indices[0]
    if first_idx > 0:
        preamble = "\n".join(lines[:first_idx]).strip()
        if preamble:
            chapters.append({"title": "Prologue", "content": preamble})

    for i, (start_idx, title) in enumerate(h1_indices):
        end_idx = h1_indices[i + 1][0] if i + 1 < len(h1_indices) else len(lines)
        chap_lines = lines[start_idx:end_idx]
        chap_content = "\n".join(chap_lines).strip()
        chapters.append({"title": title, "content": chap_content})

    return chapters


class EpubImporter:
    """
    Zero-pip pure standard library EPUB package and spine parser.
    """

    def __init__(self, epub_path: Path) -> None:
        self.epub_path = Path(epub_path).resolve()

    def parse(self) -> dict[str, Any]:
        if not zipfile.is_zipfile(self.epub_path):
            raise ValueError(f"File is not a valid EPUB zip archive: {self.epub_path}")

        with zipfile.ZipFile(self.epub_path, "r") as zf:
            # 1. Locate OPF from META-INF/container.xml
            try:
                container_data = zf.read("META-INF/container.xml")
            except KeyError as err:
                raise ValueError("EPUB missing META-INF/container.xml") from err

            if b"<!DOCTYPE" in container_data or b"<!ENTITY" in container_data:
                raise ValueError("Unsafe XML DOCTYPE/ENTITY detected in container.xml")
            container_root = ET.fromstring(container_data)  # nosec B314 # noqa: S314
            rootfile = container_root.find(".//{urn:oasis:names:tc:opendocument:xmlns:container}rootfile")
            if rootfile is None or not rootfile.attrib.get("full-path"):
                raise ValueError("EPUB container.xml missing rootfile full-path")

            opf_path = rootfile.attrib["full-path"]
            opf_dir = Path(opf_path).parent

            # 2. Parse OPF
            opf_data = zf.read(opf_path)
            if b"<!DOCTYPE" in opf_data or b"<!ENTITY" in opf_data:
                raise ValueError("Unsafe XML DOCTYPE/ENTITY detected in OPF manifest")
            opf_root = ET.fromstring(opf_data)  # nosec B314 # noqa: S314

            # Metadata extraction
            title = "Imported EPUB"
            author = "Author"
            for elem in opf_root.iter():
                tag = elem.tag.lower()
                if tag.endswith("title") and elem.text:
                    title = elem.text.strip()
                elif tag.endswith("creator") and elem.text:
                    author = elem.text.strip()

            # Manifest map: id -> href
            manifest: dict[str, str] = {}
            for item in opf_root.findall(".//{http://www.idpf.org/2007/opf}item"):
                item_id = item.attrib.get("id")
                href = item.attrib.get("href")
                if item_id and href:
                    # Resolve relative to OPF directory
                    full_href = (opf_dir / href).as_posix() if str(opf_dir) != "." else href
                    manifest[item_id] = full_href

            # Spine sequence
            spine_ids: list[str] = []
            for itemref in opf_root.findall(".//{http://www.idpf.org/2007/opf}itemref"):
                idref = itemref.attrib.get("idref")
                if idref and idref in manifest:
                    spine_ids.append(idref)

            chapters: list[dict[str, str]] = []
            for item_id in spine_ids:
                href = manifest[item_id]
                try:
                    raw_html = zf.read(href).decode("utf-8", errors="replace")
                except KeyError:
                    continue

                md_text = convert_html_to_markdown(raw_html)
                if not md_text.strip():
                    continue

                # Extract title from first heading or stem
                first_h = re.search(r"^#+\s+(.+)$", md_text, flags=re.MULTILINE)
                chap_title = first_h.group(1).strip() if first_h else Path(href).stem

                chapters.append({"title": chap_title, "content": md_text, "source_file": href})

        return {
            "title": title,
            "author": author,
            "chapters": chapters,
        }


class ScrivenerImporter:
    """
    Zero-dependency Scrivener 2 and 3 (.scriv) project binder parser.
    Extracts draft chapters, synopsis index cards, and dual-vault lore dossiers (Characters/Places).
    """

    def __init__(self, scriv_path: Path) -> None:
        self.scriv_path = Path(scriv_path).resolve()

    def parse(self) -> dict[str, Any]:
        scrivx_files = list(self.scriv_path.glob("*.scrivx"))
        if not scrivx_files:
            raise ValueError(f"No .scrivx binder file found in Scrivener package: {self.scriv_path}")

        scrivx_path = scrivx_files[0]
        scrivx_bytes = scrivx_path.read_bytes()
        if b"<!DOCTYPE" in scrivx_bytes or b"<!ENTITY" in scrivx_bytes:
            raise ValueError("Unsafe XML DOCTYPE/ENTITY detected in Scrivener project.scrivx")
        root = ET.fromstring(scrivx_bytes)  # nosec B314 # noqa: S314

        title = root.findtext(".//ProjectTitle") or self.scriv_path.stem
        author = "Author"

        draft_chapters: list[dict[str, Any]] = []
        lore_entities: list[dict[str, Any]] = []

        # Find Binder
        binder = root.find("Binder")
        if binder is None:
            raise ValueError("Invalid Scrivener project: missing <Binder> root.")

        for item in binder.findall("BinderItem"):
            item_type = item.attrib.get("Type", "")
            item_title = item.findtext("Title") or ""

            if item_type == "DraftFolder" or "manuscript" in item_title.lower() or "draft" in item_title.lower():
                self._extract_draft_items(item, draft_chapters)
            elif "character" in item_title.lower():
                self._extract_lore_items(item, "Characters", lore_entities)
            elif "place" in item_title.lower() or "location" in item_title.lower() or "setting" in item_title.lower():
                self._extract_lore_items(item, "Locations", lore_entities)
            elif "research" in item_title.lower() or "note" in item_title.lower():
                self._extract_lore_items(item, "Research", lore_entities)

        return {
            "title": title,
            "author": author,
            "chapters": draft_chapters,
            "lore_entities": lore_entities,
        }

    def _get_item_text(self, item_id: str) -> str:
        # Check Scrivener 3: Files/Data/<UUID>/content.rtf or content.txt
        data_dir = self.scriv_path / "Files" / "Data" / item_id
        if data_dir.is_dir():
            for f in data_dir.iterdir():
                if f.name.lower() in ("content.rtf", "content.txt", "content.md"):
                    content = f.read_bytes()
                    if f.suffix.lower() == ".rtf":
                        return rtf_to_text(content)
                    return content.decode("utf-8", errors="replace")

        # Check Scrivener 2: Files/Docs/<ID>.rtf or <ID>.txt
        docs_dir = self.scriv_path / "Files" / "Docs"
        if docs_dir.is_dir():
            for f in docs_dir.glob(f"{item_id}.*"):
                if f.suffix.lower() == ".rtf":
                    return rtf_to_text(f.read_bytes())
                return f.read_text(encoding="utf-8", errors="replace")

        return ""

    def _get_item_synopsis(self, item_elem: ET.Element, item_id: str) -> str:
        # Check embedded XML <Synopsis>
        embedded_syn = item_elem.findtext(".//Synopsis")
        if embedded_syn and embedded_syn.strip():
            return embedded_syn.strip()

        # Check Scrivener 3: Files/Data/<UUID>/synopsis.txt
        syn_file = self.scriv_path / "Files" / "Data" / item_id / "synopsis.txt"
        if syn_file.is_file():
            return syn_file.read_text(encoding="utf-8", errors="replace").strip()

        # Check Scrivener 2: Files/Docs/<ID>_synopsis.txt
        syn_file_v2 = self.scriv_path / "Files" / "Docs" / f"{item_id}_synopsis.txt"
        if syn_file_v2.is_file():
            return syn_file_v2.read_text(encoding="utf-8", errors="replace").strip()

        return ""

    def _extract_draft_items(self, elem: ET.Element, chapters: list[dict[str, Any]]) -> None:
        children = elem.find("Children")
        if children is None:
            return

        for child in children.findall("BinderItem"):
            item_id = child.attrib.get("ID", "")
            item_title = child.findtext("Title") or f"Chapter {len(chapters) + 1}"
            child_type = child.attrib.get("Type", "")

            text = self._get_item_text(item_id)
            synopsis = self._get_item_synopsis(child, item_id)

            if text.strip() or child_type == "Text":
                chapters.append({
                    "title": item_title,
                    "content": text,
                    "synopsis": synopsis,
                })

            # Recurse into subfolders
            self._extract_draft_items(child, chapters)

    def _extract_lore_items(self, elem: ET.Element, category: str, lore: list[dict[str, Any]]) -> None:
        children = elem.find("Children")
        if children is None:
            return

        for child in children.findall("BinderItem"):
            item_id = child.attrib.get("ID", "")
            item_title = child.findtext("Title") or "Note"
            text = self._get_item_text(item_id)
            synopsis = self._get_item_synopsis(child, item_id)

            safe_stem = sanitize_identifier(re.sub(r"\s+", "_", item_title.strip()), fallback="Lore_Item")
            rel_path = f"{safe_stem}.md"

            lore.append({
                "name": item_title,
                "type": category.rstrip("s").lower(),
                "category": category,
                "rel_path": rel_path,
                "synopsis": synopsis,
                "content": text,
            })

            # Recurse
            self._extract_lore_items(child, category, lore)


# ==============================================================================
# Safe Draft Collision & Core Batch Importer
# ==============================================================================

def resolve_sequential_draft(dest_path: Path, book_name: str, requested_draft: str) -> str:
    """
    Safe Non-Destructive Invariant:
    If dest_path/book_name/requested_draft already exists, resolve the next unused
    sequential draft (e.g., Draft-02, Draft-03).
    """
    book_dir = dest_path / book_name
    if not (book_dir / requested_draft).exists():
        return requested_draft

    # Scan existing Draft-XX folders
    max_num = 1
    m_req = re.search(r"(\d+)", requested_draft)
    if m_req:
        max_num = int(m_req.group(1))

    if book_dir.exists():
        for d in book_dir.iterdir():
            if d.is_dir():
                m = re.search(r"Draft-(\d+)", d.name, re.IGNORECASE)
                if m:
                    num = int(m.group(1))
                    if num > max_num:
                        max_num = num

    return f"Draft-{max_num + 1:02d}"


def standardize_chapter_frontmatter(
    content: str,
    title: str,
    chapter_num: int,
    synopsis: str = "",
    pov: str = "",
) -> tuple[str, int]:
    """
    Standardizes YAML frontmatter at line 0, preserving any existing custom fields.
    Returns (standardized_content, word_count).
    """
    parsed_fm, body = extract_frontmatter_and_body(content)
    fm = parsed_fm if parsed_fm is not None else {}

    # Standard Ars Arcanum Schema
    fm["title"] = fm.get("title") or title
    fm["chapter"] = fm.get("chapter", chapter_num)
    fm["status"] = fm.get("status", "imported")
    if synopsis and not fm.get("synopsis"):
        fm["synopsis"] = synopsis
    if pov and not fm.get("pov"):
        fm["pov"] = pov

    # Ensure clean heading
    clean_body = body.strip()
    if not re.match(r"^\s*#\s+", clean_body):
        clean_title = title.replace("_", " ").replace("-", " ")
        header = f"# Chapter {chapter_num}: {clean_title}\n\n"
        clean_body = header + clean_body

    word_count = count_words_prose(clean_body)
    fm["word_count"] = word_count

    final_content = serialize_yaml_frontmatter(fm, clean_body)
    return final_content, word_count


def import_manuscript_batch(
    source_path: Path | str,
    dest_path: Path | str,
    title: str | None = None,
    author: str = "Author",
    universe: str = "Default-Universe",
    world: str = "Default-World",
    book: str = "Book-01",
    draft: str = "Draft-01",
    extract_lore: bool = True,
    overwrite: bool = False,
    dry_run: bool = False,
    html_report_path: Path | str | None = None,
) -> dict[str, Any]:
    """
    Master Ingestion Engine: Imports Scrivener packages, EPUBs, DOCX, MD, and folder trees.
    Creates structured Ars Arcanum vaults with complete manifests, novelWriter integration,
    and optional dual-vault world lore dossiers.
    """
    source_p = Path(source_path).resolve()
    dest_p = Path(dest_path).resolve()

    if not source_p.exists():
        raise FileNotFoundError(f"Source path does not exist: {source_p}")

    # Determine format
    source_format = "folder"
    raw_chapters: list[dict[str, Any]] = []
    lore_entities: list[dict[str, Any]] = []
    detected_title = title or source_p.stem
    detected_author = author

    if source_p.is_dir() and (source_p.suffix.lower() == ".scriv" or list(source_p.glob("*.scrivx"))):
        source_format = "scrivener"
        parser = ScrivenerImporter(source_p)
        scriv_data = parser.parse()
        detected_title = title or scriv_data.get("title") or detected_title
        detected_author = author if author != "Author" else (scriv_data.get("author") or author)
        raw_chapters = scriv_data.get("chapters", [])
        if extract_lore:
            lore_entities = scriv_data.get("lore_entities", [])

    elif source_p.is_file() and source_p.suffix.lower() == ".epub":
        source_format = "epub"
        parser_epub = EpubImporter(source_p)
        epub_data = parser_epub.parse()
        detected_title = title or epub_data.get("title") or detected_title
        detected_author = author if author != "Author" else (epub_data.get("author") or author)
        raw_chapters = epub_data.get("chapters", [])

    elif source_p.is_file() and source_p.suffix.lower() == ".docx":
        source_format = "docx"
        text = extract_docx_text(source_p)
        raw_chapters = split_monolithic_by_headings(text, default_title=detected_title)

    elif source_p.is_file() and source_p.suffix.lower() in (".md", ".txt"):
        source_format = "markdown" if source_p.suffix.lower() == ".md" else "text"
        text = source_p.read_text(encoding="utf-8", errors="replace")
        raw_chapters = split_monolithic_by_headings(text, default_title=detected_title)

    elif source_p.is_dir():
        source_format = "folder"
        candidate_files = sorted(
            [f for f in source_p.iterdir() if f.is_file() and f.suffix.lower() in (".docx", ".md", ".txt", ".epub")]
        )
        if not candidate_files:
            raise ValueError(f"No convertible files found in directory: {source_p}")

        for f in candidate_files:
            if f.suffix.lower() == ".docx":
                f_text = extract_docx_text(f)
            else:
                f_text = f.read_text(encoding="utf-8", errors="replace")
            clean_name = re.sub(r"^[\d\s_\.-]+", "", f.stem).strip() or f.stem
            raw_chapters.append({"title": clean_name, "content": f_text})

    else:
        raise ValueError(f"Unsupported source format: {source_p}")

    if not raw_chapters:
        raise ValueError(f"No readable manuscript chapters discovered in {source_p}")

    # Resolve target draft with collision safety
    target_draft = draft
    collision_msg = "Fresh Target Directory"

    if (dest_p / book / draft).exists():
        if overwrite:
            collision_msg = "Overwritten (Atomic Backup Created)"
            if not dry_run and create_backup is not None:
                try:
                    create_backup(dest_p)
                    logger.info("[✓] Created pre-overwrite backup archive in Backups/")
                except Exception as e:
                    logger.warning("Could not create pre-overwrite backup: %s", e)
        else:
            target_draft = resolve_sequential_draft(dest_p, book, draft)
            collision_msg = f"Collision Avoided: Auto-incremented to {target_draft}"
            logger.info("[!] Target draft exists. Non-destructively redirecting to: %s", target_draft)

    draft_dir = dest_p / book / target_draft
    total_words = 0
    final_chapters_report: list[dict[str, Any]] = []

    # Prepare and write chapters
    for idx, chap in enumerate(raw_chapters, start=1):
        chap_title = chap.get("title", f"Chapter {idx}")
        raw_content = chap.get("content", "")
        chap_synopsis = chap.get("synopsis", "")
        chap_pov = chap.get("pov", "")

        clean_stem = sanitize_identifier(re.sub(r"\s+", "_", chap_title.strip()), fallback=f"Chapter_{idx:02d}")
        filename = f"{idx:02d}_{clean_stem}.md"
        target_file = draft_dir / filename

        formatted_content, w_count = standardize_chapter_frontmatter(
            content=raw_content,
            title=chap_title,
            chapter_num=idx,
            synopsis=chap_synopsis,
            pov=chap_pov,
        )
        total_words += w_count

        final_chapters_report.append({
            "index": idx,
            "title": chap_title,
            "filename": filename,
            "word_count": w_count,
            "synopsis": chap_synopsis,
            "pov": chap_pov,
        })

        if not dry_run:
            draft_dir.mkdir(parents=True, exist_ok=True)
            atomic_write(target_file, formatted_content)

    # Process World Lore Dossiers (Dual-Vault Scrivener routing)
    world_dir = dest_p.parent / "World" if dest_p.parent.exists() else dest_p / "00-World-Bible"
    if lore_entities and not dry_run:
        world_dir.mkdir(parents=True, exist_ok=True)
        for lore in lore_entities:
            cat_dir = world_dir / lore["category"]
            cat_dir.mkdir(parents=True, exist_ok=True)
            lore_file = cat_dir / lore["rel_path"]

            lore_fm = {
                "name": lore["name"],
                "type": lore["type"],
                "category": lore["category"],
                "status": "imported",
            }
            if lore.get("synopsis"):
                lore_fm["synopsis"] = lore["synopsis"]

            body = lore.get("content", "").strip()
            if not re.match(r"^\s*#\s+", body):
                body = f"# {lore['name']}\n\n" + body

            lore_doc = serialize_yaml_frontmatter(lore_fm, body)
            atomic_write(lore_file, lore_doc)

        # Ensure world.yaml exists
        world_manifest = world_dir / "world.yaml"
        if not world_manifest.exists():
            w_yaml = f"""# Ars Arcanum World Lore Manifest
schema_version: "1.0"
title: {json.dumps(world)}
author: {json.dumps(detected_author)}
universe: {json.dumps(universe)}
status: "in-progress"
"""
            atomic_write(world_manifest, w_yaml)

    # Write manuscript project manifests
    if not dry_run:
        manifest_yaml = f"""# Ars Arcanum Manuscript Project Manifest
schema_version: "1.0"
title: {json.dumps(detected_title)}
author: {json.dumps(detected_author)}
universe: {json.dumps(universe)}
world: {json.dumps(world)}
status: "imported"
"""
        atomic_write(dest_p / "manuscript.yaml", manifest_yaml)

        clean_nwx_title = saxutils.escape(detected_title)
        clean_nwx_author = saxutils.escape(detected_author)
        nwx_content = NWX_TEMPLATE.format(title=clean_nwx_title, author=clean_nwx_author)
        atomic_write(dest_p / "nwProject.nwx", nwx_content)

        gitignore_content = """# Ars Arcanum Manuscript Git Ignore
.arcanum_cache.json
.sync_state.json
*.lock
*.bak
*.tmp
*.log
.DS_Store
Backups/
05-Backups/
Exports/
04-Publishing/
"""
        atomic_write(dest_p / ".gitignore", gitignore_content)

    report = {
        "title": detected_title,
        "author": detected_author,
        "universe": universe,
        "world": world,
        "source_format": source_format,
        "source_path": str(source_p),
        "dest_path": str(dest_p),
        "book": book,
        "draft": target_draft,
        "chapters_imported": len(final_chapters_report),
        "total_words": total_words,
        "lore_entities": lore_entities,
        "collision_resolution": collision_msg,
        "dry_run": dry_run,
        "chapters": final_chapters_report,
    }

    # Render Visual Studio HTML
    html_target = Path(html_report_path) if html_report_path else dest_p / "import_studio.html"
    try:
        render_import_studio_html(report, html_target)
        report["html_report_path"] = str(html_target.resolve())
    except Exception as e:
        logger.warning("Could not render Visual Migration Studio HTML: %s", e)

    return report


# ==============================================================================
# CLI Entry Point & Telemetry Reporting
# ==============================================================================

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ars Arcanum Sovereign Batch Importer & Migration Engine")
    parser.add_argument("source", help="Source file (.scriv, .docx, .epub, .md, .txt) or directory")
    parser.add_argument("--dest", "-d", help="Target manuscript directory", default=None)
    parser.add_argument("--title", "-t", help="Manuscript title override", default=None)
    parser.add_argument("--author", "-a", help="Author name override", default="Author")
    parser.add_argument("--universe", "-u", help="Universe name", default="Default-Universe")
    parser.add_argument("--world", "-w", help="World lore vault name", default="Default-World")
    parser.add_argument("--book", "-b", help="Volume / Book name", default="Book-01")
    parser.add_argument("--draft", help="Target draft directory name", default="Draft-01")
    parser.add_argument("--no-lore", action="store_true", help="Disable auxiliary lore dossier extraction")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing draft (creates atomic backup first)")
    parser.add_argument("--dry-run", action="store_true", help="Simulate import without writing files")
    parser.add_argument("--html", help="Path to export standalone Visual Migration Studio HTML", default=None)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON output")

    args = parser.parse_args(argv)
    source_p = Path(args.source)

    if args.dest:
        dest_p = Path(args.dest)
    else:
        manuscripts_base = Path(os.environ.get("MANUSCRIPTS_BASE", Path.home() / "Manuscripts"))
        safe_name = sanitize_identifier(args.title or source_p.stem, fallback="Imported-Manuscript")
        dest_p = manuscripts_base / safe_name

    try:
        res = import_manuscript_batch(
            source_path=source_p,
            dest_path=dest_p,
            title=args.title,
            author=args.author,
            universe=args.universe,
            world=args.world,
            book=args.book,
            draft=args.draft,
            extract_lore=not args.no_lore,
            overwrite=args.overwrite,
            dry_run=args.dry_run,
            html_report_path=args.html,
        )

        if args.json:
            print(json.dumps(res, indent=2))
            return 0

        # Rich Terminal Output
        dry_badge = " [DRY-RUN SIMULATION]" if res["dry_run"] else ""
        print(f"\n⚡ Ars Arcanum Batch Importer{dry_badge}")
        print("═" * 68)
        print(f"  • Manuscript:  {res['title']} (by {res['author']})")
        print(f"  • Source:      {res['source_format'].upper()} ({res['source_path']})")
        print(f"  • Target:      {res['dest_path']} [{res['book']}/{res['draft']}]")
        print(f"  • Chapters:    {res['chapters_imported']} extracted ({res['total_words']:,} words)")
        print(f"  • World Lore:  {len(res['lore_entities'])} dossiers routed to World/")
        print(f"  • Collision:   {res['collision_resolution']}")
        if res.get("html_report_path"):
            print(f"  • Visual UI:   file:///{Path(res['html_report_path']).as_posix()}")
        print("═" * 68)

        for ch in res["chapters"]:
            print(f"    ✓ {res['book']}/{res['draft']}/{ch['filename']} ({ch['word_count']:,} words)")

        return 0

    except Exception as e:
        print(f"Error importing manuscript: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
