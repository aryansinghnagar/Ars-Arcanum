#!/usr/bin/env python3
"""
Ars Arcanum Interstellar & Regional Trade Modeling Engine
(scripts/lib/economy_trade.py)
================================================================================
Models freight transport margins, settlement trade network gravity flows,
and supply shock ripple propagation across markets.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    from lib.data_access import get_data_access
    from lib.frontmatter import parse_yaml_frontmatter
except ImportError:
    try:
        from data_access import get_data_access
        from frontmatter import parse_yaml_frontmatter
    except ImportError:
        def parse_yaml_frontmatter(text: str) -> dict[str, Any]:
            if not text.startswith("---"):
                return {}
            parts = text.split("---", 2)
            if len(parts) < 3:
                return {}
            data: dict[str, Any] = {}
            for line in parts[1].splitlines():
                line = line.strip()
                if ":" in line and not line.startswith("#"):
                    k, v = line.split(":", 1)
                    data[k.strip()] = v.strip().strip("\"'")
            return data

        def get_data_access() -> Any:
            return None


def calc_trade_margin(
    buy_price_per_ton: float,
    sell_price_per_ton: float,
    cargo_tons: float,
    distance_km_or_ly: float,
    transit_cost_per_ton_unit: float = 0.5,
    tariff_pct: float = 0.05,
    spoilage_pct: float = 0.02,
) -> dict[str, Any]:
    """Calculates trade route profitability, break-even threshold, and net margin."""
    total_cargo_buy_cost = buy_price_per_ton * cargo_tons
    gross_revenue_potential = sell_price_per_ton * cargo_tons * (1.0 - spoilage_pct)

    total_transit_cost = transit_cost_per_ton_unit * distance_km_or_ly * cargo_tons
    total_tariffs = gross_revenue_potential * tariff_pct

    total_expenses = total_cargo_buy_cost + total_transit_cost + total_tariffs
    net_profit = gross_revenue_potential - total_expenses
    roi_pct = (net_profit / max(1.0, total_expenses)) * 100.0

    # Break-even sell price per ton
    break_even_sell_price = total_expenses / max(1.0, cargo_tons * (1.0 - spoilage_pct))

    return {
        "buy_price_per_ton": buy_price_per_ton,
        "sell_price_per_ton": sell_price_per_ton,
        "cargo_tons": cargo_tons,
        "distance": distance_km_or_ly,
        "gross_revenue": round(gross_revenue_potential, 2),
        "total_transit_cost": round(total_transit_cost, 2),
        "total_tariffs": round(total_tariffs, 2),
        "net_profit": round(net_profit, 2),
        "roi_pct": round(roi_pct, 1),
        "break_even_sell_price_per_ton": round(break_even_sell_price, 2),
        "is_profitable": net_profit > 0,
        "verdict": "Profitable Trade Route" if net_profit > 0 else "Unprofitable: Transit/Tariff costs exceed price spread",
    }


def extract_settlement_network(world_dir: Path | None) -> list[dict[str, Any]]:
    """Scans Locations/*.md in World Bible to extract settlements, populations, and trade goods."""
    settlements: list[dict[str, Any]] = []
    dal = get_data_access()
    if world_dir and world_dir.is_dir():
        loc_dirs = [world_dir / "Locations", world_dir / "00-World-Bible" / "Locations"]
        for ldir in loc_dirs:
            if not ldir.is_dir():
                continue
            for md_file in sorted(ldir.rglob("*.md")):
                if md_file.name.startswith((".", "_")) or "Template" in md_file.name:
                    continue
                try:
                    content = dal.read_file(md_file) if dal else md_file.read_text(encoding="utf-8", errors="ignore")
                    fm = parse_yaml_frontmatter(content)
                    loc_type = str(fm.get("type") or fm.get("location_type") or "").lower()
                    if loc_type in ("city", "town", "settlement", "citadel", "colony", "port", "capital", "station") or fm.get("population"):
                        pop = float(fm.get("population", 25000))
                        gdp = float(fm.get("gdp", fm.get("economic_output", pop * 1.5)))
                        exports = fm.get("exports") or fm.get("primary_exports") or ["grain", "textiles"]
                        if isinstance(exports, str):
                            exports = [e.strip() for e in exports.split(",") if e.strip()]
                        imports = fm.get("imports") or fm.get("primary_imports") or ["iron", "timber"]
                        if isinstance(imports, str):
                            imports = [i.strip() for i in imports.split(",") if i.strip()]
                        settlements.append({
                            "id": md_file.stem,
                            "name": str(fm.get("name") or md_file.stem.replace("_", " ")),
                            "population": pop,
                            "economic_output": gdp,
                            "exports": exports,
                            "imports": imports,
                            "file": str(md_file.relative_to(world_dir)).replace("\\", "/"),
                        })
                except Exception:
                    pass

    if len(settlements) < 2:
        # Provide representative settlement network
        settlements = [
            {"id": "SunCitadel", "name": "Sun Citadel", "population": 120000, "economic_output": 250000, "exports": ["solar_crystals", "refined_steel"], "imports": ["grain", "timber"]},
            {"id": "WhisperingVale", "name": "Whispering Vale", "population": 45000, "economic_output": 70000, "exports": ["grain", "herbal_medicine"], "imports": ["refined_steel", "tools"]},
            {"id": "HighSanctuary", "name": "High Sanctuary", "population": 30000, "economic_output": 90000, "exports": ["relics", "astronomical_optics"], "imports": ["grain", "wine"]},
            {"id": "OuterRimPort", "name": "Outer Rim Port", "population": 60000, "economic_output": 110000, "exports": ["rare_ores", "void_leather"], "imports": ["solar_crystals", "medicine"]},
        ]

    return settlements


def calculate_gravity_trade_flow(
    settlements: list[dict[str, Any]],
    friction_matrix: dict[str, float] | None = None,
    g_constant: float = 1.0,
    distance_exponent: float = 1.5,
) -> dict[str, Any]:
    """
    Computes bilateral trade flow volumes and route viability using the economic gravity model:
    T_ij = G * (M_i * M_j) / (D_ij^alpha * (1 + friction_ij))
    """
    if not settlements:
        return {"settlements_count": 0, "routes": []}

    routes: list[dict[str, Any]] = []
    total_network_trade = 0.0

    for i in range(len(settlements)):
        for j in range(i + 1, len(settlements)):
            s1 = settlements[i]
            s2 = settlements[j]

            id1 = str(s1.get("id", s1.get("name", f"settlement_{i}")))
            id2 = str(s2.get("id", s2.get("name", f"settlement_{j}")))

            pop1 = float(s1.get("population", 10000))
            pop2 = float(s2.get("population", 10000))
            gdp1 = float(s1.get("economic_output", pop1 * 1.0))
            gdp2 = float(s2.get("economic_output", pop2 * 1.0))

            dist = float(s1.get("distances", {}).get(id2, s2.get("distances", {}).get(id1, 100.0)))
            if dist <= 0:
                dist = 1.0

            friction = 0.0
            if friction_matrix:
                friction = friction_matrix.get(f"{id1}_{id2}", friction_matrix.get(f"{id2}_{id1}", 0.0))
            else:
                terrain = str(s1.get("terrain_to", {}).get(id2, "plains")).lower()
                terrain_frictions = {
                    "plains": 0.1,
                    "road": 0.0,
                    "forest": 0.4,
                    "hills": 0.5,
                    "mountains": 1.2,
                    "swamp": 1.5,
                    "desert": 1.0,
                    "ocean": 0.2,
                    "space_vacuum": 0.05,
                }
                friction = terrain_frictions.get(terrain, 0.3)

            denom = (dist ** distance_exponent) * (1.0 + friction)
            trade_volume = g_constant * (gdp1 * gdp2) / denom if denom > 0 else 0.0

            total_network_trade += trade_volume

            exp1 = s1.get("exports", ["manufactured_goods"])
            exp2 = s2.get("exports", ["raw_materials"])

            routes.append({
                "origin": id1,
                "origin_name": s1.get("name", id1),
                "destination": id2,
                "destination_name": s2.get("name", id2),
                "distance_km": dist,
                "terrain_friction": round(friction, 2),
                "annual_trade_volume": round(trade_volume, 2),
                "primary_flow_1_to_2": exp1[:2],
                "primary_flow_2_to_1": exp2[:2],
                "viability": "High" if trade_volume > 50000 else ("Medium" if trade_volume > 10000 else "Low"),
            })

    routes.sort(key=lambda r: r["annual_trade_volume"], reverse=True)

    return {
        "settlements_count": len(settlements),
        "total_network_trade": round(total_network_trade, 2),
        "routes": routes,
    }


def simulate_supply_shock(
    settlements: list[dict[str, Any]],
    shock_event: str,
    target_settlement_id: str,
    affected_commodity: str,
    shock_magnitude: float = 0.6,
) -> dict[str, Any]:
    """
    Simulates supply shock propagation through the settlement trade network:
    Calculates localized scarcity multipliers, price inflation, and narrative conflict hooks.
    """
    gravity_res = calculate_gravity_trade_flow(settlements)
    routes = gravity_res["routes"]

    target_settlement = next(
        (s for s in settlements if str(s.get("id", "")).lower() == target_settlement_id.lower() or str(s.get("name", "")).lower() == target_settlement_id.lower()),
        None,
    )
    if not target_settlement and settlements:
        target_settlement = settlements[0]
        target_settlement_id = str(target_settlement.get("id", target_settlement.get("name", "Origin")))

    target_name = target_settlement.get("name", target_settlement_id) if target_settlement else target_settlement_id

    # Node impact matrix
    market_impacts: dict[str, dict[str, Any]] = {}
    for s in settlements:
        sid = str(s.get("id", s.get("name", "")))
        sname = str(s.get("name", sid))
        is_epicenter = (sid.lower() == target_settlement_id.lower())

        # Baseline exposure based on distance and route connection to epicenter
        if is_epicenter:
            scarcity_pct = round(shock_magnitude * 100, 1)
            price_mult = round(1.0 + (shock_magnitude * 2.5), 2)
            tier = "Epicenter (Critical)"
        else:
            # Check route connectivity to target
            connected_route = next(
                (r for r in routes if (r["origin"].lower() == target_settlement_id.lower() and r["destination"].lower() == sid.lower()) or (r["destination"].lower() == target_settlement_id.lower() and r["origin"].lower() == sid.lower())),
                None,
            )
            if connected_route:
                dist = connected_route["distance_km"]
                decay = max(0.1, 1.0 - (dist / 1000.0))
                scarcity_pct = round(shock_magnitude * decay * 70, 1)
                price_mult = round(1.0 + (shock_magnitude * decay * 1.8), 2)
                tier = "Direct Trading Partner"
            else:
                scarcity_pct = round(shock_magnitude * 20, 1)
                price_mult = round(1.0 + (shock_magnitude * 0.4), 2)
                tier = "Peripheral Market"

        market_impacts[sid] = {
            "name": sname,
            "tier": tier,
            "scarcity_index_pct": scarcity_pct,
            "commodity": affected_commodity,
            "price_multiplier": price_mult,
            "market_stress": "Emergency" if price_mult >= 2.0 else ("Severe" if price_mult >= 1.4 else "Moderate"),
        }

    # Narrative conflict advice
    story_hooks = [
        f"Smuggling syndicates establish covert trade routes to exploit the {affected_commodity} price spike ({market_impacts.get(target_settlement_id, {}).get('price_multiplier', 2.0)}x) at {target_name}.",
        f"Civil unrest and rationing laws instituted across {target_name} and neighboring markets.",
        f"Rival factions leverage stockpiles of {affected_commodity} for diplomatic coercion or extortion.",
    ]

    return {
        "shock_event": shock_event,
        "epicenter_id": target_settlement_id,
        "epicenter_name": target_name,
        "commodity": affected_commodity,
        "shock_magnitude_pct": round(shock_magnitude * 100, 1),
        "market_impacts": list(market_impacts.values()),
        "narrative_conflict_hooks": story_hooks,
    }


def resolve_world_dir(target_str: str | None = None) -> str:
    """Resolves world input string (path or name) to absolute directory path."""
    import sys
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


def resolve_manuscript_dir(target_str: str | None = None) -> str:
    """Resolves manuscript input string (path or name) to absolute directory path."""
    if target_str:
        p = Path(target_str).expanduser().resolve()
        if p.is_dir():
            return str(p)
        home = Path.home()
        for m_dir in sorted((home / "Manuscripts").glob("*")):
            if m_dir.is_dir() and m_dir.name.lower() == target_str.lower():
                return str(m_dir)
        p_cwd = Path.cwd() / target_str
        if p_cwd.is_dir():
            return str(p_cwd)
    return ""

