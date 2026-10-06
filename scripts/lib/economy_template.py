#!/usr/bin/env python3
"""
Ars Arcanum Economy & Technology Era HTML Report Template
(scripts/lib/economy_template.py)
================================================================================
Generates offline-first standalone HTML report with strict Content Security Policy
for Economic audit findings, commodity baskets, and tech era validations.
"""

from __future__ import annotations

import html
from pathlib import Path
from typing import Any

try:
    from lib._bootstrap import atomic_write
except ImportError:
    try:
        from _bootstrap import atomic_write
    except ImportError:
        def atomic_write(path: Path, content: str, encoding: str = "utf-8") -> None:
            import os as _os
            import tempfile as _tf
            p = Path(path).resolve()
            p.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp = _tf.mkstemp(dir=p.parent, prefix=f".{p.name}.", suffix=".tmp")
            try:
                with _os.fdopen(fd, "w", encoding=encoding, newline="") as f:
                    f.write(content)
                    f.flush()
                    _os.fsync(f.fileno())
                _os.replace(tmp, p)
            except BaseException:
                try:
                    Path(tmp).unlink(missing_ok=True)
                except OSError:
                    pass
                raise


def generate_economy_html_report(audit_data: dict[str, Any], output_path: Path) -> None:
    """Generates standalone HTML report for Economic audit and Tech Era check."""
    economies = audit_data.get("economies", {})
    findings = audit_data.get("findings", [])
    world_name = audit_data.get("world", "World Bible")

    econ_cards = []
    for en, e in economies.items():
        curr_str = ", ".join([f"{k} (x{v})" for k, v in e.get("currencies", {}).items()])
        basket_str = ", ".join([f"{k}: {v}" for k, v in e.get("commodity_basket", {}).items()])
        econ_cards.append(f"""
        <div class="card">
            <h3>🏛️ {html.escape(en)} ({html.escape(e.get('tech_era', 'medieval'))})</h3>
            <p><strong>Base Currency:</strong> {html.escape(e.get('base_currency', ''))}</p>
            <p><strong>Currencies:</strong> {html.escape(curr_str)}</p>
            <p><strong>Basket Prices:</strong> <small>{html.escape(basket_str)}</small></p>
        </div>
        """)

    findings_cards = []
    for fd in findings:
        badge_cls = "badge-error" if fd.get("severity") == "ERROR" else "badge-warning"
        findings_cards.append(f"""
        <div class="card finding-card">
            <span class="badge {badge_cls}">{html.escape(fd.get('severity', 'WARNING'))}</span>
            <strong>{html.escape(fd.get('id', ''))}</strong>: {html.escape(fd.get('message', ''))}
            <div style="font-size: 0.85em; color: #94a3b8; margin-top: 4px;">File: {html.escape(fd.get('file', ''))}:{fd.get('line', '')}</div>
        </div>
        """)

    findings_html = "".join(findings_cards) if findings_cards else "<div style='color: #4ade80;'>✓ No pricing anomalies or technological anachronisms detected.</div>"

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ars Arcanum — Economy & Anachronism Matrix ({html.escape(world_name)})</title>
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
  .badge {{
    display: inline-block;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: bold;
    text-transform: uppercase;
  }}
  .badge-warning {{ background: #d97706; color: #fff; }}
  .badge-error {{ background: #b91c1c; color: #fff; }}
  .finding-card {{ margin-bottom: 0.75rem; }}
</style>
</head>
<body>
<div class="container">
  <h1>💰 Ars Arcanum Economy, PPP & Anachronism Matrix</h1>
  <p>World Lore Vault: <strong>{html.escape(world_name)}</strong></p>

  <div class="card">
    <h2>Audit Findings ({len(findings)})</h2>
    {findings_html}
  </div>

  <h2>Registered In-World Economies</h2>
  {"".join(econ_cards)}
</div>
</body>
</html>
"""
    atomic_write(output_path, html_content)
