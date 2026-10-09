# Technology Stack

## Core Sections (Required)

### 1) Runtime Summary

| Area | Value | Evidence |
|------|-------|----------|
| Primary language | Python 3.10+ (Standard Library only for core/craft engines) | [`pyproject.toml#L1-L20`](file:///pyproject.toml#L1-L20), [`AGENTS.md#L20-L40`](file:///AGENTS.md#L20-L40) |
| Runtime + version | CPython 3.10, 3.11, 3.12, 3.13, 3.14 (Verified in CI & local environments) | [`.github/workflows/ci.yml#L10-L40`](file:///.github/workflows/ci.yml#L10-L40), [`pyproject.toml#L10-L15`](file:///pyproject.toml#L10-L15) |
| Package manager & build backend | Setuptools (`setuptools>=61.0`) / Standard Library (`pip install .` supported) | [`pyproject.toml#L1-L30`](file:///pyproject.toml#L1-L30), [`AGENTS.md#L20-L45`](file:///AGENTS.md#L20-L45) |
| Module/build system | Pure Python packages (`scripts`, `scripts/lib/`), POSIX shell wrapper (`scripts/arcanum`), Windows batch (`scripts/arcanum.cmd`) | [`scripts/arcanum#L1-L50`](file:///scripts/arcanum#L1-L50), [`scripts/arcanum.cmd#L1-L5`](file:///scripts/arcanum.cmd#L1-L5), [`scripts/lib/cli.py#L1-L100`](file:///scripts/lib/cli.py#L1-L100) |

### 2) Production Frameworks and Dependencies

| Dependency | Version | Role in system | Evidence |
|------------|---------|----------------|----------|
| Python Standard Library (`sqlite3`, `math`, `json`, `dataclasses`, `enum`, `pathlib`, `urllib.parse`, `tarfile`, `hashlib`) | 3.10+ | Primary execution runtime for 14 core engines: diff, heatmap, portfolio, sync, docx, importer, diagnostics, config, cache, fs_utils, migrate, preflight, codex_export, omnibus | [`scripts/lib/_bootstrap.py#L1-L50`](file:///scripts/lib/_bootstrap.py#L1-L50), [`scripts/lib/cli.py#L1-L50`](file:///scripts/lib/cli.py#L1-L50) |
| Typst | `>= 0.11.0` (musl static binary) | Print-on-demand & PDF rendering engine | [`scripts/arcanum#L180-L240`](file:///scripts/arcanum#L180-L240), [`docs/TYPOGRAPHY.md`](file:///docs/TYPOGRAPHY.md) |
| Pandoc | `>= 2.19.x` (tested on `3.1.x`) | Document AST converter (Markdown $\to$ Typst/DOCX/HTML) | [`docs/COMPATIBILITY.md#L9-L16`](file:///docs/COMPATIBILITY.md#L9-L16), [`scripts/arcanum#L180-L240`](file:///scripts/arcanum#L180-L240) |
| Obsidian | `md.obsidian.Obsidian` (desktop app) | Worldbuilding vault interface (32 pre-configured offline plugins with SHA-256 manifest) | [`templates/world-bible/.obsidian/plugins/manifest.json`](file:///templates/world-bible/.obsidian/plugins/manifest.json), [`docs/guides/OBSIDIAN_PLUGINS.md`](file:///docs/guides/OBSIDIAN_PLUGINS.md) |
| External Toolchain | PolyGlot, Gramps, Wonderdraft, Celestia, StarGen | Dedicated craft tools for conlangs, genealogy trees, cartography, and astrophysics | [`docs/guides/EXTERNAL_TOOLS_AND_PLUGINS.md`](file:///docs/guides/EXTERNAL_TOOLS_AND_PLUGINS.md), [`docs/guides/SOFTWARE_CATALOG.md`](file:///docs/guides/SOFTWARE_CATALOG.md) |
| novelWriter | `io.gitlab.novelwriter.novelWriter` | Manuscript project management & drafting tool | [`templates/manuscript/nwProject.nwx#L1-L15`](file:///templates/manuscript/nwProject.nwx#L1-L15) |

### 3) Development Toolchain

| Tool | Purpose | Evidence |
|------|---------|----------|
| Ruff | Strict linting across rule families (`E`, `F`, `B`, `S`, `UP`, `SIM`, `I`, `RUF`, `C901`) | [`pyproject.toml#L15-L35`](file:///pyproject.toml#L15-L35), [`.github/workflows/ci.yml#L25-L35`](file:///.github/workflows/ci.yml#L25-L35) |
| Mypy | Strict static type checking with `check_untyped_defs = True` (90 source files clean) | [`mypy.ini#L1-L25`](file:///mypy.ini#L1-L25), [`tests/test_type_safety.py#L1-L40`](file:///tests/test_type_safety.py#L1-L40) |
| Unittest | Automated test discovery & regression test execution (336+ tests, 100% pass) | [`tests/test_*.py`](file:///tests/), [`.github/workflows/ci.yml#L30-L40`](file:///.github/workflows/ci.yml#L30-L40) |
| Coverage | Test coverage enforcement and reporting (`fail_under = 80`) | [`pyproject.toml#L35-L45`](file:///pyproject.toml#L35-L45) |

### 4) Key Commands

```bash
# Standard package installation
pip install -e .

# Full test discovery suite (336+ tests across 48 modules)
python -m unittest discover tests

# High-performance parallel test runner (~2.5s execution)
python scripts/test_parallel.py

# Coverage report enforcement (80%+ aggregate coverage)
coverage run -m unittest discover tests; coverage report --fail-under=80

# Strict linter pass (0 violations)
ruff check .

# Static type checker pass across all source files (0 errors)
mypy --explicit-package-bases scripts tests

# Master verification run (POSIX)
bash scripts/verify.sh
```


### 5) Environment and Config

- Config sources: `~/.config/ars-arcanum/config.json`, `.arcanum_cache.json`, `.sync_state.json`
- Required env vars: `XDG_CONFIG_HOME` (optional override), `ARCANUM_WORKSPACE` (optional root path override)
- Deployment/runtime constraints: 100% offline air-gapped execution required; strict CSP `<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">` on all generated HTML reports.

### 6) Evidence

- [`pyproject.toml#L1-L45`](file:///pyproject.toml#L1-L45)
- [`mypy.ini#L1-L25`](file:///mypy.ini#L1-L25)
- [`AGENTS.md#L1-L60`](file:///AGENTS.md#L1-L60)
- [`scripts/lib/_bootstrap.py#L1-L70`](file:///scripts/lib/_bootstrap.py#L1-L70)
- [`.github/workflows/ci.yml#L1-L60`](file:///.github/workflows/ci.yml#L1-L60)
- [`docs/ROADMAP.md#L1-L90`](file:///docs/ROADMAP.md#L1-L90)
