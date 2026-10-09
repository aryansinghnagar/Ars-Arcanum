#!/usr/bin/env python3
"""
Ars Arcanum Portfolio Dashboard & Author Velocity Analytics
(scripts/lib/portfolio.py)
================================================================================
Zero-dependency, offline author portfolio dashboard and catalog analytics engine.

Capabilities (OPS-103):
1. Multi-Manuscript Portfolio Aggregation:
   - Scans ~/Manuscripts/ and ~/Universes/ for novel projects, volumes, and drafts.
   - Calculates total catalog word counts, chapter counts, and volume counts.
2. Lifecycle & Editorial Stage Tracking:
   - Identifies status: Scaffolding, First Draft, Revisions, Pre-Flight, Published.
   - Computes target completion percentages and wordcount milestones.
3. Standalone HTML Portfolio Hub:
   - Interactive dashboard with progress bars, velocity metrics, and project cards.

Zero external dependencies; 100% offline privacy.
"""

import argparse
import datetime
import html
import json
import logging
from pathlib import Path
from typing import Any

try:
    from lib._bootstrap import PROJECT_ROOT, atomic_write, count_prose_words
    from lib.frontmatter import parse_yaml_document
    from lib.scope import add_scope_arguments, parse_scope_args, resolve_manuscript_dir
except ImportError:
    from _bootstrap import PROJECT_ROOT, atomic_write, count_prose_words
    from frontmatter import parse_yaml_document
    from scope import add_scope_arguments, parse_scope_args, resolve_manuscript_dir

logger = logging.getLogger("arcanum.portfolio")


def _resolve_draft_dir(parent_dir: Path, requested_draft: str | None = None) -> Path:
    """Finds the active or requested draft directory in a volume or manuscript directory."""
    draft_dirs = sorted([d for d in parent_dir.glob("Draft-*") if d.is_dir()])
    if not draft_dirs:
        return parent_dir
    if requested_draft:
        match = [d for d in draft_dirs if d.name.lower() == str(requested_draft).lower()]
        if match:
            return match[0]
    return draft_dirs[-1]


def analyze_manuscript_project(ms_dir: Path) -> dict:
    """Analyzes a single manuscript directory for stats, stage, and word counts."""
    manifest_path = ms_dir / "manuscript.yaml"
    meta: dict[str, Any] = {}
    if manifest_path.is_file():
        try:
            raw_meta = parse_yaml_document(manifest_path.read_text(encoding="utf-8", errors="replace"))
            if isinstance(raw_meta, dict):
                meta = {str(k).lower(): v for k, v in raw_meta.items()}
        except Exception:
            meta = {}

    title = meta.get("title", ms_dir.name.replace("_", " "))
    author = meta.get("author", "Author")
    target_words = int(meta.get("target_words", 80000))
    active_draft_name = meta.get("active_draft")

    target_ms_dir = ms_dir / "01-Manuscript" if (ms_dir / "01-Manuscript").is_dir() else ms_dir

    # Chapters and volumes: count only from the active/latest draft per volume/manuscript
    book_dirs = sorted([d for d in target_ms_dir.glob("Book-*") if d.is_dir()])
    volumes = [d.name for d in book_dirs] if book_dirs else ["Book-01"]

    chapter_files: list[Path] = []
    if book_dirs:
        for b in book_dirs:
            search_dir = _resolve_draft_dir(b, active_draft_name)
            for f in sorted(search_dir.rglob("*.md")):
                if (
                    not f.name.startswith((".", "_"))
                    and "Backups" not in f.parts
                    and "04_Back_Matter" not in f.parts
                    and "Back_Matter" not in f.parts
                    and "Front_Matter" not in f.parts
                    and "Exports" not in f.parts
                ):
                    chapter_files.append(f)
    else:
        search_dir = _resolve_draft_dir(target_ms_dir, active_draft_name)
        for f in sorted(search_dir.rglob("*.md")):
            if (
                not f.name.startswith((".", "_"))
                and "Backups" not in f.parts
                and "04_Back_Matter" not in f.parts
                and "Back_Matter" not in f.parts
                and "Front_Matter" not in f.parts
                and "Exports" not in f.parts
            ):
                chapter_files.append(f)

    total_words = 0
    for cf in chapter_files:
        try:
            txt = cf.read_text(encoding="utf-8", errors="replace")
            total_words += count_prose_words(txt)
        except Exception:
            pass

    # Determine stage
    progress_pct = round((total_words / target_words * 100), 1) if target_words > 0 else 0.0
    stage = "Scaffolding"
    if total_words >= target_words:
        stage = "Revisions / Pre-Flight"
    elif total_words >= target_words * 0.5:
        stage = "Drafting (Act II/III)"
    elif total_words > 1000:
        stage = "Drafting (Act I)"

    exports_dir = ms_dir / "Exports"
    has_exports = exports_dir.is_dir() and any(exports_dir.glob("*.pdf"))
    if has_exports and progress_pct >= 90:
        stage = "Publication-Ready"

    return {
        "id": ms_dir.name,
        "title": title,
        "author": author,
        "path": str(ms_dir),
        "volumes": volumes,
        "volume_count": len(volumes),
        "chapter_count": len(chapter_files),
        "word_count": total_words,
        "target_words": target_words,
        "progress_pct": min(100.0, progress_pct),
        "stage": stage,
        "has_exports": has_exports
    }


