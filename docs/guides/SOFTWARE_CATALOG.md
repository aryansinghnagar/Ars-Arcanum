# Sovereign Authoring Software Resource Catalog & Reference Links (`docs/guides/SOFTWARE_CATALOG.md`)
> **Core Tooling, Installation Vectors & Sovereign Package Manifest**

---

## 1. Overview & Tooling Architecture

Ars Arcanum integrates a curated, sovereign suite of local-first writing tools, typesetting compilers, cartography engines, and version control utilities. Every application listed below is **100% free, open-source (or offline-native), free of third-party telemetry, and air-gapped capable**.

```
+-------------------------------------------------------------------------------+
|                    ARS ARCANUM SOFTWARE ECOSYSTEM ARCHITECTURE                |
|                                                                               |
|  [Layer 1: OS / Kernel]     --> Linux Mint XFCE / Debian 13 / Windows / macOS |
|                                                                               |
|  [Layer 2: Core Drafting]   --> Obsidian (World Bible) + novelWriter + Zen    |
|                                                                               |
|  [Layer 3: Publication]     --> Typst (PDF Engine) + Calibre (EPUB) + LibreOff|
|                                                                               |
|  [Layer 4: Specialized]     --> Krita + Inkscape + Gramps + PolyGlot + Kiwix  |
+-------------------------------------------------------------------------------+
```

---

## 2. Core Operating System & Live USB Tools

