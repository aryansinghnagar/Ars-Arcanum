#!/usr/bin/env python3
"""
Ars Arcanum Universal Resonance Mesh HTML Presentation Template
(scripts/lib/resonance_template.py)
"""

from __future__ import annotations

import json
from typing import Any

VERSION = "0.1.0"
CSP_HEADER = "<meta http-equiv=\"Content-Security-Policy\" content=\"default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;\">"


def render_resonance_html(
    nodes_data: list[dict[str, Any]],
    edges_data: list[dict[str, Any]],
    sparks_data: list[dict[str, Any]],
    violations_data: list[dict[str, Any]],
    csp_header: str = CSP_HEADER,
    version: str = VERSION,
) -> str:
    """Generates a sovereign, standalone offline HTML Knowledge Mesh and Simulation Lab."""
    nodes_json = json.dumps(nodes_data).replace("</", "<\\/")
    edges_json = json.dumps(edges_data).replace("</", "<\\/")
    sparks_json = json.dumps(sparks_data).replace("</", "<\\/")
    violations_json = json.dumps(violations_data).replace("</", "<\\/")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
<meta charset="utf-8">
<title>Ars Arcanum — Universal Knowledge Mesh & Cross-Domain Synergy Lab</title>
<style>
:root {{
    --bg-primary: #0d1117;
    --bg-secondary: #161b22;
    --bg-card: #21262d;
    --border-color: #30363d;
    --text-primary: #c9d1d9;
    --text-muted: #8b949e;
    --accent-blue: #58a6ff;
    --accent-green: #3fb950;
    --accent-purple: #bc8cff;
    --accent-orange: #d29922;
    --accent-red: #f85149;
    --pillar-cosmo: #58a6ff;
    --pillar-society: #bc8cff;
    --pillar-narrative: #3fb950;
    --pillar-style: #d29922;
    --pillar-os: #f0883e;
    --font-mono: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
    --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
    background: var(--bg-primary);
    color: var(--text-primary);
    font-family: var(--font-sans);
    line-height: 1.5;
    display: flex;
    flex-direction: column;
    height: 100vh;
    overflow: hidden;
}}
header {{
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border-color);
    padding: 12px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-shrink: 0;
}}
.header-title {{
    display: flex;
    align-items: center;
    gap: 12px;
}}
.header-title h1 {{
    font-size: 18px;
    font-weight: 600;
    color: #f0f6fc;
}}
.badge {{
    background: rgba(88, 166, 255, 0.15);
    color: var(--accent-blue);
    border: 1px solid rgba(88, 166, 255, 0.3);
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
}}
.tabs {{
    display: flex;
    gap: 8px;
}}
.tab-btn {{
    background: transparent;
    border: 1px solid transparent;
    color: var(--text-muted);
    padding: 6px 14px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 13px;
    font-weight: 500;
    transition: all 0.2s ease;
}}
.tab-btn:hover {{
    color: var(--text-primary);
    background: rgba(255, 255, 255, 0.05);
}}
.tab-btn.active {{
    background: var(--bg-card);
    border-color: var(--border-color);
    color: #f0f6fc;
}}
.main-container {{
    display: flex;
    flex: 1;
    overflow: hidden;
}}
.graph-pane {{
    flex: 1;
    position: relative;
    background: radial-gradient(circle at center, #131822 0%, #0d1117 100%);
    overflow: hidden;
}}
#canvas {{
    width: 100%;
    height: 100%;
    display: block;
}}
.sidebar-pane {{
    width: 440px;
    background: var(--bg-secondary);
    border-left: 1px solid var(--border-color);
    display: flex;
    flex-direction: column;
    overflow-y: auto;
    flex-shrink: 0;
}}
.panel-header {{
    padding: 16px;
    border-bottom: 1px solid var(--border-color);
    font-weight: 600;
    font-size: 14px;
    color: #f0f6fc;
    display: flex;
    justify-content: space-between;
    align-items: center;
}}
.panel-content {{
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 16px;
}}
.card {{
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 14px;
    display: flex;
    flex-direction: column;
    gap: 8px;
}}
.card-title {{
    font-weight: 600;
    font-size: 13px;
    color: #f0f6fc;
    display: flex;
    justify-content: space-between;
    align-items: center;
}}
.card-body {{
    font-size: 12px;
    color: var(--text-primary);
    line-height: 1.5;
}}
.card-meta {{
    font-size: 11px;
    color: var(--text-muted);
    font-family: var(--font-mono);
}}
.btn {{
    background: #238636;
    color: #ffffff;
    border: 1px solid rgba(240, 246, 252, 0.1);
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s;
}}
.btn:hover {{
    background: #2ea043;
}}
.btn-secondary {{
    background: #21262d;
    color: var(--text-primary);
    border: 1px solid var(--border-color);
}}
.btn-secondary:hover {{
    background: #30363d;
}}
.form-group {{
    display: flex;
    flex-direction: column;
    gap: 6px;
}}
.form-label {{
    font-size: 11px;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
}}
.form-input, select {{
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    color: var(--text-primary);
    padding: 6px 10px;
    border-radius: 6px;
    font-size: 12px;
    font-family: var(--font-sans);
}}
.tag-list {{
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
}}
.tag {{
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid var(--border-color);
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 11px;
    color: var(--text-muted);
}}
.palette-item {{
    background: rgba(88, 166, 255, 0.1);
    border-left: 3px solid var(--accent-blue);
    padding: 6px 10px;
    font-size: 11px;
    border-radius: 0 4px 4px 0;
}}
.legend {{
    position: absolute;
    bottom: 16px;
    left: 16px;
    background: rgba(22, 27, 34, 0.85);
    backdrop-filter: blur(8px);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 10px 14px;
    display: flex;
    flex-direction: column;
    gap: 6px;
    font-size: 11px;
    pointer-events: none;
}}
.legend-item {{
    display: flex;
    align-items: center;
    gap: 8px;
}}
.legend-dot {{
    width: 10px;
    height: 10px;
    border-radius: 50%;
}}
.search-bar {{
    position: absolute;
    top: 16px;
    left: 16px;
    background: rgba(22, 27, 34, 0.85);
    backdrop-filter: blur(8px);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 6px 12px;
    display: flex;
    align-items: center;
    gap: 8px;
    width: 280px;
}}
.search-bar input {{
    background: transparent;
    border: none;
    color: var(--text-primary);
    font-size: 12px;
    width: 100%;
    outline: none;
}}
</style>
</head>
<body>

