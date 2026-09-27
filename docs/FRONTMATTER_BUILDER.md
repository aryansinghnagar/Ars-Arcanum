# Frontmatter Builder & Metadata Normalizer (`frontmatter_builder`)
> **Domain G: Publishing & Preflight** | **CLI:** `arcanum frontmatter`

---

## 1. Overview & Theoretical Rationale
The **Frontmatter Builder** standardizes YAML frontmatter headers across all markdown files in a project, ensuring consistent schema compliance for automated indexing, story canvas arrangement, and static codex compilation.

---

## 2. Standard Chapter Frontmatter Schema
```yaml
---
title: "The Silent Citadel"
chapter: 1
pov: "Aurelia Vance"
location: "Khorvath Fortress"
thread: "Main Conspiracy"
timeline_day: 42
tension: 7.5
sensory_focus: ["auditory", "thermoception"]
status: "revised"
---
```

---

## 3. Subfeatures Matrix
- **Interactive CLI Wizard**: Prompts authors interactively to fill missing metadata.
- **Batch Normalization**: Automatically aligns legacy key names (e.g. `character` $\to$ `pov`, `setting` $\to$ `location`).
- **Dry-Run Mode**: Inspects proposed frontmatter modifications before writing to disk.

---

## 4. CLI Usage Examples
```bash
# Normalize frontmatter across all manuscript chapters
arcanum frontmatter 01_Manuscript/ --normalize

# Run interactive metadata wizard for unindexed chapters
arcanum frontmatter 01_Manuscript/Chapter_12.md --interactive
```
