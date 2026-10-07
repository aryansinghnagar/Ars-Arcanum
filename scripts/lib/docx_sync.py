#!/usr/bin/env python3
"""
Ars Arcanum DOCX Synchronization & Typesetting Engine (scripts/lib/docx_sync.py)
================================================================================
Bidirectional Word processor synchronization and native OpenXML manuscript generator.
Enables authors to draft, review, and edit manuscripts seamlessly in Microsoft Word,
Google Docs, and LibreOffice Writer while preserving Markdown integrity.

Zero external dependencies; operates 100% offline.
"""

import argparse
import hashlib
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from lib._bootstrap import atomic_write
    from lib.scope import (
        EngineScope,
        add_scope_arguments,
        filter_manuscript_scope,
        parse_scope_args,
        resolve_manuscript_path,
    )
except ImportError:
    from _bootstrap import atomic_write
    from scope import (
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
    from lib.config import get_active_docx_preset_name, get_docx_config
except Exception:
    try:
        from config import get_active_docx_preset_name, get_docx_config
    except Exception:
        def get_docx_config():
            return {
                "name": "Standard Submission (Shunn / Industry)",
                "font_family": "Times New Roman",
                "font_size_pt": 12.0,
                "line_spacing": 2.0,
                "margin_inches": 1.0,
                "first_line_indent_inches": 0.5,
                "scene_break_symbol": "#",
                "page_break_chapters": True,
                "include_header_slug": True,
            }
        def get_active_docx_preset_name():
            return "standard-submission"


try:
    from lib.docx_builder import (
        FRONTMATTER_REGEX,
        MD_BOLD_ITALIC_REGEX,
        NW_TAG_REGEX,
        build_docx_package,
        escape_xml,
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
        format_runs_xml,
        generate_docx_xml_body,
        inches_to_dxa,
        line_spacing_to_val,
        parse_markdown_to_paragraphs,
        pt_to_half_pt,
        strip_scene_tags_and_frontmatter,
    )


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
    "format_runs_xml",
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

    if docx_path.stat().st_size > MAX_DOCX_FILE_BYTES:
        raise ValueError(f"DOCX file exceeds maximum allowed size ({MAX_DOCX_FILE_BYTES // (1024*1024)} MB): {docx_path}")

    try:
        with zipfile.ZipFile(docx_path, "r") as zf:
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
                raise ValueError("Unsafe XML entity/DOCTYPE declaration detected in DOCX document.xml")

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
            elif p_text in ("#", "* * *", "***", "---"):
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
) -> dict:
    """Builds both per-chapter .docx files and consolidated draft .docx files for a manuscript."""
    mpath = Path(manuscript_dir).resolve()
    draft_dir = resolve_active_draft_dir(mpath, draft_name)
    config = get_docx_config()

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

    results = {
        "manuscript": mpath.name,
        "draft": draft_dir.name,
        "chapters_built": [],
        "consolidated_built": None,
        "errors": []
    }

    consolidated_paragraphs = []

    # Find all Markdown scenes
    md_files = sorted(draft_dir.rglob("*.md"))
    valid_scenes = [f for f in md_files if not f.name.startswith(".") and "Outlines" not in f.parts]

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
                # Strip leading numbers (e.g. 01 Chapter 01 -> Chapter 01)
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
    """Calculates SHA-256 hash of a file."""
    if not path.is_file():
        return ""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def load_sync_state(draft_dir: Path) -> dict:
    state_file = draft_dir / ".sync_state.json"
    if state_file.is_file():
        try:
            with open(state_file, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.debug("Failed to read sync state %s: %s", state_file, e)
    return {}


def save_sync_state(draft_dir: Path, state: dict) -> None:
    state_file = draft_dir / ".sync_state.json"
    atomic_write(state_file, json.dumps(state, indent=2))


def sync_manuscript_docx(manuscript_dir: Path, draft_name: str | None = None) -> dict:
    """Performs 3-way hash-verified bidirectional synchronization between .md and .docx files."""
    mpath = Path(manuscript_dir).resolve()
    draft_dir = resolve_active_draft_dir(mpath, draft_name)
    config = get_docx_config()

    sync_report = {
        "manuscript": mpath.name,
        "draft": draft_dir.name,
        "md_to_docx": [],
        "docx_to_md": [],
        "comments_extracted": [],
        "conflicts": [],
        "errors": []
    }

    state = load_sync_state(draft_dir)
    state_updated = False

    # 1. Discover all pairs
    md_files = {f.stem: f for f in draft_dir.rglob("*.md") if not f.name.startswith(".") and "Outlines" not in f.parts}
    docx_files = {f.stem: f for f in draft_dir.rglob("*.docx") if not f.name.startswith(".") and not f.stem.endswith("_Manuscript")}

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
                        "synced_at": datetime.now(timezone.utc).isoformat()
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
                    "synced_at": datetime.now(timezone.utc).isoformat()
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
                        "synced_at": datetime.now(timezone.utc).isoformat()
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
                    "conflict_file": str(conflict_md.relative_to(mpath)).replace("\\", "/")
                })
                logger.warning("Sync conflict on %s: both Markdown and DOCX modified independently.", stem)
            elif docx_changed:
                # DOCX was updated in Word Processor -> Update MD prose while preserving tags
                try:
                    old_content = md_path.read_text(encoding="utf-8", errors="replace")
                    _, _, raw_headers = strip_scene_tags_and_frontmatter(old_content)
                    new_prose = convert_docx_to_markdown(docx_path)

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
                        "synced_at": datetime.now(timezone.utc).isoformat()
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
                            "synced_at": datetime.now(timezone.utc).isoformat()
                        }
                        state_updated = True
                        sync_report["md_to_docx"].append(str(docx_path.relative_to(mpath)).replace("\\", "/"))
                except Exception as e:
                    sync_report["errors"].append(f"Error syncing {md_path} -> {docx_path}: {e}")
            else:
                state[stem] = {
                    "md_sha256": cur_md_hash,
                    "docx_sha256": cur_docx_hash,
                    "synced_at": stem_state.get("synced_at") or datetime.now(timezone.utc).isoformat()
                }

    if state_updated:
        save_sync_state(draft_dir, state)

    # Update consolidated manuscript DOCX
    build_manuscript_docx(mpath, draft_name=draft_dir.name)
    return sync_report


