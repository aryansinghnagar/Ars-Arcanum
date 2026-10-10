#!/usr/bin/env python3
"""
Ars Arcanum Project Lifecycle & Scaffolding Engine (scripts/lib/project_scaffold.py)
==================================================================================
Pure-Python, zero-dependency project scaffolding and lifecycle manager for
Universes, Obsidian World Bibles, 3-Act Novels, Standalone Novellas, and Episodic Serials.

Ensures 100% offline cross-platform parity (Linux, Windows, macOS) with atomic
writes, path traversal defenses, Authorial Constitution presets, and schema consistency.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from lib._bootstrap import PROJECT_ROOT, atomic_write, sanitize_identifier
    from lib.frontmatter import serialize_yaml_document
except ImportError:
    from _bootstrap import PROJECT_ROOT, atomic_write, sanitize_identifier
    from frontmatter import serialize_yaml_document

logger = logging.getLogger("arcanum.project_scaffold")

# Curated Authorial Constitution Presets (excluding magic modality & timeline strictness)
CONSTITUTION_PRESETS: dict[str, dict[str, Any]] = {
    "epic-fantasy": {
        "name": "Epic Fantasy",
        "description": "Multi-POV tapestry, expansive worldbuilding, descriptive pacing.",
        "canon": {
            "authority": "author",
            "narrator_reliability": "reliable",
            "allow_unresolved_mysteries": True,
        },
        "style": {
            "passive_voice": "observe",
            "repetition": "observe",
            "filter_verbs": "observe",
        },
        "structure": {
            "framework": "three_act",
            "mode": "descriptive",
            "score_enabled": False,
        },
        "naming": {
            "collision_heuristics": "advisory",
            "whitelisted_pairs": [],
        },
        "diagnostics": {
            "default_severity": "advisory",
            "suppressed_rules": ["POV-102"],
        },
    },
    "hard-scifi": {
        "name": "Hard Sci-Fi / Speculative",
        "description": "Technological causality, analytical observation, rigorous narrative consistency.",
        "canon": {
            "authority": "author",
            "narrator_reliability": "reliable",
            "allow_unresolved_mysteries": False,
        },
        "style": {
            "passive_voice": "observe",
            "repetition": "observe",
            "filter_verbs": "observe",
        },
        "structure": {
            "framework": "fichtean",
            "mode": "descriptive",
            "score_enabled": False,
        },
        "naming": {
            "collision_heuristics": "strict",
            "whitelisted_pairs": [],
        },
        "diagnostics": {
            "default_severity": "advisory",
            "suppressed_rules": [],
        },
    },
    "grimdark": {
        "name": "Grimdark / Dark Fantasy",
        "description": "Visceral realism, morally grey arcs, tension-focused pacing.",
        "canon": {
            "authority": "author",
            "narrator_reliability": "unreliable",
            "allow_unresolved_mysteries": True,
        },
        "style": {
            "passive_voice": "observe",
            "repetition": "observe",
            "filter_verbs": "observe",
        },
        "structure": {
            "framework": "none",
            "mode": "descriptive",
            "score_enabled": False,
        },
        "naming": {
            "collision_heuristics": "advisory",
            "whitelisted_pairs": [],
        },
        "diagnostics": {
            "default_severity": "advisory",
            "suppressed_rules": [],
        },
    },
    "mystery-thriller": {
        "name": "Mystery / Thriller",
        "description": "Causality tracking, clue progression, tight pacing and cliffhangers.",
        "canon": {
            "authority": "author",
            "narrator_reliability": "unreliable",
            "allow_unresolved_mysteries": False,
        },
        "style": {
            "passive_voice": "observe",
            "repetition": "observe",
            "filter_verbs": "observe",
        },
        "structure": {
            "framework": "save_the_cat",
            "mode": "descriptive",
            "score_enabled": False,
        },
        "naming": {
            "collision_heuristics": "strict",
            "whitelisted_pairs": [],
        },
        "diagnostics": {
            "default_severity": "advisory",
            "suppressed_rules": [],
        },
    },
    "literary-speculative": {
        "name": "Literary Speculative",
        "description": "Interiority, thematic motifs, Kishōtenketsu or organic structure.",
        "canon": {
            "authority": "author",
            "narrator_reliability": "unreliable",
            "allow_unresolved_mysteries": True,
        },
        "style": {
            "passive_voice": "allow",
            "repetition": "observe",
            "filter_verbs": "allow",
        },
        "structure": {
            "framework": "kishotenketsu",
            "mode": "opt_in",
            "score_enabled": False,
        },
        "naming": {
            "collision_heuristics": "advisory",
            "whitelisted_pairs": [],
        },
        "diagnostics": {
            "default_severity": "advisory",
            "suppressed_rules": ["STYLE-101", "PAC-101"],
        },
    },
    "unconstrained": {
        "name": "Unconstrained / Blank",
        "description": "Neutral baseline with all craft lenses purely observational.",
        "canon": {
            "authority": "author",
            "narrator_reliability": "reliable",
            "allow_unresolved_mysteries": True,
        },
        "style": {
            "passive_voice": "observe",
            "repetition": "observe",
            "filter_verbs": "observe",
        },
        "structure": {
            "framework": "none",
            "mode": "descriptive",
            "score_enabled": False,
        },
        "naming": {
            "collision_heuristics": "advisory",
            "whitelisted_pairs": [],
        },
        "diagnostics": {
            "default_severity": "advisory",
            "suppressed_rules": [],
        },
    },
}

# Flexible Novel Structural Paradigms & Folder Layouts
STRUCTURE_PRESETS: dict[str, dict[str, Any]] = {
    "three_act": {
        "name": "Three-Act Structure",
        "description": "Standard 3-Act dramatic arc: Setup, Confrontation, Resolution.",
        "folders": ["01_Act_I", "02_Act_II", "03_Act_III"],
        "chapters": [
            ("01_Act_I/01_Chapter_01.md", "Chapter 1", "Act I", "The Inciting Spark", "Begin drafting the opening scene here..."),
            ("01_Act_I/02_Chapter_02.md", "Chapter 2", "Act I", "The Threshold", "The journey expands..."),
            ("02_Act_II/01_Chapter_03.md", "Chapter 3", "Act II", "Into the Crucible", "Complications and stakes escalate..."),
            ("03_Act_III/01_Chapter_04.md", "Chapter 4", "Act III", "The Climax & Resolution", "The decisive confrontation unfolds..."),
        ],
    },
    "four_act": {
        "name": "Four-Act Structure",
        "description": "4-Act structure with midpoint split: Act I, Act IIA, Act IIB, Act III.",
        "folders": ["01_Act_I", "02_Act_IIA", "03_Act_IIB", "04_Act_III"],
        "chapters": [
            ("01_Act_I/01_Chapter_01.md", "Chapter 1", "Act I", "Setup & Inciting Incident", "Establish status quo and catalyst..."),
            ("02_Act_IIA/01_Chapter_02.md", "Chapter 2", "Act IIA", "Rising Action to Midpoint", "Proactive pursuit leading to midpoint..."),
            ("03_Act_IIB/01_Chapter_03.md", "Chapter 3", "Act IIB", "Crisis & Dark Night", "Consequences escalate to lowest point..."),
            ("04_Act_III/01_Chapter_04.md", "Chapter 4", "Act III", "Climax & Resolution", "Final push and resolution..."),
        ],
    },
    "five_act": {
        "name": "Five-Act Dramatic Structure (Freytag's Pyramid)",
        "description": "Classical 5-Act structure: Exposition, Rising Action, Climax, Falling Action, Resolution.",
        "folders": ["01_Exposition", "02_Rising_Action", "03_Climax", "04_Falling_Action", "05_Resolution"],
        "chapters": [
            ("01_Exposition/01_Chapter_01.md", "Chapter 1", "Exposition", "The Ordinary World", "Establish characters and world..."),
            ("02_Rising_Action/01_Chapter_02.md", "Chapter 2", "Rising Action", "The Gathering Storm", "Obstacles and rising tension..."),
            ("03_Climax/01_Chapter_03.md", "Chapter 3", "Climax", "The Zenith", "The pivotal turning point..."),
            ("04_Falling_Action/01_Chapter_04.md", "Chapter 4", "Falling Action", "The Repercussions", "Unraveling consequences..."),
            ("05_Resolution/01_Chapter_05.md", "Chapter 5", "Resolution", "The New Normal", "Denouement and new equilibrium..."),
        ],
    },
    "kishotenketsu": {
        "name": "Kishōtenketsu (4-Part Non-Conflict Structure)",
        "description": "East Asian narrative structure: Ki (Intro), Sho (Development), Ten (Twist), Ketsu (Conclusion).",
        "folders": ["01_Ki_Introduction", "02_Sho_Development", "03_Ten_Twist", "04_Ketsu_Conclusion"],
        "chapters": [
            ("01_Ki_Introduction/01_Chapter_01.md", "Chapter 1", "Ki", "The Foundation", "Introduce topic, character, setting..."),
            ("02_Sho_Development/01_Chapter_02.md", "Chapter 2", "Sho", "The Development", "Expand upon and deepen the scene..."),
            ("03_Ten_Twist/01_Chapter_03.md", "Chapter 3", "Ten", "The Unexpected Turn", "Sudden twist or unrelated element introduces new perspective..."),
            ("04_Ketsu_Conclusion/01_Chapter_04.md", "Chapter 4", "Ketsu", "The Synthesis", "Connect the twist back to the foundation..."),
        ],
    },
    "heros_journey": {
        "name": "Hero's Journey (Monomyth)",
        "description": "Campbell / Vogler 3-Phase Monomyth: Departure, Initiation, Return.",
        "folders": ["01_Departure", "02_Initiation", "03_Return"],
        "chapters": [
            ("01_Departure/01_Chapter_01.md", "Chapter 1", "Departure", "The Call to Adventure", "Ordinary world and crossing the first threshold..."),
            ("02_Initiation/01_Chapter_02.md", "Chapter 2", "Initiation", "The Road of Trials & Ordeal", "Trials, allies, and central ordeal in the abyss..."),
            ("03_Return/01_Chapter_03.md", "Chapter 3", "Return", "The Master of Two Worlds", "Resurrection and return with the elixir..."),
        ],
    },
    "flat": {
        "name": "Flat Chapter List",
        "description": "Simple flat numbered chapters directly inside draft without subfolders.",
        "folders": [],
        "chapters": [
            ("01_Chapter_01.md", "Chapter 1", "", "The Beginning", "Begin drafting chapter 1..."),
            ("02_Chapter_02.md", "Chapter 2", "", "The Continuation", "Begin drafting chapter 2..."),
            ("03_Chapter_03.md", "Chapter 3", "", "The Furtherance", "Begin drafting chapter 3..."),
        ],
    },
}


def resolve_structure_layout(
    structure: str | list[str] | None,
) -> tuple[str, list[str], list[tuple[str, str, str, str, str]]]:
    """
    Resolves novel structure preset or custom user partition into folders and chapter tuples.

    Returns:
        (structure_key, folder_list, chapter_specs)
        chapter_specs tuple format: (relative_file_path, chapter_title, act_label, subtitle, default_prompt)
    """
    if not structure:
        s_norm = "three_act"
    elif isinstance(structure, list):
        # List of custom acts/parts
        custom_parts = [sanitize_identifier(p.strip()) for p in structure if p.strip()]
        if not custom_parts:
            s_norm = "three_act"
        else:
            folders = [f"{i + 1:02d}_{p}" for i, p in enumerate(custom_parts)]
            ch_specs = [
                (
                    f"{f}/01_Chapter_{i + 1:02d}.md",
                    f"Chapter {i + 1}",
                    custom_parts[i].replace("_", " "),
                    "The Journey Continues",
                    "Begin drafting here...",
                )
                for i, f in enumerate(folders)
            ]
            return "custom", folders, ch_specs
    else:
        s_norm = structure.lower().strip().replace("-", "_").replace(" ", "_")

    # Map aliases
    alias_map = {
        "3_act": "three_act",
        "3act": "three_act",
        "threeact": "three_act",
        "4_act": "four_act",
        "4act": "four_act",
        "fouract": "four_act",
        "5_act": "five_act",
        "5act": "five_act",
        "fiveact": "five_act",
        "kisho": "kishotenketsu",
        "hero": "heros_journey",
        "hero_journey": "heros_journey",
        "monomyth": "heros_journey",
    }
    s_key = alias_map.get(s_norm, s_norm)

    if s_key in STRUCTURE_PRESETS:
        spec = STRUCTURE_PRESETS[s_key]
        return s_key, list(spec["folders"]), list(spec["chapters"])

    # If comma-separated custom structure passed as string (e.g. "Part 1, Part 2, Part 3")
    if "," in str(structure):
        parts = [p.strip() for p in str(structure).split(",") if p.strip()]
        if parts:
            clean_parts = [sanitize_identifier(p) for p in parts]
            folders = [f"{i + 1:02d}_{p}" for i, p in enumerate(clean_parts)]
            ch_specs = [
                (
                    f"{f}/01_Chapter_{i + 1:02d}.md",
                    f"Chapter {i + 1}",
                    parts[i],
                    "The Journey Continues",
                    "Begin drafting here...",
                )
                for i, f in enumerate(folders)
            ]
            return "custom", folders, ch_specs

    # Fallback to standard 3-act
    spec = STRUCTURE_PRESETS["three_act"]
    return "three_act", list(spec["folders"]), list(spec["chapters"])


def get_constitution_preset(preset_name: str) -> dict[str, Any]:
    """Retrieves normalized Authorial Constitution policy preset dictionary."""
    key = preset_name.lower().strip()
    if key in CONSTITUTION_PRESETS:
        return dict(CONSTITUTION_PRESETS[key])
    return dict(CONSTITUTION_PRESETS["unconstrained"])


def get_universes_base() -> Path:
    """Returns the base directory for narrative universes."""
    env_path = os.environ.get("UNIVERSES_BASE")
    if env_path:
        return Path(env_path).expanduser().resolve()
    return Path.home() / "Universes"


def get_manuscripts_base() -> Path:
    """Returns the base directory for standalone novel manuscripts."""
    env_path = os.environ.get("MANUSCRIPTS_BASE")
    if env_path:
        return Path(env_path).expanduser().resolve()
    return Path.home() / "Manuscripts"


def _safe_write(path: Path, content: str, dry_run: bool = False, created_list: list[str] | None = None) -> None:
    """Writes content atomically if not dry_run, recording file path."""
    if created_list is not None:
        created_list.append(str(path))
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        atomic_write(path, content)


def scaffold_universe(
    name: str,
    base_dir: Path | None = None,
    author: str = "Author",
    dry_run: bool = False,
) -> dict[str, Any]:
    """Scaffolds a narrative universe folder hierarchy at ~/Universes/<NAME>/."""
    clean_name = sanitize_identifier(name)
    target = (base_dir / clean_name) if base_dir else (get_universes_base() / clean_name)
    if target.exists() and not dry_run:
        raise FileExistsError(f"Universe directory already exists: {target}")

    created_files: list[str] = []

    if not dry_run:
        target.mkdir(parents=True, exist_ok=True)
        (target / "Manuscripts").mkdir(exist_ok=True)
        (target / "Worlds").mkdir(exist_ok=True)
        (target / "Art").mkdir(exist_ok=True)
        (target / "Audio").mkdir(exist_ok=True)

    manifest_data = {
        "title": clean_name.replace("_", " "),
        "type": "universe",
        "author": author,
        "created": datetime.now(timezone.utc).isoformat(),
        "worlds": [],
        "manuscripts": [],
        "canon_policy": "strict",
    }
    _safe_write(target / "universe.yaml", serialize_yaml_document(manifest_data), dry_run, created_files)
    _safe_write(target / ".gitignore", ".arcanum_cache.json\n*.tar.gz\n*.tmp\n*.bak\n", dry_run, created_files)

    return {
        "status": "success",
        "type": "universe",
        "name": clean_name,
        "path": str(target),
        "manifest": manifest_data,
        "created_files": created_files,
        "dry_run": dry_run,
    }


def scaffold_world(
    name: str,
    universe_name: str | None = None,
    base_dir: Path | None = None,
    template_source: Path | None = None,
    author: str = "Author",
    preset: str = "unconstrained",
    dry_run: bool = False,
) -> dict[str, Any]:
    """Scaffolds an Obsidian-ready World Bible lore vault."""
    clean_name = sanitize_identifier(name)
    base_univ = base_dir or get_universes_base()
    if universe_name:
        clean_u = sanitize_identifier(universe_name)
        target = base_univ / clean_u / "Worlds" / clean_name
    elif base_dir:
        target = base_dir / clean_name
    else:
        target = get_universes_base() / "Default-Universe" / "Worlds" / clean_name

    if target.exists() and not dry_run:
        raise FileExistsError(f"World directory already exists: {target}")

    created_files: list[str] = []

    if not dry_run:
        target.mkdir(parents=True, exist_ok=True)

    # Copy templates if available
    src_templates = template_source or (PROJECT_ROOT / "templates" / "world-bible")
    if src_templates.is_dir() and not dry_run:
        for item in src_templates.iterdir():
            if item.name.startswith((".", "_")) and item.name != ".obsidian":
                continue
            dest_item = target / item.name
            if item.is_dir():
                shutil.copytree(item, dest_item, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dest_item)
    elif not dry_run:
        # Fallback manual directory tree
        for cat in [
            "Characters",
            "Locations",
            "Factions",
            "Cosmology",
            "Magic-Technology",
            "Bestiary",
            "Artifacts",
            "Languages",
            "History",
            "Templates",
        ]:
            (target / cat).mkdir(exist_ok=True)

    manifest_data = {
        "title": clean_name.replace("_", " "),
        "type": "world_bible",
        "author": author,
        "universe": universe_name or "Default-Universe",
        "created": datetime.now(timezone.utc).isoformat(),
    }
    _safe_write(target / "world.yaml", serialize_yaml_document(manifest_data), dry_run, created_files)

    # Scaffolding constitution.yaml for the world
    constitution_data = get_constitution_preset(preset)
    _safe_write(target / "constitution.yaml", serialize_yaml_document(constitution_data), dry_run, created_files)
    _safe_write(target / ".gitignore", ".arcanum_cache.json\n*.tar.gz\n*.tmp\n*.bak\n", dry_run, created_files)

    return {
        "status": "success",
        "type": "world_bible",
        "name": clean_name,
        "universe": universe_name or "Default-Universe",
        "path": str(target),
        "manifest": manifest_data,
        "created_files": created_files,
        "dry_run": dry_run,
    }


def scaffold_manuscript(
    name: str,
    archetype: str = "novel",
    universe: str = "Default-Universe",
    world: str = "Default-World",
    base_dir: Path | None = None,
    target_words: int = 80000,
    author: str = "Author",
    preset: str = "epic-fantasy",
    structure: str = "three_act",
    template_source: Path | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Scaffolds a novel manuscript with flexible structural paradigms, Outlines, and novelWriter scaffolding."""
    clean_name = sanitize_identifier(name)
    target = (base_dir / clean_name) if base_dir else (get_manuscripts_base() / clean_name)
    if target.exists() and not dry_run:
        raise FileExistsError(f"Manuscript directory already exists: {target}")

    created_files: list[str] = []

    if not dry_run:
        target.mkdir(parents=True, exist_ok=True)
        (target / "02-Notes").mkdir(exist_ok=True)
        (target / "03-Art").mkdir(exist_ok=True)
        (target / "04-Backups").mkdir(exist_ok=True)

    draft_base = target / "01-Manuscript" / "Book-01" / "Draft-01"

    # Resolve structure paradigm and create directories & chapter templates
    struct_key, folders, ch_specs = resolve_structure_layout(structure)

    for folder in folders:
        if not dry_run:
            (draft_base / folder).mkdir(parents=True, exist_ok=True)

    for rel_path, title, act_tag, subtitle, prompt in ch_specs:
        act_line = f"act: {act_tag}\n" if act_tag else ""
        ch_text = f"""---
title: {title}
{act_line}pov: Protagonist
timeline: Scene
target_words: 3000
status: draft
---

# {title}: {subtitle}

{prompt}
"""
        _safe_write(draft_base / rel_path, ch_text, dry_run, created_files)

    # Scaffolding Outlines directory
    outlines_dir = target / "Outlines"
    src_outlines = template_source or (PROJECT_ROOT / "templates" / "manuscript" / "Outlines")
    if src_outlines.is_dir() and not dry_run:
        shutil.copytree(src_outlines, outlines_dir, dirs_exist_ok=True)
    else:
        # Fallback in-memory Master Outline
        master_outline = f"""# Master Outline: {clean_name.replace('_', ' ')}
**Author:** {author} | **Universe:** {universe} | **World:** {world} | **Target Words:** {target_words:,} | **Structure:** {struct_key}

## Narrative Arc Overview
- **Premise / High Concept**: [One-sentence logline]
- **Core Theme & Moral Premise**: [Thematic conflict]
- **Central Antagonistic Force**: [Opposition, stakes, ticking clock]

## Act-by-Act Breakdown
### Act I — Exposition & Disruption (0% – 25%)
- **Status Quo**: Ordinary world establishes protagonist's core flaw.
- **Inciting Incident**: The disruption that breaks equilibrium.
- **Plot Point 1**: Crossing the threshold into the main conflict.

### Act II — Escalation & Midpoint (25% – 75%)
- **Rising Action**: Tests, allies, enemies, and subplots develop.
- **Midpoint Shift**: Active pursuit replaces passive reaction.
- **All Hope is Lost / Dark Night**: The lowest point before the breakthrough.

### Act III — Climax & Resolution (75% – 100%)
- **Climax**: Final confrontation testing character's internal transformation.
- **Resolution**: New equilibrium and thematic culmination.
"""
        _safe_write(outlines_dir / "Master-Outline.md", master_outline, dry_run, created_files)

    manifest_data = {
        "title": clean_name.replace("_", " "),
        "archetype": archetype,
        "author": author,
        "universe": universe,
        "world": world,
        "structure": struct_key,
        "target_words": int(target_words),
        "active_draft": "Draft-01",
        "active_volume": "Book-01",
        "created": datetime.now(timezone.utc).isoformat(),
    }
    _safe_write(target / "manuscript.yaml", serialize_yaml_document(manifest_data), dry_run, created_files)

    # Scaffolding constitution.yaml
    constitution_data = get_constitution_preset(preset)
    _safe_write(target / "constitution.yaml", serialize_yaml_document(constitution_data), dry_run, created_files)

    # novelWriter project XML (v1.5 with <title>)
    nwx_content = f"""<?xml version="1.0" encoding="utf-8"?>
<novelWriterXML appVersion="2.0" fileVersion="1.5">
  <project>
    <title>{clean_name.replace('_', ' ')}</title>
    <author>{author}</author>
  </project>
</novelWriterXML>
"""
    _safe_write(target / "nwProject.nwx", nwx_content, dry_run, created_files)
    _safe_write(target / ".gitignore", ".arcanum_cache.json\n*.tar.gz\n*.tmp\n*.bak\n04-Backups/\nExports/\n", dry_run, created_files)

    return {
        "status": "success",
        "type": "manuscript",
        "archetype": archetype,
        "name": clean_name,
        "structure": struct_key,
        "path": str(target),
        "manifest": manifest_data,
        "created_files": created_files,
        "dry_run": dry_run,
    }


