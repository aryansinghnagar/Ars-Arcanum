#!/usr/bin/env python3
"""
Ars Arcanum UI Theme & Procedural Sound Studio (scripts/lib/ui_theme_studio.py)
=============================================================================
Interactive, 100% offline standalone HTML5 visualizer and acoustic drafting studio.
Provides:
- Real-time typing sandbox with live procedural typewriter audio feedback
- Instant visual preset switcher across all 11 aesthetic palettes
- 10 multi-generation acoustic typewriter and keyboard synthesis engines
- Live Words-Per-Minute (WPM), keystrokes, and pace telemetry
- Strict Content Security Policy (default-src 'none') and zero external assets
"""

from __future__ import annotations

import argparse
import sys
import tempfile
import webbrowser
from pathlib import Path

try:
    from lib._bootstrap import atomic_write
    from lib.ui_theme_engine import (
        SOUND_PRESETS,
        VISUAL_PRESETS,
        get_theme_control_center_html,
        get_theme_engine_css,
        get_theme_engine_js,
    )
except ImportError:
    from _bootstrap import atomic_write  # type: ignore[no-redef]
    from ui_theme_engine import (  # type: ignore[no-redef]
        SOUND_PRESETS,
        VISUAL_PRESETS,
        get_theme_control_center_html,
        get_theme_engine_css,
        get_theme_engine_js,
    )

_CSP = "default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;"


