#!/usr/bin/env python3
"""
Ars Arcanum Scope & Granular Target Resolution Engine (scripts/lib/scope.py)
===========================================================================
Universal targeting and scoping subsystem for Ars Arcanum.

Enables authors, CLI commands, and GUI interfaces (Studio Hub, Zen Studio, GTK)
to specify and resolve exact subsets of creative vaults:
- Specific worlds or lore categories (Characters, Locations, Bestiary, Factions, etc.)
- Specific universes and multi-volume series
- Specific manuscripts and volume/book subsets (e.g. Book 1, Book 3)
- Granular chapter lists and ranges (e.g. "1-5", "1,3,7-10", "ch01..ch05", "Chapter 1 - Chapter 4")
- Granular scene lists and ranges (e.g. "1-4", "sc01..sc03", "Scene 1, Scene 3")
- Intelligent active defaults: defaults to the currently open/configured world or
  manuscript instead of scanning the entire wiki or all manuscripts across the drive.

100% Offline Sovereign Architecture — Zero Pip Dependencies.
"""

from __future__ import annotations

import argparse
import logging
import re
from pathlib import Path
from typing import Any

try:
    from lib.scope_models import (
        EXCLUDED_DIRS,
        FRONTMATTER_REGEX,
        LORE_CATEGORIES,
        SCENE_BREAK_REGEX,
        TAG_REGEX,
        ChapterItem,
        EngineScope,
        LoreItem,
        ResolvedScope,
        SceneSlice,
    )
    from lib.scope_parser import (
        add_scope_arguments,
        format_scope_banner,
        parse_identifier_list,
        parse_number_ranges,
        parse_scope_args,
        parse_unified_scope_string,
    )
    from lib.scope_resolver import (
        get_active_manuscript,
        get_active_universe,
        get_active_world,
        resolve_manuscript_dir,
        resolve_manuscript_path,
        resolve_universe_dir,
        resolve_universe_path,
        resolve_world_dir,
        resolve_world_path,
    )
except ImportError:
    from scope_models import (  # type: ignore[no-redef]
        EXCLUDED_DIRS,
        FRONTMATTER_REGEX,
        LORE_CATEGORIES,
        SCENE_BREAK_REGEX,
        TAG_REGEX,
        ChapterItem,
        EngineScope,
        LoreItem,
        ResolvedScope,
        SceneSlice,
    )
    from scope_parser import (  # type: ignore[no-redef]
        add_scope_arguments,
        format_scope_banner,
        parse_identifier_list,
        parse_number_ranges,
        parse_scope_args,
        parse_unified_scope_string,
    )
    from scope_resolver import (  # type: ignore[no-redef]
        get_active_manuscript,
        get_active_universe,
        get_active_world,
        resolve_manuscript_dir,
        resolve_manuscript_path,
        resolve_universe_dir,
        resolve_universe_path,
        resolve_world_dir,
        resolve_world_path,
    )

__all__ = [
    "EXCLUDED_DIRS",
    "FRONTMATTER_REGEX",
    "LORE_CATEGORIES",
    "SCENE_BREAK_REGEX",
    "TAG_REGEX",
    "ChapterItem",
    "EngineScope",
    "LoreItem",
    "ResolvedScope",
    "SceneSlice",
    "add_scope_arguments",
    "extract_scenes_from_text",
    "filter_manuscript_scope",
    "filter_world_scope",
    "format_scope_banner",
    "get_active_manuscript",
    "get_active_universe",
    "get_active_world",
    "main",
    "parse_identifier_list",
    "parse_number_ranges",
    "parse_scope_args",
    "parse_unified_scope_string",
    "resolve_manuscript_dir",
    "resolve_manuscript_path",
    "resolve_scope",
    "resolve_universe_dir",
    "resolve_universe_path",
    "resolve_world_dir",
    "resolve_world_path",
]

logger = logging.getLogger("arcanum.scope")


# =============================================================================
# 2. Scene Slicing & Chapter Filtering Engine
# =============================================================================


