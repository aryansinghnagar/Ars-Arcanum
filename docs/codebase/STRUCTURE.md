# Codebase Structure

## Core Sections (Required)

### 1) Top-Level Map

| Path | Purpose | Evidence |
|------|---------|----------|
| `scripts/` | Main application entry points (`arcanum`, `arcanum_app.py`, `setup_arcanum.sh`, `verify.sh`) and Python package root (`__init__.py`) | [`scripts/arcanum`](file:///scripts/arcanum), [`scripts/arcanum_app.py`](file:///scripts/arcanum_app.py), [`scripts/__init__.py`](file:///scripts/__init__.py) |
| `scripts/lib/` | 47 sovereign deterministic domain engines, data access layer (`data_access.py`), universal scoping subsystem (`scope.py`), presentation modules, and bootstrap safety utilities | [`scripts/lib/registry.py`](file:///scripts/lib/registry.py), [`scripts/lib/data_access.py`](file:///scripts/lib/data_access.py), [`scripts/lib/registry_base.py`](file:///scripts/lib/registry_base.py), [`scripts/lib/scope.py`](file:///scripts/lib/scope.py), [`scripts/lib/_bootstrap.py`](file:///scripts/lib/_bootstrap.py) |
| `scripts/lib/registry_specs/` | Modular domain engine specifications partitioned across 7 craft and infrastructure domains | [`scripts/lib/registry_specs/domain_a_science.py`](file:///scripts/lib/registry_specs/domain_a_science.py), [`scripts/lib/registry_specs/__init__.py`](file:///scripts/lib/registry_specs/__init__.py) |
| `scripts/lib/tips_catalog/` | Modular craft tip catalog specifications partitioned across 6 craft domains and engine aliases (<60 lines/file) | [`scripts/lib/tips_catalog/domain_cosmology.py`](file:///scripts/lib/tips_catalog/domain_cosmology.py), [`scripts/lib/tips_catalog/__init__.py`](file:///scripts/lib/tips_catalog/__init__.py) |
| `scripts/lib/ui_gtk3/` | Modular PyGObject GTK3 desktop interface package (<800 lines/file) | [`scripts/lib/ui_gtk3/window.py`](file:///scripts/lib/ui_gtk3/window.py) |
| `docs/` | Comprehensive craft documentation, user guides, master engine encyclopedia, roadmap, and codebase architecture | [`docs/README.md`](file:///docs/README.md), [`docs/ENGINE_LOGIC_ENCYCLOPEDIA.md`](file:///docs/ENGINE_LOGIC_ENCYCLOPEDIA.md), [`docs/ROADMAP.md`](file:///docs/ROADMAP.md), [`docs/codebase/`](file:///docs/codebase/) |
| `tests/` | Exhaustive 960-test suite covering unit, integration, scoping, threat model, and benchmark tests | [`tests/test_*.py`](file:///tests/) |
| `templates/` | Standardized world bibles, demo cosmos (`Eldoria`), Obsidian plugins with SHA-256 manifest, and novelWriter project templates | [`templates/demo-cosmos/`](file:///templates/demo-cosmos/), [`templates/world-bible/`](file:///templates/world-bible/) |
| `configs/` | Deterministic plugin definitions, idiom dictionaries, LeechBlock rules, and core settings | [`configs/plugin_catalog.json`](file:///configs/plugin_catalog.json), [`configs/idioms.json`](file:///configs/idioms.json), [`configs/leechblock_arcanum_rules.json`](file:///configs/leechblock_arcanum_rules.json) |

### 2) Entry Points

- Main desktop GUI runtime entry: [`scripts/arcanum_app.py`](file:///scripts/arcanum_app.py)
- Unified CLI runtime dispatcher: [`scripts/lib/cli.py`](file:///scripts/lib/cli.py) / [`scripts/arcanum`](file:///scripts/arcanum) / registered entry points (`arcanum`, `ars-arcanum`)
- Studio Hub telemetry dashboard entry: [`scripts/lib/studio_hub.py`](file:///scripts/lib/studio_hub.py) (`arcanum hub`)
- Zen Drafting Studio entry: [`scripts/lib/zen_studio.py`](file:///scripts/lib/zen_studio.py) (`arcanum zen`)
- Story Canvas visual corkboard entry: [`scripts/lib/story_canvas.py`](file:///scripts/lib/story_canvas.py) (`arcanum canvas`)
- Selection mechanism: POSIX shell wrapper `scripts/arcanum` dispatches subcommands to `scripts/lib/cli.py` or bash fallback handlers.

### 3) Module Boundaries

| Boundary | What belongs here | What must not be here |
|----------|-------------------|------------------------|
| `scripts/lib/_bootstrap.py` & `fs_utils.py` | Atomic POSIX file I/O, regex token sanitization, Windows reserved device name guards (`CON`, `PRN`, `AUX`, `NUL`, etc.), lockfiles | Domain business logic, UI widgets |
| `scripts/lib/data_access.py` | Thread-safe memoized vault reader, frontmatter parser, and chapter/lore entity queries with `mtime` invalidation | Direct presentation rendering, business rules |
| `scripts/lib/registry_base.py` | Core `EngineSpec`, `EngineCategory`, and `BaseCraftEngine` contract types (<200 lines) | Individual engine metadata dictionaries |
| `scripts/lib/registry_specs/` | Pure static domain engine specifications across 7 domains (<400 lines each) | Runtime state, CLI query methods |
| `scripts/lib/tips_catalog/` | Pure static craft tips across 6 craft domains (<60 lines each) | Runtime querying, CLI dispatch |
| `scripts/lib/registry.py` | Authoritative 47-engine discovery matrix, dynamic plugin scanner, and doc formatting (<600 lines) | Monolithic 2400+ line static dictionaries |
| `scripts/lib/resonance.py`, `resonance_data.py`, `resonance_template.py` | Universal resonance mesh, 5-pillar knowledge graph, causal cascades, metaphorical bridges, and offline visualizer (<650 lines/file) | Direct unbuffered disk writes, network calls |
| `scripts/lib/economy.py`, `economy_data.py`, `economy_template.py`, `economy_trade.py` | Macroeconomic validator, Fisher equation simulation, commodity baskets, trade centrality, and offline flow maps (<780 lines/file) | Direct unbuffered disk writes |
| `scripts/lib/ui_gtk3/` | Presentation widgets, event handlers, and GTK rendering loops | Direct file system mutation (must delegate to controllers/engines) |
| Craft Simulation Engines (`astrophysics`, `climate`, `conlang`, `causality`, `vault_search`, etc.) | Pure Python mathematical simulations, deterministic models, advisory options | GTK/GUI imports, cloud network dependencies, unseeded PRNG |

### 4) Naming and Organization Rules

- File naming pattern: Lowercase snake_case (`astrophysics.py`, `vault_search.py`, `test_resonance.py`).
- Directory organization pattern: Layered architectural tiers (Root bootstrap $\to$ `scripts/lib/` engines $\to$ domain specifications $\to$ presentation packages).
- Import aliasing or path conventions: Canonical bootstrap guard `try: import lib.X; except ImportError: import X`.

### 5) Evidence

- [`scripts/lib/registry.py#L1-L60`](file:///scripts/lib/registry.py#L1-L60)
- [`scripts/lib/registry_base.py#L1-L60`](file:///scripts/lib/registry_base.py#L1-L60)
- [`scripts/lib/registry_specs/__init__.py#L1-L30`](file:///scripts/lib/registry_specs/__init__.py#L1-L30)
- [`scripts/lib/data_access.py#L1-L60`](file:///scripts/lib/data_access.py#L1-L60)
- [`scripts/lib/resonance.py#L1-L60`](file:///scripts/lib/resonance.py#L1-L60)
- [`scripts/lib/resonance_data.py#L1-L60`](file:///scripts/lib/resonance_data.py#L1-L60)
- [`scripts/lib/economy.py#L1-L60`](file:///scripts/lib/economy.py#L1-L60)
- [`scripts/lib/economy_trade.py#L1-L60`](file:///scripts/lib/economy_trade.py#L1-L60)
- [`scripts/lib/_bootstrap.py#L75-L115`](file:///scripts/lib/_bootstrap.py#L75-L115)
- [`scripts/lib/cli.py#L1-L100`](file:///scripts/lib/cli.py#L1-L100)
- [`scripts/arcanum#L1-L80`](file:///scripts/arcanum#L1-L80)
- [`scripts/lib/ui_gtk3/window.py#L1-L80`](file:///scripts/lib/ui_gtk3/window.py#L1-L80)
