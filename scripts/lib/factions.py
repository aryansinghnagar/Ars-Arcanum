#!/usr/bin/env python3
"""
Ars Arcanum Geopolitical Faction Matrix & Campaign Logistics Engine (scripts/lib/factions.py)
=============================================================================================
Zero-dependency, offline geopolitical relationship matrix, diplomatic paradox detector,
Lanchester power-law combat simulator, and military campaign logistics calculator.

Capabilities:
1. Geopolitical Faction Matrix & Relationship Graphs:
   - Scans World Bible `Factions/*.md` frontmatter.
   - Normalizes diplomatic ties (allies, rivals, vassals, overlords, treaties).
   - Detects diplomatic paradoxes:
     * FAC-101: Asymmetric Diplomatic Link (A lists B as ally, B lists A as rival/none).
     * FAC-102: Triad Tension Paradox (A allies B, B allies C, but A and C are declared rivals).
     * FAC-103: Vassal Allegiance Conflict (Vassal of A is allied with Rival of A).
     * FAC-104: Self-Contradiction / Self-Reference (Faction allied or rival with itself).
2. Obsidian Mermaid.js Relationship Visualizer:
   - Emits Obsidian-ready Mermaid flowcharts with color-coded allegiance links.
3. Standalone Interactive HTML/SVG Matrix:
   - Standalone dark-themed report with relationship chord matrix and network visualization.
4. Lanchester Power-Law Combat Calculator (`calc battle`):
   - Simulates Linear Law (un-aimed/isolated melee) and Square Law (concentrated/aimed ranged fire).
   - Incorporates fortification defense multipliers, combat effectiveness coefficients, and morale break points.
5. Military Campaign Logistics Calculator (`calc logistics`):
   - Computes daily soldier rations (food & water) and cavalry mount fodder requirements.
   - Calculates wagon train requirements, draft animal consumption, and maximum "Wagon Radius" operating distance.

Zero external dependencies; 100% offline privacy.
"""

import argparse
import json
import logging
import sys
from pathlib import Path

__all__ = [
    "FRONTMATTER_REGEX",
    "WIKILINK_REGEX",
    "audit_faction_diplomacy",
    "calc_campaign_logistics",
    "calc_lanchester_battle",
    "clean_link_name",
    "extract_faction_profiles",
    "generate_faction_html_report",
    "generate_faction_mermaid",
    "main",
    "normalize_name",
    "resolve_world_dir",
]

try:
    from lib._bootstrap import atomic_write
    from lib.factions_data import (
        FRONTMATTER_REGEX,
        WIKILINK_REGEX,
        calc_campaign_logistics,
        calc_lanchester_battle,
        clean_link_name,
        generate_faction_html_report,
        generate_faction_mermaid,
        normalize_name,
    )
    from lib.frontmatter import parse_yaml_frontmatter
    from lib.scope import (
        add_scope_arguments,
        resolve_world_path,
    )
except ImportError:
    from _bootstrap import atomic_write
    from factions_data import (  # type: ignore[no-redef]
        FRONTMATTER_REGEX,
        WIKILINK_REGEX,
        calc_campaign_logistics,
        calc_lanchester_battle,
        clean_link_name,
        generate_faction_html_report,
        generate_faction_mermaid,
        normalize_name,
    )
    from frontmatter import parse_yaml_frontmatter
    from scope import (  # type: ignore[no-redef]
        add_scope_arguments,
        resolve_world_path,
    )

logger = logging.getLogger("arcanum.factions")


