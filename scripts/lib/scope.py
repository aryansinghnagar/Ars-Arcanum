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
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    from lib._bootstrap import validate_volume_name
except ImportError:
    try:
        from _bootstrap import validate_volume_name
    except ImportError:
        def validate_volume_name(vol: str) -> str:
            if not vol:
                raise ValueError("Volume name cannot be empty.")
            if ".." in vol or "/" in vol or "\\" in vol:
                raise ValueError(f"Invalid volume name '{vol}': path traversal not allowed.")
            return vol

logger = logging.getLogger("arcanum.scope")

# Excluded system / build directories when discovering manuscript or lore files
EXCLUDED_DIRS = {
    "Outlines", "Exports", "Backups", "04_Back_Matter", "03-Art",
    "04-Publishing", "05-Backups", "00-World-Bible", "World-Bible",
    ".obsidian", ".git", ".idea", ".vscode", "__pycache__",
}

# Standard lore folder categories in World Bibles
LORE_CATEGORIES = [
    "Characters", "Locations", "Factions", "MagicSystems", "Magic-Technology",
    "History", "Bestiary", "Cosmology", "Languages", "Ecology", "Economy",
    "Calendars", "Genealogy", "Map", "Items", "Religions", "Cultures",
]

# Scene break marker patterns in manuscript text
SCENE_BREAK_REGEX = re.compile(
    r"(?:\r?\n)(?:\s*(?:---|[*][\s*]*[*]|\#{1,6}\s*(?:Scene\b|\d+\b)|@scene[:\s]|@scene_id[:\s]))",
    re.IGNORECASE,
)
TAG_REGEX = re.compile(r"^@([A-Za-z0-9_-]+):\s*(.*)$")
FRONTMATTER_REGEX = re.compile(r"^---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)", re.DOTALL)


# =============================================================================
# 1. Range & Identifier Expression Parsers
# =============================================================================

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
        cleaned = re.sub(r"\b(?:chapter|chapters|chap|scene|scenes|act|acts|book|books|vol|volume)\b|(?:chapter|chap|ch|scene|sc|act|book|vol|v)(?=\d|\b)", "", token, flags=re.IGNORECASE)
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
        pattern = r"\b(" + known_keys + r")\s*[:=]\s*([^:=]+?)(?=(?:[,:]\s*" + known_keys + r"\s*[:=]|$))"
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

    # Otherwise, check colon or slash or comma separated segments e.g. "ch01..ch05:sc01..sc03" or "Book1:ch1-5:sc1-2"
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


# =============================================================================
# 2. Scope Data Structures
# =============================================================================