def scaffold_novella(
    name: str,
    universe: str = "Default-Universe",
    world: str = "Default-World",
    base_dir: Path | None = None,
    target_words: int = 30000,
    author: str = "Author",
    preset: str = "unconstrained",
    dry_run: bool = False,
) -> dict[str, Any]:
    """Scaffolds a focused novella or short story with flat chapter hierarchy."""
    clean_name = sanitize_identifier(name)
    target = (base_dir / clean_name) if base_dir else (get_manuscripts_base() / clean_name)
    if target.exists() and not dry_run:
        raise FileExistsError(f"Novella directory already exists: {target}")

    created_files: list[str] = []

    if not dry_run:
        target.mkdir(parents=True, exist_ok=True)
        (target / "02-Notes").mkdir(exist_ok=True)
        (target / "03-Art").mkdir(exist_ok=True)

    draft_dir = target / "01-Manuscript" / "Draft-01"

    # Flat chapter files
    for idx in (1, 2, 3):
        ch_text = f"""---
title: Chapter {idx}
pov: Protagonist
timeline: Scene {idx}
target_words: 3000
status: draft
---

# Chapter {idx}

Write novella chapter content here...
"""
        _safe_write(draft_dir / f"0{idx}_Chapter_0{idx}.md", ch_text, dry_run, created_files)

    manifest_data = {
        "title": clean_name.replace("_", " "),
        "archetype": "novella",
        "author": author,
        "universe": universe,
        "world": world,
        "target_words": int(target_words),
        "active_draft": "Draft-01",
        "created": datetime.now(timezone.utc).isoformat(),
    }
    _safe_write(target / "manuscript.yaml", serialize_yaml_document(manifest_data), dry_run, created_files)

    constitution_data = get_constitution_preset(preset)
    _safe_write(target / "constitution.yaml", serialize_yaml_document(constitution_data), dry_run, created_files)
    _safe_write(target / ".gitignore", ".arcanum_cache.json\n*.tar.gz\n*.tmp\n*.bak\n", dry_run, created_files)

    return {
        "status": "success",
        "type": "novella",
        "archetype": "novella",
        "name": clean_name,
        "path": str(target),
        "manifest": manifest_data,
        "created_files": created_files,
        "dry_run": dry_run,
    }


