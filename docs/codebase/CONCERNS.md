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
| Dual CLI dispatchers (Bash vs Python) | Legacy bash facade maintains historical wrappers | `scripts/arcanum`, `scripts/lib/cli.py` | Maintenance divergence across platforms | Pure-Python CLI dispatcher (`cli.py`) handles all core engine executions |
| Large static dictionaries in Python source | Embedded metadata in executable code | `scripts/lib/tips.py`, `scripts/lib/registry.py` | Memory footprint and module bloat | Extract static tips and engine catalogs to JSON/TOML data assets if memory constraints tighten |
| GTK3 accessibility baseline | Historical UI focused on visual aesthetics | `scripts/lib/ui_gtk3/` | Screen-reader inaccessibility | Add mnemonic accelerators and ATK accessible names |

### 3) Security Concerns

| Risk | OWASP category | Evidence | Current mitigation | Gap |
|------|----------------|----------|--------------------|-----|
| Path Traversal in user-provided volume/world names | A01: Broken Access Control | `scripts/lib/_bootstrap.py`, `scripts/lib/manuscript_scaffold.py` | Strict regex validation (`^[A-Za-z0-9_-]+$`) rejecting directory traversal | Resolved (0 vulnerabilities detected) |
| Untrusted Script Execution in HTML Reports | A03: Injection | `scripts/lib/studio_hub.py`, `scripts/lib/zen_studio.py`, `scripts/lib/resonance.py` | Mandatory CSP `<meta http-equiv="Content-Security-Policy" content="default-src 'none'...">` and JSON closing tag sanitization (`<\\/`) | Resolved (Zero external CDN/script calls permitted) |
| Restore Archive Symlink & Git Config Injection | A01: Broken Access Control | `scripts/lib/restore.py`, `scripts/arcanum#L1085-L1110` | Pure Python stream validation explicitly rejecting symlinks, device nodes, `.git/hooks`, and `.git/config` | Resolved |
| Cross-Origin Requests to Local HTTP Studio Hub | A07: Identification and Auth Failures | `scripts/lib/studio_hub.py#L2106-L2170` | `_validate_origin()` blocks foreign origins on POST requests | Resolved |
| XML Entity Expansion in DOCX Imports | A03: Injection | `scripts/lib/docx_sync.py`, `scripts/lib/importer.py` | Full multi-encoding DOCTYPE/ENTITY detection and stream bounding | Resolved |
| Atomic Write Descriptor Leak on Windows | A04: Insecure Design | `scripts/lib/_bootstrap.py#L41-L66` | Added `try...finally` descriptor cleanup before `os.replace` to prevent file lock contention | Resolved |

### 4) Performance and Scaling Concerns

| Concern | Evidence | Current symptom | Scaling risk | Suggested improvement |
|---------|----------|-----------------|-------------|-----------------------|
| Multi-volume corpus indexing time | `scripts/lib/corpus_export.py` | Full corpus AST scan on 500k-word multi-book series | Slower CLI response without cache | Mtime-based `.arcanum_cache.json` acceleration index (implemented in `cache.py`) |

### 5) Fragile/High-Churn Areas

| Area | Why fragile | Churn signal | Safe change strategy |
|------|-------------|-------------|----------------------|
| `scripts/lib/registry.py` | Central authoritative hub for all 47 engines and metadata | High churn on new engine introductions | Exhaustive test suite (`test_registry.py`, `test_engine_logic_docs.py`, `test_tips.py`) |
| `scripts/lib/cli.py` | Single entry point for 47+ CLI subcommands | High subcommand density | Strict argparse subparser testing and alias resolution |

### 6) `[ASK USER]` Questions

1. [ASK USER] Would you like additional structural isomorphism presets added to `STRUCTURAL_ISOMORPHISMS` in `scripts/lib/resonance.py` for specialized fiction subgenres (e.g. Grimdark Blood Magic, Biopunk Genetic Editing, Cyberpunk Currency Networks)?
2. [ASK USER] Should we add an option in `arcanum tip` to output tips formatted as Obsidian Daily Notes markdown callouts?

### 7) Evidence

- `scripts/lib/world_doctor.py#L1-L150`
- `scripts/lib/registry.py#L1-L150`
- `scripts/lib/lockfile.py#L1-L60`
- `tests/test_path_traversal_defense.py#L1-L60`
- `tests/test_threat_model.py#L1-L50`
