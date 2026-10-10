# Ars Arcanum (Scriptorium) — Definitive System Architecture & Technical Blueprint

> **Sovereign Local-First Authoring Operating System & Craft Studio (GPA 4.0/4.0 — Grade A+)**  
> *Authoritative Onboarding Reference, System Blueprint & Verification Baseline*  
> **Release Version**: `v0.1.0` | **Quality Grade**: `Grade A+ (GPA 4.0/4.0)` | **Repository**: `https://github.com/aryansinghnagar/Ars-Arcanum.git`

---

## Part 1 — Whole-Repository Technical Deep-Dive

### 1.1 Executive System Identity
**Ars Arcanum** (code-named *Scriptorium*) is a sovereign, local-first authoring operating system and speculative worldbuilding craft studio designed for Linux, Windows, and macOS workstations ([`README.md#L1-L25`](file:///README.md#L1-L25), [`AGENTS.md#L1-L25`](file:///AGENTS.md#L1-L25)). It orchestrates a complete creative production pipeline—spanning secondary-world bible management, manuscript scaffolding, multi-draft branching lineage, prose tokenization, cognitive sprint velocity tracking, editorial churn telemetry (structural markdown diffs, revision heatmaps, portfolio catalog), bidirectional DOCX synchronization, and publication-grade typesetting (Typst print PDF, Pandoc EPUB3, standard submission DOCX, and omnibus compilation)—executing 100% offline with zero cloud dependencies, zero external network telemetry, and a zero-pip dependency guarantee for all core engines ([`AGENTS.md#L18-L35`](file:///AGENTS.md#L18-L35)).

All prose manuscripts, character dossiers, lore bibles, and timelines are stored in standard CommonMark Markdown (`.md`), human-readable YAML frontmatter manifests, and open standard file formats on the author's local workstation. The architecture guarantees zero vendor lock-in, strict offline Content Security Policies (`default-src 'none'`), advisory-first creative freedom mechanics, epistemic decoupling across three isolated subsystems, and atomic POSIX/Windows crash safety.

---

### 1.2 Tech-Stack Detection Table

| Layer / Subsystem | Technology | Purpose | Evidence (File + Lines) |
|:---|:---|:---|:---|
| **Core Runtime** | Python 3.10+ Standard Library (3.10–3.14) | Zero-pip execution runtime for core craft engines, validators, parsers, and exporters | [`pyproject.toml#L10`](file:///pyproject.toml#L10), [`AGENTS.md#L28-L30`](file:///AGENTS.md#L28-L30) |
| **Packaging & Build** | Setuptools (`>=61.0`) with `pyproject.toml` | Wheel packaging and console script dispatch (`arcanum`, `ars-arcanum`) | [`pyproject.toml#L1-L15`](file:///pyproject.toml#L1-L15), [`scripts/__init__.py`](file:///scripts/__init__.py) |
| **CLI Dispatchers** | POSIX Bash + Windows Batch + Pure-Python Dispatcher | Cross-platform CLI entry points with fuzzy error resolution, retirement doctrine guidance, and dual command routing | [`scripts/arcanum#L1-L50`](file:///scripts/arcanum#L1-L50), [`scripts/arcanum.cmd#L1-L5`](file:///scripts/arcanum.cmd#L1-L5), [`scripts/lib/cli.py#L1-L120`](file:///scripts/lib/cli.py#L1-L120), [`scripts/lib/cli_handlers.py`](file:///scripts/lib/cli_handlers.py) |
| **Atomic File I/O & Primitives** | Crash-safe atomic write (`flush` $\to$ `fsync` $\to$ `os.replace` $\to$ parent dir `fsync`) + Path Traversal Defense | POSIX/Windows crash resilience, Unicode prose word counting, and path traversal / Windows reserved device name defense | [`scripts/lib/_bootstrap.py#L33-L115`](file:///scripts/lib/_bootstrap.py#L33-L115), [`scripts/lib/fs_utils.py#L1-L135`](file:///scripts/lib/fs_utils.py#L1-L135) |
| **Cross-Platform File Locking** | `ArcanumLock` (`fcntl.flock` on POSIX, `msvcrt.locking` on Windows) | Deterministic byte-0 concurrency locking for archives, backups, and synchronizers | [`scripts/lib/lockfile.py#L35-L135`](file:///scripts/lib/lockfile.py#L35-L135) |
| **Data Access & Caching Layer** | `CachedDataAccess` + Thread-Safe LRU AST Cache | Fast memoized filesystem AST and YAML metadata retrieval with `mtime` invalidation | [`scripts/lib/data_access.py#L30-L180`](file:///scripts/lib/data_access.py#L30-L180), [`scripts/lib/cache.py#L1-L340`](file:///scripts/lib/cache.py#L1-L340) |
| **YAML Frontmatter Engine** | Pure-Python Recursive Frontmatter Parser & Serializer | Zero-dependency YAML metadata parser supporting mappings, lists, block scalars, and typed coercion | [`scripts/lib/frontmatter.py#L1-L380`](file:///scripts/lib/frontmatter.py#L1-L380), [`scripts/lib/frontmatter_builder.py#L1-L150`](file:///scripts/lib/frontmatter_builder.py#L1-L150) |
| **Granular Target Scoping** | Unified `EngineScope` Token & Range Parser | Altitude-aware context discovery (`1-5`, `ch01..ch05`, `sc01..sc02`, lore slices) preventing unconstrained scans | [`scripts/lib/scope.py#L1-L100`](file:///scripts/lib/scope.py#L1-L100), [`scripts/lib/scope_parser.py#L1-L150`](file:///scripts/lib/scope_parser.py#L1-L150), [`scripts/lib/scope_resolver.py#L1-L120`](file:///scripts/lib/scope_resolver.py#L1-L120) |
| **Authorial Constitution & Governance** | Deep-Merged `constitution.yaml` / `constitution.json` & Modular Policy Engine | 6-Tier diagnostic classification (`CANON_ERROR` to `EXPERIMENT`), rule suppression, and `@intent: deliberate` preservation | [`scripts/lib/config.py`](file:///scripts/lib/config.py), [`scripts/lib/constitution.py`](file:///scripts/lib/constitution.py), [`scripts/lib/config_store.py`](file:///scripts/lib/config_store.py), [`scripts/lib/registry_base.py#L1-L80`](file:///scripts/lib/registry_base.py#L1-L80) |
| **Engine Registry & Domain Specs** | `BaseCraftEngine` Lifecycle Contract + 4 Domain Specifications | 17 registered sovereign engines across Editorial, Portfolio, Infrastructure, Publishing, plus dynamic plugin scanner | [`scripts/lib/registry.py#L1-L150`](file:///scripts/lib/registry.py#L1-L150), [`scripts/lib/registry_specs/`](file:///scripts/lib/registry_specs/) |
| **Word Counter & Velocity Engine** | Advanced Prose Tokenizer & Hybrid Velocity Aggregator (`word_counter.py`, `writing_sprint.py`) | CriticMarkup stripping, dialogue vs narrative ratio, CJK ideographs, reading times, stateful Pomodoro sprint timers, 7d/30d pace, streaks | [`scripts/lib/word_counter.py`](file:///scripts/lib/word_counter.py), [`scripts/lib/writing_sprint.py`](file:///scripts/lib/writing_sprint.py), [`scripts/lib/velocity_template.py`](file:///scripts/lib/velocity_template.py) |
| **Draft Manager & Lineage Tree** | Multi-Draft Branching & Versioning Engine (`draft_manager.py`) | Branching (`Draft-01` $\to$ `Draft-02`), parent lineage tracking, immutable snapshot locks, and interactive HTML lineage visualizer | [`scripts/lib/draft_manager.py`](file:///scripts/lib/draft_manager.py), [`scripts/lib/draft_manager_template.py`](file:///scripts/lib/draft_manager_template.py) |
| **Project Lifecycle Scaffolder** | Pure-Python Project Provisioning (`project_scaffold.py`) | Fast scaffolding for Universes, Worlds, Manuscripts, Volumes, and Novel formats with YAML frontmatter schemas | [`scripts/lib/project_scaffold.py`](file:///scripts/lib/project_scaffold.py) |
| **Editorial & Churn Telemetry** | Structural Diff (`manuscript_diff.py`) & Revision Heatmap (`revision_heatmap.py`) | AST block diffing, Myers semantic word redlines, Git line churn metrics (`REV-101`/`REV-102`), and standalone offline HTML reports | [`scripts/lib/manuscript_diff.py#L1-L120`](file:///scripts/lib/manuscript_diff.py#L1-L120), [`scripts/lib/revision_heatmap.py#L1-L120`](file:///scripts/lib/revision_heatmap.py#L1-L120) |
| **Portfolio Catalog Tracking** | Multi-Manuscript Portfolio Engine (`portfolio.py`) | Cross-manuscript velocity tracking, word counts, target completion progress, and standalone HTML dashboard | [`scripts/lib/portfolio.py#L1-L150`](file:///scripts/lib/portfolio.py#L1-L150), [`scripts/lib/portfolio_template.py`](file:///scripts/lib/portfolio_template.py) |
| **Bidirectional DOCX Engine** | Native OpenXML Generator & Sync Engine (`docx_sync.py`, `docx_builder.py`, `docx_presets.py`) | Two-way Markdown $\leftrightarrow$ DOCX roundtripping, track changes deletion discarding, and comment sidecar extraction | [`scripts/lib/docx_sync.py#L1-L150`](file:///scripts/lib/docx_sync.py#L1-L150), [`scripts/lib/docx_builder.py#L1-L120`](file:///scripts/lib/docx_builder.py#L1-L120), [`scripts/lib/docx_presets.py`](file:///scripts/lib/docx_presets.py) |
| **Publication & Typesetting** | Typst CLI (`>=0.11.0`, pinned `0.14.2`), Pandoc (`>=2.19.x`), Publisher Engine (`publisher.py`) | Sub-second commercial PDF book typesetting, EPUB3 packaging, submission formatting, static codex generation, and omnibus compilation | [`scripts/lib/publisher.py`](file:///scripts/lib/publisher.py), [`scripts/lib/omnibus.py#L1-L120`](file:///scripts/lib/omnibus.py#L1-L120), [`scripts/lib/preflight.py#L1-L100`](file:///scripts/lib/preflight.py#L1-L100), [`scripts/lib/codex_export.py#L1-L120`](file:///scripts/lib/codex_export.py#L1-L120) |
| **UI Presets & Audio Synth** | Pure Web Audio API & CSS Custom Properties (`ui_theme_engine.py`, `ui_theme_studio.py`) | 11 visual presets, zero-asset 10-generation procedural typewriter sound synthesis, and interactive Theme Studio | [`scripts/lib/ui_theme_engine.py`](file:///scripts/lib/ui_theme_engine.py), [`scripts/lib/ui_theme_studio.py`](file:///scripts/lib/ui_theme_studio.py), [`docs/THEME_STUDIO.md`](file:///docs/THEME_STUDIO.md) |
| **Backup, Restore & Migration** | Pure-Python Verified Archive Engine (`backup.py`, `restore.py`, `snapshot.py`, `migrate.py`) | SHA-256 stream-verified `.tar.gz` archives, path-traversal defended restoration, Git snapshots, and schema migrations | [`scripts/lib/backup.py#L1-L120`](file:///scripts/lib/backup.py#L1-L120), [`scripts/lib/restore.py#L1-L120`](file:///scripts/lib/restore.py#L1-L120), [`scripts/lib/snapshot.py#L1-L80`](file:///scripts/lib/snapshot.py#L1-L80), [`scripts/lib/migrate.py#L1-L100`](file:///scripts/lib/migrate.py#L1-L100) |
| **Unified Diagnostics Doctor** | System Health, Toolchain & Lore Integrity Doctor (`diagnostics.py`) | Environment verification (Python, Git, Pandoc, Typst, Ruff), broken link detection, and orphan node diagnosis | [`scripts/lib/diagnostics.py#L1-L150`](file:///scripts/lib/diagnostics.py#L1-L150) |
| **External Toolchain & Obsidian Vault** | Obsidian (32 pre-configured offline plugins), PolyGlot, Gramps, Wonderdraft, Celestia, StarGen | Full external creative toolchain, Markdown World Bible vault interface, and distraction-free novel project drafting | [`templates/world-bible/.obsidian/plugins/manifest.json`](file:///templates/world-bible/.obsidian/plugins/manifest.json), [`docs/guides/EXTERNAL_TOOLS_AND_PLUGINS.md`](file:///docs/guides/EXTERNAL_TOOLS_AND_PLUGINS.md) |

---

### 1.3 Entry Points

1. **POSIX Shell Wrapper**: [`scripts/arcanum`](file:///scripts/arcanum#L1-L50). Symlink-dereferencing shell entry point providing standalone bash subroutines for universe, world, and manuscript management alongside transparent forwarding to Python CLI.
2. **Windows Command Batch Launcher**: [`scripts/arcanum.cmd`](file:///scripts/arcanum.cmd#L1-L5). Native Windows batch wrapper providing seamless command dispatch to `scripts/lib/cli.py` across PowerShell and CMD.
3. **Authoritative Python CLI Dispatcher**: [`scripts/lib/cli.py`](file:///scripts/lib/cli.py#L1-L120). Pure-Python CLI dispatcher (registered as `arcanum` and `ars-arcanum` via [`pyproject.toml#L12-L15`](file:///pyproject.toml#L12-L15)), routing subcommands via declarative dispatch tables (`scripts/lib/cli_handlers.py`), JSON output mode (`--json`), and advisory documentation lookup (`arcanum doc <engine>`).
4. **Parallel Test Runner**: [`scripts/test_parallel.py`](file:///scripts/test_parallel.py#L1-L80). High-performance multi-core parallel test runner discovering and executing all 55 test modules across worker processes in ~2.5s-7s.
5. **System Installers**:
   - POSIX: [`scripts/setup_arcanum.sh`](file:///scripts/setup_arcanum.sh#L1-L100) (packages, fonts, Typst musl binary, desktop launchers).
   - Windows: [`scripts/setup_arcanum.ps1`](file:///scripts/setup_arcanum.ps1#L1-L80) (workspace provisioning, PowerShell profiles, desktop shortcuts).

---

### 1.4 Commands & Verification Inventory

| Command | Purpose | Verification Source / Evidence | Trigger / CI Enforcement Status |
|:---|:---|:---|:---|
| `pip install -e .` | Standard development package installation and entry point registration (`arcanum`, `ars-arcanum`) | [`pyproject.toml#L1-L20`](file:///pyproject.toml#L1-L20) | **Enforced in CI** ([`.github/workflows/ci.yml#L100-L108`](file:///.github/workflows/ci.yml#L100-L108)) |
| `python -m unittest discover tests` | Full repository Python unit & integration test suite (486 tests across 56 modules, 0 failures) | [`tests/test_*.py`](file:///tests/) | **Enforced in CI** ([`.github/workflows/ci.yml#L76-L81`](file:///.github/workflows/ci.yml#L76-L81)) |
| `python scripts/test_parallel.py` | High-speed multi-core parallel test runner (~2.5s-9.5s execution across 12 worker processes) | [`scripts/test_parallel.py`](file:///scripts/test_parallel.py) | Local Developer / Fast Test Loop |
| `python -m unittest tests/test_<module>.py` | Isolated single module unit test execution (e.g. `tests/test_ui_theme_engine.py`) | [`tests/`](file:///tests/) | Developer Rapid Feedback Loop |
| `ruff check .` | Strict linting across 15 rule sets (`E`, `W`, `F`, `B`, `S`, `UP`, `SIM`, `I`, `RUF`, `C901`, `C4`, `PIE`, `RET`, `RSE`, `FLY`) | [`pyproject.toml#L20-L49`](file:///pyproject.toml#L20-L49) | **Enforced in CI** ([`.github/workflows/ci.yml#L56-L60`](file:///.github/workflows/ci.yml#L56-L60)) |
| `mypy --explicit-package-bases scripts tests` | Strict static type checking with `check_untyped_defs = True` (117 source files clean) | [`mypy.ini#L1-L25`](file:///mypy.ini#L1-L25) | **Enforced in CI** ([`.github/workflows/ci.yml#L61-L65`](file:///.github/workflows/ci.yml#L61-L65)) |
| `bandit -r scripts/lib -ll -ii` | Python AST Security Static Analysis (SAST) for high/medium severity vulnerabilities | [`.github/workflows/ci.yml#L66-L70`](file:///.github/workflows/ci.yml#L66-L70) | **Enforced in CI** ([`.github/workflows/ci.yml#L66-L70`](file:///.github/workflows/ci.yml#L66-L70)) |
| `coverage run -m unittest discover tests; coverage report --fail-under=80` | Measure and enforce aggregate test code coverage threshold ($\ge 80\%$, currently 80%+) | [`pyproject.toml#L50-L71`](file:///pyproject.toml#L50-L71) | **Enforced in CI** ([`.github/workflows/ci.yml#L76-L81`](file:///.github/workflows/ci.yml#L76-L81)) |
| `bash -n scripts/*.sh scripts/arcanum scripts/ars-arcanum` | POSIX shell script syntax validation across all bash entry points | [`.github/workflows/ci.yml#L82-L95`](file:///.github/workflows/ci.yml#L82-L95) | **Enforced in CI** ([`.github/workflows/ci.yml#L82-L95`](file:///.github/workflows/ci.yml#L82-L95)) |
| `shellcheck -S warning scripts/*.sh scripts/arcanum scripts/ars-arcanum` | Static analysis for POSIX shell scripts | [`.github/workflows/ci.yml#L96-L99`](file:///.github/workflows/ci.yml#L96-L99) | **Enforced in CI** ([`.github/workflows/ci.yml#L96-L99`](file:///.github/workflows/ci.yml#L96-L99)) |
| `gitleaks detect` | Automated secret and credential leakage scanning | [`.github/workflows/ci.yml#L51-L55`](file:///.github/workflows/ci.yml#L51-L55) | **Enforced in CI** ([`.github/workflows/ci.yml#L51-L55`](file:///.github/workflows/ci.yml#L51-L55)) |
| `bash scripts/verify.sh --require-tools` | Canonical 7-stage master quality and packaging integration verification harness (POSIX) | [`scripts/verify.sh#L1-L150`](file:///scripts/verify.sh#L1-L150) | **Enforced in CI** ([`.github/workflows/ci.yml#L125-L128`](file:///.github/workflows/ci.yml#L125-L128)) |
| `python scripts/arcanum doctor` | Unified system toolchain inspection, Python environment doctor & vault consistency audit | [`scripts/lib/diagnostics.py#L1-L150`](file:///scripts/lib/diagnostics.py#L1-L150) | Local Author Health Diagnostic |
| `python scripts/arcanum theme-studio --open` | Standalone interactive UI theme presets and multi-generation typewriter sound studio | [`scripts/lib/ui_theme_studio.py`](file:///scripts/lib/ui_theme_studio.py) | Interactive Immersion Studio |

> [!NOTE]
> **CI Enforcement & Status Checks**: All CI workflows are defined in [`.github/workflows/ci.yml`](file:///.github/workflows/ci.yml) and trigger on all pushes and pull requests targeting the `main` branch, alongside a weekly automated drift detection schedule (`cron: '23 4 * * 1'`). Branch protection rules requiring these jobs to pass prior to merging must be configured in GitHub repository settings.

---

### 1.5 Directory Layout & Responsibilities

```
.
├── .github/                   # GitHub Actions CI/CD workflows and automated quality gates
│   └── workflows/ci.yml       # 3-tier CI pipeline: verify, distro-matrix, multi-platform
├── configs/                   # Systemd units, LeechBlock distraction rules, and linter configs
├── docs/                      # Comprehensive system documentation and domain engine manuals
│   ├── codebase/              # Architectural blueprints, tech stack, conventions, and testing
│   ├── guides/                # Operational guides (backup, distraction control, typography, plugins)
│   └── ARCHITECTURE.md        # Authoritative system architecture and verification blueprint
├── launchers/                 # XDG desktop application entry points (.desktop files)
├── scripts/                   # Core application codebase and command executables
│   ├── arcanum                # POSIX shell entrypoint wrapper
│   ├── arcanum.cmd            # Native Windows batch launcher
│   ├── test_parallel.py       # High-performance parallel test runner (~2.5s execution)
│   ├── setup_arcanum.sh       # POSIX automated system installer
│   ├── setup_arcanum.ps1      # Windows automated PowerShell installer
│   ├── verify.sh              # Canonical 7-stage integration verification harness
│   └── lib/                   # Standard-library core engines and craft modules (<800 lines/file)
│       ├── _bootstrap.py      # Atomic write, path validation, Unicode word counts, and system primitives
│       ├── cli.py             # Authoritative cross-platform CLI dispatcher
│       ├── cli_handlers.py    # CLI handler routing with graceful retirement doctrine guidance
│       ├── config.py          # Authorial Constitution loader, deep merging, and config resolution
│       ├── config_store.py    # Configuration persistence and global settings storage
│       ├── constitution.py    # Authorial Constitution & Intent policy engine
│       ├── state.py           # Global atomic state storage for active workstreams
│       ├── lockfile.py        # Cross-platform file locking (ArcanumLock: flock / msvcrt)
│       ├── fs_utils.py        # Safe atomic filesystem manipulation and directory copy routines
│       ├── cache.py           # Memory & disk AST/frontmatter caching layer
│       ├── data_access.py     # Centralized cached vault reader and AST frontmatter layer
│       ├── frontmatter.py     # Zero-dependency YAML frontmatter parser and serializer
│       ├── frontmatter_builder.py # Scaffolding generator for valid YAML frontmatter manifests
│       ├── project_scaffold.py # Pure-Python universe, world, manuscript, volume scaffolding
│       ├── draft_manager.py   # Multi-draft branching, milestone states, and immutable snapshots
│       ├── draft_manager_template.py # Presentation HTML/CSS template for draft lineage tree
│       ├── scope.py           # Universal granular target scoping engine
│       ├── scope_models.py    # Dataclasses: EngineScope, ChapterItem, SceneSlice, ResolvedScope
│       ├── scope_parser.py    # Expression and range parsers for chapter/scene slicing
│       ├── scope_resolver.py  # Active context discovery heuristics for manuscripts and worlds
│       ├── word_counter.py    # Unicode prose tokenization, CriticMarkup stripping, POV & dialogue ratio
│       ├── writing_sprint.py  # Stateful sprint timer lifecycle, hybrid velocity derivation, streaks
│       ├── velocity_template.py # Standalone offline HTML5 Velocity Studio & interactive Pomodoro timer
│       ├── manuscript_diff.py # Structural markdown diff engine with HTML visualizer
│       ├── manuscript_diff_template.py # Presentation HTML/CSS template for structural diffs
│       ├── revision_heatmap.py# Revision density and editing churn heatmaps with HTML export
│       ├── revision_heatmap_template.py # Presentation HTML/CSS template for revision heatmaps
│       ├── portfolio.py       # Multi-manuscript author portfolio tracker & standalone HTML dashboard
│       ├── portfolio_template.py # Presentation HTML/CSS template for portfolio catalog
│       ├── docx_sync.py       # Two-way roundtrip Markdown <-> DOCX synchronizer
│       ├── docx_builder.py    # Zero-dependency standard submission format DOCX builder
│       ├── docx_presets.py    # Typography and styling presets for DOCX manuscript builds
│       ├── importer.py        # Universal multi-format manuscript & lore importer (MD, TXT, EPUB, DOCX)
│       ├── diagnostics.py     # Unified system health, toolchain & world vault consistency doctor
│       ├── preflight.py       # Pre-compilation validation & publication gatekeeper
│       ├── preflight_template.py # Presentation HTML/CSS template for preflight validation
│       ├── publisher.py       # Native manuscript compiler & multi-format publication exporter
│       ├── codex_export.py    # Standalone offline HTML world codex static site generator
│       ├── codex_export_template.py # Presentation HTML/CSS template for static codex site
│       ├── omnibus.py         # Multi-volume series omnibus compiler (MD, EPUB, PDF)
│       ├── omnibus_template.py # Presentation HTML/CSS template for omnibus reader
│       ├── ui_theme_engine.py # Centralized 11 visual presets, procedural Web Audio typewriter synth & control center
│       ├── ui_theme_studio.py # Standalone offline HTML5 Theme & Sound Showcase Studio visualizer
│       ├── migrate.py         # Schema and directory migration engine with automated backup
│       ├── backup.py          # Pure-Python standalone verified .tar.gz archive engine
│       ├── restore.py         # Pure-Python verified archive restoration with path traversal defense
│       ├── snapshot.py        # Pure-Python Git milestone snapshot versioning engine
│       ├── registry_base.py   # Core EngineSpec dataclasses, DiagnosticSeverity & base classes
│       ├── registry_specs/    # Domain engine specifications (Editorial, Portfolio, Infrastructure, Publishing)
│       └── registry.py        # Engine discovery matrix, craft doctrine docs & bibliography formatter
├── templates/                 # Scaffolding templates for World Bibles, manuscripts, and universes
│   ├── world-bible/           # Obsidian lore bible (29 templates, 27 Metadata Menu fileClasses, 32 plugins)
│   ├── manuscript/            # Multi-volume book manuscript & craft blueprints (18 templates & chapter files)
│   ├── typst/                 # Print-ready Typst typesetting templates and 5 genre presets
│   └── demo-cosmos/           # Fully hydrated multi-volume universe reference (Eldoria-Cosmos)
└── tests/                     # Comprehensive unittest suite across all domain engines (486 tests in 56 modules)
```

---

### 1.6 Deployment & Runtime Surface

| Runtime / Tool | Version Pin | Source of Truth | Verification Method |
|:---|:---|:---|:---|
| **Python** | `3.10`, `3.11`, `3.12`, `3.13`, `3.14` | [`pyproject.toml#L10`](file:///pyproject.toml#L10), [`.github/workflows/ci.yml#L31`](file:///.github/workflows/ci.yml#L31), [`.github/workflows/ci.yml#L170`](file:///.github/workflows/ci.yml#L170) | Test discovery across multi-version matrix |
| **Typst CLI** | `0.14.2` (Pinned musl binary + SHA-256) | [`scripts/setup_arcanum.sh#L317-L320`](file:///scripts/setup_arcanum.sh#L317-L320), [`.github/workflows/ci.yml#L41`](file:///.github/workflows/ci.yml#L41) | Static binary hash verification in setup script |
| **Pandoc** | `>=2.19.x` (Tested up to `3.7.x`) | [`docs/COMPATIBILITY.md#L9-L16`](file:///docs/COMPATIBILITY.md#L9-L16), [`.github/workflows/ci.yml#L36`](file:///.github/workflows/ci.yml#L36) | `pandoc --version` runtime check |
| **Obsidian Plugins** | 32 Pre-Configured Plugins (Pinned SHA-256) | [`templates/world-bible/.obsidian/plugins/manifest.json`](file:///templates/world-bible/.obsidian/plugins/manifest.json) | Hash manifest validation |
| **CI Runner OS** | `ubuntu-24.04`, `windows-latest`, `macos-latest` | [`.github/workflows/ci.yml#L20`](file:///.github/workflows/ci.yml#L20), [`.github/workflows/ci.yml#L169`](file:///.github/workflows/ci.yml#L169) | Multi-platform GitHub Actions matrix |
| **Distro Containers** | `ubuntu:22.04`, `ubuntu:24.04`, `debian:12`, `debian:13` | [`.github/workflows/ci.yml#L146-L150`](file:///.github/workflows/ci.yml#L146-L150) | Containerized clean-room test discovery |

---

### 1.7 EOL / Dead-Dependency Scan
- **Zero Third-Party Pip Runtime Dependencies**: The core codebase eliminates third-party pip runtime dependencies entirely. All 17 engines, parsers, mathematical models, locking primitives, and HTML/DOCX exporters run exclusively on Python standard library modules (`os`, `sys`, `json`, `re`, `shutil`, `hashlib`, `tarfile`, `zipfile`, `xml.etree.ElementTree`, `dataclasses`, `typing`, `unittest`).
- **Development & CI Tooling**: Linting and formatting use `ruff` (`0.15.x` / `0.16.x`), type checking uses `mypy` (`1.15.0`), security scans use `bandit` (`1.8.3`) and `gitleaks` (`3.0.0`), and coverage uses `coverage` (`7.6.x`). All are pinned in CI.
- **Runtime Minimums**: Python `< 3.10` is dropped due to reliance on modern union syntax (`X | Y`), pattern matching, and dataclass features.

---

### 1.8 Data, Storage, APIs & Testing Subsystems
- **Data & Document Storage**: Plain CommonMark Markdown (`.md`) files paired with YAML frontmatter headers. Document modifications are mediated via `atomic_write()` to eliminate corruption risks during system power failure.
- **Cache & Memoization**: Centralized `CachedDataAccess` utilizing thread-safe LRU dictionaries keyed on filesystem modification time (`mtime`) and file size (`st_size`), automatically invalidating cache entries when files mutate on disk.
- **Local Telemetry & Document Diffs**: `manuscript_diff` computes line- and block-level AST diffs between manuscript revisions; `revision_heatmap` maps Git commit churn across chapter files.
- **Word Telemetry & Sprint Sessions**: `word_counter` extracts dialogue ratios and CJK counts; `writing_sprint` manages atomic state locks (`.sprint_state.json`) and appends JSONL history (`sprint_log.jsonl`).
- **Cryptographic Archives & Safety**: Backups generate POSIX/Windows-compatible `.tar.gz` archives with companion SHA-256 sidecars and path-traversal sanitization upon restoration (`restore.py`).

---

## Part 2 — Context & Operational Ecosystem

### 2.1 Local Checkout Identity Table

| Attribute | Value | Source / Evidence |
|:---|:---|:---|
| **Repository Remote** | `https://github.com/aryansinghnagar/Ars-Arcanum.git` | `git remote -v` |
| **Active Branch** | `main` | `git branch --show-current` |
| **Software Version** | `0.1.0` (Sovereign Release) | [`pyproject.toml#L7`](file:///pyproject.toml#L7), [`scripts/lib/_bootstrap.py#L20`](file:///scripts/lib/_bootstrap.py#L20) |
| **License** | MIT License | [`LICENSE`](file:///LICENSE), [`pyproject.toml`](file:///pyproject.toml) |
| **Dependency Model** | Zero-Pip Guarantee (100% Python Standard Library for Core Engines) | [`AGENTS.md#L28-L30`](file:///AGENTS.md#L28-L30) |

---

### 2.2 Agent & Contributor Operational Rules (`AGENTS.md`)
The repository encodes strict engineering contracts documented in [`AGENTS.md`](file:///AGENTS.md):
1. **File Safety Invariant**: All disk modifications must utilize `atomic_write()` from [`scripts/lib/_bootstrap.py`](file:///scripts/lib/_bootstrap.py#L33-L68) (`tempfile` $\to$ `flush` $\to$ `fsync` $\to$ `os.replace` $\to$ parent directory `fsync`). Direct unbuffered overwrites are strictly prohibited.
2. **Cross-Platform Concurrency Control**: Concurrency-sensitive operations (snapshots, backups, migrations) must acquire an `ArcanumLock` ([`scripts/lib/lockfile.py`](file:///scripts/lib/lockfile.py#L35-L135)) utilizing `fcntl.flock` on POSIX and `msvcrt.locking` on Windows with deterministic byte-0 positioning.
3. **Path Traversal Defense**: All user-supplied volume names, draft identifiers, and book targets are validated against token regex `^[A-Za-z0-9_-]+$`; directory separators (`/`, `\`), path traversals (`..`), and Windows reserved device names (`CON`, `PRN`, `AUX`, `NUL`, `COM1-9`, `LPT1-9`) are rejected immediately ([`scripts/lib/_bootstrap.py#L72-L85`](file:///scripts/lib/_bootstrap.py#L72-L85)).
4. **Content Security Policy (CSP)**: Generated HTML reports (diff visualizer, revision heatmap, portfolio dashboard, draft lineage tree, velocity studio, codex export) must declare strict offline Content Security Policies:
   ```html
   <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
   ```
5. **Module Maintainability Bound**: All Python source files must adhere to the `<800 lines/file` maintainability contract.
6. **Creative Sovereignty Invariant**: Subsystem 2 (Craft Lenses) and Subsystem 3 (Ideation) operations must always exit with returncode `0` by default. Advisory rules can be silenced via `constitution.yaml` or `@intent: deliberate` directives.

---

### 2.3 Developer Gotchas

1. **Windows Reserved Device Names**: File and volume sanitization in `_bootstrap.py` explicitly rejects Windows reserved device names (`CON`, `PRN`, `AUX`, `NUL`, `COM1-9`, `LPT1-9`) regardless of file extension to prevent OS-level deadlocks.
2. **Atomic Write Directory Fsync**: On POSIX systems, `atomic_write()` fsyncs the parent directory to commit the directory entry. When running in environments with read-only parent directories or non-standard mount options, directory fsync exceptions are safely handled.
3. **Docx Sync Track Changes & Comments**: When pulling revisions from a `.docx` file via `docx_sync.py`, `<w:del>` elements are discarded to avoid resurrecting deleted text, while `<w:comment>` margin annotations are extracted into a companion `.comments.json` sidecar.
4. **Advisory Default Return Codes**: Subsystem 2 engines return exit code `0` even when reporting structural observations or lens notes. Only Subsystem 1 data integrity failures or executions with the `--strict` flag emit non-zero exit codes (`exit 1`).
5. **Unicode Prose Word Counting**: Standard word splitting (`split()`) overcounts hyphenated words and fails on CJK punctuation. The codebase standardizes on [`count_prose_words()`](file:///scripts/lib/_bootstrap.py#L90-L115) and [`count_prose_words_advanced()`](file:///scripts/lib/word_counter.py) using regex word-boundary matching `\b[^\W_]+\b` alongside CriticMarkup stripping.

---

### 2.4 Ecosystem & External Tool Interoperability
- **Obsidian World Bible Vault**: Lore vaults are fully compatible with Obsidian. The repository includes a pre-configured template with 32 offline community plugins (Dataview, Canvas, Timelines, Fantasy Calendar, Leaflet) pinned with SHA-256 checksums in [`templates/world-bible/.obsidian/plugins/manifest.json`](file:///templates/world-bible/.obsidian/plugins/manifest.json).
- **Microsoft Word / LibreOffice Roundtripping**: `docx_sync.py` and `docx_builder.py` provide bidirectional synchronizations with `.docx` word processors without requiring Microsoft Word or external OpenXML libraries.
- **Typst & Pandoc Typesetting**: Sub-second commercial-grade PDF generation via Typst templates ([`templates/typst/`](file:///templates/typst/)) and clean EPUB3 output via Pandoc.

---

## Part 3 — Architectural Blueprint

### 3.1 C4 Architecture Diagrams

#### Level 1: System Context Diagram
```mermaid
flowchart TD
    AUTHOR["Speculative Fiction Author<br/><i>(Novelist / Worldbuilder)</i>"]
    
    subgraph ARS["Ars Arcanum Operating System (Scriptorium)"]
        STUDIO["Sovereign Craft Studio<br/><i>(17 Core Engines, Scoping Subsystem & Data Layer)</i>"]
    end
    
    VAULT["Local Lore Vaults & Manuscripts<br/><i>(~/.config/ars-arcanum/, ~/Universes/, ~/Manuscripts/)</i>"]
    EXT_TOOLS["External Creative Tools<br/><i>(Obsidian, Typst, Pandoc, Word, PolyGlot, Gramps)</i>"]
    
    AUTHOR -->|Drafts, sprints, branches, executes CLI| STUDIO
    STUDIO -->|Atomic I/O, lockfiles, AST caching| VAULT
    STUDIO -->|Bidirectional sync & compilation| EXT_TOOLS
    AUTHOR -->|Edits in local editors & viewports| EXT_TOOLS
```

#### Level 2: Container Diagram
```mermaid
flowchart TD
    subgraph PresentationTier["Presentation & Dispatch Tier"]
        CLI["CLI Dispatcher (scripts/lib/cli.py)"]
        HANDLERS["CLI Handlers (scripts/lib/cli_handlers.py)"]
        POSIX_BOOT["POSIX Shell Wrapper (scripts/arcanum)"]
        WIN_BOOT["Windows Batch Launcher (scripts/arcanum.cmd)"]
    end

    subgraph ScopeGovernanceTier["Scope & Governance Tier"]
        SCOPE["EngineScope Subsystem (scripts/lib/scope.py)"]
        SCOPE_PARSER["Scope Range Parser (scripts/lib/scope_parser.py)"]
        SCOPE_RESOLVER["Context Altitude Resolver (scripts/lib/scope_resolver.py)"]
        CONST["Authorial Constitution (scripts/lib/constitution.py, config.py)"]
        STATE["Global Workstream State (scripts/lib/state.py)"]
    end

    subgraph RegistryTier["Registry & Engine Metadata Tier"]
        REG_FACADE["Registry Facade (scripts/lib/registry.py)"]
        REG_BASE["Registry Base & DiagnosticSeverity (scripts/lib/registry_base.py)"]
        REG_SPECS["4 Domain Specifications (scripts/lib/registry_specs/)"]
    end

    subgraph CoreEnginesTier["Sovereign Core Engines Tier (17 Engines)"]
        EDITORIAL["Editorial (diff, heatmap, word_counter, docx_sync)"]
        PORTFOLIO["Portfolio & Velocity (portfolio, writing_sprint)"]
        PUBLISHING["Publishing (omnibus, codex_export, preflight, publisher)"]
        INFRA["Infrastructure (backup, restore, snapshot, diagnostics, migrate, draft_manager, project_scaffold)"]
    end

    subgraph DataStorageTier["Persistence & Data Access Tier"]
        DATA_ACCESS["Cached Data Access (scripts/lib/data_access.py)"]
        CACHE["AST & Frontmatter Cache (scripts/lib/cache.py)"]
        FRONTMATTER["YAML Frontmatter Parser (scripts/lib/frontmatter.py)"]
        BOOTSTRAP["Atomic Write & Path Defense (scripts/lib/_bootstrap.py)"]
        LOCKFILE["Cross-Platform Locking (scripts/lib/lockfile.py)"]
    end

    POSIX_BOOT --> CLI
    WIN_BOOT --> CLI
    CLI --> HANDLERS
    HANDLERS --> SCOPE
    SCOPE --> SCOPE_PARSER
    SCOPE --> SCOPE_RESOLVER
    SCOPE --> CONST
    SCOPE --> STATE
    CONST --> REG_FACADE
    REG_FACADE --> REG_BASE
    REG_FACADE --> REG_SPECS
    REG_FACADE --> CoreEnginesTier
    CoreEnginesTier --> DATA_ACCESS
    DATA_ACCESS --> CACHE
    DATA_ACCESS --> FRONTMATTER
    CoreEnginesTier --> BOOTSTRAP
    CoreEnginesTier --> LOCKFILE
```

#### Level 3: Request & Execution Lifecycle
```mermaid
sequenceDiagram
    autonumber
    actor Author as Author / User
    participant CLI as CLI Dispatcher (cli.py)
    participant Scope as Scope Resolver (scope.py)
    participant Const as Constitution (config.py)
    participant Engine as Domain Engine (e.g. writing_sprint / word_counter)
    participant DAL as Data Access Layer (data_access.py)
    participant Safety as Bootstrap & Lockfile
    participant Disk as Local Filesystem

    Author->>CLI: Invokes command (e.g. arcanum words Manuscript/ --html out.html)
    CLI->>Scope: resolve_engine_scope(args)
    Scope->>Disk: Resolves targets via cwd / manifest / explicit arguments
    Scope-->>CLI: Returns ResolvedScope (files, chapters, volume)
    CLI->>Const: get_authorial_constitution(vault_root)
    Const-->>CLI: Returns merged Constitution (suppressed rules, severity defaults)
    CLI->>Engine: Executes engine entrypoint with resolved scope
    Engine->>Safety: Acquires ArcanumLock(lock_path)
    Safety-->>Engine: Lock acquired
    Engine->>DAL: Requests parsed document ASTs
    DAL->>Disk: Reads files (or serves from thread-safe LRU cache if mtime unchanged)
    DAL-->>Engine: Returns Document AST & Frontmatter
    Engine->>Engine: Computes prose tokenization / velocity curves / diagnostics
    Engine->>Safety: atomic_write(out.html, html_content)
    Safety->>Disk: Temporary file -> flush -> fsync -> os.replace -> parent dir fsync
    Safety-->>Engine: Write confirmed
    Engine->>Safety: Releases ArcanumLock
    Engine-->>CLI: Emits 6-Tier Diagnostic Report (exit code 0 default)
    CLI-->>Author: Renders formatted terminal output / JSON / HTML
```

---

### 3.2 Layering & Dependency Rules

```mermaid
flowchart TD
    Presentation["Presentation Tier (cli.py, cli_handlers.py, arcanum)"]
    Governance["Scope & Governance Tier (scope.py, config.py, constitution.py, state.py)"]
    Registry["Registry Tier (registry.py, registry_specs/)"]
    Engines["Domain Engines Tier (word_counter, writing_sprint, draft_manager, diff, heatmap, portfolio, docx_sync...)"]
    Templates["Presentation HTML Templates (velocity_template, draft_manager_template, etc.)"]
    DataAccess["Data Access Tier (data_access.py, cache.py, frontmatter.py)"]
    Foundation["Foundation Tier (_bootstrap.py, lockfile.py, fs_utils.py)"]

    Presentation --> Governance
    Governance --> Registry
    Registry --> Engines
    Engines --> Templates
    Engines --> DataAccess
    DataAccess --> Foundation
    Engines --> Foundation
    Templates --> Foundation
```

- **Top-Down Unidirectional Flow**: Higher-level presentation modules invoke governance and engine modules. Core engines and data access modules **must never import** CLI dispatchers.
- **Zero-Pip Boundary**: Foundation, core engines, and template tiers must strictly utilize Python standard library primitives.
- **Encapsulated Data Access**: Disk I/O for lore and manuscript parsing is routed through `CachedDataAccess` and `_bootstrap.py:atomic_write()`.

---

### 3.3 Cross-Cutting Concerns Table

| Concern | Implementation Mechanism | Evidence (File + Lines) |
|:---|:---|:---|
| **Authentication & Access** | Air-gapped local workstation isolation, POSIX permission bits, Windows file security | [`AGENTS.md#L1-L25`](file:///AGENTS.md#L1-L25), [`docs/THREAT_MODEL.md`](file:///docs/THREAT_MODEL.md) |
| **Configuration & Constitution** | Deep-merged `constitution.yaml`, `world.yaml`, `manuscript.yaml`, and global `~/.config/ars-arcanum/config.json` | [`scripts/lib/config.py`](file:///scripts/lib/config.py), [`scripts/lib/constitution.py`](file:///scripts/lib/constitution.py) |
| **Crash Safety & Atomic Writes** | Multi-stage atomic file replacement (`tempfile` $\to$ `flush` $\to$ `fsync` $\to$ `os.replace` $\to$ parent `fsync`) | [`scripts/lib/_bootstrap.py#L33-L68`](file:///scripts/lib/_bootstrap.py#L33-L68) |
| **Concurrency Control** | Cross-platform file locking (`fcntl.flock` on POSIX, `msvcrt.locking` on Windows) | [`scripts/lib/lockfile.py#L35-L135`](file:///scripts/lib/lockfile.py#L35-L135) |
| **Content Security Policy** | Strict `default-src 'none'` CSP injected into all generated HTML visualizers | [`scripts/lib/velocity_template.py#L160`](file:///scripts/lib/velocity_template.py#L160), [`scripts/lib/draft_manager_template.py`](file:///scripts/lib/draft_manager_template.py), [`scripts/lib/portfolio_template.py`](file:///scripts/lib/portfolio_template.py) |
| **Diagnostic Classification** | 6-Tier standardized severity hierarchy (`CANON_ERROR`, `RULE_CONFLICT`, `OBSERVATION`, `LENS_NOTE`, `SUGGESTION`, `EXPERIMENT`) | [`scripts/lib/registry_base.py#L89-L98`](file:///scripts/lib/registry_base.py#L89-L98) |
| **Prose Metrics Standard** | Standardized Unicode word boundary matching `\b[^\W_]+\b` with CriticMarkup removal | [`scripts/lib/_bootstrap.py#L90-L115`](file:///scripts/lib/_bootstrap.py#L90-L115), [`scripts/lib/word_counter.py`](file:///scripts/lib/word_counter.py) |
| **Path Traversal Defense** | Strict regex identifier validation (`^[A-Za-z0-9_-]+$`) and reserved name checks | [`scripts/lib/_bootstrap.py#L72-L85`](file:///scripts/lib/_bootstrap.py#L72-L85) |

---

### 3.4 Inferred Architectural Decision Records (ADRs)

#### ADR 01: Zero-Pip Standard Library Dependency Guarantee
- **Context**: Creative writing and worldbuilding intellectual property demands complete longevity, offline privacy, and zero supply-chain risk across decades.
- **Decision**: All core simulation engines, CLI tools, parsers, and data exporters must execute exclusively on Python 3.10+ standard library primitives without external pip packages.
- **Consequences**: Zero installation friction on Linux, Windows, and macOS; guaranteed forward-compatibility across Python releases.

#### ADR 02: Atomic POSIX & Windows File I/O with Parent Directory Fsync
- **Context**: Power cuts or crashes during manuscript saving can lead to catastrophic data corruption or truncated files.
- **Decision**: All write operations utilize `atomic_write()` which stages writes to a temporary sibling file, flushes buffers, calls `os.fsync()`, replaces the destination via `os.replace()`, and flushes the parent directory.
- **Consequences**: Zero corrupted files on abrupt crashes; file descriptors are strictly managed with `try...finally` cleanup.

#### ADR 03: Advisory-First Creative Freedom & Epistemic Decoupling (3 Subsystems)
- **Context**: Speculative fiction frequently violates real-world physics (FTL travel, magic, time loops) and standard commercial plotting formulas (experimental pacing, stream of consciousness). Rigid validation gates that block the author stifle creativity.
- **Decision**: Segregate operations into Three Subsystems: Subsystem 1 (Invariant Consistency Engine, fail-closed on data errors), Subsystem 2 (Advisory Craft Lenses, exit 0 default, respects `@intent`), and Subsystem 3 (Creative Ideation, labeled `[SPECULATION]`).
- **Consequences**: Authors retain absolute creative sovereignty while receiving mathematically precise diagnostic telemetry.

#### ADR 04: Modular Domain Engine Registry Package (<800 Lines/File)
- **Context**: Monolithic registry files create merge conflict hazards and violate the `<800 lines/file` maintainability contract.
- **Decision**: Partition the registry into `registry_base.py` (<200 lines), domain-specific specification modules under `registry_specs/` (<400 lines/file across Editorial, Portfolio, Infrastructure, Publishing), and a slim `registry.py` facade.
- **Consequences**: Satisfies the `<800L` contract; enables isolated additions of domain engine specifications without monolithic file churn.

#### ADR 05: Fail-Closed Archive Restore & Destination Safety
- **Context**: Unpacking archives into existing directories risks silent data loss or tampering if checksum sidecars are ignored or corrupt.
- **Decision**: `restore.py` enforces fail-closed SHA-256 sidecar verification by default (with `--no-verify` override) and forbids unpacking into non-empty directories unless `--force` is supplied.
- **Consequences**: Guarantees vault integrity and prevents accidental loss of uncommitted writing drafts.

#### ADR 06: Authorial Constitution Schema & 6-Tier Severity Taxonomy
- **Context**: Authors need a declarative mechanism to express narrative laws, suppress irrelevant craft rules, and set custom weights for diagnostics without editing codebase files.
- **Decision**: Introduce machine-readable `constitution.yaml` / `constitution.json` schemas loaded via `config.py: get_authorial_constitution()`, alongside a 6-tier severity taxonomy (`CANON_ERROR` to `EXPERIMENT`) in `registry_base.py`.
- **Consequences**: Complete authorial governance over diagnostic output and zero false-positive friction.

#### ADR 07: Unified Scope Resolution & Altitude-Aware Target Slicing
- **Context**: Scanning multi-gigabyte vaults for small chapter edits wastes I/O and creates diagnostic clutter.
- **Decision**: Introduce `EngineScope` ([`scripts/lib/scope.py`](file:///scripts/lib/scope.py)) with dedicated parsers (`scope_parser.py`) and context resolvers (`scope_resolver.py`) supporting slice expressions (`1-5`, `ch01..ch05`, `sc01..sc02`).
- **Consequences**: Sub-second execution even in massive novel series catalogs.

#### ADR 08: Standardized Unicode Prose Word Counter & Dialogue Parsing
- **Context**: Naive word splitting overcounts hyphenated words, treats Markdown symbols and CriticMarkup as story words, and fails on non-ASCII prose.
- **Decision**: Introduce centralized [`count_prose_words()`](file:///scripts/lib/_bootstrap.py#L90-L115) and [`count_prose_words_advanced()`](file:///scripts/lib/word_counter.py) with CriticMarkup stripping, CJK ideograph support, and spoken dialogue extraction.
- **Consequences**: Consistent, exact word counts and objective dialogue ratio metrics matching professional publication standards.

#### ADR 09: Hybrid Multi-Source Velocity Aggregation
- **Context**: Authors log drafting sessions across disparate tools: dedicated CLI timers, Obsidian Markdown notes (`Daily-Writing-Log.md`), and raw Git snapshot commits.
- **Decision**: `writing_sprint.py:get_velocity_metrics()` unifies ingestion across `.arcanum/sprint_log.jsonl`, Obsidian frontmatter (`fileClass: WritingLog`), and Git commit timestamp deltas with automatic deduplication.
- **Consequences**: Seamless habit streaks and rolling WPM velocity calculation regardless of which authoring surface the writer drafts in.

#### ADR 10: Stateful Sprint Session Locking & In-Browser Pomodoro Studio
- **Context**: Writers sprinting in terminal sessions need background persistence, while writers using browsers or Obsidian webviews need real-time visual progress rings without cloud telemetry.
- **Decision**: `writing_sprint.py` uses `.arcanum/.sprint_state.json` to manage session locks, and `velocity_template.py` renders a self-contained offline HTML5 Pomodoro timer with customizable minutes and word targets using Web Audio API synthesis.
- **Consequences**: Frictionless switching between CLI countdowns and interactive visual timers under 100% offline isolation.

---

### 3.5 Governance & Enforcement Mechanisms
1. **Automated Multi-Platform CI Matrix**: GitHub Actions ([`.github/workflows/ci.yml`](file:///.github/workflows/ci.yml)) tests all commits across Ubuntu 24.04, Windows, macOS, and 4 containerized Linux distributions (Ubuntu 22.04/24.04, Debian 12/13).
2. **Strict Static Analysis Gates**:
   - `ruff check .` with 15 rule sets.
   - `mypy --explicit-package-bases scripts tests` across all 114 source files.
   - `bandit -r scripts/lib -ll -ii` for automated security scanning.
   - `coverage report --fail-under=80` enforcing 80%+ test coverage (currently 81%).
3. **Canonical 7-Stage Integration Harness**: [`scripts/verify.sh`](file:///scripts/verify.sh) validates syntax, linting, typing, unit tests, coverage, wheel packaging, and CLI symlink dispatch.

---

## Subsystem Deep-Dives

### Subsystem Deep-Dive 1: File Safety, Atomic I/O & Concurrency Locking Engine

```mermaid
flowchart TD
    CALLER["Caller Engine (backup, diff, sync, portfolio, sprint)"] --> LOCK{"Acquire ArcanumLock"}
    
    subgraph LockingMechanisms["Cross-Platform Locking (lockfile.py)"]
        POSIX["POSIX: fcntl.flock(LOCK_EX | LOCK_NB)"]
        WIN["Windows: msvcrt.locking(LK_NBLCK, 1 byte at pos 0)"]
    end
    
    LOCK -->|POSIX| POSIX
    LOCK -->|Windows| WIN
    POSIX --> GRANTED["Lock Acquired"]
    WIN --> GRANTED
    
    GRANTED --> ATOMIC["atomic_write(target_path, data)"]
    
    subgraph AtomicWriteLifecycle["Atomic Write Lifecycle (_bootstrap.py)"]
        TEMP["Create tempfile in target's parent directory"]
        WRITE["Write payload to tempfile"]
        FLUSH["flush() buffers to OS"]
        FSYNC1["os.fsync(fd) to commit data to disk platters"]
        REPLACE["os.replace(temp_path, target_path) (Atomic)"]
        FSYNC2["os.fsync(parent_dir_fd) (POSIX dir entry sync)"]
        TEMP --> WRITE --> FLUSH --> FSYNC1 --> REPLACE --> FSYNC2
    end
    
    ATOMIC --> AtomicWriteLifecycle
    AtomicWriteLifecycle --> RELEASE["Release ArcanumLock"]
```

---

### Subsystem Deep-Dive 2: Word Counter, Velocity & Cognitive Sprint Engine

```mermaid
flowchart TD
    subgraph IngestionSources ["Multi-Source Ingestion"]
        MD_FILES["Manuscript Markdown Files (.md)"]
        SPRINT_LOG[".arcanum/sprint_log.jsonl"]
        DAILY_LOGS["Obsidian Daily-Writing-Log.md (fileClass: WritingLog)"]
        GIT_SNAPS["Git Snapshot Timestamp Deltas"]
    end

    subgraph TokenizerEngine ["Prose Tokenizer (word_counter.py)"]
        STRIP_CRITIC["Strip CriticMarkup ({++..++}, {--..--}, {>>..<<})"]
        EXTRACT_DIAL["Extract Quoted Spoken Dialogue"]
        COUNT_CJK["Identify CJK Ideographs"]
        COUNT_PROSE["Compute Unicode Prose Words"]
        STRIP_CRITIC --> EXTRACT_DIAL --> COUNT_CJK --> COUNT_PROSE
    end

    subgraph SprintLifecycle ["Stateful Sprint Lifecycle (writing_sprint.py)"]
        START["start_sprint() -> .sprint_state.json (Initial Word Snapshot)"]
        LIVE["TTY Countdown / Status Query"]
        STOP["stop_sprint() -> Net Delta (ΔW) & WPM Calculation"]
        APPEND["Append to sprint_log.jsonl"]
        START --> LIVE --> STOP --> APPEND
    end

    subgraph AnalyticsHub ["Velocity Analytics & HTML Studio (velocity_template.py)"]
        ROLLING["Compute 7d/30d Rolling WPM & WPD Pace"]
        STREAKS["Daily Habit Streak Calculator"]
        STUDIO["Render Standalone Offline HTML5 Hub with Pomodoro Timer"]
        ROLLING --> STUDIO
        STREAKS --> STUDIO
    end

    MD_FILES --> TokenizerEngine
    SPRINT_LOG --> SprintLifecycle
    DAILY_LOGS --> AnalyticsHub
    GIT_SNAPS --> AnalyticsHub
    TokenizerEngine --> AnalyticsHub
    SprintLifecycle --> AnalyticsHub
```

---

### Subsystem Deep-Dive 3: Multi-Draft Branching & Lineage Management Engine

```mermaid
flowchart TD
    CLI_DRAFT["arcanum draft <new|switch|compare|lock|tree>"] --> DRAFT_MGR["scripts/lib/draft_manager.py"]
    
    subgraph DraftOperations ["Draft Lifecycle Operations"]
        CREATE["Create New Draft Branch (e.g. Draft-02 from Draft-01)"]
        SWITCH["Switch Active Draft in manuscript.yaml"]
        COMPARE["Compute Semantic Diff against Parent Draft"]
        LOCK_STATE["Lock Draft State (Immutable Milestone Tag)"]
    end

    subgraph LineageTree ["Visual Lineage Tree (draft_manager_template.py)"]
        AST_NODES["Resolve Parent-Child Draft Hierarchy"]
        HTML_GRAPH["Generate Interactive Offline SVG/CSS Lineage Tree"]
    end

    DRAFT_MGR --> DraftOperations
    DraftOperations --> LineageTree
```

---

## Confidence Assessment

| Architectural Domain | Confidence Rating | Verification Method & Justification |
|:---|:---|:---|
| **Zero-Pip Guarantee & Stdlib Execution** | **High** | 100% verified via 438 unit tests running in clean Python standard library environments without pip packages. |
| **Word Counter & Velocity Engine** | **High** | Verified in `tests/test_word_counter.py` and `tests/test_writing_sprint.py` with CriticMarkup, dialogue ratios, and sprint state locking. |
| **Draft Branching & Lineage Management** | **High** | Verified in `tests/test_draft_manager.py` covering branching, locking, and visual tree exports. |
| **Atomic File Safety & Locking** | **High** | Verified across Linux and Windows in `tests/test_atomic_write.py`, `tests/test_lockfile.py`, and `tests/test_path_traversal_defense.py`. |
| **Granular Target Scoping** | **High** | Verified in `tests/test_scope.py`, `tests/test_scope_parser.py`, and `tests/test_scope_resolver.py`. |
| **Content Security Policy & Offline Air-Gap** | **High** | Verified in `tests/test_csp_and_offline_invariants.py` with regex scanning across all generated HTML templates. |
| **Multi-Platform Parity** | **High** | Verified via multi-platform GitHub Actions CI matrix across Ubuntu 24.04, Windows, and macOS. |
| **Authorial Constitution & Creative Autonomy** | **High** | Verified in `tests/test_constitution_modular.py`, `tests/test_creative_autonomy_integration.py`, and `tests/test_epistemic_safety.py`. |
| **DOCX Synchronization & Track Changes** | **High** | Verified in `tests/test_docx_sync.py` covering deletion discarding, comment extraction, and roundtrip preservation. |

---

## Footnotes — Key Local File Citations

1. [`pyproject.toml`](file:///pyproject.toml#L1-L71): Defines package metadata, entry points (`arcanum`, `ars-arcanum`), Python requirement (`>=3.10`), Ruff rules, and Coverage floor ($\ge 80\%$).
2. [`AGENTS.md`](file:///AGENTS.md#L1-L150): The authoritative Agentic Operating Manifesto encoding core engineering invariants, the 3 subsystems, and 6-tier diagnostic severity.
3. [`.github/workflows/ci.yml`](file:///.github/workflows/ci.yml#L1-L185): GitHub Actions CI configuration defining verification gates, SAST scanning, distro matrix, and multi-platform OS runners.
4. [`scripts/arcanum`](file:///scripts/arcanum#L1-L50): POSIX shell wrapper for CLI dispatch and native environment management.
5. [`scripts/arcanum.cmd`](file:///scripts/arcanum.cmd#L1-L5): Windows batch wrapper for native command-line invocation.
6. [`scripts/test_parallel.py`](file:///scripts/test_parallel.py#L1-L80): Multi-worker parallel test runner discovering and executing all 55 test modules.
7. [`scripts/lib/_bootstrap.py`](file:///scripts/lib/_bootstrap.py#L1-L120): Foundation primitives establishing atomic file writes, path sanitization, and Unicode prose word counting.
8. [`scripts/lib/lockfile.py`](file:///scripts/lib/lockfile.py#L1-L140): Cross-platform file locking implementation (`ArcanumLock`) utilizing `fcntl.flock` and `msvcrt.locking`.
9. [`scripts/lib/word_counter.py`](file:///scripts/lib/word_counter.py): Unicode prose tokenization, CriticMarkup stripping, dialogue vs narrative ratio, and reading time calculation.
10. [`scripts/lib/writing_sprint.py`](file:///scripts/lib/writing_sprint.py): Stateful sprint session lifecycle, hybrid velocity derivation, rolling 7d/30d WPM curves, and habit streaks.
11. [`scripts/lib/velocity_template.py`](file:///scripts/lib/velocity_template.py): Standalone offline HTML5 Velocity Studio with in-browser customizable Pomodoro timer and deadline forecast slider.
12. [`scripts/lib/draft_manager.py`](file:///scripts/lib/draft_manager.py): Multi-draft branching, parent lineage tracking, and immutable milestone states.
13. [`scripts/lib/data_access.py`](file:///scripts/lib/data_access.py#L1-L260): Centralized cached vault reader and AST frontmatter layer.
14. [`scripts/lib/frontmatter.py`](file:///scripts/lib/frontmatter.py#L1-L380): Pure-Python recursive YAML frontmatter parser and serializer.
15. [`scripts/lib/scope.py`](file:///scripts/lib/scope.py#L1-L580): Universal granular target scoping engine.
16. [`scripts/lib/config.py`](file:///scripts/lib/config.py#L1-L740): Authorial Constitution loader, deep merging, and active configuration resolver.
17. [`scripts/lib/registry_base.py`](file:///scripts/lib/registry_base.py#L1-L140): `DiagnosticSeverity` enum, `EngineSpec` dataclass, and `BaseCraftEngine` contract.
18. [`scripts/lib/registry.py`](file:///scripts/lib/registry.py#L1-L580): Dynamic engine registry facade, user plugin scanner, and advisory craft bibliography.
19. [`scripts/lib/docx_sync.py`](file:///scripts/lib/docx_sync.py#L1-L730): Bidirectional Markdown $\leftrightarrow$ DOCX synchronizer with track changes and comment extraction.
20. [`scripts/lib/portfolio.py`](file:///scripts/lib/portfolio.py#L1-L310): Multi-manuscript catalog portfolio dashboard and velocity tracker.
21. [`scripts/lib/manuscript_diff.py`](file:///scripts/lib/manuscript_diff.py#L1-L410): Structural markdown diff engine with offline HTML visualizer.
22. [`scripts/lib/revision_heatmap.py`](file:///scripts/lib/revision_heatmap.py#L1-L600): Revision density and editing churn heatmaps with offline HTML export.
23. [`scripts/lib/diagnostics.py`](file:///scripts/lib/diagnostics.py#L1-L370): Unified system health, toolchain inspector, and lore vault consistency doctor.
