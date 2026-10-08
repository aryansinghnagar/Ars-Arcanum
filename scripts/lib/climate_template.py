#!/usr/bin/env python3
"""
Ars Arcanum Planetary Climate Presentation Template (scripts/lib/climate_template.py)
====================================================================================
Offline HTML/SVG presentation layer for planetary insolation, circulation cells,
orographic rain shadow cross-sections, and Whittaker biome diagrams.

Zero external runtime dependencies; 100% offline air-gap with strict CSP.
"""

import html


def generate_circulation_svg(circ: dict) -> str:
    """Generates dynamic 2D SVG for atmospheric circulation cells and surface winds."""
    cells = circ.get("circulation_cells_per_hemisphere", 3)
    bands = circ.get("wind_bands", [])

    svg_parts = [
        '<svg viewBox="0 0 500 320" width="100%" height="280" xmlns="http://www.w3.org/2000/svg" style="background:#090d16; border-radius:8px;">',
        '  <defs>',
        '    <linearGradient id="globeGrad" x1="0%" y1="0%" x2="100%" y2="100%">',
        '      <stop offset="0%" stop-color="#1e3a8a"/>',
        '      <stop offset="60%" stop-color="#0f172a"/>',
        '      <stop offset="100%" stop-color="#020617"/>',
        '    </linearGradient>',
        '    <marker id="arrowHead" markerWidth="6" markerHeight="6" refX="4" refY="3" orient="auto">',
        '      <path d="M0,0 L6,3 L0,6 Z" fill="#38bdf8"/>',
        '    </marker>',
        '    <marker id="warmArrow" markerWidth="6" markerHeight="6" refX="4" refY="3" orient="auto">',
        '      <path d="M0,0 L6,3 L0,6 Z" fill="#f87171"/>',
        '    </marker>',
        '    <marker id="coldArrow" markerWidth="6" markerHeight="6" refX="4" refY="3" orient="auto">',
        '      <path d="M0,0 L6,3 L0,6 Z" fill="#60a5fa"/>',
        '    </marker>',
        '  </defs>',
        '  <!-- Planet Hemisphere Contour -->',
        '  <path d="M 60 280 A 220 220 0 0 1 280 60 L 280 280 Z" fill="url(#globeGrad)" stroke="#38bdf8" stroke-width="2"/>',
        '  <!-- Axis Line -->',
        '  <line x1="280" y1="40" x2="280" y2="290" stroke="#64748b" stroke-width="1.5" stroke-dasharray="4,4"/>',
        '  <text x="280" y="30" fill="#94a3b8" font-size="11" text-anchor="middle" font-family="sans-serif">North Pole (90°N)</text>',
        '  <!-- Equator Line -->',
        '  <line x1="50" y1="280" x2="290" y2="280" stroke="#ef4444" stroke-width="2"/>',
        '  <text x="45" y="295" fill="#f87171" font-size="11" font-family="sans-serif">Equator (0°)</text>',
    ]

    # Draw Circulation Cells
    if cells == 1:
        # Single Global Hadley Cell (Slow Rotator / Tidally Locked)
        svg_parts.extend([
            '  <!-- Global Hadley Cell Loop -->',
            '  <path d="M 120 270 Q 140 180 260 120" fill="none" stroke="#f87171" stroke-width="2.5" marker-end="url(#warmArrow)"/>',
            '  <path d="M 270 140 Q 180 220 140 275" fill="none" stroke="#60a5fa" stroke-width="2.5" marker-end="url(#coldArrow)"/>',
            '  <text x="350" y="160" fill="#f87171" font-size="12" font-weight="bold" font-family="sans-serif">Global Hadley Cell</text>',
            '  <text x="350" y="180" fill="#94a3b8" font-size="11" font-family="sans-serif">Slow Rotator Convection</text>',
            '  <text x="350" y="200" fill="#38bdf8" font-size="11" font-family="sans-serif">Direct Pole-to-Equator Flow</text>',
        ])
    elif cells == 3:
        # Standard 3-Cell (Hadley, Ferrel, Polar)
        svg_parts.extend([
            '  <!-- 30° Latitude Line -->',
            '  <line x1="90" y1="230" x2="280" y2="230" stroke="#475569" stroke-width="1" stroke-dasharray="3,3"/>',
            '  <text x="290" y="234" fill="#94a3b8" font-size="10" font-family="sans-serif">30°N (Horse Latitudes)</text>',
            '  <!-- 60° Latitude Line -->',
            '  <line x1="170" y1="140" x2="280" y2="140" stroke="#475569" stroke-width="1" stroke-dasharray="3,3"/>',
            '  <text x="290" y="144" fill="#94a3b8" font-size="10" font-family="sans-serif">60°N (Polar Front)</text>',
            '  <!-- Hadley Cell (0 - 30) -->',
            '  <path d="M 80 265 C 60 240 110 235 150 245" fill="none" stroke="#f87171" stroke-width="2" marker-end="url(#warmArrow)"/>',
            '  <text x="30" y="245" fill="#fca5a5" font-size="11" font-weight="bold" font-family="sans-serif">Hadley</text>',
            '  <!-- Ferrel Cell (30 - 60) -->',
            '  <path d="M 120 200 C 140 160 210 165 200 205" fill="none" stroke="#fbbf24" stroke-width="2" marker-end="url(#arrowHead)"/>',
            '  <text x="75" y="170" fill="#fde047" font-size="11" font-weight="bold" font-family="sans-serif">Ferrel</text>',
            '  <!-- Polar Cell (60 - 90) -->',
            '  <path d="M 210 120 C 230 90 270 95 260 125" fill="none" stroke="#60a5fa" stroke-width="2" marker-end="url(#coldArrow)"/>',
            '  <text x="180" y="90" fill="#93c5fd" font-size="11" font-weight="bold" font-family="sans-serif">Polar</text>',
        ])
    else:
        # Multi-cell fast rotator (5+ cells)
        svg_parts.extend([
            '  <text x="320" y="140" fill="#38bdf8" font-size="13" font-weight="bold" font-family="sans-serif">Fast Rotator Regime</text>',
            f'  <text x="320" y="165" fill="#94a3b8" font-size="11" font-family="sans-serif">{cells} Circulation Cells / Hemisphere</text>',
            '  <text x="320" y="185" fill="#34d399" font-size="11" font-family="sans-serif">Intense Zonal Jet Streams</text>',
        ])

    # Wind band annotations on the right pane
    y_pos = 255
    for b in reversed(bands[:4]):
        name = html.escape(b.get("name", ""))
        direction = html.escape(b.get("wind_direction", ""))
        svg_parts.append(
            f'  <text x="330" y="{y_pos}" fill="#e2e8f0" font-size="11" font-family="sans-serif">💨 <strong>{name} ({b.get("lat_min")}°–{b.get("lat_max")}°):</strong> {direction}</text>'
        )
        y_pos -= 24

    svg_parts.append('</svg>')
    return "\n".join(svg_parts)


