#!/usr/bin/env python3
"""
Ars Arcanum Revision Density & Churn Heatmap Interactive HTML Generator
(scripts/lib/revision_heatmap_template.py)
========================================================================
Pure-Python, zero-dependency, 100% offline CSP-compliant interactive HTML5/CSS/JS
authoring studio dashboard for manuscript revision density and churn telemetry.
"""

from __future__ import annotations

import html
import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass

logger = logging.getLogger("arcanum.revision_heatmap")

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

_FLAG_META: dict[str, dict[str, str]] = {
    "REV-101": {
        "label": "REV-101 High Revision Activity",
        "icon": "🔥",
        "color": "#ef4444",
        "bg": "rgba(239, 68, 68, 0.15)",
        "description": "Perfectionist rewriting loop detected; churn exceeds 3x average or 120% replacement.",
    },
    "REV-102": {
        "label": "REV-102 Pristine Draft",
        "icon": "🌱",
        "color": "#22c55e",
        "bg": "rgba(34, 197, 94, 0.15)",
        "description": "Untouched prose pass; zero line/word changes detected against baseline snapshot.",
    },
    "REV-103": {
        "label": "REV-103 Heavy Cut",
        "icon": "✂️",
        "color": "#f97316",
        "bg": "rgba(249, 115, 22, 0.15)",
        "description": "Substantial prose excision (>40% of baseline words deleted). Check for dropped plot threads.",
    },
    "REV-104": {
        "label": "REV-104 Expansion",
        "icon": "📈",
        "color": "#38bdf8",
        "bg": "rgba(56, 189, 248, 0.15)",
        "description": "Major chapter expansion (>50% word increase). Verify chapter balance and narrative pacing.",
    },
    "REV-105": {
        "label": "REV-105 Dialogue Skew",
        "icon": "💬",
        "color": "#a855f7",
        "bg": "rgba(168, 85, 247, 0.15)",
        "description": "Revision heavily skewed towards spoken dialogue (>75%) or narrative exposition (>90%).",
    },
    "REV-106": {
        "label": "REV-106 Front-Loaded",
        "icon": "⏳",
        "color": "#ec4899",
        "bg": "rgba(236, 72, 153, 0.15)",
        "description": "Opening chapters (1–3) show disproportionate churn compared to later manuscript chapters.",
    },
}

_FLAG_LABELS: dict[str, str] = {
    k: f"{v['icon']} {v['label']}" for k, v in _FLAG_META.items()
}
_FLAG_LABELS[""] = ""


def _churn_color(churn_ratio: float) -> str:
    """Map churn_ratio to a hex color for the heatmap bar (ColorBrewer-style)."""
    if churn_ratio >= 0.5:
        return "#ef4444"  # red (high churn)
    if churn_ratio >= 0.2:
        return "#f59e0b"  # amber (medium churn)
    return "#22c55e"  # green (low / stable churn)


def _bar_width(churn_score: int, max_score: int) -> int:
    """Compute a bar width percentage (1–100) relative to max_score."""
    if max_score == 0:
        return 1
    return max(1, min(100, round(churn_score / max_score * 100)))


