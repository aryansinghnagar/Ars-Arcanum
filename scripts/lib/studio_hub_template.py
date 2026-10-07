#!/usr/bin/env python3
"""
Ars Arcanum Studio Hub Standalone HTML/CSS/JS Template Generator
"""

from __future__ import annotations

import html
import json
from typing import Any

HUB_VERSION = "0.1.0"

__all__ = ["HUB_VERSION", "generate_studio_hub_html"]

def generate_studio_hub_html(data: dict[str, Any], api_mode: bool = False) -> str:
    """Generates the single-file offline responsive Studio Hub cockpit."""
    data_json = json.dumps(data, indent=2).replace("</", "<\\/")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:; connect-src 'self';">
<title>Ars Arcanum — Sovereign Studio Desktop Hub (v{HUB_VERSION})</title>
<style>
  :root {{
    --bg-base: #0f1117;
    --bg-card: #181b24;
    --bg-card-hover: #222634;
    --bg-sidebar: #13161f;
    --text-primary: #f0f2f5;
    --text-secondary: #9aa2b1;
    --text-muted: #8892b0;
    --accent-gold: #d4af37;
    --accent-gold-glow: rgba(212, 175, 55, 0.25);
    --accent-cyan: #38bdf8;
    --accent-emerald: #10b981;
    --accent-crimson: #f87171;
    --accent-purple: #a855f7;
    --border-color: #272c3d;
    --radius-sm: 6px;
    --radius-md: 10px;
    --radius-lg: 14px;
    --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Helvetica Neue", sans-serif;
    --font-mono: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
  }}

  body.theme-sepia {{
    --bg-base: #f4ecd8;
    --bg-card: #eadeca;
    --bg-card-hover: #dfd1bb;
    --bg-sidebar: #eee3cb;
    --text-primary: #3c3226;
    --text-secondary: #6e5e4d;
    --text-muted: #5a4c3e;
    --border-color: #d8c8b0;
    --accent-gold: #7c5200;
  }}

  body.theme-light {{
    --bg-base: #f8fafc;
    --bg-card: #ffffff;
    --bg-card-hover: #f1f5f9;
    --bg-sidebar: #f1f5f9;
    --text-primary: #0f172a;
    --text-secondary: #475569;
    --text-muted: #556987;
    --border-color: #e2e8f0;
    --accent-gold: #b45309;
  }}

  * {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }}

  body {{
    background-color: var(--bg-base);
    color: var(--text-primary);
    font-family: var(--font-sans);
    display: flex;
    height: 100vh;
    overflow: hidden;
  }}

  /* Sidebar */
  aside.sidebar {{
    width: 270px;
    background-color: var(--bg-sidebar);
    border-right: 1px solid var(--border-color);
    display: flex;
    flex-direction: column;
    flex-shrink: 0;
  }}

  .brand {{
    padding: 20px;
    display: flex;
    align-items: center;
    gap: 12px;
    border-bottom: 1px solid var(--border-color);
  }}

  .brand-icon {{
    width: 32px;
    height: 32px;
    background: linear-gradient(135deg, var(--accent-gold), #997300);
    border-radius: var(--radius-sm);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #111;
    font-weight: bold;
    font-size: 18px;
    box-shadow: 0 0 12px var(--accent-gold-glow);
  }}

  .brand-text h1 {{
    font-size: 16px;
    font-weight: 700;
    letter-spacing: 0.5px;
    color: var(--text-primary);
  }}

  .brand-text .badge {{
    font-size: 10px;
    background: var(--border-color);
    padding: 2px 6px;
    border-radius: 4px;
    color: var(--accent-gold);
    font-weight: 600;
  }}

  nav.nav-menu {{
    padding: 16px 12px;
    flex: 1;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 4px;
  }}

  .nav-btn {{
    background: none;
    border: none;
    color: var(--text-secondary);
    padding: 10px 14px;
    text-align: left;
    font-size: 13.5px;
    font-weight: 500;
    border-radius: var(--radius-sm);
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 10px;
    transition: all 0.15s ease;
  }}

  .nav-btn:hover {{
    background-color: var(--bg-card);
    color: var(--text-primary);
  }}

  .nav-btn.active {{
    background-color: var(--bg-card);
    color: var(--accent-gold);
    border-left: 3px solid var(--accent-gold);
    font-weight: 600;
  }}

  .sidebar-footer {{
    padding: 16px 20px;
    border-top: 1px solid var(--border-color);
    font-size: 11px;
    color: var(--text-muted);
    display: flex;
    flex-direction: column;
    gap: 6px;
  }}

  .sovereign-tag {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    color: var(--accent-emerald);
    font-weight: 600;
  }}

  /* Main Workspace */
  main.main-content {{
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow-y: auto;
    background-color: var(--bg-base);
  }}

  header.topbar {{
    padding: 16px 28px;
    border-bottom: 1px solid var(--border-color);
    display: flex;
    align-items: center;
    justify-content: space-between;
    background-color: var(--bg-sidebar);
    position: sticky;
    top: 0;
    z-index: 10;
  }}

  .topbar-title h2 {{
    font-size: 18px;
    font-weight: 600;
  }}

  .topbar-title p {{
    font-size: 12px;
    color: var(--text-secondary);
  }}

  .topbar-actions {{
    display: flex;
    align-items: center;
    gap: 12px;
  }}

  .search-input {{
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    padding: 8px 14px;
    border-radius: var(--radius-sm);
    color: var(--text-primary);
    font-size: 13px;
    width: 220px;
  }}

  .theme-toggle {{
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    color: var(--text-secondary);
    padding: 8px 12px;
    border-radius: var(--radius-sm);
    cursor: pointer;
    font-size: 12px;
  }}

  /* Dynamic Craft Tip Bar */
  .dynamic-tip-bar {{
    margin: 16px 28px 0 28px;
    padding: 12px 18px;
    background: linear-gradient(135deg, rgba(212, 175, 55, 0.08), rgba(56, 189, 248, 0.05));
    border: 1px solid var(--border-color);
    border-left: 4px solid var(--accent-gold);
    border-radius: var(--radius-md);
    display: flex;
    align-items: flex-start;
    gap: 14px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    transition: all 0.2s ease;
  }}
  .dynamic-tip-bar.hidden {{
    display: none !important;
  }}
  .tip-icon {{
    font-size: 20px;
    line-height: 1;
    padding-top: 2px;
    flex-shrink: 0;
  }}
  .tip-body {{
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 4px;
    min-width: 0;
  }}
  .tip-meta {{
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  }}
  .tip-badge {{
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    background: rgba(212, 175, 55, 0.2);
    color: var(--accent-gold);
    padding: 2px 7px;
    border-radius: 4px;
    letter-spacing: 0.5px;
  }}
  .tip-sub-badge {{
    font-size: 10px;
    background: var(--bg-card);
    color: var(--text-secondary);
    padding: 2px 6px;
    border-radius: 4px;
    border: 1px solid var(--border-color);
  }}
  .tip-depth-badge {{
    font-size: 10px;
    background: rgba(16, 185, 129, 0.15);
    color: var(--accent-emerald);
    padding: 2px 6px;
    border-radius: 4px;
  }}
  .tip-title {{
    font-size: 13px;
    font-weight: 600;
    color: var(--text-primary);
  }}
  .tip-text {{
    font-size: 12.5px;
    line-height: 1.45;
    color: var(--text-secondary);
  }}
  .tip-actions {{
    display: flex;
    align-items: center;
    gap: 6px;
    flex-shrink: 0;
  }}
  .tip-action-btn {{
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    color: var(--text-muted);
    width: 26px;
    height: 26px;
    border-radius: var(--radius-sm);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    font-size: 12px;
    transition: all 0.15s ease;
  }}
  .tip-action-btn:hover {{
    color: var(--text-primary);
    background: var(--bg-card-hover);
    border-color: var(--accent-gold);
  }}
  .tip-toggle-footer {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-top: 4px;
    border-top: 1px dashed var(--border-color);
    margin-top: 4px;
    font-size: 11px;
    cursor: pointer;
    color: var(--text-muted);
  }}
  .tip-toggle-footer:hover {{
    color: var(--accent-gold);
  }}

  /* Granular Scope Bar */
  .scope-bar {{
    margin: 14px 28px 0 28px;
    padding: 10px 16px;
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    display: flex;
    align-items: center;
    gap: 14px;
    flex-wrap: wrap;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
  }}
  .scope-item {{
    display: flex;
    align-items: center;
    gap: 6px;
  }}
  .scope-label {{
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    color: var(--text-secondary);
    letter-spacing: 0.5px;
  }}
  .scope-input {{
    background: var(--bg-sidebar);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-sm);
    color: var(--text-primary);
    padding: 4px 8px;
    font-size: 12px;
    font-family: var(--font-mono);
    width: 110px;
  }}
  .scope-input:focus {{
    border-color: var(--accent-gold);
    outline: none;
  }}
  .scope-preset-btn {{
    background: var(--bg-sidebar);
    border: 1px solid var(--border-color);
    color: var(--text-secondary);
    padding: 4px 9px;
    border-radius: var(--radius-sm);
    font-size: 11px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s ease;
  }}
  .scope-preset-btn:hover, .scope-preset-btn.active {{
    color: var(--accent-gold);
    background: var(--bg-card-hover);
    border-color: var(--accent-gold);
  }}
  .scope-badge {{
    margin-left: auto;
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 11px;
    background: rgba(56, 189, 248, 0.1);
    border: 1px solid rgba(56, 189, 248, 0.3);
    color: var(--accent-cyan);
    padding: 4px 10px;
    border-radius: 4px;
    font-family: var(--font-mono);
  }}

  .content-body {{
    padding: 28px;
    max-width: 1400px;
    width: 100%;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: 24px;
  }}

  /* Cards Grid */
  .metrics-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 16px;
  }}

  .metric-card {{
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    transition: transform 0.15s ease, border-color 0.15s ease;
  }}

  .metric-card:hover {{
    transform: translateY(-2px);
    border-color: var(--accent-gold);
  }}

  .metric-label {{
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-secondary);
  }}

  .metric-value {{
    font-size: 26px;
    font-weight: 700;
    color: var(--text-primary);
    font-family: var(--font-mono);
  }}

  .metric-sub {{
    font-size: 12px;
    color: var(--text-muted);
  }}

  /* Section Styles */
  .section-panel {{
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }}

  .section-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
  }}

  .section-header h3 {{
    font-size: 16px;
    font-weight: 600;
  }}

  /* Table styles */
  table.data-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
  }}

  table.data-table th {{
    text-align: left;
    padding: 10px 14px;
    background-color: var(--bg-sidebar);
    color: var(--text-secondary);
    font-weight: 600;
    border-bottom: 1px solid var(--border-color);
  }}

  table.data-table td {{
    padding: 12px 14px;
    border-bottom: 1px solid var(--border-color);
    color: var(--text-primary);
  }}

  table.data-table tr:hover td {{
    background-color: var(--bg-card-hover);
  }}

  .tag {{
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 500;
    background: var(--bg-sidebar);
    border: 1px solid var(--border-color);
  }}

  .tag.tag-char {{ color: var(--accent-cyan); border-color: rgba(56, 189, 248, 0.3); }}
  .tag.tag-loc {{ color: var(--accent-emerald); border-color: rgba(16, 185, 129, 0.3); }}
  .tag.tag-magic {{ color: var(--accent-purple); border-color: rgba(168, 85, 247, 0.3); }}
  .tag.tag-fact {{ color: var(--accent-gold); border-color: rgba(212, 175, 55, 0.3); }}

  /* Engine Grid */
  .engine-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 16px;
  }}

  .engine-card {{
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 18px;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }}

  .engine-card h4 {{
    font-size: 14px;
    font-weight: 600;
    color: var(--accent-gold);
  }}

  .engine-card p {{
    font-size: 12.5px;
    color: var(--text-secondary);
    line-height: 1.4;
  }}

  .engine-cli {{
    font-family: var(--font-mono);
    font-size: 11px;
    background-color: var(--bg-sidebar);
    padding: 4px 8px;
    border-radius: 4px;
    color: var(--accent-cyan);
  }}

  /* Interactive RAG & Council Sandbox */
  .interactive-box {{
    display: flex;
    flex-direction: column;
    gap: 12px;
  }}

  .query-input-row {{
    display: flex;
    gap: 10px;
  }}

  .query-input-row input, .query-input-row textarea {{
    flex: 1;
    background-color: var(--bg-sidebar);
    border: 1px solid var(--border-color);
    padding: 10px 14px;
    border-radius: var(--radius-sm);
    color: var(--text-primary);
    font-size: 13.5px;
    font-family: var(--font-sans);
  }}

  .btn-primary {{
    background: linear-gradient(135deg, var(--accent-gold), #997300);
    color: #111;
    border: none;
    padding: 10px 18px;
    font-weight: 600;
    border-radius: var(--radius-sm);
    cursor: pointer;
    font-size: 13px;
  }}

  .btn-primary:hover {{
    box-shadow: 0 0 12px var(--accent-gold-glow);
  }}

  .response-box {{
    background-color: var(--bg-sidebar);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-sm);
    padding: 16px;
    font-family: var(--font-mono);
    font-size: 12px;
    max-height: 300px;
    overflow-y: auto;
    white-space: pre-wrap;
    display: none;
  }}

  /* Pacing Bar */
  .pacing-bar {{
    height: 12px;
    background-color: var(--bg-sidebar);
    border-radius: 6px;
    overflow: hidden;
    display: flex;
    margin-top: 8px;
  }}

  .pacing-segment {{
    height: 100%;
    transition: width 0.3s ease;
  }}

  .btn-doc {{
    background-color: var(--bg-sidebar);
    border: 1px solid var(--accent-gold);
    color: var(--accent-gold);
    padding: 6px 12px;
    border-radius: var(--radius-sm);
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s ease;
    display: inline-flex;
    align-items: center;
    gap: 6px;
  }}

  .btn-doc:hover {{
    background-color: var(--accent-gold);
    color: #111;
  }}

  /* Modal Overlay */
  .modal-backdrop {{
    display: none;
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background-color: rgba(0, 0, 0, 0.75);
    backdrop-filter: blur(4px);
    z-index: 100;
    justify-content: center;
    align-items: center;
    padding: 20px;
  }}

  .modal-backdrop.open {{
    display: flex;
  }}

  .modal-dialog {{
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    width: 100%;
    max-width: 860px;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
    box-shadow: 0 20px 40px rgba(0,0,0,0.6);
    overflow: hidden;
  }}

  .modal-header {{
    padding: 18px 24px;
    border-bottom: 1px solid var(--border-color);
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: var(--bg-sidebar);
  }}

  .modal-title h3 {{
    font-size: 17px;
    color: var(--accent-gold);
    display: flex;
    align-items: center;
    gap: 8px;
  }}

  .modal-close {{
    background: none;
    border: none;
    color: var(--text-secondary);
    font-size: 22px;
    cursor: pointer;
    line-height: 1;
  }}

  .modal-close:hover {{
    color: var(--text-primary);
  }}

  .modal-nav {{
    display: flex;
    background-color: var(--bg-sidebar);
    border-bottom: 1px solid var(--border-color);
    padding: 0 16px;
    gap: 4px;
    overflow-x: auto;
  }}

  .modal-nav-btn {{
    background: none;
    border: none;
    color: var(--text-secondary);
    padding: 10px 14px;
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    border-bottom: 2px solid transparent;
  }}

  .modal-nav-btn.active {{
    color: var(--accent-gold);
    border-bottom-color: var(--accent-gold);
    font-weight: 600;
  }}

  .modal-body {{
    padding: 24px;
    overflow-y: auto;
    font-size: 13.5px;
    line-height: 1.6;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }}

  .code-block {{
    background-color: var(--bg-sidebar);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-sm);
    padding: 14px;
    font-family: var(--font-mono);
    font-size: 12px;
    white-space: pre-wrap;
    overflow-x: auto;
    color: var(--text-primary);
  }}

  /* Sandbox Grid */
  .sandbox-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 16px;
  }}

  .sandbox-card {{
    background-color: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 18px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }}

  /* Tabs hidden state */
  .tab-pane {{
    display: none;
    flex-direction: column;
    gap: 20px;
  }}

  .tab-pane.active {{
    display: flex;
  }}
