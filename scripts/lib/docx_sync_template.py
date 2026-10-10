#!/usr/bin/env python3
"""
Ars Arcanum Visual DOCX Synchronization & Typesetting Studio
(scripts/lib/docx_sync_template.py)
============================================================
Pure-Python, zero-dependency, 100% offline CSP-compliant interactive HTML5/CSS/JS
authoring studio dashboard for bidirectional Word processor synchronization,
visual redline diff approval, typesetting preset previews, and editorial comments.
"""

from __future__ import annotations

import html
import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger("arcanum.docx_sync_template")

try:
    from lib._bootstrap import atomic_write
    from lib.ui_theme_engine import (
        get_theme_control_center_html,
        get_theme_engine_css,
        get_theme_engine_js,
    )
except ImportError:
    from _bootstrap import atomic_write  # type: ignore[no-redef]
    from ui_theme_engine import (  # type: ignore[no-redef]
        get_theme_control_center_html,
        get_theme_engine_css,
        get_theme_engine_js,
    )

_CSP = (
    "default-src 'none'; "
    "style-src 'unsafe-inline'; "
    "script-src 'unsafe-inline'; "
    "img-src data:; "
    "media-src data: blob:;"
)


def render_docx_studio_html(
    report_data: dict[str, Any],
    output_path: Path | str | None = None,
) -> str:
    """Generates a standalone, rich interactive CSP-compliant offline HTML studio dashboard."""
    manuscript_title = html.escape(report_data.get("manuscript", "Manuscript"))
    draft_name = html.escape(report_data.get("draft", "Draft-01"))
    active_preset = html.escape(report_data.get("active_preset", "chicago-manual"))
    chapters = report_data.get("chapters", [])
    comments = report_data.get("comments", [])
    presets = report_data.get("presets", {})
    summary = report_data.get("summary", {})

    tot_chapters = len(chapters)
    synced_count = summary.get("synced", 0)
    docx_newer = summary.get("docx_newer", 0)
    md_newer = summary.get("md_newer", 0)
    conflicts_count = summary.get("conflicts", 0)
    total_comments = len(comments)

    # Serialize JSON payload safely for embedded offline JS
    payload_json = json.dumps(
        {
            "manuscript": report_data.get("manuscript", ""),
            "draft": report_data.get("draft", ""),
            "chapters": chapters,
            "comments": comments,
            "presets": presets,
            "active_preset": report_data.get("active_preset", "chicago-manual"),
        },
        ensure_ascii=False,
    ).replace("</", "<\\/")

    theme_css = get_theme_engine_css()
    theme_js = get_theme_engine_js()
    control_center_html = get_theme_control_center_html()

    html_content = f"""<!DOCTYPE html>
<html lang="en" data-theme="sovereign-dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Content-Security-Policy" content="{_CSP}">
<title>Ars Arcanum — DOCX Sync &amp; Typesetting Studio ({manuscript_title})</title>
<style>
{theme_css}
  :root {{
    --bg-primary: #0f172a;
    --bg-secondary: #1e293b;
    --bg-card: #1e293b;
    --bg-elevated: #334155;
    --border-color: #334155;
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
    --accent-blue: #38bdf8;
    --accent-green: #22c55e;
    --accent-amber: #f59e0b;
    --accent-red: #ef4444;
    --accent-purple: #c084fc;
    --font-mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    --font-serif: "Georgia", "EB Garamond", "Times New Roman", serif;
  }}

  [data-theme="light"] {{
    --bg-primary: #f8fafc;
    --bg-secondary: #f1f5f9;
    --bg-card: #ffffff;
    --bg-elevated: #e2e8f0;
    --border-color: #cbd5e1;
    --text-primary: #0f172a;
    --text-secondary: #475569;
    --text-muted: #94a3b8;
    --accent-blue: #0284c7;
    --accent-green: #16a34a;
    --accent-amber: #d97706;
    --accent-red: #dc2626;
    --accent-purple: #9333ea;
  }}

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: var(--font-sans);
    background-color: var(--bg-primary);
    color: var(--text-primary);
    line-height: 1.5;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }}

  header {{
    background-color: var(--bg-secondary);
    border-bottom: 1px solid var(--border-color);
    padding: 1rem 1.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: sticky;
    top: 0;
    z-index: 40;
  }}

  .header-left {{ display: flex; align-items: center; gap: 1rem; }}
  .logo {{ font-weight: 800; font-size: 1.25rem; display: flex; align-items: center; gap: 0.5rem; }}
  .logo-badge {{ background: var(--accent-blue); color: #000; font-size: 0.75rem; font-weight: 700; padding: 0.15rem 0.5rem; border-radius: 9999px; }}
  .header-meta {{ font-size: 0.9rem; color: var(--text-secondary); }}

  .header-right {{ display: flex; align-items: center; gap: 0.75rem; }}
  .btn {{
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.45rem 0.9rem;
    border-radius: 0.375rem;
    font-size: 0.85rem;
    font-weight: 600;
    cursor: pointer;
    border: 1px solid transparent;
    transition: all 0.15s ease-in-out;
  }}
  .btn-primary {{ background: var(--accent-blue); color: #000; }}
  .btn-primary:hover {{ filter: brightness(1.1); }}
  .btn-secondary {{ background: var(--bg-elevated); color: var(--text-primary); border-color: var(--border-color); }}
  .btn-secondary:hover {{ background: var(--border-color); }}
  .btn-green {{ background: var(--accent-green); color: #000; }}
  .btn-green:hover {{ filter: brightness(1.1); }}

  main {{ max-width: 1400px; width: 100%; margin: 0 auto; padding: 1.5rem; flex: 1; }}

  /* Metric cards */
  .metrics-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 1.5rem;
  }}
  .metric-card {{
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 0.5rem;
    padding: 1rem 1.25rem;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }}
  .metric-label {{ font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); font-weight: 600; }}
  .metric-val {{ font-size: 1.75rem; font-weight: 800; }}
  .metric-sub {{ font-size: 0.75rem; color: var(--text-secondary); }}

  /* Tab navigation */
  .tabs-nav {{
    display: flex;
    gap: 0.5rem;
    border-bottom: 1px solid var(--border-color);
    margin-bottom: 1.5rem;
  }}
  .tab-btn {{
    padding: 0.75rem 1.25rem;
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    color: var(--text-secondary);
    font-size: 0.95rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s ease-in-out;
  }}
  .tab-btn:hover {{ color: var(--text-primary); }}
  .tab-btn.active {{ color: var(--accent-blue); border-bottom-color: var(--accent-blue); }}

  .tab-pane {{ display: none; }}
  .tab-pane.active {{ display: block; }}

  /* Chapter table */
  .table-container {{
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 0.5rem;
    overflow: hidden;
  }}
  .table-toolbar {{
    padding: 0.75rem 1rem;
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border-color);
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
  }}
  .search-input {{
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 0.375rem;
    padding: 0.4rem 0.8rem;
    color: var(--text-primary);
    font-size: 0.85rem;
    width: 260px;
  }}
  .search-input:focus {{ outline: 2px solid var(--accent-blue); }}

  table {{ width: 100%; border-collapse: collapse; text-align: left; font-size: 0.9rem; }}
  th {{ background: var(--bg-secondary); color: var(--text-muted); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; padding: 0.75rem 1rem; font-weight: 700; border-bottom: 1px solid var(--border-color); }}
  td {{ padding: 0.85rem 1rem; border-bottom: 1px solid var(--border-color); vertical-align: middle; }}
  tr:last-child td {{ border-bottom: none; }}
  tr:hover td {{ background: var(--bg-secondary); }}

  /* Badges */
  .badge {{
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    padding: 0.2rem 0.6rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 700;
  }}
  .badge-synced {{ background: rgba(34, 197, 94, 0.15); color: var(--accent-green); border: 1px solid var(--accent-green); }}
  .badge-docx-newer {{ background: rgba(56, 189, 248, 0.15); color: var(--accent-blue); border: 1px solid var(--accent-blue); }}
  .badge-md-newer {{ background: rgba(245, 158, 11, 0.15); color: var(--accent-amber); border: 1px solid var(--accent-amber); }}
  .badge-conflict {{ background: rgba(239, 68, 68, 0.15); color: var(--accent-red); border: 1px solid var(--accent-red); }}

  /* Typography Preview Card */
  .presets-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 1.5rem;
  }}
  .preset-card {{
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 0.5rem;
    padding: 1.25rem;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    cursor: pointer;
    transition: all 0.2s ease-in-out;
  }}
  .preset-card:hover {{ border-color: var(--accent-blue); transform: translateY(-2px); }}
  .preset-card.selected {{ border-color: var(--accent-blue); box-shadow: 0 0 0 2px var(--accent-blue); }}
  .preset-name {{ font-size: 1.1rem; font-weight: 700; }}
  .preset-desc {{ font-size: 0.85rem; color: var(--text-secondary); }}
  .preset-details {{ display: flex; flex-wrap: wrap; gap: 0.4rem; font-size: 0.75rem; color: var(--text-muted); }}
  .preset-tag {{ background: var(--bg-elevated); padding: 0.15rem 0.5rem; border-radius: 0.25rem; }}

  /* Interactive Live Typesetting Simulator */
  .preview-stage {{
    margin-top: 1.5rem;
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 0.5rem;
    padding: 1.5rem;
  }}
  .manuscript-page {{
    background: #ffffff;
    color: #000000;
    max-width: 650px;
    margin: 0 auto;
    padding: 3rem 2.5rem;
    box-shadow: 0 10px 25px rgba(0,0,0,0.3);
    border-radius: 2px;
    font-size: 12pt;
    line-height: 2.0;
  }}
  .page-header-slug {{
    text-align: right;
    font-size: 10pt;
    margin-bottom: 2rem;
    color: #444;
  }}
  .manuscript-heading {{
    text-align: center;
    font-weight: bold;
    font-size: 16pt;
    margin-bottom: 1.5rem;
  }}
  .manuscript-para {{
    text-indent: 0.5in;
    text-align: justify;
    margin-bottom: 0;
  }}
  .scene-divider {{
    text-align: center;
    margin: 1rem 0;
  }}

  /* Diff Modal / View */
  .diff-container {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 0.5rem;
    padding: 1rem;
    margin-top: 1rem;
  }}
  .diff-column {{ background: var(--bg-secondary); padding: 1rem; border-radius: 0.375rem; max-height: 500px; overflow-y: auto; font-family: var(--font-mono); font-size: 0.85rem; }}
  .diff-ins {{ background: rgba(34, 197, 94, 0.2); color: var(--accent-green); text-decoration: none; font-weight: bold; padding: 0 0.2rem; }}
  .diff-del {{ background: rgba(239, 68, 68, 0.2); color: var(--accent-red); text-decoration: line-through; padding: 0 0.2rem; }}

  /* Comments List */
  .comments-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 1rem;
  }}
  .comment-card {{
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 0.5rem;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }}
  .comment-meta {{ display: flex; justify-content: space-between; align-items: center; font-size: 0.75rem; color: var(--text-muted); }}
  .comment-author {{ font-weight: 700; color: var(--accent-purple); }}
  .comment-body {{ font-size: 0.9rem; }}

  /* CLI Command Helper Bar */
  .cli-helper-bar {{
    margin-top: 1.5rem;
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 0.5rem;
    padding: 1rem 1.25rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
  }}
  .cli-code {{
    font-family: var(--font-mono);
    background: var(--bg-primary);
    padding: 0.3rem 0.6rem;
    border-radius: 0.25rem;
    font-size: 0.85rem;
    color: var(--accent-blue);
    border: 1px solid var(--border-color);
  }}
</style>
</head>
<body>

<header>
  <div class="header-left">
    <div class="logo">
      🏛️ Ars Arcanum
      <span class="logo-badge">DOCX Studio</span>
    </div>
    <div class="header-meta">
      <strong>{manuscript_title}</strong> &bull; {draft_name}
    </div>
  </div>
  <div class="header-right">
    {control_center_html}
    <button class="btn btn-secondary" onclick="copyCliCommand('arcanum docx sync .')">📋 Copy Sync CLI</button>
    <button class="btn btn-primary" onclick="copyCliCommand('arcanum docx watch .')">👁️ Copy Watch CLI</button>
  </div>
</header>

<main>
  <!-- High Level Telemetry Metrics -->
  <div class="metrics-grid">
    <div class="metric-card">
      <span class="metric-label">Total Chapters</span>
      <span class="metric-val">{tot_chapters}</span>
      <span class="metric-sub">Pairs Discovered</span>
    </div>
    <div class="metric-card">
      <span class="metric-label" style="color:var(--accent-green)">In Sync</span>
      <span class="metric-val" style="color:var(--accent-green)">{synced_count}</span>
      <span class="metric-sub">MD &amp; DOCX identical</span>
    </div>
    <div class="metric-card">
      <span class="metric-label" style="color:var(--accent-blue)">Word Newer</span>
      <span class="metric-val" style="color:var(--accent-blue)">{docx_newer}</span>
      <span class="metric-sub">Ready to pull to MD</span>
    </div>
    <div class="metric-card">
      <span class="metric-label" style="color:var(--accent-amber)">Markdown Newer</span>
      <span class="metric-val" style="color:var(--accent-amber)">{md_newer}</span>
      <span class="metric-sub">Ready to build to DOCX</span>
    </div>
    <div class="metric-card">
      <span class="metric-label" style="color:var(--accent-red)">Conflicts</span>
      <span class="metric-val" style="color:var(--accent-red)">{conflicts_count}</span>
      <span class="metric-sub">Branching sidecars</span>
    </div>
    <div class="metric-card">
      <span class="metric-label" style="color:var(--accent-purple)">Editorial Comments</span>
      <span class="metric-val" style="color:var(--accent-purple)">{total_comments}</span>
      <span class="metric-sub">Extracted in sidecars</span>
    </div>
  </div>

  <!-- Tabbed Interface -->
  <div class="tabs-nav">
    <button class="tab-btn active" onclick="switchTab('matrix')">📊 Chapter Matrix</button>
    <button class="tab-btn" onclick="switchTab('presets')">✨ Typesetting Presets &amp; CMOS</button>
    <button class="tab-btn" onclick="switchTab('comments')">💬 Editorial Comments ({total_comments})</button>
  </div>

  <!-- Tab 1: Chapter Matrix -->
  <div id="tab-matrix" class="tab-pane active">
    <div class="table-container">
      <div class="table-toolbar">
        <input type="text" id="chapter-search" class="search-input" placeholder="🔍 Search chapter titles or paths..." oninput="filterChapters()">
        <div style="display:flex; gap:0.5rem;">
          <button class="btn btn-secondary" onclick="filterStatus('all')">All ({tot_chapters})</button>
          <button class="btn btn-secondary" onclick="filterStatus('out-of-sync')">Out of Sync ({docx_newer + md_newer + conflicts_count})</button>
          <button class="btn btn-secondary" onclick="filterStatus('comments')">With Comments</button>
        </div>
      </div>
      <table id="chapters-table">
        <thead>
          <tr>
            <th>Status</th>
            <th>Chapter</th>
            <th>Markdown Word Count</th>
            <th>DOCX Word Count</th>
            <th>Word Delta</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody id="chapters-tbody">
          <!-- Populated by JavaScript -->
        </tbody>
      </table>
    </div>
  </div>

  <!-- Tab 2: Typesetting Presets -->
  <div id="tab-presets" class="tab-pane">
    <div class="presets-grid" id="presets-container">
      <!-- Populated by JavaScript -->
    </div>

    <div class="preview-stage">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
        <h3 style="font-size:1.1rem;">📄 Live Typesetting Simulator Preview</h3>
        <span id="preview-preset-label" class="badge badge-docx-newer">Active: {active_preset}</span>
      </div>
      <div class="manuscript-page" id="manuscript-sample-page">
        <div class="page-header-slug" id="sample-header-slug">AUTHOR / MANUSCRIPT / 1</div>
        <div class="manuscript-heading" id="sample-chapter-title">Chapter 1: The Inciting Spark</div>
        <p class="manuscript-para" id="sample-para-1">
          The bells of the citadel tolled three times in the freezing rain. Through the mist-shrouded parapets, Kaelen watched the arcane lanterns flicker across the lower wards. He adjusted his heavy cloak, ensuring the cipher scroll remained concealed beneath the leather strapping.
        </p>
        <p class="manuscript-para" id="sample-para-2">
          "If the archives fall before dawn," Lyra whispered from the alcove, her fingers dancing with faint azure embers, "the entire sovereign order will be compromised."
        </p>
        <div class="scene-divider" id="sample-scene-divider">#</div>
        <p class="manuscript-para" id="sample-para-3">
          Without answering, he drew the silver blade from its scabbard. The runes etched along the fuller hummed softly, vibrating against his palm in deterministic resonance.
        </p>
      </div>
    </div>
  </div>

  <!-- Tab 3: Comments Feed -->
  <div id="tab-comments" class="tab-pane">
    <div class="table-toolbar" style="margin-bottom:1rem; border-radius:0.5rem;">
      <input type="text" id="comment-search" class="search-input" placeholder="🔍 Filter comments by text or author..." oninput="filterComments()">
      <span class="header-meta" id="comments-count-label">Showing {total_comments} comments</span>
    </div>
    <div class="comments-grid" id="comments-container">
      <!-- Populated by JavaScript -->
    </div>
  </div>

  <!-- CLI Command Helper Bar -->
  <div class="cli-helper-bar">
    <div>
      <div style="font-weight:700; font-size:0.9rem;">⚡ Terminal Command Reference</div>
      <div style="font-size:0.8rem; color:var(--text-secondary);">Execute continuous sync or launch Word directly from your terminal:</div>
    </div>
    <div style="display:flex; gap:0.5rem; flex-wrap:wrap;">
      <span class="cli-code">arcanum docx sync .</span>
      <span class="cli-code">arcanum docx watch .</span>
      <span class="cli-code">arcanum docx open .</span>
    </div>
  </div>
</main>

<script>
const DATA = {payload_json};

function copyCliCommand(cmd) {{
  navigator.clipboard.writeText(cmd).then(() => {{
    alert('Copied command to clipboard:\\n' + cmd);
  }}).catch(() => {{
    prompt('Copy command:', cmd);
  }});
}}

function switchTab(tabId) {{
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
  const btn = Array.from(document.querySelectorAll('.tab-btn')).find(b => b.getAttribute('onclick').includes(tabId));
  if (btn) btn.classList.add('active');
  const target = document.getElementById('tab-' + tabId);
  if (target) target.classList.add('active');
}}

function renderChapters(list) {{
  const tbody = document.getElementById('chapters-tbody');
  if (!tbody) return;
  tbody.innerHTML = '';

  if (!list.length) {{
    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; padding:2rem; color:var(--text-muted);">No chapters found matching criteria.</td></tr>';
    return;
  }}

  list.forEach(c => {{
    let badge = '<span class="badge badge-synced">✓ Synced</span>';
    if (c.status === 'docx_newer') badge = '<span class="badge badge-docx-newer">📥 Word Newer</span>';
    else if (c.status === 'md_newer') badge = '<span class="badge badge-md-newer">📤 Markdown Newer</span>';
    else if (c.status === 'conflict') badge = '<span class="badge badge-conflict">⚠️ Conflict</span>';

    const deltaSign = c.delta >= 0 ? '+' : '';
    const deltaColor = c.delta > 0 ? 'var(--accent-green)' : (c.delta < 0 ? 'var(--accent-red)' : 'var(--text-muted)');

    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${{badge}}</td>
      <td>
        <div style="font-weight:600;">${{escapeHtml(c.title)}}</div>
        <div style="font-size:0.75rem; color:var(--text-muted);">${{escapeHtml(c.rel_path)}}</div>
      </td>
      <td><strong>${{c.md_words}}</strong> w</td>
      <td><strong>${{c.docx_words}}</strong> w</td>
      <td style="color:${{deltaColor}}; font-weight:700;">${{deltaSign}}${{c.delta}} w</td>
      <td>
        <div style="display:flex; gap:0.4rem;">
          <button class="btn btn-secondary" style="padding:0.25rem 0.5rem; font-size:0.75rem;" onclick="copyCliCommand('arcanum docx open . -c \\'${{escapeHtml(c.stem)}}\\'')">Word</button>
          <button class="btn btn-primary" style="padding:0.25rem 0.5rem; font-size:0.75rem;" onclick="copyCliCommand('arcanum docx sync .')">Sync</button>
        </div>
      </td>
    `;
    tbody.appendChild(tr);
  }});
}}

function renderPresets() {{
  const container = document.getElementById('presets-container');
  if (!container) return;
  container.innerHTML = '';

  Object.entries(DATA.presets).forEach(([key, p]) => {{
    const isSelected = key === DATA.active_preset;
    const card = document.createElement('div');
    card.className = 'preset-card' + (isSelected ? ' selected' : '');
    card.onclick = () => selectPreset(key);

    card.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <span class="preset-name">${{escapeHtml(p.name)}}</span>
        ${{isSelected ? '<span class="badge badge-synced">Active Preset</span>' : ''}}
      </div>
      <p class="preset-desc">${{escapeHtml(p.description)}}</p>
      <div class="preset-details">
        <span class="preset-tag">🔤 ${{p.font_family}} (${{p.font_size_pt}}pt)</span>
        <span class="preset-tag">📏 ${{p.line_spacing}}x line spacing</span>
        <span class="preset-tag">📐 ${{p.first_line_indent_inches}}in indent</span>
        <span class="preset-tag">✂️ '${{p.scene_break_symbol}}'</span>
      </div>
    `;
    container.appendChild(card);
  }});
}}

function selectPreset(key) {{
  DATA.active_preset = key;
  renderPresets();
  updateLivePreview(key);
}}

function updateLivePreview(key) {{
  const p = DATA.presets[key];
  if (!p) return;
  const sample = document.getElementById('manuscript-sample-page');
  const label = document.getElementById('preview-preset-label');
  const divider = document.getElementById('sample-scene-divider');
  if (label) label.textContent = 'Active: ' + p.name;
  if (divider) divider.textContent = p.scene_break_symbol || '#';

  if (sample) {{
    sample.style.fontFamily = p.font_family || 'Times New Roman';
    sample.style.fontSize = (p.font_size_pt || 12) + 'pt';
    sample.style.lineHeight = (p.line_spacing || 2.0);
    const paras = sample.querySelectorAll('.manuscript-para');
    paras.forEach(para => {{
      para.style.textIndent = (p.first_line_indent_inches || 0.5) + 'in';
    }});
  }}
}}

function renderComments(list) {{
  const container = document.getElementById('comments-container');
  if (!container) return;
  container.innerHTML = '';

  if (!list.length) {{
    container.innerHTML = '<div style="grid-column:1/-1; text-align:center; padding:2rem; color:var(--text-muted);">No editorial comments discovered in .comments.json sidecars.</div>';
    return;
  }}

  list.forEach(c => {{
    const card = document.createElement('div');
    card.className = 'comment-card';
    card.innerHTML = `
      <div class="comment-meta">
        <span class="comment-author">💬 ${{escapeHtml(c.author || 'Editor')}}</span>
        <span>${{escapeHtml(c.chapter || 'Chapter')}}</span>
      </div>
      <div class="comment-body">${{escapeHtml(c.text)}}</div>
      <div style="font-size:0.7rem; color:var(--text-muted); text-align:right;">${{escapeHtml(c.date || '')}}</div>
    `;
    container.appendChild(card);
  }});
}}

function filterChapters() {{
  const q = (document.getElementById('chapter-search').value || '').toLowerCase();
  const filtered = DATA.chapters.filter(c => c.title.toLowerCase().includes(q) || c.rel_path.toLowerCase().includes(q));
  renderChapters(filtered);
}}

function filterStatus(mode) {{
  if (mode === 'all') renderChapters(DATA.chapters);
  else if (mode === 'out-of-sync') renderChapters(DATA.chapters.filter(c => c.status !== 'synced'));
  else if (mode === 'comments') renderChapters(DATA.chapters.filter(c => c.has_comments));
}}

function filterComments() {{
  const q = (document.getElementById('comment-search').value || '').toLowerCase();
  const filtered = DATA.comments.filter(c => c.text.toLowerCase().includes(q) || (c.author || '').toLowerCase().includes(q));
  renderComments(filtered);
  const countLabel = document.getElementById('comments-count-label');
  if (countLabel) countLabel.textContent = `Showing ${{filtered.length}} comments`;
}}

function escapeHtml(str) {{
  return String(str || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}}

// Initialize
document.addEventListener('DOMContentLoaded', () => {{
  renderChapters(DATA.chapters);
  renderPresets();
  renderComments(DATA.comments);
  updateLivePreview(DATA.active_preset);
}});
</script>
<script>
{theme_js}
</script>

</body>
</html>
"""

    if output_path is not None:
        p = Path(output_path).resolve()
        p.parent.mkdir(parents=True, exist_ok=True)
        atomic_write(p, html_content)
        logger.info("[✓] Rendered Visual DOCX Studio at: %s", p)

    return html_content


__all__ = [
    "render_docx_studio_html",
]
