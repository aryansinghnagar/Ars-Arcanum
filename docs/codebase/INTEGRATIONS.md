# External Integrations

## Core Sections (Required)

### 1) Integration Inventory

| System | Type | Purpose | Auth model | Criticality | Evidence |
|--------|------|---------|------------|-------------|----------|
| Typst Binary (`typst`) | Local CLI Tool | High-speed typesetting for print-ready PDF | Local musl static binary | High | [`scripts/arcanum#L180-L240`](file:///scripts/arcanum#L180-L240), [`docs/TYPOGRAPHY.md`](file:///docs/TYPOGRAPHY.md) |
| Pandoc (`pandoc`) | Local CLI Tool | Markdown AST document conversion | Local system binary | High | [`docs/COMPATIBILITY.md#L9-L16`](file:///docs/COMPATIBILITY.md#L9-L16) |
| Obsidian | Local Desktop App | Knowledge base & World Bible editing (32 pre-configured offline plugins with SHA-256 manifest) | Local filesystem / plugins | Medium (Optional) | [`templates/world-bible/.obsidian/plugins/manifest.json`](file:///templates/world-bible/.obsidian/plugins/manifest.json), [`docs/guides/OBSIDIAN_PLUGINS.md`](file:///docs/guides/OBSIDIAN_PLUGINS.md) |
| PolyGlot / Condict | Local Desktop App / CLI | Dedicated conlang lexicon construction, phonotactics, and sound changes | Local files (`.pgd`, `.sqlite`) | Medium (Optional) | [`docs/CONLANG.md`](file:///docs/CONLANG.md), [`docs/guides/EXTERNAL_TOOLS_AND_PLUGINS.md`](file:///docs/guides/EXTERNAL_TOOLS_AND_PLUGINS.md) |
| Gramps | Local Desktop App | Comprehensive genealogical tree construction and pedigree charting | Local XML / SQLite | Medium (Optional) | [`docs/GENEALOGY.md`](file:///docs/GENEALOGY.md), [`docs/guides/EXTERNAL_TOOLS_AND_PLUGINS.md`](file:///docs/guides/EXTERNAL_TOOLS_AND_PLUGINS.md) |
| Wonderdraft | Local Desktop App | High-resolution cartography and fantasy map generation | Local `.wonderdraft_map` | Medium (Optional) | [`docs/CARTOGRAPHY.md`](file:///docs/CARTOGRAPHY.md), [`docs/guides/EXTERNAL_TOOLS_AND_PLUGINS.md`](file:///docs/guides/EXTERNAL_TOOLS_AND_PLUGINS.md) |
| Celestia / StarGen | Local Desktop App / CLI | Real-time 3D orbital mechanics, astrophysics, and planet generation | Local `.ssc`, `.stc` | Medium (Optional) | [`docs/ASTROPHYSICS.md`](file:///docs/ASTROPHYSICS.md), [`docs/guides/EXTERNAL_TOOLS_AND_PLUGINS.md`](file:///docs/guides/EXTERNAL_TOOLS_AND_PLUGINS.md) |
| novelWriter | Local Desktop App | Outlining and long-form prose drafting | Local `.nwx` project files | Medium (Optional) | [`templates/manuscript/nwProject.nwx`](file:///templates/manuscript/nwProject.nwx) |
| Calibre (`ebook-convert`) | Local CLI Tool | EPUB3 book compilation | Local system binary | Medium (Optional) | [`scripts/setup_arcanum.sh#L142-L209`](file:///scripts/setup_arcanum.sh#L142-L209) |

### 2) Data Stores

| Store | Role | Access layer | Key risk | Evidence |
|-------|------|--------------|----------|----------|
| Plain Markdown / YAML Files | Primary persistent storage for lore & prose | `fs_utils.py` & `_bootstrap.py` (atomic writes) | Partial write corruption (mitigated by `atomic_write()`) | [`scripts/lib/_bootstrap.py`](file:///scripts/lib/_bootstrap.py) |
| SQLite3 (In-Memory / File) | FTS5 semantic search & structured export | `sqlite3` standard library | Locking contention (mitigated by read-only FTS queries) | [`scripts/lib/vault_search.py`](file:///scripts/lib/vault_search.py) |
| JSON Cache (`.arcanum_cache.json`) | Mtime-based accelerated engine cache | `scripts/lib/cache.py` | Stale cache entries (mitigated by mtime invalidation) | [`scripts/lib/cache.py`](file:///scripts/lib/cache.py) |

### 3) Secrets and Credentials Handling

- Credential sources: None required (100% offline sovereign architecture).
- Hardcoding checks: Validated by Ruff `S` security rules and [`tests/test_threat_model.py`](file:///tests/test_threat_model.py) (0 hardcoded credentials).
- Rotation or lifecycle notes: N/A (zero external network connections).

### 4) Reliability and Failure Behavior

- Retry/backoff behavior: Graceful fallback to default configs and standard conventions on corrupted inputs.
- Timeout policy: Synchronous sub-second deterministic simulation algorithms.
- Circuit-breaker or fallback behavior: Pure-Python CLI dispatcher runs identically if GTK3 desktop libraries are absent.

### 5) Observability for Integrations

- Logging around external calls: `subprocess.run` calls captured with stderr logging and exit code validation ([`scripts/lib/_bootstrap.py`](file:///scripts/lib/_bootstrap.py)).
- Metrics/tracing coverage: Built-in `world_doctor` 8-point diagnostic audit and writing sprint velocity telemetry.
- Missing visibility gaps: None; all operations emit structured JSON logs or stdout summaries.

### 6) Evidence

- [`scripts/lib/_bootstrap.py#L1-L80`](file:///scripts/lib/_bootstrap.py#L1-L80)
- [`scripts/lib/vault_search.py#L1-L80`](file:///scripts/lib/vault_search.py#L1-L80)
- [`scripts/lib/cache.py#L1-L60`](file:///scripts/lib/cache.py#L1-L60)
- [`docs/COMPATIBILITY.md#L1-L40`](file:///docs/COMPATIBILITY.md#L1-L40)
- [`tests/test_threat_model.py#L1-L50`](file:///tests/test_threat_model.py#L1-L50)
