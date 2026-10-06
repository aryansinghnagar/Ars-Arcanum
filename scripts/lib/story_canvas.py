#!/usr/bin/env python3
"""
Ars Arcanum Interactive Visual Story Canvas & Corkboard Engine
(scripts/lib/story_canvas.py)
================================================================================
Zero-dependency, offline interactive HTML5 visual story corkboard and narrative
timeline arranger for novelists, screenwriters, and worldbuilders.

Capabilities:
1. Scene & Chapter Card Extraction:
   - Scans manuscript chapters and scenes (`*.md`).
   - Extracts title, word count, POV character (`@pov:`), location (`@location:`),
     plot threads (`@thread:`), tension rating, and summary excerpts.
2. Paradigm & Beat Alignment:
   - Maps scene positions against 9 canonical narrative paradigms from `structure.py`.
3. Standalone Interactive Visual Corkboard:
   - Drag-and-drop scene cards between Act columns and POV swimlanes.
   - Live client-side recalculation of word count balance and structural harmony.
   - Color-coded POV badges, tension heat indicators, and plot thread filters.
   - One-click manifest export for updated chapter ordering.

Zero external dependencies; 100% offline privacy.
"""

import argparse
import html
import json
import logging
import re
import sys
from pathlib import Path
from typing import Any

try:
    from lib._bootstrap import atomic_write
    from lib.frontmatter import parse_yaml_frontmatter
    from lib.scope import (
        EngineScope,
        add_scope_arguments,
        filter_manuscript_scope,
        parse_scope_args,
        resolve_manuscript_dir,
    )
    from lib.structure import PARADIGMS
    from lib.tips import are_tips_enabled, get_tip_database
except ImportError:
    from _bootstrap import atomic_write
    from frontmatter import parse_yaml_frontmatter
    from scope import (  # type: ignore[no-redef]
        EngineScope,
        add_scope_arguments,
        filter_manuscript_scope,
        parse_scope_args,
        resolve_manuscript_dir,
    )
    from structure import PARADIGMS
    try:
        from tips import are_tips_enabled, get_tip_database
    except ImportError:
        def are_tips_enabled() -> bool:
            return True

        def get_tip_database() -> Any:
            return None

logger = logging.getLogger("arcanum.canvas")

TAG_REGEX = re.compile(r"^@([a-zA-Z0-9_-]+):\s*(.*)$")
FRONTMATTER_REGEX = re.compile(r"^---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)", re.DOTALL)


def extract_single_card(content: str, file_path: Path | str, idx: int, title: str | None = None) -> dict[str, Any]:
    """Helper to extract a single scene/chapter card from markdown text."""
    p = Path(file_path)
    words = len(re.findall(r"\b\w+\b", content))
    meta = parse_yaml_frontmatter(content)
    body = FRONTMATTER_REGEX.sub("", content)
    pov = str(meta.get("pov", meta.get("character", "")))
    location = str(meta.get("location", meta.get("setting", "")))
    thread = str(meta.get("thread", meta.get("plot", "")))
    tension = float(meta.get("tension", 5.0))

    # Parse inline @tags if not in frontmatter
    lines = body.splitlines()
    prose_lines = []
    for line in lines:
        s_line = line.strip()
        m = TAG_REGEX.match(s_line)
        if m:
            k, v = m.group(1).lower(), m.group(2).strip()
            if k == "pov" and not pov:
                pov = v
            elif k in ("location", "setting") and not location:
                location = v
            elif k in ("thread", "plot") and not thread:
                thread = v
            elif k == "tension":
                try:
                    tension = float(v)
                except ValueError:
                    pass
        elif s_line and not s_line.startswith("#"):
            prose_lines.append(s_line)

    summary = " ".join(prose_lines)[:180].strip()
    if len(" ".join(prose_lines)) > 180:
        summary += "..."

    h1_match = re.search(r"^#\s+(.+)$", body, flags=re.MULTILINE)
    raw_title = str(meta.get("title", title if title else (h1_match.group(1).strip() if h1_match else p.stem.replace("_", " ").replace("-", " "))))
    # Strip leading numbers from title for cleanliness
    clean_title = re.sub(r"^\d+\s*[-_.]*\s*", "", raw_title).title()

    return {
        "id": f"card_{idx}",
        "index": idx,
        "filename": p.name,
        "path": str(p),
        "title": clean_title or p.stem,
        "pov": pov or "Omniscient",
        "location": location or "Unspecified",
        "thread": thread or "Main Plot",
        "tension": tension,
        "word_count": words,
        "summary": summary or "No prose summary available.",
    }


