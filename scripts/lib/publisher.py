#!/usr/bin/env python3
"""
Ars Arcanum Sovereign Typesetting & Publication Pipeline (scripts/lib/publisher.py)
==================================================================================
Pure-Python, zero-dependency publication compiler supporting:
1. Print-Ready PDF via Typst (sub-second commercial book typography)
2. Professional EPUB3 via Pandoc (embedded covers, metadata, reflowable layout)
3. Standard Submission DOCX via native OpenXML builder (William Shunn format)
4. Comprehensive --inspect / --dry-run validation of AST blocks and commands.
"""

from __future__ import annotations

import argparse
import json
import logging
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    from lib._bootstrap import atomic_write, count_prose_words, sanitize_identifier
    from lib.data_access import get_data_access
    from lib.docx_builder import build_docx_package, parse_markdown_to_paragraphs
    from lib.docx_presets import get_docx_config
    from lib.frontmatter import extract_frontmatter_and_body, parse_yaml_document
    from lib.scope import EngineScope, filter_manuscript_scope, resolve_manuscript_path
except ImportError:
    from _bootstrap import atomic_write, count_prose_words, sanitize_identifier
    from data_access import get_data_access
    from docx_builder import build_docx_package, parse_markdown_to_paragraphs
    from docx_presets import get_docx_config
    from frontmatter import extract_frontmatter_and_body, parse_yaml_document
    from scope import EngineScope, filter_manuscript_scope, resolve_manuscript_path

logger = logging.getLogger("arcanum.publisher")


def find_tool(tool_name: str) -> str | None:
    """Discovers external CLI tool binary across standard Windows and POSIX locations."""
    # Check PATH first
    found = shutil.which(tool_name)
    if found:
        return found

    # Platform-specific fallback paths
    if sys.platform == "win32":
        candidates = [
            Path(r"C:\Program Files\Pandoc\pandoc.exe"),
            Path(r"C:\Program Files (x86)\Pandoc\pandoc.exe"),
            Path(r"C:\Program Files\Typst\typst.exe"),
            Path.home() / "AppData" / "Local" / "Programs" / "typst" / "typst.exe",
            Path.home() / "AppData" / "Local" / "Programs" / "Pandoc" / "pandoc.exe",
            Path.home() / ".cargo" / "bin" / f"{tool_name}.exe",
        ]
        for c in candidates:
            if c.name.lower().startswith(tool_name.lower()) and c.is_file():
                return str(c)
    else:
        candidates = [
            Path(f"/usr/local/bin/{tool_name}"),
            Path(f"/usr/bin/{tool_name}"),
            Path(f"/opt/homebrew/bin/{tool_name}"),
            Path.home() / ".cargo" / "bin" / tool_name,
            Path.home() / ".local" / "bin" / tool_name,
        ]
        for c in candidates:
            if c.is_file():
                return str(c)

    return None


def get_manuscript_metadata(ms_dir: Path) -> dict[str, Any]:
    """Reads manuscript manifest metadata or returns sensible defaults."""
    dal = get_data_access()
    manifest_file = ms_dir / "manuscript.yaml"
    meta = {
        "title": ms_dir.name.replace("_", " "),
        "author": "Author",
        "language": "en",
        "copyright_year": "2026",
        "isbn": "",
        "paper_size": "us-trade",
        "genre": "fantasy",
    }
    if manifest_file.is_file():
        try:
            raw = dal.read_file(manifest_file)
            m_data = parse_yaml_document(raw)
            if isinstance(m_data, dict):
                meta.update(m_data)
        except Exception as e:
            logger.warning("Failed parsing manuscript manifest: %s", e)
    return meta


