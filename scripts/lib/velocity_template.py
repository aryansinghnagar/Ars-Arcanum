#!/usr/bin/env python3
"""
Ars Arcanum Velocity & Sprint Studio HTML Template (scripts/lib/velocity_template.py)
===================================================================================
Self-contained, offline HTML5 visualizer and drafting companion for manuscript words,
POV balance, dialogue ratios, historical velocity, and interactive Pomodoro sprints.

Strict Content Security Policy enforced (default-src 'none').
Zero external CDN dependencies. Zero cloud telemetry.
"""

from __future__ import annotations

import html
import json
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


def render_velocity_html(
    word_data: dict[str, Any],
    velocity_data: dict[str, Any] | None,
    output_path: Path | str,
) -> Path:
    """Generates an interactive offline HTML5 Velocity & Sprint Studio dashboard."""
    out_path = Path(output_path)
    vel = velocity_data or {}

    title = word_data.get("title", "Manuscript")
    author = word_data.get("author", "Author")
    total_words = word_data.get("total_words", 0)
    target_words = word_data.get("target_words", 80000)
    percent = word_data.get("percent_complete", 0.0)
    pages = word_data.get("estimated_pages", 0)
    reading_min = word_data.get("reading_time_minutes", round(total_words / 225, 1))
    audio_hours = word_data.get("audiobook_hours", round(total_words / 9000, 1))
    dialogue_pct = word_data.get("dialogue_percentage", 0.0)
    narrative_pct = round(100.0 - dialogue_pct, 1)

    # Velocity stats
    rolling_7d_wpd = vel.get("rolling_7d_daily_words", 0)
    rolling_7d_wpm = vel.get("rolling_7d_wpm", 0.0)
    current_streak = vel.get("current_streak_days", 0)
    best_streak = vel.get("best_streak_days", 0)

    # Prepare chapters data
    chapters = word_data.get("chapters", [])
    pov_dist = word_data.get("pov_distribution", {})
    sprint_history = vel.get("sprint_history", [])

    # Encode JSON data for interactive client-side widgets (deadline slider, charts, timer)
    client_payload = {
        "title": title,
        "total_words": total_words,
        "target_words": target_words,
        "chapters": chapters,
        "pov_distribution": pov_dist,
        "sprint_history": sprint_history,
        "rolling_7d_wpd": rolling_7d_wpd,
    }
    payload_json = json.dumps(client_payload).replace("</", "<\\/")

    # Generate Chapter Table Rows
    chapter_rows = []
    for ch in chapters:
        ch_idx = ch.get("index", 1)
        ch_title = html.escape(str(ch.get("title", "")))
        ch_pov = html.escape(str(ch.get("pov", "Unassigned")))
        ch_words = ch.get("words", 0)
        ch_dial = ch.get("dialogue_percentage", 0.0)
        ch_pages = ch.get("estimated_pages", max(1, round(ch_words / 250)))
        ch_read = ch.get("reading_time_min", round(ch_words / 225, 1))

        # Progress bar inside table
        ch_bar_width = min(100.0, round((ch_words / max(target_words / max(len(chapters), 1), 1)) * 100, 1))

        row = f"""
        <tr>
          <td style="font-weight:700;color:var(--muted);text-align:center;">{ch_idx}</td>
          <td>
            <div style="font-weight:600;color:var(--text);">{ch_title}</div>
            <div style="font-size:0.75rem;color:var(--muted);">{ch.get('volume', 'Book-01')} &bull; {ch_pages} pages &bull; ~{ch_read} min read</div>
          </td>
          <td><span class="badge badge-pov">{ch_pov}</span></td>
          <td style="text-align:right;font-weight:700;font-variant-numeric:tabular-nums;">{ch_words:,}</td>
          <td style="text-align:right;font-size:0.85rem;color:var(--accent-amber);font-variant-numeric:tabular-nums;">{ch_dial:.1f}%</td>
          <td style="min-width:120px;">
            <div class="progress-bar-bg" style="height:6px;">
              <div class="progress-bar-fill" style="width:{ch_bar_width}%;background:var(--accent-cyan);"></div>
            </div>
          </td>
        </tr>
        """
        chapter_rows.append(row)

    # Generate Sprint Session Rows
    session_rows = []
    for s in reversed(sprint_history[-20:]):  # last 20 sprints
        s_date = html.escape(str(s.get("timestamp", ""))[:16].replace("T", " "))
        s_dur = s.get("duration_min", 0.0)
        s_words = s.get("words_written", 0)
        s_wpm = s.get("wpm", 0.0)
        s_ratio = s.get("completion_ratio", 0.0) * 100.0
        s_chap = html.escape(str(s.get("chapter", "") or "General"))

        badge_class = "badge-green" if s_ratio >= 100 else ("badge-yellow" if s_ratio >= 75 else "badge-red")

        row = f"""
        <tr>
          <td style="font-size:0.85rem;color:var(--muted);font-variant-numeric:tabular-nums;">{s_date}</td>
          <td>{s_chap}</td>
          <td style="text-align:right;font-variant-numeric:tabular-nums;">{s_dur:.1f} min</td>
          <td style="text-align:right;font-weight:700;font-variant-numeric:tabular-nums;">{s_words:,}</td>
          <td style="text-align:right;font-weight:600;color:var(--accent-emerald);font-variant-numeric:tabular-nums;">{s_wpm:.1f}</td>
          <td style="text-align:right;font-variant-numeric:tabular-nums;"><span class="badge {badge_class}">{s_ratio:.0f}%</span></td>
        </tr>
        """
        session_rows.append(row)

    # POV list breakdown
    pov_items = []
    for pov, p_words in sorted(pov_dist.items(), key=lambda x: x[1], reverse=True):
        p_pct = (p_words / total_words * 100.0) if total_words > 0 else 0.0
        pov_items.append(f"""
        <div style="display:flex;justify-content:space-between;align-items:center;padding:0.5rem 0;border-bottom:1px solid var(--border);">
          <span style="font-weight:600;color:var(--text);">{html.escape(pov)}</span>
          <div style="text-align:right;">
            <span style="font-weight:700;color:var(--accent-purple);">{p_words:,} w</span>
            <span style="font-size:0.8rem;color:var(--muted);margin-left:6px;">({p_pct:.1f}%)</span>
          </div>
        </div>
        """)

    theme_css = get_theme_engine_css()
    theme_js = get_theme_engine_js()
    control_center_html = get_theme_control_center_html()

    html_content = f"""<!DOCTYPE html>
<html lang="en" data-theme="sovereign-dark">
<head>
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ars Arcanum — Word Count & Velocity Studio ({html.escape(title)})</title>
    <style>
{theme_css}
      :root {{
        --bg-main: #0b0f19;
        --bg-panel: #111827;
        --bg-panel-sub: #1f2937;
        --border: #374151;
        --border-sub: #2d3748;
        --text: #f9fafb;
        --muted: #9ca3af;
        --accent-cyan: #06b6d4;
        --accent-blue: #38bdf8;
        --accent-purple: #a855f7;
        --accent-emerald: #10b981;
        --accent-amber: #f59e0b;
        --accent-rose: #f43f5e;
      }}
      * {{ box-sizing: border-box; }}
      body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        background: var(--bg-main);
        color: var(--text);
        margin: 0;
        padding: 2rem 1.5rem;
        line-height: 1.5;
      }}
      .container {{ max-width: 1180px; margin: 0 auto; }}
      .studio-header {{
        background: linear-gradient(135deg, #111827 0%, #1e1b4b 100%);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.5);
      }}
      .studio-header h1 {{ margin: 0 0 0.5rem 0; font-size: 2rem; font-weight: 800; color: #fff; letter-spacing: -0.025em; }}
      .studio-header .subtitle {{ color: var(--muted); font-size: 1rem; margin-bottom: 1.5rem; }}
      .progress-bar-bg {{
        background: #1f2937;
        border-radius: 9999px;
        height: 14px;
        overflow: hidden;
        position: relative;
      }}
      .progress-bar-fill {{
        height: 100%;
        border-radius: 9999px;
        transition: width 0.4s ease;
      }}
      .kpi-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 1rem;
        margin-bottom: 2rem;
      }}
      .kpi-card {{
        background: var(--bg-panel);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 1.25rem;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
      }}
      .kpi-label {{ font-size: 0.75rem; text-transform: uppercase; font-weight: 700; color: var(--muted); letter-spacing: 0.05em; }}
      .kpi-val {{ font-size: 1.85rem; font-weight: 800; margin: 0.35rem 0; color: #fff; font-variant-numeric: tabular-nums; }}
      .kpi-sub {{ font-size: 0.8rem; color: var(--muted); }}
      .split-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1.5rem;
        margin-bottom: 2rem;
      }}
      @media (max-width: 900px) {{
        .split-grid {{ grid-template-columns: 1fr; }}
      }}
      .panel {{
        background: var(--bg-panel);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.5rem;
      }}
      .panel h2 {{ margin: 0 0 1.25rem 0; font-size: 1.25rem; font-weight: 700; color: #fff; border-bottom: 1px solid var(--border-sub); padding-bottom: 0.75rem; }}
      .timer-container {{
        text-align: center;
        padding: 1rem 0;
      }}
      .timer-circle-wrap {{
        position: relative;
        width: 200px;
        height: 200px;
        margin: 0 auto 1.5rem auto;
      }}
      .timer-display {{
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        text-align: center;
      }}
      .timer-time {{ font-size: 2.5rem; font-weight: 800; font-family: monospace; color: #fff; }}
      .timer-phase {{ font-size: 0.8rem; color: var(--accent-cyan); font-weight: 700; text-transform: uppercase; }}
      .btn-group {{ display: flex; justify-content: center; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1rem; }}
      .btn {{
        background: var(--bg-panel-sub);
        color: var(--text);
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        font-size: 0.875rem;
        cursor: pointer;
        transition: all 0.2s;
      }}
      .btn:hover {{ background: #374151; border-color: var(--accent-cyan); }}
      .btn-primary {{ background: var(--accent-cyan); color: #0b0f19; border: none; font-weight: 700; }}
      .btn-primary:hover {{ background: #22d3ee; }}
      .btn-rose {{ background: var(--accent-rose); color: #fff; border: none; }}
      .btn-rose:hover {{ background: #fb7185; }}
      .btn-active {{ background: #374151; border-color: var(--accent-cyan); color: var(--accent-cyan); }}
      .input-row {{
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 0.75rem;
        margin-top: 1rem;
      }}
      .text-input {{
        background: #0f172a;
        border: 1px solid var(--border);
        border-radius: 6px;
        color: #fff;
        padding: 0.4rem 0.75rem;
        font-size: 0.9rem;
        width: 110px;
        text-align: center;
      }}
      table {{ width: 100%; border-collapse: collapse; font-size: 0.9rem; }}
      th {{ text-align: left; padding: 0.75rem 0.5rem; color: var(--muted); border-bottom: 1px solid var(--border); font-size: 0.8rem; text-transform: uppercase; }}
      td {{ padding: 0.75rem 0.5rem; border-bottom: 1px solid var(--border-sub); }}
      tr:hover td {{ background: rgba(255,255,255,0.02); }}
      .badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; }}
      .badge-pov {{ background: rgba(168, 85, 247, 0.15); color: #d8b4fe; border: 1px solid rgba(168, 85, 247, 0.3); }}
      .badge-green {{ background: rgba(16, 185, 129, 0.15); color: #6ee7b7; }}
      .badge-yellow {{ background: rgba(245, 158, 11, 0.15); color: #fcd34d; }}
      .badge-red {{ background: rgba(244, 63, 94, 0.15); color: #fda4af; }}
      .slider-box {{
        background: #0f172a;
        border: 1px solid var(--border-sub);
        border-radius: 8px;
        padding: 1.25rem;
        margin-top: 1rem;
      }}
      .range-slider {{
        width: 100%;
        accent-color: var(--accent-emerald);
        cursor: pointer;
      }}
    </style>
</head>
<body>

<div class="container">

  <!-- Header Banner -->
  <div class="studio-header">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:1rem;">
      <div>
        <h1>📖 {html.escape(title)}</h1>
        <div class="subtitle">By {html.escape(author)} &bull; Sovereign Drafting & Word Velocity Studio</div>
      </div>
      <div style="display:flex;align-items:center;gap:1rem;flex-wrap:wrap;">
        <div style="text-align:right;">
          <div style="font-size:2rem;font-weight:800;color:var(--accent-cyan);">{total_words:,} <span style="font-size:1rem;color:var(--muted);font-weight:400;">/ {target_words:,} words</span></div>
          <div style="font-size:0.9rem;color:var(--muted);">{percent:.1f}% Target Achieved</div>
        </div>
        {control_center_html}
      </div>
    </div>

    <div class="progress-bar-bg" style="margin-top:1rem;height:12px;">
      <div class="progress-bar-fill" style="width:{min(100.0, percent)}%;background:linear-gradient(90deg, #06b6d4, #10b981);"></div>
    </div>
  </div>

  <!-- KPI Cards Grid -->
  <div class="kpi-grid">
    <div class="kpi-card">
      <div class="kpi-label">Estimated Pages</div>
      <div class="kpi-val" style="color:var(--accent-blue);">{pages:,}</div>
      <div class="kpi-sub">Standard 250 w/page</div>
    </div>

    <div class="kpi-card">
      <div class="kpi-label">Reading Time</div>
      <div class="kpi-val" style="color:var(--accent-cyan);">{reading_min:.0f} <span style="font-size:1rem;font-weight:400;">min</span></div>
      <div class="kpi-sub">Paced at ~225 WPM</div>
    </div>

    <div class="kpi-card">
      <div class="kpi-label">Audiobook Duration</div>
      <div class="kpi-val" style="color:var(--accent-purple);">{audio_hours:.1f} <span style="font-size:1rem;font-weight:400;">hrs</span></div>
      <div class="kpi-sub">Narrated at ~150 WPM</div>
    </div>

    <div class="kpi-card">
      <div class="kpi-label">Dialogue Ratio</div>
      <div class="kpi-val" style="color:var(--accent-amber);">{dialogue_pct:.1f}%</div>
      <div class="kpi-sub">{narrative_pct:.1f}% Narrative Prose</div>
    </div>

    <div class="kpi-card">
      <div class="kpi-label">7-Day Pace</div>
      <div class="kpi-val" style="color:var(--accent-emerald);">{rolling_7d_wpd:,}</div>
      <div class="kpi-sub">Words / Day ({rolling_7d_wpm:.1f} WPM)</div>
    </div>

    <div class="kpi-card">
      <div class="kpi-label">Writing Streak</div>
      <div class="kpi-val" style="color:#fbbf24;">{current_streak} <span style="font-size:1rem;font-weight:400;">days</span></div>
      <div class="kpi-sub">Best Streak: {best_streak} days</div>
    </div>
  </div>

  <!-- Split Grid: Interactive Sprint Timer + Deadline Forecaster -->
  <div class="split-grid">

    <!-- Sprint Timer Widget -->
    <div class="panel">
      <h2>⏱️ Interactive Pomodoro & Sprint Timer</h2>
      <div class="timer-container">

        <!-- Duration Customization Buttons -->
        <div style="font-size:0.8rem;color:var(--muted);margin-bottom:0.4rem;text-transform:uppercase;font-weight:700;">Duration Preset (Minutes)</div>
        <div class="btn-group" id="dur-buttons">
          <button class="btn" onclick="setTimerDuration(15)">15m</button>
          <button class="btn" onclick="setTimerDuration(20)">20m</button>
          <button class="btn btn-active" onclick="setTimerDuration(25)">25m</button>
          <button class="btn" onclick="setTimerDuration(30)">30m</button>
          <button class="btn" onclick="setTimerDuration(45)">45m</button>
          <button class="btn" onclick="setTimerDuration(50)">50m</button>
          <button class="btn" onclick="setTimerDuration(60)">60m</button>
        </div>

        <!-- Target Words Preset -->
        <div style="font-size:0.8rem;color:var(--muted);margin-bottom:0.4rem;text-transform:uppercase;font-weight:700;">Target Words</div>
        <div class="btn-group" id="target-buttons">
          <button class="btn" onclick="setSprintTarget(250)">250w</button>
          <button class="btn btn-active" onclick="setSprintTarget(500)">500w</button>
          <button class="btn" onclick="setSprintTarget(750)">750w</button>
          <button class="btn" onclick="setSprintTarget(1000)">1,000w</button>
          <button class="btn" onclick="setSprintTarget(1500)">1,500w</button>
        </div>

        <!-- Circular Progress Ring SVG -->
        <div class="timer-circle-wrap">
          <svg width="200" height="200" viewBox="0 0 200 200">
            <circle cx="100" cy="100" r="85" fill="none" stroke="#1f2937" stroke-width="12"></circle>
            <circle id="timer-ring" cx="100" cy="100" r="85" fill="none" stroke="#06b6d4" stroke-width="12"
                    stroke-dasharray="534" stroke-dashoffset="0" stroke-linecap="round"
                    transform="rotate(-90 100 100)" style="transition: stroke-dashoffset 1s linear;"></circle>
          </svg>
          <div class="timer-display">
            <div class="timer-time" id="timer-time-text">25:00</div>
            <div class="timer-phase" id="timer-phase-text">Focus Sprint</div>
          </div>
        </div>

        <!-- Timer Controls -->
        <div class="btn-group">
          <button class="btn btn-primary" id="btn-start" onclick="toggleTimer()">Start Sprint</button>
          <button class="btn" onclick="resetTimer()">Reset</button>
        </div>

        <!-- Live Sprint Word Calculator -->
        <div class="input-row">
          <label style="font-size:0.85rem;color:var(--muted);">Words Written:</label>
          <input type="number" id="sprint-words-input" class="text-input" placeholder="0" oninput="calculateSprintWpm()">
          <span id="sprint-wpm-calc" style="font-size:0.85rem;font-weight:700;color:var(--accent-emerald);">0.0 WPM</span>
        </div>

        <!-- Live Zen Drafting Sandbox with Authentic Typewriter Audio -->
        <div style="margin-top:1.25rem; text-align:left; border-top:1px solid var(--border); padding-top:1rem;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem;">
            <label style="font-size:0.8rem; color:var(--muted); text-transform:uppercase; font-weight:700;">Zen Drafting Pad</label>
            <span style="font-size:0.75rem; color:var(--accent-cyan); font-weight:600;">⌨️ Typewriter Sound Active</span>
          </div>
          <textarea id="zen-drafting-pad" class="typewriter-target" placeholder="Draft your sprint prose here... Typewriter audio synthesizes live with pitch variance and carriage bell!" style="width:100%; height:110px; background:var(--bg-panel-sub); color:var(--text); border:1px solid var(--border); border-radius:8px; padding:0.75rem; font-family:monospace; font-size:0.9rem; line-height:1.5; resize:vertical; outline:none;" oninput="syncZenDraftWords(this.value)"></textarea>
        </div>

      </div>
    </div>

    <!-- Deadline Forecaster & POV Distribution -->
    <div class="panel" style="display:flex;flex-direction:column;justify-content:space-between;">
      <div>
        <h2>🎯 Dynamic Deadline & Velocity Forecaster</h2>
        <p style="color:var(--muted);font-size:0.875rem;margin-top:0;">Adjust your assumed daily drafting velocity to project estimated manuscript completion dates.</p>

        <div class="slider-box">
          <div style="display:flex;justify-content:space-between;margin-bottom:0.5rem;">
            <span style="font-weight:600;font-size:0.9rem;">Daily Target Pace:</span>
            <span id="pace-display" style="font-weight:800;color:var(--accent-emerald);">1,000 words/day</span>
          </div>
          <input type="range" min="100" max="4000" step="50" value="1000" class="range-slider" id="pace-slider" oninput="updateForecast(this.value)">

          <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-top:1.25rem;">
            <div>
              <div style="font-size:0.75rem;color:var(--muted);text-transform:uppercase;">Words Remaining</div>
              <div id="words-rem-display" style="font-size:1.35rem;font-weight:700;color:#fff;">{(target_words - total_words):,}</div>
            </div>
            <div>
              <div style="font-size:0.75rem;color:var(--muted);text-transform:uppercase;">Projected Finish Date</div>
              <div id="date-finish-display" style="font-size:1.35rem;font-weight:700;color:var(--accent-cyan);">Calculating...</div>
            </div>
          </div>
        </div>
      </div>

      <div style="margin-top:1.5rem;">
        <h3 style="margin:0 0 0.75rem 0;font-size:1rem;color:#fff;">🎭 POV Distribution Share</h3>
        <div id="pov-container">
          {''.join(pov_items) or '<p style="color:var(--muted);font-size:0.85rem;">Single / Unassigned POV.</p>'}
        </div>
      </div>
    </div>

  </div>

  <!-- Chapters Breakdown Table -->
  <div class="panel" style="margin-bottom:2rem;">
    <h2>📑 Chapter Prose & Dialogue Telemetry ({len(chapters)} Chapters)</h2>
    <div style="overflow-x:auto;">
      <table>
        <thead>
          <tr>
            <th style="width:40px;text-align:center;">#</th>
            <th>Chapter Title</th>
            <th>POV</th>
            <th style="text-align:right;">Words</th>
            <th style="text-align:right;">Dialogue %</th>
            <th>Target Progress</th>
          </tr>
        </thead>
        <tbody>
          {''.join(chapter_rows) or '<tr><td colspan="6" style="color:var(--muted);text-align:center;">No chapters discovered in manuscript scope.</td></tr>'}
        </tbody>
      </table>
    </div>
  </div>

  <!-- Historical Sprint Sessions Table -->
  <div class="panel">
    <h2>⚡ Recent Drafting Sprint History (Total Sprints: {len(sprint_history)})</h2>
    <div style="overflow-x:auto;">
      <table>
        <thead>
          <tr>
            <th>Timestamp</th>
            <th>Target Chapter</th>
            <th style="text-align:right;">Duration</th>
            <th style="text-align:right;">Words Added</th>
            <th style="text-align:right;">Velocity (WPM)</th>
            <th style="text-align:right;">Target Ratio</th>
          </tr>
        </thead>
        <tbody>
          {''.join(session_rows) or '<tr><td colspan="6" style="color:var(--muted);text-align:center;">No sprint sessions logged yet. Run <code>arcanum sprint start</code> to begin drafting!</td></tr>'}
        </tbody>
      </table>
    </div>
  </div>

</div>

<script>
  // Client-Side Payload
  const DATA = {payload_json};

  // 1. Deadline Forecast Calculator
  function updateForecast(pace) {{
    document.getElementById('pace-display').innerText = Number(pace).toLocaleString() + ' words/day';
    const remaining = Math.max(0, DATA.target_words - DATA.total_words);
    document.getElementById('words-rem-display').innerText = remaining.toLocaleString() + ' words';

    if (remaining <= 0) {{
      document.getElementById('date-finish-display').innerText = 'Completed! 🎉';
      return;
    }}

    const daysNeeded = Math.ceil(remaining / Math.max(1, pace));
    const targetDate = new Date();
    targetDate.setDate(targetDate.getDate() + daysNeeded);

    const options = {{ year: 'numeric', month: 'short', day: 'numeric' }};
    document.getElementById('date-finish-display').innerText = targetDate.toLocaleDateString(undefined, options) + ' (' + daysNeeded + 'd)';
  }}
  updateForecast(1000);

  // 2. In-Browser Interactive Pomodoro Timer
  let timerDurationSec = 25 * 60;
  let timerRemainingSec = 25 * 60;
  let timerInterval = null;
  let isTimerRunning = false;
  let sprintTargetWords = 500;
  const circumference = 2 * Math.PI * 85; // 534.07

  function setTimerDuration(min) {{
    if (isTimerRunning) return;
    timerDurationSec = min * 60;
    timerRemainingSec = timerDurationSec;
    updateTimerDisplay();

    // Highlight active button
    const btns = document.querySelectorAll('#dur-buttons .btn');
    btns.forEach(b => {{
      if (b.innerText === min + 'm') b.classList.add('btn-active');
      else b.classList.remove('btn-active');
    }});
  }}

  function setSprintTarget(words) {{
    sprintTargetWords = words;
    const btns = document.querySelectorAll('#target-buttons .btn');
    btns.forEach(b => {{
      if (b.innerText.replace(',', '').includes(words)) b.classList.add('btn-active');
      else b.classList.remove('btn-active');
    }});
    calculateSprintWpm();
  }}

  function updateTimerDisplay() {{
    const min = Math.floor(timerRemainingSec / 60);
    const sec = timerRemainingSec % 60;
    document.getElementById('timer-time-text').innerText =
      String(min).padStart(2, '0') + ':' + String(sec).padStart(2, '0');

    // Update SVG Ring
    const fraction = (timerDurationSec - timerRemainingSec) / Math.max(1, timerDurationSec);
    const offset = circumference * (1 - fraction);
    document.getElementById('timer-ring').style.strokeDashoffset = offset;
  }}

  function toggleTimer() {{
    const btn = document.getElementById('btn-start');
    if (!isTimerRunning) {{
      // Start
      isTimerRunning = true;
      btn.innerText = 'Pause Sprint';
      btn.classList.add('btn-rose');
      btn.classList.remove('btn-primary');
      document.getElementById('timer-phase-text').innerText = 'Writing in Flow';

      timerInterval = setInterval(() => {{
        if (timerRemainingSec > 0) {{
          timerRemainingSec--;
          updateTimerDisplay();
          calculateSprintWpm();
        }} else {{
          clearInterval(timerInterval);
          isTimerRunning = false;
          btn.innerText = 'Sprint Completed!';
          btn.classList.remove('btn-rose');
          btn.classList.add('btn-primary');
          document.getElementById('timer-phase-text').innerText = 'Session Finished!';
          playCompletionChime();
        }}
      }}, 1000);
    }} else {{
      // Pause
      clearInterval(timerInterval);
      isTimerRunning = false;
      btn.innerText = 'Resume Sprint';
      btn.classList.remove('btn-rose');
      btn.classList.add('btn-primary');
      document.getElementById('timer-phase-text').innerText = 'Paused';
    }}
  }}

  function resetTimer() {{
    clearInterval(timerInterval);
    isTimerRunning = false;
    timerRemainingSec = timerDurationSec;
    const btn = document.getElementById('btn-start');
    btn.innerText = 'Start Sprint';
    btn.classList.remove('btn-rose');
    btn.classList.add('btn-primary');
    document.getElementById('timer-phase-text').innerText = 'Focus Sprint';
    updateTimerDisplay();
  }}

  function calculateSprintWpm() {{
    const wordsInput = document.getElementById('sprint-words-input');
    const words = parseInt(wordsInput.value, 10) || 0;
    const elapsedSec = timerDurationSec - timerRemainingSec;
    const elapsedMin = Math.max(0.1, elapsedSec / 60);
    const wpm = (words / elapsedMin).toFixed(1);
    const ratio = ((words / Math.max(1, sprintTargetWords)) * 100).toFixed(0);

    document.getElementById('sprint-wpm-calc').innerText = wpm + ' WPM (' + ratio + '% target)';
  }}

  // Web Audio API Synthesized Chime (Zero External Files)
  function playCompletionChime() {{
    try {{
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(587.33, ctx.currentTime); // D5
      osc.frequency.setValueAtTime(880.00, ctx.currentTime + 0.15); // A5
      gain.gain.setValueAtTime(0.3, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.8);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.8);
    }} catch (e) {{}}
  }}

  // Initial render
  updateTimerDisplay();

  function syncZenDraftWords(val) {{
    const words = (val || '').trim().split(/\\s+/).filter(Boolean).length;
    const input = document.getElementById('sprint-words-input');
    if (input) {{
      input.value = words;
      calculateSprintWpm();
    }}
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


__all__ = ["render_velocity_html"]
