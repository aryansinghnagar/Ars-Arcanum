#!/usr/bin/env python3
"""
Ars Arcanum Manuscript Structure Scaffolding Engine
(scripts/lib/manuscript_scaffold.py)
================================================================================
Zero-dependency, offline manuscript directory and structure scaffolding engine.

Capabilities:
1. Pluggable Narrative Structure Presets:
   - 16 built-in narrative framework presets (Classic Three-Act, Hero's Journey,
     Save the Cat!, Story Circle, Kishōtenketsu, 7-Point, Fichtean Curve,
     8-Sequence, Freytag's Pyramid, MICE Quotient, Romancing the Beat,
     The Virgin's Promise, Snowflake Method, Parallel/Multi-POV, Episodic,
     Nonlinear/Fragmented).
2. Arbitrary Custom Division Layouts:
   - User-defined named divisions with strict identifier sanitization.
3. Path Traversal & Injection Defense:
   - Regex validation (`^[A-Za-z0-9_-]+$`) rejecting all directory traversal tokens.
4. Atomic & Idempotent File Operations:
   - Uses atomic_write and directory collision checks.
5. Analysis Paradigm Linking:
   - Bridges scaffolding presets to structure.py narrative pacing paradigms.

Zero external dependencies; 100% offline privacy.
"""

import argparse
import datetime
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    from lib._bootstrap import atomic_write
except ImportError:
    try:
        from _bootstrap import atomic_write
    except ImportError:
        def atomic_write(path: Path | str, data: Any, encoding: str = "utf-8") -> None:  # type: ignore[no-redef]
            import os as _os
            import tempfile as _tf
            p = Path(path).resolve()
            p.parent.mkdir(parents=True, exist_ok=True)
            is_bytes = isinstance(data, (bytes, bytearray))
            fd, tmp = _tf.mkstemp(dir=p.parent, prefix=f".{p.name}.", suffix=".tmp")
            try:
                if is_bytes:
                    with _os.fdopen(fd, "wb") as f:
                        f.write(data)
                        f.flush()
                        _os.fsync(f.fileno())
                else:
                    with _os.fdopen(fd, "w", encoding=encoding, newline="") as f:
                        f.write(str(data))
                        f.flush()
                        _os.fsync(f.fileno())
                _os.replace(tmp, p)
            except BaseException:
                try:
                    Path(tmp).unlink(missing_ok=True)
                except OSError:
                    pass
                raise

# -----------------------------------------------------------------------------
# 16 Structure Presets Registry
# -----------------------------------------------------------------------------

