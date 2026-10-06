#!/usr/bin/env python3
"""
Ars Arcanum Standalone Offline Zen Drafting Studio & In-Situ Lore Inspector
(scripts/lib/zen_studio.py)
================================================================================
Zero-dependency, offline single-file interactive HTML5 writing environment
combining distraction-free typewriter drafting with an in-situ World Bible
lore inspector, live document metadata editor with real-time two-way frontmatter
synchronization, multi-tier outline drawer (Floating, Book, and Series outlines),
multi-paradigm structural beat tracker, and sovereign browser persistence.

Capabilities:
1. Distraction-Free Typewriter Drafting:
   - Centered typography, dark/sepia/light themes, typewriter soundscape and scrolling.
   - Live prose telemetry: word count, reading time (200 wpm), speech duration (150 wpm).
2. In-Situ Document Metadata Inspector:
   - Side panel with real-time two-way frontmatter sync (editing panel updates YAML
     frontmatter in prose without losing cursor or scroll position; editing frontmatter
     in prose reactively updates the panel).
   - Fields: Title, POV Character, Location, Cast in Scene, Plot Thread, Timeline Day,
     Drafting Status, Target Words with live progress bar, and Scene Synopsis / Notes.
3. Multi-Tier Narrative Outline Drawer:
   - 3-tier selector for Floating Scratchpad Outline (live editable beat notes per chapter
     with insert-into-prose actions), Book Master Outline (parsed acts, milestones, and
     jump-to-scene links), and Series Universe Outline (multi-volume arc chronicles).
4. Ergonomic Workspace Controls:
   - Independent Expand (320px ↔ 480px), Collapse (compact rail), and Close (✕) controls
     for all side panels, with workspace state persistence across reloads.
   - Global keyboard shortcuts (Ctrl+M, Ctrl+O, Ctrl+B, Ctrl+L, Ctrl+P, Ctrl+S).
5. In-Situ World Bible Lore Drawer:
   - Searchable character dossiers, faction allegiances, locations, magic rules, sparks,
     and craft tips.
6. Sovereign Local Persistence:
   - LocalStorage auto-save, per-chapter draft backups, and one-click markdown export.

Zero external dependencies; 100% offline privacy.
"""

from __future__ import annotations

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
            if part in (
                "Characters", "Locations", "Factions", "MagicSystems",
                "Magic-Technology", "History", "Bestiary", "Cosmology", "Languages"
            ):
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


