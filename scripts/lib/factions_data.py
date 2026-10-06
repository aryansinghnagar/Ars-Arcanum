#!/usr/bin/env python3
"""
Ars Arcanum Faction Combat, Logistics & Visualization Primitives
(scripts/lib/factions_data.py)
================================================================================
Zero-dependency Lanchester combat simulation, military campaign logistics,
Obsidian Mermaid diagram generator, and offline HTML report generator.
"""

import html
import math
import re
from pathlib import Path

__all__ = [
    "FRONTMATTER_REGEX",
    "WIKILINK_REGEX",
    "calc_campaign_logistics",
    "calc_lanchester_battle",
    "clean_link_name",
    "generate_faction_html_report",
    "generate_faction_mermaid",
    "normalize_name",
]

try:
    from lib._bootstrap import atomic_write
except ImportError:
    from _bootstrap import atomic_write

FRONTMATTER_REGEX = re.compile(r"^---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)", re.DOTALL)
WIKILINK_REGEX = re.compile(r"\[\[([^\]\|#]+)(?:\|[^\]\]]*)?\]\]")


def clean_link_name(raw: str) -> str:
    """Extracts entity name from wikilink or plain string."""
    if not raw:
        return ""
    m = WIKILINK_REGEX.search(str(raw))
    if m:
        return m.group(1).strip()
    return str(raw).strip().strip("\"'[]")


def normalize_name(name: str) -> str:
    """Normalizes string for comparison."""
    return re.sub(r"[\s_-]+", " ", str(name).strip().lower())


def generate_faction_mermaid(factions: dict) -> str:
    """Generates Obsidian-ready Mermaid.js relationship graph."""
    lines = ["```mermaid", "flowchart LR"]
    lines.append("    %% Faction Geopolitical Matrix")
    lines.append("    classDef empire fill:#1e293b,stroke:#38bdf8,stroke-width:2px,color:#f8fafc;")
    lines.append("    classDef guild fill:#1e293b,stroke:#4ade80,stroke-width:2px,color:#f8fafc;")
    lines.append("    classDef cult fill:#1e293b,stroke:#f43f5e,stroke-width:2px,color:#f8fafc;")
    lines.append("    classDef defaultNode fill:#0f172a,stroke:#64748b,stroke-width:1px,color:#f8fafc;")

    node_ids: dict[str, tuple[str, str]] = {}
    for idx, fname in enumerate(sorted(factions.keys())):
        nid = f"F{idx+1}"
        node_ids[normalize_name(fname)] = (nid, fname)
        ftype = factions[fname]["faction_type"]
        safe_name = fname.replace('"', "'")
        lines.append(f'    {nid}["{safe_name}<br/><small><i>{ftype}</i></small>"]')

    processed_edges: set[tuple[str, tuple[str, str]]] = set()

    for fname, finfo in factions.items():
        src_entry = node_ids.get(normalize_name(fname))
        if not src_entry:
            continue
        src_id = src_entry[0]

        # Alliances
        for a in finfo["allies"]:
            tgt_entry = node_ids.get(normalize_name(a))
            if tgt_entry:
                tgt_id = tgt_entry[0]
                edge_pair = tuple(sorted([src_id, tgt_id]))  # type: ignore[assignment]
                if ("ally", edge_pair) not in processed_edges:
                    processed_edges.add(("ally", edge_pair))  # type: ignore[arg-type]
                    lines.append(f"    {src_id} <==>|Ally| {tgt_id}")

        # Rivalries
        for r in finfo["rivals"]:
            tgt_entry = node_ids.get(normalize_name(r))
            if tgt_entry:
                tgt_id = tgt_entry[0]
                edge_pair = tuple(sorted([src_id, tgt_id]))  # type: ignore[assignment]
                if ("rival", edge_pair) not in processed_edges:
                    processed_edges.add(("rival", edge_pair))  # type: ignore[arg-type]
                    lines.append(f"    {src_id} -.->|Rival| {tgt_id}")

        # Vassalage
        for v in finfo["vassals"]:
            tgt_entry = node_ids.get(normalize_name(v))
            if tgt_entry:
                tgt_id = tgt_entry[0]
                lines.append(f"    {src_id} ==>|Vassal| {tgt_id}")

    lines.append("```")
    return "\n".join(lines)


