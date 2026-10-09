#!/usr/bin/env python3
"""
Ars Arcanum Unicode Prose Word Count & Manuscript Telemetry (scripts/lib/word_counter.py)
========================================================================================
Calculates accurate Unicode prose word counts, scene totals, POV distributions,
dialogue vs. narrative ratios, reading/audiobook time estimations, and target velocity
metrics across novel manuscripts and lore vaults.

Features:
- Unicode-aware prose tokenization with CriticMarkup removal and CJK ideograph support
- Dialogue vs. narrative prose ratio analysis
- Estimated reading time (~225 WPM) and audiobook duration (~150 WPM)
- Scope-aware multi-volume and draft resolution
- ANSI color gradient telemetry for interactive TTY
- Formatted CLI tables, Markdown reports, JSON output, and standalone HTML5 Velocity Studio
"""

from __future__ import annotations

import argparse
import json
import logging
import math
import re
import sys
from pathlib import Path
from typing import Any

try:
    from lib._bootstrap import count_prose_words
    from lib.frontmatter import extract_frontmatter_and_body, parse_yaml_document
    from lib.scope import EngineScope, filter_manuscript_scope, resolve_manuscript_path
    from lib.velocity_template import render_velocity_html
    from lib.writing_sprint import get_velocity_metrics
except ImportError:
    from _bootstrap import count_prose_words
    from frontmatter import extract_frontmatter_and_body, parse_yaml_document
    from scope import EngineScope, filter_manuscript_scope, resolve_manuscript_path
    try:
        from velocity_template import render_velocity_html
    except ImportError:
        render_velocity_html = None  # type: ignore[assignment]
    try:
        from writing_sprint import get_velocity_metrics
    except ImportError:
        get_velocity_metrics = None  # type: ignore[assignment]

logger = logging.getLogger("arcanum.word_counter")

# Regex patterns for CriticMarkup and Dialogue
_CRITIC_MARKUP_PATTERN = re.compile(
    r"\{--[\s\S]*?--\}|\{\+\+[\s\S]*?\+\+\}|\{~~[\s\S]*?~>[\s\S]*?~~\}|\{==[\s\S]*?==\}|\{>>[\s\S]*?<<\}",
    re.UNICODE,
)
_CJK_CHAR_PATTERN = re.compile(r"[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]", re.UNICODE)
_DIALOGUE_PATTERN = re.compile(r'(?:"[^"\\]*(?:\\.[^"\\]*)*"|“[^”]*”|‘[^’]*’)', re.UNICODE)


def count_prose_words_advanced(text: str) -> dict[str, Any]:
    """
    Advanced prose tokenization measuring total words, CJK characters,
    dialogue words, narrative words, and dialogue percentage.
    Strips CriticMarkup comments and deletions before counting.
    """
    if not text:
        return {
            "total_words": 0,
            "cjk_characters": 0,
            "dialogue_words": 0,
            "narrative_words": 0,
            "dialogue_percentage": 0.0,
        }

    # Strip CriticMarkup deletion blocks and comments
    clean_text = _CRITIC_MARKUP_PATTERN.sub("", text)

    # Base unicode prose word count from bootstrap
    base_words = count_prose_words(clean_text)

    # CJK character count (count CJK ideographs as word equivalents if not already spaced)
    cjk_chars = len(_CJK_CHAR_PATTERN.findall(clean_text))

    # Extract dialogue quotes
    dialogue_matches = _DIALOGUE_PATTERN.findall(clean_text)
    dialogue_words = sum(count_prose_words(m) for m in dialogue_matches)

    total_words = base_words
    dialogue_words = min(total_words, dialogue_words)
    narrative_words = max(0, total_words - dialogue_words)
    dialogue_pct = round((dialogue_words / max(1, total_words)) * 100.0, 1)

    return {
        "total_words": total_words,
        "cjk_characters": cjk_chars,
        "dialogue_words": dialogue_words,
        "narrative_words": narrative_words,
        "dialogue_percentage": dialogue_pct,
    }


def _is_interactive_tty() -> bool:
    """Returns True if stdout is an interactive terminal supporting ANSI escape codes."""
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def format_ansi_velocity(percent: float, text: str) -> str:
    """Formats text with an ANSI color gradient if interactive TTY, else plain text."""
    if not _is_interactive_tty():
        return text
    if percent >= 100.0:
        return f"\033[1;32m{text}\033[0m"  # Bold green
    if percent >= 75.0:
        return f"\033[32m{text}\033[0m"    # Green
    if percent >= 50.0:
        return f"\033[33m{text}\033[0m"    # Yellow
    if percent >= 25.0:
        return f"\033[38;5;208m{text}\033[0m"  # Orange
    return f"\033[31m{text}\033[0m"        # Red


