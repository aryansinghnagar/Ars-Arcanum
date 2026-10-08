# Ars Arcanum / Scriptorium — Author's Quick Start Guide
> **The Sovereign, 100% Offline Writing & Worldbuilding Studio for Fiction Authors.**
> **Release Version:** `v0.1.0` | **License:** MIT | **Privacy:** 100% Offline, Zero Telemetry

Welcome! Ars Arcanum provides a distraction-free, professional writing environment that puts you in complete control of your creative work. All notes, chapters, and lore dossiers remain in standard plain Markdown (`.md`) and YAML frontmatter manifests on your own computer—free from subscription fees, cloud lock-in, or telemetry.

---

## 🚀 1. Getting Started in 3 Clicks

### Step 1: Launch the Studio
Launch the GTK3 Desktop App via `python scripts/arcanum_app.py` or run the CLI dispatcher `arcanum` (or `python -m scripts.lib.cli`) in your terminal. For the browser-based studio, run `arcanum hub` or `arcanum zen`.

### Step 2: First-Flight Onboarding
When you launch for the first time, the **Onboarding Wizard** appears:
- **New Universe**: Enter a name (e.g. `Solaris-Verse`) to create your narrative cosmos and starter world lore vault.
- **Generate Demo Cosmos**: Click to generate *"The Chronicles of Eldoria"*, pre-populated with starter characters, magic systems, bestiary creatures, and sample manuscript chapters.
- **Open Existing**: Point to an existing universe or manuscript folder.

---

