#!/usr/bin/env python3
"""
Ars Arcanum Manuscript Draft Visual Dashboard HTML Generator
(scripts/lib/draft_manager_template.py)
============================================================
Pure-Python, zero-dependency, offline CSP-compliant HTML/CSS visual dashboard
for novel manuscript draft lineage, milestone tracking, and lock status.
"""

from __future__ import annotations

import html
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger("arcanum.draft_manager_template")

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

_MILESTONE_COLORS: dict[str, tuple[str, str]] = {
    "alpha": ("#818cf8", "rgba(129, 140, 248, 0.15)"),
    "beta": ("#38bdf8", "rgba(56, 189, 248, 0.15)"),
    "arc": ("#fbbf24", "rgba(251, 191, 36, 0.15)"),
    "line-edit": ("#f472b6", "rgba(244, 114, 182, 0.15)"),
    "proof-final": ("#34d399", "rgba(52, 211, 153, 0.15)"),
    "final": ("#34d399", "rgba(52, 211, 153, 0.15)"),
    "experiment": ("#c084fc", "rgba(192, 132, 252, 0.15)"),
    "query": ("#fb923c", "rgba(251, 146, 60, 0.15)"),
    "draft": ("#94a3b8", "rgba(148, 163, 184, 0.15)"),
}


def _get_milestone_badge(milestone: str) -> str:
    key = milestone.lower().strip()
    color, bg = _MILESTONE_COLORS.get(key, ("#94a3b8", "rgba(148, 163, 184, 0.15)"))
    safe_text = html.escape(milestone.upper())
    return (
        f'<span class="badge-milestone" style="color: {color}; background-color: {bg}; border-color: {color}40;">'
        f'🏷️ {safe_text}</span>'
    )


