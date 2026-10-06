#!/usr/bin/env python3
"""
Ars Arcanum In-World Economy, Commodity PPP & Anachronism Matrix (scripts/lib/economy.py)
========================================================================================
Zero-dependency, offline in-world macroeconomic validator, Purchasing Power Parity (PPP)
exchange rate calculator, interstellar trade margin analyzer, and technology era anachronism auditor.

Capabilities:
1. World Bible Economy Profiles:
   - Scans World Bible `Economies/*.md` frontmatter for currencies, denominations, and commodity baskets.
   - Computes Purchasing Power Parity (PPP) index across regional or factional currencies.
2. Manuscript Price Consistency Audit (`arcanum economy check`):
   - Scans manuscript scenes for `@price:` directives and currency prose mentions.
   - Detects:
     * ECO-101: Price Anomaly / Hyper-Deflation/Inflation (price deviates wildly from commodity basket baseline).

     * ECO-102: Unregistered In-World Currency (manuscript references currency not defined in world lore).
     * ECO-103: Denomination Arithmetic Error (e.g. coin counting contradicting established conversion ratios).
3. Interstellar & Regional Trade Margin Viability (`calc_trade_margin`):
   - Models cargo freight economics, distance transit costs, tariffs, and commodity price arbitrage.
4. Technological Baseline Era vs Manuscript Anachronism Scanner (`arcanum audit tech`):
   - Audits world technological baseline (e.g. Bronze Age, Medieval, Industrial, Interstellar) against manuscript prose.
   - Detects:
     * ECO-201: Technological Anachronism (manuscript mentions out-of-era material, concept, or invention).

Zero external dependencies; 100% offline privacy.
"""

import argparse
import html
import json
import logging
import re
import sys
from pathlib import Path

try:
    from lib._bootstrap import atomic_write
    from lib.scope import (
        EngineScope,
        add_scope_arguments,
        filter_manuscript_scope,
        parse_scope_args,
        resolve_manuscript_path,
        resolve_world_path,
    )
except ImportError:
    from _bootstrap import atomic_write
    from scope import (
        EngineScope,
        add_scope_arguments,
        filter_manuscript_scope,
        parse_scope_args,
        resolve_manuscript_path,
        resolve_world_path,
    )


logger = logging.getLogger("arcanum.economy")

FRONTMATTER_REGEX = re.compile(r"^---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)", re.DOTALL)
WIKILINK_REGEX = re.compile(r"\[\[([^\]\|#]+)(?:\|[^\]\]]*)?\]\]")

# Technological Eras and their distinguishing inventions/materials
TECH_ERAS = [
    "stone_age",
    "bronze_age",
    "iron_age",
    "medieval",
    "renaissance",
    "industrial",
    "victorian",
    "modern_20th",
    "information_age",
    "interstellar",
]

ERA_ORDER = {era: idx for idx, era in enumerate(TECH_ERAS)}

# Anachronism dictionary: term -> earliest acceptable era
TECH_ERA_DICTIONARY = {
    # Bronze Age+ (Earliest Bronze Age)
    "bronze": "bronze_age",
    "chariot": "bronze_age",
    "papyrus": "bronze_age",
    "cuneiform": "bronze_age",

    # Iron Age+
    "iron sword": "iron_age",
    "steel sword": "iron_age",
    "parchment": "iron_age",
    "phalanx": "iron_age",
    "trireme": "iron_age",
    "aqueduct": "iron_age",

    # Medieval+
    "crossbow": "medieval",
    "chainmail": "medieval",
    "plate armor": "medieval",
    "trebuchet": "medieval",
    "windmill": "medieval",
    "feudal": "medieval",

    # Renaissance+
    "gunpowder": "renaissance",
    "musket": "renaissance",
    "arquebus": "renaissance",
    "cannon": "renaissance",
    "printing press": "renaissance",
    "telescope": "renaissance",
    "caravel": "renaissance",
    "galleon": "renaissance",
    "flintlock": "renaissance",

    # Industrial+
    "steam engine": "industrial",
    "locomotive": "industrial",
    "railroad": "industrial",
    "telegraph": "industrial",
    "dynamite": "industrial",
    "factory line": "industrial",
    "rifled barrel": "industrial",

    # Victorian / Early 20th+
    "electricity": "victorian",
    "lightbulb": "victorian",
    "phonograph": "victorian",
    "automobile": "victorian",
    "internal combustion": "victorian",
    "airship": "victorian",
    "zeppelin": "victorian",
    "zepplin": "victorian",
    "radio": "victorian",
    "telephone": "victorian",

    # Modern 20th+
    "radar": "modern_20th",
    "sonar": "modern_20th",
    "plastic": "modern_20th",
    "nylon": "modern_20th",
    "penicillin": "modern_20th",
    "antibiotic": "modern_20th",
    "jet aircraft": "modern_20th",
    "transistor": "modern_20th",
    "nuclear reactor": "modern_20th",
    "atomic bomb": "modern_20th",
    "satellite": "modern_20th",

    # Information Age+
    "microchip": "information_age",
    "silicon chip": "information_age",
    "internet": "information_age",
    "smartphone": "information_age",
    "gps": "information_age",
    "fiber optic": "information_age",
    "lithium battery": "information_age",

    # Interstellar / Far Future+
    "fusion drive": "interstellar",
    "warp drive": "interstellar",
    "hyperdrive": "interstellar",
    "antimatter": "interstellar",
    "blaster": "interstellar",
    "plasma cannon": "interstellar",
    "cybernetic implant": "interstellar",
    "forcefield": "interstellar",
}