def scan_outlines(ms_path: Path | None, world_path: Path | None = None) -> dict[str, Any]:
    """Discovers and parses master, series, and floating outline structures."""
    candidate_dirs: list[Path] = []
    if ms_path:
        if ms_path.is_file():
            candidate_dirs.extend([ms_path.parent, ms_path.parent / "Outlines", ms_path.parent.parent / "Outlines"])
        else:
            candidate_dirs.extend([ms_path, ms_path / "Outlines", ms_path.parent / "Outlines", ms_path.parent])

    # Also search project templates if running inside repository
    repo_template_outlines = Path(__file__).resolve().parent.parent.parent / "templates" / "manuscript" / "Outlines"
    if repo_template_outlines.exists():
        candidate_dirs.append(repo_template_outlines)

    book_outline_text = ""
    book_outline_title = "Master Story Outline"
    series_outline_text = ""
    series_outline_title = "Series Universe Chronicle"
    discovered_files: list[dict[str, str]] = []

    seen_files: set[Path] = set()
    for c_dir in candidate_dirs:
        if not c_dir.exists():
            continue
        for p in sorted(c_dir.glob("*.md")):
            if p in seen_files or p.name.startswith("."):
                continue
            seen_files.add(p)
            name_lower = p.name.lower()
            if "master" in name_lower or ("outline" in name_lower and "series" not in name_lower and not book_outline_text):
                try:
                    book_outline_text = p.read_text(encoding="utf-8", errors="replace")
                    book_outline_title = p.stem.replace("-", " ").title()
                except Exception:
                    pass
            elif "series" in name_lower or "omnibus" in name_lower:
                try:
                    series_outline_text = p.read_text(encoding="utf-8", errors="replace")
                    series_outline_title = p.stem.replace("-", " ").title()
                except Exception:
                    pass

            discovered_files.append({
                "name": p.name,
                "title": p.stem.replace("-", " ").title(),
                "path": str(p),
            })

    # Default fallback book outline blueprint if none present on disk
    if not book_outline_text:
        book_outline_text = """# Master Story Outline & Structural Blueprint

## 1. High Concept & Logline
- **Logline**: When an ancient treaty seal is broken, a disgraced border guardian must master forgotten elemental arts to avert continental war.
- **Central Theme**: True sovereignty arises from transparent empathy, not enforced silence.
- **Target Word Count**: 90,000 words (4 Acts, 24 Chapters)

---

## 2. Multi-Act Milestone Matrix
- **ACT I: The Ordinary World & Call to Adventure (0% – 25% | ~22,500 words)**
  - *01. Hook & Ordinary World (0% - 10%)*: Introduce protagonist flaw, environment, and initial stakes.
  - *02. Inciting Incident (12%)*: Unforeseen catalyst breaks normal life; choice demanded.
  - *03. Plot Point 1 / Threshold Crossing (25%)*: Irreversible commitment to enter the new world.
- **ACT II-A: Rising Trials & Allies (25% – 50% | ~22,500 words)**
  - *04. Fun and Games / Promise of the Premise (30% - 40%)*: Exploration of new powers, skills, and factions.
  - *05. First Pinch Point (37%)*: Reminder of antagonistic force; stakes raised.
  - *06. Midpoint Shift (50%)*: Shift from reactive defense to proactive pursuit; false victory/defeat.
- **ACT II-B: Bad Guys Close In & Crisis (50% – 75% | ~22,500 words)**
  - *07. Second Pinch Point (62%)*: Antagonists push back harder; cracks in the team's plan.
  - *08. All Hope Is Lost / Dark Night of the Soul (75%)*: The lowest point; old methods fail completely.
- **ACT III: Climax & Resolution (75% – 100% | ~22,500 words)**
  - *09. Epiphany & Mobilization (80%)*: The thematic insight that unlocks the true solution.
  - *10. Climax Showdown (90%)*: Ultimate direct confrontation confronting core conflict.
  - *11. Resolution / Denouement (98% - 100%)*: New equilibrium established and future hinted.
"""

    if not series_outline_text:
        series_outline_text = """# Series Master Universe Chronicle

## Multi-Volume Narrative Trajectory

### 📖 Book 1: The Spark of Rebellion
- **Core Mystery**: Theft of the First Primordial Codex.
- **Protagonist Arc**: From obedient archivist to self-reliant truth-seeker.
- **Climax**: Destruction of the Sunken Spire; declaration of martial law.
- **Status**: Active Drafting / First Polish.

### 📖 Book 2: The Shattered Alliances
- **Core Mystery**: Infiltration of the High Citadel Senate.
- **Protagonist Arc**: Navigating ruthless political factions and betrayal of a mentor.
- **Climax**: The Siege of Aethelgard; severance of the ley lines.
- **Status**: Structured Beat Outline.

### 📖 Book 3: The Sovereign Horizon
- **Core Mystery**: Origin of the World-Wound and the Primordial Creators.
- **Protagonist Arc**: Uniting disparate species under a new cosmological covenant.
- **Climax**: Convergence of the Celestial Spheres; final restoration.
- **Status**: Concept Matrix.
"""

    floating_templates = [
        {
            "id": "three_act_scene",
            "name": "Three-Act Scene Beat",
            "text": "### 🎯 Scene Goal & Status Quo\n- **Objective**: What does the POV character want entering this scene?\n- **Obstacle**: What immediate barrier or conflict prevents it?\n\n### ⚡ Escalation & Tipping Point\n- **Complication**: An unexpected revelation or hostile counter-move.\n- **Action/Reaction**: Protagonist makes a costly tactical decision.\n\n### 💥 Outcome & Aftermath\n- **Disaster / Shift**: 'Yes, but...' or 'No, and furthermore...'\n- **Next Hook**: What question or goal pulls into the following scene?\n",
        },
        {
            "id": "mru_sequence",
            "name": "MRU Causal Beat (Swain)",
            "text": "### 1. External Stimulus\n- What event occurs outside the character's body (sight, sound, attack)?\n\n### 2. Involuntary Reflex\n- Immediate physical response (flinch, gasp, pupil dilation, heart spike).\n\n### 3. Emotion / Instinctive Reaction\n- Gut fear, surge of anger, or instinctual dread before reason sets in.\n\n### 4. Rational Thought & Action\n- Conscious tactical calculation followed by deliberate physical movement.\n\n### 5. Spoken Word / Response\n- Verbal dialogue or command emitted after action.\n",
        },
        {
            "id": "dialogue_debate",
            "name": "Dialogue & Subtext Clash",
            "text": "### 🗣️ Surface Topic vs. Subtext Agenda\n- **Surface Topic**: What are the characters pretending to discuss?\n- **Subtext Agenda**: What hidden leverage, secret, or emotional wound is at play?\n\n### ⚖️ Power Dynamic Shift\n- Who starts in control? What pivot sentence flips the leverage?\n\n### 🚪 Exit Beat & Lingering Tension\n- How does the conversation terminate before total comfort is restored?\n",
        },
        {
            "id": "action_skirmish",
            "name": "Action / Combat Skirmish",
            "text": "### ⚔️ Spatial Awareness & Stakes\n- Terrain layout, lighting, line of sight, environmental hazards.\n\n### 🛡️ Tactical Exchange\n- Attack, defensive counter, sensory impact (heat, shockwave, ringing ears).\n\n### 🩸 Consequence & Momentum\n- Physical injury, resource exhaustion, change in ground control.\n",
        },
    ]

    return {
        "book_outline": {
            "title": book_outline_title,
            "raw": book_outline_text,
        },
        "series_outline": {
            "title": series_outline_title,
            "raw": series_outline_text,
        },
        "floating_templates": floating_templates,
        "discovered_files": discovered_files,
    }


