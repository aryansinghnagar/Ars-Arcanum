# External Project Importer Engine (`importer`)
> **Domain F: Retrieval & Infrastructure** | **CLI:** `arcanum import`

---

## 1. Overview & Theoretical Rationale
The **Importer Engine** provides zero-dependency conversion and migration utilities for onboarding projects created in Scrivener, Obsidian, Word, or plain markdown folders into the Ars Arcanum directory and metadata architecture.

---

## 2. Ingestion Pipeline & Normalization
1. **Archive Expansion**: Unpacks `.scriv` packages or `.zip` archives.
2. **XML / RTF Parser**: Extracts text content and structural hierarchy from `scrivx` project manifests.
3. **AST CommonMark Normalizer**: Cleans whitespace, converts proprietary style tags into standard markdown headings, and extracts author notes into frontmatter annotations.
4. **Directory Organization**: Arranges chapters into `01_Manuscript/` and world notes into `00_World_Bible/`.

---

## 3. CLI Command Examples
```bash
# Import a Scrivener 3 project
arcanum import my_novel.scriv --output ./Universes/MyNovel/

# Import an Obsidian lore vault
arcanum import ./ObsidianVault/ --type obsidian --output ./Worlds/Aethelgard/
```
