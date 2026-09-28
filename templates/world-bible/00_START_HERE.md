---
type: guide
tags:
  - meta/guide
  - meta/start
---

# 🚀 Start Here: The Sovereign World Bible & Ars Arcanum Craft Ecosystem

Welcome to your **Ars Arcanum World Bible**! This sovereign lore vault is designed to connect seamlessly with your manuscript, your command-line craft engines, and your Obsidian drafting environment.

> [!NOTE] ⚠️ EDUCATIONAL TEMPLATE (AI-GENERATED)
> **Notice**: This template was AI-generated for educational demonstration and craft guidance within the Ars Arcanum operating system. It is strictly for educational purposes and is not meant to be used for commercial purposes. Authors should replace all placeholder content with their own original creative worldbuilding and manuscript prose.

<details>
<summary>💡 <b>Ars Arcanum Engine Guidance & Feature Breakdown (Click to Expand)</b></summary>

### Features Demonstrated in This Ecosystem:
- **Core Lore Validation**: `world_doctor` (`arcanum doctor`) — Audits your vault for broken wikilinks, orphan notes, timeline contradictions, and missing frontmatter schemas.
- **Dynamic Craft Wisdom**: `tips` (`arcanum tip`) — Ambiently provides non-obvious masterclass craft advice tailored to your active worldbuilding domain.
- **Local Semantic Retrieval**: `local_rag` & `corpus_export` (`arcanum rag`, `arcanum corpus`) — Index your lore notes into offline TF-IDF and SQLite FTS5 vectors for sovereign search and local LLM context feeding.
- **Single-File Wiki Publishing**: `codex_export` (`arcanum codex <WorldDir> --html`) — Compiles your entire world into a standalone offline HTML encyclopedia with interactive spoiler shields.
- **Cross-Domain Knowledge Mesh**: `resonance` (`arcanum resonance mesh`) — Maps connections between your celestial physics, languages, factions, magic systems, and manuscript scenes.

### How to Use the Templates for Your Projects:
1. **Never worldbuild to procrastinate**: Start with the 3-Step Quickstart below. Only flesh out lore categories as your story demands them.
2. **Preserve Frontmatter Structure**: The YAML frontmatter (`---`) at the top of each note powers the CLI craft calculations, Dataview indexing, and cross-volume continuity checks.
3. **Use Wikilinks Liberally**: Type `[[Note-Name]]` whenever referencing characters, locations, factions, relics, or historical events to knit your world into a living knowledge graph.
</details>

---

> **The Golden Rule of Sovereign Worldbuilding**:
> *You do **not** need to fill out all lore categories before you start writing.*
> Worldbuilding serves the story—never let worldbuilding become procrastination.

---

## 🎯 The 3-Step Quickstart (Zero Overwhelm)

If this is your first time using Ars Arcanum, follow this lightweight 3-step path to get drafting in under 5 minutes:

### 1. Create Your Protagonist (2 minutes)
- Open `Characters/` and create a note for your main character.
- Use **[[Characters/Character-Quickstart-Template|Character-Quickstart-Template]]** (just 5 essential fields) if you want to move fast, or **[[Characters/Character-Template|Character-Template]]** if you want deep psychological backstory, voice profiling, and lineage tracking.

### 2. Create Your Starting Location (1 minute)
- Open `Locations/` and create a note for your story's opening setting (e.g. `Iron-Spire-City`).
- Fill in a quick 2-sentence description and sensory mood, or use **[[Locations/Location-Template|Location-Template]]**.

### 3. Open Your Manuscript & Write!
- Open your manuscript in `~/Manuscripts/<ManuscriptName>` (or launch from Control Center / Studio Hub) in **novelWriter** or **Obsidian**.
- Open `Book-01/01_Act_I/01_Chapter_01.md`.
- Set `@pov: YourCharacterName` and start writing prose.

---

## 🌳 Comprehensive Domain Template Directory

As your narrative unfolds, create new lore notes when they appear in your draft using the specialized domain templates below. Each template includes concrete illustrative examples, YAML metadata schemas, and collapsed engine guidance:

