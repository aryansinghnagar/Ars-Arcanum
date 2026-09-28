# 📖 Ars Arcanum — Complete Setup Guide

> **A step-by-step installation walkthrough for everyone — no prior Linux or programming experience required.**

This guide will walk you from a fresh Linux installation to a fully working authoring studio. Every step is explained in plain language. If you get stuck, jump to the [Troubleshooting](#-troubleshooting) section.

---

## 📑 Table of Contents

1. [Before You Begin — System Requirements](#1-before-you-begin--system-requirements)
2. [Step 1 — Install Linux (Skip if Already Done)](#2-step-1--install-linux-skip-if-already-done)
3. [Step 2 — Get Ars Arcanum](#3-step-2--get-ars-arcanum)
4. [Step 3 — Run the One-Command Installer](#4-step-3--run-the-one-command-installer)
5. [Step 4 — First Launch & Welcome Wizard](#5-step-4--first-launch--welcome-wizard)
6. [Step 5 — Create Your First World & Novel](#6-step-5--create-your-first-world--novel)
7. [Step 6 — Start Writing](#7-step-6--start-writing)
8. [Step 7 — Protect Your Work (Backups)](#8-step-7--protect-your-work-backups)
9. [Step 8 — Publish Your Book](#9-step-8--publish-your-book)
10. [Optional Add-Ons](#10-optional-add-ons)
11. [Troubleshooting](#11-troubleshooting)

---

## 1. Before You Begin — System Requirements

### ✅ What You Need

| Item | Minimum | Recommended |
|:--|:--|:--|
| **Operating System** | Linux Mint 21, Debian 12, Ubuntu 22.04 | **Linux Mint 22 (Wilma) XFCE** ← easiest for beginners |
| **CPU** | Any 64-bit processor (Intel, AMD, or ARM64) | Intel Core i5 or AMD Ryzen 5 |
| **RAM** | 4 GB | 8–16 GB |
| **Storage** | 10 GB free disk space | 50 GB+ SSD |
| **Internet** | Needed once during setup | Not needed after setup |
| **USB Drive** | Optional | Recommended for backups |

> [!NOTE]
> **Windows or macOS?** Ars Arcanum requires Linux. If you are on Windows, you can install Linux Mint in a dual-boot configuration or in a virtual machine. See [Step 1](#2-step-1--install-linux-skip-if-already-done) below.

> [!TIP]
> **Not sure which Linux to use?** Download **Linux Mint 22 XFCE** — it is the primary reference platform, works exactly like Windows in look and feel, and is the easiest distribution for beginners.

---

## 2. Step 1 — Install Linux (Skip if Already Done)

> **Already running Linux Mint, Debian, or Ubuntu?** Skip to [Step 2](#3-step-2--get-ars-arcanum).

### Option A: Dual-Boot Linux Mint alongside Windows

A dual-boot lets you choose between Windows and Linux every time you start your computer. Your files on Windows remain untouched.

1. **Download Linux Mint 22 XFCE** from the official site:  
   👉 https://www.linuxmint.com/download.php  
   Download the **XFCE Edition** `.iso` file (~2.8 GB).

2. **Create a bootable USB drive** (minimum 4 GB):
   - On Windows: Download [Rufus](https://rufus.ie/en/) (free, portable).
   - Open Rufus, select your USB drive, select the `.iso` file you downloaded, click **Start**.
   - Wait for the process to complete (about 5 minutes).

3. **Boot from the USB**:
   - Restart your computer and press the boot key (usually `F2`, `F12`, `Del`, or `Esc` — it shows briefly on startup).
   - Select your USB drive from the boot menu.

4. **Install Linux Mint**:
   - Select "Install Linux Mint" and follow the wizard.
   - When asked about installation type, choose **"Install Linux Mint alongside Windows"**.
   - Choose how much disk space to give Linux (recommend at least 50 GB).
   - ✅ **Check "Encrypt the new Linux Mint installation"** — this protects your writing from unauthorized access.
   - Complete the wizard and restart.

### Option B: Virtual Machine (easiest, no risk to Windows)

If you want to try Ars Arcanum without modifying your computer:

1. Download [VirtualBox](https://www.virtualbox.org/wiki/Downloads) (free) and install it on Windows.
2. Download the Linux Mint 22 XFCE `.iso` from https://www.linuxmint.com/download.php.
3. In VirtualBox: click **New** → name it "Linux Mint" → Type: Linux → Version: Ubuntu 64-bit.
4. Allocate at least 4 GB RAM and 40 GB disk space.
5. Attach the `.iso` file as a virtual optical disk and start the VM.
6. Install Linux Mint inside the VM as normal.

---

## 3. Step 2 — Get Ars Arcanum

You need to download the Ars Arcanum code onto your Linux computer. There are two ways:

### Method A — Using the Terminal (Recommended)

1. Open a **Terminal** window. On Linux Mint XFCE, right-click the desktop and select **"Open Terminal Here"**, or look for **"Terminal Emulator"** in the application menu.

2. Copy and paste the following commands, pressing **Enter** after each line:

   ```bash
   cd ~/Downloads
   git clone https://github.com/aryansinghnagar/Scriptorium.git Ars-Arcanum
   cd Ars-Arcanum
   ```

   > **What this does:** `git clone` downloads all the Ars Arcanum files from GitHub into a folder called `Ars-Arcanum` inside your `Downloads` folder. `cd` navigates into that folder.

### Method B — Download as a ZIP file

1. Go to https://github.com/aryansinghnagar/Scriptorium in your browser.
2. Click the green **"Code"** button → **"Download ZIP"**.
3. Save the ZIP to your `Downloads` folder.
4. Right-click the ZIP file and choose **"Extract Here"**.
5. Open a Terminal and navigate into the extracted folder:
   ```bash
   cd ~/Downloads/Scriptorium-main
   ```

---

## 4. Step 3 — Run the One-Command Installer

With your Terminal open inside the Ars Arcanum folder, run:

```bash
bash scripts/setup_arcanum.sh
```

> [!IMPORTANT]
> You will be asked for your **password** (the one you set when you installed Linux). Type it and press Enter. The characters won't appear on screen — that is normal and expected.

### What the installer does automatically

The installer runs 6 stages. You'll see progress messages like `[1/6]`, `[2/6]`, etc.:

| Stage | What happens |
|:--|:--|
| **[1/6]** | Updates your Linux package list (like checking for updates) |
| **[2/6]** | Installs Git, Pandoc, LibreOffice, FocusWriter, and Python libraries |
| **[2b/6]** | Installs literary typography fonts (Linux Libertine, EB Garamond, Alegreya) |
| **[3/6]** | Configures Flathub (the app store for Linux applications) |
| **[4/6]** | Installs **Obsidian** (world bible), **novelWriter** (drafting), and **Calibre** (ebook) |
| **[5/6]** | Downloads and verifies **Typst v0.14.2** for print-quality PDF typesetting |
| **[6/6]** | Installs desktop launchers to your Desktop and application menu |

**How long it takes:** 5–20 minutes depending on your internet speed and Linux distribution.

### Installer options (advanced)

You don't need these for a normal install, but they're available:

| Flag | What it does |
|:--|:--|
| `--dry-run` | Preview everything the installer *would* do without making any changes |
| `--no-sudo` | Install without administrator privileges (skips system packages) |
| `--enable-timer` | Set up a daily automated backup timer using systemd |
| `-f` / `--force` | Bypass OS version checking (for unusual Linux distributions) |

### Installation complete!

When done, you'll see:
```
[SUCCESS] Ars Arcanum Writing Setup Installed Successfully!
```

If you see `[PARTIAL]` instead, some optional applications (like Calibre) may have failed to download — usually due to a slow or interrupted internet connection. The core system still works. Re-run `bash scripts/setup_arcanum.sh` when your connection is stable.

---

## 5. Step 4 — First Launch & Welcome Wizard

After installation, **look at your Desktop**. You'll see several new icons:

| Desktop Icon | What it Opens |
|:--|:--|
| **Ars Arcanum Control Center** | The main authoring dashboard — start here |
| **New World Vault Creator** | Wizard to create a world lore bible |
| **New Manuscript Creator** | Wizard to create a novel project |
| **Save Snapshot** | 1-click milestone backup |
| **Open Zen Studio** | Distraction-free drafting environment |

### Launch the Control Center

Double-click **"Ars Arcanum Control Center"**.

> [!TIP]
> If nothing happens when you double-click, right-click the icon and choose **"Trust and Launch"** or **"Allow Launching"** — this is a standard Linux security step for newly installed launchers.

### The Welcome Wizard

On first launch, the **Onboarding Wizard** appears with three choices:

```
┌─────────────────────────────────────────────┐
│         Welcome to Ars Arcanum!              │
├─────────────────────────────────────────────┤
│  [1] 🌟 Generate Demo Cosmos                │
│      "Chronicles of Eldoria" with sample    │
│      characters, magic, and chapters        │
│                                             │
│  [2] 🌍 Create New Universe & World         │
│      Start fresh with your own story idea   │
│                                             │
│  [3] 📂 Open Existing Project               │
│      Point to an existing folder            │
└─────────────────────────────────────────────┘
```

**For first-time users:** Choose **"Generate Demo Cosmos"**. This creates a complete example project called "The Chronicles of Eldoria" with pre-written characters, lore, a magic system, and sample manuscript chapters so you can explore everything immediately.

---

## 6. Step 5 — Create Your First World & Novel

### Create a World Lore Bible

Your **world bible** is where you store everything about your fictional universe — characters, maps, magic systems, languages, history, and more.

1. In the Control Center, click **"🪐 Cosmos & Worlds"** in the top navigation.
2. Click **"New World"**.
3. Enter a name (e.g. `MyFantasyWorld`). Use only letters, numbers, and hyphens — no spaces.
4. Click **Create**.

This creates `~/Universes/MyUniverse/MyFantasyWorld/` — a folder pre-configured as an **Obsidian vault** with 9 organized sub-folders and all plugins installed.

**To open your world bible:**  
Click **"Open in Obsidian"** in the Control Center, or double-click **Obsidian** in your applications.

> [!NOTE]
> **What is Obsidian?** It is a free app for writing and connecting notes. Think of it as a sophisticated notebook where every note can link to every other note. Your character profiles, location notes, and magic rules are all cross-linked.

### Create a Novel Manuscript

1. Click **"✍️ Manuscripts & Drafting"** in the Control Center.
2. Click **"New Manuscript"**.
3. Enter a name (e.g. `MyFirstNovel`) and optionally link it to your world.
4. Choose a story structure template (optional — you can choose "Blank" or "3-Act Structure", "Hero's Journey", etc.).
5. Click **Create**.

This creates `~/Manuscripts/MyFirstNovel/` with your first book folder, chapter structure, and novelWriter project ready to open.

---

## 7. Step 6 — Start Writing

Ars Arcanum gives you three ways to write — choose whichever suits your style:

### Option A — Write in Microsoft Word / LibreOffice (Recommended for Beginners)

1. In the Control Center, under **"✍️ Manuscripts & Drafting"**, click **"📝 Open in Word Processor"**.
2. Your manuscript opens in LibreOffice Writer (or Microsoft Word if you have it installed).
3. Write your chapters normally.
4. When done, click **"🔄 Sync DOCX ↔ Markdown"** to save your changes back to Markdown format automatically.

### Option B — Write in the Zen Drafting Studio

The **Zen Studio** is a minimalist, distraction-free writing environment that runs in your browser — no ads, no notifications, just your words.

```bash
arcanum studio MyFirstNovel
```

Or double-click **"Open Zen Studio"** from the Desktop. A browser tab opens with a typewriter-style interface. Your lore notes appear in a slide-out drawer on the right.

### Option C — Write in novelWriter

novelWriter is a dedicated fiction-writing app with a chapter/scene tree, status badges, and scene annotations.

1. In the Control Center, click **"Open in novelWriter"**.
2. Use the left panel to organize chapters and scenes.
3. Tag scenes with metadata: `@pov: Elena`, `@location: Capital City`, `@status: Draft`.

### Scene Metadata Tags

Whether you write in Word, novelWriter, or plain Markdown, Ars Arcanum reads these special tags at the top of each chapter file:

```
@pov: CharacterName          → Which character's point of view
@location: LocationName      → Where the scene takes place
@status: Draft               → Draft / Revision / Finished
@thread: MainPlot            → Which storyline thread this belongs to
@time: Year-1-Day-42         → In-world date
```

These tags power the visual scene inspector, pacing analyzer, timeline synchronizer, and Dramatis Personae auto-generator.

---

## 8. Step 7 — Protect Your Work (Backups)

**Your writing is irreplaceable. Don't skip this step.**

### Quick Git Snapshot (30 seconds)

After every writing session, click **"📷 Save Snapshot"** in the Control Center or press `Ctrl+S` in the GUI.

This creates an instant, timestamped backup point in Git (a version control system). You can roll back to any previous snapshot at any time.

### Verified Archive Backup

For a complete verified archive you can store on an external drive:

1. In the Control Center, go to **"🔒 Vault Safety & Backups"**.
2. Click **"🗄️ Create Backup Archive"**.

This creates a `.tar.gz` file with a SHA-256 checksum sidecar in `~/Manuscripts/<Name>/Backups/`. The checksum proves the backup hasn't been corrupted.

### Set Up External USB Backup

For full 3-2-1 protection (local + external + offsite):

1. Plug in a USB drive.
2. In the Control Center → Safety & Backups, click **"Configure External Backup"**.
3. Select your USB drive path (e.g. `/media/yourname/USBDrive`).

From now on, every backup automatically replicates to both your internal drive and the USB drive simultaneously.

> [!TIP]
> **What is the 3-2-1 Rule?** Keep **3** copies of your work, on **2** different media types, with **1** copy offsite (USB drive stored away from your computer). This protects against hardware failure, theft, and accidental deletion.

### Optional: Daily Automated Backups (Déjà Dup)

For hands-off automated daily backups, install Déjà Dup:

```bash
sudo apt install deja-dup
```

Open **Déjà Dup** from your application menu, set the backup folder to your USB drive, and enable the **"Automatic Backups"** toggle. See [Backup Setup Guide](guides/BACKUP_SETUP.md) for details.

---

## 9. Step 8 — Publish Your Book

When your manuscript is ready:

1. In the Control Center, click **"📚 Publishing & Typesetting"**.
2. Select your manuscript and choose output format:
   - **Print PDF** — Publication-quality PDF with trade margins, running headers, and front matter (half-title, copyright, dedication). Compiled in under 1 second using Typst.
   - **EPUB** — Validated EPUB for e-readers (Kindle, Kobo, etc.) compiled with Pandoc.
   - **Submission DOCX** — Industry-standard Shunn/Modern format for literary agents.
3. Click **"1-Click Publish"** (or **"Export All"** for all three at once).

Your files appear in `~/Manuscripts/<Name>/Exports/`.

### Pre-Flight Check (Before Sending to a Publisher)

Before exporting a final manuscript:

1. Click **"Pre-Flight Linter"** in the Publishing studio.
2. This scans for missing front matter, unresolved scene tags, dialogue formatting issues, and typesetting problems.
3. Fix any flagged issues, then export.

### Auto-Generate Back Matter

Ars Arcanum can automatically build a *Dramatis Personae* (character list) and *Glossary* from your world bible and manuscript tags:

```bash
arcanum concordance MyWorld --manuscript MyFirstNovel
```

The generated back matter is automatically appended to your next export.

---

## 10. Optional Add-Ons

These are useful but not required for daily writing:

### Distraction Blocking (Firefox)

Block social media during writing hours:

1. Install [LeechBlock NG](https://addons.mozilla.org/firefox/addon/leechblock-ng/) from the Firefox Add-ons Store.
2. In LeechBlock Options → click **Import** → select `configs/leechblock_arcanum_rules.json`.

This blocks YouTube, Reddit, Twitter/X, and TikTok automatically from 09:00–13:00 and 14:00–17:00 on writing days.

### Do Not Disturb (Linux Mint XFCE)

Click the **Notification Bell** icon in your taskbar and toggle **"Do Not Disturb"** to silence all desktop notifications during deep writing sprints.

### Procedural Ambient Soundscapes

```bash
arcanum ambient rain       # Procedural rain soundscape
arcanum ambient hearth     # Crackling fireplace
arcanum ambient --html     # Opens browser-based audio player
```

### Optional Creative Tools

These are not installed automatically but work seamlessly with Ars Arcanum:

| Tool | What it Does | Install |
|:--|:--|:--|
| **Azgaar's Fantasy Map Generator** | Browser-based procedural world map creator | Visit https://azgaar.github.io/Fantasy-Map-Generator/ (offline-capable) |
| **Krita** | Professional painting software for character and location art | `sudo apt install krita` |
| **Inkscape** | Vector graphics for maps and diagrams | `sudo apt install inkscape` |
| **Gramps** | Genealogy management for complex family trees | `sudo apt install gramps` |
| **PolyGlot** | Constructed language dictionary builder | See [Optional Extras Guide](guides/OPTIONAL_EXTRAS.md) |
| **Sigil** | EPUB editor for fine-tuned ebook control | `sudo apt install sigil` |

### Enable the Automatic Daily Backup Timer

```bash
bash scripts/setup_arcanum.sh --enable-timer
```

This installs a systemd user service that creates an automatic daily backup of all your projects.

---

## 11. Troubleshooting

### "Permission denied" when running the installer

```bash
bash scripts/setup_arcanum.sh
```
Make sure you are typing `bash scripts/...` — not double-clicking the file. Also ensure you are inside the Ars-Arcanum folder in your terminal (`cd ~/Downloads/Ars-Arcanum`).

### The installer says "Unsupported distribution"

If you are on Ubuntu 22.04, Fedora, Arch Linux, or another distribution, add the `--force` flag:

```bash
bash scripts/setup_arcanum.sh --force
```

### Obsidian / novelWriter / Calibre didn't install

These are installed via Flatpak and require a working internet connection. Re-run the installer:

```bash
bash scripts/setup_arcanum.sh
```

If the problem persists, install them manually:

```bash
flatpak install flathub md.obsidian.Obsidian
flatpak install flathub io.gitlab.novelwriter.novelWriter
flatpak install flathub com.calibre_ebook.calibre
```

### Desktop launchers won't open (Linux Mint XFCE)

Right-click the launcher and choose **"Trust and Launch"** or **"Allow Launching"**. This only needs to be done once per icon.

### "arcanum: command not found" in the terminal

The CLI is linked to `~/.local/bin/arcanum`. If your terminal doesn't find it, add it to your PATH:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

Then try `arcanum --version` again.

### Typst PDF export fails

Check if Typst is installed:

```bash
typst --version
```

If not found, reinstall:

```bash
bash scripts/setup_arcanum.sh
```

If your architecture is not x86_64 or aarch64, install via Cargo:

```bash
cargo install --locked typst-cli
```

### Something seems broken — run the full health check

```bash
bash scripts/verify.sh
```

This runs all 7 verification stages and prints exactly what passed, what was skipped, and what failed. Share the output if you need help.

### Still stuck?

1. Check [AUTHOR_MANUAL.md](AUTHOR_MANUAL.md) — Section 8 has a detailed FAQ.
2. Open a GitHub Issue at https://github.com/aryansinghnagar/Scriptorium/issues with the output of `bash scripts/verify.sh`.

---

## Quick Reference Card

```
┌────────────────────────────────────────────────────────────┐
│                    Daily Writing Loop                       │
├────────────────────────────────────────────────────────────┤
│  1. Open Control Center (double-click desktop icon)        │
│  2. Click "Open in Word Processor" and write               │
│  3. Click "Sync DOCX ↔ Markdown" when done                 │
│  4. Click "Save Snapshot" (Ctrl+S in the app)              │
│  5. Done! Your work is safe.                               │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│                   Where Your Files Live                     │
├────────────────────────────────────────────────────────────┤
│  ~/Universes/<Name>/<World>/    → World lore & Obsidian    │
│  ~/Manuscripts/<Name>/          → Chapters & drafts        │
│  ~/Manuscripts/<Name>/Exports/  → PDFs, EPUBs, DOCXs      │
│  ~/Manuscripts/<Name>/Backups/  → Verified archive copies  │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│               Essential Terminal Commands                   │
├────────────────────────────────────────────────────────────┤
│  arcanum check              → System health check          │
│  arcanum save -m "note"     → Git milestone snapshot       │
│  arcanum backup <project>   → Verified archive backup      │
│  arcanum publish [ms]       → Export PDF + EPUB + DOCX     │
│  arcanum studio [ms]        → Zen Drafting Studio          │
│  bash scripts/verify.sh     → Full 7-stage health check    │
└────────────────────────────────────────────────────────────┘
```

---

*Setup Guide for Ars Arcanum v4.2.1 · Branch: `main` · Commit: `3d84fa0` · Updated: 2026-09-28*