def generate_revision_heatmap_html(
    churn_data: dict[str, Any],
    output_path: Path | str,
) -> Path:
    """Generate a standalone, rich interactive CSP-compliant offline HTML heatmap.

    Parameters
    ----------
    churn_data:
        Dict with keys: manuscript, chapters (list[ChapterRevisionStats] or dicts),
        findings, avg_churn_score, total_chapters, max_churn_score, total_words,
        baseline_words, dialogue_churn_percentage, baseline_source, etc.
    output_path:
        Destination .html file path.
    """
    out_path = Path(output_path).resolve()
    manuscript = html.escape(str(churn_data.get("manuscript", "Manuscript")))
    baseline_source = html.escape(str(churn_data.get("baseline_source", "Snapshot / Backups")))
    chapters_raw = churn_data.get("chapters", [])
    findings: list[dict[str, Any]] = churn_data.get("findings", [])

    # Normalize chapters to dicts if dataclasses
    chapters: list[dict[str, Any]] = []
    for c in chapters_raw:
        if hasattr(c, "__dict__"):
            chapters.append(vars(c))
        elif isinstance(c, dict):
            chapters.append(c)

    total = churn_data.get("total_chapters", len(chapters))
    avg_churn = churn_data.get("avg_churn_score", 0.0)
    max_score = churn_data.get("max_churn_score", 0)
    avg_ratio = churn_data.get("avg_churn_ratio", 0.0)
    total_words = churn_data.get("total_words", sum(c.get("word_count", 0) for c in chapters))
    baseline_words = churn_data.get("total_baseline_words", sum(c.get("baseline_word_count", 0) for c in chapters))
    net_delta = total_words - baseline_words
    total_churn_vol = sum(c.get("churn_score", 0) for c in chapters)
    diag_churn_pct = churn_data.get(
        "dialogue_churn_percentage",
        round((sum(c.get("dialogue_churn_score", 0) for c in chapters) / max(1, total_churn_vol)) * 100.0, 1),
    )

    if max_score == 0 and chapters:
        max_score = max((c.get("churn_score", 0) for c in chapters), default=0)

    # Count flags by category
    flag_counts: dict[str, int] = dict.fromkeys(_FLAG_META, 0)
    for ch in chapters:
        for flg in ch.get("flags", []) or ([ch.get("flag")] if ch.get("flag") else []):
            if flg in flag_counts:
                flag_counts[flg] += 1

    # Build Table Rows HTML
    rows_html_parts: list[str] = []
    for idx, ch in enumerate(chapters):
        c_name = ch.get("chapter", "")
        c_rel = ch.get("rel_path", "")
        wc = ch.get("word_count", 0)
        b_wc = ch.get("baseline_word_count", 0)
        ins = ch.get("insertions", 0)
        dels = ch.get("deletions", 0)
        score = ch.get("churn_score", 0)
        ratio = ch.get("churn_ratio", 0.0)
        has_snap = ch.get("has_snapshot", False)
        ch_flag = ch.get("flag", "")
        ch_flags = ch.get("flags", []) or ([ch_flag] if ch_flag else [])
        d_score = ch.get("dialogue_churn_score", 0)
        p_score = ch.get("prose_churn_score", 0)
        sub_scenes = ch.get("sub_scenes", [])
        intent = ch.get("intent", "")

        color = _churn_color(ratio)
        bar_w = _bar_width(score, max_score)

        # Flag badges
        badges_html = []
        for flg in ch_flags:
            meta = _FLAG_META.get(flg)
            if meta:
                badges_html.append(
                    f'<span class="flag-badge" style="color:{meta["color"]};background:{meta["bg"]};" '
                    f'title="{html.escape(meta["description"])}">{meta["icon"]} {html.escape(flg)}</span>'
                )
        if intent:
            badges_html.append(
                f'<span class="intent-badge" title="Authorial Intent Directive">🎯 @intent:{html.escape(intent)}</span>'
            )
        flags_cell = "".join(badges_html) or '<span style="color:var(--text-muted);font-size:0.8rem;">—</span>'

        # Snapshot indicator
        snap_badge = ""
        if not has_snap:
            snap_badge = '<span class="no-snap-badge" title="No historical baseline found">🌱 Genesis</span>'

        # Word delta badge
        w_delta = wc - b_wc
        if b_wc > 0 and w_delta != 0:
            delta_sign = "+" if w_delta > 0 else ""
            delta_color = "var(--green)" if w_delta > 0 else "var(--red)"
            delta_badge = f'<span style="color:{delta_color};font-size:0.75rem;margin-left:4px;">({delta_sign}{w_delta:,})</span>'
        else:
            delta_badge = ""

        # Dialogue vs Prose stacked bar
        diag_pct = round((d_score / max(1, score)) * 100.0) if score > 0 else 0
        prose_pct = 100 - diag_pct if score > 0 else 0

        # Sub-scene expander toggle
        has_scenes = len(sub_scenes) > 1
        expander_btn = (
            f'<button class="scene-toggle-btn" onclick="toggleScenes({idx})" title="Toggle scene breakdowns">'
            f'<span class="toggle-icon" id="toggle-icon-{idx}">▶</span> {len(sub_scenes)} scenes</button>'
            if has_scenes
            else ""
        )

        row_classes = ["chapter-row"]
        for flg in ch_flags:
            row_classes.append(f"has-{flg.lower()}")

        rows_html_parts.append(
            f"""
      <tr class="{' '.join(row_classes)}" data-chapter="{html.escape(c_name.lower())}" data-idx="{idx}">
        <td class="col-chapter" title="{html.escape(c_rel)}">
          <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
            <span class="chap-title">{html.escape(c_name)}</span>
            {snap_badge}
            {expander_btn}
          </div>
        </td>
        <td class="col-num">{wc:,}{delta_badge}</td>
        <td class="col-num col-add">+{ins:,}</td>
        <td class="col-num col-del">-{dels:,}</td>
        <td class="col-num" style="font-weight:600;">{score:,}</td>
        <td class="col-num">
          <span class="ratio-pill" style="border-color:{color}40;color:{color};background:{color}15;">
            {ratio:.3f}
          </span>
        </td>
        <td class="col-split">
          <div class="split-bar-container" title="Dialogue Churn: {diag_pct}% ({d_score} w) | Narrative Prose: {prose_pct}% ({p_score} w)">
            <div class="split-bar-diag" style="width:{diag_pct}%;"></div>
            <div class="split-bar-prose" style="width:{prose_pct}%;"></div>
          </div>
          <div class="split-bar-labels">
            <span>💬 {diag_pct}%</span>
            <span>📖 {prose_pct}%</span>
          </div>
        </td>
        <td class="col-heat">
          <div class="heat-bar-track">
            <div class="heat-bar-fill" style="background:{color};width:{bar_w}%;"></div>
          </div>
        </td>
        <td class="col-flags">{flags_cell}</td>
      </tr>"""
        )

        # Render sub-scene rows if present
        if has_scenes:
            for s_idx, sc in enumerate(sub_scenes):
                sc_name = html.escape(str(sc.get("name", f"Scene {s_idx+1}")))
                sc_wc = sc.get("word_count", 0)
                sc_ins = sc.get("insertions", 0)
                sc_del = sc.get("deletions", 0)
                sc_score = sc.get("churn_score", 0)
                sc_ratio = sc.get("churn_ratio", 0.0)
                sc_color = _churn_color(sc_ratio)
                sc_bar_w = _bar_width(sc_score, max_score)

                rows_html_parts.append(
                    f"""
      <tr class="scene-row scene-row-{idx}" style="display:none;" data-chapter="{html.escape(c_name.lower())}">
        <td class="col-chapter scene-indent">
          <span style="color:var(--text-muted);margin-right:6px;">↳</span>
          <span style="color:var(--text-secondary);font-size:0.85rem;">{sc_name}</span>
        </td>
        <td class="col-num" style="color:var(--text-secondary);">{sc_wc:,}</td>
        <td class="col-num col-add" style="font-size:0.8rem;">+{sc_ins:,}</td>
        <td class="col-num col-del" style="font-size:0.8rem;">-{sc_del:,}</td>
        <td class="col-num" style="color:var(--text-secondary);">{sc_score:,}</td>
        <td class="col-num">
          <span class="ratio-pill ratio-pill-sm" style="border-color:{sc_color}40;color:{sc_color};background:{sc_color}15;">
            {sc_ratio:.3f}
          </span>
        </td>
        <td class="col-split">
          <div class="heat-bar-track heat-bar-sm">
            <div class="heat-bar-fill" style="background:{sc_color};width:{sc_bar_w}%;"></div>
          </div>
        </td>
        <td class="col-heat"></td>
        <td class="col-flags"></td>
      </tr>"""
                )

    rows_html = "".join(rows_html_parts)

    # Build Findings Cards HTML
    findings_cards_parts: list[str] = []
    for f in findings:
        code = html.escape(f.get("code", "REV-000"))
        chap = html.escape(f.get("chapter", "Manuscript"))
        msg = html.escape(f.get("message", ""))
        sug = html.escape(f.get("suggestion", ""))
        sev = html.escape(f.get("severity_label", "OBSERVATION"))
        meta = _FLAG_META.get(code, {"color": "#38bdf8", "bg": "rgba(56, 189, 248, 0.15)", "icon": "🔍"})

        sug_html = (
            f"""<div class="finding-sug">
            <strong>💡 Craft Advisory:</strong> {sug}
          </div>"""
            if sug
            else ""
        )

        findings_cards_parts.append(
            f"""
        <div class="finding-card" style="border-left-color:{meta['color']};">
          <div class="finding-header">
            <div style="display:flex;align-items:center;gap:8px;">
              <span class="flag-badge" style="color:{meta['color']};background:{meta['bg']};font-size:0.85rem;">
                {meta['icon']} {code}
              </span>
              <span class="finding-sev">{sev}</span>
            </div>
            <span class="finding-chap">{chap}</span>
          </div>
          <div class="finding-msg">{msg}</div>
          {sug_html}
        </div>"""
        )

    findings_html = (
        "".join(findings_cards_parts)
        if findings_cards_parts
        else '<div class="empty-findings">✨ No revision flags or perfectionist traps detected across the current scope.</div>'
    )

    # Prepare JSON serializable payload for copy button
    json_export_str = html.escape(
        json.dumps(
            {
                "manuscript": churn_data.get("manuscript"),
                "baseline_source": str(churn_data.get("baseline_source", "")),
                "total_chapters": total,
                "total_words": total_words,
                "baseline_words": baseline_words,
                "avg_churn_ratio": avg_ratio,
                "avg_churn_score": avg_churn,
                "max_churn_score": max_score,
                "dialogue_churn_percentage": diag_churn_pct,
                "chapters": chapters,
                "findings": findings,
            },
            indent=2,
        )
    )

    # Word delta formatted string
    delta_sign = "+" if net_delta > 0 else ""
    delta_class = "delta-pos" if net_delta > 0 else ("delta-neg" if net_delta < 0 else "delta-neu")
    delta_str = f"{delta_sign}{net_delta:,}" if baseline_words > 0 else "Baseline N/A"

    theme_css = get_theme_engine_css()
    theme_js = get_theme_engine_js()
    control_center_html = get_theme_control_center_html()

    html_page = f"""<!DOCTYPE html>
<html lang="en" data-theme="sovereign-dark">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="Content-Security-Policy" content="{_CSP}">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Revision Heatmap Studio — {manuscript}</title>
  <style>
{theme_css}
    :root {{
      --bg: #0f172a;
      --bg-card: #1e293b;
      --bg-card-alt: #0b1120;
      --bg-hover: #334155;
      --border: #334155;
      --border-subtle: #1e293b;
      --text: #f8fafc;
      --text-secondary: #cbd5e1;
      --text-muted: #94a3b8;
      --accent: #38bdf8;
      --accent-bg: rgba(56, 189, 248, 0.12);
      --green: #22c55e;
      --amber: #f59e0b;
      --red: #ef4444;
      --indigo: #818cf8;
      --purple: #a855f7;
      --pink: #ec4899;
      --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -2px rgba(0, 0, 0, 0.3);
    }}

    [data-theme="light"] {{
      --bg: #f8fafc;
      --bg-card: #ffffff;
      --bg-card-alt: #f1f5f9;
      --bg-hover: #f1f5f9;
      --border: #e2e8f0;
      --border-subtle: #f1f5f9;
      --text: #0f172a;
      --text-secondary: #334155;
      --text-muted: #64748b;
      --accent: #0284c7;
      --accent-bg: rgba(2, 132, 199, 0.1);
      --green: #16a34a;
      --amber: #d97706;
      --red: #dc2626;
      --indigo: #6366f1;
      --purple: #9333ea;
      --pink: #db2777;
      --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
    }}

    *, *::before, *::after {{ box-sizing: border-box; }}
    body {{
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: var(--bg);
      color: var(--text);
      margin: 0;
      padding: 24px;
      line-height: 1.5;
      transition: background-color 0.2s ease, color 0.2s ease;
    }}

    .container {{ max-width: 1300px; margin: 0 auto; }}

    /* Header & Navigation */
    .header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      flex-wrap: wrap;
      gap: 16px;
      margin-bottom: 24px;
      padding-bottom: 20px;
      border-bottom: 1px solid var(--border);
    }}
    .title-group h1 {{
      font-size: 1.75rem;
      font-weight: 700;
      margin: 0 0 6px 0;
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .subtitle {{
      color: var(--text-muted);
      font-size: 0.9rem;
      margin: 0;
    }}
    .header-actions {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .btn {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      color: var(--text);
      padding: 8px 14px;
      border-radius: 6px;
      font-size: 0.85rem;
      font-weight: 500;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.15s ease;
    }}
    .btn:hover {{
      background: var(--bg-hover);
      border-color: var(--accent);
    }}

    /* KPI Grid */
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }}
    .kpi-card {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px;
      box-shadow: var(--shadow);
    }}
    .kpi-label {{
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-muted);
      margin-bottom: 6px;
    }}
    .kpi-val {{
      font-size: 1.6rem;
      font-weight: 700;
      color: var(--text);
      display: flex;
      align-items: baseline;
      gap: 6px;
    }}
    .kpi-sub {{
      font-size: 0.8rem;
      color: var(--text-muted);
      margin-top: 4px;
    }}
    .delta-pos {{ color: var(--green); }}
    .delta-neg {{ color: var(--red); }}
    .delta-neu {{ color: var(--text-muted); }}

    /* Filters & Controls */
    .controls-panel {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px;
      margin-bottom: 20px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }}
    .search-row {{
      display: flex;
      gap: 12px;
      align-items: center;
      flex-wrap: wrap;
    }}
    .search-input {{
      flex: 1;
      min-width: 260px;
      background: var(--bg-card-alt);
      border: 1px solid var(--border);
      color: var(--text);
      padding: 8px 12px;
      border-radius: 6px;
      font-size: 0.9rem;
    }}
    .search-input:focus {{
      outline: none;
      border-color: var(--accent);
    }}
    .filter-pills {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }}
    .pill-btn {{
      background: var(--bg-card-alt);
      border: 1px solid var(--border);
      color: var(--text-secondary);
      padding: 5px 10px;
      border-radius: 20px;
      font-size: 0.8rem;
      cursor: pointer;
      transition: all 0.15s ease;
      display: inline-flex;
      align-items: center;
      gap: 5px;
    }}
    .pill-btn:hover {{
      border-color: var(--accent);
      color: var(--text);
    }}
    .pill-btn.active {{
      background: var(--accent-bg);
      border-color: var(--accent);
      color: var(--accent);
      font-weight: 600;
    }}

    /* Table */
    .table-container {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 8px;
      overflow: hidden;
      box-shadow: var(--shadow);
      margin-bottom: 24px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      text-align: left;
    }}
    thead tr {{
      background: var(--bg-card-alt);
      border-bottom: 1px solid var(--border);
    }}
    th {{
      padding: 12px 14px;
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-muted);
      cursor: pointer;
      user-select: none;
      white-space: nowrap;
    }}
    th:hover {{
      color: var(--text);
    }}
    th.sorted-asc::after {{ content: " ↑"; color: var(--accent); }}
    th.sorted-desc::after {{ content: " ↓"; color: var(--accent); }}
    tbody tr {{
      border-bottom: 1px solid var(--border-subtle);
      transition: background-color 0.15s ease;
    }}
    tbody tr:hover {{
      background-color: var(--bg-hover);
    }}
    td {{
      padding: 10px 14px;
      font-size: 0.875rem;
    }}
    .col-chapter {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 0.85rem;
      max-width: 320px;
    }}
    .chap-title {{
      font-weight: 600;
      color: var(--text);
    }}
    .col-num {{
      text-align: right;
      font-variant-numeric: tabular-nums;
    }}
    .col-add {{ color: var(--green); }}
    .col-del {{ color: var(--red); }}
    .ratio-pill {{
      display: inline-block;
      padding: 2px 8px;
      border-radius: 12px;
      font-weight: 600;
      font-size: 0.8rem;
      border: 1px solid;
    }}
    .ratio-pill-sm {{
      font-size: 0.75rem;
      padding: 1px 6px;
    }}
    .col-split {{
      min-width: 140px;
      padding: 8px 12px;
    }}
    .split-bar-container {{
      display: flex;
      height: 10px;
      border-radius: 5px;
      overflow: hidden;
      background: var(--bg-card-alt);
      border: 1px solid var(--border);
    }}
    .split-bar-diag {{
      background: var(--indigo);
      height: 100%;
    }}
    .split-bar-prose {{
      background: var(--accent);
      height: 100%;
    }}
    .split-bar-labels {{
      display: flex;
      justify-content: space-between;
      font-size: 0.7rem;
      color: var(--text-muted);
      margin-top: 3px;
    }}
    .col-heat {{
      min-width: 100px;
    }}
    .heat-bar-track {{
      background: var(--bg-card-alt);
      border-radius: 4px;
      height: 12px;
      width: 100%;
      overflow: hidden;
      border: 1px solid var(--border);
    }}
    .heat-bar-sm {{
      height: 8px;
    }}
    .heat-bar-fill {{
      height: 100%;
      border-radius: 3px;
      transition: width 0.3s ease;
    }}
    .col-flags {{
      white-space: nowrap;
    }}
    .flag-badge {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 0.75rem;
      font-weight: 600;
      margin-right: 6px;
    }}
    .intent-badge {{
      display: inline-flex;
      align-items: center;
      gap: 3px;
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 0.75rem;
      background: rgba(148, 163, 184, 0.15);
      color: var(--text-muted);
      border: 1px dashed var(--text-muted);
    }}
    .no-snap-badge {{
      font-size: 0.75rem;
      color: var(--text-muted);
      background: var(--bg-card-alt);
      border: 1px solid var(--border);
      padding: 1px 6px;
      border-radius: 4px;
    }}
    .scene-toggle-btn {{
      background: none;
      border: 1px solid var(--border);
      color: var(--accent);
      font-size: 0.75rem;
      padding: 1px 6px;
      border-radius: 4px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }}
    .scene-toggle-btn:hover {{
      background: var(--accent-bg);
    }}
    .scene-row {{
      background-color: var(--bg-card-alt);
    }}
    .scene-indent {{
      padding-left: 28px !important;
    }}

    /* Findings Section */
    .findings-panel {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 20px;
      box-shadow: var(--shadow);
      margin-bottom: 24px;
    }}
    .findings-header {{
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      margin-bottom: 16px;
    }}
    .findings-header h2 {{
      font-size: 1.15rem;
      margin: 0;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .finding-card {{
      background: var(--bg-card-alt);
      border: 1px solid var(--border);
      border-left: 4px solid var(--accent);
      border-radius: 6px;
      padding: 14px 16px;
      margin-bottom: 12px;
    }}
    .finding-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
    }}
    .finding-sev {{
      font-size: 0.7rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-muted);
      background: var(--bg-card);
      padding: 2px 6px;
      border-radius: 4px;
      border: 1px solid var(--border);
    }}
    .finding-chap {{
      font-family: monospace;
      font-size: 0.85rem;
      font-weight: 600;
      color: var(--text-secondary);
    }}
    .finding-msg {{
      font-size: 0.9rem;
      color: var(--text);
      margin-bottom: 6px;
    }}
    .finding-sug {{
      font-size: 0.85rem;
      color: var(--text-secondary);
      background: var(--bg-card);
      border-radius: 4px;
      padding: 8px 12px;
      margin-top: 8px;
      border: 1px solid var(--border-subtle);
    }}
    .empty-findings {{
      color: var(--green);
      font-size: 0.95rem;
      padding: 12px 0;
    }}

    /* Legend */
    .legend-panel {{
      display: flex;
      gap: 20px;
      flex-wrap: wrap;
      font-size: 0.8rem;
      color: var(--text-muted);
      padding: 12px 16px;
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 8px;
      margin-bottom: 24px;
    }}
    .legend-item {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}
    .legend-color {{
      width: 12px;
      height: 12px;
      border-radius: 3px;
    }}

    footer {{
      text-align: center;
      font-size: 0.75rem;
      color: var(--text-muted);
      margin-top: 32px;
      padding-top: 16px;
      border-top: 1px solid var(--border);
    }}

    #copy-toast {{
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: var(--green);
      color: #fff;
      padding: 8px 16px;
      border-radius: 6px;
      font-size: 0.85rem;
      font-weight: 600;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.2s ease;
      z-index: 1000;
    }}
  </style>
</head>
<body>
<div class="container">
  <!-- Header -->
  <header class="header">
    <div class="title-group">
      <h1>📊 Revision Heatmap Studio</h1>
      <p class="subtitle">
        Manuscript: <strong>{manuscript}</strong> · Sourced Baseline: <strong>{baseline_source}</strong>
      </p>
    </div>
    <div class="header-actions">
      {control_center_html}
      <button class="btn" onclick="copyJsonExport()">📋 Copy JSON</button>
    </div>
  </header>

  <!-- KPI Stat Grid -->
  <div class="kpi-grid">
    <div class="kpi-card">
      <div class="kpi-label">Chapters Analysed</div>
      <div class="kpi-val">{total}</div>
      <div class="kpi-sub">{len(findings)} telemetry flags</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Total Words &amp; Delta</div>
      <div class="kpi-val">{total_words:,}</div>
      <div class="kpi-sub {delta_class}">Δ {delta_str} words vs baseline</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Average Churn Ratio</div>
      <div class="kpi-val">{avg_ratio:.3f}</div>
      <div class="kpi-sub">Mean modification density</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Total Churn Volume</div>
      <div class="kpi-val">{total_churn_vol:,}</div>
      <div class="kpi-sub">Avg score: {avg_churn:.1f} w/chap</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Dialogue Churn %</div>
      <div class="kpi-val">{diag_churn_pct}%</div>
      <div class="kpi-sub">Spoken dialogue rewrites</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Flags Raised</div>
      <div class="kpi-val" style="color:{'var(--amber)' if findings else 'var(--green)'};">
        {len(findings)}
      </div>
      <div class="kpi-sub">Advisory craft alerts</div>
    </div>
  </div>

  <!-- Filter & Search Controls -->
  <div class="controls-panel">
    <div class="search-row">
      <input type="text" id="filter-search" class="search-input" placeholder="🔍 Search chapter or scene filename..." oninput="applyFilters()">
    </div>
    <div class="filter-pills">
      <button class="pill-btn active" data-filter="all" onclick="setFlagFilter('all', this)">All Chapters ({total})</button>
      <button class="pill-btn" data-filter="rev-101" onclick="setFlagFilter('rev-101', this)">🔥 High Churn ({flag_counts['REV-101']})</button>
      <button class="pill-btn" data-filter="rev-102" onclick="setFlagFilter('rev-102', this)">🌱 Pristine ({flag_counts['REV-102']})</button>
      <button class="pill-btn" data-filter="rev-103" onclick="setFlagFilter('rev-103', this)">✂️ Cuts ({flag_counts['REV-103']})</button>
      <button class="pill-btn" data-filter="rev-104" onclick="setFlagFilter('rev-104', this)">📈 Expansions ({flag_counts['REV-104']})</button>
      <button class="pill-btn" data-filter="rev-105" onclick="setFlagFilter('rev-105', this)">💬 Dialogue Skew ({flag_counts['REV-105']})</button>
      <button class="pill-btn" data-filter="rev-106" onclick="setFlagFilter('rev-106', this)">⏳ Front-Loaded ({flag_counts['REV-106']})</button>
    </div>
  </div>

  <!-- Legend -->
  <div class="legend-panel">
    <div class="legend-item"><span class="legend-color" style="background:#22c55e;"></span> Stable / Low Churn (R &lt; 0.20)</div>
    <div class="legend-item"><span class="legend-color" style="background:#f59e0b;"></span> Moderate Churn (0.20 – 0.50)</div>
    <div class="legend-item"><span class="legend-color" style="background:#ef4444;"></span> High Churn (R ≥ 0.50)</div>
    <div class="legend-item"><span class="legend-color" style="background:#818cf8;"></span> Dialogue Split (Indigo)</div>
    <div class="legend-item"><span class="legend-color" style="background:#38bdf8;"></span> Prose Split (Sky Blue)</div>
  </div>

  <!-- Heatmap Table -->
  <div class="table-container">
    <table id="heatmap-table">
      <thead>
        <tr>
          <th onclick="sortTable(0, 'str')">Chapter / Scene</th>
          <th class="col-num" onclick="sortTable(1, 'num')">Words</th>
          <th class="col-num col-add" onclick="sortTable(2, 'num')">Added (+)</th>
          <th class="col-num col-del" onclick="sortTable(3, 'num')">Deleted (-)</th>
          <th class="col-num" onclick="sortTable(4, 'num')">Churn</th>
          <th class="col-num" onclick="sortTable(5, 'num')">Ratio</th>
          <th>Dialogue vs Prose Split</th>
          <th>Churn Density</th>
          <th>Flags</th>
        </tr>
      </thead>
      <tbody>
        {rows_html}
      </tbody>
    </table>
  </div>

  <!-- Findings & Advisory Guidance Section -->
  <div class="findings-panel">
    <div class="findings-header">
      <h2>🔍 Editorial Telemetry &amp; Advisory Findings ({len(findings)})</h2>
      <span style="font-size:0.8rem;color:var(--text-muted);">Subsystem 2: Descriptive Craft Observations</span>
    </div>
    <div class="findings-list">
      {findings_html}
    </div>
  </div>

  <footer>
    Ars Arcanum (Scriptorium) Revision Heatmap Studio · 100% Offline, Privacy-First Architecture · Sovereign Authoring OS
  </footer>
</div>

<div id="copy-toast">✓ JSON copied to clipboard</div>

<script id="export-json-data" type="application/json">
{json_export_str}
</script>

<script>
  let activeFilter = 'all';
  let sortCol = -1;
  let sortAsc = true;

  function toggleScenes(idx) {{
    const rows = document.querySelectorAll('.scene-row-' + idx);
    const icon = document.getElementById('toggle-icon-' + idx);
    if (!rows.length) return;
    const isHidden = rows[0].style.display === 'none';
    rows.forEach(r => r.style.display = isHidden ? 'table-row' : 'none');
    if (icon) icon.textContent = isHidden ? '▼' : '▶';
  }}

  function setFlagFilter(filterKey, btnEl) {{
    activeFilter = filterKey;
    document.querySelectorAll('.pill-btn').forEach(b => b.classList.remove('active'));
    if (btnEl) btnEl.classList.add('active');
    applyFilters();
  }}

  function applyFilters() {{
    const query = (document.getElementById('filter-search').value || '').toLowerCase().trim();
    const rows = document.querySelectorAll('#heatmap-table tbody tr.chapter-row');

    rows.forEach(r => {{
      const chapText = r.getAttribute('data-chapter') || '';
      const matchesSearch = !query || chapText.includes(query);
      const matchesFilter = activeFilter === 'all' || r.classList.contains('has-' + activeFilter);

      const visible = matchesSearch && matchesFilter;
      r.style.display = visible ? 'table-row' : 'none';

      // Hide nested scene rows if parent chapter is hidden
      const idx = r.getAttribute('data-idx');
      const sceneRows = document.querySelectorAll('.scene-row-' + idx);
      if (!visible) {{
        sceneRows.forEach(sr => sr.style.display = 'none');
        const icon = document.getElementById('toggle-icon-' + idx);
        if (icon) icon.textContent = '▶';
      }}
    }});
  }}

  function sortTable(colIndex, type) {{
    const table = document.getElementById('heatmap-table');
    const tbody = table.querySelector('tbody');
    const ths = table.querySelectorAll('th');

    if (sortCol === colIndex) {{
      sortAsc = !sortAsc;
    }} else {{
      sortCol = colIndex;
      sortAsc = true;
    }}

    ths.forEach((th, i) => {{
      th.classList.remove('sorted-asc', 'sorted-desc');
      if (i === colIndex) {{
        th.classList.add(sortAsc ? 'sorted-asc' : 'sorted-desc');
      }}
    }});

    // Collect chapter pairs (chapter row + its scene rows)
    const chapterRows = Array.from(tbody.querySelectorAll('tr.chapter-row'));
    const rowGroups = chapterRows.map(chapRow => {{
      const idx = chapRow.getAttribute('data-idx');
      const sceneRows = Array.from(tbody.querySelectorAll('.scene-row-' + idx));
      return {{ chapRow, sceneRows }};
    }});

    rowGroups.sort((a, b) => {{
      let valA = a.chapRow.children[colIndex].innerText.replace(/,/g, '').trim();
      let valB = b.chapRow.children[colIndex].innerText.replace(/,/g, '').trim();

      if (type === 'num') {{
        // Strip non-numeric like delta badges or ratios
        let numA = parseFloat(valA.match(/[-+]?[0-9]*\\.?[0-9]+/)?.[0] || '0');
        let numB = parseFloat(valB.match(/[-+]?[0-9]*\\.?[0-9]+/)?.[0] || '0');
        return sortAsc ? numA - numB : numB - numA;
      }} else {{
        return sortAsc ? valA.localeCompare(valB) : valB.localeCompare(valA);
      }}
    }});

    // Reattach sorted rows
    rowGroups.forEach(g => {{
      tbody.appendChild(g.chapRow);
      g.sceneRows.forEach(sr => tbody.appendChild(sr));
    }});
  }}

  function copyJsonExport() {{
    const jsonScript = document.getElementById('export-json-data');
    if (!jsonScript) return;
    const text = jsonScript.textContent.trim();
    navigator.clipboard.writeText(text).then(() => {{
      const toast = document.getElementById('copy-toast');
      if (toast) {{
        toast.style.opacity = '1';
        setTimeout(() => toast.style.opacity = '0', 2000);
      }}
    }}).catch(err => console.error('Failed to copy JSON:', err));
  }}
</script>
<script>
{theme_js}
</script>
</body>
</html>"""

    atomic_write(out_path, html_page)
    logger.info("Revision heatmap visual studio dashboard written to %s", out_path)
    return out_path