| Lore Domain | Target Folder | Dedicated Template | Underlying Craft Engines & Functions |
| :--- | :--- | :--- | :--- |
| **Characters & Cast** | `Characters/` | [[Characters/Character-Template\|Character-Template]] | `continuity`, `dramatis_personae`, `series_continuity` |
| **Character Quickstart** | `Characters/` | [[Characters/Character-Quickstart-Template\|Character-Quickstart-Template]] | `world_doctor`, `dramatis_personae` |
| **Dialogue & Voice** | `Characters/` | [[Characters/Character-Voice-Profile-Template\|Character-Voice-Profile-Template]] | `voice` (formality, lexical richness, rhythm) |
| **Dynasties & Lineages** | `Characters/` | [[Characters/Genealogy-Dynasty-Template\|Genealogy-Dynasty-Template]] | `genealogy` (pedigrees, succession rules, houses) |
| **Locations & Atlas** | `Locations/` | [[Locations/Location-Template\|Location-Template]] | `cartography`, `senses`, `continuity` |
| **Climate & Biomes** | `Locations/` | [[Locations/Climate-Biome-Template\|Climate-Biome-Template]] | `climate` (Köppen biomes, rain shadows, insolation) |
| **Routes & Logistics** | `Locations/` | [[Locations/Cartography-Route-Template\|Cartography-Route-Template]] | `journey` (travel march times, rations, water, baggage) |
| **Factions & Guilds** | `Factions/` | [[Factions/Faction-Template\|Faction-Template]] | `factions` (diplomacy matrix, alliances, treaties) |
| **Tactics & Battles** | `Factions/` | [[Factions/Tactical-Skirmish-Battle-Template\|Tactical-Skirmish-Battle-Template]] | `tactical_sim` (troop frontage, morale, Lanchester attrition) |
| **Magic & Tech Systems** | `Magic-Technology/`| [[Magic-Technology/Magic-Tech-System-Template\|Magic-Tech-System-Template]] | `magic_system` (energy costs, backlash, spell tiers) |
| **Relics & Artifacts** | `Artifacts/` | [[Artifacts/Artifact-Relic-Template\|Artifact-Relic-Template]] | `magic_system`, `continuity`, `history` |
| **Bestiary & Wildlife** | `Bestiary/` | [[Bestiary/Creature-Flora-Fauna-Template\|Creature-Flora-Fauna-Template]] | `ecology`, `senses`, `continuity` |
| **Food Webs & Ecology**| `Bestiary/` | [[Bestiary/Ecology-Food-Web-Template\|Ecology-Food-Web-Template]] | `ecology` (trophic cascades, biomass transfer) |
| **Pantheons & Deities** | `Cosmology/` | [[Cosmology/Deity-Cosmology-Template\|Deity-Cosmology-Template]] | `cosmology`, `magic_system`, `factions` |
| **Astrophysics & Orbits**| `Cosmology/` | [[Cosmology/Astrophysics-System-Template\|Astrophysics-System-Template]] | `astrophysics` (Keplerian orbits, Roche limits, dilation) |
| **Planetary Calendars** | `Cosmology/` | [[Cosmology/Calendar-Moons-Template\|Calendar-Moons-Template]] | `calendar` (synodic moons, conjunctions, leap cycles) |
| **Prophecies & Fate** | `Cosmology/` | [[Cosmology/Prophecy-Template\|Prophecy-Template]] | `prophecy` (fulfillment conditions, subversions, oracle) |
| **Resonance & Themes** | `Cosmology/` | [[Cosmology/Resonance-Mesh-Template\|Resonance-Mesh-Template]] | `resonance` (cross-domain knowledge mesh, cascades) |
| **Historical Events** | `History/` | [[History/Timeline-Event-Template\|Timeline-Event-Template]] | `history`, `timeline_sync`, `continuity` |
| **Timeline Branches** | `History/` | [[History/Causality-Timeline-Branch-Template\|Causality-Timeline-Branch-Template]] | `causality` (divergence points, paradox indices) |
| **Linguistics & Conlangs**| `Languages/` | [[Languages/Glossary-Conlang-Template\|Glossary-Conlang-Template]] | `conlang` (phonotactics, syllable templates, lexicon) |
| **Macroeconomics** | `Economies/` | [[Economies/Economy-Template\|Economy-Template]] | `economy` (currencies, trade routes, inflation, guilds) |
| **Writing Logs & Sprints**| `Templates/` | [[Templates/Daily-Writing-Log\|Daily-Writing-Log]] | `writing_sprint`, `portfolio`, `ambient`, `zen_studio`, `studio_hub`, `cache` |
| **Scene Note & Sequel** | `Templates/` | [[Templates/Scene-Note-Template\|Scene-Note-Template]] | `scene_mechanics`, `pacing`, `senses`, `timeline_sync` |
| **System Ops & Engine Diagnostics** | `Templates/` | [[Templates/System-Engineering-and-Ops-Guide\|System-Engineering-and-Ops-Guide]] | `world_doctor`, `diagnostics`, `cache`, `fs_utils`, `migrate`, `config`, `local_rag`, `corpus_export`, `codex_export`, `resonance`, `tips` |

---

## 💡 Pro-Tips for Connected Lore

- **Wikilinks**: Type `[[Character-Name]]` anywhere in notes or draft scenes to create a living link.
- **Auto-Rosters**: When you set `faction: "[[Faction-Name]]"` in a character note, that character automatically appears in that faction's member table on the [[Templates/World-Bible-Index|World Bible Index]].
- **Consistency Checking**: Run `arcanum doctor` or click **Doctor Diagnostics** in the Control Center anytime to check for broken links or typos in character names.
- **Dynamic Craft Advice**: Run `arcanum tip` or `arcanum tip <engine>` to get context-aware worldbuilding advice straight from the engine wisdom registry.

---

## ⚙️ First-Time Obsidian Vault Setup Note

When opening this vault for the first time in Obsidian:
1. When prompted about **Restricted Mode**, click **"Turn on community plugins"**.
2. All plugin configurations (`dataview`, `storyline`, `calendarium`, `obsidian-git`, `metadata-menu`, `longform`, `novel-word-count`, `storyteller-suite`, `templater-obsidian`) are already pre-configured in `.obsidian/plugins/` to work seamlessly offline.
