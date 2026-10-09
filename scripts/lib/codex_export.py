#!/usr/bin/env python3
"""
Ars Arcanum Static World Wiki & Lore Codex Exporter (scripts/lib/codex_export.py)
================================================================================
Zero-dependency, offline static site generator compiling Obsidian World Bibles
into a sovereign, searchable encyclopedia and reader codex.

Capabilities (WOR-102):
1. World Bible Vault Scanning & Categorization:
   - Scans Characters/, Locations/, Factions/, Artifacts/, Bestiary/, Cosmology/,
     Languages/, MagicSystems/, and History/ via CachedDataAccess.
2. Markdown to Styled HTML Conversion:
   - Resolves Obsidian Wikilinks [[Target]] and [[Target|Label]] to internal links.
   - Parses YAML frontmatter into rich Infobox cards with trait badges.
3. Offline Client-Side Search & Multi-Theme:
   - Inlined vanilla JavaScript inverted index search.
   - Dark, Light, and Classic Sepia reading themes.
"""

from __future__ import annotations

import argparse
import html
import json
import logging
import re
import sys
from pathlib import Path
from typing import Any

try:
    from lib.codex_export_template import render_codex_html
    from lib.data_access import get_data_access
    from lib.scope import (
        EngineScope,
        add_scope_arguments,
        parse_scope_args,
        resolve_world_path,
    )
except ImportError:
    from codex_export_template import render_codex_html
    from data_access import get_data_access
    from scope import (
        EngineScope,
        add_scope_arguments,
        parse_scope_args,
        resolve_world_path,
    )

logger = logging.getLogger("arcanum.codex_export")

TAXONOMIES = [
    "Characters",
    "Locations",
    "Factions",
    "Artifacts",
    "Bestiary",
    "Cosmology",
    "Languages",
    "MagicSystems",
    "History",
]


def _md_to_styled_html(raw_body: str) -> str:
    """Converts markdown body to clean HTML with wikilinks and basic styling."""
    escaped_body = html.escape(raw_body)

    # Convert wikilinks: [[Target|Label]] -> <a href="#Target">Label</a>
    def _sub_wikilink(m: re.Match) -> str:
        target = m.group(1).strip()
        label = m.group(2).strip() if m.group(2) else target
        clean_target = html.unescape(target).replace(" ", "_")
        clean_id = re.sub(r"[^\w\-]", "", clean_target)
        return f'<a href="#{clean_id}" class="wikilink">{label}</a>'

    body_html = re.sub(r"\[\[([^\|\]]+)(?:\|([^\]]+))?\]\]", _sub_wikilink, escaped_body)

    # Basic markdown headings
    body_html = re.sub(r"^###\s+(.*)$", r"<h3>\1</h3>", body_html, flags=re.MULTILINE)
    body_html = re.sub(r"^##\s+(.*)$", r"<h2>\1</h2>", body_html, flags=re.MULTILINE)
    body_html = re.sub(r"^#\s+(.*)$", r"<h1>\1</h1>", body_html, flags=re.MULTILINE)

    # Bold and italics
    body_html = re.sub(r"\*\*\*(.*?)\*\*\*", r"<strong><em>\1</em></strong>", body_html)
    body_html = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", body_html)
    body_html = re.sub(r"\*(.*?)\*", r"<em>\1</em>", body_html)

    # Paragraphs
    paragraphs = body_html.split("\n\n")
    p_tags = []
    for p in paragraphs:
        p_clean = p.strip()
        if not p_clean:
            continue
        if p_clean.startswith("<h"):
            p_tags.append(p_clean)
        else:
            p_tags.append(f"<p>{p_clean.replace(chr(10), '<br>')}</p>")

    return "\n".join(p_tags)


def _md_to_basic_html(md_text: str) -> tuple[str, dict[str, Any]]:
    """Converts markdown text to clean HTML and extracts YAML frontmatter (backward compatibility)."""
    try:
        from lib.frontmatter import extract_frontmatter_and_body
    except ImportError:
        from frontmatter import extract_frontmatter_and_body  # type: ignore[no-redef]
    fm, body = extract_frontmatter_and_body(md_text)
    return _md_to_styled_html(body), fm


def scan_world_vault(
    world_dir: Path,
    scope: EngineScope | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Scans world vault notes grouped by taxonomy using CachedDataAccess."""
    dal = get_data_access()
    categories: dict[str, list[dict[str, Any]]] = {}

    target_taxonomies = TAXONOMIES
    if scope and scope.lore_categories:
        cat_lowers = {c.lower() for c in scope.lore_categories}
        target_taxonomies = [t for t in TAXONOMIES if t.lower() in cat_lowers]

    for tax in target_taxonomies:
        tax_dir = world_dir / tax
        items: list[dict[str, Any]] = []
        if tax_dir.is_dir():
            files = dal.list_files(tax_dir, recursive=False)
            for f in files:
                fm, body = dal.parse_frontmatter(f)
                title = fm.get("name") or fm.get("title") or f.stem.replace("_", " ")
                clean_id = re.sub(r"[^a-zA-Z0-9_\-]", "", f.stem)
                body_html = _md_to_styled_html(body)
                items.append({
                    "id": clean_id,
                    "clean_id": clean_id,
                    "title": str(title),
                    "taxonomy": tax,
                    "tax": tax,
                    "filename": f.name,
                    "frontmatter": fm,
                    "html": body_html,
                    "html_content": body_html,
                    "raw_body": body,
                    "raw_text": body[:300],
                })
        if items:
            categories[tax] = items

    return categories


def build_single_file_codex(
    categories: dict[str, list[dict[str, Any]]],
    world_name: str,
    output_path: Path,
) -> Path:
    """Builds a single standalone offline HTML file containing the complete world codex."""
    return render_codex_html(categories, world_name=world_name, output_path=output_path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ars Arcanum Static World Wiki Codex Exporter (WOR-102)")
    parser.add_argument("world", nargs="?", help="World Lore Vault directory path")
    parser.add_argument("-o", "--output", help="Output file path (default: <world_name>_codex.html)")
    parser.add_argument("--html", help="Generate HTML codex export at path")
    parser.add_argument("--json", action="store_true", help="Output JSON vault taxonomy index")
    add_scope_arguments(parser, include_manuscript=False, target_pos_arg=False)
    args = parser.parse_args(argv)

    scope = parse_scope_args(args)
    raw_world = args.world or scope.world
    world_dir = (
        str(resolve_world_path(raw_world, scope=scope))
        if resolve_world_path(raw_world, scope=scope)
        else (raw_world or "")
    )

    world_path = Path(world_dir) if world_dir else Path("")
    if not world_path.is_dir():
        print(f"Error: World directory not found: {world_path}", file=sys.stderr)
        return 1

    categories = scan_world_vault(world_path, scope=scope)

    if args.json:
        print(json.dumps({tax: len(items) for tax, items in categories.items()}, indent=2))
        return 0

    out_file = Path(args.html or args.output or f"{world_path.name}_codex.html")
    build_single_file_codex(categories, world_name=world_path.name, output_path=out_file)

    total_articles = sum(len(items) for items in categories.values())
    print("=== Ars Arcanum Static Codex Exporter ===")
    print(f"World:          {world_path.name}")
    print(f"Total Articles: {total_articles} across {len(categories)} categories")
    print(f"Generated:      {out_file} ({out_file.stat().st_size:,} bytes)")
    return 0


__all__ = [
    "TAXONOMIES",
    "build_single_file_codex",
    "main",
    "scan_world_vault",
]

if __name__ == "__main__":
    sys.exit(main())
