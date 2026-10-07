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
- [x] Implement centralized Data Access Layer (`scripts/lib/data_access.py`) with thread-safe caching and automatic `mtime` invalidation.
- [x] Propagate Data Access Layer memoization across `studio_hub.py`, `series_continuity.py`, `story_canvas.py`, and `structure.py`.
- [x] Upgrade CLI dispatcher (`cli.py`) with dynamic registry plugin discovery and fuzzy error resolution.
- [x] Modularize oversized `tips.py` (3,324 $\to$ 442 lines) into `scripts/lib/tips_catalog/` domain modules, satisfying `<800 lines/file` contract.
- [x] Extract Studio Hub presentation template into `scripts/lib/studio_hub_template.py`, reducing `studio_hub.py` by over 2,100 lines.
- [x] Modularize `resonance.py` (1,796 $\to$ 646 lines) into `resonance_data.py` (591 lines) and `resonance_template.py` (677 lines), and integrate DAL caching.
- [x] Modularize `economy.py` (1,154 $\to$ 771 lines) into `economy_data.py` (122 lines), `economy_template.py` (137 lines), and `economy_trade.py` (341 lines), and integrate DAL caching.
- [x] Modularize `scope.py` into `scope_models.py`, `scope_parser.py`, and `scope_resolver.py`.
- [x] Modularize `docx_sync.py` into `docx_builder.py`, `corpus_export.py` into `corpus_export_formatters.py`, `factions.py` into `factions_data.py`, `writing_sprint.py` into `writing_sprint_template.py`, and `revision_heatmap.py` into `revision_heatmap_template.py`.
- [x] Create comprehensive dedicated documentation for Scope (`docs/SCOPE.md`), Lockfile (`docs/LOCKFILE.md`), Data Access Layer (`docs/DATA_ACCESS.md`), Plugins (`docs/PLUGINS.md`), and Desktop GUI (`docs/DESKTOP_APP.md`).
- [x] Align README status (Beta), test count (868 total, 866 passing, 2 skipped on Windows), coverage threshold (80%), and repository URLs.
- [x] Pass 100% verification across test suite (868 tests, 0 failures), Ruff linter (0 errors), and Mypy static type checking (203 source files clean).

### `next`
- Deepen craft encyclopedia references across narrative craft, worldbuilding models, and linguistics.
- Expand interactive Studio Hub visualizations for high-dimensional narrative geometry.

### `blocked`
- None.

### `improve`
- Split monolithic 21-stage Grand Tour E2E test into isolated, parameterized test stages for faster failure localization.
- Expand golden dataset coverage across novel pacing and character arc schemas.
- Optimize SQLite FTS5 BM25+ indexing performance for multi-million word fantasy corpora.

### `recurring`
- Supply-chain integrity checks and zero external CDN audits.
- POSIX/Windows cross-platform atomic write and file lock verification.
- Universal test discovery and type safety sweeps.