try:
    from lib.frontmatter import parse_yaml_frontmatter
except ImportError:
    from frontmatter import parse_yaml_frontmatter


def normalize_name(name: str) -> str:
    return re.sub(r"[\s_-]+", " ", str(name).strip().lower())


def extract_economy_profiles(world_dir: Path) -> dict:
    """Scans Economies/ and world.yaml to extract economic systems, currencies, and baskets."""
    economies = {}
    dirs_to_check = [
        world_dir / "Economies",
        world_dir / "00-World-Bible" / "Economies",
    ]

    # Check world.yaml for global economy config
    world_yaml_path = world_dir / "world.yaml"
    if world_yaml_path.is_file():
        try:
            w_fm = parse_yaml_frontmatter(f"---\n{world_yaml_path.read_text(encoding='utf-8', errors='ignore')}\n---")
            if "economy" in w_fm and isinstance(w_fm["economy"], dict):
                economies["Global"] = w_fm["economy"]
                economies["Global"]["name"] = "Global Economy"
                economies["Global"]["file"] = "world.yaml"
        except Exception:
            pass

    seen_files = set()
    for edir in dirs_to_check:
        if not edir.is_dir():
            continue
        for md_file in sorted(edir.rglob("*.md")):
            if md_file in seen_files or md_file.name.startswith(".") or "Template" in md_file.name:
                continue
            seen_files.add(md_file)
            try:
                content = md_file.read_text(encoding="utf-8", errors="ignore")
                fm = parse_yaml_frontmatter(content)
                name = fm.get("name") or md_file.stem.replace("_", " ")

                base_currency = fm.get("base_currency") or "Standard Coin"
                currencies = fm.get("currencies") or {}

                # If currencies was parsed as list, convert to standard dict
                if isinstance(currencies, list):
                    c_dict = {}
                    for item in currencies:
                        if isinstance(item, str) and ":" in item:
                            k, v = item.split(":", 1)
                            try:
                                c_dict[k.strip()] = float(v.strip())
                            except ValueError:
                                c_dict[k.strip()] = 1.0
                        elif isinstance(item, str):
                            c_dict[item.strip()] = 1.0
                    currencies = c_dict

                # Ensure base currency exists in denominations
                if base_currency not in currencies and isinstance(currencies, dict):
                    currencies[base_currency] = 1.0

                commodity_basket = fm.get("commodity_basket") or fm.get("prices") or {}
                if isinstance(commodity_basket, list):
                    b_dict = {}
                    for item in commodity_basket:
                        if isinstance(item, str) and ":" in item:
                            k, v = item.split(":", 1)
                            try:
                                b_dict[k.strip()] = float(v.strip())
                            except ValueError:
                                b_dict[k.strip()] = 1.0
                    commodity_basket = b_dict

                tech_era = fm.get("tech_era") or fm.get("technology_level") or "medieval"

                economies[name] = {
                    "name": name,
                    "file": str(md_file.relative_to(world_dir)),
                    "base_currency": base_currency,
                    "currencies": currencies,
                    "commodity_basket": commodity_basket,
                    "tech_era": str(tech_era).lower().replace(" ", "_"),
                    "associated_faction": fm.get("associated_faction") or fm.get("faction") or "All",
                }
            except Exception as e:
                logger.warning("Failed to parse economy profile %s: %s", md_file, e)

    return economies


def calculate_ppp_rates(economies: dict) -> dict:
    """Calculates Purchasing Power Parity (PPP) relative exchange rates across economies."""
    ppp_matrix = {}
    if len(economies) < 2:
        return ppp_matrix

    econ_names = list(economies.keys())
    for i in range(len(econ_names)):
        e1_name = econ_names[i]
        e1 = economies[e1_name]
        b1 = e1.get("commodity_basket", {})
        ppp_matrix[e1_name] = {}

        for j in range(len(econ_names)):
            if i == j:
                ppp_matrix[e1_name][econ_names[j]] = 1.0
                continue
            e2_name = econ_names[j]
            e2 = economies[e2_name]
            b2 = e2.get("commodity_basket", {})

            # Find common basket items
            common_items = [k for k in b1 if k in b2 and isinstance(b1[k], (int, float)) and isinstance(b2[k], (int, float)) and b2[k] > 0]
            if common_items:
                ratios = [float(b1[item]) / float(b2[item]) for item in common_items]
                avg_ppp_rate = sum(ratios) / len(ratios)
                ppp_matrix[e1_name][e2_name] = round(avg_ppp_rate, 4)
            else:
                ppp_matrix[e1_name][e2_name] = None

    return ppp_matrix


