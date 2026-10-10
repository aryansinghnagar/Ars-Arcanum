#!/usr/bin/env python3
"""
Ars Arcanum Manuscript Revision Density & Churn Heatmap Engine (scripts/lib/revision_heatmap.py)
=================================================================================================
Zero-dependency, offline revision density and churn telemetry engine that measures
manuscript churn by comparing draft snapshots, multi-draft lineages, or arbitrary
revision folders, categorizing dialogue vs narrative rewrites and flagging craft anomalies.

Capabilities:
1. Semantic Word-Level & Line Diffing:
   - Tokenizes prose into words (excluding @tag: metadata lines and # markdown headings).
   - Computes Myers word additions, deletions, replacements, and dialogue vs prose splits.
2. Snapshot & Multi-Draft Baseline Discovery:
   - scan_manuscript_snapshots(ms_dir, snapshot_dir, baseline_target, scope): resolves current draft
     and compares against baseline snapshots (Backups/, parent draft, or explicit folder pair).
   - Sub-scene breakdown discovery for chapters with scene dividers.
3. 6-Tier Diagnostic Telemetry Suite (Subsystem 2 Craft Telemetry):
   - REV-101: Perfectionist High Churn (churn_ratio > 3.0x average or > 120% replacement)
   - REV-102: Pristine Draft (zero modifications against baseline snapshot)
   - REV-103: Heavy Narrative Cut (>40% baseline prose excised)
   - REV-104: Major Chapter Expansion (>50% word increase over baseline)
   - REV-105: Dialogue vs Narration Imbalance (>75% dialogue churn or >90% prose churn)
   - REV-106: Front-Loading Churn Anomaly (Opening chapters 1–3 over-edited vs rest of manuscript)
4. Authorial Constitution & Intent:
   - Respects suppressed_rules in constitution.yaml / manuscript.yaml and @intent: tags.
5. Interactive Visual Studio Dashboard & CLI:
   - 100% offline, CSP-compliant HTML5 interactive dashboard with sortable columns,
     flag filter pills, stacked dialogue/prose bars, and dark/light mode.
   - ANSI terminal telemetry overview for quick TTY feedback.
"""

from __future__ import annotations

import argparse
import difflib
import json
import logging
import re
import sys
import webbrowser
from dataclasses import asdict, dataclass, field
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
    "diff_word_counts",
    "extract_dialogue_and_prose",
    "generate_revision_heatmap_html",
    "main",
    "scan_manuscript_snapshots",
]

try:
    from lib.constitution import load_authorial_constitution
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
    from constitution import (  # type: ignore[no-redef]
        load_authorial_constitution,
    )
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
# Regex patterns
# ---------------------------------------------------------------------------

_AT_TAG_RE = re.compile(r"^@[A-Za-z0-9_-]+:")
_INTENT_RE = re.compile(r"^@intent:\s*([A-Za-z0-9_-]+)", re.MULTILINE | re.IGNORECASE)
_HEADING_RE = re.compile(r"^#{1,6}\s")
_WORD_RE = re.compile(r"\b\w+\b", re.UNICODE)
_DIALOGUE_RE = re.compile(r'(?:"[^"\\]*(?:\\.[^"\\]*)*"|“[^”]*”|‘[^’]*’|«[^»]*»|„[^“]*”)', re.UNICODE)
_SCENE_SPLIT_RE = re.compile(r"(?:\n\s*(?:---|\*\*\*|___|<!--\s*scene\s*-->|###+\s+Scene\b[^\n]*)\s*\n)", re.UNICODE)

# Directories to skip when scanning for chapters
_SKIP_DIRS = {"Front_Matter", "Back_Matter"}


# ---------------------------------------------------------------------------
# Dataclass
# ---------------------------------------------------------------------------


@dataclass
class ChapterRevisionStats:
    """Per-chapter revision statistics derived from snapshot or draft diffing."""

    chapter: str                          # chapter filename or display title
    rel_path: str                         # relative path from manuscript root
    word_count: int                       # current word count
    insertions: int                       # words added vs baseline (or line additions)
    deletions: int                        # words deleted vs baseline (or line deletions)
    churn_score: int                      # insertions + deletions
    churn_ratio: float                    # churn_score / max(word_count, baseline_word_count, 1)
    has_snapshot: bool                    # whether a snapshot/baseline was found
    flag: str = ""                        # primary flag: '' | 'REV-101' | 'REV-102' | etc.
    flags: list[str] = field(default_factory=list)  # all matching flags
    baseline_word_count: int = 0          # baseline snapshot word count
    line_insertions: int = 0              # structural line additions
    line_deletions: int = 0               # structural line deletions
    dialogue_word_count: int = 0          # current dialogue words
    dialogue_churn_score: int = 0         # dialogue words added + deleted
    dialogue_churn_ratio: float = 0.0     # dialogue_churn_score / max(dialogue_word_count, 1)
    prose_word_count: int = 0             # current narrative/exposition words
    prose_churn_score: int = 0            # prose words added + deleted
    prose_churn_ratio: float = 0.0        # prose_churn_score / max(prose_word_count, 1)
    intent: str = ""                      # document-level @intent tag if present
    sub_scenes: list[dict[str, Any]] = field(default_factory=list)  # scene breakdowns


