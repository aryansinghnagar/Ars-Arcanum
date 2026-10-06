# 🖋️ Ars Arcanum — Your Sovereign Writing Studio

> **A complete, distraction-free writing system for novelists and speculative worldbuilders.**  
> 100% offline · zero cloud · no subscriptions · your files, forever.

[![Release: v5.0.0](https://img.shields.io/badge/Release-v5.0.0-blue.svg)](CHANGELOG.md)
[![Status: Production Stable](https://img.shields.io/badge/Status-Production%20Stable-brightgreen.svg)](#)
[![CI](https://github.com/aryansinghnagar/Scriptorium/actions/workflows/ci.yml/badge.svg)](https://github.com/aryansinghnagar/Scriptorium/actions/workflows/ci.yml)
[![Tests: 1022](https://img.shields.io/badge/Tests-1020%2F1022%20Passing%2C%202%20Skipped-brightgreen.svg)](#)
[![Coverage: 86%](https://img.shields.io/badge/Coverage-86%25-brightgreen.svg)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Zero-Pip](https://img.shields.io/badge/Dependencies-Zero--Pip%20(100%25%20Stdlib)-success.svg)](#)

---

## What Is Ars Arcanum?

Ars Arcanum (code-named *Scriptorium*) is a **sovereign, local-first authoring platform** and craft studio. It gives fiction writers a complete professional studio — from world-bible lore notes all the way to print-ready PDFs — without a single cloud subscription, telemetry call, or pip dependency.

Everything you write is stored as **plain Markdown** (`.md`) and standard **Word format** (`.docx`) on your own hard drive. You can open your manuscript 50 years from now on any computer.

> [!IMPORTANT]
> **New here?** Skip straight to the [⚡ 5-Minute Setup](#-5-minute-setup) below, then open the [📖 Complete Setup Guide](docs/SETUP_GUIDE.md) for a step-by-step walkthrough with screenshots.

---

## ✨ What You Get

| Studio | What it does |
|:--|:--|
| **🖥️ Control Center** | One-click GTK desktop app (Linux) & browser-based Studio Hub (Cross-Platform) with real-time Scope Bar cockpit and live modal engine runner. |
| **🎯 Granular Target Scoping** | Run craft engines on exact targets — scenes (`--scene 1-3`), chapters (`-c 1-5`, `ch01..ch05`), books (`-b Book-01`), worlds (`-w`), or lore categories without whole-vault overhead. |
| **🪐 World Bible** | Obsidian-powered lore vault with pre-configured plugins for characters, maps, timelines, and magic systems. |
| **✍️ Drafting** | Write in Microsoft Word, LibreOffice, or Google Docs. Changes sync back to Markdown automatically. |
| **🔮 55+ Craft & Utility Engines** | Dynamic plugin extensibility, astrophysics, hard magic, conlang morphosyntax, deific cosmology, multi-agent editorial council, trade networks, and more — all offline. |
| **📚 1-Click Publishing** | Sub-second print PDF with commercial genre presets (Typst), EPUB (Pandoc), submission DOCX, and offline TTS proofreading. |
| **🔒 Vault Safety** | Pure-Python Git snapshots, SHA-256 verified backups, and USB replication — your work is never at risk. |
| **🧠 Semantic Search** | Ask questions across your entire lore library with local TF-IDF + SQLite full-text search. No API key needed. |

---

## ⚡ 5-Minute Setup

> **Full GUI Suite & Launchers:** Linux Mint 21/22 · Debian 12/13 · Ubuntu 22.04/24.04 · Fedora · Arch · openSUSE  
> **Core CLI, Studio Hub & 55+ Craft Engines:** Cross-Platform (Linux, macOS, Windows with Python 3.10+)  
> **CI-verified on:** Ubuntu 24.04, macOS, Windows (GitHub Actions matrix).

**Step 1 — Get the code:**
```bash
cd ~/Downloads
git clone https://github.com/aryansinghnagar/Scriptorium.git Ars-Arcanum
cd Ars-Arcanum
```

**Step 2 — Run the one-command installer:**
```bash
bash scripts/setup_arcanum.sh
```

This single command installs Git, Pandoc, literary fonts, Obsidian, novelWriter, Calibre, Typst, LibreOffice, FocusWriter, and all desktop launchers automatically. *(Takes 5–15 minutes depending on your internet speed.)*

**Step 3 — Launch:**  
Double-click **"Ars Arcanum Control Center"** on your Desktop and follow the welcome wizard.

> [!TIP]
> For a complete step-by-step walkthrough with troubleshooting, see the **[📖 Detailed Setup Guide](docs/SETUP_GUIDE.md)**.

---

## 🗂️ How Your Files Are Organized

```
~/Universes/<UniverseName>/
├── universe.yaml              → Your overarching narrative cosmos
└── <WorldName>/               → Open this directly as an Obsidian vault
    ├── world.yaml             → World manifest
    ├── Characters/            → Character profiles, arcs, and relationships
    ├── Locations/             → Maps, regional palettes, and landmarks
    ├── Factions/              → Guilds, empires, and ideologies
    ├── Magic-Technology/      → Hard/soft magic rules and constraints
    ├── Bestiary/              → Creatures, ecologies, and apex predators
    ├── Artifacts/             → Legendary relics and focal items
    ├── Cosmology/             → Pantheons, deities, and prophecies
    ├── History/               → Timelines and catalytic events
    ├── Languages/             → Conlangs, phonetic rules, and glossaries
    └── .obsidian/             → Pre-configured plugin suite

~/Manuscripts/<ManuscriptName>/
├── manuscript.yaml            → Links your Universe, World, and active draft
├── Book-01/                   → Dedicated Git repository per book
│   └── Draft-01/
│       ├── Draft-01_Manuscript.docx  → Consolidated Word draft
│       ├── 01_Act_I/
│       │   ├── 01_Chapter.md          → Markdown source (with scene tags)
│       │   └── 01_Chapter.docx        → Auto-synced Word version
│       └── 04_Back_Matter/            → Auto-generated Dramatis Personae & Glossary
├── Outlines/                  → Three-act beats and subplot matrices
├── Exports/                   → PDFs, EPUBs, and submission DOCXs
└── Backups/                   → Timestamped .tar.gz archives with SHA-256 digests
```

---

## 🔮 Featured Craft Engines (22 Highlighted / 53+ Total)

All engines run 100% offline using Python's standard library — no pip, no API keys, no internet. The full engine catalog (53 registered engines across 5 domain pillars) is accessible via `arcanum doc` or the Studio Hub Craft Guide tab.

| # | Engine | Key Commands | What It Does |
|---|---------|-------------|--------------|
| 1 | **Universal Craft Docs** | `arcanum doc <engine>` | In-CLI guide for all 50+ engines with storytelling applications |
| 2 | **Resonance Mesh** | `arcanum resonance [world]` | Cross-domain knowledge graph — finds thematic synergies between any two engines |
| 3 | **Astrophysics** | `arcanum calc transit`, `arcanum calc orbit` | Relativistic spaceflight, planetary systems, $1g$ Brachistochrone trajectories |
| 4 | **Hard Magic** | `arcanum magic check` | Sanderson-style rule contradiction and axiom consistency detector |
| 5 | **Genealogy** | `arcanum genealogy <House>` | Family tree DAG with disputed claims and Mermaid export |
| 6 | **Conlang** | `arcanum conlang generate <Lang>` | Syllable word generator with phoneme frequency and sound-law shifts |
| 7 | **Narrative Pacing** | `arcanum pace [ms]`, `arcanum tension [ms]` | Dialogue/action ratios, POV balance, interactive HTML tension curve |
| 8 | **Journeys & Calendars** | `arcanum calc journey`, `arcanum calendar` | 14 terrain types, 8 travel modes, multi-era custom date systems |
| 9 | **Faction Matrix** | `arcanum faction [world]`, `arcanum calc battle` | Alliance/rivalry chord diagrams and Lanchester battle formulas |
| 10 | **Economy & PPP** | `arcanum economy [world]` | Multi-currency commodity baskets and tech-anachronism linter |
| 11 | **Causal DAGs** | `arcanum causality [world]` | Multi-paradigm time-travel validator (Novikov, butterfly, multiverse) |
| 12 | **Climate & Ecology** | `arcanum calc climate`, `arcanum ecology` | Hadley/Ferrel cells, orographic rain shadows, trophic webs |
| 13 | **Sensory Palette** | `arcanum audit senses [ms]` | 6D balance scanner: Visual, Auditory, Olfactory, Gustatory, Tactile, Kinesthetic |
| 14 | **Prophecy Matrix** | `arcanum prophecy [world]` | Clause lifecycle tracker — audits fulfillment and contradictions |
| 15 | **Prose Stylistics** | `arcanum audit dialogue [ms]` | Said-bookism linter, word echo scanner, smart typography normalizer |
| 16 | **Voice Profiler** | `arcanum audit voice [ms]` | Lexical fingerprint per character — sentence complexity and Flesch-Kincaid grade |
| 17 | **Visual Story Canvas** | `arcanum canvas [ms]` | Drag-and-drop corkboard mapped onto 11+ story paradigms |
| 18 | **Timeline Sync** | `arcanum timeline [ms]` | Narrative vs. in-world astronomical timestamp alignment |
| 19 | **Multi-POV Threads** | `arcanum branch [ms]` | Character storyline subway map with convergence tracker |
| 20 | **Series Omnibus** | `arcanum omnibus [ms]` | Multi-volume compiler with merged Dramatis Personae |
| 21 | **Local Semantic RAG** | `arcanum rag <query>` | Hybrid TF-IDF + SQLite FTS5 lore search — no API needed |
| 22 | **Craft Wisdom Tips** | `arcanum tip [engine]` | Ambient craft hints across CLI footers, Studio Hub, and Zen Studio |

---

## 🖥️ Desktop Launchers & CLI Reference

All daily writing is accessible from GUI launchers. For power users, the `arcanum` CLI covers everything:

```bash
# Project creation
arcanum new manuscript MyNovel
arcanum new world EldariaWorld
arcanum new universe SolarisVerse

# Writing & sync
arcanum word [ms]                         # Open in Word/LibreOffice/Google Docs
arcanum docx sync [ms]                    # Sync DOCX ↔ Markdown (preserves all metadata)
arcanum studio [ms] -c 1-5                # Launch Zen Studio scoped to Chapters 1 through 5

# Auditing & craft
arcanum pace [ms] -c 1-5                  # Pacing & tension on specific chapter range
arcanum audit dialogue [ms] --scene 1-2   # Dialogue mechanics on specific scene numbers
arcanum audit voice [ms] -c ch01..ch04    # Character voice profiler on chapters 1-4
arcanum senses [ms] -b Book-01            # 6D sensory immersion on Book 1
arcanum magic check -w Eldoria            # Magic system consistency on specific world lore
arcanum continuity -w Eldoria -m MyNovel  # Multi-volume character & lore continuity audit
arcanum scope [target] -c 1-3 --scene 1   # Live scope resolution & diagnostic inspector

# Publishing
arcanum publish [ms] --format all        # PDF + EPUB + DOCX in one command
arcanum concordance <world> --manuscript <ms>  # Auto-generate back matter

# Safety & backups
arcanum save -m "Chapter 12 done"        # Git milestone snapshot
arcanum backup <project>                 # Verified .tar.gz + SHA-256 archive
arcanum backup-dest set /media/usb/      # Configure external USB backup target

# Health
arcanum check                            # System diagnostics
bash scripts/verify.sh                   # Full 7-stage verification harness
```

---

## 🛡️ Privacy & Security Guarantees

| Guarantee | Implementation |
|:--|:--|
| **Zero telemetry** | No network calls anywhere in the codebase — verified by `default-src 'none'` CSP on all generated HTML |
| **Atomic writes** | All file saves use `atomic_write()` — temp file → flush → fsync → `os.replace` — never a partial write |
| **Path traversal defence** | All user-supplied names validated against `^[A-Za-z0-9_-]+$` before any file operation |
| **Cross-platform locking** | `ArcanumLock` uses `fcntl.flock` (POSIX) or `msvcrt.locking` (Windows) to prevent data corruption |
| **Verified binary installs** | Typst v0.14.2 installed with SHA-256 digest check — refuses to install on mismatch |
| **Zero pip dependencies** | All craft engines run on Python standard library only |
| **Plain format sovereignty** | Prose stored as `.md` + `.docx` — readable on any computer, forever |

---

## 🔒 Data Safety: The 3-2-1 Rule

1. **Git version history** — automatic snapshots every 10 minutes via Obsidian Git; manual milestone via `arcanum save`
2. **Verified local archives** — `arcanum backup` creates `.tar.gz` with SHA-256 sidecar stored in `05-Backups/`
3. **External USB replication** — configure once with `arcanum backup-dest set /media/usb/`; every backup replicates automatically

---

## 🧰 Distraction Control

- **Firefox LeechBlock NG** — import `configs/leechblock_arcanum_rules.json` to block social media during writing hours (09:00–13:00, 14:00–17:00)
- **Procedural ambient audio** — `arcanum ambient rain` or `arcanum ambient hearth` for focus soundscapes
- **XFCE Do Not Disturb** — one-click notification muting via panel bell icon

---

## 📚 Documentation Index

| Document | What's Inside |
|:--|:--|
| [**📖 Setup Guide**](docs/SETUP_GUIDE.md) | Step-by-step layman-friendly installation with troubleshooting |
| [Author's Field Manual](docs/AUTHOR_MANUAL.md) | Complete plain-English handbook for daily writing workflow |
| [Architecture Deep-Dive](docs/ARCHITECTURE.md) | Technical blueprint, ADRs, invariants, and exit codes |
| [Cheat Sheet](docs/CHEATSHEET.md) | Single-page keyboard shortcuts and scene metadata tags |
| [Roadmap](docs/ROADMAP.md) | Project milestones M0–M28 and real-time status queues |
| [Changelog](CHANGELOG.md) | Release notes and feature history |
| [Software Catalog](docs/guides/SOFTWARE_CATALOG.md) | Exact package names, Flatpak IDs, and download commands |
| [Obsidian Plugins Guide](docs/guides/OBSIDIAN_PLUGINS.md) | Pre-configured plugin suite walkthrough |
| [Backup Setup Guide](docs/guides/BACKUP_SETUP.md) | 3-2-1 backup strategy with Déjà Dup |
| [Typography & Fonts](docs/guides/TYPOGRAPHY_AND_FONTS.md) | Literary typefaces and DOCX styling presets |
| [Support Matrix](docs/SUPPORT_MATRIX.md) | Supported distros, architectures, and display servers |
| [Contributing](CONTRIBUTING.md) | Quality gates, commit style, and submission flow |
| [Security Policy](SECURITY.md) | Installer privilege surface and vulnerability reporting |
| [Privacy Policy](PRIVACY.md) | Offline data minimization and zero telemetry guarantee |

---

## 🗺️ Project Docs (Contributors)

| Doc | What it is |
|:--|:--|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Technical architecture, invariants, exit codes, ADR-001–ADR-119 |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Project charter, milestones, hardware baseline |
| [CHANGELOG.md](CHANGELOG.md) | Notable changes by release |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Ground rules, quality gate, commit style |
| [SECURITY.md](SECURITY.md) | Security scope and private vulnerability reporting |
| [PRIVACY.md](PRIVACY.md) | Privacy policy and zero telemetry guarantee |
| [REFERENCES.md](REFERENCES.md) | Asset provenance and FOSS attribution |
| [scripts/verify.sh](scripts/verify.sh) | 7-stage automated health check |
