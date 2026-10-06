#!/usr/bin/env python3
"""
Ars Arcanum Revision Density Heatmap HTML Generator
(scripts/lib/revision_heatmap_template.py)
================================================================================
Zero-dependency, offline CSP-compliant HTML/CSS heatmap report generator for
manuscript revision density and churn analysis.
"""

import html
import logging
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lib.revision_heatmap import ChapterRevisionStats

__all__ = [
    "_CSP",
    "_FLAG_LABELS",
    "_bar_width",
    "_churn_color",
    "generate_revision_heatmap_html",
]

logger = logging.getLogger("arcanum.revision_heatmap")

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

_FLAG_LABELS: dict[str, str] = {
    "REV-101": "⚠ REV-101 Over-Revised",
    "REV-102": "🔵 REV-102 Pristine Draft",
    "": "",
}


def _churn_color(churn_ratio: float) -> str:
    """Map churn_ratio to a hex color for the heatmap bar."""
    if churn_ratio >= 0.5:
        return "#ef4444"  # red
    if churn_ratio >= 0.2:
        return "#f59e0b"  # amber
    return "#22c55e"  # green


def _bar_width(churn_score: int, max_score: int) -> int:
    """Compute a bar width percentage (1–100) relative to max_score."""
    if max_score == 0:
        return 1
    return max(1, min(100, round(churn_score / max_score * 100)))