def collect_manuscript_content(
    ms_dir: Path,
    draft_name: str | None = None,
    scope: EngineScope | None = None,
) -> tuple[list[dict[str, Any]], int]:
    """Gathers all chapters and scenes in canonical order with word counts."""
    dal = get_data_access()
    chapter_items, _, _ = filter_manuscript_scope(ms_dir, scope=scope)
    chapters: list[dict[str, Any]] = []
    total_words = 0

    for item in chapter_items:
        fpath = item.path
        raw = dal.read_file(fpath)
        fm, body = extract_frontmatter_and_body(raw)
        words = count_prose_words(body)
        total_words += words
        title = fm.get("title") or fpath.stem.replace("_", " ")

        chapters.append({
            "index": item.index,
            "filename": fpath.name,
            "title": str(title),
            "frontmatter": fm,
            "body": body,
            "words": words,
            "path": str(fpath),
        })

    return chapters, total_words


def compile_docx(
    ms_dir: Path,
    output_path: Path,
    chapters: list[dict[str, Any]],
    meta: dict[str, Any],
) -> Path:
    """Compiles manuscript into a standard submission DOCX package."""
    docx_cfg = get_docx_config()
    full_markdown_parts = []

    for ch in chapters:
        full_markdown_parts.append(f"# {ch['title']}\n\n{ch['body']}\n\n")

    full_md = "\n".join(full_markdown_parts)
    author = str(meta.get("author", "Author"))
    title = str(meta.get("title", ms_dir.name))

    parsed_paragraphs = parse_markdown_to_paragraphs(full_md)
    build_docx_package(
        output_path,
        parsed_paragraphs,
        config=docx_cfg,
        title=title,
        author=author,
        is_full_manuscript=True,
    )
    return output_path


def compile_typst_pdf(
    ms_dir: Path,
    output_path: Path,
    chapters: list[dict[str, Any]],
    meta: dict[str, Any],
    typst_bin: str,
    inspect_only: bool = False,
) -> dict[str, Any]:
    """Compiles manuscript into print-ready PDF using Typst."""
    title = meta.get("title", ms_dir.name)
    author = meta.get("author", "Author")

    # Generate Typst source markup
    typst_lines = [
        f'#set document(title: "{title}", author: "{author}")',
        '#set page(paper: "us-trade", margin: (inside: 2cm, outside: 1.5cm, top: 2cm, bottom: 2cm))',
        '#set text(font: "Linux Libertine", size: 11pt, lang: "en")',
        '#set par(justify: true, leading: 0.7em, first-line-indent: 1.5em)',
        "",
        f'#align(center + horizon)[\n  #text(24pt, weight: "bold")[{title}]\n  #v(1em)\n  #text(14pt)[By {author}]\n]',
        "#pagebreak()",
        "",
    ]

    for ch in chapters:
        # Escape typst markup in title
        esc_title = ch["title"].replace('"', '\\"')
        typst_lines.append(f'= {esc_title}')
        typst_lines.append("")
        # Add chapter body paragraphs
        for p in ch["body"].split("\n\n"):
            p_clean = p.strip()
            if not p_clean:
                continue
            if p_clean in ("* * *", "***", "---"):
                typst_lines.append("#align(center)[* * *]")
            elif not p_clean.startswith("#"):
                typst_lines.append(p_clean)
            typst_lines.append("")
        typst_lines.append("#pagebreak()")
        typst_lines.append("")

    typ_source = "\n".join(typst_lines)
    exports_dir = ms_dir / "Exports"
    exports_dir.mkdir(parents=True, exist_ok=True)
    temp_typ = exports_dir / f"{sanitize_identifier(ms_dir.name)}_book.typ"
    atomic_write(temp_typ, typ_source)

    cmd = [typst_bin, "compile", str(temp_typ), str(output_path)]
    if inspect_only:
        return {
            "status": "inspected",
            "format": "pdf",
            "command": cmd,
            "typ_source_path": str(temp_typ),
            "output_path": str(output_path),
        }

    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Typst compilation failed: {res.stderr}")

    return {
        "status": "success",
        "format": "pdf",
        "output_path": str(output_path),
        "size_bytes": output_path.stat().st_size if output_path.exists() else 0,
    }


