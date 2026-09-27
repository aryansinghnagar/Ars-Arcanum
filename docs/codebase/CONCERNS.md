# Codebase Concerns

## Core Sections (Required)

### 1) Top Risks (Prioritized)

| Severity | Concern | Evidence | Impact | Suggested action |
|----------|---------|----------|--------|------------------|
| Low | Headless GTK3 test environment | `scripts/arcanum_app.py#L1-L40` | Native GTK display cannot render in purely headless Windows/CI without virtual X11 server | Maintain pure-Python CLI and browser-based Studio Hub as first-class alternatives |
| Low | File Lock compatibility across platforms | `scripts/lib/lockfile.py#L1-L60` | Windows `msvcrt.locking` behaves slightly differently from POSIX `fcntl.flock` | Unified `ArcanumLock` context manager abstracting platform specifics (fully tested) |

### 2) Technical Debt

| Debt item | Why it exists | Where | Risk if ignored | Suggested fix |
|-----------|---------------|-------|-----------------|---------------|
| `world_doctor` cyclomatic complexity | Consolidated 8-point diagnostic engine in single file | `scripts/lib/world_doctor.py` | Maintenance overhead when adding new checks | Decompose individual rule checks into modular sub-checkers |
| Untyped legacy UI helper bodies | Historical GTK presentation boilerplate | `scripts/lib/ui_gtk3/window.py` | Untyped functions flagged in mypy permissive mode | Add explicit type signatures to legacy GTK3 presentation callbacks |

### 3) Security Concerns

| Risk | OWASP category | Evidence | Current mitigation | Gap |
|------|----------------|----------|--------------------|-----|
| Path Traversal in user-provided volume/world names | A01: Broken Access Control | `scripts/lib/_bootstrap.py` | Strict regex validation (`^[A-Za-z0-9_-]+$`) rejecting directory traversal | None (0 vulnerabilities detected) |
| Untrusted Script Execution in HTML Reports | A03: Injection | `scripts/lib/studio_hub.py`, `scripts/lib/resonance.py` | Mandatory CSP `<meta http-equiv="Content-Security-Policy" content="default-src 'none'...">` | None (Zero external CDN/script calls permitted) |

### 4) Performance and Scaling Concerns

| Concern | Evidence | Current symptom | Scaling risk | Suggested improvement |
|---------|----------|-----------------|-------------|-----------------------|
| Multi-volume corpus indexing time | `scripts/lib/corpus_export.py` | Full corpus AST scan on 500k-word multi-book series | Slower CLI response without cache | Mtime-based `.arcanum_cache.json` acceleration index (implemented in `cache.py`) |

### 5) Fragile/High-Churn Areas

| Area | Why fragile | Churn signal | Safe change strategy |
|------|-------------|-------------|----------------------|
| `scripts/lib/registry.py` | Central authoritative hub for all 52 engines and metadata | High churn on new engine introductions | Exhaustive test suite (`test_registry.py`, `test_engine_logic_docs.py`, `test_tips.py`) |
| `scripts/lib/cli.py` | Single entry point for 50+ CLI subcommands | High subcommand density | Strict argparse subparser testing and alias resolution |

### 6) `[ASK USER]` Questions

1. [ASK USER] Would you like additional structural isomorphism presets added to `STRUCTURAL_ISOMORPHISMS` in `scripts/lib/resonance.py` for specialized fiction subgenres (e.g. Grimdark Blood Magic, Biopunk Genetic Editing, Cyberpunk Currency Networks)?
2. [ASK USER] Should we add an option in `arcanum tip` to output tips formatted as Obsidian Daily Notes markdown callouts?

### 7) Evidence

- `scripts/lib/world_doctor.py#L1-L150`
- `scripts/lib/registry.py#L1-L150`
- `scripts/lib/lockfile.py#L1-L60`
- `tests/test_path_traversal_defense.py#L1-L60`
- `FAILURE.md#L1-L26`
