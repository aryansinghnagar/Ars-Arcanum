# Obsidian Sovereign Worldbuilding & Authoring Suite (`docs/guides/OBSIDIAN_PLUGINS.md`)
> **Domain A: Lore, Worldbuilding, Drafting & Editorial Infrastructure** | **GPA 4.0 / Grade A+**

---

## 1. Overview & Architectural Philosophy

The **Ars Arcanum Obsidian Suite** transforms a standard Markdown vault into an industrial-grade narrative operating system, relational database, dynamic visual story canvas, and worldbuilding concordance.

While standard Obsidian serves as a general-purpose note-taking tool, writing epic speculative fiction requires specialized data structures:
1. **Dynamic Lore Querying**: Instant relational tables listing all characters allied with a specific faction, their alive/deceased status, and chapter appearances.
2. **Strict Frontmatter Schemas**: Validated dropdown fields and typed constraints preventing typos in character roles, dates, or magic affinities.
3. **Linguistics & Genealogy Visualization**: Root morpheme validation and dynamic lineage graphs on Canvas.
4. **Prose Quality & Style Telemetry**: Real-time sentence variance, passive voice linting, and readability scoring.
5. **Non-Gregorian Astronomical Time**: Tracking multi-moon cycles, custom calendars, and overlapping timeline events.
6. **Automated Git Versioning**: Silent, background Git commits every 10 minutes without breaking flow state.

```
+-------------------------------------------------------------------------------+
|                    ARS ARCANUM OBSIDIAN INTEGRATION ARCHITECTURE              |
|                                                                               |
|  +--------------------+     Strict fileClass Schema   +--------------------+  |
|  | Markdown Note      | ----------------------------> | Metadata Menu &    |  |
|  | (Character/Faction)|                               | Dataview Relational|  |
|  +--------------------+                               +--------------------+  |
|            |                                                    |             |
|            v                                                    v             |
|  [Calendarium Time Engine]                            [Storyline & Roots Web] |
|  (Custom Moons & Epochs)                              (Interactive Kinship)   |
|            |                                                    |             |
|            +----------------------------------------------------+             |
|                                     |                                         |
|                                     v                                         |
|                   +-----------------------------------+                       |
|                   |  Longform & Outliner Sequencers   |                       |
|                   |  Sentence Rhythm & Write Good     |                       |
|                   |  Obsidian Git 10-Min Local Commits|                       |
|                   +-----------------------------------+                       |
|                                     |                                         |
|                                     v                                         |
|                     [The Sovereign Speculative World Bible]                   |
|                     [32 Plugins / 100% Local-First / Zero Cloud Telemetry]    |
+-------------------------------------------------------------------------------+
```

---

## 2. Core Plugin Suite & Narrative Capabilities (32 Plugins)

```mermaid
mindmap
  root((Obsidian Suite (32 Plugins)))
    Linguistics & Conlangs
      Rootweave
      LanguageForge
    Relational Lore & Data
      Dataview DQL
      Metadata Menu
      Templater
      Tag Wrangler
      Footnote Shortcut
      Copy Block Link
    Kinship & Genealogies
      Canvas Roots
      Storyline
    Drafting, Focus & Outlining
      Longform
      Noveler Page Mode
      Obsidian Outliner
      Typewriter Mode
      Writing Goals
      Novel Word Count
    Editorial, Style & Prose
      Commentator Track Changes
      Sentence Rhythm
      Smart Typography
      Write Good
      Readability Score
      Valeon Vale Bridge
      LanguageTool Server
      Global Search & Replace
    Time & Cartography
      Calendarium
      April Automatic Timelines
      Obsidian Leaflet
      Storyteller Suite
    Publishing & Styling
      Obsidian Pandoc
      Obsidian Git
      formatForge
      Style Settings
```

