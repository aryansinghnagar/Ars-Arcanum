#!/usr/bin/env python3
"""
Performance & Benchmark Regression Suite for Ars Arcanum Cache & Parsers
(tests/test_cache_benchmarks.py)
========================================================================
Validates:
1. Tag extraction throughput (>1,000 files/sec).
2. Word count tokenizer velocity.
3. Multi-file vault indexing performance.
4. Sub-millisecond incremental cache hit resolution.
"""

import sys
import time
import tempfile
import unittest
from pathlib import Path

# Add scripts directory to path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.cache import (
    compute_wordcounts,
    count_words,
    extract_tags,
    scan_project,
)


class TestCacheBenchmarks(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_single_pass_tag_extraction_throughput(self):
        """Measures throughput of single-pass extract_tags on typical manuscript scene metadata."""
        sample_scene = """---
title: "The Midnight Garrison"
status: Revision
---
# Act II Scene 3

@pov: Renée d'Anjou
@chars: Renée, Julian Vance, Commander Gary
@location: High Bastion of Solaris
@thread: Citadel Siege
@status: Draft
@time: 1420-08-15
@plot: Main Arc

Renée stood atop the [[High Bastion|Bastion]], gazing down upon the army below.
Julian approached with a map in hand. "The siege begins at dawn," he whispered.

```notes
Hidden author notes that should not count as prose.
```

The wind blew fiercely across the stone walls of [[Solaris]].
"""
        iterations = 5000
        start = time.perf_counter()
        for _ in range(iterations):
            tags = extract_tags(sample_scene)
        elapsed = time.perf_counter() - start

        self.assertIn("pov", tags)
        self.assertEqual(tags["pov"], ["Renée d'Anjou"])
        self.assertEqual(tags["location"], ["High Bastion of Solaris"])
        self.assertEqual(tags["characters"], ["Renée, Julian Vance, Commander Gary"])

        ops_per_sec = iterations / elapsed
        self.assertGreater(ops_per_sec, 2000, f"Tag extraction too slow: {ops_per_sec:.0f} ops/sec")

    def test_word_count_velocity(self):
        """Verifies word count computation velocity on substantial text."""
        paragraph = "The ancient tower stood against the howling wind as the stars glittered above the dark forest. " * 50
        iterations = 1000
        start = time.perf_counter()
        for _ in range(iterations):
            wc = count_words(paragraph)
        elapsed = time.perf_counter() - start

        self.assertGreater(wc, 500)
        words_per_sec = (wc * iterations) / elapsed
        self.assertGreater(words_per_sec, 500_000, f"Word counter too slow: {words_per_sec:.0f} words/sec")

    def test_multi_file_vault_indexing_and_cache_hits(self):
        """Tests initial cold cache scan vs warm cache hit on a synthetic 100-file project."""
        # Create 100 markdown files across 5 chapters
        for ch in range(1, 6):
            ch_dir = self.project_dir / f"Chapter_{ch:02d}"
            ch_dir.mkdir(parents=True, exist_ok=True)
            for sc in range(1, 21):
                file_path = ch_dir / f"Scene_{sc:02d}.md"
                content = f"""---
chapter: {ch}
scene: {sc}
---
# Chapter {ch} Scene {sc}
@pov: Character_{ch}
@location: Location_{sc}
@thread: Arc_{ch % 3}

This is scene {sc} of chapter {ch}. The journey continues across [[Location_{sc}]].
"""
                file_path.write_text(content, encoding="utf-8")

        # 1. Cold Scan
        cold_cache = scan_project(str(self.project_dir), force=True)
        self.assertEqual(len(cold_cache["files"]), 100)
        self.assertTrue(cold_cache.get("healthy", False))

        # 2. Warm Cache Hit Scan (no files modified)
        start_warm = time.perf_counter()
        warm_cache = scan_project(str(self.project_dir), force=False)
        warm_time = time.perf_counter() - start_warm

        self.assertEqual(len(warm_cache["files"]), 100)
        # Warm hit should be sub-second
        self.assertLess(warm_time, 0.5, f"Warm cache hit too slow: {warm_time:.4f}s")

        # 3. Incremental Update (modify 1 file)
        target_file = self.project_dir / "Chapter_01" / "Scene_01.md"
        time.sleep(0.02)  # ensure distinct mtime
        target_file.write_text(target_file.read_text(encoding="utf-8") + "\nExtra prose appended here.", encoding="utf-8")

        start_incr = time.perf_counter()
        incr_cache = scan_project(str(self.project_dir), force=False)
        incr_time = time.perf_counter() - start_incr

        self.assertLess(incr_time, 0.5, f"Incremental cache update too slow: {incr_time:.4f}s")
        self.assertGreater(incr_cache["files"]["Chapter_01/Scene_01.md"]["word_count"], cold_cache["files"]["Chapter_01/Scene_01.md"]["word_count"])

        # 4. Aggregated Wordcounts
        wc_report = compute_wordcounts(str(self.project_dir))
        self.assertEqual(wc_report["total_files"], 100)
        self.assertGreater(wc_report["total_words"], 1000)


if __name__ == "__main__":
    unittest.main()