def generate_revision_heatmap_html(
    churn_data: dict,
    output_path: Path,
) -> None:
    """Generate a standalone CSP-compliant offline HTML heatmap.

    Parameters
    ----------
    churn_data:
        Dict with keys: manuscript, chapters (list[ChapterRevisionStats]),
        findings, avg_churn_score, total_chapters, max_churn_score.
    output_path:
        Destination .html file path.
    """
    manuscript = html.escape(str(churn_data.get("manuscript", "Manuscript")))
    chapters: list[ChapterRevisionStats] = churn_data.get("chapters", [])
    findings: list[dict] = churn_data.get("findings", [])
    avg_churn = churn_data.get("avg_churn_score", 0.0)
    total = churn_data.get("total_chapters", len(chapters))
    max_score = churn_data.get("max_churn_score", 0)
    if max_score == 0 and chapters:
        max_score = max(c.churn_score for c in chapters)

    # Build chapter rows HTML
    rows_html_parts: list[str] = []
    for ch in chapters:
        color = _churn_color(ch.churn_ratio)
        bar_w = _bar_width(ch.churn_score, max_score)
        flag_label = _FLAG_LABELS.get(ch.flag, "")
        flag_badge = (
            f' <span style="font-size:0.75rem;padding:2px 6px;border-radius:4px;'
            f'background:{color};color:#fff;margin-left:8px;">{html.escape(flag_label)}</span>'
            if flag_label
            else ""
        )
        snapshot_indicator = (
            '<span style="color:#6b7280;font-size:0.75rem;"> (no snapshot)</span>'
            if not ch.has_snapshot
            else ""
        )
        rows_html_parts.append(
            f"""
      <tr>
        <td style="padding:6px 8px;font-family:monospace;font-size:0.85rem;max-width:280px;
                   overflow:hidden;text-overflow:ellipsis;white-space:nowrap;"
            title="{html.escape(ch.rel_path)}">
          {html.escape(ch.chapter)}{snapshot_indicator}{flag_badge}
        </td>
        <td style="padding:6px 8px;text-align:right;font-size:0.85rem;">{ch.word_count:,}</td>
        <td style="padding:6px 8px;text-align:right;font-size:0.85rem;">{ch.insertions:,}</td>
        <td style="padding:6px 8px;text-align:right;font-size:0.85rem;">{ch.deletions:,}</td>
        <td style="padding:6px 8px;text-align:right;font-size:0.85rem;">{ch.churn_score:,}</td>
        <td style="padding:6px 8px;text-align:right;font-size:0.85rem;">{ch.churn_ratio:.3f}</td>
        <td style="padding:6px 16px;min-width:120px;">
          <div style="background:#e5e7eb;border-radius:4px;height:16px;width:100%;">
            <div style="background:{color};border-radius:4px;height:16px;width:{bar_w}%;"></div>
          </div>
        </td>
      </tr>"""
        )
    rows_html = "".join(rows_html_parts)

    # Build findings HTML
    findings_parts: list[str] = []
    for f in findings:
        code = html.escape(f.get("code", ""))
        msg = html.escape(f.get("message", ""))
        badge_color = "#ef4444" if code == "REV-101" else "#3b82f6"
        findings_parts.append(
            f"""<li style="margin:6px 0;">
        <span style="background:{badge_color};color:#fff;padding:2px 8px;border-radius:4px;
                     font-size:0.8rem;margin-right:8px;">{code}</span>
        {msg}
      </li>"""
        )
    findings_html = (
        "<ul style='list-style:none;padding:0;margin:0;'>" + "".join(findings_parts) + "</ul>"
        if findings_parts
        else "<p style='color:#6b7280;'>No revision flags raised.</p>"
    )

    # Legend items
    legend_items = [
        ("#22c55e", "Low churn (ratio &lt; 0.2)"),
        ("#f59e0b", "Medium churn (0.2 – 0.5)"),
        ("#ef4444", "High churn (ratio ≥ 0.5)"),
    ]
    legend_html = "".join(
        f'<span style="display:inline-flex;align-items:center;margin-right:16px;">'
        f'<span style="display:inline-block;width:14px;height:14px;border-radius:3px;'
        f'background:{c};margin-right:6px;"></span>{label}</span>'
        for c, label in legend_items
    )

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="Content-Security-Policy" content="{_CSP}">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Revision Heatmap — {manuscript}</title>
  <style>
    *,*::before,*::after{{box-sizing:border-box;}}
    body{{font-family:system-ui,sans-serif;margin:0;padding:24px;
         background:#f9fafb;color:#111827;}}
    h1{{font-size:1.5rem;margin-bottom:4px;}}
    .subtitle{{color:#6b7280;font-size:0.9rem;margin-bottom:20px;}}
    .stats{{display:flex;gap:20px;flex-wrap:wrap;margin-bottom:20px;}}
    .stat-card{{background:#fff;border:1px solid #e5e7eb;border-radius:8px;
                padding:12px 20px;min-width:140px;}}
    .stat-label{{font-size:0.75rem;color:#6b7280;text-transform:uppercase;
                 letter-spacing:.05em;}}
    .stat-value{{font-size:1.5rem;font-weight:700;margin-top:4px;}}
    table{{width:100%;border-collapse:collapse;background:#fff;
           border:1px solid #e5e7eb;border-radius:8px;overflow:hidden;
           margin-bottom:24px;}}
    thead tr{{background:#f3f4f6;}}
    th{{padding:8px 8px;text-align:left;font-size:0.75rem;text-transform:uppercase;
        letter-spacing:.05em;color:#6b7280;}}
    tbody tr:hover{{background:#f9fafb;}}
    tbody tr:nth-child(even){{background:#fdfdfd;}}
    .findings-box{{background:#fff;border:1px solid #e5e7eb;border-radius:8px;
                  padding:16px 20px;margin-bottom:24px;}}
    .legend{{font-size:0.8rem;color:#374151;margin-bottom:20px;}}
    footer{{font-size:0.75rem;color:#9ca3af;margin-top:24px;}}
  </style>
</head>
<body>
  <h1>📊 Revision Heatmap — {manuscript}</h1>
  <p class="subtitle">Ars Arcanum · Manuscript Revision Density &amp; Churn Analysis</p>

  <div class="stats">
    <div class="stat-card">
      <div class="stat-label">Total Chapters</div>
      <div class="stat-value">{total}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Avg Churn Score</div>
      <div class="stat-value">{avg_churn:.1f}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Max Churn Score</div>
      <div class="stat-value">{max_score}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Flags Raised</div>
      <div class="stat-value">{len(findings)}</div>
    </div>
  </div>

  <div class="legend">{legend_html}</div>

  <table>
    <thead>
      <tr>
        <th>Chapter</th>
        <th style="text-align:right;">Words</th>
        <th style="text-align:right;">Insertions</th>
        <th style="text-align:right;">Deletions</th>
        <th style="text-align:right;">Churn</th>
        <th style="text-align:right;">Ratio</th>
        <th>Heatmap</th>
      </tr>
    </thead>
    <tbody>
      {rows_html}
    </tbody>
  </table>

  <div class="findings-box">
    <h2 style="font-size:1rem;margin:0 0 12px;">Revision Findings</h2>
    {findings_html}
  </div>

  <footer>Generated by Ars Arcanum revision-heatmap engine · offline, privacy-respecting</footer>
</body>
</html>"""

    atomic_write(output_path, page)
    logger.info("Revision heatmap written to %s", output_path)
