# Universal Granular Target Scoping & Context Engine (SCOPE)
> **Engineering Specification & Author Craft Reference** | Release v0.1.0 | Core Utility Layer

---

## 1. Executive Overview & Mission

In speculative fiction authoring and large-scale worldbuilding universes, operations frequently need to span different context altitudes: from auditing a single scene's dialogue or tension arc, to analyzing an entire 5-volume series omnibus, to querying an Obsidian world bible across specific lore taxonomies.

The **Ars Arcanum Scope Engine** ([`scripts/lib/scope.py`](file:///scripts/lib/scope.py), [`scripts/lib/scope_models.py`](file:///scripts/lib/scope_models.py), [`scripts/lib/scope_parser.py`](file:///scripts/lib/scope_parser.py), and [`scripts/lib/scope_resolver.py`](file:///scripts/lib/scope_resolver.py)) provides a deterministic, universal targeting and context-filtering system. It ensures:

1. **Altitude-Aware Defaults**: Engines never scan the entire filesystem or whole universe vault by default unless explicitly invoked with `--all`. When unconstrained, engines automatically resolve the local context via configuration (`config.json`), working directory structure, or single-project discovery.
2. **Universal Scope Expression Mini-Language**: Authors and CLI tools can specify fine-grained chapter, scene, volume, world, and category slices with concise, human-friendly range syntax (e.g. `--scope "ch:1-5,sc:1-2"` or `-b "1-3" --chapter "1,3,7-10"`).
3. **Zero-Overhead Memory & AST Slicing**: Scene and chapter extraction parses Markdown and YAML frontmatter lazily, allowing engines to run sub-millisecond audits on specific narrative slices without loading multi-megabyte corpora into memory.

---

## 2. Universal CLI Options & Flags

All Ars Arcanum craft and core engines inherit the standard scope CLI arguments via `add_scope_arguments(parser)`:

| CLI Option | Shorthand | Type / Format | Purpose & Description |
|:---|:---|:---|:---|
| `--manuscript` | `--ms` | String / Path | Target a specific manuscript project directory or name in `~/Manuscripts/`. |
| `--manuscripts` | | Comma-separated | Target multiple manuscripts (e.g. `--manuscripts "Trilogy-01,Trilogy-02"`). |
| `--series` | | String | Target all manuscripts tagged with a specific series identifier. |
| `--books` | `-b`, `--book`, `--volume`, `--volumes` | String / Range | Target specific volumes or book ranges (e.g. `-b 1-3`, `-b "Book-01,Book-02"`). |
| `--chapter` | `--chapters`, `--ch` | Integer Range / List | Target chapter ranges or lists (e.g. `--ch "1-5"`, `--ch "1,3,7-10"`, `--ch "ch01..ch05"`). |
| `--scene` | `--scenes`, `--sc` | Integer Range / List | Target scene slices within chapters (e.g. `--sc "1-3"`, `--sc "sc01..sc02"`). |
| `--world` | `-w` | String / Path | Target an Obsidian World Lore Vault directory or name in `~/Universes/<UNIVERSE>/<WORLD>`. |
| `--worlds` | | Comma-separated | Target multiple world vaults simultaneously. |
| `--universe` | `-u` | String / Path | Target an entire narrative universe root in `~/Universes/<UNIVERSE>`. |
| `--lore-category` | `--lore-categories` | Comma-separated | Restrict lore scans to specific subdirectories (e.g. `Characters,Locations,Factions`). |
| `--scope` | | Expression String | Unified composite scope mini-language expression. |
| `--all` | | Boolean Flag | Explicitly override local defaults to process all discovered manuscripts and worlds. |

---

## 3. Unified Scope Expression Mini-Language

The `--scope` argument accepts a compact, comma-separated key-value syntax combining multiple dimensions into a single parameter:

```bash
# Target Chapters 1 through 5, Scene 1 of Book-01
arcanum audit dialogue --scope "book:1,ch:1-5,sc:1"

# Target Characters and Locations inside world vault "Aethelgard"
arcanum search "solar ritual" --scope "world:Aethelgard,cat:Characters,Locations"

# Run continuity audit across Book-01 and Book-02 for Chapters 10 to 15
arcanum continuity --scope "ms:Book-01,Book-02,ch:10-15"
```

### Supported Tokens & Range Syntaxes

- **Numeric Range Expansion**: `1-5` $\to$ `[1, 2, 3, 4, 5]`
- **Dot Range Expansion**: `ch01..ch05` $\to$ `[1, 2, 3, 4, 5]`
- **Discontinuous Lists**: `1,3,7-10` $\to$ `[1, 3, 7, 8, 9, 10]`
- **Volume Shorthands**: `b1`, `Book-01`, `vol2`, `Volume-02` are normalized automatically.
- **Lore Taxonomy Keys**: `cat:Characters`, `cat:Factions,Locations`, `category:MagicSystems`.

---

## 4. Python API Architecture

Engines integrate with the Scope Engine via standard primitives in [`scripts/lib/scope.py`](file:///scripts/lib/scope.py):

```python
from scripts.lib.scope import (
    EngineScope,
    add_scope_arguments,
    extract_scope_from_args,
    filter_manuscript_scope,
    filter_world_scope,
)

# 1. Register CLI arguments into argparse
parser = argparse.ArgumentParser(description="My Craft Engine")
add_scope_arguments(parser)
args = parser.parse_args()

# 2. Extract structured EngineScope dataclass
scope: EngineScope = extract_scope_from_args(args)

# 3. Filter manuscript chapters and scene slices
filtered_chapters = filter_manuscript_scope(
    manuscript_dir="/path/to/manuscript",
    scope=scope,
)

for target in filtered_chapters:
    print(f"Chapter {target.chapter_num}: {target.title} ({len(target.scenes)} scenes)")

# 4. Filter world lore markdown files
filtered_lore_notes = filter_world_scope(
    world_dir="/path/to/world",
    scope=scope,
)
```

---

## 5. Chapter & Scene Slicing Mechanics

When slicing manuscripts, the Scope Engine processes chapter files via `ChapterTarget` and `SceneSlice` dataclasses ([`scripts/lib/scope_models.py`](file:///scripts/lib/scope_models.py)):

```text
Chapter File (e.g. 01_Chapter_01.md)
├── Frontmatter AST (@pov, @time, @location, @thread)
├── Scene 1 (delimited by '---', '***', or '### Scene 1')
│   ├── Word count & paragraph metrics
│   └── In-situ tags
└── Scene 2
    ├── Scene-level dialogue & action blocks
    └── In-situ tags
```

### Scene Break Detection
The engine recognizes standard narrative scene break conventions:
- Horizontal rules (`---`, `***`, `* * *`)
- Scene headers (`### Scene 1`, `## Scene 2`)
- Explicit NovelWriter tags (`@scene:`, `@scene_id:`)

---

## 6. Verification & Quality Gates

The Scope Engine is validated by strict unit tests in [`tests/test_scope.py`](file:///tests/test_scope.py), covering:
- Single, multi, and disjoint chapter range expansion.
- Case-insensitive volume and scene token parsing.
- World lore taxonomy filtering and path traversal sanitization.
- Composite scope string tokenization and error recovery.