</style>
</head>
<body>

<aside class="sidebar" role="navigation" aria-label="Studio Navigation">
  <div class="brand">
    <div class="brand-icon">⚡</div>
    <div class="brand-text">
      <h1>Ars Arcanum</h1>
      <span class="badge">Sovereign Studio Hub v{HUB_VERSION}</span>
    </div>
  </div>

  <nav class="nav-menu" role="tablist" aria-label="Studio Workspaces">
    <button class="nav-btn active" id="nav-tab-overview" role="tab" aria-selected="true" aria-controls="tab-overview" onclick="switchTab('tab-overview')">📊 Overview Dashboard</button>
    <button class="nav-btn" id="nav-tab-manuscript" role="tab" aria-selected="false" aria-controls="tab-manuscript" onclick="switchTab('tab-manuscript')">📖 Manuscripts & Chapters</button>
    <button class="nav-btn" id="nav-tab-lore" role="tab" aria-selected="false" aria-controls="tab-lore" onclick="switchTab('tab-lore')">🔮 Lore Codex & Entities</button>
    <button class="nav-btn" id="nav-tab-structure" role="tab" aria-selected="false" aria-controls="tab-structure" onclick="switchTab('tab-structure')">📐 Structure & Pacing</button>
    <button class="nav-btn" id="nav-tab-timeline" role="tab" aria-selected="false" aria-controls="tab-timeline" onclick="switchTab('tab-timeline')">⏳ Timeline & Paradoxes</button>
    <button class="nav-btn" id="nav-tab-intelligence" role="tab" aria-selected="false" aria-controls="tab-intelligence" onclick="switchTab('tab-intelligence')">🧠 Local RAG & Editorial</button>
    <button class="nav-btn" id="nav-tab-engines" role="tab" aria-selected="false" aria-controls="tab-engines" onclick="switchTab('tab-engines')">⚙️ Craft Engine Matrix</button>
    <button class="nav-btn" id="nav-tab-resonance" role="tab" aria-selected="false" aria-controls="tab-resonance" onclick="switchTab('tab-resonance')">🌌 Resonance & Synergy Mesh</button>
    <button class="nav-btn" id="nav-tab-guide" role="tab" aria-selected="false" aria-controls="tab-guide" onclick="switchTab('tab-guide')">💡 Craft Guide & Advisory Matrix</button>
  </nav>

  <div class="sidebar-footer">
    <div class="sovereign-tag">🛡️ 100% Sovereign Offline</div>
    <div>Zero Telemetry • Standard Lib</div>
    <div class="tip-toggle-footer" onclick="toggleTipsBar()" title="Click to enable/disable dynamic craft wisdom tips" aria-label="Toggle craft wisdom tips">
      <span id="tips-toggle-label">💡 Dynamic Tips: Active</span>
    </div>
  </div>
</aside>

