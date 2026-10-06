# 📖 Ars Arcanum — Complete Setup Guide

> **A step-by-step installation walkthrough for everyone — Linux, Windows, and macOS.**

This guide will walk you from a fresh installation to a fully working authoring studio. Every step is explained in plain language. If you get stuck, jump to the [Troubleshooting](#11-troubleshooting) section.

---

## 📑 Table of Contents

1. [Before You Begin — System Requirements](#1-before-you-begin--system-requirements)
2. [Step 1 — Install Python & Tools](#2-step-1--install-python--tools)
3. [Step 2 — Get Ars Arcanum](#3-step-2--get-ars-arcanum)
4. [Step 3 — Run the Setup / Install](#4-step-3--run-the-setup--install)
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
| **Operating System** | Linux Mint 21/22, Debian 12/13, Ubuntu 22.04/24.04, Windows 10/11, macOS 13+ | **Linux Mint 22 (Wilma) XFCE** or standard Python 3.10+ workstation |
| **Python Runtime** | Python 3.10 or higher | Python 3.11, 3.12, 3.13, or 3.14 |
| **CPU** | Any 64-bit processor (Intel, AMD, or ARM64) | Intel Core i5, AMD Ryzen 5, or Apple Silicon M-series |
| **RAM** | 4 GB | 8–16 GB |
| **Storage** | 10 GB free disk space | 50 GB+ SSD |
| **Internet** | Needed once during setup | Not needed after setup |

> [!TIP]
> **Cross-Platform Support**: All 47 core simulation engines, the CLI dispatcher, the browser-based Studio Hub, Zen Studio, and Story Canvas are 100% cross-platform standard library Python applications running seamlessly on Linux, Windows, and macOS.

---

## 2. Step 1 — Install Python & Tools

- **Linux (Mint/Debian/Ubuntu)**:
  ```bash
  sudo apt update && sudo apt install -y python3 python3-pip git
  ```
- **Windows**:
  Download and install Python 3.10+ from [python.org](https://www.python.org/downloads/). Ensure **"Add Python to PATH"** is checked during installation.
- **macOS**:
  Install Python via Homebrew (`brew install python git`) or official installer.

---

## 3. Step 2 — Get Ars Arcanum

Clone the repository to your computer:

```bash
git clone https://github.com/aryansinghnagar/Ars-Arcanum.git
cd Ars-Arcanum
```

---

## 4. Step 3 — Run the Setup / Install

### Option A: Standard Python Package Installation (All Platforms)

```bash
# Install package and register CLI entry points
pip install -e .

# Verify CLI runs
arcanum --version
```

### Option B: Native Linux Desktop Setup (Linux Mint / Debian / Ubuntu)

To install native desktop launchers, icon themes, Typst, and desktop menus:

```bash
# Inspect what the installer will do
bash scripts/setup_arcanum.sh --dry-run

# Run the installer
bash scripts/setup_arcanum.sh
```

---

## 5. Step 4 — First Launch & Welcome Wizard

### Launching the Studio

- **Desktop GUI (Linux)**: Run `python scripts/arcanum_app.py` or click the application menu icon.
- **Studio Hub (Web Browser, All Platforms)**: Run `arcanum hub` to open the interactive telemetry cockpit in your browser.
- **Zen Studio (All Platforms)**: Run `arcanum zen` for distraction-free typewriter drafting.
- **CLI Dispatcher (All Platforms)**: Run `arcanum --help` or `arcanum <subcommand>`.

---

## 6. Step 5 — Create Your First World & Novel

```bash
# Initialize a new Universe and World Bible
arcanum universe create "Solaris-Verse"
arcanum world create "Aethelgard" --universe "Solaris-Verse"

# Initialize a new Novel Manuscript
arcanum manuscript scaffold "The-Starlight-Saga" --preset three_act_classic
```

---

## 7. Step 6 — Start Writing

Use the Visual Scene Inspector, open your favorite markdown editor, or write in Zen Studio (`arcanum zen`). Use `@pov:`, `@location:`, and `@time:` headers to unlock instant timeline synchronization and character roster tracking.

---

## 8. Step 7 — Protect Your Work (Backups)

```bash
# Record an instant snapshot
arcanum snapshot "Completed Act I revision"

# Create a standalone verified archive
arcanum backup --target ~/Universes/Solaris-Verse

# Restore with fail-closed safety
arcanum restore /path/to/archive.tar.gz /path/to/restore-destination
```

---

## 9. Step 8 — Publish Your Book

```bash
# Compile trade-quality PDF via Typst
arcanum export The-Starlight-Saga --format typst

# Compile EPUB via Calibre
arcanum export The-Starlight-Saga --format epub
```

---

## 10. Optional Add-Ons

- **Obsidian**: Open your World Bible folder (`~/Universes/<Universe>/<World>`) in Obsidian to use the 10 bundled worldbuilding plugins.
- **novelWriter**: Open `nwProject.nwx` in novelWriter for hierarchical chapter outlining.

---

## 11. Troubleshooting

- **Command Not Found (`arcanum`)**: Run `pip install -e .` from the repository root, or invoke directly via `python -m scripts.lib.cli`.
- **Port Conflict in Studio Hub**: Pass a custom port: `arcanum hub --port 8999`.
- **Restore Refused Overwrite**: The restore command refuses to overwrite non-empty folders without `--force`. Pass `--force` to confirm overwrite.