def compile_pandoc_epub(
    ms_dir: Path,
    output_path: Path,
    chapters: list[dict[str, Any]],
    meta: dict[str, Any],
    pandoc_bin: str,
    inspect_only: bool = False,
) -> dict[str, Any]:
    """Compiles manuscript into professional EPUB3 using Pandoc."""
    title = meta.get("title", ms_dir.name)
    author = meta.get("author", "Author")

    md_lines = [
        "---",
        f"title: {json.dumps(title)}",
        f"author: {json.dumps(author)}",
        f"rights: Copyright {meta.get('copyright_year', '2026')} {author}. All rights reserved.",
        f"language: {meta.get('language', 'en')}",
        "---",
        "",
    ]

    for ch in chapters:
        md_lines.append(f"# {ch['title']}\n\n")
        md_lines.append(ch["body"])
        md_lines.append("\n\n---\n\n")

    full_md = "\n".join(md_lines)
    exports_dir = ms_dir / "Exports"
    exports_dir.mkdir(parents=True, exist_ok=True)
    temp_md = exports_dir / f"{sanitize_identifier(ms_dir.name)}_epub_source.md"
    atomic_write(temp_md, full_md)

    cmd = [
        pandoc_bin,
        str(temp_md),
        "-o",
        str(output_path),
        "--to=epub3",
        "--split-level=1",
    ]

    # Check for cover image
    cover = ms_dir / "03-Art" / "cover.png"
    if not cover.is_file():
        cover = ms_dir / "cover.png"
    if cover.is_file():
        cmd.extend([f"--epub-cover-image={cover}"])

    if inspect_only:
        return {
            "status": "inspected",
            "format": "epub",
            "command": cmd,
            "md_source_path": str(temp_md),
            "output_path": str(output_path),
        }

    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Pandoc EPUB compilation failed: {res.stderr}")

    return {
        "status": "success",
        "format": "epub",
        "output_path": str(output_path),
        "size_bytes": output_path.stat().st_size if output_path.exists() else 0,
    }


