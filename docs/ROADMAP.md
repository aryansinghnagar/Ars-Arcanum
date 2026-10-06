# Ars Arcanum (Scriptorium) — Sovereign Roadmap & Momentum Queues
> **Version 0.1.0** | Tracking Continuous Evolution Across Sovereign Craft Disciplines

---

## 1. Operating Architecture & Momentum Queues

Ars Arcanum manages ongoing engineering, research, and craft capabilities across five formal momentum queues, as established in [`AGENTS.md`](file:///AGENTS.md) and [`tasks.md`](file:///tasks.md):

```mermaid
flowchart LR
    NOW["`**now** (Active Focus)`"] --> VERIFY{"Verification Gate"}
    VERIFY -->|Pass| NEXT["`**next** (Ready Backlog)`"]
    VERIFY -->|Blocker| BLOCKED["`**blocked** (Dependencies)`"]
    VERIFY -->|Ratcheting| IMPROVE["`**improve** (Quality/Evals)`"]
    IMPROVE --> RECURRING["`**recurring** (Automated Sweeps)`"]
```

---

## 2. Active Momentum State

### `now` (Active Focus)
- **v0.1.0 Core Hardening & Modular Architecture**:
  - [x] **Modular Registry Architecture**: Successfully decomposed `scripts/lib/registry.py` from 2,490 lines to 511 lines via `registry_base.py` and 7 domain specification modules in `scripts/lib/registry_specs/` (<800 lines/file contract satisfied).
  - [x] **Packaging & Entrypoints**: Added standard `setuptools>=61.0` build system to `pyproject.toml` and package root `scripts/__init__.py`, registering `arcanum` and `ars-arcanum` CLI entry points.
  - [x] **Security & Concurrency**:
    - Enforced cross-platform Windows reserved device name rejections (`CON`, `PRN`, `AUX`, `NUL`, `COM1-9`, `LPT1-9`) across path validation endpoints in `_bootstrap.py` and `scope.py`.
    - Hardened `ArcanumLock` on Windows with deterministic seek-to-0 before `msvcrt.locking` and transparent debug logging.
    - Hardened Studio Hub REST server with exact Host/Origin checks (supporting IPv6 `::1`), allowlisted engine execution, and mutex locking.
    - Hardened `restore.py` with non-empty directory overwrite guards (`--force`) and fail-closed SHA-256 sidecar verification (`--no-verify`).
  - [x] **Data Access Layer & Engine Modularization**:
    - Centralized file reading, frontmatter parsing, chapter discovery, and lore querying into thread-safe cached `data_access.py` with automatic `mtime` cache invalidation.
    - Modularized `scripts/lib/tips.py` from 3,324 lines down to 442 lines across `scripts/lib/tips_catalog/` (<60 lines/file).
    - Extracted Studio Hub presentation template into `scripts/lib/studio_hub_template.py`, reducing `studio_hub.py` by over 2,100 lines.
  - [x] **Verification Gate**: Passed 100% verification across test suite (861 tests, 0 failures, 2 skipped on Windows), Ruff strict linting (0 errors), Mypy static typing (181 source files clean), and Coverage threshold (`fail_under = 80`).

### `next` (Ready Backlog)
- **Dynamic CLI Routing**:
  - Refactor CLI dispatcher (`cli.py`) to dynamic registry-driven command routing to eliminate static dispatch tables.
- **Interactive Visualizations**:
  - Expand Studio Hub and Zen Studio offline widgets for high-dimensional narrative geometry and multi-branch causality graphs.

### `blocked` (External / Human Decisions)
- *None currently.* All core engines execute with zero external pip dependencies and 100% offline sovereignty.

### `improve` (Refactoring & Evals)
- **Engine Size Optimization**:
  - Modularize remaining oversized modules (`scope.py`, `economy.py`, `astrophysics.py`) to conform with the `<800 lines/file` engineering contract.
- **Testing Architecture**:
  - Decompose monolithic 21-stage E2E tests into isolated, parameterized test stages for faster failure localization.
  - Expand golden physics and astrodynamics datasets to anchor more simulation parameters.

### `recurring` (Automated Background Invariants)
- **Supply-Chain & CDN Sweeps**: Automated verification ensuring 0% external CDN scripts, tracking beacons, or network dependencies in generated HTML artifacts, verified against Obsidian plugin digest manifest (`manifest.json`).
- **Strict Content Security Policy**: Verification of `<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">` in all HTML exports.
- **Coverage Floor**: Maintain minimum 80% test coverage enforcement in `pyproject.toml`.
- **Cross-Platform Lock Sweeps**: Ensure POSIX `fcntl.flock` and Windows `msvcrt.locking` concurrency compliance.

---

## 3. Long-Term Version Milestones

| Milestone | Target Horizon | Focus Area | Key Deliverables |
|:---|:---:|:---|:---|
| **v0.1.0** | Current | Stability, Packaging & Security | Standard setuptools packaging, Windows device defenses, lockfile hardening, hardened REST API & restore safety. |
| **v0.2.0** | Next Sprint | Dynamic CLI & DAL | Registry-driven CLI dispatch, centralized vault repository pattern, frontmatter schema validation. |
| **v0.3.0** | Future | Modular Engine Tier | Complete `<800L` refactoring across remaining oversized engine modules. |
| **v1.0.0** | Long-Term | Sovereign Studio Suite | Fully unified offline visual canvas, real-time causality graph rendering. |
