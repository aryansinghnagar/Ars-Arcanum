#!/usr/bin/env python3
"""
Ars Arcanum Static Codex HTML Template (scripts/lib/codex_export_template.py)
=============================================================================
Self-contained, offline HTML5 visualizer and static wiki encyclopedia for World Bibles.
Enforces strict Content Security Policy (default-src 'none') and offline search index.
"""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

try:
    from lib._bootstrap import atomic_write
except ImportError:
    from _bootstrap import atomic_write


def render_codex_html(
    categories: dict[str, list[dict[str, Any]]],
    world_name: str,
    output_path: Path | str,
) -> Path:
    """Renders a self-contained offline interactive World Wiki Codex."""
    out_path = Path(output_path)
    total_articles = sum(len(items) for items in categories.values())

    sidebar_links = []
    entries_html = []
    search_index = []

    for tax, items in sorted(categories.items()):
        if not items:
            continue
        sidebar_links.append(f'<div class="tax-header">{html.escape(tax)} ({len(items)})</div>')
        for item in sorted(items, key=lambda x: x["title"]):
            clean_id = item["clean_id"]
            title = item["title"]
            sidebar_links.append(
                f'<a href="#{clean_id}" class="nav-link" onclick="showArticle(\'{clean_id}\')">{html.escape(title)}</a>'
            )

            # Build infobox rows
            infobox_rows = []
            for k, v in sorted(item.get("frontmatter", {}).items()):
                if k not in ("title", "type", "tax") and str(v).strip():
                    infobox_rows.append(
                        f"<tr><th>{html.escape(k.title())}</th><td>{html.escape(str(v))}</td></tr>"
                    )

            infobox_html = ""
            if infobox_rows:
                infobox_html = f"""
                <table class="infobox">
                  <thead><tr><th colspan="2" class="infobox-title">{html.escape(title)}</th></tr></thead>
                  <tbody>{''.join(infobox_rows)}</tbody>
                </table>
                """

            entries_html.append(f"""
            <article id="{clean_id}" class="codex-article" style="display:none;">
              <div class="article-header">
                <span class="tax-badge">{html.escape(tax)}</span>
                <h1>{html.escape(title)}</h1>
              </div>
              {infobox_html}
              <div class="article-body">
                {item.get('html_content', '')}
              </div>
            </article>
            """)

            search_index.append({
                "id": clean_id,
                "title": title,
                "tax": tax,
                "text": item.get("raw_body", "")[:300],
            })

    search_json = json.dumps(search_index).replace("</", "<\\/")

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ars Arcanum — {html.escape(world_name)} Codex</title>
<style>
  :root {{
    --bg: #0f172a; --panel: #1e293b; --border: #334155;
    --text: #f8fafc; --muted: #94a3b8; --accent: #38bdf8;
    --link: #60a5fa; --infobox-bg: #1e293b;
  }}
  body[data-theme="light"] {{
    --bg: #f8fafc; --panel: #ffffff; --border: #cbd5e1;
    --text: #0f172a; --muted: #64748b; --accent: #0284c7;
    --link: #2563eb; --infobox-bg: #f1f5f9;
  }}
  body[data-theme="sepia"] {{
    --bg: #f4ecd8; --panel: #faf4e6; --border: #dcd0ba;
    --text: #3c2f1e; --muted: #7c6f5a; --accent: #b45309;
    --link: #92400e; --infobox-bg: #eee5d0;
  }}
  body {{ font-family: system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--text); margin: 0; display: flex; height: 100vh; overflow: hidden; }}
  #sidebar {{ width: 320px; background: var(--panel); border-right: 1px solid var(--border); display: flex; flex-direction: column; }}
  .sidebar-header {{ padding: 1.25rem; border-bottom: 1px solid var(--border); }}
  .sidebar-header h2 {{ margin: 0; color: var(--accent); font-size: 1.25rem; }}
  .search-input {{ width: 100%; box-sizing: border-box; padding: 0.6rem; margin-top: 0.75rem; background: var(--bg); border: 1px solid var(--border); border-radius: 6px; color: var(--text); }}
  .nav-container {{ overflow-y: auto; flex: 1; padding: 0.75rem; }}
  .tax-header {{ font-size: 0.75rem; text-transform: uppercase; color: var(--muted); font-weight: 700; margin: 1rem 0 0.25rem 0.5rem; }}
  .nav-link {{ display: block; padding: 0.4rem 0.5rem; color: var(--text); text-decoration: none; border-radius: 4px; font-size: 0.875rem; }}
  .nav-link:hover, .nav-link.active {{ background: var(--bg); color: var(--accent); }}
  #main {{ flex: 1; overflow-y: auto; padding: 2.5rem; }}
  .theme-toggle {{ position: fixed; top: 1rem; right: 1.5rem; display: flex; gap: 0.5rem; z-index: 10; }}
  .btn-theme {{ background: var(--panel); border: 1px solid var(--border); color: var(--text); padding: 0.4rem 0.75rem; border-radius: 6px; cursor: pointer; font-size: 0.8rem; }}
  .tax-badge {{ background: #334155; color: var(--accent); padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; }}
  .infobox {{ float: right; margin: 0 0 1.5rem 1.5rem; background: var(--infobox-bg); border: 1px solid var(--border); border-radius: 8px; width: 280px; border-collapse: collapse; font-size: 0.85rem; }}
  .infobox-title {{ background: var(--border); padding: 0.5rem; font-size: 1rem; text-align: center; color: var(--accent); }}
  .infobox th, .infobox td {{ padding: 0.4rem 0.6rem; text-align: left; border-bottom: 1px solid var(--border); }}
  .wikilink {{ color: var(--link); text-decoration: underline; }}
  .home-splash {{ max-width: 700px; margin: 3rem auto; text-align: center; }}
</style>
</head>
<body>

<div id="sidebar">
  <div class="sidebar-header">
    <h2>📖 {html.escape(world_name)} Codex</h2>
    <p style="color:var(--muted); font-size:0.8rem; margin:4px 0 0 0;">{total_articles} Articles Indexed</p>
    <input type="text" id="search" class="search-input" placeholder="Search world lore..." oninput="doSearch()">
  </div>
  <div class="nav-container" id="navLinks">
    {''.join(sidebar_links)}
  </div>
</div>

<main id="main">
  <div class="theme-toggle">
    <button class="btn-theme" onclick="setTheme('dark')">🌙 Dark</button>
    <button class="btn-theme" onclick="setTheme('light')">☀️ Light</button>
    <button class="btn-theme" onclick="setTheme('sepia')">📜 Sepia</button>
  </div>

  <div id="homeView" class="home-splash">
    <h1 style="color:var(--accent); font-size:2.5rem; margin-bottom:0.5rem;">{html.escape(world_name)}</h1>
    <p style="color:var(--muted); font-size:1.1rem;">A sovereign, static encyclopedia of lore, history, factions, and characters.</p>
    <p style="color:var(--muted);">Select an entry from the sidebar navigation or use search to explore.</p>
  </div>

  {''.join(entries_html)}
</main>

<script>
function escapeHtml(str) {{
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}}

const index = {search_json};
let originalNavHtml = '';

function setTheme(theme) {{
  document.body.setAttribute('data-theme', theme);
}}

function showArticle(id) {{
  document.getElementById('homeView').style.display = 'none';
  document.querySelectorAll('.codex-article').forEach(a => a.style.display = 'none');
  const target = document.getElementById(id);
  if (target) {{
    target.style.display = 'block';
    if (window.location.hash.replace('#', '') !== id) {{
      window.location.hash = id;
    }}
  }}
}}

function doSearch() {{
  const q = document.getElementById('search').value.toLowerCase().trim();
  const nav = document.getElementById('navLinks');
  if (!originalNavHtml) originalNavHtml = nav.innerHTML;
  if (!q) {{
    nav.innerHTML = originalNavHtml;
    return;
  }}
  const matches = index.filter(item => item.title.toLowerCase().includes(q) || item.text.toLowerCase().includes(q));
  nav.innerHTML = '<div class="tax-header">Search Results (' + matches.length + ')</div>';
  matches.forEach(m => {{
    const a = document.createElement('a');
    a.className = 'nav-link';
    a.href = '#' + encodeURIComponent(m.id);
    a.innerHTML = `<strong>${{escapeHtml(m.title)}}</strong> <small style="color:var(--muted);">(${{escapeHtml(m.tax)}})</small>`;
    a.onclick = () => showArticle(m.id);
    nav.appendChild(a);
  }});
}}

function handleHash() {{
  const hash = window.location.hash.replace('#', '');
  if (hash) showArticle(hash);
}}

window.addEventListener('load', () => {{
  originalNavHtml = document.getElementById('navLinks').innerHTML;
  handleHash();
}});
window.addEventListener('hashchange', handleHash);
</script>
</body>
</html>
"""
    atomic_write(out_path, html_content)
    return out_path


__all__ = ["render_codex_html"]