def calc_lanchester_battle(
    attacker_force: float,
    defender_force: float,
    attacker_eff: float = 1.0,
    defender_eff: float = 1.0,
    fort_bonus: float = 1.0,
    law: str = "square",
    rounds: int = 20,
    morale_threshold: float = 0.5,
) -> dict:
    """
    Computes Lanchester combat engagement casualty curves and victor prediction.

    Laws:
    - square: Modern/aimed ranged firepower. dA/dt = -beta * D, dD/dt = -alpha * A
    - linear: Melee/un-aimed area fire. dA/dt = -beta * (A*D) / D or constant rate
    """
    a = float(attacker_force)
    d = float(defender_force)
    alpha = float(attacker_eff)
    beta = float(defender_eff) * float(fort_bonus)

    a_initial = a
    d_initial = d
    a_morale_limit = a_initial * (1.0 - morale_threshold)
    d_morale_limit = d_initial * (1.0 - morale_threshold)

    history = [{
        "round": 0,
        "attacker_remaining": round(a),
        "defender_remaining": round(d),
        "attacker_casualties": 0,
        "defender_casualties": 0,
    }]

    dt = 0.1
    current_time = 0.0
    victor = "Draw"
    outcome_reason = "Max rounds reached"

    total_steps = rounds * 10
    for step in range(1, total_steps + 1):
        if a <= 0 or d <= 0 or a <= a_morale_limit or d <= d_morale_limit:
            break

        if law == "square":
            da = beta * d * dt
            dd = alpha * a * dt
        else:
            # Linear law: Melee front line engagement bounded by contact width min(a, d)
            contact = min(a, d)
            da = beta * contact * dt
            dd = alpha * contact * dt

        a = max(0.0, a - da)
        d = max(0.0, d - dd)
        current_time += dt

        if step % 10 == 0:
            history.append({
                "round": step // 10,
                "attacker_remaining": round(a),
                "defender_remaining": round(d),
                "attacker_casualties": round(a_initial - a),
                "defender_casualties": round(d_initial - d),
            })

    if a <= a_morale_limit and d <= d_morale_limit:
        victor = "Mutual Morale Collapse / Pyrrhic Draw"
        outcome_reason = "Both forces suffered critical morale breakage (>50% casualties)."
    elif a <= a_morale_limit or a <= 0:
        victor = "Defender"
        outcome_reason = "Attacker broken or destroyed."
    elif d <= d_morale_limit or d <= 0:
        victor = "Attacker"
        outcome_reason = "Defender broken or destroyed."
    else:
        victor = "Attacker" if (a / a_initial) > (d / d_initial) else "Defender"
        outcome_reason = "Inconclusive engagement; advantage based on casualty ratio."

    return {
        "law": law,
        "initial_attacker": round(a_initial),
        "initial_defender": round(d_initial),
        "final_attacker": round(a),
        "final_defender": round(d),
        "attacker_loss_pct": round((a_initial - a) / a_initial * 100, 1) if a_initial else 0,
        "defender_loss_pct": round((d_initial - d) / d_initial * 100, 1) if d_initial else 0,
        "victor": victor,
        "outcome_reason": outcome_reason,
        "rounds_simulated": len(history) - 1,
        "history": history,
    }


def calc_campaign_logistics(
    infantry: int,
    cavalry: int,
    support: int = 0,
    distance_km: float = 200.0,
    march_speed_km_day: float = 20.0,
    ration_kg_soldier: float = 1.5,
    water_liters_soldier: float = 3.0,
    fodder_kg_mount: float = 10.0,
    wagon_payload_kg: float = 500.0,
    draft_horses_per_wagon: int = 2,
    forage_pct: float = 0.0,
) -> dict:
    """
    Calculates campaign supply requirements, daily consumption, wagon train logistics,
    and the theoretical operational 'Wagon Radius' (point of self-starvation).
    """
    total_soldiers = infantry + cavalry + support
    total_mounts = cavalry  # Base cavalry mounts

    # Daily consumption
    daily_food_kg = total_soldiers * ration_kg_soldier * (1.0 - forage_pct)
    daily_water_liters = total_soldiers * water_liters_soldier
    daily_fodder_kg = total_mounts * fodder_kg_mount * (1.0 - forage_pct)

    total_daily_supply_kg = daily_food_kg + daily_water_liters + daily_fodder_kg
    daily_metric_tons = total_daily_supply_kg / 1000.0

    days_one_way = distance_km / max(1.0, march_speed_km_day)
    total_campaign_days = days_one_way * 2.0  # Round trip supply expectation

    # Wagon train calculation
    # Each wagon carries wagon_payload_kg. Draft animals also consume fodder!
    draft_animal_consumption_day_per_wagon = draft_horses_per_wagon * fodder_kg_mount * (1.0 - forage_pct)

    # Wagon Radius formula: R_max = (Wagon Payload / (2 * Draft Animal Daily Fodder)) * March Speed
    if draft_animal_consumption_day_per_wagon > 0:
        max_wagon_days = wagon_payload_kg / (2.0 * draft_animal_consumption_day_per_wagon)
        max_wagon_radius_km = max_wagon_days * march_speed_km_day
    else:
        max_wagon_days = 999.0
        max_wagon_radius_km = 99999.0

    total_supplies_needed_kg = total_daily_supply_kg * total_campaign_days
    # Extra draft horses needed for wagons
    wagons_needed = math.ceil(total_supplies_needed_kg / max(1.0, wagon_payload_kg))
    draft_horses_total = wagons_needed * draft_horses_per_wagon

    feasible = distance_km <= max_wagon_radius_km

    return {
        "army_composition": {
            "infantry": infantry,
            "cavalry": cavalry,
            "support": support,
            "total_personnel": total_soldiers,
            "cavalry_mounts": cavalry,
            "draft_horses": draft_horses_total,
        },
        "campaign_parameters": {
            "distance_km": distance_km,
            "march_speed_km_day": march_speed_km_day,
            "duration_days_one_way": round(days_one_way, 1),
            "duration_days_round_trip": round(total_campaign_days, 1),
            "forage_discount_pct": round(forage_pct * 100, 1),
        },
        "daily_consumption": {
            "food_kg": round(daily_food_kg, 1),
            "water_liters": round(daily_water_liters, 1),
            "cavalry_fodder_kg": round(daily_fodder_kg, 1),
            "total_daily_supply_tons": round(daily_metric_tons, 2),
        },
        "logistics_requirements": {
            "total_campaign_supply_tons": round(total_supplies_needed_kg / 1000.0, 2),
            "wagons_required": wagons_needed,
            "draft_horses_required": draft_horses_total,
            "wagon_radius_limit_km": round(max_wagon_radius_km, 1),
            "is_within_wagon_radius": feasible,
            "logistics_verdict": "Feasible without intermediate depots" if feasible else "SUPPLY FAILURE: Exceeds wagon radius limit. Depots or forage required.",
        },
    }