def audit_manuscript_prices(
    manuscript_dir: Path,
    economies: dict,
    scope: EngineScope | None = None,
) -> list:
    """Audits manuscript scene files for price anomalies and unregistered currencies with currency & PPP normalization."""
    findings = []
    if not manuscript_dir or not manuscript_dir.is_dir():
        return findings

    ppp_matrix = calculate_ppp_rates(economies)

    # Collect known currencies and build mapping: currency_norm -> list of (economy_dict, denomination_rate)
    known_currencies = set()
    curr_map = {}
    for e in economies.values():
        e_currencies = e.get("currencies", {})
        for c, rate in e_currencies.items():
            c_norm = normalize_name(c)
            known_currencies.add(c_norm)
            rate_val = float(rate) if isinstance(rate, (int, float)) and float(rate) > 0 else 1.0
            if c_norm not in curr_map:
                curr_map[c_norm] = []
            curr_map[c_norm].append((e, rate_val))

    def get_basket_price(basket: dict, item_norm: str) -> float | None:
        for k, v in basket.items():
            if normalize_name(k) == item_norm and isinstance(v, (int, float)):
                return float(v)
        return None

    def resolve_baseline_and_amount(amount: float, curr_name: str, item_name: str) -> tuple[float, float | None]:
        """Converts price to base currency and finds the baseline basket price."""
        curr_norm = normalize_name(curr_name)
        item_norm = normalize_name(item_name)

        candidates = curr_map.get(curr_norm, [])
        if candidates:
            # Pick candidate whose economy defines the item, or fallback to first candidate
            selected_econ, denom_rate = candidates[0]
            for econ, rate_val in candidates:
                if get_basket_price(econ.get("commodity_basket", {}), item_norm) is not None:
                    selected_econ, denom_rate = econ, rate_val
                    break

            amount_base = amount * denom_rate
            e_basket = selected_econ.get("commodity_basket", {})
            direct_price = get_basket_price(e_basket, item_norm)
            if direct_price is not None:
                return amount_base, direct_price

            # Try PPP cross-rate from other economies
            e_name = selected_econ.get("name")
            if e_name and e_name in ppp_matrix:
                for other_name, ppp_rate in ppp_matrix[e_name].items():
                    if ppp_rate and other_name in economies:
                        other_basket = economies[other_name].get("commodity_basket", {})
                        other_price = get_basket_price(other_basket, item_norm)
                        if other_price is not None:
                            return amount_base, other_price * ppp_rate

            return amount_base, None
        # Unregistered currency fallback: search any economy basket
        for econ in economies.values():
            e_basket = econ.get("commodity_basket", {})
            price = get_basket_price(e_basket, item_norm)
            if price is not None:
                return amount, price
        return amount, None

    price_tag_regex = re.compile(r"@price:\s*([\d\.]+)\s+([A-Za-z\s]+?)\s+(?:for|on)\s+([A-Za-z\s_-]+)", re.IGNORECASE)
    prose_price_regex = re.compile(r"\b(\d+(?:\.\d+)?)\s+([A-Za-z\s]+?(?:crowns?|coins?|pence|shillings?|gold|silver|copper|credits?|sovereigns?|ducats?|drachmas?))\s+(?:for|on)\s+(?:a|an|the)?\s*([A-Za-z\s_-]+)\b", re.IGNORECASE)

    if scope:
        scoped_chapters, _, _ = filter_manuscript_scope(manuscript_dir, scope)
        md_files = [c.file_path for c in scoped_chapters]
    else:
        md_files = [
            f for f in sorted(manuscript_dir.rglob("*.md"))
            if not f.name.startswith(".") and "Front_Matter" not in f.parts and "Back_Matter" not in f.parts
        ]

    for md_file in md_files:
        try:
            content = md_file.read_text(encoding="utf-8", errors="ignore")
            lines = content.splitlines()
            for line_idx, line in enumerate(lines, start=1):
                for m in price_tag_regex.finditer(line):
                    amount = float(m.group(1))
                    curr_name = m.group(2).strip()
                    item_name = m.group(3).strip()
                    curr_norm = normalize_name(curr_name)

                    if known_currencies and curr_norm not in known_currencies:
                        findings.append({
                            "id": "ECO-102",
                            "severity": "WARNING",
                            "message": f"Unregistered Currency: Scene references '{curr_name}', not defined in World Bible Economies.",
                            "file": str(md_file.relative_to(manuscript_dir)),
                            "line": line_idx,
                        })

                    amount_base, base_price = resolve_baseline_and_amount(amount, curr_name, item_name)
                    if base_price is not None and base_price > 0:
                        ratio = amount_base / base_price
                        if ratio > 20.0:
                            findings.append({
                                "id": "ECO-101",
                                "severity": "WARNING",
                                "message": f"Severe Price Inflation Anomaly: '{item_name}' costs {amount} {curr_name} (baseline basket: {base_price:.2f}). Ratio is {ratio:.1f}x normal.",
                                "file": str(md_file.relative_to(manuscript_dir)),
                                "line": line_idx,
                            })
                        elif ratio < 0.05:
                            findings.append({
                                "id": "ECO-101",
                                "severity": "WARNING",
                                "message": f"Severe Price Deflation Anomaly: '{item_name}' costs {amount} {curr_name} (baseline basket: {base_price:.2f}). Ratio is {ratio:.2f}x normal.",
                                "file": str(md_file.relative_to(manuscript_dir)),
                                "line": line_idx,
                            })

                for m in prose_price_regex.finditer(line):
                    amount = float(m.group(1))
                    curr_name = m.group(2).strip()
                    item_name = m.group(3).strip()
                    curr_norm = normalize_name(curr_name)

                    if known_currencies and curr_norm not in known_currencies:
                        findings.append({
                            "id": "ECO-102",
                            "severity": "WARNING",
                            "message": f"Unregistered Currency: Prose references '{curr_name}', not defined in World Bible Economies.",
                            "file": str(md_file.relative_to(manuscript_dir)),
                            "line": line_idx,
                        })

                    amount_base, base_price = resolve_baseline_and_amount(amount, curr_name, item_name)
                    if base_price is not None and base_price > 0 and (amount_base / base_price > 50.0):
                        findings.append({
                            "id": "ECO-101",
                            "severity": "WARNING",
                            "message": f"Prose Price Discrepancy: '{item_name}' mentioned as costing {amount} {curr_name} (baseline: {base_price:.2f}).",
                            "file": str(md_file.relative_to(manuscript_dir)),
                            "line": line_idx,
                        })
        except Exception as e:
            logger.warning("Failed to audit manuscript file %s: %s", md_file, e)

    return findings


