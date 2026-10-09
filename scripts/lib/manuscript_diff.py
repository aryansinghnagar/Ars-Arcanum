#!/usr/bin/env python3
"""
Ars Arcanum Manuscript Comparison & Redline Diff Engine (scripts/lib/manuscript_diff.py)
======================================================================================
Provides word-level and chapter-level comparison between manuscript drafts.
Generates:
  1. Accessible, beautiful HTML Redline changelog with chapter navigation,
     word delta metrics, light/dark mode, and inline/side-by-side views.
  2. ANSI colorized terminal diff with summary metrics.
  3. Machine-readable JSON change metrics.
  4. Bridge to LibreOffice Writer Track Changes comparison.

100% offline, privacy-respecting, zero-telemetry, and accessible.
"""

import argparse
import difflib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    from lib._bootstrap import atomic_write
    from lib.manuscript_diff_template import render_manuscript_diff_html
    from lib.scope import (
        EngineScope,
        add_scope_arguments,
        filter_manuscript_scope,
        parse_scope_args,
    )
except ImportError:
    from _bootstrap import atomic_write
    from manuscript_diff_template import (  # type: ignore[no-redef]
        render_manuscript_diff_html,
    )
    from scope import (  # type: ignore[no-redef]
        EngineScope,
        add_scope_arguments,
        filter_manuscript_scope,
        parse_scope_args,
    )


NW_TAG_REGEX = re.compile(r"^@[A-Za-z0-9_-]+:")
TOKEN_REGEX = re.compile(r"\S+|\s+")
WORD_REGEX = re.compile(r"\b\w+\b", re.UNICODE)
STEM_CLEAN_REGEX = re.compile(r"^\d+_")
_FM = re.compile(r"^---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)", re.DOTALL)
_CODEBLOCK_REGEX = re.compile(r"```.*?```", re.DOTALL)

try:
    from lib._bootstrap import count_prose_words as count_words
except ImportError:
    from _bootstrap import count_prose_words as count_words


def strip_nw_metadata(text: str) -> str:
    """Removes novelWriter metadata tags (@pov:, @status:) and comments (%) for comparison."""
    lines = text.splitlines()
    filtered = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("@") and NW_TAG_REGEX.match(stripped):
            continue
        if stripped.startswith("%"):
            continue
        filtered.append(line)
    return "\n".join(filtered)


def tokenize_words(text: str) -> list[str]:
    """Splits text into words, whitespace, and punctuation tokens preserving full structure."""
    return TOKEN_REGEX.findall(text)


def compute_word_diff(tokens_a: list[str], tokens_b: list[str]) -> tuple[list[dict[str, Any]], int, int]:
    """
    Computes word-level diff using difflib.SequenceMatcher.
    Returns:
      (diff_chunks, added_word_count, deleted_word_count)
    Each chunk: {'tag': 'equal'|'insert'|'delete'|'replace', 'text_a': str, 'text_b': str}
    """
    matcher = difflib.SequenceMatcher(None, tokens_a, tokens_b)
    chunks = []
    added_words = 0
    deleted_words = 0

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        sub_a = "".join(tokens_a[i1:i2])
        sub_b = "".join(tokens_b[j1:j2])

        if tag == "insert":
            words = len(WORD_REGEX.findall(sub_b))
            added_words += words
            chunks.append({"tag": "insert", "text": sub_b})
        elif tag == "delete":
            words = len(WORD_REGEX.findall(sub_a))
            deleted_words += words
            chunks.append({"tag": "delete", "text": sub_a})
        elif tag == "replace":
            w_a = len(WORD_REGEX.findall(sub_a))
            w_b = len(WORD_REGEX.findall(sub_b))
            deleted_words += w_a
            added_words += w_b
            chunks.append({"tag": "delete", "text": sub_a})
            chunks.append({"tag": "insert", "text": sub_b})
        elif tag == "equal":
            chunks.append({"tag": "equal", "text": sub_b})

    return chunks, added_words, deleted_words


