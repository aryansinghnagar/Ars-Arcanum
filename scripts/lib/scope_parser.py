#!/usr/bin/env python3
"""
Ars Arcanum Scope Parser & CLI Helpers (scripts/lib/scope_parser.py)
===================================================================
Range parsers, unified scope expression resolvers, and CLI argument
injectors for granular manuscript and world target scoping.
"""

from __future__ import annotations

import argparse
import re
from collections.abc import Sequence
from typing import Any

try:
    from lib.scope_models import EngineScope, ResolvedScope
except ImportError:
    from scope_models import EngineScope, ResolvedScope  # type: ignore[no-redef]


def parse_number_ranges(expr: str | int | Sequence[Any] | None) -> list[int]:
    """
    Parses a string, integer, or sequence containing comma-separated numbers and ranges.

    Examples:
      - 5                      -> [5]
      - "1"                    -> [1]
      - "1,2,3"                -> [1, 2, 3]
      - "1-5"                  -> [1, 2, 3, 4, 5]
      - "1..5"                 -> [1, 2, 3, 4, 5]
      - "01-05"                -> [1, 2, 3, 4, 5]
      - "ch1-ch5"              -> [1, 2, 3, 4, 5]
      - "Chapter 1 - 3"        -> [1, 2, 3]
      - "sc1, sc3, sc5-8"      -> [1, 3, 5, 6, 7, 8]
      - ["1-3", 5, "7..9"]     -> [1, 2, 3, 5, 7, 8, 9]

    Returns a sorted list of unique positive integers.
    """
    if expr is None:
        return []
    if isinstance(expr, int):
        return [expr] if expr > 0 else []

    if isinstance(expr, (list, tuple, set)):
        collected: set[int] = set()
        for item in expr:
            collected.update(parse_number_ranges(item))
        return sorted(collected)

    s = str(expr).strip()
    if not s or s.lower() in ("all", "none", "*", ""):
        return []

    results: set[int] = set()

    # Split by comma or semicolon
    parts = re.split(r"[,;]+", s)
    for part in parts:
        token = part.strip()
        if not token:
            continue

        # Clean prefix markers (ch, chapter, sc, scene, act, book, vol, volume, #)
        cleaned = re.sub(
            r"\b(?:chapter|chapters|chap|scene|scenes|act|acts|book|books|vol|volume)\b|(?:chapter|chap|ch|scene|sc|act|book|vol|v)(?=\d|\b)",
            "",
            token,
            flags=re.IGNORECASE,
        )
        cleaned = cleaned.replace("#", "").strip()

        # Match range e.g. "1-5", "1..5", "1 to 5"
        range_match = re.match(r"^(\d+)\s*(?:-|[.]{2,}|to)\s*(\d+)$", cleaned, re.IGNORECASE)
        if range_match:
            start_num = int(range_match.group(1))
            end_num = int(range_match.group(2))
            if start_num <= end_num:
                results.update(range(start_num, end_num + 1))
            else:
                results.update(range(end_num, start_num + 1))
            continue

        # Match single integer e.g. "4"
        single_match = re.match(r"^(\d+)$", cleaned)
        if single_match:
            val = int(single_match.group(1))
            if val > 0:
                results.add(val)
            continue

        # Extract all numbers from messy token if simple match failed
        nums = [int(n) for n in re.findall(r"\d+", cleaned)]
        if len(nums) == 2 and ("-" in cleaned or ".." in cleaned or "to" in cleaned):
            lo, hi = min(nums), max(nums)
            results.update(range(lo, hi + 1))
        elif nums:
            results.update(n for n in nums if n > 0)

    return sorted(results)


def parse_identifier_list(expr: str | Sequence[str] | None) -> list[str]:
    """
    Parses a string or sequence into a cleaned list of string identifiers/names.

    Examples:
      - "Book-01, Book-02"       -> ["Book-01", "Book-02"]
      - "Characters; Locations"  -> ["Characters", "Locations"]
      - ["Book-01", "Book-02"]   -> ["Book-01", "Book-02"]
    """
    if expr is None:
        return []
    if isinstance(expr, (list, tuple, set)):
        out = []
        for item in expr:
            for sub in parse_identifier_list(item):
                if sub not in out:
                    out.append(sub)
        return out

    s = str(expr).strip()
    if not s or s.lower() in ("all", "none", "*", ""):
        return []

    tokens = re.split(r"[,;]+", s)
    cleaned = []
    for t in tokens:
        val = t.strip().strip("\"'")
        if val and val not in cleaned:
            cleaned.append(val)
    return cleaned


