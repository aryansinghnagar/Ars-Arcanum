#!/usr/bin/env python3
"""
Domain engine specification definitions for Ars Arcanum Registry.
"""
from __future__ import annotations

try:
    from lib.registry_base import EngineCategory, EngineSpec
except ImportError:
    from registry_base import EngineCategory, EngineSpec

ENGINES: dict[str, EngineSpec] = {

    # =========================================================================
    # DOMAIN E: STUDIOS, AUTHORING COCKPITS & AUDIO FOCUS
    # =========================================================================
    "studio_hub": EngineSpec(
        name="studio_hub",
        category=EngineCategory.CORE,
        title="Sovereign Studio Desktop Hub & Dashboard",
        description="Master unified desktop and web orchestrator dashboard unifying all 50 craft engines",
        module_name="lib.studio_hub",
        cli_command="hub",
        aliases=["dashboard", "studio-hub", "gui-web", "hub"],
        studio_tab="Tools",
        logic_documentation="Master local-first web and desktop orchestrator providing live manuscript telemetry, lore entity cards, structural harmony curves, timeline paradox audits, and craft engine matrix.",
        scientific_logic="""1. Local-First Orchestration Architecture:
   Zero-dependency Python HTTP/WebSocket server running on localhost ($127.0.0.1$) serving 100% offline single-page application with strict Content Security Policy:
   `default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:; connect-src 'self';`

2. Real-Time Telemetry Extractor:
   Scans workspace ASTs on modification, updating word count milestones, reading time (200 wpm), narration time (150 wpm), and timeline bilocation paradox counters.""",
        why_this_way="Authors need a central, beautiful command cockpit to inspect their universe, drafts, and craft engines without relying on cloud services.",
        worldbuilding_relevance="Central command cockpit unifying all 50 domain engines into an intuitive GUI.",
        storytelling_relevance="Displays real-time project metrics: words, reading hours, chapters, and paradoxes.",
        writing_relevance="Runs 100% offline with zero external network calls or cloud dependencies.",
        subfeatures=[
            {"name": "Craft Science Encyclopedia Viewer", "rule": "Searchable interactive browser drawer detailing mathematical/physical logic and examples for all 50 engines.", "example": "arcanum hub --tab guide"},
            {"name": "Live Telemetry Dashboard", "rule": "Displays real-time word counts, reading hours, and timeline health.", "example": "arcanum hub"},
        ],
        extension_guide="""Launch Studio Hub on custom port:
```bash
arcanum hub --port 8085
```""",
        advisory_guidance=[
            {"pattern": "Port 8080 already bound by another process", "option_a": "Automatically increment to next available port (e.g. 8081)", "option_b": "Export standalone static HTML dashboard file", "option_c": "Launch desktop GTK window instead of web hub"},
        ],
    ),

    "zen_studio": EngineSpec(
        name="zen_studio",
        category=EngineCategory.CORE,
        title="Zen Drafting Studio",
        description="Distraction-free typewriter drafting cockpit with in-situ lore drawer and beat tracker",
        module_name="lib.zen_studio",
        cli_command="studio",
        aliases=["zen", "zen-studio", "editor"],
        studio_tab="Editor",
        logic_documentation="Zero-dependency, single-file offline HTML5 typewriter drafting environment featuring dark/sepia/light themes, live reading/speech telemetry, in-situ world lore drawer, and LocalStorage autosave.",
        scientific_logic="""1. Typewriter Scroll & Focus Ergonomics:
   Maintains active typing line centered vertically in viewport (50% screen height), eliminating neck strain.

2. In-Situ Lore Split Drawer:
   Allows instant full-text search across World Bible dossiers without breaking drafting flow or switching windows.

3. Offline LocalStorage Autosave:
   Saves buffer on every keystroke to browser LocalStorage with 1-click Markdown download backup.""",
        why_this_way="Cluttered word processors with hundreds of toolbars distract authors from flow state drafting. Zen Studio strips away all distractions while keeping lore reference at your fingertips.",
        worldbuilding_relevance="Allows writers to search character dossiers and magic rules without breaking drafting flow.",
        storytelling_relevance="Provides live chapter word counts and reading time estimates while drafting.",
        writing_relevance="Delivers a distraction-free, pure typewriter focus environment with 100% offline privacy.",
        subfeatures=[
            {"name": "Typewriter Mode", "rule": "Keeps active line centered with distraction-free dark/sepia themes.", "example": "arcanum studio Manuscript/01_Chapter.md"},
            {"name": "In-Situ Lore Drawer", "rule": "Slide-out drawer displaying character and location infoboxes.", "example": "arcanum studio Manuscript/ -w World/"},
        ],
        extension_guide="""Launch Zen Studio from CLI:
```bash
arcanum studio Manuscript/ -w World/
```""",
        advisory_guidance=[
            {"pattern": "Drafting in Zen Studio with unsaved local buffer changes", "option_a": "Auto-save changes to browser LocalStorage and disk", "option_b": "Download standalone Markdown export file", "option_c": "Discard local buffer and restore canonical disk state"},
        ],
    ),

    "ambient": EngineSpec(
        name="ambient",
        category=EngineCategory.CRAFT,
        title="Ambient Focus & Binaural Beats",
        description="Local offline sound synthesis for deep writing focus (binaural beats, rain, fire, library)",
        module_name="lib.ambient",
        cli_command="ambient",
        aliases=["ambient", "binaural", "focus-sound"],
        studio_tab="Tools",
        logic_documentation="Synthesizes pure offline procedural soundscapes using Python standard library and Web Audio API: brown noise, pink noise, binaural alpha/theta waves, rain, fireplace, and quiet library ambiance.",
        scientific_logic="""1. Procedural Noise Synthesis:
   - Brown Noise: Integrated white noise with $1/f^2$ spectral power density (deep soothing rumble for concentration).
   - Pink Noise: $1/f$ power density (balanced acoustic masking).

2. Binaural Beats Neuromodulation:
   Plays carrier frequency $f_c = 220\\text{ Hz}$ in left ear and $f_c + \\Delta f$ in right ear:
   - Alpha Waves ($\\Delta f = 10\\text{ Hz}$): Relaxed cognitive alertness and flow state.
   - Theta Waves ($\\Delta f = 6\\text{ Hz}$): Deep creative visualization and associative ideation.
   - Gamma Waves ($\\Delta f = 40\\text{ Hz}$): High-intensity analytical problem solving.""",
        why_this_way="Streaming ambient audio from YouTube or Spotify leaks privacy and requires internet. Procedural Web Audio synthesis runs 100% offline with zero bandwidth.",
        worldbuilding_relevance="Creates deep auditory immersion matching the environment being drafted.",
        storytelling_relevance="Assists authors in entering deep flow states for focused writing sessions.",
        writing_relevance="100% offline audio generator requiring no internet or external media files.",
        subfeatures=[
            {"name": "Binaural Beat Synthesizer", "rule": "Generates real-time 40Hz Gamma and 10Hz Alpha waves for deep focus.", "example": "arcanum ambient --binaural alpha"},
            {"name": "Procedural Soundscapes", "rule": "Web Audio synthesis of rain on parchment, crackling hearth, and library.", "example": "arcanum ambient rain"},
        ],
        extension_guide="""Play ambient focus audio:
```bash
arcanum ambient library --volume 0.7
```""",
        advisory_guidance=[
            {"pattern": "Audio playback requested in headless terminal environment", "option_a": "Generate WAV audio file for external local media player", "option_b": "Launch Web Audio synthesis in browser Studio Hub", "option_c": "Display visual Pomodoro focus timer without sound"},
        ],
    ),

    "portfolio": EngineSpec(
        name="portfolio",
        category=EngineCategory.CRAFT,
        title="Portfolio & Drafting Velocity",
        description="Multi-manuscript word count tracker, sprint pacing, and catalog overview dashboard",
        module_name="lib.portfolio",
        cli_command="portfolio",
        aliases=["portfolio", "catalog", "series-overview"],
        studio_tab="Overview",
        logic_documentation="Aggregates multi-book catalog analytics, lifetime drafting velocity, release pipeline Gantt milestones, and writing streak heatmaps.",
        scientific_logic="""1. Portfolio Multi-Book Velocity Aggregator:
   Aggregates total output across all series volumes:
   $$\\text{Total Words} = \\sum_{i=1}^M W_i, \\quad \\text{Lifetime Velocity} = \\frac{\\text{Total Words}}{\\text{Days Elapsed}}$$
   Forecasts completion dates based on 30-day moving average velocity.""",
        why_this_way="Authors managing multi-book series or shared universes need high-altitude catalog visibility over release pipelines.",
        worldbuilding_relevance="Tracks master lore integration across multi-book shared universes.",
        storytelling_relevance="Monitors series-level narrative arcs and production schedules.",
        writing_relevance="Celebrates daily word count milestones and sustains creative momentum.",
        subfeatures=[
            {"name": "Catalog Analytics Overview", "rule": "Displays word count, chapter counts, and completion percentages for all manuscripts.", "example": "arcanum portfolio Manuscripts/"},
            {"name": "Drafting Velocity Forecast", "rule": "Projects series completion milestones based on 30-day moving average.", "example": "arcanum portfolio Manuscripts/ --forecast"},
        ],
        extension_guide="""Run portfolio analysis:
```bash
arcanum portfolio Manuscripts/ --html dist/portfolio.html
```""",
        advisory_guidance=[
            {"pattern": "Drafting velocity lull detected (>14 days inactive)", "option_a": "Schedule a 15-minute low-pressure writing sprint", "option_b": "Switch focus to worldbuilding lore or character sketches", "option_c": "Acknowledge planned creative rest period"},
        ],
    ),
}

__all__ = ["ENGINES"]
