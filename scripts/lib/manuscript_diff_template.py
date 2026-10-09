#!/usr/bin/env python3
"""
Ars Arcanum Manuscript Diff HTML Presentation Template
======================================================
scripts/lib/manuscript_diff_template.py

Generates standalone, CSP-compliant offline HTML Redline Changelog reports
with chapter navigation sidebar, word metrics, search, light/dark mode, and
accessible deletion/insertion highlighting.
"""

from __future__ import annotations

import html
from typing import Any


def render_manuscript_diff_html(
    summary: dict[str, Any],
    chapters: list[dict[str, Any]],
    label_a: str = "Draft 1",
    label_b: str = "Draft 2",
) -> str:
    """
    Generates accessible, standalone HTML Redline Changelog.
    Includes chapter sidebar, word counts, search, light/dark mode, and inline/side-by-side view.
    """
    esc_label_a = html.escape(label_a)
    esc_label_b = html.escape(label_b)
    tot_a = summary.get("total_words_a", 0)
    tot_b = summary.get("total_words_b", 0)
    add_w = summary.get("added_words", 0)
    del_w = summary.get("deleted_words", 0)
    net_w = summary.get("net_change", 0)
    sim_pct = round(summary.get("similarity_ratio", 0.0) * 100, 1)
    net_sign = "+" if net_w >= 0 else ""

    # Build sidebar chapter list and main content
    sidebar_items: list[str] = []
    chapter_sections: list[str] = []

    for idx, chap in enumerate(chapters, 1):
        chap_id = f"chap-{idx}"
        esc_title = html.escape(chap["title"])
        esc_rel = html.escape(chap["rel_path"])
        c_add = chap["added_words"]
        c_del = chap["deleted_words"]
        c_net = chap["net_change"]
        c_net_sign = "+" if c_net >= 0 else ""
        c_sim = round(chap["similarity"] * 100, 1)

        sidebar_items.append(f"""
        <a href="#{chap_id}" class="nav-item" data-target="{chap_id}">
            <div class="nav-title">{esc_title}</div>
            <div class="nav-stats">
                <span class="pill-add">+{c_add}</span>
                <span class="pill-del">-{c_del}</span>
                <span class="pill-net">{c_net_sign}{c_net} w</span>
            </div>
        </a>
        """)

        # Render redline tokens into formatted HTML paragraphs
        inline_html: list[str] = []
        for chunk in chap["chunks"]:
            tag = chunk["tag"]
            raw_txt = chunk["text"]
            esc_txt = html.escape(raw_txt)

            if tag == "insert":
                paragraphs = esc_txt.split("\n\n")
                ins_paras = [f'<ins class="diff-ins" title="Added in {esc_label_b}">{p.replace(chr(10), "<br/>")}</ins>' for p in paragraphs]
                inline_html.append("</p><p>".join(ins_paras))
            elif tag == "delete":
                paragraphs = esc_txt.split("\n\n")
                del_paras = [f'<del class="diff-del" title="Cut from {esc_label_a}">{p.replace(chr(10), "<br/>")}</del>' for p in paragraphs]
                inline_html.append("</p><p>".join(del_paras))
            else:
                paragraphs = esc_txt.split("\n\n")
                eq_paras = [f'<span class="diff-eq">{p.replace(chr(10), "<br/>")}</span>' for p in paragraphs]
                inline_html.append("</p><p>".join(eq_paras))

        body_prose = "".join(inline_html)
        # Wrap in paragraphs
        if not body_prose.startswith("<p>"):
            body_prose = "<p>" + body_prose + "</p>"

        chapter_sections.append(f"""
        <section id="{chap_id}" class="chapter-card">
            <header class="chapter-header">
                <div class="chapter-meta">
                    <h2>{esc_title}</h2>
                    <span class="chapter-path">{esc_rel}</span>
                </div>
                <div class="chapter-pills">
                    <span class="badge badge-words">{chap['words_a']} &rarr; {chap['words_b']} words</span>
                    <span class="badge badge-add">+{c_add} added</span>
                    <span class="badge badge-del">-{c_del} cut</span>
                    <span class="badge badge-sim">{c_sim}% match</span>
                </div>
            </header>
            <div class="prose-content">
                {body_prose}
            </div>
        </section>
        """)

    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manuscript Redline Diff: {esc_label_a} vs {esc_label_b} | Ars Arcanum</title>
    <style>
        :root {{
            --bg-body: #f8f9fa;
            --bg-surface: #ffffff;
            --bg-sidebar: #f1f3f5;
            --border-color: #e9ecef;
            --text-main: #212529;
            --text-muted: #6c757d;
            --primary: #495057;
            --font-prose: "EB Garamond", "Libertinus Serif", "Georgia", serif;
            --font-ui: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;

            /* Accessible Redline Pastel Highlights */
            --del-bg: #f8d7da;
            --del-color: #721c24;
            --del-border: #f5c6cb;
            --ins-bg: #d4edda;
            --ins-color: #155724;
            --ins-border: #c3e6cb;
        }}

        [data-theme="dark"] {{
            --bg-body: #121416;
            --bg-surface: #1a1d20;
            --bg-sidebar: #15181a;
            --border-color: #2c3136;
            --text-main: #e9ecef;
            --text-muted: #adb5bd;
            --primary: #dee2e6;

            /* Dark Mode Accessible Pastel Highlights */
            --del-bg: #3a1e22;
            --del-color: #f8d7da;
            --del-border: #842029;
            --ins-bg: #1e3a24;
            --ins-color: #d4edda;
            --ins-border: #0f5132;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: var(--font-ui);
            background-color: var(--bg-body);
            color: var(--text-main);
            display: flex;
            height: 100vh;
            overflow: hidden;
        }}

        /* App Sidebar */
        .sidebar {{
            width: 320px;
            background-color: var(--bg-sidebar);
            border-right: 1px solid var(--border-color);
            display: flex;
            flex-direction: column;
            flex-shrink: 0;
        }}

        .sidebar-header {{
            padding: 20px;
            border-bottom: 1px solid var(--border-color);
        }}

        .sidebar-header h1 {{
            font-size: 1.1rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            margin-bottom: 4px;
        }}

        .sidebar-header .subtitle {{
            font-size: 0.8rem;
            color: var(--text-muted);
        }}

        .search-box {{
            padding: 12px 20px;
            border-bottom: 1px solid var(--border-color);
        }}

        .search-box input {{
            width: 100%;
            padding: 8px 12px;
            border-radius: 6px;
            border: 1px solid var(--border-color);
            background-color: var(--bg-surface);
            color: var(--text-main);
            font-size: 0.85rem;
            outline: none;
        }}

        .search-box input:focus {{
            border-color: #80bdff;
        }}

        .nav-list {{
            flex: 1;
            overflow-y: auto;
            padding: 10px;
        }}

        .nav-item {{
            display: block;
            padding: 10px 14px;
            border-radius: 6px;
            color: var(--text-main);
            text-decoration: none;
            margin-bottom: 4px;
            transition: background 0.15s ease;
        }}

        .nav-item:hover {{
            background-color: var(--bg-surface);
        }}

        .nav-title {{
            font-size: 0.9rem;
            font-weight: 600;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .nav-stats {{
            display: flex;
            gap: 6px;
            font-size: 0.75rem;
            margin-top: 4px;
        }}

        .pill-add {{ color: #28a745; font-weight: 600; }}
        .pill-del {{ color: #dc3545; font-weight: 600; }}
        .pill-net {{ color: var(--text-muted); }}

        /* Main Workspace Content */
        .main-workspace {{
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }}

        /* Executive Header */
        .executive-header {{
            background-color: var(--bg-surface);
            border-bottom: 1px solid var(--border-color);
            padding: 16px 32px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .metrics-grid {{
            display: flex;
            gap: 24px;
        }}

        .metric-card {{
            display: flex;
            flex-direction: column;
        }}

        .metric-label {{
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
            font-weight: 600;
        }}

        .metric-value {{
            font-size: 1.25rem;
            font-weight: 700;
        }}

        .metric-value.added {{ color: #28a745; }}
        .metric-value.deleted {{ color: #dc3545; }}

        .toolbar {{
            display: flex;
            gap: 10px;
        }}

        .btn {{
            padding: 8px 14px;
            border-radius: 6px;
            border: 1px solid var(--border-color);
            background-color: var(--bg-surface);
            color: var(--text-main);
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.15s ease;
        }}

        .btn:hover {{
            background-color: var(--bg-body);
        }}

        /* Manuscript Scroll Area */
        .diff-scroll-area {{
            flex: 1;
            overflow-y: auto;
            padding: 32px;
            display: flex;
            justify-content: center;
        }}

        .manuscript-container {{
            width: 100%;
            max-width: 820px;
        }}

        /* Chapter Cards */
        .chapter-card {{
            background-color: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            margin-bottom: 32px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.02);
            overflow: hidden;
        }}

        .chapter-header {{
            padding: 18px 24px;
            border-bottom: 1px solid var(--border-color);
            background-color: var(--bg-body);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .chapter-meta h2 {{
            font-size: 1.15rem;
            font-weight: 700;
        }}

        .chapter-path {{
            font-size: 0.8rem;
            color: var(--text-muted);
            font-family: monospace;
        }}

        .chapter-pills {{
            display: flex;
            gap: 8px;
        }}

        .badge {{
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
        }}

        .badge-words {{ background-color: var(--border-color); color: var(--text-main); }}
        .badge-add {{ background-color: var(--ins-bg); color: var(--ins-color); }}
        .badge-del {{ background-color: var(--del-bg); color: var(--del-color); }}
        .badge-sim {{ background-color: var(--bg-surface); border: 1px solid var(--border-color); color: var(--text-muted); }}

        /* Prose Typography */
        .prose-content {{
            padding: 32px 36px;
            font-family: var(--font-prose);
            font-size: 1.18rem;
            line-height: 1.8;
            color: var(--text-main);
        }}

        .prose-content p {{
            margin-bottom: 1.5em;
            text-indent: 1.5em;
        }}

        .prose-content p:first-of-type {{
            text-indent: 0;
        }}

        /* Redline Highlights */
        ins.diff-ins {{
            background-color: var(--ins-bg);
            color: var(--ins-color);
            text-decoration: none;
            padding: 1px 2px;
            border-radius: 2px;
            font-weight: 500;
        }}

        del.diff-del {{
            background-color: var(--del-bg);
            color: var(--del-color);
            text-decoration: line-through;
            opacity: 0.85;
            padding: 1px 2px;
            border-radius: 2px;
        }}

        /* Changelog-Only / Highlights Filter Mode */
        body.changelog-mode span.diff-eq {{
            display: none;
        }}
        body.changelog-mode .prose-content p {{
            text-indent: 0;
            margin-bottom: 0.8em;
        }}
    </style>
</head>
<body>
    <!-- Navigation Sidebar -->
    <aside class="sidebar">
        <div class="sidebar-header">
            <h1>Manuscript Changelog</h1>
            <div class="subtitle">{esc_label_a} &rarr; {esc_label_b}</div>
        </div>
        <div class="search-box">
            <input type="text" id="searchInput" placeholder="Filter chapters..." autocomplete="off">
        </div>
        <nav class="nav-list" id="navList">
            {"".join(sidebar_items)}
        </nav>
    </aside>

    <!-- Main Workspace -->
    <main class="main-workspace">
        <header class="executive-header">
            <div class="metrics-grid">
                <div class="metric-card">
                    <span class="metric-label">Draft 1 Words</span>
                    <span class="metric-value">{tot_a:,}</span>
                </div>
                <div class="metric-card">
                    <span class="metric-label">Draft 2 Words</span>
                    <span class="metric-value">{tot_b:,}</span>
                </div>
                <div class="metric-card">
                    <span class="metric-label">Words Added</span>
                    <span class="metric-value added">+{add_w:,}</span>
                </div>
                <div class="metric-card">
                    <span class="metric-label">Words Cut</span>
                    <span class="metric-value deleted">-{del_w:,}</span>
                </div>
                <div class="metric-card">
                    <span class="metric-label">Net Delta</span>
                    <span class="metric-value">{net_sign}{net_w:,}</span>
                </div>
                <div class="metric-card">
                    <span class="metric-label">Similarity</span>
                    <span class="metric-value">{sim_pct}%</span>
                </div>
            </div>
            <div class="toolbar">
                <button class="btn" id="btnToggleChangelog">Highlight Changes Only</button>
                <button class="btn" id="btnToggleTheme">Theme: Light</button>
            </div>
        </header>

        <div class="diff-scroll-area">
            <div class="manuscript-container" id="manuscriptContainer">
                {"".join(chapter_sections)}
            </div>
        </div>
    </main>

    <script>
        // Dark / Light Theme Toggle
        const btnTheme = document.getElementById('btnToggleTheme');
        let currentTheme = 'light';

        btnTheme.addEventListener('click', () => {{
            currentTheme = currentTheme === 'light' ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', currentTheme);
            btnTheme.textContent = 'Theme: ' + (currentTheme === 'dark' ? 'Dark' : 'Light');
        }});

        // Changelog mode toggle
        const btnChangelog = document.getElementById('btnToggleChangelog');
        btnChangelog.addEventListener('click', () => {{
            document.body.classList.toggle('changelog-mode');
            const active = document.body.classList.contains('changelog-mode');
            btnChangelog.textContent = active ? 'Show Full Prose' : 'Highlight Changes Only';
        }});

        // Live search filter
        const searchInput = document.getElementById('searchInput');
        searchInput.addEventListener('input', (e) => {{
            const query = e.target.value.toLowerCase().trim();
            document.querySelectorAll('.chapter-card').forEach(card => {{
                const text = card.textContent.toLowerCase();
                card.style.display = text.includes(query) ? 'block' : 'none';
            }});
        }});
    </script>
</body>
</html>
"""