def parse_unified_scope_string(scope_str: str) -> dict[str, Any]:
    """
    Parses a unified scope string with optional key:value components.

    Examples:
      - "ch:1-5"                           -> {"chapters": [1, 2, 3, 4, 5]}
      - "ch:1-5,sc:1-2"                    -> {"chapters": [1..5], "scenes": [1, 2]}
      - "book:1-2,ch:3-7"                  -> {"books": ["1-2"], "chapters": [3..7]}
      - "world:Aethelgard,cat:Characters"  -> {"world": "Aethelgard", "lore_categories": ["Characters"]}
      - "series:Trilogy-1,books:1-3"       -> {"series": ["Trilogy-1"], "books": ["1-3"]}
      - "1-5"                              -> {"chapters": [1, 2, 3, 4, 5]} (shorthand)
    """
    res: dict[str, Any] = {
        "manuscript": None,
        "world": None,
        "universe": None,
        "series": [],
        "books": [],
        "chapters": [],
        "scenes": [],
        "lore_categories": [],
    }
    s = scope_str.strip()
    if not s:
        return res

    # If it's a pure number range shorthand e.g. "1-5" or "ch01..ch05"
    if re.match(r"^(?:ch|chapter|sc|scene)?\s*\d+\s*(?:[-.,;]|[.]{2,}|to|\d+)+$", s, re.IGNORECASE):
        if s.lower().startswith(("sc", "scene")):
            res["scenes"] = parse_number_ranges(s)
        else:
            res["chapters"] = parse_number_ranges(s)
        return res

    # Check key:value pairs where key is a known scope keyword
    known_keys = r"(?:manuscript|ms|novel|world|vault|universe|cosmos|series|books?|vols?|volumes?|chapters?|ch|scenes?|sc|lore(?:_categor(?:y|ies))?|cat(?:egor(?:y|ies))?)"
    if re.search(r"\b" + known_keys + r"\s*[:=]", s, re.IGNORECASE):
        pattern = r"\b(" + known_keys + r")\s*[:=]\s*(.+?)(?=(?:[,;\s]+\b" + known_keys + r"\s*[:=]|$))"
        matches = re.findall(pattern, s, re.IGNORECASE)

        for k, v in matches:
            k_clean = k.lower().strip()
            v_clean = v.strip().rstrip(",")
            if k_clean in ("m", "ms", "manuscript", "novel"):
                res["manuscript"] = v_clean
            elif k_clean in ("w", "world", "vault"):
                res["world"] = v_clean
            elif k_clean in ("u", "universe", "cosmos"):
                res["universe"] = v_clean
            elif k_clean in ("s", "series"):
                res["series"] = parse_identifier_list(v_clean)
            elif k_clean in ("b", "book", "books", "vol", "vols", "volume", "volumes"):
                res["books"] = parse_identifier_list(v_clean)
            elif k_clean in ("c", "ch", "chapter", "chapters"):
                res["chapters"] = parse_number_ranges(v_clean)
            elif k_clean in ("sc", "scene", "scenes"):
                res["scenes"] = parse_number_ranges(v_clean)
            elif k_clean in ("lore", "lore_category", "lore_categories", "cat", "category", "categories"):
                res["lore_categories"] = parse_identifier_list(v_clean)
        return res

    # Otherwise, check colon or slash or comma separated segments
    parts = [p.strip() for p in re.split(r"[:/]", s) if p.strip()]
    matched_any = False
    for part in parts:
        if re.match(r"^(?:ch|chapter)\b|^(?:ch|chapter)\d", part, re.IGNORECASE):
            res["chapters"] = parse_number_ranges(part)
            matched_any = True
        elif re.match(r"^(?:sc|scene)\b|^(?:sc|scene)\d", part, re.IGNORECASE):
            res["scenes"] = parse_number_ranges(part)
            matched_any = True
        elif re.match(r"^(?:bk|book|vol|volume)\b|^(?:bk|book|vol)\d", part, re.IGNORECASE):
            res["books"] = parse_identifier_list(part)
            matched_any = True
        elif not res["books"] and not res["manuscript"] and not matched_any:
            res["books"] = [part]
            matched_any = True

    if not matched_any:
        nums = parse_number_ranges(s)
        if nums:
            res["chapters"] = nums
        else:
            res["manuscript"] = s

    return res