STRUCTURE_PRESETS: dict[str, dict[str, Any]] = {
    "three_act": {
        "name": "Classic Three-Act Structure",
        "paradigm_key": "three_act",
        "divisions": [
            {"label": "Act_I", "desc": "Setup — establish protagonist, world, and inciting incident"},
            {"label": "Act_II", "desc": "Confrontation — rising action, midpoint, complications"},
            {"label": "Act_III", "desc": "Resolution — climax, denouement, new equilibrium"},
        ],
    },
    "freytags_pyramid": {
        "name": "Freytag's Dramatic Pyramid",
        "paradigm_key": "freytags_pyramid",
        "divisions": [
            {"label": "Exposition", "desc": "Background, setting, character establishment"},
            {"label": "Rising_Action", "desc": "Series of events building suspense"},
            {"label": "Climax", "desc": "Central turning point and maximum intensity"},
            {"label": "Falling_Action", "desc": "Aftermath and tightening threads"},
            {"label": "Denouement", "desc": "Final resolution and unknotting"},
        ],
    },
    "heros_journey": {
        "name": "Hero's Journey (Monomyth)",
        "paradigm_key": "heros_journey",
        "divisions": [
            {"label": "Departure", "desc": "Ordinary world, call to adventure, crossing the threshold"},
            {"label": "Initiation", "desc": "Trials, ordeal, reward in the special world"},
            {"label": "Return", "desc": "Road back, resurrection, return with elixir"},
        ],
    },
    "save_the_cat": {
        "name": "Save the Cat! Beat Sheet",
        "paradigm_key": "save_the_cat",
        "divisions": [
            {"label": "Act_I-Setup", "desc": "Opening image through break into two"},
            {"label": "Act_II-Fun_and_Games", "desc": "Promise of the premise through dark night"},
            {"label": "Act_III-Finale", "desc": "Break into three through final image"},
        ],
    },
    "story_circle": {
        "name": "Dan Harmon Story Circle",
        "paradigm_key": "story_circle",
        "divisions": [
            {"label": "Comfort_Zone", "desc": "You — character in comfort, wanting something"},
            {"label": "Unfamiliar_World", "desc": "Go & Search — adapting to the unknown"},
            {"label": "Return_Path", "desc": "Find & Pay — getting and paying the price"},
            {"label": "Transformation", "desc": "Return & Change — returning transformed"},
        ],
    },
    "kishotenketsu": {
        "name": "Kishōtenketsu (起承転結)",
        "paradigm_key": "kishotenketsu",
        "divisions": [
            {"label": "Ki-Introduction", "desc": "起 — introduces characters, setting, tone"},
            {"label": "Sho-Development", "desc": "承 — expands without major conflict"},
            {"label": "Ten-Twist", "desc": "転 — unexpected element or perspective shift"},
            {"label": "Ketsu-Reconciliation", "desc": "結 — harmonizes twist with premise"},
        ],
    },
    "seven_point": {
        "name": "Seven-Point Story Structure",
        "paradigm_key": "seven_point",
        "divisions": [
            {"label": "Hook_and_Turn", "desc": "Hook, Plot Turn 1, and first pinch point"},
            {"label": "Midpoint_and_Reversal", "desc": "Midpoint pivot and second pinch point"},
            {"label": "Resolution", "desc": "Plot Turn 2 and climactic resolution"},
        ],
    },
    "fichtean_curve": {
        "name": "The Fichtean Curve",
        "paradigm_key": "fichtean_curve",
        "divisions": [
            {"label": "Rising_Crises", "desc": "Escalating crises from exposition to point of no return"},
            {"label": "Climax_and_Resolution", "desc": "Supreme confrontation and denouement"},
        ],
    },
    "eight_sequence": {
        "name": "Eight-Sequence Method",
        "paradigm_key": "eight_sequence",
        "divisions": [
            {"label": "Seq_A-Status_Quo", "desc": "Ordinary world and inciting event"},
            {"label": "Seq_B-Lock_In", "desc": "Predicament formulated, protagonist committed"},
            {"label": "Seq_C-First_Obstacle", "desc": "First major barrier encountered"},
            {"label": "Seq_D-Midpoint_Crisis", "desc": "Crucial revelation, point of no return"},
            {"label": "Seq_E-Complications", "desc": "Rising complications, subplot climax"},
            {"label": "Seq_F-Act_II_Climax", "desc": "Highest tension, all hope lost"},
            {"label": "Seq_G-Final_Twist", "desc": "Discovery of unexpected path forward"},
            {"label": "Seq_H-Resolution", "desc": "Ultimate resolution and new equilibrium"},
        ],
    },
    "mice_quotient": {
        "name": "MICE Quotient (Orson Scott Card)",
        "paradigm_key": None,
        "divisions": [
            {"label": "Milieu", "desc": "World/setting-driven thread — arrival to departure"},
            {"label": "Idea", "desc": "Mystery/inquiry thread — question to answer"},
            {"label": "Character", "desc": "Identity/growth thread — discontent to shift"},
            {"label": "Event", "desc": "Status quo disruption thread — incident to new order"},
        ],
    },
    "romancing_the_beat": {
        "name": "Romancing the Beat (Gwen Hayes)",
        "paradigm_key": "romancing_the_beat",
        "divisions": [
            {"label": "Setup_and_Meet", "desc": "Introductions, meet cute, inciting incident"},
            {"label": "Romance_and_Retreat", "desc": "Attraction, midpoint love, pulling away"},
            {"label": "Black_Moment_and_HEA", "desc": "Breakup, grand gesture, happily ever after"},
        ],
    },
    "virgins_promise": {
        "name": "The Virgin's Promise (Kim Hudson)",
        "paradigm_key": "virgins_promise",
        "divisions": [
            {"label": "Dependent_World", "desc": "Conformity, price of fitting in, opportunity to shine"},
            {"label": "Secret_World", "desc": "Hidden self, caught shining, giving up old beliefs"},
            {"label": "Reorder", "desc": "Kingdom in chaos, wilderness, choosing the light"},
        ],
    },
    "snowflake": {
        "name": "Snowflake Method (Flat Chapters)",
        "paradigm_key": None,
        "divisions": [
            {"label": "Chapters", "desc": "Flat chapter layout — iteratively expanded from summary"},
        ],
    },
    "parallel": {
        "name": "Parallel / Multi-POV Structure",
        "paradigm_key": None,
        "divisions": [
            {"label": "Thread-A", "desc": "First narrative thread or POV"},
            {"label": "Thread-B", "desc": "Second narrative thread or POV"},
            {"label": "Thread-C", "desc": "Third narrative thread or POV"},
        ],
    },
    "episodic": {
        "name": "Episodic Structure",
        "paradigm_key": None,
        "divisions": [
            {"label": "Episode-01", "desc": "Self-contained episode with internal arc"},
            {"label": "Episode-02", "desc": "Self-contained episode with internal arc"},
            {"label": "Episode-03", "desc": "Self-contained episode with internal arc"},
        ],
    },
    "nonlinear": {
        "name": "Nonlinear / Fragmented Structure",
        "paradigm_key": None,
        "divisions": [
            {"label": "Fragment-01", "desc": "Non-chronological narrative segment"},
            {"label": "Fragment-02", "desc": "Non-chronological narrative segment"},
            {"label": "Fragment-03", "desc": "Non-chronological narrative segment"},
        ],
    },
}