def extract_scene_cards(target_path: Path | str | None = None, scope: Any = None) -> list[dict[str, Any]]:
    """Extracts rich metadata for every scene/chapter in the manuscript with granular scope support."""
    target_str = resolve_manuscript_dir(target_path) if target_path else resolve_manuscript_dir()
    if target_path and Path(target_path).exists():
        p_target = Path(target_path)
    elif target_str and Path(target_str).exists():
        p_target = Path(target_str)
    else:
        p_target = Path(target_path) if target_path else Path.cwd()

    cards = []
    total_words_accum = 0

    if p_target.is_file():
        content = p_target.read_text(encoding="utf-8", errors="replace")
        card = extract_single_card(content, p_target, 1)
        card["cumulative_words"] = card["word_count"]
        cards.append(card)
    elif p_target.is_dir():
        if scope:
            if not isinstance(scope, EngineScope):
                if isinstance(scope, dict):
                    from lib.scope import resolve_scope
                    scope = resolve_scope(scope).scope_filter
                elif isinstance(scope, str):
                    from lib.scope import parse_unified_scope_string
                    p_dict = parse_unified_scope_string(scope)
                    scope = EngineScope(**p_dict)
            scoped_chaps, scoped_scenes, _ = filter_manuscript_scope(p_target, scope)
            if scope.scenes and scoped_scenes:
                items = [(s.global_scene_idx, s.title, s.content, s.chapter_file) for s in scoped_scenes]
            else:
                items = [(c.chapter_num, c.title, c.scoped_content, c.file_path) for c in scoped_chaps]
            for idx, title, content, fpath in items:
                card = extract_single_card(content, fpath, idx, title=title)
                total_words_accum += card["word_count"]
                card["cumulative_words"] = total_words_accum
                cards.append(card)
        else:
            files = []
            for p in sorted(p_target.rglob("*.md")):
                if not p.name.startswith((".", "_")) and "Backups" not in p.parts and "04_Back_Matter" not in p.parts:
                    files.append(p)
            for idx, f in enumerate(files, 1):
                content = f.read_text(encoding="utf-8", errors="replace")
                card = extract_single_card(content, f, idx)
                total_words_accum += card["word_count"]
                card["cumulative_words"] = total_words_accum
                cards.append(card)
    else:
        raise FileNotFoundError(f"Target path not found: {p_target}")

    return cards