def add_scope_arguments(
    parser: argparse.ArgumentParser,
    include_world: bool = True,
    include_manuscript: bool = True,
    include_chapters: bool = True,
    include_scenes: bool = True,
    include_books: bool = True,
    target_pos_arg: bool = False,
) -> None:
    """Standardizes and injects granular scope flags into an argparse ArgumentParser."""
    existing_opts: set[str] = set()
    for action in parser._actions:
        existing_opts.update(action.option_strings)

    scope_grp = parser.add_argument_group("Granular Scope & Target Options")

    def _add(opts: list[str], **kwargs: Any) -> None:
        avail = [o for o in opts if o not in existing_opts]
        if avail:
            scope_grp.add_argument(*avail, **kwargs)
            existing_opts.update(avail)

    if target_pos_arg:
        parser.add_argument("target", nargs="?", default=None, help="Target manuscript or world directory/name")

    if include_manuscript:
        _add(["-m", "--manuscript", "--ms"], dest="manuscript", help="Target manuscript directory or name")
        _add(["--manuscripts"], dest="manuscripts", help="Comma-separated list of manuscripts")
        _add(["--series"], dest="series", help="Filter by series identifier or name")

    if include_books:
        _add(["-b", "--book", "--books", "--volume", "--volumes"], dest="books", help="Filter by book/volume range or names (e.g. '1-3', 'Book-01, Book-02')")

    if include_chapters:
        _add(["-c", "--chapter", "--chapters", "--ch"], dest="chapters", help="Filter by chapter range or list (e.g. '1-5', '1,3,7-10', 'ch01..ch05')")

    if include_scenes:
        _add(["--scene", "--scenes", "--sc"], dest="scenes", help="Filter by scene range or list (e.g. '1-4', 'sc01..sc03')")

    if include_world:
        _add(["-w", "--world"], dest="world", help="Target World Bible directory or name")
        _add(["--worlds"], dest="worlds", help="Comma-separated list of worlds")
        _add(["-u", "--universe"], dest="universe", help="Target Universe directory or name")
        _add(["--lore-category", "--lore-categories", "--category"], dest="lore_categories", help="Filter by lore categories (e.g. 'Characters, Locations, Bestiary')")

    _add(["--scope"], dest="scope", help="Unified scope expression (e.g. 'ch:1-5,sc:1-2', 'book:1-2,ch:3-7', 'world:Aethelgard,cat:Characters')")
    _add(["--all"], dest="all_targets", action="store_true", help="Explicitly run across all discovered projects / entire vault without restrictions")


def parse_scope_args(args: argparse.Namespace) -> EngineScope:
    """Extracts and standardizes scope parameters from parsed CLI arguments."""
    target = getattr(args, "target", None)
    ms = getattr(args, "manuscript", None) or getattr(args, "ms", None) or getattr(args, "ms_flag", None) or target
    w = getattr(args, "world", None) or getattr(args, "w", None)
    u = getattr(args, "universe", None) or getattr(args, "u", None)

    raw_scope = str(getattr(args, "scope", "") or "")
    all_targets = bool(getattr(args, "all_targets", False))

    mss = parse_identifier_list(getattr(args, "manuscripts", None))
    ws = parse_identifier_list(getattr(args, "worlds", None))
    series = parse_identifier_list(getattr(args, "series", None))
    books = parse_identifier_list(getattr(args, "books", None) or getattr(args, "book", None) or getattr(args, "target_book", None))
    chapters = parse_number_ranges(getattr(args, "chapters", None) or getattr(args, "chapter", None) or getattr(args, "ch", None))
    scenes = parse_number_ranges(getattr(args, "scenes", None) or getattr(args, "scene", None) or getattr(args, "sc", None))
    lore_cats = parse_identifier_list(getattr(args, "lore_categories", None) or getattr(args, "lore_category", None) or getattr(args, "category", None))

    return EngineScope(
        manuscript=ms,
        manuscripts=mss,
        world=w,
        worlds=ws,
        universe=u,
        series=series,
        books=books,
        chapters=chapters,
        scenes=scenes,
        lore_categories=lore_cats,
        raw_scope=raw_scope,
        all_targets=all_targets,
    )


def format_scope_banner(
    target: ResolvedScope | EngineScope | str | None = None,
    scope: EngineScope | None = None,
) -> str:
    """Formats a concise terminal banner summarizing the active scope."""
    if isinstance(target, ResolvedScope):
        status_label = "Granular Filter Active" if target.is_scoped else "Active Context Default"
        target_info = []
        if target.manuscript_dir:
            target_info.append(f"Manuscript: {target.manuscript_dir.name}")
        if target.world_dir:
            target_info.append(f"World: {target.world_dir.name}")
        if target.universe_dir:
            target_info.append(f"Universe: {target.universe_dir.name}")

        target_str = " | ".join(target_info) if target_info else "Default Vault"
        lines = [
            f"🎯 Scope [{status_label}]: {target.summary}",
            f"   Context: {target_str} -> {len(target.chapters)} ch ({target.get_total_word_count():,} words) | {len(target.scenes)} sc | {len(target.lore_items)} lore items",
        ]
        return "\n".join(lines)
    if isinstance(target, EngineScope):
        status_label = "Granular Filter Active" if target.is_scoped() else "Active Context Default"
        return f"🎯 Scope [{status_label}]: {target.summary}"
    if isinstance(target, str):
        title = target
        scope_obj = scope or EngineScope()
        status_label = "Granular Filter Active" if scope_obj.is_scoped() else "Active Context Default"
        lines = [
            "=" * 75,
            f"  🏛️  {title}",
            f"  🎯 Scope [{status_label}]: {scope_obj.summary}",
            "=" * 75,
        ]
        return "\n".join(lines)
    return "🎯 Scope: Active Context Default"
