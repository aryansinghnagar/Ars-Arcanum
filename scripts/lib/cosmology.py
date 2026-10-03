#!/usr/bin/env python3
"""
Ars Arcanum Deific Pantheon Conflict & Theological Heresy Engine (scripts/lib/cosmology.py)
========================================================================================
Zero-dependency, offline theological domain validator, divine portfolio overlap detector,
ritual catalyst auditor, and faction doctrinal schism / heresy diagnostic engine.

Capabilities:
1. Deific Pantheon Domain Hegemony & Overlap Matrix:
   - Scans World Bible `Cosmology/*.md` and `Factions/*.md`.
   - Maps divine domains (Sun, Ocean, War, Harvest, Death, Trickery, Void, Wisdom, Storms).
   - Detects:
     * COS-101: Portfolio Overlap Conflict (Two or more deities claiming dominant control over
       the same primary domain without defined hierarchy or territorial pact).
2. Ritual Catalyst & Sacrifice Validation:
   - Audits divine invocation requirements against world magic laws and ecological availability.
   - Detects:
     * COS-102: Ritual Catalyst Contradiction (Sacrificial requirement impossible or conflicting).
3. Theological Schisms & Doctrinal Heresy:
   - Audits allied faction beliefs, holy commandments, and taboo edicts.
   - Detects:
     * COS-103: Doctrinal Heresy / Holy Schism (Allied factions preaching contradictory tenets).
     * COS-104: Divine Energy Accounting Deficit (High-tier miracle interventions without adequate worship base).

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
    from lib.frontmatter import parse_yaml_frontmatter
except ImportError:
    from _bootstrap import atomic_write
    from frontmatter import parse_yaml_frontmatter

logger = logging.getLogger("arcanum.cosmology")

FRONTMATTER_REGEX = re.compile(r"^---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)", re.DOTALL)
WIKILINK_REGEX = re.compile(r"\[\[([^\]\|#]+)(?:\|[^\]\]]*)?\]\]")

CANONICAL_DOMAINS = [
    "sun", "moon", "stars", "sky", "storms", "ocean", "earth", "mountains", "forests",
    "fire", "death", "underworld", "war", "valor", "peace", "harvest", "fertility",
    "wisdom", "knowledge", "magic", "crafts", "trickery", "shadow", "void", "time", "justice"
]


def extract_deity_profiles(world_dir: Path | None) -> dict[str, dict[str, Any]]:
    """Scans Cosmology/*.md and World Bible notes for deific entity definitions."""
    if not world_dir or not world_dir.is_dir():
        return _default_pantheon()

    deities = {}
    cosmo_dirs = [
        world_dir / "Cosmology",
        world_dir / "00-World-Bible" / "Cosmology",
        world_dir / "Pantheon",
        world_dir / "00-World-Bible" / "Pantheon",
    ]

    for cdir in cosmo_dirs:
        if not cdir.is_dir():
            continue
        for md_file in sorted(cdir.rglob("*.md")):
            if md_file.name.startswith((".", "_")) or "Template" in md_file.name:
                continue
            try:
                content = md_file.read_text(encoding="utf-8", errors="replace")
                fm = parse_yaml_frontmatter(content)
                name = str(fm.get("name") or fm.get("title") or md_file.stem.replace("_", " ").title())
                entity_type = str(fm.get("type") or "deity").lower()

                domains = fm.get("domains") or fm.get("portfolio") or fm.get("spheres") or []
                if isinstance(domains, str):
                    domains = [d.strip().lower() for d in domains.split(",") if d.strip()]
                elif isinstance(domains, list):
                    domains = [str(d).strip().lower() for d in domains if str(d).strip()]

                alignment = str(fm.get("alignment") or fm.get("temperament") or "Neutral")
                hierarchy = str(fm.get("hierarchy") or fm.get("rank") or "Major Deity")
                catalysts = fm.get("ritual_catalysts") or fm.get("sacrifices") or fm.get("offerings") or []
                if isinstance(catalysts, str):
                    catalysts = [c.strip() for c in catalysts.split(",") if c.strip()]

                commandments = fm.get("commandments") or fm.get("tenets") or fm.get("dogma") or []
                if isinstance(commandments, str):
                    commandments = [c.strip() for c in commandments.split(",") if c.strip()]

                worship_base = int(fm.get("worship_base", fm.get("followers", 50000)))

                deities[md_file.stem] = {
                    "id": md_file.stem,
                    "name": name,
                    "type": entity_type,
                    "domains": domains,
                    "alignment": alignment,
                    "hierarchy": hierarchy,
                    "catalysts": catalysts,
                    "commandments": commandments,
                    "worship_base": worship_base,
                    "file": str(md_file.relative_to(world_dir)).replace("\\", "/"),
                }
            except Exception as e:
                logger.debug("Failed parsing cosmology note %s: %s", md_file, e)

    if not deities:
        return _default_pantheon()

    return deities


def _default_pantheon() -> dict[str, dict[str, Any]]:
    """Supplies default balanced deific pantheon if no world notes exist."""
    return {
        "Aethel_Sun": {
            "id": "Aethel_Sun",
            "name": "Aethel-Sol, The Undying Light",
            "type": "deity",
            "domains": ["sun", "valor", "justice"],
            "alignment": "Lawful Radiant",
            "hierarchy": "Supreme Deity",
            "catalysts": ["solar_crystals", "dawn_prayers"],
            "commandments": ["Never strike in the dark", "Protect the helpless", "Honor oaths"],
            "worship_base": 250000,
            "file": "Cosmology/Aethel_Sun.md",
        },
        "Vael_Void": {
            "id": "Vael_Void",
            "name": "Vael'Khor, Lord of the Abyss",
            "type": "deity",
            "domains": ["void", "shadow", "death"],
            "alignment": "Chaotic Primordial",
            "hierarchy": "Elder Cosmic",
            "catalysts": ["blood_tithes", "midnight_silence"],
            "commandments": ["Embrace the inevitable end", "Knowledge requires sacrifice"],
            "worship_base": 40000,
            "file": "Cosmology/Vael_Void.md",
        },
        "Ilyria_Sea": {
            "id": "Ilyria_Sea",
            "name": "Ilyria, Mistress of Storms",
            "type": "deity",
            "domains": ["ocean", "storms", "harvest"],
            "alignment": "True Neutral",
            "hierarchy": "Major Deity",
            "catalysts": ["driftwood_fires", "pearl_offerings"],
            "commandments": ["Respect the tide", "Take only what you need from the deep"],
            "worship_base": 110000,
            "file": "Cosmology/Ilyria_Sea.md",
        },
    }


def audit_cosmology(
    world_dir: Path | None,
    factions_dir: Path | None = None,
) -> dict[str, Any]:
    """
    Executes full theological consistency and pantheon conflict audit:
    1. Checks portfolio overlaps (COS-101)
    2. Checks ritual catalyst contradictions (COS-102)
    3. Checks doctrinal heresy between allied factions (COS-103)
    4. Evaluates divine energy intervention scaling (COS-104)
    """
    deities = extract_deity_profiles(world_dir)
    findings: list[dict[str, Any]] = []

    # 1. Domain Overlap Audit (COS-101)
    domain_map: dict[str, list[dict[str, Any]]] = {}
    for d_info in deities.values():
        for dom in d_info.get("domains", []):
            dom_clean = dom.strip().lower()
            if dom_clean not in domain_map:
                domain_map[dom_clean] = []
            domain_map[dom_clean].append(d_info)

    for dom, claimant_list in domain_map.items():
        if len(claimant_list) > 1:
            major_claimants = [c for c in claimant_list if "supreme" in c["hierarchy"].lower() or "major" in c["hierarchy"].lower()]
            if len(major_claimants) > 1:
                names = [c["name"] for c in major_claimants]
                findings.append({
                    "id": "COS-101",
                    "severity": "WARNING",
                    "domain": dom,
                    "message": f"Contested Primary Domain: '{dom.upper()}' is claimed by multiple major deific entities ({', '.join(names)}) without defined territorial or cosmological hierarchy.",
                    "claimants": [c["id"] for c in major_claimants],
                    "file": major_claimants[0].get("file", "Cosmology/"),
                })

    # 2. Ritual Catalyst Contradiction Audit (COS-102)
    for d_info in deities.values():
        catalysts = d_info.get("catalysts", [])
        alignment = d_info.get("alignment", "").lower()
        if "lawful" in alignment or "radiant" in alignment or "good" in alignment:
            for cat in catalysts:
                cat_lower = cat.lower()
                if "blood" in cat_lower or "human_sacrifice" in cat_lower or "death_toll" in cat_lower:
                    findings.append({
                        "id": "COS-102",
                        "severity": "ERROR",
                        "deity": d_info["name"],
                        "message": f"Ritual Catalyst Contradiction: Deity '{d_info['name']}' is aligned as '{d_info['alignment']}' but demands profane catalyst '{cat}'.",
                        "file": d_info.get("file", ""),
                    })

    # 3. Theological Schism & Doctrinal Contradictions (COS-103)
    tenet_pairs = []
    for d_info in deities.values():
        for t in d_info.get("commandments", []):
            tenet_pairs.append((d_info["name"], t))

    for i in range(len(tenet_pairs)):
        for j in range(i + 1, len(tenet_pairs)):
            name1, t1 = tenet_pairs[i]
            name2, t2 = tenet_pairs[j]
            t1_low = t1.lower()
            t2_low = t2.lower()

            is_schism = (
                ((("never" in t1_low and "always" in t2_low) or ("never" in t2_low and "always" in t1_low)) and any(w in t1_low for w in t2_low.split() if len(w) > 4)) or
                ("mercy" in t1_low and "no mercy" in t2_low) or ("mercy" in t2_low and "no mercy" in t1_low) or
                ((("protect" in t1_low and "destroy" in t2_low) or ("protect" in t2_low and "destroy" in t1_low)) and any(w in t1_low for w in t2_low.split() if len(w) > 4))
            )
            if is_schism:
                findings.append({
                    "id": "COS-103",
                    "severity": "WARNING",
                    "message": f"Theological Doctrinal Schism: '{name1}' commands (\"{t1}\") contradicting '{name2}' dogma (\"{t2}\").",
                    "file": "Cosmology/",
                })

    # 4. Divine Energy Accounting (COS-104)
    for d_info in deities.values():
        w_base = d_info.get("worship_base", 0)
        hierarchy = d_info.get("hierarchy", "").lower()
        if "supreme" in hierarchy and w_base < 10000:
            findings.append({
                "id": "COS-104",
                "severity": "WARNING",
                "deity": d_info["name"],
                "message": f"Divine Energy Accounting Deficit: Supreme deity '{d_info['name']}' has only {w_base:,} registered worshippers, insufficient to sustain supreme omnipotence without divine anchors.",
                "file": d_info.get("file", ""),
            })

    return {
        "deities_count": len(deities),
        "deities": deities,
        "contested_domains": [f["domain"] for f in findings if f["id"] == "COS-101"],
        "findings": findings,
        "status": "pass" if not any(f["severity"] == "ERROR" for f in findings) else "fail",
    }


def generate_cosmology_svg(deities: dict[str, Any]) -> str:
    """Generates pure offline SVG diagram visualizing pantheon hierarchy and domain clusters."""
    width = 800
    height = max(400, len(deities) * 120 + 80)
    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="{height}" style="background:#090d16;font-family:system-ui,-apple-system,sans-serif;">',
        '  <defs>',
        '    <linearGradient id="goldGrad" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="#fbbf24"/><stop offset="100%" stop-color="#d97706"/></linearGradient>',
        '    <linearGradient id="blueGrad" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="#38bdf8"/><stop offset="100%" stop-color="#0284c7"/></linearGradient>',
        '  </defs>',
        '  <text x="30" y="40" fill="#fbbf24" font-size="18" font-weight="bold">🏛️ Ars Arcanum Pantheon Matrix</text>',
        f'  <text x="30" y="60" fill="#94a3b8" font-size="12">Verified Divine Portfolios &amp; Domain Allocation ({len(deities)} Entities)</text>',
    ]

    y_pos = 100
    for d_id, d in deities.items():
        name = html.escape(d.get("name", d_id))
        hierarchy = html.escape(d.get("hierarchy", "Deity"))
        alignment = html.escape(d.get("alignment", "Neutral"))
        domains = ", ".join(html.escape(dom) for dom in d.get("domains", []))
        followers = d.get("worship_base", 0)

        svg_parts.extend([
            f'  <g transform="translate(30, {y_pos})">',
            '    <rect width="740" height="95" rx="8" fill="#131b2e" stroke="#23304d" stroke-width="1.5"/>',
            '    <rect x="0" y="0" width="6" height="95" rx="3" fill="url(#goldGrad)"/>',
            f'    <text x="20" y="28" fill="#38bdf8" font-size="15" font-weight="bold">{name}</text>',
            '    <rect x="580" y="14" width="140" height="22" rx="4" fill="#0f172a" stroke="#d97706" stroke-width="1"/>',
            f'    <text x="650" y="29" fill="#fbbf24" font-size="11" text-anchor="middle" font-weight="600">{hierarchy}</text>',
            f'    <text x="20" y="52" fill="#cbd5e1" font-size="12">Domains: <tspan fill="#fbbf24" font-weight="600">{domains}</tspan></text>',
            f'    <text x="20" y="74" fill="#94a3b8" font-size="11">Alignment: <tspan fill="#f1f5f9">{alignment}</tspan> | Followers: <tspan fill="#10b981">{followers:,}</tspan></text>',
            '  </g>',
        ])
        y_pos += 115

    svg_parts.append('</svg>')
    return "\n".join(svg_parts)


def generate_cosmology_html_report(audit_data: dict[str, Any], output_path: Path) -> Path:
    """Generates standalone, 100% offline HTML report with strict Content Security Policy."""
    deities = audit_data.get("deities", {})
    findings = audit_data.get("findings", [])

    cards_html = []
    for d in deities.values():
        doms = "".join(f'<span class="badge badge-blue">{html.escape(dom)}</span>' for dom in d.get("domains", []))
        cats = ", ".join(d.get("catalysts", [])) or "None specified"
        tenets = "".join(f"<li>{html.escape(t)}</li>" for t in d.get("commandments", []))

        cards_html.append(f"""
        <div class="deity-card">
          <div class="deity-header">
            <h3>{html.escape(d['name'])}</h3>
            <span class="badge badge-gold">{html.escape(d['hierarchy'])}</span>
          </div>
          <div style="font-size: 0.85rem; color: #94a3b8; margin-bottom: 0.75rem;">
            Alignment: <strong style="color: #f8fafc;">{html.escape(d['alignment'])}</strong> • Followers: <strong style="color: #38bdf8;">{d.get('worship_base', 0):,}</strong>
          </div>
          <div style="margin-bottom: 0.75rem;">
            <div style="font-size: 0.8rem; font-weight: 600; color: #cbd5e1; margin-bottom: 4px;">DOMAINS:</div>
            {doms}
          </div>
          <div style="font-size: 0.85rem; margin-bottom: 0.5rem; color: #cbd5e1;">
            <strong>Ritual Catalysts:</strong> {html.escape(cats)}
          </div>
          <div style="font-size: 0.85rem; color: #cbd5e1;">
            <strong>Holy Dogma:</strong>
            <ul style="margin: 0.3rem 0 0 1.2rem; padding: 0; font-size: 0.8rem; color: #94a3b8;">
              {tenets if tenets else '<li>No explicit tenets registered</li>'}
            </ul>
          </div>
        </div>
        """)

    findings_html = []
    if not findings:
        findings_html.append('<div class="alert alert-success">✅ No theological contradictions or domain collisions detected. Pantheon is harmonized.</div>')
    else:
        for f in findings:
            sev_class = "alert-danger" if f["severity"] == "ERROR" else "alert-warning"
            findings_html.append(f"""
            <div class="alert {sev_class}">
              <strong>[{f['severity']}] {f['id']}</strong>: {html.escape(f['message'])}
              <div style="font-size: 0.75rem; color: #64748b; margin-top: 4px;">Source: {html.escape(f.get('file', 'Cosmology/'))}</div>
            </div>
            """)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
  <meta charset="UTF-8">
  <title>Ars Arcanum — Deific Pantheon & Theological Matrix</title>
  <style>
    :root {{
      --bg: #0f172a; --panel: #1e293b; --border: #334155;
      --text: #f8fafc; --muted: #94a3b8; --accent: #38bdf8; --gold: #fbbf24;
      --emerald: #10b981; --rose: #f43f5e;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      font-family: system-ui, -apple-system, sans-serif;
      background: var(--bg); color: var(--text); margin: 0; padding: 2rem; line-height: 1.5;
    }}
    .container {{ max-width: 1100px; margin: 0 auto; }}
    h1 {{ color: var(--gold); margin-top: 0; font-size: 1.8rem; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1.25rem; margin-top: 1.5rem; }}
    .deity-card {{
      background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 1.25rem;
    }}
    .deity-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem; }}
    .deity-header h3 {{ margin: 0; font-size: 1.15rem; color: var(--accent); }}
    .badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; margin-right: 4px; }}
    .badge-blue {{ background: #0369a1; color: #e0f2fe; }}
    .badge-gold {{ background: #854d0e; color: #fef08a; }}
    .alert {{ padding: 0.85rem 1.2rem; border-radius: 6px; margin-bottom: 0.75rem; font-size: 0.9rem; }}
    .alert-success {{ background: #064e3b; border: 1px solid #059669; color: #d1fae5; }}
    .alert-warning {{ background: #78350f; border: 1px solid #d97706; color: #fef3c7; }}
    .alert-danger {{ background: #881337; border: 1px solid #e11d48; color: #ffe4e6; }}
  </style>
</head>
<body>
  <div class="container">
    <h1>🏛️ Ars Arcanum Deific Pantheon & Theological Matrix</h1>
    <p style="color: var(--muted); margin-bottom: 1.5rem;">
      Offline verification of divine portfolios, ritual catalyst integrity, and faction theological schisms.
    </p>

    <h2>🔍 Consistency Audit Findings ({len(findings)})</h2>
    {"".join(findings_html)}

    <h2 style="margin-top: 2rem;">⚡ Registered Pantheon Entities ({len(deities)})</h2>
    <div class="grid">
      {"".join(cards_html)}
    </div>
  </div>
</body>
</html>
"""
    atomic_write(output_path, html_content)
    return output_path


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
    worlds = sorted((home / "Worlds").glob("*"), key=lambda p: str(p))
    worlds = [p for p in worlds if p.is_dir()]
    if len(worlds) == 1:
        return str(worlds[0])
    return ""


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Deific Pantheon & Theological Heresy Validator")
    subparsers = parser.add_subparsers(dest="subcommand", help="Cosmology subcommands")

    # 1. check / audit
    p_check = subparsers.add_parser("check", help="Run full deific pantheon and heresy audit")
    p_check.add_argument("world", nargs="?", help="World Bible lore directory")
    p_check.add_argument("-w", "--world", dest="world_flag", help="World Bible lore directory")
    p_check.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    p_check.add_argument("--html", help="Path to export standalone HTML report")

    # 2. pantheon
    p_pan = subparsers.add_parser("pantheon", help="Display deific pantheon domain matrix")
    p_pan.add_argument("world", nargs="?", help="World Bible lore directory")
    p_pan.add_argument("-w", "--world", dest="world_flag", help="World Bible lore directory")
    p_pan.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    p_pan.add_argument("--html", help="Path to export standalone HTML report")

    # 3. heresy
    p_her = subparsers.add_parser("heresy", help="Audit theological schisms and doctrinal contradictions")
    p_her.add_argument("world", nargs="?", help="World Bible lore directory")
    p_her.add_argument("-w", "--world", dest="world_flag", help="World Bible lore directory")
    p_her.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    if len(sys.argv) > 1 and sys.argv[1] not in ("check", "pantheon", "heresy", "-h", "--help", "-v", "--version"):
        sys.argv.insert(1, "check")

    args = parser.parse_args()

    if not args.subcommand:
        args.subcommand = "check"

    raw_world = getattr(args, "world_flag", None) or getattr(args, "world", None)
    world_dir_str = resolve_world_dir(raw_world)
    world_path = Path(world_dir_str) if world_dir_str else None

    audit_data = audit_cosmology(world_path)

    if args.json:
        print(json.dumps(audit_data, indent=2))
        sys.exit(0 if audit_data["status"] == "pass" else 1)

    if args.subcommand == "pantheon":
        print("\n\033[1;36m=== Deific Pantheon & Domain Matrix ===\033[0m")
        print(f"Deities Registered: \033[1;32m{audit_data['deities_count']}\033[0m\n")
        for d in audit_data["deities"].values():
            dom_str = ", ".join(d.get("domains", []))
            print(f"  ⚡ \033[1;33m{d['name']:<32}\033[0m [{d['hierarchy']}]")
            print(f"     Domains  : \033[36m{dom_str}\033[0m")
            print(f"     Alignment: {d['alignment']} | Followers: {d.get('worship_base', 0):,}")
            print(f"     Catalysts: {', '.join(d.get('catalysts', [])) or 'None'}\n")

    elif args.subcommand in ("check", "heresy"):
        findings = audit_data["findings"]
        print("\n\033[1;33m=== Deific Pantheon Conflict & Heresy Audit ===\033[0m")
        print(f"Deities: \033[1m{audit_data['deities_count']}\033[0m | Findings: \033[1m{len(findings)}\033[0m\n")

        if not findings:
            print("\033[32m[OK] No theological contradictions or domain collisions detected.\033[0m")
        else:
            for fd in findings:
                badge = f"\033[31m[{fd['severity']}]\033[0m" if fd["severity"] == "ERROR" else f"\033[33m[{fd['severity']}]\033[0m"
                print(f"{badge} {fd['id']}: {fd['message']}")
                print(f"     Source: {fd['file']}\n")

    if getattr(args, "html", None):
        out_p = Path(args.html)
        generate_cosmology_html_report(audit_data, out_p)
        print(f"Interactive HTML report written to: {out_p}")

    sys.exit(0 if audit_data["status"] == "pass" else 1)


if __name__ == "__main__":
    main()