def generate_orographic_svg(oro: dict) -> str:
    """Generates dynamic 2D SVG profile of orographic lifting and rain shadow."""
    elev = oro.get("mountain_elevation_m", 3000.0)
    wind_p = oro.get("windward", {}).get("precipitation_mm", 1000.0)
    leew_p = oro.get("leeward", {}).get("precipitation_mm", 300.0)
    wind_b = html.escape(oro.get("windward", {}).get("biome", "Forest"))
    leew_b = html.escape(oro.get("leeward", {}).get("biome", "Desert"))

    svg_parts = [
        '<svg viewBox="0 0 600 240" width="100%" height="220" xmlns="http://www.w3.org/2000/svg" style="background:#090d16; border-radius:8px;">',
        '  <defs>',
        '    <linearGradient id="mtnGrad" x1="0%" y1="0%" x2="100%" y2="0%">',
        '      <stop offset="0%" stop-color="#15803d"/>',
        '      <stop offset="45%" stop-color="#334155"/>',
        '      <stop offset="55%" stop-color="#64748b"/>',
        '      <stop offset="100%" stop-color="#78350f"/>',
        '    </linearGradient>',
        '    <linearGradient id="oceanGrad" x1="0%" y1="0%" x2="100%" y2="0%">',
        '      <stop offset="0%" stop-color="#0284c7"/>',
        '      <stop offset="100%" stop-color="#0369a1"/>',
        '    </linearGradient>',
        '  </defs>',
        '  <!-- Ocean / Water Source -->',
        '  <rect x="20" y="190" width="100" height="40" fill="url(#oceanGrad)" rx="3"/>',
        '  <text x="70" y="215" fill="#e0f2fe" font-size="11" text-anchor="middle" font-family="sans-serif">Ocean / Moisture</text>',
        '  <!-- Mountain Ridge Profile -->',
        '  <path d="M 120 200 L 280 50 L 450 200 L 580 200 L 580 230 L 120 230 Z" fill="url(#mtnGrad)"/>',
        '  <!-- Ridge Peak Marker -->',
        '  <circle cx="280" cy="50" r="4" fill="#f8fafc"/>',
        f'  <text x="280" y="38" fill="#f8fafc" font-size="11" font-weight="bold" text-anchor="middle" font-family="sans-serif">{int(elev)}m Crest</text>',
        '  <!-- Windward Moist Air Arrow & Cloud -->',
        '  <path d="M 60 170 Q 140 160 200 110" fill="none" stroke="#38bdf8" stroke-width="2.5" stroke-dasharray="4,4"/>',
        '  <text x="110" y="140" fill="#38bdf8" font-size="10" font-family="sans-serif">Moist Ascent (5°C/km)</text>',
        '  <ellipse cx="230" cy="85" rx="35" ry="18" fill="#94a3b8" opacity="0.85"/>',
        '  <text x="230" y="89" fill="#0f172a" font-size="10" font-weight="bold" text-anchor="middle" font-family="sans-serif">Rain Cloud</text>',
        '  <!-- Rain Streaks -->',
        '  <line x1="215" y1="108" x2="205" y2="135" stroke="#38bdf8" stroke-width="1.5" stroke-linecap="round"/>',
        '  <line x1="230" y1="108" x2="220" y2="138" stroke="#38bdf8" stroke-width="1.5" stroke-linecap="round"/>',
        '  <line x1="245" y1="108" x2="235" y2="135" stroke="#38bdf8" stroke-width="1.5" stroke-linecap="round"/>',
        '  <!-- Leeward Dry Air Arrow -->',
        '  <path d="M 330 80 Q 380 130 460 175" fill="none" stroke="#f59e0b" stroke-width="2.5" stroke-dasharray="4,4"/>',
        '  <text x="360" y="115" fill="#f59e0b" font-size="10" font-family="sans-serif">Dry Descent (9.8°C/km)</text>',
        '  <!-- Biome Badges -->',
        '  <g transform="translate(130, 205)">',
        f'    <text x="0" y="0" fill="#4ade80" font-size="11" font-weight="bold" font-family="sans-serif">🌿 Windward: {int(wind_p)} mm/yr</text>',
        f'    <text x="0" y="14" fill="#cbd5e1" font-size="10" font-family="sans-serif">({wind_b})</text>',
        '  </g>',
        '  <g transform="translate(430, 205)">',
        f'    <text x="0" y="0" fill="#fbbf24" font-size="11" font-weight="bold" font-family="sans-serif">🏜️ Leeward: {int(leew_p)} mm/yr</text>',
        f'    <text x="0" y="14" fill="#cbd5e1" font-size="10" font-family="sans-serif">({leew_b})</text>',
        '  </g>',
        '</svg>',
    ]
    return "\n".join(svg_parts)


