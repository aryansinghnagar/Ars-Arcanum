#!/usr/bin/env python3
"""
Ars Arcanum Zen Drafting Studio Presentation Template
(scripts/lib/zen_studio_template.py)
================================================================================
Single-file offline HTML5 presentation template for the Sovereign Zen Drafting Studio.
Declares strict offline Content Security Policy (default-src 'none'), 6 high-contrast
and parchment themes, in-situ metadata inspector, multi-tier narrative outline drawer,
typewriter audio synthesizer, and real-time two-way frontmatter synchronization.
"""

from __future__ import annotations


def render_zen_studio_html(
    chapters_json: str,
    lore_json: str,
    outlines_json: str,
    catalog_json: str,
    sparks_json: str,
    tips_json: str,
    tips_enabled_val: str,
    lore_entities_count: int = 0,
) -> str:
    """Renders the complete standalone offline Zen Studio HTML5 document."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ars Arcanum — Sovereign Zen Drafting Studio</title>
<style>
  :root {{
    --bg: #0f172a; --panel: #1e293b; --panel-alt: #131b2e; --border: #334155;
    --text: #f8fafc; --muted: #94a3b8; --accent: #38bdf8; --accent-hover: #0284c7;
    --gold: #fbbf24; --emerald: #10b981; --rose: #f43f5e;
  }}
  body[data-theme="slate"] {{
    --bg: #0f172a; --panel: #1e293b; --panel-alt: #131b2e; --border: #334155;
    --text: #f8fafc; --muted: #94a3b8; --accent: #38bdf8; --accent-hover: #0284c7;
    --gold: #fbbf24; --emerald: #10b981; --rose: #f43f5e;
  }}
  body[data-theme="parchment"] {{
    --bg: #f5eedb; --panel: #e8dcc4; --panel-alt: #ded0b5; --border: #d4c5a9;
    --text: #2d241e; --muted: #756253; --accent: #8c4320; --accent-hover: #6d3318;
    --gold: #9e6b28; --emerald: #2d6a4f; --rose: #9e2a2b;
  }}
  body[data-theme="nordic"] {{
    --bg: #eceff4; --panel: #e5e9f0; --panel-alt: #d8dee9; --border: #c8d0df;
    --text: #2e3440; --muted: #4c566a; --accent: #5e81ac; --accent-hover: #434c5e;
    --gold: #d08770; --emerald: #a3be8c; --rose: #bf616a;
  }}
  body[data-theme="solarized"] {{
    --bg: #002b36; --panel: #073642; --panel-alt: #001f27; --border: #586e75;
    --text: #839496; --muted: #657b83; --accent: #268bd2; --accent-hover: #2aa198;
    --gold: #b58900; --emerald: #859900; --rose: #dc322f;
  }}
  body[data-theme="gruvbox"] {{
    --bg: #282828; --panel: #3c3836; --panel-alt: #1d2021; --border: #504945;
    --text: #ebdbb2; --muted: #a89984; --accent: #83a598; --accent-hover: #b8bb26;
    --gold: #fabd2f; --emerald: #b8bb26; --rose: #fb4934;
  }}
  body[data-theme="amber"] {{
    --bg: #120e00; --panel: #241c00; --panel-alt: #1a1400; --border: #4d3b00;
    --text: #ffb000; --muted: #b37b00; --accent: #ffd000; --accent-hover: #ff9000;
    --gold: #ffb000; --emerald: #33ff33; --rose: #ff3333;
  }}

  body[data-font="serif"] {{ font-family: 'Literata', 'Bookerly', Georgia, 'Times New Roman', serif; }}
  body[data-font="sans"] {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }}
  body[data-font="dyslexic"] {{ font-family: 'OpenDyslexic', 'Atkinson Hyperlegible', system-ui, sans-serif; letter-spacing: 0.35px; word-spacing: 1.5px; }}
  body[data-font="mono"] {{ font-family: 'JetBrains Mono', 'Fira Code', Consolas, monospace; }}

  * {{ box-sizing: border-box; }}
  body {{
    font-family: 'Literata', 'Bookerly', Georgia, 'Times New Roman', serif; background: var(--bg); color: var(--text);
    margin: 0; padding: 0; height: 100vh; display: flex; flex-direction: column; overflow: hidden;
  }}
  header {{
    background: var(--panel); border-bottom: 1px solid var(--border);
    padding: 0.5rem 1.25rem; display: flex; justify-content: space-between; align-items: center;
    font-family: system-ui, -apple-system, sans-serif; font-size: 0.85rem; flex-shrink: 0;
  }}
  .brand-title {{
    font-weight: 700; color: var(--accent); display: flex; align-items: center; gap: 0.5rem;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 420px;
  }}
  .controls {{ display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap; }}
  button, select, input, textarea {{
    background: var(--bg); color: var(--text); border: 1px solid var(--border);
    border-radius: 6px; font-size: 0.85rem; font-family: system-ui, -apple-system, sans-serif;
  }}
  button, select {{ padding: 0.35rem 0.65rem; cursor: pointer; transition: all 0.15s ease; }}
  button:hover {{ border-color: var(--accent); }}
  button.active {{ background: rgba(56, 189, 248, 0.18); border-color: var(--accent); color: var(--accent); font-weight: 600; }}
  .btn-accent {{ background: #0284c7 !important; color: white !important; border: none; font-weight: 600; }}
  .btn-gold {{ background: #b45309 !important; color: #fef3c7 !important; border: none; font-weight: 600; }}

  /* Main Workspace */
  .main-workspace {{ display: flex; flex: 1; overflow: hidden; position: relative; }}

  /* Generic Side Panels */
  .side-panel {{
    width: 320px; min-width: 260px; background: var(--panel); border-right: 1px solid var(--border);
    display: none; flex-direction: column; font-family: system-ui, -apple-system, sans-serif;
    flex-shrink: 0; transition: width 0.2s cubic-bezier(0.4, 0, 0.2, 1); position: relative; z-index: 10;
  }}
  .side-panel.right-dock {{ border-right: none; border-left: 1px solid var(--border); }}
  .side-panel.open {{ display: flex; }}
  .side-panel.expanded {{ width: 500px; }}
  .side-panel.collapsed {{ width: 44px; min-width: 44px; overflow: hidden; }}
  .side-panel.collapsed .side-panel-body,
  .side-panel.collapsed .outline-tabs,
  .side-panel.collapsed .meta-sync-badge,
  .side-panel.collapsed .panel-title-text {{ display: none !important; }}

  .side-panel-header {{
    padding: 0.6rem 0.85rem; border-bottom: 1px solid var(--border); font-weight: 600;
    display: flex; justify-content: space-between; align-items: center; background: var(--panel-alt);
    font-size: 0.85rem; color: var(--text); flex-shrink: 0;
  }}
  .panel-header-actions {{ display: flex; gap: 0.25rem; align-items: center; }}
  .btn-tool-action {{
    background: transparent; border: none; padding: 0.2rem 0.4rem; color: var(--muted);
    font-size: 0.85rem; border-radius: 4px; line-height: 1;
  }}
  .btn-tool-action:hover {{ color: var(--accent); background: rgba(255,255,255,0.06); }}

  .side-panel-body {{
    flex: 1; overflow-y: auto; padding: 0.85rem; display: flex; flex-direction: column; gap: 0.75rem;
  }}

  /* Sidebar Chapters List */
  .sidebar {{
    width: 250px; background: var(--panel); border-right: 1px solid var(--border);
    display: flex; flex-direction: column; font-family: system-ui, -apple-system, sans-serif; flex-shrink: 0;
  }}
  .chap-list {{ flex: 1; overflow-y: auto; list-style: none; margin: 0; padding: 0; }}
  .chap-item {{
    padding: 0.65rem 0.85rem; border-bottom: 1px solid rgba(255,255,255,0.04);
    cursor: pointer; transition: background 0.15s ease; font-size: 0.85rem;
  }}
  .chap-item:hover {{ background: rgba(255,255,255,0.04); }}
  .chap-item.active {{ background: rgba(56, 189, 248, 0.15); border-left: 3px solid var(--accent); }}

  /* Center Editor Area */
  .editor-area {{
    flex: 1; display: flex; justify-content: center; overflow-y: auto; padding: 2rem 1.5rem;
    gap: 1.5rem; position: relative;
  }}
  .editor-container {{ width: 100%; max-width: 760px; display: flex; flex-direction: column; }}
  textarea.zen-editor {{
    width: 100%; flex: 1; min-height: 82vh; background: transparent; color: var(--text);
    border: none; outline: none; resize: none; font-family: inherit; font-size: 1.18rem;
    line-height: 1.85; padding: 0; margin: 0;
  }}

  /* Preview Pane */
  .preview-pane {{
    width: 460px; max-width: 48%; background: var(--panel); border: 1px solid var(--border);
    border-radius: 8px; padding: 1.25rem; overflow-y: auto; font-family: system-ui, -apple-system, sans-serif;
    display: none; font-size: 0.95rem; line-height: 1.6; flex-shrink: 0;
  }}
  .scene-badge {{
    display: inline-flex; align-items: center; background: rgba(56, 189, 248, 0.1); border: 1px solid var(--accent);
    padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; color: var(--accent); margin: 0.2rem 0.2rem 0.2rem 0;
  }}
  .badge-tag {{ font-weight: bold; margin-right: 4px; }}
  .scene-break {{ border: 0; height: 1px; background: var(--border); margin: 1.5rem 0; }}

  /* Metadata Form Fields */
  .meta-field {{ display: flex; flex-direction: column; gap: 0.3rem; }}
  .meta-field label {{ font-size: 0.75rem; font-weight: 600; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; }}
  .meta-field input, .meta-field select, .meta-field textarea {{
    padding: 0.4rem 0.6rem; border-radius: 5px; outline: none; width: 100%;
    border: 1px solid var(--border); background: var(--bg); color: var(--text); font-size: 0.85rem;
  }}
  .meta-field input:focus, .meta-field select:focus, .meta-field textarea:focus {{
    border-color: var(--accent);
  }}
  .meta-sync-badge {{
    display: flex; align-items: center; gap: 0.4rem; font-size: 0.75rem; color: var(--emerald);
    padding: 0.35rem 0.6rem; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.25);
    border-radius: 4px;
  }}
  .sync-pulse {{ width: 6px; height: 6px; border-radius: 50%; background: var(--emerald); animation: pulseDot 2s infinite; }}
  @keyframes pulseDot {{ 0%, 100% {{ opacity: 1; transform: scale(1); }} 50% {{ opacity: 0.4; transform: scale(1.2); }} }}

  .progress-wrap {{ display: flex; flex-direction: column; gap: 0.25rem; }}
  .progress-bar-bg {{ height: 6px; background: var(--bg); border: 1px solid var(--border); border-radius: 3px; overflow: hidden; }}
  .progress-bar-fill {{ height: 100%; width: 0%; background: linear-gradient(90deg, var(--accent), var(--emerald)); transition: width 0.3s ease; }}

  /* Outline Tabs & Containers */
  .outline-tabs {{ display: flex; border-bottom: 1px solid var(--border); background: var(--panel-alt); flex-shrink: 0; }}
  .o-tab {{
    flex: 1; padding: 0.5rem 0.3rem; background: transparent; border: none; color: var(--muted);
    font-size: 0.8rem; cursor: pointer; text-align: center; border-bottom: 2px solid transparent; border-radius: 0;
  }}
  .o-tab.active {{ color: var(--accent); font-weight: 600; border-bottom-color: var(--accent); background: var(--panel); }}

  .outline-card {{
    background: var(--bg); border: 1px solid var(--border); border-radius: 6px;
    padding: 0.75rem; font-size: 0.85rem; line-height: 1.45;
  }}
  .outline-card-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem; }}
  .outline-card-title {{ font-weight: 600; color: var(--gold); font-size: 0.85rem; }}

  /* Lore Drawer */
  .lore-drawer {{
    width: 360px; background: var(--panel); border-left: 1px solid var(--border);
    display: none; flex-direction: column; font-family: system-ui, -apple-system, sans-serif; flex-shrink: 0;
  }}
  .lore-drawer.open {{ display: flex; }}
  .drawer-tabs {{ display: flex; border-bottom: 1px solid var(--border); background: var(--panel-alt); }}
  .d-tab {{
    flex: 1; padding: 0.5rem 0.2rem; background: transparent; border: none; color: var(--muted);
    font-size: 0.8rem; cursor: pointer; border-bottom: 2px solid transparent; border-radius: 0;
  }}
  .d-tab.active {{ color: var(--accent); font-weight: 600; border-bottom-color: var(--accent); background: var(--panel); }}
  .lore-search {{ padding: 0.65rem; border-bottom: 1px solid var(--border); }}
  .lore-search input {{ width: 100%; padding: 0.35rem 0.6rem; border-radius: 4px; outline: none; }}
  .lore-list {{ flex: 1; overflow-y: auto; padding: 0.75rem; display: flex; flex-direction: column; gap: 0.6rem; }}
  .lore-card {{
    background: var(--bg); border: 1px solid var(--border); border-radius: 6px;
    padding: 0.65rem 0.75rem; font-size: 0.85rem;
  }}

  /* Modals */
  .craft-modal {{
    display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(0,0,0,0.85); z-index: 1000; justify-content: center; align-items: center;
    font-family: system-ui, -apple-system, sans-serif;
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

  /* Footer Telemetry */
  footer.telemetry {{
    background: var(--panel); border-top: 1px solid var(--border);
    padding: 0.35rem 1.25rem; display: flex; justify-content: space-between; align-items: center;
    font-family: system-ui, -apple-system, sans-serif; font-size: 0.8rem; color: var(--muted); flex-shrink: 0;
  }}
</style>
</head>
<body data-theme="slate" data-font="serif">

<header role="banner">
  <div class="brand-title">
    🏛️ Ars Arcanum Zen Studio <span id="hdrDocTitle" style="color:var(--text);font-weight:400;" aria-live="polite">—</span>
  </div>
  <div class="controls" role="toolbar" aria-label="Editor controls and studio panels">
    <select id="themeSelect" onchange="switchTheme(this.value)" title="Color Themes" aria-label="Color Themes">
      <option value="slate">Classic Slate</option>
      <option value="parchment">Parchment Classical</option>
      <option value="nordic">Nordic Snow</option>
      <option value="solarized">Solarized Dark</option>
      <option value="gruvbox">Gruvbox Warmth</option>
      <option value="amber">Cyberpunk Amber</option>
    </select>
    <select id="fontSelect" onchange="switchFont(this.value)" title="Typography & Accessibility Font" aria-label="Typography Font Style">
      <option value="serif">Literary Serif</option>
      <option value="sans">Modern Sans</option>
      <option value="dyslexic">Dyslexia-Friendly</option>
      <option value="mono">Monospace Focus</option>
    </select>
    <button id="btnSound" onclick="toggleTypewriterSound()" title="Typewriter Mechanical Soundscape" aria-label="Toggle Typewriter Sound">🔇 Sound: OFF</button>
    <button id="btnSidebar" onclick="toggleSidebar()" title="Toggle Chapters Sidebar (Ctrl+B)" aria-label="Toggle Chapters Sidebar">📁 Files</button>
    <button id="btnMeta" onclick="toggleMetaPanel()" title="Toggle Document Metadata Inspector (Ctrl+M)" aria-label="Toggle Document Metadata Inspector">📋 Metadata</button>
    <button id="btnOutline" onclick="toggleOutlinePanel()" title="Toggle Multi-Tier Outline Drawer (Ctrl+O)" aria-label="Toggle Multi-Tier Outline Drawer">🗺️ Outline</button>
    <button id="btnPreview" onclick="toggleSplitPreview()" title="Live Scene Tag & Markdown Inspector (Ctrl+P)" aria-label="Toggle Live Markdown Preview">👁️ Preview: Off</button>
    <button id="btnLore" onclick="toggleLoreDrawer()" title="World Lore Drawer (Ctrl+L)" aria-label="Toggle World Lore Drawer">📜 Lore ({lore_entities_count})</button>
    <button class="btn-gold" onclick="openCraftModal()" aria-label="Open Craft Engine Encyclopedia">💡 Craft Logic</button>
    <button class="btn-accent" onclick="exportMarkdown()" title="Export Active Chapter Markdown (Ctrl+S)" aria-label="Export Markdown File">💾 Download</button>
  </div>
</header>

<main class="main-workspace" role="main">
  <!-- Left Column: Chapters Sidebar -->
  <aside class="sidebar" id="sidebar" role="region" aria-label="Manuscript Chapters">
    <div class="side-panel-header">
      <span class="panel-title-text">Manuscript Chapters</span>
      <div class="panel-header-actions">
        <button class="btn-tool-action" onclick="toggleSidebar()" title="Close Sidebar" aria-label="Close Chapters Sidebar">✕</button>
      </div>
    </div>
    <ul class="chap-list" id="chapList" role="listbox" aria-label="Chapter List"></ul>
  </aside>

  <!-- In-Situ Document Metadata Inspector Side Panel -->
  <aside class="side-panel" id="metaPanel" role="region" aria-label="Document Metadata Inspector">
    <div class="side-panel-header">
      <div style="display:flex;align-items:center;gap:0.4rem;">
        <span>📋</span>
        <span class="panel-title-text">Document Metadata</span>
      </div>
      <div class="panel-header-actions">
        <button class="btn-tool-action" id="btnMetaExpand" onclick="togglePanelExpand('metaPanel')" title="Toggle Width (Compact / Wide)" aria-label="Toggle Metadata Panel Width">🗗</button>
        <button class="btn-tool-action" id="btnMetaCollapse" onclick="togglePanelCollapse('metaPanel')" title="Collapse Panel" aria-label="Collapse Metadata Panel">▾</button>
        <button class="btn-tool-action" onclick="closePanel('metaPanel')" title="Close Metadata Inspector" aria-label="Close Metadata Panel">✕</button>
      </div>
    </div>

    <div class="side-panel-body" id="metaPanelBody">
      <div class="meta-sync-badge" aria-live="polite">
        <span class="sync-pulse"></span>
        <span>Real-time frontmatter 2-way sync active</span>
      </div>

      <div class="meta-field">
        <label for="metaTitle">Scene / Chapter Title</label>
        <input type="text" id="metaTitle" placeholder="Title of active scene..." oninput="handleMetadataInput('title', this.value)">
      </div>

      <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem;">
        <div class="meta-field">
          <label for="metaPov">POV Character (@pov)</label>
          <input type="text" id="metaPov" placeholder="Primary POV..." oninput="handleMetadataInput('pov', this.value)">
        </div>
        <div class="meta-field">
          <label for="metaStatus">Drafting Status</label>
          <select id="metaStatus" onchange="handleMetadataInput('status', this.value)">
            <option value="Draft">Draft</option>
            <option value="Revision">Revision</option>
            <option value="First Polish">First Polish</option>
            <option value="Final">Final</option>
          </select>
        </div>
      </div>

      <div class="meta-field">
        <label for="metaLocation">Setting / Location (@location)</label>
        <input type="text" id="metaLocation" placeholder="Specific scene locale..." oninput="handleMetadataInput('location', this.value)">
      </div>

      <div class="meta-field">
        <label for="metaCast">Cast Present in Scene (@char)</label>
        <input type="text" id="metaCast" placeholder="Characters present (comma separated)..." oninput="handleMetadataInput('characters', this.value)">
      </div>

      <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem;">
        <div class="meta-field">
          <label for="metaThread">Plot Thread (@thread)</label>
          <input type="text" id="metaThread" placeholder="A-Plot, B-Plot..." oninput="handleMetadataInput('plot_thread', this.value)">
        </div>
        <div class="meta-field">
          <label for="metaTime">Timeline / Day (@time)</label>
          <input type="text" id="metaTime" placeholder="Day 14 - Dusk..." oninput="handleMetadataInput('time_marker', this.value)">
        </div>
      </div>

      <div class="meta-field">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <label for="metaTargetWords">Target Words</label>
          <span id="metaTargetProgressLabel" style="font-size:0.75rem;color:var(--accent);" aria-live="polite">0 / 2,500 w (0%)</span>
        </div>
        <input type="number" id="metaTargetWords" min="100" step="100" value="2500" oninput="handleMetadataInput('target_words', parseInt(this.value)||2500)">
        <div class="progress-wrap" style="margin-top:0.25rem;">
          <div class="progress-bar-bg">
            <div class="progress-bar-fill" id="metaWordProgressBar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"></div>
          </div>
        </div>
      </div>

      <div class="meta-field">
        <label for="metaSynopsis">Scene Synopsis & Intent</label>
        <textarea id="metaSynopsis" rows="3" placeholder="Brief scene objective, conflict, and key turning point..." oninput="handleMetadataInput('synopsis', this.value)"></textarea>
      </div>

      <div class="meta-field">
        <label for="metaTags">Tags & Categories</label>
        <input type="text" id="metaTags" placeholder="climax, magic-duel, politics..." oninput="handleMetadataInput('tags', this.value)">
      </div>

      <div style="display:flex;gap:0.5rem;margin-top:0.25rem;">
        <button onclick="refreshMetadataFromEditor()" style="flex:1;font-size:0.75rem;" aria-label="Refresh metadata from markdown editor">🔄 Refresh from Doc</button>
        <button onclick="formatDocumentFrontmatter()" style="flex:1;font-size:0.75rem;" aria-label="Clean and format document frontmatter">🧹 Clean Header</button>
      </div>
    </div>
  </aside>

  <!-- Center Drafting Canvas Area -->
  <div class="editor-area">
    <div class="editor-container">
      <textarea class="zen-editor" id="editor" placeholder="Write your prose here..." oninput="handleEditorInput()" onkeydown="handleKeyDown(event)" aria-label="Manuscript Prose Drafting Editor"></textarea>
    </div>
    <div class="preview-pane" id="previewPane" role="region" aria-label="Live Markdown & Scene Tag Preview">
      <div style="font-weight:600;color:var(--accent);margin-bottom:0.75rem;border-bottom:1px solid var(--border);padding-bottom:0.4rem;display:flex;justify-content:space-between;">
        <span>🔍 Live Markdown & Scene Tag Inspector</span>
        <button class="btn-tool-action" onclick="toggleSplitPreview()" aria-label="Close Markdown Preview">✕</button>
      </div>
      <div id="previewContent" aria-live="polite"></div>
    </div>
  </div>

  <!-- Multi-Tier Narrative Outline Drawer -->
  <aside class="side-panel right-dock" id="outlinePanel" role="region" aria-label="Narrative Outlines">
    <div class="side-panel-header">
      <div style="display:flex;align-items:center;gap:0.4rem;">
        <span>🗺️</span>
        <span class="panel-title-text">Narrative Outlines</span>
      </div>
      <div class="panel-header-actions">
        <button class="btn-tool-action" id="btnOutlineExpand" onclick="togglePanelExpand('outlinePanel')" title="Toggle Width (Compact / Wide)" aria-label="Toggle Outline Panel Width">🗗</button>
        <button class="btn-tool-action" id="btnOutlineCollapse" onclick="togglePanelCollapse('outlinePanel')" title="Collapse Panel" aria-label="Collapse Outline Panel">▾</button>
        <button class="btn-tool-action" onclick="closePanel('outlinePanel')" title="Close Outline Drawer" aria-label="Close Outline Drawer">✕</button>
      </div>
    </div>

    <div class="outline-tabs" role="tablist" aria-label="Outline Levels">
      <button class="o-tab active" id="tabBtnFloating" role="tab" aria-selected="true" aria-controls="paneFloatingOutline" onclick="switchOutlineTab('floating')">📝 Floating</button>
      <button class="o-tab" id="tabBtnBook" role="tab" aria-selected="false" aria-controls="paneBookOutline" onclick="switchOutlineTab('book')">📖 Book</button>
      <button class="o-tab" id="tabBtnSeries" role="tab" aria-selected="false" aria-controls="paneSeriesOutline" onclick="switchOutlineTab('series')">🌌 Series</button>
    </div>

    <div class="side-panel-body" id="outlinePanelBody">
      <!-- Tier 1: Floating Scratchpad Outline -->
      <div id="paneFloatingOutline" role="tabpanel" aria-labelledby="tabBtnFloating" style="display:flex;flex-direction:column;gap:0.75rem;flex:1;">
        <div style="display:flex;gap:0.5rem;align-items:center;">
          <select id="floatingTemplateSelect" style="flex:1;font-size:0.8rem;" aria-label="Beat Template Selector">
            <!-- Populated dynamically -->
          </select>
          <button onclick="applyFloatingTemplate()" title="Load selected beat template" style="font-size:0.8rem;" aria-label="Load selected beat template">📋 Load</button>
        </div>

        <textarea id="floatingOutlineText" style="flex:1;min-height:220px;padding:0.6rem;font-family:system-ui,sans-serif;font-size:0.85rem;line-height:1.5;resize:vertical;" placeholder="Jot down active scene beats, checklist points, and scratchpad notes..." oninput="handleFloatingOutlineChange(this.value)" aria-label="Floating Scratchpad Outline Notes"></textarea>

        <div style="display:flex;gap:0.5rem;">
          <button class="btn-accent" onclick="insertFloatingBeatToEditor()" style="flex:1;font-size:0.8rem;" title="Insert scratchpad beats at current prose cursor position" aria-label="Insert scratchpad beats at cursor position">➕ Insert into Draft</button>
          <button onclick="clearFloatingOutline()" style="font-size:0.8rem;" aria-label="Clear scratchpad outline">🗑️ Clear</button>
        </div>
      </div>

      <!-- Tier 2: Book Master Outline -->
      <div id="paneBookOutline" role="tabpanel" aria-labelledby="tabBtnBook" style="display:none;flex-direction:column;gap:0.75rem;">
        <div class="lore-search" style="padding:0;border:none;">
          <input type="text" id="bookOutlineQuery" placeholder="Search book acts, milestones, beats..." oninput="filterBookOutline(this.value)" aria-label="Search book outline">
        </div>
        <div id="bookOutlineContent" style="display:flex;flex-direction:column;gap:0.6rem;"></div>
      </div>

      <!-- Tier 3: Series Universe Outline -->
      <div id="paneSeriesOutline" role="tabpanel" aria-labelledby="tabBtnSeries" style="display:none;flex-direction:column;gap:0.75rem;">
        <div class="lore-search" style="padding:0;border:none;">
          <input type="text" id="seriesOutlineQuery" placeholder="Search series volumes, arcs, reveals..." oninput="filterSeriesOutline(this.value)" aria-label="Search series universe chronicle">
        </div>
        <div id="seriesOutlineContent" style="display:flex;flex-direction:column;gap:0.6rem;"></div>
      </div>
    </div>
  </aside>

  <!-- Right Lore Drawer -->
  <aside class="lore-drawer" id="loreDrawer" role="region" aria-label="World Bible Lore Drawer">
    <div class="side-panel-header">
      <div style="display:flex;align-items:center;gap:0.4rem;">
        <span>📜</span>
        <span>World Bible Lore</span>
      </div>
      <div class="panel-header-actions">
        <button class="btn-tool-action" onclick="toggleLoreDrawer()" title="Close Lore Drawer" aria-label="Close Lore Drawer">✕</button>
      </div>
    </div>
    <div class="drawer-tabs" role="tablist" aria-label="Lore Categories">
      <button class="d-tab active" id="tabBtnLore" role="tab" aria-selected="true" aria-controls="loreList" onclick="switchDrawerTab('lore')">📜 Lore</button>
      <button class="d-tab" id="tabBtnRules" role="tab" aria-selected="false" aria-controls="loreList" onclick="switchDrawerTab('rules')">📐 Rules</button>
      <button class="d-tab" id="tabBtnSparks" role="tab" aria-selected="false" aria-controls="loreList" onclick="switchDrawerTab('sparks')">💡 Sparks</button>
      <button class="d-tab" id="tabBtnTips" role="tab" aria-selected="false" aria-controls="loreList" onclick="switchDrawerTab('tips')">💡 Tips</button>
    </div>
    <div class="lore-search">
      <input type="text" id="loreQuery" placeholder="Search characters, locations, rules, tips..." oninput="filterDrawer(this.value)" aria-label="Search World Lore">
    </div>
    <div class="lore-list" id="loreList" role="region" aria-live="polite"></div>
  </aside>
</main>

<!-- Telemetry Footer -->
<footer class="telemetry" role="contentinfo" aria-label="Live Writing Telemetry and Craft Tips">
  <div aria-live="polite">
    <span id="telWords">0 words</span> | <span id="telChars">0 chars</span>
  </div>
  <div id="zenTipBar" style="color:var(--gold);cursor:pointer;max-width:520px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;" onclick="cycleZenTip()" title="Click for next craft wisdom tip" aria-live="polite">
    💡 <span id="zenTipText">Loading craft wisdom...</span>
  </div>
  <div aria-live="polite">
    📖 Reading: <span id="telReadTime">0 min</span> | 🎙️ Narration: <span id="telSpeakTime">0 min</span> | <span id="telSaveStatus">Autosaved</span>
  </div>
</footer>

<!-- Craft Engine Modal -->
<div class="craft-modal" id="craftModal" role="dialog" aria-modal="true" aria-labelledby="craftModalTitle" onclick="if(event.target===this)closeCraftModal()">
  <div class="craft-modal-content" role="document">
    <div class="craft-modal-header">
      <div>
        <span id="craftModalTitle" style="font-weight:700;font-size:1.1rem;color:var(--accent);">💡 Ars Arcanum Craft & Engine Encyclopedia</span>
        <div style="font-size:0.8rem;color:var(--muted);margin-top:2px;">50 Verified Engines • Mathematical Logic • Narrative Physics • Extension Guides</div>
      </div>
      <button onclick="closeCraftModal()" style="font-size:1.2rem;line-height:1;background:transparent;border:none;color:var(--muted);cursor:pointer;" aria-label="Close Craft Modal">✕</button>
    </div>
    <div class="lore-search" style="background:var(--panel-alt);padding:0.75rem 1.5rem;">
      <input type="text" id="modalEngineSearch" placeholder="Search any engine, formula, or craft principle..." oninput="filterModalEngines(this.value)" aria-label="Search craft engines">
    </div>
    <div class="craft-modal-body" id="modalEngineList" role="region" aria-live="polite"></div>
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
  const outlinesData = {outlines_json};
  const catalog = {catalog_json};
  const sparks = {sparks_json};
  const tips = {tips_json};
  let tipsEnabled = {tips_enabled_val};
  let currentChapIdx = 0;
  let activeDrawerTab = "lore";
  let activeOutlineTab = "floating";
  let currentZenTipIdx = 0;
  let audioCtx = null;
  let soundEnabled = false;
  let previewEnabled = false;
  let isFrontmatterSyncing = false;

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
    const savedFont = localStorage.getItem("arcanum_zen_font") || "serif";
    switchFont(savedFont);
    renderChapList();
    if (chapters.length > 0) {{
      loadChapter(0);
    }}
    renderDrawer();
    initOutlines();
    renderModalEngines(catalog);
    initZenTip();
    loadUIState();
  }}

  /* ---------------- Theme, Font & Sound ---------------- */
  function switchTheme(theme) {{
    document.body.setAttribute("data-theme", theme);
    const select = document.getElementById("themeSelect");
    if (select) select.value = theme;
    localStorage.setItem("arcanum_zen_theme", theme);
  }}

  function switchFont(fontName) {{
    document.body.setAttribute("data-font", fontName);
    const select = document.getElementById("fontSelect");
    if (select) select.value = fontName;
    localStorage.setItem("arcanum_zen_font", fontName);
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
    }} catch (e) {{}}
  }}

  /* ---------------- UI Panels & Ergonomics ---------------- */
  function toggleSidebar() {{
    const sb = document.getElementById("sidebar");
    const btn = document.getElementById("btnSidebar");
    const isOpen = sb.style.display !== "none";
    sb.style.display = isOpen ? "none" : "flex";
    if (btn) btn.classList.toggle("active", !isOpen);
    saveUIState();
  }}

  function toggleMetaPanel() {{
    const panel = document.getElementById("metaPanel");
    const btn = document.getElementById("btnMeta");
    panel.classList.toggle("open");
    const isOpen = panel.classList.contains("open");
    if (btn) btn.classList.toggle("active", isOpen);
    saveUIState();
  }}

  function toggleOutlinePanel() {{
    const panel = document.getElementById("outlinePanel");
    const btn = document.getElementById("btnOutline");
    panel.classList.toggle("open");
    const isOpen = panel.classList.contains("open");
    if (btn) btn.classList.toggle("active", isOpen);
    saveUIState();
  }}

  function toggleLoreDrawer() {{
    const drawer = document.getElementById("loreDrawer");
    const btn = document.getElementById("btnLore");
    drawer.classList.toggle("open");
    const isOpen = drawer.classList.contains("open");
    if (btn) btn.classList.toggle("active", isOpen);
    saveUIState();
  }}

  function toggleSplitPreview() {{
    previewEnabled = !previewEnabled;
    const pane = document.getElementById("previewPane");
    const btn = document.getElementById("btnPreview");
    if (pane) pane.style.display = previewEnabled ? "block" : "none";
    if (btn) {{
      btn.textContent = previewEnabled ? "👁️ Preview: ON" : "👁️ Preview: OFF";
      btn.classList.toggle("active", previewEnabled);
    }}
    if (previewEnabled) renderSplitPreview();
    saveUIState();
  }}

  function togglePanelExpand(panelId) {{
    const panel = document.getElementById(panelId);
    if (!panel) return;
    panel.classList.toggle("expanded");
    const isExp = panel.classList.contains("expanded");
    const btn = document.getElementById(panelId === "metaPanel" ? "btnMetaExpand" : "btnOutlineExpand");
    if (btn) btn.textContent = isExp ? "🗗" : "⛶";
    saveUIState();
  }}

  function togglePanelCollapse(panelId) {{
    const panel = document.getElementById(panelId);
    if (!panel) return;
    panel.classList.toggle("collapsed");
    const isCol = panel.classList.contains("collapsed");
    const btn = document.getElementById(panelId === "metaPanel" ? "btnMetaCollapse" : "btnOutlineCollapse");
    if (btn) btn.textContent = isCol ? "▸" : "▾";
    saveUIState();
  }}

  function closePanel(panelId) {{
    const panel = document.getElementById(panelId);
    if (!panel) return;
    panel.classList.remove("open");
    const btn = document.getElementById(panelId === "metaPanel" ? "btnMeta" : (panelId === "outlinePanel" ? "btnOutline" : ""));
    if (btn) btn.classList.remove("active");
    saveUIState();
  }}

  function saveUIState() {{
    const state = {{
      sidebar: document.getElementById("sidebar").style.display !== "none",
      metaOpen: document.getElementById("metaPanel").classList.contains("open"),
      metaExpanded: document.getElementById("metaPanel").classList.contains("expanded"),
      metaCollapsed: document.getElementById("metaPanel").classList.contains("collapsed"),
      outlineOpen: document.getElementById("outlinePanel").classList.contains("open"),
      outlineExpanded: document.getElementById("outlinePanel").classList.contains("expanded"),
      outlineCollapsed: document.getElementById("outlinePanel").classList.contains("collapsed"),
      loreOpen: document.getElementById("loreDrawer").classList.contains("open"),
      previewOpen: previewEnabled,
      activeOutlineTab: activeOutlineTab,
    }};
    localStorage.setItem("arcanum_zen_ui_state", JSON.stringify(state));
  }}

  function loadUIState() {{
    const raw = localStorage.getItem("arcanum_zen_ui_state");
    if (!raw) return;
    try {{
      const state = JSON.parse(raw);
      if (state.sidebar === false) {{
        document.getElementById("sidebar").style.display = "none";
        const btn = document.getElementById("btnSidebar");
        if (btn) btn.classList.remove("active");
      }} else {{
        const btn = document.getElementById("btnSidebar");
        if (btn) btn.classList.add("active");
      }}
      if (state.metaOpen) {{
        document.getElementById("metaPanel").classList.add("open");
        const btn = document.getElementById("btnMeta");
        if (btn) btn.classList.add("active");
      }}
      if (state.metaExpanded) document.getElementById("metaPanel").classList.add("expanded");
      if (state.metaCollapsed) {{
        document.getElementById("metaPanel").classList.add("collapsed");
        const btn = document.getElementById("btnMetaCollapse");
        if (btn) btn.textContent = "▸";
      }}
      if (state.outlineOpen) {{
        document.getElementById("outlinePanel").classList.add("open");
        const btn = document.getElementById("btnOutline");
        if (btn) btn.classList.add("active");
      }}
      if (state.outlineExpanded) document.getElementById("outlinePanel").classList.add("expanded");
      if (state.outlineCollapsed) {{
        document.getElementById("outlinePanel").classList.add("collapsed");
        const btn = document.getElementById("btnOutlineCollapse");
        if (btn) btn.textContent = "▸";
      }}
      if (state.loreOpen) {{
        document.getElementById("loreDrawer").classList.add("open");
        const btn = document.getElementById("btnLore");
        if (btn) btn.classList.add("active");
      }}
      if (state.previewOpen) toggleSplitPreview();
      if (state.activeOutlineTab) switchOutlineTab(state.activeOutlineTab);
    }} catch (e) {{}}
  }}

  /* ---------------- Chapter & Editor Management ---------------- */
  function renderChapList() {{
    const list = document.getElementById("chapList");
    list.innerHTML = "";
    chapters.forEach((c, idx) => {{
      const li = document.createElement("li");
      li.className = `chap-item ${{idx === currentChapIdx ? "active" : ""}}`;
      li.innerHTML = `<strong>${{escapeHtml(c.title)}}</strong><br><small style="color:var(--muted);">${{c.word_count || 0}} words • ${{escapeHtml(c.metadata?.status || 'Draft')}}</small>`;
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
    const docText = saved !== null ? saved : chap.content;
    document.getElementById("editor").value = docText;

    populateMetadataPanel(chap);
    loadFloatingOutlineForChapter(chap.id);
    renderChapList();
    updateTelemetry();
    if (previewEnabled) renderSplitPreview();
  }}

  /* ---------------- Document Metadata Real-Time Two-Way Sync ---------------- */
  function populateMetadataPanel(chap) {{
    if (!chap) return;
    const meta = chap.metadata || {{}};
    document.getElementById("metaTitle").value = meta.title || chap.title || "";
    document.getElementById("metaPov").value = meta.pov || "";
    document.getElementById("metaLocation").value = meta.location || "";
    document.getElementById("metaCast").value = meta.cast || "";
    document.getElementById("metaThread").value = meta.thread || "";
    document.getElementById("metaTime").value = meta.time || "";
    document.getElementById("metaStatus").value = meta.status || "Draft";
    document.getElementById("metaTargetWords").value = meta.target_words || 2500;
    document.getElementById("metaSynopsis").value = meta.synopsis || "";
    document.getElementById("metaTags").value = meta.tags || "";
    updateTargetWordProgress();
  }}

  function updateTargetWordProgress() {{
    const editor = document.getElementById("editor");
    const text = editor ? editor.value : "";
    const cleanBody = text.replace(/^---[\\s\\S]*?---\\s*/, "");
    const words = (cleanBody.match(/\\b\\w+\\b/g) || []).length;
    const target = parseInt(document.getElementById("metaTargetWords").value) || 2500;
    const pct = Math.min(100, Math.round((words / target) * 100));

    const lbl = document.getElementById("metaTargetProgressLabel");
    if (lbl) lbl.textContent = `${{words.toLocaleString()}} / ${{target.toLocaleString()}} w (${{pct}}%)`;
    const bar = document.getElementById("metaWordProgressBar");
    if (bar) bar.style.width = `${{pct}}%`;
  }}

  function handleMetadataInput(field, value) {{
    const chap = chapters[currentChapIdx];
    if (!chap) return;
    if (!chap.metadata) chap.metadata = {{}};
    chap.metadata[field] = value;

    if (field === "title") {{
      chap.title = value;
      document.getElementById("hdrDocTitle").textContent = value;
      renderChapList();
    }}

    updateTargetWordProgress();
    syncFrontmatterToEditor();
  }}

  function syncFrontmatterToEditor() {{
    if (isFrontmatterSyncing) return;
    isFrontmatterSyncing = true;
    try {{
      const editor = document.getElementById("editor");
      if (!editor) return;
      const text = editor.value;
      const chap = chapters[currentChapIdx];
      const meta = chap ? chap.metadata : {{}};

      const match = text.match(/^---\\s*\\r?\\n([\\s\\S]*?)\\r?\\n---\\s*(?:\\r?\\n|$)/);
      let existingFm = {{}};
      let bodyText = text;

      if (match) {{
        existingFm = parseSimpleYaml(match[1]);
        bodyText = text.substring(match[0].length);
      }}

      // Merge updated metadata
      if (meta.title) existingFm["title"] = meta.title;
      if (meta.pov) existingFm["pov"] = meta.pov;
      if (meta.location) existingFm["location"] = meta.location;
      if (meta.cast) existingFm["characters"] = meta.cast.includes(",") ? meta.cast.split(",").map(s => s.trim()).filter(Boolean) : meta.cast;
      if (meta.thread) existingFm["plot_thread"] = meta.thread;
      if (meta.time) existingFm["time_marker"] = meta.time;
      if (meta.status) existingFm["status"] = meta.status;
      if (meta.target_words) existingFm["target_words"] = parseInt(meta.target_words);
      if (meta.synopsis) existingFm["synopsis"] = meta.synopsis;
      if (meta.tags) existingFm["tags"] = meta.tags.includes(",") ? meta.tags.split(",").map(s => s.trim()).filter(Boolean) : meta.tags;

      const newFmString = serializeYaml(existingFm);
      const newDocText = `---\\n${{newFmString}}---\\n\\n${{bodyText.replace(/^\\n+/, "")}}`;

      const start = editor.selectionStart;
      const end = editor.selectionEnd;
      const scroll = editor.scrollTop;

      editor.value = newDocText;
      editor.selectionStart = start;
      editor.selectionEnd = end;
      editor.scrollTop = scroll;

      updateTelemetry();
    }} finally {{
      isFrontmatterSyncing = false;
    }}
  }}

  function refreshMetadataFromEditor() {{
    syncMetadataFromEditorText();
  }}

  function formatDocumentFrontmatter() {{
    syncFrontmatterToEditor();
  }}

  function syncMetadataFromEditorText() {{
    if (isFrontmatterSyncing) return;
    const editor = document.getElementById("editor");
    if (!editor) return;
    const text = editor.value;
    const match = text.match(/^---\\s*\\r?\\n([\\s\\S]*?)\\r?\\n---\\s*(?:\\r?\\n|$)/);
    if (!match) return;

    const parsed = parseSimpleYaml(match[1]);
    const chap = chapters[currentChapIdx];
    if (!chap) return;
    if (!chap.metadata) chap.metadata = {{}};

    if (parsed.title) {{
      chap.title = parsed.title;
      chap.metadata.title = parsed.title;
      document.getElementById("metaTitle").value = parsed.title;
      document.getElementById("hdrDocTitle").textContent = parsed.title;
    }}
    if (parsed.pov || parsed.pov_character) {{
      chap.metadata.pov = parsed.pov || parsed.pov_character;
      document.getElementById("metaPov").value = chap.metadata.pov;
    }}
    if (parsed.location || parsed.setting) {{
      chap.metadata.location = parsed.location || parsed.setting;
      document.getElementById("metaLocation").value = chap.metadata.location;
    }}
    if (parsed.characters || parsed.cast || parsed.char) {{
      const cVal = parsed.characters || parsed.cast || parsed.char;
      chap.metadata.cast = Array.isArray(cVal) ? cVal.join(", ") : String(cVal);
      document.getElementById("metaCast").value = chap.metadata.cast;
    }}
    if (parsed.plot_thread || parsed.thread) {{
      chap.metadata.thread = parsed.plot_thread || parsed.thread;
      document.getElementById("metaThread").value = chap.metadata.thread;
    }}
    if (parsed.time_marker || parsed.time || parsed.timeline_day) {{
      chap.metadata.time = parsed.time_marker || parsed.time || parsed.timeline_day;
      document.getElementById("metaTime").value = chap.metadata.time;
    }}
    if (parsed.status) {{
      chap.metadata.status = parsed.status;
      document.getElementById("metaStatus").value = parsed.status;
    }}
    if (parsed.target_words || parsed.target_word_count) {{
      chap.metadata.target_words = parseInt(parsed.target_words || parsed.target_word_count) || 2500;
      document.getElementById("metaTargetWords").value = chap.metadata.target_words;
    }}
    if (parsed.synopsis || parsed.summary || parsed.notes) {{
      chap.metadata.synopsis = parsed.synopsis || parsed.summary || parsed.notes;
      document.getElementById("metaSynopsis").value = chap.metadata.synopsis;
    }}
    if (parsed.tags) {{
      chap.metadata.tags = Array.isArray(parsed.tags) ? parsed.tags.join(", ") : String(parsed.tags);
      document.getElementById("metaTags").value = chap.metadata.tags;
    }}
    renderChapList();
    updateTargetWordProgress();
  }}

  function parseSimpleYaml(str) {{
    const res = {{}};
    const lines = str.split("\\n");
    let currentKey = null;

    lines.forEach(l => {{
      const trimmed = l.trim();
      if (!trimmed || trimmed.startsWith("#")) return;
      if (trimmed.startsWith("- ") && currentKey) {{
        if (!Array.isArray(res[currentKey])) res[currentKey] = [];
        res[currentKey].push(trimmed.slice(2).trim().replace(/^["']|["']$/g, ""));
        return;
      }}
      const colonIdx = trimmed.indexOf(":");
      if (colonIdx > 0) {{
        const k = trimmed.substring(0, colonIdx).trim();
        const v = trimmed.substring(colonIdx + 1).trim().replace(/^["']|["']$/g, "");
        currentKey = k;
        if (v === "") {{
          res[k] = [];
        }} else if (v.startsWith("[") && v.endsWith("]")) {{
          res[k] = v.slice(1, -1).split(",").map(s => s.trim().replace(/^["']|["']$/g, ""));
        }} else if (!isNaN(v) && v !== "") {{
          res[k] = Number(v);
        }} else if (v.toLowerCase() === "true" || v.toLowerCase() === "false") {{
          res[k] = v.toLowerCase() === "true";
        }} else {{
          res[k] = v;
        }}
      }}
    }});
    return res;
  }}

  function serializeYaml(obj) {{
    let res = "";
    for (const [k, v] of Object.entries(obj)) {{
      if (v === null || v === undefined || v === "") continue;
      if (Array.isArray(v)) {{
        if (v.length === 0) continue;
        res += `${{k}}:\\n`;
        v.forEach(it => {{ res += `  - "${{String(it).replace(/"/g, '\\\\"')}}"\\n`; }});
      }} else if (typeof v === "number" || typeof v === "boolean") {{
        res += `${{k}}: ${{v}}\\n`;
      }} else if (String(v).includes("\\n")) {{
        res += `${{k}}: |\\n`;
        String(v).split("\\n").forEach(line => {{ res += `  ${{line}}\\n`; }});
      }} else {{
        res += `${{k}}: "${{String(v).replace(/"/g, '\\\\"')}}"\\n`;
      }}
    }}
    return res;
  }}

  /* ---------------- Multi-Tier Narrative Outlines ---------------- */
  function initOutlines() {{
    // Populate floating templates
    const select = document.getElementById("floatingTemplateSelect");
    select.innerHTML = "";
    (outlinesData.floating_templates || []).forEach(t => {{
      const opt = document.createElement("option");
      opt.value = t.id;
      opt.textContent = t.name;
      select.appendChild(opt);
    }});

    renderBookOutline();
    renderSeriesOutline();
  }}

  function switchOutlineTab(tab) {{
    activeOutlineTab = tab;
    const btnF = document.getElementById("tabBtnFloating");
    const btnB = document.getElementById("tabBtnBook");
    const btnS = document.getElementById("tabBtnSeries");
    if (btnF) {{
      btnF.className = `o-tab ${{tab === 'floating' ? 'active' : ''}}`;
      btnF.setAttribute("aria-selected", tab === 'floating' ? "true" : "false");
    }}
    if (btnB) {{
      btnB.className = `o-tab ${{tab === 'book' ? 'active' : ''}}`;
      btnB.setAttribute("aria-selected", tab === 'book' ? "true" : "false");
    }}
    if (btnS) {{
      btnS.className = `o-tab ${{tab === 'series' ? 'active' : ''}}`;
      btnS.setAttribute("aria-selected", tab === 'series' ? "true" : "false");
    }}

    document.getElementById("paneFloatingOutline").style.display = tab === 'floating' ? 'flex' : 'none';
    document.getElementById("paneBookOutline").style.display = tab === 'book' ? 'flex' : 'none';
    document.getElementById("paneSeriesOutline").style.display = tab === 'series' ? 'flex' : 'none';
    saveUIState();
  }}

  function loadFloatingOutlineForChapter(chapId) {{
    const saved = localStorage.getItem(`arcanum_zen_floating_${{chapId}}`);
    const txtArea = document.getElementById("floatingOutlineText");
    if (txtArea) {{
      txtArea.value = saved || "";
    }}
  }}

  function handleFloatingOutlineChange(val) {{
    const chap = chapters[currentChapIdx];
    if (chap) {{
      localStorage.setItem(`arcanum_zen_floating_${{chap.id}}`, val);
    }}
  }}

  function applyFloatingTemplate() {{
    const select = document.getElementById("floatingTemplateSelect");
    const tId = select ? select.value : "";
    const tmpl = (outlinesData.floating_templates || []).find(t => t.id === tId);
    if (!tmpl) return;

    const txtArea = document.getElementById("floatingOutlineText");
    if (txtArea) {{
      txtArea.value = (txtArea.value ? txtArea.value + "\\n\\n" : "") + tmpl.text;
      handleFloatingOutlineChange(txtArea.value);
    }}
  }}

  function clearFloatingOutline() {{
    const txtArea = document.getElementById("floatingOutlineText");
    if (txtArea) {{
      txtArea.value = "";
      handleFloatingOutlineChange("");
    }}
  }}

  function insertFloatingBeatToEditor() {{
    const txtArea = document.getElementById("floatingOutlineText");
    const beatText = txtArea ? txtArea.value.trim() : "";
    if (!beatText) return;

    const editor = document.getElementById("editor");
    if (!editor) return;

    const start = editor.selectionStart;
    const end = editor.selectionEnd;
    const prefix = editor.value.substring(0, start);
    const suffix = editor.value.substring(end);
    const insertBlock = `\\n\\n<!-- 🗺️ OUTLINE BEAT -->\\n${{beatText}}\\n<!-- END BEAT -->\\n\\n`;

    editor.value = prefix + insertBlock + suffix;
    editor.selectionStart = editor.selectionEnd = start + insertBlock.length;
    handleEditorInput();
  }}

  function renderBookOutline() {{
    const container = document.getElementById("bookOutlineContent");
    const raw = outlinesData.book_outline?.raw || "";
    const q = (document.getElementById("bookOutlineQuery")?.value || "").toLowerCase();

    container.innerHTML = "";
    const sections = raw.split(/^##\\s+/m).filter(Boolean);

    sections.forEach(sec => {{
      const lines = sec.split("\\n");
      const title = lines[0].trim();
      const body = lines.slice(1).join("\\n").trim();

      if (q && !title.toLowerCase().includes(q) && !body.toLowerCase().includes(q)) return;

      const card = document.createElement("div");
      card.className = "outline-card";

      let parsedBody = escapeHtml(body)
        .replace(/\\*\\*(.*?)\\*\\*/g, "<strong>$1</strong>")
        .replace(/\\*(.*?)\\*/g, "<em>$1</em>")
        .replace(/^-\\s+(.+)$/gm, "<li style='margin-left:1rem;'>$1</li>");

      card.innerHTML = `
        <div class="outline-card-header">
          <span class="outline-card-title">📖 ${{escapeHtml(title)}}</span>
        </div>
        <div style="font-size:0.8rem;color:var(--text);">${{parsedBody}}</div>
      `;
      container.appendChild(card);
    }});
  }}

  function filterBookOutline(q) {{
    renderBookOutline();
  }}

  function renderSeriesOutline() {{
    const container = document.getElementById("seriesOutlineContent");
    const raw = outlinesData.series_outline?.raw || "";
    const q = (document.getElementById("seriesOutlineQuery")?.value || "").toLowerCase();

    container.innerHTML = "";
    const sections = raw.split(/^###\\s+/m).filter(Boolean);

    sections.forEach(sec => {{
      const lines = sec.split("\\n");
      const title = lines[0].trim();
      const body = lines.slice(1).join("\\n").trim();

      if (q && !title.toLowerCase().includes(q) && !body.toLowerCase().includes(q)) return;

      const card = document.createElement("div");
      card.className = "outline-card";
      card.style.borderLeft = "3px solid var(--accent)";

      let parsedBody = escapeHtml(body)
        .replace(/\\*\\*(.*?)\\*\\*/g, "<strong>$1</strong>")
        .replace(/\\*(.*?)\\*/g, "<em>$1</em>")
        .replace(/^-\\s+(.+)$/gm, "<li style='margin-left:1rem;'>$1</li>");

      card.innerHTML = `
        <div class="outline-card-header">
          <span class="outline-card-title" style="color:var(--accent);">🌌 ${{escapeHtml(title)}}</span>
        </div>
        <div style="font-size:0.8rem;color:var(--text);">${{parsedBody}}</div>
      `;
      container.appendChild(card);
    }});
  }}

  function filterSeriesOutline(q) {{
    renderSeriesOutline();
  }}

  /* ---------------- Preview & Editor Keystrokes ---------------- */
  function renderSplitPreview() {{
    const text = document.getElementById("editor").value;
    const preview = document.getElementById("previewContent");
    if (!preview) return;

    const lines = text.split("\\n");
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

    if (inList) html += "</ul>";
    preview.innerHTML = html;
  }}

  function handleEditorInput() {{
    updateTelemetry();
    syncMetadataFromEditorText();
    if (previewEnabled) renderSplitPreview();
  }}

  function handleKeyDown(event) {{
    playTypewriterSound(event.key === "Enter");
    const isCtrl = event.ctrlKey || event.metaKey;

    if (event.key === "Tab") {{
      event.preventDefault();
      const editor = document.getElementById("editor");
      const start = editor.selectionStart;
      const end = editor.selectionEnd;
      editor.value = editor.value.substring(0, start) + "  " + editor.value.substring(end);
      editor.selectionStart = editor.selectionEnd = start + 2;
      handleEditorInput();
    }} else if (isCtrl && event.key.toLowerCase() === "s") {{
      event.preventDefault();
      updateTelemetry();
      flashSaveIndicator();
    }} else if (isCtrl && event.key.toLowerCase() === "m") {{
      event.preventDefault();
      toggleMetaPanel();
    }} else if (isCtrl && event.key.toLowerCase() === "o") {{
      event.preventDefault();
      toggleOutlinePanel();
    }} else if (isCtrl && event.key.toLowerCase() === "b") {{
      event.preventDefault();
      toggleSidebar();
    }} else if (isCtrl && event.key.toLowerCase() === "l") {{
      event.preventDefault();
      toggleLoreDrawer();
    }} else if (isCtrl && event.key.toLowerCase() === "p") {{
      event.preventDefault();
      toggleSplitPreview();
    }}
  }}

  function flashSaveIndicator() {{
    const el = document.getElementById("telSaveStatus");
    if (el) {{
      el.textContent = "💾 Saved to Local Storage!";
      el.style.color = "var(--emerald)";
      setTimeout(() => {{
        el.textContent = "Autosaved";
        el.style.color = "var(--muted)";
      }}, 1500);
    }}
  }}

  /* ---------------- Telemetry & Tips ---------------- */
  function updateTelemetry() {{
    const text = document.getElementById("editor").value;
    const cleanBody = text.replace(/^---[\\s\\S]*?---\\s*/, "");
    const words = (cleanBody.match(/\\b\\w+\\b/g) || []).length;
    const chars = cleanBody.length;
    const readMins = Math.ceil(words / 200);
    const speakMins = (words / 150).toFixed(1);

    document.getElementById("telWords").textContent = `${{words.toLocaleString()}} words`;
    document.getElementById("telChars").textContent = `${{chars.toLocaleString()}} chars`;
    document.getElementById("telReadTime").textContent = `${{readMins}} min`;
    document.getElementById("telSpeakTime").textContent = `${{speakMins}} min`;

    const chap = chapters[currentChapIdx];
    if (chap) {{
      chap.word_count = words;
      localStorage.setItem(`arcanum_zen_${{chap.id}}`, text);
    }}
    updateTargetWordProgress();
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

  /* ---------------- Lore Drawer & Engine Encyclopedia ---------------- */
  function switchDrawerTab(tab) {{
    activeDrawerTab = tab;
    ["lore", "rules", "sparks", "tips"].forEach(t => {{
      const btn = document.getElementById(`tabBtn${{t.charAt(0).toUpperCase() + t.slice(1)}}`);
      if (btn) {{
        btn.className = `d-tab ${{tab === t ? 'active' : ''}}`;
        btn.setAttribute("aria-selected", tab === t ? "true" : "false");
      }}
    }});
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

  function openCraftModal() {{
    const modal = document.getElementById("craftModal");
    if (modal) {{
      modal.style.display = "flex";
      const search = document.getElementById("modalEngineSearch");
      if (search) setTimeout(() => search.focus(), 50);
    }}
  }}

  function closeCraftModal() {{
    const modal = document.getElementById("craftModal");
    if (modal) {{
      modal.style.display = "none";
    }}
  }}

  window.addEventListener("keydown", (e) => {{
    if (e.key === "Escape") {{
      closeCraftModal();
    }}
  }});

  function renderModalEngines(items) {{
    const container = document.getElementById("modalEngineList");
    container.innerHTML = "";
    if (items.length === 0) {{
      container.innerHTML = `<div style="color:var(--muted);text-align:center;padding:2rem;">No matching craft engines found</div>`;
      return;
    }}
    items.forEach(spec => {{
      const card = document.createElement("div");
      card.style.background = "var(--panel)";
      card.style.border = "1px solid var(--border)";
      card.style.borderRadius = "8px";
      card.style.padding = "1rem 1.25rem";

      card.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;">
          <h3 style="margin:0;font-size:1.1rem;color:var(--accent);">${{escapeHtml(spec.name)}} <code style="font-size:0.8rem;color:var(--gold);margin-left:0.5rem;">arcanum ${{escapeHtml(spec.name)}}</code></h3>
          <span style="background:var(--bg);padding:2px 8px;border-radius:4px;font-size:0.75rem;color:var(--muted);">${{escapeHtml(spec.category)}}</span>
        </div>
        <p style="margin:0 0 0.75rem 0;color:var(--text);font-size:0.9rem;">${{escapeHtml(spec.description)}}</p>
        <div style="background:var(--panel-alt);border-left:3px solid var(--accent);padding:0.6rem 0.8rem;margin-bottom:0.75rem;font-size:0.85rem;color:#cbd5e1;white-space:pre-wrap;"><strong>📐 Science & Craft Logic:</strong>\\n${{escapeHtml(spec.scientific_logic || "Underlying logic defined in registry.")}}</div>
        <div style="background:var(--panel-alt);border-left:3px solid var(--gold);padding:0.6rem 0.8rem;margin-bottom:0.75rem;font-size:0.85rem;color:#cbd5e1;white-space:pre-wrap;"><strong>💡 Why This Way:</strong>\\n${{escapeHtml(spec.why_this_way || "Design rationale defined in registry.")}}</div>
        <div style="background:var(--panel-alt);border-left:3px solid var(--emerald);padding:0.6rem 0.8rem;font-size:0.85rem;color:#cbd5e1;white-space:pre-wrap;"><strong>🛠️ How to Extend:</strong>\\n${{escapeHtml(spec.extension_guide || "Extension patterns defined in registry.")}}</div>
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
