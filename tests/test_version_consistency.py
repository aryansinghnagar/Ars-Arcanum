#!/usr/bin/env python3
"""
Unit test for version consistency across CLI and core engines (tests/test_version_consistency.py).
"""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
ARCANUM_BASH = REPO_ROOT / "scripts" / "arcanum"
CLI_PY = REPO_ROOT / "scripts" / "lib" / "cli.py"
CHANGELOG_MD = REPO_ROOT / "CHANGELOG.md"
DIAGNOSTICS_PY = REPO_ROOT / "scripts" / "lib" / "diagnostics.py"


class TestVersionConsistency(unittest.TestCase):
    """Ensures version numbers across all dispatchers and modules are synchronized."""

    def test_version_strings_match(self):
        # 1. Read Bash dispatcher version
        self.assertTrue(ARCANUM_BASH.is_file())
        bash_text = ARCANUM_BASH.read_text(encoding="utf-8")
        bash_match = re.search(r'VERSION="([^"]+)"', bash_text)
        self.assertIsNotNone(bash_match, "Could not find VERSION in scripts/arcanum")
        bash_version = bash_match.group(1)

        # 2. Read Python CLI version
        self.assertTrue(CLI_PY.is_file())
        py_text = CLI_PY.read_text(encoding="utf-8")
        py_match = re.search(r'VERSION\s*=\s*"([^"]+)"', py_text)
        self.assertIsNotNone(py_match, "Could not find VERSION in scripts/lib/cli.py")
        py_version = py_match.group(1)

        # 3. Check CHANGELOG.md top released version
        self.assertTrue(CHANGELOG_MD.is_file())
        changelog_text = CHANGELOG_MD.read_text(encoding="utf-8")
        cl_match = re.search(r'##\s*\[([0-9.]+)\]', changelog_text)
        self.assertIsNotNone(cl_match, "Could not find version header in CHANGELOG.md")
        cl_version = cl_match.group(1)

        # 4. Diagnostics
        self.assertTrue(DIAGNOSTICS_PY.is_file())
        diag_text = DIAGNOSTICS_PY.read_text(encoding="utf-8")
        diag_match = re.search(r'VERSION\s*=\s*"([^"]+)"', diag_text)
        self.assertIsNotNone(diag_match, "Could not find VERSION in diagnostics.py")
        diag_version = diag_match.group(1)

        # Assert all versions match exactly 0.1.0
        expected_version = "0.1.0"
        for label, ver in [
            ("Bash arcanum", bash_version),
            ("Python CLI", py_version),
            ("CHANGELOG.md", cl_version),
            ("Diagnostics", diag_version),
        ]:
            self.assertEqual(
                ver,
                expected_version,
                f"{label} version ({ver}) does not match expected standardized version ({expected_version})"
            )


if __name__ == "__main__":
    unittest.main()