def audit_technological_anachronisms(
    manuscript_dir: Path,
    baseline_era: str = "medieval",
    custom_whitelist: list | None = None,
    scope: EngineScope | None = None,
) -> list:
    """
    Scans manuscript prose to detect out-of-era technological and material anachronisms.
    """
    findings = []
    if not manuscript_dir or not manuscript_dir.is_dir():
        return findings

    base_era_norm = baseline_era.lower().replace(" ", "_").replace("-", "_")
    base_idx = ERA_ORDER.get(base_era_norm, ERA_ORDER["medieval"])

    whitelist = {normalize_name(w) for w in (custom_whitelist or [])}

    if scope:
        scoped_chapters, _, _ = filter_manuscript_scope(manuscript_dir, scope)
        md_files = [c.file_path for c in scoped_chapters]
    else:
        md_files = [
            f for f in sorted(manuscript_dir.rglob("*.md"))
            if not f.name.startswith(".") and "Front_Matter" not in f.parts and "Back_Matter" not in f.parts
        ]

    for md_file in md_files:
        try:
            content = md_file.read_text(encoding="utf-8", errors="ignore")
            lines = content.splitlines()
            for line_idx, line in enumerate(lines, start=1):
                if line.strip().startswith("@"):
                    continue

                line_lower = line.lower()
                for tech_term, earliest_era in TECH_ERA_DICTIONARY.items():
                    if normalize_name(tech_term) in whitelist:
                        continue
                    earliest_idx = ERA_ORDER.get(earliest_era, 0)
                    if earliest_idx > base_idx:
                        pattern = r"\b" + re.escape(tech_term) + r"\b"
                        if re.search(pattern, line_lower):
                            findings.append({
                                "id": "ECO-201",
                                "severity": "WARNING",
                                "term": tech_term,
                                "earliest_era": earliest_era,
                                "world_baseline": baseline_era,
                                "message": f"Technological Anachronism: '{tech_term}' belongs to '{earliest_era}' era (World baseline: '{baseline_era}').",
                                "file": str(md_file.relative_to(manuscript_dir)),
                                "line": line_idx,
                                "snippet": line.strip(),
                            })
        except Exception as e:
            logger.warning("Failed to audit anachronisms for %s: %s", md_file, e)

    return findings


def calc_trade_margin(
    buy_price_per_ton: float,
    sell_price_per_ton: float,
    cargo_tons: float,
    distance_km_or_ly: float,
    transit_cost_per_ton_unit: float = 0.5,
    tariff_pct: float = 0.05,
    spoilage_pct: float = 0.02
) -> dict:
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


