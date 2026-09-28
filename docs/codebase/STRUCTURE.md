# Codebase Structure

## Core Sections (Required)

### 1) Top-Level Map

| Path | Purpose | Evidence |
|------|---------|----------|
| `scripts/` | Main application entry points (`arcanum`, `arcanum_app.py`, `package_distribution.py`) | `scripts/arcanum`, `scripts/arcanum_app.py` |
| `scripts/lib/` | 53 core and craft domain engines, presentation modules, and bootstrap safety utilities | `scripts/lib/registry.py`, `scripts/lib/_bootstrap.py` |
| `scripts/lib/ui_gtk3/` | Modular PyGObject GTK3 desktop interface package (<800 lines/file) | `scripts/lib/ui_gtk3/window.py` |
| `docs/` | Comprehensive craft documentation, user guides, and master engine encyclopedia | `docs/README.md`, `docs/ENGINE_LOGIC_ENCYCLOPEDIA.md` |
| `tests/` | Exhaustive 937-test suite covering unit, integration, and security constraints | `tests/test_*.py` |
| `templates/` | Standardized world bibles, demo cosmos (`Eldoria`), novelWriter project templates | `templates/demo-cosmos/`, `templates/world-bible/` |
| `flatpak/` | Flathub manifest validator and packaging scripts | `flatpak/flathub_submission_validate.py` |
| `launchers/` | FreeDesktop desktop entry files and application icons | `launchers/org.arsarcanum.ArsArcanum.desktop` |
| `configs/` | Systemd service/timer definitions and distraction blocking profiles | `configs/systemd/` |
| `pkg/` | Multi-distribution packaging manifests (Debian, Arch PKGBUILD, RPM spec) | `pkg/arch/`, `pkg/rpm/`, `debian/` |

### 2) Entry Points

- Main desktop GUI runtime entry: [`scripts/arcanum_app.py`](file:///scripts/arcanum_app.py)
- Unified CLI runtime dispatcher: [`scripts/lib/cli.py`](file:///scripts/lib/cli.py) / [`scripts/arcanum`](file:///scripts/arcanum)
- Studio Hub telemetry dashboard entry: [`scripts/lib/studio_hub.py`](file:///scripts/lib/studio_hub.py) (`arcanum hub`)
- Zen Drafting Studio entry: [`scripts/lib/zen_studio.py`](file:///scripts/lib/zen_studio.py) (`arcanum zen`)
- Release Packager entry: [`scripts/package_distribution.py`](file:///scripts/package_distribution.py)
- Selection mechanism: POSIX shell wrapper `scripts/arcanum` dispatches subcommands to `scripts/lib/cli.py` or bash fallback handlers.

### 3) Module Boundaries

| Boundary | What belongs here | What must not be here |
|----------|-------------------|------------------------|
| `scripts/lib/_bootstrap.py` & `fs_utils.py` | Atomic POSIX file I/O, regex token sanitization, path traversal defense | Domain business logic, UI widgets |
| `scripts/lib/registry.py` | Authoritative 53-engine discovery specs, CLI aliases, and subfeature matrices | Heavy simulation calculations |
| `scripts/lib/ui_gtk3/` & `ui_adw.py` | Presentation widgets, event handlers, and GTK rendering loops | Direct file system mutation (must delegate to controllers/engines) |
| Craft Simulation Engines (`astrophysics`, `climate`, `conlang`, `resonance`, etc.) | Pure Python mathematical simulations, deterministic models, advisory options | GTK/GUI imports, cloud network dependencies |

### 4) Naming and Organization Rules

- File naming pattern: Lowercase snake_case (`astrophysics.py`, `local_rag.py`, `test_resonance.py`).
- Directory organization pattern: Layered architectural tiers (Root bootstrap $\to$ `scripts/lib/` engines $\to$ presentation packages).
- Import aliasing or path conventions: Canonical bootstrap guard `try: import lib._bootstrap; except ImportError: import _bootstrap`.

### 5) Evidence

- `scripts/lib/registry.py#L1-L100`
- `scripts/lib/_bootstrap.py#L1-L60`
- `scripts/lib/cli.py#L1-L100`
- `scripts/arcanum#L1-L80`
- `scripts/lib/ui_gtk3/window.py#L1-L80`