def extract_scenes_from_text(
    text: str,
    chapter_file: Path | None = None,
    chapter_num: int = 1,
    volume_name: str = "",
    global_start_idx: int = 1,
) -> list[SceneSlice]:
    """
    Extracts granular scene slices from chapter markdown text.

    Identifies scenes separated by headings (## Scene...), dividers (---, * * *, #),
    or @scene directives. Preserves line numbers and tag metadata.
    """
    fpath = chapter_file or Path("unknown_chapter.md")
    lines = text.splitlines(keepends=True)
    if not lines:
        return []

    body_start_line = 0
    # Check for frontmatter block at start
    if lines and lines[0].strip() == "---":
        for idx in range(1, len(lines)):
            if lines[idx].strip() == "---":
                body_start_line = idx + 1
                break

    scene_starts: list[tuple[int, int]] = []  # (content_start_line, raw_start_line)
    curr_start = body_start_line

    idx = body_start_line
    while idx < len(lines):
        clean = lines[idx].strip()
        is_heading_scene = bool(re.match(r"^#{1,4}\s+(?:Scene\b|\d+\b|Part\b)", clean, re.IGNORECASE))
        is_divider = bool(re.match(r"^(?:---|[*][\s*]*[*])\s*$", clean))
        is_scene_directive = bool(re.match(r"^@scene(?:_id)?:\s*", clean, re.IGNORECASE))

        if idx > body_start_line and (is_heading_scene or is_divider or is_scene_directive):
            # Save previous scene
            scene_starts.append((curr_start, idx))
            curr_start = idx + 1 if is_divider else idx
        idx += 1

    scene_starts.append((curr_start, len(lines)))

    slices: list[SceneSlice] = []
    s_idx = 1
    for start_l, end_l in scene_starts:
        scene_lines = lines[start_l:end_l]
        scene_text = "".join(scene_lines).strip()
        if not scene_text:
            continue

        # Extract tags and title for this scene
        tags: dict[str, list[str]] = {}
        scene_title = f"Scene {s_idx}"
        for s_line in scene_lines:
            s_clean = s_line.strip()
            if s_clean.startswith("@"):
                m = TAG_REGEX.match(s_clean)
                if m:
                    t_name = m.group(1).lower()
                    t_val = m.group(2).strip()
                    tags.setdefault(t_name, []).append(t_val)
                    if t_name in ("scene", "title", "scene_title"):
                        scene_title = t_val
            elif s_clean.startswith("#") and scene_title == f"Scene {s_idx}":
                scene_title = re.sub(r"^#+\s*", "", s_clean).strip()

        slices.append(
            SceneSlice(
                scene_idx=s_idx,
                global_scene_idx=global_start_idx + len(slices),
                scene_id=f"ch{chapter_num:02d}_sc{s_idx:02d}",
                title=scene_title,
                content=scene_text,
                start_line=start_l + 1,
                end_line=end_l,
                tags=tags,
                chapter_file=fpath,
                chapter_num=chapter_num,
                volume_name=volume_name,
            )
        )
        s_idx += 1

    if not slices:
        slices.append(
            SceneSlice(
                scene_idx=1,
                global_scene_idx=global_start_idx,
                scene_id=f"ch{chapter_num:02d}_sc01",
                title="Scene 1",
                content=text.strip(),
                start_line=1,
                end_line=len(lines),
                tags={},
                chapter_file=fpath,
                chapter_num=chapter_num,
                volume_name=volume_name,
            )
        )

    return slices


