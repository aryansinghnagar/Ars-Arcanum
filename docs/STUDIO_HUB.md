# Ars Arcanum — Sovereign Studio Desktop Hub Guide

> `arcanum hub` · **v4.4.0 — Granular Scope & Telemetry Cockpit** · 100% Offline · Zero-pip

---

## Overview

The **Sovereign Studio Desktop Hub** is a unified telemetry cockpit for your entire Ars Arcanum writing project. It aggregates real-time data from all 55+ craft engines — chapters, lore entities, timeline events, paradox alerts, structural pacing harmony, and the **Granular Scope Cockpit** — into a single responsive offline HTML5 dashboard accessible from your browser.

The hub features a persistent **Header Scope Bar** with quick targeting presets (`Active Project`, `Whole Book`, `Ch 1-5`, `Act 1`, `Custom...`) and an **Interactive Modal Engine Runner** that lets you execute any craft engine directly from the browser on your selected scope, complete with streaming diagnostic output.

The hub runs as an embedded local HTTP server using Python's standard library `http.server`, requires no external pip packages, and generates fully self-contained CSP-compliant HTML that never makes external network requests.

---

## Quick Start

```bash
# Open the Studio Hub for a Cosmos project directory
arcanum hub /path/to/My-Cosmos

# Use the current directory as project root
arcanum hub

# Custom port
arcanum hub /path/to/My-Cosmos --port 8765

# Export a single-file static HTML snapshot (no server)
arcanum hub /path/to/My-Cosmos --export-static ./hub-snapshot.html

# Print hub data as JSON (headless / CI mode)
arcanum hub /path/to/My-Cosmos --json

# Start the server without opening a browser
arcanum hub /path/to/My-Cosmos --no-browser
```

---

## CLI Reference

```
arcanum hub [TARGET] [OPTIONS]
arcanum dashboard [...]
arcanum gui-web [...]
arcanum studio-hub [...]

Arguments:
  TARGET                 Project directory (Cosmos root). Defaults to current directory.

Options:
  --port PORT            Port to bind the local HTTP server (default: 8749).
  --host HOST            Hostname to bind (default: 127.0.0.1).
  --no-browser           Start the server but do not open the system browser.
  --export-static FILE   Export a self-contained offline HTML snapshot and exit.
  --json                 Print hub telemetry data as JSON and exit (no server).
  -h, --help             Show this help message.
```

---

## Dashboard Panels

### 🎯 Scope Cockpit & Target Selector
Header-mounted scope controller allowing authors to select specific books, chapter ranges (`1-5`, `ch01..ch05`), and scene slices. Provides quick presets (`Active Project`, `Whole Book`, `Ch 1-5`, `Act 1`, `Custom...`) and displays a live telemetry pill badge summarizing active targets.

### ⚡ Interactive Engine Runner Modal
Launch any of the 55+ craft engines directly from the browser on the currently active scope. Inspect live streaming stdout/stderr diagnostics without switching to a terminal.

### 📖 Chapter Word-Count Telemetry
Live per-chapter word count bars showing total manuscript progress. Scans all `*.md` files recursively under any `Draft-*/` folder structure.

### 🏛️ Lore Entity Inventory
Entity counts by category (Characters, Factions, Places, Magic, Bestiary, Technology, Religions, Languages) parsed from sub-directory names in your World Bible.

### 🕰️ Timeline & Paradox Alerts
Event count and any detected bilocation paradoxes from `@time:` directives across all chapter scenes. Paradoxes are highlighted in amber as action items.

### 📐 Structural Pacing Harmony
Bar chart showing chapter word counts as a pacing curve overlay on a three-act structure model. Helps visualize tension rises and act breaks visually.

---

## REST API

The embedded local server exposes a lightweight REST API for programmatic integration:

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Full interactive HTML dashboard |
| `GET` | `/api/hub` | Complete JSON telemetry bundle |
| `GET` | `/api/scope` | Active session scope configuration and resolved counts |
| `POST` | `/api/scope` | Update session target scope (`chapter`, `scene`, `book`, `world`, `lore`) |
| `POST` | `/api/engine/run` | Execute craft engine asynchronously on active scope with captured output |
| `GET` | `/api/chapters` | Chapter list with word counts |
| `GET` | `/api/lore` | Lore entity category summary |
| `GET` | `/api/timeline` | Timeline events and paradox summary |
| `POST` | `/api/refresh` | Re-scan project directory and return fresh data |

### Example API call

