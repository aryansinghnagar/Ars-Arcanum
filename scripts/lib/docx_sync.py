#!/usr/bin/env python3
"""
Ars Arcanum DOCX Synchronization & Typesetting Engine (scripts/lib/docx_sync.py)
================================================================================
Bidirectional Word processor synchronization, live debounced file watching,
visual diff review, and native OpenXML manuscript generator.
Enables authors to draft, review, and edit manuscripts seamlessly in Microsoft Word,
Google Docs, and LibreOffice Writer while preserving Markdown integrity.

Zero external dependencies; operates 100% offline.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from lib._bootstrap import atomic_write, count_prose_words
    from lib.scope import (
        EngineScope,
        add_scope_arguments,
        filter_manuscript_scope,
        parse_scope_args,
        resolve_manuscript_path,
    )
except ImportError:
    from _bootstrap import atomic_write, count_prose_words  # type: ignore[no-redef]
    from scope import (  # type: ignore[no-redef]
        EngineScope,
        add_scope_arguments,
        filter_manuscript_scope,
        parse_scope_args,
        resolve_manuscript_path,
    )

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("arcanum.docx_sync")

try:
    from lib.config import (
        get_active_docx_preset_name,
        get_docx_config,
        list_docx_presets,
        set_docx_preset,
    )
except ImportError:
    from config import (  # type: ignore[no-redef]
        get_active_docx_preset_name,
        get_docx_config,
        list_docx_presets,
        set_docx_preset,
    )

try:
    from lib.docx_builder import (
        FRONTMATTER_REGEX,
        MD_BOLD_ITALIC_REGEX,
        NW_TAG_REGEX,
        build_docx_package,
        escape_xml,
        extract_docx_heading1,
        format_runs_xml,
        generate_docx_xml_body,
        inches_to_dxa,
        line_spacing_to_val,
        parse_markdown_to_paragraphs,
        pt_to_half_pt,
        strip_scene_tags_and_frontmatter,
    )
except ImportError:
    from docx_builder import (  # type: ignore[no-redef]
        FRONTMATTER_REGEX,
        MD_BOLD_ITALIC_REGEX,
        NW_TAG_REGEX,
        build_docx_package,
        escape_xml,
        extract_docx_heading1,
        format_runs_xml,
        generate_docx_xml_body,
        inches_to_dxa,
        line_spacing_to_val,
        parse_markdown_to_paragraphs,
        pt_to_half_pt,
        strip_scene_tags_and_frontmatter,
    )

try:
    from lib.docx_sync_template import render_docx_studio_html
except ImportError:
    try:
        from docx_sync_template import render_docx_studio_html  # type: ignore[no-redef]
    except ImportError:
        render_docx_studio_html = None  # type: ignore[assignment]


MAX_DOCX_UNCOMPRESSED_BYTES = 50 * 1024 * 1024  # 50 MB safety limit
MAX_DOCX_FILE_BYTES = 20 * 1024 * 1024  # 20 MB safety limit

__all__ = [
    "FRONTMATTER_REGEX",
    "MAX_DOCX_FILE_BYTES",
    "MAX_DOCX_UNCOMPRESSED_BYTES",
    "MD_BOLD_ITALIC_REGEX",
    "NW_TAG_REGEX",
    "build_docx_package",
    "build_manuscript_docx",
    "convert_docx_to_markdown",
    "escape_xml",
    "extract_docx_comments",
    "extract_docx_heading1",
    "format_runs_xml",
    "generate_docx_studio_report",
    "generate_docx_xml_body",
    "get_active_docx_preset_name",
    "get_docx_config",
    "get_file_sha256",
    "inches_to_dxa",
    "line_spacing_to_val",
    "load_sync_state",
    "main",
    "open_in_word_processor",
    "parse_markdown_to_paragraphs",
    "pt_to_half_pt",
    "resolve_active_draft_dir",
    "resolve_manuscript_path",
    "save_sync_state",
    "strip_scene_tags_and_frontmatter",
    "sync_manuscript_docx",
    "watch_manuscript_docx",
]


def _extract_active_runs_from_element(elem: ET.Element, ns: dict[str, str]) -> list[tuple[str, bool, bool]]:
    """
    Recursively extracts active (non-deleted) text runs from XML element.
    Returns list of (text, is_bold, is_italic).
    Explicitly ignores <w:del> (Track Changes deleted content) to prevent zombie text revival.
    """
    w_tag = f"{{{ns['w']}}}"
    runs: list[tuple[str, bool, bool]] = []

    for child in elem:
        tag = child.tag
        if tag == f"{w_tag}del":
            # Skip Track Changes deleted text branch completely
            continue
        if tag == f"{w_tag}r":
            # Regular run
            rPr = child.find(f"{w_tag}rPr")
            is_bold = rPr is not None and rPr.find(f"{w_tag}b") is not None
            is_italic = rPr is not None and rPr.find(f"{w_tag}i") is not None
            t_elem = child.find(f"{w_tag}t")
            if t_elem is not None and t_elem.text:
                runs.append((t_elem.text, bool(is_bold), bool(is_italic)))
        elif tag in (f"{w_tag}ins", f"{w_tag}hyperlink", f"{w_tag}smartTag", f"{w_tag}sdt", f"{w_tag}sdtContent"):
            # Active container elements - recurse into children
            runs.extend(_extract_active_runs_from_element(child, ns))

    return runs


def extract_docx_comments(docx_path: Path) -> list[dict[str, Any]]:
    """Extracts editorial comments from word/comments.xml in DOCX zip archive."""
    if not docx_path.is_file():
        return []
    comments = []
    try:
        with zipfile.ZipFile(docx_path, "r") as zf:
            if "word/comments.xml" not in zf.namelist():
                return []
            with zf.open("word/comments.xml") as f:
                comments_xml_bytes = f.read(MAX_DOCX_UNCOMPRESSED_BYTES + 1)
            if len(comments_xml_bytes) > MAX_DOCX_UNCOMPRESSED_BYTES:
                return []

            for sample in (
                comments_xml_bytes.decode("utf-8", errors="ignore").lower(),
                comments_xml_bytes.decode("utf-16le", errors="ignore").lower(),
                comments_xml_bytes.decode("utf-16be", errors="ignore").lower(),
            ):
                if "<!entity" in sample or "<!doctype" in sample:
                    return []

            root = ET.fromstring(comments_xml_bytes)  # nosec B314 # noqa: S314
            ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
            w_tag = f"{{{ns['w']}}}"
            for c in root.iter(f"{w_tag}comment"):
                c_id = c.attrib.get(f"{w_tag}id", "")
                author = c.attrib.get(f"{w_tag}author", "Editor")
                date = c.attrib.get(f"{w_tag}date", "")
                text_parts = []
                for t in c.iter(f"{w_tag}t"):
                    if t.text:
                        text_parts.append(t.text)
                full_comment_text = " ".join(text_parts).strip()
                if full_comment_text:
                    comments.append({
                        "id": c_id,
                        "author": author,
                        "date": date,
                        "text": full_comment_text,
                    })
    except Exception as e:
        logger.debug("Failed extracting comments from %s: %s", docx_path, e)
    return comments


def convert_docx_to_markdown(docx_path: Path) -> str:
    """Extracts prose from a DOCX file and converts it into clean Markdown, ignoring deleted track changes."""
    if not docx_path.is_file():
        raise FileNotFoundError(f"DOCX file not found: {docx_path}")

    if not zipfile.is_zipfile(docx_path):
        raise ValueError(f"File is not a valid zip/docx archive: {docx_path}")

    try:
        with zipfile.ZipFile(docx_path, "r") as zf:
            if "word/document.xml" not in zf.namelist():
                raise ValueError(f"word/document.xml missing in docx: {docx_path}")
            total_uncompressed = sum(info.file_size for info in zf.infolist())
            if total_uncompressed > MAX_DOCX_UNCOMPRESSED_BYTES:
                raise ValueError(f"DOCX uncompressed payload exceeds safety threshold ({MAX_DOCX_UNCOMPRESSED_BYTES // (1024*1024)} MB)")
            with zf.open("word/document.xml") as f:
                doc_xml_bytes = f.read(MAX_DOCX_UNCOMPRESSED_BYTES + 1)
            if len(doc_xml_bytes) > MAX_DOCX_UNCOMPRESSED_BYTES:
                raise ValueError(f"DOCX document.xml exceeds maximum safety threshold ({MAX_DOCX_UNCOMPRESSED_BYTES // (1024*1024)} MB)")

        for sample in (
            doc_xml_bytes.decode("utf-8", errors="ignore").lower(),
            doc_xml_bytes.decode("utf-16le", errors="ignore").lower(),
            doc_xml_bytes.decode("utf-16be", errors="ignore").lower(),
        ):
            if "<!entity" in sample or "<!doctype" in sample:
                raise ValueError("Unsafe DOCTYPE/ENTITY and Unsafe XML entity declaration detected in DOCX document.xml")

        root = ET.fromstring(doc_xml_bytes)  # nosec B314 # noqa: S314
        ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

        md_paragraphs = []
        for p in root.iter(f"{{{ns['w']}}}p"):
            # Check for style
            pPr = p.find(f"{{{ns['w']}}}pPr")
            style_val = ""
            if pPr is not None:
                pStyle = pPr.find(f"{{{ns['w']}}}pStyle")
                if pStyle is not None:
                    style_val = pStyle.attrib.get(f"{{{ns['w']}}}val", "").lower()

            p_runs = []
            for r_text, is_bold, is_italic in _extract_active_runs_from_element(p, ns):
                if is_bold and is_italic:
                    p_runs.append(f"***{r_text}***")
                elif is_bold:
                    p_runs.append(f"**{r_text}**")
                elif is_italic:
                    p_runs.append(f"*{r_text}*")
                else:
                    p_runs.append(r_text)

            p_text = "".join(p_runs).strip()
            if not p_text:
                continue

            if "heading1" in style_val or "heading 1" in style_val:
                md_paragraphs.append(f"# {p_text}")
            elif "heading2" in style_val or "heading 2" in style_val:
                md_paragraphs.append(f"## {p_text}")
            elif "heading3" in style_val or "heading 3" in style_val:
                md_paragraphs.append(f"### {p_text}")
            elif p_text in ("#", "* * *", "***", "---", "___", "- - -"):
                md_paragraphs.append("* * *")
            else:
                md_paragraphs.append(p_text)

        return "\n\n".join(md_paragraphs) + "\n"

    except Exception as e:
        logger.error("Failed to convert DOCX to Markdown for %s: %s", docx_path, e)
        raise


def resolve_active_draft_dir(manuscript_dir: Path, requested_draft: str | None = None) -> Path:
    """Finds the active or requested draft directory in a manuscript project."""
    ms_dir = manuscript_dir / "01-Manuscript" if (manuscript_dir / "01-Manuscript").is_dir() else manuscript_dir

    # Check volume Book-01 or books
    book_dirs = sorted([d for d in ms_dir.glob("Book-*") if d.is_dir()])
    target_vol = book_dirs[0] if book_dirs else ms_dir

    draft_dirs = sorted([d for d in target_vol.glob("Draft-*") if d.is_dir()])
    if not draft_dirs:
        return target_vol

    if requested_draft:
        match = [d for d in draft_dirs if d.name.lower() == requested_draft.lower()]
        if match:
            return match[0]

    # Check manifest
    manifest = manuscript_dir / "manuscript.yaml"
    if manifest.is_file():
        try:
            content = manifest.read_text(encoding="utf-8")
            for line in content.splitlines():
                if line.startswith("active_draft:"):
                    ad = line.split(":", 1)[1].strip().strip("\"'")
                    match = [d for d in draft_dirs if d.name.lower() == ad.lower()]
                    if match:
                        return match[0]
        except Exception:
            pass

    return draft_dirs[-1]


def build_manuscript_docx(
    manuscript_dir: Path,
    draft_name: str | None = None,
    preset_name: str | None = None,
    scope: EngineScope | None = None,
) -> dict[str, Any]:
    """Builds both per-chapter .docx files and consolidated draft .docx files for a manuscript."""
    mpath = Path(manuscript_dir).resolve()
    draft_dir = resolve_active_draft_dir(mpath, draft_name)
    config = get_docx_config(preset_name)

    # Read title and author from manifest
    title = mpath.name
    author = "Author"
    manifest = mpath / "manuscript.yaml"
    if manifest.is_file():
        try:
            content = manifest.read_text(encoding="utf-8")
            for line in content.splitlines():
                if line.startswith("title:"):
                    title = line.split(":", 1)[1].strip().strip("\"'")
                elif line.startswith("author:"):
                    author = line.split(":", 1)[1].strip().strip("\"'")
        except Exception:
            pass

    results: dict[str, Any] = {
        "manuscript": mpath.name,
        "draft": draft_dir.name,
        "chapters_built": [],
        "consolidated_built": None,
        "errors": [],
    }

    consolidated_paragraphs = []

    # Find all Markdown scenes
    md_files = sorted(draft_dir.rglob("*.md"))
    valid_scenes = [f for f in md_files if not f.name.startswith(".") and "Outlines" not in f.parts and not f.name.endswith(".comments.json")]

    if scope:
        scoped_chapters, _, _ = filter_manuscript_scope(draft_dir, scope)
        scoped_paths = {c.file_path for c in scoped_chapters if c.file_path}
        valid_scenes = [f for f in valid_scenes if f in scoped_paths]

    for scene_file in valid_scenes:
        try:
            content = scene_file.read_text(encoding="utf-8", errors="replace")
            parsed = parse_markdown_to_paragraphs(content)
            if not parsed:
                continue

            # If no heading1 present, add scene title as heading1
            if not any(p["type"] == "heading1" for p in parsed):
                clean_title = scene_file.stem.replace("_", " ").replace("-", " ")
                clean_title = re.sub(r"^\d+\s*", "", clean_title)
                parsed.insert(0, {"type": "heading1", "text": clean_title})

            # 1. Build individual chapter .docx
            ch_docx_path = scene_file.with_suffix(".docx")
            scene_mtime = scene_file.stat().st_mtime
            if build_docx_package(ch_docx_path, parsed, config, title=title, author=author, is_full_manuscript=False, source_mtime=scene_mtime):
                results["chapters_built"].append(str(ch_docx_path.relative_to(mpath)).replace("\\", "/"))

            # Accumulate for consolidated draft manuscript
            consolidated_paragraphs.extend(parsed)

        except Exception as e:
            err = f"Failed to build chapter DOCX for {scene_file}: {e}"
            logger.error(err)
            results["errors"].append(err)

    # 2. Build consolidated full draft .docx
    if consolidated_paragraphs:
        draft_label = draft_dir.name if draft_dir.name.startswith("Draft-") else "Draft-01"
        consolidated_docx_name = f"{draft_label}_Manuscript.docx"
        consolidated_path = draft_dir / consolidated_docx_name
        max_mtime = max((f.stat().st_mtime for f in valid_scenes), default=None)

        if build_docx_package(consolidated_path, consolidated_paragraphs, config, title=title, author=author, is_full_manuscript=True, source_mtime=max_mtime):
            results["consolidated_built"] = str(consolidated_path.relative_to(mpath)).replace("\\", "/")

    return results


def get_file_sha256(path: Path) -> str:
    """Calculates SHA-256 hash of a file with lock-retry resilience."""
    if not path.is_file():
        return ""
    for attempt in range(4):
        try:
            h = hashlib.sha256()
            with open(path, "rb") as f:
                while chunk := f.read(65536):
                    h.update(chunk)
            return h.hexdigest()
        except (PermissionError, OSError):
            if attempt == 3:
                return ""
            time.sleep(0.05 * (2**attempt))
    return ""


def load_sync_state(draft_dir: Path) -> dict[str, Any]:
    state_file = draft_dir / ".sync_state.json"
    if state_file.is_file():
        try:
            with open(state_file, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.debug("Failed to read sync state %s: %s", state_file, e)
    return {}


def save_sync_state(draft_dir: Path, state: dict[str, Any]) -> None:
    state_file = draft_dir / ".sync_state.json"
    atomic_write(state_file, json.dumps(state, indent=2))


def _update_frontmatter_title(raw_headers: list[str], new_title: str) -> list[str]:
    """Updates title: key in raw headers/frontmatter while preserving all other keys."""
    updated: list[str] = []
    has_updated_title = False
    in_fm = False

    for line in raw_headers:
        if line.strip() == "---":
            in_fm = not in_fm
            updated.append(line)
            continue

        if in_fm and re.match(r"^title\s*:", line, re.IGNORECASE):
            updated.append(f'title: "{new_title}"')
            has_updated_title = True
        else:
            updated.append(line)

    if not has_updated_title and any(line.strip() == "---" for line in raw_headers):
        # Insert title before closing ---
        idx = len(updated) - 1
        while idx >= 0 and updated[idx].strip() != "---":
            idx -= 1
        if idx > 0:
            updated.insert(idx, f'title: "{new_title}"')

    return updated


def sync_manuscript_docx(
    manuscript_dir: Path,
    draft_name: str | None = None,
    interactive: bool = False,
    visual_diff: bool = False,
) -> dict[str, Any]:
    """Performs 3-way hash-verified bidirectional synchronization between .md and .docx files."""
    mpath = Path(manuscript_dir).resolve()
    draft_dir = resolve_active_draft_dir(mpath, draft_name)
    config = get_docx_config()

    sync_report: dict[str, Any] = {
        "manuscript": mpath.name,
        "draft": draft_dir.name,
        "md_to_docx": [],
        "docx_to_md": [],
        "comments_extracted": [],
        "conflicts": [],
        "errors": [],
    }

    state = load_sync_state(draft_dir)
    state_updated = False

    # 1. Discover all pairs, filtering temporary and backup files
    md_files = {
        f.stem: f
        for f in draft_dir.rglob("*.md")
        if not f.name.startswith(".")
        and "Outlines" not in f.parts
        and not f.name.endswith(".conflict_*.md")
    }
    docx_files = {
        f.stem: f
        for f in draft_dir.rglob("*.docx")
        if not f.name.startswith(".")
        and not f.name.startswith("~$")
        and not f.name.startswith(".~lock")
        and not f.stem.endswith("_Manuscript")
    }

    all_stems = set(md_files.keys()).union(set(docx_files.keys()))

    for stem in sorted(all_stems):
        md_path = md_files.get(stem)
        docx_path = docx_files.get(stem)
        stem_state = state.get(stem, {})
        stored_md_hash = stem_state.get("md_sha256")
        stored_docx_hash = stem_state.get("docx_sha256")

        if md_path and not docx_path:
            # MD exists, DOCX missing -> Build DOCX
            target_docx = md_path.with_suffix(".docx")
            try:
                content = md_path.read_text(encoding="utf-8", errors="replace")
                parsed = parse_markdown_to_paragraphs(content)
                if not any(p["type"] == "heading1" for p in parsed):
                    clean_title = re.sub(r"^\d+\s*", "", md_path.stem.replace("_", " ").replace("-", " "))
                    parsed.insert(0, {"type": "heading1", "text": clean_title})
                if build_docx_package(target_docx, parsed, config, title=mpath.name, is_full_manuscript=False, source_mtime=md_path.stat().st_mtime):
                    sync_report["md_to_docx"].append(str(target_docx.relative_to(mpath)).replace("\\", "/"))
                    state[stem] = {
                        "md_sha256": get_file_sha256(md_path),
                        "docx_sha256": get_file_sha256(target_docx),
                        "synced_at": datetime.now(timezone.utc).isoformat(),
                    }
                    state_updated = True
            except Exception as e:
                sync_report["errors"].append(f"Error compiling {target_docx}: {e}")

        elif docx_path and not md_path:
            # DOCX exists, MD missing -> Import to MD
            target_md = docx_path.with_suffix(".md")
            try:
                prose = convert_docx_to_markdown(docx_path)
                atomic_write(target_md, prose)
                comments = extract_docx_comments(docx_path)
                if comments:
                    comments_file = target_md.parent / f"{target_md.stem}.comments.json"
                    atomic_write(comments_file, json.dumps({"source": docx_path.name, "comments": comments}, indent=2))
                    sync_report["comments_extracted"].append(str(comments_file.relative_to(mpath)).replace("\\", "/"))
                sync_report["docx_to_md"].append(str(target_md.relative_to(mpath)).replace("\\", "/"))
                state[stem] = {
                    "md_sha256": get_file_sha256(target_md),
                    "docx_sha256": get_file_sha256(docx_path),
                    "synced_at": datetime.now(timezone.utc).isoformat(),
                }
                state_updated = True
            except Exception as e:
                sync_report["errors"].append(f"Error importing {docx_path}: {e}")

        elif md_path and docx_path:
            cur_md_hash = get_file_sha256(md_path)
            cur_docx_hash = get_file_sha256(docx_path)

            md_changed = (stored_md_hash is not None and cur_md_hash != stored_md_hash)
            docx_changed = (stored_docx_hash is not None and cur_docx_hash != stored_docx_hash)

            # Initial baseline when no state was recorded
            if stored_md_hash is None or stored_docx_hash is None:
                md_mtime = md_path.stat().st_mtime
                docx_mtime = docx_path.stat().st_mtime
                if docx_mtime > md_mtime + 2.0:
                    docx_changed = True
                elif md_mtime > docx_mtime + 2.0:
                    md_changed = True
                else:
                    state[stem] = {
                        "md_sha256": cur_md_hash,
                        "docx_sha256": cur_docx_hash,
                        "synced_at": datetime.now(timezone.utc).isoformat(),
                    }
                    state_updated = True
                    continue

            if md_changed and docx_changed:
                # Conflict detected! Do not overwrite either file.
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                conflict_md = md_path.parent / f"{md_path.stem}.conflict_{ts}.md"
                new_prose = convert_docx_to_markdown(docx_path)
                atomic_write(conflict_md, f"<!-- SYNC CONFLICT from {docx_path.name} -->\n\n{new_prose}")
                sync_report["conflicts"].append({
                    "stem": stem,
                    "md_file": str(md_path.relative_to(mpath)).replace("\\", "/"),
                    "docx_file": str(docx_path.relative_to(mpath)).replace("\\", "/"),
                    "conflict_file": str(conflict_md.relative_to(mpath)).replace("\\", "/"),
                })
                logger.warning("Sync conflict on %s: both Markdown and DOCX modified independently.", stem)
            elif docx_changed:
                # DOCX was updated in Word Processor -> Update MD prose while preserving tags & updating title if renamed
                try:
                    old_content = md_path.read_text(encoding="utf-8", errors="replace")
                    _, _, raw_headers = strip_scene_tags_and_frontmatter(old_content)
                    new_prose = convert_docx_to_markdown(docx_path)

                    # Bidirectional Title Sync: check if Heading 1 in Word was changed
                    new_heading = extract_docx_heading1(docx_path)
                    if new_heading and raw_headers:
                        old_h_match = re.search(r"^#\s+([^\r\n]+)", old_content, flags=re.MULTILINE)
                        old_heading = old_h_match.group(1).strip() if old_h_match else ""
                        if old_heading and new_heading.strip() != old_heading.strip():
                            raw_headers = _update_frontmatter_title(raw_headers, new_heading.strip())

                    combined_lines = []
                    if raw_headers:
                        combined_lines.extend(raw_headers)
                        combined_lines.append("")
                    combined_lines.append(new_prose.strip())
                    combined_lines.append("")

                    atomic_write(md_path, "\n".join(combined_lines))
                    comments = extract_docx_comments(docx_path)
                    if comments:
                        comments_file = md_path.parent / f"{md_path.stem}.comments.json"
                        atomic_write(comments_file, json.dumps({"source": docx_path.name, "comments": comments}, indent=2))
                        sync_report["comments_extracted"].append(str(comments_file.relative_to(mpath)).replace("\\", "/"))
                    state[stem] = {
                        "md_sha256": get_file_sha256(md_path),
                        "docx_sha256": cur_docx_hash,
                        "synced_at": datetime.now(timezone.utc).isoformat(),
                    }
                    state_updated = True
                    sync_report["docx_to_md"].append(str(md_path.relative_to(mpath)).replace("\\", "/"))
                except Exception as e:
                    sync_report["errors"].append(f"Error syncing {docx_path} -> {md_path}: {e}")
            elif md_changed:
                # MD was updated in editor -> Rebuild DOCX
                try:
                    content = md_path.read_text(encoding="utf-8", errors="replace")
                    parsed = parse_markdown_to_paragraphs(content)
                    if not any(p["type"] == "heading1" for p in parsed):
                        clean_title = re.sub(r"^\d+\s*", "", md_path.stem.replace("_", " ").replace("-", " "))
                        parsed.insert(0, {"type": "heading1", "text": clean_title})
                    if build_docx_package(docx_path, parsed, config, title=mpath.name, is_full_manuscript=False, source_mtime=md_path.stat().st_mtime):
                        state[stem] = {
                            "md_sha256": cur_md_hash,
                            "docx_sha256": get_file_sha256(docx_path),
                            "synced_at": datetime.now(timezone.utc).isoformat(),
                        }
                        state_updated = True
                        sync_report["md_to_docx"].append(str(docx_path.relative_to(mpath)).replace("\\", "/"))
                except Exception as e:
                    sync_report["errors"].append(f"Error syncing {md_path} -> {docx_path}: {e}")
            else:
                state[stem] = {
                    "md_sha256": cur_md_hash,
                    "docx_sha256": cur_docx_hash,
                    "synced_at": stem_state.get("synced_at") or datetime.now(timezone.utc).isoformat(),
                }

    if state_updated:
        save_sync_state(draft_dir, state)

    # Update consolidated manuscript DOCX
    build_manuscript_docx(mpath, draft_name=draft_dir.name)
    return sync_report


def generate_docx_studio_report(
    manuscript_dir: Path | str,
    draft_name: str | None = None,
    open_browser: bool = False,
    output_html: Path | str | None = None,
) -> Path:
    """Generates the primary offline HTML5 Visual DOCX Studio report for the manuscript."""
    mpath = Path(manuscript_dir).resolve()
    draft_dir = resolve_active_draft_dir(mpath, draft_name)
    state = load_sync_state(draft_dir)

    md_files = {
        f.stem: f
        for f in draft_dir.rglob("*.md")
        if not f.name.startswith(".") and "Outlines" not in f.parts and not f.name.endswith(".comments.json")
    }
    docx_files = {
        f.stem: f
        for f in draft_dir.rglob("*.docx")
        if not f.name.startswith(".")
        and not f.name.startswith("~$")
        and not f.name.startswith(".~lock")
        and not f.stem.endswith("_Manuscript")
    }

    all_stems = sorted(set(md_files.keys()).union(set(docx_files.keys())))
    chapter_rows: list[dict[str, Any]] = []
    all_comments: list[dict[str, Any]] = []

    synced_cnt = 0
    docx_newer_cnt = 0
    md_newer_cnt = 0
    conflicts_cnt = 0

    for stem in all_stems:
        md_p = md_files.get(stem)
        docx_p = docx_files.get(stem)
        stem_state = state.get(stem, {})
        stored_md_h = stem_state.get("md_sha256")
        stored_docx_h = stem_state.get("docx_sha256")

        cur_md_h = get_file_sha256(md_p) if md_p else ""
        cur_docx_h = get_file_sha256(docx_p) if docx_p else ""

        md_w = 0
        docx_w = 0
        title = stem.replace("_", " ")

        if md_p:
            try:
                md_text = md_p.read_text(encoding="utf-8", errors="replace")
                md_w = count_prose_words(md_text)
                h1 = extract_docx_heading1(docx_p) if docx_p else None
                if not h1:
                    first_h = re.search(r"^#\s+(.+)$", md_text, flags=re.MULTILINE)
                    title = first_h.group(1).strip() if first_h else title
                else:
                    title = h1
            except Exception:
                pass

        if docx_p:
            try:
                doc_text = convert_docx_to_markdown(docx_p)
                docx_w = count_prose_words(doc_text)
            except Exception:
                pass

        # Check sidecar comments
        comments_file = (md_p.parent / f"{stem}.comments.json") if md_p else None
        has_comments = False
        if comments_file and comments_file.is_file():
            try:
                c_data = json.loads(comments_file.read_text(encoding="utf-8"))
                for c in c_data.get("comments", []):
                    c["chapter"] = title
                    all_comments.append(c)
                    has_comments = True
            except Exception:
                pass

        # Determine status
        if md_p and not docx_p:
            status = "md_newer"
            md_newer_cnt += 1
        elif docx_p and not md_p:
            status = "docx_newer"
            docx_newer_cnt += 1
        else:
            md_changed = bool(stored_md_h and cur_md_h != stored_md_h)
            docx_changed = bool(stored_docx_h and cur_docx_h != stored_docx_h)
            if md_changed and docx_changed:
                status = "conflict"
                conflicts_cnt += 1
            elif docx_changed:
                status = "docx_newer"
                docx_newer_cnt += 1
            elif md_changed:
                status = "md_newer"
                md_newer_cnt += 1
            else:
                status = "synced"
                synced_cnt += 1

        rel_p = str((md_p or docx_p).relative_to(mpath)).replace("\\", "/") if (md_p or docx_p) else stem
        chapter_rows.append({
            "stem": stem,
            "title": title,
            "rel_path": rel_p,
            "status": status,
            "md_words": md_w,
            "docx_words": docx_w,
            "delta": docx_w - md_w,
            "has_comments": has_comments,
        })

    ms_title = mpath.name
    ms_yaml = mpath / "manuscript.yaml"
    if ms_yaml.is_file():
        try:
            try:
                from lib.frontmatter import parse_yaml_document
            except ImportError:
                from frontmatter import parse_yaml_document
            d = parse_yaml_document(ms_yaml.read_text(encoding="utf-8"))
            if isinstance(d, dict) and d.get("title"):
                ms_title = str(d["title"])
        except Exception:
            pass

    report_payload = {
        "manuscript": ms_title,
        "draft": draft_dir.name,
        "active_preset": get_active_docx_preset_name(),
        "presets": list_docx_presets(),
        "chapters": chapter_rows,
        "comments": all_comments,
        "summary": {
            "total": len(chapter_rows),
            "synced": synced_cnt,
            "docx_newer": docx_newer_cnt,
            "md_newer": md_newer_cnt,
            "conflicts": conflicts_cnt,
        },
    }

    out_file = Path(output_html).resolve() if output_html else draft_dir / "docx_studio.html"
    if render_docx_studio_html:
        render_docx_studio_html(report_payload, output_path=out_file)

    if open_browser and out_file.is_file():
        open_in_word_processor(out_file)

    return out_file


def watch_manuscript_docx(
    manuscript_dir: Path | str,
    draft_name: str | None = None,
    poll_interval: float = 0.5,
    debounce_sec: float = 0.5,
    interactive: bool = False,
    open_studio: bool = False,
    max_iterations: int | None = None,
) -> dict[str, Any]:
    """
    Continuous debounced live file watcher with Windows lock-retry resilience.
    Tracks both .md and .docx files, syncing immediately upon change stability.
    """
    mpath = Path(manuscript_dir).resolve()
    draft_dir = resolve_active_draft_dir(mpath, draft_name)
    logger.info("Starting live DOCX sync watcher on: %s", draft_dir)

    if open_studio:
        generate_docx_studio_report(mpath, draft_name=draft_dir.name, open_browser=True)

    # Initialize file hashes and mtimes
    def _snapshot_files() -> dict[str, tuple[float, str]]:
        snap: dict[str, tuple[float, str]] = {}
        # MD files
        for f in draft_dir.rglob("*.md"):
            if not f.name.startswith(".") and "Outlines" not in f.parts and not f.name.endswith(".comments.json") and not f.name.endswith(".conflict_*.md"):
                snap[str(f)] = (f.stat().st_mtime, get_file_sha256(f))
        # DOCX files (ignoring temporary lockfiles)
        for f in draft_dir.rglob("*.docx"):
            if not f.name.startswith(".") and not f.name.startswith("~$") and not f.name.startswith(".~lock") and not f.stem.endswith("_Manuscript"):
                snap[str(f)] = (f.stat().st_mtime, get_file_sha256(f))
        return snap

    last_snap = _snapshot_files()
    total_syncs = 0
    iterations = 0

    try:
        while True:
            if max_iterations is not None and iterations >= max_iterations:
                break
            iterations += 1
            time.sleep(poll_interval)

            cur_snap = _snapshot_files()
            has_diff = False

            if set(cur_snap.keys()) != set(last_snap.keys()):
                has_diff = True
            else:
                for k, (mtime, sha) in cur_snap.items():
                    if k not in last_snap or last_snap[k][0] != mtime or (sha and last_snap[k][1] != sha):
                        has_diff = True
                        break

            if has_diff:
                # Debounce: wait for Word/Editor write completion
                time.sleep(debounce_sec)
                logger.info("[↻] Changes detected. Executing synchronization...")
                sync_res = sync_manuscript_docx(mpath, draft_name=draft_dir.name, interactive=interactive)
                total_syncs += 1
                last_snap = _snapshot_files()
                logger.info(
                    "[✓] Sync complete: %d MD->DOCX, %d DOCX->MD, %d conflicts.",
                    len(sync_res["md_to_docx"]),
                    len(sync_res["docx_to_md"]),
                    len(sync_res["conflicts"]),
                )

    except KeyboardInterrupt:
        logger.info("Watcher terminated by user.")

    return {
        "status": "stopped",
        "manuscript": mpath.name,
        "draft": draft_dir.name,
        "iterations": iterations,
        "total_syncs": total_syncs,
    }


def open_in_word_processor(file_path: Path | str, watch: bool = False) -> bool:
    """Launches the specified DOCX or HTML document in the default word processor / browser."""
    fpath = Path(file_path).resolve()
    if not fpath.is_file():
        logger.error("File does not exist: %s", fpath)
        return False

    try:
        if sys.platform.startswith("win"):
            os.startfile(str(fpath))  # noqa: S606
            if watch:
                watch_manuscript_docx(fpath.parent)
            return True
        if sys.platform.startswith("darwin"):
            subprocess.Popen(["open", str(fpath)])
            if watch:
                watch_manuscript_docx(fpath.parent)
            return True
        # Linux: Check for LibreOffice Writer / browser
        if fpath.suffix.lower() == ".html" and shutil.which("xdg-open"):
            subprocess.Popen(["xdg-open", str(fpath)])
            return True
        if shutil.which("libreoffice"):
            subprocess.Popen(["libreoffice", "--writer", str(fpath)])
            if watch:
                watch_manuscript_docx(fpath.parent)
            return True
        if shutil.which("xdg-open"):
            subprocess.Popen(["xdg-open", str(fpath)])
            if watch:
                watch_manuscript_docx(fpath.parent)
            return True
    except Exception as e:
        logger.error("Failed to launch application for %s: %s", fpath, e)

    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Ars Arcanum DOCX Synchronization & Typesetting Engine")
    subparsers = parser.add_subparsers(dest="subcommand")

    # studio (default visual entry point)
    studio_p = subparsers.add_parser("studio", help="Generate and open the Visual DOCX Studio dashboard")
    studio_p.add_argument("manuscript", nargs="?", default=".", help="Path to manuscript directory")
    studio_p.add_argument("-d", "--draft", help="Specific draft name (e.g. Draft-01)")
    studio_p.add_argument("--no-open", action="store_true", help="Do not automatically launch in default browser")
    studio_p.add_argument("-o", "--output", help="Custom path for generated HTML studio")

    # watch (live debounced background sync)
    watch_p = subparsers.add_parser("watch", help="Start live debounced continuous sync watcher")
    watch_p.add_argument("manuscript", nargs="?", default=".", help="Path to manuscript directory")
    watch_p.add_argument("-d", "--draft", help="Specific draft name")
    watch_p.add_argument("--interval", type=float, default=0.5, help="Poll interval in seconds")
    watch_p.add_argument("--debounce", type=float, default=0.5, help="Debounce delay in seconds")
    watch_p.add_argument("--studio", action="store_true", help="Open Visual Studio alongside watcher")

    # build
    build_p = subparsers.add_parser("build", help="Build/refresh .docx files for manuscript")
    build_p.add_argument("manuscript", nargs="?", default=".", help="Path to manuscript directory")
    build_p.add_argument("-d", "--draft", help="Specific draft name (e.g. Draft-01, Draft-02)")
    build_p.add_argument("-p", "--preset", help="Typesetting preset name (chicago-manual, standard-submission, modern-manuscript, classic-trade)")
    add_scope_arguments(build_p, include_world=False, include_manuscript=False, target_pos_arg=False)

    # sync
    sync_p = subparsers.add_parser("sync", help="Bidirectional sync between .docx and .md")
    sync_p.add_argument("manuscript", nargs="?", default=".", help="Path to manuscript directory")
    sync_p.add_argument("-d", "--draft", help="Specific draft name (e.g. Draft-01)")
    sync_p.add_argument("-i", "--interactive", action="store_true", help="Interactive review mode")
    sync_p.add_argument("--diff", action="store_true", help="Launch visual diff before applying sync")

    # presets
    preset_p = subparsers.add_parser("presets", help="Inspect or change active typesetting presets")
    preset_p.add_argument("action", nargs="?", default="list", choices=["list", "set"], help="Preset action")
    preset_p.add_argument("name", nargs="?", help="Preset name to activate")

    # import
    import_p = subparsers.add_parser("import", help="Import external .docx into clean Markdown")
    import_p.add_argument("docx_file", help="Path to source .docx file")
    import_p.add_argument("--to", required=True, help="Target markdown file path")

    # open
    open_p = subparsers.add_parser("open", help="Open manuscript in default word processor")
    open_p.add_argument("manuscript", nargs="?", default=".", help="Path to manuscript directory")
    open_p.add_argument("-d", "--draft", help="Specific draft name")
    open_p.add_argument("-c", "--chapter", help="Specific chapter file name or path")
    open_p.add_argument("-w", "--watch", action="store_true", help="Start background watcher alongside word processor")

    args = parser.parse_args()

    if not args.subcommand or args.subcommand in ("studio", "ui", "dashboard"):
        ms_arg = getattr(args, "manuscript", ".") or "."
        ms_p = resolve_manuscript_path(ms_arg) or Path(ms_arg)
        out_html = getattr(args, "output", None)
        no_open = getattr(args, "no_open", False)
        report_p = generate_docx_studio_report(ms_p, draft_name=getattr(args, "draft", None), open_browser=not no_open, output_html=out_html)
        print(f"🏛️ Visual DOCX Studio generated at: {report_p}")
        sys.exit(0)

    scope = parse_scope_args(args)

    if args.subcommand == "watch":
        ms_p = resolve_manuscript_path(args.manuscript) or Path(args.manuscript)
        watch_manuscript_docx(
            ms_p,
            draft_name=args.draft,
            poll_interval=args.interval,
            debounce_sec=args.debounce,
            open_studio=args.studio,
        )
        sys.exit(0)

    elif args.subcommand == "build":
        ms_p = resolve_manuscript_path(args.manuscript) or Path(args.manuscript)
        res = build_manuscript_docx(ms_p, draft_name=args.draft, preset_name=args.preset, scope=scope)
        print("=== Ars Arcanum DOCX Build ===")
        print(f"Manuscript: {res['manuscript']} ({res['draft']})")
        print(f"Chapters Built: {len(res['chapters_built'])}")
        if res['consolidated_built']:
            print(f"Consolidated Draft: {res['consolidated_built']}")
        if res['errors']:
            print(f"Errors: {len(res['errors'])}")
            for err in res['errors']:
                print(f"  [!] {err}")
            sys.exit(1)
        sys.exit(0)

    elif args.subcommand == "sync":
        ms_p = resolve_manuscript_path(args.manuscript) or Path(args.manuscript)
        res = sync_manuscript_docx(ms_p, draft_name=args.draft, interactive=args.interactive, visual_diff=args.diff)
        print("=== Ars Arcanum DOCX Sync ===")
        print(f"Manuscript: {res['manuscript']} ({res['draft']})")
        print(f"Markdown -> DOCX Updated: {len(res['md_to_docx'])}")
        print(f"DOCX -> Markdown Updated: {len(res['docx_to_md'])}")
        if res['comments_extracted']:
            print(f"Comments Extracted: {len(res['comments_extracted'])}")
        if res['conflicts']:
            print(f"Conflicts: {len(res['conflicts'])}")
        if res['errors']:
            print(f"Errors: {len(res['errors'])}")
            for err in res['errors']:
                print(f"  [!] {err}")
            sys.exit(1)
        sys.exit(0)

    elif args.subcommand == "presets":
        if args.action == "set":
            if not args.name:
                print("Error: Specify preset name to activate.", file=sys.stderr)
                sys.exit(2)
            if set_docx_preset(args.name):
                print(f"✓ Active DOCX preset set to: {args.name}")
                sys.exit(0)
            else:
                print(f"Error: Unknown preset '{args.name}'", file=sys.stderr)
                sys.exit(1)
        else:
            active = get_active_docx_preset_name()
            presets_map = list_docx_presets()
            print("=== Ars Arcanum Typesetting Presets ===")
            for k, v in presets_map.items():
                cur = " (ACTIVE)" if k == active else ""
                print(f"  • {k:<22}{cur}: {v['name']} — {v['description']}")
            sys.exit(0)

    elif args.subcommand == "import":
        try:
            prose = convert_docx_to_markdown(Path(args.docx_file))
            target_path = Path(args.to)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            atomic_write(target_path, prose)
            print(f"[✓] Successfully imported {args.docx_file} -> {args.to}")
            sys.exit(0)
        except Exception as e:
            print(f"[!] Error importing DOCX: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.subcommand == "open":
        mpath = Path(args.manuscript).resolve()
        draft_dir = resolve_active_draft_dir(mpath, args.draft)
        target_file = None

        if args.chapter:
            ch_candidates = list(draft_dir.rglob(f"*{args.chapter}*.docx"))
            if ch_candidates:
                target_file = ch_candidates[0]

        if not target_file:
            # Check consolidated draft docx
            cons = list(draft_dir.glob("*_Manuscript.docx"))
            if cons:
                target_file = cons[0]
            else:
                docxs = [f for f in draft_dir.rglob("*.docx") if not f.name.startswith("~$")]
                if docxs:
                    target_file = docxs[0]

        if target_file and target_file.is_file():
            print(f"Launching word processor for: {target_file}")
            if open_in_word_processor(target_file, watch=args.watch):
                sys.exit(0)
            else:
                sys.exit(1)
        else:
            # Build first if missing
            print("No .docx files found. Generating .docx package first...")
            build_manuscript_docx(mpath, draft_name=args.draft)
            cons = list(draft_dir.glob("*_Manuscript.docx"))
            if cons:
                open_in_word_processor(cons[0], watch=args.watch)
                sys.exit(0)
            sys.exit(1)


if __name__ == "__main__":
    main()