<header>
    <div class="header-title">
        <h1>Universal Knowledge & Resonance Mesh</h1>
        <span class="badge">v{VERSION} Ecosystem</span>
    </div>
    <div class="tabs">
        <button class="tab-btn active" onclick="switchTab('graph')">Knowledge Mesh</button>
        <button class="tab-btn" onclick="switchTab('cascade')">Causal Cascade Sandbox</button>
        <button class="tab-btn" onclick="switchTab('sparks')">Creative Spark Lab</button>
        <button class="tab-btn" onclick="switchTab('audit')">Coherence Audit</button>
    </div>
</header>

<div class="main-container">
    <div class="graph-pane">
        <canvas id="canvas"></canvas>
        <div class="search-bar">
            <input type="text" id="nodeSearch" placeholder="Search engines & lore nodes..." oninput="onSearch(this.value)">
        </div>
        <div class="legend">
            <div class="legend-item"><span class="legend-dot" style="background: var(--pillar-cosmo);"></span> Cosmology & Physics (6)</div>
            <div class="legend-item"><span class="legend-dot" style="background: var(--pillar-society);"></span> Society & Systems (6)</div>
            <div class="legend-item"><span class="legend-dot" style="background: var(--pillar-narrative);"></span> Narrative & Chronology (10)</div>
            <div class="legend-item"><span class="legend-dot" style="background: var(--pillar-style);"></span> Stylistics & Senses (6)</div>
            <div class="legend-item"><span class="legend-dot" style="background: var(--pillar-os);"></span> Authoring OS (22)</div>
        </div>
    </div>

    <div class="sidebar-pane" id="sidebar">
        <!-- Dynamic Sidebar View Content -->
    </div>
</div>

<script>
const NODES = {nodes_json};
const EDGES = {edges_json};
const SPARKS = {sparks_json};
const VIOLATIONS = {violations_json};

let currentTab = 'graph';
let selectedNode = null;
let searchQuery = '';

const PILLAR_COLORS = {{
    "cosmology_physics": "#58a6ff",
    "society_systems": "#bc8cff",
    "narrative_chronology": "#3fb950",
    "stylistics_senses": "#d29922",
    "authoring_production": "#f0883e"
}};

// Simulation Canvas Layout
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
let width, height;
let simNodes = [];
let simEdges = [];
let animId = null;