# ---------------------------------------------------------------------------
# Core text utilities & word-level diffing
# ---------------------------------------------------------------------------


def clean_prose_lines(text: str) -> str:
    """Filter out metadata lines starting with '@tag:' and '#' markdown headings."""
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
    return "\n".join(kept_lines)


def count_words(text: str) -> int:
    """Count whitespace-separated words, ignoring @-tags and markdown headers."""
    cleaned = clean_prose_lines(text)
    return len(_WORD_RE.findall(cleaned))


def extract_dialogue_and_prose(text: str) -> tuple[str, str, int, int]:
    """Separate text into dialogue quotes and narrative prose.

    Returns
    -------
    tuple[str, str, int, int]
        (dialogue_text, prose_text, dialogue_word_count, prose_word_count)
    """
    cleaned = clean_prose_lines(text)
    dialogue_matches = _DIALOGUE_RE.findall(cleaned)
    dialogue_text = " ".join(dialogue_matches)
    prose_text = _DIALOGUE_RE.sub(" ", cleaned)

    d_words = len(_WORD_RE.findall(dialogue_text))
    p_words = len(_WORD_RE.findall(prose_text))
    return dialogue_text, prose_text, d_words, p_words


def diff_word_counts(
    current_text: str,
    baseline_text: str,
) -> tuple[int, int, int, int, int, int]:
    """Compute word-level additions and deletions with dialogue/prose breakdown.

    Returns
    -------
    tuple[int, int, int, int, int, int]
        (total_added, total_deleted, diag_added, diag_deleted, prose_added, prose_deleted)
    """
    clean_curr = clean_prose_lines(current_text)
    clean_base = clean_prose_lines(baseline_text)

    curr_words = _WORD_RE.findall(clean_curr)
    base_words = _WORD_RE.findall(clean_base)

    matcher = difflib.SequenceMatcher(None, base_words, curr_words)
    total_add = 0
    total_del = 0
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag in ("replace", "insert"):
            total_add += j2 - j1
        if tag in ("replace", "delete"):
            total_del += i2 - i1

    # Dialogue diff
    diag_curr, prose_curr, _, _ = extract_dialogue_and_prose(current_text)
    diag_base, prose_base, _, _ = extract_dialogue_and_prose(baseline_text)

    d_curr_words = _WORD_RE.findall(diag_curr)
    d_base_words = _WORD_RE.findall(diag_base)
    d_matcher = difflib.SequenceMatcher(None, d_base_words, d_curr_words)
    diag_add = 0
    diag_del = 0
    for tag, i1, i2, j1, j2 in d_matcher.get_opcodes():
        if tag in ("replace", "insert"):
            diag_add += j2 - j1
        if tag in ("replace", "delete"):
            diag_del += i2 - i1

    # Prose diff
    p_curr_words = _WORD_RE.findall(prose_curr)
    p_base_words = _WORD_RE.findall(prose_base)
    p_matcher = difflib.SequenceMatcher(None, p_base_words, p_curr_words)
    prose_add = 0
    prose_del = 0
    for tag, i1, i2, j1, j2 in p_matcher.get_opcodes():
        if tag in ("replace", "insert"):
            prose_add += j2 - j1
        if tag in ("replace", "delete"):
            prose_del += i2 - i1

    return total_add, total_del, diag_add, diag_del, prose_add, prose_del


def diff_line_counts(current_text: str, snapshot_text: str) -> tuple[int, int]:
    """Return (insertions, deletions) using difflib.unified_diff line comparison."""
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


