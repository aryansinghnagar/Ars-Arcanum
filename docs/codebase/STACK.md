# Technology Stack

## Core Sections (Required)

### 1) Runtime Summary

| Area | Value | Evidence |
|------|-------|----------|
| Primary language | Python 3.10+ (Standard Library only for core/craft logic) | `pyproject.toml#L1-L20`, `AGENTS.md#L20-L40` |
| Runtime + version | CPython 3.10, 3.11, 3.12, 3.13, 3.14 (Verified in CI & local) | `.github/workflows/ci.yml#L10-L40`, `pyproject.toml#L10-L15` |
| Package manager | Pip / Standard Library (Zero-Pip Dependency Guarantee for core engines) | `AGENTS.md#L30-L45`, `pyproject.toml#L1-L25` |
| Module/build system | Pure Python modules (`scripts/lib/`), POSIX shell (`scripts/arcanum`), Flatpak manifest | `scripts/arcanum#L1-L50`, `org.arsarcanum.ArsArcanum.yaml#L1-L40` |

### 2) Production Frameworks and Dependencies

List only high-impact production dependencies (frameworks, data, transport, auth).

| Dependency | Version | Role in system | Evidence |
|------------|---------|----------------|----------|
| Python Standard Library (`sqlite3`, `math`, `json`, `dataclasses`, `enum`, `pathlib`) | 3.10+ | Primary execution runtime, storage, and simulation engines | `scripts/lib/_bootstrap.py#L1-L50`, `scripts/lib/resonance.py#L1-L40` |
| PyGObject (`Gtk 3.0`, `Gdk`, `GLib`, `Pango`) | Pinned system packages | Native Linux desktop GUI presentation layer | `scripts/arcanum_app.py#L1-L50`, `scripts/lib/ui_gtk3/window.py#L1-L60` |
| Libadwaita / GTK4 | System packages (optional modern UI) | Adaptive modern GNOME/Adwaita interface | `scripts/lib/ui_adw.py#L1-L50` |
| Typst | `0.14.2` (musl static binary) | Print-on-demand & PDF rendering engine | `dependencies.lock#L1-L15`, `scripts/arcanum#L180-L240` |
| Pandoc | `>= 2.19.x` (tested on `3.1.x`) | Document AST converter (Markdown $\to$ Typst/DOCX/HTML) | `docs/COMPATIBILITY.md#L9-L16`, `scripts/arcanum#L180-L240` |
| Calibre | System package (`ebook-convert`) | EPUB3 compilation engine | `scripts/setup_arcanum.sh#L142-L209` |
| Obsidian | `md.obsidian.Obsidian` (desktop app) | Worldbuilding vault interface (10 vendored plugins) | `templates/world-bible/.obsidian/community-plugins.json#L1-L15` |
| novelWriter | `io.gitlab.novelwriter.novelWriter` | Manuscript project management & drafting tool | `templates/manuscript/nwProject.nwx#L1-L15` |

### 3) Development Toolchain

| Tool | Purpose | Evidence |
|------|---------|----------|
| Ruff | Strict linting across rule families (`E`, `F`, `B`, `S`, `UP`, `SIM`, `I`, `RUF`, `C901`) | `pyproject.toml#L15-L35`, `.github/workflows/ci.yml#L25-L35` |
| Mypy | Strict static type checking with `check_untyped_defs = True` | `mypy.ini#L1-L25`, `tests/test_type_safety.py#L1-L40` |
| Unittest | Automated test discovery & regression test execution (937 tests, 86% coverage) | `tests/test_*.py`, `.github/workflows/ci.yml#L30-L40` |
| AppStream CLI / Flatpak | Flathub manifest and metainfo validation | `flatpak/flathub_submission_validate.py#L1-L60` |
| Shellcheck / Bash | Shell script syntax validation and POSIX compliance | `tests/test_shell_scripts_syntax.py#L1-L40` |

### 4) Key Commands

```bash
# Full test discovery suite (937 tests)
python -m unittest discover tests

# Coverage report enforcement (86% coverage, fail_under = 85)
coverage run -m unittest discover tests; coverage report

# Strict linter pass
ruff check .

# Static type checker pass
mypy --config-file mypy.ini scripts/lib/

# Master 7-stage verification harness (POSIX)
bash scripts/verify.sh
```

### 5) Environment and Config

- Config sources: `~/.config/ars-arcanum/config.json`, `.arcanum_cache.json`, `.sync_state.json`
- Required env vars: `XDG_CONFIG_HOME` (optional override), `ARCANUM_WORKSPACE` (optional root path override)
- Deployment/runtime constraints: 100% offline air-gapped execution required; strict CSP `<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">` on all generated HTML reports.

### 6) Evidence

- `pyproject.toml#L1-L45`
- `mypy.ini#L1-L25`
- `dependencies.lock#L1-L30`
- `AGENTS.md#L1-L60`
- `scripts/lib/_bootstrap.py#L1-L70`
- `.github/workflows/ci.yml#L1-L60`
