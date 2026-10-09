#!/usr/bin/env python3
"""
Comprehensive Performance Benchmark & Execution Velocity Suite for Ars Arcanum
(tests/test_benchmark_suite.py)
================================================================================
Benchmarks core craft engines, validation gates, and publishing tools to ensure
strictly sub-second execution speeds across all sovereign offline tools.
"""

import tempfile
import time
import unittest
from pathlib import Path

from scripts.lib.codex_export import build_single_file_codex, scan_world_vault
from scripts.lib.data_access import get_data_access
from scripts.lib.manuscript_diff import compute_word_diff, tokenize_words
from scripts.lib.preflight import run_preflight_linter
from scripts.lib.revision_heatmap import diff_line_counts


class TestBenchmarkSuite(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

        # 5,000 word synthetic manuscript
        scene_paragraphs = []
        for i in range(25):
            scene_paragraphs.append(f"## Scene {i+1}\n\nDawn broke over the high parapets of Citadel {i}. Elena drew her runic sword and shouted, 'Hold the gates!' The sound of thunder echoed through the valley.\n\nMarcus nodded grimly. 'If the leylines collapse, all is lost.'\n")
        self.sample_text = "\n\n---\n\n".join(scene_paragraphs)
        self.ms_file = self.root / "benchmark_ms.md"
        self.ms_file.write_text(self.sample_text, encoding="utf-8")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_benchmark_manuscript_diff(self) -> None:
        """Benchmarks tokenization and word-level diffing over 10,000 words."""
        text_a = self.sample_text * 2
        text_b = text_a.replace("Elena", "Aurelia").replace("Citadel", "Fortress")

        t0 = time.perf_counter()
        tokens_a = tokenize_words(text_a)
        tokens_b = tokenize_words(text_b)
        _chunks, added, deleted = compute_word_diff(tokens_a, tokens_b)
        t_elapsed = time.perf_counter() - t0

        self.assertLess(t_elapsed, 0.50, f"Diffing 10k words took {t_elapsed:.3f}s (must be <0.5s)")
        self.assertGreater(added, 0)
        self.assertGreater(deleted, 0)

    def test_benchmark_revision_heatmap(self) -> None:
        """Benchmarks revision churn computation over multiple chapters."""
        text_old = self.sample_text
        text_new = self.sample_text.replace("Elena", "Aurelia").replace("thunder", "lightning")

        t0 = time.perf_counter()
        for _ in range(50):
            diff_line_counts(text_new, text_old)
        t_elapsed = time.perf_counter() - t0

        self.assertLess(t_elapsed, 0.50, f"50 chapter churn calculations took {t_elapsed:.3f}s (must be <0.5s)")

    def test_benchmark_preflight_linter(self) -> None:
        """Benchmarks preflight typesetting & publishing validation."""
        ms_dir = self.root / "Manuscript"
        ms_dir.mkdir(parents=True, exist_ok=True)
        (ms_dir / "manuscript.yaml").write_text("title: Benchmark\nauthor: Tester\nlanguage: en\n", encoding="utf-8")

        for i in range(20):
            (ms_dir / f"ch_{i:02d}.md").write_text(f"# Chapter {i}\n\n" + self.sample_text, encoding="utf-8")

        t0 = time.perf_counter()
        report = run_preflight_linter(ms_dir)
        t_elapsed = time.perf_counter() - t0

        self.assertLess(t_elapsed, 0.75, f"Preflight validation of 20 chapters took {t_elapsed:.3f}s (must be <0.75s)")
        self.assertEqual(report["chapter_count"], 20)

    def test_benchmark_codex_export(self) -> None:
        """Benchmarks static wiki codex building across 100 lore notes."""
        world_dir = self.root / "World"
        world_dir.mkdir(parents=True, exist_ok=True)

        for i in range(100):
            cat = "Characters" if i % 2 == 0 else "Locations"
            (world_dir / f"entity_{i}.md").write_text(
                f"---\nname: Entity {i}\ncategory: {cat}\n---\n# Entity {i}\nLore description with [[entity_{max(0, i-1)}]].\n",
                encoding="utf-8"
            )

        t0 = time.perf_counter()
        cats = scan_world_vault(world_dir)
        out_html = self.root / "codex.html"
        build_single_file_codex(cats, world_name="BenchmarkWorld", output_path=out_html)
        t_elapsed = time.perf_counter() - t0

        self.assertLess(t_elapsed, 0.40, f"Codex compilation of 100 notes took {t_elapsed:.3f}s (must be <0.4s)")
        self.assertTrue(out_html.is_file())

    def test_benchmark_data_access_caching(self) -> None:
        """Benchmarks cached DataAccessLayer read performance."""
        dal = get_data_access()
        dal.clear()

        world_dir = self.root / "World"
        t0 = time.perf_counter()
        entities1 = dal.get_lore_entities(world_dir)
        _t_first = time.perf_counter() - t0

        t0 = time.perf_counter()
        entities2 = dal.get_lore_entities(world_dir)
        t_cached = time.perf_counter() - t0

        self.assertEqual(len(entities1), len(entities2))
        self.assertLess(t_cached, 0.05, f"Cached retrieval took {t_cached:.3f}s (must be <0.05s)")


if __name__ == "__main__":
    unittest.main()

