# Ars Arcanum / Scriptorium — Author's Quick Reference Cheatsheet
> **100% Offline, Sovereign Writing & Speculative Worldbuilding Studio** | Version 5.0.0

---

## ⌨️ Desktop Keyboard Accelerators

| Shortcut | Action | Scope / Studio |
| :--- | :--- | :--- |
| `Ctrl + N` | **+ New Project Wizard** (Manuscript / World / Universe) | Global Scaffolding |
| `Ctrl + S` | **Quick Version Snapshot** (Git commit with milestone prompt) | Global Versioning |
| `Ctrl + E` | **Compile & Export Book** (Print PDF / EPUB / DOCX) | Studio 4: Publishing |
| `Ctrl + B` | **Create Standalone Backup Archive** (`.tar.gz` / `.tar.gz.gpg`) | Studio 5: Safety |
| `Ctrl + H` | **Toggle High-Contrast Mode** (WCAG 2.1 AA compliant palette) | Accessibility |
| `Ctrl + R` | **Refresh Project Discovery** (Reload universes & manuscripts) | Top Selector Bar |
| `F1` | **Open Author's Field Manual** | Offline Reference |

---

## ✍️ Markdown Scene Metadata Headers

Place these optional tags in your chapter scenes (or edit via the GUI Scene Inspector). All tags are automatically scrubbed during export to print/ebook formats:

```markdown
@pov: Kaelen Vance
@char: Vance, Lysandra, Archon Scribe
@location: SunCitadel Archives
@plot: Main-Heist
@thread: Arcane-Romance
@arc: Vance-Redemption
@time: 1422 3E, Night
@status: Draft
@magic: Aether-Weaving
@reagent: Lumic Crystal, Silver Dust

# Chapter 1: Into the Vault

Prose begins here...
```

---

## 🎯 Granular Target Scoping & Altitude Control

Filter craft engines to exact scenes, chapters, books, or lore categories without running against entire vaults:

| Flag / Shorthand | Example Syntax | Target Resolved |
| :--- | :--- | :--- |
| `-c`, `--chapter`, `--ch` | `-c 1-5`, `-c 1,3,7-10`, `-c ch01..ch05` | Specific chapter numbers or ranges |
| `--scene`, `--scenes`, `--sc` | `--scene 1-3`, `--sc sc01..sc02` | Specific scene numbers or ranges |
| `-b`, `--book`, `--volume` | `-b Book-01`, `-b 1-2` | Specific volume or book directory |
| `-w`, `--world` | `-w Eldoria`, `-w Eldoria-Prime` | Specific world lore vault |
| `--lore-category` | `--lore-category Characters,Magic` | Specific lore subdirectories |
| `--scope` | `--scope "world:Eldoria:lore:Characters"` | Unified scoping expression string |
| `--all` | `--all` | Explicitly bypass intelligent defaults and scan full vault |
| `arcanum scope` | `arcanum scope [MS] -c 1-5 --json` | Diagnostic preview of resolved files & scene slices |

---

## 🚀 Essential CLI Commands

