#!/usr/bin/env python3
"""
Ars Arcanum Manuscript Revision Density & Churn Heatmap Engine (scripts/lib/revision_heatmap.py)
=================================================================================================
Zero-dependency, offline revision density analyzer that measures manuscript churn
by comparing draft snapshots, flagging over-revised and under-revised chapters.

Capabilities:
1. Snapshot-Based Diffing:
   - scan_manuscript_snapshots(ms_dir): finds chapter .md files and computes line-level diff stats between
     the CURRENT draft and a BACKUP snapshot if available (from Backups/ dir or supplied snapshot_dir)
2. Churn Analysis:
   - analyze_revision_churn(chapter_stats): computes churn_ratio per chapter, flags outliers
   - REV-101: Over-Revised Chapter (churn_ratio > 3x average — rewriting instability)
   - REV-102: Under-Revised / Pristine Draft (no insertions OR deletions since initial — possibly forgotten)
3. Heatmap Visualization:
   - generate_revision_heatmap_html(churn_data, output_path): standalone offline CSP-compliant HTML heatmap
     with chapter-level colored churn bars (green=low, amber=medium, red=high)
4. CLI: main(argv) for 'arcanum revision-heatmap [MANUSCRIPT] [--export-html FILE] [--json] [--snapshot-dir DIR]'
"""

import argparse
import difflib
import json
import logging
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

__all__ = [
    "_CSP",
    "_FLAG_LABELS",
    "ChapterRevisionStats",
    "_bar_width",
    "_churn_color",
    "analyze_revision_churn",
    "count_words",
    "diff_line_counts",
    "generate_revision_heatmap_html",
    "main",
    "scan_manuscript_snapshots",
]

try:
    from lib.revision_heatmap_template import (
        _CSP,
        _FLAG_LABELS,
        _bar_width,
        _churn_color,
        generate_revision_heatmap_html,
    )
    from lib.scope import (
        EngineScope,
        add_scope_arguments,
        filter_manuscript_scope,
        parse_scope_args,
        resolve_manuscript_dir,
    )
except ImportError:
    from revision_heatmap_template import (  # type: ignore[no-redef]
        _CSP,
        _FLAG_LABELS,
        _bar_width,
        _churn_color,
        generate_revision_heatmap_html,
    )
    from scope import (  # type: ignore[no-redef]
        EngineScope,
        add_scope_arguments,
        filter_manuscript_scope,
        parse_scope_args,
        resolve_manuscript_dir,
    )

logger = logging.getLogger("arcanum.revision_heatmap")

# ---------------------------------------------------------------------------
# Regex helpers
# ---------------------------------------------------------------------------

_AT_TAG_RE = re.compile(r"^@[A-Za-z0-9_-]+:")
_HEADING_RE = re.compile(r"^#{1,6}\s")
_WORD_RE = re.compile(r"\b\w+\b", re.UNICODE)

# Directories to skip when scanning for chapters
_SKIP_DIRS = {"Front_Matter", "Back_Matter"}

# ---------------------------------------------------------------------------
# Dataclass
# ---------------------------------------------------------------------------


@dataclass
class ChapterRevisionStats:
    """Per-chapter revision statistics derived from snapshot diffing."""

    chapter: str       # chapter filename
    rel_path: str      # relative path from ms_dir
    word_count: int    # current word count
    insertions: int    # lines added vs snapshot (0 if no snapshot)
    deletions: int     # lines removed vs snapshot (0 if no snapshot)
    churn_score: int   # insertions + deletions
    churn_ratio: float  # churn_score / max(word_count, 1)
    has_snapshot: bool  # whether a snapshot was found for comparison
    flag: str          # '' | 'REV-101' | 'REV-102'


# ---------------------------------------------------------------------------
# Core text utilities
# ---------------------------------------------------------------------------


