#!/usr/bin/env python3
"""
Ars Arcanum Batch Importer & Migration Visual Studio (scripts/lib/importer_template.py)
====================================================================================
Pure-Python, zero-dependency, offline CSP-compliant HTML5 visual studio and dashboard
for manuscript ingestion, Scrivener binder inspection, EPUB chapter extraction,
lore routing visualization, and safe draft collision telemetry.
"""

from __future__ import annotations

import html
import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger("arcanum.importer_template")

try:
    from lib._bootstrap import atomic_write
except ImportError:
    from _bootstrap import atomic_write  # type: ignore[no-redef]

_CSP = (
    "default-src 'none'; "
    "style-src 'unsafe-inline'; "
    "script-src 'unsafe-inline'; "
    "img-src data:; "
    "media-src data: blob:;"
)


def render_import_studio_html(
    report: dict[str, Any],
    output_path: Path | str,
) -> Path:
    """
    Renders a standalone, interactive offline HTML5 Visual Migration Studio.
    """
    out_path = Path(output_path).resolve()

    title = html.escape(str(report.get("title", "Imported Project")))
    author = html.escape(str(report.get("author", "Author")))
    source_format = html.escape(str(report.get("source_format", "Unknown")).upper())
    source_path = html.escape(str(report.get("source_path", "")))
    dest_path = html.escape(str(report.get("dest_path", "")))
    book = html.escape(str(report.get("book", "Book-01")))
    draft = html.escape(str(report.get("draft", "Draft-01")))
    total_words = int(report.get("total_words", 0))
    total_chapters = int(report.get("chapters_imported", 0))
    lore_entities = report.get("lore_entities", [])
    total_lore = len(lore_entities)
    collision_mode = html.escape(str(report.get("collision_resolution", "Sequential (Non-Destructive)")))
    is_dry_run = bool(report.get("dry_run", False))

    chapters_data = report.get("chapters", [])
    report_json_escaped = html.escape(json.dumps(report, indent=2))

    # Build Chapter Cards HTML
    chapter_cards = []
    for ch in chapters_data:
        ch_idx = ch.get("index", 1)
        ch_title = html.escape(str(ch.get("title", f"Chapter {ch_idx}")))
        ch_file = html.escape(str(ch.get("filename", f"{ch_idx:02d}_Chapter.md")))
        ch_words = int(ch.get("word_count", 0))
        ch_synopsis = html.escape(str(ch.get("synopsis", "")).strip() or "No synopsis index card.")
        ch_pov = html.escape(str(ch.get("pov", "")).strip())

        pov_badge = f'<span class="badge pov-badge">👤 POV: {ch_pov}</span>' if ch_pov else ""

        card = f"""
        <div class="card chapter-card" data-idx="{ch_idx}">
            <div class="card-header">
                <div class="card-title-group">
                    <span class="chapter-number">#{ch_idx:02d}</span>
                    <span class="chapter-title">{ch_title}</span>
                </div>
                <div class="badges">
                    {pov_badge}
                    <span class="badge words-badge">📝 {ch_words:,} words</span>
                </div>
            </div>
            <div class="card-meta">
                <code>{book}/{draft}/{ch_file}</code>
            </div>
            <div class="card-synopsis">
                <span class="synopsis-label">📌 Synopsis:</span>
                <p>{ch_synopsis}</p>
            </div>
        </div>
        """
        chapter_cards.append(card)

    # Build Lore Dossiers HTML
    lore_cards = []
    for lore in lore_entities:
        l_name = html.escape(str(lore.get("name", "Unknown Entity")))
        l_type = html.escape(str(lore.get("type", "General")).capitalize())
        l_cat = html.escape(str(lore.get("category", "World")))
        l_path = html.escape(str(lore.get("rel_path", "")))
        l_synopsis = html.escape(str(lore.get("synopsis", "")).strip() or "Auto-extracted from binder.")

        type_icon = "👤" if "char" in l_type.lower() else ("🗺️" if "loc" in l_type.lower() or "place" in l_type.lower() else "📜")

        card = f"""
        <div class="card lore-card">
            <div class="card-header">
                <div class="card-title-group">
                    <span class="lore-icon">{type_icon}</span>
                    <span class="lore-name">{l_name}</span>
                </div>
                <span class="badge lore-badge">{l_type}</span>
            </div>
            <div class="card-meta">
                <code>World/{l_cat}/{l_path}</code>
            </div>
            <div class="card-synopsis">
                <p>{l_synopsis}</p>
            </div>
        </div>
        """
        lore_cards.append(card)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta http-equiv="Content-Security-Policy" content="{_CSP}">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ars Arcanum — Batch Importer & Migration Visual Studio</title>
    <style>
        :root {{
            --bg: #090d16;
            --surface: #111827;
            --surface-elevated: #1f2937;
            --border: #374151;
            --border-light: #4b5563;
            --text: #f9fafb;
            --text-secondary: #9ca3af;
            --accent-primary: #38bdf8;
            --accent-glow: rgba(56, 189, 248, 0.2);
            --accent-green: #34d399;
            --accent-amber: #fbbf24;
            --accent-purple: #c084fc;
            --accent-rose: #f43f5e;
            --radius-sm: 6px;
            --radius-md: 10px;
            --radius-lg: 16px;
            --shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.5);
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.5;
            padding: 2rem 1.5rem;
            min-height: 100vh;
        }}

        .studio-container {{
            max-width: 1280px;
            margin: 0 auto;
        }}

        /* Header Bar */
        .studio-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1.5rem;
            background: linear-gradient(135deg, rgba(31, 41, 55, 0.9) 0%, rgba(17, 24, 39, 0.95) 100%);
            border: 1px solid var(--border);
            padding: 1.75rem 2rem;
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow);
            margin-bottom: 2rem;
        }}

        .header-title-block h1 {{
            font-size: 1.85rem;
            font-weight: 800;
            background: linear-gradient(135deg, #e0f2fe 0%, #38bdf8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}

        .header-subtitle {{
            color: var(--text-secondary);
            font-size: 0.95rem;
            margin-top: 0.35rem;
        }}

        .mode-tag {{
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.35rem 0.85rem;
            border-radius: 9999px;
            font-size: 0.8rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .mode-tag.live {{
            background: rgba(52, 211, 153, 0.15);
            color: var(--accent-green);
            border: 1px solid rgba(52, 211, 153, 0.3);
        }}

        .mode-tag.dry-run {{
            background: rgba(251, 191, 36, 0.15);
            color: var(--accent-amber);
            border: 1px solid rgba(251, 191, 36, 0.3);
        }}

        /* Metrics Row */
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1.25rem;
            margin-bottom: 2rem;
        }}

        .metric-card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            padding: 1.25rem 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 0.4rem;
            transition: transform 0.2s ease, border-color 0.2s ease;
        }}

        .metric-card:hover {{
            transform: translateY(-2px);
            border-color: var(--accent-primary);
        }}

        .metric-label {{
            font-size: 0.75rem;
            font-weight: 700;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .metric-value {{
            font-size: 1.85rem;
            font-weight: 800;
            color: var(--accent-primary);
        }}

        .metric-subtext {{
            font-size: 0.8rem;
            color: var(--text-secondary);
        }}

        /* Studio Navigation Tabs */
        .tabs-nav {{
            display: flex;
            gap: 0.75rem;
            border-bottom: 1px solid var(--border);
            margin-bottom: 2rem;
            padding-bottom: 0.5rem;
        }}

        .tab-btn {{
            background: transparent;
            border: none;
            color: var(--text-secondary);
            font-size: 0.95rem;
            font-weight: 600;
            padding: 0.6rem 1.2rem;
            border-radius: var(--radius-sm);
            cursor: pointer;
            transition: all 0.2s ease;
        }}

        .tab-btn:hover {{
            color: var(--text);
            background: var(--surface-elevated);
        }}

        .tab-btn.active {{
            color: var(--accent-primary);
            background: rgba(56, 189, 248, 0.12);
            border-bottom: 2px solid var(--accent-primary);
        }}

        /* Tab Content Panels */
        .tab-pane {{
            display: none;
        }}

        .tab-pane.active {{
            display: block;
        }}

        /* Target Manifest Overview */
        .manifest-summary {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            padding: 1.5rem;
            margin-bottom: 2rem;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.25rem;
        }}

        .manifest-row {{
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
        }}

        .manifest-row-label {{
            font-size: 0.75rem;
            font-weight: 700;
            color: var(--text-secondary);
            text-transform: uppercase;
        }}

        .manifest-row-value {{
            font-size: 0.95rem;
            font-weight: 600;
            color: var(--text);
            word-break: break-all;
        }}

        /* Card Listings */
        .section-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.25rem;
        }}

        .section-title {{
            font-size: 1.25rem;
            font-weight: 700;
            color: #f3f4f6;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .card-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
            gap: 1.25rem;
            margin-bottom: 2.5rem;
        }}

        .card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            padding: 1.25rem;
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
            transition: all 0.2s ease;
        }}

        .card:hover {{
            border-color: var(--border-light);
            box-shadow: 0 4px 15px -2px rgba(0, 0, 0, 0.4);
        }}

        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 0.75rem;
        }}

        .card-title-group {{
            display: flex;
            align-items: baseline;
            gap: 0.6rem;
            flex: 1;
        }}

        .chapter-number {{
            font-size: 0.9rem;
            font-weight: 800;
            color: var(--accent-primary);
            background: rgba(56, 189, 248, 0.1);
            padding: 0.2rem 0.5rem;
            border-radius: var(--radius-sm);
        }}

        .chapter-title {{
            font-size: 1.05rem;
            font-weight: 700;
            color: #f9fafb;
        }}

        .badges {{
            display: flex;
            gap: 0.4rem;
            flex-wrap: wrap;
        }}

        .badge {{
            font-size: 0.75rem;
            font-weight: 600;
            padding: 0.2rem 0.55rem;
            border-radius: var(--radius-sm);
            background: var(--surface-elevated);
            color: var(--text-secondary);
            border: 1px solid var(--border);
        }}

        .badge.words-badge {{
            background: rgba(52, 211, 153, 0.1);
            color: var(--accent-green);
            border-color: rgba(52, 211, 153, 0.25);
        }}

        .badge.pov-badge {{
            background: rgba(192, 132, 252, 0.1);
            color: var(--accent-purple);
            border-color: rgba(192, 132, 252, 0.25);
        }}

        .badge.lore-badge {{
            background: rgba(251, 191, 36, 0.1);
            color: var(--accent-amber);
            border-color: rgba(251, 191, 36, 0.25);
        }}

        .card-meta {{
            font-size: 0.8rem;
            color: var(--text-secondary);
        }}

        .card-meta code {{
            background: rgba(0, 0, 0, 0.3);
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
            font-family: monospace;
            color: #cbd5e1;
        }}

        .card-synopsis {{
            background: rgba(0, 0, 0, 0.25);
            border-radius: var(--radius-sm);
            padding: 0.75rem;
            font-size: 0.85rem;
            color: #d1d5db;
            border-left: 3px solid var(--accent-primary);
        }}

        .synopsis-label {{
            font-size: 0.7rem;
            font-weight: 700;
            text-transform: uppercase;
            color: var(--text-secondary);
            display: block;
            margin-bottom: 0.25rem;
        }}

        .lore-icon {{
            font-size: 1.1rem;
        }}

        .lore-name {{
            font-size: 1.05rem;
            font-weight: 700;
            color: #f9fafb;
        }}

        .raw-json-block {{
            background: #000;
            color: #10b981;
            font-family: monospace;
            font-size: 0.85rem;
            padding: 1.5rem;
            border-radius: var(--radius-md);
            overflow-x: auto;
            max-height: 500px;
            border: 1px solid var(--border);
        }}

        /* Footer */
        .studio-footer {{
            border-top: 1px solid var(--border);
            padding-top: 1.5rem;
            margin-top: 3rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: var(--text-secondary);
            font-size: 0.85rem;
            flex-wrap: wrap;
            gap: 1rem;
        }}

        .footer-badge {{
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            background: var(--surface);
            padding: 0.3rem 0.75rem;
            border-radius: 9999px;
            border: 1px solid var(--border);
            font-weight: 600;
        }}
    </style>
