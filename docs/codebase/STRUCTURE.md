# Codebase Structure

## Core Sections (Required)

### 1) Top-Level Map

| Path | Purpose | Evidence |
|------|---------|----------|
| `scripts/` | Main application entry points (`arcanum`, `test_parallel.py`, `setup_arcanum.sh`, `verify.sh`) and Python package root (`__init__.py`) | [`scripts/arcanum`](file:///scripts/arcanum), [`scripts/__init__.py`](file:///scripts/__init__.py) |
| `scripts/lib/` | 14 sovereign deterministic core engines, data access layer (`data_access.py`), universal scoping subsystem (`scope.py`), and bootstrap safety utilities | [`scripts/lib/registry.py`](file:///scripts/lib/registry.py), [`scripts/lib/data_access.py`](file:///scripts/lib/data_access.py), [`scripts/lib/registry_base.py`](file:///scripts/lib/registry_base.py), [`scripts/lib/scope.py`](file:///scripts/lib/scope.py), [`scripts/lib/_bootstrap.py`](file:///scripts/lib/_bootstrap.py) |
| `scripts/lib/registry_specs/` | Modular domain engine specifications partitioned across 4 active domains (Editorial, Portfolio, Infrastructure, Publishing) | [`scripts/lib/registry_specs/domain_editorial.py`](file:///scripts/lib/registry_specs/domain_editorial.py), [`scripts/lib/registry_specs/__init__.py`](file:///scripts/lib/registry_specs/__init__.py) |
| `docs/` | Comprehensive craft documentation, user guides, master engine encyclopedia, roadmap, and codebase architecture | [`docs/README.md`](file:///docs/README.md), [`docs/ENGINE_LOGIC_ENCYCLOPEDIA.md`](file:///docs/ENGINE_LOGIC_ENCYCLOPEDIA.md), [`docs/ROADMAP.md`](file:///docs/ROADMAP.md), [`docs/codebase/`](file:///docs/codebase/) |
| `tests/` | Exhaustive 353-test suite across 48 modules covering unit, integration, scoping, threat model, and benchmark tests | [`tests/test_*.py`](file:///tests/) |
| `templates/` | Standardized world bibles (29 templates, 27 Metadata Menu fileClasses), manuscript blueprints (18 templates & chapter files), 5 Typst presets, demo cosmos (`Eldoria`), and 32 pre-configured Obsidian plugins | [`templates/world-bible/`](file:///templates/world-bible/), [`templates/manuscript/`](file:///templates/manuscript/), [`templates/typst/`](file:///templates/typst/), [`templates/demo-cosmos/`](file:///templates/demo-cosmos/) |
| `configs/` | Deterministic plugin definitions, idiom dictionaries, LeechBlock rules, and core settings | [`configs/plugin_catalog.json`](file:///configs/plugin_catalog.json), [`configs/idioms.json`](file:///configs/idioms.json), [`configs/leechblock_arcanum_rules.json`](file:///configs/leechblock_arcanum_rules.json) |

### 2) Entry Points

- Unified CLI runtime dispatcher: [`scripts/lib/cli.py`](file:///scripts/lib/cli.py) / [`scripts/arcanum`](file:///scripts/arcanum) / registered entry points (`arcanum`, `ars-arcanum`)
- Parallel test runner: [`scripts/test_parallel.py`](file:///scripts/test_parallel.py)
- Selection mechanism: POSIX shell wrapper `scripts/arcanum` dispatches subcommands to `scripts/lib/cli.py` or bash fallback handlers.

### 3) Module Boundaries

| Boundary | What belongs here | What must not be here |
|----------|-------------------|------------------------|
| `scripts/lib/_bootstrap.py` & `fs_utils.py` | Atomic POSIX/Windows file I/O, regex token sanitization, Windows reserved device name guards (`CON`, `PRN`, `AUX`, `NUL`, etc.), lockfiles | Domain business logic, UI widgets |
| `scripts/lib/data_access.py` | Thread-safe memoized vault reader, frontmatter parser, and chapter/lore entity queries with `mtime` invalidation | Direct presentation rendering, business rules |
| `scripts/lib/registry_base.py` | Core `EngineSpec`, `EngineCategory`, and `BaseCraftEngine` contract types (<200 lines) | Individual engine metadata dictionaries |
| `scripts/lib/registry_specs/` | Pure static domain engine specifications across 4 domains (Editorial, Portfolio, Infrastructure, Publishing) | Runtime state, CLI query methods |
| `scripts/lib/registry.py` | Authoritative 14-engine discovery matrix, dynamic plugin scanner, and doc formatting (<600 lines) | Monolithic static dictionaries |
| `scripts/lib/manuscript_diff.py` & `revision_heatmap.py` | Manuscript AST difference calculations, churn scores, revision density statistics, and standalone offline visualizers | Direct unbuffered disk writes |
| `scripts/lib/portfolio.py` | Multi-manuscript progress tracking, wordcount statistics, publication stage auditing, and standalone HTML catalog dashboard | External network telemetry |
| `scripts/lib/docx_sync.py` & `docx_builder.py` | Roundtrip Markdown <-> DOCX AST parsing and standard submission formatting | Proprietary cloud APIs |
| `scripts/lib/diagnostics.py` | System health check, toolchain inspection, and vault link consistency doctor | Prescriptive aesthetic rules |

### 4) Naming and Organization Rules

- File naming pattern: Lowercase snake_case (`manuscript_diff.py`, `revision_heatmap.py`, `test_portfolio.py`).
- Directory organization pattern: Layered architectural tiers (Root bootstrap $\to$ `scripts/lib/` engines $\to$ domain specifications).
- Import aliasing or path conventions: Canonical bootstrap guard `try: import lib.X; except ImportError: import X`.

### 5) Evidence

- [`scripts/lib/registry.py#L1-L60`](file:///scripts/lib/registry.py#L1-L60)
- [`scripts/lib/registry_base.py#L1-L60`](file:///scripts/lib/registry_base.py#L1-L60)
- [`scripts/lib/registry_specs/__init__.py#L1-L30`](file:///scripts/lib/registry_specs/__init__.py#L1-L30)
- [`scripts/lib/data_access.py#L1-L60`](file:///scripts/lib/data_access.py#L1-L60)
- [`scripts/lib/_bootstrap.py#L75-L115`](file:///scripts/lib/_bootstrap.py#L75-L115)
- [`scripts/lib/cli.py#L1-L100`](file:///scripts/lib/cli.py#L1-L100)
- [`scripts/arcanum#L1-L80`](file:///scripts/arcanum#L1-L80)