def filter_manuscript_scope(
    manuscript_dir: Path,
    scope: EngineScope,
) -> tuple[list[ChapterItem], list[SceneSlice], list[str]]:
    """
    Discovers, filters, and slices chapters and scenes in a manuscript according to EngineScope.

    Returns: (filtered_chapters, filtered_scenes, active_volumes)
    """
    if not manuscript_dir.exists():
        return [], [], []

    # Find volume directories
    volume_dirs: list[Path] = []
    for item in sorted(manuscript_dir.iterdir()):
        if item.is_dir() and not item.name.startswith((".", "_")) and item.name not in EXCLUDED_DIRS and any(item.rglob("*.md")):
            volume_dirs.append(item)

    if not volume_dirs:
        volume_dirs = [manuscript_dir]

    # Filter volumes by scope.books
    active_vol_dirs: list[Path] = []
    if scope.books:
        book_nums = parse_number_ranges(scope.books)
        book_names = [b.lower() for b in scope.books if not str(b).isdigit() and "-" not in str(b)]
        for v_idx, v_dir in enumerate(volume_dirs, 1):
            v_name_lower = v_dir.name.lower()
            if v_idx in book_nums:
                active_vol_dirs.append(v_dir)
                continue
            extracted_nums = [int(n) for n in re.findall(r"\d+", v_dir.name)]
            if any(n in book_nums for n in extracted_nums):
                active_vol_dirs.append(v_dir)
                continue
            if any(b_name in v_name_lower for b_name in book_names):
                active_vol_dirs.append(v_dir)
    else:
        active_vol_dirs = volume_dirs

    all_raw_files: list[tuple[Path, str, str]] = []  # (file_path, volume_name, division_name)
    for v_dir in active_vol_dirs:
        vol_name = v_dir.name if v_dir != manuscript_dir else manuscript_dir.name
        for md_file in sorted(v_dir.rglob("*.md")):
            if any(part.startswith((".", "_")) or part in EXCLUDED_DIRS for part in md_file.parts):
                continue
            div_name = md_file.parent.name if md_file.parent != v_dir else "Main"
            all_raw_files.append((md_file, vol_name, div_name))

    all_raw_files.sort(key=lambda t: str(t[0]))

    chapters: list[ChapterItem] = []
    all_scenes: list[SceneSlice] = []
    global_scene_counter = 1

    for ch_idx, (md_file, vol_name, div_name) in enumerate(all_raw_files, 1):
        if scope.chapters:
            extracted_nums = [int(n) for n in re.findall(r"\d+", md_file.stem)]
            is_ch_match = (ch_idx in scope.chapters) or any(n in scope.chapters for n in extracted_nums)
            if not is_ch_match:
                continue

        try:
            content = md_file.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            logger.warning("Could not read manuscript chapter %s: %s", md_file, e)
            continue

        lines = content.splitlines()
        tags: dict[str, list[str]] = {}
        title = md_file.stem.replace("_", " ").replace("-", " ")
        for line in lines:
            clean = line.strip()
            if clean.startswith("@"):
                m = TAG_REGEX.match(clean)
                if m:
                    tags.setdefault(m.group(1).lower(), []).append(m.group(2).strip())
            elif clean.startswith("# ") and title == md_file.stem.replace("_", " ").replace("-", " "):
                title = clean[2:].strip()

        scenes = extract_scenes_from_text(
            text=content,
            chapter_file=md_file,
            chapter_num=ch_idx,
            volume_name=vol_name,
            global_start_idx=global_scene_counter,
        )
        global_scene_counter += len(scenes)

        if scope.scenes:
            scoped_scenes = [
                s for s in scenes
                if s.scene_idx in scope.scenes or s.global_scene_idx in scope.scenes
            ]
            if not scoped_scenes:
                continue
            scoped_content = "\n\n---\n\n".join(s.content for s in scoped_scenes)
            active_scenes_for_ch = scoped_scenes
        else:
            active_scenes_for_ch = scenes
            scoped_content = content

        ch_item = ChapterItem(
            chapter_num=ch_idx,
            title=title,
            file_path=md_file,
            volume_name=vol_name,
            division_name=div_name,
            full_content=content,
            scoped_content=scoped_content,
            scenes=active_scenes_for_ch,
            tags=tags,
            word_count=len(re.findall(r"\b\w+(?:[-']\w+)*\b", scoped_content)),
        )
        chapters.append(ch_item)
        all_scenes.extend(active_scenes_for_ch)

    active_vol_names = sorted({v.name for v in active_vol_dirs})
    return chapters, all_scenes, active_vol_names


