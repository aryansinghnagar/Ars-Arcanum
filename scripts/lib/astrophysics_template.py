#!/usr/bin/env python3
"""
Ars Arcanum Astrophysics HTML/Markdown Presentation Templates
=============================================================
scripts/lib/astrophysics_template.py

Generates standalone, CSP-compliant offline HTML and Markdown reports
for astrophysics simulations, orbital mechanics, and planetary dossiers.
"""

from __future__ import annotations

import html
from pathlib import Path
from typing import Any

try:
    from lib._bootstrap import atomic_write
except ImportError:
    from _bootstrap import atomic_write  # type: ignore[no-redef]


def generate_dossier_html_report(title: str, dossier: dict[str, Any], output_file: Path) -> None:
    """Generates an offline HTML report for a planetary dossier."""
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)} — Star System Dossier</title>
<style>
  :root {{ --bg: #0d1117; --surface: #161b22; --border: #30363d; --text: #c9d1d9; --accent: #58a6ff; --warning: #d29922; }}
  body {{ background-color: var(--bg); color: var(--text); font-family: sans-serif; padding: 24px; }}
  .container {{ max-width: 900px; margin: 0 auto; }}
  .card {{ background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 20px; margin-bottom: 20px; }}
  h1, h2 {{ color: var(--accent); }}
  .warning {{ color: var(--warning); font-weight: bold; }}
</style>
</head>
<body>
<div class="container">
  <h1>🌌 {html.escape(title)}</h1>
  <div class="card">
    <h2>Dossier Overview</h2>
    <p>Planet Type: <strong>{html.escape(str(dossier.get('planet_type', '')))}</strong></p>
    <p>Surface Gravity: {dossier.get('habitability_metrics', {}).get('surface_gravity_g', 0.0):.2f} g</p>
    <p>Surface Temp: {dossier.get('climate_insolation', {}).get('surface_temp_c', 0.0)} °C</p>
  </div>
  <div class="card">
    <h2>Scientific Plausibility Warnings</h2>
    <ul>
"""
    for w in dossier.get("scientific_plausibility_warnings", []):
        html_content += f"      <li class='warning'>{html.escape(str(w))}</li>\n"
    html_content += """    </ul>
  </div>
</div>
</body>
</html>
"""
    atomic_write(output_file, html_content)


def generate_dossier_markdown_report(title: str, dossier: dict[str, Any], output_file: Path) -> None:
    """Generates a Markdown report for a planetary dossier."""
    md = f"# {title} - Star System Dossier\n\n"
    md += f"**Planet Type**: {dossier.get('planet_type', '')}\n"
    md += f"**Surface Gravity**: {dossier.get('habitability_metrics', {}).get('surface_gravity_g', 0.0):.2f} g\n"
    md += f"**Surface Temp**: {dossier.get('climate_insolation', {}).get('surface_temp_c', 0.0)} °C\n\n"
    md += "## Scientific Plausibility Warnings\n"
    for w in dossier.get("scientific_plausibility_warnings", []):
        md += f"- {w}\n"
    atomic_write(output_file, md)


def generate_astrophysics_html_report(title: str, results: dict[str, Any], output_file: Path) -> None:
    """Generates an interactive standalone HTML report."""
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)} — Ars Arcanum Astrophysics Report</title>
<style>
  :root {{
    --bg: #0d1117;
    --surface: #161b22;
    --border: #30363d;
    --text: #c9d1d9;
    --accent: #58a6ff;
    --success: #3fb950;
    --warning: #d29922;
    --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  }}
  body {{
    background-color: var(--bg);
    color: var(--text);
    font-family: var(--font);
    line-height: 1.6;
    margin: 0;
    padding: 24px;
  }}
  .container {{
    max-width: 900px;
    margin: 0 auto;
  }}
  header {{
    border-bottom: 1px solid var(--border);
    padding-bottom: 16px;
    margin-bottom: 24px;
  }}
  h1 {{ color: var(--accent); margin: 0 0 8px 0; }}
  .badge {{
    background: #1f6feb22;
    color: var(--accent);
    border: 1px solid var(--accent);
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 12px;
  }}
  .card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
  }}
  h2 {{ margin-top: 0; color: #f0f6fc; font-size: 18px; border-bottom: 1px solid var(--border); padding-bottom: 8px; }}
  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0;
  }}
  th, td {{
    padding: 10px 12px;
    text-align: left;
    border-bottom: 1px solid var(--border);
  }}
  th {{ color: #8b949e; font-weight: 600; width: 40%; }}
  td {{ color: #f0f6fc; font-family: ui-monospace, SFMono-Regular, Consolas, monospace; }}
  .val-highlight {{ color: var(--success); font-weight: bold; }}
  footer {{
    text-align: center;
    font-size: 12px;
    color: #8b949e;
    margin-top: 40px;
    border-top: 1px solid var(--border);
    padding-top: 16px;
  }}
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>🌌 {html.escape(title)}</h1>
    <span class="badge">Ars Arcanum Relativistic & Astrophysics Engine</span>
  </header>
"""
    for section_title, data in results.items():
        html_content += f"""  <div class="card">\n    <h2>{html.escape(section_title)}</h2>\n    <table>\n"""
        if isinstance(data, dict):
            for k, v in data.items():
                v_str = ", ".join(f"{sub_k}: {sub_v}" for sub_k, sub_v in v.items()) if isinstance(v, dict) else str(v)
                html_content += f"""      <tr><th>{html.escape(k.replace('_', ' ').title())}</th><td>{html.escape(v_str)}</td></tr>\n"""
        html_content += """    </table>\n  </div>\n"""

    html_content += """
  <footer>
    Generated by Ars Arcanum • 100% Offline Speculative Authoring Suite
  </footer>
</div>
</body>
</html>
"""
    atomic_write(output_file, html_content)