</head>
<body>

<div class="studio-container">
    <!-- Header -->
    <header class="studio-header">
        <div class="header-title-block">
            <h1>⚡ Batch Importer & Migration Visual Studio</h1>
            <div class="header-subtitle">Sovereign Manuscript Ingestion, Scrivener Dual-Vault Extraction & Strict Splitting</div>
        </div>
        <div>
            {"<span class='mode-tag dry-run'>🔍 DRY-RUN PREVIEW</span>" if is_dry_run else "<span class='mode-tag live'>✓ MIGRATION COMMITTED</span>"}
        </div>
    </header>

    <!-- Metrics Row -->
    <section class="metrics-grid">
        <div class="metric-card">
            <span class="metric-label">Source Format</span>
            <span class="metric-value">{source_format}</span>
            <span class="metric-subtext">Detected Package Architecture</span>
        </div>
        <div class="metric-card">
            <span class="metric-label">Chapters Extracted</span>
            <span class="metric-value">{total_chapters}</span>
            <span class="metric-subtext">Strict Heading 1 / Spine Split</span>
        </div>
        <div class="metric-card">
            <span class="metric-label">Total Word Count</span>
            <span class="metric-value">{total_words:,}</span>
            <span class="metric-subtext">Pure Prose Tokenization</span>
        </div>
        <div class="metric-card">
            <span class="metric-label">World Lore Dossiers</span>
            <span class="metric-value">{total_lore}</span>
            <span class="metric-subtext">Characters & Locations Routed</span>
        </div>
    </section>

    <!-- Manifest Overview Card -->
    <section class="manifest-summary">
        <div class="manifest-row">
            <span class="manifest-row-label">Manuscript Title</span>
            <span class="manifest-row-value">{title} (by {author})</span>
        </div>
        <div class="manifest-row">
            <span class="manifest-row-label">Source Path</span>
            <span class="manifest-row-value"><code>{source_path}</code></span>
        </div>
        <div class="manifest-row">
            <span class="manifest-row-label">Target Destination Vault</span>
            <span class="manifest-row-value"><code>{dest_path}</code></span>
        </div>
        <div class="manifest-row">
            <span class="manifest-row-label">Volume & Target Draft</span>
            <span class="manifest-row-value">{book} / {draft}</span>
        </div>
        <div class="manifest-row">
            <span class="manifest-row-label">Collision Resolution Mode</span>
            <span class="manifest-row-value">{collision_mode}</span>
        </div>
    </section>

    <!-- Navigation Tabs -->
    <nav class="tabs-nav">
        <button class="tab-btn active" onclick="switchTab('chapters')">📖 Extracted Chapters ({total_chapters})</button>
        <button class="tab-btn" onclick="switchTab('lore')">🗺️ World Lore Dossiers ({total_lore})</button>
        <button class="tab-btn" onclick="switchTab('telemetry')">📊 Migration Telemetry (JSON)</button>
    </nav>

    <!-- Chapters Panel -->
    <section id="pane-chapters" class="tab-pane active">
        <div class="section-header">
            <h2 class="section-title">Chapter Manifest Breakdown</h2>
            <span style="color:var(--text-secondary);font-size:0.85rem;">Deterministic line-0 frontmatter injected</span>
        </div>
        <div class="card-grid">
            {"".join(chapter_cards) or "<div class='card'><p style='color:var(--text-secondary);'>No chapters detected.</p></div>"}
        </div>
    </section>

    <!-- Lore Panel -->
    <section id="pane-lore" class="tab-pane">
        <div class="section-header">
            <h2 class="section-title">World Lore & Entity Routing</h2>
            <span style="color:var(--text-secondary);font-size:0.85rem;">Routed to World/Characters & World/Locations</span>
        </div>
        <div class="card-grid">
            {"".join(lore_cards) or "<div class='card'><p style='color:var(--text-secondary);'>No auxiliary world lore dossiers detected in source.</p></div>"}
        </div>
    </section>

    <!-- Telemetry JSON Panel -->
    <section id="pane-telemetry" class="tab-pane">
        <div class="section-header">
            <h2 class="section-title">Machine-Readable Diagnostic Report</h2>
            <span style="color:var(--text-secondary);font-size:0.85rem;">Canonical JSON Sidecar</span>
        </div>
        <pre class="raw-json-block"><code>{report_json_escaped}</code></pre>
    </section>

    <!-- Footer -->
    <footer class="studio-footer">
        <div>
            Ars Arcanum (Scriptorium) Sovereign Authoring Operating System
        </div>
        <div class="footer-badge">
            🔒 100% Offline | Zero-Pip Guarantee | Grade A+
        </div>
    </footer>
</div>

<script>
    function switchTab(tabId) {{
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));

        const activePane = document.getElementById('pane-' + tabId);
        if (activePane) {{
            activePane.classList.add('active');
        }}

        if (event && event.target) {{
            event.target.classList.add('active');
        }}
    }}
</script>

</body>
</html>
"""
    atomic_write(out_path, html_content)
    logger.info("Rendered Visual Migration Studio at: %s", out_path)
    return out_path


__all__ = ["render_import_studio_html"]
