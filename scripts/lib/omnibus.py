#!/usr/bin/env python3
"""
Ars Arcanum Multi-Volume Series Omnibus Compiler
(scripts/lib/omnibus.py)
================================================================================
Zero-dependency, offline multi-volume series compilation engine for epic fantasy,
sci-fi sagas, serial fiction, and multi-book universe bundles.

Capabilities:
1. Multi-Book Discovery & Sequence Resolution:
   - Scans Universe, Cosmos, and Manuscript directories for volumes (`Book-01`, `Book-02`...).
   - Resolves latest active revision drafts (`Draft-01`, `Draft-02`...).
2. Unified Series Lore & Structure Synthesis:
   - Compiles master Series Table of Contents with volume subtitle partitions.
   - Synthesizes a unified cross-volume Dramatis Personae with character debut/arc tracking.
   - Generates a combined Master Chronology Appendix.
   - Computes series-wide POV distribution and pacing metrics.
3. Master Omnibus Assembly:
   - Produces clean, unified Markdown master document (`*_Omnibus.md`).
   - Generates standalone, offline interactive HTML5 Omnibus Reader via omnibus_template.
   - Outputs machine-readable series manifest (`omnibus_manifest.json`).
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

try:
    from lib._bootstrap import atomic_write, count_prose_words
    from lib.data_access import get_data_access
    from lib.frontmatter import parse_yaml_frontmatter
    from lib.omnibus_template import render_omnibus_html
    from lib.scope import (
        EngineScope,
        add_scope_arguments,
        filter_manuscript_scope,
        parse_number_ranges,
        parse_scope_args,
        resolve_manuscript_path,
        resolve_universe_path,
    )
except ImportError:
    from _bootstrap import atomic_write, count_prose_words
    from data_access import get_data_access
    from frontmatter import parse_yaml_frontmatter
    from omnibus_template import render_omnibus_html
    from scope import (
        EngineScope,
        add_scope_arguments,
        filter_manuscript_scope,
        parse_number_ranges,
        parse_scope_args,
        resolve_manuscript_path,
        resolve_universe_path,
    )

logger = logging.getLogger("arcanum.omnibus")

FRONTMATTER_REGEX = re.compile(r"^---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)", re.DOTALL)
TAG_REGEX = re.compile(r"^@([a-zA-Z0-9_-]+):\s*(.*)$")


@dataclass
class VolumeData:
    index: int
    name: str
    title: str
    draft_name: str
    path: str
    chapters: list[dict[str, Any]] = field(default_factory=list)
    word_count: int = 0
    povs: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def discover_series_volumes(target_path: Path, scope: EngineScope | None = None) -> list[VolumeData]:
    """Discovers all volumes/books within a universe, cosmos, or manuscript directory."""
    dal = get_data_access()
    volumes: list[VolumeData] = []

    # Check if target is a universe containing Manuscripts/
    manuscripts_dir = target_path / "Manuscripts" if (target_path / "Manuscripts").is_dir() else target_path

    # Search for Book-XX directories or sub-manuscripts
    book_dirs = []
    for item in sorted(manuscripts_dir.rglob("Book-*")):
        if item.is_dir() and "Backups" not in item.parts:
            book_dirs.append(item)

    # Fallback: if no Book-* directories, look for immediate draft folders
    if not book_dirs:
        for item in sorted(manuscripts_dir.rglob("Draft-*")):
            if item.is_dir() and "Backups" not in item.parts:
                book_dirs.append(item.parent)
                break

    # If still empty and target contains .md files directly
    if not book_dirs and list(target_path.glob("*.md")):
        book_dirs.append(target_path)

    # De-duplicate while preserving order
    seen = set()
    unique_books = []
    for b in book_dirs:
        if str(b) not in seen:
            seen.add(str(b))
            unique_books.append(b)

    # Filter books by scope if provided
    if scope and scope.books:
        book_nums = parse_number_ranges(scope.books)
        book_names = [b.lower() for b in scope.books if not str(b).isdigit() and "-" not in str(b)]
        filtered_unique = []
        for v_idx, b_dir in enumerate(unique_books, 1):
            v_name_lower = b_dir.name.lower()
            if v_idx in book_nums:
                filtered_unique.append(b_dir)
                continue
            extracted_nums = [int(n) for n in re.findall(r"\d+", b_dir.name)]
            if any(n in book_nums for n in extracted_nums):
                filtered_unique.append(b_dir)
                continue
            if any(b_name in v_name_lower for b_name in book_names):
                filtered_unique.append(b_dir)
                continue
        if filtered_unique:
            unique_books = filtered_unique

    for idx, b_dir in enumerate(unique_books, 1):
        # Find latest draft directory
        draft_dirs = sorted([d for d in b_dir.glob("Draft-*") if d.is_dir()], reverse=True)
        active_draft = draft_dirs[0] if draft_dirs else b_dir

        chapters = []
        vol_words = 0
        vol_povs = set()

        raw_ch_files = sorted(active_draft.rglob("*.md"))
        ch_files = [
            f
            for f in raw_ch_files
            if not f.name.startswith((".", "_")) and "Backups" not in f.parts and "04_Back_Matter" not in f.parts
        ]

        if scope:
            scoped_chaps, _, _ = filter_manuscript_scope(active_draft, scope)
            if scoped_chaps:
                scoped_paths = {c.file_path for c in scoped_chaps if c.file_path}
                ch_files = [f for f in ch_files if f in scoped_paths]

        for ch_file in ch_files:
            content = dal.read_file(ch_file)
            words = count_prose_words(content)
            vol_words += words

            meta = parse_yaml_frontmatter(content)
            body = FRONTMATTER_REGEX.sub("", content)
            pov = meta.get("pov", meta.get("character", ""))

            for line in body.splitlines():
                m = TAG_REGEX.match(line.strip())
                if m and m.group(1).lower() == "pov" and not pov:
                    pov = m.group(2).strip()

            if pov:
                vol_povs.add(pov)

            clean_body = re.sub(r"^@[a-zA-Z0-9_-]+:.*$", "", body, flags=re.MULTILINE).strip()

            title = meta.get("title", ch_file.stem.replace("_", " ").replace("-", " "))
            clean_title = re.sub(r"^\d+\s*[-_.]*\s*", "", title).title()

            chapters.append({
                "filename": ch_file.name,
                "path": str(ch_file),
                "title": clean_title or ch_file.stem,
                "pov": pov or "Omniscient",
                "words": words,
                "body": clean_body,
            })

        vol_name = b_dir.name
        vol_title = vol_name.replace("_", " ").replace("-", " ").title()

        volumes.append(
            VolumeData(
                index=idx,
                name=vol_name,
                title=vol_title,
                draft_name=active_draft.name,
                path=str(b_dir),
                chapters=chapters,
                word_count=vol_words,
                povs=sorted(vol_povs),
            )
        )

    return volumes


def compile_omnibus_manuscript(
    volumes: list[VolumeData],
    series_title: str = "Series Omnibus",
    author: str = "Author",
) -> dict[str, Any]:
    """Compiles discovered volumes into a master omnibus document and metadata."""
    total_words = sum(v.word_count for v in volumes)
    total_chapters = sum(len(v.chapters) for v in volumes)

    # Master Dramatis Personae
    char_appearances: dict[str, list[str]] = {}
    for v in volumes:
        for ch in v.chapters:
            pov = ch["pov"]
            if pov and pov != "Omniscient":
                clean_pov = pov.replace("[[", "").replace("]]", "").strip()
                if clean_pov not in char_appearances:
                    char_appearances[clean_pov] = []
                if v.title not in char_appearances[clean_pov]:
                    char_appearances[clean_pov].append(v.title)

    # Markdown assembly
    md_lines = [
        "---",
        f"title: {json.dumps(series_title)}",
        f"author: {json.dumps(author)}",
        f"volumes_count: {len(volumes)}",
        f"total_word_count: {total_words}",
        "---",
        "",
        f"# {series_title}",
        f"### By {author}",
        "",
        "---",
        "",
        "## Table of Contents",
        "",
    ]

    for v in volumes:
        md_lines.append(f"- **Volume {v.index}: {v.title}** ({v.word_count:,} words)")
        for ch_idx, ch in enumerate(v.chapters, 1):
            md_lines.append(f"  - Chapter {ch_idx}: {ch['title']}")

    md_lines.extend([
        "",
        "---",
        "",
        "## Dramatis Personae (Series Master Ledger)",
        "",
    ])

    for char_name, vols in sorted(char_appearances.items()):
        md_lines.append(f"- **{char_name}** — Appears in: *{', '.join(vols)}*")

    md_lines.extend(["", "---", ""])

    # Append book chapters
    for v in volumes:
        md_lines.extend([
            f"# Volume {v.index}: {v.title}",
            "",
        ])
        for ch_idx, ch in enumerate(v.chapters, 1):
            md_lines.extend([
                f"## Chapter {ch_idx}: {ch['title']}",
                "",
                ch["body"],
                "",
                "---",
                "",
            ])

    full_markdown = "\n".join(md_lines)

    return {
        "title": series_title,
        "author": author,
        "total_words": total_words,
        "total_volumes": len(volumes),
        "total_chapters": total_chapters,
        "volumes": [v.to_dict() for v in volumes],
        "dramatis_personae": char_appearances,
        "markdown_content": full_markdown,
    }


def generate_omnibus_html_reader(omnibus_report: dict[str, Any], output_path: Path | str) -> Path:
    """Generates an offline HTML5 Omnibus Reader."""
    return render_omnibus_html(omnibus_report, output_path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ars Arcanum Multi-Volume Series Omnibus Compiler")
    parser.add_argument("target", help="Universe, Cosmos, or Manuscript directory")
    parser.add_argument("--output", "-o", help="Output directory or file path")
    parser.add_argument("--title", default="Series Master Omnibus", help="Title for the compiled omnibus")
    parser.add_argument("--author", default="Author", help="Author name")
    parser.add_argument("--html", help="Generate HTML5 reader document to path")
    parser.add_argument("--json", action="store_true", help="Output manifest JSON")
    add_scope_arguments(parser, include_world=False, include_manuscript=False, target_pos_arg=False)
    args = parser.parse_args(argv)

    scope = parse_scope_args(args)
    target_path = resolve_manuscript_path(args.target) or resolve_universe_path(args.target) or Path(args.target)
    if not target_path.exists():
        print(f"Error: Target path does not exist: {target_path}", file=sys.stderr)
        sys.exit(1)

    volumes = discover_series_volumes(target_path, scope=scope)
    if not volumes:
        print(f"Error: No volumes or book chapters found under {target_path}", file=sys.stderr)
        sys.exit(1)

    report = compile_omnibus_manuscript(volumes, series_title=args.title, author=args.author)

    if args.json:
        manifest = {k: v for k, v in report.items() if k != "markdown_content"}
        print(json.dumps(manifest, indent=2))
        return 0

    out_dir = Path(args.output) if args.output else (target_path if target_path.is_dir() else target_path.parent)
    md_file = out_dir / f"{re.sub(r'[^A-Za-z0-9_-]', '_', args.title)}_Omnibus.md"
    atomic_write(md_file, report["markdown_content"])

    print("=== Ars Arcanum Omnibus Compiler ===")
    print(f"Series Title:  {report['title']}")
    print(f"Volumes:       {report['total_volumes']} | Total Chapters: {report['total_chapters']}")
    print(f"Total Words:   {report['total_words']:,}")
    print(f"Omnibus Markdown: {md_file}")

    if args.html:
        out_html = Path(args.html)
        generate_omnibus_html_reader(report, out_html)
        print(f"Omnibus HTML Reader: {out_html}")
    return 0


__all__ = [
    "VolumeData",
    "compile_omnibus_manuscript",
    "discover_series_volumes",
    "generate_omnibus_html_reader",
    "main",
]

if __name__ == "__main__":
    main()
