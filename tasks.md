# Ars Arcanum (Scriptorium) — Momentum Queues & Milestone Roadmap
> Sovereign Authoring Operating System | Release v0.1.0

---

### `now`
- **Active Focus**: Core Hardening & Architectural Modularization across sovereign craft engines.
- [x] Enforce cross-platform Windows reserved device name validation (`CON`, `PRN`, `AUX`, `NUL`, `COM1-9`, `LPT1-9`) across path validation endpoints.
- [x] Modularize `scripts/lib/registry.py` God Object into `registry_base.py` and `registry_specs/` package (<800 lines/file rule).
- [x] Harden `ArcanumLock` on Windows with deterministic seek-to-0 before `msvcrt.locking` and debug diagnostics.
- [x] Complete 100% verification across test suite (853 tests, 0 failures), Ruff linter (0 errors), and Mypy static analysis (156 source files clean).

### `next`
- Introduce cached Data Access Layer (`data_access.py`) to eliminate redundant vault `rglob` disk traversals.
- Refactor CLI dispatcher (`cli.py`) to dynamic registry-driven command routing.
- Deepen craft encyclopedia references across narrative craft, worldbuilding models, and linguistics.
- Expand interactive Studio Hub visualizations for high-dimensional narrative geometry.

### `blocked`
- None.

### `improve`
- Modularize remaining oversized engine modules (`studio_hub.py`, `scope.py`, `economy.py`, `astrophysics.py`) to strictly satisfy `<800 lines/file`.
- Split monolithic 21-stage Grand Tour E2E test into isolated, parameterized test stages for faster failure localization.
- Expand golden dataset coverage across novel pacing and character arc schemas.
- Optimize SQLite FTS5 BM25+ indexing performance for multi-million word fantasy corpora.

### `recurring`
- Supply-chain integrity checks and zero external CDN audits.
- POSIX/Windows cross-platform atomic write and file lock verification.
- Universal test discovery and type safety sweeps.