def filter_world_scope(
    world_dir: Path,
    scope: EngineScope,
) -> list[LoreItem]:
    """
    Discovers and filters lore files in a World Bible according to EngineScope.
    """
    if not world_dir.exists():
        return []

    items: list[LoreItem] = []
    cat_filters = [c.lower() for c in scope.lore_categories] if scope.lore_categories else []

    try:
        from lib.frontmatter import parse_yaml_frontmatter
    except ImportError:
        try:
            from frontmatter import parse_yaml_frontmatter
        except ImportError:
            def parse_yaml_frontmatter(t: str) -> dict[str, Any]:
                return {}

    for md_file in sorted(world_dir.rglob("*.md")):
        if any(part.startswith((".", "_")) or part in EXCLUDED_DIRS for part in md_file.parts):
            continue

        category = "General"
        for part in md_file.parts:
            for std_cat in LORE_CATEGORIES:
                if part.lower() == std_cat.lower():
                    category = std_cat
                    break

        if cat_filters and category.lower() not in cat_filters and not any(f in md_file.name.lower() for f in cat_filters):
            continue

        try:
            content = md_file.read_text(encoding="utf-8", errors="replace")
            meta = parse_yaml_frontmatter(content)
            body = FRONTMATTER_REGEX.sub("", content).strip()
            h1 = re.search(r"^#\s+(.+)$", body, flags=re.MULTILINE)
            name = str(meta.get("name", meta.get("title", h1.group(1).strip() if h1 else md_file.stem.replace("-", " ").title())))

            items.append(
                LoreItem(
                    name=name,
                    category=category,
                    file_path=md_file,
                    world_name=world_dir.name,
                    content=body,
                    frontmatter=meta,
                )
            )
        except Exception as e:
            logger.warning("Could not read lore file %s: %s", md_file, e)

    return items


# =============================================================================
# 3. Universal Scope Resolution API
# =============================================================================

def resolve_scope(
    scope: EngineScope | argparse.Namespace | dict[str, Any] | None = None,
    default_to_active: bool = True,
) -> ResolvedScope:
    """
    Master resolution entry point. Converts an EngineScope, argparse.Namespace,
    or dictionary into a fully resolved ResolvedScope with chapters, scenes, lore items.
    """
    if scope is None:
        engine_scope = EngineScope()
    elif isinstance(scope, EngineScope):
        engine_scope = scope
    elif isinstance(scope, argparse.Namespace):
        engine_scope = parse_scope_args(scope)
    elif isinstance(scope, dict):
        engine_scope = EngineScope(
            manuscript=scope.get("manuscript"),
            manuscripts=parse_identifier_list(scope.get("manuscripts")),
            world=scope.get("world"),
            worlds=parse_identifier_list(scope.get("worlds")),
            universe=scope.get("universe"),
            series=parse_identifier_list(scope.get("series")),
            books=parse_identifier_list(scope.get("books")),
            chapters=parse_number_ranges(scope.get("chapters")),
            scenes=parse_number_ranges(scope.get("scenes")),
            lore_categories=parse_identifier_list(scope.get("lore_categories")),
            raw_scope=str(scope.get("raw_scope", "")),
            all_targets=bool(scope.get("all_targets", False)),
        )
    else:
        engine_scope = EngineScope()

    if engine_scope.raw_scope:
        parsed_str = parse_unified_scope_string(engine_scope.raw_scope)
        if not engine_scope.manuscript and parsed_str.get("manuscript"):
            engine_scope.manuscript = parsed_str["manuscript"]
        if not engine_scope.world and parsed_str.get("world"):
            engine_scope.world = parsed_str["world"]
        if not engine_scope.universe and parsed_str.get("universe"):
            engine_scope.universe = parsed_str["universe"]
        if not engine_scope.series and parsed_str.get("series"):
            engine_scope.series = parsed_str["series"]
        if not engine_scope.books and parsed_str.get("books"):
            engine_scope.books = parsed_str["books"]
        if not engine_scope.chapters and parsed_str.get("chapters"):
            engine_scope.chapters = parsed_str["chapters"]
        if not engine_scope.scenes and parsed_str.get("scenes"):
            engine_scope.scenes = parsed_str["scenes"]
        if not engine_scope.lore_categories and parsed_str.get("lore_categories"):
            engine_scope.lore_categories = parsed_str["lore_categories"]

    ms_path = resolve_manuscript_path(engine_scope.manuscript) if (engine_scope.manuscript or default_to_active) else None
    world_path = resolve_world_path(engine_scope.world) if (engine_scope.world or default_to_active) else None
    universe_path = resolve_universe_path(engine_scope.universe) if (engine_scope.universe or default_to_active) else None

    ms_dirs: list[Path] = []
    if engine_scope.manuscripts:
        for m_name in engine_scope.manuscripts:
            p = resolve_manuscript_path(m_name)
            if p and p.is_dir() and p not in ms_dirs:
                ms_dirs.append(p)
    elif ms_path:
        ms_dirs = [ms_path]

    world_dirs: list[Path] = []
    if engine_scope.worlds:
        for w_name in engine_scope.worlds:
            p = resolve_world_path(w_name)
            if p and p.is_dir() and p not in world_dirs:
                world_dirs.append(p)
    elif world_path:
        world_dirs = [world_path]

    all_chapters: list[ChapterItem] = []
    all_scenes: list[SceneSlice] = []
    all_vol_names: list[str] = []

    for m_dir in ms_dirs:
        chaps, scs, vols = filter_manuscript_scope(m_dir, engine_scope)
        all_chapters.extend(chaps)
        all_scenes.extend(scs)
        for v in vols:
            if v not in all_vol_names:
                all_vol_names.append(v)

    all_lore: list[LoreItem] = []
    for w_dir in world_dirs:
        lore = filter_world_scope(w_dir, engine_scope)
        all_lore.extend(lore)

    summary_str = engine_scope.summary
    is_scoped = engine_scope.is_scoped()

    return ResolvedScope(
        manuscript_dir=ms_path,
        manuscript_dirs=ms_dirs,
        world_dir=world_path,
        world_dirs=world_dirs,
        universe_dir=universe_path,
        series_names=list(engine_scope.series),
        volume_names=all_vol_names,
        chapters=all_chapters,
        scenes=all_scenes,
        lore_items=all_lore,
        is_scoped=is_scoped,
        scope_filter=engine_scope,
        summary=summary_str,
    )


