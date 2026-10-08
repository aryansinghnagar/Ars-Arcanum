#!/usr/bin/env python3
"""
Test Suite: Sovereign Agentic Operating System Doctrine & Contracts
(tests/test_agentic_doctrine.py)
================================================================================
Validates AGENTS.md contract declarations, momentum queue definitions, and
engineering invariants across repository task specifications.
"""

import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestAgenticDoctrine(unittest.TestCase):
    def setUp(self):
        self.agents_md = PROJECT_ROOT / "AGENTS.md"
        self.roadmap_md = (
            PROJECT_ROOT / "docs" / "ROADMAP.md"
            if (PROJECT_ROOT / "docs" / "ROADMAP.md").exists()
            else PROJECT_ROOT / "ROADMAP.md"
        )

    def test_agents_manifesto_exists(self):
        self.assertTrue(self.agents_md.exists(), "Missing AGENTS.md manifesto file")
        content = self.agents_md.read_text(encoding="utf-8")

        # Invariant contracts
        self.assertIn("Atomic Writes", content)
        self.assertIn("Cross-Platform File Locking", content)
        self.assertIn("Path Traversal Defense", content)
        self.assertIn("Zero-Pip Dependency Guarantee", content)
        self.assertIn("Content-Security-Policy", content)

        # 5 Momentum Queues
        self.assertIn("`now`", content)
        self.assertIn("`next`", content)
        self.assertIn("`blocked`", content)
        self.assertIn("`improve`", content)
        self.assertIn("`recurring`", content)

    def test_roadmap_momentum_queues_aligned(self):
        self.assertTrue(self.roadmap_md.exists(), "Missing ROADMAP.md file")
        content = self.roadmap_md.read_text(encoding="utf-8")

        self.assertIn("### `now`", content)
        self.assertIn("### `next`", content)
        self.assertIn("### `blocked`", content)
        self.assertIn("### `improve`", content)
        self.assertIn("### `recurring`", content)


if __name__ == "__main__":
    unittest.main()