def scaffold_serial(
    name: str,
    universe: str = "Default-Universe",
    world: str = "Default-World",
    base_dir: Path | None = None,
    target_words: int = 150000,
    author: str = "Author",
    preset: str = "unconstrained",
    cadence: str = "biweekly",
    dry_run: bool = False,
) -> dict[str, Any]:
    """Scaffolds an episodic web serial structured into Arcs and Episodes."""
    clean_name = sanitize_identifier(name)
    target = (base_dir / clean_name) if base_dir else (get_manuscripts_base() / clean_name)
    if target.exists() and not dry_run:
        raise FileExistsError(f"Serial directory already exists: {target}")

    created_files: list[str] = []

    if not dry_run:
        target.mkdir(parents=True, exist_ok=True)
        (target / "02-Notes").mkdir(exist_ok=True)
        (target / "03-Backlog-Buffer").mkdir(exist_ok=True)

    arc1_dir = target / "01-Manuscript" / "Arc-01" / "Draft-01"
    arc2_dir = target / "01-Manuscript" / "Arc-02" / "Draft-01"

    ep1 = """---
title: Episode 1: The Inciting Signal
arc: Arc-01
episode: 1
target_words: 2500
status: ready_for_release
cliffhanger_rating: 4/5
---

# Episode 1: The Inciting Signal

Serial episode opening scene...
"""

    ep2 = """---
title: Episode 2: Echoes in the Dark
arc: Arc-01
episode: 2
target_words: 2500
status: in_progress
cliffhanger_rating: 5/5
---

# Episode 2: Echoes in the Dark

Serial episode continuation...
"""

    _safe_write(arc1_dir / "01_Episode_01.md", ep1, dry_run, created_files)
    _safe_write(arc1_dir / "02_Episode_02.md", ep2, dry_run, created_files)
    _safe_write(arc2_dir / "01_Episode_01.md", ep1.replace("Arc-01", "Arc-02"), dry_run, created_files)

    manifest_data = {
        "title": clean_name.replace("_", " "),
        "archetype": "serial",
        "author": author,
        "universe": universe,
        "world": world,
        "target_words": int(target_words),
        "active_arc": "Arc-01",
        "cadence": cadence,
        "created": datetime.now(timezone.utc).isoformat(),
    }
    _safe_write(target / "manuscript.yaml", serialize_yaml_document(manifest_data), dry_run, created_files)

    constitution_data = get_constitution_preset(preset)
    _safe_write(target / "constitution.yaml", serialize_yaml_document(constitution_data), dry_run, created_files)
    _safe_write(target / ".gitignore", ".arcanum_cache.json\n*.tar.gz\n*.tmp\n*.bak\n", dry_run, created_files)

    return {
        "status": "success",
        "type": "serial",
        "archetype": "serial",
        "name": clean_name,
        "path": str(target),
        "manifest": manifest_data,
        "created_files": created_files,
        "dry_run": dry_run,
    }