def scan_portfolio(root_dir: Path | None = None, scope: Any = None) -> dict:
    """Scans all manuscripts in the environment."""
    candidates = []
    if root_dir and root_dir.is_dir():
        candidates.append(root_dir)
    elif scope is not None and getattr(scope, "manuscript", None):
        try:
            ms_str = resolve_manuscript_dir(str(scope.manuscript), scope=scope)
            if ms_str:
                ms_p = Path(ms_str)
                if ms_p.is_dir():
                    candidates.append(ms_p)
        except Exception:
            pass

    if not candidates:
        home = Path.home()
        candidates.extend([
            home / "Manuscripts",
            PROJECT_ROOT / "fixtures",
            PROJECT_ROOT / "templates",
        ])

    manuscript_dirs = []
    for c in candidates:
        if c.is_dir():
            # Check if c itself is directly a manuscript project
            if (c / "manuscript.yaml").is_file() or (c / "Book-01").is_dir() or any(c.glob("*.nwx")):
                manuscript_dirs.append(c)
            else:
                # Look for subdirectories with manuscript.yaml or Book-*
                for sub in sorted(c.iterdir()):
                    if sub.is_dir() and not sub.name.startswith((".", "_")) and ((sub / "manuscript.yaml").is_file() or (sub / "Book-01").is_dir() or any(sub.glob("*.nwx"))):
                        manuscript_dirs.append(sub)

    projects = [analyze_manuscript_project(d) for d in manuscript_dirs]
    total_words = sum(p["word_count"] for p in projects)
    total_chapters = sum(p["chapter_count"] for p in projects)
    total_volumes = sum(p["volume_count"] for p in projects)
    total_target_words = sum(p.get("target_words", 0) for p in projects)
    overall_progress_pct = round((total_words / total_target_words * 100), 1) if total_target_words > 0 else 0.0

    return {
        "scan_time": datetime.datetime.now().isoformat(),
        "total_projects": len(projects),
        "total_words": total_words,
        "total_target_words": total_target_words,
        "overall_progress_pct": min(100.0, overall_progress_pct),
        "total_chapters": total_chapters,
        "total_volumes": total_volumes,
        "projects": projects
    }