@dataclass
class EngineScope:
    """Specification of target scope filter for engine execution."""
    manuscript: str | Path | None = None
    manuscripts: list[str] = field(default_factory=list)
    world: str | Path | None = None
    worlds: list[str] = field(default_factory=list)
    universe: str | Path | None = None
    series: list[str] = field(default_factory=list)
    books: list[str] = field(default_factory=list)
    chapters: list[int] = field(default_factory=list)
    scenes: list[int] = field(default_factory=list)
    lore_categories: list[str] = field(default_factory=list)
    raw_scope: str = ""
    all_targets: bool = False

    @property
    def book(self) -> str | None:
        """Returns the primary book filter if specified."""
        return self.books[0] if self.books else None

    def is_scoped(self) -> bool:
        """Returns True if any granular filtering is active."""
        return bool(
            self.books or self.chapters or self.scenes or
            self.series or self.lore_categories or
            (self.manuscripts and len(self.manuscripts) > 1) or
            (self.worlds and len(self.worlds) > 1)
        )

    def is_manuscript_scoped(self) -> bool:
        """Returns True if manuscript/chapter/scene/book filtering is active."""
        return bool(self.books or self.chapters or self.scenes or self.series or (self.manuscripts and len(self.manuscripts) > 1))

    def is_world_scoped(self) -> bool:
        """Returns True if world or lore category filtering is active."""
        return bool(self.lore_categories or (self.worlds and len(self.worlds) > 1))

    def to_dict(self) -> dict[str, Any]:
        """Serializes EngineScope to a dictionary."""
        return {
            "manuscript": str(self.manuscript) if self.manuscript else None,
            "manuscripts": self.manuscripts,
            "world": str(self.world) if self.world else None,
            "worlds": self.worlds,
            "universe": str(self.universe) if self.universe else None,
            "series": self.series,
            "books": self.books,
            "chapters": self.chapters,
            "scenes": self.scenes,
            "lore_categories": self.lore_categories,
            "raw_scope": self.raw_scope,
            "all_targets": self.all_targets,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EngineScope:
        """Deserializes EngineScope from a dictionary."""
        return cls(
            manuscript=data.get("manuscript"),
            manuscripts=data.get("manuscripts", []),
            world=data.get("world"),
            worlds=data.get("worlds", []),
            universe=data.get("universe"),
            series=data.get("series", []),
            books=data.get("books", []),
            chapters=data.get("chapters", []),
            scenes=data.get("scenes", []),
            lore_categories=data.get("lore_categories", []),
            raw_scope=data.get("raw_scope", ""),
            all_targets=bool(data.get("all_targets", False)),
        )

    @property
    def summary(self) -> str:
        """Human-readable scope description."""
        parts = []
        if self.all_targets:
            return "Scope: ALL (Unrestricted)"
        if self.universe:
            parts.append(f"Universe: {self.universe}")
        if self.world:
            parts.append(f"World: {Path(self.world).name if isinstance(self.world, Path) else self.world}")
        if self.lore_categories:
            parts.append(f"Lore Categories: [{', '.join(self.lore_categories)}]")
        if self.manuscript:
            parts.append(f"Manuscript: {Path(self.manuscript).name if isinstance(self.manuscript, Path) else self.manuscript}")
        if self.series:
            parts.append(f"Series: [{', '.join(self.series)}]")
        if self.books:
            parts.append(f"Books: [{', '.join(self.books)}]")
        if self.chapters:
            if len(self.chapters) > 1 and self.chapters == list(range(self.chapters[0], self.chapters[-1] + 1)):
                parts.append(f"Chapters: [ch{self.chapters[0]:02d}-{self.chapters[-1]:02d}]")
            else:
                parts.append(f"Chapters: [{', '.join(str(c) for c in self.chapters)}]")
        if self.scenes:
            parts.append(f"Scenes: [{', '.join(str(s) for s in self.scenes)}]")
        return " | ".join(parts) if parts else "Scope: Default Active Project"


@dataclass
class SceneSlice:
    """A granular scene slice within a manuscript chapter."""
    scene_idx: int
    global_scene_idx: int
    scene_id: str
    title: str
    content: str
    start_line: int
    end_line: int
    tags: dict[str, list[str]]
    chapter_file: Path
    chapter_num: int
    volume_name: str

    @property
    def word_count(self) -> int:
        return len(re.findall(r"\b\w+(?:[-']\w+)*\b", self.content))


@dataclass
class ChapterItem:
    """A structured manuscript chapter item with its scenes and metadata."""
    chapter_num: int
    title: str
    file_path: Path
    volume_name: str
    division_name: str
    full_content: str
    scoped_content: str
    scenes: list[SceneSlice]
    tags: dict[str, list[str]]
    word_count: int

    @property
    def content(self) -> str:
        """Convenience property for scoped content."""
        return self.scoped_content


@dataclass
class LoreItem:
    """A worldbuilding lore document from a World Bible."""
    name: str
    category: str
    file_path: Path
    world_name: str
    content: str
    frontmatter: dict[str, Any]


@dataclass
class ResolvedScope:
    """Comprehensive resolved scope containing exact filtered files and elements."""
    manuscript_dir: Path | None
    manuscript_dirs: list[Path]
    world_dir: Path | None
    world_dirs: list[Path]
    universe_dir: Path | None
    series_names: list[str]
    volume_names: list[str]
    chapters: list[ChapterItem]
    scenes: list[SceneSlice]
    lore_items: list[LoreItem]
    is_scoped: bool
    scope_filter: EngineScope
    summary: str

    def get_markdown_files(self) -> list[Path]:
        """Returns all matching chapter markdown files."""
        return [c.file_path for c in self.chapters]

    def get_lore_files(self) -> list[Path]:
        """Returns all matching lore markdown files."""
        return [item.file_path for item in self.lore_items]

    def get_total_chapter_count(self) -> int:
        """Returns count of scoped chapters."""
        return len(self.chapters)

    def get_total_scene_count(self) -> int:
        """Returns count of scoped scenes."""
        return len(self.scenes)

    def get_total_word_count(self) -> int:
        """Returns total word count across scoped chapter contents."""
        return sum(
            len(re.findall(r"\b\w+(?:[-']\w+)*\b", c.scoped_content))
            for c in self.chapters
        )

    def to_dict(self) -> dict[str, Any]:
        """Serializes resolved scope to dictionary."""
        return {
            "manuscript": str(self.manuscript_dir) if self.manuscript_dir else None,
            "world": str(self.world_dir) if self.world_dir else None,
            "universe": str(self.universe_dir) if self.universe_dir else None,
            "series": self.series_names,
            "volumes": self.volume_names,
            "total_chapters": len(self.chapters),
            "total_scenes": len(self.scenes),
            "total_lore_items": len(self.lore_items),
            "total_words": self.get_total_word_count(),
            "is_scoped": self.is_scoped,
            "summary": self.summary,
            "chapter_files": [str(c.file_path) for c in self.chapters],
            "lore_files": [str(item.file_path) for item in self.lore_items],
        }


# =============================================================================
# 3. Active Context & Default Project Resolution
# =============================================================================

def get_active_manuscript() -> Path | None:
    """
    Resolves the active manuscript using intelligent context precedence:
    1. Config setting ('active_manuscript') in config.json
    2. Current working directory (if inside a manuscript or has manuscript.yaml)
    3. Exactly one manuscript in ~/Manuscripts
    4. Most recently modified manuscript in ~/Manuscripts
    """
    try:
        from lib.config import load_config
        cfg = load_config()
        active_name = cfg.get("active_manuscript")
        if active_name:
            p = resolve_manuscript_path(active_name)
            if p and p.is_dir():
                return p
    except Exception:
        pass

    # Check cwd
    cwd = Path.cwd()
    if (cwd / "manuscript.yaml").is_file():
        return cwd
    for parent in [cwd, *cwd.parents]:
        if (parent / "manuscript.yaml").is_file():
            return parent
        if parent.parent.name == "Manuscripts" and parent.is_dir():
            return parent

    # Check ~/Manuscripts
    home = Path.home()
    mss = sorted((home / "Manuscripts").glob("*"), key=lambda p: str(p))
    mss = [p for p in mss if p.is_dir() and not p.name.startswith(".")]
    if len(mss) == 1:
        return mss[0]
    if len(mss) > 1:
        # Pick most recently modified as intelligent default
        mss_sorted = sorted(mss, key=lambda p: p.stat().st_mtime, reverse=True)
        return mss_sorted[0]

    return None


def get_active_world() -> Path | None:
    """
    Resolves the active World Bible using intelligent context precedence:
    1. Config setting ('active_world') in config.json
    2. Current working directory (if inside a world or has world.yaml)
    3. Exactly one world in ~/Universes/*/* or ~/Worlds/*
    4. Most recently modified world vault
    """
    try:
        from lib.config import load_config
        cfg = load_config()
        active_name = cfg.get("active_world")
        if active_name:
            p = resolve_world_path(active_name)
            if p and p.is_dir():
                return p
    except Exception:
        pass

    # Check cwd
    cwd = Path.cwd()
    if (cwd / "world.yaml").is_file():
        return cwd
    for parent in [cwd, *cwd.parents]:
        if (parent / "world.yaml").is_file():
            return parent

    # Check ~/Universes/*/*
    home = Path.home()
    univ_worlds = sorted((home / "Universes").glob("*/*"), key=lambda p: str(p))
    univ_worlds = [p for p in univ_worlds if p.is_dir() and p.name not in ("Worlds", ".git") and not p.name.startswith(".")]
    if len(univ_worlds) == 1:
        return univ_worlds[0]

    # Check ~/Worlds/*
    legacy_worlds = sorted((home / "Worlds").glob("*"), key=lambda p: str(p))
    legacy_worlds = [p for p in legacy_worlds if p.is_dir() and not p.name.startswith(".")]
    if len(legacy_worlds) == 1:
        return legacy_worlds[0]

    all_worlds = univ_worlds + legacy_worlds
    if all_worlds:
        all_sorted = sorted(all_worlds, key=lambda p: p.stat().st_mtime, reverse=True)
        return all_sorted[0]

    return None


def get_active_universe() -> Path | None:
    """Resolves active universe directory."""
    try:
        from lib.config import load_config
        cfg = load_config()
        active_name = cfg.get("active_universe")
        if active_name:
            p = resolve_universe_path(active_name)
            if p and p.is_dir():
                return p
    except Exception:
        pass

    home = Path.home()
    universes = sorted((home / "Universes").glob("*"), key=lambda p: str(p))
    universes = [p for p in universes if p.is_dir() and not p.name.startswith(".")]
    if universes:
        return sorted(universes, key=lambda p: p.stat().st_mtime, reverse=True)[0]
    return None


def resolve_manuscript_path(
    target_str: str | Path | None = None,
    scope: EngineScope | None = None,
) -> Path | None:
    """Resolves manuscript path or name to absolute Path."""
    if not target_str and scope and scope.manuscript:
        target_str = scope.manuscript

    if not target_str:
        return get_active_manuscript()

    p = Path(target_str).expanduser().resolve()
    if p.is_dir():
        return p

    home = Path.home()
    target_clean = str(target_str).strip().lower()

    # Search in ~/Manuscripts
    for m_dir in sorted((home / "Manuscripts").glob("*")):
        if m_dir.is_dir() and m_dir.name.lower() == target_clean:
            return m_dir

    # Search in cwd
    p_cwd = Path.cwd() / target_str
    if p_cwd.is_dir():
        return p_cwd

    # Fuzzy match
    for m_dir in sorted((home / "Manuscripts").glob("*")):
        if m_dir.is_dir() and target_clean in m_dir.name.lower():
            return m_dir

    return None


def resolve_world_path(
    target_str: str | Path | None = None,
    scope: EngineScope | None = None,
) -> Path | None:
    """Resolves world path or name to absolute Path."""
    if not target_str and scope and scope.world:
        target_str = scope.world

    if not target_str:
        return get_active_world()

    p = Path(target_str).expanduser().resolve()
    if p.is_dir():
        return p

    home = Path.home()
    target_clean = str(target_str).strip().lower()

    # Search in ~/Universes/*/*
    for w_dir in sorted((home / "Universes").glob("*/*")):
        if w_dir.is_dir() and w_dir.name.lower() == target_clean:
            return w_dir

    # Search in ~/Worlds/*
    for w_dir in sorted((home / "Worlds").glob("*")):
        if w_dir.is_dir() and w_dir.name.lower() == target_clean:
            return w_dir

    # Search in cwd
    p_cwd = Path.cwd() / target_str
    if p_cwd.is_dir():
        return p_cwd

    # Fuzzy match
    for w_dir in sorted((home / "Universes").glob("*/*")):
        if w_dir.is_dir() and target_clean in w_dir.name.lower():
            return w_dir

    return None


def resolve_universe_path(
    target_str: str | Path | None = None,
    scope: EngineScope | None = None,
) -> Path | None:
    """Resolves universe path or name to absolute Path."""
    if not target_str and scope and scope.universe:
        target_str = scope.universe

    if not target_str:
        return get_active_universe()

    p = Path(target_str).expanduser().resolve()
    if p.is_dir():
        return p

    home = Path.home()
    target_clean = str(target_str).strip().lower()

    for u_dir in sorted((home / "Universes").glob("*")):
        if u_dir.is_dir() and u_dir.name.lower() == target_clean:
            return u_dir

    return None


def resolve_manuscript_dir(
    target_str: str | Path | None = None,
    scope: EngineScope | None = None,
) -> str:
    """Resolves manuscript target string or path to directory string path or empty string."""
    p = resolve_manuscript_path(target_str, scope=scope)
    return str(p) if p and p.is_dir() else ""


def resolve_world_dir(
    target_str: str | Path | None = None,
    scope: EngineScope | None = None,
) -> str:
    """Resolves world target string or path to directory string path or empty string."""
    p = resolve_world_path(target_str, scope=scope)
    return str(p) if p and p.is_dir() else ""


def resolve_universe_dir(
    target_str: str | Path | None = None,
    scope: EngineScope | None = None,
) -> str:
    """Resolves universe target string or path to directory string path or empty string."""
    p = resolve_universe_path(target_str, scope=scope)
    return str(p) if p and p.is_dir() else ""



# =============================================================================
# 4. Scene Slicing & Chapter Filtering Engine
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
            # Match by index
            if v_idx in book_nums:
                active_vol_dirs.append(v_dir)
                continue
            # Match by extracted numbers in folder name e.g. "Book-01" -> 1
            extracted_nums = [int(n) for n in re.findall(r"\d+", v_dir.name)]
            if any(n in book_nums for n in extracted_nums):
                active_vol_dirs.append(v_dir)
                continue
            # Match by name
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
        # Chapter index filtering
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
# 5. Universal Scope Resolution API
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


# =============================================================================
# 6. CLI Argument Parsing Helpers
# =============================================================================

def add_scope_arguments(
    parser: argparse.ArgumentParser,
    include_world: bool = True,
    include_manuscript: bool = True,
    include_chapters: bool = True,
    include_scenes: bool = True,
    include_books: bool = True,
    target_pos_arg: bool = False,
) -> None:
    """
    Standardizes and injects granular scope flags into an argparse ArgumentParser.
    """
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
    """
    Extracts and standardizes scope parameters from parsed CLI arguments.
    """
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


# =============================================================================
# 7. Self-Diagnostic CLI
# =============================================================================

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
