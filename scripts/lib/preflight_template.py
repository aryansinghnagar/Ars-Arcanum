#!/usr/bin/env python3
"""
Ars Arcanum Pre-Flight Certificate HTML Template (scripts/lib/preflight_template.py)
===================================================================================
Self-contained, offline HTML5 visualizer and certificate report for manuscript pre-flight checks.
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


def render_preflight_html(report: dict[str, Any], output_path: Path | str) -> Path:
    """Generates an offline HTML5 Pre-Flight Certificate & Compliance Report."""
    out_path = Path(output_path)
    issues = report.get("issues", [])
    issue_rows = []

    for iss in issues:
        badge = (
            "<span style='background:#ef4444;color:#fff;padding:2px 6px;border-radius:4px;font-size:0.75rem;font-weight:700;'>FAIL</span>"
            if iss["level"] == "FAIL"
            else "<span style='background:#f59e0b;color:#000;padding:2px 6px;border-radius:4px;font-size:0.75rem;font-weight:700;'>WARN</span>"
        )
        loc = f"{iss.get('file', 'manifest')}" + (f":{iss['line']}" if "line" in iss else "")
        row = f"""
        <tr>
          <td>{badge}</td>
          <td><code>{html.escape(iss['code'])}</code></td>
          <td>{html.escape(loc)}</td>
          <td>{html.escape(iss['message'])}</td>
        </tr>
        """
        issue_rows.append(row)

    fail_count = report.get("fail_count", 0)
    warn_count = report.get("warn_count", 0)
    fail_color = "var(--danger)" if fail_count > 0 else "var(--success)"
    warn_color = "var(--warn)" if warn_count > 0 else "var(--muted)"

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ars Arcanum — Pre-Flight Export Coverage Map</title>
<style>
  :root {{
    --bg: #0f172a; --panel: #1e293b; --border: #334155;
    --text: #f8fafc; --muted: #94a3b8; --accent: #38bdf8;
    --warn: #f59e0b; --danger: #ef4444; --success: #10b981;
  }}
  body {{ font-family: system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 2rem; }}
  .container {{ max-width: 950px; margin: 0 auto; }}
  .header {{ border-bottom: 1px solid var(--border); padding-bottom: 1rem; margin-bottom: 2rem; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
  .card {{ background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 1.25rem; }}
  .card h3 {{ margin-top: 0; color: var(--muted); font-size: 0.875rem; text-transform: uppercase; }}
  .metric {{ font-size: 2rem; font-weight: 700; color: var(--accent); }}
  .status-box {{ padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem; text-align: center; }}
  .status-pass {{ background: #064e3b; border: 1px solid #059669; color: #a7f3d0; }}
  .status-fail {{ background: #1e293b; border: 1px solid var(--border); color: var(--text); }}
  .table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
  .table th, .table td {{ text-align: left; padding: 0.75rem 0.5rem; border-bottom: 1px solid var(--border); }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>✈️ Pre-Flight Typesetting & Export Coverage Map</h1>
    <p style="color: var(--muted);">Target: {html.escape(str(report.get('target') or report.get('title') or report.get('manuscript') or 'Manuscript'))} | Chapters: {report.get('chapter_count', 0)}</p>
  </div>

  <div class="grid">
    <div class="card">
      <h3>Total Words</h3>
      <div class="metric">{report.get('total_words', 0):,}</div>
      <p style="color: var(--muted); margin: 0.25rem 0 0 0;">Across {report.get('chapter_count', 0)} chapters</p>
    </div>
    <div class="card">
      <h3>Estimated Pages</h3>
      <div class="metric">~{report.get('estimated_pages', 0)}</div>
      <p style="color: var(--muted); margin: 0.25rem 0 0 0;">@ 250 w/page Trade 6x9</p>
    </div>
    <div class="card">
      <h3>Structural Fails</h3>
      <div class="metric" style="color: {fail_color};">{fail_count}</div>
      <p style="color: var(--muted); margin: 0.25rem 0 0 0;">Blocking format issues</p>
    </div>
    <div class="card">
      <h3>Advisory Notices</h3>
      <div class="metric" style="color: {warn_color};">{warn_count}</div>
      <p style="color: var(--muted); margin: 0.25rem 0 0 0;">Author review items</p>
    </div>
  </div>

  <h2>📋 Export Coverage & Checklist</h2>
  <table class="table">
    <thead><tr><th>Category</th><th>Rule Code</th><th>Location</th><th>Item Description</th></tr></thead>
    <tbody>
      {''.join(issue_rows) or '<tr><td colspan="4" style="color:var(--success);">✓ All technical export checks verified with zero warnings or errors.</td></tr>'}
    </tbody>
  </table>
</div>
</body>
</html>
"""
    atomic_write(out_path, html_content)
    return out_path


__all__ = ["render_preflight_html"]
