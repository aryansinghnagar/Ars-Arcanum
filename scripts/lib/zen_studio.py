#!/usr/bin/env python3
"""
Ars Arcanum Standalone Offline Zen Drafting Studio & In-Situ Lore Inspector
(scripts/lib/zen_studio.py)
================================================================================
Zero-dependency, offline single-file interactive HTML5 writing environment
combining distraction-free typewriter drafting with an in-situ World Bible
lore inspector, live structural beat progress, and offline browser persistence.

Capabilities:
1. Distraction-Free Typewriter Drafting:
   - Centered typography, dark/sepia/light themes, typewriter scrolling.
   - Live prose telemetry: word count, reading time (200 wpm), speech duration (150 wpm).
2. In-Situ World Bible Lore Drawer:
   - Side-drawer split view allowing authors to search and view character dossiers,
     faction allegiances, location maps, and magic constraints while drafting.
3. Multi-Paradigm Story Beat Tracker:
   - Interactive beat milestones for 3-Act Structure, 8-Sequence Method, and Kishōtenketsu.
4. Sovereign Local Persistence:
   - LocalStorage auto-save and one-click single-file markdown export.

Zero external dependencies; 100% offline privacy.
"""

import argparse
import json
import logging
import re
import sys
from pathlib import Path
from typing import Any

try:
    from lib._bootstrap import atomic_write
    from lib.frontmatter import parse_yaml_frontmatter
    from lib.registry import get_engine_catalog
    from lib.resonance import ResonanceMesh
    from lib.scope import (
        EngineScope,
        add_scope_arguments,
        filter_manuscript_scope,
        filter_world_scope,
        format_scope_banner,
        parse_scope_args,
        resolve_manuscript_dir,
        resolve_world_dir,
    )
    from lib.tips import are_tips_enabled, get_tip_database
except ImportError:
    from _bootstrap import atomic_write
    from frontmatter import parse_yaml_frontmatter
    from registry import get_engine_catalog
    from resonance import ResonanceMesh
    from scope import (  # type: ignore[no-redef]
        EngineScope,
        add_scope_arguments,
        filter_manuscript_scope,
        filter_world_scope,
        format_scope_banner,
        parse_scope_args,
        resolve_manuscript_dir,
        resolve_world_dir,
    )
    from tips import are_tips_enabled, get_tip_database

logger = logging.getLogger("arcanum.studio")

FRONTMATTER_REGEX = re.compile(r"^---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)", re.DOTALL)


def scan_lore_entities(world_dir: Path | None) -> list[dict[str, Any]]:
    """Extracts lore entity infoboxes for in-situ drawer viewing."""
    if not world_dir or not world_dir.exists():
        return []

    entities: list[dict[str, Any]] = []
    for p in sorted(world_dir.rglob("*.md")):
        if p.name.startswith((".", "_")) or "Backups" in p.parts:
            continue
        content = p.read_text(encoding="utf-8", errors="replace")
        meta = parse_yaml_frontmatter(content)
        body = FRONTMATTER_REGEX.sub("", content).strip()

        # Category from folder
        category = "General"
        for part in p.parts:
            if part in ("Characters", "Locations", "Factions", "MagicSystems", "Magic-Technology", "History", "Bestiary", "Cosmology", "Languages"):
                category = part
                break

        h1 = re.search(r"^#\s+(.+)$", body, flags=re.MULTILINE)
        name = str(meta.get("name", meta.get("title", h1.group(1).strip() if h1 else p.stem.replace("-", " ").title())))

        entities.append({
            "name": name,
            "category": category,
            "path": str(p.relative_to(world_dir)).replace("\\", "/"),
            "metadata": meta,
            "snippet": body[:300] + ("..." if len(body) > 300 else ""),
        })

    return entities


