#!/usr/bin/env python3
"""
Ars Arcanum Bootstrap Utilities (scripts/lib/_bootstrap.py)
===========================================================
Shared bootstrap module providing:
1. Universal UTF-8 stream re-encoding for POSIX/Windows CLI safety.
2. Standardized sys.path insertion for domain engines.
3. Fail-safe export of atomic_write primitive.
4. Common CLI execution helpers.
"""

import re
import sys
from pathlib import Path

# 1. UTF-8 standard stream re-encoding
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# 2. Path resolution
LIB_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = LIB_DIR.parent
PROJECT_ROOT = SCRIPTS_DIR.parent

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

# 3. Fail-safe atomic_write export
try:
    from lib.fs_utils import atomic_write
except ImportError:
    from fs_utils import atomic_write  # type: ignore[no-redef]


# 4. Volume and identifier validation helpers (Path Traversal Defense)
WINDOWS_RESERVED_NAMES = frozenset({
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
})


def validate_volume_name(vol: str) -> str:
    """Validate volume identifier against path traversal and forbidden characters.

    Returns the validated volume name or raises ValueError.
    """
    if not vol:
        raise ValueError("Volume name cannot be empty.")
    if vol in ("all", "ALL", "all-books", "omnibus"):
        return vol
    if ".." in vol or "/" in vol or "\\" in vol:
        raise ValueError(f"Invalid volume name '{vol}': path traversal characters ('..', '/', '\\') are not allowed.")
    import re

    if not re.match(r"^[A-Za-z0-9_-]+$", vol):
        raise ValueError(f"Invalid volume name '{vol}': only alphanumeric characters, hyphens, and underscores allowed.")

    base_name = vol.split(".")[0].upper()
    if base_name in WINDOWS_RESERVED_NAMES:
        raise ValueError(f"Invalid volume name '{vol}': Windows reserved device name not allowed.")

    return vol


def sanitize_identifier(name: str, fallback: str = "item") -> str:
    """Sanitize a name to a safe filesystem identifier token [A-Za-z0-9_-]."""
    if not name:
        return fallback
    import re

    base = str(name).split(".")[0].upper()
    if base in WINDOWS_RESERVED_NAMES:
        return fallback

    safe = re.sub(r"[^A-Za-z0-9_-]", "", str(name))
    if not safe or safe.split(".")[0].upper() in WINDOWS_RESERVED_NAMES or safe.upper() in WINDOWS_RESERVED_NAMES:
        return fallback
    return safe


# 5. Canonical Prose Word Counter (ANA-01)
_FRONTMATTER_PATTERN = re.compile(r"^---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)", re.DOTALL)
_FENCED_CODE_PATTERN = re.compile(r"```[\s\S]*?```", re.DOTALL)
_HTML_COMMENT_PATTERN = re.compile(r"<!--[\s\S]*?-->", re.DOTALL)
_NW_TAG_LINE_PATTERN = re.compile(r"^@[A-Za-z0-9_-]+:", re.MULTILINE)
_WORD_PATTERN = re.compile(r"\b\w+\b", re.UNICODE)


def count_prose_words(text: str) -> int:
    """
    Canonical, Unicode-aware prose word counter across all Ars Arcanum engines.
    Strips YAML frontmatter headers, fenced code blocks, HTML comments,
    Typst comment lines (%), and NovelCrafter scene directives (@tag:).
    """
    if not text:
        return 0
    clean = _FRONTMATTER_PATTERN.sub("", text)
    clean = _FENCED_CODE_PATTERN.sub("", clean)
    clean = _HTML_COMMENT_PATTERN.sub("", clean)
    lines = []
    for ln in clean.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("@") and _NW_TAG_LINE_PATTERN.match(s):
            continue
        if s.startswith("%"):
            continue
        lines.append(ln)
    return len(_WORD_PATTERN.findall("\n".join(lines)))


# Canonical alias
count_words = count_prose_words


__all__ = [
    "LIB_DIR",
    "PROJECT_ROOT",
    "SCRIPTS_DIR",
    "WINDOWS_RESERVED_NAMES",
    "atomic_write",
    "count_prose_words",
    "count_words",
    "sanitize_identifier",
    "validate_volume_name",
]
