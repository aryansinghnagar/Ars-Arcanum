# Ars Arcanum Threat Model & Security Posture (STRIDE-Lite)

**Version:** 0.1.0  
**Scope:** Core CLI (`arcanum`), Scaffolding Scripts, 47 Deterministic Python Library Engines (`scripts/lib/`), GTK Desktop App, Studio Hub Local HTTP Server (`scripts/lib/studio_hub.py`), Typesetting Bridges (Typst/Pandoc), and Storage/Backup Subsystems.  
**Target Environment:** Local single-user cross-platform desktop workstations (Linux Mint, Ubuntu, Debian, Arch, Fedora, Windows).

---

## 1. System Architecture & Trust Boundaries

Ars Arcanum operates exclusively as a **local-first desktop platform**. It does not expose public network ports or transmit user prose or metadata to cloud backends. When launched, the interactive **Studio Hub** (`arcanum hub`) binds exclusively to local loopback (`127.0.0.1` / `localhost` / `[::1]`).

### Key Trust Boundaries:
1. **User Working Tree (`~/Universes/`, `~/Manuscripts/`)**: Trusted local filesystem where author prose, notes, and manifests are stored and versioned via local Git.
2. **Local Studio Hub Interface (`http://127.0.0.1:8765`)**: Local HTTP/REST boundary providing interactive visualizations, telemetry inspection, and scoped craft engine execution under strict Host/Origin gating and an authorized engine allowlist.
3. **Untrusted External Inputs**:
   - Word Documents (`.docx`) imported from beta readers, co-authors, or editors.
   - Restored Backup Archives (`.tar.gz`) from external or shared drives.
   - Markdown notes containing arbitrary user text, YAML frontmatter, and WikiLinks (`[[...]]`).
   - Community Obsidian Plugin configurations (`.obsidian/`).
4. **Privileged Installer Surface**: `setup_arcanum.sh` (multi-distribution setup script).
5. **Offline Viewing Sandbox**: Generated static HTML visualization reports and charts opened in local web browsers.

```
[ External DOCX / Backup Archives / Community Plugins ] (Untrusted)
                         │
                         ▼ (Sanitization & Validation Barrier)
[ Ars Arcanum Core Engines: docx_sync, world_doctor, restore, cli ]
                         │
                         ▼ (Atomic Writes & Local Git)
[ Local Author Workspaces: ~/Universes, ~/Manuscripts ] (Trusted)
                         ▲
                         │ (Loopback HTTP / Scope API / Allowlist Runner)
[ Studio Hub Local Server: 127.0.0.1 / localhost ]
```

---

## 2. STRIDE-Lite Threat Analysis & Mitigations

### 1. Spoofing Identity (S)
* **Threat S1: Git Author Spoofing during Scaffolding.**
  - *Risk:* Automated scaffolding commits using an arbitrary or misleading identity, overwriting author attribution.
  - *Mitigation:* Scaffolding scripts query `git config user.name` and `git config user.email`. If configured, the user's authentic local Git identity is used. If unset, a neutral tool identity (`Ars Arcanum Studio <arcanum@local>`) is applied.

### 2. Tampering with Data (T)
* **Threat T1: Power Loss or Crash during File Write (Data Corruption).**
  - *Risk:* Mid-write crashes corrupting manuscripts, chapters, or world manifests.
  - *Mitigation:* All write operations across all library modules use `atomic_write()` (`scripts/lib/_bootstrap.py`), writing to a temporary file in the same parent directory, flushing, syncing (`fsync`), and atomically replacing via `os.replace`.
* **Threat T2: Silent Prose Loss during DOCX ↔ Markdown Synchronization.**
  - *Risk:* Asymmetrical mtime updates causing newer Markdown prose to be overwritten by older DOCX files.
  - *Mitigation:* Three-way SHA-256 state tracking (`.sync_state.json`). If both Markdown and DOCX diverge independently, the engine refuses in-place overwrite and branches to `<chapter>.conflict_<timestamp>.md`.