def extract_sub_scenes(
    current_text: str,
    baseline_text: str | None = None,
) -> list[dict[str, Any]]:
    """Extract and calculate scene-level churn breakdowns within a chapter."""
    curr_scenes = _SCENE_SPLIT_RE.split(current_text)
    if len(curr_scenes) <= 1:
        return []

    base_scenes = _SCENE_SPLIT_RE.split(baseline_text) if baseline_text else []
    sub_scenes: list[dict[str, Any]] = []

    for idx, sc_text in enumerate(curr_scenes):
        sc_wc = count_words(sc_text)
        b_text = base_scenes[idx] if idx < len(base_scenes) else ""
        if b_text:
            s_add, s_del, _, _, _, _ = diff_word_counts(sc_text, b_text)
            s_churn = s_add + s_del
            s_ratio = s_churn / max(sc_wc, count_words(b_text), 1)
        else:
            s_add = 0
            s_del = 0
            s_churn = 0
            s_ratio = 0.0

        sub_scenes.append({
            "scene_idx": idx + 1,
            "name": f"Scene {idx+1}",
            "word_count": sc_wc,
            "churn_score": s_churn,
            "churn_ratio": s_ratio,
            "insertions": s_add,
            "deletions": s_del,
        })

    return sub_scenes


# ---------------------------------------------------------------------------
# Snapshot & Baseline Scanning
# ---------------------------------------------------------------------------


def _build_snapshot_index(snapshot_dir: Path) -> dict[str, Path]:
    """Walk snapshot_dir recursively and map stem/rel_path -> matching path."""
    index: dict[str, Path] = {}
    try:
        for p in snapshot_dir.rglob("*.md"):
            if p.name.startswith("."):
                continue
            stem = p.stem
            if stem not in index:
                index[stem] = p
            try:
                rel = str(p.relative_to(snapshot_dir)).replace("\\", "/")
                index[rel] = p
            except ValueError:
                pass
    except OSError as e:
        logger.debug("Cannot read snapshot_dir %s: %s", snapshot_dir, e)
    return index


def _extract_intent_tag(text: str) -> str:
    """Extract @intent: tag value if present."""
    m = _INTENT_RE.search(text)
    return m.group(1).lower().strip() if m else ""