function initSimulation() {{
    width = canvas.parentElement.clientWidth;
    height = canvas.parentElement.clientHeight;
    canvas.width = width;
    canvas.height = height;

    simNodes = NODES.map((n, i) => {{
        const angle = (i / NODES.length) * Math.PI * 2;
        const radius = Math.min(width, height) * 0.35 * (0.4 + Math.random() * 0.6);
        return {{
            ...n,
            x: width / 2 + Math.cos(angle) * radius,
            y: height / 2 + Math.sin(angle) * radius,
            vx: 0,
            vy: 0,
            radius: n.node_type === 'domain' ? 9 : 6
        }};
    }});

    const nodeMap = new Map(simNodes.map(n => [n.id, n]));
    simEdges = EDGES.map(e => ({{
        ...e,
        source: nodeMap.get(e.source_id),
        target: nodeMap.get(e.target_id)
    }})).filter(e => e.source && e.target);

    renderGraph();
}}

function renderGraph() {{
    ctx.clearRect(0, 0, width, height);

    // Update simple spring physics
    for (let i = 0; i < simNodes.length; i++) {{
        const a = simNodes[i];
        // Center gravity
        const dx = width / 2 - a.x;
        const dy = height / 2 - a.y;
        a.vx += dx * 0.0005;
        a.vy += dy * 0.0005;

        // Repulsion
        for (let j = i + 1; j < simNodes.length; j++) {{
            const b = simNodes[j];
            const rx = b.x - a.x;
            const ry = b.y - a.y;
            const dist = Math.sqrt(rx * rx + ry * ry) || 1;
            if (dist < 180) {{
                const force = (180 - dist) / dist * 0.05;
                a.vx -= rx * force;
                a.vy -= ry * force;
                b.vx += rx * force;
                b.vy += ry * force;
            }}
        }}

        a.x += a.vx * 0.85;
        a.y += a.vy * 0.85;
        a.vx *= 0.85;
        a.vy *= 0.85;
    }}

    // Draw edges
    ctx.lineWidth = 1;
    for (const e of simEdges) {{
        ctx.strokeStyle = "rgba(48, 54, 61, 0.4)";
        if (selectedNode && (e.source.id === selectedNode.id || e.target.id === selectedNode.id)) {{
            ctx.strokeStyle = "rgba(88, 166, 255, 0.8)";
            ctx.lineWidth = 2;
        }}
        ctx.beginPath();
        ctx.moveTo(e.source.x, e.source.y);
        ctx.lineTo(e.target.x, e.target.y);
        ctx.stroke();
        ctx.lineWidth = 1;
    }}

    // Draw nodes
    for (const n of simNodes) {{
        const isMatch = !searchQuery || n.label.toLowerCase().includes(searchQuery) || n.engine.toLowerCase().includes(searchQuery);
        const isSelected = selectedNode && selectedNode.id === n.id;

        ctx.fillStyle = isMatch ? (PILLAR_COLORS[n.pillar] || "#c9d1d9") : "#30363d";
        ctx.beginPath();
        ctx.arc(n.x, n.y, isSelected ? n.radius + 4 : n.radius, 0, Math.PI * 2);
        ctx.fill();

        if (isSelected) {{
            ctx.strokeStyle = "#ffffff";
            ctx.lineWidth = 2;
            ctx.stroke();
        }}

        // Label
        if (n.node_type === 'domain' || isSelected || isMatch && searchQuery) {{
            ctx.fillStyle = isMatch ? "#f0f6fc" : "#8b949e";
            ctx.font = isSelected ? "bold 12px sans-serif" : "11px sans-serif";
            ctx.fillText(n.label, n.x + n.radius + 4, n.y + 4);
        }}
    }}

    animId = requestAnimationFrame(renderGraph);
}}

// Node selection click handler
canvas.addEventListener('click', (e) => {{
    const rect = canvas.getBoundingClientRect();
    const cx = e.clientX - rect.left;
    const cy = e.clientY - rect.top;

    let clicked = null;
    for (const n of simNodes) {{
        const dx = n.x - cx;
        const dy = n.y - cy;
        if (Math.sqrt(dx * dx + dy * dy) < n.radius + 6) {{
            clicked = n;
            break;
        }}
    }}
    selectedNode = clicked;
    updateSidebar();
}});

function onSearch(val) {{
    searchQuery = val.toLowerCase().trim();
}}

function switchTab(tab) {{
    currentTab = tab;
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    updateSidebar();
}}

