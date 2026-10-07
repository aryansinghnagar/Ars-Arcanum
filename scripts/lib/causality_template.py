#!/usr/bin/env python3
"""
Ars Arcanum Causal DAG Presentation & SVG Report Template
(scripts/lib/causality_template.py)
================================================================================
Presentation layer for narrative causal graphs, timeline branches, and loop visualizers.
Renders clean, offline HTML5 with strict Content Security Policy and SVG graph diagrams.

Zero external dependencies; 100% offline air-gapped privacy.
"""

from __future__ import annotations

import html
from pathlib import Path
from typing import Any

try:
    from lib._bootstrap import atomic_write
except ImportError:
    from _bootstrap import atomic_write


def generate_causal_svg_graph(events: dict[str, Any], timelines: dict[str, Any]) -> str:
    """Generates pure offline SVG diagram showing timeline branches, causal vectors, and paradox loops."""
    if not events:
        return "<svg viewBox='0 0 600 120' style='width:100%;height:auto;'><text x='20' y='60' fill='#94a3b8'>No causal events registered</text></svg>"

    timeline_list = list(timelines.keys())
    if "prime" not in timeline_list:
        timeline_list.insert(0, "prime")

    y_spacing = 90
    x_spacing = 160
    svg_width = max(800, len(events) * x_spacing + 200)
    svg_height = max(350, len(timeline_list) * y_spacing + 150)

    tl_y = {tl: 80 + idx * y_spacing for idx, tl in enumerate(timeline_list)}

    event_coords = {}
    track_counts: dict[str, int] = {}
    for eid, ev in events.items():
        tl = ev.get("timeline", "prime")
        if tl not in tl_y:
            tl = "prime"
        c = track_counts.get(tl, 0)
        track_counts[tl] = c + 1
        x = 100 + c * x_spacing
        y = tl_y[tl]
        event_coords[eid] = (x, y)

    svg_elements = [
        f'<svg viewBox="0 0 {svg_width} {svg_height}" style="width:100%;height:auto;background:#0b1120;border-radius:8px;border:1px solid #334155;" xmlns="http://www.w3.org/2000/svg">',
        '<defs>',
        '  <marker id="arrow" viewBox="0 0 10 10" refX="22" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#38bdf8"/></marker>',
        '  <marker id="arrow-loop" viewBox="0 0 10 10" refX="22" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#f43f5e"/></marker>',
        '  <marker id="arrow-branch" viewBox="0 0 10 10" refX="22" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#fbbf24"/></marker>',
        '</defs>',
    ]

    for tl, y in tl_y.items():
        svg_elements.append(f'<line x1="40" y1="{y}" x2="{svg_width - 40}" y2="{y}" stroke="#1e293b" stroke-width="3" stroke-dasharray="4,4"/>')
        svg_elements.append(f'<text x="50" y="{y - 12}" fill="#38bdf8" font-size="12" font-family="monospace" font-weight="bold">TIMELINE: {html.escape(tl.upper())}</text>')

    for eid, ev in events.items():
        x1, y1 = event_coords.get(eid, (100, 80))
        for tgt_id in ev.get("causes", []):
            if tgt_id in event_coords:
                x2, y2 = event_coords[tgt_id]
                is_loop = (x2 <= x1)
                marker = "url(#arrow-loop)" if is_loop else ("url(#arrow-branch)" if y1 != y2 else "url(#arrow)")
                color = "#f43f5e" if is_loop else ("#fbbf24" if y1 != y2 else "#38bdf8")
                path_style = "stroke-dasharray: 5,5;" if is_loop else ""
                mid_x = (x1 + x2) / 2
                mid_y = min(y1, y2) - 40 if is_loop else (y1 + y2) / 2
                svg_elements.append(f'<path d="M {x1} {y1} Q {mid_x} {mid_y} {x2} {y2}" fill="none" stroke="{color}" stroke-width="2" marker-end="{marker}" style="{path_style}"/>')

    for eid, ev in events.items():
        x, y = event_coords.get(eid, (100, 80))
        has_paradox = bool(ev.get("paradox_type"))
        node_color = "#f43f5e" if has_paradox else "#0284c7"
        stroke_color = "#fbbf24" if has_paradox else "#38bdf8"

        name_trunc = ev['name'][:16] + ("..." if len(ev['name']) > 16 else "")
        svg_elements.append('<g class="node-group" style="cursor:pointer;">')
        svg_elements.append(f'  <circle cx="{x}" cy="{y}" r="14" fill="{node_color}" stroke="{stroke_color}" stroke-width="2"/>')
        svg_elements.append(f'  <text x="{x}" y="{y + 28}" text-anchor="middle" fill="#f8fafc" font-size="11" font-weight="600" font-family="sans-serif">{html.escape(name_trunc)}</text>')
        if ev.get("time_coord"):
            svg_elements.append(f'  <text x="{x}" y="{y + 42}" text-anchor="middle" fill="#94a3b8" font-size="9" font-family="monospace">@{html.escape(str(ev["time_coord"]))}</text>')
        svg_elements.append('</g>')

    svg_elements.append('</svg>')
    return "\n".join(svg_elements)


