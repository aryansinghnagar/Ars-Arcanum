# Toolchain Diagnostics Engine (`diagnostics`)
> **Domain F: Retrieval & Infrastructure** | **CLI:** `arcanum doctor` / `arcanum diag`

---

## 1. Overview & Theoretical Rationale
The **Diagnostics Engine** scans the host environment to verify binary capabilities, file system health, Python interpreter versions, and compilation toolchains (Pandoc, Typst, Git, GPG, FFmpeg).

---

## 2. Capability Matrix Checks
- **Core Runtime**: Python 3.10+ standard library primitives.
- **Typesetting & Export**: Typst (`typst --version`), Pandoc (`pandoc --version`).
- **Cryptographic Security**: GnuPG (`gpg --version`).
- **Version Control**: Git (`git --version`).
- **Storage Subsystem**: Atomic write capability and filesystem lock availability (`flock` on POSIX, `locking` on Windows).

---

## 3. CLI Command
```bash
# Run comprehensive diagnostic scan
arcanum doctor

# Output diagnostic report in JSON format for automated CI
arcanum doctor --json
```
