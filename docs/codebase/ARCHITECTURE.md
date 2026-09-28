# Architecture

## Core Sections (Required)

### 1) Architectural Style

- Primary style: Layered Domain Engine & Presentation Modular Architecture with Universal Knowledge Graph Mesh
- Why this classification: Decouples pure standard-library simulation and craft engines (`scripts/lib/`) from presentation layers (`ui_gtk3`, `ui_adw`, `studio_hub`, `zen_studio`, `cli`) and data persistence formats (Markdown, YAML, SQLite).
- Primary constraints:
  1. 100% offline air-gapped sovereign execution (zero external pip packages or telemetry).
  2. POSIX atomic file safety (`atomic_write` and `ArcanumLock`).
  3. Non-blocking advisory-first validation (Path A: Hard Realism, Path B: Speculative Trope, Path C: Author Sovereignty).

### 2) System Flow

```text
[Author Input / CLI / GUI / REST] -> [CLI / Controller / Dispatcher] -> [Registry & Validation Guard] -> [53 Domain & Craft Engines] -> [Atomic POSIX File I/O & Presentation Engine]
```

1. **Invocation**: Author triggers action via POSIX wrapper (`scripts/arcanum`), Python CLI (`scripts/lib/cli.py`), Studio Hub (`studio_hub.py`), or GTK3 Desktop GUI (`scripts/arcanum_app.py`).
2. **Sanitization & Dispatch**: `_bootstrap.py` and `cli.py` validate paths (`^[A-Za-z0-9_-]+$`) and route arguments to the registered engine.
3. **Execution**: Engine computes deterministic mathematical models (e.g. `astrophysics`, `climate`, `resonance`, `causality`).
4. **Advisory Synthesis**: Invariants evaluate anomalies and return non-blocking advisory options with confidence scores.
5. **Persistence & Render**: Changes commit via `atomic_write()` and render as interactive offline HTML (with strict CSP), Markdown, or CLI output.

### 3) Layer/Module Responsibilities

| Layer or module | Owns | Must not own | Evidence |
|-----------------|------|--------------|----------|
| Bootstrap & Safety (`_bootstrap.py`, `lockfile.py`) | Atomic file write primitives, concurrency locks, regex token sanitization | Domain business logic, UI state | `scripts/lib/_bootstrap.py#L1-L60` |
| Registry (`registry.py`) | Engine metadata, CLI aliases, documentation, subfeature catalog | Heavy computational loops | `scripts/lib/registry.py#L1-L100` |
| Domain Engines (`resonance.py`, `causality.py`, etc.) | Mathematical invariants, graph DAGs, simulation calculations | GUI widgets, unsanitized file I/O | `scripts/lib/resonance.py#L1-L100` |
| Presentation (`ui_gtk3/`, `studio_hub.py`, `zen_studio.py`) | User interaction, event loops, rendering, HTML/CSS generation | Direct unbuffered disk writes | `scripts/lib/ui_gtk3/window.py#L1-L100` |

### 4) Reused Patterns

| Pattern | Where found | Why it exists |
|---------|-------------|---------------|
| Atomic File Write (`atomic_write`) | `scripts/lib/_bootstrap.py` | Guarantees zero corrupted files on crash or power failure |
| Bi-Directional Graph & Causal DAG | `scripts/lib/causality.py`, `scripts/lib/resonance.py` | Evaluates multi-hop causality, Novikov consistency, and cross-domain resonance |
| Inverted Index & SQLite FTS5 | `scripts/lib/local_rag.py`, `scripts/lib/concordance.py` | Delivers sub-millisecond local semantic lore search without vector APIs |
| Non-Repeating LRU History Cycling | `scripts/lib/tips.py` | Ensures novel craft tip rotation without immediate repetition |

### 5) Known Architectural Risks

- Cross-platform file locking differences: POSIX `fcntl.flock` vs Windows `msvcrt.locking` handled via unified `ArcanumLock` fallback abstraction (`scripts/lib/lockfile.py`).
- HTML Report Content Security: All generated HTML interfaces enforce strict `default-src 'none'` CSP to guarantee complete offline air-gapping.

### 6) Evidence

- `scripts/lib/_bootstrap.py#L1-L60`
- `scripts/lib/registry.py#L1-L120`
- `scripts/lib/cli.py#L1-L100`
- `scripts/lib/resonance.py#L1-L150`
- `scripts/lib/tips.py#L1-L120`