def analyze_manuscript_words(
    target_dir: Path | str,
    draft_name: str | None = None,
    scope: EngineScope | None = None,
) -> dict[str, Any]:
    """Analyzes a manuscript directory for chapter word counts, POV breakdown, and dialogue ratios."""
    ms_path = resolve_manuscript_path(target_dir) or Path(target_dir).resolve()
    if not ms_path.is_dir():
        raise FileNotFoundError(f"Manuscript directory not found: {target_dir}")

    # Read manifest if present
    manifest_file = ms_path / "manuscript.yaml"
    target_words = 80000
    ms_title = ms_path.name.replace("_", " ")
    author = "Author"
    active_draft = draft_name

    if manifest_file.is_file():
        try:
            m_data = parse_yaml_document(manifest_file.read_text(encoding="utf-8", errors="replace"))
            if isinstance(m_data, dict):
                target_words = int(m_data.get("target_words", 80000))
                ms_title = str(m_data.get("title", ms_title))
                author = str(m_data.get("author", author))
                if not active_draft:
                    active_draft = m_data.get("active_draft")
        except Exception:
            pass

    # Gather chapter files
    chapter_items, _, _ = filter_manuscript_scope(ms_path, scope=scope)
    chapters: list[dict[str, Any]] = []
    total_words = 0
    total_cjk = 0
    total_dialogue_words = 0
    pov_words: dict[str, int] = {}
    volume_words: dict[str, int] = {}

    for item in chapter_items:
        fpath = item.path
        try:
            content = fpath.read_text(encoding="utf-8", errors="replace")
            fm, body = extract_frontmatter_and_body(content)
            tok_res = count_prose_words_advanced(body)
            w_count = tok_res["total_words"]
            cjk_count = tok_res["cjk_characters"]
            dial_words = tok_res["dialogue_words"]
            dial_pct = tok_res["dialogue_percentage"]
        except Exception:
            fm = {}
            w_count = 0
            cjk_count = 0
            dial_words = 0
            dial_pct = 0.0

        title = fm.get("title") or fpath.stem.replace("_", " ")
        pov = fm.get("pov") or "Unassigned"
        vol = item.volume_name or "Volume-1"

        total_words += w_count
        total_cjk += cjk_count
        total_dialogue_words += dial_words
        pov_words[pov] = pov_words.get(pov, 0) + w_count
        volume_words[vol] = volume_words.get(vol, 0) + w_count

        chapters.append({
            "index": item.index,
            "filename": fpath.name,
            "title": str(title),
            "pov": str(pov),
            "volume": vol,
            "words": w_count,
            "cjk_characters": cjk_count,
            "dialogue_words": dial_words,
            "dialogue_percentage": dial_pct,
            "estimated_pages": max(1, math.ceil(w_count / 250)) if w_count > 0 else 0,
            "reading_time_min": round(w_count / 225, 1),
            "path": str(fpath),
        })

    percent = (total_words / target_words * 100.0) if target_words > 0 else 0.0
    overall_dialogue_pct = round((total_dialogue_words / max(1, total_words)) * 100.0, 1)

    return {
        "status": "success",
        "title": ms_title,
        "author": author,
        "path": str(ms_path),
        "total_words": total_words,
        "total_cjk_characters": total_cjk,
        "total_dialogue_words": total_dialogue_words,
        "dialogue_percentage": overall_dialogue_pct,
        "target_words": target_words,
        "percent_complete": round(percent, 1),
        "estimated_pages": math.ceil(total_words / 250),
        "reading_time_minutes": round(total_words / 225, 1),
        "audiobook_hours": round(total_words / 9000, 1),
        "chapter_count": len(chapters),
        "chapters": chapters,
        "pov_distribution": pov_words,
        "volume_distribution": volume_words,
    }


