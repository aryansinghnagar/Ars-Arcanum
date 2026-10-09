# Ars Arcanum (Scriptorium) — Definitive System Architecture & Technical Blueprint
> **Sovereign Local-First Authoring Operating System (GPA 4.0/4.0 — Grade A+)** | Release v0.1.0 (Beta)  
> *Authoritative Onboarding Reference, System Blueprint & Verification Baseline*

---

## Part 1 — Whole-Repository Technical Deep-Dive

### 1.1 Executive System Identity
**Ars Arcanum** (code-named *Scriptorium*) is a sovereign, local-first authoring platform and craft studio designed for speculative fiction authors, novelists, and narrative designers ([`README.md#L1-L25`](file:///README.md#L1-L25)). It provides a complete creative production pipeline — spanning world-bible lore management, manuscript drafting, editorial telemetry (structural diffs, editing heatmaps, catalog portfolio), bidirectional DOCX synchronization, and 1-click publishing (print-ready PDF, EPUB, submission DOCX, omnibus) — executing 100% offline with zero cloud dependencies, zero external network telemetry, and zero `pip` packages required for core engines ([`AGENTS.md#L1-L35`](file:///AGENTS.md#L1-L35)).

### 1.2 Tech-Stack Detection Table

| Layer / Subsystem | Technology | Purpose | Evidence (File + Lines) |
|---|---|---|---|
| **Core Runtime** | Python 3.10+ (Standard Library) | Primary execution runtime for 14 sovereign core engines | [`pyproject.toml#L10-L15`](file:///pyproject.toml#L10-L15), [`AGENTS.md#L20-L40`](file:///AGENTS.md#L20-L40) |
| **Package / Build System** | Setuptools (`setuptools>=61.0`) | Standard wheel packaging and console entry point dispatch (`arcanum`, `ars-arcanum`) | [`pyproject.toml#L1-L30`](file:///pyproject.toml#L1-L30) |
| **CLI Dispatchers** | POSIX Bash + Windows CMD + Python Dispatcher | Authoritative multi-platform CLI dispatch with fuzzy error resolution, retirement doctrine guidance, and registry plugins | [`scripts/arcanum#L1-L50`](file:///scripts/arcanum#L1-L50), [`scripts/arcanum.cmd#L1-L5`](file:///scripts/arcanum.cmd#L1-L5), [`scripts/lib/cli.py#L1-L120`](file:///scripts/lib/cli.py#L1-L120) |
| **Storage & Data Access** | Plaintext Markdown, YAML Frontmatter | Local-first atomic document store, AST cache, and fast frontmatter index | [`scripts/lib/_bootstrap.py#L30-L75`](file:///scripts/lib/_bootstrap.py#L30-L75), [`scripts/lib/data_access.py#L1-L150`](file:///scripts/lib/data_access.py#L1-L150) |
| **Concurrency Control** | `ArcanumLock` (`fcntl.flock` on POSIX, `msvcrt.locking` on Windows) | Cross-platform file locking for backup, restore, and synchronization routines | [`scripts/lib/lockfile.py#L1-L110`](file:///scripts/lib/lockfile.py#L1-L110) |
| **Publishing Pipeline** | Typst CLI (`>=0.11.0`), Pandoc (`>=2.19.x`) | Commercial PDF typesetting with genre presets, EPUB3 compilation, DOCX AST translation, and omnibus creation | [`scripts/lib/omnibus.py#L1-L120`](file:///scripts/lib/omnibus.py#L1-L120), [`docs/COMPATIBILITY.md#L1-L30`](file:///docs/COMPATIBILITY.md#L1-L30) |
| **External Integrations** | Obsidian (32 pre-configured offline plugins), PolyGlot, Gramps, Wonderdraft, Celestia, StarGen, Pandoc, Typst, novelWriter | Full external creative toolchain, Markdown World Bible vault interface, and distraction-free novel project drafting | [`templates/world-bible/.obsidian/plugins/manifest.json`](file:///templates/world-bible/.obsidian/plugins/manifest.json), [`docs/guides/EXTERNAL_TOOLS_AND_PLUGINS.md`](file:///docs/guides/EXTERNAL_TOOLS_AND_PLUGINS.md) |

### 1.3 Entry Points

1. **POSIX Shell Wrapper**: [`scripts/arcanum`](file:///scripts/arcanum#L1-L50) (symlink-dereferencing POSIX CLI wrapper).
2. **Windows Command Wrapper**: [`scripts/arcanum.cmd`](file:///scripts/arcanum.cmd#L1-L5) (native Windows batch entry point calling `scripts/lib/cli.py`).
3. **Authoritative Python Dispatcher**: [`scripts/lib/cli.py`](file:///scripts/lib/cli.py#L1-L100) (pure Python entry point with dynamic plugin registry).
4. **Parallel Test Runner**: [`scripts/test_parallel.py`](file:///scripts/test_parallel.py) (high-speed parallel test execution).

---

### 1.4 Commands & Verification Inventory

| Command | Purpose | Verification Evidence | CI Enforcement Status |
|---|---|---|---|
| `python -m unittest discover tests` | Run complete unit and regression test suite (336+ tests across 48 modules) | [`tests/test_*.py`](file:///tests/) | **Enforced in CI** ([`.github/workflows/ci.yml#L36`](file:///.github/workflows/ci.yml#L36)) |
| `python scripts/test_parallel.py` | Run parallel multi-core test suite across CPU workers (~2.5s execution) | [`scripts/test_parallel.py`](file:///scripts/test_parallel.py) | Local Developer / Fast CI |
| `ruff check .` | Strict linting across 9 rule families (`E`, `F`, `B`, `S`, `UP`, `SIM`, `I`, `RUF`, `C901`) | [`pyproject.toml#L15-L35`](file:///pyproject.toml#L15-L35) | **Enforced in CI** ([`.github/workflows/ci.yml#L33`](file:///.github/workflows/ci.yml#L33)) |
| `mypy --explicit-package-bases scripts tests` | Static type checking with `check_untyped_defs = True` (90 source files clean) | [`mypy.ini#L1-L25`](file:///mypy.ini#L1-L25) | **Enforced in CI** ([`.github/workflows/ci.yml#L34`](file:///.github/workflows/ci.yml#L34)) |
| `coverage run -m unittest discover tests; coverage report --fail-under=80` | Measure and enforce aggregate test coverage threshold ($\ge 80\%$) | [`pyproject.toml#L35-L45`](file:///pyproject.toml#L35-L45) | **Enforced in CI** ([`.github/workflows/ci.yml#L38`](file:///.github/workflows/ci.yml#L38)) |
| `bash scripts/verify.sh` | Canonical 7-stage master integration and packaging verification harness | [`scripts/verify.sh#L1-L150`](file:///scripts/verify.sh#L1-L150) | **Enforced in CI** ([`.github/workflows/ci.yml#L39`](file:///.github/workflows/ci.yml#L39)) |
| `bash scripts/setup_arcanum.sh` | Automated POSIX system installer (packages, fonts, Typst, launchers) | [`scripts/setup_arcanum.sh#L1-L100`](file:///scripts/setup_arcanum.sh#L1-L100) | Local Developer / User Script |
| `powershell -ExecutionPolicy Bypass -File scripts\setup_arcanum.ps1` | Automated Windows 1-click system installer (workspaces, shortcuts, tasks) | [`scripts/setup_arcanum.ps1#L1-L80`](file:///scripts/setup_arcanum.ps1#L80) | Local Developer / User Script |
| `pip install -e .` | Editable development package installation | [`pyproject.toml#L1-L30`](file:///pyproject.toml#L1-L30) | **Enforced in CI** ([`.github/workflows/ci.yml#L32`](file:///.github/workflows/ci.yml#L32)) |

---

### 1.5 Directory Layout & Responsibilities

```
.
├── .github/                   # GitHub Actions CI/CD workflows and automated quality gates
├── configs/                   # Systemd units, LeechBlock distraction rules, and linter configs
├── docs/                      # Comprehensive system documentation and domain engine manuals
│   ├── codebase/              # Architectural blueprints, tech stack, testing, and conventions
│   └── guides/                # Author operational guides (backup, distraction control, typography, plugins)
├── launchers/                 # XDG desktop application entry points (.desktop files)
├── scripts/                   # Core application codebase and command executables
│   ├── arcanum                # POSIX shell entrypoint wrapper
│   ├── arcanum.cmd            # Native Windows batch launcher
│   ├── test_parallel.py       # High-performance parallel test runner
│   └── lib/                   # Standard-library core engines and craft modules (<800 lines/file)
│       ├── _bootstrap.py      # Atomic write, path validation, and system primitives
│       ├── cli.py             # Authoritative cross-platform CLI dispatcher
│       ├── cli_handlers.py    # CLI handler routing with graceful retirement doctrine guidance
│       ├── data_access.py     # Centralized cached vault reader and AST frontmatter layer
│       ├── scope.py           # Universal granular target scoping engine
│       ├── registry_base.py   # Core EngineSpec dataclasses and BaseCraftEngine
│       ├── registry_specs/    # Domain engine metadata specifications (4 active domain modules)
│       ├── manuscript_diff.py # Structural markdown diff engine with HTML visualizer
│       ├── revision_heatmap.py# Revision density and editing churn heatmaps with HTML export
│       ├── portfolio.py       # Multi-manuscript author portfolio tracker & standalone HTML dashboard
│       ├── docx_sync.py       # Two-way roundtrip Markdown <-> DOCX synchronizer
│       ├── docx_builder.py    # Zero-dependency standard submission format DOCX builder
│       ├── importer.py        # Universal multi-format manuscript & lore importer
│       ├── diagnostics.py     # Unified system health, toolchain & world vault consistency doctor
│       ├── migrate.py         # Schema and directory migration engine with automated backup
│       ├── preflight.py       # Pre-compilation validation & publication gatekeeper
│       ├── codex_export.py    # Standalone offline HTML world codex static site generator
│       ├── omnibus.py         # Multi-volume series omnibus compiler
│       ├── backup.py          # Pure-Python standalone verified .tar.gz archive engine
│       ├── restore.py         # Pure-Python verified archive restoration with path traversal defense
│       └── snapshot.py        # Pure-Python Git milestone snapshot versioning engine
├── templates/                 # Scaffolding templates for World Bibles, manuscripts, and universes
└── tests/                     # Comprehensive unittest suite across all domain engines (336+ tests)
```

---

### 1.6 Deployment & Runtime Surface

| Runtime / Tool | Version Pin | Source of Truth | Verification Method |
|---|---|---|---|
| **Python** | `3.10`, `3.11`, `3.12`, `3.13`, `3.14` | [`pyproject.toml#L10-L15`](file:///pyproject.toml#L10-L15), [`.github/workflows/ci.yml#L18`](file:///.github/workflows/ci.yml#L18) | Matrix test discovery |
| **Typst CLI** | `0.14.2` (Pinned musl binary + SHA-256) | [`scripts/setup_arcanum.sh#L317-L320`](file:///scripts/setup_arcanum.sh#L317-L320) | Hardcoded digest verification |
| **Pandoc** | `>=2.19.x` (Tested up to `3.7.x`) | [`docs/COMPATIBILITY.md#L9-L16`](file:///docs/COMPATIBILITY.md#L9-L16) | `pandoc --version` check |
| **Obsidian Plugins** | 32 Pre-Configured Plugins (Pinned SHA-256) | [`templates/world-bible/.obsidian/plugins/manifest.json`](file:///templates/world-bible/.obsidian/plugins/manifest.json) | Hash manifest validation |
| **CI Runner OS** | `ubuntu-24.04`, `macos-latest`, `windows-latest` | [`.github/workflows/ci.yml#L17`](file:///.github/workflows/ci.yml#L17) | Multi-platform GitHub Actions matrix |

---

## Part 2 — Context & Operational Ecosystem

### 2.1 Local Checkout Identity Table

| Attribute | Value |
|---|---|
| **Repository Remote** | `https://github.com/aryansinghnagar/Ars-Arcanum.git` |
| **Active Branch** | `main` |
| **Software Version** | `0.1.0` (Beta Release) |
| **License** | MIT License ([`LICENSE`](file:///LICENSE)) |
| **Dependency Model** | Zero-Pip Guarantee (100% Standard Library for core craft engines) |

### 2.2 Governance & Invariant Rules
The repository encodes strict operational contracts documented in [`AGENTS.md`](file:///AGENTS.md):
1. **File Safety Invariant**: All disk modifications must utilize `atomic_write()` (`tempfile` $\to$ `flush` $\to$ `fsync` $\to$ `os.replace` $\to$ parent directory `fsync`). Direct unbuffered overwrites are prohibited ([`scripts/lib/_bootstrap.py#L35-L70`](file:///scripts/lib/_bootstrap.py#L35-L70)).
2. **Path Traversal Defense**: All user-supplied volume names, draft identifiers, and book targets are validated against token regex `^[A-Za-z0-9_-]+$`; path traversals (`..`, `/`, `\`) and Windows reserved device names (`CON`, `PRN`, `AUX`, `NUL`, `COM1-9`, `LPT1-9`) are rejected immediately ([`scripts/lib/_bootstrap.py#L75-L105`](file:///scripts/lib/_bootstrap.py#L75-L105)).
3. **Content Security Policy (CSP)**: Generated HTML reports declare strict offline policies:
   ```html
   <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
   ```
4. **Module Bound Contract**: Source files must strictly maintain `<800 lines/file` maintainability boundaries.
5. **Creative Sovereignty Invariant**: Systems must never block creative expression; validation engines provide non-blocking advisory telemetry.

---

## Part 3 — Architectural Blueprint & Subsystem Topology

### 3.1 C4 Architecture Diagrams

#### Level 1: System Context
```mermaid
flowchart TD
    Author["Author / Worldbuilder (Sovereign User)"]
    
    subgraph ArsArcanum["Ars Arcanum Studio System (100% Offline)"]
        CLI["CLI Dispatcher (arcanum / cli.py)"]
        Engines["14 Core Sovereign Engines (Stdlib)"]
        DAL["Cached Data Access Layer (data_access.py)"]
    end
    
    subgraph Storage["Local Storage Layer"]
        Vault["Obsidian World Bible Vault (~/Universes/)"]
        Manuscript["Markdown & Word Manuscripts (~/Manuscripts/)"]
        Backups["Verified Backup Tarballs (.tar.gz)"]
    end
    
    Author -->|Commands & Queries| CLI
    CLI --> Engines
    Engines --> DAL
    DAL <-->|Atomic I/O & Caching| Storage
```

#### Level 2: Container & Engine Topology
```mermaid
flowchart LR
    subgraph Dispatch["Registry & Scope Tier"]
        R1["CLI Dispatcher (cli.py)"]
        R2["Scope Engine (scope.py)"]
        R3["Registry Facade (registry.py)"]
        R4["Domain Specs (registry_specs/)"]
    end

    subgraph CoreEngines["Core Sovereign Engines Tier"]
        E1["Editorial (diff, heatmap, docx_sync)"]
        E2["Portfolio (portfolio dashboard)"]
        E3["Publishing (omnibus, codex_export, preflight)"]
        E4["Infrastructure (backup, restore, snapshot, diagnostics, migrate)"]
    end

    subgraph Data["Persistence & Storage Tier"]
        D1["Data Access Layer (data_access.py)"]
        D2["Atomic Write & Path Sanitizer (_bootstrap.py)"]
        D3["Lockfile Concurrency (lockfile.py)"]
        D4["Frontmatter AST Layer (frontmatter.py)"]
    end

    Dispatch --> CoreEngines
    CoreEngines --> Data
```

---

### 3.2 Subsystem Deep-Dives

#### 1. Scope & Target Resolution Engine ([`scripts/lib/scope.py`](file:///scripts/lib/scope.py))
* **Responsibility**: Provides granular context bounding so engines never scan entire multi-gigabyte vaults needlessly.
* **Capabilities**: Parses integer lists and ranges (`1-5`, `1,3,7-10`, `ch01..ch05`), scene slices (`1-3`, `sc01..sc02`), universe names, worlds, and lore categories.
* **Context Invariants**: Resolves defaults from active manuscript/world configuration, working directory, or single-project discovery.

#### 2. Centralized Data Access Layer & Pure-Python YAML AST ([`scripts/lib/data_access.py`](file:///scripts/lib/data_access.py), [`scripts/lib/frontmatter.py`](file:///scripts/lib/frontmatter.py))
* **Responsibility**: Eliminates redundant disk reads and YAML AST parsing via thread-safe memoization.
* **Mechanisms**: Thread-safe LRU caching keyed on filesystem modification time (`mtime`) and file size; automatic cache invalidation when files mutate.
* **Recursive AST Parser**: Fully standard-library recursive YAML parser in `frontmatter.py` supporting nested mappings, object lists, block scalars, and typed scalar coercion without `PyYAML`.

#### 3. Two-Way Word Synchronization & In-Situ Comment Anchors ([`scripts/lib/docx_sync.py`](file:///scripts/lib/docx_sync.py), [`scripts/lib/docx_builder.py`](file:///scripts/lib/docx_builder.py))
* **Responsibility**: Synchronizes Microsoft Word `.docx` manuscripts with plain Markdown files.
* **Track Changes & Comments**: Excludes `<w:del>` tracked deletions to prevent resurrecting deleted prose on import; extracts `<w:comment>` margin comments into companion `.comments.json` sidecars during manuscript synchronization.
* **Preservation Guarantees**: Differentiates top-level YAML frontmatter from mid-document `@scene:`, `@pov:`, and `%` comments, keeping metadata anchored to the exact prose paragraphs during bidirectional roundtrips.

#### 4. Unified Health Diagnostics ([`scripts/lib/diagnostics.py`](file:///scripts/lib/diagnostics.py))
* **Responsibility**: Unified system health check, external toolchain inspection (Python, Git, Pandoc, Typst, Ruff), and world vault link/manifest consistency doctor (`arcanum doctor`).

---

### 3.3 Confidence Assessment & Verification Matrix

| Architectural Domain | Confidence Rating | Verification Method & Evidence |
|---|---|---|
| **Zero-Pip Guarantee & Stdlib Execution** | **High** | Verified by test suite discovery running in clean standard Python environment without pip dependencies. |
| **Atomic File Safety & Locking** | **High** | Verified via unit tests (`test_atomic_write`, `test_lockfile`) with simulated concurrency and fault injection. |
| **Granular Target Scoping** | **High** | Verified via dedicated test suite (`test_scope`, `test_scope_parser`, `test_scope_resolver`). |
| **Content Security Policy & Offline Air-Gap** | **High** | Verified via automated regex scanning across all generated HTML templates. |
| **Windows & Linux Multi-Platform Parity** | **High** | Verified via GitHub Actions CI matrix across Ubuntu 24.04, macOS, and Windows. |

---

### 3.4 Key Footnotes & Local File Citations

1. [`scripts/lib/_bootstrap.py`](file:///scripts/lib/_bootstrap.py): Establishes atomic write primitives, POSIX/Windows directory resolution, Unicode word boundary counting, and path sanitization.
2. [`scripts/lib/data_access.py`](file:///scripts/lib/data_access.py): Establishes thread-safe LRU cached AST access, frontmatter querying, and explicit cache eviction hooks.
3. [`scripts/lib/frontmatter.py`](file:///scripts/lib/frontmatter.py): Establishes zero-pip recursive YAML frontmatter parsing and structured metadata extraction.
4. [`scripts/lib/scope.py`](file:///scripts/lib/scope.py): Establishes universal granular scope models and range parsing algorithms.
5. [`scripts/lib/lockfile.py`](file:///scripts/lib/lockfile.py): Establishes cross-platform flock/msvcrt file locking.
6. [`scripts/lib/cli.py`](file:///scripts/lib/cli.py): Establishes authoritative command-line entrypoint and plugin dispatch.
7. [`scripts/lib/registry.py`](file:///scripts/lib/registry.py): Establishes engine discovery, dynamic plugin loading, and advisory documentation formatting.
8. [`scripts/setup_arcanum.ps1`](file:///scripts/setup_arcanum.ps1): Establishes 1-click Windows installation, workspace provisioning, and desktop launcher generation.

