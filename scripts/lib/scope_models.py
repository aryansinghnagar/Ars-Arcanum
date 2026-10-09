#!/usr/bin/env python3
"""
Ars Arcanum Scope Models & Dataclasses (scripts/lib/scope_models.py)
===================================================================
Data structures and constants for target scoping across universes,
worlds, lore categories, manuscripts, volumes, chapters, and scenes.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

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

    @property
    def path(self) -> Path:
        """Convenience property for file_path."""
        return self.file_path

    @property
    def index(self) -> int:
        """Convenience property for chapter_num."""
        return self.chapter_num


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
        return len(self.chapters)

    def get_total_scene_count(self) -> int:
        return len(self.scenes)

    def get_total_word_count(self) -> int:
        return sum(c.word_count for c in self.chapters)

    def to_dict(self) -> dict[str, Any]:
        """Serializes ResolvedScope to JSON-compatible dictionary."""
        return {
            "manuscript_dir": str(self.manuscript_dir) if self.manuscript_dir else None,
            "manuscript_dirs": [str(p) for p in self.manuscript_dirs],
            "world_dir": str(self.world_dir) if self.world_dir else None,
            "world_dirs": [str(p) for p in self.world_dirs],
            "universe_dir": str(self.universe_dir) if self.universe_dir else None,
            "series_names": self.series_names,
            "volume_names": self.volume_names,
            "total_chapters": len(self.chapters),
            "total_scenes": len(self.scenes),
            "total_lore_items": len(self.lore_items),
            "total_words": self.get_total_word_count(),
            "is_scoped": self.is_scoped,
            "summary": self.summary,
            "scope_filter": self.scope_filter.to_dict(),
        }