def count_words(text: str) -> int:
    """Count whitespace-separated words, ignoring @-tags and markdown headers.

    Lines that begin with '@tag:' syntax or '#' headings are excluded entirely
    from the word count, matching novelWriter metadata conventions.
    """
    kept_lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if _AT_TAG_RE.match(stripped):
            continue
        if _HEADING_RE.match(stripped):
            continue
        kept_lines.append(stripped)
    return len(_WORD_RE.findall("\n".join(kept_lines)))


def diff_line_counts(current_text: str, snapshot_text: str) -> tuple[int, int]:
    """Return (insertions, deletions) using difflib.unified_diff line comparison.

    Lines starting with '+' (but not '+++') are insertions.
    Lines starting with '-' (but not '---') are deletions.
    """
    current_lines = current_text.splitlines(keepends=True)
    snapshot_lines = snapshot_text.splitlines(keepends=True)

    insertions = 0
    deletions = 0

    for line in difflib.unified_diff(snapshot_lines, current_lines, lineterm=""):
        if line.startswith(("+++", "---")):
            continue
        if line.startswith("+"):
            insertions += 1
        elif line.startswith("-"):
            deletions += 1

    return insertions, deletions


# ---------------------------------------------------------------------------
# Snapshot scanning
# ---------------------------------------------------------------------------


def _build_snapshot_index(snapshot_dir: Path) -> dict[str, Path]:
    """Walk snapshot_dir recursively and map stem -> first matching path."""
    index: dict[str, Path] = {}
    try:
        for p in snapshot_dir.rglob("*.md"):
            if p.name.startswith("."):
                continue
            stem = p.stem
            if stem not in index:
                index[stem] = p
    except OSError as e:
        logger.debug("Cannot read snapshot_dir %s: %s", snapshot_dir, e)
    return index


