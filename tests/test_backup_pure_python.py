#!/usr/bin/env python3
"""
Unit tests for Pure-Python Backup, Restore, and Snapshot Engines
(lib/backup.py, lib/restore.py, lib/snapshot.py)
"""

import os
import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.backup import create_backup, list_backups, verify_backup_integrity
from lib.restore import restore_archive
from lib.snapshot import save_snapshot
from lib.lockfile import ArcanumLock, LockTimeoutError


class TestPurePythonBackupRestore(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.project_dir = self.root / "Project"
        self.project_dir.mkdir(parents=True, exist_ok=True)

        # Configure git test user environment
        os.environ["GIT_AUTHOR_NAME"] = "Test Author"
        os.environ["GIT_AUTHOR_EMAIL"] = "test@example.com"
        os.environ["GIT_COMMITTER_NAME"] = "Test Author"
        os.environ["GIT_COMMITTER_EMAIL"] = "test@example.com"

        # Create mock project structure
        (self.project_dir / "world.yaml").write_text("name: TestWorld\n", encoding="utf-8")
        (self.project_dir / "World").mkdir()
        (self.project_dir / "World" / "lore.md").write_text("# Lore Note\nAncient secrets.\n", encoding="utf-8")
        (self.project_dir / "Manuscript").mkdir()
        (self.project_dir / "Manuscript" / "ch1.md").write_text("# Chapter 1\nIt was a dark night.\n", encoding="utf-8")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_save_snapshot_git_milestone(self):
        res = save_snapshot(self.project_dir, message="Initial chapter draft")
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["commit_hash"])
        self.assertEqual(res["message"], "Initial chapter draft")

        # Second save with no changes
        res_clean = save_snapshot(self.project_dir)
        self.assertEqual(res_clean["status"], "clean")

    def test_create_backup_and_restore(self):
        backup_out_dir = self.root / "Backups"
        res_backup = create_backup(self.project_dir, output_dir=backup_out_dir)
        archive_path = Path(res_backup["archive_path"])
        meta = res_backup["metadata"]
        self.assertTrue(archive_path.is_file())
        self.assertIn("sha256", meta)
        self.assertGreater(meta["total_files"], 0)

        # Verify backup listing
        backups = list_backups(backup_out_dir)
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0]["filename"], archive_path.name)

        # Verify integrity
        integrity = verify_backup_integrity(archive_path)
        self.assertTrue(integrity["valid"])

        # Restore to fresh target directory
        restore_target = self.root / "RestoredProject"
        res = restore_archive(archive_path, target_dir=restore_target)
        self.assertEqual(res["status"], "success")
        restored_lore = restore_target / "Project" / "World" / "lore.md"
        self.assertTrue(restored_lore.is_file())
        self.assertEqual(restored_lore.read_text(encoding="utf-8"), "# Lore Note\nAncient secrets.\n")

    def test_restore_archive_path_traversal_defense(self):
        import tarfile
        from lib.restore import compute_file_sha256
        malicious_tar = self.root / "evil.tar.gz"
        with tarfile.open(malicious_tar, "w:gz") as tar:
            data = b"EVIL DATA"
            ti = tarfile.TarInfo(name="../outside.txt")
            ti.size = len(data)
            import io
            tar.addfile(ti, io.BytesIO(data))

        # Provide valid sha256 sidecar so it proceeds to member validation
        (self.root / "evil.tar.gz.sha256").write_text(compute_file_sha256(malicious_tar), encoding="utf-8")

        restore_target = self.root / "SafeRestore"
        restore_target.mkdir()
        with self.assertRaises(ValueError) as cm:
            restore_archive(malicious_tar, target_dir=restore_target, force=True)
        self.assertIn("path traversal", str(cm.exception).lower())

    def test_restore_fails_closed_without_sidecar(self):
        backup_out_dir = self.root / "BackupsNoSha"
        res_backup = create_backup(self.project_dir, output_dir=backup_out_dir)
        archive_path = Path(res_backup["archive_path"])
        sha_file = archive_path.with_name(f"{archive_path.name}.sha256")
        if sha_file.exists():
            sha_file.unlink()

        restore_target = self.root / "RestoredNoSha"
        with self.assertRaises(ValueError) as cm:
            restore_archive(archive_path, target_dir=restore_target)
        self.assertIn("missing or unreadable sha-256", str(cm.exception).lower())

        # With require_checksum=False, it should succeed
        res = restore_archive(archive_path, target_dir=restore_target, require_checksum=False)
        self.assertEqual(res["status"], "success")

    def test_restore_force_overwrite_protection(self):
        backup_out_dir = self.root / "BackupsForce"
        res_backup = create_backup(self.project_dir, output_dir=backup_out_dir)
        archive_path = Path(res_backup["archive_path"])

        # Create non-empty destination
        restore_target = self.root / "NonEmptyRestore"
        restore_target.mkdir()
        (restore_target / "existing_chapter.md").write_text("Don't overwrite me!", encoding="utf-8")

        # Without force=True, should raise FileExistsError
        with self.assertRaises(FileExistsError) as cm:
            restore_archive(archive_path, target_dir=restore_target, force=False)
        self.assertIn("already contains", str(cm.exception).lower())

        # With force=True, should succeed
        res = restore_archive(archive_path, target_dir=restore_target, force=True)
        self.assertEqual(res["status"], "success")

    def test_concurrent_lock_safety(self):
        lock1 = ArcanumLock(self.project_dir / ".arcanum.lock", timeout=1.0)
        with lock1:
            lock2 = ArcanumLock(self.project_dir / ".arcanum.lock", timeout=0.1)
            with self.assertRaises(LockTimeoutError):
                with lock2:
                    pass

        # After releasing lock1, lock2 should acquire cleanly
        with lock2:
            pass


if __name__ == "__main__":
    unittest.main()