def scan_manuscript_snapshots(
    ms_dir: Path | str | None = None,
    snapshot_dir: Path | str | None = None,
    baseline_target: Path | str | None = None,
    scope: Any = None,
) -> list[ChapterRevisionStats]:
    """Scan chapter *.md files in ms_dir recursively with scope and baseline support.

    Parameters
    ----------
    ms_dir:
        Path to manuscript or current draft directory.
    snapshot_dir:
        Explicit directory containing baseline snapshots (or Backups/).
    baseline_target:
        Optional secondary draft directory to compare against (e.g. Draft-01 vs Draft-02).
    scope:
        Optional EngineScope or scope dict/string for granular slicing.
    """
    target_str = resolve_manuscript_dir(ms_dir) if ms_dir else resolve_manuscript_dir()
    if ms_dir and Path(ms_dir).exists():
        p_ms = Path(ms_dir).resolve()
    elif target_str and Path(target_str).exists():
        p_ms = Path(target_str).resolve()
    else:
        p_ms = Path(ms_dir).resolve() if ms_dir else Path.cwd()

    # Determine baseline directory
    p_baseline: Path | None = None
    if baseline_target and Path(baseline_target).is_dir():
        p_baseline = Path(baseline_target).resolve()
    elif snapshot_dir and Path(snapshot_dir).is_dir():
        p_baseline = Path(snapshot_dir).resolve()
    elif (p_ms / "Backups").is_dir():
        p_baseline = p_ms / "Backups"

    snapshot_index = _build_snapshot_index(p_baseline) if p_baseline else {}
    results: list[ChapterRevisionStats] = []

    # Single file scanning
    if p_ms.is_file():
        current_text = p_ms.read_text(encoding="utf-8", errors="replace")
        wc = count_words(current_text)
        stem = p_ms.stem
        snapshot_path = snapshot_index.get(stem)
        snapshot_text = snapshot_path.read_text(encoding="utf-8", errors="replace") if snapshot_path else ""
        has_snapshot = snapshot_path is not None
        b_wc = count_words(snapshot_text) if has_snapshot else 0
        intent = _extract_intent_tag(current_text)

        _, _, d_wc, p_wc = extract_dialogue_and_prose(current_text)

        if has_snapshot:
            w_add, w_del, d_add, d_del, pr_add, pr_del = diff_word_counts(current_text, snapshot_text)
            l_ins, l_del = diff_line_counts(current_text, snapshot_text)
            churn_score = w_add + w_del
            churn_ratio = churn_score / max(wc, b_wc, 1)
            d_churn = d_add + d_del
            d_ratio = d_churn / max(d_wc, 1)
            p_churn = pr_add + pr_del
            p_ratio = p_churn / max(p_wc, 1)
        else:
            w_add = w_del = d_churn = p_churn = l_ins = l_del = churn_score = 0
            churn_ratio = d_ratio = p_ratio = 0.0

        sub_scenes = extract_sub_scenes(current_text, snapshot_text if has_snapshot else None)

        results.append(
            ChapterRevisionStats(
                chapter=p_ms.name,
                rel_path=p_ms.name,
                word_count=wc,
                baseline_word_count=b_wc,
                insertions=w_add,
                deletions=w_del,
                line_insertions=l_ins,
                line_deletions=l_del,
                churn_score=churn_score,
                churn_ratio=churn_ratio,
                dialogue_word_count=d_wc,
                dialogue_churn_score=d_churn,
                dialogue_churn_ratio=d_ratio,
                prose_word_count=p_wc,
                prose_churn_score=p_churn,
                prose_churn_ratio=p_ratio,
                has_snapshot=has_snapshot,
                flag="",
                flags=[],
                intent=intent,
                sub_scenes=sub_scenes,
            )
        )
        return results

    # Scoped scanning
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
                b_wc = count_words(snapshot_text) if has_snapshot else 0
                intent = _extract_intent_tag(current_text)

                _, _, d_wc, p_wc = extract_dialogue_and_prose(current_text)

                if has_snapshot:
                    w_add, w_del, d_add, d_del, pr_add, pr_del = diff_word_counts(current_text, snapshot_text)
                    l_ins, l_del = diff_line_counts(current_text, snapshot_text)
                    churn_score = w_add + w_del
                    churn_ratio = churn_score / max(wc, b_wc, 1)
                    d_churn = d_add + d_del
                    d_ratio = d_churn / max(d_wc, 1)
                    p_churn = pr_add + pr_del
                    p_ratio = p_churn / max(p_wc, 1)
                else:
                    w_add = w_del = d_churn = p_churn = l_ins = l_del = churn_score = 0
                    churn_ratio = d_ratio = p_ratio = 0.0

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
                        baseline_word_count=b_wc,
                        insertions=w_add,
                        deletions=w_del,
                        line_insertions=l_ins,
                        line_deletions=l_del,
                        churn_score=churn_score,
                        churn_ratio=churn_ratio,
                        dialogue_word_count=d_wc,
                        dialogue_churn_score=d_churn,
                        dialogue_churn_ratio=d_ratio,
                        prose_word_count=p_wc,
                        prose_churn_score=p_churn,
                        prose_churn_ratio=p_ratio,
                        has_snapshot=has_snapshot,
                        flag="",
                        flags=[],
                        intent=intent,
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
                b_wc = count_words(snapshot_text) if has_snapshot else 0
                intent = _extract_intent_tag(current_text)

                _, _, d_wc, p_wc = extract_dialogue_and_prose(current_text)

                if has_snapshot:
                    w_add, w_del, d_add, d_del, pr_add, pr_del = diff_word_counts(current_text, snapshot_text)
                    l_ins, l_del = diff_line_counts(current_text, snapshot_text)
                    churn_score = w_add + w_del
                    churn_ratio = churn_score / max(wc, b_wc, 1)
                    d_churn = d_add + d_del
                    d_ratio = d_churn / max(d_wc, 1)
                    p_churn = pr_add + pr_del
                    p_ratio = p_churn / max(p_wc, 1)
                else:
                    w_add = w_del = d_churn = p_churn = l_ins = l_del = churn_score = 0
                    churn_ratio = d_ratio = p_ratio = 0.0

                try:
                    rel = c.file_path.relative_to(p_ms)
                except ValueError:
                    rel = Path(c.file_path.name)

                sub_scenes = extract_sub_scenes(current_text, snapshot_text if has_snapshot else None)

                results.append(
                    ChapterRevisionStats(
                        chapter=c.file_path.name,
                        rel_path=str(rel).replace("\\", "/"),
                        word_count=wc,
                        baseline_word_count=b_wc,
                        insertions=w_add,
                        deletions=w_del,
                        line_insertions=l_ins,
                        line_deletions=l_del,
                        churn_score=churn_score,
                        churn_ratio=churn_ratio,
                        dialogue_word_count=d_wc,
                        dialogue_churn_score=d_churn,
                        dialogue_churn_ratio=d_ratio,
                        prose_word_count=p_wc,
                        prose_churn_score=p_churn,
                        prose_churn_ratio=p_ratio,
                        has_snapshot=has_snapshot,
                        flag="",
                        flags=[],
                        intent=intent,
                        sub_scenes=sub_scenes,
                    )
                )
        results.sort(key=lambda s: s.rel_path)
        return results

    # Full directory walk
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
        if p_baseline:
            try:
                chapter_path.relative_to(p_baseline)
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
        rel_key = str(rel).replace("\\", "/")
        snapshot_path = snapshot_index.get(rel_key) or snapshot_index.get(stem)

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
        b_wc = count_words(snapshot_text) if has_snapshot else 0
        intent = _extract_intent_tag(current_text)

        _, _, d_wc, p_wc = extract_dialogue_and_prose(current_text)

        if has_snapshot:
            w_add, w_del, d_add, d_del, pr_add, pr_del = diff_word_counts(current_text, snapshot_text)
            l_ins, l_del = diff_line_counts(current_text, snapshot_text)
            churn_score = w_add + w_del
            churn_ratio = churn_score / max(wc, b_wc, 1)
            d_churn = d_add + d_del
            d_ratio = d_churn / max(d_wc, 1)
            p_churn = pr_add + pr_del
            p_ratio = p_churn / max(p_wc, 1)
        else:
            w_add = w_del = d_churn = p_churn = l_ins = l_del = churn_score = 0
            churn_ratio = d_ratio = p_ratio = 0.0

        sub_scenes = extract_sub_scenes(current_text, snapshot_text if has_snapshot else None)

        results.append(
            ChapterRevisionStats(
                chapter=chapter_path.name,
                rel_path=str(rel).replace("\\", "/"),
                word_count=wc,
                baseline_word_count=b_wc,
                insertions=w_add,
                deletions=w_del,
                line_insertions=l_ins,
                line_deletions=l_del,
                churn_score=churn_score,
                churn_ratio=churn_ratio,
                dialogue_word_count=d_wc,
                dialogue_churn_score=d_churn,
                dialogue_churn_ratio=d_ratio,
                prose_word_count=p_wc,
                prose_churn_score=p_churn,
                prose_churn_ratio=p_ratio,
                has_snapshot=has_snapshot,
                flag="",
                flags=[],
                intent=intent,
                sub_scenes=sub_scenes,
            )
        )

    results.sort(key=lambda s: s.rel_path)
    return results


