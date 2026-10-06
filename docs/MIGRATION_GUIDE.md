# Ars Arcanum Migration Guide

> **The Definitive Guide to Migrating Manuscripts, Lore Bibles, and Worldbuilding Data into Ars Arcanum**  
> *100% Offline, Open Standards, Zero Vendor Lock-in* | **Release Version:** `v0.1.0`

This guide provides step-by-step instructions for importing your existing manuscripts, lore vaults, and worldbuilding notes from proprietary writing suites (Scrivener, World Anvil, Campfire, Dabble, Microsoft Word, Google Docs) into Ars Arcanum's sovereign, plain Markdown architecture.

---

## 1. Migrating from Scrivener

Scrivener stores projects in proprietary `.scriv` XML/RTF bundles. To import your Scrivener manuscript into Ars Arcanum:

### Step 1: Export from Scrivener
1. In Scrivener, navigate to **File $\to$ Export $\to$ Files...**
2. Choose **Format: Markdown (`.md`)** or **Word Document (`.docx`)**.
3. Under *Export Options*, check **Export each document to its own file**.
4. Save the exported folder (e.g. `~/Downloads/MyNovel_Scrivener_Export/`).

### Step 2: Batch Import into Ars Arcanum
Run the batch import command:
```bash
arcanum import-docx-batch ~/Downloads/MyNovel_Scrivener_Export/ \
  --title "My Novel Title" \
  --author "Your Name" \
  --universe "My-Universe" \
  --world "My-World"
```
Ars Arcanum will automatically:
- Create `~/Manuscripts/My-Novel-Title/`
- Number and convert each chapter file into `Book-01/Draft-01/01_Chapter_01.md`, etc.
- Generate `manuscript.yaml` and `nwProject.nwx` (novelWriter project file)
- Configure sovereign `.gitignore` rules

---

## 2. Migrating from Microsoft Word / Google Docs (`.docx`)

### Single or Multi-File Word Imports
If you have your chapters saved as `.docx` files in a folder:
```bash
arcanum import-docx-batch ~/Documents/Drafts/ \
  --title "The Starlight Saga" \
  --author "Jane Doe"
```
The importer preserves headings (`# Heading 1`, `## Heading 2`), dialogue italics, and paragraph breaks without requiring Microsoft Word or external converters.

---

## 3. Migrating from Obsidian / Existing Lore Vaults

Ars Arcanum world bibles are 100% standard Obsidian vaults:
1. Place your world vault inside your universe directory:
   ```bash
   mkdir -p ~/Universes/My-Universe/My-World
   cp -r ~/ObsidianVaults/MyWorld/* ~/Universes/My-Universe/My-World/
   ```
2. Run the vault migration command:
   ```bash
   arcanum migrate ~/Universes/My-Universe/My-World
   ```
3. Run `arcanum world-doctor My-World` to verify all wikilinks, timeline dates, and entity tags.

---

## 4. Migrating from World Anvil / Campfire / Dabble

### Step 1: Export from Web Platforms
- **World Anvil**: Export your world as a zip of Markdown / JSON files via *Settings $\to$ Export World*.
- **Campfire Write**: Export your project as `.docx` chapters and Character sheets.
- **Dabble**: Export project to `.docx`.

### Step 2: Ingest into World Lore Vault
Copy your Markdown notes or `.docx` exports into `~/Universes/<Universe>/<World>/Characters/`, `Places/`, `Factions/`, etc., and run:
```bash
arcanum frontmatter normalize ~/Universes/My-Universe/My-World
arcanum world-doctor My-World
```

---

## 5. Live Bidirectional Synchronization with Microsoft Word (`.docx`)

Once your manuscript is in Ars Arcanum, you can bidirectionally sync edits made in Microsoft Word or LibreOffice Writer:
```bash
# Export Markdown draft to styled DOCX for an editor
arcanum docx build "My-Manuscript"

# Re-import edited DOCX from your editor back into Markdown
arcanum docx sync "My-Manuscript"
```
Edits are merged with three-way hash tracking and conflict isolation (`.conflict.md`).

---

## 6. Recommended Reading & Migration References

1. **CommonMark Specification** (2021). *Standardizing Markdown syntax across platforms*.
2. **ISO/IEC 29500-1** (2016). *Information technology — Document description and processing languages — Office Open XML File Formats*.
3. **Bringhurst, Robert** (2012). *The Elements of Typographic Style*. Hartley & Marks.
