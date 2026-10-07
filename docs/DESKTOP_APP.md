# Native Desktop Application & GUI Presentation Architecture (DESKTOP_APP)
> **Engineering Specification & User Interface Reference** | Release v0.1.0 | Presentation Layer

---

## 1. System Overview & Adaptive Presentation Model

Ars Arcanum delivers a sovereign, native desktop control center for authoring, worldbuilding, and publishing pipelines without external electron or web runtime bloat.

The **Desktop Application** ([`scripts/arcanum_app.py`](file:///scripts/arcanum_app.py), [`scripts/lib/ui_gtk3/`](file:///scripts/lib/ui_gtk3/), [`scripts/lib/ui_adw.py`](file:///scripts/lib/ui_adw.py)) features an **Adaptive Presentation Tier**:

```text
                                [ arcanum_app.py ]
                                        |
                 +----------------------+----------------------+
                 |                      |                      |
      [ Tier 1: Libadwaita / GTK4 ]   [ Tier 2: Modular GTK3 ]   [ Tier 3: Browser Studio Hub ]
                 |                      |                      |
      Modern GNOME 45+ UI           Debian / Mint / XFCE      Headless / Zero PyGObject Fallback
      (AdwApplicationWindow)        (Gtk.ApplicationWindow)   (localhost HTTP Server + Browser)
```

1. **Tier 1 (Modern Libadwaita / GTK 4)**: Adaptive dark/light theme integration, `AdwNavigationView`, `AdwActionRow`, and native gesture navigation on modern GNOME / Wayland environments.
2. **Tier 2 (Modular GTK 3 Desktop)**: High-performance, lightweight GTK 3 application partitioned into cleanly decoupled tab controllers (<800 lines/file) running on Linux Mint, Ubuntu, and standard X11/Wayland desktops.
3. **Tier 3 (Zero-Dependency Sovereign Studio Hub)**: If PyGObject / GTK is missing (e.g. standard developer Python environments or Windows), automatically falls back to launching the local browser Studio Hub ([`scripts/lib/studio_hub.py`](file:///scripts/lib/studio_hub.py)).

---

## 2. Desktop Tab Taxonomy

The desktop window is organized into 7 focused creative workstations:

| Tab Identifier | Workstation Title | Key Capabilities & Integrations |
|:---|:---|:---|
| `cosmos` | **Universe & World Explorer** | Browse and scaffold narrative universes (`~/Universes/`), Obsidian world vaults, and volume branches. |
| `drafting` | **Manuscript Studio & Outlines** | Wordcount progress bars, Zen Studio launcher, NovelWriter integration, Redline diffing, and Scene Canvas. |
| `worldbuilding` | **Craft Engines Matrix** | Interactive forms for Astrophysics, Ecology, Conlang shifts, Causality DAGs, Factions, and Resonance Graph. |
| `publishing` | **Typesetting & Release Packager** | Pre-flight validation, Typst compile triggers, DOCX sync, Frontmatter builder, and Multi-volume Omnibus. |
| `safety` | **Git Milestones & Secure Backups** | Instant Git snapshots, SHA-256 verified .tar.gz archive creation, and Non-empty restore drills. |
| `doctor` | **Diagnostics & World Doctor** | Toolchain audit, LeechBlock rules validator, Novikov loop detection, and trait contradiction audits. |
| `tools` | **Retrieval, Heatmap & Soundscapes** | Hybrid TF-IDF / FTS5 search query bar, Revision Heatmap, Sprint Timer, and Ambient soundscape loops. |

---

## 3. Launching & CLI Controls

Authors and desktop launchers execute the application via `scripts/arcanum_app.py` or the `arcanum gui` CLI command:

```bash
# Auto-detect best available desktop presentation tier
arcanum gui

# Open directly to a specific workspace tab
arcanum gui --tab drafting
arcanum gui --tab worldbuilding

# Force modern Libadwaita / GTK 4 presentation layer
python3 scripts/arcanum_app.py --adw

# Force standard modular GTK 3 presentation layer
python3 scripts/arcanum_app.py --gtk3

# Probe system for available GUI backends
python3 scripts/arcanum_app.py --check-ui
```

---

## 4. Desktop Integration & Launchers

Ars Arcanum integrates into Linux application menus (GNOME, KDE, XFCE, Cinnamon) via standard `.desktop` entries in [`launchers/`](file:///launchers/):

- [`launchers/arcanum-app.desktop`](file:///launchers/arcanum-app.desktop): Main Desktop Application Launcher.
- [`launchers/arcanum-hub.desktop`](file:///launchers/arcanum-hub.desktop): Sovereign Studio Web Hub Launcher.
- [`launchers/arcanum-zen.desktop`](file:///launchers/arcanum-zen.desktop): Offline Zen Drafting Studio Launcher.

Install desktop files and icon assets into `~/.local/share/applications/` via:
```bash
arcanum setup
```

---

## 5. Verification & Headless CI Smoke Tests

The GUI presentation layers are verified automatically in CI pipelines using virtual X framebuffers (`xvfb`):

```bash
# Headless smoke test verifying clean startup without fatal GTK warnings
PYTHONPATH="/usr/lib/python3/dist-packages:${PYTHONPATH:-}" \
G_DEBUG=fatal-criticals timeout 10 \
xvfb-run -a python3 scripts/arcanum_app.py --adw || [ $? -eq 124 ]
```

Desktop entry file conformance is verified via `desktop-file-validate launchers/*.desktop` in [`scripts/verify.sh`](file:///scripts/verify.sh).