# ---------------------------------------------------------------------------
# Churn Analysis & 6-Tier Diagnostic Telemetry Engine
# ---------------------------------------------------------------------------


def analyze_revision_churn(
    stats: list[ChapterRevisionStats],
    over_revised_threshold: float = 3.0,
    cut_threshold: float = 0.40,
    expansion_threshold: float = 0.50,
    suppressed_rules: list[str] | None = None,
) -> dict[str, Any]:
    """Flag REV-101 through REV-106 diagnostic findings across chapter stats.

    Rules
    -----
    REV-101 (Perfectionist High Churn):
        chapter.churn_ratio > over_revised_threshold * avg_churn_ratio OR churn_ratio >= 1.20
    REV-102 (Pristine / Untouched Draft):
        chapter.churn_score == 0 AND chapter.word_count > 50 AND chapter.has_snapshot is True
    REV-103 (Heavy Narrative Cut):
        chapter.deletions >= cut_threshold * chapter.baseline_word_count
    REV-104 (Major Chapter Expansion):
        chapter.insertions >= expansion_threshold * chapter.baseline_word_count
    REV-105 (Dialogue vs Narration Imbalance):
        Dialogue churn >= 75% or Exposition churn >= 90% when total churn >= 50
    REV-106 (Front-Loading Churn Anomaly):
        Opening chapters (Ch 1-3) average >2.5x higher churn ratio than remaining chapters
    """
    if suppressed_rules is None:
        try:
            suppressed_rules = load_authorial_constitution().get("diagnostics", {}).get("suppressed_rules", [])
        except Exception:
            suppressed_rules = []

    suppressed_set = set(suppressed_rules or [])

    if not stats:
        return {
            "total_chapters": 0,
            "total_words": 0,
            "total_baseline_words": 0,
            "avg_churn_score": 0.0,
            "max_churn_score": 0,
            "avg_churn_ratio": 0.0,
            "total_dialogue_words": 0,
            "total_dialogue_churn": 0,
            "dialogue_churn_percentage": 0.0,
            "findings": [],
        }

    total = len(stats)
    total_words = sum(s.word_count for s in stats)
    total_baseline_words = sum(s.baseline_word_count for s in stats)
    total_churn_score = sum(s.churn_score for s in stats)
    avg_churn_score = total_churn_score / total
    max_churn_score = max((s.churn_score for s in stats), default=0)
    avg_churn_ratio = sum(s.churn_ratio for s in stats) / total
    total_dialogue_words = sum(s.dialogue_word_count for s in stats)
    total_dialogue_churn = sum(s.dialogue_churn_score for s in stats)
    dialogue_churn_pct = round((total_dialogue_churn / max(1, total_churn_score)) * 100.0, 1)

    findings: list[dict[str, Any]] = []

    for chapter in stats:
        chapter.flags = []
        chapter.flag = ""

        # Intent directive check
        is_deliberate = chapter.intent in ("deliberate", "raw-draft", "experimental", "high-churn")

        # REV-101: High Revision Density / Perfectionist Loop
        if (
            "REV-101" not in suppressed_set
            and not is_deliberate
            and avg_churn_ratio > 0
            and (chapter.churn_ratio > over_revised_threshold * avg_churn_ratio or chapter.churn_ratio >= 1.20)
            and chapter.churn_score >= 10
        ):
            chapter.flags.append("REV-101")
            findings.append({
                "id": "REV-101",
                "code": "REV-101",
                "severity": 3,
                "severity_label": "OBSERVATION",
                "chapter": chapter.chapter,
                "rel_path": chapter.rel_path,
                "message": (
                    f"High revision density: churn_ratio={chapter.churn_ratio:.3f} is "
                    f">{over_revised_threshold:.1f}x the average ({avg_churn_ratio:.3f}) or exceeds 120% replacement."
                ),
                "suggestion": "Review scene objective to avoid endless polishing loops; consider locking this chapter and advancing forward.",
            })

        # REV-102: Pristine Draft (no churn, has snapshot, substantial word count)
        if (
            "REV-102" not in suppressed_set
            and not is_deliberate
            and chapter.churn_score == 0
            and chapter.word_count > 50
            and chapter.has_snapshot
        ):
            chapter.flags.append("REV-102")
            findings.append({
                "id": "REV-102",
                "code": "REV-102",
                "severity": 3,
                "severity_label": "OBSERVATION",
                "chapter": chapter.chapter,
                "rel_path": chapter.rel_path,
                "message": f"Pristine draft: zero modifications detected against baseline snapshot ({chapter.word_count} words).",
                "suggestion": "Schedule developmental read-through and line-editing pass.",
            })

        # REV-103: Heavy Narrative Cut / Excision
        if (
            "REV-103" not in suppressed_set
            and not is_deliberate
            and chapter.has_snapshot
            and chapter.baseline_word_count >= 50
            and chapter.deletions >= cut_threshold * chapter.baseline_word_count
        ):
            chapter.flags.append("REV-103")
            cut_pct = (chapter.deletions / max(chapter.baseline_word_count, 1)) * 100.0
            findings.append({
                "id": "REV-103",
                "code": "REV-103",
                "severity": 2,
                "severity_label": "LENS_NOTE",
                "chapter": chapter.chapter,
                "rel_path": chapter.rel_path,
                "message": f"Heavy narrative cut: {chapter.deletions} words deleted ({cut_pct:.1f}% reduction from baseline {chapter.baseline_word_count} words).",
                "suggestion": "Verify no unresolved plot threads or excised character introductions; consider saving cut passages to a Scraps/ vault.",
            })

        # REV-104: Major Chapter Expansion / Bloat
        if (
            "REV-104" not in suppressed_set
            and not is_deliberate
            and chapter.has_snapshot
            and chapter.baseline_word_count >= 50
            and chapter.insertions >= expansion_threshold * chapter.baseline_word_count
        ):
            chapter.flags.append("REV-104")
            exp_pct = (chapter.insertions / max(chapter.baseline_word_count, 1)) * 100.0
            findings.append({
                "id": "REV-104",
                "code": "REV-104",
                "severity": 2,
                "severity_label": "LENS_NOTE",
                "chapter": chapter.chapter,
                "rel_path": chapter.rel_path,
                    "message": f"Major chapter expansion: +{chapter.insertions} words added (+{exp_pct:.1f}% expansion over baseline).",
                    "suggestion": "Evaluate scene pacing and chapter word count balance against neighboring chapters.",
                })

        # REV-105: Dialogue vs Narration Churn Imbalance
        if "REV-105" not in suppressed_set and not is_deliberate and chapter.has_snapshot and chapter.churn_score >= 50:
            diag_ratio = chapter.dialogue_churn_score / max(chapter.churn_score, 1)
            prose_ratio = chapter.prose_churn_score / max(chapter.churn_score, 1)
            if diag_ratio >= 0.75:
                chapter.flags.append("REV-105")
                findings.append({
                    "id": "REV-105",
                    "code": "REV-105",
                    "severity": 1,
                    "severity_label": "SUGGESTION",
                    "chapter": chapter.chapter,
                    "rel_path": chapter.rel_path,
                    "message": f"Dialogue-concentrated revision: {diag_ratio * 100:.0f}% of churn occurred in spoken character dialogue.",
                    "suggestion": "Ensure narrative blocking, character actions, and sensory details match updated dialogue cadence.",
                })
            elif prose_ratio >= 0.90 and chapter.dialogue_word_count > 30:
                chapter.flags.append("REV-105")
                findings.append({
                    "id": "REV-105",
                    "code": "REV-105",
                    "severity": 1,
                    "severity_label": "SUGGESTION",
                    "chapter": chapter.chapter,
                    "rel_path": chapter.rel_path,
                    "message": f"Exposition-concentrated revision: {prose_ratio * 100:.0f}% of churn occurred in narrative prose while dialogue remained static.",
                    "suggestion": "Check if character spoken reactions should reflect updated scene atmosphere and pacing changes.",
                })

        chapter.flag = chapter.flags[0] if chapter.flags else ""

    # REV-106: Front-Loading Churn Anomaly across entire manuscript
    if "REV-106" not in suppressed_set and len(stats) >= 5:
        early_chaps = stats[:3]
        late_chaps = stats[3:]
        early_avg = sum(s.churn_ratio for s in early_chaps) / len(early_chaps)
        late_avg = sum(s.churn_ratio for s in late_chaps) / len(late_chaps)

        if early_avg > 2.5 * late_avg and early_avg >= 0.15:
            for s in early_chaps:
                if "REV-106" not in s.flags:
                    s.flags.append("REV-106")
                    if not s.flag:
                        s.flag = "REV-106"
            findings.append({
                "id": "REV-106",
                "code": "REV-106",
                "severity": 3,
                "severity_label": "OBSERVATION",
                "chapter": "Chapters 1–3 (Opening Arc)",
                "rel_path": stats[0].rel_path,
                "message": f"Front-loading churn anomaly: Opening chapters average {early_avg:.3f} churn ratio, >2.5x higher than later chapters ({late_avg:.3f}).",
                "suggestion": "Classic perfectionist opening trap: consider freezing chapters 1–3 to focus drafting energy on Act 2/3 progression.",
            })

    return {
        "total_chapters": total,
        "total_words": total_words,
        "total_baseline_words": total_baseline_words,
        "avg_churn_score": avg_churn_score,
        "max_churn_score": max_churn_score,
        "avg_churn_ratio": avg_churn_ratio,
        "total_dialogue_words": total_dialogue_words,
        "total_dialogue_churn": total_dialogue_churn,
        "dialogue_churn_percentage": dialogue_churn_pct,
        "findings": findings,
    }


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> None:
    """Entry point: arcanum revision-heatmap [MANUSCRIPT] [BASELINE] [--html FILE] [--open] [--json]"""
    parser = argparse.ArgumentParser(
        prog="arcanum revision-heatmap",
        description="Manuscript Revision Density & Churn Telemetry Studio",
    )
    parser.add_argument(
        "manuscript",
        nargs="?",
        default=None,
        help="Path to manuscript or current draft directory",
    )
    parser.add_argument(
        "baseline",
        nargs="?",
        default=None,
        help="Optional path to baseline snapshot or prior draft directory for comparison",
    )
    parser.add_argument(
        "--snapshot-dir",
        metavar="DIR",
        help="Directory containing snapshot files for comparison (default: <manuscript>/Backups/)",
    )
    parser.add_argument(
        "--export-html",
        "--html",
        metavar="FILE",
        dest="export_html",
        help="Export interactive Studio Dashboard to this HTML file",
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="Automatically open generated visual Studio Dashboard in default browser",
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
        "--cut-threshold",
        type=float,
        default=0.40,
        metavar="RATIO",
        help="Heavy deletion detection threshold (default: 0.40 / 40%%)",
    )
    parser.add_argument(
        "--expansion-threshold",
        type=float,
        default=0.50,
        metavar="RATIO",
        help="Major expansion detection threshold (default: 0.50 / 50%%)",
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

    baseline_dir = Path(args.baseline).resolve() if args.baseline else None
    snapshot_dir = Path(args.snapshot_dir).resolve() if args.snapshot_dir else None

    # Scan
    chapter_stats = scan_manuscript_snapshots(
        ms_dir,
        snapshot_dir=snapshot_dir,
        baseline_target=baseline_dir,
        scope=scope,
    )
    if not chapter_stats:
        logger.warning("No chapter files found in %s", ms_dir)
        sys.exit(0)

    # Analyse
    summary = analyze_revision_churn(
        chapter_stats,
        over_revised_threshold=args.threshold,
        cut_threshold=args.cut_threshold,
        expansion_threshold=args.expansion_threshold,
    )

    baseline_desc = str(baseline_dir.name if baseline_dir else (snapshot_dir.name if snapshot_dir else "Backups/ Snapshots"))

    churn_data: dict[str, Any] = {
        "manuscript": ms_dir.name,
        "baseline_source": baseline_desc,
        "chapters": chapter_stats,
        "findings": summary["findings"],
        "avg_churn_score": summary["avg_churn_score"],
        "max_churn_score": summary["max_churn_score"],
        "avg_churn_ratio": summary["avg_churn_ratio"],
        "total_chapters": summary["total_chapters"],
        "total_words": summary["total_words"],
        "total_baseline_words": summary["total_baseline_words"],
        "total_dialogue_words": summary["total_dialogue_words"],
        "total_dialogue_churn": summary["total_dialogue_churn"],
        "dialogue_churn_percentage": summary["dialogue_churn_percentage"],
    }

    if args.output_json:
        serialisable = {
            **{k: v for k, v in churn_data.items() if k != "chapters"},
            "chapters": [asdict(c) for c in chapter_stats],
        }
        print(json.dumps(serialisable, indent=2))
        return

    if args.export_html or args.open:
        out_path = Path(args.export_html).resolve() if args.export_html else ms_dir / "revision_heatmap.html"
        generate_revision_heatmap_html(churn_data, out_path)
        print(f"\n✨ Interactive Revision Heatmap Studio exported → {out_path}")
        if args.open:
            try:
                webbrowser.open(out_path.as_uri())
                print(f"🚀 Opened visual dashboard in browser: {out_path.name}")
            except Exception as e:
                logger.debug("Could not launch browser: %s", e)
        return

    # Terminal summary
    _COLORS = {
        "green": "\033[92m",
        "amber": "\033[93m",
        "red": "\033[91m",
        "indigo": "\033[94m",
        "reset": "\033[0m",
        "bold": "\033[1m",
        "dim": "\033[2m",
    }

    print(f"\n📊 {_COLORS['bold']}Revision Heatmap Studio — {ms_dir.name}{_COLORS['reset']}")
    print(f"   Baseline Sourced  : {baseline_desc}")
    print(f"   Chapters analysed : {summary['total_chapters']}")
    print(f"   Total Word Count  : {summary['total_words']:,} (Δ {summary['total_words'] - summary['total_baseline_words']:+,} vs baseline)")
    print(f"   Avg churn score   : {summary['avg_churn_score']:.1f} words/chapter")
    print(f"   Avg churn ratio   : {summary['avg_churn_ratio']:.3f}")
    print(f"   Dialogue Churn    : {summary['dialogue_churn_percentage']}% of total rewrites")
    print()

    for ch in chapter_stats:
        if ch.churn_ratio >= 0.5:
            color = _COLORS["red"]
        elif ch.churn_ratio >= 0.2:
            color = _COLORS["amber"]
        else:
            color = _COLORS["green"]

        flag_str = f"  [{ch.flag}]" if ch.flag else ""
        bar = "█" * min(30, max(1, round(ch.churn_ratio * 30)))
        diag_ind = f" (💬 {ch.dialogue_churn_score}w)" if ch.dialogue_churn_score > 0 else ""

        print(
            f"  {color}{bar:<30}{_COLORS['reset']} "
            f"{ch.chapter:<36} "
            f"ratio={ch.churn_ratio:.3f} "
            f"churn={ch.churn_score:<4}{diag_ind}{flag_str}"
        )

    if summary["findings"]:
        print(f"\n{_COLORS['bold']}🔍 Editorial Telemetry & Advisory Findings ({len(summary['findings'])}):{_COLORS['reset']}")
        for finding in summary["findings"]:
            code_col = _COLORS["red"] if finding["code"] == "REV-101" else _COLORS["amber"]
            print(f"  {code_col}[{finding['code']}]{_COLORS['reset']} {finding['chapter']} — {finding['message']}")
            if finding.get("suggestion"):
                print(f"    {_COLORS['dim']}↳ Craft Advisory: {finding['suggestion']}{_COLORS['reset']}")
    else:
        print(f"\n{_COLORS['green']}✓ No revision flags raised.{_COLORS['reset']}")

    print(f"\n{_COLORS['dim']}💡 Tip: Run with '--html studio.html --open' to launch the interactive visual Studio Dashboard.{_COLORS['reset']}\n")


if __name__ == "__main__":
    main()
