#!/usr/bin/env python3
"""
Ars Arcanum Tactical Combat Simulator Presentation Template (scripts/lib/tactical_sim_template.py)
==================================================================================================
Offline HTML/SVG presentation layer for tactical skirmish simulations, unit rosters,
Monte Carlo victory probability gauges, and Lanchester campaign planning.

Zero external runtime dependencies; 100% offline air-gap with strict CSP.
"""

import html


def generate_combatant_card_svg(c: dict, side: int) -> str:
    """Generates a dynamic 2D SVG card for a combatant with HP, Armor, and Morale meters."""
    name = html.escape(c.get("name", "Fighter"))
    hp = c.get("hp", 20)
    max_hp = c.get("max_hp", hp)
    armor = c.get("armor", 2)
    atk = c.get("attack", 5)
    dmg = c.get("damage", 8)
    morale = c.get("morale", 70)
    c_type = html.escape(c.get("type", "melee"))
    alive = c.get("is_alive", True)
    routed = c.get("is_routed", False)

    # Health percent
    hp_pct = max(0.0, min(100.0, (hp / max(1.0, max_hp)) * 100.0))
    hp_color = "#34d399" if hp_pct > 50 else ("#fbbf24" if hp_pct > 25 else "#f87171")
    if not alive:
        status_text = "💀 KIA"
        status_color = "#94a3b8"
    elif routed:
        status_text = "🏃 Routed"
        status_color = "#f59e0b"
    else:
        status_text = "⚔️ Active"
        status_color = "#38bdf8" if side == 1 else "#a855f7"

    side_accent = "#38bdf8" if side == 1 else "#a855f7"

    return f"""
    <svg viewBox="0 0 280 120" width="100%" height="110" xmlns="http://www.w3.org/2000/svg" style="background:#0b0f19; border:1px solid #1f2937; border-left:4px solid {side_accent}; border-radius:6px; margin-bottom:8px;">
      <!-- Header -->
      <text x="12" y="22" fill="#f8fafc" font-size="12" font-weight="bold" font-family="sans-serif">{name}</text>
      <text x="268" y="22" fill="{status_color}" font-size="10" font-weight="bold" text-anchor="end" font-family="sans-serif">{status_text}</text>
      <text x="12" y="38" fill="#94a3b8" font-size="10" font-family="sans-serif">Type: {c_type.title()} | Armor: {armor} | Atk: +{atk} | Dmg: {dmg}</text>

      <!-- HP Bar Background & Fill -->
      <text x="12" y="58" fill="#cbd5e1" font-size="10" font-family="sans-serif">HP: {hp}/{max_hp}</text>
      <rect x="12" y="64" width="256" height="8" fill="#1e293b" rx="4"/>
      <rect x="12" y="64" width="{round(2.56 * hp_pct, 1)}" height="8" fill="{hp_color}" rx="4"/>

      <!-- Morale Bar Background & Fill -->
      <text x="12" y="88" fill="#cbd5e1" font-size="10" font-family="sans-serif">Morale: {morale}%</text>
      <rect x="12" y="94" width="256" height="6" fill="#1e293b" rx="3"/>
      <rect x="12" y="94" width="{round(2.56 * max(0, min(100, morale)), 1)}" height="6" fill="#eab308" rx="3"/>
    </svg>
    """


def generate_victory_gauge_svg(side1_rate: float, side2_rate: float, draw_rate: float, side1_name: str = "Side 1", side2_name: str = "Side 2") -> str:
    """Generates a dynamic 2D SVG victory probability bar and gauge."""
    w1 = round(side1_rate * 4.0, 1)
    wd = round(draw_rate * 4.0, 1)
    w2 = round(side2_rate * 4.0, 1)

    return f"""
    <svg viewBox="0 0 500 130" width="100%" height="120" xmlns="http://www.w3.org/2000/svg" style="background:#090d16; border-radius:8px; padding:10px;">
      <!-- Title -->
      <text x="10" y="20" fill="#94a3b8" font-size="11" font-family="sans-serif">MONTE CARLO PROBABILITY DISTRIBUTION</text>

      <!-- Probability Bar -->
      <g transform="translate(10, 35)">
        <rect x="0" y="0" width="{w1}" height="24" fill="#38bdf8" rx="4"/>
        <rect x="{w1}" y="0" width="{wd}" height="24" fill="#64748b"/>
        <rect x="{w1 + wd}" y="0" width="{w2}" height="24" fill="#a855f7" rx="4"/>
      </g>

      <!-- Labels -->
      <g transform="translate(10, 80)">
        <circle cx="6" cy="6" r="5" fill="#38bdf8"/>
        <text x="18" y="10" fill="#e2e8f0" font-size="11" font-weight="bold" font-family="sans-serif">{html.escape(side1_name)}: {side1_rate}%</text>

        <circle cx="180" cy="6" r="5" fill="#64748b"/>
        <text x="192" y="10" fill="#e2e8f0" font-size="11" font-family="sans-serif">Stalemate: {draw_rate}%</text>

        <circle cx="330" cy="6" r="5" fill="#a855f7"/>
        <text x="342" y="10" fill="#e2e8f0" font-size="11" font-weight="bold" font-family="sans-serif">{html.escape(side2_name)}: {side2_rate}%</text>
      </g>
    </svg>
    """


