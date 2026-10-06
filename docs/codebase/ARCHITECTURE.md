# Architecture

## Core Sections (Required)

### 1) Architectural Style

- Primary style: Layered Domain Engine & Presentation Modular Architecture with Universal Knowledge Graph Mesh
- Why this classification: Decouples pure standard-library simulation and craft engines (`scripts/lib/`) from presentation layers (`ui_gtk3`, `studio_hub`, `zen_studio`, `story_canvas`, `cli`), engine metadata domain specifications (`scripts/lib/registry_specs/`), and data persistence formats (Markdown, YAML frontmatter, SQLite).
- Primary constraints:
  1. 100% offline air-gapped sovereign execution (zero external pip packages or cloud telemetry for core engines).
  2. POSIX/Windows atomic file safety (`atomic_write` and `ArcanumLock`).
  3. Strict mathematical determinism (zero unseeded randomness or probabilistic hallucinations).
  4. Non-blocking advisory-first validation (Path A: Hard Realism, Path B: Speculative Trope, Path C: Author Sovereignty).
  5. Module size bounds: `<800 lines/file` engineering contract enforced across source files.

### 2) System Flow

```text
[Author Input / CLI / GUI] -> [CLI / Controller / Dispatcher] -> [Registry & Validation Guard] -> [47 Deterministic Domain Engines] -> [Atomic File I/O & Presentation Engine]
```

1. **Invocation**: Author triggers action via POSIX wrapper (`scripts/arcanum`), Python CLI (`scripts/lib/cli.py` or entry points `arcanum` / `ars-arcanum`), Studio Hub (`studio_hub.py`), Zen Studio (`zen_studio.py`), or GTK3 Desktop GUI (`scripts/arcanum_app.py`).
2. **Sanitization & Dispatch**: `_bootstrap.py` and `cli.py` validate paths (`^[A-Za-z0-9_-]+$` plus Windows device name rejections) and route arguments to the registered engine.
3. **Execution**: Engine computes deterministic mathematical models (e.g. `astrophysics`, `climate`, `resonance`, `causality`, `tactical_sim`).
4. **Advisory Synthesis**: Invariants evaluate anomalies and return non-blocking advisory options with confidence scores.
5. **Persistence & Render**: Changes commit via `atomic_write()` and render as interactive offline HTML (with strict CSP), Markdown, or CLI output.

### 3) Layer/Module Responsibilities

