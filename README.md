# 🖋️ Ars Arcanum — Sovereign Authoring Operating System & Craft Studio

> **A 100% offline, privacy-first operating system and craft studio for speculative fiction authors, worldbuilders, and narrative designers.**  
> Zero cloud dependencies · Zero telemetry · Deterministic rails over probabilistic drift · Your intellectual property, sovereign forever.

[![Release: v0.1.0](https://img.shields.io/badge/Release-v0.1.0-blue.svg)](CHANGELOG.md)
[![Status: Sovereign Craft Studio](https://img.shields.io/badge/Status-Sovereign%20Studio-brightgreen.svg)](#)
[![Tests: 353+](https://img.shields.io/badge/Tests-353%2B%20Passing%20(100%25)-brightgreen.svg)](#)
[![Coverage: 80%+](https://img.shields.io/badge/Coverage-80%25%2B-brightgreen.svg)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Zero-Pip](https://img.shields.io/badge/Dependencies-Zero--Pip%20(100%25%20Stdlib)-success.svg)](#)

---

## The Sovereignty Principle

> **"Measure everything that helps the author think; prescribe nothing unless the author explicitly asks for a prescription."**

Ars Arcanum (code-named *Scriptorium*) is a sovereign, local-first authoring platform and worldbuilding operating system. It provides speculative fiction novelists, epic fantasy worldbuilders, and narrative designers with an exhaustive professional craft studio—from secondary-world bibles and conlang phonotactics to sub-second typesetting and omnibus compilation—without a single cloud dependency, external telemetry ping, or Python pip requirement.

All manuscripts and lore vaults are stored in **standard CommonMark Markdown** (`.md`), human-readable **YAML frontmatter**, and standard **DOCX / Typst** source. Your intellectual property remains un-scraped, un-monetized, and completely readable 50 years from now on any POSIX or Windows machine.

---

## ✨ Architectural Pillars & Studio Capabilities

| Studio Component | Core Capabilities |
|:--|:--|
| **🎯 Altitude-Aware Scoping** | Execute craft engines on exact slices: scenes (`--scenes 1-3`), chapters (`-c 1-5`, `ch01..ch05`), books (`-b 1-2`), lore categories, or worlds without whole-vault overhead. |
| **🪐 World Bible Ecosystem** | Obsidian-compatible vault architecture with 32 pre-configured offline community plugins and structured schemas for characters, cultures, pantheons, genealogies, and magic systems. |
| **✍️ Editorial & Churn Telemetry** | Structural markdown diffs (`arcanum diff`), editing density heatmaps (`arcanum heatmap`), and multi-manuscript catalog portfolio dashboards (`arcanum portfolio`). |
| **🔄 Bidirectional Sync** | Seamless roundtrip Markdown ↔ DOCX synchronization (`arcanum sync`) and zero-dependency standard manuscript submission builder (`arcanum docx`). |
| **🔮 Sovereign Core Engines & Toolchain** | 14 sovereign core Python engines alongside an integrated toolchain (PolyGlot, Gramps, Wonderdraft, Celestia, StarGen, Typst) across Linguistics, Genealogy, Cartography, Astrophysics, Pacing, Economy, and Narrative Geometry. |
| **📚 Sub-Second Typesetting & Publishing** | Single-command compilation to print-ready PDF (Typst presets), clean EPUB (Pandoc), submission DOCX (William Shunn format), and multi-volume series omnibus compilation (`arcanum omnibus`). |
| **🔒 Immutable Safety & Cryptography** | POSIX/Windows atomic file writes (`atomic_write`), cross-platform file locking (`ArcanumLock`), SHA-256 backup verification, and GPG encryption (`arcanum backup`, `arcanum restore`, `arcanum snapshot`). |
| **🩺 Unified Health Diagnostics** | Complete system health, toolchain inspection, and vault link consistency doctor (`arcanum doctor`). |

---

## 🏛️ The Three Subsystems & Epistemic Safety

To protect authorial sovereignty and prevent technical algorithms from masquerading as subjective aesthetic rules, Ars Arcanum strictly segregates all operations into three isolated subsystems:

```mermaid
graph TD
    subgraph Subsystem1["Subsystem 1: Invariant Consistency Engine"]
        S1["Deterministic Safety & Syntax"]
        S1A["• Atomic File I/O (atomic_write)"]
        S1B["• Cross-Platform Locking (ArcanumLock)"]
        S1C["• SHA-256 Vault Checksums"]
        S1D["• Author-Declared Rules ([AUTHOR RULE])"]
        S1E["Fails builds (exit 1) on syntax/IO errors or --strict"]
    end

    subgraph Subsystem2["Subsystem 2: Selected Craft Lenses"]
        S2["Advisory Telemetry & Reference Overlays"]
        S2A["• Gary Provost Syntactic Waveforms"]
        S2B["• Dwight Swain MRU Sequence Tracking"]
        S2C["• Save the Cat & 3-Act Milestone Windows"]
        S2D["• Whittaker Climate & Lanchester Dynamics"]
        S2E["Always advisory (exit 0 default), dismissible via @intent"]
    end

    subgraph Subsystem3["Subsystem 3: Creative Ideation & Sparks"]
        S3["Combinatorial Analogy & Generative Prompts"]
        S3A["• Trope Inversions & Dialectical Sparks"]
        S3B["• Mythic Resonance Conceptual Bridges"]
        S3C["• Historical Anachronism Ideation"]
        S3D["Clearly labeled with [SPECULATION] tags"]
    end
```

### The 6-Tier Diagnostic Severity Taxonomy
Diagnostics across all engines are categorized into six explicit severity tiers:
1. **`CANON_ERROR`**: Provable contradiction against explicit author-declared facts.
2. **`RULE_CONFLICT`**: Violation of an explicit author-declared world invariant (`[AUTHOR RULE]`).
3. **`OBSERVATION`**: Objective statistical telemetry (word counts, sentence distributions, timeline ordering).
4. **`LENS_NOTE`**: Insights generated by an opt-in craft lens (Save the Cat, Swain MRUs, Provost waveforms).
5. **`SUGGESTION`**: Optional revision pathways presenting concrete tradeoffs.
6. **`EXPERIMENT`**: Creative prompts and speculative brainstorming labeled with `[SPECULATION]`.

---

## 📜 The Authorial Constitution

Authors declare their narrative conventions, world axioms, and diagnostic filters in `constitution.yaml` or `constitution.json`:

```yaml
---
# ~/.config/ars-arcanum/config.json or World/Manuscript constitution.yaml
canon:
  authority: author
  narrator_reliability: unreliable       # Allows narrative ambiguity
  allow_unresolved_mysteries: true

style:
  passive_voice: observe                 # "observe" | "allow"
  repetition: observe                    # "observe" | "allow"
  filter_verbs: observe

structure:
  framework: three_act                   # "none" | "three_act" | "kishotenketsu" | "heros_journey"
  mode: descriptive                      # Observational telemetry only

magic:
  modality: mythic                       # "mythic" | "soft" | "rationalist" | "unconstrained"
  enforce_thermodynamics: false

continuity:
  timeline: flexible
  preserve_poetic_variation: true        # Permits metaphorical eye/hair color variations

diagnostics:
  default_severity: advisory             # Universal exit code 0 default
  suppressed_rules: []                   # Rule IDs to silence
---
```

---

## ⚡ 5-Minute Quickstart

### Prerequisites
- Python 3.10+ (Standard Library only — zero pip packages required)
- *Optional recommended tools:* Git, Pandoc, Typst, Obsidian

### 1. Installation

**Linux / macOS:**
```bash
git clone https://github.com/aryansinghnagar/Ars-Arcanum.git Ars-Arcanum
cd Ars-Arcanum
bash scripts/setup_arcanum.sh
```

**Windows (PowerShell):**
```powershell
git clone https://github.com/aryansinghnagar/Ars-Arcanum.git Ars-Arcanum
cd Ars-Arcanum
powershell -ExecutionPolicy Bypass -File scripts\setup_arcanum.ps1
```

### 2. Launching CLI Commands

```bash
# Unified system health & toolchain diagnostics
python scripts/arcanum doctor

# Structural markdown diff visualizer
python scripts/arcanum diff Draft-01 Draft-02 --html diff_report.html

# Manuscript revision density & editing churn heatmap
python scripts/arcanum heatmap --chapters 1-5 --export-html heatmap.html

# Multi-manuscript portfolio dashboard
python scripts/arcanum portfolio --html portfolio.html

# Bidirectional Markdown <-> DOCX synchronization
python scripts/arcanum sync pull --docx manuscript.docx

# Multi-volume series omnibus compiler
python scripts/arcanum omnibus compile --format epub

# Cryptographically verified standalone archive
python scripts/arcanum backup --tag milestone-1
```

---

## 🗂️ Sovereign Vault Structure

```
~/Universes/<UniverseName>/
├── universe.yaml              → Overarching cosmological container
└── <WorldName>/               → Obsidian-compatible World Bible lore vault
    ├── world.yaml             → World manifest & axioms
    ├── constitution.yaml      → Local Authorial Constitution
    ├── Characters/            → Character dossiers, arcs, and voice profiles
    ├── Locations/             → Regional climate biomes, routes, and maps
    ├── Factions/              → Diplomatic matrices, treaties, and vassals
    ├── Magic-Technology/      → Magic modalities, costs, and limits
    ├── Bestiary/              → Species, ecosystems, and food webs
    ├── Artifacts/             → Relics, focal items, and provenance
    ├── Cosmology/             → Pantheons, astrophysics, and prophecies
    ├── History/               → Timelines, causal DAGs, and branches
    ├── Languages/             → Conlang morphosyntax and glossaries
    └── .obsidian/             → Pre-configured offline Obsidian workspace (32 plugins)

~/Manuscripts/<ManuscriptName>/
├── manuscript.yaml            → Links Universe, World Bible, and active book
├── constitution.yaml          → Manuscript-specific craft constitution
├── Book-01/                   → Dedicated repository container
│   ├── Draft-01/
│   │   ├── 01_Act_I/
│   │   │   ├── 01_Chapter.md  → Chapter markdown source with scene directives
│   │   │   └── 02_Chapter.md
│   │   └── 02_Act_II/
│   └── Export/                → PDF, EPUB, and submission DOCX exports
```

---

## 🔍 Verification & Engineering Gates

Ars Arcanum enforces strict deterministic quality gates across POSIX and Windows:

```bash
# 1. Full 48-module parallel test discovery (353+ tests, 0 failures)
python scripts/test_parallel.py

# 2. Strict Ruff linter pass (0 violations)
ruff check .

# 3. Strict Mypy static type checking across all 90 source files
mypy --explicit-package-bases scripts tests

# 4. Coverage Threshold Enforcement (>= 80%)
coverage run -m unittest discover tests; coverage report --fail-under=80

# 5. Canonical POSIX Integration Verification Harness
bash scripts/verify.sh
```


---

## 📖 Documentation Index

- **[📖 Author's Craft Manual](docs/AUTHOR_MANUAL.md)** — Exhaustive guide to sovereign worldbuilding and narrative drafting.
- **[🔌 External Tools & 32-Plugin Suite](docs/guides/EXTERNAL_TOOLS_AND_PLUGINS.md)** — Complete guide to all integrated external software and pre-configured Obsidian plugins.
- **[🧩 Obsidian Plugin Catalog](docs/guides/OBSIDIAN_PLUGINS.md)** — Exhaustive directory of the 32 pre-installed Obsidian plugins.
- **[💻 Software Catalog](docs/guides/SOFTWARE_CATALOG.md)** — Comprehensive software directory, installation vectors, and license matrix.
- **[🏛️ System Architecture Blueprint](docs/codebase/ARCHITECTURE.md)** — C4 diagrams, Three Subsystem breakdown, and engine topology.
- **[📚 Craft Logic Encyclopedia](docs/ENGINE_LOGIC_ENCYCLOPEDIA.md)** — Historical lineages, mathematical models, and tradeoffs for sovereign engines.
- **[⚡ Complete Setup & Installation Guide](docs/SETUP_GUIDE.md)** — Step-by-step installation instructions for Linux, macOS, and Windows.
- **[🔒 Security & Threat Model](docs/THREAT_MODEL.md)** — Air-gapped CSP policies, path traversal defense, and cryptographic guarantees.
- **[📚 Master Academic & Craft References](REFERENCES.md)** — 340+ verified academic and literary citations.

---

## 📄 License & Intellectual Property

Ars Arcanum is open-source software licensed under the **[MIT License](LICENSE)**.  
All creative works, manuscripts, world bibles, and lore created using Ars Arcanum remain the **100% sovereign intellectual property of the author**, free from any licensing claim, telemetry tracking, or cloud retention.
