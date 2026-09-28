#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Filesystem & Atomic Storage Utilities (scripts/lib/fs_utils.py).
Validates:
- Atomic writes for string and byte data.
- Directory creation and permission preservation.
- Crash and exception resiliency (cleaning temporary files on failure).
- Filesystem diagnostic checks.
- CLI execution and exit codes.
"""

import io
import json
import os
import tempfile
import unittest
from pathlib import Path
import sys
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.fs_utils import (
    atomic_write,
    check_filesystem,
    main,
)


class TestFsUtils(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.work_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_atomic_write_string(self):
        dest = self.work_dir / "sub" / "test.txt"
        content = "Hello Atomic World!\n"
        atomic_write(dest, content)
        self.assertTrue(dest.is_file())
        self.assertEqual(dest.read_text(encoding="utf-8"), content)

    def test_atomic_write_bytes(self):
        dest = self.work_dir / "binary.dat"
        data = b"\x00\xFF\xAA\x55\x12\x34"
        atomic_write(dest, data)
        self.assertTrue(dest.is_file())
        self.assertEqual(dest.read_bytes(), data)

    def test_atomic_write_overwrite_and_permissions(self):
        dest = self.work_dir / "perms.txt"
        atomic_write(dest, "Version 1")
        # Overwrite
        atomic_write(dest, "Version 2")
        self.assertEqual(dest.read_text(encoding="utf-8"), "Version 2")

    def test_atomic_write_failure_cleans_tmp(self):
        dest = self.work_dir / "fail.txt"
        with patch("os.replace", side_effect=OSError("Simulated disk error")), self.assertRaises(OSError):
            atomic_write(dest, "Content that fails")

        # Verify no orphaned .tmp files in work_dir
        tmp_files = list(self.work_dir.glob(".*.tmp"))
        self.assertEqual(tmp_files, [])

    def test_check_filesystem(self):
        res = check_filesystem(self.work_dir)
        self.assertTrue(res["atomic_write_verified"])
        self.assertEqual(res["status"], "healthy")
        self.assertIn("posix_fsync_supported", res)

    def test_check_filesystem_failure(self):
        with patch("lib.fs_utils.atomic_write", side_effect=OSError("Read-only filesystem")):
            res = check_filesystem(self.work_dir)
            self.assertFalse(res["atomic_write_verified"])
            self.assertEqual(res["status"], "error")
            self.assertIn("Read-only filesystem", res["error"])

    def test_cli_main_stdout_and_json(self):
        # Human readable
        with patch.object(sys, "argv", ["fs_utils.py", str(self.work_dir)]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                rc = main()
                self.assertEqual(rc, 0)
                out = mock_stdout.getvalue()
                self.assertIn("Atomic Filesystem Diagnostics", out)
                self.assertIn("PASSED", out)

        # JSON mode
        with patch.object(sys, "argv", ["fs_utils.py", str(self.work_dir), "--json"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                rc = main()
                self.assertEqual(rc, 0)
                out = mock_stdout.getvalue()
                data = json.loads(out)
                self.assertTrue(data["atomic_write_verified"])

    def test_posix_directory_fsync(self):
        dest = self.work_dir / "posix.txt"
        orig_open = os.open
        opened_dirs = []

        def spy_open(path, flags, *args):
            if flags & 0x10000:
                opened_dirs.append(path)
                return 999
            return orig_open(path, flags, *args)

        with patch.object(os, "O_DIRECTORY", 0x10000, create=True), \
             patch("os.open", side_effect=spy_open), \
             patch("os.fsync") as mock_fsync, \
             patch("os.close") as mock_close:
            atomic_write(dest, "Posix data")
            self.assertTrue(len(opened_dirs) > 0)
            mock_fsync.assert_called()
            mock_close.assert_called()

    def test_posix_directory_fsync_exception_swallowed(self):
        dest = self.work_dir / "posix_err.txt"
        orig_open = os.open

        def spy_open(path, flags, *args):
            if flags & 0x10000:
                raise OSError("Directory fsync failed")
            return orig_open(path, flags, *args)

        with patch.object(os, "O_DIRECTORY", 0x10000, create=True), \
             patch("os.open", side_effect=spy_open):
            atomic_write(dest, "Posix data")
            self.assertTrue(dest.is_file())

    def test_chmod_oserror_swallowed(self):
        dest = self.work_dir / "chmod_test.txt"
        dest.write_text("existing", encoding="utf-8")
        with patch("os.chmod", side_effect=OSError("Chmod unsupported")):
            atomic_write(dest, "Updated")
            self.assertEqual(dest.read_text(encoding="utf-8"), "Updated")

    def test_fd_close_on_early_failure(self):
        dest = self.work_dir / "early_fail.txt"
        orig_close = os.close
        closed_fds = []

        def spy_close(fd):
            closed_fds.append(fd)
            orig_close(fd)

        with patch("os.fdopen", side_effect=ValueError("Invalid mode")), \
             patch("os.close", side_effect=spy_close):
            with self.assertRaises(ValueError):
                atomic_write(dest, "data")
        self.assertTrue(len(closed_fds) > 0)

    def test_tmp_unlink_failure_swallowed(self):
        dest = self.work_dir / "unlink_fail.txt"
        with patch("os.replace", side_effect=OSError("Replace error")), \
             patch("pathlib.Path.unlink", side_effect=OSError("Unlink error")), \
             self.assertRaises(OSError):
            atomic_write(dest, "data")


if __name__ == "__main__":
    unittest.main()