| Plugin Name | Identifier | Primary Function | Pre-Configured Capabilities & Workflows |
|---|---|---|---|
| **Rootweave** | `rootweave` | Conlang Lexicon & Morphemes | In-vault morpheme manager, word builder/validator, dictionary compiler, and interlinear glossing in notes. |
| **LanguageForge** | `languageforge` | Naming Cultures & Phonology | Phonology-based name/vocabulary generator and language family tree visualizer. |
| **Dataview** | `dataview` | Relational Database & Queries | Executes DQL (Dataview Query Language) across character dossiers, faction rosters, and magic rules. |
| **Metadata Menu** | `metadata-menu` | Frontmatter Schema Enforcement | Strict `fileClass` schemas with modal dropdowns, type checking, and auto-completion for YAML keys. |
| **Canvas Roots** | `charted-roots` | Visual Family Trees on Canvas | Visual family trees, pedigrees, descendant trees, and GEDCOM timeline integrations on Obsidian Canvas. |
| **Storyline** | `storyline` | Character Relationship Matrix | Visual node graphs of alliances, rivalries, kinship trees, and character arc trajectories. |
| **Longform** | `longform` | Manuscript Organization | Drag-and-drop scene ordering, atomic drafting pane, inline comment stripping (`%% note %%`), and compile bridge. |
| **Noveler** | `noveler-a-storyline-expansion` | Dedicated Manuscript Surface | Visual page layout mode, formatting toolbar, live status bar counts, and StoryLine scene routing. |
| **Obsidian Outliner** | `obsidian-outliner` | Hierarchical Scene Outliner | Keyboard-driven tree outliner for structuring plot points, scene sequences, and notes. |
| **Typewriter Mode** | `typewriter-mode` | Drafting Focus & Ergonomics | Keeps cursor centered on screen, dims inactive paragraphs, and highlights current sentence for distraction-free flow. |
| **Writing Goals** | `writing-goals` | Pacing & Sprint Telemetry | Tracks daily word count sprints and novel project goals with visual progress rings linked to note frontmatter (`word-goal`). |
| **Novel Word Count** | `novel-word-count` | Live Explorer Telemetry | Injects live word counts beside every chapter, folder, and act in the file explorer tree. |
| **Commentator** | `commentator` | Track Changes & Editorial Review | Plain-text **CriticMarkup** review mode (`{++add++}`, `{--del--}`, `{>>comment<<}`) with live visual preview and accept/reject sidebar. |
| **Sentence Rhythm** | `sentence-rhythm` | Prose Variation Telemetry | Real-time color-coding of sentences based on length (Gary Provost cadence mapping). |
| **Smart Typography** | `obsidian-smart-typography` | Typesetting Punctuation | Automatically formats straight quotes to curly quotes (`“ ”`), double hyphens to em-dashes (`—`), and ellipses (`…`). |
| **Write Good** | `write-good` | Prose & Style Linting | Active in-editor highlighting of passive voice, weasel words, adverb overuse, and wordy phrases. |
| **Readability Score** | `readability-score` | Readability Telemetry | Real-time Flesch Reading Ease (FRE) score and US grade level in the status bar. |
| **Valeon** | `valeon` | Vale CLI Prose Linter | In-vault integration for the Vale prose linter, enforcing style guides and author dictionaries. |
| **LanguageTool** | `languagetool` | Offline Grammar & Spellcheck | Contextual grammar and spelling checking connected to a local/offline LanguageTool server. |
| **Global Search & Replace** | `global-search-and-replace` | Vault-Wide Naming Refactor | Multi-file Regex search and replace with side-by-side diff previews for character and settlement name updates. |
| **Calendarium** | `calendarium` | Astronomical & Calendar Mechanics | Non-Gregorian fictional calendars, custom month lengths, moon phase cycles, and in-world event agendas linked via `fc-date`. |
| **April Automatic Timelines** | `aprils-automatic-timelines` | Automated Chronology Generator | Generates dynamic horizontal/vertical timeline views across scenes and history notes using frontmatter dates. |
| **Obsidian Leaflet** | `obsidian-leaflet-plugin` | Interactive Vector Maps | Embeds interactive high-resolution fantasy maps with custom coordinates, marker pins, polygon layers, and distance rulers. |
| **Storyteller** | `storyteller-suite` | Spatial Interactive Cartography | Pins interactive lore nodes and settlement gazetteers directly to high-resolution world map images. |
| **Footnote Shortcut** | `obsidian-footnotes` | World Bible Annotations | Instant hotkey footnote scaffolding (`[^1]`) with in-place popup editing and auto-indexing for lore treatises and appendices. |
| **Copy Block Link** | `obsidian-copy-block-link` | Deep Lore Referencing | 1-click context menu copying of deep block links (`[[Note#^block-id]]`) for quoting lore inside scene notes. |
| **Tag Wrangler** | `tag-wrangler` | Lore Taxonomy & Tag Refactor | Bulk tag renaming, merging, and tag page hubs directly from the tag pane. |
| **Templater** | `templater-obsidian` | Dynamic Template Engine | Injects date math, UUIDs, folder context, and default frontmatter on note creation. |
| **Obsidian Pandoc** | `obsidian-pandoc` | Manuscript Export Bridge | Direct 1-click export from manuscript notes to industry-standard submission formats (**DOCX**, **EPUB**, **PDF**, **Typst**). |
| **Obsidian Git** | `obsidian-git` | Automated Local Version Control | Silent background Git commits every 10 minutes and on file close, with zero network requirements. |
| **formatForge** | `formatforge` | Novel Typography & Dividers | Typography palettes, novel themes, and decorative scene dividers for manuscripts. |
| **Style Settings** | `obsidian-style-settings` | Focus Typography & Layout | Distraction-free typography, custom line measure, and distraction-free dark/sepia themes. |

