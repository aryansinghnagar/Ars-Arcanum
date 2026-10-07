#!/usr/bin/env python3
"""
Ars Arcanum Story Paradigm HTML Report Template
(scripts/lib/structure_template.py)
================================================================================
Presentation layer for narrative structural and paradigm alignment reporting.
Renders clean, offline HTML5 with strict Content Security Policy and WCAG tokens.

Zero external dependencies; 100% offline air-gapped privacy.
"""

from __future__ import annotations

import html
from pathlib import Path

try:
    from lib._bootstrap import atomic_write
except ImportError:
    from _bootstrap import atomic_write


def render_structure_html_page(report: dict) -> str:
    """Renders the HTML report string for story paradigm alignment."""
    beats = report.get("beats", [])
    score = report.get("harmony_score", 0.0)

    beat_rows = []
    for b in beats:
        status_badge = (
            "<span style='background:#064e3b;color:#a7f3d0;padding:2px 8px;border-radius:4px;font-size:0.75rem;'>In Window</span>"
            if b["is_in_window"]
            else f"<span style='background:#1e3a5f;color:#93c5fd;padding:2px 8px;border-radius:4px;font-size:0.75rem;'>Offset ({b['drift_pct']}%)</span>"
        )
        row = f"""
        <tr>
          <td><strong>{html.escape(b['beat_name'])}</strong><br><small style="color:#94a3b8;">{html.escape(b['desc'])}</small></td>
          <td>{int(b['target_pct']*100)}% ({b['target_words']:,} w)</td>
          <td>Ch {b['assigned_chapter']} ({int(b['actual_pct']*100)}%)</td>
          <td>{status_badge}</td>
        </tr>
        """
        beat_rows.append(row)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ars Arcanum — Story Paradigm Alignment Report</title>
<style>
  :root {{
    --bg: #0f172a; --panel: #1e293b; --border: #334155;
    --text: #f8fafc; --muted: #94a3b8; --accent: #38bdf8;
    --warn: #f59e0b; --danger: #ef4444; --success: #10b981;
  }}
  body {{ font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 2rem; }}
  .container {{ max-width: 1000px; margin: 0 auto; }}
  .header {{ border-bottom: 1px solid var(--border); padding-bottom: 1rem; margin-bottom: 2rem; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
  .card {{ background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 1.25rem; }}
  .card h3 {{ margin-top: 0; color: var(--muted); font-size: 0.875rem; text-transform: uppercase; }}
  .metric {{ font-size: 2rem; font-weight: 700; color: var(--accent); }}
  .section {{ background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; }}
  .table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
  .table th, .table td {{ text-align: left; padding: 0.75rem 0.5rem; border-bottom: 1px solid var(--border); }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>📐 Story Paradigm & Structure Alignment (Observational Telemetry)</h1>
    <p style="color: var(--muted);">Model: {html.escape(report.get('paradigm_name', ''))} | Target: {html.escape(report.get('target', ''))}</p>
  </div>

  <div class="grid">
    <div class="card">
      <h3>Milestone Alignment</h3>
      <div class="metric" style="color: {'var(--success)' if score >= 80 else ('var(--warn)' if score >= 60 else 'var(--accent)')};">{score}%</div>
      <p style="color: var(--muted); margin: 0.5rem 0 0 0;">Observational Beat Alignment</p>
    </div>
    <div class="card">
      <h3>Total Word Count</h3>
      <div class="metric">{report.get('total_words', 0):,}</div>
      <p style="color: var(--muted); margin: 0.5rem 0 0 0;">Across {report.get('total_chapters', 0)} chapters</p>
    </div>
    <div class="card">
      <h3>Paradigm Beats</h3>
      <div class="metric">{len(beats)}</div>
      <p style="color: var(--muted); margin: 0.5rem 0 0 0;">Mapped to narrative milestones</p>
    </div>
  </div>

  <div class="section">
    <h2>🎯 Structural Beat Sheet Map</h2>
    <table class="table">
      <thead><tr><th>Story Beat</th><th>Target Pct</th><th>Assigned Position</th><th>Status</th></tr></thead>
      <tbody>
        {''.join(beat_rows)}
      </tbody>
    </table>
  </div>
</div>
</body>
</html>
"""


def generate_structure_html_report(report: dict, output_path: Path) -> Path:
    """Generates an offline HTML visual timeline report for story structure."""
    html_content = render_structure_html_page(report)
    atomic_write(output_path, html_content)
    return output_path


__all__ = ["generate_structure_html_report", "render_structure_html_page"]
