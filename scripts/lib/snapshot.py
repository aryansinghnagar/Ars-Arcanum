#!/usr/bin/env python3
"""
Ars Arcanum Pure-Python Snapshot & Version Milestone Engine (scripts/lib/snapshot.py)
=====================================================================================
Saves instantaneous Git version milestones for manuscripts, world vaults, and
universes under ArcanumLock safety invariants.

Provides programmatic and CLI interfaces across Windows, macOS, and Linux.
"""

from __future__ import annotations

import argparse
import json
import logging
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from lib.lockfile import ArcanumLock
except ImportError:
    from lockfile import ArcanumLock

logger = logging.getLogger("arcanum.snapshot")


def save_snapshot(
    target_path: Path | str = ".",
    message: str | None = None,
    timeout: float = 10.0,
) -> dict[str, Any]:
    """
    Records a Git milestone commit for the target project workspace under ArcanumLock.
    """
    target = Path(target_path).resolve()
    if not target.exists():
        raise FileNotFoundError(f"Snapshot target does not exist: {target}")

    git_bin = shutil.which("git")
    if not git_bin:
        raise RuntimeError("Git executable not found in PATH.")

    # Find the nearest git repository root
    git_root: Path | None = None
    cur = target if target.is_dir() else target.parent
    while cur != cur.parent:
        if (cur / ".git").exists():
            git_root = cur
            break
        cur = cur.parent

    if not git_root:
        # If target is a directory, initialize git
        if target.is_dir():
            subprocess.run([git_bin, "init", "-q"], cwd=str(target), check=True)
            git_root = target
        else:
            raise RuntimeError(f"Target '{target}' is not inside a Git repository.")

    lock_file = git_root / ".arcanum.lock"
    timestamp_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    commit_msg = message or f"Milestone Snapshot: {timestamp_str}"

    with ArcanumLock(lock_file, timeout=timeout, op_name="snapshot"):
        # 1. Stage all changes (excluding the active lock file)
        add_proc = subprocess.run(
            [git_bin, "add", "-A", ":!.arcanum.lock"],
            cwd=str(git_root),
            capture_output=True,
            text=True,
            check=False,
        )
        if add_proc.returncode != 0:
            raise RuntimeError(f"Git add failed: {add_proc.stderr}")

        # 2. Check if working tree has changes
        status_proc = subprocess.run(
            [git_bin, "status", "--porcelain", "--", ":!.arcanum.lock"],
            cwd=str(git_root),
            capture_output=True,
            text=True,
            check=True,
        )
        has_changes = bool(status_proc.stdout.strip())

        if not has_changes:
            # Retrieve latest commit hash
            rev_proc = subprocess.run(
                [git_bin, "rev-parse", "--short", "HEAD"],
                cwd=str(git_root),
                capture_output=True,
                text=True,
                check=False,
            )
            head_commit = rev_proc.stdout.strip() if rev_proc.returncode == 0 else "initial"
            return {
                "status": "clean",
                "message": "Working tree clean, nothing to commit.",
                "commit_hash": head_commit,
                "project_root": str(git_root),
            }

        # 3. Create commit with fallback author identity
        commit_proc = subprocess.run(
            [
                git_bin,
                "-c", "user.name=Arcanum Snapshot",
                "-c", "user.email=arcanum@local",
                "commit",
                "-m", commit_msg,
            ],
            cwd=str(git_root),
            capture_output=True,
            text=True,
            check=False,
        )
        if commit_proc.returncode != 0:
            raise RuntimeError(f"Git commit failed: {commit_proc.stderr}")

        rev_proc = subprocess.run(
            [git_bin, "rev-parse", "--short", "HEAD"],
            cwd=str(git_root),
            capture_output=True,
            text=True,
            check=True,
        )
        new_commit = rev_proc.stdout.strip()

        return {
            "status": "success",
            "message": commit_msg,
            "commit_hash": new_commit,
            "project_root": str(git_root),
            "timestamp": timestamp_str,
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="arcanum snapshot",
        description="Ars Arcanum Git Version Milestone Engine",
    )
    parser.add_argument("target", nargs="?", default=".", help="Target project directory")
    parser.add_argument("-m", "--message", help="Custom milestone note or commit message")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON status")

    args = parser.parse_args(argv)
    try:
        res = save_snapshot(target_path=args.target, message=args.message)
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            if res["status"] == "clean":
                print(f"[i] {res['message']} (HEAD: {res['commit_hash']})")
            else:
                print(f"[✓] Milestone snapshot saved: [{res['commit_hash']}] {res['message']}")
        return 0
    except Exception as e:
        if args.json:
            print(json.dumps({"status": "error", "error": str(e)}, indent=2))
        else:
            print(f"Error saving snapshot: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