def extract_faction_profiles(world_dir: Path) -> dict:
    """Scans World Bible Factions/ directory and extracts structured profiles."""
    factions = {}
    dirs_to_check = [
        world_dir / "Factions",
        world_dir / "00-World-Bible" / "Factions",
    ]

    seen_files = set()
    for fdir in dirs_to_check:
        if not fdir.is_dir():
            continue
        for md_file in sorted(fdir.rglob("*.md")):
            if md_file in seen_files or md_file.name.startswith(".") or "Template" in md_file.name:
                continue
            seen_files.add(md_file)
            try:
                content = md_file.read_text(encoding="utf-8", errors="ignore")
                fm = parse_yaml_frontmatter(content)
                name = fm.get("name") or md_file.stem.replace("_", " ").replace("-", " ")

                # Extract allies
                raw_allies = fm.get("allies") or fm.get("ally") or []
                if isinstance(raw_allies, str):
                    raw_allies = [raw_allies]
                allies = [clean_link_name(a) for a in raw_allies if clean_link_name(a)]

                # Extract rivals
                raw_rivals = fm.get("rivals") or fm.get("rival") or fm.get("enemies") or []
                if isinstance(raw_rivals, str):
                    raw_rivals = [raw_rivals]
                rivals = [clean_link_name(r) for r in raw_rivals if clean_link_name(r)]

                # Extract vassals
                raw_vassals = fm.get("vassals") or fm.get("vassal") or []
                if isinstance(raw_vassals, str):
                    raw_vassals = [raw_vassals]
                vassals = [clean_link_name(v) for v in raw_vassals if clean_link_name(v)]

                # Extract overlord
                overlord = clean_link_name(fm.get("overlord") or fm.get("suzerain") or "")

                # Extract treaties
                raw_treaties = fm.get("treaties") or fm.get("pacts") or []
                if isinstance(raw_treaties, str):
                    raw_treaties = [raw_treaties]
                treaties = [clean_link_name(t) for t in raw_treaties if clean_link_name(t)]

                # Strength / military
                military_strength = fm.get("military_strength", 1000)
                try:
                    military_strength = float(military_strength)
                except (ValueError, TypeError):
                    military_strength = 1000.0

                factions[name] = {
                    "name": name,
                    "file": str(md_file.relative_to(world_dir)),
                    "faction_type": str(fm.get("faction_type", "Faction")),
                    "leader": clean_link_name(fm.get("leader", "Unknown")),
                    "headquarters": clean_link_name(fm.get("headquarters", "Unknown")),
                    "influence_level": str(fm.get("influence_level", "Regional")),
                    "military_strength": military_strength,
                    "allies": allies,
                    "rivals": rivals,
                    "vassals": vassals,
                    "overlord": overlord,
                    "treaties": treaties,
                }
            except Exception as e:
                logger.warning("Failed to parse %s: %s", md_file, e)

    return factions


def audit_faction_diplomacy(factions: dict) -> list:
    """Detects diplomatic paradoxes and asymmetric alliances across factions."""
    findings = []
    norm_map = {normalize_name(k): k for k in factions}

    for fname, f_info in factions.items():
        fn_norm = normalize_name(fname)

        # 1. Self-reference check (FAC-104)
        for a in f_info["allies"]:
            if normalize_name(a) == fn_norm:
                findings.append({
                    "id": "FAC-104",
                    "severity": "WARNING",
                    "faction": fname,
                    "message": f"Faction '{fname}' lists itself as an ally.",
                    "file": f_info["file"],
                })
        for r in f_info["rivals"]:
            if normalize_name(r) == fn_norm:
                findings.append({
                    "id": "FAC-104",
                    "severity": "WARNING",
                    "faction": fname,
                    "message": f"Faction '{fname}' lists itself as a rival.",
                    "file": f_info["file"],
                })

        # 2. Asymmetric Alliance / Rivalry check (FAC-101)
        for ally in f_info["allies"]:
            anorm = normalize_name(ally)
            if anorm in norm_map:
                target_real = norm_map[anorm]
                target_info = factions[target_real]
                target_allies_norm = [normalize_name(x) for x in target_info["allies"]]
                target_rivals_norm = [normalize_name(x) for x in target_info["rivals"]]

                if fn_norm in target_rivals_norm:
                    findings.append({
                        "id": "FAC-101",
                        "severity": "OBSERVATION",
                        "faction": fname,
                        "message": f"Geopolitical Tension / Secret Betrayal: '{fname}' lists '{target_real}' as an ally, but '{target_real}' lists '{fname}' as a rival.",
                        "file": f_info["file"],
                    })
                elif fn_norm not in target_allies_norm:
                    findings.append({
                        "id": "FAC-101",
                        "severity": "OBSERVATION",
                        "faction": fname,
                        "message": f"Asymmetric Alliance: '{fname}' claims alliance with '{target_real}', but '{target_real}' does not reciprocate in frontmatter.",
                        "file": f_info["file"],
                    })

        # 3. Triad Paradox: Ally of Enemy (FAC-102)
        # If A is ally with B, and B is ally with C, but A is rival with C
        for b_name in f_info["allies"]:
            bnorm = normalize_name(b_name)
            if bnorm in norm_map:
                b_info = factions[norm_map[bnorm]]
                for c_name in b_info["allies"]:
                    cnorm = normalize_name(c_name)
                    if cnorm == fn_norm:
                        continue
                    # Check if A considers C a rival
                    if cnorm in [normalize_name(x) for x in f_info["rivals"]]:
                        c_real = norm_map.get(cnorm, c_name)
                        b_real = norm_map[bnorm]
                        findings.append({
                            "id": "FAC-102",
                            "severity": "OBSERVATION",
                            "faction": fname,
                            "message": f"Triad Tension Paradox: '{fname}' is allied with '{b_real}', who is allied with '{c_real}', but '{fname}' and '{c_real}' are declared rivals.",
                            "file": f_info["file"],
                        })

        # 4. Vassal Allegiance Conflict (FAC-103)
        for v_name in f_info["vassals"]:
            vnorm = normalize_name(v_name)
            if vnorm in norm_map:
                v_info = factions[norm_map[vnorm]]
                v_allies_norm = [normalize_name(x) for x in v_info["allies"]]
                # Check if vassal is allied with any of overlord's rivals
                for r_name in f_info["rivals"]:
                    rnorm = normalize_name(r_name)
                    if rnorm in v_allies_norm:
                        v_real = norm_map[vnorm]
                        r_real = norm_map.get(rnorm, r_name)
                        findings.append({
                            "id": "FAC-103",
                            "severity": "OBSERVATION",
                            "faction": fname,
                            "message": f"Vassal Intrigue / Conflict: Vassal '{v_real}' of overlord '{fname}' is allied with overlord's rival '{r_real}'.",
                            "file": f_info["file"],
                        })

    return findings


