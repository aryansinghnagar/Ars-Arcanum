#!/usr/bin/env python3
"""
Ars Arcanum Portfolio Dashboard HTML Template (scripts/lib/portfolio_template.py)
================================================================================
Self-contained, offline HTML5 visualizer and author dashboard for multi-manuscript catalogs.
Strict Content Security Policy enforced (default-src 'none').
"""

from __future__ import annotations

import html
from pathlib import Path
from typing import Any

try:
    from lib._bootstrap import atomic_write
except ImportError:
    from _bootstrap import atomic_write


def render_portfolio_html(report: dict[str, Any], output_path: Path | str) -> Path:
    """Generates an offline HTML5 Author Portfolio & Catalog Dashboard."""
    out_path = Path(output_path)
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
    atomic_write(out_path, html_content)
    return out_path


__all__ = ["render_portfolio_html"]