```bash
# Get current hub data
curl http://127.0.0.1:8749/api/hub | python3 -m json.tool

# Update active session scope to Chapters 1-5
curl -X POST http://127.0.0.1:8749/api/scope -d '{"chapter": "1-5"}'

# Execute Pacing engine on the active scope
curl -X POST http://127.0.0.1:8749/api/engine/run -d '{"engine": "pacing"}'
```

---

## Static Export

The `--export-static` mode generates a single self-contained offline HTML file with all data baked into embedded JavaScript. This file can be shared, archived, or opened offline without a running server:

```bash
arcanum hub /path/to/My-Cosmos --export-static ./project-status.html
```

The exported HTML declares a strict Content Security Policy:
```
default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;
```
No external CDN scripts, remote fonts, or network requests are ever made.

---

## JSON / Headless Mode

The `--json` flag is designed for CI pipelines, shell scripting, and integration with external monitoring tools:

```bash
arcanum hub /path/to/My-Cosmos --json
```

Output structure:
```json
{
  "project_name": "Aethelgard",
  "total_chapters": 12,
  "total_words": 84210,
  "lore_entities": {"Characters": 8, "Places": 5, "Magic": 3},
  "timeline_events": 24,
  "paradox_count": 0,
  "pacing_harmony": 0.87,
  "generated_at": "2026-09-21T21:00:00"
}
```

---

## Engine Registration

The Studio Hub is registered in `scripts/lib/registry.py` as `"studio_hub"`:

```python
"studio_hub": EngineSpec(
    name="studio_hub",
    module="scripts.lib.studio_hub",
    commands=["hub", "dashboard", "gui-web", "studio-hub"],
    description="Sovereign Studio Desktop Hub & Telemetry Cockpit",
)
```

---

## Architecture Notes

- **Zero external dependencies**: Uses only `http.server`, `threading`, `json`, `pathlib`, `datetime`, and `socket` from the Python standard library.
- **Atomic project scan**: All filesystem reads complete before the first browser response; no concurrent filesystem mutations.
- **CSP-compliant HTML**: All generated HTML passes strict offline Content Security Policy with no inline `<script src>` or `<link rel=stylesheet href>` external references.
- **Thread safety**: `SovereignStudioHandler.data` and `SovereignStudioHandler.project_dir` are class-level attributes set before the server thread starts; `/api/refresh` re-scans synchronously and atomically replaces the class attribute.

---

## Architectural Decision Records

- **ADR-063**: Sovereign Studio Hub & Unified Offline Local Webview Architecture — see [`decisions.md`](../decisions.md).

---

## Theoretical Foundations & Reference Sources

### Primary Treatises & Dashboard Interface Design
- **Few, Stephen (2006)**. *Information Dashboard Design: The Effective Visual Communication of Data*. O'Reilly Media. ISBN: 978-0596100162.  
  *Foundational principles for high-density visual cockpits, single-screen situational awareness, and eliminating chartjunk.*
- **Shneiderman, Ben (1986)**. *Designing the User Interface: Strategies for Effective Human-Computer Interaction*. Addison-Wesley.  
  *Establishes the Eight Golden Rules of Interface Design, direct manipulation paradigms, and informative feedback.*
- **Nielsen, Jakob (1994)**. "Enhancing the Explanatory Power of Usability Heuristics", *Proceedings of the SIGCHI Conference on Human Factors in Computing Systems (CHI '94)*, pp. 152–158. [DOI: 10.1145/191666.191729](https://doi.org/10.1145/191666.191729).  
  *Authoritative heuristic evaluation framework ensuring visibility of system status, user control, and error prevention.*

### Offline Web Architecture & Zero-Trust Security
- **Fielding, Roy Thomas (2000)**. *Architectural Styles and the Design of Network-based Software Architectures*. Doctoral dissertation, University of California, Irvine. [UC Irvine eScholarship](https://escholarship.org/uc/item/52m7v0j7).  
  *Foundational derivation of the REST architectural style and stateless representation interchange over HTTP.*
- **World Wide Web Consortium (W3C) (2016)**. *Content Security Policy Level 3*. W3C Recommendation. [W3C CSP Spec](https://www.w3.org/TR/CSP3/).  
  *Normative security standard defining strict sandboxing (`default-src 'none'`) for sovereign offline applications.*

### Beyond the Engine: Advanced Telemetry Frontiers
- **Server-Sent Events (SSE) Live Telemetry Streaming**: Zero-dependency unidirectional push pipelines delivering real-time word count updates without polling.
- **Micro-Frontend Architecture for Custom Lore Modules**: Decoupled Web Component plugin architecture allowing author-built custom craft engines to dock into the main hub grid.
- **Biometric Stress & Typing Velocity Telemetry**: Visualizing authorial typing cadence, pause lengths, and drafting bursts alongside manuscript structure.