def resolve_world_dir(target_str: str | None = None) -> str:
    """Resolves world input string (path or name) to absolute directory path."""
    if target_str:
        p = Path(target_str).expanduser().resolve()
        if p.is_dir():
            return str(p)
        home = Path.home()
        for u_dir in sorted((home / "Universes").glob("*/*")):
            if u_dir.is_dir() and u_dir.name.lower() == target_str.lower():
                return str(u_dir)
        for w_dir in sorted((home / "Worlds").glob("*")):
            if w_dir.is_dir() and w_dir.name.lower() == target_str.lower():
                return str(w_dir)
        p_cwd = Path.cwd() / target_str
        if p_cwd.is_dir():
            return str(p_cwd)

    home = Path.home()
    universes = sorted((home / "Universes").glob("*/*"), key=lambda p: str(p))
    universes = [p for p in universes if p.is_dir() and p.name not in ("Worlds", ".git")]
    if len(universes) == 1:
        return str(universes[0])
    if len(universes) > 1:
        print("Error: Multiple worlds discovered — specify one explicitly.", file=sys.stderr)
        sys.exit(2)
    else:
        worlds = sorted((home / "Worlds").glob("*"), key=lambda p: str(p))
        worlds = [p for p in worlds if p.is_dir()]
        if len(worlds) == 1:
            return str(worlds[0])
        if len(worlds) > 1:
            print("Error: Multiple legacy worlds discovered — specify one explicitly.", file=sys.stderr)
            sys.exit(2)
    return ""


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Geopolitical Faction Matrix & Campaign Logistics Engine")
    subparsers = parser.add_subparsers(dest="subcommand", help="Faction subcommands")

    # 1. matrix / audit (default)
    p_audit = subparsers.add_parser("check", help="Run diplomatic consistency audit on faction relations")
    p_audit.add_argument("world", nargs="?", help="World Bible lore directory")
    p_audit.add_argument("-w", "--world", dest="world_flag", help="World Bible lore directory")
    p_audit.add_argument("--strict", action="store_true", help="Fail with non-zero exit code if issues are found")
    p_audit.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    p_audit.add_argument("--html", help="Path to export standalone HTML report")
    p_audit.add_argument("--write-note", help="Export Mermaid.js relationship graph to note")
    add_scope_arguments(p_audit, target_pos_arg=False, include_manuscript=False, include_world=False)

    p_matrix = subparsers.add_parser("matrix", help="Display faction matrix and relationship graph")
    p_matrix.add_argument("world", nargs="?", help="World Bible lore directory")
    p_matrix.add_argument("-w", "--world", dest="world_flag", help="World Bible lore directory")
    p_matrix.add_argument("--strict", action="store_true", help="Fail with non-zero exit code if issues are found")
    p_matrix.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    p_matrix.add_argument("--html", help="Path to export standalone HTML report")
    p_matrix.add_argument("--write-note", help="Export Mermaid.js relationship graph to note")
    add_scope_arguments(p_matrix, target_pos_arg=False, include_manuscript=False, include_world=False)

    # 2. calc battle
    p_battle = subparsers.add_parser("battle", help="Lanchester power-law combat calculator")
    p_battle.add_argument("-a", "--attacker", type=float, required=True, help="Attacker starting force")
    p_battle.add_argument("-d", "--defender", type=float, required=True, help="Defender starting force")
    p_battle.add_argument("--attacker-eff", type=float, default=1.0, help="Attacker combat effectiveness (default 1.0)")
    p_battle.add_argument("--defender-eff", type=float, default=1.0, help="Defender combat effectiveness (default 1.0)")
    p_battle.add_argument("--fort", type=float, default=1.0, help="Fortification defense multiplier (default 1.0)")
    p_battle.add_argument("--law", choices=["square", "linear"], default="square", help="Lanchester law (square or linear)")
    p_battle.add_argument("--rounds", type=int, default=20, help="Max combat rounds (default 20)")
    p_battle.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # 3. calc logistics
    p_log = subparsers.add_parser("logistics", help="Military campaign supply and wagon radius calculator")
    p_log.add_argument("--infantry", type=int, default=10000, help="Infantry troop count")
    p_log.add_argument("--cavalry", type=int, default=2000, help="Cavalry mounted troops count")
    p_log.add_argument("--support", type=int, default=1000, help="Support/camp follower count")
    p_log.add_argument("--distance", type=float, default=200.0, help="Campaign distance in km (default 200)")
    p_log.add_argument("--speed", type=float, default=20.0, help="March speed in km/day (default 20)")
    p_log.add_argument("--forage", type=float, default=0.0, help="Local forage fraction 0.0 to 1.0 (default 0.0)")
    p_log.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    if len(sys.argv) > 1 and sys.argv[1] not in ("check", "matrix", "battle", "logistics", "-h", "--help", "-v", "--version"):
        sys.argv.insert(1, "check")

    args = parser.parse_args()

    if not args.subcommand:
        # Default to matrix check if world argument passed or no subcommand
        args.subcommand = "check"

    if args.subcommand in ("check", "matrix"):
        raw_world = getattr(args, "world_flag", None) or getattr(args, "world", None)
        world_dir_str = str(resolve_world_path(raw_world)) if resolve_world_path(raw_world) else resolve_world_dir(raw_world)
        if not world_dir_str or not Path(world_dir_str).is_dir():
            print("Error: No valid World Bible directory specified or discovered.", file=sys.stderr)
            sys.exit(2)

        world_path = Path(world_dir_str)
        factions = extract_faction_profiles(world_path)
        findings = audit_faction_diplomacy(factions)
        mermaid_graph = generate_faction_mermaid(factions)

        audit_data = {
            "world": world_path.name,
            "factions_count": len(factions),
            "findings_count": len(findings),
            "factions": factions,
            "findings": findings,
            "mermaid": mermaid_graph,
        }

        if getattr(args, "json", False):
            print(json.dumps(audit_data, indent=2))
        else:
            print("\n\033[1;36m=== Ars Arcanum Geopolitical Faction Matrix ===\033[0m")
            print(f"World: \033[1m{world_path.name}\033[0m | Total Factions: \033[32m{len(factions)}\033[0m")
            print(f"Diplomatic Paradoxes / Issues: \033[1m{len(findings)}\033[0m\n")

            if factions:
                print("\033[1mRegistered Factions & Diplomatic Alignments:\033[0m")
                for fn, finfo in factions.items():
                    print(f"  👑 \033[1;33m{fn}\033[0m [{finfo['faction_type']}] — Military Strength: {finfo['military_strength']:,.0f}")
                    if finfo["allies"]:
                        print(f"     Allies : \033[32m{', '.join(finfo['allies'])}\033[0m")
                    if finfo["rivals"]:
                        print(f"     Rivals : \033[31m{', '.join(finfo['rivals'])}\033[0m")
                    if finfo["vassals"]:
                        print(f"     Vassals: \033[34m{', '.join(finfo['vassals'])}\033[0m")
                print()

            if not findings:
                print("\033[32m[OK] Diplomatic matrix is internally consistent (no paradoxes).\033[0m")
            else:
                for fd in findings:
                    badge = f"\033[31m[{fd['severity']}]\033[0m" if fd["severity"] == "ERROR" else f"\033[33m[{fd['severity']}]\033[0m"
                    print(f"{badge} {fd['id']}: {fd['message']}")
                    print(f"     File: {fd['file']}\n")

        if getattr(args, "write_note", None):
            note_p = Path(args.write_note)
            atomic_write(note_p, mermaid_graph)
            print(f"\nObsidian Mermaid note written to: {note_p}")

        if getattr(args, "html", None):
            out_p = Path(args.html)
            generate_faction_html_report(audit_data, out_p)
            print(f"\nInteractive HTML report written to: {out_p}")

        sys.exit(1 if len(findings) > 0 and getattr(args, "strict", False) else 0)

    elif args.subcommand == "battle":
        result = calc_lanchester_battle(
            attacker_force=args.attacker,
            defender_force=args.defender,
            attacker_eff=args.attacker_eff,
            defender_eff=args.defender_eff,
            fort_bonus=args.fort,
            law=args.law,
            rounds=args.rounds,
        )
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"\n\033[1;35m=== Lanchester Combat Simulation ({args.law.capitalize()} Law) ===\033[0m")
            print(f"Initial Forces : Attacker \033[1;31m{result['initial_attacker']:,}\033[0m vs Defender \033[1;34m{result['initial_defender']:,}\033[0m (Fort bonus: {args.fort}x)")
            print(f"Final Forces   : Attacker \033[1;31m{result['final_attacker']:,}\033[0m (-{result['attacker_loss_pct']}%) | Defender \033[1;34m{result['final_defender']:,}\033[0m (-{result['defender_loss_pct']}%)")
            print(f"Outcome        : \033[1;32m{result['victor']}\033[0m — {result['outcome_reason']}")
            print(f"Combat Rounds  : {result['rounds_simulated']}\n")
        sys.exit(0)

    elif args.subcommand == "logistics":
        result = calc_campaign_logistics(
            infantry=args.infantry,
            cavalry=args.cavalry,
            support=args.support,
            distance_km=args.distance,
            march_speed_km_day=args.speed,
            forage_pct=args.forage,
        )
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            comp = result["army_composition"]
            cons = result["daily_consumption"]
            req = result["logistics_requirements"]
            param = result["campaign_parameters"]

            print("\n\033[1;36m=== Military Campaign Logistics & Supply Calculator ===\033[0m")
            print(f"Personnel      : {comp['total_personnel']:,} ({comp['infantry']:,} inf, {comp['cavalry']:,} cav, {comp['support']:,} support)")
            print(f"Campaign March : {param['distance_km']} km @ {param['march_speed_km_day']} km/day ({param['duration_days_one_way']} days one-way)")
            print(f"Daily Demand   : {cons['food_kg']:,} kg food, {cons['water_liters']:,} L water, {cons['cavalry_fodder_kg']:,} kg fodder ({cons['total_daily_supply_tons']} metric tons/day)")
            print(f"Wagon Train    : {req['wagons_required']:,} wagons ({req['draft_horses_required']:,} draft horses)")
            print(f"Wagon Radius   : \033[1m{req['wagon_radius_limit_km']} km\033[0m maximum operational limit")
            verdict_col = "\033[32m" if req["is_within_wagon_radius"] else "\033[31m"
            print(f"Verdict        : {verdict_col}{req['logistics_verdict']}\033[0m\n")
        sys.exit(0)


if __name__ == "__main__":
    main()


