# Ars Arcanum — Sovereign Studio Desktop Hub Guide

> `arcanum hub` · **v0.1.0 — Granular Scope & Telemetry Cockpit** · 100% Offline · Zero-pip · Hardened REST Security

---

## Overview

The **Sovereign Studio Desktop Hub** is a unified telemetry cockpit for your entire Ars Arcanum writing project. It aggregates real-time data from all 47 craft and simulation engines — chapters, lore entities, timeline events, paradox alerts, structural pacing harmony, and the **Granular Scope Cockpit** — into a single responsive offline HTML5 dashboard accessible from your browser.

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
Launch any registered craft engine directly from the browser on the currently active scope. Inspect live streaming stdout/stderr diagnostics without switching to a terminal.

### 📖 Chapter Word-Count Telemetry
Live per-chapter word count bars showing total manuscript progress. Scans all `*.md` files recursively under any `Draft-*/` folder structure.

### 🏛️ Lore Entity Inventory
Entity counts by category (Characters, Factions, Places, Magic, Bestiary, Technology, Religions, Languages) parsed from sub-directory names in your World Bible.

### 🕰️ Timeline & Paradox Alerts
Event count and any detected bilocation paradoxes from `@time:` directives across all chapter scenes. Paradoxes are highlighted in amber as action items.

### 📐 Structural Pacing Harmony
Bar chart showing chapter word counts as a pacing curve overlay on a three-act structure model. Helps visualize tension rises and act breaks visually.

---

## REST API & Security Hardening

The embedded local server exposes a hardened REST API for programmatic integration:

| Method | Endpoint | Description | Security Controls |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Full interactive HTML dashboard | Strict CSP (`default-src 'none'`) |
| `GET` | `/api/hub` | Complete JSON telemetry bundle | Read-only |
| `GET` | `/api/scope` | Active session scope configuration and resolved counts | Read-only |
| `POST` | `/api/scope` | Update session target scope (`chapter`, `scene`, `book`, `world`, `lore`) | Strict Origin & Host match |
| `POST` | `/api/engine/run` | Execute craft engine asynchronously on active scope with captured output | Strict Origin match, `ENGINE_ALLOWLIST`, Mutex lock |
| `POST` | `/api/chapter/save` | Atomically save updated Markdown chapter prose and evict DAL cache | Strict Origin match, path traversal validation, `.md` extension check, atomic write |
| `GET` | `/api/chapters` | Chapter list with word counts | Read-only |
| `GET` | `/api/lore` | Lore entity category summary | Read-only |
| `GET` | `/api/timeline` | Timeline events and paradox summary | Read-only |
| `POST` | `/api/refresh` | Re-scan project directory and return fresh data | Strict Origin & Host match |

### Security Invariants

1. **Origin Verification (`_validate_origin`)**: State-modifying endpoints (`POST`) require an `Origin` header matching the bound `Host` header (supporting both IPv4 `127.0.0.1` / `localhost` and IPv6 `::1` / `[::1]`). Requests with `null` or mismatched foreign origins return HTTP `403 Forbidden`.
2. **Engine Allowlist (`ENGINE_ALLOWLIST`)**: `POST /api/engine/run` restricts execution to an explicit set of registered craft engines. Non-allowlisted engine names return HTTP `400 Bad Request`.
3. **Path Traversal & Extension Defense**: `POST /api/chapter/save` enforces strict canonical path containment within the project root (`Path.resolve().is_relative_to(project_dir)`), rejects directory traversal tokens (`..`), and requires `.md` file extensions.
4. **Atomic Persistence & Cache Eviction**: Saves use `atomic_write()` and immediately invoke `get_dal().evict(resolved_path)` to ensure zero cache staleness across engines.
5. **Thread Safety & Mutex**: Engine execution runs under a dedicated `threading.Lock()` to prevent race conditions and concurrent process conflicts.

### Example API call

```bash
# Get current hub data
curl http://127.0.0.1:8749/api/hub | python3 -m json.tool

# Update active session scope to Chapters 1-5
curl -X POST http://127.0.0.1:8749/api/scope -H "Origin: http://127.0.0.1:8749" -d '{"chapter": "1-5"}'

# Execute Pacing engine on the active scope
curl -X POST http://127.0.0.1:8749/api/engine/run -H "Origin: http://127.0.0.1:8749" -d '{"engine": "pacing"}'

# Save updated chapter prose atomically
curl -X POST http://127.0.0.1:8749/api/chapter/save -H "Origin: http://127.0.0.1:8749" -d '{"path": "Book-01/01_Act_I/01_Chapter_01.md", "content": "# Chapter 1\n\nThe obsidian spire loomed..."}'
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
  "generated_at": "2026-10-06T12:00:00"
}
```

---

## Architecture & Accessibility Notes

- **Zero external dependencies**: Uses only `http.server`, `threading`, `json`, `pathlib`, `datetime`, and `socket` from the Python standard library.
- **Atomic project scan**: All filesystem reads complete before the first browser response; no concurrent filesystem mutations.
- **CSP-compliant HTML**: All generated HTML passes strict offline Content Security Policy with no inline `<script src>` or `<link rel=stylesheet href>` external references.
- **Thread safety**: `SovereignStudioHandler.data` and `SovereignStudioHandler.project_dir` are class-level attributes set before the server thread starts; `/api/refresh` re-scans synchronously and atomically replaces the class attribute.
- **ARIA & Assistive Technology Compliance**:
  - Full semantic landmark hierarchy (`role="navigation"`, `role="main"`, `role="banner"`, `role="toolbar"`).
  - WAI-ARIA tab navigation pattern (`role="tablist"`, `role="tab"`, `role="tabpanel"`, `aria-selected`, `aria-controls`).
  - Screen reader execution console with live region telemetry (`aria-live="polite"`).
  - Accessible modal dialogs (`role="dialog"`, `aria-modal="true"`, `aria-labelledby`, global keyboard `Escape` dismissal).
  - High-contrast WCAG 2.1 AA verified palettes across Dark, Sepia, and Light themes.

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