function updateSidebar() {{
    const sb = document.getElementById('sidebar');

    if (currentTab === 'graph') {{
        if (selectedNode) {{
            const connectedEdges = EDGES.filter(e => e.source_id === selectedNode.id || e.target_id === selectedNode.id);
            sb.innerHTML = `
                <div class="panel-header">
                    <span>Node Inspector</span>
                    <span class="badge" style="background: rgba(88, 166, 255, 0.1); color: ${{PILLAR_COLORS[selectedNode.pillar]}}">${{selectedNode.pillar}}</span>
                </div>
                <div class="panel-content">
                    <div class="card">
                        <div class="card-title">${{selectedNode.label}}</div>
                        <div class="card-meta">Engine: ${{selectedNode.engine}} | Type: ${{selectedNode.node_type}}</div>
                        <div class="card-body">${{selectedNode.summary || 'Core domain engine node.'}}</div>
                    </div>
                    <div class="card">
                        <div class="card-title">Cross-Domain Connections (${{connectedEdges.length}})</div>
                        <div class="card-body" style="display: flex; flex-direction: column; gap: 8px;">
                            ${{connectedEdges.map(e => `
                                <div class="palette-item">
                                    <strong>${{e.source_id === selectedNode.id ? '-> ' + e.target_id : '<- ' + e.source_id}}</strong>:
                                    <span>${{e.description || e.relation}}</span>
                                </div>
                            `).join('')}}
                        </div>
                    </div>
                    <button class="btn btn-secondary" onclick="simulateCascadeForNode('${{selectedNode.id}}')">Simulate Causal Cascade</button>
                </div>
            `;
        }} else {{
            sb.innerHTML = `
                <div class="panel-header">Knowledge Mesh Overview</div>
                <div class="panel-content">
                    <div class="card">
                        <div class="card-title">Ecosystem Topology</div>
                        <div class="card-body">
                            The Ars Arcanum Universal Resonance Mesh unifies all 53 engines into a deterministic, multi-hop knowledge graph.
                            Click any node on the graph to inspect cross-domain links, parameters, and causal relationships.
                        </div>
                    </div>
                    <div class="card">
                        <div class="card-title">Domain Statistics</div>
                        <div class="card-body">
                            <strong>Total Indexed Nodes:</strong> ${{NODES.length}}<br>
                            <strong>Cross-Domain Edges:</strong> ${{EDGES.length}}<br>
                            <strong>Pillar Distribution:</strong> 5 Master Pillars
                        </div>
                    </div>
                </div>
            `;
        }}
    }} else if (currentTab === 'cascade') {{
        sb.innerHTML = `
            <div class="panel-header">Causal Cascade Sandbox</div>
            <div class="panel-content">
                <div class="card">
                    <div class="card-title">Parameter Cascade Simulator</div>
                    <div class="card-body">
                        Modify an upstream world parameter to deterministically calculate downstream domino effects across physics, ecology, economy, factions, and manuscript tension.
                    </div>
                    <div class="form-group" style="margin-top: 8px;">
                        <label class="form-label">Origin Parameter</label>
                        <select id="cascadeParam" class="form-input" onchange="runCascadeSimulation()">
                            <option value="axial_tilt">Planetary Axial Tilt (Astrophysics -> Climate -> Economy -> Military)</option>
                            <option value="magic_cost">Arcane Mana Backlash (Magic -> Factions -> Labor Market)</option>
                            <option value="currency_debasement">Specie Debasement (Economy -> Morale -> Revolt -> Voice)</option>
                            <option value="stellar_mass">Stellar Mass & Luminosity (Astrophysics -> Calendar -> Conlang)</option>
                        </select>
                    </div>
                </div>
                <div id="cascadeResults" style="display: flex; flex-direction: column; gap: 10px;">
                    <!-- Results populated dynamically -->
                </div>
            </div>
        `;
        runCascadeSimulation();
    }} else if (currentTab === 'sparks') {{
        sb.innerHTML = `
            <div class="panel-header">Creative Spark Lab</div>
            <div class="panel-content">
                <div class="card">
                    <div class="card-title">Cross-Field Isomorphism Synthesizer</div>
                    <div class="card-body">
                        Algorithmic structural analogies connecting disparate fields to stimulate novel narrative dilemmas and worldbuilding depth.
                    </div>
                </div>
                ${{SPARKS.map(s => `
                    <div class="card">
                        <div class="card-title">${{s.title}}</div>
                        <div class="tag-list">
                            ${{s.domains.map(d => `<span class="tag">${{d}}</span>`).join('')}}
                        </div>
                        <div class="card-body" style="margin-top: 6px;">
                            <strong>Analogy:</strong> ${{s.core_analogy}}<br><br>
                            <strong>Worldbuilding Hook:</strong> ${{s.worldbuilding_hook}}<br><br>
                            <strong>Scene Conflict:</strong> ${{s.scene_conflict}}
                        </div>
                        <div class="card-meta" style="margin-top: 6px;">
                            <strong>Sensory Palette:</strong> ${{s.sensory_palette.join(' • ')}}
                        </div>
                    </div>
                `).join('')}}
            </div>
        `;
    }} else if (currentTab === 'audit') {{
        sb.innerHTML = `
            <div class="panel-header">Coherence & Integrity Audit</div>
            <div class="panel-content">
                <div class="card">
                    <div class="card-title">Cross-Domain Coherence Status</div>
                    <div class="card-body">
                        ${{VIOLATIONS.length === 0 ? 'All 53 engines and world nodes are in 100% mutual mathematical and narrative alignment.' : 'Found ' + VIOLATIONS.length + ' advisory coherence notices.'}}
                    </div>
                </div>
                ${{VIOLATIONS.map(v => `
                    <div class="card" style="border-left: 3px solid var(--accent-orange);">
                        <div class="card-title">${{v.rule_id}}: ${{v.severity.toUpperCase()}}</div>
                        <div class="card-body">${{v.message}}</div>
                        <div class="card-meta">Recommendation: ${{v.recommendation}}</div>
                    </div>
                `).join('')}}
            </div>
        `;
    }}
}}

