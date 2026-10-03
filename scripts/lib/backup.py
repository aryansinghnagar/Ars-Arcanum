#!/usr/bin/env python3
"""
Ars Arcanum Pure-Python Standalone Backup Engine (scripts/lib/backup.py)
========================================================================
Creates verified, standalone, self-contained .tar.gz backup archives of
world vaults, manuscript workspaces, and universes with cryptographic SHA-256
checksum manifests, metadata sidecars, and optional GPG symmetric encryption.

Zero-dependency standard library implementation providing cross-platform
reliability across Linux, macOS, and Windows with ArcanumLock safety invariants.
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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from lib._bootstrap import atomic_write
    from lib.config import get_backup_destination
    from lib.lockfile import ArcanumLock
except ImportError:
    from _bootstrap import atomic_write
    from config import get_backup_destination
    from lockfile import ArcanumLock

logger = logging.getLogger("arcanum.backup")

BACKUP_VERSION = "4.2.1"

# Patterns and directories excluded from standalone archives
EXCLUDE_PATTERNS = {
    ".git",
    "Backups",
    ".arcanum.lock",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".DS_Store",
    "Thumbs.db",
    ".obsidian/cache",
}


def compute_file_sha256(file_path: Path) -> str:
    """Computes SHA-256 hexadecimal hash of a file."""
    h = hashlib.sha256()
    with file_path.open("rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def detect_target_type(target_path: Path) -> tuple[str, str]:
    """Detects project type (world, manuscript, universe, generic) and canonical name."""
    target = target_path.resolve()
    name = target.name

    if (target / "universe.yaml").is_file():
        return "universe", name
    if (target / "world.yaml").is_file():
        return "world", name
    if (target / "manuscript.yaml").is_file() or (target / "nwProject.nwx").is_file():
        return "manuscript", name
    if (target / "01-Manuscript").is_dir() or (target / "00-World-Bible").is_dir():
        return "manuscript", name
    return "project", name


def resolve_backup_destination(target_path: Path, custom_dest: Path | str | None = None) -> Path:
    """Resolves target backup directory honoring config and environment overrides."""
    if custom_dest:
        dest = Path(custom_dest).resolve()
        dest.mkdir(parents=True, exist_ok=True)
        return dest

    # Check configured secondary destination
    configured = get_backup_destination()
    if configured and Path(configured).is_dir():
        return Path(configured).resolve()

    # Default to Backups/ folder inside target or target parent
    dest = target_path / "Backups" if target_path.is_dir() else target_path.parent / "Backups"
    dest.mkdir(parents=True, exist_ok=True)
    return dest


def should_exclude(rel_posix_path: str) -> bool:
    """Checks if a relative path matches any exclusion patterns."""
    parts = rel_posix_path.split("/")
    return any(p in EXCLUDE_PATTERNS or p.endswith((".tmp", ".bak")) for p in parts)


def create_backup(
    target_path: Path | str,
    output_dir: Path | str | None = None,
    encrypt: bool = False,
    passphrase: str | None = None,
    tag: str | None = None,
    timeout: float = 10.0,
) -> dict[str, Any]:
    """
    Creates an atomic, stream-verified .tar.gz backup archive under ArcanumLock.
    """
    target = Path(target_path).resolve()
    if not target.exists():
        raise FileNotFoundError(f"Backup target not found: {target}")

    proj_type, proj_name = detect_target_type(target)
    dest_dir = resolve_backup_destination(target, output_dir)

    timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    tag_suffix = f"_{tag}" if tag else ""
    archive_stem = f"{proj_name}_{timestamp_str}{tag_suffix}.tar.gz"
    final_tar_path = dest_dir / archive_stem
    tmp_tar_path = dest_dir / f".{archive_stem}.tmp"

    lock_file = target / ".arcanum.lock" if target.is_dir() else target.parent / ".arcanum.lock"

    with ArcanumLock(lock_file, timeout=timeout, op_name="backup"):
        # 1. Collect files to archive
        file_list: list[Path] = []
        if target.is_dir():
            for root, dirs, files in os.walk(target):
                # Prune excluded directories in-place
                dirs[:] = [d for d in dirs if not should_exclude(d)]
                for f in files:
                    fp = Path(root) / f
                    rel_p = fp.relative_to(target).as_posix()
                    if not should_exclude(rel_p):
                        file_list.append(fp)
        else:
            file_list.append(target)

        # 2. Build tar.gz archive
        with tarfile.open(tmp_tar_path, "w:gz", compresslevel=6) as tar:
            for fp in file_list:
                arcname = fp.relative_to(target.parent if target.is_file() else target).as_posix()
                tar.add(fp, arcname=f"{proj_name}/{arcname}")

        # Atomic move to final archive
        if final_tar_path.exists():
            final_tar_path.unlink()
        tmp_tar_path.replace(final_tar_path)

        # 3. Compute SHA-256 checksum
        archive_sha = compute_file_sha256(final_tar_path)
        sha_file = final_tar_path.with_name(f"{final_tar_path.name}.sha256")
        sha_content = f"{archive_sha}  {final_tar_path.name}\n"
        atomic_write(sha_file, sha_content)

        # 4. Generate metadata sidecar
        meta_file = final_tar_path.with_name(f"{final_tar_path.name}.meta.json")
        meta_data = {
            "version": BACKUP_VERSION,
            "project_name": proj_name,
            "project_type": proj_type,
            "source_path": str(target),
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "archive_filename": final_tar_path.name,
            "archive_size_bytes": final_tar_path.stat().st_size,
            "sha256": archive_sha,
            "total_files": len(file_list),
            "encrypted": False,
        }

        # 5. Optional GPG encryption
        active_passphrase = passphrase or os.environ.get("ARCANUM_PASSPHRASE")
        if encrypt or active_passphrase:
            gpg_bin = shutil.which("gpg") or shutil.which("gpg2")
            if not gpg_bin:
                raise RuntimeError("GPG binary not found in PATH for encrypted backup.")

            if not active_passphrase and sys.stdin.isatty():
                active_passphrase = getpass.getpass("Enter GPG symmetric passphrase for backup: ")

            if not active_passphrase:
                raise ValueError("A passphrase is required for encrypted backups.")

            gpg_archive_path = final_tar_path.with_suffix(".tar.gz.gpg")
            gpg_cmd = [
                gpg_bin,
                "--batch",
                "--yes",
                "--symmetric",
                "--cipher-algo", "AES256",
                "--passphrase-fd", "0",
                "--pinentry-mode", "loopback",
                "--output", str(gpg_archive_path),
                str(final_tar_path),
            ]

            proc = subprocess.run(
                gpg_cmd,
                input=active_passphrase.encode("utf-8"),
                capture_output=True,
                check=False,
            )
            if proc.returncode != 0:
                raise RuntimeError(f"GPG encryption failed: {proc.stderr.decode('utf-8', errors='replace')}")

            # Remove unencrypted tar.gz
            final_tar_path.unlink(missing_ok=True)
            sha_file.unlink(missing_ok=True)

            # Re-compute SHA256 of encrypted archive
            enc_sha = compute_file_sha256(gpg_archive_path)
            enc_sha_file = gpg_archive_path.with_name(f"{gpg_archive_path.name}.sha256")
            atomic_write(enc_sha_file, f"{enc_sha}  {gpg_archive_path.name}\n")

            meta_data["archive_filename"] = gpg_archive_path.name
            meta_data["archive_size_bytes"] = gpg_archive_path.stat().st_size
            meta_data["sha256"] = enc_sha
            meta_data["encrypted"] = True
            atomic_write(meta_file, json.dumps(meta_data, indent=2) + "\n")

            return {
                "status": "success",
                "archive_path": str(gpg_archive_path),
                "sha256": enc_sha,
                "metadata": meta_data,
            }

        atomic_write(meta_file, json.dumps(meta_data, indent=2) + "\n")

        return {
            "status": "success",
            "archive_path": str(final_tar_path),
            "sha256": archive_sha,
            "metadata": meta_data,
        }


def list_backups(dest_dir: Path | str) -> list[dict[str, Any]]:
    """Lists available backup archives in a destination directory."""
    d = Path(dest_dir).resolve()
    if not d.is_dir():
        return []
    results = []
    for f in sorted(d.glob("*.tar.gz*")):
        if f.name.endswith(".sha256") or f.name.endswith(".meta.json") or f.name.startswith("."):
            continue
        meta_f = f.with_name(f"{f.name}.meta.json")
        meta = {}
        if meta_f.is_file():
            try:
                meta = json.loads(meta_f.read_text(encoding="utf-8"))
            except Exception:
                meta = {}
        results.append({
            "filename": f.name,
            "path": str(f),
            "size_bytes": f.stat().st_size,
            "metadata": meta,
        })
    return results


def verify_backup_integrity(archive_path: Path | str) -> dict[str, Any]:
    """Verifies SHA-256 integrity and tar structure of a backup archive."""
    p = Path(archive_path).resolve()
    if not p.is_file():
        return {"valid": False, "error": f"File not found: {p}"}

    actual_sha = compute_file_sha256(p)
    sha_file = p.with_name(f"{p.name}.sha256")
    if sha_file.is_file():
        expected_sha = sha_file.read_text(encoding="utf-8").strip().split()[0]
        if actual_sha != expected_sha:
            return {"valid": False, "error": f"SHA-256 mismatch: expected {expected_sha}, got {actual_sha}"}

    if p.name.endswith(".tar.gz"):
        try:
            with tarfile.open(p, "r:gz") as tar:
                members = tar.getnames()
                return {"valid": True, "sha256": actual_sha, "members_count": len(members)}
        except Exception as e:
            return {"valid": False, "error": f"Corrupt tar archive: {e}"}

    return {"valid": True, "sha256": actual_sha}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="arcanum backup",
        description="Ars Arcanum Verified Standalone Archive Generator",
    )
    parser.add_argument("target", nargs="?", default=".", help="Target world, manuscript or universe directory")
    parser.add_argument("-o", "--output", help="Destination directory for backup archive")
    parser.add_argument("-t", "--tag", help="Optional descriptive tag suffix (e.g. 'milestone-1')")
    parser.add_argument("-e", "--encrypt", action="store_true", help="Encrypt archive with GPG AES-256")
    parser.add_argument("--passphrase", help="Symmetric passphrase (prefer ARCANUM_PASSPHRASE env var)")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON status")

    args = parser.parse_args(argv)
    try:
        res = create_backup(
            target_path=args.target,
            output_dir=args.output,
            encrypt=args.encrypt,
            passphrase=args.passphrase,
            tag=args.tag,
        )
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            meta = res["metadata"]
            print(f"[✓] Backup created successfully: {res['archive_path']}")
            print(f"    Size     : {meta['archive_size_bytes'] / 1024:.1f} KB ({meta['total_files']} files)")
            print(f"    SHA-256  : {res['sha256']}")
            if meta["encrypted"]:
                print("    Security : GPG AES-256 Encrypted")
        return 0
    except Exception as e:
        if args.json:
            print(json.dumps({"status": "error", "error": str(e)}, indent=2))
        else:
            print(f"Error creating backup: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