def generate_faction_html_report(audit_data: dict, output_path: Path):
    """Generates a standalone dark-mode HTML report for the Faction Matrix & Campaign Logistics."""
    factions = audit_data.get("factions", {})
    findings = audit_data.get("findings", [])
    world_name = audit_data.get("world", "World Bible")

    rows = []
    for fn, f in factions.items():
        allies_str = ", ".join(f["allies"]) if f["allies"] else "None"
        rivals_str = ", ".join(f["rivals"]) if f["rivals"] else "None"
        vassals_str = ", ".join(f["vassals"]) if f["vassals"] else "None"
        rows.append(f"""
        <tr>
            <td><strong>{html.escape(fn)}</strong></td>
            <td><span class="badge badge-type">{html.escape(f['faction_type'])}</span></td>
            <td>{html.escape(f['leader'])}</td>
            <td>{f['military_strength']:,.0f}</td>
            <td style="color: #4ade80;">{html.escape(allies_str)}</td>
            <td style="color: #f87171;">{html.escape(rivals_str)}</td>
            <td style="color: #cbd5e1;">{html.escape(vassals_str)}</td>
        </tr>
        """)

    findings_rows = []
    for fd in findings:
        badge_cls = "badge-error" if fd["severity"] == "ERROR" else "badge-warning"
        findings_rows.append(f"""
        <div class="card finding-card">
            <span class="badge {badge_cls}">{html.escape(fd['severity'])}</span>
            <strong>{html.escape(fd['id'])}</strong>: {html.escape(fd['message'])}
            <div style="font-size: 0.85em; color: #94a3b8; margin-top: 4px;">Faction: {html.escape(fd.get('faction', ''))} | File: {html.escape(fd.get('file', ''))}</div>
        </div>
        """)

    findings_html = "".join(findings_rows) if findings_rows else "<div style='color: #4ade80;'>✓ No diplomatic paradoxes detected across factions.</div>"

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ars Arcanum — Geopolitical Faction Matrix ({html.escape(world_name)})</title>
<style>
  :root {{
    --bg: #0f172a;
    --card-bg: #1e293b;
    --border: #334155;
    --text: #f8fafc;
    --accent: #38bdf8;
    --danger: #f43f5e;
    --warning: #fbbf24;
    --success: #34d399;
  }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background-color: var(--bg);
    color: var(--text);
    margin: 0;
    padding: 2rem;
  }}
  .container {{ max-width: 1200px; margin: 0 auto; }}
  h1, h2, h3 {{ color: var(--accent); }}
  .card {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 1rem;
  }}
  th, td {{
    padding: 0.75rem;
    text-align: left;
    border-bottom: 1px solid var(--border);
  }}
  th {{ background: #0f172a; color: var(--accent); }}
  .badge {{
    display: inline-block;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: bold;
    text-transform: uppercase;
  }}
  .badge-type {{ background: #0369a1; color: #fff; }}
  .badge-warning {{ background: #d97706; color: #fff; }}
  .badge-error {{ background: #b91c1c; color: #fff; }}
  .finding-card {{ margin-bottom: 0.75rem; }}
</style>
</head>
<body>
<div class="container">
  <h1>⚔️ Ars Arcanum Geopolitical Faction Matrix</h1>
  <p>World Lore Vault: <strong>{html.escape(world_name)}</strong> | Total Factions: <strong>{len(factions)}</strong></p>

  <div class="card">
    <h2>Diplomatic Paradox Diagnostics ({len(findings)})</h2>
    {findings_html}
  </div>

  <div class="card">
    <h2>Faction Diplomatic Roster</h2>
    <table>
      <thead>
        <tr>
          <th>Faction</th>
          <th>Type</th>
          <th>Leader</th>
          <th>Military Strength</th>
          <th>Allies</th>
          <th>Rivals</th>
          <th>Vassals</th>
        </tr>
      </thead>
      <tbody>
        {"".join(rows)}
      </tbody>
    </table>
  </div>
</div>
</body>
</html>
"""
    atomic_write(output_path, html_content)
