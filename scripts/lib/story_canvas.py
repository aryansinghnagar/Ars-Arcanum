#!/usr/bin/env python3
"""
Ars Arcanum Interactive Visual Story Canvas & Corkboard Engine
(scripts/lib/story_canvas.py)
================================================================================
Zero-dependency, offline interactive HTML5 visual story corkboard and narrative
timeline arranger for novelists, screenwriters, and worldbuilders.

Capabilities:
1. Scene & Chapter Card Extraction:
   - Scans manuscript chapters and scenes (`*.md`).
   - Extracts title, word count, POV character (`@pov:`), location (`@location:`),
     plot threads (`@thread:`), tension rating, and summary excerpts.
2. Paradigm & Beat Alignment:
   - Maps scene positions against 9 canonical narrative paradigms from `structure.py`.
3. Standalone Interactive Visual Corkboard:
   - Drag-and-drop scene cards between Act columns and POV swimlanes.
   - Live client-side recalculation of word count balance and structural harmony.
   - Color-coded POV badges, tension heat indicators, and plot thread filters.
   - One-click manifest export for updated chapter ordering.

Zero external dependencies; 100% offline privacy.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from pathlib import Path
from typing import Any

try:
    from lib._bootstrap import atomic_write, count_prose_words
    from lib.data_access import get_data_access
    from lib.frontmatter import parse_yaml_frontmatter
    from lib.scope import (
        EngineScope,
        add_scope_arguments,
        filter_manuscript_scope,
        parse_scope_args,
        resolve_manuscript_dir,
    )
    from lib.story_canvas_template import render_story_canvas_page
    from lib.structure import PARADIGMS
    from lib.tips import are_tips_enabled, get_tip_database
except ImportError:
    from _bootstrap import atomic_write, count_prose_words
    from data_access import get_data_access
    from frontmatter import parse_yaml_frontmatter
    from scope import (  # type: ignore[no-redef]
        EngineScope,
        add_scope_arguments,
        filter_manuscript_scope,
        parse_scope_args,
        resolve_manuscript_dir,
    )
    from story_canvas_template import render_story_canvas_page  # type: ignore[no-redef]
    from structure import PARADIGMS
    try:
        from tips import are_tips_enabled, get_tip_database
    except ImportError:
        def are_tips_enabled() -> bool:
            return True

        def get_tip_database() -> Any:
            return None

logger = logging.getLogger("arcanum.canvas")

TAG_REGEX = re.compile(r"^@([a-zA-Z0-9_-]+):\s*(.*)$")
FRONTMATTER_REGEX = re.compile(r"^---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)", re.DOTALL)


def extract_single_card(content: str, file_path: Path | str, idx: int, title: str | None = None) -> dict[str, Any]:
    """Helper to extract a single scene/chapter card from markdown text."""
    p = Path(file_path)
    meta = parse_yaml_frontmatter(content)
    body = FRONTMATTER_REGEX.sub("", content)
    words = count_prose_words(content)
    pov = str(meta.get("pov", meta.get("character", "")))
    location = str(meta.get("location", meta.get("setting", "")))
    thread = str(meta.get("thread", meta.get("plot", "")))
    tension = float(meta.get("tension", 5.0))

    # Parse inline @tags if not in frontmatter
    lines = body.splitlines()
    prose_lines = []
    for line in lines:
        s_line = line.strip()
        m = TAG_REGEX.match(s_line)
        if m:
            k, v = m.group(1).lower(), m.group(2).strip()
            if k == "pov" and not pov:
                pov = v
            elif k in ("location", "setting") and not location:
                location = v
            elif k in ("thread", "plot") and not thread:
                thread = v
            elif k == "tension":
                try:
                    tension = float(v)
                except ValueError:
                    pass
        elif s_line and not s_line.startswith("#"):
            prose_lines.append(s_line)

    summary = " ".join(prose_lines)[:180].strip()
    if len(" ".join(prose_lines)) > 180:
        summary += "..."

    h1_match = re.search(r"^#\s+(.+)$", body, flags=re.MULTILINE)
    raw_title = str(meta.get("title", title if title else (h1_match.group(1).strip() if h1_match else p.stem.replace("_", " ").replace("-", " "))))
    # Strip leading numbers from title for cleanliness
    clean_title = re.sub(r"^\d+\s*[-_.]*\s*", "", raw_title).title()

    return {
        "id": f"card_{idx}",
        "index": idx,
        "filename": p.name,
        "path": str(p),
        "title": clean_title or p.stem,
        "pov": pov or "Omniscient",
        "location": location or "Unspecified",
        "thread": thread or "Main Plot",
        "tension": tension,
        "word_count": words,
        "summary": summary or "No prose summary available.",
    }


def extract_scene_cards(target_path: Path | str | None = None, scope: Any = None) -> list[dict[str, Any]]:
    """Extracts rich metadata for every scene/chapter in the manuscript with granular scope support."""
    target_str = resolve_manuscript_dir(target_path) if target_path else resolve_manuscript_dir()
    if target_path and Path(target_path).exists():
        p_target = Path(target_path)
    elif target_str and Path(target_str).exists():
        p_target = Path(target_str)
    else:
        p_target = Path(target_path) if target_path else Path.cwd()

    cards = []
    total_words_accum = 0

    if p_target.is_file():
        content = get_data_access().read_file(p_target)
        card = extract_single_card(content, p_target, 1)
        card["cumulative_words"] = card["word_count"]
        cards.append(card)
    elif p_target.is_dir():
        if scope:
            if not isinstance(scope, EngineScope):
                if isinstance(scope, dict):
                    from lib.scope import resolve_scope
                    scope = resolve_scope(scope).scope_filter
                elif isinstance(scope, str):
                    from lib.scope import parse_unified_scope_string
                    p_dict = parse_unified_scope_string(scope)
                    scope = EngineScope(**p_dict)
            scoped_chaps, scoped_scenes, _ = filter_manuscript_scope(p_target, scope)
            if scope.scenes and scoped_scenes:
                items = [(s.global_scene_idx, s.title, s.content, s.chapter_file) for s in scoped_scenes]
            else:
                items = [(c.chapter_num, c.title, c.scoped_content, c.file_path) for c in scoped_chaps]
            for idx, title, content, fpath in items:
                card = extract_single_card(content, fpath, idx, title=title)
                total_words_accum += card["word_count"]
                card["cumulative_words"] = total_words_accum
                cards.append(card)
        else:
            files = []
            for p in sorted(p_target.rglob("*.md")):
                if not p.name.startswith((".", "_")) and "Backups" not in p.parts and "04_Back_Matter" not in p.parts:
                    files.append(p)
            for idx, f in enumerate(files, 1):
                content = get_data_access().read_file(f)
                card = extract_single_card(content, f, idx)
                total_words_accum += card["word_count"]
                card["cumulative_words"] = total_words_accum
                cards.append(card)
    else:
        raise FileNotFoundError(f"Target path not found: {p_target}")

    return cards


def generate_story_canvas_html(
    target_path: Path,
    cards: list[dict[str, Any]],
    paradigm_key: str = "eight_sequence",
    output_path: Path | None = None,
) -> str:
    """Generates a standalone, fully offline interactive HTML5 story canvas."""
    total_words = sum(c.get("word_count", 0) for c in cards)

    # Compute assigned acts/beats
    for c in cards:
        pct = (c["cumulative_words"] / total_words) if total_words > 0 else 0.0
        c["pct"] = round(pct, 3)

    tips_data: list[dict[str, Any]] = []
    tips_enabled = True
    try:
        tips_enabled = are_tips_enabled()
        db = get_tip_database()
        if db:
            canvas_engines = ["story_canvas", "structure", "pacing", "scene_mechanics", "timeline_sync", "revision_heatmap"]
            for eng in canvas_engines:
                for t in db.get_by_engine(eng):
                    tips_data.append(t.to_dict())
            if not tips_data:
                tips_data = [t.to_dict() for t in db.get_by_context("drafting")]
    except Exception as e:
        logger.debug("Story canvas tips extraction skipped: %s", e)

    html_content = render_story_canvas_page(
        target_path=target_path,
        cards=cards,
        paradigm_key=paradigm_key,
        tips_data=tips_data,
        tips_enabled=tips_enabled,
    )

    if output_path:
        atomic_write(output_path, html_content)
    return html_content


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ars Arcanum Interactive Visual Story Canvas")
    parser.add_argument("target", nargs="?", default=None, help="Manuscript directory or file")
    parser.add_argument(
        "--paradigm", "-p",
        choices=list(PARADIGMS.keys()),
        default="eight_sequence",
        help="Story paradigm structure for canvas lanes",
    )
    parser.add_argument("--html", help="Output HTML canvas report path")
    parser.add_argument("--json", action="store_true", help="Output extracted scene cards as JSON")
    add_scope_arguments(parser, include_world=False)
    args = parser.parse_args(argv)

    scope = parse_scope_args(args)
    target_raw = args.target or scope.manuscript or (scope.books[0] if scope.books else None)
    if not target_raw:
        resolved_dir = resolve_manuscript_dir()
        if resolved_dir and Path(resolved_dir).exists():
            target_path = Path(resolved_dir)
        else:
            parser.print_help()
            return 1
    else:
        tp = Path(target_raw)
        if tp.exists():
            target_path = tp
        else:
            resolved_dir = resolve_manuscript_dir(target_raw)
            if resolved_dir and Path(resolved_dir).exists():
                target_path = Path(resolved_dir)
            else:
                print(f"Error: Target path does not exist: {target_raw}", file=sys.stderr)
                sys.exit(1)

    cards = extract_scene_cards(target_path, scope=scope)

    if args.json:
        print(json.dumps(cards, indent=2))
        return 0

    out_p = Path(args.html) if args.html else (target_path if target_path.is_dir() else target_path.parent) / "story_canvas.html"
    generate_story_canvas_html(target_path, cards, paradigm_key=args.paradigm, output_path=out_p)

    print("=== Ars Arcanum Story Canvas ===")
    print(f"Target: {target_path.name} | Scenes/Chapters: {len(cards)} | Total Words: {sum(c['word_count'] for c in cards):,}")
    print(f"Paradigm: {PARADIGMS.get(args.paradigm, {}).get('name', args.paradigm)}")
    print(f"Interactive Story Canvas written to: {out_p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