def publish_manuscript(
    target_dir: Path | str,
    output_format: str = "all",
    preset_name: str | None = None,
    inspect_only: bool = False,
    scope: EngineScope | None = None,
) -> dict[str, Any]:
    """Master publication orchestrator compiling to requested formats."""
    ms_path = resolve_manuscript_path(target_dir) or Path(target_dir).resolve()
    if not ms_path.is_dir():
        raise FileNotFoundError(f"Manuscript directory not found: {target_dir}")

    meta = get_manuscript_metadata(ms_path)
    chapters, total_words = collect_manuscript_content(ms_path, scope=scope)

    if not chapters:
        raise ValueError(f"No chapters or scenes found to publish in {ms_path}")

    exports_dir = ms_path / "Exports"
    exports_dir.mkdir(parents=True, exist_ok=True)
    clean_stem = sanitize_identifier(ms_path.name)

    results: dict[str, Any] = {
        "status": "success",
        "manuscript": ms_path.name,
        "title": meta.get("title", ms_path.name),
        "author": meta.get("author", "Author"),
        "total_words": total_words,
        "chapters_count": len(chapters),
        "formats": {},
    }

    req_formats = [output_format.lower()] if output_format.lower() != "all" else ["docx", "pdf", "epub"]

    # 1. DOCX Standard Submission
    if "docx" in req_formats:
        out_docx = exports_dir / f"{clean_stem}_StandardSubmission.docx"
        if inspect_only:
            results["formats"]["docx"] = {
                "status": "inspected",
                "format": "docx",
                "output_path": str(out_docx),
                "builder": "native_zero_pip_openxml",
            }
        else:
            compile_docx(ms_path, out_docx, chapters, meta)
            results["formats"]["docx"] = {
                "status": "success",
                "format": "docx",
                "output_path": str(out_docx),
                "size_bytes": out_docx.stat().st_size if out_docx.exists() else 0,
            }

    # 2. Typst Print PDF
    if "pdf" in req_formats:
        typst_bin = find_tool("typst")
        out_pdf = exports_dir / f"{clean_stem}_Book.pdf"
        if not typst_bin and not inspect_only:
            results["formats"]["pdf"] = {
                "status": "skipped",
                "reason": "Typst executable not found in PATH or standard directories.",
            }
        else:
            bin_path = typst_bin or "typst"
            try:
                res_pdf = compile_typst_pdf(
                    ms_path,
                    out_pdf,
                    chapters,
                    meta,
                    typst_bin=bin_path,
                    inspect_only=inspect_only,
                )
                results["formats"]["pdf"] = res_pdf
            except Exception as e:
                results["formats"]["pdf"] = {"status": "error", "error": str(e)}

    # 3. Pandoc EPUB3
    if "epub" in req_formats:
        pandoc_bin = find_tool("pandoc")
        out_epub = exports_dir / f"{clean_stem}_Ebook.epub"
        if not pandoc_bin and not inspect_only:
            results["formats"]["epub"] = {
                "status": "skipped",
                "reason": "Pandoc executable not found in PATH or standard directories.",
            }
        else:
            bin_path = pandoc_bin or "pandoc"
            try:
                res_epub = compile_pandoc_epub(
                    ms_path,
                    out_epub,
                    chapters,
                    meta,
                    pandoc_bin=bin_path,
                    inspect_only=inspect_only,
                )
                results["formats"]["epub"] = res_epub
            except Exception as e:
                results["formats"]["epub"] = {"status": "error", "error": str(e)}

    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ars Arcanum Sovereign Publication Pipeline")
    parser.add_argument("manuscript", nargs="?", default=".", help="Manuscript name or directory")
    parser.add_argument(
        "--format",
        "-f",
        choices=["all", "docx", "pdf", "epub"],
        default="all",
        help="Target publication format (default: all)",
    )
    parser.add_argument("--inspect", "--dry-run", action="store_true", help="Inspect and validate AST without executing binaries")
    parser.add_argument("--json", "-j", action="store_true", help="Output machine-readable JSON manifest")

    args = parser.parse_args(argv)

    try:
        res = publish_manuscript(
            args.manuscript,
            output_format=args.format,
            inspect_only=args.inspect,
        )

        if args.json:
            print(json.dumps(res, indent=2))
            return 0

        mode_str = " (INSPECT / DRY-RUN)" if args.inspect else ""
        print(f"📚 Ars Arcanum Publication Pipeline{mode_str}")
        print(f"  Title:     {res['title']}")
        print(f"  Author:    {res['author']}")
        print(f"  Words:     {res['total_words']:,} across {res['chapters_count']} chapters")
        print("─" * 70)

        for fmt, info in res.get("formats", {}).items():
            st = info.get("status", "unknown").upper()
            if st == "SUCCESS":
                sz = f" ({info.get('size_bytes', 0):,} bytes)"
                print(f"  ✓ [{fmt.upper()}] Generated: {info.get('output_path')}{sz}")
            elif st == "INSPECTED":
                cmd_str = " ".join(info.get("command", [])) if info.get("command") else "Native OpenXML Builder"
                print(f"  🔍 [{fmt.upper()}] Inspected -> Target: {info.get('output_path')}")
                print(f"     Command: {cmd_str}")
            elif st == "SKIPPED":
                print(f"  ⚠️ [{fmt.upper()}] Skipped: {info.get('reason')}")
            else:
                print(f"  ❌ [{fmt.upper()}] Failed: {info.get('error')}")

        print("═" * 70)
        return 0

    except Exception as e:
        if args.json:
            print(json.dumps({"status": "error", "error": str(e)}, indent=2))
        else:
            print(f"Error: {e}", file=sys.stderr)
        return 1


__all__ = [
    "compile_docx",
    "compile_pandoc_epub",
    "compile_typst_pdf",
    "find_tool",
    "main",
    "publish_manuscript",
]

if __name__ == "__main__":
    sys.exit(main())
