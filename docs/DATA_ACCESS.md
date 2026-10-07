# Centralized Data Access Layer (DATA_ACCESS)
> **Engineering Specification & Cache Architecture** | Release v0.1.0 | Core Infrastructure Layer

---

## 1. Executive Summary & Design Rationale

In a large speculative fiction universe with thousands of lore dossier notes, multi-volume manuscripts, and dozens of cross-auditing engines (such as Continuity, Resonance, Economy, Factions, and World Doctor), executing repetitive filesystem traversals and YAML AST parsing creates significant disk I/O bottlenecks.

The **Centralized Data Access Layer (DAL)** ([`scripts/lib/data_access.py`](file:///scripts/lib/data_access.py)) provides a thread-safe, high-speed cached reader and AST query layer across all Ars Arcanum repositories. It guarantees:

1. **Zero Redundant Disk Reads**: Memoizes file text, YAML frontmatter dictionaries, and Markdown bodies in an in-memory `OrderedDict` LRU cache (500-file capacity).
2. **Deterministic mtime Invalidation**: Every cached entry tracks file modification timestamp (`mtime`) and file size (`size`). If a file is edited in Obsidian, novelWriter, or Zen Studio, the DAL automatically detects the stale cache and re-parses the file on the next access.
3. **Explicit Eviction Hook (`.evict(path)`)**: When saving chapters or editing notes programmatically (e.g. via Zen Studio or Studio Hub REST API), calling `dal.evict(path)` immediately flushes that file's cache entry to ensure subsequent reads reflect the fresh disk state.
4. **Thread Safety**: Uses recursive locks (`threading.RLock`) to support concurrent reads, evictions, and cache updates from GUI threads, background timer tasks, and multi-engine CLI pipelines.
5. **Structured Entity & Chapter Queries**: Provides high-level abstractions (`get_vault_entities`, `get_manuscript_chapters`) so engines work with structured Python dataclasses rather than raw filesystem globbing.

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
               |  - OrderedDict LRU cache (Cap: 500)       |
               |  - Automatic mtime / size change checks   |
               |  - Explicit .evict(path) invalidation     |
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

# 3. Explicit cache eviction upon write operations
dal.evict("/path/to/note.md")

# 4. Structured entity discovery across lore categories
entities = dal.get_vault_entities("/path/to/world", category="Characters")
for ent in entities:
    print(f"Character: {ent['name']} (Path: {ent['path']})")

# 5. Structured manuscript chapter queries
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

## 4. Recursive Frontmatter Parsing Engine

The DAL extracts YAML frontmatter delimited by `---` blocks via [`scripts/lib/frontmatter.py`](file:///scripts/lib/frontmatter.py):
- **Recursive Zero-Pip Parser**: Full standard-library YAML parser handling arbitrary dictionary nesting, lists of objects (`subordinates:\n  - name: Alistair\n    rank: Captain`), inline arrays (`tags: [a, b]`), and multi-line block scalars (`|` literal, `>` folded).
- **Typed Scalar Coercion**: Automatically coerces booleans (`true`/`false`), integers (`42`), floats (`3.14`), and quoted strings (`"value"`, `'value'`).
- **Obsidian Wiki-Link Resolution**: Automatically strips or indexes wiki-link brackets (`[[Aethelgard]]` $\to$ `Aethelgard`) for relationship graphs and entity indexing.
- **Prose Preservation**: Preserves raw body text unchanged without extraneous allocations.

---

## 5. Verification & Testing

The Data Access Layer is thoroughly tested in [`tests/test_data_access.py`](file:///tests/test_data_access.py), [`tests/test_frontmatter.py`](file:///tests/test_frontmatter.py), and [`tests/test_cache.py`](file:///tests/test_cache.py), verifying:
- LRU cache capacity boundaries (eviction of least-recently-used items when exceeding 500 entries).
- Programmatic cache invalidation with `.evict(path)`.
- Cache hit vs. cache miss counters.
- Automatic cache invalidation upon `mtime` modification.
- Concurrent multi-threaded reads under thread pool stress.
- Complex nested YAML AST parsing across all template schemas.
- Zero external dependencies on `PyYAML` or third-party parsing libraries.