# -----------------------------------------------------------------------------
# Validation & Helper Primitives
# -----------------------------------------------------------------------------

def validate_division_name(name: str) -> str:
    """Validate division name against path traversal and forbidden characters.

    Enforces strict token pattern ^[A-Za-z0-9_-]+$.
    Raises ValueError on validation failure.
    """
    if not name or not isinstance(name, str) or not name.strip():
        raise ValueError("Division name cannot be empty.")
    name = name.strip()
    if ".." in name or "/" in name or "\\" in name:
        raise ValueError(f"Invalid division name '{name}': path traversal characters ('..', '/', '\\') are not allowed.")
    if not re.match(r"^[A-Za-z0-9_-]+$", name):
        raise ValueError(f"Invalid division name '{name}': only alphanumeric characters, hyphens, and underscores allowed.")
    return name


def get_preset(structure_key: str) -> dict[str, Any] | None:
    """Retrieve preset definition by key."""
    if not structure_key:
        return None
    return STRUCTURE_PRESETS.get(structure_key.strip().lower())


def get_paradigm_key(structure_key: str) -> str | None:
    """Map scaffold structure preset key to structure.py analysis paradigm key."""
    preset = get_preset(structure_key)
    if preset:
        return preset.get("paradigm_key")
    return None


def list_presets() -> str:
    """Format and return all available manuscript structure presets for CLI display."""
    lines = [
        "=" * 78,
        "Ars Arcanum — Manuscript Structure Presets (16 Built-in + Custom)",
        "=" * 78,
    ]
    for key, info in STRUCTURE_PRESETS.items():
        paradigm = info.get("paradigm_key")
        paradigm_str = f" [Analysis: {paradigm}]" if paradigm else ""
        lines.append(f"\n* {key}: {info['name']}{paradigm_str}")
        for div in info["divisions"]:
            lines.append(f"    - {div['label']}: {div['desc']}")
    lines.append("\n* custom: User-defined division list (e.g. --divisions 'Prologue,Act_I,Act_II,Epilogue')")
    lines.append("=" * 78)
    return "\n".join(lines)


# -----------------------------------------------------------------------------
# Scaffolding Engine
# -----------------------------------------------------------------------------