def build_zen_studio_bundle(
    ms_path: Path,
    world_path: Path | None = None,
    output_path: Path | None = None,
    scope: EngineScope | None = None,
) -> Path:
    """Compiles manuscript files and world lore into an offline interactive Zen studio HTML file."""
    chapters: list[dict[str, Any]] = []
    if scope and (scope.chapters or scope.scenes or scope.manuscript or scope.book):
        scoped_chaps, _, _ = filter_manuscript_scope(ms_path, scope)
        for idx, ch in enumerate(scoped_chaps, 1):
            body = ch.content
            fm = parse_yaml_frontmatter(body)
            body_clean = FRONTMATTER_REGEX.sub("", body).strip()
            word_count = len(re.findall(r"\b\w+\b", body_clean))
            chapters.append({
                "id": f"chap_{idx}",
                "filename": ch.file_path.name,
                "title": ch.title,
                "frontmatter": fm,
                "content": body,
                "body": body_clean,
                "word_count": word_count,
            })
    else:
        files: list[Path] = []
        if ms_path.is_file():
            files.append(ms_path)
        elif ms_path.is_dir():
            for p in sorted(ms_path.rglob("*.md")):
                if not p.name.startswith((".", "_")) and "Backups" not in p.parts and "04_Back_Matter" not in p.parts:
                    files.append(p)

        for idx, f in enumerate(files, 1):
            content = f.read_text(encoding="utf-8", errors="replace")
            fm = parse_yaml_frontmatter(content)
            body = FRONTMATTER_REGEX.sub("", content).strip()
            h1 = re.search(r"^#\s+(.+)$", body, flags=re.MULTILINE)
            title = str(fm.get("title", h1.group(1).strip() if h1 else f.stem.replace("_", " ")))
            word_count = len(re.findall(r"\b\w+\b", body))
            chapters.append({
                "id": f"chap_{idx}",
                "filename": f.name,
                "title": title,
                "frontmatter": fm,
                "content": content,
                "body": body,
                "word_count": word_count,
            })

    if world_path and scope and (scope.lore_categories or scope.world):
        lore_items = filter_world_scope(world_path, scope)
        lore_entities = []
        for l_item in lore_items:
            meta = parse_yaml_frontmatter(l_item.content)
            body = FRONTMATTER_REGEX.sub("", l_item.content).strip()
            lore_entities.append({
                "name": l_item.name,
                "category": l_item.category,
                "path": str(l_item.file_path.relative_to(world_path)).replace("\\", "/") if world_path and world_path in l_item.file_path.parents else l_item.file_path.name,
                "metadata": meta,
                "snippet": body[:300] + ("..." if len(body) > 300 else ""),
            })
    else:
        lore_entities = scan_lore_entities(world_path)

    engine_catalog = get_engine_catalog()
    try:
        mesh = ResonanceMesh()
        sparks = [s.to_dict() for s in mesh.generate_sparks(count=8)]
    except Exception:
        sparks = []

    tip_db = get_tip_database()
    tips_list = [t.to_dict() for t in tip_db.get_by_context("drafting")] + [t.to_dict() for t in tip_db.get_all()[:35]]
    tips_json = json.dumps(tips_list).replace("</", "<\\/")
    tips_enabled_val = "true" if are_tips_enabled() else "false"

    chapters_json = json.dumps(chapters).replace("</", "<\\/")
    lore_json = json.dumps(lore_entities).replace("</", "<\\/")
    catalog_json = json.dumps(engine_catalog).replace("</", "<\\/")
    sparks_json = json.dumps(sparks).replace("</", "<\\/")

    target_out = output_path or Path("dist") / "zen_studio.html"

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ars Arcanum — Sovereign Zen Drafting Studio</title>
<style>
  :root {{
    --bg: #0f172a; --panel: #1e293b; --border: #334155;
    --text: #f8fafc; --muted: #94a3b8; --accent: #38bdf8; --gold: #fbbf24;
    --emerald: #10b981; --rose: #f43f5e;
  }}
  body[data-theme="slate"] {{ --bg: #0f172a; --panel: #1e293b; --border: #334155; --text: #f8fafc; --muted: #94a3b8; --accent: #38bdf8; --gold: #fbbf24; }}
  body[data-theme="parchment"] {{ --bg: #f5eedb; --panel: #e8dcc4; --border: #d4c5a9; --text: #2d241e; --muted: #756253; --accent: #8c4320; --gold: #9e6b28; }}
  body[data-theme="nordic"] {{ --bg: #eceff4; --panel: #e5e9f0; --border: #d8dee9; --text: #2e3440; --muted: #4c566a; --accent: #5e81ac; --gold: #d08770; }}
  body[data-theme="solarized"] {{ --bg: #002b36; --panel: #073642; --border: #586e75; --text: #839496; --muted: #657b83; --accent: #268bd2; --gold: #b58900; }}
  body[data-theme="gruvbox"] {{ --bg: #282828; --panel: #3c3836; --border: #504945; --text: #ebdbb2; --muted: #a89984; --accent: #83a598; --gold: #fabd2f; }}
  body[data-theme="amber"] {{ --bg: #120e00; --panel: #241c00; --border: #4d3b00; --text: #ffb000; --muted: #b37b00; --accent: #ffd000; --gold: #ffb000; }}

  * {{ box-sizing: border-box; }}
  body {{
    font-family: Georgia, 'Times New Roman', serif; background: var(--bg); color: var(--text);
    margin: 0; padding: 0; height: 100vh; display: flex; flex-direction: column; overflow: hidden;
  }}
  header {{
    background: var(--panel); border-bottom: 1px solid var(--border);
    padding: 0.6rem 1.5rem; display: flex; justify-content: space-between; align-items: center;
    font-family: system-ui, sans-serif; font-size: 0.875rem;
  }}
  .controls {{ display: flex; gap: 0.6rem; align-items: center; }}
  button, select {{
    background: var(--bg); color: var(--text); border: 1px solid var(--border);
    padding: 0.4rem 0.75rem; border-radius: 6px; font-size: 0.85rem; cursor: pointer;
  }}
  button:hover {{ border-color: var(--accent); }}
  .btn-accent {{ background: #0284c7 !important; color: white !important; border: none; font-weight: 600; }}
  .btn-gold {{ background: #b45309 !important; color: #fef3c7 !important; border: none; font-weight: 600; }}

  .main-workspace {{ display: flex; flex: 1; overflow: hidden; position: relative; }}

  .sidebar {{
    width: 260px; background: var(--panel); border-right: 1px solid var(--border);
    display: flex; flex-direction: column; font-family: system-ui, sans-serif;
  }}
  .sidebar-header {{ padding: 0.75rem 1rem; border-bottom: 1px solid var(--border); font-weight: 600; color: var(--muted); }}
  .chap-list {{ flex: 1; overflow-y: auto; list-style: none; margin: 0; padding: 0; }}
  .chap-item {{
    padding: 0.75rem 1rem; border-bottom: 1px solid rgba(255,255,255,0.04);
    cursor: pointer; transition: background 0.15s ease;
  }}
  .chap-item:hover {{ background: rgba(255,255,255,0.03); }}
  .chap-item.active {{ background: rgba(56, 189, 248, 0.15); border-left: 3px solid var(--accent); }}

  .editor-area {{
    flex: 1; display: flex; justify-content: center; overflow-y: auto; padding: 2.5rem 1.5rem;
    gap: 1.5rem;
  }}
  .editor-container {{ width: 100%; max-width: 740px; display: flex; flex-direction: column; }}
  textarea.zen-editor {{
    width: 100%; flex: 1; min-height: 80vh; background: transparent; color: var(--text);
    border: none; outline: none; resize: none; font-family: inherit; font-size: 1.2rem;
    line-height: 1.85; padding: 0; margin: 0;
  }}

  .preview-pane {{
    width: 480px; max-width: 50%; background: var(--panel); border: 1px solid var(--border);
    border-radius: 8px; padding: 1.5rem; overflow-y: auto; font-family: system-ui, -apple-system, sans-serif;
    display: none; font-size: 0.95rem; line-height: 1.6;
  }}
  .scene-badge {{
    display: inline-flex; align-items: center; background: rgba(56, 189, 248, 0.1); border: 1px solid var(--accent);
    padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; color: var(--accent); margin: 0.2rem 0.2rem 0.2rem 0;
  }}
  .badge-tag {{ font-weight: bold; margin-right: 4px; }}
  .lore-link {{ color: var(--gold); cursor: pointer; text-decoration: underline; }}
  .scene-break {{ border: 0; height: 1px; background: var(--border); margin: 1.5rem 0; }}

  .lore-drawer {{
    width: 360px; background: var(--panel); border-left: 1px solid var(--border);
    display: none; flex-direction: column; font-family: system-ui, sans-serif;
  }}
  .lore-drawer.open {{ display: flex; }}
  .drawer-tabs {{ display: flex; border-bottom: 1px solid var(--border); }}
  .d-tab {{ flex: 1; padding: 0.5rem; background: var(--bg); border: none; color: var(--muted); font-size: 0.8rem; cursor: pointer; }}
  .d-tab.active {{ background: var(--panel); color: var(--accent); font-weight: 600; border-bottom: 2px solid var(--accent); }}
  .lore-search {{ padding: 0.75rem; border-bottom: 1px solid var(--border); }}
  .lore-search input {{
    width: 100%; background: var(--bg); color: var(--text); border: 1px solid var(--border);
    padding: 0.4rem 0.6rem; border-radius: 4px; outline: none; font-size: 0.85rem;
  }}
  .lore-list {{ flex: 1; overflow-y: auto; padding: 0.75rem; }}
  .lore-card {{
    background: var(--bg); border: 1px solid var(--border); border-radius: 6px;
    padding: 0.75rem; margin-bottom: 0.75rem; font-size: 0.85rem;
  }}

  .craft-modal {{
    display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(0,0,0,0.85); z-index: 1000; justify-content: center; align-items: center;
    font-family: system-ui, sans-serif;
  }}
  .craft-modal-content {{
    background: var(--bg); border: 1px solid var(--border); border-radius: 12px;
    width: 90%; max-width: 900px; height: 85vh; display: flex; flex-direction: column; overflow: hidden;
  }}
  .craft-modal-header {{
    background: var(--panel); padding: 1rem 1.5rem; border-bottom: 1px solid var(--border);
    display: flex; justify-content: space-between; align-items: center;
  }}
  .craft-modal-body {{
    flex: 1; overflow-y: auto; padding: 1.5rem; display: flex; flex-direction: column; gap: 1.25rem;
  }}

  footer.telemetry {{
    background: var(--panel); border-top: 1px solid var(--border);
    padding: 0.4rem 1.5rem; display: flex; justify-content: space-between;
    font-family: system-ui, sans-serif; font-size: 0.8rem; color: var(--muted);
  }}
</style>
</head>
<body data-theme="slate">

<header>
  <div style="font-weight:700;color:var(--accent);display:flex;align-items:center;gap:0.5rem;">
    🏛️ Ars Arcanum Zen Studio <span id="hdrDocTitle" style="color:var(--text);font-weight:400;">—</span>
  </div>
  <div class="controls">
    <select id="themeSelect" onchange="switchTheme(this.value)" title="Color Themes">
      <option value="slate">Classic Slate</option>
      <option value="parchment">Parchment Classical</option>
      <option value="nordic">Nordic Snow</option>
      <option value="solarized">Solarized Dark</option>
      <option value="gruvbox">Gruvbox Warmth</option>
      <option value="amber">Cyberpunk Amber</option>
    </select>
    <button id="btnSound" onclick="toggleTypewriterSound()" title="Typewriter Mechanical Soundscape">🔇 Sound: OFF</button>
    <button id="btnPreview" onclick="toggleSplitPreview()" title="Live Scene Tag & Markdown Inspector">👁️ Preview: Off</button>
    <button onclick="toggleSidebar()">📁 Files</button>
    <button onclick="toggleLoreDrawer()">📜 Lore Vault ({len(lore_entities)})</button>
    <button class="btn-gold" onclick="openCraftModal()">💡 Craft Logic</button>
    <button class="btn-accent" onclick="exportMarkdown()">💾 Download</button>
  </div>
</header>

<div class="main-workspace">
  <div class="sidebar" id="sidebar">
    <div class="sidebar-header">Manuscript Chapters</div>
    <ul class="chap-list" id="chapList"></ul>
  </div>

  <div class="editor-area">
    <div class="editor-container">
      <textarea class="zen-editor" id="editor" placeholder="Write your prose here..." oninput="handleEditorInput()" onkeydown="handleKeyDown(event)"></textarea>
    </div>
    <div class="preview-pane" id="previewPane">
      <div style="font-weight:600;color:var(--accent);margin-bottom:0.75rem;border-bottom:1px solid var(--border);padding-bottom:0.4rem;">
        🔍 Live Markdown & Scene Tag Inspector
      </div>
      <div id="previewContent"></div>
    </div>
  </div>

  <div class="lore-drawer" id="loreDrawer">
    <div class="drawer-tabs">
      <button class="d-tab active" id="tabBtnLore" onclick="switchDrawerTab('lore')">📜 Lore</button>
      <button class="d-tab" id="tabBtnRules" onclick="switchDrawerTab('rules')">📐 Rules</button>
      <button class="d-tab" id="tabBtnSparks" onclick="switchDrawerTab('sparks')">💡 Sparks</button>
      <button class="d-tab" id="tabBtnTips" onclick="switchDrawerTab('tips')">💡 Tips</button>
    </div>
    <div class="lore-search">
      <input type="text" id="loreQuery" placeholder="Search characters, locations, craft rules, tips..." oninput="filterDrawer(this.value)">
    </div>
    <div class="lore-list" id="loreList"></div>
  </div>
</div>

<footer class="telemetry">
  <div>
    <span id="telWords">0 words</span> | <span id="telChars">0 chars</span>
  </div>
  <div id="zenTipBar" style="color:var(--gold);cursor:pointer;max-width:520px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;" onclick="cycleZenTip()" title="Click for next craft wisdom tip">
    💡 <span id="zenTipText">Loading craft wisdom...</span>
  </div>
  <div>
    📖 Reading: <span id="telReadTime">0 min</span> | 🎙️ Narration: <span id="telSpeakTime">0 min</span> | Autosaved
  </div>
</footer>

<div class="craft-modal" id="craftModal" onclick="if(event.target===this)closeCraftModal()">
  <div class="craft-modal-content">
    <div class="craft-modal-header">
      <div>
        <span style="font-weight:700;font-size:1.1rem;color:var(--accent);">💡 Ars Arcanum Craft & Engine Encyclopedia</span>
        <div style="font-size:0.8rem;color:var(--muted);margin-top:2px;">50 Verified Engines • Mathematical Logic • Narrative Physics • Extension Guides</div>
      </div>
      <button onclick="closeCraftModal()" style="font-size:1.2rem;line-height:1;background:transparent;border:none;color:var(--muted);">✕</button>
    </div>
    <div class="lore-search" style="background:#131b2e;padding:0.75rem 1.5rem;">
      <input type="text" id="modalEngineSearch" placeholder="Search any engine, formula, or craft principle (e.g. astrophysics, MRU, pacing, trophic, conlang)..." oninput="filterModalEngines(this.value)">
    </div>
    <div class="craft-modal-body" id="modalEngineList">
      <!-- Dynamic Engine Cards -->
    </div>
  </div>
</div>

<script>
  function escapeHtml(str) {{
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }}

  const chapters = {chapters_json};
  const lore = {lore_json};
  const catalog = {catalog_json};
  const sparks = {sparks_json};
  const tips = {tips_json};
  let tipsEnabled = {tips_enabled_val};
  let currentChapIdx = 0;
  let activeDrawerTab = "lore";
  let currentZenTipIdx = 0;
  let audioCtx = null;
  let soundEnabled = false;
  let previewEnabled = false;

  const CRAFT_RULES = [
    {{
      title: "Motivational Response Unit (MRU)",
      domain: "Prose Mechanics",
      desc: "Dwight Swain's causal sequence: Stimulus (External) -> Reflex (Involuntary) -> Fear/Rational Emotion -> Deliberate Action -> Spoken Word."
    }},
    {{
      title: "Gary Provost Sentence Waveform",
      domain: "Stylistics & Rhythm",
      desc: "Vary sentence length across 5, 8, 14, 25 words to create musicality and prevent ear fatigue."
    }},
    {{
      title: "8 Sensory Channels",
      domain: "Atmosphere & Polish",
      desc: "Balance visual (sight), auditory (sound), olfactory (smell), gustatory (taste), tactile (touch), proprioception (body orientation), thermoception (temperature), chronoception (time passage)."
    }},
    {{
      title: "Sanderson's First Law of Magic",
      domain: "Magic Systems",
      desc: "An author's ability to solve problems with magic satisfyingly is directly proportional to how well the reader understands said magic."
    }},
    {{
      title: "Trophic Energy Transfer (10% Law)",
      domain: "Ecology & Worldbuilding",
      desc: "Each trophic level supports ~10% of the biomass of the level beneath it. Colossal apex predators require immense herbivore biomes."
    }}
  ];

  function init() {{
    const savedTheme = localStorage.getItem("arcanum_zen_theme") || "slate";
    switchTheme(savedTheme);
    renderChapList();
    if (chapters.length > 0) {{
      loadChapter(0);
    }}
    renderDrawer();
    renderModalEngines(catalog);
    initZenTip();
  }}

  function switchTheme(theme) {{
    document.body.setAttribute("data-theme", theme);
    const select = document.getElementById("themeSelect");
    if (select) select.value = theme;
    localStorage.setItem("arcanum_zen_theme", theme);
  }}

  function toggleTypewriterSound() {{
    soundEnabled = !soundEnabled;
    const btn = document.getElementById("btnSound");
    if (soundEnabled) {{
      if (!audioCtx) {{
        const AudioContextClass = window.AudioContext || window.webkitAudioContext;
        if (AudioContextClass) {{
          audioCtx = new AudioContextClass();
        }}
      }}
      if (audioCtx && audioCtx.state === "suspended") {{
        audioCtx.resume();
      }}
      if (btn) btn.textContent = "🔊 Sound: ON";
      playTypewriterSound(false);
    }} else {{
      if (btn) btn.textContent = "🔇 Sound: OFF";
    }}
  }}

  function playTypewriterSound(isReturn) {{
    if (!soundEnabled || !audioCtx) return;
    try {{
      const now = audioCtx.currentTime;
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      if (isReturn) {{
        osc.type = "sine";
        osc.frequency.setValueAtTime(440, now);
        osc.frequency.exponentialRampToValueAtTime(880, now + 0.08);
        gain.gain.setValueAtTime(0.12, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.12);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start(now);
        osc.stop(now + 0.12);
      }} else {{
        const bufferSize = Math.floor(audioCtx.sampleRate * 0.025);
        const noiseBuffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
        const output = noiseBuffer.getChannelData(0);
        for (let i = 0; i < bufferSize; i++) {{
          output[i] = Math.random() * 2 - 1;
        }}
        const whiteNoise = audioCtx.createBufferSource();
        whiteNoise.buffer = noiseBuffer;

        const filter = audioCtx.createBiquadFilter();
        filter.type = "bandpass";
        filter.frequency.value = 1200 + Math.random() * 400;
        filter.Q.value = 3.0;

        const noiseGain = audioCtx.createGain();
        noiseGain.gain.setValueAtTime(0.18, now);
        noiseGain.gain.exponentialRampToValueAtTime(0.001, now + 0.025);

        whiteNoise.connect(filter);
        filter.connect(noiseGain);
        noiseGain.connect(audioCtx.destination);
        whiteNoise.start(now);
      }}
    }} catch (e) {{
      // AudioContext unavailable or error
    }}
  }}

  function toggleSplitPreview() {{
    previewEnabled = !previewEnabled;
    const pane = document.getElementById("previewPane");
    const btn = document.getElementById("btnPreview");
    if (pane) {{
      pane.style.display = previewEnabled ? "block" : "none";
    }}
    if (btn) {{
      btn.textContent = previewEnabled ? "👁️ Preview: ON" : "👁️ Preview: OFF";
    }}
    if (previewEnabled) {{
      renderSplitPreview();
    }}
  }}

  function renderSplitPreview() {{
    const text = document.getElementById("editor").value;
    const preview = document.getElementById("previewContent");
    if (!preview) return;

    const lines = text.split("\n");
    let html = "";
    let inList = false;

    lines.forEach(line => {{
      let trimmed = line.trim();
      const tagMatch = trimmed.match(/^\\[([A-Za-z0-9_-]+):\\s*(.+)\\]$/);
      if (tagMatch) {{
        html += `<div class="scene-badge"><span class="badge-tag">${{escapeHtml(tagMatch[1].toUpperCase())}}</span>${{escapeHtml(tagMatch[2])}}</div>`;
        return;
      }}
      if (trimmed.startsWith("<!--") && trimmed.endsWith("-->")) {{
        html += `<div class="scene-badge" style="border-color:var(--gold);color:var(--gold);"><span class="badge-tag">NOTE</span>${{escapeHtml(trimmed.slice(4, -3).trim())}}</div>`;
        return;
      }}
      if (trimmed === "---" || trimmed === "***" || trimmed === "___") {{
        if (inList) {{ html += "</ul>"; inList = false; }}
        html += '<hr class="scene-break">';
        return;
      }}
      if (trimmed.startsWith("### ")) {{
        if (inList) {{ html += "</ul>"; inList = false; }}
        html += `<h3 style="color:var(--accent);margin:1rem 0 0.5rem 0;">${{escapeHtml(trimmed.slice(4))}}</h3>`;
        return;
      }}
      if (trimmed.startsWith("## ")) {{
        if (inList) {{ html += "</ul>"; inList = false; }}
        html += `<h2 style="color:var(--accent);margin:1.2rem 0 0.6rem 0;border-bottom:1px solid var(--border);padding-bottom:0.3rem;">${{escapeHtml(trimmed.slice(3))}}</h2>`;
        return;
      }}
      if (trimmed.startsWith("# ")) {{
        if (inList) {{ html += "</ul>"; inList = false; }}
        html += `<h1 style="color:var(--gold);margin:1.5rem 0 0.75rem 0;font-size:1.4rem;">${{escapeHtml(trimmed.slice(2))}}</h1>`;
        return;
      }}
      if (trimmed.startsWith("> ")) {{
        if (inList) {{ html += "</ul>"; inList = false; }}
        html += `<blockquote style="border-left:3px solid var(--gold);margin:0.5rem 0;padding-left:0.8rem;color:var(--muted);font-style:italic;">${{escapeHtml(trimmed.slice(2))}}</blockquote>`;
        return;
      }}
      if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {{
        if (!inList) {{ html += '<ul style="margin:0.5rem 0;padding-left:1.5rem;">'; inList = true; }}
        html += `<li>${{escapeHtml(trimmed.slice(2))}}</li>`;
        return;
      }}
      if (inList) {{
        html += "</ul>";
        inList = false;
      }}
      if (trimmed === "") {{
        html += '<div style="height:0.75rem;"></div>';
        return;
      }}

      let parsedLine = escapeHtml(line);
      parsedLine = parsedLine.replace(/\\*\\*(.*?)\\*\\*/g, "<strong>$1</strong>");
      parsedLine = parsedLine.replace(/\\*(.*?)\\*/g, "<em>$1</em>");
      parsedLine = parsedLine.replace(/`([^`]+)`/g, "<code style='background:rgba(255,255,255,0.08);padding:1px 4px;border-radius:3px;'>$1</code>");

      html += `<p style="margin:0 0 0.75rem 0;text-indent:1.2rem;line-height:1.7;">${{parsedLine}}</p>`;
    }});

    if (inList) {{
      html += "</ul>";
    }}
    preview.innerHTML = html;
  }}

  function handleEditorInput() {{
    updateTelemetry();
    if (previewEnabled) {{
      renderSplitPreview();
    }}
  }}

  function handleKeyDown(event) {{
    playTypewriterSound(event.key === "Enter");
    if (event.key === "Tab") {{
      event.preventDefault();
      const editor = document.getElementById("editor");
      const start = editor.selectionStart;
      const end = editor.selectionEnd;
      editor.value = editor.value.substring(0, start) + "  " + editor.value.substring(end);
      editor.selectionStart = editor.selectionEnd = start + 2;
      handleEditorInput();
    }} else if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "s") {{
      event.preventDefault();
      updateTelemetry();
      const hdr = document.getElementById("hdrDocTitle");
      if (hdr) {{
        const orig = hdr.textContent;
        hdr.textContent = orig + " (Saved)";
        setTimeout(() => {{ hdr.textContent = orig; }}, 1200);
      }}
    }}
  }}

  function initZenTip() {{
    if (!tipsEnabled || !tips.length) {{
      const bar = document.getElementById("zenTipBar");
      if (bar) bar.style.display = "none";
      return;
    }}
    renderZenTip(tips[0]);
  }}

  function renderZenTip(tip) {{
    if (!tip) return;
    const txt = document.getElementById("zenTipText");
    if (txt) {{
      txt.textContent = `[${{(tip.engine || 'CRAFT').toUpperCase()}}]: ${{tip.title}} — ${{tip.content}}`;
    }}
  }}

  function cycleZenTip() {{
    if (!tips.length) return;
    currentZenTipIdx = (currentZenTipIdx + 1) % tips.length;
    renderZenTip(tips[currentZenTipIdx]);
  }}

  function renderChapList() {{
    const list = document.getElementById("chapList");
    list.innerHTML = "";
    chapters.forEach((c, idx) => {{
      const li = document.createElement("li");
      li.className = `chap-item ${{idx === currentChapIdx ? "active" : ""}}`;
      li.innerHTML = `<strong>${{escapeHtml(c.title)}}</strong><br><small style="color:var(--muted);">${{c.word_count}} words</small>`;
      li.onclick = () => loadChapter(idx);
      list.appendChild(li);
    }});
  }}

  function loadChapter(idx) {{
    currentChapIdx = idx;
    const chap = chapters[idx];
    if (!chap) return;

    document.getElementById("hdrDocTitle").textContent = chap.title;
    const saved = localStorage.getItem(`arcanum_zen_${{chap.id}}`);
    document.getElementById("editor").value = saved !== null ? saved : chap.content;
    renderChapList();
    updateTelemetry();
  }}

  function updateTelemetry() {{
    const text = document.getElementById("editor").value;
    const words = (text.match(/\\b\\w+\\b/g) || []).length;
    const chars = text.length;
    const readMins = Math.ceil(words / 200);
    const speakMins = (words / 150).toFixed(1);

    document.getElementById("telWords").textContent = `${{words.toLocaleString()}} words`;
    document.getElementById("telChars").textContent = `${{chars.toLocaleString()}} chars`;
    document.getElementById("telReadTime").textContent = `${{readMins}} min`;
    document.getElementById("telSpeakTime").textContent = `${{speakMins}} min`;

    const chap = chapters[currentChapIdx];
    if (chap) {{
      localStorage.setItem(`arcanum_zen_${{chap.id}}`, text);
    }}
  }}

  function switchDrawerTab(tab) {{
    activeDrawerTab = tab;
    document.getElementById("tabBtnLore").className = `d-tab ${{tab === 'lore' ? 'active' : ''}}`;
    document.getElementById("tabBtnRules").className = `d-tab ${{tab === 'rules' ? 'active' : ''}}`;
    document.getElementById("tabBtnSparks").className = `d-tab ${{tab === 'sparks' ? 'active' : ''}}`;
    document.getElementById("tabBtnTips").className = `d-tab ${{tab === 'tips' ? 'active' : ''}}`;
    renderDrawer();
  }}

  function renderDrawer() {{
    const q = (document.getElementById("loreQuery").value || "").toLowerCase();
    const list = document.getElementById("loreList");
    list.innerHTML = "";

    if (activeDrawerTab === "lore") {{
      const filtered = lore.filter(it =>
        it.name.toLowerCase().includes(q) ||
        it.category.toLowerCase().includes(q) ||
        it.snippet.toLowerCase().includes(q)
      );
      if (filtered.length === 0) {{
        list.innerHTML = `<div style="color:var(--muted);text-align:center;padding:2rem;">No matching lore found</div>`;
        return;
      }}
      filtered.forEach(it => {{
        const card = document.createElement("div");
        card.className = "lore-card";
        card.innerHTML = `
          <div style="display:flex;justify-content:space-between;color:var(--accent);font-weight:600;">
            <span>${{escapeHtml(it.name)}}</span>
            <small style="color:var(--gold);">${{escapeHtml(it.category)}}</small>
          </div>
          <p style="margin:0.4rem 0 0 0;color:var(--muted);font-size:0.8rem;">${{escapeHtml(it.snippet)}}</p>
        `;
        list.appendChild(card);
      }});
    }} else if (activeDrawerTab === "rules") {{
      const filteredRules = CRAFT_RULES.filter(r =>
        r.title.toLowerCase().includes(q) ||
        r.domain.toLowerCase().includes(q) ||
        r.desc.toLowerCase().includes(q)
      );
      filteredRules.forEach(r => {{
        const card = document.createElement("div");
        card.className = "lore-card";
        card.innerHTML = `
          <div style="display:flex;justify-content:space-between;color:var(--gold);font-weight:600;">
            <span>${{escapeHtml(r.title)}}</span>
            <small style="color:var(--accent);">${{escapeHtml(r.domain)}}</small>
          </div>
          <p style="margin:0.4rem 0 0 0;color:var(--text);font-size:0.825rem;line-height:1.4;">${{escapeHtml(r.desc)}}</p>
        `;
        list.appendChild(card);
      }});
    }} else if (activeDrawerTab === "sparks") {{
      const filteredSparks = sparks.filter(s =>
        s.title.toLowerCase().includes(q) ||
        (s.domains && s.domains.some(d => d.toLowerCase().includes(q))) ||
        (s.core_analogy && s.core_analogy.toLowerCase().includes(q)) ||
        (s.scene_conflict && s.scene_conflict.toLowerCase().includes(q))
      );
      if (filteredSparks.length === 0) {{
        list.innerHTML = `<div style="color:var(--muted);text-align:center;padding:2rem;">No matching sparks found</div>`;
        return;
      }}
      filteredSparks.forEach(s => {{
        const card = document.createElement("div");
        card.className = "lore-card";
        card.innerHTML = `
          <div style="display:flex;justify-content:space-between;color:var(--gold);font-weight:600;font-size:0.85rem;">
            <span>💡 ${{escapeHtml(s.title)}}</span>
          </div>
          <div style="color:var(--accent);font-size:0.75rem;margin-top:2px;">${{escapeHtml((s.domains || []).join(' • '))}}</div>
          <p style="margin:0.4rem 0 0 0;color:var(--text);font-size:0.8rem;line-height:1.4;"><strong>Analogy:</strong> ${{escapeHtml(s.core_analogy)}}</p>
          <p style="margin:0.3rem 0 0 0;color:var(--muted);font-size:0.78rem;"><strong>Conflict:</strong> ${{escapeHtml(s.scene_conflict)}}</p>
          <div style="margin-top:0.3rem;font-size:0.72rem;color:var(--emerald);">Sensory: ${{escapeHtml((s.sensory_palette || []).join(' • '))}}</div>
        `;
        list.appendChild(card);
      }});
    }} else if (activeDrawerTab === "tips") {{
      const filteredTips = tips.filter(t =>
        (t.title && t.title.toLowerCase().includes(q)) ||
        (t.content && t.content.toLowerCase().includes(q)) ||
        (t.engine && t.engine.toLowerCase().includes(q)) ||
        (t.subfeature && t.subfeature.toLowerCase().includes(q))
      );
      if (filteredTips.length === 0) {{
        list.innerHTML = `<div style="color:var(--muted);text-align:center;padding:2rem;">No matching craft tips found</div>`;
        return;
      }}
      filteredTips.forEach(t => {{
        const card = document.createElement("div");
        card.className = "lore-card";
        card.style.borderLeft = "3px solid var(--gold)";
        card.innerHTML = `
          <div style="display:flex;justify-content:space-between;color:var(--gold);font-weight:600;font-size:0.85rem;">
            <span>💡 ${{escapeHtml(t.title)}}</span>
            <small style="color:var(--accent);text-transform:uppercase;">${{escapeHtml(t.engine)}}</small>
          </div>
          <div style="color:var(--muted);font-size:0.75rem;margin-top:2px;">${{escapeHtml(t.subfeature || t.feature || '')}} • ${{escapeHtml(t.depth || 'Advanced')}}</div>
          <p style="margin:0.4rem 0 0 0;color:var(--text);font-size:0.825rem;line-height:1.45;">${{escapeHtml(t.content)}}</p>
          ${{t.example ? `<div style="margin-top:0.35rem;font-size:0.75rem;color:var(--emerald);font-family:monospace;">⚡ ${{escapeHtml(t.example)}}</div>` : ''}}
        `;
        list.appendChild(card);
      }});
    }}
  }}

  function filterDrawer(q) {{
    renderDrawer();
  }}

  function filterLore(q) {{
    renderDrawer();
  }}

  function toggleSidebar() {{
    const sb = document.getElementById("sidebar");
    sb.style.display = sb.style.display === "none" ? "flex" : "none";
  }}

  function toggleLoreDrawer() {{
    const drawer = document.getElementById("loreDrawer");
    drawer.classList.toggle("open");
  }}

  function openCraftModal() {{
    document.getElementById("craftModal").style.display = "flex";
  }}

  function closeCraftModal() {{
    document.getElementById("craftModal").style.display = "none";
  }}

  function renderModalEngines(items) {{
    const container = document.getElementById("modalEngineList");
    container.innerHTML = "";
    if (items.length === 0) {{
      container.innerHTML = `<div style="color:var(--muted);text-align:center;padding:2rem;">No matching craft engines found</div>`;
      return;
    }}
    items.forEach(spec => {{
      const card = document.createElement("div");
      card.style.background = "#1e293b";
      card.style.border = "1px solid var(--border)";
      card.style.borderRadius = "8px";
      card.style.padding = "1rem 1.25rem";

      card.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;">
          <h3 style="margin:0;font-size:1.1rem;color:var(--accent);">${{escapeHtml(spec.name)}} <code style="font-size:0.8rem;color:var(--gold);margin-left:0.5rem;">arcanum ${{escapeHtml(spec.name)}}</code></h3>
          <span style="background:#0f172a;padding:2px 8px;border-radius:4px;font-size:0.75rem;color:var(--muted);">${{escapeHtml(spec.category)}}</span>
        </div>
        <p style="margin:0 0 0.75rem 0;color:var(--text);font-size:0.9rem;">${{escapeHtml(spec.description)}}</p>
        <div style="background:#0b1120;border-left:3px solid var(--accent);padding:0.6rem 0.8rem;margin-bottom:0.75rem;font-size:0.85rem;color:#cbd5e1;white-space:pre-wrap;"><strong>📐 Science & Craft Logic:</strong>\n${{escapeHtml(spec.scientific_logic || "Underlying logic defined in registry.")}}</div>
        <div style="background:#0b1120;border-left:3px solid var(--gold);padding:0.6rem 0.8rem;margin-bottom:0.75rem;font-size:0.85rem;color:#cbd5e1;white-space:pre-wrap;"><strong>💡 Why This Way:</strong>\n${{escapeHtml(spec.why_this_way || "Design rationale defined in registry.")}}</div>
        <div style="background:#0b1120;border-left:3px solid var(--emerald);padding:0.6rem 0.8rem;font-size:0.85rem;color:#cbd5e1;white-space:pre-wrap;"><strong>🛠️ How to Extend:</strong>\n${{escapeHtml(spec.extension_guide || "Extension patterns defined in registry.")}}</div>
      `;
      container.appendChild(card);
    }});
  }}

  function filterModalEngines(q) {{
    const query = q.toLowerCase();
    const filtered = catalog.filter(spec =>
      spec.name.toLowerCase().includes(query) ||
      (spec.description && spec.description.toLowerCase().includes(query)) ||
      (spec.scientific_logic && spec.scientific_logic.toLowerCase().includes(query)) ||
      (spec.why_this_way && spec.why_this_way.toLowerCase().includes(query)) ||
      (spec.extension_guide && spec.extension_guide.toLowerCase().includes(query)) ||
      (spec.category && spec.category.toLowerCase().includes(query))
    );
    renderModalEngines(filtered);
  }}

  function exportMarkdown() {{
    const chap = chapters[currentChapIdx];
    const text = document.getElementById("editor").value;
    const blob = new Blob([text], {{ type: "text/markdown;charset=utf-8" }});
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = chap ? chap.filename : "manuscript.md";
    a.click();
    URL.revokeObjectURL(url);
  }}

  window.addEventListener("DOMContentLoaded", init);
</script>
</body>
</html>
"""
    atomic_write(target_out, html_content)
    return target_out


generate_zen_studio_bundle = build_zen_studio_bundle


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ars Arcanum Standalone Zen Drafting Studio")
    parser.add_argument("target", nargs="?", default=".", help="Manuscript directory or Markdown chapter file")
    parser.add_argument("--world", "-w", help="Optional World Bible directory for in-situ drawer inspection")
    parser.add_argument("--output", "-o", help="Output standalone HTML file path (default: dist/zen_studio.html)")
    parser.add_argument("--json", action="store_true", help="Print studio metadata as JSON to stdout")
    add_scope_arguments(parser)
    args = parser.parse_args(argv)
    scope_obj = parse_scope_args(args)

    if args.target and args.target != ".":
        p_cand = Path(args.target)
        if p_cand.exists():
            target_path = p_cand
        else:
            r_str = resolve_manuscript_dir(args.target, scope=scope_obj)
            if r_str and Path(r_str).exists():
                target_path = Path(r_str)
            else:
                print(f"Error: Target path does not exist: {args.target}", file=sys.stderr)
                if argv is None:
                    sys.exit(1)
                return 1
    else:
        r_str = resolve_manuscript_dir(scope=scope_obj)
        target_path = Path(r_str) if r_str and Path(r_str).exists() else Path.cwd()

    raw_world = resolve_world_dir(args.world, scope=scope_obj)
    world_path = Path(raw_world) if raw_world else None
    out_path = Path(args.output) if args.output else None

    bundle = build_zen_studio_bundle(target_path, world_path=world_path, output_path=out_path, scope=scope_obj)

    if args.json:
        report = {
            "target": str(target_path),
            "world": str(world_path) if world_path else None,
            "bundle_path": str(bundle),
            "status": "ready",
            "scope": {
                "chapters": scope_obj.chapters,
                "scenes": scope_obj.scenes,
                "raw_scope": scope_obj.raw_scope,
            } if scope_obj else None,
        }
        print(json.dumps(report, indent=2))
        return 0

    print(format_scope_banner("Ars Arcanum Sovereign Zen Studio — v2.0.0", scope_obj))
    print(f"Manuscript Target: {target_path}")
    if world_path:
        print(f"World Bible Lore:  {world_path}")
    print(f"Zen Studio Bundle: {bundle}")
    print("-" * 75)
    print("Open the HTML file in any modern web browser for offline drafting.")
    print("=" * 75)
    return 0


if __name__ == "__main__":
    main()