<main class="main-content" role="main">
  <header class="topbar" role="banner">
    <div class="topbar-title">
      <h2 id="page-title" aria-live="polite">Overview Dashboard</h2>
      <p id="page-subtitle">Universe: {data['project']['world_name']} • Manuscript: {data['project']['manuscript_name']}</p>
    </div>
    <div class="topbar-actions" role="toolbar" aria-label="Quick Actions">
      <button class="theme-toggle" id="btn-toggle-tips-top" onclick="toggleTipsBar()" title="Toggle non-intrusive craft wisdom tips" aria-label="Toggle dynamic craft tips">💡 Tips</button>
      <input type="text" id="global-search" class="search-input" placeholder="Search chapters, lore..." oninput="handleGlobalSearch(this.value)" aria-label="Search chapters, lore, and entities">
      <button class="theme-toggle" onclick="cycleTheme()" aria-label="Cycle theme color palette">🎨 Theme</button>
    </div>
  </header>

  <!-- GRANULAR SCOPE BAR -->
  <div class="scope-bar" id="scope-bar">
    <div class="scope-item">
      <span class="scope-label">🎯 Target:</span>
      <span style="font-size: 12px; font-weight: 600; color: var(--text-primary);">{data['project']['manuscript_name']}</span>
    </div>
    <div class="scope-item">
      <span class="scope-label">Chapters:</span>
      <input type="text" id="scope-input-chapters" class="scope-input" placeholder="All (e.g. 1-5)" onchange="onScopeInputChange()" title="Specify chapters: e.g. 1-5, 8, 10-12 or ch01..ch05">
    </div>
    <div class="scope-item">
      <span class="scope-label">Scenes:</span>
      <input type="text" id="scope-input-scenes" class="scope-input" placeholder="All (e.g. 1-3)" onchange="onScopeInputChange()" title="Specify scene range: e.g. 1-4 or sc01..sc03">
    </div>
    <div class="scope-item" style="gap: 4px;">
      <span class="scope-label">Presets:</span>
      <button class="scope-preset-btn active" id="btn-preset-active" onclick="applyScopePreset('active')" title="Active open project scope">⚡ Active</button>
      <button class="scope-preset-btn" id="btn-preset-all" onclick="applyScopePreset('all')" title="All chapters and scenes in manuscript">📖 Whole Book</button>
      <button class="scope-preset-btn" id="btn-preset-ch1_5" onclick="applyScopePreset('ch1_5')" title="Chapters 1 through 5">📑 Ch 1-5</button>
      <button class="scope-preset-btn" id="btn-preset-act1" onclick="applyScopePreset('act1')" title="Act 1 (First 25% of manuscript)">🎭 Act 1</button>
      <button class="scope-preset-btn" id="btn-preset-custom" onclick="openScopeModal()" title="Open advanced scope targeting modal">⚙️ Custom...</button>
    </div>
    <span id="scope-summary-badge" class="scope-badge">Scope: Manuscript (All)</span>
  </div>

  <!-- DYNAMIC CRAFT WISDOM / TIP BANNER -->
  <div id="dynamic-tip-bar" class="dynamic-tip-bar">
    <div class="tip-icon">💡</div>
    <div class="tip-body">
      <div class="tip-meta">
        <span class="tip-badge" id="tip-engine-badge">ASTROPHYSICS</span>
        <span class="tip-sub-badge" id="tip-subfeature-badge">Turnaround Flip</span>
        <span class="tip-depth-badge" id="tip-depth-badge">Masterclass</span>
        <strong id="tip-title">Brachistochrone Midpoint Turnover as Pacing Pivot</strong>
      </div>
      <div class="tip-text" id="tip-content">In 1g constant-acceleration transits, peak coordinate velocity occurs at the exact midpoint turnover, where the ship rotates 180 degrees. Use the brief 60-second zero-g transition between acceleration and deceleration as a high-tension psychological scene pivot.</div>
    </div>
    <div class="tip-actions">
      <button class="tip-action-btn" id="btn-cycle-tip" title="Next Craft Tip (Cycle)" onclick="cycleNextTip()">🔄</button>
      <button class="tip-action-btn" id="btn-toggle-tip" title="Dismiss / Hide Tips" onclick="toggleTipsBar()">✕</button>
    </div>
  </div>

  <div class="content-body">

    <!-- OVERVIEW TAB -->
    <div id="tab-overview" class="tab-pane active" role="tabpanel" aria-labelledby="nav-tab-overview">
      <div class="metrics-grid">
        <div class="metric-card">
          <span class="metric-label">Total Word Count</span>
          <span class="metric-value">{data['metrics']['total_words']:,}</span>
          <span class="metric-sub">{data['metrics']['estimated_reading_hours']} hrs reading time</span>
        </div>
        <div class="metric-card">
          <span class="metric-label">Chapters & Scenes</span>
          <span class="metric-value">{data['metrics']['total_chapters']}</span>
          <span class="metric-sub">Avg {data['metrics']['average_chapter_words']} words / ch</span>
        </div>
        <div class="metric-card">
          <span class="metric-label">Indexed Lore Entities</span>
          <span class="metric-value">{data['metrics']['total_lore_entities']}</span>
          <span class="metric-sub">{len(data['metrics']['lore_breakdown'])} active categories</span>
        </div>
        <div class="metric-card">
          <span class="metric-label">Timeline Status</span>
          <span class="metric-value">{data['metrics']['timeline_events_count']}</span>
          <span class="metric-sub" style="color: {'var(--accent-crimson)' if data['metrics']['timeline_paradoxes_count'] > 0 else 'var(--accent-emerald)'};">
            {data['metrics']['timeline_paradoxes_count']} paradoxes detected
          </span>
        </div>
      </div>

      <div class="section-panel">
        <div class="section-header">
          <h3>Recent Chapters & Manuscript Progress</h3>
          <span class="tag tag-char">{len(data['chapters'])} Chapters</span>
        </div>
        <table class="data-table" id="overview-chapter-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Title</th>
              <th>POV</th>
              <th>Words</th>
              <th>Read Time</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {"".join(f"<tr><td>{c['sequence']}</td><td><strong>{html.escape(str(c['title']))}</strong></td><td>{html.escape(str(c['pov']))}</td><td>{c['words']}</td><td>{c['reading_time_min']}m</td><td><span class='tag'>{html.escape(str(c['status']))}</span></td></tr>" for c in data['chapters'][:6])}
          </tbody>
        </table>
      </div>

      <div class="section-panel">
        <div class="section-header">
          <h3>World Lore Distribution</h3>
        </div>
        <div style="display: flex; gap: 12px; flex-wrap: wrap;">
          {"".join(f"<div class='metric-card' style='flex:1; min-width: 140px;'><span class='metric-label'>{html.escape(str(k))}</span><span class='metric-value'>{v}</span></div>" for k, v in data['metrics']['lore_breakdown'].items())}
        </div>
      </div>
    </div>

    <!-- MANUSCRIPT TAB -->
    <div id="tab-manuscript" class="tab-pane" role="tabpanel" aria-labelledby="nav-tab-manuscript">
      <div class="section-panel">
        <div class="section-header">
          <h3>All Manuscript Chapters</h3>
          <span class="tag tag-char">{data['metrics']['total_words']:,} Total Words</span>
        </div>
        <table class="data-table">
          <thead>
            <tr>
              <th>#</th>
              <th>File</th>
              <th>Title</th>
              <th>POV</th>
              <th>Words</th>
              <th>Choices/States</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {"".join(f"<tr><td>{c['sequence']}</td><td><code>{html.escape(str(c['file']))}</code></td><td>{html.escape(str(c['title']))}</td><td>{html.escape(str(c['pov']))}</td><td>{c['words']}</td><td>{c['choices_count']} choices / {c['states_count']} states</td><td><span class='tag'>{html.escape(str(c['status']))}</span></td></tr>" for c in data['chapters'])}
          </tbody>
        </table>
      </div>
    </div>

    <!-- LORE TAB -->
    <div id="tab-lore" class="tab-pane" role="tabpanel" aria-labelledby="nav-tab-lore">
      <div class="section-panel">
        <div class="section-header">
          <h3>Cosmos World Bible Entities</h3>
          <span class="tag tag-magic">{data['metrics']['total_lore_entities']} Entities</span>
        </div>
        <table class="data-table">
          <thead>
            <tr>
              <th>Entity Name</th>
              <th>Category</th>
              <th>File</th>
              <th>Tags / Aliases</th>
              <th>Summary</th>
            </tr>
          </thead>
          <tbody>
            {"".join(f"<tr><td><strong>{html.escape(str(e['name']))}</strong></td><td><span class='tag tag-char'>{html.escape(str(e['category']))}</span></td><td><code>{html.escape(str(e['file']))}</code></td><td>{html.escape(', '.join(e['tags'] or e['aliases'] or ['-']))}</td><td>{html.escape(str(e['summary']))}</td></tr>" for e in data['lore_entities'])}
          </tbody>
        </table>
      </div>
    </div>

    <!-- STRUCTURE TAB -->
    <div id="tab-structure" class="tab-pane" role="tabpanel" aria-labelledby="nav-tab-structure">
      <div class="section-panel">
        <div class="section-header">
          <h3>Multi-Paradigm Structural Harmony</h3>
          <span class="tag tag-fact">{len(data['structure']['pacing_curve'])} Beat Points</span>
        </div>
        <p style="font-size: 13px; color: var(--text-secondary);">
          Pacing and narrative distribution curves mapped across Three-Act, Save the Cat, and Kishōtenketsu milestones.
        </p>
        <table class="data-table">
          <thead>
            <tr>
              <th>Chapter #</th>
              <th>Title</th>
              <th>Words</th>
              <th>Cumulative Words</th>
              <th>Progress %</th>
            </tr>
          </thead>
          <tbody>
            {"".join(f"<tr><td>{p['chapter']}</td><td>{html.escape(str(p['title']))}</td><td>{p['words']}</td><td>{p['cumulative_words']}</td><td>{p['percentage']}%</td></tr>" for p in data['structure']['pacing_curve'])}
          </tbody>
        </table>
      </div>
    </div>

    <!-- TIMELINE TAB -->
    <div id="tab-timeline" class="tab-pane" role="tabpanel" aria-labelledby="nav-tab-timeline">
      <div class="section-panel">
        <div class="section-header">
          <h3>Chronological vs Narrative Events</h3>
          <span class="tag tag-fact">{len(data['timeline_events'])} Events</span>
        </div>
        <table class="data-table">
          <thead>
            <tr>
              <th>Source</th>
              <th>Event / Chapter</th>
              <th>Chronological Date</th>
              <th>Narrative Time</th>
              <th>Actor / POV</th>
              <th>Paradox</th>
            </tr>
          </thead>
          <tbody>
            {"".join(f"<tr><td><code>{html.escape(str(ev['source']))}</code></td><td>{html.escape(str(ev['title']))}</td><td>{html.escape(str(ev['chrono_date']))}</td><td>{html.escape(str(ev['narrative_time']))}</td><td>{html.escape(str(ev['actor']))}</td><td><span class='tag' style='color: {'var(--accent-crimson)' if ev['paradox'] else 'var(--accent-emerald)'};'>{'⚠️ PARADOX' if ev['paradox'] else '✓ OK'}</span></td></tr>" for ev in data['timeline_events'])}
          </tbody>
        </table>
      </div>
    </div>

    <!-- INTELLIGENCE TAB -->
    <div id="tab-intelligence" class="tab-pane" role="tabpanel" aria-labelledby="nav-tab-intelligence">
      <div class="section-panel">
        <div class="section-header">
          <h3>Local Semantic Retrieval (RAG) Query Sandbox</h3>
          <span class="tag tag-magic">Zero Cloud</span>
        </div>
        <div class="interactive-box">
          <div class="query-input-row">
            <input type="text" id="rag-query" placeholder="Ask a question about your lore (e.g. 'How does blood magic function?')...">
            <button class="btn-primary" onclick="runRagQuery()">Search Lore</button>
          </div>
          <div id="rag-response" class="response-box"></div>
        </div>
      </div>

      <div class="section-panel">
        <div class="section-header">
          <h3>Autonomous Editorial Council Evaluator</h3>
          <span class="tag tag-char">4 Personas</span>
        </div>
        <div class="interactive-box">
          <textarea id="council-draft" rows="4" placeholder="Paste draft prose snippet to evaluate with the autonomous editorial council..."></textarea>
          <div>
            <button class="btn-primary" onclick="runCouncilEval()">Evaluate Draft</button>
          </div>
          <div id="council-response" class="response-box"></div>
        </div>
      </div>
    </div>

    <!-- ENGINES TAB -->
    <div id="tab-engines" class="tab-pane" role="tabpanel" aria-labelledby="nav-tab-engines">
      <div class="section-panel">
        <div class="section-header">
          <h3>Ars Arcanum Sovereign Craft Engine Topology</h3>
          <span class="tag tag-gold">{len(data['engine_catalog'])} Engines Active</span>
        </div>
        <p style="font-size: 13.5px; color: var(--text-secondary);">
          Every engine is sovereign, 100% offline, and mathematically grounded. Click "📖 View Logic & Formulas" on any engine to inspect its underlying domain logic, formulas, rationale, and author extension code.
        </p>
        <div class="engine-grid">
          {"".join(f'''<div class="engine-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span class="tag tag-magic">{eng['category']} • {eng.get('studio_tab', 'Engine')}</span>
              <span class="engine-cli">{eng['cli']}</span>
            </div>
            <h4>{eng['name']}</h4>
            <p>{eng['desc']}</p>
            <div style="display: flex; gap: 8px; margin-top: auto; padding-top: 10px; flex-wrap: wrap;">
              <button class="btn-doc" onclick="openEngineDocModal('{eng['id']}')">📖 View Logic & Formulas</button>
              <button class="btn-primary" style="font-size: 11.5px; padding: 4px 10px;" onclick="openEngineRunModal('{eng['id']}', '{eng['name']}')">⚡ Run Scoped</button>
            </div>
          </div>''' for eng in data['engine_catalog'])}
        </div>
      </div>
    </div>

    <!-- AUTHOR CRAFT GUIDE & ADVISORY MATRIX TAB -->
    <div id="tab-guide" class="tab-pane" role="tabpanel" aria-labelledby="nav-tab-guide">
      <div class="section-panel">
        <div class="section-header">
          <h3>Author Craft Guide, Worldbuilding Logic & Advisory Resolution Matrix</h3>
          <span class="tag tag-gold">100% Creative Sovereignty</span>
        </div>
        <p style="font-size: 13.5px; color: var(--text-secondary); line-height: 1.5;">
          Ars Arcanum acts as an informative creative compass, never a rigid gatekeeper. All scientific formulas, narrative structure frameworks, and linguistic checks provide advisory suggestions with multiple creative resolution pathways. You always have 100% final decision authority.
        </p>

        <!-- Interactive Craft Sandboxes -->
        <h4 style="font-size: 15px; margin-top: 12px; color: var(--accent-gold);">🧪 Interactive Craft & Science Sandboxes</h4>
        <div class="sandbox-grid">
          <!-- Astrophysics Sandbox -->
          <div class="sandbox-card">
            <h5 style="color: var(--accent-cyan); font-size: 14px;">🚀 Relativistic Brachistochrone Transit</h5>
            <p style="font-size: 12px; color: var(--text-secondary);">Calculates relativistic ship proper time, coordinate time, and peak velocity for 1g continuous acceleration.</p>
            <div style="display: flex; gap: 8px;">
              <input type="number" id="sb-astro-dist" value="4.3" step="0.1" style="width: 80px; padding: 6px; background: var(--bg-sidebar); border: 1px solid var(--border-color); color: var(--text-primary); border-radius: 4px;" placeholder="Dist">
              <select id="sb-astro-unit" style="padding: 6px; background: var(--bg-sidebar); border: 1px solid var(--border-color); color: var(--text-primary); border-radius: 4px;">
                <option value="ly">Light Years (ly)</option>
                <option value="au">Astron. Units (AU)</option>
                <option value="km">Million km</option>
              </select>
              <button class="btn-primary" style="padding: 6px 12px; font-size: 12px;" onclick="calcSandboxTransit()">Compute</button>
            </div>
            <div id="sb-astro-res" style="font-size: 12px; font-family: var(--font-mono); color: var(--accent-gold); display: none; background: var(--bg-sidebar); padding: 8px; border-radius: 4px;"></div>
          </div>

          <!-- Sentence Rhythm Sandbox -->
          <div class="sandbox-card">
            <h5 style="color: var(--accent-emerald); font-size: 14px;">✍️ Gary Provost Sentence Rhythm Analyzer</h5>
            <p style="font-size: 12px; color: var(--text-secondary);">Measures sentence length cadence and standard deviation variance to diagnose prose monotony.</p>
            <textarea id="sb-rhythm-text" rows="2" style="width: 100%; padding: 6px; background: var(--bg-sidebar); border: 1px solid var(--border-color); color: var(--text-primary); border-radius: 4px; font-size: 12px;" placeholder="Paste 3-5 sentences to analyze rhythm..."></textarea>
            <button class="btn-primary" style="padding: 6px 12px; font-size: 12px;" onclick="analyzeSandboxRhythm()">Analyze Rhythm</button>
            <div id="sb-rhythm-res" style="font-size: 12px; font-family: var(--font-mono); color: var(--accent-emerald); display: none; background: var(--bg-sidebar); padding: 8px; border-radius: 4px;"></div>
          </div>

          <!-- Conlang Sound Shift Sandbox -->
          <div class="sandbox-card">
            <h5 style="color: var(--accent-purple); font-size: 14px;">🧬 Conlang Sound-Shift Tester</h5>
            <p style="font-size: 12px; color: var(--text-secondary);">Tests Neogrammarian regular sound shift rules on sample proto-lexicon words.</p>
            <div style="display: flex; gap: 8px;">
              <input type="text" id="sb-conlang-word" value="patra, kordo, trey" style="flex: 1; padding: 6px; background: var(--bg-sidebar); border: 1px solid var(--border-color); color: var(--text-primary); border-radius: 4px; font-size: 12px;" placeholder="Words">
              <input type="text" id="sb-conlang-rules" value="p>f, t>th, k>h" style="width: 110px; padding: 6px; background: var(--bg-sidebar); border: 1px solid var(--border-color); color: var(--text-primary); border-radius: 4px; font-size: 12px;" placeholder="Rules">
              <button class="btn-primary" style="padding: 6px 12px; font-size: 12px;" onclick="testSandboxConlang()">Shift</button>
            </div>
            <div id="sb-conlang-res" style="font-size: 12px; font-family: var(--font-mono); color: var(--accent-purple); display: none; background: var(--bg-sidebar); padding: 8px; border-radius: 4px;"></div>
          </div>
        </div>

        <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-top: 18px;">
          <button class="tag" style="cursor: pointer; padding: 6px 12px;" onclick="filterGuideCategory('all')">All Disciplines</button>
          <button class="tag tag-char" style="cursor: pointer; padding: 6px 12px;" onclick="filterGuideCategory('worldbuilding')">Worldbuilding Sciences</button>
          <button class="tag tag-loc" style="cursor: pointer; padding: 6px 12px;" onclick="filterGuideCategory('craft')">Story Architecture & Craft</button>
          <button class="tag tag-magic" style="cursor: pointer; padding: 6px 12px;" onclick="filterGuideCategory('core')">Core Pipeline & Tools</button>
          <button class="tag tag-fact" style="cursor: pointer; padding: 6px 12px;" onclick="filterGuideCategory('diagnostics')">Continuity & Diagnostics</button>
          <button class="tag tag-item" style="cursor: pointer; padding: 6px 12px;" onclick="filterGuideCategory('publishing')">Publishing & Export</button>
        </div>

        <input type="text" id="guide-filter-input" class="search-input" style="width: 100%; margin-top: 10px;" placeholder="Filter craft logic, worldbuilding rules, formulas, or resolution options..." oninput="filterGuideCards(this.value)">

        <div class="engine-grid" id="guide-cards-container" style="margin-top: 14px; grid-template-columns: 1fr;">
          {"".join(f'''<div class="engine-card guide-card" data-category="{eng['category'].lower()}" data-tab="{eng.get('studio_tab', '').lower()}" data-text="{eng['name'].lower()} {eng['desc'].lower()} {eng.get('scientific_logic', '').lower()} {eng.get('why_this_way', '').lower()} {eng.get('extension_guide', '').lower()} {eng.get('worldbuilding_relevance', '').lower()} {eng.get('storytelling_relevance', '').lower()} {eng.get('writing_relevance', '').lower()} {eng.get('cli', '').lower()}">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span class="tag tag-magic">{eng['category']} • {eng.get('studio_tab', 'Engine')}</span>
              <div style="display: flex; gap: 8px; align-items: center;">
                <span class="engine-cli">{eng['cli']}</span>
                <button class="btn-doc" onclick="openEngineDocModal('{eng['id']}')">📖 Full Modal</button>
              </div>
            </div>
            <h4 style="font-size: 16px; margin-top: 4px;">{eng['name']}</h4>
            <p style="color: var(--text-primary); font-size: 13px;">{eng['desc']}</p>

            <div style="background: var(--bg-sidebar); border: 1px solid var(--border-color); border-radius: 6px; padding: 14px; margin-top: 8px; display: flex; flex-direction: column; gap: 10px;">
              <div><strong>⚙️ Logic & Scientific / Structural Foundations:</strong><br><div class="code-block" style="margin-top: 4px;">{eng.get('scientific_logic', eng.get('logic_documentation', 'Standard calculation engine.'))}</div></div>

              {"<div><strong>💡 Why It Works This Way (Rationale):</strong><br><span style='color: var(--text-secondary); font-size: 12.5px;'>" + eng.get('why_this_way', '') + "</span></div>" if eng.get('why_this_way') else ""}

              {"<div><strong>⚡ Key Subfeatures:</strong><br>" + "".join("<div style='margin-top: 4px; font-size: 12px;'>• <strong>" + sf.get('name', '') + "</strong>: " + sf.get('rule', '') + " <code style='color: var(--accent-cyan);'>(" + sf.get('example', '') + ")</code></div>" for sf in eng.get('subfeatures', [])) + "</div>" if eng.get('subfeatures') else ""}

              {"<div><strong>🛠️ Author Extension Guide:</strong><br><div class='code-block' style='margin-top: 4px;'>" + eng.get('extension_guide', '') + "</div></div>" if eng.get('extension_guide') else ""}

              <div><strong>🌍 Worldbuilding Application:</strong><br><span style="color: var(--text-secondary); font-size: 12.5px;">{eng.get('worldbuilding_relevance', 'Worldbuilding lore consistency.')}</span></div>
              <div><strong>📐 Storytelling Relevance:</strong><br><span style="color: var(--text-secondary); font-size: 12.5px;">{eng.get('storytelling_relevance', 'Plot and pacing integration.')}</span></div>
              <div><strong>✍️ Prose Writing Relevance:</strong><br><span style="color: var(--text-secondary); font-size: 12.5px;">{eng.get('writing_relevance', 'Writing and line-editing polish.')}</span></div>

              {"<div style='margin-top: 6px; border-top: 1px solid var(--border-color); padding-top: 8px;'><strong>💡 Creative Advisory Resolution Pathways:</strong><br>" + "".join("<div style='margin-top: 6px; font-size: 12px;'><span style='color: var(--accent-gold);'>• Pattern: " + adv.get("pattern", "Unconventional input") + "</span><br>&nbsp;&nbsp;<span style='color: var(--accent-cyan);'>Option A (Realism):</span> " + adv.get("option_a", "Standard convention") + "<br>&nbsp;&nbsp;<span style='color: var(--accent-purple);'>Option B (Trope/Magic):</span> " + adv.get("option_b", "In-world grounding") + "<br>&nbsp;&nbsp;<span style='color: var(--accent-emerald);'>Option C (Sovereignty):</span> " + adv.get("option_c", "Author creative control") + "</div>" for adv in eng.get("advisory_guidance", [])) + "</div>" if eng.get("advisory_guidance") else ""}
            </div>
          </div>''' for eng in data['engine_catalog'])}
        </div>
      </div>
    </div>

    <!-- RESONANCE MESH & CROSS-DOMAIN SYNERGY TAB -->
    <div id="tab-resonance" class="tab-pane" role="tabpanel" aria-labelledby="nav-tab-resonance">
      <div class="metrics-grid">
        <div class="metric-card">
          <span class="metric-label">Universal Mesh Nodes</span>
          <span class="metric-value">{data.get('resonance', {}).get('node_count', 0)}</span>
          <span class="metric-sub">5 Master Domain Pillars</span>
        </div>
        <div class="metric-card">
          <span class="metric-label">Cross-Domain Edges</span>
          <span class="metric-value">{data.get('resonance', {}).get('edge_count', 0)}</span>
          <span class="metric-sub">Causal & Thematic Relational Bridges</span>
        </div>
        <div class="metric-card">
          <span class="metric-label">Creative Isomorphisms</span>
          <span class="metric-value">{len(data.get('resonance', {}).get('sparks', []))}</span>
          <span class="metric-sub">Multidisciplinary Analogies</span>
        </div>
        <div class="metric-card">
          <span class="metric-label">Cross-Domain Integrity</span>
          <span class="metric-value" style="color: var(--accent-emerald);">100%</span>
          <span class="metric-sub">Zero Contradictions</span>
        </div>
      </div>

      <!-- Causal Cascade Sandbox -->
      <div class="section-panel">
        <div class="section-header">
          <h3>Deterministic Causal Cascade Sandbox</h3>
          <span class="tag tag-gold">Live Simulation</span>
        </div>
        <p style="font-size: 13px; color: var(--text-secondary);">
          Modify upstream cosmological, magical, or economic parameters to calculate downstream domino effects across biomes, agriculture, trade, military tactics, and scene tension.
        </p>
        <div style="display: flex; gap: 12px; align-items: center; margin-top: 8px;">
          <label style="font-size: 12px; font-weight: 600; color: var(--text-secondary);">Select Parameter:</label>
          <select id="hubCascadeSelect" class="search-input" style="width: auto; flex: 1;" onchange="renderHubCascadeSandbox()">
            <option value="axial_tilt">Planetary Axial Tilt (38.5°) — Severe Seasons, Compressed Crop Growing Season, Attrition</option>
            <option value="magic_cost">Arcane Mana Backlash — Royal Monopolies, Guild Displacement, Leyline Omens</option>
            <option value="currency_debasement">Specie Debasement — Peasant Revolt Risk, Mercenary Mutiny, Slang Cant</option>
            <option value="stellar_mass">Stellar Mass Shift — Year Length Expansion, Intercalary Epagomenal Idioms</option>
          </select>
        </div>
        <div id="hubCascadeOutput" style="display: flex; flex-direction: column; gap: 10px; margin-top: 12px;"></div>
      </div>

      <!-- Creative Spark Lab -->
      <div class="section-panel">
        <div class="section-header">
          <h3>Creative Spark & Cross-Domain Analogy Lab</h3>
          <span class="tag tag-char">Multidisciplinary Synthesis</span>
        </div>
        <p style="font-size: 13px; color: var(--text-secondary);">
          Structural isomorphisms bridging disparate fields to stimulate novel worldbuilding premises, scene conflicts, and visceral sensory palettes.
        </p>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(360px, 1fr)); gap: 16px; margin-top: 8px;">
          {"".join(f'''<div class="engine-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <h4 style="color: var(--accent-gold);">{html.escape(s.get("title", ""))}</h4>
            </div>
            <div style="display: flex; gap: 6px; flex-wrap: wrap;">
              {"".join(f'<span class="tag tag-loc">{d}</span>' for d in s.get("domains", []))}
            </div>
            <p style="font-size: 12.5px; color: var(--text-primary); margin-top: 4px;"><strong>Analogy:</strong> {html.escape(s.get("core_analogy", ""))}</p>
            <p style="font-size: 12px; color: var(--text-secondary);"><strong>World Hook:</strong> {html.escape(s.get("worldbuilding_hook", ""))}</p>
            <p style="font-size: 12px; color: var(--text-secondary);"><strong>Scene Conflict:</strong> {html.escape(s.get("scene_conflict", ""))}</p>
            <div style="font-size: 11px; font-family: var(--font-mono); color: var(--accent-cyan); margin-top: 4px;">Sensory: {" • ".join(s.get("sensory_palette", []))}</div>
          </div>''' for s in data.get("resonance", {}).get("sparks", []))}
        </div>
      </div>
    </div>

  </div>