## 🎨 2. The Integrated Creative Studios

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Ars Arcanum Studio Hub                          │
├──────────────┬──────────────┬──────────────┬─────────────┬─────────────┤
│ 🪐 Cosmos     │ ✍️ Drafting   │ 🔮 Speculative │ 📚 Publish  │ 🔒 Safety   │
│   & Worlds   │   & Word     │    Sciences  │   & Export  │   & Backups │
└──────────────┴──────────────┴──────────────┴─────────────┴─────────────┘
```

### Studio 1: 🪐 Cosmos & Worlds (Lore Bible)
- **Open World Bible**: Launches your lore vault with full support for Obsidian wikilinks and structured frontmatter dossiers.
- **32 Bundled & Activated Plugins**: Pre-configured suite with pinned SHA-256 manifests including `rootweave`, `languageforge`, `charted-roots` (Canvas Roots), `obsidian-leaflet-plugin`, `obsidian-outliner`, `formatforge`, `valeon`, `write-good`, `languagetool`, `readability-score`, `longform`, `noveler-a-storyline-expansion`, `commentator` (CriticMarkup), `sentence-rhythm`, `calendarium`, `aprils-automatic-timelines`, `metadata-menu`, `tag-wrangler`, `typewriter-mode`, `writing-goals`, `global-search-and-replace`, and `obsidian-smart-typography`. See the [Master Reference Guide](file:///docs/guides/EXTERNAL_TOOLS_AND_PLUGINS.md) and [Obsidian Plugins Guide](file:///docs/guides/OBSIDIAN_PLUGINS.md).
- **Taxonomy Register**: View instant counts of characters, factions, magic systems, languages, and historical events registered across your world.

### Studio 2: ✍️ Manuscripts & Drafting
- **Visual Scene Inspector**: Select any chapter scene to view and edit scene metadata headers (`@pov:`, `@location:`, `@status:`, `@thread:`) without breaking your writing flow.
- **Word Processor Sync**: Click **"📝 Open in Word Processor"** to write or edit chapters directly in Microsoft Word or LibreOffice Writer. Click **"🔄 Sync DOCX ↔ Markdown"** to import changes safely.
- **Story Canvas & Corkboard**: Open `arcanum canvas` for visual drag-and-drop story corkboards and scene beat tracking.
- **Zen Studio**: Open `arcanum zen` for distraction-free typewriter drafting with in-situ lore drawer and sine-wave ambient soundscapes.

### Studio 3: 🔮 Speculative Sciences & Craft Studio
Access 47 deterministic offline modeling and consistency engines:
- **Astrophysics & Habitable Zones**: Calculate Keplerian orbits, stellar classification, and Roche limits.
- **Climate & Köppen Biomes**: Model atmospheric circulation cells, Coriolis deflections, and rain shadows.
- **Magic System Thermodynamics**: Verify energy sources, transformation costs, and caster exhaustion curves.
- **Timeline & Multi-Era Chronology**: Check dates, moon phases, and historical event sequences.
- **Faction Dynamics & Combat**: Evaluate diplomatic alliances and Lanchester law combat balances.
- **Conlang & Sound Shifts**: Generate phonemic inventories and apply historical sound shift mutations.

### Studio 4: 📚 Publishing & Book Compilation
- **1-Click Print PDF**: Sub-second compilation into trade-quality PDF using **Typst**.
- **EPUB & Ebook**: Compiles validated EPUB with cover art detection via Calibre.
- **Universal Corpus Exporter**: Export structured JSONL datasets and SQLite FTS5 databases for local LLMs and offline semantic retrieval (`vault_search`).
- **Omnibus Compiler**: Compile multi-volume series into unified anthologies with global Tables of Contents.

### Studio 5: 🔒 Snapshots & Safe Backups
- **📷 Quick Snapshot**: Record a 1-click version milestone in local Git (`Ctrl+S`).
- **Offline Verified Archive**: Create a standalone `.tar.gz` archive with SHA-256 integrity verification (`Ctrl+B`).
- **GPG Encryption**: Protect confidential manuscripts with AES-256 passphrase encryption.
- **Safe Restoration**: Non-destructive restore protection refusing to overwrite existing folders without `--force`.

---

## 📖 3. Master Reference Documentation

Every craft discipline in Ars Arcanum is paired with a masterclass reference manual in `docs/`:

| Craft / Science Discipline | Master Reference Manual |
| :--- | :--- |
| **Scene Construction & Swain MRUs** | [`docs/SCENE_MECHANICS.md`](file:///docs/SCENE_MECHANICS.md) |
| **Pacing & Provost Cadence** | [`docs/PACING.md`](file:///docs/PACING.md) |
| **Interactive Fiction & Branching** | [`docs/BRANCHING_GRAPH.md`](file:///docs/BRANCHING_GRAPH.md) |
| **Character Idiolects & Voice** | [`docs/VOICE.md`](file:///docs/VOICE.md) |
| **Classical Rhetoric & Prose Style** | [`docs/STYLISTICS.md`](file:///docs/STYLISTICS.md) |
| **Speculative Lexicons & Glossaries** | [`docs/CONCORDANCE.md`](file:///docs/CONCORDANCE.md) |
| **8-Channel Sensory Immersion** | [`docs/SENSES.md`](file:///docs/SENSES.md) |
| **Audio Proofing & Prosody** | [`docs/AUDIO_PROOF.md`](file:///docs/AUDIO_PROOF.md) |
| **Editorial Personas & Critique** | [`docs/COUNCIL.md`](file:///docs/COUNCIL.md) |
| **Astrophysics & Orbital Mechanics** | [`docs/ASTROPHYSICS.md`](file:///docs/ASTROPHYSICS.md) |
| **Planetary Climate & Biomes** | [`docs/CLIMATE.md`](file:///docs/CLIMATE.md) |
| **Trophic Ecology & Food Webs** | [`docs/ECOLOGY.md`](file:///docs/ECOLOGY.md) |
| **Lanchester Tactical Warfare** | [`docs/TACTICAL_SIM.md`](file:///docs/TACTICAL_SIM.md) |
| **Hard Magic System Thermodynamics** | [`docs/MAGIC_SYSTEM.md`](file:///docs/MAGIC_SYSTEM.md) |
| **Conlang Phonotactics & Grammar** | [`docs/CONLANG.md`](file:///docs/CONLANG.md) |

---

## 📚 4. Recommended Reading & Media

1. **McKee, Robert** (1997). *Story: Substance, Structure, Style and the Principles of Screenwriting*. ReganBooks.
2. **Truby, John** (2007). *The Anatomy of Story: 22 Steps to Becoming a Master Storyteller*. Faber & Faber.
3. **Swain, Dwight V.** (1965). *Techniques of the Selling Writer*. University of Oklahoma Press.
4. **Dole, Stephen H.** (1964). *Habitable Planets for Man*. RAND Corporation.
5. **Rosenfelder, Mark** (2010). *The Language Construction Kit*. Yonagu Books.
6. **Brandon Sanderson** (2020). *Creative Writing Lectures at BYU* (YouTube Course).
7. **Artifexian & Biblaridion** (YouTube Worldbuilding & Conlang Masterclasses).