def generate_causality_html_report(audit_data: dict[str, Any], output_path: Path) -> str:
    """Generates standalone interactive HTML report for Causal DAGs and timelines."""
    events = audit_data.get("events", {})
    timelines = audit_data.get("timelines", {})
    findings = audit_data.get("findings", [])
    world_name = audit_data.get("world", "World Bible")
    svg_diagram = generate_causal_svg_graph(events, timelines)

    findings_cards = []
    for fd in findings:
        badge_cls = "badge-error" if fd.get("severity") == "ERROR" else "badge-warning"
        findings_cards.append(f"""
        <div class="card finding-card">
            <span class="badge {badge_cls}">{html.escape(fd.get('severity', 'WARNING'))}</span>
            <strong>{html.escape(fd.get('id', ''))}</strong>: {html.escape(fd.get('message', ''))}
            <div style="font-size: 0.85em; color: #94a3b8; margin-top: 4px;">File: {html.escape(fd.get('file', ''))}</div>
        </div>
        """)

    findings_html = "".join(findings_cards) if findings_cards else "<div style='color: #4ade80;'>✓ All causal sequences and closed loops are self-consistent.</div>"

    events_rows = []
    for eid, e in events.items():
        events_rows.append(f"""
        <tr>
            <td><strong>{html.escape(e['name'])}</strong><br/><small>{html.escape(eid)}</small></td>
            <td><span class="badge badge-timeline">{html.escape(e['timeline'])}</span></td>
            <td>{html.escape(e['time_coord'] or 'N/A')}</td>
            <td>{html.escape(', '.join(e['causal_origins']) or '—')}</td>
            <td>{html.escape(', '.join(e['causes']) or '—')}</td>
            <td>{html.escape(e['paradox_type'] or 'Linear')}</td>
        </tr>
        """)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ars Arcanum — Causal DAG & Multiverse Engine ({html.escape(world_name)})</title>
<style>
  :root {{
    --bg: #0f172a;
    --card-bg: #1e293b;
    --border: #334155;
    --text: #f8fafc;
    --accent: #38bdf8;
    --danger: #f43f5e;
    --warning: #fbbf24;
    --success: #34d399;
  }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background-color: var(--bg);
    color: var(--text);
    margin: 0;
    padding: 2rem;
  }}
  .container {{ max-width: 1200px; margin: 0 auto; }}
  h1, h2, h3 {{ color: var(--accent); }}
  .card {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 1rem;
  }}
  th, td {{
    padding: 0.75rem;
    text-align: left;
    border-bottom: 1px solid var(--border);
  }}
  th {{ background: #0f172a; color: var(--accent); }}
  .badge {{
    display: inline-block;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: bold;
    text-transform: uppercase;
  }}
  .badge-timeline {{ background: #0284c7; color: #fff; }}
  .badge-warning {{ background: #d97706; color: #fff; }}
  .badge-error {{ background: #b91c1c; color: #fff; }}
  .finding-card {{ margin-bottom: 0.75rem; }}
</style>
</head>
<body>
<div class="container">
  <h1>⏳ Ars Arcanum Causal DAG & Multiverse Engine</h1>
  <p>World: <strong>{html.escape(world_name)}</strong> | Total Events: <strong>{len(events)}</strong> | Timelines: <strong>{len(timelines)}</strong></p>

  <div class="card">
    <h2>⚡ Visual Causal Branch Graph & Paradox Loops</h2>
    {svg_diagram}
  </div>

  <div class="card">
    <h2>Causal Consistency Diagnostics ({len(findings)})</h2>
    {findings_html}
  </div>

  <div class="card">
    <h2>Event Causal Sequence Roster</h2>
    <table>
      <thead>
        <tr>
          <th>Event</th>
          <th>Timeline</th>
          <th>Coord</th>
          <th>Prerequisites</th>
          <th>Causes</th>
          <th>Paradox Type</th>
        </tr>
      </thead>
      <tbody>
        {"".join(events_rows)}
      </tbody>
    </table>
  </div>
</div>
</body>
</html>
"""
    if output_path:
        atomic_write(output_path, html_content)
    return html_content


__all__ = ["generate_causal_svg_graph", "generate_causality_html_report"]
