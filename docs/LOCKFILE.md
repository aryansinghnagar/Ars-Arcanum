# Cross-Platform Concurrency Control & Lockfile Management (LOCKFILE)
> **Engineering Specification & Safety Manifesto** | Release v0.1.0 | Core Safety Layer

---

## 1. System Invariants & Purpose

In a local-first creative environment where background Git snapshots, automated hourly backups, CLI craft audits, and interactive GUI apps (Zen Studio, Desktop Hub, GTK3 Control Center) operate concurrently across shared vaults, file corruption from race conditions must be mathematically prevented.

The **Arcanum Lockfile Engine** ([`scripts/lib/lockfile.py`](file:///scripts/lib/lockfile.py)) implements an advisory concurrency gate guaranteeing:

1. **Zero Data Corruption**: Concurrency-sensitive operations (archive creation, schema migrations, Git snapshot commits, DOCX two-way synchronizations) must acquire an `ArcanumLock` before mutating vault files.
2. **Cross-Platform Native Primitives**: Uses native POSIX kernel file locking (`fcntl.flock`) on Linux/macOS and native Win32 C runtime file locking (`msvcrt.locking`) on Windows with explicit descriptor offset alignment (`os.lseek(fd, 0, os.SEEK_SET)`).
3. **Stale Lock Auto-Healing**: If a process crashes or is killed ungracefully (`SIGKILL`), subsequent lock acquisitions detect stale lock metadata via process PID probing (`os.kill(pid, 0)` on POSIX, `OpenProcess` / Win32 process handles on Windows) and safely break abandoned locks.
4. **Structured JSON Telemetry**: Lock files write structured JSON diagnostics (`pid`, `op_name`, `timestamp`, `host`, `exclusive`) to facilitate immediate debugging during lock contention.

---

## 2. Cross-Platform Architectural Matrix

```text
                                 [ ArcanumLock Request ]
                                            |
                         +------------------+------------------+
                         |                                     |
                 [ POSIX (Linux/macOS) ]             [ Windows (Win32) ]
                         |                                     |
               fcntl.flock(LOCK_EX/SH)             msvcrt.locking(LK_NBLCK)
                         |                                     |
               Atomic Kernel Descriptor           C Runtime File Descriptor Lock
                         +------------------+------------------+
                                            |
                                  [ Success / Retry ]
                                            |
                                  [ Write JSON Lock Info ]
```

### Locking Strategy Comparison

| Feature | POSIX Implementation | Windows Implementation |
|:---|:---|:---|
| **Lock Primitive** | `fcntl.flock(fd, fcntl.LOCK_EX \| fcntl.LOCK_NB)` | `msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)` |
| **Shared Read Locks** | `fcntl.LOCK_SH` | Shared read simulation via descriptor sharing |
| **File Offset Handling** | Invariant across file offset | Strict `os.lseek(fd, 0, os.SEEK_SET)` before lock/unlock |
| **Stale Lock Detection** | `os.kill(pid, 0)` (tests process existence without signal) | `ctypes.windll.kernel32.OpenProcess` query |
| **Cleanup on Crash** | Kernel automatically releases flock on FD close | OS kernel closes handle and releases lock on process exit |

---

## 3. Python Usage & Integration

The `ArcanumLock` class is an `AbstractContextManager` designed for idiomatic `with` blocks:

```python
from pathlib import Path
from scripts.lib.lockfile import ArcanumLock, LockTimeoutError

vault_dir = Path("/path/to/manuscript")
lock_path = vault_dir / ".arcanum_lock"

try:
    with ArcanumLock(lock_path, timeout=5.0, op_name="git_snapshot"):
        # Critical section: Concurrency-safe vault mutation
        execute_vault_backup(vault_dir)
except LockTimeoutError as e:
    print(f"Failed to acquire lock on {vault_dir} within timeout: {e}")
```

### Explicit Acquisition and Release

```python
lock = ArcanumLock("/path/to/vault/.arcanum_lock", timeout=10.0, op_name="migration")
try:
    lock.acquire()
    # Perform migration...
finally:
    lock.release()
```

---

## 4. Lockfile JSON Payload Schema

When active, the `.arcanum_lock` file stores a JSON payload:

```json
{
  "pid": 48291,
  "op_name": "git_snapshot",
  "exclusive": true,
  "timestamp": 1728288000.123,
  "datetime": "2026-10-07T10:50:00Z",
  "host": "author-laptop"
}
```

If another process attempts to lock the vault while active, it reads this diagnostic header and logs an informative message before backing off or timing out:
```text
Lock held by PID 48291 (git_snapshot) since 2026-10-07T10:50:00Z. Retrying...
```

---

## 5. Verification & Testing

The lockfile engine is validated by [`tests/test_lockfile.py`](file:///tests/test_lockfile.py), verifying:
- Exclusive vs. shared acquisition semantics.
- Timeout expiration behavior and custom timeout limits.
- Process death stale lock eviction.
- Windows `msvcrt` and POSIX `fcntl` mock execution suites.
- Context manager exit cleanup guarantees under unhandled exceptions.
