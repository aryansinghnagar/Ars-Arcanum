# Centralized Data Access Layer (DATA_ACCESS)
> **Engineering Specification & Cache Architecture** | Release v0.1.0 | Core Infrastructure Layer

---

## 1. Executive Summary & Design Rationale

In a large speculative fiction universe with thousands of lore dossier notes, multi-volume manuscripts, and dozens of cross-auditing engines (such as Continuity, Resonance, Economy, Factions, and World Doctor), executing repetitive filesystem traversals and YAML AST parsing creates significant disk I/O bottlenecks.

The **Centralized Data Access Layer (DAL)** ([`scripts/lib/data_access.py`](file:///scripts/lib/data_access.py)) provides a thread-safe, high-speed cached reader and AST query layer across all Ars Arcanum repositories. It guarantees:

1. **Zero Redundant Disk Reads**: Memoizes file text, YAML frontmatter dictionaries, and Markdown bodies in-memory.
2. **Deterministic mtime Invalidation**: Every cached entry tracks file modification timestamp (`mtime`) and file size (`size`). If a file is edited in Obsidian, novelWriter, or Zen Studio, the DAL automatically detects the stale cache and re-parses the file on the next access.
3. **Thread Safety**: Uses recursive locks (`threading.RLock`) to support concurrent reads and cache updates from GUI threads, background timer tasks, and multi-engine CLI pipelines.
4. **Structured Entity & Chapter Queries**: Provides high-level abstractions (`get_vault_entities`, `get_manuscript_chapters`) so engines work with structured Python dataclasses rather than raw filesystem globbing.

---

## 2. Architectural Structure

```text
               +-------------------------------------------+
               |             Craft & Core Engines          |
               | (Continuity, Resonance, Economy, Doctor)  |
               +-------------------------------------------+
                                     |
                          [ get_dal() Singleton ]
                                     |
               +-------------------------------------------+
               |        DataAccessLayer (Thread-Safe)      |
               |  - RLock concurrency protection           |
               |  - In-memory _file_cache                  |
               |  - Automatic mtime / size change checks   |
               +-------------------------------------------+
                                     |
               +-------------------------------------------+
               |         Sovereign Vault on Disk           |
               |  (Markdown Files, YAML Frontmatter AST)   |
               +-------------------------------------------+
```

---

## 3. Python API & Methods

Engines obtain the global DAL instance using `get_dal()`:

```python
from scripts.lib.data_access import get_dal

dal = get_dal()

# 1. Thread-safe cached text file reading
content = dal.read_file("/path/to/note.md")

# 2. Fast cached Frontmatter AST and Markdown body extraction
frontmatter, body = dal.parse_frontmatter_and_body("/path/to/note.md")
character_role = frontmatter.get("role", "protagonist")

# 3. Structured entity discovery across lore categories
entities = dal.get_vault_entities("/path/to/world", category="Characters")
for ent in entities:
    print(f"Character: {ent['name']} (Path: {ent['path']})")

# 4. Structured manuscript chapter queries
chapters = dal.get_manuscript_chapters("/path/to/manuscript", book="Book-01")
for ch in chapters:
    print(f"Chapter {ch['chapter_num']}: {ch['title']} ({ch['word_count']} words)")
```

### Cache Statistics & Telemetry

```python
stats = dal.get_stats()
print(f"Cached Files: {stats['cached_files']}, Hits: {stats['cache_hits']}, Misses: {stats['cache_misses']}")
```

---

## 4. Frontmatter Parsing Engine

The DAL extracts YAML frontmatter delimited by `---` blocks:
- Custom zero-pip YAML dictionary parser handling nested objects, lists (`tags: [a, b]`, `languages:\n  - Solar\n  - High Archaic`), boolean/integer coercion, and double/single quoted strings.
- Strips obsidian wiki-link brackets (`[[Aethelgard]]` $\to$ `Aethelgard`) where appropriate for entity indexing.
- Preserves raw body text unchanged without extraneous allocations.

---

## 5. Verification & Testing

The Data Access Layer is thoroughly tested in [`tests/test_data_access.py`](file:///tests/test_data_access.py) and [`tests/test_cache.py`](file:///tests/test_cache.py), verifying:
- Cache hit vs. cache miss counters.
- Automatic cache invalidation upon `mtime` modification.
- Concurrent multi-threaded reads under thread pool stress.
- Malformed YAML frontmatter graceful degradation.
- Zero external dependencies on `PyYAML` or third-party parsing libraries.