def discover_draft_files(draft_dir: Path) -> list[Path]:
    """Finds and sorts all markdown files in a draft directory."""
    if not draft_dir.is_dir():
        return []
    md_files = []
    for p in sorted(draft_dir.rglob("*.md")):
        # Skip outlines, backups, exports, or hidden files
        rel_parts = p.relative_to(draft_dir).parts
        if any(part in ("Outlines", "Exports", "Backups", "05-Backups", "04-Publishing") or part.startswith(".") for part in rel_parts):
            continue
        # If draft_dir is a parent folder containing other Draft-* subdirectories, skip files inside nested Draft-* subdirectories
        if len(rel_parts) > 1 and any(part.startswith("Draft-") for part in rel_parts[:-1]):
            continue
        md_files.append(p)
    return sorted(md_files)


def extract_chapter_title(file_path: Path, content: str) -> str:
    """Extracts chapter title from first markdown heading or filename."""
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
        if line.startswith("## "):
            return line[3:].strip()
    # Fallback to readable filename
    stem = file_path.stem
    clean = STEM_CLEAN_REGEX.sub("", stem).replace("_", " ").replace("-", " ")
    return clean.title()


class ManuscriptComparator:
    def __init__(self, path_a: Path, path_b: Path, label_a: str = "Draft 1", label_b: str = "Draft 2", scope: Any = None):
        self.path_a = path_a
        self.path_b = path_b
        self.label_a = label_a
        self.label_b = label_b
        self.scope = scope
        self.chapters: list[dict[str, Any]] = []
        self.summary: dict[str, Any] = {}

    def compare(self) -> dict[str, Any]:
        """Performs full comparison across all chapters/files."""
        if self.path_a.is_file() and self.path_b.is_file():
            self._compare_single_files(self.path_a, self.path_b)
        else:
            self._compare_directories(self.path_a, self.path_b)

        total_a = sum(c["words_a"] for c in self.chapters)
        total_b = sum(c["words_b"] for c in self.chapters)
        added = sum(c["added_words"] for c in self.chapters)
        deleted = sum(c["deleted_words"] for c in self.chapters)
        net_change = total_b - total_a

        # Overall similarity
        if total_a + total_b > 0:
            sim_sum = sum(c["similarity"] * (c["words_a"] + c["words_b"]) for c in self.chapters)
            overall_sim = round(sim_sum / (total_a + total_b), 4)
        else:
            overall_sim = 1.0

        self.summary = {
            "label_a": self.label_a,
            "label_b": self.label_b,
            "path_a": str(self.path_a),
            "path_b": str(self.path_b),
            "total_words_a": total_a,
            "total_words_b": total_b,
            "added_words": added,
            "deleted_words": deleted,
            "net_change": net_change,
            "similarity_ratio": overall_sim,
            "chapter_count": len(self.chapters),
            "chapters": self.chapters
        }
        return self.summary

    def _compare_single_files(self, file_a: Path, file_b: Path):
        content_a = file_a.read_text(encoding="utf-8", errors="replace") if file_a.is_file() else ""
        content_b = file_b.read_text(encoding="utf-8", errors="replace") if file_b.is_file() else ""

        title = extract_chapter_title(file_b if file_b.is_file() else file_a, content_b or content_a)
        chap_data = self._diff_prose(content_a, content_b, title, file_b.name)
        self.chapters.append(chap_data)

    def _compare_directories(self, dir_a: Path, dir_b: Path):
        if self.scope:
            scope = self.scope
            if not isinstance(scope, EngineScope):
                if isinstance(scope, dict):
                    from lib.scope import resolve_scope
                    scope = resolve_scope(scope).scope_filter
                elif isinstance(scope, str):
                    from lib.scope import parse_unified_scope_string
                    p_dict = parse_unified_scope_string(scope)
                    scope = EngineScope(**p_dict)
            chaps_a, _, _ = filter_manuscript_scope(dir_a, scope)
            chaps_b, _, _ = filter_manuscript_scope(dir_b, scope)
            files_a = {c.file_path.relative_to(dir_a): c.file_path for c in chaps_a}
            files_b = {c.file_path.relative_to(dir_b): c.file_path for c in chaps_b}
        else:
            files_a = {p.relative_to(dir_a): p for p in discover_draft_files(dir_a)}
            files_b = {p.relative_to(dir_b): p for p in discover_draft_files(dir_b)}

        all_rel_paths = sorted(set(files_a.keys()).union(set(files_b.keys())))

        for rel_path in all_rel_paths:
            file_a = files_a.get(rel_path)
            file_b = files_b.get(rel_path)

            content_a = file_a.read_text(encoding="utf-8", errors="replace") if file_a else ""
            content_b = file_b.read_text(encoding="utf-8", errors="replace") if file_b else ""

            target_file = file_b or file_a
            if target_file is not None:
                title = extract_chapter_title(target_file, content_b or content_a)
                chap_data = self._diff_prose(content_a, content_b, title, str(rel_path))
                self.chapters.append(chap_data)

    def _diff_prose(self, raw_a: str, raw_b: str, title: str, rel_path: str) -> dict[str, Any]:
        clean_a = strip_nw_metadata(raw_a)
        clean_b = strip_nw_metadata(raw_b)

        words_a = count_words(clean_a)
        words_b = count_words(clean_b)

        tokens_a = tokenize_words(clean_a)
        tokens_b = tokenize_words(clean_b)

        chunks, added, deleted = compute_word_diff(tokens_a, tokens_b)

        matcher = difflib.SequenceMatcher(None, tokens_a, tokens_b)
        sim = round(matcher.ratio(), 4)

        return {
            "title": title,
            "rel_path": rel_path,
            "words_a": words_a,
            "words_b": words_b,
            "added_words": added,
            "deleted_words": deleted,
            "net_change": words_b - words_a,
            "similarity": sim,
            "chunks": chunks,
            "raw_a": clean_a,
            "raw_b": clean_b
        }

    def to_json(self, indent: int = 2) -> str:
        """Returns JSON representation without huge raw chunk bloat unless requested."""
        if not self.summary:
            self.compare()
        # Create serializable view
        export_data = dict(self.summary)
        export_data["chapters"] = [
            {k: v for k, v in c.items() if k not in ("chunks", "raw_a", "raw_b")}
            for c in self.chapters
        ]
        return json.dumps(export_data, indent=indent, ensure_ascii=False)

    def to_terminal_ansi(self) -> str:
        """Generates rich ANSI colored diff output for terminal."""
        if not self.summary:
            self.compare()

        RED = "\033[38;2;220;53;69m\033[9m"  # Soft red + strikethrough
        GREEN = "\033[38;2;40;167;69m\033[4m"  # Soft green + underline
        CYAN = "\033[1;36m"
        BOLD = "\033[1m"
        RESET = "\033[0m"
        DIM = "\033[2m"

        out = []
        out.append(f"\n{BOLD}{CYAN}=== Ars Arcanum Manuscript Revision Comparison ==={RESET}")
        out.append(f"{DIM}Base  Draft (A):{RESET} {self.label_a} ({self.summary['total_words_a']:,} words)")
        out.append(f"{DIM}Prior Draft (B):{RESET} {self.label_b} ({self.summary['total_words_b']:,} words)")
        net = self.summary['net_change']
        net_str = f"+{net:,}" if net >= 0 else f"{net:,}"
        out.append(f"{DIM}Delta Stats:{RESET} {GREEN}+{self.summary['added_words']:,} added{RESET} | {RED}-{self.summary['deleted_words']:,} deleted{RESET} | Net: {BOLD}{net_str}{RESET} | Similarity: {self.summary['similarity_ratio']*100:.1f}%\n")

        for chap in self.chapters:
            c_net = chap['net_change']
            c_net_str = f"+{c_net:,}" if c_net >= 0 else f"{c_net:,}"
            out.append(f"{CYAN}--- {chap['title']} [{chap['rel_path']}] ---{RESET} ({chap['words_a']:,} -> {chap['words_b']:,} words, {GREEN}+{chap['added_words']}{RESET}/{RED}-{chap['deleted_words']}{RESET}, Net: {c_net_str})")

            # Print inline chunk tokens
            line_buf = []
            for chunk in chap["chunks"]:
                tag = chunk["tag"]
                txt = chunk["text"]
                if tag == "insert":
                    line_buf.append(f"{GREEN}{txt}{RESET}")
                elif tag == "delete":
                    line_buf.append(f"{RED}{txt}{RESET}")
                else:
                    line_buf.append(txt)
            out.append("".join(line_buf))
            out.append("")

        return "\n".join(out)

    def to_html(self) -> str:
        """
        Generates accessible, standalone HTML Redline Changelog.
        Includes chapter sidebar, word counts, search, light/dark mode, and inline/side-by-side view.
        """
        if not self.summary:
            self.compare()
        return render_manuscript_diff_html(
            summary=self.summary,
            chapters=self.chapters,
            label_a=self.label_a,
            label_b=self.label_b,
        )


    def open_in_libreoffice(self) -> bool:
        """
        Converts Draft A and Draft B to ODT via pandoc (if installed)
        and launches LibreOffice Writer comparison.
        """
        import tempfile
        tmp_dir = Path(tempfile.mkdtemp(prefix="arcanum_lo_diff_"))
        doc_a = tmp_dir / f"{self.label_a}.odt"
        doc_b = tmp_dir / f"{self.label_b}.odt"

        # Combine text for each draft
        text_a = "\n\n".join(f"# {c['title']}\n\n{c['raw_a']}" for c in self.chapters)
        text_b = "\n\n".join(f"# {c['title']}\n\n{c['raw_b']}" for c in self.chapters)

        src_a = tmp_dir / "draft_a.md"
        src_b = tmp_dir / "draft_b.md"
        atomic_write(src_a, text_a)
        atomic_write(src_b, text_b)

        # Convert to ODT with pandoc
        try:
            subprocess.run(["pandoc", str(src_a), "-o", str(doc_a)], check=True)
            subprocess.run(["pandoc", str(src_b), "-o", str(doc_b)], check=True)
            # Launch LibreOffice
            lo_cmd = ["libreoffice", "--writer", str(doc_b)]
            subprocess.Popen(lo_cmd)
            return True
        except Exception as e:
            print(f"[!] Could not launch LibreOffice comparison: {e}", file=sys.stderr)
            return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ars Arcanum Manuscript Diff & Redline Generator")
    parser.add_argument("paths", nargs="+", help="Draft directories/files to compare (path_a path_b OR ms_dir draft_b draft_a)")
    parser.add_argument("--label-a", default="", help="Display label for Draft A (default: folder name)")
    parser.add_argument("--label-b", default="", help="Display label for Draft B (default: folder name)")
    parser.add_argument("--html", help="Path to write standalone HTML Redline report")
    parser.add_argument("--json", action="store_true", help="Output summary change metrics as JSON")
    parser.add_argument("--terminal", action="store_true", help="Print colorized ANSI diff to stdout")
    parser.add_argument("--libreoffice", action="store_true", help="Export to ODT and launch LibreOffice Writer")
    add_scope_arguments(parser, include_world=False, target_pos_arg=False)

    args = parser.parse_args(argv)

    scope = parse_scope_args(args)

    if len(args.paths) == 1:
        print("Error: At least two draft paths or a manuscript project with two drafts are required.", file=sys.stderr)
        sys.exit(2)
    if len(args.paths) == 2:
        p_a = Path(args.paths[0]).expanduser().resolve()
        p_b = Path(args.paths[1]).expanduser().resolve()
        label_a = args.label_a or p_a.name
        label_b = args.label_b or p_b.name
    else:
        # 3 arguments: ms_dir, draft_b, draft_a
        ms_dir = Path(args.paths[0]).expanduser().resolve()
        if not ms_dir.exists():
            cand = Path.home() / "Manuscripts" / args.paths[0]
            if cand.is_dir():
                ms_dir = cand
        d_b_name = args.paths[1]
        d_a_name = args.paths[2]

        # Check Book-01
        book_dir = ms_dir / "Book-01" if (ms_dir / "Book-01").is_dir() else ms_dir

        p_a = book_dir / d_a_name if (book_dir / d_a_name).is_dir() else book_dir
        p_b = book_dir / d_b_name if (book_dir / d_b_name).is_dir() else book_dir
        label_a = args.label_a or d_a_name
        label_b = args.label_b or d_b_name

    if not p_a.exists():
        print(f"Error: Path A does not exist: {p_a}", file=sys.stderr)
        sys.exit(2)
    if not p_b.exists():
        print(f"Error: Path B does not exist: {p_b}", file=sys.stderr)
        sys.exit(2)

    comparator = ManuscriptComparator(p_a, p_b, label_a, label_b, scope=scope)
    comparator.compare()

    if args.json:
        print(comparator.to_json())
    elif args.html:
        out_path = Path(args.html).expanduser().resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        atomic_write(out_path, comparator.to_html(), encoding="utf-8")
        print(f"[✓] Redline HTML report generated at: {out_path}")
    elif args.libreoffice:
        comparator.open_in_libreoffice()
    else:
        # Default to terminal ANSI diff
        print(comparator.to_terminal_ansi())

    return 0


if __name__ == "__main__":
    sys.exit(main())