* **Threat T3: Backup Archive Tampering & Silent Overwrites.**
  - *Risk:* Accidental corruption or byte alteration in `.tar.gz` backups; silent overwriting of working directory chapters on restore.
  - *Mitigation:* Every archive generation emits a companion `.sha256` digest sidecar verified before any restoration drill. `restore.py` enforces fail-closed SHA-256 validation and refuses to extract into non-empty directories unless `--force` is explicitly specified.

### 3. Repudiation (R)
* **Threat R1: Untracked Draft Modifications.**
  - *Risk:* Authors unable to identify what changed between draft revisions.
  - *Mitigation:* Automatic draft milestone snapshotting (`arcanum draft`) and fine-grained visual redline diff reporting (`manuscript_diff.py`).

### 4. Information Disclosure (I)
* **Threat I1: Accidental Cloud Leakage of Unpublished Manuscripts.**
  - *Risk:* Background telemetry or third-party cloud analytics uploading creative IP.
  - *Mitigation:* Zero cloud telemetry, zero remote dependencies, zero analytics scripts. 100% offline air-gapped architecture.
* **Threat I2: XSS in Generated HTML Reports.**
  - *Risk:* Malicious script execution when rendering HTML corkboards, timelines, or codices.
  - *Mitigation:* Strict Content Security Policy declared in all HTML outputs:
    ```html
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
    ```

### 5. Denial of Service (D)
* **Threat D1: XML Entity Expansion Bomb (Billion Laughs) in DOCX Imports.**
  - *Risk:* Malicious DOCX input consuming infinite memory/CPU via recursive XML entity definitions.
  - *Mitigation:* DOCTYPE and ENTITY scanning on all incoming XML streams before AST processing (`docx_sync.py`, `importer.py`).
* **Threat D2: Path Traversal / Directory Injection.**
  - *Risk:* User-provided names containing `../` overwriting arbitrary system files.
  - *Mitigation:* Strict regex token validation `^[A-Za-z0-9_-]+$` enforced across all volume names, draft identifiers, and world targets (`_bootstrap.py`).

### 6. Elevation of Privilege & Web Perimeter (E)
* **Threat E1: Archive Restore Symlink & Hook Injection.**
  - *Risk:* Malicious backup archives extracting symlinks pointing to sensitive system files or placing executable `.git/hooks`.
  - *Mitigation:* Pure-Python archive extractor (`restore.py`) strictly filters out symlinks escaping the destination root, hardlinks, FIFOs, device nodes, and rejects any paths within `.git/hooks` or `.git/config`.
* **Threat E2: Cross-Origin / DNS Rebinding Attacks on Studio Hub Local Server.**
  - *Risk:* Malicious website in author's browser sending cross-origin POST requests to `http://127.0.0.1:8765/api/engine/run` to execute arbitrary commands.
  - *Mitigation:* 
    - Strict `Host` header validation rejecting DNS rebinding (allowing only `localhost`, `127.0.0.1`, `::1`, `[::1]`).
    - Strict `Origin` header validation rejecting `Origin: null` and cross-origin domains.
    - Strict Engine Execution Allowlist in `_execute_scoped_engine`: only registered craft modules in the static allowlist can be triggered; unlisted modules and system operations are rejected.
    - Global thread execution mutex preventing concurrent command stream interleaving.

---

## 3. Recommended Reading & Security References

1. **Howard, Michael & Lipner, Steve** (2006). *The Security Development Lifecycle: SDL: A Process for Developing Demonstrably More Secure Software*. Microsoft Press. (STRIDE methodology).
2. **Scarfone, Karen et al.** (2008). *Guide to Storage Security* (NIST SP 800-111). National Institute of Standards and Technology.
3. **OWASP Top 10** (2021). *Open Web Application Security Project*. (Injection, Broken Access Control, and Insecure Design mitigations).
