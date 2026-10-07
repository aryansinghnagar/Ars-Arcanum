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
    from lib._bootstrap import atomic_write, count_prose_words
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
    from lib.zen_studio_template import render_zen_studio_html
except ImportError:
    from _bootstrap import atomic_write, count_prose_words
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
    from zen_studio_template import render_zen_studio_html

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
            word_count = count_prose_words(body_clean)

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
            word_count = count_prose_words(body)

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

    html_content = render_zen_studio_html(
        chapters_json=chapters_json,
        lore_json=lore_json,
        outlines_json=outlines_json,
        catalog_json=catalog_json,
        sparks_json=sparks_json,
        tips_json=tips_json,
        tips_enabled_val=tips_enabled_val,
        lore_entities_count=len(lore_entities),
    )
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
