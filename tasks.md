# Ars Arcanum (Scriptorium) — Momentum Queues & Milestone Roadmap
> Sovereign Authoring Operating System | Release v0.1.0 (Beta)

---

### `now`
- **Active Focus**: Multi-Lens Software Audit Remediations & Production Hardening.
- [x] Restore missing Bash launcher helper subroutines (`resolve_target_dir`, `discover_worlds`, `discover_manuscripts`, `sanitize_name`, `git_commit_safe`) and base path invariants in `scripts/arcanum`.
- [x] Configure standard setuptools packaging (`[build-system]`, package discovery, and `scripts/__init__.py`) enabling clean `pip install .` and entry point execution.
- [x] Clean and synchronize `.github/workflows/ci.yml` (remove dead paths, add wheel install smoke test, add Bandit SAST `# nosec` annotations).
- [x] Secure Studio Hub local HTTP API (strict exact Origin validation, loopback IPv6 support, authorized engine execution allowlist, and thread execution mutex).
- [x] Harden `restore.py` with `force=False` non-empty destination overwrite protection and fail-closed SHA-256 sidecar validation.
- [x] Generate Obsidian community plugin SHA-256 integrity manifest (`templates/world-bible/.obsidian/plugins/manifest.json`).
- [x] Align README status (Beta), test count (855 total, 853 passing), coverage threshold (81%), and repository URLs.
- [x] Pass 100% verification across test suite (855 tests, 0 failures), Ruff linter (0 errors), and Mypy static type checking.

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