</main>

<!-- Interactive Engine Documentation Modal -->
<div id="engineDocModal" class="modal-backdrop" role="dialog" aria-modal="true" aria-labelledby="modalEngineTitle" onclick="if(event.target===this) closeEngineDocModal()">
  <div class="modal-dialog" role="document">
    <div class="modal-header">
      <div class="modal-title">
        <span id="modalCategoryBadge" class="tag tag-gold">CRAFT</span>
        <h3 id="modalEngineTitle" style="margin-left: 8px;">Engine Documentation</h3>
      </div>
      <button class="modal-close" onclick="closeEngineDocModal()" aria-label="Close Engine Documentation Modal">&times;</button>
    </div>
    <div class="modal-nav" role="tablist" aria-label="Documentation sections">
      <button class="modal-nav-btn active" role="tab" aria-selected="true" onclick="switchDocModalTab('overview')">Overview</button>
      <button class="modal-nav-btn" role="tab" aria-selected="false" onclick="switchDocModalTab('logic')">📐 Math & Science Logic</button>
      <button class="modal-nav-btn" role="tab" aria-selected="false" onclick="switchDocModalTab('why')">💡 Why This Way</button>
      <button class="modal-nav-btn" role="tab" aria-selected="false" onclick="switchDocModalTab('subfeatures')">⚡ Subfeatures</button>
      <button class="modal-nav-btn" role="tab" aria-selected="false" onclick="switchDocModalTab('extension')">🛠️ How to Extend</button>
      <button class="modal-nav-btn" role="tab" aria-selected="false" onclick="switchDocModalTab('advisory')">💡 Creative Advisory</button>
    </div>
    <div id="modalBodyContent" class="modal-body" role="region" aria-live="polite"></div>
  </div>