def render_theme_studio_html(output_path: Path | str | None = None) -> str:
    """Generates the interactive, standalone offline Theme & Sound Studio HTML document."""
    theme_css = get_theme_engine_css()
    theme_js = get_theme_engine_js()
    control_center_html = get_theme_control_center_html()

    # Visual Preset Chips for Gallery
    preset_gallery_cards = []
    for pid, pdata in VISUAL_PRESETS.items():
        swatches = "".join(
            f'<span class="arcanum-swatch-dot" style="background:{s}; width:16px; height:16px;"></span>'
            for s in pdata.get("swatches", [])
        )
        card = f"""
        <div class="studio-card preset-card" data-preset-id="{pid}" onclick="ArcanumThemeEngine.setTheme('{pid}'); updateStudioStatus();">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem;">
                <span style="font-weight:700; font-size:1rem;">{pdata.get('icon', '🎨')} {pdata.get('name', pid)}</span>
                <span class="badge badge-accent">{pdata.get('category', 'core').upper()}</span>
            </div>
            <div class="arcanum-swatch-row" style="margin:0.5rem 0;">{swatches}</div>
            <div style="font-size:0.8rem; color:var(--text-muted); line-height:1.4;">{pdata.get('description', '')}</div>
        </div>
        """
        preset_gallery_cards.append(card)

    # Sound Model Cards for Gallery
    sound_gallery_cards = []
    for sid, sdata in SOUND_PRESETS.items():
        card = f"""
        <div class="studio-card sound-card" data-sound-id="{sid}" onclick="ArcanumAudio.setModel('{sid}'); ArcanumAudio.play('a'); updateStudioStatus();">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem;">
                <span style="font-weight:700; font-size:0.95rem;">{sdata.get('icon', '⌨️')} {sdata.get('name', sid)}</span>
                <span class="badge badge-amber">{sdata.get('era', 'Classic')}</span>
            </div>
            <div style="font-size:0.8rem; color:var(--text-muted); line-height:1.4;">{sdata.get('description', '')}</div>
        </div>
        """
        sound_gallery_cards.append(card)

    html_content = f"""<!DOCTYPE html>
<html lang="en" data-theme="sovereign-dark">
<head>
    <meta http-equiv="Content-Security-Policy" content="{_CSP}">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ars Arcanum — Theme &amp; Typewriter Sound Studio</title>
    <style>
{theme_css}

        /* Studio Shell Layout */
        * {{ box-sizing: border-box; }}
        body {{
            font-family: var(--font-sans);
            background: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 2rem 1.5rem;
            line-height: 1.6;
            min-height: 100vh;
            transition: background 0.25s ease, color 0.25s ease;
        }}
        .studio-container {{
            max-width: 1280px;
            margin: 0 auto;
        }}
        .studio-banner {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 2rem;
            margin-bottom: 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1.5rem;
            box-shadow: var(--shadow);
        }}
        .banner-title-group h1 {{
            margin: 0 0 0.5rem 0;
            font-size: 2rem;
            font-weight: 800;
            color: var(--text);
            letter-spacing: -0.025em;
            display: flex;
            align-items: center;
            gap: 0.6rem;
        }}
        .banner-subtitle {{
            color: var(--text-muted);
            font-size: 0.95rem;
            margin: 0;
        }}
        .banner-actions {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            flex-wrap: wrap;
        }}

        /* Main Workspace Grid */
        .workspace-grid {{
            display: grid;
            grid-template-columns: 1.15fr 0.85fr;
            gap: 2rem;
            margin-bottom: 2.5rem;
        }}
        @media (max-width: 1024px) {{
            .workspace-grid {{
                grid-template-columns: 1fr;
            }}
        }}

        /* Sandbox & Drafting Terminal */
        .sandbox-panel {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 1.75rem;
            display: flex;
            flex-direction: column;
            box-shadow: var(--shadow);
        }}
        .sandbox-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
            padding-bottom: 0.75rem;
            border-bottom: 1px solid var(--border);
            flex-wrap: wrap;
            gap: 0.5rem;
        }}
        .sandbox-header h2 {{
            margin: 0;
            font-size: 1.25rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .typing-textarea {{
            width: 100%;
            min-height: 280px;
            background: var(--bg);
            color: var(--text);
            border: 2px solid var(--border);
            border-radius: 12px;
            padding: 1.25rem;
            font-family: var(--font-mono);
            font-size: 1.05rem;
            line-height: 1.6;
            resize: vertical;
            outline: none;
            transition: border-color 0.2s, box-shadow 0.2s;
        }}
        .typing-textarea:focus {{
            border-color: var(--accent);
            box-shadow: 0 0 15px var(--accent-glow);
        }}

        /* Live Telemetry KPI Bar */
        .telemetry-bar {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
            gap: 0.75rem;
            margin-top: 1.25rem;
        }}
        .telemetry-item {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 0.85rem;
            text-align: center;
        }}
        .telemetry-label {{
            font-size: 0.725rem;
            text-transform: uppercase;
            font-weight: 700;
            color: var(--text-muted);
            letter-spacing: 0.05em;
        }}
        .telemetry-val {{
            font-size: 1.5rem;
            font-weight: 800;
            color: var(--accent);
            margin-top: 0.25rem;
            font-variant-numeric: tabular-nums;
        }}

        /* Studio Cards & Galleries */
        .section-header {{
            margin: 2rem 0 1rem 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
            padding-bottom: 0.5rem;
        }}
        .section-header h2 {{
            margin: 0;
            font-size: 1.35rem;
            font-weight: 800;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .gallery-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 1rem;
        }}
        .studio-card {{
            background: var(--surface);
            border: 2px solid var(--border);
            border-radius: 12px;
            padding: 1.15rem;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        .studio-card:hover {{
            border-color: var(--accent);
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.3);
        }}
        .studio-card.active {{
            border-color: var(--accent);
            background: var(--bg-card);
            box-shadow: 0 0 16px var(--accent-glow);
        }}
        .badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 6px;
            font-size: 0.7rem;
            font-weight: 700;
            text-transform: uppercase;
        }}
        .badge-accent {{
            background: var(--accent-glow);
            color: var(--accent);
            border: 1px solid var(--accent);
        }}
        .badge-amber {{
            background: rgba(245, 158, 11, 0.15);
            color: var(--amber);
            border: 1px solid var(--amber);
        }}
        .btn {{
            background: var(--surface);
            color: var(--text);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 600;
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .btn:hover {{
            background: var(--surface-hover);
            border-color: var(--accent);
            color: var(--accent);
        }}
        .btn-primary {{
            background: var(--accent);
            color: var(--bg);
            border: none;
            font-weight: 700;
        }}
        .btn-primary:hover {{
            opacity: 0.9;
        }}
    </style>
</head>
<body>

<div class="studio-container">

    <!-- Top Header Banner -->
    <header class="studio-banner">
        <div class="banner-title-group">
            <h1>🎨 🎛️ Ars Arcanum Theme &amp; Sound Studio</h1>
            <p class="banner-subtitle">
                11 Atmospheric Visual Presets &bull; 10 Procedural Typewriter Acoustic Models &bull; 100% Offline Web Audio Synthesis
            </p>
        </div>
        <div class="banner-actions">
            {control_center_html}
        </div>
    </header>

    <!-- Main Interactive Workspace -->
    <div class="workspace-grid">

        <!-- Left Column: Live Typing Sandbox -->
        <div class="sandbox-panel">
            <div class="sandbox-header">
                <h2>⌨️ Interactive Typing Sandbox</h2>
                <div style="display:flex; gap:0.5rem; align-items:center;">
                    <span id="activeSoundBadge" class="badge badge-amber">Model: Remington (1890)</span>
                    <button class="btn" onclick="clearSandbox()" title="Clear text">Clear</button>
                    <button class="btn" onclick="loadSampleText()" title="Load test passage">Sample</button>
                </div>
            </div>

            <textarea id="typingSandbox" class="typing-textarea" placeholder="Start typing here to test live procedural typewriter acoustics, pitch variance, spacebar thuds, and carriage return bell pings..."></textarea>

            <!-- Live Telemetry KPI Bar -->
            <div class="telemetry-bar">
                <div class="telemetry-item">
                    <div class="telemetry-label">Typing Speed</div>
                    <div class="telemetry-val" id="statWpm">0.0</div>
                    <div style="font-size:0.7rem; color:var(--text-muted);">Words / Min</div>
                </div>
                <div class="telemetry-item">
                    <div class="telemetry-label">Words</div>
                    <div class="telemetry-val" id="statWords">0</div>
                    <div style="font-size:0.7rem; color:var(--text-muted);">Prose Count</div>
                </div>
                <div class="telemetry-item">
                    <div class="telemetry-label">Keystrokes</div>
                    <div class="telemetry-val" id="statKeys">0</div>
                    <div style="font-size:0.7rem; color:var(--text-muted);">Strikes Logged</div>
                </div>
                <div class="telemetry-item">
                    <div class="telemetry-label">Active Theme</div>
                    <div class="telemetry-val" id="statTheme" style="font-size:1rem; font-weight:700; color:var(--text); padding-top:0.4rem;">Sovereign</div>
                    <div style="font-size:0.7rem; color:var(--text-muted);" id="statThemeSub">Dark</div>
                </div>
            </div>
        </div>

        <!-- Right Column: Live Audio Controls & Quick Tests -->
        <div class="sandbox-panel">
            <div class="sandbox-header">
                <h2>🔊 Acoustic Synthesizer Controller</h2>
                <span class="badge badge-accent">Zero Disk WAVs</span>
            </div>

            <div style="margin-bottom:1.5rem;">
                <div class="arcanum-control-row">
                    <label style="font-weight:700; font-size:0.9rem;">Master Acoustic Volume:</label>
                    <div style="display:flex; align-items:center; gap:0.5rem;">
                        <input type="range" id="studioVolSlider" min="0" max="100" value="75" style="accent-color:var(--accent); cursor:pointer;" oninput="ArcanumAudio.setVolume(this.value/100); document.getElementById('studioVolVal').innerText=this.value+'%';">
                        <span id="studioVolVal" style="font-weight:700; font-size:0.9rem; color:var(--accent); min-width:40px;">75%</span>
                    </div>
                </div>

                <div class="arcanum-control-row" style="margin-top:1rem;">
                    <button id="studioMuteBtn" class="btn" onclick="ArcanumAudio.setMuted(!ArcanumAudio.isMuted); this.innerText=ArcanumAudio.isMuted?'🔇 Unmute Audio':'🔊 Mute Audio';">🔊 Mute Audio</button>
                    <label style="display:flex; align-items:center; gap:0.4rem; font-size:0.9rem; font-weight:600; cursor:pointer;">
                        <input type="checkbox" id="studioCrtToggle" onchange="ArcanumThemeEngine.setCrtEffect(this.checked)" style="accent-color:var(--accent);">
                        📺 CRT Scanlines Mode
                    </label>
                </div>
            </div>

            <div style="margin-top:0.5rem;">
                <div style="font-size:0.75rem; text-transform:uppercase; color:var(--text-muted); font-weight:700; margin-bottom:0.5rem;">Acoustic Key Strike Triggers:</div>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.5rem;">
                    <button class="btn" onclick="ArcanumAudio.play('a'); logKeystroke();">Letter Key (A)</button>
                    <button class="btn" onclick="ArcanumAudio.play(' '); logKeystroke();">Spacebar (Thud)</button>
                    <button class="btn" onclick="ArcanumAudio.play('enter'); logKeystroke();">Enter (Carriage Bell 🔔)</button>
                    <button class="btn" onclick="ArcanumAudio.play('backspace'); logKeystroke();">Backspace (Ratchet)</button>
                </div>
            </div>

            <div style="margin-top:1.5rem; padding-top:1rem; border-top:1px solid var(--border);">
                <div style="font-size:0.8rem; color:var(--text-muted);">
                    💡 <strong>Sovereign Privacy Guarantee:</strong> All keystroke sounds are synthesized mathematically on the fly via the Web Audio API without reading external audio files or sending telemetry.
                </div>
            </div>
        </div>

    </div>

    <!-- Section 1: Visual Presets Gallery (11) -->
    <div class="section-header">
        <h2>🎨 Visual Presets Gallery (11 Styles)</h2>
        <span style="font-size:0.85rem; color:var(--text-muted);">Click any preset to apply instantly across the whole interface</span>
    </div>
    <div class="gallery-grid" id="presetGallery">
        {"".join(preset_gallery_cards)}
    </div>

    <!-- Section 2: Typewriter Sound Models Gallery (10) -->
    <div class="section-header">
        <h2>🔊 Typewriter &amp; Keyboard Sound Models (10 Generations)</h2>
        <span style="font-size:0.85rem; color:var(--text-muted);">Click any model to audition and set active typewriter engine</span>
    </div>
    <div class="gallery-grid" id="soundGallery">
        {"".join(sound_gallery_cards)}
    </div>

</div>

<script>
{theme_js}

    // Studio Telemetry & Live Typing Tracking
    let keyCount = 0;
    let typingStartTime = null;
    let wpmInterval = null;

    const samplePassage = "The ancient scriptorium hummed with quiet focus. High arched windows framed the celestial dusk as the iron carriage struck parchment with rhythmic, measured precision. Every strike of the slug left dark, permanent ink upon the fiber, binding idea to record in sovereign permanence.";

    function loadSampleText() {{
        const box = document.getElementById('typingSandbox');
        box.value = samplePassage;
        box.focus();
        calculateStats();
    }}

    function clearSandbox() {{
        const box = document.getElementById('typingSandbox');
        box.value = '';
        keyCount = 0;
        typingStartTime = null;
        calculateStats();
        box.focus();
    }}

    function logKeystroke() {{
        keyCount++;
        if (!typingStartTime) typingStartTime = Date.now();
        calculateStats();
    }}

    function calculateStats() {{
        const box = document.getElementById('typingSandbox');
        const text = box.value || '';
        const words = text.trim().split(/\\s+/).filter(Boolean).length;
        const chars = text.length;

        document.getElementById('statWords').innerText = words.toLocaleString();
        document.getElementById('statKeys').innerText = keyCount.toLocaleString();

        let wpm = 0.0;
        if (typingStartTime && keyCount > 2) {{
            const elapsedMin = Math.max(0.05, (Date.now() - typingStartTime) / 60000);
            wpm = (words / elapsedMin).toFixed(1);
        }}
        document.getElementById('statWpm').innerText = wpm;
    }}

    function updateStudioStatus() {{
        const activeTheme = localStorage.getItem('arcanum_theme_preset') || 'sovereign-dark';
        const presetObj = ArcanumThemeEngine.presets[activeTheme] || {{ name: 'Sovereign Dark', category: 'core' }};
        const parts = (presetObj.name || activeTheme).split(' ');
        document.getElementById('statTheme').innerText = parts[0] || 'Theme';
        document.getElementById('statThemeSub').innerText = parts.slice(1).join(' ') || presetObj.category;

        // Highlight preset gallery cards
        document.querySelectorAll('.preset-card').forEach(c => {{
            c.classList.toggle('active', c.getAttribute('data-preset-id') === activeTheme);
        }});

        // Highlight sound gallery cards
        const activeSound = ArcanumAudio.currentModel;
        const soundObj = ArcanumThemeEngine.soundModels[activeSound] || {{ name: activeSound }};
        document.getElementById('activeSoundBadge').innerText = 'Model: ' + soundObj.name;
        document.querySelectorAll('.sound-card').forEach(c => {{
            c.classList.toggle('active', c.getAttribute('data-sound-id') === activeSound);
        }});

        // Sync volume
        const vol = Math.round(ArcanumAudio.volume * 100);
        const sSlider = document.getElementById('studioVolSlider');
        if (sSlider) sSlider.value = vol;
        const sVal = document.getElementById('studioVolVal');
        if (sVal) sVal.innerText = vol + '%';

        const muteBtn = document.getElementById('studioMuteBtn');
        if (muteBtn) muteBtn.innerText = ArcanumAudio.isMuted ? '🔇 Unmute Audio' : '🔊 Mute Audio';

        const crt = document.getElementById('studioCrtToggle');
        if (crt) crt.checked = document.body.classList.contains('crt-effect');
    }}

    // Hook sandbox typing
    const sandbox = document.getElementById('typingSandbox');
    sandbox.addEventListener('keydown', (e) => {{
        logKeystroke();
    }});
    sandbox.addEventListener('input', () => {{
        calculateStats();
    }});

    // Initialize status
    document.addEventListener('DOMContentLoaded', () => {{
        updateStudioStatus();
    }});
    setTimeout(updateStudioStatus, 100);
</script>

</body>
</html>
"""

    if output_path is not None:
        out_file = Path(output_path)
        atomic_write(out_file, html_content)
        return str(out_file)

    return html_content


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for Ars Arcanum Theme & Typewriter Sound Studio."""
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        prog="arcanum theme-studio",
        description="Launch the Ars Arcanum UI Visual Presets & Procedural Typewriter Sound Studio",
    )
    parser.add_argument(
        "--html",
        "-o",
        dest="output_file",
        help="Export standalone interactive HTML studio to specified file path",
        default=None,
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="Generate and immediately open the Theme & Sound Studio in default web browser",
    )
    parser.add_argument(
        "--preset",
        "-p",
        choices=list(VISUAL_PRESETS.keys()),
        help="Initial visual preset (retro, futuristic, retrofuturistic, fantastical, grim, edgy, cozy, scifi, horror, sovereign-dark, classic-light)",
        default=None,
    )
    parser.add_argument(
        "--sound",
        "-s",
        choices=list(SOUND_PRESETS.keys()),
        help="Initial typewriter sound model",
        default=None,
    )

    args = parser.parse_args(argv)

    if args.preset and args.preset in VISUAL_PRESETS:
        try:
            from lib.config import set_ui_visual_preset
            set_ui_visual_preset(args.preset)
        except Exception:
            pass

    if args.sound and args.sound in SOUND_PRESETS:
        try:
            from lib.config import set_typewriter_sound_preset
            set_typewriter_sound_preset(args.sound)
        except Exception:
            pass

    out_path = args.output_file
    if not out_path and args.open:
        # Generate to a temporary file for browser opening
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False, prefix="arcanum_theme_studio_") as tmp:
            out_path = tmp.name
    elif not out_path:
        out_path = "theme_studio.html"

    rendered_file = render_theme_studio_html(out_path)
    print(f"✨ Ars Arcanum Theme & Sound Studio generated: {rendered_file}")
    print(f"   Visual Presets: {len(VISUAL_PRESETS)} | Sound Models: {len(SOUND_PRESETS)}")

    if args.open:
        print("Opening in default web browser...")
        try:
            webbrowser.open(f"file://{Path(rendered_file).resolve()}")
        except Exception as e:
            print(f"Could not open browser automatically: {e}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
