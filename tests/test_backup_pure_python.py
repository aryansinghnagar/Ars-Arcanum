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

    def test_detect_target_type(self):
        from lib.backup import detect_target_type
        # Universe
        u_dir = self.root / "TestUniv"
        u_dir.mkdir()
        (u_dir / "universe.yaml").write_text("name: U\n", encoding="utf-8")
        self.assertEqual(detect_target_type(u_dir), ("universe", "TestUniv"))

        # World
        w_dir = self.root / "TestW"
        w_dir.mkdir()
        (w_dir / "world.yaml").write_text("name: W\n", encoding="utf-8")
        self.assertEqual(detect_target_type(w_dir), ("world", "TestW"))

        # Manuscript
        m_dir = self.root / "TestM"
        m_dir.mkdir()
        (m_dir / "manuscript.yaml").write_text("name: M\n", encoding="utf-8")
        self.assertEqual(detect_target_type(m_dir), ("manuscript", "TestM"))

        # Generic Project
        p_dir = self.root / "TestP"
        p_dir.mkdir()
        self.assertEqual(detect_target_type(p_dir), ("project", "TestP"))

    def test_should_exclude(self):
        from lib.backup import should_exclude
        self.assertTrue(should_exclude(".git/config"))
        self.assertTrue(should_exclude("Backups/archive.tar.gz"))
        self.assertTrue(should_exclude("notes/draft.tmp"))
        self.assertTrue(should_exclude("notes/draft.bak"))
        self.assertFalse(should_exclude("01-Manuscript/ch1.md"))

    def test_verify_backup_integrity_edge_cases(self):
        # Non-existent file
        res = verify_backup_integrity(self.root / "nonexistent.tar.gz")
        self.assertFalse(res["valid"])

        # Checksum mismatch
        backup_out_dir = self.root / "BackupsCorrupt"
        res_backup = create_backup(self.project_dir, output_dir=backup_out_dir)
        archive_path = Path(res_backup["archive_path"])
        sha_file = archive_path.with_name(f"{archive_path.name}.sha256")
        sha_file.write_text("0000000000000000000000000000000000000000000000000000000000000000  fake\n", encoding="utf-8")
        res_corrupt = verify_backup_integrity(archive_path)
        self.assertFalse(res_corrupt["valid"])

    def test_restore_checksum_mismatch_error(self):
        backup_out_dir = self.root / "BackupsMismatch"
        res_backup = create_backup(self.project_dir, output_dir=backup_out_dir)
        archive_path = Path(res_backup["archive_path"])
        sha_file = archive_path.with_name(f"{archive_path.name}.sha256")
        sha_file.write_text("1111111111111111111111111111111111111111111111111111111111111111  bad\n", encoding="utf-8")

        restore_target = self.root / "MismatchRestore"
        with self.assertRaises(ValueError) as cm:
            restore_archive(archive_path, target_dir=restore_target)
        self.assertIn("checksum mismatch", str(cm.exception).lower())

    def test_restore_missing_archive_error(self):
        missing_tar = self.root / "does_not_exist.tar.gz"
        with self.assertRaises(FileNotFoundError):
            restore_archive(missing_tar, target_dir=self.root / "out")

    def test_cli_main_entry_points(self):
        from lib.backup import main as backup_main
        from lib.restore import main as restore_main
        from lib.snapshot import main as snapshot_main

        backup_dir = self.root / "CliBackups"
        ret = backup_main([str(self.project_dir), "-o", str(backup_dir), "--json", "-t", "test-tag"])
        self.assertEqual(ret, 0)

        # Test backup error branch
        ret_err = backup_main(["nonexistent_dir_123", "--json"])
        self.assertEqual(ret_err, 1)

        backups = list_backups(backup_dir)
        self.assertEqual(len(backups), 1)

        # Restore CLI
        restore_dir = self.root / "CliRestored"
        ret_restore = restore_main([backups[0]["path"], "-d", str(restore_dir), "--json", "-f"])
        self.assertEqual(ret_restore, 0)

        # Restore CLI error branch
        ret_restore_err = restore_main(["nonexistent.tar.gz", "--json"])
        self.assertEqual(ret_restore_err, 1)

        # Snapshot CLI
        ret_snap = snapshot_main([str(self.project_dir), "-m", "CLI snapshot", "--json"])
        self.assertEqual(ret_snap, 0)


if __name__ == "__main__":
    unittest.main()