def generate_portfolio_html(report: dict, output_path: Path) -> Path:
    """Generates a standalone HTML portfolio hub."""
    projects = report.get("projects", [])
    total_words = report.get("total_words", 0)

    proj_cards = []
    for p in projects:
        card = f"""
        <div style="background:#1e293b;border:1px solid #334155;border-radius:8px;padding:1.5rem;margin-bottom:1rem;">
          <div style="display:flex;justify-content:space-between;align-items:baseline;">
            <h3 style="margin:0;color:#38bdf8;font-size:1.25rem;">{html.escape(p['title'])}</h3>
            <span style="background:#334155;color:#94a3b8;padding:2px 8px;border-radius:4px;font-size:0.75rem;font-weight:700;">{html.escape(p['stage'])}</span>
          </div>
          <p style="color:#94a3b8;font-size:0.875rem;margin:0.5rem 0;">{p['volume_count']} Volumes | {p['chapter_count']} Chapters | {p['word_count']:,} / {p['target_words']:,} words ({p['progress_pct']}%)</p>
          <div style="background:#0f172a;border-radius:6px;height:10px;overflow:hidden;margin-top:0.75rem;">
            <div style="background:#38bdf8;height:100%;width:{p['progress_pct']}%;"></div>
          </div>
        </div>
        """
        proj_cards.append(card)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ars Arcanum — Author Portfolio Hub</title>
<style>
  :root {{
    --bg: #0f172a; --panel: #1e293b; --border: #334155;
    --text: #f8fafc; --muted: #94a3b8; --accent: #38bdf8;
  }}
  body {{ font-family: system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 2rem; }}
  .container {{ max-width: 950px; margin: 0 auto; }}
  .header {{ border-bottom: 1px solid var(--border); padding-bottom: 1rem; margin-bottom: 2rem; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
  .card {{ background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 1.25rem; }}
  .card h3 {{ margin-top: 0; color: var(--muted); font-size: 0.875rem; text-transform: uppercase; }}
  .metric {{ font-size: 2rem; font-weight: 700; color: var(--accent); }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>📚 Author Portfolio & Catalog Dashboard</h1>
    <p style="color: var(--muted);">Unified Authorial Progress & Editorial Pipeline</p>
  </div>

  <div class="grid">
    <div class="card">
      <h3>Active Manuscripts</h3>
      <div class="metric">{report.get('total_projects', 0)}</div>
    </div>
    <div class="card">
      <h3>Total Catalog Words</h3>
      <div class="metric">{total_words:,}</div>
    </div>
    <div class="card">
      <h3>Total Chapters</h3>
      <div class="metric">{report.get('total_chapters', 0)}</div>
    </div>
    <div class="card">
      <h3>Total Volumes</h3>
      <div class="metric">{report.get('total_volumes', 0)}</div>
    </div>
  </div>

  <h2>📖 Manuscript Projects</h2>
  {''.join(proj_cards) or '<p style="color:var(--muted);">No active manuscripts discovered.</p>'}
</div>
</body>
</html>
"""
    atomic_write(output_path, html_content)
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Portfolio Dashboard (OPS-103)")
    parser.add_argument("path", nargs="?", help="Optional root path to scan for manuscripts")
    parser.add_argument("--html", help="Generate HTML portfolio hub to output path")
    parser.add_argument("--json", action="store_true", help="Output JSON results")
    try:
        add_scope_arguments(parser, include_manuscript=False, include_world=False, target_pos_arg=False)
    except NameError:
        pass

    args = parser.parse_args()

    scope = None
    try:
        scope = parse_scope_args(args)
    except NameError:
        pass

    root_p = Path(args.path) if args.path else None
    report = scan_portfolio(root_p, scope=scope)

    if args.json:
        print(json.dumps(report, indent=2))
        return

    print("=== Ars Arcanum Author Portfolio Dashboard ===")
    print(f"Projects: {report['total_projects']} | Catalog Words: {report['total_words']:,} | Chapters: {report['total_chapters']}")
    print("-" * 75)
    for p in report["projects"]:
        print(f"  📖 {p['title']:<24} | {p['stage']:<20} | {p['word_count']:>6,} / {p['target_words']:>6,} w ({p['progress_pct']:>5.1f}%)")

    if args.html:
        out_p = Path(args.html)
        generate_portfolio_html(report, out_p)
        print(f"\nHTML Portfolio Hub written to: {out_p}")


if __name__ == "__main__":
    main()
