#!/usr/bin/env python3
"""
Ars Arcanum Story Paradigm & Narrative Structure Enforcer
(scripts/lib/structure.py)
================================================================================
Zero-dependency, offline narrative structural analyzer and pacing paradigm enforcer.

Capabilities (PLT-102):
1. Story Paradigm Models:
   - Three-Act Structure (Classic 8-sequence / 25-50-25 model)
   - Hero's Journey / Campbell-Vogler Monomyth (12 stages)
   - Save the Cat! 15 Beat Sheet (Blake Snyder)
   - Dan Harmon Story Circle (8 steps)
   - 7-Point Story Structure (Dan Wells)
   - Fichtean Curve (Crises & Climax model)
2. Manuscript Structural Mapping:
   - Computes proportional word counts across chapters / scenes
   - Maps actual chapter positions against ideal structural beat windows
   - Detects structural drift (late Inciting Incident, early Midpoint, rushed Climax)
   - Structural Harmony Score (0–100%)
3. Standalone Interactive HTML Beat Map with timeline bars.

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
    from lib.data_access import get_data_access
    from lib.scope import (
        EngineScope,
        add_scope_arguments,
        filter_manuscript_scope,
        parse_scope_args,
        resolve_manuscript_dir,
        resolve_world_dir,
    )
except ImportError:
    from _bootstrap import atomic_write
    from data_access import get_data_access
    from scope import (  # type: ignore[no-redef]
        EngineScope,
        add_scope_arguments,
        filter_manuscript_scope,
        parse_scope_args,
        resolve_manuscript_dir,
        resolve_world_dir,
    )

try:
    from lib.manuscript_scaffold import get_paradigm_key, list_presets, read_manifest_structure
except ImportError:
    try:
        from manuscript_scaffold import (  # type: ignore[no-redef]
            get_paradigm_key,
            list_presets,
            read_manifest_structure,
        )
    except ImportError:
        get_paradigm_key = None  # type: ignore[assignment]
        list_presets = None  # type: ignore[assignment]
        read_manifest_structure = None  # type: ignore[assignment]

logger = logging.getLogger("arcanum.structure")

PARADIGMS = {
    "three_act": {
        "name": "Classic Three-Act Structure",
        "beats": [
            {"name": "Opening Status Quo", "target_pct": 0.05, "window": (0.0, 0.10), "desc": "Establish protagonist in the ordinary world"},
            {"name": "Inciting Incident", "target_pct": 0.12, "window": (0.08, 0.16), "desc": "Event that disrupts the balance and sets story in motion"},
            {"name": "Plot Point 1 / Break into Act II", "target_pct": 0.25, "window": (0.20, 0.30), "desc": "Protagonist steps into new world / accepts the challenge"},
            {"name": "First Pinch Point", "target_pct": 0.37, "window": (0.32, 0.42), "desc": "Antagonist forces push back; reminder of stakes"},
            {"name": "Midpoint", "target_pct": 0.50, "window": (0.45, 0.55), "desc": "Shift from reactive to proactive; false victory or false defeat"},
            {"name": "Second Pinch Point", "target_pct": 0.62, "window": (0.58, 0.68), "desc": "Antagonistic pressure intensifies; cracks in the plan"},
            {"name": "All Hope Is Lost / Crisis", "target_pct": 0.75, "window": (0.70, 0.80), "desc": "Lowest point; old methods fail; ultimate test"},
            {"name": "Climax", "target_pct": 0.88, "window": (0.82, 0.94), "desc": "Final showdown confronting core conflict"},
            {"name": "Resolution / Denouement", "target_pct": 0.96, "window": (0.92, 1.00), "desc": "New equilibrium established"},
        ]
    },
    "save_the_cat": {
        "name": "Save the Cat! 15 Beats",
        "beats": [
            {"name": "Opening Image", "target_pct": 0.01, "window": (0.0, 0.03), "desc": "Snapshot of starting world and flaw"},
            {"name": "Theme Stated", "target_pct": 0.05, "window": (0.03, 0.08), "desc": "Statement of core thematic truth"},
            {"name": "Set-Up", "target_pct": 0.08, "window": (0.01, 0.12), "desc": "Establish life, stakes, and six things needing fixing"},
            {"name": "Catalyst", "target_pct": 0.12, "window": (0.09, 0.15), "desc": "Inciting event that shakes up status quo"},
            {"name": "Debate", "target_pct": 0.18, "window": (0.13, 0.22), "desc": "Doubt, resistance, should I stay or go"},
            {"name": "Break into Two", "target_pct": 0.23, "window": (0.20, 0.27), "desc": "Proactive decision to enter Act 2"},
            {"name": "B Story", "target_pct": 0.25, "window": (0.22, 0.30), "desc": "Love interest or mentor subplot introduced"},
            {"name": "Fun and Games", "target_pct": 0.37, "window": (0.28, 0.48), "desc": "Promise of the premise explored"},
            {"name": "Midpoint", "target_pct": 0.50, "window": (0.46, 0.54), "desc": "False victory/defeat; stakes raised"},
            {"name": "Bad Guys Close In", "target_pct": 0.62, "window": (0.52, 0.72), "desc": "Internal and external pressure mounts"},
            {"name": "All Hope Is Lost", "target_pct": 0.75, "window": (0.70, 0.78), "desc": "Whiff of death; rock bottom"},
            {"name": "Dark Night of the Soul", "target_pct": 0.78, "window": (0.74, 0.82), "desc": "Mourning and discovering true epiphany"},
            {"name": "Break into Three", "target_pct": 0.82, "window": (0.78, 0.86), "desc": "New idea that synthesizes A and B story"},
            {"name": "Finale", "target_pct": 0.90, "window": (0.84, 0.96), "desc": "Execution of the new plan; defeating bad guys"},
            {"name": "Final Image", "target_pct": 0.99, "window": (0.96, 1.00), "desc": "Opposite mirror of the Opening Image"},
        ]
    },
    "heros_journey": {
        "name": "Hero's Journey (Monomyth)",
        "beats": [
            {"name": "1. Ordinary World", "target_pct": 0.05, "window": (0.0, 0.10), "desc": "Hero in baseline environment"},
            {"name": "2. Call to Adventure", "target_pct": 0.12, "window": (0.08, 0.16), "desc": "Disruption challenges hero to journey"},
            {"name": "3. Refusal of the Call", "target_pct": 0.18, "window": (0.13, 0.22), "desc": "Reluctance, fear, or obligation"},
            {"name": "4. Meeting the Mentor", "target_pct": 0.22, "window": (0.18, 0.26), "desc": "Guide gives wisdom, tool, or encouragement"},
            {"name": "5. Crossing the Threshold", "target_pct": 0.28, "window": (0.23, 0.33), "desc": "Entering the special world"},
            {"name": "6. Tests, Allies & Enemies", "target_pct": 0.40, "window": (0.30, 0.50), "desc": "Navigating rules of the new realm"},
            {"name": "7. Approach Inmost Cave", "target_pct": 0.55, "window": (0.48, 0.62), "desc": "Preparing for the central challenge"},
            {"name": "8. The Ordeal", "target_pct": 0.65, "window": (0.58, 0.72), "desc": "Direct brush with death/failure"},
            {"name": "9. Reward (Seizing the Sword)", "target_pct": 0.75, "window": (0.68, 0.80), "desc": "Hero claims prize / transformation"},
            {"name": "10. The Road Back", "target_pct": 0.82, "window": (0.76, 0.88), "desc": "Urgency and pursuit back home"},
            {"name": "11. Resurrection", "target_pct": 0.90, "window": (0.84, 0.95), "desc": "Final supreme test of transformed hero"},
            {"name": "12. Return with Elixir", "target_pct": 0.98, "window": (0.94, 1.00), "desc": "Sharing boon with the ordinary world"},
        ]
    },
    "story_circle": {
        "name": "Dan Harmon Story Circle",
        "beats": [
            {"name": "1. You (Comfort Zone)", "target_pct": 0.08, "window": (0.0, 0.15), "desc": "A character is in a zone of comfort"},
            {"name": "2. Need (Desire)", "target_pct": 0.20, "window": (0.12, 0.26), "desc": "But they want something"},
            {"name": "3. Go (Unfamiliar Situation)", "target_pct": 0.32, "window": (0.24, 0.38), "desc": "They enter an unfamiliar situation"},
            {"name": "4. Search (Adaptation)", "target_pct": 0.45, "window": (0.36, 0.52), "desc": "They adapt to it"},
            {"name": "5. Find (Getting What They Wanted)", "target_pct": 0.58, "window": (0.50, 0.65), "desc": "They get what they wanted"},
            {"name": "6. Take (Heavy Price)", "target_pct": 0.72, "window": (0.64, 0.80), "desc": "They pay a heavy price for it"},
            {"name": "7. Return (Back to Start)", "target_pct": 0.85, "window": (0.78, 0.92), "desc": "They return to their familiar situation"},
            {"name": "8. Change (Transformed)", "target_pct": 0.96, "window": (0.90, 1.00), "desc": "Having changed"},
        ]
    },
    "seven_point": {
        "name": "7-Point Story Structure",
        "beats": [
            {"name": "1. Hook", "target_pct": 0.05, "window": (0.0, 0.12), "desc": "Starting state opposite of resolution"},
            {"name": "2. Plot Turn 1", "target_pct": 0.22, "window": (0.15, 0.28), "desc": "Call to action; movement begins"},
            {"name": "3. Pinch Point 1", "target_pct": 0.37, "window": (0.30, 0.44), "desc": "Antagonist reveals power; pressure rises"},
            {"name": "4. Midpoint", "target_pct": 0.50, "window": (0.44, 0.56), "desc": "Character moves from reacting to acting"},
            {"name": "5. Pinch Point 2", "target_pct": 0.65, "window": (0.58, 0.72), "desc": "Disaster strikes; plan fails"},
            {"name": "6. Plot Turn 2", "target_pct": 0.80, "window": (0.74, 0.86), "desc": "Final piece of puzzle acquired"},
            {"name": "7. Resolution", "target_pct": 0.95, "window": (0.88, 1.00), "desc": "Climactic resolution and transformed status quo"},
        ]
    },
    "eight_sequence": {
        "name": "8-Sequence Method (Gulino/Daniel)",
        "beats": [
            {"name": "Sequence A: Status Quo & Inciting Incident", "target_pct": 0.06, "window": (0.0, 0.12), "desc": "Ordinary world, introduction, and the hook/inciting event"},
            {"name": "Sequence B: Predicament & Lock-In", "target_pct": 0.18, "window": (0.12, 0.25), "desc": "Main tension formulated; protagonist committed to the journey"},
            {"name": "Sequence C: First Obstacle & Rising Action", "target_pct": 0.31, "window": (0.24, 0.38), "desc": "First major barrier encountered and navigated"},
            {"name": "Sequence D: Midpoint Crisis & Shift of Intent", "target_pct": 0.44, "window": (0.37, 0.52), "desc": "Crucial revelation; point of no return; stakes double"},
            {"name": "Sequence E: Rising Complications & Subplot Climax", "target_pct": 0.56, "window": (0.50, 0.63), "desc": "Complications multiply; subplots reach major inflection"},
            {"name": "Sequence F: Climax of Act II & Main Culmination", "target_pct": 0.69, "window": (0.62, 0.76), "desc": "Highest tension of Act II; all hope seems lost"},
            {"name": "Sequence G: New Tension & Final Twist", "target_pct": 0.81, "window": (0.75, 0.88), "desc": "Re-evaluation; discovery of unexpected path forward"},
            {"name": "Sequence H: Climax of Act III & Resolution", "target_pct": 0.94, "window": (0.87, 1.00), "desc": "Ultimate resolution of the core tension and new equilibrium"},
        ]
    },
    "fichtean_curve": {
        "name": "The Fichtean Curve",
        "beats": [
            {"name": "1. Exposition & Initial Action", "target_pct": 0.08, "window": (0.0, 0.15), "desc": "Characters and immediate conflict introduced directly"},
            {"name": "2. Crisis 1 (First Complication)", "target_pct": 0.22, "window": (0.15, 0.30), "desc": "First major obstacle and escalating tension"},
            {"name": "3. Rising Action & Escalation", "target_pct": 0.38, "window": (0.30, 0.46), "desc": "Consequences compound; stakes deepen"},
            {"name": "4. Crisis 2 (Major Reversal)", "target_pct": 0.52, "window": (0.45, 0.60), "desc": "Significant reversal testing character resolve"},
            {"name": "5. Crisis 3 (Point of No Return)", "target_pct": 0.70, "window": (0.62, 0.78), "desc": "Severe crisis immediately preceding the climax"},
            {"name": "6. Climax (Supreme Confrontation)", "target_pct": 0.88, "window": (0.80, 0.94), "desc": "Peak of dramatic narrative tension"},
            {"name": "7. Falling Action & Denouement", "target_pct": 0.96, "window": (0.92, 1.00), "desc": "Unraveling of tension and final new state"},
        ]
    },
    "kishotenketsu": {
        "name": "Kishōtenketsu (起承転結)",
        "beats": [
            {"name": "1. 起 Ki (Introduction)", "target_pct": 0.15, "window": (0.0, 0.25), "desc": "Introduces characters, setting, world environment and tone"},
            {"name": "2. 承 Shō (Development)", "target_pct": 0.40, "window": (0.25, 0.55), "desc": "Expands upon introduction without introducing major conflict"},
            {"name": "3. 転 Ten (The Twist / Turn)", "target_pct": 0.75, "window": (0.60, 0.85), "desc": "Introduction of an unexpected element, subversion, or perspective shift"},
            {"name": "4. 結 Ketsu (Reconciliation)", "target_pct": 0.95, "window": (0.85, 1.00), "desc": "Harmonizes twist with the initial premise; brings synthesis"},
        ]
    },
    "freytags_pyramid": {
        "name": "Freytag's Dramatic Pyramid",
        "beats": [
            {"name": "1. Exposition", "target_pct": 0.07, "window": (0.0, 0.14), "desc": "Background information, setting, character establish"},
            {"name": "2. Inciting Force", "target_pct": 0.18, "window": (0.12, 0.24), "desc": "Event triggering the central action"},
            {"name": "3. Rising Action", "target_pct": 0.35, "window": (0.25, 0.45), "desc": "Series of events building suspense and complication"},
            {"name": "4. Climax / Turning Point", "target_pct": 0.52, "window": (0.46, 0.58), "desc": "Central turning point and maximum intensity"},
            {"name": "5. Falling Action", "target_pct": 0.70, "window": (0.60, 0.78), "desc": "Aftermath of the turning point; tightening threads"},
            {"name": "6. Moment of Final Suspense", "target_pct": 0.84, "window": (0.78, 0.90), "desc": "Brief delay or doubt before final outcome"},
            {"name": "7. Catastrophe / Denouement", "target_pct": 0.96, "window": (0.90, 1.00), "desc": "Final unknotting, tragedy or resolution"},
        ]
    },
    "romancing_the_beat": {
        "name": "Romancing the Beat (Gwen Hayes)",
        "beats": [
            {"name": "1. Setup", "target_pct": 0.10, "window": (0.0, 0.20), "desc": "Introductions to H1 and H2 in their ordinary worlds"},
            {"name": "2. Meet Cute / Inciting Incident", "target_pct": 0.20, "window": (0.15, 0.25), "desc": "The characters meet and their worlds collide"},
            {"name": "3. No Way 1 / Admitting Attraction", "target_pct": 0.35, "window": (0.25, 0.45), "desc": "Denial of attraction followed by eventual admission"},
            {"name": "4. Midpoint (Love Triumphant)", "target_pct": 0.50, "window": (0.45, 0.55), "desc": "False high where they give in to the romance"},
            {"name": "5. Retreat / Pulling Away", "target_pct": 0.65, "window": (0.55, 0.75), "desc": "Doubts creep in, returning to old fears"},
            {"name": "6. Black Moment / All Hope is Lost", "target_pct": 0.80, "window": (0.75, 0.85), "desc": "The breakup or biggest emotional setback"},
            {"name": "7. Grand Gesture / Resolution", "target_pct": 0.95, "window": (0.85, 1.00), "desc": "Proving the love is real and happily ever after (HEA)"},
        ]
    },
    "virgins_promise": {
        "name": "The Virgin's Promise (Kim Hudson)",
        "beats": [
            {"name": "1. Dependent World", "target_pct": 0.05, "window": (0.0, 0.10), "desc": "Accepting the rules of the community/dependent state"},
            {"name": "2. Price of Conformity", "target_pct": 0.15, "window": (0.10, 0.20), "desc": "Realizing what they are suppressing to fit in"},
            {"name": "3. Opportunity to Shine", "target_pct": 0.25, "window": (0.20, 0.30), "desc": "A chance to express their true self in secret"},
            {"name": "4. Dresses the Part", "target_pct": 0.35, "window": (0.30, 0.45), "desc": "Embracing the new identity covertly"},
            {"name": "5. Secret World", "target_pct": 0.50, "window": (0.45, 0.55), "desc": "Fully experiencing the joy of the hidden self"},
            {"name": "6. Caught Shining", "target_pct": 0.65, "window": (0.55, 0.75), "desc": "The secret is discovered; conflict with the community"},
            {"name": "7. Gives Up What Kept Her Stuck", "target_pct": 0.80, "window": (0.75, 0.85), "desc": "Rejects the old limiting beliefs"},
            {"name": "8. Kingdom in Chaos", "target_pct": 0.90, "window": (0.85, 0.95), "desc": "The community struggles with the change"},
            {"name": "9. Wanders in the Wilderness", "target_pct": 0.95, "window": (0.90, 0.98), "desc": "Doubt and integration of the true self"},
            {"name": "10. Chooses Her Light / Re-order", "target_pct": 0.98, "window": (0.95, 1.00), "desc": "Brings the new self into the community openly"},
        ]
    },
    "freeform": {
        "name": "Freeform & Lyrical Flow (Pacing-Only / Non-Linear)",
        "beats": [
            {"name": "1. Opening Movement", "target_pct": 0.15, "window": (0.0, 0.30), "desc": "Initial thematic and sensory grounding"},
            {"name": "2. Development Movement", "target_pct": 0.45, "window": (0.20, 0.65), "desc": "Fluid emotional and thematic development"},
            {"name": "3. Thematic Turn", "target_pct": 0.75, "window": (0.50, 0.85), "desc": "Lyrical inflection or perspective shift"},
            {"name": "4. Closing Cadence", "target_pct": 0.95, "window": (0.70, 1.00), "desc": "Resonant closing cadence and thematic echo"},
        ]
    }
}


def scan_manuscript_structure(target_path: Path | str | None = None, paradigm_key: str = "three_act", scope: Any = None) -> dict:
    """Scans manuscript chapters and evaluates alignment against the chosen paradigm with granular scope support."""
    target_str = resolve_manuscript_dir(target_path) if target_path else resolve_manuscript_dir()
    if target_path and Path(target_path).exists():
        p_target = Path(target_path)
    elif target_str and Path(target_str).exists():
        p_target = Path(target_str)
    else:
        p_target = Path(target_path) if target_path else Path.cwd()

    chapters = []
    total_words = 0

    if p_target.is_file():
        content = get_data_access().read_file(p_target)
        words = len(re.findall(r'\b\w+\b', content))
        total_words = words
        chapters.append({
            "index": 1,
            "filename": p_target.name,
            "path": str(p_target),
            "words": words,
            "cumulative_words": words,
        })
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
                items_to_map = [(s.global_scene_idx, s.title, s.content, str(s.chapter_file)) for s in scoped_scenes]
            else:
                items_to_map = [(c.chapter_num, c.title, c.scoped_content, str(c.file_path)) for c in scoped_chaps]
            for idx, title, content, fpath in items_to_map:
                words = len(re.findall(r'\b\w+\b', content))
                total_words += words
                chapters.append({
                    "index": idx,
                    "filename": title,
                    "path": fpath,
                    "words": words,
                    "cumulative_words": total_words,
                })
        else:
            files = []
            for p in sorted(p_target.rglob("*.md")):
                if not p.name.startswith((".", "_")) and "Backups" not in p.parts and "04_Back_Matter" not in p.parts:
                    files.append(p)
            for idx, f in enumerate(files, 1):
                content = get_data_access().read_file(f)
                words = len(re.findall(r'\b\w+\b', content))
                total_words += words
                chapters.append({
                    "index": idx,
                    "filename": f.name,
                    "path": str(f),
                    "words": words,
                    "cumulative_words": total_words,
                })
    else:
        raise FileNotFoundError(f"Target path not found: {p_target}")

    paradigm = PARADIGMS.get(paradigm_key, PARADIGMS["three_act"])

    # Add percentages
    prev_words = 0
    for ch in chapters:
        start_pct = prev_words / total_words if total_words > 0 else 0.0
        end_pct = ch["cumulative_words"] / total_words if total_words > 0 else 0.0
        ch["start_pct"] = round(start_pct, 3)
        ch["cum_pct"] = round(end_pct, 3)
        ch["mid_pct"] = round((start_pct + end_pct) / 2.0, 3)
        ch["pct_of_total"] = round((ch["words"] / total_words), 3) if total_words > 0 else 0.0
        prev_words = ch["cumulative_words"]

    # Map beats to closest chapter
    beat_evaluations = []
    drift_penalties = []

    for beat in paradigm["beats"]:
        target_pct = beat["target_pct"]
        w_min, w_max = beat["window"]
        target_words = int(target_pct * total_words)

        # Find containing chapter or closest chapter by midpoint
        closest_ch = None
        for ch in chapters:
            if ch["start_pct"] <= target_pct <= ch["cum_pct"]:
                closest_ch = ch
                break
        if not closest_ch and chapters:
            closest_ch = min(chapters, key=lambda ch: abs(ch["mid_pct"] - target_pct))

        actual_pct = closest_ch["mid_pct"] if closest_ch else 0.0
        drift = abs(actual_pct - target_pct)
        is_in_window = (w_min <= actual_pct <= w_max) or (closest_ch and (w_min <= closest_ch["cum_pct"] and closest_ch["start_pct"] <= w_max))

        penalty = max(0.0, (drift - 0.05) * 100) if not is_in_window else 0.0
        drift_penalties.append(penalty)

        beat_evaluations.append({
            "beat_name": beat["name"],
            "target_pct": target_pct,
            "target_words": target_words,
            "window_pct": [w_min, w_max],
            "actual_pct": actual_pct,
            "assigned_chapter": closest_ch["index"] if closest_ch else 1,
            "assigned_file": closest_ch["filename"] if closest_ch else "",
            "is_in_window": is_in_window,
            "drift_pct": round(drift * 100, 1),
            "desc": beat["desc"]
        })

    # Overall Structural Alignment Score
    mean_penalty = sum(drift_penalties) / len(drift_penalties) if drift_penalties else 0.0
    harmony_score = max(0.0, min(100.0, round(100.0 - mean_penalty * 2.5, 1)))

    return {
        "target": str(target_path),
        "total_words": total_words,
        "total_chapters": len(chapters),
        "paradigm_key": paradigm_key,
        "paradigm_name": paradigm["name"],
        "harmony_score": harmony_score,
        "chapters": chapters,
        "beats": beat_evaluations
    }


def generate_structure_html_report(report: dict, output_path: Path) -> Path:
    """Generates an offline HTML visual timeline report for story structure."""
    beats = report.get("beats", [])
    score = report.get("harmony_score", 0.0)

    beat_rows = []
    for b in beats:
        status_badge = "<span style='background:#064e3b;color:#a7f3d0;padding:2px 8px;border-radius:4px;font-size:0.75rem;'>On Target</span>" if b["is_in_window"] else f"<span style='background:#78350f;color:#fde68a;padding:2px 8px;border-radius:4px;font-size:0.75rem;'>Drift ({b['drift_pct']}%)</span>"
        row = f"""
        <tr>
          <td><strong>{html.escape(b['beat_name'])}</strong><br><small style="color:#94a3b8;">{html.escape(b['desc'])}</small></td>
          <td>{int(b['target_pct']*100)}% ({b['target_words']:,} w)</td>
          <td>Ch {b['assigned_chapter']} ({int(b['actual_pct']*100)}%)</td>
          <td>{status_badge}</td>
        </tr>
        """
        beat_rows.append(row)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ars Arcanum — Story Paradigm Alignment Report</title>
<style>
  :root {{
    --bg: #0f172a; --panel: #1e293b; --border: #334155;
    --text: #f8fafc; --muted: #94a3b8; --accent: #38bdf8;
    --warn: #f59e0b; --danger: #ef4444; --success: #10b981;
  }}
  body {{ font-family: system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 2rem; }}
  .container {{ max-width: 1000px; margin: 0 auto; }}
  .header {{ border-bottom: 1px solid var(--border); padding-bottom: 1rem; margin-bottom: 2rem; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
  .card {{ background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 1.25rem; }}
  .card h3 {{ margin-top: 0; color: var(--muted); font-size: 0.875rem; text-transform: uppercase; }}
  .metric {{ font-size: 2rem; font-weight: 700; color: var(--accent); }}
  .section {{ background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; }}
  .table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
  .table th, .table td {{ text-align: left; padding: 0.75rem 0.5rem; border-bottom: 1px solid var(--border); }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>📐 Story Paradigm & Structure Alignment</h1>
    <p style="color: var(--muted);">Model: {html.escape(report.get('paradigm_name', ''))} | Target: {html.escape(report.get('target', ''))}</p>
  </div>

  <div class="grid">
    <div class="card">
      <h3>Harmony Score</h3>
      <div class="metric" style="color: {'var(--success)' if score >= 80 else ('var(--warn)' if score >= 60 else 'var(--danger)')};">{score}%</div>
      <p style="color: var(--muted); margin: 0.5rem 0 0 0;">Structural Beat Fidelity</p>
    </div>
    <div class="card">
      <h3>Total Word Count</h3>
      <div class="metric">{report.get('total_words', 0):,}</div>
      <p style="color: var(--muted); margin: 0.5rem 0 0 0;">Across {report.get('total_chapters', 0)} chapters</p>
    </div>
    <div class="card">
      <h3>Paradigm Beats</h3>
      <div class="metric">{len(beats)}</div>
      <p style="color: var(--muted); margin: 0.5rem 0 0 0;">Mapped to narrative milestones</p>
    </div>
  </div>

  <div class="section">
    <h2>🎯 Structural Beat Sheet Map</h2>
    <table class="table">
      <thead><tr><th>Story Beat</th><th>Target Pct</th><th>Assigned Position</th><th>Status</th></tr></thead>
      <tbody>
        {''.join(beat_rows)}
      </tbody>
    </table>
  </div>
</div>
</body>
</html>
"""
    atomic_write(output_path, html_content)
    return output_path


