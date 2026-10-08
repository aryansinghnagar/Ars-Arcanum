# Codebase Concerns

## Core Sections (Required)

### 1) Top Risks (Prioritized)

| Severity | Concern | Evidence | Impact | Suggested action |
|----------|---------|----------|--------|------------------|
| Low | Headless GTK3 test environment | [`scripts/arcanum_app.py#L1-L40`](file:///scripts/arcanum_app.py#L1-L40) | Native GTK display cannot render in purely headless Windows/CI without virtual X11 server | Maintain pure-Python CLI and browser-based Studio Hub as first-class alternatives |
| Low | File Lock compatibility across platforms | [`scripts/lib/lockfile.py#L70-L140`](file:///scripts/lib/lockfile.py#L70-L140) | Windows `msvcrt.locking` behaves slightly differently from POSIX `fcntl.flock` | Hardened with explicit `os.lseek` to byte 0 and unified `ArcanumLock` context manager (fully tested) |

### 2) Technical Debt

| Debt item | Why it exists | Where | Risk if ignored | Status / Mitigation |
|-----------|---------------|-------|-----------------|---------------------|
| Dual CLI dispatchers (Bash vs Python) | Legacy bash facade maintains historical wrappers | [`scripts/arcanum`](file:///scripts/arcanum), [`scripts/lib/cli.py`](file:///scripts/lib/cli.py) | Maintenance divergence across platforms | Pure-Python CLI dispatcher (`cli.py`) handles all core engine executions with packaging entry points |
| Large static dictionaries in Python source | Embedded metadata in executable code | [`scripts/lib/registry.py`](file:///scripts/lib/registry.py) | Monolithic God Object violating `<800L` contract | **Resolved**: Decomposed into `scripts/lib/registry_base.py` and `scripts/lib/registry_specs/`, reducing `registry.py` to 434 lines |
| Oversized engine modules (`resonance.py`, `economy.py`, `tips.py`, `studio_hub.py`, `scope.py`, `astrophysics.py`, `climate.py`, `tactical_sim.py`, `causality.py`) | Rich single-file implementation | `scripts/lib/*.py` | Maintenance friction | **Resolved**: 100% of core and craft engines refactored to `<800L/file`. `tips.py` decomposed to `tips_catalog/`, `studio_hub.py` via `studio_hub_template.py`, `resonance.py` via `resonance_data.py` & `resonance_template.py`, `economy.py` via `economy_data.py`, `economy_template.py` & `economy_trade.py`, `scope.py` via `scope_models.py`, `scope_parser.py` & `scope_resolver.py`, `astrophysics.py` via `astrophysics_calc.py`, `astrophysics_data.py` & `astrophysics_template.py`, `climate.py` via `climate_template.py`, `tactical_sim.py` via `tactical_sim_template.py`, and `causality.py` via `causality_template.py`. |
| GTK3 accessibility baseline | Historical UI focused on visual aesthetics | `scripts/lib/ui_gtk3/` | Screen-reader inaccessibility | Add mnemonic accelerators and ATK accessible names |

### 3) Security Concerns

| Risk | OWASP category | Evidence | Current mitigation | Gap |
|------|----------------|----------|--------------------|-----|
| Path Traversal in user-provided volume/world names | A01: Broken Access Control | [`scripts/lib/_bootstrap.py#L75-L100`](file:///scripts/lib/_bootstrap.py#L75-L100), [`scripts/lib/scope.py#L30-L45`](file:///scripts/lib/scope.py#L30-L45) | Strict regex validation (`^[A-Za-z0-9_-]+$`) + Windows device name rejection (`CON`, `PRN`, `AUX`, `NUL`, `COM1-9`, `LPT1-9`) | Resolved (0 vulnerabilities detected, tested in [`tests/test_path_traversal_defense.py`](file:///tests/test_path_traversal_defense.py)) |
| Untrusted Script Execution in HTML Reports | A03: Injection | [`scripts/lib/studio_hub.py`](file:///scripts/lib/studio_hub.py), [`scripts/lib/zen_studio.py`](file:///scripts/lib/zen_studio.py), [`scripts/lib/resonance.py`](file:///scripts/lib/resonance.py) | Mandatory CSP `<meta http-equiv="Content-Security-Policy" content="default-src 'none'...">` and JSON closing tag sanitization (`<\\/`) | Resolved (Zero external CDN/script calls permitted) |
| Restore Archive Directory Traversal & Overwrite | A01: Broken Access Control | [`scripts/lib/restore.py`](file:///scripts/lib/restore.py) | Safe path extraction, rejection of symlinks/device nodes, non-empty directory defense (`force=True` required), and fail-closed SHA-256 sidecar verification | Resolved (Tested in [`tests/test_backup_pure_python.py`](file:///tests/test_backup_pure_python.py)) |
| Cross-Origin Requests to Local HTTP Studio Hub | A07: Identification and Auth Failures | [`scripts/lib/studio_hub.py`](file:///scripts/lib/studio_hub.py) | `_validate_origin()` strictly compares Origin against Host (supporting IPv4 and IPv6 `::1`), rejecting foreign and null origins | Resolved |
| Arbitrary Engine Execution via REST API | A01: Broken Access Control | [`scripts/lib/studio_hub.py`](file:///scripts/lib/studio_hub.py) | Strict static `ENGINE_ALLOWLIST` and mutex locking (`threading.Lock()`) around `POST /api/engine/run` | Resolved |
| XML Entity Expansion in DOCX Imports | A03: Injection | [`scripts/lib/docx_sync.py`](file:///scripts/lib/docx_sync.py), [`scripts/lib/importer.py`](file:///scripts/lib/importer.py) | Full multi-encoding DOCTYPE/ENTITY detection and stream bounding (Bandit `# nosec B314`) | Resolved |
| Atomic Write Descriptor Leak on Windows | A04: Insecure Design | [`scripts/lib/_bootstrap.py#L40-L75`](file:///scripts/lib/_bootstrap.py#L40-L75), [`scripts/lib/fs_utils.py`](file:///scripts/lib/fs_utils.py) | Added `try...finally` descriptor cleanup before `os.replace` to prevent file lock contention | Resolved |

### 4) Performance and Scaling Concerns

| Concern | Evidence | Current symptom | Scaling risk | Suggested improvement |
|---------|----------|-----------------|-------------|-----------------------|
| Multi-volume corpus indexing time | [`scripts/lib/corpus_export.py`](file:///scripts/lib/corpus_export.py) | Full corpus AST scan on 500k-word multi-book series | Slower CLI response without cache | Mtime-based `.arcanum_cache.json` acceleration index (implemented in `cache.py`) |
| Redundant filesystem scans across engines | Multiple craft engines calling `Path.rglob()` | Multiple full-vault walks when running batch reports | Slower execution on 1M+ word vaults | **Resolved**: Thread-safe cached Data Access Layer (`data_access.py`) integrated with memoized AST/frontmatter reader and automatic mtime invalidation |

### 5) Fragile/High-Churn Areas

| Area | Why fragile | Churn signal | Safe change strategy |
|------|-------------|-------------|----------------------|
| [`scripts/lib/registry_specs/`](file:///scripts/lib/registry_specs/) | Engine specifications and documentation | Adding new engine specs | Isolated domain files (`domain_a_science.py` through `domain_g_publishing.py`) prevent monolithic merge conflicts |
| [`scripts/lib/cli.py`](file:///scripts/lib/cli.py) | Single entry point for 47+ CLI subcommands | High subcommand density | Strict argparse subparser testing and alias resolution |

### 6) `[ASK USER]` Questions

1. [ASK USER] Would you like additional structural isomorphism presets added to `STRUCTURAL_ISOMORPHISMS` in `scripts/lib/resonance.py` for specialized fiction subgenres (e.g. Grimdark Blood Magic, Biopunk Genetic Editing, Cyberpunk Currency Networks)?
2. [ASK USER] Should we add an option in `arcanum tip` to output tips formatted as Obsidian Daily Notes markdown callouts?
3. [ASK USER] Would you like additional planetary climate models (e.g. Tidally Locked Eyeball worlds, Runaway Greenhouse, Glaciated Super-Earth) expanded in Studio Hub interactive tabs?

### 7) Evidence

- [`scripts/lib/world_doctor.py#L1-L150`](file:///scripts/lib/world_doctor.py#L1-L150)
- [`scripts/lib/registry.py#L1-L60`](file:///scripts/lib/registry.py#L1-L60)
- [`scripts/lib/registry_base.py#L1-L60`](file:///scripts/lib/registry_base.py#L1-L60)
- [`scripts/lib/registry_specs/__init__.py#L1-L30`](file:///scripts/lib/registry_specs/__init__.py#L1-L30)
- [`scripts/lib/lockfile.py#L65-L145`](file:///scripts/lib/lockfile.py#L65-L145)
- [`tests/test_path_traversal_defense.py#L50-L80`](file:///tests/test_path_traversal_defense.py#L50-L80)
- [`tests/test_backup_pure_python.py#L1-L100`](file:///tests/test_backup_pure_python.py#L1-L100)
- [`tests/test_threat_model.py#L1-L50`](file:///tests/test_threat_model.py#L1-L50)
- [`docs/ROADMAP.md#L1-L60`](file:///docs/ROADMAP.md#L1-L60)