def build_zen_studio_bundle(
    ms_path: Path,
    world_path: Path | None = None,
    output_path: Path | None = None,
    scope: EngineScope | None = None,
) -> Path:
    """Compiles manuscript files, lore, and outlines into an offline interactive Zen studio HTML file."""
    chapters: list[dict[str, Any]] = []
    if scope and (scope.chapters or scope.scenes or scope.manuscript or scope.book):
        scoped_chaps, _, _ = filter_manuscript_scope(ms_path, scope)
        for idx, ch in enumerate(scoped_chaps, 1):
            body = ch.content
            fm = parse_yaml_frontmatter(body)
            body_clean = FRONTMATTER_REGEX.sub("", body).strip()
            word_count = len(re.findall(r"\b\w+\b", body_clean))

            # Normalized metadata structure
            pov = str(fm.get("pov", fm.get("pov_character", "")))
            location = str(fm.get("location", fm.get("setting", "")))
            cast_raw = fm.get("characters", fm.get("cast", fm.get("char", [])))
            cast = ", ".join(cast_raw) if isinstance(cast_raw, list) else str(cast_raw or "")
            thread = str(fm.get("plot_threads", fm.get("plot_thread", fm.get("thread", ""))))
            time_marker = str(fm.get("time_marker", fm.get("time", fm.get("timeline_day", ""))))
            status = str(fm.get("status", "Draft"))
            target_words = int(fm.get("target_words", fm.get("target_word_count", 2500)) or 2500)
            synopsis = str(fm.get("synopsis", fm.get("summary", fm.get("notes", ""))))
            tags_raw = fm.get("tags", [])
            tags = ", ".join(tags_raw) if isinstance(tags_raw, list) else str(tags_raw or "")

            chapters.append({
                "id": f"chap_{idx}",
                "filename": ch.file_path.name,
                "title": ch.title,
                "frontmatter": fm,
                "metadata": {
                    "title": ch.title,
                    "pov": pov,
                    "location": location,
                    "cast": cast,
                    "thread": thread,
                    "time": time_marker,
                    "status": status,
                    "target_words": target_words,
                    "synopsis": synopsis,
                    "tags": tags,
                },
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
            title = str(fm.get("title", h1.group(1).strip() if h1 else f.stem.replace("_", " ").title()))
            word_count = len(re.findall(r"\b\w+\b", body))

            pov = str(fm.get("pov", fm.get("pov_character", "")))
            location = str(fm.get("location", fm.get("setting", "")))
            cast_raw = fm.get("characters", fm.get("cast", fm.get("char", [])))
            cast = ", ".join(cast_raw) if isinstance(cast_raw, list) else str(cast_raw or "")
            thread = str(fm.get("plot_threads", fm.get("plot_thread", fm.get("thread", ""))))
            time_marker = str(fm.get("time_marker", fm.get("time", fm.get("timeline_day", ""))))
            status = str(fm.get("status", "Draft"))
            target_words = int(fm.get("target_words", fm.get("target_word_count", 2500)) or 2500)
            synopsis = str(fm.get("synopsis", fm.get("summary", fm.get("notes", ""))))
            tags_raw = fm.get("tags", [])
            tags = ", ".join(tags_raw) if isinstance(tags_raw, list) else str(tags_raw or "")

            chapters.append({
                "id": f"chap_{idx}",
                "filename": f.name,
                "title": title,
                "frontmatter": fm,
                "metadata": {
                    "title": title,
                    "pov": pov,
                    "location": location,
                    "cast": cast,
                    "thread": thread,
                    "time": time_marker,
                    "status": status,
                    "target_words": target_words,
                    "synopsis": synopsis,
                    "tags": tags,
                },
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

    outlines_data = scan_outlines(ms_path if ms_path.exists() else None, world_path=world_path)
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
    outlines_json = json.dumps(outlines_data).replace("</", "<\\/")
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

  * {{ box-sizing: border-box; }}
  body {{
    font-family: Georgia, 'Times New Roman', serif; background: var(--bg); color: var(--text);
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
<body data-theme="slate">

<header>
  <div class="brand-title">
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
    <button id="btnSidebar" onclick="toggleSidebar()" title="Toggle Chapters Sidebar (Ctrl+B)">📁 Files</button>
    <button id="btnMeta" onclick="toggleMetaPanel()" title="Toggle Document Metadata Inspector (Ctrl+M)">📋 Metadata</button>
    <button id="btnOutline" onclick="toggleOutlinePanel()" title="Toggle Multi-Tier Outline Drawer (Ctrl+O)">🗺️ Outline</button>
    <button id="btnPreview" onclick="toggleSplitPreview()" title="Live Scene Tag & Markdown Inspector (Ctrl+P)">👁️ Preview: Off</button>
    <button id="btnLore" onclick="toggleLoreDrawer()" title="World Lore Drawer (Ctrl+L)">📜 Lore ({len(lore_entities)})</button>
    <button class="btn-gold" onclick="openCraftModal()">💡 Craft Logic</button>
    <button class="btn-accent" onclick="exportMarkdown()" title="Export Active Chapter Markdown (Ctrl+S)">💾 Download</button>
  </div>
</header>

<div class="main-workspace">
  <!-- Left Column: Chapters Sidebar -->
  <div class="sidebar" id="sidebar">
    <div class="side-panel-header">
      <span class="panel-title-text">Manuscript Chapters</span>
      <div class="panel-header-actions">
        <button class="btn-tool-action" onclick="toggleSidebar()" title="Close Sidebar">✕</button>
      </div>
    </div>
    <ul class="chap-list" id="chapList"></ul>
  </div>

  <!-- In-Situ Document Metadata Inspector Side Panel -->
  <div class="side-panel" id="metaPanel">
    <div class="side-panel-header">
      <div style="display:flex;align-items:center;gap:0.4rem;">
        <span>📋</span>
        <span class="panel-title-text">Document Metadata</span>
      </div>
      <div class="panel-header-actions">
        <button class="btn-tool-action" id="btnMetaExpand" onclick="togglePanelExpand('metaPanel')" title="Toggle Width (Compact / Wide)">🗗</button>
        <button class="btn-tool-action" id="btnMetaCollapse" onclick="togglePanelCollapse('metaPanel')" title="Collapse Panel">▾</button>
        <button class="btn-tool-action" onclick="closePanel('metaPanel')" title="Close Metadata Inspector">✕</button>
      </div>
    </div>

    <div class="side-panel-body" id="metaPanelBody">
      <div class="meta-sync-badge">
        <span class="sync-pulse"></span>
        <span>Real-time frontmatter 2-way sync active</span>
      </div>

      <div class="meta-field">
        <label>Scene / Chapter Title</label>
        <input type="text" id="metaTitle" placeholder="Title of active scene..." oninput="handleMetadataInput('title', this.value)">
      </div>

      <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem;">
        <div class="meta-field">
          <label>POV Character (@pov)</label>
          <input type="text" id="metaPov" placeholder="Primary POV..." oninput="handleMetadataInput('pov', this.value)">
        </div>
        <div class="meta-field">
          <label>Drafting Status</label>
          <select id="metaStatus" onchange="handleMetadataInput('status', this.value)">
            <option value="Draft">Draft</option>
            <option value="Revision">Revision</option>
            <option value="First Polish">First Polish</option>
            <option value="Final">Final</option>
          </select>
        </div>
      </div>

      <div class="meta-field">
        <label>Setting / Location (@location)</label>
        <input type="text" id="metaLocation" placeholder="Specific scene locale..." oninput="handleMetadataInput('location', this.value)">
      </div>

      <div class="meta-field">
        <label>Cast Present in Scene (@char)</label>
        <input type="text" id="metaCast" placeholder="Characters present (comma separated)..." oninput="handleMetadataInput('characters', this.value)">
      </div>

      <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem;">
        <div class="meta-field">
          <label>Plot Thread (@thread)</label>
          <input type="text" id="metaThread" placeholder="A-Plot, B-Plot..." oninput="handleMetadataInput('plot_thread', this.value)">
        </div>
        <div class="meta-field">
          <label>Timeline / Day (@time)</label>
          <input type="text" id="metaTime" placeholder="Day 14 - Dusk..." oninput="handleMetadataInput('time_marker', this.value)">
        </div>
      </div>

      <div class="meta-field">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <label>Target Words</label>
          <span id="metaTargetProgressLabel" style="font-size:0.75rem;color:var(--accent);">0 / 2,500 w (0%)</span>
        </div>
        <input type="number" id="metaTargetWords" min="100" step="100" value="2500" oninput="handleMetadataInput('target_words', parseInt(this.value)||2500)">
        <div class="progress-wrap" style="margin-top:0.25rem;">
          <div class="progress-bar-bg">
            <div class="progress-bar-fill" id="metaWordProgressBar"></div>
          </div>
        </div>
      </div>

      <div class="meta-field">
        <label>Scene Synopsis & Intent</label>
        <textarea id="metaSynopsis" rows="3" placeholder="Brief scene objective, conflict, and key turning point..." oninput="handleMetadataInput('synopsis', this.value)"></textarea>
      </div>

      <div class="meta-field">
        <label>Tags & Categories</label>
        <input type="text" id="metaTags" placeholder="climax, magic-duel, politics..." oninput="handleMetadataInput('tags', this.value)">
      </div>

      <div style="display:flex;gap:0.5rem;margin-top:0.25rem;">
        <button onclick="refreshMetadataFromEditor()" style="flex:1;font-size:0.75rem;">🔄 Refresh from Doc</button>
        <button onclick="formatDocumentFrontmatter()" style="flex:1;font-size:0.75rem;">🧹 Clean Header</button>
      </div>
    </div>
  </div>

  <!-- Center Drafting Canvas Area -->
  <div class="editor-area">
    <div class="editor-container">
      <textarea class="zen-editor" id="editor" placeholder="Write your prose here..." oninput="handleEditorInput()" onkeydown="handleKeyDown(event)"></textarea>
    </div>
    <div class="preview-pane" id="previewPane">
      <div style="font-weight:600;color:var(--accent);margin-bottom:0.75rem;border-bottom:1px solid var(--border);padding-bottom:0.4rem;display:flex;justify-content:space-between;">
        <span>🔍 Live Markdown & Scene Tag Inspector</span>
        <button class="btn-tool-action" onclick="toggleSplitPreview()">✕</button>
      </div>
      <div id="previewContent"></div>
    </div>
  </div>

  <!-- Multi-Tier Narrative Outline Drawer -->
  <div class="side-panel right-dock" id="outlinePanel">
    <div class="side-panel-header">
      <div style="display:flex;align-items:center;gap:0.4rem;">
        <span>🗺️</span>
        <span class="panel-title-text">Narrative Outlines</span>
      </div>
      <div class="panel-header-actions">
        <button class="btn-tool-action" id="btnOutlineExpand" onclick="togglePanelExpand('outlinePanel')" title="Toggle Width (Compact / Wide)">🗗</button>
        <button class="btn-tool-action" id="btnOutlineCollapse" onclick="togglePanelCollapse('outlinePanel')" title="Collapse Panel">▾</button>
        <button class="btn-tool-action" onclick="closePanel('outlinePanel')" title="Close Outline Drawer">✕</button>
      </div>
    </div>

    <div class="outline-tabs">
      <button class="o-tab active" id="tabBtnFloating" onclick="switchOutlineTab('floating')">📝 Floating</button>
      <button class="o-tab" id="tabBtnBook" onclick="switchOutlineTab('book')">📖 Book</button>
      <button class="o-tab" id="tabBtnSeries" onclick="switchOutlineTab('series')">🌌 Series</button>
    </div>

    <div class="side-panel-body" id="outlinePanelBody">
      <!-- Tier 1: Floating Scratchpad Outline -->
      <div id="paneFloatingOutline" style="display:flex;flex-direction:column;gap:0.75rem;flex:1;">
        <div style="display:flex;gap:0.5rem;align-items:center;">
          <select id="floatingTemplateSelect" style="flex:1;font-size:0.8rem;">
            <!-- Populated dynamically -->
          </select>
          <button onclick="applyFloatingTemplate()" title="Load selected beat template" style="font-size:0.8rem;">📋 Load</button>
        </div>

        <textarea id="floatingOutlineText" style="flex:1;min-height:220px;padding:0.6rem;font-family:system-ui,sans-serif;font-size:0.85rem;line-height:1.5;resize:vertical;" placeholder="Jot down active scene beats, checklist points, and scratchpad notes..." oninput="handleFloatingOutlineChange(this.value)"></textarea>

        <div style="display:flex;gap:0.5rem;">
          <button class="btn-accent" onclick="insertFloatingBeatToEditor()" style="flex:1;font-size:0.8rem;" title="Insert scratchpad beats at current prose cursor position">➕ Insert into Draft</button>
          <button onclick="clearFloatingOutline()" style="font-size:0.8rem;">🗑️ Clear</button>
        </div>
      </div>

      <!-- Tier 2: Book Master Outline -->
      <div id="paneBookOutline" style="display:none;flex-direction:column;gap:0.75rem;">
        <div class="lore-search" style="padding:0;border:none;">
          <input type="text" id="bookOutlineQuery" placeholder="Search book acts, milestones, beats..." oninput="filterBookOutline(this.value)">
        </div>
        <div id="bookOutlineContent" style="display:flex;flex-direction:column;gap:0.6rem;"></div>
      </div>

      <!-- Tier 3: Series Universe Outline -->
      <div id="paneSeriesOutline" style="display:none;flex-direction:column;gap:0.75rem;">
        <div class="lore-search" style="padding:0;border:none;">
          <input type="text" id="seriesOutlineQuery" placeholder="Search series volumes, arcs, reveals..." oninput="filterSeriesOutline(this.value)">
        </div>
        <div id="seriesOutlineContent" style="display:flex;flex-direction:column;gap:0.6rem;"></div>
      </div>
    </div>
  </div>

  <!-- Right Lore Drawer -->
  <div class="lore-drawer" id="loreDrawer">
    <div class="side-panel-header">
      <div style="display:flex;align-items:center;gap:0.4rem;">
        <span>📜</span>
        <span>World Bible Lore</span>
      </div>
      <div class="panel-header-actions">
        <button class="btn-tool-action" onclick="toggleLoreDrawer()" title="Close Lore Drawer">✕</button>
      </div>
    </div>
    <div class="drawer-tabs">
      <button class="d-tab active" id="tabBtnLore" onclick="switchDrawerTab('lore')">📜 Lore</button>
      <button class="d-tab" id="tabBtnRules" onclick="switchDrawerTab('rules')">📐 Rules</button>
      <button class="d-tab" id="tabBtnSparks" onclick="switchDrawerTab('sparks')">💡 Sparks</button>
      <button class="d-tab" id="tabBtnTips" onclick="switchDrawerTab('tips')">💡 Tips</button>
    </div>
    <div class="lore-search">
      <input type="text" id="loreQuery" placeholder="Search characters, locations, rules, tips..." oninput="filterDrawer(this.value)">
    </div>
    <div class="lore-list" id="loreList"></div>
  </div>
</div>

<!-- Telemetry Footer -->
<footer class="telemetry">
  <div>
    <span id="telWords">0 words</span> | <span id="telChars">0 chars</span>
  </div>
  <div id="zenTipBar" style="color:var(--gold);cursor:pointer;max-width:520px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;" onclick="cycleZenTip()" title="Click for next craft wisdom tip">
    💡 <span id="zenTipText">Loading craft wisdom...</span>
  </div>
  <div>
    📖 Reading: <span id="telReadTime">0 min</span> | 🎙️ Narration: <span id="telSpeakTime">0 min</span> | <span id="telSaveStatus">Autosaved</span>
  </div>
</footer>

<!-- Craft Engine Modal -->
<div class="craft-modal" id="craftModal" onclick="if(event.target===this)closeCraftModal()">
  <div class="craft-modal-content">
    <div class="craft-modal-header">
      <div>
        <span style="font-weight:700;font-size:1.1rem;color:var(--accent);">💡 Ars Arcanum Craft & Engine Encyclopedia</span>
        <div style="font-size:0.8rem;color:var(--muted);margin-top:2px;">50 Verified Engines • Mathematical Logic • Narrative Physics • Extension Guides</div>
      </div>
      <button onclick="closeCraftModal()" style="font-size:1.2rem;line-height:1;background:transparent;border:none;color:var(--muted);cursor:pointer;">✕</button>
    </div>
    <div class="lore-search" style="background:var(--panel-alt);padding:0.75rem 1.5rem;">
      <input type="text" id="modalEngineSearch" placeholder="Search any engine, formula, or craft principle..." oninput="filterModalEngines(this.value)">
    </div>
    <div class="craft-modal-body" id="modalEngineList"></div>
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

  /* ---------------- Theme & Sound ---------------- */
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
    document.getElementById("tabBtnFloating").className = `o-tab ${{tab === 'floating' ? 'active' : ''}}`;
    document.getElementById("tabBtnBook").className = `o-tab ${{tab === 'book' ? 'active' : ''}}`;
    document.getElementById("tabBtnSeries").className = `o-tab ${{tab === 'series' ? 'active' : ''}}`;

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