def generate_whittaker_svg(temp_c: float, precip_mm: float, biome_name: str) -> str:
    """Generates dynamic 2D SVG Whittaker Biome diagram (Temp vs Precip) with active coordinate marker."""
    # Plot bounds: Temp -20 to 35°C (X: 50 to 350 px), Precip 0 to 4000 mm (Y: 220 to 30 px)
    def to_x(t: float) -> float:
        clamped = max(-20.0, min(35.0, t))
        return 50.0 + (clamped + 20.0) / 55.0 * 300.0

    def to_y(p: float) -> float:
        clamped = max(0.0, min(4000.0, p))
        return 220.0 - (clamped / 4000.0 * 190.0)

    cur_x = round(to_x(temp_c), 1)
    cur_y = round(to_y(precip_mm), 1)

    svg_parts = [
        '<svg viewBox="0 0 420 260" width="100%" height="240" xmlns="http://www.w3.org/2000/svg" style="background:#090d16; border-radius:8px;">',
        '  <!-- Grid Axes -->',
        '  <line x1="50" y1="220" x2="380" y2="220" stroke="#475569" stroke-width="1.5"/>',
        '  <line x1="50" y1="220" x2="50" y2="30" stroke="#475569" stroke-width="1.5"/>',
        '  <!-- Axis Labels -->',
        '  <text x="215" y="248" fill="#94a3b8" font-size="11" text-anchor="middle" font-family="sans-serif">Mean Annual Temperature (°C)</text>',
        '  <text x="15" y="125" fill="#94a3b8" font-size="11" text-anchor="middle" transform="rotate(-90 15 125)" font-family="sans-serif">Precip (mm/yr)</text>',
        '  <!-- Temp Ticks -->',
        '  <text x="50" y="235" fill="#64748b" font-size="9" text-anchor="middle" font-family="sans-serif">-20°</text>',
        '  <text x="159" y="235" fill="#64748b" font-size="9" text-anchor="middle" font-family="sans-serif">0°</text>',
        '  <text x="268" y="235" fill="#64748b" font-size="9" text-anchor="middle" font-family="sans-serif">20°</text>',
        '  <text x="350" y="235" fill="#64748b" font-size="9" text-anchor="middle" font-family="sans-serif">35°</text>',
        '  <!-- Precip Ticks -->',
        '  <text x="45" y="223" fill="#64748b" font-size="9" text-anchor="end" font-family="sans-serif">0</text>',
        '  <text x="45" y="130" fill="#64748b" font-size="9" text-anchor="end" font-family="sans-serif">2000</text>',
        '  <text x="45" y="38" fill="#64748b" font-size="9" text-anchor="end" font-family="sans-serif">4000</text>',
        '  <!-- Biome Polygonal Zones -->',
        '  <!-- Tundra / Ice -->',
        '  <polygon points="50,220 159,220 130,170 50,170" fill="#38bdf8" opacity="0.25"/>',
        '  <text x="85" y="200" fill="#7dd3fc" font-size="10" font-family="sans-serif">Tundra</text>',
        '  <!-- Boreal Forest / Taiga -->',
        '  <polygon points="100,170 200,170 180,110 90,140" fill="#0284c7" opacity="0.3"/>',
        '  <text x="125" y="150" fill="#38bdf8" font-size="10" font-family="sans-serif">Taiga</text>',
        '  <!-- Temperate Forest / Grassland -->',
        '  <polygon points="170,220 270,220 290,120 180,120" fill="#16a34a" opacity="0.25"/>',
        '  <text x="205" y="180" fill="#86efac" font-size="10" font-family="sans-serif">Temperate</text>',
        '  <!-- Subtropical Desert -->',
        '  <polygon points="270,220 370,220 370,195 270,205" fill="#d97706" opacity="0.3"/>',
        '  <text x="300" y="212" fill="#fcd34d" font-size="10" font-family="sans-serif">Desert</text>',
        '  <!-- Tropical Rainforest -->',
        '  <polygon points="260,120 370,120 370,35 250,60" fill="#059669" opacity="0.35"/>',
        '  <text x="285" y="80" fill="#6ee7b7" font-size="10" font-weight="bold" font-family="sans-serif">Tropical Rainforest</text>',
        '  <!-- Active Point Marker -->',
        f'  <circle cx="{cur_x}" cy="{cur_y}" r="6" fill="#f43f5e" stroke="#ffffff" stroke-width="2"/>',
        f'  <text x="{min(340.0, cur_x + 10)}" y="{max(45.0, cur_y - 8)}" fill="#fda4af" font-size="11" font-weight="bold" font-family="sans-serif">📍 {html.escape(biome_name)}</text>',
        '</svg>',
    ]
    return "\n".join(svg_parts)