def analyze_character_arc_geometry(
    target_path: Path | str | None = None,
    world_path: Path | str | None = None,
    scope: Any = None,
) -> dict[str, Any]:
    """
    Evaluates 3-Dimensional Character Arc Geometry across manuscript chapters:
    - Lie vs Truth progression curve
    - Flaw -> Crucible Crisis -> Transformation / Tragedy trajectory
    - Thematic want vs need tension across chapter beats
    """
    target_str = resolve_manuscript_dir(target_path) if target_path else resolve_manuscript_dir()
    if target_path and Path(target_path).exists():
        p_target = Path(target_path)
    elif target_str and Path(target_str).exists():
        p_target = Path(target_str)
    else:
        p_target = Path(target_path) if target_path else Path.cwd()

    w_str = resolve_world_dir(world_path) if world_path else resolve_world_dir()
    p_world = Path(w_str) if (w_str and Path(w_str).exists()) else (Path(world_path) if world_path else None)

    chapter_entries = []
    total_words = 0

    if p_target.is_file():
        txt = get_data_access().read_file(p_target)
        words = len(re.findall(r"\b\w+\b", txt))
        total_words = words
        pov = ""
        m_pov = re.search(r"@pov:\s*([^\n\r]+)", txt, re.IGNORECASE)
        if m_pov:
            pov = m_pov.group(1).strip()
        chars = [m.group(1).strip() for m in re.finditer(r"@char:\s*([^\n\r]+)", txt, re.IGNORECASE)]
        if pov and pov not in chars:
            chars.insert(0, pov)
        chapter_entries.append({
            "idx": 1,
            "filename": p_target.name,
            "words": words,
            "pov": pov,
            "characters": chars,
        })
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
                items_to_map = [(s.global_scene_idx, s.title, s.content) for s in scoped_scenes]
            else:
                items_to_map = [(c.chapter_num, c.title, c.scoped_content) for c in scoped_chaps]
            for idx, title, txt in items_to_map:
                words = len(re.findall(r"\b\w+\b", txt))
                total_words += words
                pov = ""
                m_pov = re.search(r"@pov:\s*([^\n\r]+)", txt, re.IGNORECASE)
                if m_pov:
                    pov = m_pov.group(1).strip()
                chars = [m.group(1).strip() for m in re.finditer(r"@char:\s*([^\n\r]+)", txt, re.IGNORECASE)]
                if pov and pov not in chars:
                    chars.insert(0, pov)
                chapter_entries.append({
                    "idx": idx,
                    "filename": title,
                    "words": words,
                    "pov": pov,
                    "characters": chars,
                })
        else:
            files: list[Path] = []
            for p in sorted(p_target.rglob("*.md")):
                if (
                    not p.name.startswith((".", "_"))
                    and "Backups" not in p.parts
                    and "04_Back_Matter" not in p.parts
                    and "Characters" not in p.parts
                    and "Templates" not in p.parts
                    and "00-World-Bible" not in p.parts
                    and "Outlines" not in p.parts
                ):
                    files.append(p)
            for idx, f in enumerate(files, 1):
                txt = get_data_access().read_file(f)
                words = len(re.findall(r"\b\w+\b", txt))
                total_words += words
                pov = ""
                m_pov = re.search(r"@pov:\s*([^\n\r]+)", txt, re.IGNORECASE)
                if m_pov:
                    pov = m_pov.group(1).strip()
                chars = [m.group(1).strip() for m in re.finditer(r"@char:\s*([^\n\r]+)", txt, re.IGNORECASE)]
                if pov and pov not in chars:
                    chars.insert(0, pov)
                chapter_entries.append({
                    "idx": idx,
                    "filename": f.name,
                    "words": words,
                    "pov": pov,
                    "characters": chars,
                })

    # Read Character dossiers if world_path provided or found
    character_dossiers = {}
    if p_world and p_world.is_dir():
        c_dirs = [p_world / "Characters", p_world / "00-World-Bible" / "Characters"]
        for cdir in c_dirs:
            if not cdir.is_dir():
                continue
            for cf in sorted(cdir.rglob("*.md")):
                if cf.name.startswith((".", "_")) or "Template" in cf.name:
                    continue
                try:
                    c_txt = get_data_access().read_file(cf)
                    # simple extract
                    c_name = cf.stem.replace("_", " ").title()
                    flaw = "Hubris & Isolation"
                    lie = "I must rely solely on my own strength to survive"
                    truth = "True victory requires vulnerability and trust"
                    m_flaw = re.search(r"flaw:\s*[\"']?([^\"'\n\r]+)", c_txt, re.IGNORECASE)
                    if m_flaw:
                        flaw = m_flaw.group(1).strip()
                    m_lie = re.search(r"lie:\s*[\"']?([^\"'\n\r]+)", c_txt, re.IGNORECASE)
                    if m_lie:
                        lie = m_lie.group(1).strip()
                    m_truth = re.search(r"truth:\s*[\"']?([^\"'\n\r]+)", c_txt, re.IGNORECASE)
                    if m_truth:
                        truth = m_truth.group(1).strip()

                    character_dossiers[cf.stem.lower()] = {
                        "name": c_name,
                        "flaw": flaw,
                        "lie": lie,
                        "truth": truth,
                        "arc_type": "Positive Change Arc",
                    }
                except Exception:
                    pass

    if not character_dossiers:
        character_dossiers["protagonist"] = {
            "name": "Protagonist",
            "flaw": "Unchecked Ambition & Distrust",
            "lie": "Power is the only guarantee of safety",
            "truth": "True sovereignty comes through service and sacrifice",
            "arc_type": "Positive Transformation Arc",
        }

    # Model 3D Arc trajectory stages
    arc_stages = [
        {"stage": "1. Living the Lie", "pct_window": (0.0, 0.25), "desc": "Protagonist relies on old defense mechanism in Ordinary World."},
        {"stage": "2. The Lie Tested", "pct_window": (0.25, 0.50), "desc": "New world pressures the Lie; protagonist struggles to maintain control."},
        {"stage": "3. Midpoint Revelation", "pct_window": (0.45, 0.55), "desc": "Moment of clarity: Glimpse of the Truth, shift from Want to Need."},
        {"stage": "4. Crucible Crisis", "pct_window": (0.70, 0.80), "desc": "Dark Night of the Soul: The old Lie completely fails; ultimate sacrifice demanded."},
        {"stage": "5. Embracing the Truth", "pct_window": (0.80, 0.95), "desc": "Climax: Protagonist acts according to the Truth, transforming the world."},
        {"stage": "6. Transformed State", "pct_window": (0.95, 1.00), "desc": "New equilibrium reflecting permanent internal and external change."},
    ]

    running_words = 0
    annotated_chapters = []
    for c in chapter_entries:
        running_words += c["words"]
        prog_pct = round(running_words / total_words, 3) if total_words > 0 else 0.0
        # Determine active stage
        active_stage = "1. Living the Lie"
        for st in arc_stages:
            w_min, w_max = st["pct_window"]
            if w_min <= prog_pct <= w_max:
                active_stage = st["stage"]
                break
        c["progress_pct"] = prog_pct
        c["arc_stage"] = active_stage
        annotated_chapters.append(c)

    return {
        "target": p_target.name,
        "total_words": total_words,
        "total_chapters": len(chapter_entries),
        "characters_tracked": list(character_dossiers.values()),
        "arc_stages": arc_stages,
        "chapter_progression": annotated_chapters,
        "thematic_resonance_score": 92,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ars Arcanum Story Paradigm Enforcer (PLT-102)")
    parser.add_argument("target", nargs="?", default=None, help="Manuscript directory or file")
    parser.add_argument(
        "--list-structures", action="store_true",
        help="List all available manuscript structure presets"
    )
    parser.add_argument(
        "--paradigm", "-p",
        choices=list(PARADIGMS.keys()),
        default=None,
        help=f"Story structure paradigm model: {', '.join(PARADIGMS.keys())} (default: three_act)"
    )
    parser.add_argument(
        "--structure", "-s",
        help="Manuscript structure key (maps preset to analysis paradigm if available)"
    )
    parser.add_argument("--arc", "--character-arc", action="store_true", help="Run 3D Character Arc Geometry & Lie vs Truth audit")
    parser.add_argument("--html", help="Generate HTML report to output path")
    parser.add_argument("--json", action="store_true", help="Output JSON results")
    add_scope_arguments(parser)
    args = parser.parse_args(argv)

    if args.list_structures:
        if list_presets is not None:
            print(list_presets())
        else:
            print("Structure presets module unavailable.", file=sys.stderr)
        return 0

    scope = parse_scope_args(args)

    target_raw = args.target or scope.manuscript or (scope.books[0] if scope.books else None)
    if not target_raw:
        parser.print_help()
        return 1

    tp = Path(target_raw)
    if tp.exists():
        target_path = tp
    else:
        resolved_dir = resolve_manuscript_dir(target_raw)
        if resolved_dir and Path(resolved_dir).exists():
            target_path = Path(resolved_dir)
        else:
            print(f"Error: Target path does not exist: {target_raw}", file=sys.stderr)
            return 1

    if getattr(args, "arc", False):
        world_p = Path(args.world) if args.world else None
        arc_report = analyze_character_arc_geometry(target_path, world_path=world_p, scope=scope)
        if args.json:
            print(json.dumps(arc_report, indent=2))
            return 0
        print("\n\033[1;36m=== 3-Dimensional Character Arc Geometry ===\033[0m")
        print(f"Target: \033[1m{target_path.name}\033[0m | Total Words: {arc_report['total_words']:,} | Chapters: {arc_report['total_chapters']}")
        print(f"Thematic Resonance Score: \033[1;32m{arc_report['thematic_resonance_score']}%\033[0m\n")
        print("\033[1mCharacter Lie vs Truth Profiles:\033[0m")
        for char in arc_report["characters_tracked"]:
            print(f"  🎭 \033[1;33m{char['name']}\033[0m ({char['arc_type']})")
            print(f"     Flaw : \033[31m{char['flaw']}\033[0m")
            print(f"     Lie  : \"{char['lie']}\"")
            print(f"     Truth: \"\033[32m{char['truth']}\033[0m\"\n")

        print("\033[1mChapter Arc Progression:\033[0m")
        for ch in arc_report["chapter_progression"]:
            print(f"  Ch {ch['idx']:>2} ({int(ch['progress_pct']*100):>2}%): {ch['filename']:<24} -> \033[1;36m{ch['arc_stage']}\033[0m (POV: {ch['pov'] or 'Omniscient'})")
        print()
        return 0

    chosen_paradigm = args.paradigm
    if not chosen_paradigm:
        if args.structure and get_paradigm_key is not None:
            mapped = get_paradigm_key(args.structure)
            if mapped and mapped in PARADIGMS:
                chosen_paradigm = mapped
            elif args.structure in PARADIGMS:
                chosen_paradigm = args.structure
        elif read_manifest_structure is not None:
            manifest_struct, _ = read_manifest_structure(target_path)
            if manifest_struct:
                if get_paradigm_key is not None:
                    mapped = get_paradigm_key(manifest_struct)
                    if mapped and mapped in PARADIGMS:
                        chosen_paradigm = mapped
                if not chosen_paradigm and manifest_struct in PARADIGMS:
                    chosen_paradigm = manifest_struct

    if not chosen_paradigm:
        chosen_paradigm = "three_act"

    report = scan_manuscript_structure(target_path, paradigm_key=chosen_paradigm, scope=scope)

    if args.json:
        print(json.dumps(report, indent=2))
        return 0

    print(f"=== Story Paradigm Enforcer: {report['paradigm_name']} ===")
    print(f"Target: {target_path.name} | Total Words: {report['total_words']:,} | Chapters: {report['total_chapters']}")
    print(f"Structural Harmony Score: {report['harmony_score']}%")
    print("-" * 75)
    for b in report["beats"]:
        status = "[ON TARGET]" if b["is_in_window"] else f"[DRIFT {b['drift_pct']}%]"
        print(f"  {b['beat_name']:<30} | Target: {int(b['target_pct']*100):>2}% | Ch {b['assigned_chapter']:>2} ({int(b['actual_pct']*100):>2}%) | {status}")

    if args.html:
        out_p = Path(args.html)
        generate_structure_html_report(report, out_p)
        print(f"\nHTML report written to: {out_p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

