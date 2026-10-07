#!/usr/bin/env python3
"""
Ars Arcanum Centralized Data Access Layer (DAL) (scripts/lib/data_access.py)
===========================================================================
Sovereign, offline, thread-safe cached data access layer for World Bibles,
manuscript repositories, and lore dossiers.

Provides high-speed memoized file reading, AST frontmatter extraction, and entity
catalog queries with automatic mtime-based cache invalidation and LRU memory bounds
to eliminate redundant disk walks across multi-engine pipelines.
"""

from __future__ import annotations

import logging
import threading
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from lib._bootstrap import count_prose_words
    from lib.frontmatter import extract_frontmatter_and_body
except ImportError:
    try:
        from _bootstrap import count_prose_words
        from frontmatter import extract_frontmatter_and_body
    except ImportError:
        def count_prose_words(text: str) -> int:
            return len(text.split())

        def extract_frontmatter_and_body(content: str) -> tuple[dict[str, Any], str]:
            return {}, content

logger = logging.getLogger("arcanum.data_access")


@dataclass
class _CachedFileEntry:
    mtime: float
    size: int
    content: str
    frontmatter: dict[str, Any]
    body: str


class DataAccessLayer:
    """Thread-safe cached data access layer for Ars Arcanum repositories with LRU bounds."""

    def __init__(self, max_entries: int = 500) -> None:
        self._lock = threading.RLock()
        self._file_cache: OrderedDict[str, _CachedFileEntry] = OrderedDict()
        self.max_entries = max_entries
        self._hits = 0
        self._misses = 0

    def clear(self) -> None:
        """Clears all cached file and frontmatter entries."""
        with self._lock:
            self._file_cache.clear()
            self._hits = 0
            self._misses = 0

    def evict(self, file_path: Path | str) -> bool:
        """Evicts a specific file path from cache."""
        p = Path(file_path).resolve()
        path_key = str(p)
        with self._lock:
            if path_key in self._file_cache:
                del self._file_cache[path_key]
                return True
        return False

    def get_stats(self) -> dict[str, int]:
        """Returns cache telemetry statistics."""
        with self._lock:
            return {
                "cached_files": len(self._file_cache),
                "max_entries": self.max_entries,
                "cache_hits": self._hits,
                "cache_misses": self._misses,
            }

    def read_file(self, file_path: Path | str) -> str:
        """Reads text content of a file using thread-safe mtime caching with LRU promotion."""
        p = Path(file_path).resolve()
        if not p.is_file():
            return ""

        try:
            stat = p.stat()
            mtime = stat.st_mtime
            size = stat.st_size
        except OSError:
            return ""

        path_key = str(p)
        with self._lock:
            cached = self._file_cache.get(path_key)
            if cached is not None and cached.mtime == mtime and cached.size == size:
                self._hits += 1
                self._file_cache.move_to_end(path_key)
                return cached.content

        # Cache miss or stale entry: read from disk
        try:
            content = p.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            logger.warning("Failed reading file %s: %s", p, e)
            return ""

        frontmatter, body = extract_frontmatter_and_body(content)

        with self._lock:
            self._misses += 1
            if path_key in self._file_cache:
                self._file_cache.move_to_end(path_key)
            self._file_cache[path_key] = _CachedFileEntry(
                mtime=mtime,
                size=size,
                content=content,
                frontmatter=frontmatter,
                body=body,
            )
            # LRU eviction
            while len(self._file_cache) > self.max_entries:
                self._file_cache.popitem(last=False)

        return content

    def parse_frontmatter(self, file_path: Path | str) -> tuple[dict[str, Any], str]:
        """Returns cached (frontmatter_dict, body_text) tuple for a markdown file."""
        p = Path(file_path).resolve()
        path_key = str(p)

        # Trigger read_file to ensure entry is populated & validated against mtime
        content = self.read_file(p)
        if not content:
            return {}, ""

        with self._lock:
            cached = self._file_cache.get(path_key)
            if cached is not None:
                return dict(cached.frontmatter), cached.body

        frontmatter, body = extract_frontmatter_and_body(content)
        return frontmatter, body

    def list_files(
        self,
        directory: Path | str,
        extensions: tuple[str, ...] = (".md", ".markdown"),
        recursive: bool = True,
    ) -> list[Path]:
        """Lists files matching extensions under directory, sorted by path."""
        p = Path(directory).resolve()
        if not p.is_dir():
            return []

        results: list[Path] = []
        iterator = p.rglob("*") if recursive else p.glob("*")
        for f in iterator:
            if f.is_file() and not f.name.startswith((".", "_")) and f.suffix.lower() in extensions:
                results.append(f)

        return sorted(results)

    def get_manuscript_chapters(self, manuscript_dir: Path | str) -> list[dict[str, Any]]:
        """Extracts structured chapter descriptors from a manuscript directory with canonical word counting."""
        p = Path(manuscript_dir).resolve()
        if not p.is_dir():
            return []

        chapters: list[dict[str, Any]] = []
        files = self.list_files(p)

        for f in files:
            # Skip outlines, notes, non-draft scenes if outside book structure
            if "outlines" in f.parts or "back_matter" in str(f).lower():
                continue
            content = self.read_file(f)
            prose_words = count_prose_words(content)
            raw_words = len(content.split())
            fm, _ = self.parse_frontmatter(f)
            title = fm.get("title", f.stem.replace("_", " ").replace("-", " "))
            chapters.append({
                "path": str(f),
                "file": f.name,
                "title": title,
                "words": prose_words,
                "prose_words": prose_words,
                "raw_words": raw_words,
                "frontmatter": fm,
            })

        return chapters

    def get_lore_entities(self, world_dir: Path | str) -> list[dict[str, Any]]:
        """Extracts lore entities categorized by sub-directory under a World Bible."""
        p = Path(world_dir).resolve()
        if not p.is_dir():
            return []

        entities: list[dict[str, Any]] = []
        files = self.list_files(p)

        for f in files:
            rel = f.relative_to(p)
            category = rel.parts[0] if len(rel.parts) > 1 else "Root"
            if category.startswith("."):
                continue

            fm, _body = self.parse_frontmatter(f)
            name = fm.get("name", f.stem.replace("_", " "))
            tags = fm.get("tags", [])
            if isinstance(tags, str):
                tags = [t.strip() for t in tags.split(",") if t.strip()]

            entities.append({
                "path": str(f),
                "file": f.name,
                "name": name,
                "category": category,
                "tags": tags,
                "frontmatter": fm,
            })

        return entities


# Global Data Access Layer singleton
_GLOBAL_DAL: DataAccessLayer | None = None


def get_data_access() -> DataAccessLayer:
    """Returns the global shared DataAccessLayer singleton instance."""
    global _GLOBAL_DAL
    if _GLOBAL_DAL is None:
        _GLOBAL_DAL = DataAccessLayer()
    return _GLOBAL_DAL


__all__ = ["DataAccessLayer", "get_data_access"]
