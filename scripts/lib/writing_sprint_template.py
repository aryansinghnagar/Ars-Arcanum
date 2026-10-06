#!/usr/bin/env python3
"""
Ars Arcanum Writing Sprint HTML Dashboard Template
===================================================
scripts/lib/writing_sprint_template.py

Generates standalone, CSP-compliant offline HTML velocity dashboards
for writing sprints, tracking daily streaks, bar charts, and session history.
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

try:
    from lib._bootstrap import atomic_write
except ImportError:
    from _bootstrap import atomic_write  # type: ignore[no-redef]

logger = logging.getLogger("arcanum.writing_sprint.template")

_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Ars Arcanum · Writing Sprint Dashboard</title>
  <style>
    :root {{
      --bg: #0d0f14;
      --surface: #161922;
      --card: #1e2330;
      --border: #2a3148;
      --accent: #7c6af7;
      --accent2: #e2a84b;
      --text: #d4d8e8;
      --muted: #6b7499;
      --good: #4caf80;
      --warn: #e2a84b;
      --danger: #e05a5a;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: var(--bg);
      color: var(--text);
      font-family: 'Georgia', serif;
      padding: 2rem;
      min-height: 100vh;
    }}
    h1 {{
      font-size: 1.9rem;
      color: var(--accent);
      letter-spacing: .04em;
      margin-bottom: .25rem;
    }}
    .subtitle {{
      color: var(--muted);
      font-size: .9rem;
      margin-bottom: 2rem;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 1rem;
      margin-bottom: 2rem;
    }}
    .card {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 1.25rem 1rem;
      text-align: center;
    }}
    .card .label {{
      font-size: .75rem;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: .08em;
      margin-bottom: .4rem;
    }}
    .card .value {{
      font-size: 1.9rem;
      font-weight: bold;
      color: var(--accent);
    }}
    .card .unit {{
      font-size: .75rem;
      color: var(--muted);
      margin-top: .15rem;
    }}
    .section-title {{
      font-size: 1.1rem;
      color: var(--accent2);
      border-bottom: 1px solid var(--border);
      padding-bottom: .5rem;
      margin: 2rem 0 1rem;
    }}
    /* Bar chart */
    .chart-wrap {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 1.5rem 1rem 1rem;
      overflow-x: auto;
    }}
    .bars {{
      display: flex;
      align-items: flex-end;
      gap: 6px;
      height: 160px;
    }}
    .bar-col {{
      display: flex;
      flex-direction: column;
      align-items: center;
      flex: 1;
      min-width: 32px;
    }}
    .bar {{
      width: 100%;
      background: linear-gradient(180deg, var(--accent) 0%, #4a3cc7 100%);
      border-radius: 4px 4px 0 0;
      transition: opacity .2s;
    }}
    .bar:hover {{ opacity: .8; }}
    .bar-label {{
      font-size: .6rem;
      color: var(--muted);
      margin-top: .4rem;
      writing-mode: vertical-rl;
      transform: rotate(180deg);
      white-space: nowrap;
    }}
    .bar-val {{
      font-size: .65rem;
      color: var(--text);
      margin-bottom: 2px;
    }}
    /* Session table */
    .tbl-wrap {{ overflow-x: auto; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: .85rem;
    }}
    thead tr {{
      background: var(--surface);
    }}
    th, td {{
      padding: .6rem .8rem;
      border: 1px solid var(--border);
      text-align: left;
    }}
    th {{
      color: var(--muted);
      font-weight: normal;
      text-transform: uppercase;
      font-size: .72rem;
      letter-spacing: .06em;
    }}
    tr:nth-child(even) {{ background: var(--surface); }}
    .pill {{
      display: inline-block;
      padding: .1rem .55rem;
      border-radius: 999px;
      font-size: .7rem;
      font-weight: bold;
    }}
    .pill-good {{ background: #1e3d2f; color: var(--good); }}
    .pill-warn {{ background: #3d2e1a; color: var(--warn); }}
    .pill-neutral {{ background: #2a2d42; color: var(--text); }}
    footer {{
      margin-top: 3rem;
      text-align: center;
      font-size: .75rem;
      color: var(--muted);
    }}
  </style>
</head>
<body>
  <h1>⚡ Writing Sprint Dashboard</h1>
  <p class="subtitle">Ars Arcanum · Sovereign Craft Analytics · Generated {generated_at}</p>

  <!-- Stat Cards -->
  <div class="grid">
    <div class="card">
      <div class="label">Total Words</div>
      <div class="value">{total_words}</div>
      <div class="unit">across all sprints</div>
    </div>
    <div class="card">
      <div class="label">Avg WPM</div>
      <div class="value">{avg_wpm}</div>
      <div class="unit">words per minute</div>
    </div>
    <div class="card">
      <div class="label">Best WPM</div>
      <div class="value">{best_wpm}</div>
      <div class="unit">personal record</div>
    </div>
    <div class="card">
      <div class="label">Sessions</div>
      <div class="value">{total_sessions}</div>
      <div class="unit">completed sprints</div>
    </div>
    <div class="card">
      <div class="label">Current Streak</div>
      <div class="value">{current_streak}</div>
      <div class="unit">consecutive days</div>
    </div>
    <div class="card">
      <div class="label">Longest Streak</div>
      <div class="value">{longest_streak}</div>
      <div class="unit">days</div>
    </div>
    <div class="card">
      <div class="label">Today</div>
      <div class="value">{today_words}</div>
      <div class="unit">words written</div>
    </div>
  </div>

  <!-- Daily Bar Chart -->
  <div class="section-title">Daily Word Count (Last {chart_days} Days)</div>
  <div class="chart-wrap">
    <div class="bars">
{bar_rows}
    </div>
  </div>

  <!-- Session Table -->
  <div class="section-title">Session History</div>
  <div class="tbl-wrap">
    <table>
      <thead>
        <tr>
          <th>#</th>
          <th>Date</th>
          <th>Start</th>
          <th>Duration (min)</th>
          <th>Words</th>
          <th>WPM</th>
          <th>Target</th>
          <th>Goal</th>
        </tr>
      </thead>
      <tbody>
{table_rows}
      </tbody>
    </table>
  </div>

  <footer>Ars Arcanum Scriptorium · Offline Sprint Analytics Engine</footer>
</body>
</html>
"""


