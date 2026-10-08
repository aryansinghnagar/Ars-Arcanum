# Ars Arcanum Platform & Environment Support Matrix

This document defines the formal compatibility, architecture tiers, and display server support for **Ars Arcanum**.

---

## 1. Operating System Tiers

| Environment | Version | Desktop / Terminal Interface | Architecture | Support Tier | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Linux Mint** | 22 (Wilma) / 21.x | XFCE (Primary Reference) / GTK3 | x86_64 / ARM64 | **Tier 1** | Target Reference Platform (Desktop + CLI) |
| **Ubuntu Desktop** | 24.04 LTS (Noble) / 22.04 LTS | GNOME / XFCE / GTK3 | x86_64 / ARM64 | **Tier 1** | CI Reference & Fully Supported |
| **Debian** | 13 (Trixie) / 12 (Bookworm) | XFCE / GTK3 | x86_64 / ARM64 | **Tier 1** | Fully Supported |
| **Windows** | 10 / 11 | PowerShell / Windows Terminal / Studio Hub / Desktop Shortcuts | x86_64 / ARM64 | **Tier 1** | Pure Python CLI, 1-Click Installer (`setup_arcanum.ps1`), Hub, Zen Studio, Engines & `pip install .` |
| **macOS** | 13+ (Ventura, Sonoma, Sequoia) | Terminal / Studio Hub / Zen Studio | Apple Silicon / Intel | **Tier 1** | Pure Python CLI, Hub, Zen Studio, Engines & `pip install .` |
| **Fedora / RHEL** | 39 / 40 / 41 | GNOME / XFCE | x86_64 | **Tier 2** | Supported via DNF & RPM spec (`pkg/rpm/`) |
| **Arch Linux / Manjaro** | Rolling | Any | x86_64 | **Tier 2** | Supported via Pacman & AUR PKGBUILD (`pkg/arch/`) |
| **openSUSE** | Tumbleweed / Leap | Any | x86_64 | **Tier 2** | Supported via Zypper |

### Tier Definitions
- **Tier 1 (Target Reference & Cross-Platform Python Core)**: Fully verified through automated test suites (958 tests), packaging builds (`pip install .`), Studio Hub, Zen Studio, Story Canvas, Windows 1-click installer (`setup_arcanum.ps1`), and all 47 craft engines. Linux provides native GTK3 desktop menus, system launchers, and shell wrappers (`scripts/arcanum`).
- **Tier 2 (Compatible Distributions)**: Supported via distro package specs and `--force` flag in shell setup scripts. Package manager variations are handled gracefully by fallback routines.

---

## 2. Display Server & Desktop Integration

| Component | X11 | Wayland | Windows / macOS | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **PyGObject GTK3 Desktop GUI** | :white_check_mark: Verified | :white_check_mark: Supported | :warning: Requires X11 / GTK stack | Native Linux desktop GUI |
| **Studio Hub (Webview)** | :white_check_mark: Verified | :white_check_mark: Supported | :white_check_mark: Native Browser | Standalone offline browser cockpit |
| **Zen Drafting Studio** | :white_check_mark: Verified | :white_check_mark: Supported | :white_check_mark: Native Browser | Standalone offline typewriter interface |
| **Zenity Dialogs** | :white_check_mark: Verified | :white_check_mark: Supported | N/A | Detected via `$WAYLAND_DISPLAY` / `$DISPLAY` |
| **Desktop Launchers** (`.desktop`) | :white_check_mark: Verified | :white_check_mark: Supported | N/A | Installed to `~/.local/share/applications` |
| **Notifications** (`notify-send`) | :white_check_mark: Verified | :white_check_mark: Supported | N/A | Standard `org.freedesktop.Notifications` |
| **Focus Mode** (FocusWriter) | :white_check_mark: Verified | :white_check_mark: Supported | Optional | Native Qt fullscreen support |

---

## 3. Hardware Baseline Recommendations

| Resource | Minimum | Recommended |
| :--- | :--- | :--- |
| **CPU** | 64-bit Dual Core (Intel / AMD / ARM64) | Intel Core i5-1335U or AMD Ryzen 5 / Apple Silicon M-series |
| **RAM** | 4 GB | 16 GB |
| **Storage** | 10 GB free space | 50 GB+ NVMe SSD (with LUKS or BitLocker Full-Disk Encryption) |
| **Display** | 1366 × 768 | 1920 × 1080 (FHD) or higher |
| **External Media** | USB Flash Drive | Dedicated USB 3.0 External SSD/HDD for 3-2-1 backups |