def format_words_table(data: dict[str, Any], show_pov: bool = False, show_dialogue: bool = False) -> str:
    """Formats word count telemetry into a human-readable terminal report."""
    lines = []
    title = data.get("title", "Manuscript")
    total = data.get("total_words", 0)
    target = data.get("target_words", 80000)
    pct = data.get("percent_complete", 0.0)
    pages = data.get("estimated_pages", 0)
    read_min = data.get("reading_time_minutes", 0.0)
    audio_hrs = data.get("audiobook_hours", 0.0)
    dial_pct = data.get("dialogue_percentage", 0.0)
    chap_count = data.get("chapter_count", 0)

    prog_str = f"{pct:.1f}%"
    colored_prog = format_ansi_velocity(pct, prog_str)

    lines.append(f"📖  {title} — Manuscript Word Count & Telemetry")
    lines.append("═" * 78)
    lines.append(f"  Total Words:      {total:,} / {target:,} words ({colored_prog})")
    lines.append(f"  Estimated Pages:  {pages:,} pages (at 250 words/page)")
    lines.append(f"  Reading Time:     ~{read_min:.0f} min (Audiobook: ~{audio_hrs:.1f} hrs)")
    lines.append(f"  Dialogue Ratio:   {dial_pct:.1f}% dialogue ({100.0 - dial_pct:.1f}% narrative)")
    lines.append(f"  Chapters Count:   {chap_count} chapters")
    lines.append("─" * 78)
    lines.append(f"{'#':<4} {'Chapter Title':<30} {'POV':<14} {'Words':>8} {'Dialogue':>10}")
    lines.append("─" * 78)

    for ch in data.get("chapters", []):
        t = ch["title"][:28] + ".." if len(ch["title"]) > 28 else ch["title"]
        p = ch["pov"][:12] + ".." if len(ch["pov"]) > 12 else ch["pov"]
        d_str = f"{ch.get('dialogue_percentage', 0.0):.1f}%"
        lines.append(f"{ch['index']:<4} {t:<30} {p:<14} {ch['words']:>8,} {d_str:>10}")

    lines.append("═" * 78)

    if show_pov or len(data.get("pov_distribution", {})) > 1:
        lines.append("\n🎭  POV Distribution Breakdown:")
        for pov, w in sorted(data.get("pov_distribution", {}).items(), key=lambda x: x[1], reverse=True):
            pov_pct = (w / total * 100.0) if total > 0 else 0.0
            lines.append(f"  • {pov:<20} {w:>8,} words ({pov_pct:5.1f}%)")

    return "\n".join(lines)


def format_words_markdown(data: dict[str, Any]) -> str:
    """Formats word count telemetry as standard GitHub Markdown."""
    lines = []
    lines.append(f"# {data.get('title', 'Manuscript')} — Word Count Analytics\n")
    lines.append(f"- **Total Words**: {data.get('total_words', 0):,} / {data.get('target_words', 80000):,} ({data.get('percent_complete', 0.0)}%)")
    lines.append(f"- **Estimated Pages**: {data.get('estimated_pages', 0):,} pages")
    lines.append(f"- **Reading Time**: ~{data.get('reading_time_minutes', 0.0):.0f} min (Audiobook: ~{data.get('audiobook_hours', 0.0):.1f} hours)")
    lines.append(f"- **Dialogue Ratio**: {data.get('dialogue_percentage', 0.0)}% dialogue\n")
    lines.append("| Index | Title | POV | Words | Dialogue % | Reading Time |")
    lines.append("| :--- | :--- | :--- | ---: | ---: | ---: |")
    for ch in data.get("chapters", []):
        lines.append(f"| {ch['index']} | {ch['title']} | {ch['pov']} | {ch['words']:,} | {ch.get('dialogue_percentage', 0.0):.1f}% | ~{ch.get('reading_time_min', 0.0):.1f}m |")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ars Arcanum Unicode Prose Word Count Engine")
    parser.add_argument("manuscript", nargs="?", default=".", help="Manuscript name or directory")
    parser.add_argument("--json", "-j", action="store_true", help="Output machine-readable JSON")
    parser.add_argument("--md", "--markdown", action="store_true", help="Output GitHub Markdown")
    parser.add_argument("--html", help="Generate standalone offline HTML5 Velocity Studio to specified output path")
    parser.add_argument("--pov", action="store_true", help="Display detailed POV distribution")
    parser.add_argument("--dialogue", action="store_true", help="Display detailed dialogue vs narrative analysis")
    parser.add_argument("--draft", "-d", help="Explicit draft name (e.g. Draft-02)")

    args = parser.parse_args(argv)

    try:
        data = analyze_manuscript_words(args.manuscript, draft_name=args.draft)

        if args.html:
            if render_velocity_html:
                vel_data = get_velocity_metrics(args.manuscript) if get_velocity_metrics else None
                render_velocity_html(data, vel_data, args.html)
                print(f"✓ Standalone Velocity Studio written to: {args.html}")
                return 0
            print("Error: HTML template engine not available.", file=sys.stderr)
            return 1

        if args.json:
            print(json.dumps(data, indent=2))
        elif args.md:
            print(format_words_markdown(data))
        else:
            print(format_words_table(data, show_pov=args.pov, show_dialogue=args.dialogue))
        return 0
    except Exception as e:
        if args.json:
            print(json.dumps({"status": "error", "error": str(e)}, indent=2))
        else:
            print(f"Error: {e}", file=sys.stderr)
        return 1


__all__ = [
    "analyze_manuscript_words",
    "count_prose_words_advanced",
    "format_ansi_velocity",
    "format_words_markdown",
    "format_words_table",
    "main",
]

if __name__ == "__main__":
    sys.exit(main())