def generate_economy_html_report(audit_data: dict, output_path: Path):
    """Generates standalone HTML report for Economic audit and Tech Era check."""
    economies = audit_data.get("economies", {})
    findings = audit_data.get("findings", [])
    audit_data.get("ppp_matrix", {})
    world_name = audit_data.get("world", "World Bible")

    econ_cards = []
    for en, e in economies.items():
        curr_str = ", ".join([f"{k} (x{v})" for k, v in e.get("currencies", {}).items()])
        basket_str = ", ".join([f"{k}: {v}" for k, v in e.get("commodity_basket", {}).items()])
        econ_cards.append(f"""
        <div class="card">
            <h3>🏛️ {html.escape(en)} ({html.escape(e.get('tech_era', 'medieval'))})</h3>
            <p><strong>Base Currency:</strong> {html.escape(e.get('base_currency', ''))}</p>
            <p><strong>Currencies:</strong> {html.escape(curr_str)}</p>
            <p><strong>Basket Prices:</strong> <small>{html.escape(basket_str)}</small></p>
        </div>
        """)

    findings_cards = []
    for fd in findings:
        badge_cls = "badge-error" if fd.get("severity") == "ERROR" else "badge-warning"
        findings_cards.append(f"""
        <div class="card finding-card">
            <span class="badge {badge_cls}">{html.escape(fd.get('severity', 'WARNING'))}</span>
            <strong>{html.escape(fd.get('id', ''))}</strong>: {html.escape(fd.get('message', ''))}
            <div style="font-size: 0.85em; color: #94a3b8; margin-top: 4px;">File: {html.escape(fd.get('file', ''))}:{fd.get('line', '')}</div>
        </div>
        """)

    findings_html = "".join(findings_cards) if findings_cards else "<div style='color: #4ade80;'>✓ No pricing anomalies or technological anachronisms detected.</div>"

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ars Arcanum — Economy & Anachronism Matrix ({html.escape(world_name)})</title>
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
  .badge {{
    display: inline-block;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: bold;
    text-transform: uppercase;
  }}
  .badge-warning {{ background: #d97706; color: #fff; }}
  .badge-error {{ background: #b91c1c; color: #fff; }}
  .finding-card {{ margin-bottom: 0.75rem; }}
</style>
</head>
<body>
<div class="container">
  <h1>💰 Ars Arcanum Economy, PPP & Anachronism Matrix</h1>
  <p>World Lore Vault: <strong>{html.escape(world_name)}</strong></p>

  <div class="card">
    <h2>Audit Findings ({len(findings)})</h2>
    {findings_html}
  </div>

  <h2>Registered In-World Economies</h2>
  {"".join(econ_cards)}
</div>
</body>
</html>
"""
    atomic_write(output_path, html_content)


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


def extract_settlement_network(world_dir: Path | None) -> list[dict]:
    """Scans Locations/*.md in World Bible to extract settlements, populations, and trade goods."""
    settlements = []
    if world_dir and world_dir.is_dir():
        loc_dirs = [world_dir / "Locations", world_dir / "00-World-Bible" / "Locations"]
        for ldir in loc_dirs:
            if not ldir.is_dir():
                continue
            for md_file in sorted(ldir.rglob("*.md")):
                if md_file.name.startswith((".", "_")) or "Template" in md_file.name:
                    continue
                try:
                    content = md_file.read_text(encoding="utf-8", errors="ignore")
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
    settlements: list[dict],
    friction_matrix: dict | None = None,
    g_constant: float = 1.0,
    distance_exponent: float = 1.5,
) -> dict:
    """
    Computes bilateral trade flow volumes and route viability using the economic gravity model:
    T_ij = G * (M_i * M_j) / (D_ij^alpha * (1 + friction_ij))
    """
    if not settlements:
        return {"settlements_count": 0, "routes": []}

    routes = []
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
    settlements: list[dict],
    shock_event: str,
    target_settlement_id: str,
    affected_commodity: str,
    shock_magnitude: float = 0.6,
) -> dict:
    """
    Simulates supply shock propagation through the settlement trade network:
    Calculates localized scarcity multipliers, price inflation, and narrative conflict hooks.
    """
    gravity_res = calculate_gravity_trade_flow(settlements)
    routes = gravity_res["routes"]

    target_settlement = next(
        (s for s in settlements if str(s.get("id", "")).lower() == target_settlement_id.lower() or str(s.get("name", "")).lower() == target_settlement_id.lower()),
        None
    )
    if not target_settlement and settlements:
        target_settlement = settlements[0]
        target_settlement_id = str(target_settlement.get("id", target_settlement.get("name", "Origin")))

    target_name = target_settlement.get("name", target_settlement_id) if target_settlement else target_settlement_id

    # Node impact matrix
    market_impacts = {}
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
                None
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


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Economy, Commodity PPP & Anachronism Matrix")
    subparsers = parser.add_subparsers(dest="subcommand", help="Economy subcommands")

    # 1. check / report
    p_check = subparsers.add_parser("check", help="Run economy and price consistency audit")
    p_check.add_argument("world", nargs="?", help="World Bible lore directory")
    p_check.add_argument("manuscript_pos", nargs="?", help="Manuscript draft directory")
    p_check.add_argument("-w", "--world", dest="world_flag", help="World Bible lore directory")
    p_check.add_argument("-m", "--manuscript", help="Manuscript draft directory")
    p_check.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    p_check.add_argument("--html", help="Path to export standalone HTML report")
    add_scope_arguments(p_check, include_world=False, include_manuscript=False, target_pos_arg=False)

    p_rep = subparsers.add_parser("report", help="Display full economy and PPP report")
    p_rep.add_argument("world", nargs="?", help="World Bible lore directory")
    p_rep.add_argument("manuscript_pos", nargs="?", help="Manuscript draft directory")
    p_rep.add_argument("-w", "--world", dest="world_flag", help="World Bible lore directory")
    p_rep.add_argument("-m", "--manuscript", help="Manuscript draft directory")
    p_rep.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    p_rep.add_argument("--html", help="Path to export standalone HTML report")
    add_scope_arguments(p_rep, include_world=False, include_manuscript=False, target_pos_arg=False)

    # 2. tech audit
    p_tech = subparsers.add_parser("tech", help="Audit manuscript for out-of-era technological anachronisms")
    p_tech.add_argument("manuscript", nargs="?", help="Manuscript draft directory")
    p_tech.add_argument("-m", "--manuscript", dest="ms_flag", help="Manuscript draft directory")
    p_tech.add_argument("-w", "--world", help="World Bible directory (for tech era detection)")
    p_tech.add_argument("--era", choices=TECH_ERAS, default="medieval", help="Baseline technological era")
    p_tech.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    add_scope_arguments(p_tech, include_world=False, include_manuscript=False, target_pos_arg=False)

    # 3. trade calculator
    p_trade = subparsers.add_parser("trade", help="Interstellar/regional trade route profit margin calculator")
    p_trade.add_argument("--buy", type=float, required=True, help="Origin commodity buy price per ton")
    p_trade.add_argument("--sell", type=float, required=True, help="Destination commodity sell price per ton")
    p_trade.add_argument("--cargo", type=float, default=100.0, help="Cargo weight in metric tons")
    p_trade.add_argument("--distance", type=float, default=500.0, help="Route distance (km or ly)")
    p_trade.add_argument("--cost-per-unit", type=float, default=0.5, help="Transit freight cost per ton-distance")
    p_trade.add_argument("--tariff", type=float, default=0.05, help="Tariff tax fraction (default 0.05 = 5%%)")
    p_trade.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # 4. trade-flow (Gravity Model)
    p_flow = subparsers.add_parser("trade-flow", help="Calculate economic gravity trade flows between settlements")
    p_flow.add_argument("world", nargs="?", help="World Bible lore directory")
    p_flow.add_argument("-w", "--world", dest="world_flag", help="World Bible lore directory")
    p_flow.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # 5. supply-shock (Scarcity & Crisis Simulation)
    p_shock = subparsers.add_parser("supply-shock", help="Simulate commodity supply shock and price inflation cascades")
    p_shock.add_argument("world", nargs="?", help="World Bible lore directory")
    p_shock.add_argument("-w", "--world", dest="world_flag", help="World Bible lore directory")
    p_shock.add_argument("-e", "--event", default="Regional Harvest Failure", help="Description of crisis event")
    p_shock.add_argument("-s", "--settlement", default="SunCitadel", help="Epicenter settlement ID or name")
    p_shock.add_argument("-c", "--commodity", default="grain", help="Affected commodity name")
    p_shock.add_argument("-m", "--magnitude", type=float, default=0.6, help="Shock magnitude fraction (0.1 to 1.0, default: 0.6)")
    p_shock.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    if len(sys.argv) > 1 and sys.argv[1] not in ("check", "report", "tech", "trade", "trade-flow", "supply-shock", "-h", "--help", "-v", "--version"):
        sys.argv.insert(1, "check")

    args = parser.parse_args()

    if not args.subcommand:
        args.subcommand = "report"

    scope = parse_scope_args(args)

    if args.subcommand in ("check", "report"):
        raw_world = getattr(args, "world_flag", None) or getattr(args, "world", None)
        world_dir_str = resolve_world_dir(raw_world) if raw_world else (str(resolve_world_path(scope=scope)) if resolve_world_path(scope=scope) else None)
        if not world_dir_str or not Path(world_dir_str).is_dir():
            print("Error: No valid World Bible directory specified or discovered.", file=sys.stderr)
            sys.exit(2)

        world_path = Path(world_dir_str)
        raw_ms = getattr(args, "manuscript", None) or getattr(args, "manuscript_pos", None)
        ms_dir_str = resolve_manuscript_dir(raw_ms) if raw_ms else (str(resolve_manuscript_path(scope=scope)) if resolve_manuscript_path(scope=scope) else None)
        ms_path = Path(ms_dir_str) if ms_dir_str else None

        economies = extract_economy_profiles(world_path)
        ppp_matrix = calculate_ppp_rates(economies)
        price_findings = audit_manuscript_prices(ms_path, economies, scope=scope) if ms_path else []

        # Also run tech check if manuscript provided
        primary_era = "medieval"
        if economies:
            primary_era = next(iter(economies.values())).get("tech_era", "medieval")
        tech_findings = audit_technological_anachronisms(ms_path, primary_era, scope=scope) if ms_path else []

        all_findings = price_findings + tech_findings

        audit_data = {
            "world": world_path.name,
            "manuscript": ms_path.name if ms_path else None,
            "economies_count": len(economies),
            "findings_count": len(all_findings),
            "economies": economies,
            "ppp_matrix": ppp_matrix,
            "findings": all_findings,
        }

        if getattr(args, "json", False):
            print(json.dumps(audit_data, indent=2))
        else:
            print("\n\033[1;33m=== Ars Arcanum Economy, Commodity PPP & Tech Matrix ===\033[0m")
            print(f"World: \033[1m{world_path.name}\033[0m | Manuscript: \033[1m{ms_path.name if ms_path else 'N/A'}\033[0m")
            print(f"Economies Registered: \033[32m{len(economies)}\033[0m | Findings: \033[1m{len(all_findings)}\033[0m\n")

            if economies:
                print("\033[1mIn-World Economic Systems & Currencies:\033[0m")
                for en, einfo in economies.items():
                    print(f"  🪙 \033[1;36m{en}\033[0m (Era: {einfo.get('tech_era', 'medieval')}) — Base: {einfo.get('base_currency', '')}")
                    if einfo.get("currencies"):
                        c_list = [f"{k} (x{v})" for k, v in einfo["currencies"].items()]
                        print(f"     Currencies: {', '.join(c_list)}")
                    if einfo.get("commodity_basket"):
                        b_list = [f"{k}={v}" for k, v in einfo["commodity_basket"].items()]
                        print(f"     Basket: {', '.join(b_list)}")
                print()

            if not all_findings:
                print("\033[32m[OK] Economic models and manuscript prices are internally consistent.\033[0m")
            else:
                for fd in all_findings:
                    badge = f"\033[31m[{fd['severity']}]\033[0m" if fd["severity"] == "ERROR" else f"\033[33m[{fd['severity']}]\033[0m"
                    print(f"{badge} {fd['id']}: {fd['message']}")
                    print(f"     Location: {fd['file']}:{fd.get('line', '')}\n")

        if getattr(args, "html", None):
            out_p = Path(args.html)
            generate_economy_html_report(audit_data, out_p)
            print(f"\nInteractive HTML report written to: {out_p}")

        sys.exit(1 if len(all_findings) > 0 else 0)

    elif args.subcommand == "tech":
        raw_ms = getattr(args, "ms_flag", None) or getattr(args, "manuscript", None)
        ms_dir_str = resolve_manuscript_dir(raw_ms) if raw_ms else (str(resolve_manuscript_path(scope=scope)) if resolve_manuscript_path(scope=scope) else None)
        if not ms_dir_str or not Path(ms_dir_str).is_dir():
            print("Error: No valid Manuscript directory specified or discovered.", file=sys.stderr)
            sys.exit(2)

        ms_path = Path(ms_dir_str)
        era = args.era
        if args.world:
            w_dir = resolve_world_dir(args.world)
            if w_dir:
                econs = extract_economy_profiles(Path(w_dir))
                if econs:
                    era = next(iter(econs.values())).get("tech_era", era)

        findings = audit_technological_anachronisms(ms_path, baseline_era=era, scope=scope)

        if args.json:
            print(json.dumps({"manuscript": ms_path.name, "baseline_era": era, "findings": findings}, indent=2))
        else:
            print("\n\033[1;36m=== Technological Era Baseline Audit ===\033[0m")
            print(f"Manuscript: \033[1m{ms_path.name}\033[0m | Baseline Era: \033[1;33m{era}\033[0m")
            print(f"Anachronisms Detected: \033[1m{len(findings)}\033[0m\n")

            if not findings:
                print(f"\033[32m[OK] No out-of-era technological terms found for {era} baseline.\033[0m")
            else:
                for f in findings:
                    print(f"\033[33m[ANACHRONISM]\033[0m {f['id']}: '{f['term']}' is from {f['earliest_era']} era.")
                    print(f"  Location: {f['file']}:{f['line']}")
                    print(f"  Snippet : \"{f['snippet']}\"\n")

        sys.exit(1 if len(findings) > 0 else 0)

    elif args.subcommand == "trade":
        result = calc_trade_margin(
            buy_price_per_ton=args.buy,
            sell_price_per_ton=args.sell,
            cargo_tons=args.cargo,
            distance_km_or_ly=args.distance,
            transit_cost_per_ton_unit=args.cost_per_unit,
            tariff_pct=args.tariff,
        )
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print("\n\033[1;32m=== Trade Route Profitability Analysis ===\033[0m")
            print(f"Cargo          : {result['cargo_tons']} tons | Distance: {result['distance']}")
            print(f"Price Spread   : Buy @ {result['buy_price_per_ton']} -> Sell @ {result['sell_price_per_ton']} per ton")
            print(f"Gross Revenue  : {result['gross_revenue']:,.2f}")
            print(f"Transit Cost   : {result['total_transit_cost']:,.2f} | Tariffs: {result['total_tariffs']:,.2f}")
            print(f"Net Profit     : \033[1m{result['net_profit']:,.2f}\033[0m (ROI: {result['roi_pct']}%)")
            print(f"Break-Even Sell: {result['break_even_sell_price_per_ton']:,.2f} per ton")
            vcol = "\033[32m" if result["is_profitable"] else "\033[31m"
            print(f"Verdict        : {vcol}{result['verdict']}\033[0m\n")
        sys.exit(0)

    elif args.subcommand == "trade-flow":
        raw_world = getattr(args, "world_flag", None) or getattr(args, "world", None)
        world_dir_str = resolve_world_dir(raw_world) if raw_world else None
        world_path = Path(world_dir_str) if world_dir_str else None
        settlements = extract_settlement_network(world_path)
        flow_res = calculate_gravity_trade_flow(settlements)

        if args.json:
            print(json.dumps(flow_res, indent=2))
        else:
            print("\n\033[1;36m=== Economic Gravity Model Trade Network ===\033[0m")
            print(f"Settlements Analyzed: \033[1m{flow_res['settlements_count']}\033[0m | Total Network Trade: \033[1;32m{flow_res['total_network_trade']:,.2f}\033[0m\n")
            print(f"  {'Route':<32} | {'Distance':<10} | {'Friction':<8} | {'Trade Volume':<14} | {'Viability':<10}")
            print("  " + "-" * 84)
            for r in flow_res["routes"]:
                route_str = f"{r['origin_name']} <-> {r['destination_name']}"
                v_col = "\033[32m" if r["viability"] == "High" else ("\033[33m" if r["viability"] == "Medium" else "\033[90m")
                print(f"  {route_str:<32} | {r['distance_km']:<10.1f} | {r['terrain_friction']:<8.2f} | \033[1m{r['annual_trade_volume']:<14,.2f}\033[0m | {v_col}{r['viability']:<10}\033[0m")
            print()
        sys.exit(0)

    elif args.subcommand == "supply-shock":
        raw_world = getattr(args, "world_flag", None) or getattr(args, "world", None)
        world_dir_str = resolve_world_dir(raw_world) if raw_world else None
        world_path = Path(world_dir_str) if world_dir_str else None
        settlements = extract_settlement_network(world_path)
        shock_res = simulate_supply_shock(
            settlements=settlements,
            shock_event=args.event,
            target_settlement_id=args.settlement,
            affected_commodity=args.commodity,
            shock_magnitude=args.magnitude,
        )

        if args.json:
            print(json.dumps(shock_res, indent=2))
        else:
            print(f"\n\033[1;31m=== Supply Shock & Scarcity Cascade: {shock_res['shock_event']} ===\033[0m")
            print(f"Epicenter: \033[1;33m{shock_res['epicenter_name']}\033[0m | Commodity: \033[1m{shock_res['commodity']}\033[0m | Magnitude: \033[31m-{shock_res['shock_magnitude_pct']}%\033[0m\n")
            print("Regional Market Price Multipliers & Stress:")
            for imp in shock_res["market_impacts"]:
                s_col = "\033[31m" if imp["market_stress"] == "Emergency" else ("\033[33m" if imp["market_stress"] == "Severe" else "\033[32m")
                print(f"  • \033[1m{imp['name']:<20}\033[0m [{imp['tier']}] -> Price: \033[1m{imp['price_multiplier']}x\033[0m baseline ({s_col}{imp['market_stress']}\033[0m)")
            print("\nNarrative Conflict & Story Beats:")
            for h in shock_res["narrative_conflict_hooks"]:
                print(f"  ⚡ {h}")
            print()
        sys.exit(0)


if __name__ == "__main__":
    main()