def scaffold_volume(
    target_dir: Path | str,
    structure_key: str = "three_act",
    custom_divisions: list[str] | None = None,
    create_starter_chapter: bool = True,
) -> list[Path]:
    """Scaffold numbered division directories under a volume directory.

    Args:
        target_dir: Path to the target volume directory (e.g., Book-01).
        structure_key: Structure preset key from STRUCTURE_PRESETS, or 'custom'.
        custom_divisions: List of custom division names if structure_key is 'custom'
                          or when overriding preset divisions.
        create_starter_chapter: Whether to create 01_Chapter_01.md in the first division.

    Returns:
        List of created division directory Path objects.

    Raises:
        ValueError: For unknown structure preset or invalid/empty division names.
        FileExistsError: If any of the target division directories already exist.
    """
    target_path = Path(target_dir)
    norm_key = (structure_key or "three_act").strip().lower()

    if norm_key == "custom" or (custom_divisions is not None and len(custom_divisions) > 0):
        if not custom_divisions:
            raise ValueError("Custom structure requires at least one division name specified via custom_divisions.")
        division_names = [validate_division_name(d) for d in custom_divisions if d and d.strip()]
        if not division_names:
            raise ValueError("Custom structure requires at least one non-empty division name.")
    else:
        preset = get_preset(norm_key)
        if not preset:
            valid_keys = ", ".join(STRUCTURE_PRESETS.keys())
            raise ValueError(f"Unknown structure preset '{structure_key}'. Choose from: {valid_keys}, custom")
        division_names = [d["label"] for d in preset["divisions"]]

    if not division_names:
        raise ValueError("No divisions specified to scaffold.")

    # Check for directory collisions before creating anything
    planned_dirs: list[Path] = []
    for idx, div_name in enumerate(division_names, 1):
        dir_name = f"{idx:02d}_{div_name}"
        div_path = target_path / dir_name
        if div_path.exists():
            raise FileExistsError(f"Division directory '{div_path.name}' already exists in '{target_path}'.")
        planned_dirs.append(div_path)

    # Atomic creation of parent and division directories
    target_path.mkdir(parents=True, exist_ok=True)
    created_dirs: list[Path] = []
    for div_path in planned_dirs:
        div_path.mkdir(parents=True, exist_ok=False)
        created_dirs.append(div_path)

    # Create starter chapter in first division if requested
    if create_starter_chapter and created_dirs:
        starter_file = created_dirs[0] / "01_Chapter_01.md"
        if not starter_file.exists():
            vol_name = target_path.name or "Book-01"
            content = f"# Chapter 1\n\nBegin writing {vol_name} here...\n"
            atomic_write(starter_file, content)

    return created_dirs


# -----------------------------------------------------------------------------
# Manifest Helper Functions
# -----------------------------------------------------------------------------

def generate_manuscript_manifest(
    title: str,
    author: str = "Author Name",
    universe: str = "Default-Universe",
    world: str = "",
    structure: str = "three_act",
    custom_divisions: list[str] | None = None,
    created_at: str | None = None,
) -> str:
    """Generate YAML manifest content for manuscript.yaml."""
    date_str = created_at or datetime.date.today().isoformat()
    lines = [
        "# Ars Arcanum Manuscript Manifest",
        'schema_version: "1.1"',
        f'title: "{title}"',
        f'author: "{author}"',
        f'universe: "{universe or "Default-Universe"}"',
        f'world: "{world or ""}"',
        f'structure: "{structure}"',
    ]
    if structure == "custom" and custom_divisions:
        lines.append("custom_divisions:")
        for div in custom_divisions:
            clean_div = validate_division_name(div)
            lines.append(f'  - "{clean_div}"')
    lines.append(f'created_at: "{date_str}"\n')
    return "\n".join(lines)