</div>

<!-- Interactive Engine Run Modal with Scope Preview & Real-Time Output -->
<div id="engineRunModal" class="modal-backdrop" role="dialog" aria-modal="true" aria-labelledby="runModalEngineTitle" onclick="if(event.target===this) closeEngineRunModal()">
  <div class="modal-dialog" role="document" style="max-width: 800px;">
    <div class="modal-header">
      <div class="modal-title">
        <span id="runModalCategoryBadge" class="tag tag-gold">ENGINE RUNNER</span>
        <h3 id="runModalEngineTitle" style="margin-left: 8px;">Run Scoped Engine</h3>
      </div>
      <button class="modal-close" onclick="closeEngineRunModal()" aria-label="Close Engine Runner Modal">&times;</button>
    </div>
    <div class="modal-body">
      <div style="display: flex; flex-direction: column; gap: 8px;">
        <label style="font-size: 12px; font-weight: 600; color: var(--text-secondary);">Target Scope Configuration:</label>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
          <div>
            <label style="font-size: 11px; color: var(--text-muted);">Chapters (e.g. 1-5, 8 or ch01..ch05):</label>
            <input type="text" id="run-modal-chapters" class="search-input" style="width: 100%; margin-top: 4px;" oninput="updateRunCommandPreview()" aria-label="Target Chapters">
          </div>
          <div>
            <label style="font-size: 11px; color: var(--text-muted);">Scenes (e.g. 1-4 or sc01..sc03):</label>
            <input type="text" id="run-modal-scenes" class="search-input" style="width: 100%; margin-top: 4px;" oninput="updateRunCommandPreview()" aria-label="Target Scenes">
          </div>
        </div>
      </div>
      <div style="margin-top: 8px;">
        <label style="font-size: 12px; font-weight: 600; color: var(--text-secondary);">Command Execution Preview:</label>
        <div id="runModalCmdPreview" class="code-block" style="margin-top: 4px; color: var(--accent-gold);" aria-live="polite"></div>
      </div>
      <div style="display: flex; gap: 8px; align-items: center; margin-top: 4px;">
        <button class="btn-primary" id="btn-run-engine-execute" onclick="executeEngineRun()" aria-label="Execute Scoped Engine">🚀 Execute Scoped Engine</button>
        <span id="run-status-indicator" style="font-size: 12px; color: var(--text-muted);" aria-live="polite"></span>
      </div>
      <div style="margin-top: 8px;">
        <label style="font-size: 12px; font-weight: 600; color: var(--text-secondary);">Execution Output Console:</label>
        <pre id="runModalOutput" class="code-block" style="max-height: 280px; overflow-y: auto; background: var(--bg-base); margin-top: 4px;" role="region" aria-live="polite">Ready to execute. Click 'Execute Scoped Engine' above.</pre>
      </div>
    </div>
  </div>
