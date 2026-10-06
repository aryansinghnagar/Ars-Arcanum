#!/usr/bin/env python3
"""
Ars Arcanum Smart Typography Normalizer & Polish Engine
(scripts/lib/typography_cleaner.py)
================================================================================
Zero-dependency, offline typography cleaner and smart punctuation formatter with
interactive review and consent-based change approval.

Capabilities (PRO-104):
1. Smart Typographic Quotes:
   - Converts straight double quotes ("...") to curly open/close pairs (“...”)
   - Converts straight single quotes ('...') to curly open/close pairs (‘...’)
   - Preserves apostrophes in contractions (don't, it's, 'tis, '90s)
2. Em-Dash & En-Dash Normalization:
   - Converts triple/double dashes (`---`, `--`) to typographic em-dash (`—`)
   - Converts numeric date/range hyphens (`1914-1918`, `pp. 20-25`) to en-dash (`–`)
3. Ellipsis Normalization:
   - Converts three dots (`...` or `. . .`) to unicode ellipsis (`…`)
4. Whitespace & Scene Break Cleanliness:
   - Removes trailing whitespace from line ends
   - Collapses multiple redundant spaces inside sentences
   - Standardizes ornamental scene break indicators
5. Interactive Review & Consent Control:
   - Marks proposed changes with exact line numbers and rule descriptions
   - Interactive prompt allowing user to accept [y], reject [n], or accept all [a]
   - Explicit consent flag (-y / --yes / --auto-accept) for batch acceptance
   - Dry-run diffing, backup creation, and directory batch processing.

Zero external dependencies; 100% offline privacy.
"""

from __future__ import annotations

import argparse
import difflib
import json
import logging
import re
import sys
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

try:
    from lib._bootstrap import atomic_write
    from lib.scope import (
        EngineScope,
        add_scope_arguments,
        filter_manuscript_scope,
        parse_scope_args,
        resolve_manuscript_dir,
    )
except ImportError:
    from _bootstrap import atomic_write
    from scope import (  # type: ignore[no-redef]
        EngineScope,
        add_scope_arguments,
        filter_manuscript_scope,
        parse_scope_args,
        resolve_manuscript_dir,
    )


logger = logging.getLogger("arcanum.typography")