def scan_manuscript_snapshots(
    ms_dir: Path | str | None = None,
    snapshot_dir: Path | str | None = None,
    scope: Any = None,
) -> list[ChapterRevisionStats]:
    """Scan all *.md chapter files in ms_dir recursively with scope and snapshot support."""
    target_str = resolve_manuscript_dir(ms_dir) if ms_dir else resolve_manuscript_dir()
    if ms_dir and Path(ms_dir).exists():
        p_ms = Path(ms_dir).resolve()
    elif target_str and Path(target_str).exists():
        p_ms = Path(target_str).resolve()
    else:
        p_ms = Path(ms_dir).resolve() if ms_dir else Path.cwd()

    p_snap = Path(snapshot_dir).resolve() if snapshot_dir else None
    effective_snapshot_dir = p_snap or (p_ms / "Backups")
    snapshot_index = _build_snapshot_index(effective_snapshot_dir) if effective_snapshot_dir.is_dir() else {}

    results: list[ChapterRevisionStats] = []

    if p_ms.is_file():
        current_text = p_ms.read_text(encoding="utf-8", errors="replace")
        wc = count_words(current_text)
        stem = p_ms.stem
        snapshot_path = snapshot_index.get(stem)
        snapshot_text = snapshot_path.read_text(encoding="utf-8", errors="replace") if snapshot_path else ""
        has_snapshot = snapshot_path is not None
        if has_snapshot:
            insertions, deletions = diff_line_counts(current_text, snapshot_text)
        else:
            insertions = wc
            deletions = 0
        churn_score = insertions + deletions
        churn_ratio = churn_score / max(wc, 1)
        results.append(
            ChapterRevisionStats(
                chapter=p_ms.name,
                rel_path=p_ms.name,
                word_count=wc,
                insertions=insertions,
                deletions=deletions,
                churn_score=churn_score,
                churn_ratio=churn_ratio,
                has_snapshot=has_snapshot,
                flag="",
            )
        )
        return results

    if scope:
        if not isinstance(scope, EngineScope):
            if isinstance(scope, dict):
                from lib.scope import resolve_scope
                scope = resolve_scope(scope).scope_filter
            elif isinstance(scope, str):
                from lib.scope import parse_unified_scope_string
                p_dict = parse_unified_scope_string(scope)
                scope = EngineScope(**p_dict)
        scoped_chaps, scoped_scenes, _ = filter_manuscript_scope(p_ms, scope)
        if scope.scenes and scoped_scenes:
            for s in scoped_scenes:
                current_text = s.content
                wc = count_words(current_text)
                stem = s.chapter_file.stem
                snapshot_path = snapshot_index.get(stem)
                snapshot_text = snapshot_path.read_text(encoding="utf-8", errors="replace") if snapshot_path else ""
                has_snapshot = snapshot_path is not None
                if has_snapshot:
                    insertions, deletions = diff_line_counts(current_text, snapshot_text)
                else:
                    insertions = wc
                    deletions = 0
                churn_score = insertions + deletions
                churn_ratio = churn_score / max(wc, 1)
                try:
                    rel = s.chapter_file.relative_to(p_ms)
                except ValueError:
                    rel = Path(s.chapter_file.name)
                rel_str = str(rel).replace("\\", "/")
                results.append(
                    ChapterRevisionStats(
                        chapter=f"{s.chapter_file.name}#sc{s.global_scene_idx}",
                        rel_path=f"{rel_str}#sc{s.global_scene_idx}",
                        word_count=wc,
                        insertions=insertions,
                        deletions=deletions,
                        churn_score=churn_score,
                        churn_ratio=churn_ratio,
                        has_snapshot=has_snapshot,
                        flag="",
                    )
                )
        else:
            for c in scoped_chaps:
                current_text = c.scoped_content
                wc = count_words(current_text)
                stem = c.file_path.stem
                snapshot_path = snapshot_index.get(stem)
                snapshot_text = snapshot_path.read_text(encoding="utf-8", errors="replace") if snapshot_path else ""
                has_snapshot = snapshot_path is not None
                if has_snapshot:
                    insertions, deletions = diff_line_counts(current_text, snapshot_text)
                else:
                    insertions = wc
                    deletions = 0
                churn_score = insertions + deletions
                churn_ratio = churn_score / max(wc, 1)
                try:
                    rel = c.file_path.relative_to(p_ms)
                except ValueError:
                    rel = Path(c.file_path.name)
                results.append(
                    ChapterRevisionStats(
                        chapter=c.file_path.name,
                        rel_path=str(rel).replace("\\", "/"),
                        word_count=wc,
                        insertions=insertions,
                        deletions=deletions,
                        churn_score=churn_score,
                        churn_ratio=churn_ratio,
                        has_snapshot=has_snapshot,
                        flag="",
                    )
                )
        results.sort(key=lambda s: s.rel_path)
        return results

    try:
        all_md = sorted(p_ms.rglob("*.md"))
    except OSError as e:
        logger.debug("Cannot rglob ms_dir %s: %s", p_ms, e)
        return results

    for chapter_path in all_md:
        if chapter_path.name.startswith("."):
            continue
        rel = chapter_path.relative_to(p_ms)
        if any(part in _SKIP_DIRS for part in rel.parts):
            continue
        try:
            chapter_path.relative_to(effective_snapshot_dir)
            continue
        except ValueError:
            pass

        try:
            current_text = chapter_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            logger.debug("Skipping unreadable chapter %s: %s", chapter_path, e)
            continue

        wc = count_words(current_text)
        stem = chapter_path.stem
        snapshot_path = snapshot_index.get(stem)

        if snapshot_path is not None:
            try:
                snapshot_text = snapshot_path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError) as e:
                logger.debug("Skipping unreadable snapshot %s: %s", snapshot_path, e)
                snapshot_path = None
                snapshot_text = ""
        else:
            snapshot_text = ""

        has_snapshot = snapshot_path is not None

        if has_snapshot:
            insertions, deletions = diff_line_counts(current_text, snapshot_text)
        else:
            insertions = wc
            deletions = 0

        churn_score = insertions + deletions
        churn_ratio = churn_score / max(wc, 1)

        results.append(
            ChapterRevisionStats(
                chapter=chapter_path.name,
                rel_path=str(rel).replace("\\", "/"),
                word_count=wc,
                insertions=insertions,
                deletions=deletions,
                churn_score=churn_score,
                churn_ratio=churn_ratio,
                has_snapshot=has_snapshot,
                flag="",
            )
        )

    results.sort(key=lambda s: s.rel_path)
    return results


