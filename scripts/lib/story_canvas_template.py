#!/usr/bin/env python3
"""
Ars Arcanum Visual Story Canvas HTML Template
(scripts/lib/story_canvas_template.py)
================================================================================
Presentation layer for the interactive visual story corkboard and narrative arranger.
Renders standalone, zero-dependency HTML5 with strict Content Security Policy,
WCAG 2.1 AA accessibility tokens, drag-and-drop card physics, and paradigm math guides.

Zero external dependencies; 100% offline air-gapped privacy.
"""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

try:
    from lib.structure import PARADIGMS
except ImportError:
    from structure import PARADIGMS  # type: ignore[no-redef]


def render_story_canvas_page(
    target_path: Path,
    cards: list[dict[str, Any]],
    paradigm_key: str = "eight_sequence",
    tips_data: list[dict[str, Any]] | None = None,
    tips_enabled: bool = True,
) -> str:
    """Renders the self-contained interactive Story Canvas HTML5 page."""
    total_words = sum(c.get("word_count", 0) for c in cards)
    tips_list = tips_data or []

    cards_json = json.dumps(cards).replace("</", "<\\/")
    paradigms_json = json.dumps(PARADIGMS).replace("</", "<\\/")
    tips_json = json.dumps(tips_list).replace("</", "<\\/")

    paradigm_options = "".join(
        f'<option value="{k}" {"selected" if k == paradigm_key else ""}>{html.escape(str(v["name"]))}</option>'
        for k, v in PARADIGMS.items()
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
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
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
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

<header role="banner">
  <div class="brand">
    <span aria-hidden="true">📐</span>
    <span>Ars Arcanum Story Canvas</span>
  </div>
  <div class="toolbar" role="toolbar" aria-label="Story Canvas Controls">
    <label style="font-size: 0.85rem; color: var(--muted);">Story Paradigm:
      <select id="paradigmSelect" aria-label="Select Story Paradigm" onchange="updateParadigm(this.value)">
        {paradigm_options}
      </select>
    </label>
    <label style="font-size: 0.85rem; color: var(--muted);">Filter POV:
      <select id="povFilter" aria-label="Filter by POV" onchange="filterCards()">
        <option value="all">All POVs</option>
      </select>
    </label>
    <button style="background:#b45309;color:#fef3c7;border:none;font-weight:600;" aria-label="Open Paradigm Guide & Math" onclick="openParadigmGuide()">📐 Paradigm Guide & Math</button>
    <button class="btn-primary" aria-label="Export Manifest" onclick="exportManifest()">Export Manifest</button>
  </div>
</header>

<div class="stats-bar" role="region" aria-label="Manuscript Metrics">
  <div>Target: <span id="statTarget" class="stat-val">{html.escape(target_path.name)}</span></div>
  <div>Chapters: <span id="statChapters" class="stat-val">{len(cards)}</span></div>
  <div>Total Words: <span id="statWords" class="stat-val">{total_words:,}</span></div>
  <div>Milestone Proximity: <span id="statHarmony" class="stat-val" style="color: var(--accent);">--</span></div>
</div>

<main class="canvas-container" id="columnsContainer" role="main" aria-label="Story Beat Columns">
  <!-- Dynamic Columns and Cards -->
</main>

<div class="tip-bar" id="tipBar" role="region" aria-label="Craft Tip" aria-live="polite" style="display: {'flex' if (tips_enabled and tips_list) else 'none'};">
  <div class="tip-content-box">
    <span class="tip-icon" aria-hidden="true">💡</span>
    <span class="tip-badge" id="tipBadge">CRAFT WISDOM</span>
    <span class="tip-text" id="tipText">Loading craft insight...</span>
  </div>
  <div class="tip-actions">
    <button class="tip-btn" title="Cycle to next non-obvious craft tip" aria-label="Cycle to next craft tip" onclick="cycleCanvasTip()">🔄 Next Tip</button>
    <button class="tip-btn" title="Hide tips" aria-label="Hide craft tips" onclick="dismissCanvasTip()">✕</button>
  </div>
</div>

<div class="modal-backdrop" id="paradigmGuideModal" role="dialog" aria-modal="true" aria-labelledby="paradigmGuideTitle" onclick="if(event.target===this)closeParadigmGuide()">
  <div class="modal-window">
    <div class="modal-header">
      <div>
        <span id="paradigmGuideTitle" style="font-weight:700;font-size:1.1rem;color:var(--accent);">📐 Narrative Paradigm Guide & Mathematical Harmony</span>
        <div style="font-size:0.8rem;color:var(--muted);margin-top:2px;">9 Canonical Structural Architectures • Mathematical Beat Tolerances • Dynamic Tension Curves</div>
      </div>
      <button onclick="closeParadigmGuide()" aria-label="Close Paradigm Guide" style="font-size:1.2rem;line-height:1;background:transparent;border:none;color:var(--muted);cursor:pointer;">✕</button>
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

  window.addEventListener("keydown", function(e) {{
    if (e.key === "Escape") {{
      closeParadigmGuide();
    }}
  }});

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
    const totalWords = cardsData.reduce((acc, c) => acc + (c.word_count || 0), 0);

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
        <span class="badge badge-words">${{(card.word_count || 0).toLocaleString()}} w</span>
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
        curWords += card.word_count || 0;
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
    const totalWords = cardsData.reduce((acc, c) => acc + (c.word_count || 0), 0);
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
          if (card) beatWords += card.word_count || 0;
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

    const mathCard = document.createElement("div");
    mathCard.style.background = "#1e293b";
    mathCard.style.border = "1px solid var(--border)";
    mathCard.style.borderRadius = "8px";
    mathCard.style.padding = "1rem 1.25rem";
    mathCard.innerHTML = `
      <h3 style="margin:0 0 0.5rem 0;color:var(--accent);font-size:1rem;">📐 Milestone Proximity Reference & Structural Harmony Equation</h3>
      <p style="margin:0 0 0.5rem 0;font-size:0.85rem;color:var(--text);line-height:1.5;">
        Ars Arcanum maps narrative architecture by measuring the total variation distance between actual chapter word distributions and paradigm milestone targets for reference:
      </p>
      <div style="background:#0b1120;padding:0.6rem 1rem;border-radius:6px;font-family:monospace;font-size:0.85rem;color:var(--gold);margin-bottom:0.5rem;">
        Proximity % = max(0, min(100, round(100 * (1 - 0.5 * sum(|ActualPct_b - TargetPct_b|)))))
      </div>
      <p style="margin:0;font-size:0.8rem;color:var(--muted);">
        Milestone telemetry is purely observational to assist pacing navigation and reflects proximity to classical paradigm models without prescribing story rhythm.
      </p>
    `;
    container.appendChild(mathCard);

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


__all__ = ["render_story_canvas_page"]