---

## 3. Dynamic Dataview Relational Queries (DQL)

### 3.1 Active Character Roster by Faction
```sql
```dataview
TABLE role AS "Role", status AS "Status", origin AS "Origin"
FROM "World/Characters"
WHERE contains(faction, "House Vaelen") AND status != "Deceased"
SORT file.name ASC
```
```

### 3.2 Unfulfilled Prophecies & Ominous Timeline Clauses
```sql
```dataview
TABLE era_given AS "Era", oracle AS "Oracle / Source", intended_resolution AS "Target"
FROM "World/Prophecy"
WHERE fulfillment_status = "Unfulfilled"
SORT era_given ASC
```
```

---

## 4. Editorial Review & CriticMarkup Workflow

The pre-configured **Commentator** plugin enables non-destructive, plain-text editorial review cycles between author and editors without proprietary database locks:

| CriticMarkup Syntax | Rendered Visual State | Editorial Intent |
|---|---|---|
| `{++added text++}` | Green underline / highlight | Proposed addition to manuscript |
| `{--deleted text--}` | Red strikethrough | Proposed deletion from prose |
| `{~~original~>replacement~~}` | Red strikethrough $\to$ Green text | Proposed word choice substitution |
| `{>>editor comment<<}` | Margin note / highlight bubble | Inline question or craft note |
| `{==highlighted text==}` | Yellow background highlight | Emphasis for line revision pass |

* **Accept/Reject**: Click any suggested mark or use the sidebar review pane to accept or reject changes across scenes.
* **100% Plain-Text Portability**: All review tokens are standard CriticMarkup stored directly inside Markdown files.

---

## 5. Plugin Supply-Chain Integrity & Cryptographic Manifest

To guarantee air-gapped security and defense against supply-chain tampering, all 32 bundled Obsidian plugins are tracked in a cryptographic SHA-256 manifest:

- **Manifest Location**: [`templates/world-bible/.obsidian/plugins/manifest.json`](file:///templates/world-bible/.obsidian/plugins/manifest.json)
- **Active Registry**: [`templates/world-bible/.obsidian/community-plugins.json`](file:///templates/world-bible/.obsidian/community-plugins.json)
- Every file (`main.js`, `manifest.json`, `styles.css`, `data.json`) is hashed with SHA-256 digests.
- Verified as part of the automated regression suite to ensure zero untracked code modifications.
