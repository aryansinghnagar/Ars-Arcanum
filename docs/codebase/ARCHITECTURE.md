# Architecture

## Core Sections (Required)

### 1) Architectural Style

- Primary style: Layered Domain Engine & Presentation Modular Architecture with Universal Knowledge Graph Mesh
- Why this classification: Decouples pure standard-library simulation and craft engines (`scripts/lib/`) from presentation layers (`ui_gtk3`, `studio_hub`, `zen_studio`, `story_canvas`, `cli`) and data persistence formats (Markdown, YAML frontmatter, SQLite).
- Primary constraints:
  1. 100% offline air-gapped sovereign execution (zero external pip packages or cloud telemetry).
  2. POSIX atomic file safety (`atomic_write` and `ArcanumLock`).
  3. Strict mathematical determinism (zero unseeded randomness or probabilistic hallucinations).
  4. Non-blocking advisory-first validation (Path A: Hard Realism, Path B: Speculative Trope, Path C: Author Sovereignty).

### 2) System Flow

```text
[Author Input / CLI / GUI] -> [CLI / Controller / Dispatcher] -> [Registry & Validation Guard] -> [47 Deterministic Domain Engines] -> [Atomic POSIX File I/O & Presentation Engine]
```

1. **Invocation**: Author triggers action via POSIX wrapper (`scripts/arcanum`), Python CLI (`scripts/lib/cli.py`), Studio Hub (`studio_hub.py`), Zen Studio (`zen_studio.py`), or GTK3 Desktop GUI (`scripts/arcanum_app.py`).
2. **Sanitization & Dispatch**: `_bootstrap.py` and `cli.py` validate paths (`^[A-Za-z0-9_-]+$`) and route arguments to the registered engine.
3. **Execution**: Engine computes deterministic mathematical models (e.g. `astrophysics`, `climate`, `resonance`, `causality`, `tactical_sim`).
4. **Advisory Synthesis**: Invariants evaluate anomalies and return non-blocking advisory options with confidence scores.
5. **Persistence & Render**: Changes commit via `atomic_write()` and render as interactive offline HTML (with strict CSP), Markdown, or CLI output.

### 3) Layer/Module Responsibilities

| Layer or module | Owns | Must not own | Evidence |
|-----------------|------|--------------|----------|
| Bootstrap & Safety (`_bootstrap.py`, `lockfile.py`) | Atomic file write primitives, concurrency locks, regex token sanitization | Domain business logic, UI state | `scripts/lib/_bootstrap.py#L1-L70` |
| Scope & Context Resolution (`scope.py`) | Unified scope expression parsing, chapter/scene range tokenizing, context altitude resolution | Heavy computational simulation loops | `scripts/lib/scope.py#L1-L120` |
| Lifecycle & Vault Engines (`backup.py`, `restore.py`, `snapshot.py`) | Pure-Python tarfile archive creation, SHA-256 manifests, GPG symmetric encryption, restore validation | Direct shell dependencies, UI rendering | `scripts/lib/backup.py#L1-L150`, `scripts/lib/restore.py#L1-L150` |
| Registry (`registry.py`) | Engine metadata, CLI aliases, documentation, subfeature catalog across 47 engines | Heavy computational loops | `scripts/lib/registry.py#L1-L100` |
| Domain Engines (`astrophysics.py`, `economy.py`, `ecology.py`, `resonance.py`, `causality.py`, `vault_search.py`, etc.) | Mathematical invariants, graph DAGs, simulation calculations | GUI widgets, unsanitized file I/O | `scripts/lib/resonance.py#L1-L100`, `scripts/lib/astrophysics.py#L1-L100` |
| Presentation (`ui_gtk3/`, `studio_hub.py`, `zen_studio.py`, `story_canvas.py`) | User interaction, event loops, rendering, HTML/CSS generation | Direct unbuffered disk writes | `scripts/lib/ui_gtk3/window.py#L1-L100` |

### 4) Reused Patterns

| Pattern | Where found | Why it exists |
|---------|-------------|---------------|
| Atomic File Write (`atomic_write`) | `scripts/lib/_bootstrap.py` | Guarantees zero corrupted files on crash or power failure with descriptor cleanup |
| Cross-Platform Lockfile (`ArcanumLock`) | `scripts/lib/lockfile.py` | Abstracted `fcntl.flock` (POSIX) and `msvcrt.locking` (Windows) concurrency control |
| Granular Target Scoping & Shorthands | `scripts/lib/scope.py` | Universal integer range expansion (`1-5`, `ch01..ch05`) and context-aware target resolution |
| Bi-Directional Graph & Causal DAG | `scripts/lib/causality.py`, `scripts/lib/resonance.py` | Evaluates multi-hop causality, Novikov consistency, and cross-domain resonance |
| 3-Color DFS Cycle Detection | `scripts/lib/ecology.py` | Detects arbitrary N-tier circular predation loops across food webs |
| Inverted Index & SQLite FTS5 / TF-IDF | `scripts/lib/vault_search.py` | Delivers sub-millisecond local semantic lore search without cloud vector APIs |
| Non-Repeating LRU History Cycling | `scripts/lib/tips.py` | Ensures novel craft tip rotation without immediate repetition |

### 5) Known Architectural Risks

- Cross-platform file locking differences: POSIX `fcntl.flock` vs Windows `msvcrt.locking` handled via unified `ArcanumLock` fallback abstraction (`scripts/lib/lockfile.py`).
- HTML Report Content Security: All generated HTML interfaces enforce strict `default-src 'none'` CSP to guarantee complete offline air-gapping.

### 6) Evidence

- `scripts/lib/_bootstrap.py#L1-L70`
- `scripts/lib/scope.py#L1-L120`
- `scripts/lib/backup.py#L1-L180`
- `scripts/lib/restore.py#L1-L180`
- `scripts/lib/snapshot.py#L1-L120`
- `scripts/lib/registry.py#L1-L120`
- `scripts/lib/cli.py#L1-L100`
- `scripts/lib/astrophysics.py#L457-L505`
- `scripts/lib/economy.py#L280-L375`
- `scripts/lib/ecology.py#L195-L260`
- `scripts/lib/resonance.py#L1-L150`
- `scripts/lib/vault_search.py#L1-L100`
- `scripts/lib/tips.py#L1-L120`
