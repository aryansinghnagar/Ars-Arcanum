# Atomic Filesystem & Security Primitives (`fs_utils`)
> **Domain F: Retrieval & Infrastructure** | **Module:** `scripts/lib/_bootstrap.py` & `scripts/lib/lockfile.py`

---

## 1. Overview & Architectural Rationale
Ars Arcanum enforces strict filesystem safety guarantees to prevent data corruption during unexpected system power loss or process crashes.

---

## 2. Invariant Storage Contracts

### 2.1 Atomic File Replacement (`atomic_write`)
Every file modification follows the POSIX atomic write lifecycle:
1. Write payload to a unique temporary file (`.tmp_xxxx`) in the target directory.
2. Flush user-space buffers via `file.flush()`.
3. Force OS disk sync via `os.fsync(file.fileno())`.
4. Close file descriptor.
5. Atomically replace destination via `os.replace(tmp, dest)`.
6. Force parent directory directory entry sync on POSIX platforms.

### 2.2 Cross-Platform Concurrency Locking (`ArcanumLock`)
Concurrency-sensitive operations (such as multi-file corpus exports and snapshot restorations) acquire exclusive advisory file locks:
- **POSIX**: `fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)`
- **Windows**: `msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)`

### 2.3 Path Traversal Sanitization
User-supplied identifiers (volume titles, draft names, snapshot IDs) must match the strict alphanumeric regex `^[A-Za-z0-9_-]+$`. Directory separators (`/`, `\`) and traversal tokens (`..`) are rejected immediately.
