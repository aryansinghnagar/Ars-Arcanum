#!/usr/bin/env python3
"""
Unit Tests for Ars Arcanum Lockfile & Concurrency Control (tests/test_lockfile.py)
================================================================================
Validates:
1. Lock acquisition, re-entrance/exclusive blocking, and timeout handling.
2. Context manager cleanup and descriptor release.
3. Metadata recording into lockfile.
4. World and manuscript lock helpers.
"""

import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch
import os

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.lockfile import (
    ArcanumLock,
    LockError,
    LockTimeoutError,
    acquire_manuscript_lock,
    acquire_world_lock,
)


class TestLockfile(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.work_dir = Path(self.tmp_dir.name)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_basic_lock_acquisition_and_release(self):
        lock_file = self.work_dir / ".arcanum.lock"
        with ArcanumLock(lock_file, op_name="test_op") as lock:
            self.assertTrue(lock._is_locked)
            self.assertTrue(lock_file.is_file())

        self.assertFalse(lock._is_locked)
        content = lock_file.read_text(encoding="utf-8")
        self.assertIn("test_op", content)
        self.assertIn("pid", content)

    def test_shared_lock_acquisition(self):
        lock_file = self.work_dir / ".arcanum_shared.lock"
        with ArcanumLock(lock_file, exclusive=False, op_name="shared_read") as lock:
            self.assertTrue(lock._is_locked)
        self.assertFalse(lock._is_locked)

    def test_nested_lock_timeout(self):
        lock_file = self.work_dir / ".arcanum.lock"
        with ArcanumLock(lock_file, op_name="outer"):
            t0 = time.monotonic()
            try:
                with ArcanumLock(lock_file, timeout=0.2, op_name="inner"):
                    pass
            except LockTimeoutError as e:
                self.assertIn("Timed out", str(e))
            elapsed = time.monotonic() - t0
            self.assertGreaterEqual(elapsed, 0.15)

    def test_world_and_manuscript_helpers(self):
        world_dir = self.work_dir / "TestWorld"
        world_dir.mkdir()
        with acquire_world_lock(world_dir, op_name="lore_update"):
            self.assertTrue((world_dir / ".arcanum.lock").is_file())

        ms_dir = self.work_dir / "TestManuscript"
        ms_dir.mkdir()
        with acquire_manuscript_lock(ms_dir, op_name="draft_edit"):
            self.assertTrue((ms_dir / ".arcanum.lock").is_file())

    def test_lock_error_hierarchy(self):
        err = LockError("Base error")
        self.assertIsInstance(err, Exception)
        timeout_err = LockTimeoutError("Timeout error")
        self.assertIsInstance(timeout_err, LockError)

    def test_posix_fcntl_locking_and_unlocking(self):
        import types
        fake_fcntl = types.ModuleType("fcntl")
        fake_fcntl.LOCK_EX = 2
        fake_fcntl.LOCK_SH = 1
        fake_fcntl.LOCK_NB = 4
        fake_fcntl.LOCK_UN = 8
        fake_fcntl.flock = unittest.mock.MagicMock()

        lock_file = self.work_dir / ".fcntl.lock"
        with patch("lib.lockfile.HAS_FCNTL", True), patch("lib.lockfile.fcntl", fake_fcntl, create=True):
            with ArcanumLock(lock_file, exclusive=True, op_name="fcntl_test") as lock:
                self.assertTrue(lock._is_locked)
                fake_fcntl.flock.assert_called()
            self.assertFalse(lock._is_locked)

    def test_fallback_locking_when_no_fcntl_or_msvcrt(self):
        lock_file = self.work_dir / ".fallback.lock"
        with patch("lib.lockfile.HAS_FCNTL", False), patch("lib.lockfile.HAS_MSVCRT", False):
            with ArcanumLock(lock_file, op_name="fallback_test") as lock:
                self.assertTrue(lock._is_locked)
            self.assertFalse(lock._is_locked)

    def test_metadata_write_exception_ignored(self):
        lock_file = self.work_dir / ".meta_err.lock"
        with patch("os.write", side_effect=OSError("Disk write error")):
            with ArcanumLock(lock_file, op_name="meta_err") as lock:
                self.assertTrue(lock._is_locked)

    def test_release_oserror_handling(self):
        lock_file = self.work_dir / ".release_err.lock"
        lock = ArcanumLock(lock_file)
        lock.acquire()
        fd = lock._fd
        try:
            with patch("os.close", side_effect=OSError("Close error")):
                lock.release()
                self.assertFalse(lock._is_locked)
        finally:
            if fd is not None:
                try:
                    os.close(fd)
                except OSError:
                    pass


if __name__ == "__main__":
    unittest.main()