def open_in_word_processor(file_path: Path) -> bool:
    """Launches the specified DOCX document in the default word processor."""
    fpath = Path(file_path).resolve()
    if not fpath.is_file():
        logger.error("File does not exist: %s", fpath)
        return False

    try:
        if sys.platform.startswith("win"):
            os.startfile(str(fpath))  # noqa: S606
            return True
        if sys.platform.startswith("darwin"):
            subprocess.Popen(["open", str(fpath)])
            return True
        # Linux: Check for LibreOffice Writer / word processor
        if shutil.which("libreoffice"):
            subprocess.Popen(["libreoffice", "--writer", str(fpath)])
            return True
        if shutil.which("xdg-open"):
            subprocess.Popen(["xdg-open", str(fpath)])
            return True
    except Exception as e:
        logger.error("Failed to launch word processor for %s: %s", fpath, e)

    return False


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum DOCX Synchronization & Typesetting Engine")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # build
    build_p = subparsers.add_parser("build", help="Build/refresh .docx files for manuscript")
    build_p.add_argument("manuscript", help="Path to manuscript directory")
    build_p.add_argument("-d", "--draft", help="Specific draft name (e.g. Draft-01, Draft-02)")
    add_scope_arguments(build_p, include_world=False, include_manuscript=False, target_pos_arg=False)

    # sync
    sync_p = subparsers.add_parser("sync", help="Bidirectional sync between .docx and .md")
    sync_p.add_argument("manuscript", help="Path to manuscript directory")
    sync_p.add_argument("-d", "--draft", help="Specific draft name (e.g. Draft-01)")

    # import
    import_p = subparsers.add_parser("import", help="Import external .docx into clean Markdown")
    import_p.add_argument("docx_file", help="Path to source .docx file")
    import_p.add_argument("--to", required=True, help="Target markdown file path")

    # open
    open_p = subparsers.add_parser("open", help="Open manuscript in default word processor")
    open_p.add_argument("manuscript", help="Path to manuscript directory")
    open_p.add_argument("-d", "--draft", help="Specific draft name")
    open_p.add_argument("-c", "--chapter", help="Specific chapter file name or path")

    args = parser.parse_args()
    scope = parse_scope_args(args)

    if args.subcommand == "build":
        ms_p = resolve_manuscript_path(args.manuscript) or Path(args.manuscript)
        res = build_manuscript_docx(ms_p, draft_name=args.draft, scope=scope)
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
        res = sync_manuscript_docx(Path(args.manuscript), draft_name=args.draft)
        print("=== Ars Arcanum DOCX Sync ===")
        print(f"Manuscript: {res['manuscript']} ({res['draft']})")
        print(f"Markdown -> DOCX Updated: {len(res['md_to_docx'])}")
        print(f"DOCX -> Markdown Updated: {len(res['docx_to_md'])}")
        if res['errors']:
            print(f"Errors: {len(res['errors'])}")
            for err in res['errors']:
                print(f"  [!] {err}")
            sys.exit(1)
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
                docxs = list(draft_dir.rglob("*.docx"))
                if docxs:
                    target_file = docxs[0]

        if target_file and target_file.is_file():
            print(f"Launching word processor for: {target_file}")
            if open_in_word_processor(target_file):
                sys.exit(0)
            else:
                sys.exit(1)
        else:
            # Build first if missing
            print("No .docx files found. Generating .docx package first...")
            build_manuscript_docx(mpath, draft_name=args.draft)
            cons = list(draft_dir.glob("*_Manuscript.docx"))
            if cons:
                open_in_word_processor(cons[0])
                sys.exit(0)
            sys.exit(1)


if __name__ == "__main__":
    main()