def read_manifest_structure(manuscript_dir: Path | str) -> tuple[str, list[str] | None]:
    """Read manuscript.yaml and return (structure_key, custom_divisions).

    Searches in manuscript_dir and traverses parent directories until manuscript.yaml
    is located or filesystem root is reached.
    """
    p = Path(manuscript_dir).resolve()
    yaml_file: Path | None = None
    cur: Path = p if p.is_dir() else p.parent
    while True:
        candidate = cur / "manuscript.yaml"
        if candidate.exists() and candidate.is_file():
            yaml_file = candidate
            break
        if cur.parent == cur:
            break
        cur = cur.parent

    if yaml_file is None or not yaml_file.exists():
        return "three_act", None

    try:
        content = yaml_file.read_text(encoding="utf-8", errors="replace")
        structure_match = re.search(r'^\s*structure:\s*["\']?([^"\n\r\']+)["\']?', content, re.MULTILINE)
        structure_key = structure_match.group(1).strip() if structure_match else "three_act"

        custom_divs: list[str] = []
        if "custom_divisions:" in content:
            div_block = content.split("custom_divisions:", 1)[1]
            for line in div_block.splitlines():
                if line.strip().startswith("-"):
                    val = re.sub(r'^\s*-\s*["\']?([^"\n\r\']+)["\']?', r'\1', line).strip()
                    if val:
                        custom_divs.append(val)
                elif line.strip() and not line.startswith(" ") and not line.startswith("\t"):
                    break
        return structure_key, (custom_divs if custom_divs else None)
    except Exception:
        return "three_act", None


# -----------------------------------------------------------------------------
# CLI Entry Point
# -----------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    """CLI dispatcher for manuscript scaffolding."""
    parser = argparse.ArgumentParser(
        description="Ars Arcanum Manuscript Structure Scaffolding Engine",
    )
    parser.add_argument(
        "--list-structures", "--list", "-l",
        action="store_true",
        help="List all available manuscript structure presets",
    )

    subparsers = parser.add_subparsers(dest="subcommand")

    # scaffold subcommand
    scaffold_p = subparsers.add_parser("scaffold", help="Scaffold volume divisions")
    scaffold_p.add_argument("target", help="Target volume directory path")
    scaffold_p.add_argument(
        "--structure", "-s",
        default="three_act",
        help=f"Structure preset key ({', '.join(STRUCTURE_PRESETS.keys())}, custom)",
    )
    scaffold_p.add_argument(
        "--divisions", "-d",
        help="Comma-separated custom division names (for 'custom' structure)",
    )
    scaffold_p.add_argument(
        "--no-starter",
        action="store_true",
        help="Do not create starter chapter (01_Chapter_01.md)",
    )

    # list subcommand
    list_p = subparsers.add_parser("list", help="List all available structure presets")
    list_p.add_argument("--json", action="store_true", help="Output presets in JSON format")

    # info subcommand
    info_p = subparsers.add_parser("info", help="Show details for a structure preset")
    info_p.add_argument("preset", help="Structure preset key")

    args = parser.parse_args(argv)

    if args.list_structures or args.subcommand == "list":
        if getattr(args, "json", False):
            print(json.dumps(STRUCTURE_PRESETS, indent=2))
        else:
            print(list_presets())
        return 0

    if args.subcommand == "info":
        preset = get_preset(args.preset)
        if not preset:
            print(f"Error: Unknown structure preset '{args.preset}'.", file=sys.stderr)
            return 1
        print(f"Structure Preset: {preset['name']} ({args.preset})")
        print(f"Analysis Paradigm: {preset.get('paradigm_key') or 'None (structural scaffold only)'}")
        print("Divisions:")
        for idx, div in enumerate(preset["divisions"], 1):
            print(f"  {idx:02d}_{div['label']}: {div['desc']}")
        return 0

    if args.subcommand == "scaffold":
        custom_divs = None
        if args.divisions:
            custom_divs = [d.strip() for d in args.divisions.split(",") if d.strip()]
        try:
            created = scaffold_volume(
                target_dir=Path(args.target),
                structure_key=args.structure,
                custom_divisions=custom_divs,
                create_starter_chapter=not args.no_starter,
            )
            print(f"[✓] Scaffolded {len(created)} division(s) for structure '{args.structure}' in: {args.target}")
            for d in created:
                print(f"    └── {d.name}")
            return 0
        except (ValueError, FileExistsError) as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"Error scaffolding volume: {e}", file=sys.stderr)
            return 2

    # If no subcommand provided, show help
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