# ---------------------------------------------------------------------------
# Churn analysis & flag assignment
# ---------------------------------------------------------------------------


def analyze_revision_churn(
    stats: list[ChapterRevisionStats],
    over_revised_threshold: float = 3.0,
) -> dict:
    """Flag REV-101 and REV-102 on each ChapterRevisionStats in-place.

    Rules
    -----
    REV-101 (Over-Revised):
        chapter.churn_ratio > over_revised_threshold * avg_churn_ratio  AND  avg_churn_ratio > 0

    REV-102 (Pristine / Under-Revised):
        chapter.churn_score == 0  AND  chapter.word_count > 50  AND  chapter.has_snapshot is True

    Returns a summary dict with total_chapters, avg_churn_score, max_churn_score,
    and a 'findings' list of dicts for flagged chapters.
    """
    if not stats:
        return {
            "total_chapters": 0,
            "avg_churn_score": 0.0,
            "max_churn_score": 0,
            "avg_churn_ratio": 0.0,
            "findings": [],
        }

    total = len(stats)
    avg_churn_score = sum(s.churn_score for s in stats) / total
    max_churn_score = max(s.churn_score for s in stats)
    avg_churn_ratio = sum(s.churn_ratio for s in stats) / total

    findings: list[dict] = []

    for chapter in stats:
        chapter.flag = ""  # reset

        # REV-101: Over-Revised
        if avg_churn_ratio > 0 and chapter.churn_ratio > over_revised_threshold * avg_churn_ratio:
            chapter.flag = "REV-101"
            findings.append({
                "id": "REV-101",
                "code": "REV-101",
                "chapter": chapter.chapter,
                "rel_path": chapter.rel_path,
                "message": (
                    f"Over-revised chapter: churn_ratio={chapter.churn_ratio:.3f} is "
                    f">{over_revised_threshold}x the average ({avg_churn_ratio:.3f}). "
                    "Consider stabilising this section."
                ),
            })
            continue  # only one flag per chapter

        # REV-102: Pristine Draft (no churn, has snapshot, non-trivial word count)
        if chapter.churn_score == 0 and chapter.word_count > 50 and chapter.has_snapshot:
            chapter.flag = "REV-102"
            findings.append({
                "id": "REV-102",
                "code": "REV-102",
                "chapter": chapter.chapter,
                "rel_path": chapter.rel_path,
                "message": (
                    f"Under-revised chapter: zero churn detected against snapshot with "
                    f"{chapter.word_count} words. This chapter may have been forgotten in revision."
                ),
            })

    return {
        "total_chapters": total,
        "avg_churn_score": avg_churn_score,
        "max_churn_score": max_churn_score,
        "avg_churn_ratio": avg_churn_ratio,
        "findings": findings,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list | None = None) -> None:
    """Entry point: arcanum revision-heatmap [MANUSCRIPT] [--export-html FILE] [--json] [--snapshot-dir DIR]"""
    parser = argparse.ArgumentParser(
        prog="arcanum revision-heatmap",
        description="Manuscript Revision Density & Churn Heatmap Engine",
    )
    parser.add_argument(
        "manuscript",
        nargs="?",
        default=None,
        help="Path to manuscript directory (default: active manuscript or current directory)",
    )
    parser.add_argument(
        "--snapshot-dir",
        metavar="DIR",
        help="Directory containing snapshot files for comparison (default: <manuscript>/Backups/)",
    )
    parser.add_argument(
        "--export-html",
        metavar="FILE",
        help="Export heatmap to this HTML file",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="output_json",
        help="Output results as JSON to stdout",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=3.0,
        metavar="FACTOR",
        help="Over-revised detection multiplier (default: 3.0)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable debug logging",
    )
    add_scope_arguments(parser, include_world=False)

    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s  %(name)s  %(message)s",
    )

    scope = parse_scope_args(args)
    target_raw = args.manuscript or scope.manuscript or (scope.books[0] if scope.books else None)
    if not target_raw:
        resolved_dir = resolve_manuscript_dir()
        ms_dir = Path(resolved_dir).resolve() if resolved_dir and Path(resolved_dir).exists() else Path(".").resolve()
    else:
        tp = Path(target_raw)
        if tp.exists():
            ms_dir = tp.resolve()
        else:
            resolved_dir = resolve_manuscript_dir(target_raw)
            if resolved_dir and Path(resolved_dir).exists():
                ms_dir = Path(resolved_dir).resolve()
            else:
                logger.error("Manuscript directory not found: %s", target_raw)
                sys.exit(1)

    snapshot_dir = Path(args.snapshot_dir).resolve() if args.snapshot_dir else None

    # Scan
    chapter_stats = scan_manuscript_snapshots(ms_dir, snapshot_dir=snapshot_dir, scope=scope)
    if not chapter_stats:
        logger.warning("No chapter files found in %s", ms_dir)
        sys.exit(0)

    # Analyse
    summary = analyze_revision_churn(chapter_stats, over_revised_threshold=args.threshold)

    churn_data: dict = {
        "manuscript": ms_dir.name,
        "chapters": chapter_stats,
        "findings": summary["findings"],
        "avg_churn_score": summary["avg_churn_score"],
        "max_churn_score": summary["max_churn_score"],
        "avg_churn_ratio": summary["avg_churn_ratio"],
        "total_chapters": summary["total_chapters"],
    }

    if args.output_json:
        # Serialise dataclasses to plain dicts
        serialisable = {
            **{k: v for k, v in churn_data.items() if k != "chapters"},
            "chapters": [asdict(c) for c in chapter_stats],
        }
        print(json.dumps(serialisable, indent=2))
        return

    if args.export_html:
        out_path = Path(args.export_html).resolve()
        generate_revision_heatmap_html(churn_data, out_path)
        print(f"Heatmap exported → {out_path}")
        return

    # Terminal summary
    print(f"\n📊 Revision Heatmap — {ms_dir.name}")
    print(f"   Chapters analysed : {summary['total_chapters']}")
    print(f"   Avg churn score   : {summary['avg_churn_score']:.1f}")
    print(f"   Max churn score   : {summary['max_churn_score']}")
    print()

    _COLORS = {
        "green": "\033[92m",
        "amber": "\033[93m",
        "red": "\033[91m",
        "reset": "\033[0m",
        "bold": "\033[1m",
    }

    for ch in chapter_stats:
        if ch.churn_ratio >= 0.5:
            color = _COLORS["red"]
        elif ch.churn_ratio >= 0.2:
            color = _COLORS["amber"]
        else:
            color = _COLORS["green"]
        flag_str = f"  [{ch.flag}]" if ch.flag else ""
        bar = "█" * min(40, max(1, round(ch.churn_ratio * 40)))
        print(
            f"  {color}{bar:<40}{_COLORS['reset']} "
            f"{ch.chapter:<40} "
            f"ratio={ch.churn_ratio:.3f} "
            f"churn={ch.churn_score}{flag_str}"
        )

    if summary["findings"]:
        print(f"\n{_COLORS['bold']}Findings:{_COLORS['reset']}")
        for finding in summary["findings"]:
            print(f"  {finding['code']}  {finding['chapter']}  — {finding['message']}")
    else:
        print("\n✓ No revision flags raised.")


if __name__ == "__main__":
    main()
