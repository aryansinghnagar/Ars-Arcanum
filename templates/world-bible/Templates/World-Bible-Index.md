---
type: dashboard
tags:
  - meta/index
---

# 📖 Sovereign World Bible & Codex Master Index

Welcome to your central worldbuilding hub. Every note created in this vault is interconnected via wikilinks, validated by `arcanum doctor`, and indexed dynamically below using **Dataview**.

> [!NOTE] ⚠️ EDUCATIONAL TEMPLATE (AI-GENERATED)
> **Notice**: This template was AI-generated for educational demonstration and craft guidance within the Ars Arcanum operating system. It is strictly non-commercial and provided solely to demonstrate system features, metadata schemas, and engine capabilities. Authors should replace placeholder values with their original worldbuilding details.

<details>
<summary>💡 <b>Ars Arcanum Engine Guidance & Feature Breakdown (Click to Expand)</b></summary>

### Features Demonstrated in This Index:
- **Central Knowledge Hub & Codex Exporter**: `codex_export` (`arcanum codex <WorldDir> --html`) — Compiles this entire index and linked notes into a standalone, searchable offline HTML encyclopedia.
- **Dynamic Dataview Aggregation**: Real-time structured query tables for characters, locations, factions, battles, astrophysics, conlangs, and writing sprints.
- **System Doctor & Integrity Audits**: `world_doctor` (`arcanum doctor`) — Scans all notes indexed here for broken cross-references, orphan files, and frontmatter parse errors.
- **Offline Semantic Search**: `local_rag` (`arcanum rag "query"`) — Uses TF-IDF and SQLite FTS5 to index all vault markdown content for offline contextual query retrieval.

### How to Use for Your Projects:
1. Click any template link in the Quick Navigation Directory below to scaffold a new lore note.
2. When creating notes, assign appropriate tags (`#world/character`, `#world/location`, `#world/faction`, etc.) to automatically populate the Dataview dashboards.
3. Keep the file paths organized under their domain folders for clean structure.
</details>

---

## 🏛️ Comprehensive Quick Navigation Directory

| Category | Primary Template | Specialized Sub-Templates |
| :--- | :--- | :--- |
| **Getting Started** | 🚀 **[[00_START_HERE\|Minimum Viable World Bible Guide]]** | — |
| **Characters & Cast**| 👤 **[[Characters/Character-Template\|Character Vault (Detailed)]]** | ⚡ **[[Characters/Character-Quickstart-Template\|Quickstart Character Card]]**<br/>🗣️ **[[Characters/Character-Voice-Profile-Template\|Character Voice Profile]]**<br/>👑 **[[Characters/Genealogy-Dynasty-Template\|Genealogy & Dynasties]]** |
| **Geography & Travel**| 🗺️ **[[Locations/Location-Template\|World Atlas & Geography]]** | 🌦️ **[[Locations/Climate-Biome-Template\|Climate & Köppen Biomes]]**<br/>🧭 **[[Locations/Cartography-Route-Template\|Cartography & Travel Routes]]** |
| **Factions & Warfare**| ⚔️ **[[Factions/Faction-Template\|Factions & Diplomatic Matrix]]** | 🛡️ **[[Factions/Tactical-Skirmish-Battle-Template\|Tactical Battle Simulator]]** |
| **Magic & Science** | ⚡ **[[Magic-Technology/Magic-Tech-System-Template\|Magic & Tech Systems]]** | 🗡️ **[[Artifacts/Artifact-Relic-Template\|Relics & Arcane Foci]]** |
| **Bestiary & Ecology**| 🐾 **[[Bestiary/Creature-Flora-Fauna-Template\|Bestiary & Species]]** | 🌿 **[[Bestiary/Ecology-Food-Web-Template\|Ecology & Trophic Webs]]** |
| **Cosmology & Time** | ✨ **[[Cosmology/Deity-Cosmology-Template\|Pantheons & Cosmology]]** | 🌌 **[[Cosmology/Astrophysics-System-Template\|Astrophysics & Orbital Mechanics]]**<br/>📅 **[[Cosmology/Calendar-Moons-Template\|Calendars & Lunar Phases]]**<br/>🔮 **[[Cosmology/Prophecy-Template\|Prophecy Lifecycle Tracker]]**<br/>🕸️ **[[Cosmology/Resonance-Mesh-Template\|Universal Resonance Mesh]]** |
| **History & Causality**| ⏳ **[[History/Timeline-Event-Template\|Historical Chronology]]** | 🔀 **[[History/Causality-Timeline-Branch-Template\|Causality & Multiverse Branches]]** |
| **Linguistics** | 🗣️ **[[Languages/Glossary-Conlang-Template\|Linguistics & Conlangs]]** | — |
| **Macroeconomics** | 💰 **[[Economies/Economy-Template\|Macroeconomics & Currencies]]** | — |
| **Drafting Tools** | 📝 **[[Templates/Daily-Writing-Log\|Writing Sprint Logs]]** | 🎬 **[[Templates/Scene-Note-Template\|Scene & Sequel Worksheets]]** |
| **System & Ops** | ⚙️ **[[Templates/System-Engineering-and-Ops-Guide\|System & Ops Guide]]** | 🛠️ **[[../manuscript/Outlines/Revision-Diff-and-Diagnostics-Workflow\|Revision & Diff Workflow]]** |

---

## 👤 Active Characters
```dataview
TABLE role as "Role", status as "Status", faction as "Faction", current_location as "Location"
FROM #world/character
SORT file.name ASC
```

---

## 🗺️ Key Locations & Realms
```dataview
TABLE region as "Region", dominant_faction as "Ruling Faction", scale as "Scale", danger_level as "Danger"
FROM #world/location
SORT file.name ASC
```

---

## ⚔️ Factions & Power Structures
```dataview
TABLE leader as "Leader", headquarters as "HQ", faction_type as "Type", influence_level as "Influence"
FROM #world/faction
SORT file.name ASC
```

---

## ⚡ Magic & Tech Systems
```dataview
TABLE classification as "Classification", source_of_power as "Power Source", prevalence as "Prevalence", danger_cost as "Cost / Danger"
FROM #world/system
SORT file.name ASC
```

---

## 🗣️ Languages & Dialects
```dataview
TABLE language_family as "Family", spoken_by as "Spoken By", status as "Status", writing_system as "Writing System"
FROM #world/language
SORT file.name ASC
```

---

## 🐾 Bestiary & Flora / Fauna
```dataview
TABLE classification as "Classification", threat_level as "Threat", habitat as "Habitat"
FROM #world/bestiary
SORT file.name ASC
```

---

## 🗡️ Legendary Artifacts & Relics
```dataview
TABLE artifact_type as "Type", rarity as "Rarity", current_bearer as "Bearer"
FROM #world/artifact
SORT file.name ASC
```

---

## ✨ Pantheons, Deities & Cosmology
```dataview
TABLE concept_type as "Type", domain as "Domain", worship_status as "Worship"
FROM #world/cosmology
SORT file.name ASC
```

---

## ⏳ Historical Timeline
```dataview
TABLE year as "Year", era as "Era", primary_location as "Location", significance as "Significance"
FROM #world/history
SORT year ASC
```

---

## 📊 Recent Writing Logs
```dataview
TABLE words_written as "Words", writing_time_minutes as "Minutes", mood_focus as "Focus (1-5)"
FROM #meta/log
SORT date DESC
LIMIT 10
```
