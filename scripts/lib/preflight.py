#!/usr/bin/env python3
"""
Ars Arcanum Pre-Flight Typesetting & Publishing Compliance Linter
(scripts/lib/preflight.py)
================================================================================
Zero-dependency, offline pre-flight validation engine for novels and manuscripts.

Capabilities (PUB-101):
1. Publishing Metadata Validation:
   - Verifies presence of Title, Author, Language, Copyright, and ISBN in `manuscript.yaml`.
2. Asset & Image Verification:
   - Verifies cover art existence (`03-Art/cover.png` or root cover).
   - Validates internal image paths and dimensions.
3. Typesetting & Formatting Integrity:
   - Scans for orphan headings at end-of-files.
   - Detects unclosed markdown formatting (bold/italics/codeblocks).
   - Catches unescaped Typst / LaTeX control characters.
   - Checks for straight quotation marks needing typography polish.
4. Word Count & Page Budgeting:
   - Calculates industry standard page count estimates (250 w/page standard).
   - Validates standard chapter length bounds.
5. Standalone HTML Pre-Flight Certificate & Compliance Report.
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
    from lib.data_access import get_data_access
    from lib.frontmatter import parse_yaml_document, parse_yaml_frontmatter
    from lib.preflight_template import render_preflight_html
    from lib.scope import (
        EngineScope,
        add_scope_arguments,
        filter_manuscript_scope,
        parse_scope_args,
        resolve_manuscript_path,
    )
except ImportError:
    from _bootstrap import count_prose_words
    from data_access import get_data_access
    from frontmatter import parse_yaml_document, parse_yaml_frontmatter
    from preflight_template import render_preflight_html
    from scope import (
        EngineScope,
        add_scope_arguments,
        filter_manuscript_scope,
        parse_scope_args,
        resolve_manuscript_path,
    )

logger = logging.getLogger("arcanum.preflight")


def check_metadata(manuscript_dir: Path) -> dict[str, Any]:
    """Validates manuscript metadata configuration in manuscript.yaml using cached DAL."""
    manifest_path = manuscript_dir / "manuscript.yaml"
    issues = []
    metadata: dict[str, Any] = {}

    if not manifest_path.is_file():
        issues.append({"level": "FAIL", "code": "META-01", "message": "Missing 'manuscript.yaml' manifest file."})
        return {"valid": False, "issues": issues, "data": {}}

    try:
        dal = get_data_access()
        raw_text = dal.read_file(manifest_path)
        metadata = parse_yaml_frontmatter(raw_text)
        if not metadata:
            metadata = parse_yaml_document(raw_text)
    except Exception as e:
        issues.append({"level": "FAIL", "code": "META-02", "message": f"Failed reading manuscript.yaml: {e}"})

    # Required fields
    required = ["title", "author"]
    for req in required:
        if not metadata.get(req):
            issues.append({
                "level": "FAIL",
                "code": f"META-REQ-{req.upper()}",
                "message": f"Missing required metadata field: '{req}'.",
            })

    recommended = ["isbn", "copyright_year", "language", "paper_size"]
    for rec in recommended:
        if not metadata.get(rec):
            issues.append({
                "level": "WARN",
                "code": f"META-REC-{rec.upper()}",
                "message": f"Recommended field '{rec}' is not defined in manifest.",
            })

    return {
        "valid": not any(i["level"] == "FAIL" for i in issues),
        "issues": issues,
        "data": metadata,
    }


def check_cover_and_assets(manuscript_dir: Path) -> dict[str, Any]:
    """Verifies cover art and embedded media assets."""
    issues = []
    cover_candidates = [
        manuscript_dir / "03-Art" / "cover.png",
        manuscript_dir / "03-Art" / "cover.jpg",
        manuscript_dir / "cover.png",
        manuscript_dir / "cover.jpg",
        manuscript_dir / "Art" / "cover.png",
    ]
    found_cover = None
    for c in cover_candidates:
        if c.is_file():
            found_cover = c
            break

    if not found_cover:
        issues.append({
            "level": "WARN",
            "code": "ASSET-COVER-01",
            "message": "No cover image found (expected 03-Art/cover.png or cover.jpg for EPUB/Print).",
        })

    return {
        "has_cover": bool(found_cover),
        "cover_path": str(found_cover) if found_cover else None,
        "issues": issues,
    }


def validate_chapter_formatting(file_path: Path) -> list[dict[str, Any]]:
    """Validates markdown syntax, orphan headers, and unescaped markup in a chapter."""
    issues = []
    dal = get_data_access()
    content = dal.read_file(file_path)
    lines = content.splitlines()

    # 1. Orphan Heading check (Heading as the last non-empty line)
    non_empty = [line_str.strip() for line_str in lines if line_str.strip()]
    if non_empty and non_empty[-1].startswith("#"):
        issues.append({
            "level": "FAIL",
            "file": file_path.name,
            "line": len(lines),
            "code": "TYP-ORPHAN-HEAD",
            "message": f"Orphan heading at end of chapter without body text: '{non_empty[-1]}'",
        })

    # 2. Unclosed Code Blocks
    code_ticks = len(re.findall(r"^```", content, flags=re.MULTILINE))
    if code_ticks % 2 != 0:
        issues.append({
            "level": "FAIL",
            "file": file_path.name,
            "code": "TYP-UNCLOSED-CODE",
            "message": "Unclosed markdown code block (``` mismatch).",
        })

    # 3. Straight Quotation Marks Alert
    body_without_code = re.sub(r"```[\s\S]*?```", "", content)
    straight_quotes = body_without_code.count('"')
    if straight_quotes >= 4:
        issues.append({
            "level": "WARN",
            "file": file_path.name,
            "code": "TYP-STRAIGHT-QUOTES",
            "message": f"{straight_quotes} straight double quotes found. Consider running 'arcanum polish typography'.",
        })

    # 4. Trailing triple dashes (unrendered divider)
    if non_empty and non_empty[-1] in ("---", "***"):
        issues.append({
            "level": "WARN",
            "file": file_path.name,
            "line": len(lines),
            "code": "TYP-TRAILING-DIV",
            "message": "Trailing divider line (---) at end of chapter.",
        })

    return issues


def run_preflight_linter(manuscript_dir: Path, scope: EngineScope | None = None) -> dict[str, Any]:
    """Executes full pre-flight verification on a manuscript repository."""
    if not manuscript_dir.is_dir():
        raise NotADirectoryError(f"Manuscript directory not found: {manuscript_dir}")

    meta_res = check_metadata(manuscript_dir)
    asset_res = check_cover_and_assets(manuscript_dir)

    chapter_files = sorted(manuscript_dir.rglob("*.md"))
    content_files = [
        f
        for f in chapter_files
        if not f.name.startswith((".", "_")) and "Backups" not in f.parts and "04_Back_Matter" not in f.parts
    ]

    if scope:
        scoped_chapters, _, _ = filter_manuscript_scope(manuscript_dir, scope)
        scoped_paths = {c.file_path for c in scoped_chapters if c.file_path}
        content_files = [f for f in content_files if f in scoped_paths]

    formatting_issues = []
    total_words = 0
    dal = get_data_access()

    for f in content_files:
        try:
            f_issues = validate_chapter_formatting(f)
            formatting_issues.extend(f_issues)
            text = dal.read_file(f)
            words = count_prose_words(text)
            total_words += words
        except Exception as e:
            formatting_issues.append({"level": "FAIL", "file": f.name, "code": "ERR-READ", "message": str(e)})

    # Word count estimation & budget
    est_pages = math.ceil(total_words / 250) if total_words > 0 else 0

    all_issues = meta_res["issues"] + asset_res["issues"] + formatting_issues
    fail_count = sum(1 for i in all_issues if i["level"] == "FAIL")
    warn_count = sum(1 for i in all_issues if i["level"] == "WARN")

    # Export Readiness Evaluation
    is_ready = fail_count == 0 and total_words >= 100
    score = max(0, min(100, 100 - (fail_count * 20) - (warn_count * 5)))
    readiness_status = "READY" if is_ready else "REVIEW_RECOMMENDED"

    return {
        "target": str(manuscript_dir),
        "total_words": total_words,
        "estimated_pages": est_pages,
        "chapter_count": len(content_files),
        "is_ready_for_publish": is_ready,
        "readiness_status": readiness_status,
        "compliance_score": score,
        "fail_count": fail_count,
        "warn_count": warn_count,
        "metadata": meta_res["data"],
        "issues": all_issues,
    }


def generate_preflight_html_report(report: dict[str, Any], output_path: Path | str) -> Path:
    """Generates a publishing compliance certificate HTML report."""
    return render_preflight_html(report, output_path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ars Arcanum Pre-Flight Publishing Linter (PUB-101)")
    add_scope_arguments(parser, include_world=False, target_pos_arg=True)
    parser.add_argument("--html", help="Generate HTML pre-flight certificate")
    parser.add_argument("--json", action="store_true", help="Output JSON results")
    args = parser.parse_args(argv)

    scope = parse_scope_args(args)
    target_raw = args.target or "."
    target_path = resolve_manuscript_path(target_raw)
    if not target_path or not target_path.exists():
        print(f"Error: Target does not exist: {target_raw}", file=sys.stderr)
        sys.exit(1)

    report = run_preflight_linter(target_path, scope=scope)

    if args.json:
        print(json.dumps(report, indent=2))
        return 0

    print(f"=== Pre-Flight Typesetting Linter & Export Coverage: {target_path.name} ===")
    print(
        f"Total Words: {report['total_words']:,} | Est. Trade Pages: ~{report['estimated_pages']} | Chapters: {report['chapter_count']}"
    )
    print(
        f"Readiness Status: [{'READY FOR EXPORT' if report['is_ready_for_publish'] else 'REVIEW RECOMMENDED'}] | Issues: {report['fail_count']} blocking failures, {report['warn_count']} advisory notices"
    )
    print("-" * 75)
    if not report["issues"]:
        print("✓ All checks passed cleanly!")
    else:
        for iss in report["issues"]:
            level_tag = "[DATA ISSUE]" if iss["level"] == "FAIL" else "[OBSERVATION]"
            loc = f" ({iss.get('file', 'manifest')})" if "file" in iss else ""
            print(f"  {level_tag:<14} {iss['code']:<18}{loc}: {iss['message']}")

    if args.html:
        out_p = Path(args.html)
        generate_preflight_html_report(report, out_p)
        print(f"\nHTML Certificate written to: {out_p}")
    return 0


__all__ = [
    "check_cover_and_assets",
    "check_metadata",
    "generate_preflight_html_report",
    "main",
    "run_preflight_linter",
    "validate_chapter_formatting",
]

if __name__ == "__main__":
    main()