def build_climate_html_report(climate_data: dict) -> str:
    """Renders complete standalone HTML report for planetary climate dynamics."""
    ins = climate_data.get("insolation", {})
    circ = climate_data.get("circulation", {})
    oro = climate_data.get("orography", {})

    wind_rows = []
    for b in circ.get("wind_bands", []):
        wind_rows.append(f"""
        <tr>
            <td>{b['lat_min']}° - {b['lat_max']}°</td>
            <td><strong>{html.escape(b['name'])}</strong></td>
            <td>{html.escape(b['wind_direction'])}</td>
            <td>{html.escape(b['surface_flow'])}</td>
        </tr>
        """)

    circ_svg = generate_circulation_svg(circ)
    oro_svg = generate_orographic_svg(oro)
    whittaker_svg = generate_whittaker_svg(
        temp_c=ins.get("surface_temp_c", 15.0),
        precip_mm=oro.get("windward", {}).get("precipitation_mm", 1000.0),
        biome_name=oro.get("windward", {}).get("biome", "Temperate Forest"),
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ars Arcanum — Planetary Climate & Biome Simulator</title>
<style>
  :root {{
    --bg: #0b0f19;
    --card-bg: #111827;
    --border: #1f2937;
    --text: #f3f4f6;
    --text-muted: #9ca3af;
    --accent: #38bdf8;
    --warning: #fbbf24;
    --success: #34d399;
    --danger: #f87171;
  }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background-color: var(--bg);
    color: var(--text);
    margin: 0;
    padding: 2rem;
  }}
  .container {{ max-width: 1200px; margin: 0 auto; }}
  h1, h2, h3 {{ color: var(--accent); margin-top: 0; }}
  .card {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
  }}
  .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }}
  .grid-3 {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1.5rem; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
  th, td {{ padding: 0.75rem; text-align: left; border-bottom: 1px solid var(--border); }}
  th {{ background: #090d16; color: var(--accent); }}
  .stat-badge {{
    display: inline-block;
    padding: 0.25rem 0.6rem;
    border-radius: 9999px;
    font-size: 0.85rem;
    font-weight: 600;
  }}
  .badge-success {{ background: rgba(52, 211, 153, 0.15); color: var(--success); border: 1px solid var(--success); }}
  .badge-danger {{ background: rgba(248, 113, 113, 0.15); color: var(--danger); border: 1px solid var(--danger); }}
</style>
</head>
<body>
<div class="container">
  <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.5rem;">
    <h1>🌍 Ars Arcanum Planetary Climate & Biome Simulator</h1>
    <span class="stat-badge {('badge-success' if ins.get('liquid_water_habitable') else 'badge-danger')}">
      {('✓ Liquid Water Habitable' if ins.get('liquid_water_habitable') else '✗ Hostile / Uninhabitable')}
    </span>
  </div>

  <div class="grid-2">
    <div class="card">
      <h2>Stellar Insolation & Surface Dynamics</h2>
      <p>Stellar Flux: <strong>{ins.get('stellar_flux_w_m2')} W/m²</strong> ({ins.get('stellar_luminosity_sun')} L☉ @ {ins.get('semi_major_axis_au')} AU)</p>
      <p>Bond Albedo: <strong>{ins.get('bond_albedo')}</strong> | Greenhouse Delta: <strong>+{ins.get('greenhouse_warming_k')} K</strong></p>
      <p>Equilibrium Temp: <strong>{ins.get('equilibrium_temp_k')} K</strong></p>
      <p>Mean Surface Temp: <strong style="color:{'#34d399' if ins.get('liquid_water_habitable') else '#f87171'};">{ins.get('surface_temp_c')} °C ({ins.get('surface_temp_f')} °F)</strong></p>
    </div>

    <div class="card">
      <h2>Atmospheric Circulation Regime</h2>
      <p>Rotation Period: <strong>{circ.get('rotation_period_hours')} hours</strong></p>
      <p>Circulation Cells: <strong>{circ.get('circulation_cells_per_hemisphere')} per hemisphere</strong></p>
      <p>Coriolis Effect: <strong>{circ.get('coriolis_effect')}</strong></p>
    </div>
  </div>

  <div class="grid-2">
    <div class="card">
      <h2>Atmospheric Circulation Cross-Section</h2>
      {circ_svg}
    </div>
    <div class="card">
      <h2>Whittaker Biome Matrix</h2>
      {whittaker_svg}
    </div>
  </div>

  <div class="card">
    <h2>Orographic Rain Shadow Dynamics ({int(oro.get('mountain_elevation_m', 3000))}m Ridge)</h2>
    {oro_svg}
  </div>

  <div class="card">
    <h2>Prevailing Planetary Wind Bands</h2>
    <table>
      <thead>
        <tr><th>Latitude</th><th>Circulation Cell</th><th>Prevailing Wind Direction</th><th>Surface Flow</th></tr>
      </thead>
      <tbody>
        {"".join(wind_rows)}
      </tbody>
    </table>
  </div>
</div>
</body>
</html>
"""
