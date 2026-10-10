# GitHub Copilot & Automated Agent Instructions — Ars Arcanum (Scriptorium)

> **Sovereign Local-First Authoring Operating System & Craft Studio**  
> *Authoritative Instructions for Copilot, Claude, Gemini, and Autonomous Agents*

---

## 1. System Identity & Stack Architecture

Ars Arcanum (*Scriptorium*) is a sovereign, 100% offline, privacy-first authoring platform and worldbuilding operating system for speculative fiction novelists and narrative designers.

### The Unified 5-Tier Stack:
1. **External Tools & 32-Plugin Suite**: Obsidian World Bible vault with 32 pre-configured offline plugins (`manifest.json`), Typst musl binary (`0.14.2`), Pandoc (`3.7.x`), PolyGlot, Gramps, Wonderdraft, Celestia, StarGen, novelWriter.
2. **Python 3.10+ Stdlib Core Engines**: 17 sovereign craft engines in `scripts/lib/`, pure standard library primitives, zero-pip dependency guarantee, strict Mypy typing, Ruff linting.
3. **HTML5 / Modern CSS / Vanilla JavaScript**: Air-gapped offline interactive visualizers (`velocity_template.py`, `draft_manager_template.py`, `manuscript_diff_template.py`, `revision_heatmap_template.py`, `portfolio_template.py`, `codex_export_template.py`, `omnibus_template.py`) with strict CSP.
4. **Django & React Modernization Architecture**: Modular local API and React component system for extended desktop/web studio views.
5. **Shell & Linux System Integration**: POSIX shell CLI dispatcher (`scripts/arcanum`, `verify.sh`), XDG desktop launchers (`launchers/*.desktop`), systemd background service/timer configs (`configs/`), and POSIX `fcntl.flock` file locking.

---

## 2. Canonical Commands & Verification Inventory

Before proposing or committing changes, ensure the following commands run cleanly:

| Command | Purpose | Verification Requirement |
|:---|:---|:---|
| `pip install -e .` | Package installation in development mode | Must succeed without errors |
| `python -m unittest discover tests` | Canonical unit & integration test discovery (438 tests, 55 modules) | **0 failures permitted** |
| `python scripts/test_parallel.py` | High-speed multi-core parallel test runner (~2.5s execution) | **0 failures permitted** |
| `coverage run -m unittest discover tests; coverage report --fail-under=80` | Measure code coverage | **$\ge 80\%$ floor enforced** |
| `ruff check .` | Strict linting across 15 rule families | **0 violations permitted** |
| `mypy --explicit-package-bases scripts tests` | Static type checking with `check_untyped_defs = True` | **0 errors across all source files** |
| `bash scripts/verify.sh --require-tools` | 7-stage POSIX packaging & integration harness | **Passes all 7 verification stages** |
| `python scripts/arcanum doctor` | Unified system toolchain & vault health check | **Status: HEALTHY** |

---

## 3. Non-Negotiable Engineering Contracts

### 3.1 File Safety & Concurrency
- **Atomic Writes**: ALL file modifications must use `atomic_write()` from `scripts/lib/_bootstrap.py` (`tempfile` $\to$ `flush` $\to$ `fsync` $\to$ `os.replace` $\to$ parent directory `fsync`). Direct unbuffered file overwrites are strictly prohibited.
- **Cross-Platform File Locking**: Concurrency-sensitive operations must acquire `ArcanumLock` (`scripts/lib/lockfile.py`), utilizing `fcntl.flock` on POSIX and `msvcrt.locking` on Windows with deterministic seek-to-0 positioning.
- **Path Traversal Defense**: All user-supplied volume names, draft identifiers, and book targets must be sanitized via regex token validation `^[A-Za-z0-9_-]+$`. Reject Windows reserved device names (`CON`, `PRN`, `AUX`, `NUL`, `COM1-9`, `LPT1-9`) immediately.

### 3.2 Offline Security & Content Security Policy
- Every generated HTML report, dashboard, and visualizer must declare strict air-gapped Content Security Policies:
  ```html
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
  ```
- No external CDN scripts, remote fonts, or network telemetry are permitted.

### 3.3 Epistemic Safety & Three Subsystems
- **Subsystem 1 (Invariant Consistency Engine)**: File safety, atomic locks, SHA-256 validation, broken link checks. Fails builds (`exit 1`) in strict mode.
- **Subsystem 2 (Selected Craft Lenses)**: Advisory reference overlays (Three-Act, MRU, Save the Cat, Pacing, Economy). Always advisory (`exit 0` default), dismissible via `@intent: deliberate` or `constitution.yaml`.
- **Subsystem 3 (Creative Ideation & Sparks)**: Combinatorial analogies and generative prompts. Always clearly labeled with `[SPECULATION]` provenance tags.

### 3.4 6-Tier Diagnostic Severity Taxonomy
- `CANON_ERROR` (Severity 5): Broken links, invalid YAML frontmatter, missing mandatory identifiers.
- `RULE_CONFLICT` (Severity 4): Contradiction of an author-declared world rule in `constitution.yaml`.
- `OBSERVATION` (Severity 3): Neutral mathematical or structural telemetry.
- `LENS_NOTE` (Severity 2): Comparative feedback against an optional craft framework.
- `SUGGESTION` (Severity 1): Optional creative spark or phrasing prompt.
- `EXPERIMENT` (Severity 0): Speculative lateral thinking prompts labeled `[SPECULATION]`.

### 3.5 Module Size Contract
- Every Python source file must strictly remain `< 800 lines/file`. When expanding engines, split presentation templates into `<engine>_template.py` and modularize data/models into dedicated sub-packages.

---

## 4. Branching & PR Governance

1. **Branch per feature/phase**: Always create a feature branch (`git checkout -b feature/<name>`).
2. **Merge to trunk, never stack**: Each branch is cut from `main` and merged to `main` before dependent work begins.
3. **Keep living documentation synchronized**: Any architectural or CLI changes must be updated in `docs/codebase/`, `README.md`, and `CHANGELOG.md` within the same pull request.