def scaffold_volume(
    ms_dir: Path | str,
    volume_name: str,
    title: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Adds a new volume/book structure to an existing manuscript."""
    target_ms = Path(ms_dir).resolve()
    clean_v = sanitize_identifier(volume_name)
    if not clean_v.lower().startswith("book-") and not clean_v.lower().startswith("volume-") and not clean_v.lower().startswith("arc-"):
        clean_v = f"Book-{clean_v}"

    target_parent = target_ms / "01-Manuscript" if (target_ms / "01-Manuscript").is_dir() else target_ms
    volume_dir = target_parent / clean_v
    draft_dir = volume_dir / "Draft-01"
    if volume_dir.exists() and not dry_run:
        raise FileExistsError(f"Volume directory already exists: {volume_dir}")

    created_files: list[str] = []

    if not dry_run:
        draft_dir.mkdir(parents=True, exist_ok=True)

    vol_title = title or clean_v.replace("_", " ")

    ch1_content = f"""---
title: Chapter 1
volume: {vol_title}
pov: Protagonist
---

# Chapter 1

Begin drafting volume here...
"""
    _safe_write(draft_dir / "01_Chapter_01.md", ch1_content, dry_run, created_files)

    return {
        "status": "success",
        "type": "volume",
        "name": clean_v,
        "path": str(volume_dir),
        "created_files": created_files,
        "dry_run": dry_run,
    }


def list_universes(base_dir: Path | None = None) -> list[dict[str, Any]]:
    """Lists all narrative universes."""
    base = base_dir or get_universes_base()
    if not base.is_dir():
        return []
    res = []
    for d in sorted(base.iterdir()):
        if d.is_dir() and not d.name.startswith((".", "_")):
            res.append({"name": d.name, "path": str(d)})
    return res


def list_worlds(universe_filter: str | None = None, base_dir: Path | None = None) -> list[dict[str, Any]]:
    """Lists all World Bible lore vaults."""
    base = base_dir or get_universes_base()
    if not base.is_dir():
        return []
    res = []
    for u_dir in sorted(base.iterdir()):
        if not u_dir.is_dir() or u_dir.name.startswith((".", "_")):
            continue
        if universe_filter and u_dir.name.lower() != universe_filter.lower():
            continue
        w_base = u_dir / "Worlds"
        if w_base.is_dir():
            for w_dir in sorted(w_base.iterdir()):
                if w_dir.is_dir() and not w_dir.name.startswith((".", "_")):
                    res.append({"name": w_dir.name, "universe": u_dir.name, "path": str(w_dir)})
    return res


def list_manuscripts(base_dir: Path | None = None) -> list[dict[str, Any]]:
    """Lists all standalone novel manuscripts."""
    base = base_dir or get_manuscripts_base()
    if not base.is_dir():
        return []
    res = []
    for d in sorted(base.iterdir()):
        if d.is_dir() and not d.name.startswith((".", "_")):
            res.append({"name": d.name, "path": str(d)})
    return res


def run_interactive_wizard() -> int:
    """Runs an interactive terminal wizard for guided project scaffolding."""
    print("=" * 70)
    print("🏛️  Ars Arcanum — Sovereign Project Scaffolding Wizard")
    print("=" * 70)

    # 1. Archetype selection
    print("\nSelect Project Archetype:")
    print("  [1] Novel (3-Act structured multi-chapter manuscript with Outlines)")
    print("  [2] World Bible (Obsidian-ready lore vault with categories & fileClasses)")
    print("  [3] Universe / Cosmos (Top-level container holding Worlds & Manuscripts)")
    print("  [4] Novella / Short Story (Flat chapter structure, focused narrative arc)")
    print("  [5] Episodic Serial (Arc & Episode structure with release cadence)")

    choice = input("\nEnter choice [1-5] (default: 1): ").strip() or "1"
    archetype_map = {
        "1": "novel",
        "2": "world",
        "3": "universe",
        "4": "novella",
        "5": "serial",
    }
    selected_type = archetype_map.get(choice, "novel")

    # 2. Project Name
    default_name = f"My-{selected_type.capitalize()}"
    name_input = input(f"\nProject Title / Name (default: {default_name}): ").strip() or default_name

    # 3. Author Name
    author_input = input("Author Name (default: Author): ").strip() or "Author"

    # Universe & World context for manuscripts/worlds
    u_name = "Default-Universe"
    w_name = "Default-World"
    if selected_type in ("novel", "novella", "serial", "world"):
        u_name = input("Parent Universe name (default: Default-Universe): ").strip() or "Default-Universe"
    if selected_type in ("novel", "novella", "serial"):
        w_name = input("Linked World Bible name (default: Default-World): ").strip() or "Default-World"

    # Target word count
    default_words = {"novel": 80000, "novella": 30000, "serial": 150000}.get(selected_type, 80000)
    words_val = default_words
    if selected_type in ("novel", "novella", "serial"):
        w_in = input(f"Target Word Count (default: {default_words:,}): ").strip()
        if w_in.isdigit():
            words_val = int(w_in)

    # Structure choice for novel manuscripts
    structure_choice = "three_act"
    if selected_type == "novel":
        print("\nSelect Novel Structure Layout:")
        print("  [1] three_act     (3-Act dramatic arc: Setup, Confrontation, Resolution)")
        print("  [2] four_act      (4-Act structure with midpoint split: I, IIA, IIB, III)")
        print("  [3] five_act      (5-Act classical dramatic structure / Freytag's Pyramid)")
        print("  [4] kishotenketsu (4-Part non-conflict structure: Ki, Sho, Ten, Ketsu)")
        print("  [5] heros_journey (Hero's Journey Monomyth: Departure, Initiation, Return)")
        print("  [6] flat          (Flat numbered chapter list without subfolders)")
        print("  [7] custom        (Custom comma-separated acts/parts)")
        s_in = input("\nStructure [1-7] (default: 1): ").strip()
        s_map = {
            "1": "three_act",
            "2": "four_act",
            "3": "five_act",
            "4": "kishotenketsu",
            "5": "heros_journey",
            "6": "flat",
        }
        if s_in == "7":
            custom_parts = input("Enter comma-separated act/part names (e.g. Part 1, Part 2, Part 3): ").strip()
            structure_choice = custom_parts or "three_act"
        else:
            structure_choice = s_map.get(s_in, "three_act")

    # Constitution preset
    preset_choice = "unconstrained"
    if selected_type in ("novel", "novella", "serial", "world"):
        print("\nSelect Authorial Constitution Preset:")
        print("  [1] epic-fantasy        (Multi-POV, rich worldbuilding, descriptive pacing)")
        print("  [2] hard-scifi          (Rigorous consistency, analytical observation)")
        print("  [3] grimdark            (Visceral realism, morally grey arcs, tension)")
        print("  [4] mystery-thriller    (Causality tracking, clue progression, cliffhangers)")
        print("  [5] literary-speculative(Interiority, thematic motifs, Kishōtenketsu)")
        print("  [6] unconstrained       (Neutral baseline, all craft lenses observational)")
        p_in = input("\nPreset [1-6] (default: 1 for Novel, 6 for others): ").strip()
        p_map = {
            "1": "epic-fantasy",
            "2": "hard-scifi",
            "3": "grimdark",
            "4": "mystery-thriller",
            "5": "literary-speculative",
            "6": "unconstrained",
        }
        preset_choice = p_map.get(p_in, "epic-fantasy" if selected_type == "novel" else "unconstrained")

    # Output directory
    dir_in = input("\nDestination Directory (leave blank for standard base folder): ").strip()
    target_base = Path(dir_in).resolve() if dir_in else None

    print("\n" + "-" * 70)
    print(f"Scaffolding {selected_type.upper()}: '{name_input}' by {author_input}")
    print(f"Preset: {preset_choice} | Structure: {structure_choice} | Destination: {target_base or 'Standard Base'}")
    print("-" * 70)

    if selected_type == "universe":
        res = scaffold_universe(name_input, base_dir=target_base, author=author_input)
    elif selected_type == "world":
        res = scaffold_world(name_input, universe_name=u_name, base_dir=target_base, author=author_input, preset=preset_choice)
    elif selected_type == "novella":
        res = scaffold_novella(name_input, universe=u_name, world=w_name, base_dir=target_base, target_words=words_val, author=author_input, preset=preset_choice)
    elif selected_type == "serial":
        res = scaffold_serial(name_input, universe=u_name, world=w_name, base_dir=target_base, target_words=words_val, author=author_input, preset=preset_choice)
    else:
        res = scaffold_manuscript(
            name_input,
            archetype="novel",
            universe=u_name,
            world=w_name,
            base_dir=target_base,
            target_words=words_val,
            author=author_input,
            preset=preset_choice,
            structure=structure_choice,
        )

    print(f"✓ Successfully created {res['type'].capitalize()}: {res['name']} at {res['path']}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ars Arcanum Project Lifecycle & Scaffolding Engine")
    sub = parser.add_subparsers(dest="subcommand")

    # new / scaffold command
    new_p = sub.add_parser("new", help="Scaffold new project structure")
    new_p.add_argument("type", nargs="?", choices=["manuscript", "novel", "book", "world", "lore", "vault", "universe", "cosmos", "novella", "short", "serial", "webserial", "volume"])
    new_p.add_argument("name", nargs="?", help="Name of the project or volume")
    new_p.add_argument("--preset", "-p", default="unconstrained", choices=list(CONSTITUTION_PRESETS.keys()), help="Constitution craft preset")
    new_p.add_argument("--structure", "-s", default="three_act", help="Novel structure preset (flat, three_act, four_act, five_act, kishotenketsu, heros_journey, or custom)")
    new_p.add_argument("--author", "-a", default="Author", help="Author name")
    new_p.add_argument("--universe", "-u", default="Default-Universe", help="Universe name")
    new_p.add_argument("--world", "-w", default="Default-World", help="World name")
    new_p.add_argument("--target-words", "-t", type=int, default=80000, help="Target word count")
    new_p.add_argument("--dir", "-d", help="Explicit parent directory destination")
    new_p.add_argument("--dry-run", action="store_true", help="Preview scaffolding actions without writing to disk")
    new_p.add_argument("--json", action="store_true", help="Output JSON results")

    # universe command
    u_p = sub.add_parser("universe", help="Manage universes")
    u_p.add_argument("name", nargs="?", help="Universe name to create")
    u_p.add_argument("--author", "-a", default="Author", help="Author name")
    u_p.add_argument("--dir", "-d", help="Explicit parent directory destination")
    u_p.add_argument("--dry-run", action="store_true", help="Preview without writing")
    u_p.add_argument("--json", action="store_true", help="Output JSON results")
    u_p.add_argument("--list", "-l", action="store_true", help="List all universes")

    # world command
    w_p = sub.add_parser("world", help="Manage world bibles")
    w_p.add_argument("name", nargs="?", help="World name to create")
    w_p.add_argument("--author", "-a", default="Author", help="Author name")
    w_p.add_argument("--preset", "-p", default="unconstrained", choices=list(CONSTITUTION_PRESETS.keys()), help="Constitution preset")
    w_p.add_argument("--universe", "-u", default="Default-Universe", help="Parent universe")
    w_p.add_argument("--dir", "-d", help="Explicit parent directory destination")
    w_p.add_argument("--dry-run", action="store_true", help="Preview without writing")
    w_p.add_argument("--json", action="store_true", help="Output JSON results")
    w_p.add_argument("--list", "-l", action="store_true", help="List all worlds")

    # manuscript / novel command
    m_p = sub.add_parser("manuscript", help="Manage novel manuscripts")
    m_p.add_argument("name", nargs="?", help="Manuscript name to create")
    m_p.add_argument("--author", "-a", default="Author", help="Author name")
    m_p.add_argument("--preset", "-p", default="epic-fantasy", choices=list(CONSTITUTION_PRESETS.keys()), help="Constitution preset")
    m_p.add_argument("--structure", "-s", default="three_act", help="Novel structure preset (flat, three_act, four_act, five_act, kishotenketsu, heros_journey, or custom)")
    m_p.add_argument("--universe", "-u", default="Default-Universe", help="Universe")
    m_p.add_argument("--world", "-w", default="Default-World", help="World")
    m_p.add_argument("--target-words", "-t", type=int, default=80000, help="Target word count")
    m_p.add_argument("--dir", "-d", help="Explicit parent directory destination")
    m_p.add_argument("--dry-run", action="store_true", help="Preview without writing")
    m_p.add_argument("--json", action="store_true", help="Output JSON results")
    m_p.add_argument("--list", "-l", action="store_true", help="List all manuscripts")

    # novella command
    nov_p = sub.add_parser("novella", help="Manage novella manuscripts")
    nov_p.add_argument("name", nargs="?", help="Novella name to create")
    nov_p.add_argument("--author", "-a", default="Author", help="Author name")
    nov_p.add_argument("--preset", "-p", default="unconstrained", choices=list(CONSTITUTION_PRESETS.keys()), help="Constitution preset")
    nov_p.add_argument("--universe", "-u", default="Default-Universe", help="Universe")
    nov_p.add_argument("--world", "-w", default="Default-World", help="World")
    nov_p.add_argument("--target-words", "-t", type=int, default=30000, help="Target word count")
    nov_p.add_argument("--dir", "-d", help="Explicit parent directory destination")
    nov_p.add_argument("--dry-run", action="store_true", help="Preview without writing")
    nov_p.add_argument("--json", action="store_true", help="Output JSON results")

    # serial command
    ser_p = sub.add_parser("serial", help="Manage web serial manuscripts")
    ser_p.add_argument("name", nargs="?", help="Serial name to create")
    ser_p.add_argument("--author", "-a", default="Author", help="Author name")
    ser_p.add_argument("--preset", "-p", default="unconstrained", choices=list(CONSTITUTION_PRESETS.keys()), help="Constitution preset")
    ser_p.add_argument("--universe", "-u", default="Default-Universe", help="Universe")
    ser_p.add_argument("--world", "-w", default="Default-World", help="World")
    ser_p.add_argument("--target-words", "-t", type=int, default=150000, help="Target word count")
    ser_p.add_argument("--cadence", default="biweekly", help="Release cadence (e.g. weekly, biweekly)")
    ser_p.add_argument("--dir", "-d", help="Explicit parent directory destination")
    ser_p.add_argument("--dry-run", action="store_true", help="Preview without writing")
    ser_p.add_argument("--json", action="store_true", help="Output JSON results")

    # volume command
    v_p = sub.add_parser("volume", help="Add new volume to manuscript")
    v_p.add_argument("manuscript", help="Manuscript directory or name")
    v_p.add_argument("volume", help="Volume name (e.g. Book-02)")
    v_p.add_argument("--title", help="Volume title")
    v_p.add_argument("--dry-run", action="store_true", help="Preview without writing")
    v_p.add_argument("--json", action="store_true", help="Output JSON results")

    # presets command
    sub.add_parser("presets", help="List all craft Constitution presets")

    args = parser.parse_args(argv)

    if not args.subcommand:
        # If run with no subcommand in interactive terminal, trigger wizard
        if sys.stdin.isatty():
            return run_interactive_wizard()
        parser.print_help()
        return 0

    if args.subcommand == "presets":
        print("🏛️ Ars Arcanum — Curated Authorial Constitution Presets:\n")
        for k, v in CONSTITUTION_PRESETS.items():
            print(f"  • {k:<22} : {v['name']} — {v['description']}")
        print("\n🏛️ Ars Arcanum — Flexible Novel Structural Layouts:\n")
        for k, v in STRUCTURE_PRESETS.items():
            print(f"  • {k:<22} : {v['name']} — {v['description']}")
        return 0

    try:
        if args.subcommand == "new":
            if not args.type or not args.name:
                if sys.stdin.isatty():
                    return run_interactive_wizard()
                parser.error("Both 'type' and 'name' are required for 'arcanum new'.")

            stype = args.type.lower()
            base = Path(args.dir).resolve() if args.dir else None
            dry = bool(args.dry_run)

            if stype in ("universe", "cosmos"):
                res = scaffold_universe(args.name, base_dir=base, author=args.author, dry_run=dry)
                type_label = "Universe"
            elif stype in ("world", "lore", "vault"):
                res = scaffold_world(args.name, universe_name=args.universe, base_dir=base, author=args.author, preset=args.preset, dry_run=dry)
                type_label = "World Lore Bible"
            elif stype in ("novella", "short"):
                res = scaffold_novella(args.name, universe=args.universe, world=args.world, base_dir=base, target_words=args.target_words, author=args.author, preset=args.preset, dry_run=dry)
                type_label = "Novella"
            elif stype in ("serial", "webserial"):
                res = scaffold_serial(args.name, universe=args.universe, world=args.world, base_dir=base, target_words=args.target_words, author=args.author, preset=args.preset, dry_run=dry)
                type_label = "Serial"
            elif stype in ("manuscript", "novel", "book"):
                res = scaffold_manuscript(
                    args.name,
                    archetype="novel",
                    universe=args.universe,
                    world=args.world,
                    base_dir=base,
                    target_words=args.target_words,
                    author=args.author,
                    preset=args.preset,
                    structure=getattr(args, "structure", "three_act"),
                    dry_run=dry,
                )
                type_label = "Novel Manuscript"
            elif stype == "volume":
                res = scaffold_volume(args.name, args.name, title=None, dry_run=dry)
                type_label = "Volume"
            else:
                parser.error(f"Unknown project type '{args.type}'.")

            if getattr(args, "json", False):
                print(json.dumps(res, indent=2))
            else:
                prefix = "[DRY RUN] Would create" if dry else "✓ Created"
                print(f"{prefix} {type_label}: {res['name']} at {res['path']}")
            return 0

        if args.subcommand == "universe":
            if args.list or not args.name:
                univs = list_universes()
                if getattr(args, "json", False):
                    print(json.dumps(univs, indent=2))
                else:
                    print(f"Narrative Universes ({len(univs)} total):")
                    for u in univs:
                        print(f"  • {u['name']} ({u['path']})")
                return 0
            base = Path(args.dir).resolve() if args.dir else None
            res = scaffold_universe(args.name, base_dir=base, author=args.author, dry_run=bool(args.dry_run))
            if getattr(args, "json", False):
                print(json.dumps(res, indent=2))
            else:
                prefix = "[DRY RUN] Would create" if args.dry_run else "✓ Created"
                print(f"{prefix} Universe: {res['name']} at {res['path']}")
            return 0

        if args.subcommand == "world":
            if args.list or not args.name:
                wrlds = list_worlds(universe_filter=args.universe if args.universe != "Default-Universe" else None)
                if getattr(args, "json", False):
                    print(json.dumps(wrlds, indent=2))
                else:
                    print(f"World Lore Bibles ({len(wrlds)} total):")
                    for w in wrlds:
                        print(f"  • {w['name']} [Universe: {w['universe']}] ({w['path']})")
                return 0
            base = Path(args.dir).resolve() if args.dir else None
            res = scaffold_world(args.name, universe_name=args.universe, base_dir=base, author=args.author, preset=args.preset, dry_run=bool(args.dry_run))
            if getattr(args, "json", False):
                print(json.dumps(res, indent=2))
            else:
                prefix = "[DRY RUN] Would create" if args.dry_run else "✓ Created"
                print(f"{prefix} World Lore Bible: {res['name']} at {res['path']}")
            return 0

        if args.subcommand == "manuscript":
            if args.list or not args.name:
                mss = list_manuscripts()
                if getattr(args, "json", False):
                    print(json.dumps(mss, indent=2))
                else:
                    print(f"Novel Manuscripts ({len(mss)} total):")
                    for m in mss:
                        print(f"  • {m['name']} ({m['path']})")
                return 0
            base = Path(args.dir).resolve() if args.dir else None
            res = scaffold_manuscript(
                args.name,
                archetype="novel",
                universe=args.universe,
                world=args.world,
                base_dir=base,
                target_words=args.target_words,
                author=args.author,
                preset=args.preset,
                structure=getattr(args, "structure", "three_act"),
                dry_run=bool(args.dry_run),
            )
            if getattr(args, "json", False):
                print(json.dumps(res, indent=2))
            else:
                prefix = "[DRY RUN] Would create" if args.dry_run else "✓ Created"
                print(f"{prefix} Novel Manuscript: {res['name']} at {res['path']}")
            return 0

        if args.subcommand == "novella":
            base = Path(args.dir).resolve() if args.dir else None
            res = scaffold_novella(
                args.name,
                universe=args.universe,
                world=args.world,
                base_dir=base,
                target_words=args.target_words,
                author=args.author,
                preset=args.preset,
                dry_run=bool(args.dry_run),
            )
            if getattr(args, "json", False):
                print(json.dumps(res, indent=2))
            else:
                prefix = "[DRY RUN] Would create" if args.dry_run else "✓ Created"
                print(f"{prefix} Novella: {res['name']} at {res['path']}")
            return 0

        if args.subcommand == "serial":
            base = Path(args.dir).resolve() if args.dir else None
            res = scaffold_serial(
                args.name,
                universe=args.universe,
                world=args.world,
                base_dir=base,
                target_words=args.target_words,
                author=args.author,
                preset=args.preset,
                cadence=args.cadence,
                dry_run=bool(args.dry_run),
            )
            if getattr(args, "json", False):
                print(json.dumps(res, indent=2))
            else:
                prefix = "[DRY RUN] Would create" if args.dry_run else "✓ Created"
                print(f"{prefix} Serial: {res['name']} at {res['path']}")
            return 0

        if args.subcommand == "volume":
            res = scaffold_volume(args.manuscript, args.volume, title=args.title, dry_run=bool(args.dry_run))
            if getattr(args, "json", False):
                print(json.dumps(res, indent=2))
            else:
                prefix = "[DRY RUN] Would add" if args.dry_run else "✓ Added"
                print(f"{prefix} Volume: {res['name']} at {res['path']}")
            return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


__all__ = [
    "CONSTITUTION_PRESETS",
    "STRUCTURE_PRESETS",
    "get_constitution_preset",
    "get_manuscripts_base",
    "get_universes_base",
    "list_manuscripts",
    "list_universes",
    "list_worlds",
    "main",
    "resolve_structure_layout",
    "run_interactive_wizard",
    "scaffold_manuscript",
    "scaffold_novella",
    "scaffold_serial",
    "scaffold_universe",
    "scaffold_volume",
    "scaffold_world",
]

if __name__ == "__main__":
    sys.exit(main())
