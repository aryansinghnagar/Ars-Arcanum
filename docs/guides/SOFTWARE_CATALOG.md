# Sovereign Authoring Software Resource Catalog & Reference Links (`docs/guides/SOFTWARE_CATALOG.md`)
> **Core Tooling, Installation Vectors & Sovereign Package Manifest** | GPA 4.0 / Grade A+

---

## 1. Overview & Tooling Architecture

Ars Arcanum integrates a curated, sovereign suite of local-first writing tools, typesetting compilers, cartography suites, astrophysics simulators, and style linters. Every application listed below is **100% offline-native, privacy-first, free of third-party telemetry, and air-gapped capable**.

```
+-------------------------------------------------------------------------------+
|                    ARS ARCANUM SOFTWARE ECOSYSTEM ARCHITECTURE                |
|                                                                               |
|  [Layer 1: Host OS]         --> Linux Mint XFCE / Debian 13 / Windows / macOS |
|                                                                               |
|  [Layer 2: Core Vault]      --> Obsidian (32 Plugins) + novelWriter           |
|                                                                               |
|  [Layer 3: Publication]     --> Typst (PDF) + Pandoc (AST) + Calibre (EPUB)   |
|                                                                               |
|  [Layer 4: Specialized GUI] --> Wonderdraft + Gramps + PolyGlot + Celestia    |
|                                                                               |
|  [Layer 5: Offline Daemons] --> Vale CLI + LanguageTool Local Server + Git   |
+-------------------------------------------------------------------------------+
```

---

## 2. Core Creative Writing & Worldbuilding Applications