### 2.1 Linux Mint XFCE Edition (Primary Recommended Host)
- **Role**: Lightweight, ultra-stable authorial operating system with native full-disk LUKS encryption, out-of-the-box Flatpak support, and sub-1GB RAM idle usage.
- **Official Portal**: [https://linuxmint.com/download.php](https://linuxmint.com/download.php)
- **Direct ISO (XFCE 64-bit)**: [https://www.linuxmint.com/edition.php?id=318](https://www.linuxmint.com/edition.php?id=318)
- **SHA-256 Checksum**: Available on the official release hub for cryptographic verification.

### 2.2 USB Imaging & Flasher Utilities
- **balenaEtcher**: [https://etcher.balena.io/](https://etcher.balena.io/) (Windows, macOS, Linux AppImage).
- **Ventoy (Multi-Boot USB Utility)**: [https://www.ventoy.net/](https://www.ventoy.net/) (Drag-and-drop ISO boot utility).
- **Rufus (Windows Portable Flasher)**: [https://rufus.ie/](https://rufus.ie/).

---

## 3. Core Creative Writing & Worldbuilding Applications

### 3.1 Obsidian (World Bible & Knowledge Graph)
- **Role**: Lore concordance, character dossiers, location tracking, non-linear story canvas.
- **Official Hub**: [https://obsidian.md/](https://obsidian.md/)
- **Flatpak Installation**:
  ```bash
  flatpak install -y flathub md.obsidian.Obsidian
  ```

### 3.2 novelWriter (Outlining & Manuscript Drafting)
- **Role**: Structured novel drafting, chapter/scene tree, POV filtering, and word count goals.
- **Official Hub**: [https://novelwriter.io/](https://novelwriter.io/)
- **Documentation**: [https://novelwriter.readthedocs.io/](https://novelwriter.readthedocs.io/)
- **Flatpak Installation**:
  ```bash
  flatpak install -y flathub io.gitlab.novelwriter.novelWriter
  ```

### 3.3 FocusWriter (Distraction-Free Minimalist Page)
- **Role**: Fullscreen distraction-free sprint page with ambient typing acoustics.
- **Official Hub**: [https://gottcode.org/focuswriter/](https://gottcode.org/focuswriter/)
- **Installation**:
  ```bash
  sudo apt install -y focuswriter
  # Or: flatpak install -y flathub org.gottcode.FocusWriter
  ```

### 3.4 LibreOffice Writer & Desktop Word Processors (DOCX Bridge)
- **Role**: Reviewing editor comments and tracked changes in `.docx` formats with bidirectional Markdown sync.
- **Official Hub**: [https://www.libreoffice.org/](https://www.libreoffice.org/)
- **Installation**:
  ```bash
  sudo apt install -y libreoffice-writer libreoffice-gtk3
  ```

---

## 4. Typesetting, Compilation & Digital Publishing

### 4.1 Typst (Next-Generation Typesetting Compiler)
- **Role**: Lightning-fast, mathematical publication typesetting engine for print-ready PDFs.
- **Official Hub**: [https://typst.app/](https://typst.app/)
- **GitHub**: [https://github.com/typst/typst](https://github.com/typst/typst)
- **Binary Installation**:
  ```bash
  curl -L -o /tmp/typst.tar.xz "https://github.com/typst/typst/releases/latest/download/typst-x86_64-unknown-linux-musl.tar.xz"
  tar -xf /tmp/typst.tar.xz -C /tmp/
  sudo install -m 755 /tmp/typst-*/typst /usr/local/bin/
  ```

### 4.2 Calibre (EPUB Compilation & E-Reader Suite)
- **Role**: E-book format compilation, metadata embedding, and device synchronization.
- **Official Hub**: [https://calibre-ebook.com/](https://calibre-ebook.com/)
- **Installation**:
  ```bash
  sudo -v && wget -nv -O- https://download.calibre-ebook.com/linux-installer.sh | sudo sh /dev/stdin
  ```

### 4.3 Pandoc (Universal Document Converter)
- **Role**: Universal document AST converter between Markdown, DOCX, EPUB, and LaTeX.
- **Official Hub**: [https://pandoc.org/](https://pandoc.org/)
- **Installation**:
  ```bash
  sudo apt install -y pandoc
  ```

---

## 5. Visual Art, Cartography & Specialized Utilities

| Tool Name | Domain | Primary Purpose | Installation Vector |
|---|---|---|---|
| **Krita** | Visual Concept Art | Hand-painted digital world maps and cover art | `flatpak install -y flathub org.kde.krita` |
| **Inkscape** | Vector Heraldry | Scalable vector faction coats of arms and symbols | `sudo apt install -y inkscape` |
| **Gramps** | Dynasties | Standalone complex family lineage databases | `sudo apt install -y gramps` |
| **PolyGlot** | Conlangs | Conlang phonology and vocabulary management | `java -jar PolyGlot.jar` |
| **Kiwix** | Offline Research | Air-gapped Wikipedia & Wiktionary ZIM dumps | `flatpak install -y flathub org.kiwix.desktop` |
| **Sigil** | EPUB Polish | Deep inspection of EPUB XHTML and CSS tables | `sudo apt install -y sigil` |

---

## 6. Recommended Reading, References & Media

### 6.1 Open-Source Software & Digital Longevity Treatises
- **Stallman, Richard M. (2002)**. *Free Software, Free Society: Selected Essays of Richard M. Stallman*. GNU Press. ISBN: 978-1882114986.  
  *The foundational philosophy of software freedom, open data formats, and digital autonomy.*
- **Raymond, Eric S. (1999)**. *The Cathedral and the Bazaar: Musings on Linux and Open Source by an Accidental Revolutionary*. O'Reilly Media. ISBN: 978-1565927247.  
  *Principles of decentralized, open-source software architectures.*
- **Doctorow, Cory (2014)**. *Information Doesn't Want to Be Free: Laws of the Internet Age*. McSweeney's.  
  *Why proprietary lock-in harms creative authors and how open standards preserve literature.*

### 6.2 Video Lectures & Masterclasses
- **Brandon Sanderson's BYU Creative Writing Lectures**: *Software Tools for Authors: Building a Robust Writing Setup*.  
  *Practical analysis of writing software, backup strategies, and formatting tools.*
- **Linux Mint Community**: *Linux Mint XFCE: The Minimalist Writer's Operating System*.  
  *Setting up a distraction-free, air-gapped Linux workstation for long-form novel drafting.*
