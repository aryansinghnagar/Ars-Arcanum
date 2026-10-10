#!/usr/bin/env python3
"""
Ars Arcanum Manuscript Comparison & Redline Diff Engine (scripts/lib/manuscript_diff.py)
======================================================================================
Provides word-level, paragraph-level, and chapter-level comparison between manuscript drafts.
Generates:
  1. Standalone Multi-Tab HTML Editorial Studio with Unified Redline, Side-by-Side Split View,
     Excised Scraps Inspector, Chapter Churn Matrix, light/dark mode, and instant search.
  2. Automatic Scraps Vault synchronization (extracting cut prose >= 50 words to Scraps/*.md).
  3. ANSI colorized terminal diff with executive word-delta summary.
  4. Machine-readable JSON change metrics.
  5. Bridge to LibreOffice Writer Track Changes comparison.

100% offline, privacy-respecting, zero-telemetry, and accessible.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from lib._bootstrap import atomic_write
    from lib.constitution import get_authorial_constitution
    from lib.draft_manager import DraftManager
    from lib.manuscript_diff_template import render_manuscript_diff_html
    from lib.scope import (
        EngineScope,
        add_scope_arguments,
        filter_manuscript_scope,
        parse_scope_args,
    )
    from lib.scope_resolver import get_active_manuscript
except ImportError:
    from _bootstrap import atomic_write
    from constitution import get_authorial_constitution  # type: ignore[no-redef]
    from draft_manager import DraftManager  # type: ignore[no-redef]
    from manuscript_diff_template import (  # type: ignore[no-redef]
        render_manuscript_diff_html,
    )
    from scope import (  # type: ignore[no-redef]
        EngineScope,
        add_scope_arguments,
        filter_manuscript_scope,
        parse_scope_args,
    )
    from scope_resolver import get_active_manuscript  # type: ignore[no-redef]


NW_TAG_REGEX = re.compile(r"^@[A-Za-z0-9_-]+:")
TOKEN_REGEX = re.compile(r"\S+|\s+")
WORD_REGEX = re.compile(r"\b\w+\b", re.UNICODE)
STEM_CLEAN_REGEX = re.compile(r"^\d+_")
INTENT_TAG_REGEX = re.compile(r"@intent:\s*([A-Za-z0-9_-]+)", re.IGNORECASE)

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


def extract_intent_directives(text: str) -> list[str]:
    """Extracts @intent: directives declared in chapter header or comments."""
    return [m.lower() for m in INTENT_TAG_REGEX.findall(text)]


def tokenize_words(text: str) -> list[str]:
    """Splits text into words, whitespace, and punctuation tokens preserving full structure."""
    return TOKEN_REGEX.findall(text)


def compute_word_diff(tokens_a: list[str], tokens_b: list[str]) -> tuple[list[dict[str, Any]], int, int]:
    """
    Computes word-level diff using difflib.SequenceMatcher.
    Returns:
      (diff_chunks, added_word_count, deleted_word_count)
    """
    matcher = difflib.SequenceMatcher(None, tokens_a, tokens_b)
    chunks: list[dict[str, Any]] = []
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


def _normalize_fingerprint(text: str) -> str:
    """Creates a normalized alphanumeric fingerprint for paragraph move detection."""
    return re.sub(r"\W+", "", text.lower())


def detect_moved_paragraphs(
    paras_a: list[str],
    paras_b: list[str],
    min_words: int = 15,
) -> tuple[set[int], set[int], dict[int, int]]:
    """
    Detects paragraphs in Draft A that were relocated to a different position in Draft B.
    Returns:
      (moved_indices_a, moved_indices_b, mapping_a_to_b)
    """
    fp_a = [_normalize_fingerprint(p) for p in paras_a]
    fp_b = [_normalize_fingerprint(p) for p in paras_b]

    moved_a: set[int] = set()
    moved_b: set[int] = set()
    a_to_b: dict[int, int] = {}

    for i, p_a in enumerate(paras_a):
        if len(WORD_REGEX.findall(p_a)) < min_words:
            continue
        fp = fp_a[i]
        if not fp:
            continue
        for j, p_b in enumerate(paras_b):
            if j in moved_b:
                continue
            if len(WORD_REGEX.findall(p_b)) < min_words:
                continue
            if fp == fp_b[j] and abs(i - j) > 1:
                moved_a.add(i)
                moved_b.add(j)
                a_to_b[i] = j
                break

    return moved_a, moved_b, a_to_b


def discover_draft_files(draft_dir: Path) -> list[Path]:
    """Finds and sorts all markdown files in a draft directory."""
    if not draft_dir.is_dir():
        return []
    md_files = []
    for p in sorted(draft_dir.rglob("*.md")):
        rel_parts = p.relative_to(draft_dir).parts
        if any(part in ("Outlines", "Exports", "Backups", "05-Backups", "04-Publishing", "Scraps") or part.startswith(".") for part in rel_parts):
            continue
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
    stem = file_path.stem
    clean = STEM_CLEAN_REGEX.sub("", stem).replace("_", " ").replace("-", " ")
    return clean.title()


class ManuscriptComparator:
    def __init__(
        self,
        path_a: Path,
        path_b: Path,
        label_a: str = "Draft 1",
        label_b: str = "Draft 2",
        scope: Any = None,
        ms_root: Path | None = None,
        scrap_threshold: int = 50,
        sync_scraps: bool = True,
        scraps_dir: Path | None = None,
    ):
        self.path_a = path_a
        self.path_b = path_b
        self.label_a = label_a
        self.label_b = label_b
        self.scope = scope
        self.ms_root = ms_root or (path_a.parent if path_a.parent.name.startswith("Draft-") else path_a)
        self.scrap_threshold = scrap_threshold
        self.sync_scraps = sync_scraps
        self.scraps_dir = scraps_dir
        self.chapters: list[dict[str, Any]] = []
        self.summary: dict[str, Any] = {}
        self.scraps: list[dict[str, Any]] = []
        self.advisories: list[dict[str, Any]] = []

    def compare(self) -> dict[str, Any]:
        """Performs full comparison across all chapters/files."""
        self.chapters.clear()
        self.scraps.clear()
        self.advisories.clear()

        if self.path_a.is_file() and self.path_b.is_file():
            self._compare_single_files(self.path_a, self.path_b)
        else:
            self._compare_directories(self.path_a, self.path_b)

        total_a = sum(c["words_a"] for c in self.chapters)
        total_b = sum(c["words_b"] for c in self.chapters)
        added = sum(c["added_words"] for c in self.chapters)
        deleted = sum(c["deleted_words"] for c in self.chapters)
        moved = sum(c.get("moved_words", 0) for c in self.chapters)
        net_change = total_b - total_a

        if total_a + total_b > 0:
            sim_sum = sum(c["similarity"] * (c["words_a"] + c["words_b"]) for c in self.chapters)
            overall_sim = round(sim_sum / (total_a + total_b), 4)
        else:
            overall_sim = 1.0

        # Subsystem 2 Diagnostic Advisory Checks
        self._evaluate_advisory_telemetry()

        # Sync Scraps to Vault if enabled
        if self.sync_scraps and self.scraps:
            self._archive_scraps_to_vault()

        self.summary = {
            "label_a": self.label_a,
            "label_b": self.label_b,
            "path_a": str(self.path_a),
            "path_b": str(self.path_b),
            "total_words_a": total_a,
            "total_words_b": total_b,
            "added_words": added,
            "deleted_words": deleted,
            "moved_words": moved,
            "net_change": net_change,
            "similarity_ratio": overall_sim,
            "chapter_count": len(self.chapters),
            "chapters": self.chapters,
            "scraps": self.scraps,
            "advisories": self.advisories,
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
        intents_a = extract_intent_directives(raw_a)
        intents_b = extract_intent_directives(raw_b)
        combined_intents = list(set(intents_a + intents_b))

        clean_a = strip_nw_metadata(raw_a)
        clean_b = strip_nw_metadata(raw_b)

        words_a = count_words(clean_a)
        words_b = count_words(clean_b)

        # Split paragraphs for moved detection and split pairing
        paras_a = [p.strip() for p in clean_a.split("\n\n") if p.strip()]
        paras_b = [p.strip() for p in clean_b.split("\n\n") if p.strip()]

        moved_a, moved_b, _ = detect_moved_paragraphs(paras_a, paras_b)
        moved_words = sum(len(WORD_REGEX.findall(paras_b[idx])) for idx in moved_b)

        # Build paragraph-level split pairs for Side-by-Side Split View
        split_pairs: list[dict[str, Any]] = []
        max_paras = max(len(paras_a), len(paras_b))

        for p_idx in range(max_paras):
            pa = paras_a[p_idx] if p_idx < len(paras_a) else None
            pb = paras_b[p_idx] if p_idx < len(paras_b) else None

            if pa is not None and pb is not None:
                if p_idx in moved_a or p_idx in moved_b:
                    split_pairs.append({"tag": "moved", "text_a": pa, "text_b": pb})
                elif pa == pb:
                    split_pairs.append({"tag": "equal", "text_a": pa, "text_b": pb})
                else:
                    split_pairs.append({"tag": "replace", "text_a": pa, "text_b": pb})
            elif pa is not None:
                split_pairs.append({"tag": "delete", "text_a": pa, "text_b": ""})
            elif pb is not None:
                split_pairs.append({"tag": "insert", "text_a": "", "text_b": pb})

        # Token-level diff for unified inline view
        tokens_a = tokenize_words(clean_a)
        tokens_b = tokenize_words(clean_b)
        chunks, added, deleted = compute_word_diff(tokens_a, tokens_b)

        # Identify excised chunks exceeding scrap threshold
        for chunk in chunks:
            if chunk["tag"] == "delete":
                txt = chunk["text"].strip()
                w_count = len(WORD_REGEX.findall(txt))
                if w_count >= self.scrap_threshold:
                    content_hash = hashlib.sha256(txt.encode("utf-8")).hexdigest()[:8]
                    clean_title_stem = re.sub(r"[^A-Za-z0-9_-]", "_", title)[:24]
                    scrap_id = f"SCRAP-{clean_title_stem}-{content_hash}"
                    self.scraps.append({
                        "scrap_id": scrap_id,
                        "chapter": title,
                        "rel_path": rel_path,
                        "source_draft": self.label_a,
                        "compared_with": self.label_b,
                        "cut_date": datetime.now(timezone.utc).isoformat(),
                        "word_count": w_count,
                        "content": txt,
                    })

        matcher = difflib.SequenceMatcher(None, tokens_a, tokens_b)
        sim = round(matcher.ratio(), 4)

        return {
            "title": title,
            "rel_path": rel_path,
            "words_a": words_a,
            "words_b": words_b,
            "added_words": added,
            "deleted_words": deleted,
            "moved_words": moved_words,
            "net_change": words_b - words_a,
            "similarity": sim,
            "intents": combined_intents,
            "chunks": chunks,
            "split_pairs": split_pairs,
            "raw_a": clean_a,
            "raw_b": clean_b,
        }

    def _evaluate_advisory_telemetry(self):
        """Generates Subsystem 2 advisory telemetry observations honoring Authorial Constitution."""
        constitution = get_authorial_constitution(manuscript_path=self.ms_root)
        diag_conf = constitution.get("diagnostics", {})
        suppressed = diag_conf.get("suppressed_rules", [])

        for chap in self.chapters:
            intents = chap.get("intents", [])
            if "deliberate" in intents or "rewrite" in intents:
                continue

            w_a = chap.get("words_a", 0)
            c_del = chap.get("deleted_words", 0)
            c_sim = chap.get("similarity", 1.0)
            title = chap.get("title", "")

            # 1. Massive cut observation (>30% loss or >1500 cut)
            if "DIFF-301" not in suppressed and w_a > 0 and (c_del / w_a) > 0.30 and c_del >= 500:
                self.advisories.append({
                    "rule_id": "DIFF-301",
                    "severity": "OBSERVATION",
                    "chapter": title,
                    "message": f"Substantial prose cut detected (-{c_del:,} words, {round((c_del/w_a)*100)}% of chapter). Excised sections archived in Scraps vault.",
                })

            # 2. Heavy rewrite / churn loop alert (similarity < 50%)
            if "DIFF-302" not in suppressed and w_a > 300 and c_sim < 0.50:
                self.advisories.append({
                    "rule_id": "DIFF-302",
                    "severity": "LENS_NOTE",
                    "chapter": title,
                    "message": f"High developmental churn ({round((1 - c_sim)*100)}% revision divergence). Check scene pacing and character intent.",
                })

    def _archive_scraps_to_vault(self):
        """Writes excised prose scraps to Manuscripts/<MS>/Scraps/*.md using atomic_write."""
        dest_dir = self.scraps_dir or (self.ms_root / "Scraps" if self.ms_root and self.ms_root.is_dir() else Path.cwd() / "Scraps")
        dest_dir.mkdir(parents=True, exist_ok=True)

        for scrap in self.scraps:
            s_id = scrap["scrap_id"]
            file_path = dest_dir / f"{s_id}.md"
            if file_path.exists():
                continue

            content_md = f"""---
scrap_id: "{scrap['scrap_id']}"
chapter: "{scrap['chapter']}"
source_draft: "{scrap['source_draft']}"
compared_with: "{scrap['compared_with']}"
cut_date: "{scrap['cut_date']}"
word_count: {scrap['word_count']}
rel_path: "{scrap['rel_path']}"
---

{scrap['content']}
"""
            atomic_write(file_path, content_md, encoding="utf-8")

    def to_json(self, indent: int = 2) -> str:
        """Returns JSON representation with clean chapter summaries and scraps."""
        if not self.summary:
            self.compare()
        export_data = dict(self.summary)
        export_data["chapters"] = [
            {k: v for k, v in c.items() if k not in ("chunks", "split_pairs", "raw_a", "raw_b")}
            for c in self.chapters
        ]
        return json.dumps(export_data, indent=indent, ensure_ascii=False)

    def to_terminal_ansi(self) -> str:
        """Generates rich ANSI colored diff output for terminal."""
        if not self.summary:
            self.compare()

        RED = "\033[38;2;220;53;69m\033[9m"
        GREEN = "\033[38;2;40;167;69m\033[4m"
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
        moved_str = f" | {CYAN}⇄ {self.summary['moved_words']:,} moved{RESET}" if self.summary['moved_words'] else ""
        out.append(f"{DIM}Delta Stats:{RESET} {GREEN}+{self.summary['added_words']:,} added{RESET} | {RED}-{self.summary['deleted_words']:,} deleted{RESET}{moved_str} | Net: {BOLD}{net_str}{RESET} | Similarity: {self.summary['similarity_ratio']*100:.1f}%\n")

        for chap in self.chapters:
            c_net = chap['net_change']
            c_net_str = f"+{c_net:,}" if c_net >= 0 else f"{c_net:,}"
            out.append(f"{CYAN}--- {chap['title']} [{chap['rel_path']}] ---{RESET} ({chap['words_a']:,} -> {chap['words_b']:,} words, {GREEN}+{chap['added_words']}{RESET}/{RED}-{chap['deleted_words']}{RESET}, Net: {c_net_str})")

            line_buf = []
            for chunk in chap["chunks"]:
                tag = chunk["tag"]
                txt = chunk["text"]
                if tag == "insert":
                    line_buf.append(f"{GREEN}{txt}{RESET}")
                elif tag == "delete":
                    line_buf.append(f"{RED}{txt}{RESET}")
                elif tag == "moved":
                    line_buf.append(f"{CYAN}{txt}{RESET}")
                else:
                    line_buf.append(txt)
            out.append("".join(line_buf))
            out.append("")

        return "\n".join(out)

    def to_html(self) -> str:
        """Generates accessible, standalone Multi-Tab HTML Editorial Studio report."""
        if not self.summary:
            self.compare()
        return render_manuscript_diff_html(
            summary=self.summary,
            chapters=self.chapters,
            label_a=self.label_a,
            label_b=self.label_b,
            scraps=self.scraps,
            advisories=self.advisories,
        )

    def open_in_libreoffice(self) -> bool:
        """Converts Draft A and Draft B to ODT via pandoc and launches LibreOffice Writer comparison."""
        import tempfile
        tmp_dir = Path(tempfile.mkdtemp(prefix="arcanum_lo_diff_"))
        doc_a = tmp_dir / f"{self.label_a}.odt"
        doc_b = tmp_dir / f"{self.label_b}.odt"

        text_a = "\n\n".join(f"# {c['title']}\n\n{c['raw_a']}" for c in self.chapters)
        text_b = "\n\n".join(f"# {c['title']}\n\n{c['raw_b']}" for c in self.chapters)

        src_a = tmp_dir / "draft_a.md"
        src_b = tmp_dir / "draft_b.md"
        atomic_write(src_a, text_a)
        atomic_write(src_b, text_b)

        try:
            subprocess.run(["pandoc", str(src_a), "-o", str(doc_a)], check=True)
            subprocess.run(["pandoc", str(src_b), "-o", str(doc_b)], check=True)
            lo_cmd = ["libreoffice", "--writer", str(doc_b)]
            subprocess.Popen(lo_cmd)
            return True
        except Exception as e:
            print(f"[!] Could not launch LibreOffice comparison: {e}", file=sys.stderr)
            return False


def resolve_comparison_targets(
    paths: list[str] | None = None,
) -> tuple[Path, Path, str, str, Path | None]:
    """
    Intelligently resolves Base (Draft A) and Prior (Draft B) targets:
    - 0 args: Auto-discover active manuscript and pick two latest drafts
    - 1 arg: If directory contains Draft-* folders, pick two latest drafts in that manuscript
    - 2 args: Compare two directories/files/draft-names
    - 3 args: ms_dir, draft_b, draft_a
    """
    if not paths or len(paths) == 0:
        active_ms = get_active_manuscript()
        if not active_ms:
            raise ValueError("No active manuscript detected. Please specify draft paths to compare.")
        mgr = DraftManager(active_ms)
        drafts = mgr.list_drafts()
        if len(drafts) < 2:
            raise ValueError(f"Manuscript '{active_ms.name}' requires at least 2 drafts to compare (found {len(drafts)}).")
        # Take two latest drafts
        d_base = drafts[-2]
        d_prior = drafts[-1]
        return Path(d_base.path), Path(d_prior.path), d_base.name, d_prior.name, active_ms

    if len(paths) == 1:
        cand_dir = Path(paths[0]).expanduser().resolve()
        if cand_dir.is_dir():
            mgr = DraftManager(cand_dir)
            drafts = mgr.list_drafts()
            if len(drafts) >= 2:
                d_base = drafts[-2]
                d_prior = drafts[-1]
                return Path(d_base.path), Path(d_prior.path), d_base.name, d_prior.name, cand_dir
        raise ValueError(f"Cannot compare a single path '{paths[0]}' without two draft iterations.")

    if len(paths) == 2:
        cand_a = Path(paths[0]).expanduser().resolve()
        cand_b = Path(paths[1]).expanduser().resolve()

        # Check if bare draft names given inside active manuscript
        if not cand_a.exists() or not cand_b.exists():
            active_ms = get_active_manuscript()
            if active_ms:
                alt_a = active_ms / paths[0]
                alt_b = active_ms / paths[1]
                if alt_a.exists() and alt_b.exists():
                    return alt_a, alt_b, paths[0], paths[1], active_ms

        label_a = cand_a.name
        label_b = cand_b.name
        ms_root = cand_a.parent if cand_a.parent.name.startswith("Draft-") else (cand_a if cand_a.is_dir() else cand_a.parent)
        return cand_a, cand_b, label_a, label_b, ms_root

    # 3 arguments: ms_dir, draft_b, draft_a
    ms_dir = Path(paths[0]).expanduser().resolve()
    if not ms_dir.exists():
        cand = Path.home() / "Manuscripts" / paths[0]
        if cand.is_dir():
            ms_dir = cand

    d_b_name = paths[1]
    d_a_name = paths[2]

    book_dir = ms_dir / "Book-01" if (ms_dir / "Book-01").is_dir() else ms_dir
    p_a = book_dir / d_a_name if (book_dir / d_a_name).is_dir() else book_dir
    p_b = book_dir / d_b_name if (book_dir / d_b_name).is_dir() else book_dir
    return p_a, p_b, d_a_name, d_b_name, ms_dir


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ars Arcanum Manuscript Diff & Redline Generator")
    parser.add_argument("paths", nargs="*", default=[], help="Draft directories/files to compare (path_a path_b OR auto-discovered)")
    parser.add_argument("--label-a", default="", help="Display label for Draft A (default: folder name)")
    parser.add_argument("--label-b", default="", help="Display label for Draft B (default: folder name)")
    parser.add_argument("--html", help="Path to write standalone Multi-Tab HTML Redline report")
    parser.add_argument("--json", action="store_true", help="Output summary change metrics as JSON")
    parser.add_argument("--terminal", action="store_true", help="Print full colorized ANSI diff to stdout")
    parser.add_argument("--libreoffice", action="store_true", help="Export to ODT and launch LibreOffice Writer")
    parser.add_argument("--no-scraps", action="store_true", help="Disable automatic Scraps Vault archiving")
    parser.add_argument("--scraps-dir", help="Custom destination directory for excised prose scraps")
    parser.add_argument("--threshold", type=int, default=50, help="Word threshold for excised scraps (default: 50 words)")
    parser.add_argument("--open", action="store_true", help="Automatically open generated HTML report in browser")
    add_scope_arguments(parser, include_world=False, target_pos_arg=False)

    args = parser.parse_args(argv)
    scope = parse_scope_args(args)

    try:
        p_a, p_b, resolved_label_a, resolved_label_b, ms_root = resolve_comparison_targets(args.paths)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)

    label_a = args.label_a or resolved_label_a
    label_b = args.label_b or resolved_label_b

    if not p_a.exists():
        print(f"Error: Path A does not exist: {p_a}", file=sys.stderr)
        sys.exit(2)
    if not p_b.exists():
        print(f"Error: Path B does not exist: {p_b}", file=sys.stderr)
        sys.exit(2)

    scraps_path = Path(args.scraps_dir).expanduser().resolve() if args.scraps_dir else None

    comparator = ManuscriptComparator(
        p_a,
        p_b,
        label_a=label_a,
        label_b=label_b,
        scope=scope,
        ms_root=ms_root,
        scrap_threshold=args.threshold,
        sync_scraps=not args.no_scraps,
        scraps_dir=scraps_path,
    )
    comparator.compare()

    # Determine default HTML output destination
    html_target = None
    if args.html:
        html_target = Path(args.html).expanduser().resolve()
    else:
        # Default report path inside manuscript reports or workspace reports
        reports_dir = (ms_root / "reports") if ms_root and ms_root.is_dir() else (Path.cwd() / "reports")
        html_target = reports_dir / f"diff_{label_a}_{label_b}.html"

    # Always write HTML visual studio report
    html_target.parent.mkdir(parents=True, exist_ok=True)
    atomic_write(html_target, comparator.to_html(), encoding="utf-8")

    if args.json:
        print(comparator.to_json())
    elif args.libreoffice:
        comparator.open_in_libreoffice()
    elif args.terminal:
        print(comparator.to_terminal_ansi())
    else:
        # Visual-First CLI Output: Print clean executive summary + links to Visual Studio & Scraps
        summary = comparator.summary
        total_a = summary["total_words_a"]
        total_b = summary["total_words_b"]
        added = summary["added_words"]
        deleted = summary["deleted_words"]
        net = summary["net_change"]
        net_str = f"+{net:,}" if net >= 0 else f"{net:,}"
        sim_pct = round(summary["similarity_ratio"] * 100, 1)

        print("\n\033[1;36m=== Ars Arcanum Manuscript Revision Comparison & Editorial Studio ===\033[0m")
        print(f"Comparing: \033[1m{label_a}\033[0m ({total_a:,} words) \033[36m→\033[0m \033[1m{label_b}\033[0m ({total_b:,} words)")
        print(f"Word Delta: \033[32m+{added:,} added\033[0m | \033[31m-{deleted:,} cut\033[0m | Net: \033[1m{net_str}\033[0m | Match: \033[1m{sim_pct}%\033[0m")
        print(f"Chapters Analyzed: {len(comparator.chapters)} | Excised Scraps: {len(comparator.scraps)}")

        if comparator.advisories:
            print("\n\033[1;33mEditorial Advisories:\033[0m")
            for adv in comparator.advisories:
                print(f"  • [{adv['chapter']}] {adv['message']}")

        html_uri = f"file:///{str(html_target).replace(chr(92), '/')}"
        print("\n\033[32m[✓]\033[0m Standalone Visual Studio generated:")
        print(f"    \033[4;34m{html_uri}\033[0m")

        if comparator.scraps and not args.no_scraps:
            s_dir = scraps_path or (ms_root / "Scraps" if ms_root else Path.cwd() / "Scraps")
            print(f"\033[32m[✓]\033[0m Excised Scraps Vault updated ({len(comparator.scraps)} cuts archived in {s_dir.name}/)")

    if args.open and html_target.exists():
        try:
            import webbrowser
            webbrowser.open(html_target.as_uri())
        except Exception:
            pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
