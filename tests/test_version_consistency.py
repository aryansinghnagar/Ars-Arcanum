#!/usr/bin/env python3
"""
Unit test for version consistency across CLI, package definitions, and documentation (tests/test_version_consistency.py).
"""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
ARCANUM_BASH = REPO_ROOT / "scripts" / "arcanum"
CLI_PY = REPO_ROOT / "scripts" / "lib" / "cli.py"
DEBIAN_CHANGELOG = REPO_ROOT / "debian" / "changelog"
CHANGELOG_MD = REPO_ROOT / "CHANGELOG.md"
ARCH_PKGBUILD = REPO_ROOT / "pkg" / "arch" / "PKGBUILD"
RPM_SPEC = REPO_ROOT / "pkg" / "rpm" / "ars-arcanum.spec"
FLATPAK_METAINFO = REPO_ROOT / "flatpak" / "org.arsarcanum.ArsArcanum.metainfo.xml"
DIAGNOSTICS_PY = REPO_ROOT / "scripts" / "lib" / "diagnostics.py"
RESONANCE_PY = REPO_ROOT / "scripts" / "lib" / "resonance.py"
STUDIO_HUB_PY = REPO_ROOT / "scripts" / "lib" / "studio_hub.py"


class TestVersionConsistency(unittest.TestCase):
    """Ensures version numbers across all dispatchers and packaging manifests are synchronized."""

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

        # 3. Read Debian changelog version
        self.assertTrue(DEBIAN_CHANGELOG.is_file())
        deb_text = DEBIAN_CHANGELOG.read_text(encoding="utf-8")
        deb_match = re.search(r'ars-arcanum\s*\(([0-9.]+)(?:-[0-9]+)?\)', deb_text)
        self.assertIsNotNone(deb_match, "Could not find version in debian/changelog")
        deb_version = deb_match.group(1)

        # 4. Check CHANGELOG.md top released version
        self.assertTrue(CHANGELOG_MD.is_file())
        changelog_text = CHANGELOG_MD.read_text(encoding="utf-8")
        cl_match = re.search(r'##\s*\[([0-9.]+)\]', changelog_text)
        self.assertIsNotNone(cl_match, "Could not find version header in CHANGELOG.md")
        cl_version = cl_match.group(1)

        # 5. Arch PKGBUILD
        self.assertTrue(ARCH_PKGBUILD.is_file())
        arch_text = ARCH_PKGBUILD.read_text(encoding="utf-8")
        arch_match = re.search(r'pkgver=([0-9.]+)', arch_text)
        self.assertIsNotNone(arch_match, "Could not find pkgver in PKGBUILD")
        arch_version = arch_match.group(1)

        # 6. RPM Spec
        self.assertTrue(RPM_SPEC.is_file())
        rpm_text = RPM_SPEC.read_text(encoding="utf-8")
        rpm_match = re.search(r'Version:\s*([0-9.]+)', rpm_text)
        self.assertIsNotNone(rpm_match, "Could not find Version in RPM spec")
        rpm_version = rpm_match.group(1)

        # 7. Flatpak Metainfo
        self.assertTrue(FLATPAK_METAINFO.is_file())
        flatpak_text = FLATPAK_METAINFO.read_text(encoding="utf-8")
        flatpak_match = re.search(r'<release\s+version="([0-9.]+)"', flatpak_text)
        self.assertIsNotNone(flatpak_match, "Could not find release version in Flatpak metainfo")
        flatpak_version = flatpak_match.group(1)

        # 8. Diagnostics
        self.assertTrue(DIAGNOSTICS_PY.is_file())
        diag_text = DIAGNOSTICS_PY.read_text(encoding="utf-8")
        diag_match = re.search(r'VERSION\s*=\s*"([^"]+)"', diag_text)
        self.assertIsNotNone(diag_match, "Could not find VERSION in diagnostics.py")
        diag_version = diag_match.group(1)

        # 9. Resonance
        self.assertTrue(RESONANCE_PY.is_file())
        res_text = RESONANCE_PY.read_text(encoding="utf-8")
        res_match = re.search(r'VERSION\s*=\s*"([^"]+)"', res_text)
        self.assertIsNotNone(res_match, "Could not find VERSION in resonance.py")
        res_version = res_match.group(1)

        # 10. Studio Hub
        self.assertTrue(STUDIO_HUB_PY.is_file())
        hub_text = STUDIO_HUB_PY.read_text(encoding="utf-8")
        hub_match = re.search(r'HUB_VERSION\s*=\s*"([^"]+)"', hub_text)
        self.assertIsNotNone(hub_match, "Could not find HUB_VERSION in studio_hub.py")
        hub_version = hub_match.group(1)

        # Assert all 10 versions match exactly
        expected_version = "4.2.1"
        for label, ver in [
            ("Bash arcanum", bash_version),
            ("Python CLI", py_version),
            ("Debian changelog", deb_version),
            ("CHANGELOG.md", cl_version),
            ("Arch PKGBUILD", arch_version),
            ("RPM spec", rpm_version),
            ("Flatpak metainfo", flatpak_version),
            ("Diagnostics", diag_version),
            ("Resonance", res_version),
            ("Studio Hub", hub_version),
        ]:
            self.assertEqual(
                ver,
                expected_version,
                f"{label} version ({ver}) does not match expected standardized version ({expected_version})"
            )


if __name__ == "__main__":
    unittest.main()
