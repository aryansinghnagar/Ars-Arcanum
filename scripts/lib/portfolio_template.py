#!/usr/bin/env python3
"""
Ars Arcanum Portfolio Dashboard HTML Template (scripts/lib/portfolio_template.py)
================================================================================
Self-contained, offline HTML5 visualizer and interactive author studio for multi-manuscript catalogs.
Strict Content Security Policy enforced (default-src 'none').
"""

from __future__ import annotations

import html
from pathlib import Path
from typing import Any

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


def render_portfolio_html(report: dict[str, Any], output_path: Path | str) -> Path:
    """Generates an interactive, sovereign offline HTML5 Author Portfolio & Catalog Studio."""
    out_path = Path(output_path)
    projects = report.get("projects", [])
    universes = report.get("universes", [])
    velocity = report.get("velocity", {})
    total_words = report.get("total_words", 0)
    total_target = report.get("total_target_words", 0)
    total_lore_words = report.get("total_lore_words", 0)
    total_lore_notes = report.get("total_lore_notes", 0)
    overall_pct = report.get("overall_progress_pct", 0.0)

    # 14-day history for velocity SVG chart
    history_14d = velocity.get("history_14d", [])
    max_history_words = max([h.get("words", 0) for h in history_14d] + [1000])

    # Build SVG Velocity Bars
    svg_bars = []
    bar_width = 32
    chart_height = 140
    gap = 14
    for idx, h in enumerate(history_14d):
        w = h.get("words", 0)
        h_pct = (w / max_history_words) if max_history_words > 0 else 0
        b_h = max(4, int(h_pct * (chart_height - 30)))
        x_pos = 20 + idx * (bar_width + gap)
        y_pos = chart_height - b_h - 20
        date_lbl = h.get("label", "")
        bar_color = "#38bdf8" if w > 0 else "#334155"
        svg_bars.append(f"""
        <g class="bar-group" data-tip="{date_lbl}: {w:,} words">
            <rect x="{x_pos}" y="{y_pos}" width="{bar_width}" height="{b_h}" rx="4" fill="{bar_color}" />
            <text x="{x_pos + bar_width/2}" y="{chart_height - 6}" font-size="10" fill="#94a3b8" text-anchor="middle">{date_lbl[:6]}</text>
            <text x="{x_pos + bar_width/2}" y="{y_pos - 6}" font-size="9" fill="#38bdf8" font-weight="bold" text-anchor="middle">{w if w > 0 else ''}</text>
        </g>
        """)

    svg_velocity_chart = f"""
    <svg viewBox="0 0 {max(600, 40 + len(history_14d) * (bar_width + gap))} {chart_height}" class="chart-svg" style="width:100%; height:auto; overflow:visible;">
        <line x1="10" y1="{chart_height - 20}" x2="100%" y2="{chart_height - 20}" stroke="#334155" stroke-dasharray="4 4" />
        {''.join(svg_bars)}
    </svg>
    """

    # Build Manuscript Cards
    proj_cards = []
    for p in projects:
        p_title = str(p.get("title", "Untitled"))
        p_author = str(p.get("author", "Author"))
        p_stage = str(p.get("stage", "Scaffolding"))
        p_series = str(p.get("series", ""))
        p_progress = float(p.get("progress_pct", 0.0))
        p_words = int(p.get("word_count", 0))
        p_target = int(p.get("target_words", 80000))
        p_volumes = int(p.get("volume_count", 1))
        p_chapters = int(p.get("chapter_count", 0))
        p_path = str(p.get("path", ""))
        p_draft = str(p.get("active_draft", "Latest"))

        stage_cls = "stage-drafting"
        if "Publication" in p_stage:
            stage_cls = "stage-published"
        elif "Revision" in p_stage or "Pre-Flight" in p_stage:
            stage_cls = "stage-revision"
        elif "Scaffolding" in p_stage:
            stage_cls = "stage-scaffold"

        # Export tags
        export_badges = "".join(f'<span class="badge badge-export">📦 {exp}</span>' for exp in p.get("export_types", []))

        # Deadline badge
        deadline_badge = ""
        if p.get("deadline"):
            dl_status = str(p.get("deadline_status", ""))
            dl_days = int(p.get("days_remaining", 0) or 0)
            req_w = int(p.get("daily_words_needed", 0) or 0)
            status_color = "#ef4444" if dl_days < 0 else ("#f59e0b" if dl_days <= 14 else "#10b981")
            status_suffix = f" • {dl_status}" if dl_status else ""
            deadline_badge = f"""
            <span class="badge" style="background:rgba(245, 158, 11, 0.15); color:{status_color}; border:1px solid {status_color};">
                ⏰ {html.escape(str(p['deadline']))} ({dl_days}d left • {req_w:,} w/day req{status_suffix})
            </span>
            """

        # Chapters list
        chapter_rows = []
        for ch in p.get("chapters", []):
            ch_name = str(ch.get("name", "Chapter"))
            ch_words = int(ch.get("words", 0))
            chapter_rows.append(f"""
            <div class="chapter-row">
                <span class="chapter-name">{html.escape(ch_name)}</span>
                <span class="chapter-words">{ch_words:,} words</span>
            </div>
            """)
        chapters_accordion = ""
        if chapter_rows:
            chapters_accordion = f"""
            <details class="chapter-drawer" style="margin-top:0.75rem;">
                <summary style="font-size:0.8rem; color:#38bdf8; cursor:pointer; user-select:none;">📖 View Chapter Breakdown ({len(chapter_rows)} chapters)</summary>
                <div class="chapters-grid" style="margin-top:0.5rem; max-height:220px; overflow-y:auto;">
                    {''.join(chapter_rows)}
                </div>
            </details>
            """

        series_tag = f'<span class="badge badge-series">📚 {html.escape(p_series)}</span>' if p_series else ""

        card = f"""
        <div class="project-card" data-title="{html.escape(p_title.lower())}" data-author="{html.escape(p_author.lower())}" data-stage="{html.escape(p_stage.lower())}" data-series="{html.escape(p_series.lower())}" data-progress="{p_progress}" data-words="{p_words}" data-target="{p_target}">
          <div class="card-header">
            <div>
                <h3 class="card-title">{html.escape(p_title)}</h3>
                <div class="card-subtitle">by {html.escape(p_author)} {series_tag}</div>
            </div>
            <div style="display:flex; gap:0.5rem; flex-wrap:wrap; align-items:center;">
                {deadline_badge}
                <span class="badge {stage_cls}">{html.escape(p_stage)}</span>
            </div>
          </div>

          <div class="meta-row">
            <span><strong>{p_volumes}</strong> Vol</span> •
            <span><strong>{p_chapters}</strong> Ch</span> •
            <span><strong>{p_words:,}</strong> / {p_target:,} words</span>
            <span class="progress-pill">{p_progress}%</span>
          </div>

          <div class="progress-track">
            <div class="progress-fill" style="width:{p_progress}%;"></div>
          </div>

          {chapters_accordion}

          <div class="card-footer">
            <div style="display:flex; gap:0.4rem; flex-wrap:wrap;">
                <span class="badge badge-draft">Draft: {html.escape(p_draft)}</span>
                {export_badges}
            </div>
            <div class="quick-actions">
                <button class="action-btn" onclick="copyCli('arcanum sprint start --target 1000 --minutes 45')">⚡ Sprint</button>
                <button class="action-btn" onclick="copyCli('arcanum words \\'{html.escape(p_path)}\\'')">📊 Telemetry</button>
                <button class="action-btn" onclick="copyCli('arcanum preflight \\'{html.escape(p_path)}\\'')">🛡️ Preflight</button>
            </div>
          </div>
        </div>
        """
        proj_cards.append(card)

    # Build Universe Cards
    uni_cards = []
    for u in universes:
        u_name = str(u.get("name", "Universe"))
        u_desc = str(u.get("description", "Shared Lore Codex Vault"))
        u_status = str(u.get("status", "Active Lore Vault"))
        u_notes = int(u.get("total_notes", 0))
        u_words = int(u.get("total_words", 0))
        u_health = float(u.get("link_health_pct", 100.0))
        u_broken = int(u.get("broken_links", 0))
        u_path = str(u.get("path", ""))

        cat_chips = []
        for cname, cstat in u.get("categories", {}).items():
            if isinstance(cstat, dict) and cstat.get("count", 0) > 0:
                cat_chips.append(f"""
                <span class="badge badge-lore-cat">{html.escape(str(cname))}: <strong>{cstat.get('count', 0)}</strong> ({cstat.get('words', 0):,} w)</span>
                """)

        health_color = "#10b981" if u_health >= 95 else ("#f59e0b" if u_health >= 80 else "#ef4444")

        card = f"""
        <div class="project-card universe-card" data-title="{html.escape(u_name.lower())}" data-stage="universe">
          <div class="card-header">
            <div>
                <h3 class="card-title" style="color:#a855f7;">🪐 {html.escape(u_name)}</h3>
                <div class="card-subtitle">{html.escape(u_desc)}</div>
            </div>
            <div>
                <span class="badge" style="background:rgba(168, 85, 247, 0.15); color:#c084fc; border:1px solid #c084fc;">
                    {html.escape(u_status)}
                </span>
            </div>
          </div>

          <div class="meta-row">
            <span><strong>{u_notes}</strong> Lore Notes</span> •
            <span><strong>{u_words:,}</strong> Lore Words</span> •
            <span style="color:{health_color}; font-weight:700;">{u_health}% Link Integrity</span>
          </div>

          <div class="category-chips-grid" style="display:flex; flex-wrap:wrap; gap:0.4rem; margin:0.75rem 0;">
            {''.join(cat_chips) or '<span class="badge">No categorized entries</span>'}
          </div>

          <div class="card-footer">
            <span class="badge" style="background:#0f172a; color:#94a3b8;">Broken Links: {u_broken}</span>
            <div class="quick-actions">
                <button class="action-btn" onclick="copyCli('arcanum codex \\'{html.escape(u_path)}\\' --html')">📖 Static Codex</button>
                <button class="action-btn" onclick="copyCli('arcanum doctor \\'{html.escape(u_path)}\\'')">🩺 Lore Audit</button>
            </div>
          </div>
        </div>
        """
        uni_cards.append(card)

    theme_css = get_theme_engine_css()
    theme_js = get_theme_engine_js()
    control_center_html = get_theme_control_center_html()

    html_content = f"""<!DOCTYPE html>
<html lang="en" data-theme="sovereign-dark">
<head>
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ars Arcanum — Sovereign Author Portfolio Studio</title>
<style>
{theme_css}
  :root {{
    --bg: #090d16;
    --surface: #111827;
    --surface-hover: #1f2937;
    --card-bg: #131d31;
    --card-border: #1e2e4a;
    --text: #f8fafc;
    --text-muted: #94a3b8;
    --accent: #38bdf8;
    --accent-glow: rgba(56, 189, 248, 0.25);
    --purple: #c084fc;
    --green: #10b981;
    --amber: #f59e0b;
    --rose: #f43f5e;
    --shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.5);
  }}

  [data-theme="light"] {{
    --bg: #f1f5f9;
    --surface: #ffffff;
    --surface-hover: #f8fafc;
    --card-bg: #ffffff;
    --card-border: #cbd5e1;
    --text: #0f172a;
    --text-muted: #64748b;
    --accent: #0284c7;
    --accent-glow: rgba(2, 132, 199, 0.15);
    --purple: #9333ea;
    --green: #059669;
    --amber: #d97706;
    --rose: #e11d48;
    --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  }}

  * {{ box-sizing: border-box; transition: background-color 0.2s, border-color 0.2s, color 0.2s; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    background: var(--bg);
    color: var(--text);
    margin: 0;
    padding: 0;
    line-height: 1.5;
  }}

  .studio-container {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem 1.5rem;
  }}

  /* Header & Navigation */
  .studio-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--card-border);
    padding-bottom: 1.25rem;
    margin-bottom: 2rem;
    flex-wrap: wrap;
    gap: 1rem;
  }}
  .logo-group {{
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }}
  .logo-icon {{
    font-size: 2.2rem;
    filter: drop-shadow(0 0 8px var(--accent-glow));
  }}
  .header-title {{
    margin: 0;
    font-size: 1.75rem;
    font-weight: 800;
    letter-spacing: -0.025em;
    background: linear-gradient(135deg, var(--text) 30%, var(--accent));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }}
  .header-subtitle {{
    margin: 0.25rem 0 0;
    font-size: 0.875rem;
    color: var(--text-muted);
  }}
  .header-controls {{
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }}
  .theme-toggle-btn {{
    background: var(--surface);
    border: 1px solid var(--card-border);
    color: var(--text);
    padding: 0.5rem 0.85rem;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.9rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
  }}
  .theme-toggle-btn:hover {{
    background: var(--surface-hover);
    border-color: var(--accent);
  }}

  /* KPI Cards Grid */
  .kpi-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 1.25rem;
    margin-bottom: 2rem;
  }}
  .kpi-card {{
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 12px;
    padding: 1.25rem;
    box-shadow: var(--shadow);
    position: relative;
    overflow: hidden;
  }}
  .kpi-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, var(--accent), var(--purple));
  }}
  .kpi-label {{
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-muted);
    font-weight: 700;
    margin-bottom: 0.5rem;
    display: flex;
    justify-content: space-between;
  }}
  .kpi-value {{
    font-size: 2.2rem;
    font-weight: 800;
    color: var(--text);
    line-height: 1.1;
  }}
  .kpi-subtext {{
    font-size: 0.8rem;
    color: var(--text-muted);
    margin-top: 0.5rem;
  }}

  /* Analytics Visualizations Row */
  .charts-section {{
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 2rem;
    box-shadow: var(--shadow);
  }}
  .section-heading {{
    margin: 0 0 1rem;
    font-size: 1.1rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }}

  /* Search & Filter Controls */
  .filter-toolbar {{
    display: flex;
    gap: 1rem;
    align-items: center;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
  }}
  .search-input {{
    flex: 1;
    min-width: 260px;
    background: var(--surface);
    border: 1px solid var(--card-border);
    color: var(--text);
    padding: 0.65rem 1rem;
    border-radius: 8px;
    font-size: 0.9rem;
  }}
  .search-input:focus {{
    outline: none;
    border-color: var(--accent);
    box-shadow: 0 0 0 3px var(--accent-glow);
  }}
  .filter-pills {{
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
  }}
  .filter-pill {{
    background: var(--surface);
    border: 1px solid var(--card-border);
    color: var(--text-muted);
    padding: 0.4rem 0.85rem;
    border-radius: 20px;
    font-size: 0.8rem;
    cursor: pointer;
    font-weight: 600;
  }}
  .filter-pill.active, .filter-pill:hover {{
    background: var(--accent);
    color: #ffffff;
    border-color: var(--accent);
  }}

  /* Project Cards Grid */
  .projects-grid {{
    display: grid;
    grid-template-columns: 1fr;
    gap: 1.25rem;
    margin-bottom: 2.5rem;
  }}
  .project-card {{
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: var(--shadow);
  }}
  .project-card:hover {{
    border-color: var(--accent);
    transform: translateY(-2px);
    transition: transform 0.2s, border-color 0.2s;
  }}
  .universe-card {{
    border-left: 4px solid var(--purple);
  }}
  .card-header {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 0.75rem;
    flex-wrap: wrap;
    gap: 0.5rem;
  }}
  .card-title {{
    margin: 0;
    font-size: 1.3rem;
    font-weight: 700;
    color: var(--accent);
  }}
  .card-subtitle {{
    color: var(--text-muted);
    font-size: 0.85rem;
    margin-top: 0.25rem;
  }}
  .meta-row {{
    font-size: 0.875rem;
    color: var(--text-muted);
    margin-bottom: 0.85rem;
  }}
  .progress-pill {{
    background: var(--surface);
    color: var(--text);
    padding: 2px 6px;
    border-radius: 4px;
    font-weight: 700;
    margin-left: 0.4rem;
  }}
  .progress-track {{
    background: var(--surface);
    height: 10px;
    border-radius: 5px;
    overflow: hidden;
    margin-bottom: 1rem;
  }}
  .progress-fill {{
    height: 100%;
    background: linear-gradient(90deg, var(--accent), #60a5fa);
    border-radius: 5px;
    transition: width 0.5s ease-out;
  }}
  .card-footer {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-top: 1px solid var(--card-border);
    padding-top: 0.85rem;
    margin-top: 0.85rem;
    flex-wrap: wrap;
    gap: 0.75rem;
  }}
  .badge {{
    display: inline-block;
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 700;
    background: var(--surface);
    color: var(--text-muted);
    border: 1px solid var(--card-border);
  }}
  .stage-published {{ background: rgba(16, 185, 129, 0.15); color: var(--green); border-color: var(--green); }}
  .stage-revision {{ background: rgba(245, 158, 11, 0.15); color: var(--amber); border-color: var(--amber); }}
  .stage-drafting {{ background: rgba(56, 189, 248, 0.15); color: var(--accent); border-color: var(--accent); }}
  .stage-scaffold {{ background: rgba(148, 163, 184, 0.15); color: var(--text-muted); border-color: var(--card-border); }}
  .badge-export {{ background: rgba(192, 132, 252, 0.15); color: var(--purple); border-color: var(--purple); }}
  .badge-series {{ background: rgba(96, 165, 250, 0.15); color: #60a5fa; border-color: #60a5fa; }}
  .badge-draft {{ background: var(--surface); color: var(--text-muted); }}
  .badge-lore-cat {{ background: var(--surface); color: var(--purple); border: 1px solid rgba(192, 132, 252, 0.3); }}

  .quick-actions {{
    display: flex;
    gap: 0.4rem;
  }}
  .action-btn {{
    background: var(--surface);
    border: 1px solid var(--card-border);
    color: var(--text);
    padding: 0.35rem 0.65rem;
    border-radius: 6px;
    font-size: 0.75rem;
    cursor: pointer;
    font-weight: 600;
  }}
  .action-btn:hover {{
    background: var(--surface-hover);
    border-color: var(--accent);
    color: var(--accent);
  }}

  .chapter-row {{
    display: flex;
    justify-content: space-between;
    padding: 0.35rem 0.5rem;
    border-bottom: 1px solid var(--card-border);
    font-size: 0.8rem;
  }}
  .chapter-name {{ color: var(--text); }}
  .chapter-words {{ color: var(--text-muted); font-weight: 600; }}

  /* Toast Notification */
  #toast {{
    visibility: hidden;
    min-width: 250px;
    background: var(--surface);
    color: var(--accent);
    border: 1px solid var(--accent);
    text-align: center;
    border-radius: 8px;
    padding: 12px;
    position: fixed;
    z-index: 1000;
    bottom: 30px;
    right: 30px;
    font-size: 0.85rem;
    font-weight: 600;
    box-shadow: var(--shadow);
  }}
  #toast.show {{
    visibility: visible;
    animation: fadein 0.3s, fadeout 0.3s 2.2s;
  }}
  @keyframes fadein {{ from {{ bottom: 0; opacity: 0; }} to {{ bottom: 30px; opacity: 1; }} }}
  @keyframes fadeout {{ from {{ bottom: 30px; opacity: 1; }} to {{ bottom: 0; opacity: 0; }} }}
</style>
</head>
<body>
<div class="studio-container">
  <!-- Header -->
  <header class="studio-header">
    <div class="logo-group">
        <span class="logo-icon">🏛️</span>
        <div>
            <h1 class="header-title">Ars Arcanum Portfolio Studio</h1>
            <p class="header-subtitle">Author Portfolio & Catalog Dashboard • Sovereign Velocity Telemetry & Lore Hub</p>
        </div>
    </div>
    <div class="header-controls">
        <span style="font-size:0.75rem; color:var(--text-muted);">Scanned: {str(report.get('scan_time', ''))[:19].replace('T', ' ')}</span>
        {control_center_html}
    </div>
  </header>

  <!-- Executive KPI Grid -->
  <section class="kpi-grid">
    <div class="kpi-card">
        <div class="kpi-label"><span>Total Prose Words</span> <span>📚</span></div>
        <div class="kpi-value">{total_words:,}</div>
        <div class="kpi-subtext">{overall_pct}% of {total_target:,} target words</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label"><span>Active Sprint Pace</span> <span>⚡</span></div>
        <div class="kpi-value">{velocity.get('rolling_7d_wpd', 0):,} <span style="font-size:1rem; font-weight:600;">w/day</span></div>
        <div class="kpi-subtext">7-day avg pace ({velocity.get('rolling_7d_wpm', 0.0)} WPM)</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label"><span>Habit Streak</span> <span>🔥</span></div>
        <div class="kpi-value">{velocity.get('current_streak', 0)} <span style="font-size:1rem; font-weight:600;">Days</span></div>
        <div class="kpi-subtext">{velocity.get('total_sessions', 0)} total recorded sprint sessions</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label"><span>Creative Ecosystem</span> <span>🪐</span></div>
        <div class="kpi-value">{report.get('total_projects', 0)} <span style="font-size:1rem; font-weight:600;">Books</span> • {len(universes)} <span style="font-size:1rem; font-weight:600;">Lore</span></div>
        <div class="kpi-subtext">{total_lore_notes} lore notes ({total_lore_words:,} lore words)</div>
    </div>
  </section>

  <!-- Rolling 14-Day Drafting Velocity SVG Chart -->
  <section class="charts-section">
    <h2 class="section-heading">📈 14-Day Drafting Velocity & Sprint Distribution</h2>
    {svg_velocity_chart}
  </section>

  <!-- Search & Filter Controls -->
  <div class="filter-toolbar">
    <input type="text" id="searchInput" class="search-input" placeholder="🔍 Search manuscripts, authors, series, or universes..." oninput="filterCards()" />
    <div class="filter-pills">
        <button class="filter-pill active" onclick="setFilter('all', this)">All</button>
        <button class="filter-pill" onclick="setFilter('drafting', this)">Drafting</button>
        <button class="filter-pill" onclick="setFilter('revision', this)">Revisions</button>
        <button class="filter-pill" onclick="setFilter('published', this)">Published</button>
        <button class="filter-pill" onclick="setFilter('universe', this)">Lore Universes</button>
    </div>
  </div>

  <!-- Projects Grid -->
  <main class="projects-grid" id="projectsContainer">
    {''.join(proj_cards)}
    {''.join(uni_cards)}
  </main>
</div>

<div id="toast">Command copied to clipboard!</div>

<script>
  let currentFilter = 'all';

  function setFilter(filterType, btn) {{
    currentFilter = filterType;
    document.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    filterCards();
  }}

  function filterCards() {{
    const query = (document.getElementById('searchInput').value || '').toLowerCase().trim();
    const cards = document.querySelectorAll('.project-card');

    cards.forEach(card => {{
      const title = card.getAttribute('data-title') || '';
      const author = card.getAttribute('data-author') || '';
      const stage = card.getAttribute('data-stage') || '';
      const series = card.getAttribute('data-series') || '';

      const matchesQuery = !query || title.includes(query) || author.includes(query) || series.includes(query);

      let matchesFilter = true;
      if (currentFilter === 'drafting') {{
        matchesFilter = stage.includes('draft');
      }} else if (currentFilter === 'revision') {{
        matchesFilter = stage.includes('revision') || stage.includes('pre-flight');
      }} else if (currentFilter === 'published') {{
        matchesFilter = stage.includes('publish') || stage.includes('ready');
      }} else if (currentFilter === 'universe') {{
        matchesFilter = stage === 'universe';
      }}

      if (matchesQuery && matchesFilter) {{
        card.style.display = 'block';
      }} else {{
        card.style.display = 'none';
      }}
    }});
  }}

  function copyCli(cmd) {{
    if (navigator.clipboard) {{
      navigator.clipboard.writeText(cmd).then(() => showToast(`Copied: ${{cmd}}`));
    }} else {{
      showToast(`Command: ${{cmd}}`);
    }}
  }}

  function showToast(msg) {{
    const toast = document.getElementById('toast');
    toast.innerText = msg;
    toast.className = 'show';
    setTimeout(() => {{ toast.className = toast.className.replace('show', ''); }}, 2500);
  }}
</script>
<script>
{theme_js}
</script>
</body>
</html>
"""
    atomic_write(out_path, html_content)
    return out_path


__all__ = ["render_portfolio_html"]
