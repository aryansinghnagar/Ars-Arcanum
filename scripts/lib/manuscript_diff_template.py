#!/usr/bin/env python3
"""
Ars Arcanum Manuscript Diff Multi-Tab Editorial Studio Template
===============================================================
scripts/lib/manuscript_diff_template.py

Generates standalone, CSP-compliant offline HTML Multi-Tab Editorial Studio reports
with Unified Redline, Side-by-Side Split View, Excised Scraps Inspector, Chapter Churn
Telemetry, dark/light theme, live search, and accessible diff highlights.
"""

from __future__ import annotations

import html
import json
from typing import Any

try:
    from lib.ui_theme_engine import (
        get_theme_control_center_html,
        get_theme_engine_css,
        get_theme_engine_js,
    )
except ImportError:
    from ui_theme_engine import (  # type: ignore[no-redef]
        get_theme_control_center_html,
        get_theme_engine_css,
        get_theme_engine_js,
    )


def render_manuscript_diff_html(
    summary: dict[str, Any],
    chapters: list[dict[str, Any]],
    label_a: str = "Draft 1",
    label_b: str = "Draft 2",
    scraps: list[dict[str, Any]] | None = None,
    advisories: list[dict[str, Any]] | None = None,
) -> str:
    """
    Generates the standalone, 100% offline, CSP-isolated Multi-Tab Editorial Studio HTML document.
    """
    esc_label_a = html.escape(label_a)
    esc_label_b = html.escape(label_b)
    tot_a = summary.get("total_words_a", 0)
    tot_b = summary.get("total_words_b", 0)
    add_w = summary.get("added_words", 0)
    del_w = summary.get("deleted_words", 0)
    net_w = summary.get("net_change", 0)
    moved_w = summary.get("moved_words", 0)
    sim_pct = round(summary.get("similarity_ratio", 0.0) * 100, 1)
    net_sign = "+" if net_w >= 0 else ""
    gross_churn = round(((add_w + del_w) / max(tot_a, 1)) * 100, 1)

    all_scraps = scraps or summary.get("scraps", [])
    all_advisories = advisories or summary.get("advisories", [])

    # Build Sidebar and Content
    sidebar_items: list[str] = []
    unified_sections: list[str] = []
    split_sections: list[str] = []
    churn_rows: list[str] = []

    for idx, chap in enumerate(chapters, 1):
        chap_id = f"chap-{idx}"
        esc_title = html.escape(chap["title"])
        esc_rel = html.escape(chap.get("rel_path", f"Chapter {idx}"))
        c_add = chap.get("added_words", 0)
        c_del = chap.get("deleted_words", 0)
        c_net = chap.get("net_change", 0)
        c_moved = chap.get("moved_words", 0)
        c_net_sign = "+" if c_net >= 0 else ""
        c_sim = round(chap.get("similarity", 0.0) * 100, 1)
        w_a = chap.get("words_a", 0)
        w_b = chap.get("words_b", 0)
        c_churn = round(((c_add + c_del) / max(w_a, 1)) * 100, 1)

        # Churn classification tag
        if c_sim >= 96:
            status_tag = '<span class="status-badge pristine">Pristine / Polish</span>'
        elif c_churn > 80 or c_sim < 60:
            status_tag = '<span class="status-badge overhaul">Heavy Rewrite</span>'
        elif c_net > 300:
            status_tag = '<span class="status-badge expansion">Expansion</span>'
        elif c_net < -300:
            status_tag = '<span class="status-badge trimmed">Trimmed</span>'
        else:
            status_tag = '<span class="status-badge balanced">Balanced Churn</span>'

        # 1. Sidebar Nav Item
        sidebar_items.append(f"""
        <a href="#{chap_id}" class="nav-item" data-target="{chap_id}">
            <div class="nav-title">{esc_title}</div>
            <div class="nav-stats">
                <span class="pill-add">+{c_add}</span>
                <span class="pill-del">-{c_del}</span>
                <span class="pill-net">{c_net_sign}{c_net}w</span>
                <span class="pill-sim">{c_sim}%</span>
            </div>
        </a>
        """)

        # 2. Unified Inline Redline Content
        inline_html: list[str] = []
        chunks = chap.get("chunks", [])
        for chunk in chunks:
            tag = chunk.get("tag", "equal")
            raw_txt = chunk.get("text", "")
            esc_txt = html.escape(raw_txt)
            is_dialogue = bool('"' in raw_txt or '“' in raw_txt or '”' in raw_txt)
            diag_attr = ' data-dialogue="true"' if is_dialogue else ''

            if tag == "insert":
                paragraphs = esc_txt.split("\n\n")
                ins_paras = [f'<ins class="diff-ins"{diag_attr} title="Added in {esc_label_b}">{p.replace(chr(10), "<br/>")}</ins>' for p in paragraphs]
                inline_html.append("</p><p>".join(ins_paras))
            elif tag == "delete":
                paragraphs = esc_txt.split("\n\n")
                del_paras = [f'<del class="diff-del"{diag_attr} title="Cut from {esc_label_a}">{p.replace(chr(10), "<br/>")}</del>' for p in paragraphs]
                inline_html.append("</p><p>".join(del_paras))
            elif tag == "moved":
                paragraphs = esc_txt.split("\n\n")
                moved_paras = [f'<span class="diff-moved"{diag_attr} title="Relocated block in manuscript"><span class="badge-moved-pill">⇄ MOVED</span>{p.replace(chr(10), "<br/>")}</span>' for p in paragraphs]
                inline_html.append("</p><p>".join(moved_paras))
            else:
                paragraphs = esc_txt.split("\n\n")
                eq_paras = [f'<span class="diff-eq"{diag_attr}>{p.replace(chr(10), "<br/>")}</span>' for p in paragraphs]
                inline_html.append("</p><p>".join(eq_paras))

        body_prose = "".join(inline_html)
        if not body_prose.startswith("<p>"):
            body_prose = "<p>" + body_prose + "</p>"

        unified_sections.append(f"""
        <section id="{chap_id}" class="chapter-card" data-chapter-title="{esc_title.lower()}">
            <header class="chapter-header">
                <div class="chapter-meta">
                    <h2>{esc_title}</h2>
                    <span class="chapter-path">{esc_rel}</span>
                </div>
                <div class="chapter-pills">
                    <span class="badge badge-words">{w_a:,} &rarr; {w_b:,} words</span>
                    <span class="badge badge-add">+{c_add:,} added</span>
                    <span class="badge badge-del">-{c_del:,} cut</span>
                    {f'<span class="badge badge-moved">⇄ {c_moved:,} moved</span>' if c_moved else ''}
                    <span class="badge badge-sim">{c_sim}% match</span>
                </div>
            </header>
            <div class="prose-content">
                {body_prose}
            </div>
        </section>
        """)

        # 3. Side-by-Side Split View Rows
        split_rows: list[str] = []
        split_pairs = chap.get("split_pairs", [])
        if split_pairs:
            for pair in split_pairs:
                p_tag = pair.get("tag", "equal")
                text_a = pair.get("text_a", "")
                text_b = pair.get("text_b", "")
                esc_a = html.escape(text_a).replace("\n", "<br/>")
                esc_b = html.escape(text_b).replace("\n", "<br/>")

                if p_tag == "delete":
                    col_a = f'<div class="split-cell del-cell"><del class="diff-del">{esc_a}</del></div>'
                    col_b = '<div class="split-cell empty-cell"><span class="ghost-bar"></span></div>'
                elif p_tag == "insert":
                    col_a = '<div class="split-cell empty-cell"><span class="ghost-bar"></span></div>'
                    col_b = f'<div class="split-cell ins-cell"><ins class="diff-ins">{esc_b}</ins></div>'
                elif p_tag == "moved":
                    col_a = f'<div class="split-cell moved-cell"><span class="badge-moved-pill">⇄ RELOCATED</span>{esc_a}</div>'
                    col_b = f'<div class="split-cell moved-cell"><span class="badge-moved-pill">⇄ MOVED HERE</span>{esc_b}</div>'
                elif p_tag == "replace":
                    col_a = f'<div class="split-cell del-cell"><del class="diff-del">{esc_a}</del></div>'
                    col_b = f'<div class="split-cell ins-cell"><ins class="diff-ins">{esc_b}</ins></div>'
                else:
                    col_a = f'<div class="split-cell eq-cell">{esc_a}</div>'
                    col_b = f'<div class="split-cell eq-cell">{esc_b}</div>'

                split_rows.append(f'<div class="split-row">{col_a}{col_b}</div>')
        else:
            # Fallback split row with raw text
            esc_raw_a = html.escape(chap.get("raw_a", "")).replace("\n\n", "</p><p>")
            esc_raw_b = html.escape(chap.get("raw_b", "")).replace("\n\n", "</p><p>")
            split_rows.append(f"""
            <div class="split-row">
                <div class="split-cell"><p>{esc_raw_a}</p></div>
                <div class="split-cell"><p>{esc_raw_b}</p></div>
            </div>
            """)

        split_sections.append(f"""
        <section id="split-{chap_id}" class="chapter-card split-chapter-card" data-chapter-title="{esc_title.lower()}">
            <header class="chapter-header">
                <div class="chapter-meta">
                    <h2>{esc_title}</h2>
                    <span class="chapter-path">{esc_rel}</span>
                </div>
                <div class="chapter-pills">
                    <span class="badge badge-words">{w_a:,} &rarr; {w_b:,} words</span>
                    <span class="badge badge-sim">{c_sim}% match</span>
                </div>
            </header>
            <div class="split-grid-header">
                <div class="split-grid-col-title">◀ {esc_label_a} (Base)</div>
                <div class="split-grid-col-title">▶ {esc_label_b} (Target)</div>
            </div>
            <div class="split-grid-body">
                {"".join(split_rows)}
            </div>
        </section>
        """)

        # 4. Churn Matrix Row
        churn_rows.append(f"""
        <tr>
            <td class="cell-title"><strong>{esc_title}</strong><br/><small class="text-muted">{esc_rel}</small></td>
            <td>{w_a:,}</td>
            <td>{w_b:,}</td>
            <td class="text-add">+{c_add:,}</td>
            <td class="text-del">-{c_del:,}</td>
            <td><strong>{c_net_sign}{c_net:,}</strong></td>
            <td>
                <div class="churn-bar-container">
                    <div class="churn-bar" style="width: {min(c_churn, 100)}%;"></div>
                    <span>{c_churn}%</span>
                </div>
            </td>
            <td><strong>{c_sim}%</strong></td>
            <td>{status_tag}</td>
        </tr>
        """)

    # 5. Scraps Inspector Cards
    scraps_cards: list[str] = []
    for s_idx, scrap in enumerate(all_scraps, 1):
        s_id = html.escape(scrap.get("scrap_id", f"SCRAP-{s_idx:02d}"))
        s_chap = html.escape(scrap.get("chapter", "Manuscript Excision"))
        s_words = scrap.get("word_count", 0)
        s_content = scrap.get("content", "")
        esc_content = html.escape(s_content).replace("\n\n", "</p><p>").replace("\n", "<br/>")
        s_json = html.escape(json.dumps(scrap))

        scraps_cards.append(f"""
        <article class="scrap-card" data-scrap-id="{s_id}" data-chapter="{s_chap.lower()}">
            <header class="scrap-header">
                <div class="scrap-meta">
                    <span class="scrap-id-badge">{s_id}</span>
                    <h3 class="scrap-chap-title">{s_chap}</h3>
                </div>
                <div class="scrap-stats">
                    <span class="badge badge-del">✂️ {s_words:,} words cut</span>
                    <button class="btn btn-sm btn-copy-scrap" data-json="{s_json}" title="Copy markdown scrap to clipboard">📋 Copy Scrap</button>
                </div>
            </header>
            <div class="scrap-body">
                <p>{esc_content}</p>
            </div>
        </article>
        """)

    if not scraps_cards:
        scraps_cards.append("""
        <div class="empty-state">
            <div class="empty-icon">✂️</div>
            <h3>No Major Excised Scraps Found</h3>
            <p>No prose deletions exceeding the threshold (&ge; 50 words) were detected between these drafts.</p>
        </div>
        """)

    # 6. Advisory Findings Banner
    advisory_cards: list[str] = []
    for adv in all_advisories:
        adv_sev = html.escape(str(adv.get("severity", "OBSERVATION")))
        adv_msg = html.escape(adv.get("message", ""))
        adv_chap = html.escape(adv.get("chapter", ""))
        advisory_cards.append(f"""
        <div class="advisory-pill adv-{adv_sev.lower()}">
            <span class="adv-badge">{adv_sev}</span>
            <span class="adv-chap">[{adv_chap}]</span>
            <span class="adv-msg">{adv_msg}</span>
        </div>
        """)

    theme_css = get_theme_engine_css()
    theme_js = get_theme_engine_js()
    control_center_html = get_theme_control_center_html()

    return f"""<!DOCTYPE html>
<html lang="en" data-theme="sovereign-dark">
<head>
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Editorial Studio: {esc_label_a} vs {esc_label_b} | Ars Arcanum</title>
    <style>
{theme_css}
        :root {{
            --bg-body: #f8f9fa;
            --bg-surface: #ffffff;
            --bg-sidebar: #f1f3f5;
            --border-color: #e2e8f0;
            --text-main: #1a202c;
            --text-muted: #718096;
            --accent-primary: #3182ce;
            --accent-hover: #2b6cb0;
            --font-prose: "EB Garamond", "Libertinus Serif", "Georgia", serif;
            --font-ui: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            --font-mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;

            /* Accessible Redline Pastel Highlights */
            --del-bg: #fee2e2;
            --del-color: #991b1b;
            --del-border: #fca5a5;
            --ins-bg: #dcfce7;
            --ins-color: #166534;
            --ins-border: #86efac;
            --moved-bg: #e0f2fe;
            --moved-color: #0369a1;
            --moved-border: #7dd3fc;
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }}

        [data-theme="dark"] {{
            --bg-body: #0f172a;
            --bg-surface: #1e293b;
            --bg-sidebar: #131d31;
            --border-color: #334155;
            --text-main: #f1f5f9;
            --text-muted: #94a3b8;
            --accent-primary: #60a5fa;
            --accent-hover: #93c5fd;

            /* Dark Mode Accessible Highlights */
            --del-bg: #451a1a;
            --del-color: #fca5a5;
            --del-border: #7f1d1d;
            --ins-bg: #0f3822;
            --ins-color: #86efac;
            --ins-border: #14532d;
            --moved-bg: #0c334d;
            --moved-color: #7dd3fc;
            --moved-border: #0369a1;
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.3);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.4);
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
            z-index: 10;
        }}

        .sidebar-header {{
            padding: 16px 20px;
            border-bottom: 1px solid var(--border-color);
        }}

        .sidebar-brand {{
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--accent-primary);
            font-weight: 700;
        }}

        .sidebar-title {{
            font-size: 1.15rem;
            font-weight: 700;
            margin-top: 2px;
        }}

        .sidebar-subtitle {{
            font-size: 0.8rem;
            color: var(--text-muted);
            margin-top: 2px;
        }}

        .search-box {{
            padding: 12px 16px;
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
            border-color: var(--accent-primary);
        }}

        .nav-list {{
            flex: 1;
            overflow-y: auto;
            padding: 10px;
        }}

        .nav-item {{
            display: block;
            padding: 10px 12px;
            border-radius: 6px;
            color: var(--text-main);
            text-decoration: none;
            margin-bottom: 4px;
            transition: background 0.15s ease;
        }}

        .nav-item:hover, .nav-item.active {{
            background-color: var(--bg-surface);
            box-shadow: var(--shadow-sm);
        }}

        .nav-title {{
            font-size: 0.88rem;
            font-weight: 600;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .nav-stats {{
            display: flex;
            gap: 6px;
            font-size: 0.72rem;
            margin-top: 4px;
        }}

        .pill-add {{ color: #16a34a; font-weight: 600; }}
        .pill-del {{ color: #dc2626; font-weight: 600; }}
        .pill-net {{ color: var(--text-muted); }}
        .pill-sim {{ margin-left: auto; color: var(--accent-primary); font-weight: 600; }}

        /* Main Studio Workspace */
        .main-workspace {{
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }}

        /* Executive Header & Tabs */
        .studio-topbar {{
            background-color: var(--bg-surface);
            border-bottom: 1px solid var(--border-color);
            padding: 12px 24px;
            display: flex;
            flex-direction: column;
            gap: 12px;
            flex-shrink: 0;
            box-shadow: var(--shadow-sm);
        }}

        .topbar-row-1 {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .metrics-ribbon {{
            display: flex;
            gap: 20px;
            align-items: center;
            flex-wrap: wrap;
        }}

        .metric-badge {{
            display: flex;
            flex-direction: column;
        }}

        .metric-label {{
            font-size: 0.68rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
            font-weight: 700;
        }}

        .metric-val {{
            font-size: 1.15rem;
            font-weight: 700;
        }}

        .metric-val.add {{ color: #16a34a; }}
        .metric-val.del {{ color: #dc2626; }}
        .metric-val.sim {{ color: var(--accent-primary); }}

        .topbar-controls {{
            display: flex;
            gap: 8px;
            align-items: center;
        }}

        .btn {{
            padding: 6px 12px;
            border-radius: 6px;
            border: 1px solid var(--border-color);
            background-color: var(--bg-surface);
            color: var(--text-main);
            font-size: 0.82rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.15s ease;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}

        .btn:hover {{
            background-color: var(--bg-body);
            border-color: var(--accent-primary);
        }}

        .btn-sm {{
            padding: 4px 8px;
            font-size: 0.75rem;
        }}

        .btn-primary {{
            background-color: var(--accent-primary);
            color: #ffffff;
            border-color: var(--accent-primary);
        }}

        .btn-primary:hover {{
            background-color: var(--accent-hover);
        }}

        /* Tab Switcher & Filter Bar */
        .tab-filter-bar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 1px solid var(--border-color);
            padding-top: 10px;
        }}

        .tab-switcher {{
            display: flex;
            gap: 4px;
            background-color: var(--bg-body);
            padding: 3px;
            border-radius: 8px;
            border: 1px solid var(--border-color);
        }}

        .tab-btn {{
            padding: 6px 14px;
            border: none;
            background: transparent;
            color: var(--text-muted);
            font-size: 0.82rem;
            font-weight: 600;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.15s ease;
        }}

        .tab-btn.active {{
            background-color: var(--bg-surface);
            color: var(--text-main);
            box-shadow: var(--shadow-sm);
        }}

        .filter-controls {{
            display: flex;
            gap: 8px;
            align-items: center;
        }}

        .select-filter {{
            padding: 4px 8px;
            border-radius: 6px;
            border: 1px solid var(--border-color);
            background-color: var(--bg-surface);
            color: var(--text-main);
            font-size: 0.8rem;
            outline: none;
        }}

        /* Advisory Banner */
        .advisory-container {{
            padding: 8px 24px;
            background-color: var(--bg-body);
            border-bottom: 1px solid var(--border-color);
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }}

        .advisory-pill {{
            font-size: 0.75rem;
            padding: 3px 8px;
            border-radius: 4px;
            display: flex;
            gap: 6px;
            align-items: center;
        }}

        .adv-observation {{ background-color: var(--moved-bg); color: var(--moved-color); }}
        .adv-lens_note {{ background-color: #fef3c7; color: #92400e; }}
        .adv-rule_conflict {{ background-color: var(--del-bg); color: var(--del-color); }}
        .adv-badge {{ font-weight: 700; text-transform: uppercase; font-size: 0.65rem; }}

        /* Scroll Area & Tabs Viewport */
        .tab-viewport {{
            flex: 1;
            overflow-y: auto;
            position: relative;
        }}

        .tab-content {{
            display: none;
            padding: 24px 32px;
            max-width: 1200px;
            margin: 0 auto;
        }}

        .tab-content.active {{
            display: block;
        }}

        /* Chapter Cards & Prose */
        .chapter-card {{
            background-color: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            margin-bottom: 24px;
            box-shadow: var(--shadow-sm);
            overflow: hidden;
        }}

        .chapter-header {{
            padding: 14px 20px;
            border-bottom: 1px solid var(--border-color);
            background-color: var(--bg-body);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .chapter-meta h2 {{
            font-size: 1.1rem;
            font-weight: 700;
        }}

        .chapter-path {{
            font-size: 0.75rem;
            color: var(--text-muted);
            font-family: var(--font-mono);
        }}

        .chapter-pills {{
            display: flex;
            gap: 6px;
            flex-wrap: wrap;
        }}

        .badge {{
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.72rem;
            font-weight: 600;
        }}

        .badge-words {{ background-color: var(--border-color); color: var(--text-main); }}
        .badge-add {{ background-color: var(--ins-bg); color: var(--ins-color); }}
        .badge-del {{ background-color: var(--del-bg); color: var(--del-color); }}
        .badge-moved {{ background-color: var(--moved-bg); color: var(--moved-color); }}
        .badge-sim {{ background-color: var(--bg-surface); border: 1px solid var(--border-color); color: var(--text-muted); }}

        /* Prose Content Typography */
        .prose-content {{
            padding: 28px 36px;
            font-family: var(--font-prose);
            font-size: 1.18rem;
            line-height: 1.8;
            color: var(--text-main);
        }}

        .prose-content p {{
            margin-bottom: 1.4em;
            text-indent: 1.5em;
        }}

        .prose-content p:first-of-type {{
            text-indent: 0;
        }}

        /* Diff Highlights */
        ins.diff-ins {{
            background-color: var(--ins-bg);
            color: var(--ins-color);
            text-decoration: none;
            padding: 1px 3px;
            border-radius: 3px;
            font-weight: 500;
        }}

        del.diff-del {{
            background-color: var(--del-bg);
            color: var(--del-color);
            text-decoration: line-through;
            opacity: 0.85;
            padding: 1px 3px;
            border-radius: 3px;
        }}

        .diff-moved {{
            background-color: var(--moved-bg);
            color: var(--moved-color);
            padding: 2px 4px;
            border-radius: 3px;
            border-left: 3px solid var(--moved-border);
        }}

        .badge-moved-pill {{
            font-size: 0.65rem;
            font-family: var(--font-ui);
            font-weight: 700;
            background-color: var(--moved-border);
            color: var(--moved-color);
            padding: 1px 4px;
            border-radius: 3px;
            margin-right: 4px;
            vertical-align: middle;
        }}

        /* Filter view modes */
        body.filter-changes-only span.diff-eq {{
            display: none;
        }}
        body.filter-changes-only .prose-content p {{
            text-indent: 0;
            margin-bottom: 0.8em;
        }}

        body.filter-dialogue-only .prose-content *:not([data-dialogue="true"]) {{
            opacity: 0.3;
        }}

        /* Side-by-Side Split View */
        .split-chapter-card {{
            max-width: 100%;
        }}

        .split-grid-header {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            background-color: var(--bg-body);
            border-bottom: 1px solid var(--border-color);
            padding: 8px 20px;
            font-weight: 700;
            font-size: 0.85rem;
            color: var(--text-muted);
        }}

        .split-grid-body {{
            display: flex;
            flex-direction: column;
        }}

        .split-row {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            border-bottom: 1px solid var(--border-color);
        }}

        .split-cell {{
            padding: 12px 18px;
            font-family: var(--font-prose);
            font-size: 1.05rem;
            line-height: 1.6;
            overflow-x: auto;
        }}

        .split-cell:first-child {{
            border-right: 1px solid var(--border-color);
            background-color: rgba(239, 68, 68, 0.02);
        }}

        .split-cell:last-child {{
            background-color: rgba(34, 197, 94, 0.02);
        }}

        .split-cell.del-cell {{ background-color: var(--del-bg); }}
        .split-cell.ins-cell {{ background-color: var(--ins-bg); }}
        .split-cell.moved-cell {{ background-color: var(--moved-bg); }}
        .split-cell.empty-cell {{
            background-color: var(--bg-body);
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .ghost-bar {{
            height: 2px;
            width: 40px;
            background-color: var(--border-color);
            border-radius: 1px;
        }}

        /* Scraps Inspector Tab */
        .scraps-deck {{
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}

        .scrap-card {{
            background-color: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-left: 4px solid var(--del-color);
            border-radius: 8px;
            padding: 16px 20px;
            box-shadow: var(--shadow-sm);
        }}

        .scrap-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            border-bottom: 1px dashed var(--border-color);
            padding-bottom: 8px;
        }}

        .scrap-meta {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .scrap-id-badge {{
            font-family: var(--font-mono);
            font-size: 0.75rem;
            padding: 2px 6px;
            border-radius: 4px;
            background-color: var(--bg-body);
            color: var(--text-muted);
            font-weight: 600;
        }}

        .scrap-chap-title {{
            font-size: 0.95rem;
            font-weight: 700;
        }}

        .scrap-body {{
            font-family: var(--font-prose);
            font-size: 1.05rem;
            line-height: 1.6;
            color: var(--text-main);
            background-color: var(--bg-body);
            padding: 12px 16px;
            border-radius: 6px;
        }}

        /* Churn & Telemetry Matrix */
        .telemetry-table-container {{
            background-color: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            overflow: hidden;
            box-shadow: var(--shadow-sm);
        }}

        .telemetry-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
        }}

        .telemetry-table th {{
            background-color: var(--bg-body);
            padding: 12px 16px;
            text-align: left;
            font-weight: 700;
            border-bottom: 1px solid var(--border-color);
            color: var(--text-muted);
            text-transform: uppercase;
            font-size: 0.72rem;
            letter-spacing: 0.05em;
        }}

        .telemetry-table td {{
            padding: 12px 16px;
            border-bottom: 1px solid var(--border-color);
        }}

        .telemetry-table tr:last-child td {{
            border-bottom: none;
        }}

        .text-add {{ color: #16a34a; font-weight: 600; }}
        .text-del {{ color: #dc2626; font-weight: 600; }}

        .churn-bar-container {{
            width: 100px;
            background-color: var(--bg-body);
            height: 8px;
            border-radius: 4px;
            overflow: hidden;
            display: inline-block;
            vertical-align: middle;
            margin-right: 6px;
        }}

        .churn-bar {{
            height: 100%;
            background-color: var(--accent-primary);
            border-radius: 4px;
        }}

        .status-badge {{
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.72rem;
            font-weight: 700;
        }}

        .status-badge.pristine {{ background-color: #f1f5f9; color: #475569; }}
        .status-badge.overhaul {{ background-color: #fee2e2; color: #991b1b; }}
        .status-badge.expansion {{ background-color: #dcfce7; color: #166534; }}
        .status-badge.trimmed {{ background-color: #fef3c7; color: #92400e; }}
        .status-badge.balanced {{ background-color: #e0f2fe; color: #0369a1; }}

        .empty-state {{
            text-align: center;
            padding: 48px;
            background-color: var(--bg-surface);
            border: 1px dashed var(--border-color);
            border-radius: 8px;
        }}

        .empty-icon {{ font-size: 2.5rem; margin-bottom: 12px; }}

        /* Toast notifications */
        #toast {{
            position: fixed;
            bottom: 24px;
            right: 24px;
            padding: 10px 18px;
            background-color: #1e293b;
            color: #ffffff;
            border-radius: 6px;
            font-size: 0.85rem;
            font-weight: 600;
            box-shadow: var(--shadow-md);
            opacity: 0;
            transition: opacity 0.2s ease;
            pointer-events: none;
            z-index: 1000;
        }}
        #toast.show {{ opacity: 1; }}
    </style>
</head>
<body>
    <!-- Sidebar Navigation -->
    <aside class="sidebar">
        <div class="sidebar-header">
            <div class="sidebar-brand">Ars Arcanum</div>
            <h1 class="sidebar-title">Editorial Studio</h1>
            <div class="sidebar-subtitle">{esc_label_a} &rarr; {esc_label_b}</div>
        </div>
        <div class="search-box">
            <input type="text" id="searchInput" placeholder="Filter chapters & scenes..." autocomplete="off">
        </div>
        <nav class="nav-list" id="navList">
            {"".join(sidebar_items)}
        </nav>
    </aside>

    <!-- Main Workspace -->
    <main class="main-workspace">
        <header class="studio-topbar">
            <div class="topbar-row-1">
                <div class="metrics-ribbon">
                    <div class="metric-badge">
                        <span class="metric-label">{esc_label_a}</span>
                        <span class="metric-val">{tot_a:,}w</span>
                    </div>
                    <div class="metric-badge">
                        <span class="metric-label">{esc_label_b}</span>
                        <span class="metric-val">{tot_b:,}w</span>
                    </div>
                    <div class="metric-badge">
                        <span class="metric-label">Words Added</span>
                        <span class="metric-val add">+{add_w:,}</span>
                    </div>
                    <div class="metric-badge">
                        <span class="metric-label">Words Cut</span>
                        <span class="metric-val del">-{del_w:,}</span>
                    </div>
                    {f'<div class="metric-badge"><span class="metric-label">Moved</span><span class="metric-val">{moved_w:,}w</span></div>' if moved_w else ''}
                    <div class="metric-badge">
                        <span class="metric-label">Net Delta</span>
                        <span class="metric-val">{net_sign}{net_w:,}</span>
                    </div>
                    <div class="metric-badge">
                        <span class="metric-label">Similarity</span>
                        <span class="metric-val sim">{sim_pct}%</span>
                    </div>
                    <div class="metric-badge">
                        <span class="metric-label">Gross Churn</span>
                        <span class="metric-val">{gross_churn}%</span>
                    </div>
                </div>
                <div class="topbar-controls">
                    {control_center_html}
                </div>
            </div>

            <div class="tab-filter-bar">
                <div class="tab-switcher">
                    <button class="tab-btn active" data-tab="tab-unified">📝 Unified Redline</button>
                    <button class="tab-btn" data-tab="tab-split">📖 Side-by-Side Split</button>
                    <button class="tab-btn" data-tab="tab-scraps">✂️ Excised Scraps ({len(all_scraps)})</button>
                    <button class="tab-btn" data-tab="tab-churn">📊 Churn & Telemetry</button>
                </div>
                <div class="filter-controls">
                    <select class="select-filter" id="selectViewFilter">
                        <option value="all">View: Full Prose</option>
                        <option value="changes-only">View: Changes Only</option>
                    </select>
                    <select class="select-filter" id="selectContentFilter">
                        <option value="all">Focus: All Content</option>
                        <option value="dialogue-only">Focus: Dialogue Only</option>
                    </select>
                </div>
            </div>
        </header>

        {f'<div class="advisory-container">{"".join(advisory_cards)}</div>' if advisory_cards else ''}

        <div class="tab-viewport">
            <!-- TAB 1: Unified Inline Redline -->
            <div id="tab-unified" class="tab-content active">
                {"".join(unified_sections)}
            </div>

            <!-- TAB 2: Side-by-Side Split View -->
            <div id="tab-split" class="tab-content">
                {"".join(split_sections)}
            </div>

            <!-- TAB 3: Excised Scraps Inspector -->
            <div id="tab-scraps" class="tab-content">
                <div class="scraps-deck">
                    {"".join(scraps_cards)}
                </div>
            </div>

            <!-- TAB 4: Churn & Telemetry -->
            <div id="tab-churn" class="tab-content">
                <div class="telemetry-table-container">
                    <table class="telemetry-table">
                        <thead>
                            <tr>
                                <th>Chapter / Scope</th>
                                <th>Base Words</th>
                                <th>Target Words</th>
                                <th>Added</th>
                                <th>Cut</th>
                                <th>Net Change</th>
                                <th>Churn Index</th>
                                <th>Match %</th>
                                <th>Editorial Assessment</th>
                            </tr>
                        </thead>
                        <tbody>
                            {"".join(churn_rows)}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </main>

    <div id="toast">Scrap copied to clipboard!</div>

    <script>
        // 1. Theme Toggle
        const btnTheme = document.getElementById('btnThemeToggle');
        let currentTheme = 'light';
        btnTheme.addEventListener('click', () => {{
            currentTheme = currentTheme === 'light' ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', currentTheme);
            btnTheme.textContent = 'Theme: ' + (currentTheme === 'dark' ? 'Dark' : 'Light');
        }});

        // 2. Tab Navigation
        const tabBtns = document.querySelectorAll('.tab-btn');
        const tabContents = document.querySelectorAll('.tab-content');
        tabBtns.forEach(btn => {{
            btn.addEventListener('click', () => {{
                tabBtns.forEach(b => b.classList.remove('active'));
                tabContents.forEach(c => c.classList.remove('active'));
                btn.classList.add('active');
                const targetId = btn.getAttribute('data-tab');
                const target = document.getElementById(targetId);
                if (target) target.classList.add('active');
            }});
        }});

        // 3. View Filters
        const selectView = document.getElementById('selectViewFilter');
        selectView.addEventListener('change', (e) => {{
            document.body.classList.toggle('filter-changes-only', e.target.value === 'changes-only');
        }});

        const selectContent = document.getElementById('selectContentFilter');
        selectContent.addEventListener('change', (e) => {{
            document.body.classList.toggle('filter-dialogue-only', e.target.value === 'dialogue-only');
        }});

        // 4. Search Filter
        const searchInput = document.getElementById('searchInput');
        searchInput.addEventListener('input', (e) => {{
            const query = e.target.value.toLowerCase().trim();
            document.querySelectorAll('.chapter-card').forEach(card => {{
                const title = card.getAttribute('data-chapter-title') || card.textContent.toLowerCase();
                card.style.display = title.includes(query) ? 'block' : 'none';
            }});
            document.querySelectorAll('.scrap-card').forEach(card => {{
                const text = card.textContent.toLowerCase();
                card.style.display = text.includes(query) ? 'block' : 'none';
            }});
        }});

        // 5. Copy Scrap to Clipboard
        function showToast(msg) {{
            const toast = document.getElementById('toast');
            toast.textContent = msg;
            toast.classList.add('show');
            setTimeout(() => toast.classList.remove('show'), 2500);
        }}

        document.querySelectorAll('.btn-copy-scrap').forEach(btn => {{
            btn.addEventListener('click', () => {{
                try {{
                    const rawJson = btn.getAttribute('data-json');
                    const scrap = JSON.parse(rawJson);
                    const md = '---\\nscrap_id: "' + scrap.scrap_id + '"\\nchapter: "' + scrap.chapter + '"\\nword_count: ' + scrap.word_count + '\\n---\\n\\n' + scrap.content;
                    navigator.clipboard.writeText(md).then(() => {{
                        showToast('Scrap ' + scrap.scrap_id + ' copied to clipboard!');
                    }}).catch(() => {{
                        showToast('Copied to clipboard');
                    }});
                }} catch (e) {{
                    showToast('Failed to copy scrap');
                }}
            }});
        }});
    </script>
    <script>
{theme_js}
    </script>
</body>
</html>
"""
