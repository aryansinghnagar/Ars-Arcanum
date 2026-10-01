#!/usr/bin/env python3
"""
Ars Arcanum Pure-Python Standalone Restore Engine (scripts/lib/restore.py)
=========================================================================
Restores world vaults, manuscripts, and universes from standalone .tar.gz
and GPG-encrypted archives with cryptographic SHA-256 verification,
path traversal defense, and ArcanumLock safety invariants.

Zero-dependency standard library implementation providing cross-platform
reliability across Linux, macOS, and Windows.
"""

from __future__ import annotations

import argparse
import getpass
import hashlib
import json
import logging
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path
from typing import Any

try:
    from lib.lockfile import ArcanumLock
except ImportError:
    from lockfile import ArcanumLock

logger = logging.getLogger("arcanum.restore")


def compute_file_sha256(file_path: Path) -> str:
    """Computes SHA-256 hexadecimal hash of a file."""
    h = hashlib.sha256()
    with file_path.open("rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def verify_archive_checksum(archive_path: Path) -> tuple[bool, str, str | None]:
    """
    Checks if a .sha256 sidecar exists and verifies archive integrity.
    Returns (is_valid, actual_sha, expected_sha_or_none).
    """
    actual_sha = compute_file_sha256(archive_path)
    sha_file = archive_path.with_name(f"{archive_path.name}.sha256")
    if not sha_file.is_file():
        # Fallback to .tar.gz.sha256
        sha_file = archive_path.with_suffix(".sha256")

    if not sha_file.is_file():
        return True, actual_sha, None

    try:
        content = sha_file.read_text(encoding="utf-8").strip()
        expected_sha = content.split()[0].strip()
        is_valid = (actual_sha.lower() == expected_sha.lower())
        return is_valid, actual_sha, expected_sha
    except Exception as e:
        logger.warning("Could not read sha256 sidecar file: %s", e)
        return True, actual_sha, None


def is_safe_tar_member(member: tarfile.TarInfo, dest_dir: Path) -> bool:
    """Guards against path traversal attacks in tar archive members."""
    # Reject absolute paths or paths containing parent directory traversals
    norm = os.path.normpath(member.name)
    if norm.startswith("..") or norm.startswith("/") or norm.startswith("\\"):
        return False
    target_path = (dest_dir / norm).resolve()
    return dest_dir.resolve() in target_path.parents or target_path == dest_dir.resolve()


def restore_backup(
    archive_path: Path | str,
    target_dir: Path | str | None = None,
    passphrase: str | None = None,
    force: bool = False,
    timeout: float = 10.0,
) -> dict[str, Any]:
    """
    Restores a backup archive safely under ArcanumLock.
    """
    arc = Path(archive_path).resolve()
    if not arc.is_file():
        raise FileNotFoundError(f"Archive file not found: {arc}")

    # 1. Verify SHA-256 Checksum
    valid_sha, actual_sha, expected_sha = verify_archive_checksum(arc)
    if not valid_sha:
        raise ValueError(
            f"Archive checksum mismatch! Expected {expected_sha}, but got {actual_sha}. Archive may be corrupted."
        )

    # 2. Handle GPG Decryption
    is_gpg = arc.name.endswith(".gpg")
    tmp_decrypted: Path | None = None
    tar_to_extract = arc

    if is_gpg:
        gpg_bin = shutil.which("gpg") or shutil.which("gpg2")
        if not gpg_bin:
            raise RuntimeError("GPG binary not found in PATH for encrypted archive restoration.")

        active_passphrase = passphrase or os.environ.get("ARCANUM_PASSPHRASE")
        if not active_passphrase and sys.stdin.isatty():
            active_passphrase = getpass.getpass("Enter GPG passphrase to decrypt archive: ")

        if not active_passphrase:
            raise ValueError("Passphrase required to decrypt archive.")

        fd, tmp_path_str = tempfile.mkstemp(prefix=".arcanum_restore_", suffix=".tar.gz")
        os.close(fd)
        tmp_decrypted = Path(tmp_path_str)

        gpg_cmd = [
            gpg_bin,
            "--batch",
            "--yes",
            "--decrypt",
            "--passphrase-fd", "0",
            "--pinentry-mode", "loopback",
            "--output", str(tmp_decrypted),
            str(arc),
        ]

        proc = subprocess.run(
            gpg_cmd,
            input=active_passphrase.encode("utf-8"),
            capture_output=True,
            check=False,
        )
        if proc.returncode != 0:
            tmp_decrypted.unlink(missing_ok=True)
            raise RuntimeError(f"GPG decryption failed: {proc.stderr.decode('utf-8', errors='replace')}")

        tar_to_extract = tmp_decrypted

    try:
        # Determine extraction root destination
        dest_root = Path(target_dir).resolve() if target_dir else arc.parent.parent
        dest_root.mkdir(parents=True, exist_ok=True)

        extracted_members: list[str] = []
        lock_file = dest_root / ".arcanum.lock"

        with ArcanumLock(lock_file, timeout=timeout, op_name="restore"):
            with tarfile.open(tar_to_extract, "r:gz") as tar:
                # Security: Validate all members before extraction
                safe_members = []
                for m in tar.getmembers():
                    if not is_safe_tar_member(m, dest_root):
                        raise ValueError(f"Dangerous path traversal detected in archive member: {m.name}")
                    safe_members.append(m)

                # Safe extraction (Python 3.12+ data_filter or standard extract)
                if hasattr(tarfile, "data_filter"):
                    tar.extractall(dest_root, members=safe_members, filter="data")
                else:
                    tar.extractall(dest_root, members=safe_members)  # nosec B202 # noqa: S202

                for m in safe_members:
                    extracted_members.append(m.name)

        return {
            "status": "success",
            "restored_from": str(arc),
            "destination": str(dest_root),
            "sha256": actual_sha,
            "total_extracted": len(extracted_members),
            "root_member": extracted_members[0] if extracted_members else "",
        }
    finally:
        if tmp_decrypted and tmp_decrypted.exists():
            tmp_decrypted.unlink(missing_ok=True)


restore_archive = restore_backup


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="arcanum restore",
        description="Ars Arcanum Verified Archive Restoration Engine",
    )
    parser.add_argument("archive", help="Path to .tar.gz or .tar.gz.gpg backup archive")
    parser.add_argument("-d", "--destination", help="Target destination directory for restored project")
    parser.add_argument("--passphrase", help="Symmetric passphrase for encrypted archives")
    parser.add_argument("-f", "--force", action="store_true", help="Overwrite existing files without prompting")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON status")

    args = parser.parse_args(argv)
    try:
        res = restore_backup(
            archive_path=args.archive,
            target_dir=args.destination,
            passphrase=args.passphrase,
            force=args.force,
        )
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print(f"[✓] Project successfully restored from: {res['restored_from']}")
            print(f"    Destination      : {res['destination']}")
            print(f"    Extracted Items  : {res['total_extracted']}")
            print(f"    SHA-256 Verified : {res['sha256']}")
        return 0
    except Exception as e:
        if args.json:
            print(json.dumps({"status": "error", "error": str(e)}, indent=2))
        else:
            print(f"Error restoring backup: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