```bash
# Core Authoring & Project Management
arcanum write [TARGET]               # Open writing workspace in novelWriter / Obsidian (alias: open)
arcanum zen [MS] [-w WORLD]          # Standalone offline Zen drafting studio & in-situ lore drawer
arcanum canvas [MS]                  # Interactive visual story canvas & drag-and-drop corkboard
arcanum hub [TARGET] [--port PORT]   # Sovereign Studio Desktop Hub — unified offline telemetry cockpit
arcanum portfolio [ROOT] [--html]    # Author portfolio dashboard, catalog velocity & progress rollups
arcanum typography [TARGET] [-i]     # Smart typography normalizer (curly quotes, em/en-dashes, ellipses)
arcanum corpus <export|restore> [TARGET] # Universal structured corpus (JSONL/SQLite) and vault restore
arcanum word [MS]                    # Open manuscript in Microsoft Word / LibreOffice (alias: writer)
arcanum docx sync [MS]               # Bidirectional synchronization between Word (.docx) & Markdown
arcanum new <manuscript|world|universe|volume> <NAME>  # Scaffold new project components
arcanum draft <MS> [DRAFT_NAME]      # Fork discrete revision draft (e.g. Draft-02)
arcanum compare <MS> [NEW] [OLD]     # Visual Redline changelog comparison in browser
arcanum save [TARGET] -m "Note"      # Save Git version milestone snapshot (alias: snapshot)
arcanum words [MS] [--pov|--json]    # Live word count report and POV balance breakdown

# Sovereign Local Retrieval & Deterministic Craft Engines
arcanum search <QUERY> [-d DB]       # Zero-dependency local TF-IDF & SQLite FTS5 semantic lore retrieval
arcanum ambient [PROFILE]            # Sine-wave binaural beat focus soundscape generator (alpha, theta)
arcanum sprint <start|stop|status|stats|report> # Writing sprint timer, WPM velocity analytics & dashboard
arcanum revision-heatmap [MS] [--html] # Snapshot revision churn heatmap & over-revised chapter detector
arcanum causality [MS] [-w WORLD]     # Causal DAG builder, Novikov self-consistency & loop detector
arcanum prophecy [MS] [-w WORLD]      # Prophecy resolution matrix & clause cross-validation
arcanum cast [UNIVERSE] [--html|--md] # Multi-volume Dramatis Personae & Universe Cast Matrix
arcanum codex [WORLD] [-o OUT.html]   # Single-file standalone offline World Wiki & Codex exporter
arcanum magic-check [WORLD] [-m MS]   # Thermodynamic hard magic tier, catalyst & fatigue constraint validator
arcanum faction <check|battle|logistics> # Geopolitical relations, Lanchester combat & campaign logistics
arcanum economy <check|ppp|trade>     # Macroeconomic commodity PPP, trade freight margins & anachronisms
arcanum journey --dist <D> --mode <M> # Overland/naval expedition modeler, terrain friction & Naismith's rule
arcanum map [WORLD] [--svg|--html]    # Offline vector SVG cartography & interactive HTML map viewer
arcanum structure [MS] -p <PARADIGM>  # 11-Paradigm story structure & beat window enforcer (3-Act, STC, Kisho...)
arcanum tactical [--terrain T]        # Lanchester law combat simulator & battle planning guide
arcanum plot-matrix [MS] [--html]     # Multi-track narrative plot grid, subplot matrix & Chekhov gun lifecycles
arcanum climate [--star-lum L] [--html]# Planetary climate, orographic rain shadows & Köppen biomes
arcanum ecology [WORLD] [--html|--note]# Trophic food web auditor, Lindeman 10% efficiency & cycle detection
arcanum astro <system|orbit|habitable> # Keplerian orbital physics, stellar classification, Roche limits

# Speculative Worldbuilding & Consistency Checks
arcanum world-doctor [WORLD]         # Deep lore vault validation, broken links, trait anomalies
arcanum continuity -w [W] -m [MS]    # Multi-book character trait & narrative continuity check
arcanum timeline [MS|WORLD]          # Dual-track chronological vs narrative timeline synchronizer
arcanum omnibus <UNIVERSE>           # Compile multi-volume series omnibus with unified lore
arcanum resonance [WORLD]            # 47-node knowledge graph mesh & causal cascade simulation
arcanum tip                          # Contextual craft wisdom & non-repeating writing advice
arcanum genealogy -w [W] [-f mermaid]# Dynastic family trees, succession DAGs & consanguinity scanner
arcanum conlang generate -w [W] -l [L]# Conlang phonotactics word/name generator & sound shift laws
arcanum calendar [WORLD] [--phases]  # Planetary calendar arithmetic, seasons & moon syzygies

# Publishing, Distribution & Backups
arcanum publish [MS] [--format all]  # Compile print PDF (Typst), EPUB (Pandoc), submission DOCX
arcanum preflight [MS]               # Typesetting pre-flight validator (PUB-101)
arcanum backup [TARGET] [--symmetric]# Standalone archive backup (supports GPG AES-256 encryption)
arcanum restore [ARCHIVE]            # Disaster recovery restoration with SHA-256 verification
arcanum doctor                       # System diagnostic & toolchain health check
```

---

## 🔒 3-2-1 Data Safety & GPG Encryption

```bash
# Standard backup with dual-target secondary replication
arcanum backup My-World

# Encrypted backup with GPG symmetric AES-256 passphrase
arcanum backup My-World --symmetric

# Safe verified restore
arcanum restore /path/to/My-World_2026-10-06.tar.gz.gpg
```

---

## 📚 Recommended Reading & Media

1. **McKee, Robert** (1997). *Story: Substance, Structure, Style and the Principles of Screenwriting*.
2. **Swain, Dwight V.** (1965). *Techniques of the Selling Writer*.
3. **Provost, Gary** (1985). *100 Ways to Improve Your Writing*.
4. **Sanderson, Brandon** (2020). *Creative Writing Lectures at BYU* (YouTube).
5. **Artifexian & Biblaridion** (YouTube Worldbuilding Channels).