def generate_story_canvas_html(
    target_path: Path,
    cards: list[dict[str, Any]],
    paradigm_key: str = "eight_sequence",
    output_path: Path | None = None,
) -> str:
    """Generates a standalone, fully offline interactive HTML5 story canvas."""
    total_words = sum(c["word_count"] for c in cards)

    # Compute assigned acts/beats
    for c in cards:
        pct = (c["cumulative_words"] / total_words) if total_words > 0 else 0.0
        c["pct"] = round(pct, 3)

    tips_data: list[dict[str, Any]] = []
    tips_enabled = True
    try:
        tips_enabled = are_tips_enabled()
        db = get_tip_database()
        if db:
            canvas_engines = ["story_canvas", "structure", "pacing", "scene_mechanics", "timeline_sync", "revision_heatmap"]
            for eng in canvas_engines:
                for t in db.get_by_engine(eng):
                    tips_data.append(t.to_dict())
            if not tips_data:
                tips_data = [t.to_dict() for t in db.get_by_context("drafting")]
    except Exception as e:
        logger.debug("Story canvas tips extraction skipped: %s", e)

    cards_json = json.dumps(cards).replace("</", "<\\/")
    paradigms_json = json.dumps(PARADIGMS).replace("</", "<\\/")
    tips_json = json.dumps(tips_data).replace("</", "<\\/")

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ars Arcanum — Interactive Visual Story Canvas</title>
<style>
  :root {{
    --bg: #090d16; --panel: #131b2e; --panel-hover: #1e293b;
    --border: #27354f; --text: #f8fafc; --muted: #94a3b8;
    --accent: #38bdf8; --accent-glow: rgba(56, 189, 248, 0.2);
    --gold: #f59e0b; --danger: #ef4444; --success: #10b981;
    --card-bg: #1c263d; --card-border: #3b4d71;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    font-family: system-ui, -apple-system, sans-serif;
    background: var(--bg); color: var(--text);
    margin: 0; padding: 0; height: 100vh; display: flex; flex-direction: column; overflow: hidden;
  }}
  header {{
    background: var(--panel); border-bottom: 1px solid var(--border);
    padding: 0.75rem 1.5rem; display: flex; justify-content: space-between; align-items: center;
  }}
  .brand {{ display: flex; align-items: center; gap: 0.75rem; font-weight: 700; font-size: 1.1rem; color: var(--accent); }}
  .toolbar {{ display: flex; gap: 1rem; align-items: center; }}
  select, button {{
    background: var(--card-bg); color: var(--text); border: 1px solid var(--border);
    padding: 0.4rem 0.8rem; border-radius: 6px; font-size: 0.875rem; cursor: pointer;
  }}
  button:hover {{ border-color: var(--accent); background: var(--panel-hover); }}
  .btn-primary {{ background: #0284c7; color: white; border: none; font-weight: 600; }}
  .btn-primary:hover {{ background: #0369a1; }}

  .stats-bar {{
    background: #0f172a; border-bottom: 1px solid var(--border);
    padding: 0.5rem 1.5rem; display: flex; gap: 2rem; font-size: 0.85rem; color: var(--muted);
  }}
  .stat-val {{ font-weight: 700; color: var(--text); margin-left: 0.25rem; }}

  .canvas-container {{
    flex: 1; overflow-x: auto; overflow-y: hidden; padding: 1.5rem;
    display: flex; gap: 1.5rem;
  }}
  .column {{
    background: var(--panel); border: 1px solid var(--border);
    border-radius: 8px; width: 320px; min-width: 320px; display: flex; flex-direction: column;
    max-height: 100%;
  }}
  .column-header {{
    padding: 0.75rem 1rem; border-bottom: 1px solid var(--border);
    font-weight: 600; font-size: 0.95rem; display: flex; justify-content: space-between; align-items: center;
    background: rgba(255,255,255,0.02);
  }}
  .column-meta {{ font-size: 0.75rem; color: var(--muted); font-weight: 400; }}
  .cards-list {{
    flex: 1; overflow-y: auto; padding: 0.75rem; display: flex; flex-direction: column; gap: 0.75rem;
  }}

  .card {{
    background: var(--card-bg); border: 1px solid var(--card-border);
    border-radius: 6px; padding: 0.875rem; cursor: grab; user-select: none;
    transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
  }}
  .card:hover {{
    transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    border-color: var(--accent);
  }}
  .card.dragging {{ opacity: 0.4; cursor: grabbing; }}
  .card-top {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem; }}
  .card-title {{ font-weight: 600; font-size: 0.95rem; color: var(--text); }}
  .card-idx {{ font-size: 0.75rem; color: var(--muted); font-family: monospace; }}
  .card-badges {{ display: flex; flex-wrap: wrap; gap: 0.35rem; margin-bottom: 0.5rem; }}
  .badge {{
    font-size: 0.7rem; padding: 2px 6px; border-radius: 4px; font-weight: 500;
  }}
  .badge-pov {{ background: #312e81; color: #c7d2fe; }}
  .badge-loc {{ background: #1e293b; color: #94a3b8; }}
  .badge-thread {{ background: #064e3b; color: #a7f3d0; }}
  .badge-words {{ background: #78350f; color: #fde68a; font-family: monospace; }}
  .card-summary {{ font-size: 0.8rem; color: var(--muted); line-height: 1.4; }}

  .drop-indicator {{
    height: 3px; background: var(--accent); border-radius: 2px; margin: 4px 0;
  }}

  .modal-backdrop {{
    display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(0,0,0,0.85); z-index: 1000; justify-content: center; align-items: center;
  }}
  .modal-window {{
    background: #0f172a; border: 1px solid var(--border); border-radius: 12px;
    width: 90%; max-width: 920px; height: 85vh; display: flex; flex-direction: column; overflow: hidden;
  }}
  .modal-header {{
    background: #1e293b; padding: 1rem 1.5rem; border-bottom: 1px solid var(--border);
    display: flex; justify-content: space-between; align-items: center;
  }}
  .modal-body {{
    flex: 1; overflow-y: auto; padding: 1.5rem; display: flex; flex-direction: column; gap: 1.25rem;
  }}

  .tip-bar {{
    background: #0b1120; border-top: 1px solid var(--border);
    padding: 0.45rem 1.25rem; display: flex; justify-content: space-between; align-items: center;
    font-size: 0.8rem; color: var(--muted); z-index: 100;
  }}
  .tip-content-box {{ display: flex; align-items: center; gap: 0.75rem; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }}
  .tip-icon {{ font-size: 1rem; flex-shrink: 0; }}
  .tip-badge {{ background: #1e293b; color: var(--accent); font-weight: 700; font-size: 0.7rem; padding: 2px 6px; border-radius: 4px; text-transform: uppercase; letter-spacing: 0.5px; flex-shrink: 0; }}
  .tip-text {{ color: #e2e8f0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
  .tip-text b {{ color: var(--gold); }}
  .tip-actions {{ display: flex; align-items: center; gap: 0.5rem; flex-shrink: 0; margin-left: 1rem; }}
  .tip-btn {{ background: transparent; border: 1px solid var(--border); color: var(--muted); font-size: 0.75rem; padding: 2px 8px; border-radius: 4px; cursor: pointer; transition: all 0.15s; }}
  .tip-btn:hover {{ color: var(--text); border-color: var(--accent); background: var(--panel-hover); }}
</style>
</head>
<body>

<header>
  <div class="brand">
    <span>📐</span>
    <span>Ars Arcanum Story Canvas</span>
  </div>
  <div class="toolbar">
    <label style="font-size: 0.85rem; color: var(--muted);">Story Paradigm:
      <select id="paradigmSelect" onchange="updateParadigm(this.value)">
        {"".join(f'<option value="{k}" {"selected" if k == paradigm_key else ""}>{html.escape(str(v["name"]))}</option>' for k, v in PARADIGMS.items())}
      </select>
    </label>
    <label style="font-size: 0.85rem; color: var(--muted);">Filter POV:
      <select id="povFilter" onchange="filterCards()">
        <option value="all">All POVs</option>
      </select>
    </label>
    <button style="background:#b45309;color:#fef3c7;border:none;font-weight:600;" onclick="openParadigmGuide()">📐 Paradigm Guide & Math</button>
    <button class="btn-primary" onclick="exportManifest()">Export Manifest</button>
  </div>
</header>

<div class="stats-bar">
  <div>Target: <span id="statTarget" class="stat-val">{html.escape(target_path.name)}</span></div>
  <div>Chapters: <span id="statChapters" class="stat-val">{len(cards)}</span></div>
  <div>Total Words: <span id="statWords" class="stat-val">{total_words:,}</span></div>
  <div>Structural Harmony: <span id="statHarmony" class="stat-val" style="color: var(--success);">--</span></div>
</div>

<div class="canvas-container" id="columnsContainer">
  <!-- Dynamic Columns and Cards -->
</div>

<div class="tip-bar" id="tipBar" style="display: {'flex' if (tips_enabled and tips_data) else 'none'};">
  <div class="tip-content-box">
    <span class="tip-icon">💡</span>
    <span class="tip-badge" id="tipBadge">CRAFT WISDOM</span>
    <span class="tip-text" id="tipText">Loading craft insight...</span>
  </div>
  <div class="tip-actions">
    <button class="tip-btn" title="Cycle to next non-obvious craft tip" onclick="cycleCanvasTip()">🔄 Next Tip</button>
    <button class="tip-btn" title="Hide tips" onclick="dismissCanvasTip()">✕</button>
  </div>
</div>

<div class="modal-backdrop" id="paradigmGuideModal" onclick="if(event.target===this)closeParadigmGuide()">
  <div class="modal-window">
    <div class="modal-header">
      <div>
        <span style="font-weight:700;font-size:1.1rem;color:var(--accent);">📐 Narrative Paradigm Guide & Mathematical Harmony</span>
        <div style="font-size:0.8rem;color:var(--muted);margin-top:2px;">9 Canonical Structural Architectures • Mathematical Beat Tolerances • Dynamic Tension Curves</div>
      </div>
      <button onclick="closeParadigmGuide()" style="font-size:1.2rem;line-height:1;background:transparent;border:none;color:var(--muted);cursor:pointer;">✕</button>
    </div>
    <div class="modal-body" id="paradigmModalBody">
      <!-- Dynamic Paradigm Math and Beat Targets -->
    </div>
  </div>
</div>

<script>
  let cardsData = {cards_json};
  let paradigmsData = {paradigms_json};
  let tipsData = {tips_json};
  let currentTipIdx = 0;
  let currentParadigmKey = "{paradigm_key}";
  let draggedCardId = null;

  function init() {{
    populatePOVFilter();
    renderColumns();
    initTips();
  }}

  function initTips() {{
    if (!tipsData || tipsData.length === 0) return;
    showCanvasTip(0);
  }}

  function showCanvasTip(idx) {{
    if (!tipsData || tipsData.length === 0) return;
    currentTipIdx = (idx + tipsData.length) % tipsData.length;
    const tip = tipsData[currentTipIdx];
    const badgeEl = document.getElementById("tipBadge");
    const textEl = document.getElementById("tipText");
    if (badgeEl && textEl) {{
      badgeEl.textContent = `${{tip.engine.toUpperCase()}} • ${{tip.subfeature}}`;
      textEl.innerHTML = `<b>${{escapeHtml(tip.title)}}:</b> ${{escapeHtml(tip.content)}}`;
    }}
  }}

  function cycleCanvasTip() {{
    showCanvasTip(currentTipIdx + 1);
  }}

  function dismissCanvasTip() {{
    const bar = document.getElementById("tipBar");
    if (bar) bar.style.display = "none";
  }}

  function populatePOVFilter() {{
    const select = document.getElementById("povFilter");
    const povs = Array.from(new Set(cardsData.map(c => c.pov))).filter(Boolean);
    povs.forEach(p => {{
      const opt = document.createElement("option");
      opt.value = p;
      opt.textContent = p;
      select.appendChild(opt);
    }});
  }}

  function renderColumns() {{
    const container = document.getElementById("columnsContainer");
    container.innerHTML = "";
    const paradigm = paradigmsData[currentParadigmKey] || paradigmsData["three_act"];
    const totalWords = cardsData.reduce((acc, c) => acc + c.word_count, 0);

    // Group cards into beats
    const beats = paradigm.beats;
    beats.forEach((beat, bIdx) => {{
      const col = document.createElement("div");
      col.className = "column";
      col.dataset.beatIndex = bIdx;

      const targetWords = Math.round(beat.target_pct * totalWords);
      col.innerHTML = `
        <div class="column-header">
          <div>
            ${{escapeHtml(beat.name)}}
            <div class="column-meta">${{Math.round(beat.target_pct * 100)}}% target (~${{targetWords.toLocaleString()}} w)</div>
          </div>
          <span class="column-meta" id="count_beat_${{bIdx}}">0 scenes</span>
        </div>
        <div class="cards-list" id="list_beat_${{bIdx}}" ondragover="handleDragOver(event)" ondrop="handleDrop(event, ${{bIdx}})">
        </div>
      `;
      container.appendChild(col);
    }});

    // Distribute cards to closest beat
    cardsData.forEach((card, cIdx) => {{
      const cumPct = totalWords > 0 ? (card.cumulative_words / totalWords) : 0;
      let assignedBeatIdx = 0;
      for (let i = 0; i < beats.length; i++) {{
        if (cumPct <= beats[i].window[1] || i === beats.length - 1) {{
          assignedBeatIdx = i;
          break;
        }}
      }}

      const list = document.getElementById(`list_beat_${{assignedBeatIdx}}`);
      if (list) {{
        list.appendChild(createCardElement(card));
      }}
    }});

    updateColumnCounts();
    calculateHarmonyScore();
  }}

  function createCardElement(card) {{
    const div = document.createElement("div");
    div.className = "card";
    div.id = card.id;
    div.draggable = true;
    div.dataset.pov = card.pov;
    div.ondragstart = (e) => handleDragStart(e, card.id);
    div.ondragend = handleDragEnd;

    div.innerHTML = `
      <div class="card-top">
        <span class="card-title">${{escapeHtml(card.title)}}</span>
        <span class="card-idx">#${{card.index}}</span>
      </div>
      <div class="card-badges">
        <span class="badge badge-pov">👤 ${{escapeHtml(card.pov)}}</span>
        <span class="badge badge-loc">📍 ${{escapeHtml(card.location)}}</span>
        <span class="badge badge-thread">🧵 ${{escapeHtml(card.thread)}}</span>
        <span class="badge badge-words">${{card.word_count.toLocaleString()}} w</span>
      </div>
      <div class="card-summary">${{escapeHtml(card.summary)}}</div>
    `;
    return div;
  }}

  function handleDragStart(e, cardId) {{
    draggedCardId = cardId;
    e.target.classList.add("dragging");
    e.dataTransfer.setData("text/plain", cardId);
  }}

  function handleDragEnd(e) {{
    e.target.classList.remove("dragging");
    draggedCardId = null;
  }}

  function handleDragOver(e) {{
    e.preventDefault();
  }}

  function handleDrop(e, beatIdx) {{
    e.preventDefault();
    if (!draggedCardId) return;
    const cardEl = document.getElementById(draggedCardId);
    const targetList = document.getElementById(`list_beat_${{beatIdx}}`);
    if (targetList && cardEl) {{
      targetList.appendChild(cardEl);
      updateOrderFromDOM();
    }}
  }}

  function updateOrderFromDOM() {{
    const newCards = [];
    let curWords = 0;
    document.querySelectorAll(".card").forEach((el, newIdx) => {{
      const card = cardsData.find(c => c.id === el.id);
      if (card) {{
        card.index = newIdx + 1;
        curWords += card.word_count;
        card.cumulative_words = curWords;
        newCards.push(card);
      }}
    }});
    cardsData = newCards;
    updateColumnCounts();
    calculateHarmonyScore();
  }}

  function updateColumnCounts() {{
    const paradigm = paradigmsData[currentParadigmKey] || paradigmsData["three_act"];
    paradigm.beats.forEach((b, idx) => {{
      const list = document.getElementById(`list_beat_${{idx}}`);
      const countEl = document.getElementById(`count_beat_${{idx}}`);
      if (list && countEl) {{
        const count = list.querySelectorAll(".card").length;
        countEl.textContent = `${{count}} scene${{count === 1 ? '' : 's'}}`;
      }}
    }});
  }}

  function calculateHarmonyScore() {{
    const totalWords = cardsData.reduce((acc, c) => acc + c.word_count, 0);
    const harmonyEl = document.getElementById("statHarmony");
    if (totalWords === 0 || cardsData.length === 0) {{
      harmonyEl.textContent = "100%";
      return;
    }}
    const paradigm = paradigmsData[currentParadigmKey] || paradigmsData["three_act"];
    let totalDeviation = 0;
    paradigm.beats.forEach((b, idx) => {{
      const list = document.getElementById(`list_beat_${{idx}}`);
      let beatWords = 0;
      if (list) {{
        list.querySelectorAll(".card").forEach(el => {{
          const card = cardsData.find(c => c.id === el.id);
          if (card) beatWords += card.word_count;
        }});
      }}
      const actualPct = beatWords / totalWords;
      const targetPct = b.target_pct;
      totalDeviation += Math.abs(actualPct - targetPct);
    }});
    const harmony = Math.max(0, Math.min(100, Math.round((1.0 - (totalDeviation / 2.0)) * 100)));
    harmonyEl.textContent = `${{harmony}}%`;
  }}

  function updateParadigm(key) {{
    currentParadigmKey = key;
    renderColumns();
  }}

  function filterCards() {{
    const pov = document.getElementById("povFilter").value;
    document.querySelectorAll(".card").forEach(el => {{
      if (pov === "all" || el.dataset.pov === pov) {{
        el.style.display = "block";
      }} else {{
        el.style.display = "none";
      }}
    }});
  }}

  function openParadigmGuide() {{
    renderParadigmGuide();
    document.getElementById("paradigmGuideModal").style.display = "flex";
  }}

  function closeParadigmGuide() {{
    document.getElementById("paradigmGuideModal").style.display = "none";
  }}

  function renderParadigmGuide() {{
    const container = document.getElementById("paradigmModalBody");
    container.innerHTML = "";

    const cur = paradigmsData[currentParadigmKey] || paradigmsData["three_act"];

    // Math Explanation Card
    const mathCard = document.createElement("div");
    mathCard.style.background = "#1e293b";
    mathCard.style.border = "1px solid var(--border)";
    mathCard.style.borderRadius = "8px";
    mathCard.style.padding = "1rem 1.25rem";
    mathCard.innerHTML = `
      <h3 style="margin:0 0 0.5rem 0;color:var(--accent);font-size:1rem;">📐 Structural Harmony Equation</h3>
      <p style="margin:0 0 0.5rem 0;font-size:0.85rem;color:var(--text);line-height:1.5;">
        Ars Arcanum evaluates narrative architecture by calculating the L1 norm total variation distance between actual cumulative word distributions and canonical paradigm milestone targets:
      </p>
      <div style="background:#0b1120;padding:0.6rem 1rem;border-radius:6px;font-family:monospace;font-size:0.85rem;color:var(--gold);margin-bottom:0.5rem;">
        Harmony % = max(0, min(100, round(100 * (1 - 0.5 * sum(|ActualPct_b - TargetPct_b|)))))
      </div>
      <p style="margin:0;font-size:0.8rem;color:var(--muted);">
        A score of 80%+ indicates balanced narrative pacing and optimal dramatic tension delivery.
      </p>
    `;
    container.appendChild(mathCard);

    // Active Paradigm Beats
    const beatCard = document.createElement("div");
    beatCard.style.background = "#1e293b";
    beatCard.style.border = "1px solid var(--border)";
    beatCard.style.borderRadius = "8px";
    beatCard.style.padding = "1rem 1.25rem";
    beatCard.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.75rem;">
        <h3 style="margin:0;color:var(--gold);font-size:1.05rem;">Active Architecture: ${{escapeHtml(cur.name)}}</h3>
        <span style="font-size:0.8rem;color:var(--muted);">${{cur.beats.length}} Structural Beats</span>
      </div>
      <div style="display:flex;flex-direction:column;gap:0.5rem;">
        ${{cur.beats.map(b => `
          <div style="background:#0b1120;padding:0.6rem 0.8rem;border-radius:6px;border-left:3px solid var(--accent);display:flex;justify-content:space-between;align-items:center;">
            <div>
              <strong style="color:var(--text);font-size:0.85rem;">${{escapeHtml(b.name)}}</strong>
              <div style="font-size:0.75rem;color:var(--muted);">${{escapeHtml(b.description || "Milestone")}}</div>
            </div>
            <div style="text-align:right;">
              <span style="color:var(--accent);font-family:monospace;font-weight:600;font-size:0.85rem;">${{Math.round(b.target_pct * 100)}}%</span>
              <div style="font-size:0.7rem;color:var(--muted);font-family:monospace;">[${{Math.round(b.window[0] * 100)}}% - ${{Math.round(b.window[1] * 100)}}%]</div>
            </div>
          </div>
        `).join('')}}
      </div>
    `;
    container.appendChild(beatCard);
  }}

  function exportManifest() {{
    const data = JSON.stringify(cardsData, null, 2);
    const blob = new Blob([data], {{type: "application/json"}});
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "story_canvas_manifest.json";
    a.click();
    URL.revokeObjectURL(url);
  }}

  function escapeHtml(str) {{
    return String(str || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }}

  window.addEventListener("DOMContentLoaded", init);
</script>
</body>
</html>
"""
    if output_path:
        atomic_write(output_path, html_content)
    return html_content


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ars Arcanum Interactive Visual Story Canvas")
    parser.add_argument("target", nargs="?", default=None, help="Manuscript directory or file")
    parser.add_argument(
        "--paradigm", "-p",
        choices=list(PARADIGMS.keys()),
        default="eight_sequence",
        help="Story paradigm structure for canvas lanes",
    )
    parser.add_argument("--html", help="Output HTML canvas report path")
    parser.add_argument("--json", action="store_true", help="Output extracted scene cards as JSON")
    add_scope_arguments(parser, include_world=False)
    args = parser.parse_args(argv)

    scope = parse_scope_args(args)
    target_raw = args.target or scope.manuscript or (scope.books[0] if scope.books else None)
    if not target_raw:
        resolved_dir = resolve_manuscript_dir()
        if resolved_dir and Path(resolved_dir).exists():
            target_path = Path(resolved_dir)
        else:
            parser.print_help()
            return 1
    else:
        tp = Path(target_raw)
        if tp.exists():
            target_path = tp
        else:
            resolved_dir = resolve_manuscript_dir(target_raw)
            if resolved_dir and Path(resolved_dir).exists():
                target_path = Path(resolved_dir)
            else:
                print(f"Error: Target path does not exist: {target_raw}", file=sys.stderr)
                sys.exit(1)

    cards = extract_scene_cards(target_path, scope=scope)

    if args.json:
        print(json.dumps(cards, indent=2))
        return 0

    out_p = Path(args.html) if args.html else (target_path if target_path.is_dir() else target_path.parent) / "story_canvas.html"
    generate_story_canvas_html(target_path, cards, paradigm_key=args.paradigm, output_path=out_p)

    print("=== Ars Arcanum Story Canvas ===")
    print(f"Target: {target_path.name} | Scenes/Chapters: {len(cards)} | Total Words: {sum(c['word_count'] for c in cards):,}")
    print(f"Paradigm: {PARADIGMS.get(args.paradigm, {}).get('name', args.paradigm)}")
    print(f"Interactive Story Canvas written to: {out_p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())