def build_tactical_sim_html(data: dict) -> str:
    """Renders standalone HTML report for tactical skirmish or campaign planning."""
    is_plan = "scenario" in data or "predicted_outcome" in data

    if is_plan:
        scenario = html.escape(data.get("scenario", "Campaign Warfare"))
        outcome = html.escape(data.get("predicted_outcome", "Undetermined"))
        ratio = data.get("combat_power_ratio", 1.0)
        terrain = html.escape(data.get("terrain", "open_field"))
        season = html.escape(data.get("season", "autumn"))
        turning_point = html.escape(data.get("narrative_turning_point", ""))
        frictions = data.get("frictions", [])
        beats = data.get("story_beats", [])
        lanchester = data.get("lanchester_analysis", {})

        frictions_html = "".join(f"<li>⚠️ {html.escape(f)}</li>" for f in frictions) or "<li>No critical frictions identified.</li>"
        beats_html = "".join(f"<div class='beat-card'><strong>Beat {i+1}:</strong> {html.escape(b)}</div>" for i, b in enumerate(beats))

        body_content = f"""
        <div class="card">
          <h2>⚔️ Warfare Scenario Analysis: {scenario}</h2>
          <div class="grid-2">
            <div>
              <p>Predicted Outcome: <strong style="color:#38bdf8;">{outcome}</strong></p>
              <p>Combat Power Ratio: <strong>{ratio} : 1</strong></p>
              <p>Terrain: <strong>{terrain.replace('_', ' ').title()}</strong> | Season: <strong>{season.title()}</strong></p>
            </div>
            <div>
              <p>Turning Point Catalyst: <em>"{turning_point}"</em></p>
              <p>Lanchester Law: <strong>{html.escape(lanchester.get('law_applied', 'Square Law'))}</strong></p>
            </div>
          </div>
        </div>

        <div class="grid-2">
          <div class="card">
            <h3>⚠️ Tactical & Logistical Frictions</h3>
            <ul style="padding-left:1.2rem; line-height:1.7;">
              {frictions_html}
            </ul>
          </div>
          <div class="card">
            <h3>📖 Narrative Campaign Story Beats</h3>
            {beats_html}
          </div>
        </div>
        """
    else:
        # Skirmish / Monte Carlo simulation
        is_mc = "side1_win_rate" in data
        terrain_name = html.escape(data.get("terrain_name", data.get("terrain", "Open Field")))

        if is_mc:
            s1_rate = data.get("side1_win_rate", 50.0)
            s2_rate = data.get("side2_win_rate", 50.0)
            d_rate = data.get("draw_rate", 0.0)
            runs = data.get("runs", 100)
            avg_rounds = data.get("avg_rounds", 5.0)
            gauge_svg = generate_victory_gauge_svg(s1_rate, s2_rate, d_rate)

            body_content = f"""
            <div class="card">
              <h2>🎲 Monte Carlo Combat Simulation ({runs} Runs)</h2>
              <p>Terrain: <strong>{terrain_name}</strong> | Average Duration: <strong>{avg_rounds} rounds</strong></p>
              {gauge_svg}
            </div>
            """
        else:
            winner = html.escape(data.get("winner_name", "Stalemate"))
            rounds = data.get("rounds_lasted", 1)
            mvp = data.get("mvp", {})
            mvp_name = html.escape(mvp.get("name", "None"))
            mvp_dmg = mvp.get("damage", 0)
            mvp_kills = mvp.get("kills", 0)
            log = data.get("log", [])

            log_html = "".join(f"<div class='log-line'>{html.escape(line)}</div>" for line in log)

            body_content = f"""
            <div class="card">
              <h2>🏆 Skirmish Victory: <span style="color:#38bdf8;">{winner}</span></h2>
              <div class="grid-2">
                <div>
                  <p>Terrain: <strong>{terrain_name}</strong></p>
                  <p>Duration: <strong>{rounds} Rounds</strong></p>
                </div>
                <div>
                  <p>🌟 MVP Combatant: <strong>{mvp_name}</strong> ({mvp_dmg} damage dealt, {mvp_kills} kills)</p>
                </div>
              </div>
            </div>

            <div class="card">
              <h3>📜 Blow-by-Blow Narrative Combat Log</h3>
              <div class="combat-log-stream">
                {log_html}
              </div>
            </div>
            """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ars Arcanum — Tactical Combat Simulator</title>
<style>
  :root {{
    --bg: #0b0f19;
    --card-bg: #111827;
    --border: #1f2937;
    --text: #f3f4f6;
    --accent: #38bdf8;
    --purple: #a855f7;
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
  .container {{ max-width: 1100px; margin: 0 auto; }}
  h1, h2, h3 {{ color: var(--accent); margin-top: 0; }}
  .card {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
  }}
  .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }}
  .beat-card {{
    background: #090d16;
    border: 1px solid #334155;
    border-left: 3px solid #38bdf8;
    border-radius: 4px;
    padding: 0.75rem;
    margin-bottom: 0.5rem;
    font-size: 0.95rem;
  }}
  .combat-log-stream {{
    background: #090d16;
    border: 1px solid #1f2937;
    border-radius: 6px;
    padding: 1rem;
    max-height: 400px;
    overflow-y: auto;
    font-family: "Cascadia Code", "Fira Code", monospace;
    font-size: 0.9rem;
    line-height: 1.6;
  }}
  .log-line {{
    padding: 0.25rem 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  }}
</style>
</head>
<body>
<div class="container">
  <h1>🛡️ Ars Arcanum Tactical Combat Simulator</h1>
  {body_content}
</div>
</body>
</html>
"""
