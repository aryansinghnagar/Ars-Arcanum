# Ars Arcanum — The Grand Tour: 21-Stage Sovereign Lifecycle Verification

> `tests/test_grand_tour_e2e.py` · **v5.0.0 — The Sovereign Craft Studio & Reference Encyclopedia** · Full-Pipeline Integration Harness

---

## Overview

The **Grand Tour** is the definitive end-to-end integration test harness for Ars Arcanum. It exercises the deterministic craft engines in a single ordered test ([`tests/test_grand_tour_e2e.py`](file:///tests/test_grand_tour_e2e.py)), verifying that the full sovereign authoring pipeline operates as a coherent integrated system from Cosmos initialization through to multi-bundle release compilation and static telemetry cockpit export.

Each of the 21 stages asserts invariants before proceeding to the next, making it impossible for a downstream stage to silently mask an upstream failure.

---

## Why the Grand Tour Exists

Unit tests verify individual engine correctness in isolation. The Grand Tour answers the harder question: **do all deterministic domain engines work together as a sovereign authoring operating system?**

Specifically, the Grand Tour verifies:

- **API contract stability**: Parameter validation, data classes, and method signatures operate seamlessly across engine boundaries.
- **Data flow integrity**: From initial YAML frontmatter and chapter drafting through to knowledge mesh graphs and FTS5 indexes.
- **Cross-engine pipeline coherence**: The corpus exported in Stage 10 and 21 is mathematically consistent with the manuscript authored in Stage 3.
- **Strict offline CSP enforcement**: Verifies that every generated HTML report contains valid Content-Security-Policy headers (`default-src 'none'`) without external CDNs.
- **Zero-Pip Dependency Guarantee**: All 21 stages execute exclusively on standard library Python primitives.

---

## Test Execution

```bash
# Run the Grand Tour standalone
python -m unittest tests/test_grand_tour_e2e.py

# Run as part of the full test discovery suite (853 tests)
python -m unittest discover tests
```

---

## The 21 Stages

### Stage 1 — Cosmos Universe & Manuscript Scaffolding
**Engine**: [`scripts/lib/fs_utils.py`](file:///scripts/lib/fs_utils.py) / [`scripts/lib/_bootstrap.py`](file:///scripts/lib/_bootstrap.py)
Scaffolds a test Cosmos directory with the canonical directory layout: `universe.yaml`, `world.yaml`, `Characters/`, `Places/`, `Magic/`, `Factions/`, and `Manuscripts/`.

### Stage 2 — Cosmos Lore Bible Population
**Engine**: Standardized YAML frontmatter note generation.
Populates canonical lore entities: `Characters/Lyra_Vael.md`, `Places/Valenreach.md`, `Magic/Aetheric_Resonance.md`, and `Factions/Silver_Tribunal.md`.

### Stage 3 — Multi-Chapter Manuscript Drafting with Directives
**Engine**: Markdown authoring with `@pov:`, `@time:`, `@char:`, `@location:`, and scene headers.
Authors multiple chapters with embedded narrative metadata and frontmatter declarations.

### Stage 4 — World Doctor Diagnostic Audit
**Engine**: [`scripts/lib/world_doctor.py`](file:///scripts/lib/world_doctor.py) $\to$ `check_world(world_dir)`
Runs deep diagnostic validation across link integrity, YAML schemas, and timeline invariants.

### Stage 5 — Dual-Track Timeline Synchronization
**Engine**: [`scripts/lib/timeline_sync.py`](file:///scripts/lib/timeline_sync.py) $\to$ `extract_timeline_events()` + `analyze_timeline_synchronization()`
Extracts chronologic dates vs. narrative sequence and detects temporal bilocation paradoxes.

### Stage 6 — Character Cast & Entity Association
**Engine**: [`scripts/lib/dramatis_personae.py`](file:///scripts/lib/dramatis_personae.py) $\to$ `scan_character_profiles()`
Extracts character dossiers from YAML frontmatter and computes Levenshtein name collisions.

### Stage 7 — Local Semantic Retrieval (Vault Search) Indexing & Query
**Engine**: [`scripts/lib/vault_search.py`](file:///scripts/lib/vault_search.py) $\to$ `LocalLoreRetrievalEngine().load_from_directory()` + `.query()`
Loads the World Bible into hybrid TF-IDF / SQLite FTS5 search index and executes semantic lore queries.

### Stage 8 — Multi-Calendar & Era Chronology
**Engine**: [`scripts/lib/calendar.py`](file:///scripts/lib/calendar.py) $\to$ `load_calendar_spec()` + `get_moon_phase()`
Calculates astronomical moon phases and synodic cycles from world calendar configurations.

### Stage 9 — Narrative Structure & Story Canvas Modeling
**Engine**: [`scripts/lib/structure.py`](file:///scripts/lib/structure.py) + [`scripts/lib/story_canvas.py`](file:///scripts/lib/story_canvas.py)
Evaluates manuscript beat distribution across 11 classical paradigms and generates the interactive corkboard.

### Stage 10 — Universal Corpus Exporter (JSONL, SQLite, Markdown)
**Engine**: [`scripts/lib/corpus_export.py`](file:///scripts/lib/corpus_export.py) $\to$ `CorpusScanner` + `export_jsonl()` + `export_sqlite()` + `export_markdown_summary()`
Scans the cosmos and exports structured JSONL datasets and SQLite databases with FTS5 search indexing.

### Stage 11 — Multi-Volume Series Omnibus Compilation
**Engine**: [`scripts/lib/omnibus.py`](file:///scripts/lib/omnibus.py) $\to$ `discover_series_volumes()` + `compile_omnibus_manuscript()`
Discovers all series volumes and compiles an omnibus manuscript with unified frontmatter and unified Table of Contents.

### Stage 12 — Series Continuity & Mortality Tracking
**Engine**: [`scripts/lib/series_continuity.py`](file:///scripts/lib/series_continuity.py) $\to$ `audit_series_continuity()`
Audits character trait drift, aging timeskips, and mortality invariants across multi-volume series.

### Stage 13 — Sovereign Studio Desktop Hub Static Telemetry Compilation
**Engine**: [`scripts/lib/studio_hub.py`](file:///scripts/lib/studio_hub.py) $\to$ `collect_studio_hub_data()` + `export_static_studio_hub()`
Compiles live telemetry into a standalone, 100% offline CSP-compliant HTML telemetry dashboard.

### Stage 14 — Sovereign Writing Sprint & Session Velocity Analytics
**Engine**: [`scripts/lib/writing_sprint.py`](file:///scripts/lib/writing_sprint.py) $\to$ `start_sprint()`, `end_sprint()`, `compute_velocity_stats()`, `generate_sprint_report_html()`
Tracks writing sprint sessions, computes words-per-minute velocity, calculates daily streaks, and renders analytics HTML.

### Stage 15 — Causal DAG Novikov Self-Consistency & Revision Density Heatmap
**Engine**: [`scripts/lib/causality.py`](file:///scripts/lib/causality.py) + [`scripts/lib/revision_heatmap.py`](file:///scripts/lib/revision_heatmap.py)
Audits multi-paradigm causality timelines for closed timelike curves (CTCs) and generates chapter revision churn metrics.

### Stage 16 — Multi-Volume Dramatis Personae Synthesis
**Engine**: [`scripts/lib/dramatis_personae.py`](file:///scripts/lib/dramatis_personae.py) $\to$ `cross_reference_manuscripts()`, `generate_dramatis_personae_markdown()`, `generate_dramatis_personae_html()`
Synthesizes cross-volume character rosters into Markdown tables and interactive visual character galleries.

### Stage 17 — World Codex, Arcane Constraints, Genealogy, Conlang & Factions
**Engine**:
- [`scripts/lib/codex_export.py`](file:///scripts/lib/codex_export.py) (Static single-file offline encyclopedia wiki)
- [`scripts/lib/magic_system.py`](file:///scripts/lib/magic_system.py) (Thermodynamic arcane rule and catalyst validator)
- [`scripts/lib/genealogy.py`](file:///scripts/lib/genealogy.py) (Dynastic lineage flowcharts & validation)
- [`scripts/lib/conlang.py`](file:///scripts/lib/conlang.py) (Phonotactics & historical sound shift engine)
- [`scripts/lib/factions.py`](file:///scripts/lib/factions.py) (Geopolitical diplomacy audit, alliance balance)

### Stage 18 — Planetary Economics, Journey Modeler & Cartography
**Engine**:
- [`scripts/lib/economy.py`](file:///scripts/lib/economy.py) (In-world economy, trade route gravity model, supply shocks)
- [`scripts/lib/journey.py`](file:///scripts/lib/journey.py) (Overland travel calculations, Naismith's rule, and journey reports)
- [`scripts/lib/cartography.py`](file:///scripts/lib/cartography.py) (Vector SVG map generation and interactive map viewer)

### Stage 19 — Worldbuilding Sciences, Climate, Ecology & Astrophysics
**Engine**:
- [`scripts/lib/astrophysics.py`](file:///scripts/lib/astrophysics.py) (Stellar classification, Keplerian orbits, habitable zones)
- [`scripts/lib/climate.py`](file:///scripts/lib/climate.py) (Planetary insolation, atmospheric circulation, orographic rain shadows)
- [`scripts/lib/ecology.py`](file:///scripts/lib/ecology.py) (Trophic energy pyramids, 10% rule, food-web cycle detection)
- [`scripts/lib/tactical_sim.py`](file:///scripts/lib/tactical_sim.py) (Lanchester law tactical combat simulator)

### Stage 20 — Authoring Studios, Ambient Audio & Typography Cleaner
**Engine**:
- [`scripts/lib/ambient.py`](file:///scripts/lib/ambient.py) (Pure trigonometric sine-wave binaural beat soundscape)
- [`scripts/lib/zen_studio.py`](file:///scripts/lib/zen_studio.py) (Distraction-free typewriter studio with in-situ lore drawer)
- [`scripts/lib/typography_cleaner.py`](file:///scripts/lib/typography_cleaner.py) (Curly quotes, em-dashes, and ellipsis normalizer)
- [`scripts/lib/portfolio.py`](file:///scripts/lib/portfolio.py) (Multi-manuscript catalog dashboard and velocity analytics)

### Stage 21 — Universal Resonance Mesh & Knowledge Discovery
**Engine**:
- [`scripts/lib/resonance.py`](file:///scripts/lib/resonance.py) (47-node deterministic knowledge mesh graph & causal cascades)
- [`scripts/lib/tips.py`](file:///scripts/lib/tips.py) (Contextual craft wisdom rotation)
- [`scripts/lib/vault_search.py`](file:///scripts/lib/vault_search.py) (Local semantic retrieval query)
- [`scripts/lib/world_doctor.py`](file:///scripts/lib/world_doctor.py) (Deep cosmos integrity audit)

---

## Verification Pipeline

```bash
# Run the complete test suite (853 tests)
python -m unittest discover tests

# Verify zero lint errors
ruff check .

# Verify type safety
mypy --config-file mypy.ini --explicit-package-bases scripts/lib tests
```