@dataclass
class TypographyProposal:
    """Represents a specific proposed typographical edit."""

    line_number: int
    rule: str
    original: str
    replacement: str
    description: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def normalize_typography_line(line: str, in_frontmatter: bool, in_codeblock: bool) -> tuple[str, dict[str, int], list[dict[str, Any]], bool, bool]:
    """Normalizes a single line of text and returns (new_line, stats, proposals, new_in_fm, new_in_cb)."""
    stats: dict[str, int] = {
        "curly_double_quotes": 0,
        "curly_single_quotes": 0,
        "em_dashes": 0,
        "en_dashes": 0,
        "ellipses": 0,
        "trailing_spaces_removed": 0,
        "multi_spaces_collapsed": 0,
    }
    proposals: list[dict[str, Any]] = []

    newline_char = "\r\n" if line.endswith("\r\n") else "\n" if line.endswith("\n") else ""
    raw_without_nl = line[:-len(newline_char)] if newline_char else line

    # 1. Trailing whitespace
    clean_end = raw_without_nl.rstrip(" \t")
    if len(clean_end) < len(raw_without_nl):
        stats["trailing_spaces_removed"] += 1
        proposals.append({
            "rule": "trailing_whitespace",
            "desc": "Remove trailing whitespace",
            "from": raw_without_nl,
            "to": clean_end,
        })
    cur_line = clean_end

    # Handle frontmatter block (--- ... ---)
    if cur_line.startswith("---"):
        if in_frontmatter:
            return cur_line + newline_char, stats, proposals, False, in_codeblock
        return cur_line + newline_char, stats, proposals, True, in_codeblock

    if in_frontmatter:
        return cur_line + newline_char, stats, proposals, True, in_codeblock

    # Handle fenced codeblocks (``` ... ```)
    if cur_line.startswith("```"):
        return cur_line + newline_char, stats, proposals, in_frontmatter, not in_codeblock

    if in_codeblock or cur_line.startswith("    "):
        return cur_line + newline_char, stats, proposals, in_frontmatter, True

    # Guard markdown horizontal rules / thematic scene breaks
    stripped = cur_line.strip()
    if stripped in ("---", "***", "* * *", "- - -", "___", "_ _ _"):
        return cur_line + newline_char, stats, proposals, in_frontmatter, in_codeblock

    # 2. Ellipses: ... or . . . -> …
    ellipsis_count = len(re.findall(r"\.\s*\.\s*\.", cur_line))
    if ellipsis_count > 0:
        cur_line = re.sub(r"\.\s*\.\s*\.", "…", cur_line)
        stats["ellipses"] += ellipsis_count
        proposals.append({
            "rule": "ellipsis",
            "desc": "Convert three dots to unicode ellipsis (…)",
            "count": ellipsis_count,
        })

    # 3. En-dash for numeric ranges (e.g., 1914-1918, pp. 20-35)
    cur_line, en_c = re.subn(r"(?<=\d)\s*(?:--|-)\s*(?=\d)", "–", cur_line)
    if en_c > 0:
        stats["en_dashes"] += en_c
        proposals.append({
            "rule": "en_dash",
            "desc": "Convert numeric range hyphen to en-dash (–)",
            "count": en_c,
        })

    # 4. Em-dashes: --- or -- -> —
    cur_line, em_c = re.subn(r"\s*---\s*|\s*--\s*", "—", cur_line)
    if em_c > 0:
        stats["em_dashes"] += em_c
        proposals.append({
            "rule": "em_dash",
            "desc": "Convert double/triple dashes to typographic em-dash (—)",
            "count": em_c,
        })

    # 5. Smart Double Quotes: " -> “ / ”
    def replace_double_quotes(s: str) -> tuple[str, int]:
        s, c1 = re.subn(r'(^|[\s\(\[\{—–])"', r"\1“", s)
        s, c2 = re.subn(r'([^\s])"', r"\1”", s)
        s, c3 = re.subn(r'"', r"”", s)
        return s, c1 + c2 + c3

    cur_line, d_count = replace_double_quotes(cur_line)
    if d_count > 0:
        stats["curly_double_quotes"] += d_count
        proposals.append({
            "rule": "curly_double_quotes",
            "desc": "Convert straight double quotes to smart curly quotes (“ ”)",
            "count": d_count,
        })

    # 6. Smart Single Quotes & Apostrophes: ' -> ‘ / ’
    cur_line = re.sub(r"\b'([0-9]{2}s?)\b", r"’\1", cur_line)
    cur_line = re.sub(r"(^|\s)'(tis|twas|cause|em|round|bout)\b", r"\1’\2", cur_line, flags=re.IGNORECASE)

    # Contraction / possessive apostrophes
    cur_line, a_count = re.subn(r"([A-Za-z0-9])'([A-Za-z0-9])", r"\1’\2", cur_line)

    # Single quote pairs
    cur_line, s1 = re.subn(r"(^|[\s\(\[\{—–])\'", r"\1‘", cur_line)
    cur_line, s2 = re.subn(r"([^\s])\'", r"\1’", cur_line)
    cur_line, s3 = re.subn(r"\'", r"’", cur_line)
    s_total = a_count + s1 + s2 + s3
    if s_total > 0:
        stats["curly_single_quotes"] += s_total
        proposals.append({
            "rule": "curly_single_quotes",
            "desc": "Convert straight single quotes/apostrophes to typographic curls (‘ ’)",
            "count": s_total,
        })

    # 7. Redundant internal spaces
    leading_indent = len(cur_line) - len(cur_line.lstrip(" "))
    indent_str = cur_line[:leading_indent]
    body_str = cur_line[leading_indent:]
    collapsed_body, sp_count = re.subn(r"[ ]{2,}", " ", body_str)
    if sp_count > 0:
        stats["multi_spaces_collapsed"] += sp_count
        proposals.append({
            "rule": "multi_spaces",
            "desc": "Collapse redundant internal whitespace",
            "count": sp_count,
        })
    cur_line = indent_str + collapsed_body

    return cur_line + newline_char, stats, proposals, in_frontmatter, in_codeblock


def normalize_typography_text(text: str) -> tuple[str, dict[str, int]]:
    """Normalizes straight punctuation into clean literary typography."""
    stats: dict[str, int] = {
        "curly_double_quotes": 0,
        "curly_single_quotes": 0,
        "em_dashes": 0,
        "en_dashes": 0,
        "ellipses": 0,
        "trailing_spaces_removed": 0,
        "multi_spaces_collapsed": 0,
    }

    lines = text.splitlines(keepends=True)
    new_lines = []
    in_frontmatter = False
    in_codeblock = False

    for idx, line in enumerate(lines):
        if idx == 0 and line.startswith("---"):
            in_frontmatter = True
            new_lines.append(line)
            continue

        new_l, l_stats, _props, in_frontmatter, in_codeblock = normalize_typography_line(
            line, in_frontmatter=in_frontmatter, in_codeblock=in_codeblock
        )
        for k in stats:
            stats[k] += l_stats[k]
        new_lines.append(new_l)

    return "".join(new_lines), stats


