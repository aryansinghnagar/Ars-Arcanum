# Codebase Structure — Ars Arcanum (Scriptorium)

## Core Sections (Required)

### 1) Top-Level Map

| Path | Purpose | Stack Layer | Evidence |
|:---|:---|:---|:---|
| `scripts/` | Main application entry points (`arcanum`, `test_parallel.py`, `setup_arcanum.sh`, `verify.sh`) and Python package root (`__init__.py`) | Shell / Linux / Python Runtime | [`scripts/arcanum`](file:///scripts/arcanum), [`scripts/__init__.py`](file:///scripts/__init__.py) |
| `scripts/lib/` | 17 sovereign deterministic core engines, data access layer (`data_access.py`), universal scoping subsystem (`scope.py`), and bootstrap safety utilities | Python Stdlib Core Engines | [`scripts/lib/registry.py`](file:///scripts/lib/registry.py), [`scripts/lib/data_access.py`](file:///scripts/lib/data_access.py), [`scripts/lib/scope.py`](file:///scripts/lib/scope.py), [`scripts/lib/_bootstrap.py`](file:///scripts/lib/_bootstrap.py) |
| `scripts/lib/*_template.py` | Embedded offline presentation templates for standalone HTML/CSS/JS visualizers (Velocity Studio, Draft Lineage, Diff, Heatmap, Portfolio, Codex, Omnibus, Preflight) | HTML5 / CSS3 / JavaScript Presentation | [`scripts/lib/velocity_template.py`](file:///scripts/lib/velocity_template.py), [`scripts/lib/draft_manager_template.py`](file:///scripts/lib/draft_manager_template.py), [`scripts/lib/portfolio_template.py`](file:///scripts/lib/portfolio_template.py) |
| `scripts/lib/ui_theme_engine.py` & `ui_theme_studio.py` | 11 visual presets, procedural Web Audio typewriter sound synth (10 models), and standalone Theme Studio | CSS Custom Properties / Web Audio API | [`scripts/lib/ui_theme_engine.py`](file:///scripts/lib/ui_theme_engine.py), [`scripts/lib/ui_theme_studio.py`](file:///scripts/lib/ui_theme_studio.py) |
| `scripts/lib/registry_specs/` | Modular domain engine specifications partitioned across 4 active domains (Editorial, Portfolio, Infrastructure, Publishing) | Python Metadata & Contracts | [`scripts/lib/registry_specs/domain_editorial.py`](file:///scripts/lib/registry_specs/domain_editorial.py), [`scripts/lib/registry_specs/__init__.py`](file:///scripts/lib/registry_specs/__init__.py) |
| `launchers/` | Linux XDG desktop entry files (`.desktop`) for Zen Studio, Studio Hub, and Desktop App | Linux OS Desktop Integration | [`launchers/arcanum-app.desktop`](file:///launchers/arcanum-app.desktop), [`launchers/arcanum-hub.desktop`](file:///launchers/arcanum-hub.desktop), [`launchers/arcanum-zen.desktop`](file:///launchers/arcanum-zen.desktop) |
| `templates/` | Standardized world bibles (29 templates, 27 Metadata Menu fileClasses), manuscript blueprints (18 templates & chapter files), 5 Typst presets, demo cosmos (`Eldoria`), and 32 pre-configured Obsidian plugins | External Tools & Plugins Templates | [`templates/world-bible/`](file:///templates/world-bible/), [`templates/world-bible/.obsidian/plugins/`](file:///templates/world-bible/.obsidian/plugins/), [`templates/manuscript/`](file:///templates/manuscript/), [`templates/typst/`](file:///templates/typst/) |
| `configs/` | Deterministic plugin definitions, idiom dictionaries, LeechBlock rules, and core settings | External Plugins & Distraction Control | [`configs/plugin_catalog.json`](file:///configs/plugin_catalog.json), [`configs/idioms.json`](file:///configs/idioms.json), [`configs/leechblock_arcanum_rules.json`](file:///configs/leechblock_arcanum_rules.json) |
| `docs/` | Comprehensive craft documentation, user guides, master engine encyclopedia, roadmap, and codebase architecture | Documentation & Governance | [`docs/README.md`](file:///docs/README.md), [`docs/ENGINE_LOGIC_ENCYCLOPEDIA.md`](file:///docs/ENGINE_LOGIC_ENCYCLOPEDIA.md), [`docs/ROADMAP.md`](file:///docs/ROADMAP.md), [`docs/codebase/`](file:///docs/codebase/) |
| `tests/` | Exhaustive 486-test suite across 56 modules covering unit, integration, scoping, threat model, and benchmark tests | Python Testing & CI Gates | [`tests/test_*.py`](file:///tests/) |
| `.github/` | Multi-stage continuous integration workflows, multi-platform runner matrix, and security auditing | Shell / Linux CI/CD Automation | [`.github/workflows/ci.yml`](file:///.github/workflows/ci.yml) |

---

### 2) Entry Points

- **POSIX Shell Entry Point**: [`scripts/arcanum`](file:///scripts/arcanum) — Symlink-aware bash dispatcher handling CLI subcommands, environment validation, and system installer invocations.
- **Windows Batch Launcher**: [`scripts/arcanum.cmd`](file:///scripts/arcanum.cmd) — Windows CMD/PowerShell launcher forwarding directly to `scripts/lib/cli.py`.
- **Python CLI Runtime Dispatcher**: [`scripts/lib/cli.py`](file:///scripts/lib/cli.py) — Registered console scripts (`arcanum`, `ars-arcanum`) via [`pyproject.toml#L12-L15`](file:///pyproject.toml#L12-L15).
- **Parallel Test Runner**: [`scripts/test_parallel.py`](file:///scripts/test_parallel.py) — Multi-core test discovery across 12 worker processes.
- **Platform Installers**:
  - POSIX / Linux: [`scripts/setup_arcanum.sh`](file:///scripts/setup_arcanum.sh)
  - Windows: [`scripts/setup_arcanum.ps1`](file:///scripts/setup_arcanum.ps1)
- **Linux Desktop Launchers**:
  - `launchers/arcanum-zen.desktop` (Zen drafting mode)
  - `launchers/arcanum-hub.desktop` (Interactive web/browser studio)
  - `launchers/arcanum-app.desktop` (Native desktop workspace)

---

### 3) Module Boundaries & Layer Separation

| Boundary / Module Group | What belongs here | What must not be here |
|:---|:---|:---|
| `scripts/lib/_bootstrap.py` & `fs_utils.py` | Atomic POSIX/Windows file I/O, path traversal defense, Windows reserved device name checks (`CON`, `PRN`, `AUX`, `NUL`, etc.), cross-platform file locking | Craft business rules, UI rendering |
| `scripts/lib/data_access.py` & `cache.py` | Thread-safe memoized vault reader, AST cache with `mtime` invalidation, frontmatter queries | Presentation HTML markup, CLI argument parsing |
| `scripts/lib/scope.py`, `scope_parser.py`, `scope_resolver.py` | Granular range and target resolution (`1-5`, `ch01..ch05`, `sc01..sc02`, lore slices) | Hardcoded file paths, monolithic scans |
| `scripts/lib/registry_base.py` & `registry_specs/` | Engine specifications, 6-tier severity taxonomy, base engine contracts (<800L/file) | Runtime state, CLI query methods |
| `scripts/lib/*_template.py` | Self-contained offline HTML5/CSS3/JS presentation templates with strict CSP | Direct filesystem mutations, network requests |
| `scripts/lib/word_counter.py` & `writing_sprint.py` | Prose word tokenization, CriticMarkup stripping, dialogue extraction, Pomodoro sprint lifecycle | Normative composite scores, external cloud telemetry |
| `scripts/lib/docx_sync.py` & `docx_builder.py` | Bidirectional Markdown $\leftrightarrow$ DOCX AST translation, track change deletion discarding, sidecar comment preservation | Proprietary Microsoft Word dependencies |
| `scripts/lib/importer.py` & `publisher.py` | Multi-format manuscript ingestion (MD, TXT, EPUB, DOCX, Scrivener) and export (Typst PDF, Pandoc EPUB, DOCX, Omnibus) | Cloud conversion APIs |

---

### 4) Naming and Organization Rules

- **Python Source Files**: Lowercase snake_case (`manuscript_diff.py`, `writing_sprint.py`, `docx_sync_template.py`).
- **Template Files**: Co-located presentation templates named `<engine>_template.py` returning strict CSP-isolated HTML strings.
- **Test Modules**: Prefix `test_<module_name>.py` located strictly in `tests/`.
- **Import Ordering**: Standard library modules $\to$ local core imports (`from lib._bootstrap import ...`).
- **Module Size Contract**: Strict `<800 lines/file` maintainability contract enforced across all Python source files.

---

### 5) Evidence

- [`scripts/lib/registry.py#L1-L60`](file:///scripts/lib/registry.py#L1-L60)
- [`scripts/lib/registry_base.py#L1-L60`](file:///scripts/lib/registry_base.py#L1-L60)
- [`scripts/lib/registry_specs/__init__.py#L1-L30`](file:///scripts/lib/registry_specs/__init__.py#L1-L30)
- [`scripts/lib/data_access.py#L1-L60`](file:///scripts/lib/data_access.py#L1-L60)
- [`scripts/lib/_bootstrap.py#L1-L120`](file:///scripts/lib/_bootstrap.py#L1-L120)
- [`scripts/lib/cli.py#L1-L100`](file:///scripts/lib/cli.py#L1-L100)
- [`scripts/arcanum#L1-L80`](file:///scripts/arcanum#L1-L80)
- [`launchers/arcanum-app.desktop#L1-L15`](file:///launchers/arcanum-app.desktop#L1-L15)