def _build_bar_rows(sessions: list[Any], max_days: int = 30) -> str:
    """Build pure-CSS bar-chart HTML rows for the last *max_days* calendar days."""
    date_words: dict[str, int] = {}
    for s in sessions:
        day = s.start_ts[:10]
        date_words[day] = date_words.get(day, 0) + s.actual_words

    today = date.today()
    days: list[str] = [(today - timedelta(days=i)).isoformat() for i in range(max_days - 1, -1, -1)]

    if not date_words:
        return "      <div class='bar-col'><span style='color:var(--muted);font-size:.8rem'>No data yet</span></div>"

    max_words = max((date_words.get(d, 0) for d in days), default=1) or 1
    lines: list[str] = []
    for d in days:
        words = date_words.get(d, 0)
        height_pct = round((words / max_words) * 100)
        short_label = d[5:]  # MM-DD
        lines.append(
            f"      <div class='bar-col'>"
            f"<div class='bar-val'>{words if words else ''}</div>"
            f"<div class='bar' style='height:{height_pct}%' title='{d}: {words} words'></div>"
            f"<div class='bar-label'>{short_label}</div>"
            f"</div>"
        )
    return "\n".join(lines)


def _build_table_rows(sessions: list[Any]) -> str:
    """Build HTML table rows for all sessions, newest first."""
    if not sessions:
        return "        <tr><td colspan='8' style='text-align:center;color:var(--muted)'>No sessions recorded yet.</td></tr>"

    sorted_sessions = sorted(sessions, key=lambda s: s.start_ts, reverse=True)
    rows: list[str] = []
    for idx, s in enumerate(sorted_sessions, start=1):
        met_goal = s.actual_words >= s.target_words
        pill_class = "pill-good" if met_goal else "pill-warn"
        pill_text = "✓ Met" if met_goal else "~ In Progress"
        date_part = s.start_ts[:10]
        time_part = s.start_ts[11:19] if len(s.start_ts) > 10 else ""
        rows.append(
            f"        <tr>"
            f"<td>{idx}</td>"
            f"<td>{date_part}</td>"
            f"<td>{time_part}</td>"
            f"<td>{s.duration_minutes:.1f}</td>"
            f"<td>{s.actual_words}</td>"
            f"<td>{s.wpm:.1f}</td>"
            f"<td>{s.target_words}</td>"
            f"<td><span class='pill {pill_class}'>{pill_text}</span></td>"
            f"</tr>"
        )
    return "\n".join(rows)


def generate_sprint_report_html(
    stats: dict[str, Any],
    streak: dict[str, Any],
    sessions: list[Any],
    output_path: Path,
) -> None:
    """
    Generate a standalone, CSP-compliant offline HTML velocity dashboard.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    bar_rows = _build_bar_rows(sessions, max_days=30)
    table_rows = _build_table_rows(sessions)

    html_content = _HTML_TEMPLATE.format(
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
        total_words=f"{stats.get('total_words', 0):,}",
        avg_wpm=f"{stats.get('avg_wpm', 0.0):.1f}",
        best_wpm=f"{stats.get('best_wpm', 0.0):.1f}",
        total_sessions=stats.get("total_sessions", 0),
        current_streak=streak.get("current_streak_days", 0),
        longest_streak=streak.get("longest_streak_days", 0),
        today_words=f"{streak.get('today_words', 0):,}",
        chart_days=30,
        bar_rows=bar_rows,
        table_rows=table_rows,
    )

    atomic_write(output_path, html_content)
    logger.info("Sprint report written to %s", output_path)