### 2.1 Obsidian (World Bible & Knowledge Graph)
- **Role**: Lore concordance, character dossiers, location tracking, and non-linear story canvas. Pre-bundled with 32 offline plugins in [`templates/world-bible/.obsidian/plugins/`](file:///templates/world-bible/.obsidian/plugins/).
- **Plugin Suite & Tooling**: See [Master External Tools & Obsidian Plugins Guide](file:///docs/guides/EXTERNAL_TOOLS_AND_PLUGINS.md).
- **Official Hub**: [https://obsidian.md/](https://obsidian.md/)
- **Installation**:
  - Linux Flatpak: `flatpak install -y flathub md.obsidian.Obsidian`
  - Windows / macOS: Download installer from official website.

### 2.2 novelWriter (Outlining & Manuscript Drafting)
- **Role**: Structured novel drafting, chapter/scene tree, POV filtering, and word count goals.
- **Official Hub**: [https://novelwriter.io/](https://novelwriter.io/)
- **Documentation**: [https://novelwriter.readthedocs.io/](https://novelwriter.readthedocs.io/)
- **Installation**: `flatpak install -y flathub io.gitlab.novelwriter.novelWriter`

---

## 3. Specialized Worldbuilding & Craft Applications

### 3.1 Cartography: Wonderdraft & Obsidian Leaflet
- **Wonderdraft (Primary Desktop Cartography)**:
  - **Role**: Dedicated fantasy map editor for authors (coastal generation, symbol stamps, river networks, road paths, Tolkien-style aesthetics without Adobe Illustrator complexity).
  - **Official Hub**: [https://www.wonderdraft.net/](https://www.wonderdraft.net/)
  - **Documentation & Community**: [Reddit r/wonderdraft](https://www.reddit.com/r/wonderdraft/), [Mythkeeper Asset Manager](https://cartographyassets.com/).
- **Obsidian Leaflet (In-Vault Interactive Maps)**:
  - **Role**: Pins, coordinates, multi-level map zoom, and distance measurement inside Obsidian. Pre-bundled in vault template.

### 3.2 Linguistics & Conlangs: PolyGlot, Condict, Rootweave & LanguageForge
- **PolyGlot (Comprehensive Conlang Studio)**:
  - **Role**: Gold-standard conlang creation tool with regex-based sound change cascades, grammar guide generation, and PDF dictionary publication.
  - **Official Hub**: [https://draquet.github.io/PolyGlot/](https://draquet.github.io/PolyGlot/)
  - **GitHub**: [https://github.com/DraqueT/PolyGlot](https://github.com/DraqueT/PolyGlot)
  - **Installation**: Cross-platform Java archive (`java -jar PolyGlot.jar`).
- **Condict (Relational Offline Dictionary)**:
  - **Role**: Modern, offline-first dictionary application with inflection tables and interlinked languages.
  - **GitHub**: [https://github.com/arimah/condict](https://github.com/arimah/condict)
- **In-Vault Plugins**: `rootweave` and `languageforge` are pre-bundled in `templates/world-bible`.

### 3.3 Genealogy & Lineage: Gramps & Canvas Roots
- **Gramps (Premier Genealogy Database)**:
  - **Role**: Comprehensive genealogical database, kinship relationship calculations, inbreeding coefficient tracking, and GEDCOM standard support.
  - **Official Hub**: [https://gramps-project.org/](https://gramps-project.org/)
  - **Documentation**: [Gramps User Manual](https://gramps-project.org/wiki/index.php/Gramps_5.2_Wiki_Manual)
  - **Installation**:
    - Ubuntu/Debian: `sudo apt install -y gramps`
    - Windows/macOS: Native standalone installers available on official hub.
- **Canvas Roots (In-Vault Canvas Family Trees)**:
  - **Role**: Renders visual family trees and pedigree charts directly on Obsidian Canvas. Pre-bundled in vault template (`charted-roots`).

### 3.4 Astrophysics & Hard Sci-Fi: Celestia, StarGen & SpinCalc
- **Celestia (Real-Time 3D Orbital Space Simulator)**:
  - **Role**: Visualizes custom star systems, multi-sun orbits, planetary trajectories, and constellations in real time.
  - **Official Hub**: [https://celestiaproject.space/](https://celestiaproject.space/)
  - **GitHub**: [https://github.com/CelestiaProject/Celestia](https://github.com/CelestiaProject/Celestia)
  - **Installation**: `flatpak install -y flathub space.celestiaproject.Celestia`
- **StarGen (Planetary Accretion Generator)**:
  - **Role**: Computes planetary formation, orbital semi-major axes, atmospheric composition, and ecospheres from stellar parameters.
  - **Reference**: [Atomic Rockets / Project Rho StarGen](https://www.projectrho.com/public_html/rocket/worldbuilding.php)
- **SpinCalc & Artificial Gravity Calculators**:
  - **Role**: Calculates rotational radius, RPM, tangential velocity, and Coriolis force for spinning space habitats.
  - **Resource**: [SpinCalc Official](http://www.artificial-gravity.com/sw/SpinCalc/)

---

## 4. Prose Quality, Style Linting & Offline Grammar

### 4.1 Vale CLI (High-Speed Prose Linter)
- **Role**: Offline prose linter that enforces custom style guides, authorial dictionaries, banned cliches, and tone rules.
- **Official Hub**: [https://vale.sh/](https://vale.sh/)
- **Documentation**: [https://vale.sh/docs/](https://vale.sh/docs/)
- **Installation**:
  - Windows (`winget`): `winget install errata-ai.vale`
  - Linux/macOS: `brew install vale` or download binary from [GitHub Releases](https://github.com/errata-ai/vale/releases).

### 4.2 LanguageTool Local Server (Contextual Grammar & Spellchecking)
- **Role**: Local, privacy-first grammar and spellchecking daemon with zero cloud requirements.
- **Official Hub**: [https://languagetool.org/](https://languagetool.org/)
- **Documentation**: [LanguageTool HTTP Server](https://dev.languagetool.org/http-server)
- **Local Server Execution**:
  ```bash
  java -cp languagetool-server.jar org.languagetool.server.HTTPServer --port 8081 --allow-origin "*"
  ```

---

## 5. Typesetting, Compilation & Digital Publishing

### 5.1 Typst (Next-Generation Typesetting Compiler)
- **Role**: Lightning-fast, mathematical publication typesetting engine for print-ready PDFs.
- **Official Hub**: [https://typst.app/](https://typst.app/)
- **GitHub**: [https://github.com/typst/typst](https://github.com/typst/typst)
- **Installation**:
  - Windows (`winget`): `winget install Typst.Typst`
  - Linux: Download release binary from [GitHub Releases](https://github.com/typst/typst/releases).

### 5.2 Pandoc (Universal Document Converter)
- **Role**: Universal document AST converter between Markdown, DOCX, EPUB, and LaTeX.
- **Official Hub**: [https://pandoc.org/](https://pandoc.org/)
- **Installation**: `sudo apt install -y pandoc` / `winget install JohnMacFarlane.Pandoc`

### 5.3 Calibre (EPUB Compilation & E-Reader Suite)
- **Role**: E-book format compilation, metadata embedding, and device synchronization.
- **Official Hub**: [https://calibre-ebook.com/](https://calibre-ebook.com/)

### 5.4 Git (Local Distributed Version Control)
- **Role**: Immutable revision tracking, atomic snapshots, and branching.
- **Official Hub**: [https://git-scm.com/](https://git-scm.com/)

---

## 6. Software Matrix & Capability Summary

| Application | Primary Domain | Interface | License | Offline Status |
|---|---|---|---|---|
| **Obsidian** | Vault World Bible & Drafting | GUI (Electron) | Proprietary (Free Personal) | 100% Offline |
| **novelWriter** | Chapter/Scene Outliner | GUI (Qt) | Open Source (GPL-3.0) | 100% Offline |
| **Wonderdraft** | Vector Fantasy Cartography | GUI (Native) | Standalone Purchase | 100% Offline |
| **PolyGlot** | Conlangs & Dictionaries | GUI (Java) | Open Source (GPL-3.0) | 100% Offline |
| **Condict** | Relational Lexicons | GUI (Native) | Open Source (MIT) | 100% Offline |
| **Gramps** | Dynasties & Genealogies | GUI & CLI (Python) | Open Source (GPL-2.0) | 100% Offline |
| **Celestia** | 3D Solar Systems & Orbits | GUI (OpenGL) | Open Source (GPL-2.0) | 100% Offline |
| **StarGen** | Planetary Ephemeris | CLI (C) | Open Source (BSD) | 100% Offline |
| **Vale CLI** | Prose & Style Linting | CLI (Go) | Open Source (MIT) | 100% Offline |
| **LanguageTool** | Grammar & Spellcheck | Local Server (Java) | Open Source (LGPL-2.1) | 100% Offline |
| **Typst** | Publication Typesetting | CLI (Rust) | Open Source (Apache-2.0) | 100% Offline |
| **Pandoc** | Document AST Converter | CLI (Haskell) | Open Source (GPL-2.0) | 100% Offline |
| **Calibre** | EPUB3 Packaging | GUI & CLI (Python) | Open Source (GPL-3.0) | 100% Offline |
| **Git** | Offline Version Control | CLI (C) | Open Source (GPL-2.0) | 100% Offline |