| Layer or module | Owns | Must not own | Evidence |
|-----------------|------|--------------|----------|
| Bootstrap & Safety (`_bootstrap.py`, `lockfile.py`) | Atomic file write primitives, concurrency locks, regex token sanitization, Windows reserved device checks | Domain business logic, UI state | [`scripts/lib/_bootstrap.py#L1-L115`](file:///scripts/lib/_bootstrap.py#L1-L115) |
| Data Access Layer (`data_access.py`) | Thread-safe cached vault reader, AST frontmatter parsing, chapter/entity queries with mtime invalidation | Presentation rendering, business mutations | [`scripts/lib/data_access.py#L1-L200`](file:///scripts/lib/data_access.py#L1-L200) |
| Scope & Context Resolution (`scope.py`) | Unified scope expression parsing, chapter/scene range tokenizing, context altitude resolution | Heavy computational simulation loops | [`scripts/lib/scope.py#L1-L120`](file:///scripts/lib/scope.py#L1-L120) |
| Lifecycle & Vault Engines (`backup.py`, `restore.py`, `snapshot.py`) | Pure-Python tarfile archive creation, SHA-256 manifests, GPG symmetric encryption, restore non-empty directory defenses | Direct shell dependencies, UI rendering | [`scripts/lib/backup.py#L1-L150`](file:///scripts/lib/backup.py#L1-L150), [`scripts/lib/restore.py#L1-L150`](file:///scripts/lib/restore.py#L1-L150) |
| Registry Abstractions (`registry_base.py`) | `EngineCategory`, `EngineSpec`, `BaseCraftEngine` contract types (<200 lines) | Implementation logic, CLI dispatch | [`scripts/lib/registry_base.py#L80-L180`](file:///scripts/lib/registry_base.py#L80-L180) |
| Domain Engine Specs (`registry_specs/`) | Modular static engine metadata partitioned across 7 domains (<400 lines each) | Runtime state, CLI query methods | [`scripts/lib/registry_specs/__init__.py#L1-L30`](file:///scripts/lib/registry_specs/__init__.py#L1-L30) |
| Craft Tip Catalogs (`tips_catalog/`) | Modular static craft tips partitioned across 6 domains (<60 lines each) | Runtime querying, CLI dispatch | [`scripts/lib/tips_catalog/__init__.py#L1-L30`](file:///scripts/lib/tips_catalog/__init__.py#L1-L30) |
| Registry Facade (`registry.py`) | Engine catalog discovery, dynamic plugin discovery, terminal doc formatting (<600 lines) | Monolithic 2400+ line static dictionaries | [`scripts/lib/registry.py#L1-L80`](file:///scripts/lib/registry.py#L1-L80) |
| Universal Resonance Modules (`resonance.py`, `resonance_data.py`, `resonance_template.py`) | 5-pillar knowledge graph, causal cascades, metaphorical bridges, offline HTML visualizer (<650 lines/file) | Unsanitized file I/O, cloud network calls | [`scripts/lib/resonance.py#L1-L100`](file:///scripts/lib/resonance.py#L1-L100) |
| Macroeconomic Modules (`economy.py`, `economy_data.py`, `economy_template.py`, `economy_trade.py`) | Macroeconomic validation, Fisher equation, coin debasement, trade route graph centrality, offline HTML flow maps (<780 lines/file) | Unbuffered direct disk writes | [`scripts/lib/economy.py#L1-L100`](file:///scripts/lib/economy.py#L1-L100) |
| Domain Engines (`astrophysics.py`, `ecology.py`, `causality.py`, `vault_search.py`, etc.) | Mathematical invariants, graph DAGs, simulation calculations | GUI widgets, unsanitized file I/O | [`scripts/lib/astrophysics.py#L1-L100`](file:///scripts/lib/astrophysics.py#L1-L100) |
| Presentation (`ui_gtk3/`, `studio_hub.py`, `zen_studio.py`, `story_canvas.py`) | User interaction, event loops, rendering, HTML/CSS generation with strict CSP | Direct unbuffered disk writes | [`scripts/lib/ui_gtk3/window.py#L1-L100`](file:///scripts/lib/ui_gtk3/window.py#L1-L100) |

### 4) Reused Patterns

| Pattern | Where found | Why it exists |
|---------|-------------|---------------|
| Atomic File Write (`atomic_write`) | [`scripts/lib/_bootstrap.py`](file:///scripts/lib/_bootstrap.py) | Guarantees zero corrupted files on crash or power failure with descriptor cleanup |
| Cross-Platform Lockfile (`ArcanumLock`) | [`scripts/lib/lockfile.py`](file:///scripts/lib/lockfile.py) | Abstracted `fcntl.flock` (POSIX) and `msvcrt.locking` (Windows) concurrency control with explicit seek to 0 |
| Centralized Cached Data Access | [`scripts/lib/data_access.py`](file:///scripts/lib/data_access.py) | Eliminates redundant disk reads and YAML AST parsing via thread-safe memoization with mtime invalidation |
| Granular Target Scoping & Shorthands | [`scripts/lib/scope.py`](file:///scripts/lib/scope.py) | Universal integer range expansion (`1-5`, `ch01..ch05`) and context-aware target resolution |
| Modular Domain Spec & Tip Aggregation | [`scripts/lib/registry_specs/`](file:///scripts/lib/registry_specs/), [`scripts/lib/tips_catalog/`](file:///scripts/lib/tips_catalog/) | Partitions engine specifications and tips into domain packages ensuring `<800 lines/file` maintainability |
| Bi-Directional Graph & Causal DAG | [`scripts/lib/causality.py`](file:///scripts/lib/causality.py), [`scripts/lib/resonance.py`](file:///scripts/lib/resonance.py), [`scripts/lib/resonance_data.py`](file:///scripts/lib/resonance_data.py) | Evaluates multi-hop causality, Novikov consistency, and cross-domain resonance |
| Trade Network Centrality & Gravity Model | [`scripts/lib/economy_trade.py`](file:///scripts/lib/economy_trade.py) | Models commercial choke points, degree/betweenness centrality, and bilateral trade flows |
| 3-Color DFS Cycle Detection | [`scripts/lib/ecology.py`](file:///scripts/lib/ecology.py) | Detects arbitrary N-tier circular predation loops across food webs |
| Inverted Index & SQLite FTS5 / TF-IDF | [`scripts/lib/vault_search.py`](file:///scripts/lib/vault_search.py) | Delivers sub-millisecond local semantic lore search without cloud vector APIs |
| Non-Repeating LRU History Cycling | [`scripts/lib/tips.py`](file:///scripts/lib/tips.py) | Ensures novel craft tip rotation without immediate repetition |

### 5) Known Architectural Risks

- Cross-platform file locking differences: POSIX `fcntl.flock` vs Windows `msvcrt.locking` handled via unified `ArcanumLock` fallback abstraction with explicit `os.lseek(fd, 0, os.SEEK_SET)`.
- HTML Report Content Security: All generated HTML interfaces enforce strict `default-src 'none'` CSP to guarantee complete offline air-gapping.
- Remaining oversized engine modules (`scope.py`, `astrophysics.py`): Scheduled for modularization in `docs/ROADMAP.md` (`resonance.py` and `economy.py` successfully modularized).

### 6) Evidence

- [`scripts/lib/_bootstrap.py#L1-L115`](file:///scripts/lib/_bootstrap.py#L1-L115)
- [`scripts/lib/data_access.py#L1-L200`](file:///scripts/lib/data_access.py#L1-L200)
- [`scripts/lib/registry.py#L1-L80`](file:///scripts/lib/registry.py#L1-L80)
- [`scripts/lib/registry_base.py#L1-L80`](file:///scripts/lib/registry_base.py#L1-L80)
- [`scripts/lib/registry_specs/__init__.py#L1-L30`](file:///scripts/lib/registry_specs/__init__.py#L1-L30)
- [`scripts/lib/resonance.py#L1-L100`](file:///scripts/lib/resonance.py#L1-L100)
- [`scripts/lib/resonance_data.py#L1-L100`](file:///scripts/lib/resonance_data.py#L1-L100)
- [`scripts/lib/economy.py#L1-L100`](file:///scripts/lib/economy.py#L1-L100)
- [`scripts/lib/economy_trade.py#L1-L100`](file:///scripts/lib/economy_trade.py#L1-L100)
- [`scripts/lib/scope.py#L1-L120`](file:///scripts/lib/scope.py#L1-L120)
- [`scripts/lib/backup.py#L1-L180`](file:///scripts/lib/backup.py#L1-L180)
- [`scripts/lib/restore.py#L1-L180`](file:///scripts/lib/restore.py#L1-L180)
- [`docs/ROADMAP.md#L1-L60`](file:///docs/ROADMAP.md#L1-L60)