def inspect_typography_proposals(text: str) -> list[TypographyProposal]:
    """Returns a structured list of individual typographical improvement proposals."""
    proposals: list[TypographyProposal] = []
    lines = text.splitlines(keepends=True)
    in_frontmatter = False
    in_codeblock = False

    for idx, line in enumerate(lines, start=1):
        if idx == 1 and line.startswith("---"):
            in_frontmatter = True
            continue

        raw_orig = line.rstrip("\r\n")
        new_l, _stats, props, in_frontmatter, in_codeblock = normalize_typography_line(
            line, in_frontmatter=in_frontmatter, in_codeblock=in_codeblock
        )
        raw_new = new_l.rstrip("\r\n")

        if raw_orig != raw_new:
            rule_names = [p["rule"] for p in props]
            desc = "; ".join(p["desc"] for p in props)
            proposals.append(
                TypographyProposal(
                    line_number=idx,
                    rule=",".join(rule_names),
                    original=raw_orig,
                    replacement=raw_new,
                    description=desc,
                )
            )

    return proposals


def clean_file(
    file_path: Path,
    in_place: bool = False,
    make_backup: bool = True,
    interactive: bool = False,
    auto_accept: bool = False,
    prompt_fn: Callable[[str], str] | None = None,
) -> tuple[dict[str, Any], str]:
    """Cleans a single file and returns stats and diff, with interactive acceptance support."""
    content = file_path.read_text(encoding="utf-8", errors="replace")
    cleaned, stats = normalize_typography_text(content)

    diff = ""
    if content != cleaned:
        diff_lines = list(
            difflib.unified_diff(
                content.splitlines(),
                cleaned.splitlines(),
                fromfile=str(file_path),
                tofile=str(file_path) + " (polished)",
                lineterm="",
            )
        )
        diff = "\n".join(diff_lines)

        should_write = False
        if in_place:
            if auto_accept or not interactive:
                should_write = True
            elif interactive:
                # Interactive proposal review
                proposals = inspect_typography_proposals(content)
                print(f"\n📄 Reviewing typography for: {file_path.name} ({len(proposals)} proposed changes)")
                for p in proposals:
                    print(f"  Line {p.line_number} [{p.rule}]: {p.description}")
                    print(f"    - {p.original}")
                    print(f"    + {p.replacement}")

                ask = prompt_fn if prompt_fn else input
                try:
                    resp = ask(f"Apply {len(proposals)} typography changes to '{file_path.name}'? [y/N/a(all)/q(quit)]: ").strip().lower()
                    if resp in ("y", "yes", "a", "all"):
                        should_write = True
                    elif resp in ("q", "quit"):
                        print("Review aborted by user.")
                        return stats, diff
                except (EOFError, KeyboardInterrupt):
                    print("\nReview cancelled.")
                    return stats, diff

            if should_write:
                if make_backup:
                    bak_path = file_path.with_suffix(file_path.suffix + ".bak")
                    atomic_write(bak_path, content)
                atomic_write(file_path, cleaned)

    return stats, diff


def clean_target(
    target_path: Path | str | None = None,
    in_place: bool = False,
    make_backup: bool = True,
    interactive: bool = False,
    auto_accept: bool = False,
    scope: Any = None,
    prompt_fn: Callable[[str], str] | None = None,
) -> dict[str, Any]:
    """Cleans a single file or an entire manuscript tree with granular scope and interactive review support."""
    target_str = resolve_manuscript_dir(target_path) if target_path else resolve_manuscript_dir()
    if target_path and Path(target_path).exists():
        p_target = Path(target_path)
    elif target_str and Path(target_str).exists():
        p_target = Path(target_str)
    else:
        p_target = Path(target_path) if target_path else Path.cwd()

    files = []
    if p_target.is_file():
        files.append(p_target)
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
            if scoped_chaps:
                files = [c.file_path for c in scoped_chaps]
            elif scoped_scenes:
                seen_f = set()
                for s in scoped_scenes:
                    if s.chapter_file not in seen_f:
                        seen_f.add(s.chapter_file)
                        files.append(s.chapter_file)
        else:
            for p in sorted(p_target.rglob("*.md")):
                if not p.name.startswith((".", "_")) and "Backups" not in p.parts:
                    files.append(p)
    else:
        raise FileNotFoundError(f"Target path not found: {p_target}")

    total_stats: dict[str, Any] = {
        "files_scanned": len(files),
        "files_modified": 0,
        "curly_double_quotes": 0,
        "curly_single_quotes": 0,
        "em_dashes": 0,
        "en_dashes": 0,
        "ellipses": 0,
        "trailing_spaces_removed": 0,
        "multi_spaces_collapsed": 0,
    }
    file_results = []
    global_auto = auto_accept

    for f in files:
        f_stats, diff = clean_file(
            f,
            in_place=in_place,
            make_backup=make_backup,
            interactive=interactive and not global_auto,
            auto_accept=global_auto,
            prompt_fn=prompt_fn,
        )
        is_mod = bool(diff)
        if is_mod:
            total_stats["files_modified"] += 1

        for k in f_stats:
            if k in total_stats:
                total_stats[k] += f_stats[k]

        proposals = inspect_typography_proposals(f.read_text(encoding="utf-8", errors="replace")) if is_mod else []
        file_results.append({
            "file": str(f),
            "modified": is_mod,
            "stats": f_stats,
            "proposals": [p.to_dict() for p in proposals],
            "diff": diff,
        })

    return {
        "target": str(p_target),
        "in_place": in_place,
        "interactive": interactive,
        "auto_accepted": auto_accept,
        "summary": total_stats,
        "files": file_results,
    }


