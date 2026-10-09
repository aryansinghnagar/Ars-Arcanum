#!/usr/bin/env python3
"""
Ars Arcanum Omnibus HTML Reader Template (scripts/lib/omnibus_template.py)
==========================================================================
Self-contained, offline HTML5 visualizer and reader for multi-volume series omnibuses.
Strict Content Security Policy enforced (zero external CDNs or network calls).
"""

from __future__ import annotations

import html
from pathlib import Path
from typing import Any

try:
    from lib._bootstrap import atomic_write
except ImportError:
    from _bootstrap import atomic_write


def _format_markdown_prose(text: str) -> str:
    """Basic HTML paragraph formatter for manuscript prose."""
    escaped = html.escape(text.strip())
    paragraphs = escaped.split("\n\n")
    p_tags = []
    for p in paragraphs:
        p_clean = p.strip()
        if not p_clean:
            continue
        if p_clean.startswith(("&lt;h", "<h")):
            p_tags.append(p_clean)
        elif p_clean in ("* * *", "***", "---"):
            p_tags.append("<hr class='scene-break'>")
        else:
            p_tags.append(f"<p>{p_clean.replace(chr(10), '<br>')}</p>")
    return "\n".join(p_tags)


def render_omnibus_html(omnibus_report: dict[str, Any], output_path: Path | str) -> Path:
    """Generates an offline HTML5 Omnibus Reader."""
    out_path = Path(output_path)
    title = omnibus_report["title"]
    author = omnibus_report["author"]
    volumes = omnibus_report["volumes"]
    dp = omnibus_report.get("dramatis_personae", {})

    toc_items = []
    volume_sections = []

    for v in volumes:
        toc_items.append(
            f"<li><strong>Volume {v['index']}: {html.escape(v['title'])}</strong> ({v['word_count']:,} words)</li>"
        )
        ch_blocks = []
        for ch_idx, ch in enumerate(v["chapters"], 1):
            ch_blocks.append(f"""
            <article class="chapter">
              <h3>Chapter {ch_idx}: {html.escape(ch['title'])}</h3>
              <div class="meta-tag">POV: {html.escape(ch['pov'])} | {ch['words']:,} words</div>
              <div class="prose">{_format_markdown_prose(ch.get('body', ''))}</div>
            </article>
            """)

        volume_sections.append(f"""
        <section class="volume-block">
          <h2>Volume {v['index']}: {html.escape(v['title'])}</h2>
          {''.join(ch_blocks)}
        </section>
        """)

    dp_items = "".join(
        f"<li><strong>{html.escape(char)}</strong> &mdash; <em>{html.escape(', '.join(vols))}</em></li>"
        for char, vols in sorted(dp.items())
    )

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)} — Ars Arcanum Omnibus Reader</title>
<style>
  :root {{
    --bg: #0f172a; --panel: #1e293b; --border: #334155;
    --text: #f8fafc; --muted: #94a3b8; --accent: #38bdf8;
    --gold: #f59e0b;
  }}
  body {{
    font-family: Georgia, Cambria, serif; background: var(--bg); color: var(--text);
    margin: 0; padding: 2rem 1rem; line-height: 1.7;
  }}
  .container {{ max-width: 800px; margin: 0 auto; background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 3rem 2.5rem; }}
  h1, h2, h3 {{ font-family: system-ui, -apple-system, sans-serif; color: var(--accent); }}
  .title-header {{ text-align: center; border-bottom: 2px solid var(--border); padding-bottom: 2rem; margin-bottom: 3rem; }}
  .author {{ font-size: 1.25rem; color: var(--muted); margin-top: 0.5rem; }}
  .meta-tag {{ font-family: system-ui, sans-serif; font-size: 0.8rem; color: var(--muted); margin-bottom: 1rem; }}
  .prose {{ margin-top: 1rem; font-size: 1.05rem; }}
  .volume-block {{ margin-top: 4rem; border-top: 1px solid var(--border); padding-top: 2rem; }}
  .chapter {{ margin-bottom: 3rem; }}
  .scene-break {{ border: 0; text-align: center; margin: 2rem 0; }}
  .scene-break::before {{ content: "* * *"; color: var(--muted); letter-spacing: 0.5em; }}
  .toc-box {{ background: rgba(0,0,0,0.2); border: 1px solid var(--border); border-radius: 6px; padding: 1.5rem; margin-bottom: 3rem; font-family: system-ui, sans-serif; }}
</style>
</head>
<body>
<div class="container">
  <div class="title-header">
    <h1>{html.escape(title)}</h1>
    <div class="author">By {html.escape(author)}</div>
    <div class="meta-tag" style="margin-top:1rem;">Omnibus Edition &bull; {omnibus_report.get('total_volumes', len(volumes))} Volumes &bull; {omnibus_report.get('total_words', 0):,} Total Words</div>
  </div>

  <div class="toc-box">
    <h3 style="margin-top:0;">Table of Contents</h3>
    <ul>
      {''.join(toc_items)}
    </ul>
    <h3>Dramatis Personae</h3>
    <ul>
      {dp_items or '<li>No POV characters registered.</li>'}
    </ul>
  </div>

  {''.join(volume_sections)}
</div>
</body>
</html>
"""
    atomic_write(out_path, html_content)
    return out_path


__all__ = ["render_omnibus_html"]