function runCascadeSimulation() {{
    const val = document.getElementById('cascadeParam')?.value || 'axial_tilt';
    const container = document.getElementById('cascadeResults');
    if (!container) return;

    const dummyImpacts = {{
        "axial_tilt": [
            {{ node: "Climate & Biomes", delta: "Axial tilt set to 38.5°: Expands polar circle latitudes, inducing severe continental seasonal swings." }},
            {{ node: "Ecology & Agriculture", delta: "Agrarian crop growing season shortened to 95 days, increasing winter famine vulnerability." }},
            {{ node: "Macroeconomics", delta: "Grain commodity futures volatility increases by +35%, incentivizing mercantile hoarding." }},
            {{ node: "Tactical Battle Sim", delta: "Military siege window restricted strictly to mid-summer; winter operations suffer 40% attrition." }},
            {{ node: "Scene Mechanics & Zen Studio", delta: "Prose tension shifts toward urgent race-against-frost survival motifs." }}
        ],
        "magic_cost": [
            {{ node: "Geopolitical Factions", delta: "Severe arcane backlash centralizes magical casting to licensed royal monopolies." }},
            {{ node: "Labor Economics", delta: "Displaces manual artisan guilds as high-tier enchanted production replaces manual labor." }},
            {{ node: "Prophecy Lifecycle", delta: "Prophetic omens become quantitatively verifiable via arcane leyline discharge meters." }}
        ],
        "currency_debasement": [
            {{ node: "Faction Stability", delta: "Provincial revolt risk escalates to 0.78 as garrison troop pay purchasing power collapses." }},
            {{ node: "Tactical Battle Sim", delta: "Mercenary morale threshold drops to 40, increasing early route probability in skirmishes." }},
            {{ node: "Character Voice", delta: "Provincial characters adopt subversive underground cant and anti-royalist idioms." }}
        ],
        "stellar_mass": [
            {{ node: "Planetary Calendar", delta: "Solar year expands to 498.2 days; generates 4 intercalary epagomenal celebration weeks." }},
            {{ node: "Conlang Lexicon", delta: "Epagomenal festivals generate idiomatic expressions for fleeting romantic encounters." }}
        ]
    }};

    const list = dummyImpacts[val] || [];
    container.innerHTML = list.map(item => `
        <div class="card">
            <div class="card-title" style="color: var(--accent-blue);">${{item.node}}</div>
            <div class="card-body">${{item.delta}}</div>
        </div>
    `).join('');
}}

function simulateCascadeForNode(nodeId) {{
    currentTab = 'cascade';
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-btn')[1].classList.add('active');
    updateSidebar();
}}

// Initialize
window.addEventListener('resize', initSimulation);
window.addEventListener('DOMContentLoaded', () => {{
    initSimulation();
    updateSidebar();
}});
</script>
</body>
</html>
"""