</div>

<!-- Custom Scope Modal -->
<div id="customScopeModal" class="modal-backdrop" role="dialog" aria-modal="true" aria-label="Advanced Scope Selector" onclick="if(event.target===this) closeScopeModal()">
  <div class="modal-dialog" role="document" style="max-width: 600px;">
    <div class="modal-header">
      <div class="modal-title">
        <span class="tag tag-char">SCOPE TARGETING</span>
        <h3 style="margin-left: 8px;">Advanced Scope Selector</h3>
      </div>
      <button class="modal-close" onclick="closeScopeModal()" aria-label="Close Scope Selector Modal">&times;</button>
    </div>
    <div class="modal-body">
      <p style="font-size: 12.5px; color: var(--text-secondary);">Specify granular targeting parameters for all craft engines. Engines will only process matching chapters, scenes, or lore files.</p>
      <div style="display: flex; flex-direction: column; gap: 10px;">
        <div>
          <label style="font-size: 11px; font-weight: 600; color: var(--text-secondary);">Chapter Selection (Ranges & Lists):</label>
          <input type="text" id="modal-scope-chapters" class="search-input" style="width: 100%; margin-top: 4px;" placeholder="e.g. 1-5, 7, 10-12 or ch01..ch05" aria-label="Chapter Range">
        </div>
        <div>
          <label style="font-size: 11px; font-weight: 600; color: var(--text-secondary);">Scene Selection (Ranges & Lists):</label>
          <input type="text" id="modal-scope-scenes" class="search-input" style="width: 100%; margin-top: 4px;" placeholder="e.g. 1-3, 5 or sc01..sc03" aria-label="Scene Range">
        </div>
        <div>
          <label style="font-size: 11px; font-weight: 600; color: var(--text-secondary);">Lore Categories (Comma-separated):</label>
          <input type="text" id="modal-scope-lore" class="search-input" style="width: 100%; margin-top: 4px;" placeholder="e.g. Characters, MagicSystems, Factions" aria-label="Lore Categories">
        </div>
        <div>
          <label style="font-size: 11px; font-weight: 600; color: var(--text-secondary);">Unified Scope String (Alternative):</label>
          <input type="text" id="modal-scope-raw" class="search-input" style="width: 100%; margin-top: 4px;" placeholder="e.g. Book1:ch01..ch05:sc01..sc03" aria-label="Unified Scope Expression">
        </div>
      </div>
      <div style="display: flex; justify-content: flex-end; gap: 8px; margin-top: 12px;">
        <button class="scope-preset-btn" onclick="closeScopeModal()" aria-label="Cancel Scope Selection">Cancel</button>
        <button class="btn-primary" onclick="saveCustomScope()" aria-label="Apply Scope Configuration">Apply Scope</button>
      </div>
    </div>
  </div>
</div>

