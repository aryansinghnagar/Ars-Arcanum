#!/usr/bin/env python3
"""
Ars Arcanum DOCX OpenXML Package Builder (scripts/lib/docx_builder.py)
=====================================================================
Low-level XML schema formatting, Markdown to DOCX paragraph parsing,
run generators, typography conversions, and zip package creation.
"""

from __future__ import annotations

import logging
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger("arcanum.docx_builder")

FRONTMATTER_REGEX = re.compile(r"^---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)", re.DOTALL)
NW_TAG_REGEX = re.compile(r"^@[A-Za-z0-9_-]+:", re.MULTILINE)
MD_BOLD_ITALIC_REGEX = re.compile(r"(\*\*\*[^*]+\*\*\*|\*\*[^*]+\*\*|\*[^*]+\*|___[^_]+___|__[^_]+__|_[^_]+_)")
_ILLEGAL_XML_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def escape_xml(text: str) -> str:
    """Escapes XML special characters and strips illegal XML 1.0 control characters."""
    clean = _ILLEGAL_XML_CHARS.sub("", str(text))
    return (
        clean
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def inches_to_dxa(inches: float) -> int:
    """Converts inches to twentieths of a point (dxa). 1 in = 1440 dxa."""
    return round(inches * 1440)


def pt_to_half_pt(pt: float) -> int:
    """Converts points to half-points. 12 pt = 24."""
    return round(pt * 2)


def line_spacing_to_val(line_spacing: float) -> tuple[int, str]:
    """Returns (w:line, w:lineRule) for Word OpenXML paragraph spacing."""
    if line_spacing >= 2.0:
        return (480, "auto")
    if line_spacing >= 1.5:
        return (360, "auto")
    if line_spacing >= 1.3:
        return (round(240 * line_spacing), "auto")
    return (240, "auto")


def strip_scene_tags_and_frontmatter(text: str) -> tuple[str, dict[str, str], list[str]]:
    """Strips YAML frontmatter and novelWriter metadata tags from prose.

    Returns (clean_prose, metadata_dict, raw_header_lines)
    """
    metadata: dict[str, str] = {}
    header_lines: list[str] = []

    # Extract YAML frontmatter if present
    clean_text = text
    fm_match = FRONTMATTER_REGEX.match(text)
    if fm_match:
        fm_content = fm_match.group(1)
        header_lines.append("---")
        for line in fm_content.splitlines():
            header_lines.append(line)
            if ":" in line:
                k, v = line.split(":", 1)
                metadata[k.strip().lower()] = v.strip().strip("\"'")
        header_lines.append("---")
        clean_text = FRONTMATTER_REGEX.sub("", text, count=1)

    prose_lines: list[str] = []
    for line in clean_text.splitlines():
        trimmed = line.strip()
        if trimmed.startswith("@") and NW_TAG_REGEX.match(trimmed):
            header_lines.append(trimmed)
            if ":" in trimmed:
                tag_name, tag_val = trimmed[1:].split(":", 1)
                metadata[tag_name.strip().lower()] = tag_val.strip().strip("\"'")
        elif trimmed.startswith("%"):
            # Comment line
            header_lines.append(trimmed)
        else:
            prose_lines.append(line)

    return ("\n".join(prose_lines), metadata, header_lines)


def parse_markdown_to_paragraphs(md_text: str) -> list[dict[str, str]]:
    """Parses markdown text into structured paragraph tokens for DOCX generation."""
    clean_text, _, _ = strip_scene_tags_and_frontmatter(md_text)
    paragraphs: list[dict[str, str]] = []

    # Split by blank lines or multiple newlines
    raw_blocks = re.split(r"\n\s*\n", clean_text)
    for block in raw_blocks:
        b = block.strip()
        if not b:
            continue

        # Check for headings
        if b.startswith("# "):
            paragraphs.append({"type": "heading1", "text": b[2:].strip()})
        elif b.startswith("## "):
            paragraphs.append({"type": "heading2", "text": b[3:].strip()})
        elif b.startswith("### "):
            paragraphs.append({"type": "heading3", "text": b[4:].strip()})
        elif b in ("#", "* * *", "***", "---", "___", "- - -"):
            paragraphs.append({"type": "scene_break", "text": b})
        else:
            # Body paragraph with potential inline formatting
            single_line_text = " ".join([ln.strip() for ln in b.splitlines() if ln.strip()])
            paragraphs.append({"type": "body", "text": single_line_text})

    return paragraphs


def format_runs_xml(text: str, font_family: str, font_size_half_pt: int) -> str:
    """Parses inline Markdown formatting (**bold**, *italic*) and returns OpenXML <w:r> tags."""
    runs_xml: list[str] = []

    # Tokenize text by markdown delimiters
    tokens = re.split(r"(\*\*\*[^*]+\*\*\*|\*\*[^*]+\*\*|\*[^*]+\*|___[^_]+___|__[^_]+__|_[^_]+_)", text)

    for tok in tokens:
        if not tok:
            continue

        is_bold = False
        is_italic = False
        inner_text = tok

        if (tok.startswith("***") and tok.endswith("***")) or (tok.startswith("___") and tok.endswith("___")):
            is_bold = True
            is_italic = True
            inner_text = tok[3:-3]
        elif (tok.startswith("**") and tok.endswith("**")) or (tok.startswith("__") and tok.endswith("__")):
            is_bold = True
            inner_text = tok[2:-2]
        elif (tok.startswith("*") and tok.endswith("*")) or (tok.startswith("_") and tok.endswith("_")):
            is_italic = True
            inner_text = tok[1:-1]

        rpr_parts = [
            f'<w:rFonts w:ascii="{escape_xml(font_family)}" w:hAnsi="{escape_xml(font_family)}" w:cs="{escape_xml(font_family)}"/>',
            f'<w:sz w:val="{font_size_half_pt}"/>',
            f'<w:szCs w:val="{font_size_half_pt}"/>',
        ]
        if is_bold:
            rpr_parts.append('<w:b/><w:bCs/>')
        if is_italic:
            rpr_parts.append('<w:i/><w:iCs/>')

        rpr_str = "".join(rpr_parts)
        t_xml = f'<w:t xml:space="preserve">{escape_xml(inner_text)}</w:t>'
        runs_xml.append(f'<w:r><w:rPr>{rpr_str}</w:rPr>{t_xml}</w:r>')

    return "".join(runs_xml)


def generate_docx_xml_body(parsed_paragraphs: list[dict[str, str]], config: dict[str, Any], is_full_manuscript: bool = False) -> str:
    """Generates the OpenXML <w:body> XML string from parsed paragraphs."""
    font_family = config.get("font_family", "Times New Roman")
    font_size_pt = float(config.get("font_size_pt", 12.0))
    font_size_half_pt = pt_to_half_pt(font_size_pt)
    heading1_size_half_pt = pt_to_half_pt(font_size_pt + 4.0)
    heading2_size_half_pt = pt_to_half_pt(font_size_pt + 2.0)

    line_spacing = float(config.get("line_spacing", 2.0))
    line_val, line_rule = line_spacing_to_val(line_spacing)

    margin_in = float(config.get("margin_inches", 1.0))
    margin_dxa = inches_to_dxa(margin_in)

    indent_in = float(config.get("first_line_indent_inches", 0.5))
    indent_dxa = inches_to_dxa(indent_in)

    scene_break_sym = config.get("scene_break_symbol", "#")
    page_break_chapters = bool(config.get("page_break_chapters", True))

    body_xml_parts: list[str] = []
    chapter_index = 0

    for p in parsed_paragraphs:
        ptype = p["type"]
        ptext = p["text"]

        if ptype == "heading1":
            chapter_index += 1
            pPr_parts = [
                '<w:pStyle w:val="Heading1"/>',
                '<w:jc w:val="center"/>',
                f'<w:spacing w:before="720" w:after="360" w:line="{line_val}" w:lineRule="{line_rule}"/>',
            ]
            # Add page break before subsequent chapters in full manuscript
            if is_full_manuscript and chapter_index > 1 and page_break_chapters:
                pPr_parts.append('<w:pageBreakBefore/>')

            r_xml = format_runs_xml(ptext, font_family, heading1_size_half_pt)
            body_xml_parts.append(f'<w:p><w:pPr>{"".join(pPr_parts)}</w:pPr>{r_xml}</w:p>')

        elif ptype == "heading2":
            pPr_parts = [
                '<w:pStyle w:val="Heading2"/>',
                '<w:jc w:val="left"/>',
                f'<w:spacing w:before="360" w:after="180" w:line="{line_val}" w:lineRule="{line_rule}"/>',
            ]
            r_xml = format_runs_xml(ptext, font_family, heading2_size_half_pt)
            body_xml_parts.append(f'<w:p><w:pPr>{"".join(pPr_parts)}</w:pPr>{r_xml}</w:p>')

        elif ptype == "heading3":
            pPr_parts = [
                '<w:pStyle w:val="Heading3"/>',
                '<w:jc w:val="left"/>',
                f'<w:spacing w:before="240" w:after="120" w:line="{line_val}" w:lineRule="{line_rule}"/>',
            ]
            r_xml = format_runs_xml(ptext, font_family, font_size_half_pt)
            body_xml_parts.append(f'<w:p><w:pPr>{"".join(pPr_parts)}</w:pPr>{r_xml}</w:p>')

        elif ptype == "scene_break":
            # Centered scene break
            symbol = scene_break_sym if scene_break_sym else "#"
            pPr_parts = [
                '<w:jc w:val="center"/>',
                f'<w:spacing w:before="360" w:after="360" w:line="{line_val}" w:lineRule="{line_rule}"/>',
            ]
            r_xml = format_runs_xml(symbol, font_family, font_size_half_pt)
            body_xml_parts.append(f'<w:p><w:pPr>{"".join(pPr_parts)}</w:pPr>{r_xml}</w:p>')

        else:
            # Body paragraph
            pPr_parts = [
                f'<w:ind w:firstLine="{indent_dxa}"/>',
                f'<w:spacing w:before="0" w:after="0" w:line="{line_val}" w:lineRule="{line_rule}"/>',
                '<w:jc w:val="both"/>',
            ]
            r_xml = format_runs_xml(ptext, font_family, font_size_half_pt)
            body_xml_parts.append(f'<w:p><w:pPr>{"".join(pPr_parts)}</w:pPr>{r_xml}</w:p>')

    # Section properties (Page layout, size & margins)
    sect_pr = (
        f'<w:sectPr>'
        f'<w:pgSz w:w="12240" w:h="15840"/>'
        f'<w:pgMar w:top="{margin_dxa}" w:right="{margin_dxa}" w:bottom="{margin_dxa}" w:left="{margin_dxa}" w:header="720" w:footer="720" w:gutter="0"/>'
        f'<w:cols w:space="720"/>'
        f'<w:docGrid w:linePitch="360"/>'
        f'</w:sectPr>'
    )
    body_xml_parts.append(sect_pr)

    return "".join(body_xml_parts)


def build_docx_package(
    output_path: Path,
    parsed_paragraphs: list[dict[str, str]],
    config: dict[str, Any],
    title: str = "",
    author: str = "",
    is_full_manuscript: bool = False,
    source_mtime: float | None = None,
) -> bool:
    """Builds a fully compliant OpenXML .docx file package."""
    font_family = config.get("font_family", "Times New Roman")
    font_size_pt = float(config.get("font_size_pt", 12.0))
    font_size_half_pt = pt_to_half_pt(font_size_pt)

    content_types_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>"""

    root_rels_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>"""

    word_rels_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>"""

    styles_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:docDefaults>
    <w:rPrDefault>
      <w:rPr>
        <w:rFonts w:ascii="{escape_xml(font_family)}" w:hAnsi="{escape_xml(font_family)}" w:cs="{escape_xml(font_family)}"/>
        <w:sz w:val="{font_size_half_pt}"/>
        <w:szCs w:val="{font_size_half_pt}"/>
        <w:lang w:val="en-US"/>
      </w:rPr>
    </w:rPrDefault>
    <w:pPrDefault/>
  </w:docDefaults>
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal">
    <w:name w:val="Normal"/>
    <w:qFormat/>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading1">
    <w:name w:val="heading 1"/>
    <w:basedOn w:val="Normal"/>
    <w:next w:val="Normal"/>
    <w:qFormat/>
    <w:rPr>
      <w:b/><w:bCs/>
      <w:sz w:val="{font_size_half_pt + 8}"/>
      <w:szCs w:val="{font_size_half_pt + 8}"/>
    </w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading2">
    <w:name w:val="heading 2"/>
    <w:basedOn w:val="Normal"/>
    <w:next w:val="Normal"/>
    <w:qFormat/>
    <w:rPr>
      <w:b/><w:bCs/>
      <w:sz w:val="{font_size_half_pt + 4}"/>
      <w:szCs w:val="{font_size_half_pt + 4}"/>
    </w:rPr>
  </w:style>
</w:styles>"""

    if source_mtime is not None:
        created_dt = datetime.fromtimestamp(source_mtime, tz=timezone.utc)
    else:
        created_dt = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    now_iso = created_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    zip_dt_tuple = created_dt.timetuple()[:6]

    core_props_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>{escape_xml(title)}</dc:title>
  <dc:creator>{escape_xml(author or 'Author')}</dc:creator>
  <cp:lastModifiedBy>Ars Arcanum</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{now_iso}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{now_iso}</dcterms:modified>
</cp:coreProperties>"""

    app_props_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Ars Arcanum</Application>
  <DocSecurity>0</DocSecurity>
  <Company>Ars Arcanum Studio</Company>
</Properties>"""

    body_xml = generate_docx_xml_body(parsed_paragraphs, config, is_full_manuscript=is_full_manuscript)
    document_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <w:body>
    {body_xml}
  </w:body>
</w:document>"""

    tmp_zip = output_path.with_suffix(".docx.tmp")
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(tmp_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            entries = [
                ("[Content_Types].xml", content_types_xml),
                ("_rels/.rels", root_rels_xml),
                ("word/_rels/document.xml.rels", word_rels_xml),
                ("word/document.xml", document_xml),
                ("word/styles.xml", styles_xml),
                ("docProps/core.xml", core_props_xml),
                ("docProps/app.xml", app_props_xml),
            ]
            for entry_name, entry_data in entries:
                zinfo = zipfile.ZipInfo(filename=entry_name, date_time=zip_dt_tuple)
                zinfo.compress_type = zipfile.ZIP_DEFLATED
                zf.writestr(zinfo, entry_data.encode("utf-8") if isinstance(entry_data, str) else entry_data)

        if tmp_zip.is_file():
            tmp_zip.replace(output_path)
            return True
    except Exception as e:
        logger.error("Failed to compile DOCX package at %s: %s", output_path, e)
        if tmp_zip.is_file():
            tmp_zip.unlink(missing_ok=True)

    return False
