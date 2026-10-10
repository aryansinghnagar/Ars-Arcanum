# External Integrations — Ars Arcanum (Scriptorium)

## Core Sections (Required)

### 1) Integration Inventory

| System | Type | Purpose | Auth Model | Criticality | Evidence |
|:---|:---|:---|:---|:---|:---|
| **Typst Binary (`typst`)** | Local CLI Tool | High-speed typesetting for print-ready PDF (`v0.14.2` musl binary) | Local system binary | High | [`scripts/setup_arcanum.sh#L317-L320`](file:///scripts/setup_arcanum.sh#L317-L320), [`docs/TYPOGRAPHY.md`](file:///docs/TYPOGRAPHY.md) |
| **Pandoc (`pandoc`)** | Local CLI Tool | Markdown AST document conversion (EPUB, DOCX, HTML) | Local system binary | High | [`docs/COMPATIBILITY.md#L9-L16`](file:///docs/COMPATIBILITY.md#L9-L16), [`scripts/lib/importer.py`](file:///scripts/lib/importer.py) |
| **Obsidian** | Local Desktop App | Knowledge base & World Bible editing (32 pre-configured offline plugins with SHA-256 manifest) | Local filesystem / plugins | Medium (First-Class Vault) | [`templates/world-bible/.obsidian/plugins/manifest.json`](file:///templates/world-bible/.obsidian/plugins/manifest.json), [`docs/guides/OBSIDIAN_PLUGINS.md`](file:///docs/guides/OBSIDIAN_PLUGINS.md) |
| **PolyGlot / Condict** | Local Desktop App / CLI | Dedicated conlang lexicon construction, phonotactics, and sound changes | Local files (`.pgd`, `.sqlite`) | Medium (Optional) | [`docs/CONLANG.md`](file:///docs/CONLANG.md), [`docs/guides/EXTERNAL_TOOLS_AND_PLUGINS.md`](file:///docs/guides/EXTERNAL_TOOLS_AND_PLUGINS.md) |
| **Gramps** | Local Desktop App | Comprehensive genealogical tree construction and pedigree charting | Local XML / SQLite | Medium (Optional) | [`docs/GENEALOGY.md`](file:///docs/GENEALOGY.md), [`docs/guides/EXTERNAL_TOOLS_AND_PLUGINS.md`](file:///docs/guides/EXTERNAL_TOOLS_AND_PLUGINS.md) |
| **Wonderdraft** | Local Desktop App | High-resolution cartography and fantasy map generation | Local `.wonderdraft_map` | Medium (Optional) | [`docs/CARTOGRAPHY.md`](file:///docs/CARTOGRAPHY.md), [`docs/guides/EXTERNAL_TOOLS_AND_PLUGINS.md`](file:///docs/guides/EXTERNAL_TOOLS_AND_PLUGINS.md) |
| **Celestia / StarGen** | Local Desktop App / CLI | Real-time 3D orbital mechanics, astrophysics, and planet generation | Local `.ssc`, `.stc` | Medium (Optional) | [`docs/ASTROPHYSICS.md`](file:///docs/ASTROPHYSICS.md), [`docs/guides/EXTERNAL_TOOLS_AND_PLUGINS.md`](file:///docs/guides/EXTERNAL_TOOLS_AND_PLUGINS.md) |
| **novelWriter** | Local Desktop App | Outlining and long-form prose drafting | Local `.nwx` project files | Medium (Optional) | [`templates/manuscript/nwProject.nwx`](file:///templates/manuscript/nwProject.nwx) |
| **Calibre (`ebook-convert`)** | Local CLI Tool | EPUB3 book compilation | Local system binary | Medium (Optional) | [`scripts/setup_arcanum.sh#L142-L209`](file:///scripts/setup_arcanum.sh#L142-L209) |
| **Linux Desktop (XDG)** | OS Desktop Shell | Desktop application menu entries, MIME bindings, and taskbar icons | Local `.desktop` specs | Medium (First-Class Linux) | [`launchers/arcanum-app.desktop`](file:///launchers/arcanum-app.desktop), [`launchers/arcanum-hub.desktop`](file:///launchers/arcanum-hub.desktop) |
| **Systemd Units** | Linux OS Service/Timer | Background verified archive timers and auto-backup schedules | Local user systemd unit | Medium (Optional) | [`configs/`](file:///configs/) |

---

### 2) Data Stores

| Store | Role | Access Layer | Key Risk | Evidence |
|:---|:---|:---|:---|:---|
| **Plain Markdown / YAML Files** | Primary persistent storage for lore & prose | `fs_utils.py` & `_bootstrap.py` (atomic writes) | Partial write corruption (mitigated by `atomic_write()`) | [`scripts/lib/_bootstrap.py`](file:///scripts/lib/_bootstrap.py) |
| **JSON Cache (`.arcanum_cache.json`)** | Mtime-based accelerated engine cache | `scripts/lib/cache.py` | Stale cache entries (mitigated by mtime invalidation) | [`scripts/lib/cache.py`](file:///scripts/lib/cache.py) |
| **Sprint Log (`sprint_log.jsonl`)** | Append-only drafting session history | `scripts/lib/writing_sprint.py` | Unclosed writes (mitigated by atomic locks) | [`scripts/lib/writing_sprint.py`](file:///scripts/lib/writing_sprint.py) |

---

### 3) Secrets and Credentials Handling

- **Zero Remote Credentials**: The system operates 100% offline with zero cloud API keys, zero token dependencies, and zero remote tracking.
- **Hardcoding Probes**: Enforced by Ruff `S` security rules and [`tests/test_threat_model.py`](file:///tests/test_threat_model.py) (0 hardcoded credentials).
- **GPG Keyring**: Optional local GPG encryption for archive snapshots uses the author's local system keyring without network transmission ([`scripts/lib/backup.py`](file:///scripts/lib/backup.py)).

---

### 4) Reliability and Failure Behavior

- **Deterministic Fallbacks**: Missing external tools gracefully degrade to standard format outputs (e.g. Markdown fallback if Typst or Pandoc is not installed).
- **Zero-Pip Core Execution**: All core CLI subcommands execute cleanly on any machine with standard Python 3.10+.
- **Sub-Second Execution**: Deterministic AST algorithms execute in milliseconds.

---

### 5) Observability for Integrations

- **Unified Doctor Diagnostic**: `python scripts/arcanum doctor` probes all 10 integrated tools and reports operational readiness.
- **Subprocess Error Logging**: External tool invocations capture stdout/stderr with detailed failure diagnostics.

---

### 6) Evidence

- [`scripts/lib/_bootstrap.py#L1-L80`](file:///scripts/lib/_bootstrap.py#L1-L80)
- [`scripts/lib/data_access.py#L1-L80`](file:///scripts/lib/data_access.py#L1-L80)
- [`scripts/lib/diagnostics.py#L1-L120`](file:///scripts/lib/diagnostics.py#L1-L120)
- [`scripts/lib/cache.py#L1-L60`](file:///scripts/lib/cache.py#L1-L60)
- [`docs/COMPATIBILITY.md#L1-L40`](file:///docs/COMPATIBILITY.md#L1-L40)
- [`tests/test_threat_model.py#L1-L50`](file:///tests/test_threat_model.py#L1-L50)
