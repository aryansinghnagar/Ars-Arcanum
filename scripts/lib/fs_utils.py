#!/usr/bin/env python3
"""
Ars Arcanum Filesystem & Atomic Storage Utilities (scripts/lib/fs_utils.py)
Provides crash-resilient transactional file writes and secure directory operations.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any


def atomic_write(path: Path | str, data: str | bytes, encoding: str = "utf-8") -> None:
    """
    Safely and atomically writes data to path using a staged temporary file and os.replace.
    Ensures that interrupted writes never leave corrupted or truncated files.
    """
    target = Path(path).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)

    is_bytes = isinstance(data, (bytes, bytearray))
    mode = "wb" if is_bytes else "w"

    # Stage temporary file in the same directory to ensure same filesystem for os.replace
    prefix = f".{target.name}."
    fd, tmp_path_str = tempfile.mkstemp(dir=target.parent, prefix=prefix, suffix=".tmp")
    tmp_path = Path(tmp_path_str)
    fd_closed = False

    try:
        try:
            if is_bytes:
                with os.fdopen(fd, mode) as f:
                    fd_closed = True
                    f.write(data)
                    f.flush()
                    os.fsync(f.fileno())
            else:
                with os.fdopen(fd, mode, encoding=encoding, newline="") as f:
                    fd_closed = True
                    f.write(data)
                    f.flush()
                    os.fsync(f.fileno())
        finally:
            if not fd_closed:
                try:
                    os.close(fd)
                except OSError:
                    pass

        # Preserve permissions of the original file if it exists
        if target.exists():
            try:
                os.chmod(tmp_path, target.stat().st_mode & 0o7777)
            except OSError:
                pass

        os.replace(tmp_path, target)

        # On POSIX systems, fsync parent directory to ensure directory entry is flushed
        if hasattr(os, "O_DIRECTORY"):
            try:
                dfd = os.open(target.parent, os.O_RDONLY | os.O_DIRECTORY)
                try:
                    os.fsync(dfd)
                finally:
                    os.close(dfd)
            except Exception:
                pass
    except BaseException:
        try:
            if tmp_path.exists():
                tmp_path.unlink()
        except OSError:
            pass
        raise


def check_filesystem(target_dir: Path | str | None = None) -> dict[str, Any]:
    """Runs diagnostics on filesystem write safety and atomic replacement guarantees."""
    base = Path(target_dir).resolve() if target_dir else Path.cwd()
    base.mkdir(parents=True, exist_ok=True)
    test_file = base / ".arcanum_fs_test.tmp"
    test_content = "Ars Arcanum Atomic Write Test\n"

    try:
        atomic_write(test_file, test_content)
        read_back = test_file.read_text(encoding="utf-8")
        is_match = (read_back == test_content)
        test_file.unlink(missing_ok=True)
        return {
            "path": str(base),
            "atomic_write_verified": is_match,
            "status": "healthy" if is_match else "corrupted",
            "posix_fsync_supported": hasattr(os, "O_DIRECTORY"),
        }
    except Exception as e:
        if test_file.exists():
            test_file.unlink(missing_ok=True)
        return {
            "path": str(base),
            "atomic_write_verified": False,
            "status": "error",
            "error": str(e),
            "posix_fsync_supported": hasattr(os, "O_DIRECTORY"),
        }


def main(argv: list[str] | None = None) -> int:
    import argparse
    import json

    parser = argparse.ArgumentParser(
        prog="arcanum fs",
        description="Atomic Storage & Filesystem Diagnostic Utility",
    )
    parser.add_argument("target", nargs="?", default=".", help="Target directory for filesystem audit")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON status")
    parser.add_argument("--check", action="store_true", help="Verify atomic write integrity")

    args = parser.parse_args(argv)
    res = check_filesystem(args.target)

    if args.json:
        print(json.dumps(res, indent=2))
        return 0 if res.get("atomic_write_verified") else 1

    print("Ars Arcanum Atomic Filesystem Diagnostics")
    print("=" * 55)
    print(f"Target Directory     : {res['path']}")
    print(f"Atomic Write Status  : {'✓ PASSED' if res.get('atomic_write_verified') else '✗ FAILED'}")
    print(f"Parent Directory Fsync: {'Supported (POSIX)' if res.get('posix_fsync_supported') else 'Emulated (Windows / Fallback)'}")
    if res.get("error"):
        print(f"Error Detail         : {res['error']}")
    return 0 if res.get("atomic_write_verified") else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())