def generate_draft_dashboard_html(
    manuscript_title: str,
    drafts_data: list[dict[str, Any]],
    active_draft_name: str | None = None,
    universe_name: str = "",
    world_name: str = "",
    output_path: Path | str | None = None,
) -> str:
    """Generates a standalone, interactive offline HTML dashboard for manuscript draft management."""
    safe_title = html.escape(manuscript_title or "Manuscript")
    safe_univ = html.escape(universe_name)
    safe_world = html.escape(world_name)

    total_drafts = len(drafts_data)
    locked_count = sum(1 for d in drafts_data if d.get("locked"))
    total_words = sum(d.get("word_count", 0) for d in drafts_data)

    # Active draft card resolution
    active_draft_dict = None
    if active_draft_name:
        for d in drafts_data:
            if d.get("name", "").lower() == active_draft_name.lower():
                active_draft_dict = d
                break
    if not active_draft_dict and drafts_data:
        active_draft_dict = drafts_data[-1]

    # Build DAG Nodes and Cards HTML
    cards_html_parts = []
    tree_nodes_parts = []

    for idx, d in enumerate(drafts_data):
        d_name = html.escape(d.get("name", f"Draft-{idx+1:02d}"))
        is_active = d.get("is_active", False) or (active_draft_dict and d.get("name") == active_draft_dict.get("name"))
        is_locked = d.get("locked", False)
        milestone = d.get("milestone", "Draft")
        parent = html.escape(d.get("parent_draft") or "Root Genesis")
        created = html.escape(d.get("created_at", "Unknown")[:10] if d.get("created_at") else "Unknown")
        words = d.get("word_count", 0)
        chaps = d.get("chapter_count", 0)
        notes = html.escape(d.get("notes", ""))
        vol = html.escape(d.get("volume", "Root"))

        # Lock Badge
        if is_locked:
            lock_badge = '<span class="badge-lock locked">🔒 LOCKED (Immutable)</span>'
            card_lock_class = "card-locked"
        else:
            lock_badge = '<span class="badge-lock unlocked">🔓 ACTIVE (Editable)</span>'
            card_lock_class = "card-unlocked"

        # Active Badge
        active_badge = '<span class="badge-active">🟢 ACTIVE WORKSTREAM</span>' if is_active else ""
        active_class = "card-is-active" if is_active else ""

        milestone_badge = _get_milestone_badge(milestone)

        # Chapter breakdown table rows
        chap_rows = []
        for ch in d.get("chapters", []):
            ch_title = html.escape(ch.get("title", ch.get("filename", "Chapter")))
            ch_words = ch.get("words", 0)
            chap_rows.append(
                f'<tr><td class="ch-title">{ch_title}</td><td class="ch-words">{ch_words:,} w</td></tr>'
            )
        chap_table_html = "".join(chap_rows)
        if not chap_table_html:
            chap_table_html = '<tr><td colspan="2" class="empty-chaps">No chapters recorded</td></tr>'

        # Card HTML
        card_html = f"""
        <div class="draft-card {active_class} {card_lock_class}" id="draft-{html.escape(d.get('name', ''))}" data-name="{d_name}" data-volume="{vol}">
            <div class="card-header">
                <div class="header-left">
                    <span class="draft-volume">[{vol}]</span>
                    <h3 class="draft-name">{d_name}</h3>
                </div>
                <div class="header-badges">
                    {active_badge}
                    {lock_badge}
                    {milestone_badge}
                </div>
            </div>

            <div class="card-body">
                <div class="stats-grid">
                    <div class="stat-box">
                        <span class="stat-label">Word Count</span>
                        <span class="stat-val">{words:,}</span>
                    </div>
                    <div class="stat-box">
                        <span class="stat-label">Chapters</span>
                        <span class="stat-val">{chaps}</span>
                    </div>
                    <div class="stat-box">
                        <span class="stat-label">Lineage Parent</span>
                        <span class="stat-val parent-val">{parent}</span>
                    </div>
                    <div class="stat-box">
                        <span class="stat-label">Created</span>
                        <span class="stat-val">{created}</span>
                    </div>
                </div>

                {f'<div class="draft-notes"><strong>Notes:</strong> {notes}</div>' if notes else ''}

                <details class="chapter-accordion">
                    <summary>View Chapter Breakdown ({chaps} chapters)</summary>
                    <table class="chapter-table">
                        <tbody>
                            {chap_table_html}
                        </tbody>
                    </table>
                </details>
            </div>
        </div>
        """
        cards_html_parts.append(card_html)

        # Tree Visual Node
        active_tree_class = "tree-node-active" if is_active else ""
        locked_tree_icon = "🔒" if is_locked else "🔓"
        tree_node_html = f"""
        <div class="tree-node {active_tree_class}" onclick="document.getElementById('draft-{html.escape(d.get('name', ''))}').scrollIntoView({{behavior: 'smooth', block: 'center'}})">
            <div class="tree-node-header">
                <span class="tree-icon">{locked_tree_icon}</span>
                <span class="tree-name">{d_name}</span>
            </div>
            <div class="tree-node-meta">
                <span class="tree-words">{words:,} w</span> • <span>{milestone}</span>
            </div>
            {f'<div class="tree-parent-arrow">↳ from {parent}</div>' if parent != 'Root Genesis' else '<div class="tree-parent-arrow">🌱 Genesis</div>'}
        </div>
        """
        tree_nodes_parts.append(tree_node_html)

    cards_joined = "\n".join(cards_html_parts)
    tree_joined = "\n".join(tree_nodes_parts)

    # Active Hero summary
    if active_draft_dict:
        act_name = html.escape(active_draft_dict.get("name", "Unknown"))
        act_words = active_draft_dict.get("word_count", 0)
        act_chaps = active_draft_dict.get("chapter_count", 0)
        act_milestone = html.escape(active_draft_dict.get("milestone", "Draft"))
        act_locked = active_draft_dict.get("locked", False)
        act_lock_text = "🔒 Locked (Immutable)" if act_locked else "🔓 Active (Editable)"
        act_parent = html.escape(active_draft_dict.get("parent_draft") or "Root")
    else:
        act_name = "None"
        act_words = 0
        act_chaps = 0
        act_milestone = "Draft"
        act_lock_text = "None"
        act_parent = "None"

    theme_css = get_theme_engine_css()
    theme_js = get_theme_engine_js()
    control_center_html = get_theme_control_center_html()

    html_content = f"""<!DOCTYPE html>
<html lang="en" data-theme="sovereign-dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="{_CSP}">
    <title>{safe_title} — Manuscript Draft Manager | Ars Arcanum</title>
    <style>
{theme_css}
        :root {{
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-card: #182234;
            --bg-accent: #334155;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --border: #334155;
            --accent: #6366f1;
            --accent-glow: rgba(99, 102, 241, 0.35);
            --success: #22c55e;
            --success-glow: rgba(34, 197, 94, 0.25);
            --warning: #f59e0b;
            --danger: #ef4444;
            --danger-glow: rgba(239, 68, 68, 0.2);
            --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            --font-mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            background-color: var(--bg-primary);
            color: var(--text-primary);
            font-family: var(--font-sans);
            line-height: 1.6;
            padding: 2rem;
            min-height: 100vh;
        }}

        .container {{
            max-width: 1280px;
            margin: 0 auto;
        }}

        /* Header */
        header {{
            margin-bottom: 2rem;
            border-bottom: 1px solid var(--border);
            padding-bottom: 1.5rem;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            flex-wrap: wrap;
            gap: 1rem;
        }}

        .title-area h1 {{
            font-size: 2.2rem;
            font-weight: 700;
            letter-spacing: -0.025em;
            color: #ffffff;
        }}

        .title-area .subtitle {{
            color: var(--text-secondary);
            font-size: 1rem;
            margin-top: 0.25rem;
        }}

        .meta-pills {{
            display: flex;
            gap: 0.75rem;
            flex-wrap: wrap;
        }}

        .pill {{
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            padding: 0.4rem 0.85rem;
            border-radius: 9999px;
            font-size: 0.85rem;
            font-family: var(--font-mono);
            color: var(--text-secondary);
        }}

        /* Hero Banner */
        .hero-banner {{
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.9));
            border: 1px solid rgba(99, 102, 241, 0.4);
            border-radius: 12px;
            padding: 1.5rem 2rem;
            margin-bottom: 2.5rem;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1.5rem;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5), 0 0 15px var(--accent-glow);
        }}

        .hero-stat {{
            display: flex;
            flex-direction: column;
        }}

        .hero-label {{
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
            margin-bottom: 0.25rem;
        }}

        .hero-val {{
            font-size: 1.6rem;
            font-weight: 700;
            color: #ffffff;
        }}

        .hero-val.active-highlight {{
            color: var(--success);
            text-shadow: 0 0 10px var(--success-glow);
        }}

        /* Lineage Section */
        .section-title {{
            font-size: 1.4rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: #ffffff;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .tree-container {{
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 2.5rem;
            overflow-x: auto;
        }}

        .tree-nodes-wrapper {{
            display: flex;
            gap: 1.5rem;
            align-items: stretch;
            flex-wrap: wrap;
        }}

        .tree-node {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1rem 1.25rem;
            min-width: 200px;
            cursor: pointer;
            transition: all 0.2s ease;
            position: relative;
        }}

        .tree-node:hover {{
            transform: translateY(-2px);
            border-color: var(--accent);
            box-shadow: 0 4px 12px var(--accent-glow);
        }}

        .tree-node.tree-node-active {{
            border-color: var(--success);
            box-shadow: 0 0 12px var(--success-glow);
        }}

        .tree-node-header {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-weight: 600;
            font-size: 1.1rem;
            margin-bottom: 0.35rem;
        }}

        .tree-node-meta {{
            font-size: 0.85rem;
            color: var(--text-secondary);
            margin-bottom: 0.5rem;
        }}

        .tree-parent-arrow {{
            font-size: 0.75rem;
            color: var(--text-muted);
            font-family: var(--font-mono);
        }}

        /* Filter Controls */
        .filter-bar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
            flex-wrap: wrap;
            gap: 1rem;
        }}

        .search-box {{
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            color: var(--text-primary);
            padding: 0.5rem 1rem;
            border-radius: 6px;
            font-size: 0.9rem;
            min-width: 260px;
        }}

        .search-box:focus {{
            outline: none;
            border-color: var(--accent);
        }}

        /* Draft Cards Grid */
        .draft-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
            gap: 1.5rem;
        }}

        .draft-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.5rem;
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
        }}

        .draft-card.card-is-active {{
            border-color: var(--success);
            box-shadow: 0 0 15px var(--success-glow);
        }}

        .draft-card.card-locked {{
            background: linear-gradient(180deg, var(--bg-card) 0%, rgba(30, 41, 59, 0.6) 100%);
        }}

        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 1rem;
            border-bottom: 1px solid var(--border);
            padding-bottom: 0.75rem;
        }}

        .draft-volume {{
            font-size: 0.75rem;
            font-family: var(--font-mono);
            color: var(--accent);
            text-transform: uppercase;
        }}

        .draft-name {{
            font-size: 1.3rem;
            font-weight: 700;
            color: #ffffff;
        }}

        .header-badges {{
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            gap: 0.35rem;
        }}

        .badge-active {{
            font-size: 0.75rem;
            font-weight: 600;
            color: var(--success);
            background: var(--success-glow);
            border: 1px solid var(--success);
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
        }}

        .badge-lock {{
            font-size: 0.75rem;
            font-weight: 600;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
        }}

        .badge-lock.locked {{
            color: var(--danger);
            background: var(--danger-glow);
            border: 1px solid var(--danger);
        }}

        .badge-lock.unlocked {{
            color: var(--text-secondary);
            background: var(--bg-secondary);
            border: 1px solid var(--border);
        }}

        .badge-milestone {{
            font-size: 0.75rem;
            font-weight: 600;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            border: 1px solid transparent;
            font-family: var(--font-mono);
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.75rem;
            margin-bottom: 1rem;
        }}

        .stat-box {{
            background: var(--bg-secondary);
            padding: 0.6rem 0.8rem;
            border-radius: 6px;
        }}

        .stat-label {{
            display: block;
            font-size: 0.75rem;
            color: var(--text-muted);
            text-transform: uppercase;
        }}

        .stat-val {{
            font-size: 1.1rem;
            font-weight: 600;
            color: #ffffff;
        }}

        .stat-val.parent-val {{
            font-size: 0.95rem;
            font-family: var(--font-mono);
            color: var(--text-secondary);
        }}

        .draft-notes {{
            font-size: 0.9rem;
            color: var(--text-secondary);
            background: var(--bg-secondary);
            border-left: 3px solid var(--accent);
            padding: 0.6rem 0.8rem;
            border-radius: 0 6px 6px 0;
            margin-bottom: 1rem;
        }}

        /* Chapter Accordion */
        .chapter-accordion summary {{
            font-size: 0.85rem;
            color: var(--text-secondary);
            cursor: pointer;
            padding: 0.4rem 0;
            user-select: none;
        }}

        .chapter-accordion summary:hover {{
            color: var(--text-primary);
        }}

        .chapter-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 0.5rem;
            font-size: 0.85rem;
        }}

        .chapter-table td {{
            padding: 0.35rem 0.5rem;
            border-bottom: 1px solid var(--border);
        }}

        .chapter-table tr:last-child td {{
            border-bottom: none;
        }}

        .ch-title {{
            color: var(--text-primary);
        }}

        .ch-words {{
            text-align: right;
            color: var(--text-muted);
            font-family: var(--font-mono);
        }}

        .empty-chaps {{
            text-align: center;
            color: var(--text-muted);
            font-style: italic;
        }}

        /* Footer */
        footer {{
            margin-top: 4rem;
            border-top: 1px solid var(--border);
            padding-top: 1.5rem;
            text-align: center;
            color: var(--text-muted);
            font-size: 0.85rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="title-area">
                <h1>{safe_title}</h1>
                <div class="subtitle">
                    Ars Arcanum Sovereign Manuscript Draft Management & Lineage
                    {f' • Universe: {safe_univ}' if safe_univ else ''}
                    {f' • World: {safe_world}' if safe_world else ''}
                </div>
            </div>
            <div class="meta-pills">
                <span class="pill">📁 {total_drafts} Total Drafts</span>
                <span class="pill">🔒 {locked_count} Locked</span>
                <span class="pill">📝 {total_words:,} Lifetime Words</span>
                {control_center_html}
            </div>
        </header>

        <!-- Hero Active Draft Overview -->
        <section class="hero-banner">
            <div class="hero-stat">
                <span class="hero-label">Active Workstream Draft</span>
                <span class="hero-val active-highlight">🟢 {act_name}</span>
            </div>
            <div class="hero-stat">
                <span class="hero-label">Active Milestone</span>
                <span class="hero-val">{act_milestone}</span>
            </div>
            <div class="hero-stat">
                <span class="hero-label">Active Word Count</span>
                <span class="hero-val">{act_words:,} words</span>
            </div>
            <div class="hero-stat">
                <span class="hero-label">Active Chapters</span>
                <span class="hero-val">{act_chaps} chapters</span>
            </div>
            <div class="hero-stat">
                <span class="hero-label">Lineage Parent</span>
                <span class="hero-val" style="font-size: 1.1rem; margin-top: 0.35rem; font-family: var(--font-mono);">{act_parent}</span>
            </div>
            <div class="hero-stat">
                <span class="hero-label">Lock & Security State</span>
                <span class="hero-val" style="font-size: 1.1rem; margin-top: 0.35rem;">{act_lock_text}</span>
            </div>

        </section>

        <!-- Visual Draft Lineage Tree -->
        <section>
            <h2 class="section-title">🌿 Version Lineage DAG & Revision Branches</h2>
            <div class="tree-container">
                <div class="tree-nodes-wrapper">
                    {tree_joined}
                </div>
            </div>
        </section>

        <!-- All Drafts Detailed Grid -->
        <section>
            <div class="filter-bar">
                <h2 class="section-title" style="margin-bottom: 0;">📚 All Manuscript Revisions & Drafts</h2>
                <input type="text" id="draftSearch" class="search-box" placeholder="Filter drafts by name or volume..." oninput="filterDrafts()">
            </div>
            <div class="draft-grid" id="draftsGrid">
                {cards_joined}
            </div>
        </section>

        <footer>
            Ars Arcanum Craft Studio • 100% Offline Sovereign Intellectual Property Protection • No External CDN Telemetry
        </footer>
    </div>

    <script>
        function filterDrafts() {{
            var query = document.getElementById('draftSearch').value.toLowerCase();
            var cards = document.querySelectorAll('.draft-card');
            cards.forEach(function(card) {{
                var name = card.getAttribute('data-name').toLowerCase();
                var vol = card.getAttribute('data-volume').toLowerCase();
                if (name.indexOf(query) !== -1 || vol.indexOf(query) !== -1) {{
                    card.style.display = 'block';
                }} else {{
                    card.style.display = 'none';
                }}
            }});
        }}
    </script>
    <script>
{theme_js}
    </script>
</body>
</html>
"""
    if output_path:
        out_p = Path(output_path).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)
        atomic_write(out_p, html_content)
        logger.info("Draft Manager dashboard written to %s", out_p)

    return html_content


__all__ = [
    "generate_draft_dashboard_html",
]