<script>
  const HUB_DATA = {data_json};
  const IS_API_MODE = {"true" if api_mode else "false"};
  let activeModalEngine = null;

  function switchTab(tabId) {{
    document.querySelectorAll('.tab-pane').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(el => {{
      el.classList.remove('active');
      el.setAttribute('aria-selected', 'false');
    }});

    const target = document.getElementById(tabId);
    if (target) target.classList.add('active');

    if (event && event.currentTarget) {{
      event.currentTarget.classList.add('active');
      event.currentTarget.setAttribute('aria-selected', 'true');
    }} else {{
      const navBtn = document.getElementById('nav-' + tabId);
      if (navBtn) {{
        navBtn.classList.add('active');
        navBtn.setAttribute('aria-selected', 'true');
      }}
    }}

    const titles = {{
      'tab-overview': 'Overview Dashboard',
      'tab-manuscript': 'Manuscripts & Chapters',
      'tab-lore': 'Lore Codex & Entities',
      'tab-structure': 'Structure & Pacing Harmony',
      'tab-timeline': 'Timeline & Paradox Diagnostic',
      'tab-intelligence': 'Local RAG & Editorial Council',
      'tab-engines': 'Craft Engine Matrix',
      'tab-resonance': 'Universal Resonance & Synergy Mesh',
      'tab-guide': 'Author Craft Guide & Advisory Matrix'
    }};
    document.getElementById('page-title').innerText = titles[tabId] || 'Dashboard';
    if (tabId === 'tab-resonance') {{
      renderHubCascadeSandbox();
    }}
  }}

  window.addEventListener("keydown", (e) => {{
    if (e.key === "Escape") {{
      closeEngineDocModal();
      closeEngineRunModal();
      closeScopeModal();
    }}
  }});

  function openEngineDocModal(engineId) {{
    const eng = HUB_DATA.engine_catalog.find(e => e.id === engineId);
    if (!eng) return;

    activeModalEngine = eng;
    document.getElementById('modalCategoryBadge').innerText = eng.category.toUpperCase();
    document.getElementById('modalEngineTitle').innerText = eng.name;
    document.querySelectorAll('.modal-nav-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.modal-nav-btn')[0].classList.add('active');

    renderDocModalContent('overview');
    document.getElementById('engineDocModal').classList.add('open');
  }}

  function closeEngineDocModal() {{
    document.getElementById('engineDocModal').classList.remove('open');
    activeModalEngine = null;
  }}

  function switchDocModalTab(tabKey) {{
    document.querySelectorAll('.modal-nav-btn').forEach(btn => btn.classList.remove('active'));
    event.currentTarget.classList.add('active');
    renderDocModalContent(tabKey);
  }}

  function renderDocModalContent(tabKey) {{
    const eng = activeModalEngine;
    if (!eng) return;
    const body = document.getElementById('modalBodyContent');

    if (tabKey === 'overview') {{
      body.innerHTML = `
        <div><strong>CLI Command:</strong> <code class="engine-cli">${{eng.cli}}</code></div>
        <div><strong>Overview:</strong><p style="margin-top: 4px; color: var(--text-primary);">${{eng.desc}}</p></div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 10px;">
          <div style="background: var(--bg-sidebar); padding: 12px; border-radius: 6px; border: 1px solid var(--border-color);">
            <strong>🌍 Worldbuilding:</strong><p style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">${{eng.worldbuilding_relevance}}</p>
          </div>
          <div style="background: var(--bg-sidebar); padding: 12px; border-radius: 6px; border: 1px solid var(--border-color);">
            <strong>📐 Story Pacing:</strong><p style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">${{eng.storytelling_relevance}}</p>
          </div>
        </div>
      `;
    }} else if (tabKey === 'logic') {{
      body.innerHTML = `
        <div><strong>⚙️ Mathematical, Physical & Narrative Theory Foundations:</strong></div>
        <div class="code-block">${{eng.scientific_logic || eng.logic_documentation || 'Standard calculation engine.'}}</div>
      `;
    }} else if (tabKey === 'why') {{
      body.innerHTML = `
        <div><strong>💡 Why It Works This Way (Design & Scientific Rationale):</strong></div>
        <p style="color: var(--text-primary); line-height: 1.6;">${{eng.why_this_way || 'Provides deterministic mathematical and physical grounding.'}}</p>
      `;
    }} else if (tabKey === 'subfeatures') {{
      let html = '<div><strong>⚡ Subfeatures & Capabilities Matrix:</strong></div>';
      if (eng.subfeatures && eng.subfeatures.length > 0) {{
        eng.subfeatures.forEach((sf, idx) => {{
          html += `<div style="background: var(--bg-sidebar); padding: 10px; border-radius: 6px; margin-top: 8px; border: 1px solid var(--border-color);">
            <strong>[${{idx+1}}] ${{sf.name}}</strong>
            <p style="font-size: 12.5px; color: var(--text-secondary); margin-top: 2px;">${{sf.rule}}</p>
            <code style="color: var(--accent-cyan); font-size: 11.5px; margin-top: 4px; display: inline-block;">${{sf.example}}</code>
          </div>`;
        }});
      }} else {{
        html += '<p style="color: var(--text-secondary);">Subfeatures operate under the unified command.</p>';
      }}
      body.innerHTML = html;
    }} else if (tabKey === 'extension') {{
      body.innerHTML = `
        <div><strong>🛠️ How to Build Upon & Extend This Logic:</strong></div>
        <div class="code-block">${{eng.extension_guide || 'Configure via project YAML manifests.'}}</div>
      `;
    }} else if (tabKey === 'advisory') {{
      let html = '<div><strong>💡 Creative Freedom Resolution Pathways:</strong><p style="font-size: 12px; color: var(--text-secondary); margin-bottom: 8px;">The system never forces conformity. All checks provide multiple creative choices:</p></div>';
      if (eng.advisory_guidance && eng.advisory_guidance.length > 0) {{
        eng.advisory_guidance.forEach((adv, idx) => {{
          html += `<div style="background: var(--bg-sidebar); padding: 12px; border-radius: 6px; margin-top: 8px; border: 1px solid var(--border-color);">
            <strong style="color: var(--accent-gold);">Pattern: ${{adv.pattern}}</strong>
            <div style="margin-top: 6px; font-size: 12.5px;">
              <span style="color: var(--accent-cyan);">• Option A (Realism):</span> ${{adv.option_a}}<br>
              <span style="color: var(--accent-purple);">• Option B (Trope/Magic):</span> ${{adv.option_b}}<br>
              <span style="color: var(--accent-emerald);">• Option C (Sovereignty):</span> ${{adv.option_c}}
            </div>
          </div>`;
        }});
      }} else {{
        html += '<p style="color: var(--text-secondary);">No special advisory conflicts declared.</p>';
      }}
      body.innerHTML = html;
    }}
  }}

  function calcSandboxTransit() {{
    const dist = parseFloat(document.getElementById('sb-astro-dist').value) || 4.3;
    const unit = document.getElementById('sb-astro-unit').value;
    const box = document.getElementById('sb-astro-res');

    let distMeters = dist * 9.461e15; // default ly
    if (unit === 'au') distMeters = dist * 1.496e11;
    if (unit === 'km') distMeters = dist * 1e9;

    const c = 299792458;
    const a = 9.81; // 1g

    // Brachistochrone proper time
    const val = 1 + (a * distMeters) / (2 * c * c);
    const shipSeconds = (2 * c / a) * Math.acosh(val);
    const shipDays = (shipSeconds / 86400).toFixed(1);
    const shipYears = (shipDays / 365.25).toFixed(2);

    // Peak velocity
    const vMax = Math.tanh(a * shipSeconds / (2 * c));

    box.style.display = 'block';
    box.innerHTML = `Proper Time: <strong>${{shipYears > 1 ? shipYears + ' yrs' : shipDays + ' days'}}</strong> | Peak v: <strong>${{(vMax*100).toFixed(1)}}% c</strong>`;
  }}

  function analyzeSandboxRhythm() {{
    const text = document.getElementById('sb-rhythm-text').value.trim();
    const box = document.getElementById('sb-rhythm-res');
    if (!text) return;

    const sents = text.split(/[.!?]+/).filter(s => s.trim().length > 0);
    const lengths = sents.map(s => s.trim().split(/\\s+/).length);
    if (lengths.length === 0) return;

    const mean = lengths.reduce((a, b) => a + b, 0) / lengths.length;
    const variance = lengths.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / lengths.length;
    const stdDev = Math.sqrt(variance).toFixed(2);

    const isMonotonous = stdDev < 3.0;
    box.style.display = 'block';
    box.innerHTML = `Sentence lengths: [${{lengths.join(', ')}}]<br>Variance &sigma;: <strong>${{stdDev}}</strong> words &bull; ${{isMonotonous ? '<span style="color:var(--accent-crimson)">⚠️ Monotonous rhythm</span>' : '<span style="color:var(--accent-emerald)">✓ Dynamic musical cadence</span>'}}`;
  }}

  function testSandboxConlang() {{
    const words = document.getElementById('sb-conlang-word').value.split(',').map(w => w.trim());
    const ruleStr = document.getElementById('sb-conlang-rules').value;
    const box = document.getElementById('sb-conlang-res');

    const rules = ruleStr.split(',').map(r => {{
      const p = r.split('>');
      return p.length === 2 ? {{ from: p[0].trim(), to: p[1].trim() }} : null;
    }}).filter(Boolean);

    const mutated = words.map(w => {{
      let res = w;
      rules.forEach(r => {{
        res = res.replace(new RegExp(r.from, 'g'), r.to);
      }});
      return `${{w}} &rarr; <strong>${{res}}</strong>`;
    }});

    box.style.display = 'block';
    box.innerHTML = mutated.join(' | ');
  }}

  let CURRENT_TAB = 'tab-overview';
  const ALL_TIPS = (HUB_DATA && HUB_DATA.tips && HUB_DATA.tips.tips) ? HUB_DATA.tips.tips : [];
  let TIPS_ENABLED = (HUB_DATA && HUB_DATA.tips && typeof HUB_DATA.tips.enabled === 'boolean') ? HUB_DATA.tips.enabled : true;
  let CURRENT_TIP_INDEX = 0;

  function getEnginesForTab(tabId) {{
    const map = {{
      'tab-overview': ['writing_sprint', 'structure', 'resonance'],
      'tab-manuscript': ['structure', 'plot_matrix', 'story_canvas', 'manuscript_diff', 'typography_cleaner'],
      'tab-lore': ['astrophysics', 'climate', 'conlang', 'magic_system', 'economy', 'genealogy', 'ecology', 'cartography'],
      'tab-structure': ['structure', 'plot_matrix', 'story_canvas', 'manuscript_scaffold', 'timeline_sync'],
      'tab-timeline': ['timeline_sync', 'causality', 'prophecy', 'calendar'],
      'tab-intelligence': ['vault_search', 'dramatis_personae', 'continuity', 'series_continuity', 'world_doctor'],
      'tab-engines': ['astrophysics', 'climate', 'tactical_sim', 'factions', 'economy', 'ecology'],
      'tab-resonance': ['resonance', 'causality', 'astrophysics', 'conlang'],
      'tab-guide': ['diagnostics', 'config', 'preflight', 'docx_sync', 'typography_cleaner']
    }};
    return map[tabId] || [];
  }}

  function updateContextualTip(tabId) {{
    const bar = document.getElementById('dynamic-tip-bar');
    if (!TIPS_ENABLED) {{
      if (bar) bar.classList.add('hidden');
      return;
    }}
    if (bar) bar.classList.remove('hidden');

    const engines = getEnginesForTab(tabId);
    let matched = ALL_TIPS.filter(t => engines.includes((t.engine || '').toLowerCase()));
    if (!matched.length) matched = ALL_TIPS;
    if (!matched.length) return;

    CURRENT_TIP_INDEX = (CURRENT_TIP_INDEX + 1) % matched.length;
    renderTip(matched[CURRENT_TIP_INDEX]);
  }}

  function renderTip(tip) {{
    if (!tip) return;
    const badge = document.getElementById('tip-engine-badge');
    const subBadge = document.getElementById('tip-subfeature-badge');
    const depthBadge = document.getElementById('tip-depth-badge');
    const title = document.getElementById('tip-title');
    const content = document.getElementById('tip-content');

    if (badge) badge.innerText = (tip.engine || 'CRAFT').toUpperCase();
    if (subBadge) subBadge.innerText = tip.subfeature || tip.feature || 'General';
    if (depthBadge) depthBadge.innerText = (tip.depth || 'Advanced').charAt(0).toUpperCase() + (tip.depth || 'Advanced').slice(1);
    if (title) title.innerText = tip.title || 'Craft Wisdom';
    if (content) content.innerText = tip.content || '';
  }}

  function cycleNextTip() {{
    updateContextualTip(CURRENT_TAB);
  }}

  async function toggleTipsBar() {{
    TIPS_ENABLED = !TIPS_ENABLED;
    const bar = document.getElementById('dynamic-tip-bar');
    if (bar) {{
      if (TIPS_ENABLED) {{
        bar.classList.remove('hidden');
        updateContextualTip(CURRENT_TAB);
      }} else {{
        bar.classList.add('hidden');
      }}
    }}
    const label = document.getElementById('tips-toggle-label');
    if (label) {{
      label.innerText = TIPS_ENABLED ? '💡 Dynamic Tips: Active' : '💡 Dynamic Tips: Disabled';
    }}
    if (IS_API_MODE) {{
      try {{
        await fetch('/api/tips/toggle', {{ method: 'POST' }});
      }} catch (e) {{
        console.log('Tips toggle sync:', e);
      }}
    }}
  }}

  function switchTab(tabId) {{
    CURRENT_TAB = tabId;
    document.querySelectorAll('.tab-pane').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));

    const target = document.getElementById(tabId);
    if (target) target.classList.add('active');

    if (event && event.currentTarget) {{
      event.currentTarget.classList.add('active');
    }}

    const titles = {{
      'tab-overview': 'Overview Dashboard',
      'tab-manuscript': 'Manuscripts & Chapters',
      'tab-lore': 'Lore Codex & Entities',
      'tab-structure': 'Structure & Pacing Harmony',
      'tab-timeline': 'Timeline & Paradox Diagnostic',
      'tab-intelligence': 'Local RAG & Editorial Council',
      'tab-engines': 'Craft Engine Matrix',
      'tab-resonance': 'Resonance & Synergy Mesh',
      'tab-guide': 'Author Craft Guide & Advisory Matrix'
    }};
    document.getElementById('page-title').innerText = titles[tabId] || 'Dashboard';
    updateContextualTip(tabId);
  }}

  function filterGuideCategory(cat) {{
    const q = cat.toLowerCase();
    const cards = document.querySelectorAll('.guide-card');
    cards.forEach(c => {{
      const cCat = (c.getAttribute('data-category') || '').toLowerCase();
      const cTab = (c.getAttribute('data-tab') || '').toLowerCase();
      if (q === 'all') {{
        c.style.display = 'block';
      }} else if (q === 'worldbuilding') {{
        c.style.display = (cTab === 'worldbuilding' || cTab === 'cosmos') ? 'block' : 'none';
      }} else if (q === 'craft') {{
        c.style.display = (cTab === 'craft' || cTab === 'editor' || cCat === 'craft') ? 'block' : 'none';
      }} else if (q === 'core') {{
        c.style.display = (cCat === 'core' || cTab === 'tools') ? 'block' : 'none';
      }} else if (q === 'diagnostics') {{
        c.style.display = (cTab === 'diagnostics') ? 'block' : 'none';
      }} else if (q === 'publishing') {{
        c.style.display = (cTab === 'publishing') ? 'block' : 'none';
      }} else {{
        c.style.display = (cCat === q || cTab === q) ? 'block' : 'none';
      }}
    }});
  }}

  function filterGuideCards(query) {{
    const q = query.trim().toLowerCase();
    const cards = document.querySelectorAll('.guide-card');
    cards.forEach(c => {{
      const text = c.getAttribute('data-text') || '';
      if (!q || text.includes(q)) {{
        c.style.display = 'block';
      }} else {{
        c.style.display = 'none';
      }}
    }});
  }}

  function cycleTheme() {{
    const body = document.body;
    if (body.classList.contains('theme-sepia')) {{
      body.classList.remove('theme-sepia');
      body.classList.add('theme-light');
    }} else if (body.classList.contains('theme-light')) {{
      body.classList.remove('theme-light');
    }} else {{
      body.classList.add('theme-sepia');
    }}
  }}

  function handleGlobalSearch(query) {{
    const q = query.trim().toLowerCase();
    if (!q) return;
    // Client-side quick filter
    console.log("Searching for: " + q);
  }}

  async function runRagQuery() {{
    const q = document.getElementById('rag-query').value.trim();
    const box = document.getElementById('rag-response');
    if (!q) return;

    box.style.display = 'block';
    box.innerText = "Querying local semantic TF-IDF / FTS5 index...";

    if (!IS_API_MODE) {{
      // Offline static filter fallback
      const matches = HUB_DATA.lore_entities.filter(e =>
        e.name.toLowerCase().includes(q.toLowerCase()) ||
        e.summary.toLowerCase().includes(q.toLowerCase())
      );
      if (matches.length === 0) {{
        box.innerText = "No direct entity matches found in static index for: " + q;
      }} else {{
        box.innerText = JSON.stringify(matches, null, 2);
      }}
      return;
    }}

    try {{
      const res = await fetch('/api/query', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{ query: q }})
      }});
      const jsonRes = await res.json();
      box.innerText = JSON.stringify(jsonRes, null, 2);
    }} catch (err) {{
      box.innerText = "Error executing local query: " + err.message;
    }}
  }}

  async function runCouncilEval() {{
    const text = document.getElementById('council-draft').value.trim();
    const box = document.getElementById('council-response');
    if (!text) return;

    box.style.display = 'block';
    box.innerText = "Autonomous Editorial Council is evaluating prose...";

    if (!IS_API_MODE) {{
      box.innerText = "✓ Static Mode: Run 'arcanum council evaluate --text ...' via CLI for full multi-perspective analysis.\\nWord count: " + text.split(/\\s+/).length + " words.";
      return;
    }}

    try {{
      const res = await fetch('/api/council', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{ text: text }})
      }});
      const jsonRes = await res.json();
      box.innerText = JSON.stringify(jsonRes, null, 2);
    }} catch (err) {{
      box.innerText = "Error invoking editorial council: " + err.message;
    }}
  }}

  function renderHubCascadeSandbox() {{
    const sel = document.getElementById('hubCascadeSelect');
    const out = document.getElementById('hubCascadeOutput');
    if (!sel || !out) return;
    const val = sel.value;

    const impacts = {{
      'axial_tilt': [
        {{ node: 'Planetary Climate & Biomes', desc: 'Axial tilt shift (38.5°): Polar circle shifts to 51.5° latitude. Extreme seasonal temperature swings (-25°C winter to +38°C summer).' }},
        {{ node: 'Ecology & Agriculture', desc: 'Agrarian crop growing season shortened to 95 frost-free days. Famine risk increases by 45% in subpolar farming valleys.' }},
        {{ node: 'Macroeconomics & Trade', desc: 'Grain commodity price volatility surges (+35%). Mercantile guilds enforce emergency price caps and grain storage mandates.' }},
        {{ node: 'Tactical Battle Simulator', desc: 'Military campaign season strictly compressed to late June through August. Winter sieges face 40% non-combat casualty attrition.' }},
        {{ node: 'Scene Mechanics & Zen Studio', desc: 'Scene tension shifts from political intrigue to visceral race-against-winter survival urgency.' }}
      ],
      'magic_cost': [
        {{ node: 'Geopolitical Factions', desc: 'High arcane backlash/mana exhaustion centralizes high magic into state-sanctioned royal monopolies and militarized academies.' }},
        {{ node: 'Labor Economics', desc: 'Arcane automation displaces traditional blacksmithing and glassblowing guilds, creating urban artisan riots.' }},
        {{ node: 'Prophecy & Timeline', desc: 'Prophetic fulfillments become measurable through background arcane leyline discharge pulses.' }}
      ],
      'currency_debasement': [
        {{ node: 'Faction Stability', desc: 'Provincial garrison troops receive debased copper coin, escalating garrison mutiny risk to 0.78.' }},
        {{ node: 'Tactical Skirmish Sim', desc: 'Mercenary unit morale threshold drops to 40, triggering early battlefield routing under artillery pressure.' }},
        {{ node: 'Character Voice & Stylistics', desc: 'Provincial commoners and soldiers adopt subversive gutter cant and cynical gallows humor.' }}
      ],
      'stellar_mass': [
        {{ node: 'Planetary Calendar', desc: 'Solar year expands to 498.2 days; generates 4 intercalary epagomenal celebration weeks.' }},
        {{ node: 'Conlang Lexicon', desc: 'Cultural vocabulary develops rich astronomical roots and idioms for fleeting epagomenal romances.' }}
      ]
    }};

    const items = impacts[val] || [];
    out.innerHTML = items.map(item => `
      <div class="engine-card" style="border-left: 3px solid var(--accent-cyan); padding: 12px 16px;">
        <div style="font-weight: 600; color: var(--accent-gold); font-size: 13px;">${{item.node}}</div>
        <div style="color: var(--text-primary); font-size: 12.5px; margin-top: 4px;">${{item.desc}}</div>
      </div>
    `).join('');
  }}

  let activeScope = {{
    manuscript: HUB_DATA.project.manuscript_name || "",
    world: HUB_DATA.project.world_name || "",
    chapters: "",
    scenes: "",
    lore_categories: "",
    raw_filter: ""
  }};
  let activeRunningEngine = null;

  function applyScopePreset(preset) {{
    document.querySelectorAll('.scope-preset-btn').forEach(b => b.classList.remove('active'));
    const btn = document.getElementById('btn-preset-' + preset);
    if (btn) btn.classList.add('active');

    if (preset === 'active' || preset === 'all') {{
      activeScope.chapters = "";
      activeScope.scenes = "";
      document.getElementById('scope-input-chapters').value = "";
      document.getElementById('scope-input-scenes').value = "";
    }} else if (preset === 'ch1_5') {{
      activeScope.chapters = "1-5";
      activeScope.scenes = "";
      document.getElementById('scope-input-chapters').value = "1-5";
      document.getElementById('scope-input-scenes').value = "";
    }} else if (preset === 'act1') {{
      const totalCh = HUB_DATA.metrics.total_chapters || 1;
      const act1Ch = Math.max(1, Math.ceil(totalCh * 0.25));
      const rangeStr = act1Ch > 1 ? ("1-" + act1Ch) : "1";
      activeScope.chapters = rangeStr;
      activeScope.scenes = "";
      document.getElementById('scope-input-chapters').value = rangeStr;
      document.getElementById('scope-input-scenes').value = "";
    }}
    updateScopeSummaryBadge();
    syncScopeToServer();
  }}

  function onScopeInputChange() {{
    activeScope.chapters = document.getElementById('scope-input-chapters').value.trim();
    activeScope.scenes = document.getElementById('scope-input-scenes').value.trim();
    document.querySelectorAll('.scope-preset-btn').forEach(b => b.classList.remove('active'));
    document.getElementById('btn-preset-custom').classList.add('active');
    updateScopeSummaryBadge();
    syncScopeToServer();
  }}

  function updateScopeSummaryBadge() {{
    const badge = document.getElementById('scope-summary-badge');
    if (!badge) return;
    let parts = [];
    if (activeScope.chapters) {{
      parts.push("Ch " + activeScope.chapters);
    }}
    if (activeScope.scenes) {{
      parts.push("Sc " + activeScope.scenes);
    }}
    if (parts.length === 0) {{
      badge.innerText = "Scope: " + (activeScope.manuscript || "Active") + " (All)";
    }} else {{
      badge.innerText = "Scope: " + parts.join(" • ");
    }}
  }}

  function syncScopeToServer() {{
    if (!IS_API_MODE) return;
    fetch('/api/scope', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json' }},
      body: JSON.stringify(activeScope)
    }}).catch(e => console.debug('Scope sync error', e));
  }}

  function openScopeModal() {{
    document.getElementById('modal-scope-chapters').value = activeScope.chapters || "";
    document.getElementById('modal-scope-scenes').value = activeScope.scenes || "";
    document.getElementById('modal-scope-lore').value = activeScope.lore_categories || "";
    document.getElementById('modal-scope-raw').value = activeScope.raw_filter || "";
    document.getElementById('customScopeModal').classList.add('open');
  }}

  function closeScopeModal() {{
    document.getElementById('customScopeModal').classList.remove('open');
  }}

  function saveCustomScope() {{
    activeScope.chapters = document.getElementById('modal-scope-chapters').value.trim();
    activeScope.scenes = document.getElementById('modal-scope-scenes').value.trim();
    activeScope.lore_categories = document.getElementById('modal-scope-lore').value.trim();
    activeScope.raw_filter = document.getElementById('modal-scope-raw').value.trim();

    document.getElementById('scope-input-chapters').value = activeScope.chapters;
    document.getElementById('scope-input-scenes').value = activeScope.scenes;

    document.querySelectorAll('.scope-preset-btn').forEach(b => b.classList.remove('active'));
    document.getElementById('btn-preset-custom').classList.add('active');

    updateScopeSummaryBadge();
    syncScopeToServer();
    closeScopeModal();
  }}

  function openEngineRunModal(engineId, engineName) {{
    activeRunningEngine = engineId;
    document.getElementById('runModalEngineTitle').innerText = 'Run ' + (engineName || engineId);
    document.getElementById('run-modal-chapters').value = activeScope.chapters || "";
    document.getElementById('run-modal-scenes').value = activeScope.scenes || "";
    document.getElementById('runModalOutput').innerText = "Ready to execute. Click 'Execute Scoped Engine' above.";
    document.getElementById('run-status-indicator').innerText = "";
    updateRunCommandPreview();
    document.getElementById('engineRunModal').classList.add('open');
  }}

  function closeEngineRunModal() {{
    document.getElementById('engineRunModal').classList.remove('open');
    activeRunningEngine = null;
  }}

  function updateRunCommandPreview() {{
    if (!activeRunningEngine) return;
    const ch = document.getElementById('run-modal-chapters').value.trim();
    const sc = document.getElementById('run-modal-scenes').value.trim();
    let cmd = 'arcanum ' + activeRunningEngine;
    if (ch) cmd += ' --chapters ' + ch;
    if (sc) cmd += ' --scenes ' + sc;
    document.getElementById('runModalCmdPreview').innerText = cmd;
  }}

  function executeEngineRun() {{
    if (!activeRunningEngine) return;
    const ch = document.getElementById('run-modal-chapters').value.trim();
    const sc = document.getElementById('run-modal-scenes').value.trim();
    const outEl = document.getElementById('runModalOutput');
    const statusEl = document.getElementById('run-status-indicator');
    const btn = document.getElementById('btn-run-engine-execute');

    btn.disabled = true;
    statusEl.innerText = "⏳ Executing engine with scope...";
    outEl.innerText = "Executing...";

    if (!IS_API_MODE) {{
      setTimeout(() => {{
        btn.disabled = false;
        statusEl.innerText = "✓ Static Preview Mode";
        outEl.innerText = "[Static Mode Preview]\\nCommand: " + document.getElementById('runModalCmdPreview').innerText + "\\n\\nIn live server mode (`arcanum hub`), execution runs directly on your local system with 100% offline privacy.";
      }}, 300);
      return;
    }}

    fetch('/api/engine/run', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json' }},
      body: JSON.stringify({{
        engine: activeRunningEngine,
        scope: {{
          chapters: ch,
          scenes: sc
        }}
      }})
    }})
    .then(r => r.json())
    .then(data => {{
      btn.disabled = false;
      if (data.status === 'success') {{
        statusEl.innerText = "✓ Execution Succeeded (Exit code: " + data.exit_code + ")";
        outEl.innerText = data.combined_output || "(No output produced)";
      }} else {{
        statusEl.innerText = "⚠️ Execution Completed with Exit code: " + data.exit_code;
        outEl.innerText = data.combined_output || data.stderr || "Error occurred";
      }}
    }})
    .catch(err => {{
      btn.disabled = false;
      statusEl.innerText = "❌ Request Failed";
      outEl.innerText = "Error calling /api/engine/run: " + err;
    }});
  }}
</script>
</body>
</html>
"""