# Self-Diagnostic CLI
def main(argv: list[str] | None = None) -> int:
    """CLI diagnostic tool to inspect and test scope resolution."""
    import json
    parser = argparse.ArgumentParser(
        prog="arcanum scope",
        description="Ars Arcanum Scope & Granular Target Resolution Engine",
    )
    add_scope_arguments(parser, target_pos_arg=True)
    parser.add_argument("--json", action="store_true", help="Output machine-readable resolved scope JSON")

    args = parser.parse_args(argv)
    res = resolve_scope(args)

    if args.json:
        print(json.dumps(res.to_dict(), indent=2))
        return 0

    print("═══════════════════════════════════════════════════════════════════")
    print("🎯 Ars Arcanum Scope Resolution Diagnostic")
    print("═══════════════════════════════════════════════════════════════════")
    print(f"Summary          : {res.summary}")
    print(f"Scoped Filter    : {'YES (Granular Filter Active)' if res.is_scoped else 'NO (Full Target / Default)'}")
    print(f"Active Universe  : {res.universe_dir.name if res.universe_dir else 'None'}")
    print(f"Active World     : {res.world_dir.name if res.world_dir else 'None'}")
    print(f"Active Manuscript: {res.manuscript_dir.name if res.manuscript_dir else 'None'}")
    print(f"Volumes Scoped   : {', '.join(res.volume_names) or 'None'}")
    print(f"Chapters Scoped  : {len(res.chapters)} chapters ({res.get_total_word_count()} words)")
    print(f"Scenes Scoped    : {len(res.scenes)} scenes")
    print(f"Lore Docs Scoped : {len(res.lore_items)} lore items")
    print("───────────────────────────────────────────────────────────────────")

    if res.chapters:
        print("Chapters in Scope:")
        for c in res.chapters[:10]:
            print(f"  📖 [Ch {c.chapter_num:02d}] {c.title:<28} ({len(c.scenes)} scenes, {c.word_count} words)")
        if len(res.chapters) > 10:
            print(f"  ... and {len(res.chapters) - 10} more chapters.")

    if res.lore_items:
        print("\nLore Items in Scope:")
        for item in res.lore_items[:10]:
            print(f"  📜 [{item.category:<12}] {item.name}")
        if len(res.lore_items) > 10:
            print(f"  ... and {len(res.lore_items) - 10} more lore items.")

    print("═══════════════════════════════════════════════════════════════════\n")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