def clean_directory(
    dir_path: Path,
    in_place: bool = False,
    make_backup: bool = True,
    interactive: bool = False,
    auto_accept: bool = False,
    scope: Any = None,
) -> dict[str, Any]:
    """Batch cleans all markdown files in a directory."""
    return clean_target(
        dir_path,
        in_place=in_place,
        make_backup=make_backup,
        interactive=interactive,
        auto_accept=auto_accept,
        scope=scope,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ars Arcanum Smart Typography Normalizer & Interactive Polish (PRO-104)")
    parser.add_argument("target", nargs="?", default=None, help="File or manuscript directory to polish")
    parser.add_argument("-i", "--in-place", action="store_true", help="Modify files in-place on disk")
    parser.add_argument("-y", "--yes", "--auto", "--auto-accept", dest="auto_accept", action="store_true", help="Automatically accept and apply all proposed typography changes with explicit user consent")
    parser.add_argument("--interactive", action="store_true", help="Interactively review and accept/reject proposed changes per file")
    parser.add_argument("--proposals", action="store_true", help="List detailed line-by-line proposals without modifying files")
    parser.add_argument("--no-backup", action="store_true", help="Do not create .bak backup files when modifying in-place")
    parser.add_argument("--diff", action="store_true", help="Show unified diff of changes")
    parser.add_argument("--json", action="store_true", help="Output JSON results")
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
                print(f"Error: Target does not exist: {target_raw}", file=sys.stderr)
                sys.exit(1)

    in_place = args.in_place or args.auto_accept
    interactive = args.interactive and not args.auto_accept

    result = clean_target(
        target_path,
        in_place=in_place,
        make_backup=not args.no_backup,
        interactive=interactive,
        auto_accept=args.auto_accept,
        scope=scope,
    )

    if args.json:
        print(json.dumps(result, indent=2))
        return 0

    summary = result["summary"]
    print(f"=== Smart Typography Polish & Review: {target_path.name} ===")
    if args.auto_accept:
        mode_str = "[AUTO-ACCEPTED WITH USER CONSENT]"
    elif in_place:
        mode_str = "[IN-PLACE WRITTEN]"
    elif interactive:
        mode_str = "[INTERACTIVE REVIEW]"
    else:
        mode_str = "[DRY-RUN / PROPOSALS MARKED ONLY]"
    print(f"Mode: {mode_str}")
    print(f"Files Scanned: {summary['files_scanned']} | Candidate Files: {summary['files_modified']}")
    print("-" * 65)
    print(f"  Curly Double Quotes (“ ”): {summary['curly_double_quotes']}")
    print(f"  Curly Single Quotes (‘ ’): {summary['curly_single_quotes']}")
    print(f"  Em-Dashes (—):            {summary['em_dashes']}")
    print(f"  En-Dashes (–):            {summary['en_dashes']}")
    print(f"  Ellipses (…):             {summary['ellipses']}")
    print(f"  Trailing Spaces Removed:  {summary['trailing_spaces_removed']}")
    print(f"  Spaces Collapsed:         {summary['multi_spaces_collapsed']}")

    if args.proposals:
        print("\n=== Detailed Typography Proposals ===")
        for f in result["files"]:
            if f["proposals"]:
                print(f"\n📄 {Path(f['file']).name} ({len(f['proposals'])} proposals):")
                for p in f["proposals"]:
                    print(f"  • Line {p['line_number']} [{p['rule']}]: {p['description']}")
                    print(f"    Original:    {p['original']}")
                    print(f"    Replacement: {p['replacement']}")

    if args.diff and not args.proposals:
        diff_count = 0
        for f in result["files"]:
            if f["modified"] and f["diff"]:
                diff_count += 1
                if diff_count <= 5 or args.diff:
                    print(f"\n--- Diff: {Path(f['file']).name} ---")
                    print(f["diff"][:1000] + ("\n... [truncated]" if len(f["diff"]) > 1000 else ""))

    if not in_place and summary["files_modified"] > 0:
        print("\n💡 Tip: To apply these changes interactively, run with: arcanum polish typography --interactive")
        print("💡 Tip: To auto-accept all changes with consent, run with: arcanum polish typography --yes (or -y)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
