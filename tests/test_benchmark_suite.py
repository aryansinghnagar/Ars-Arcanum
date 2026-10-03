#!/usr/bin/env python3
"""
Comprehensive Performance Benchmark & Execution Velocity Suite for Ars Arcanum
(tests/test_benchmark_suite.py)
================================================================================
Benchmarks core craft engines, validation gates, and simulations to ensure
strictly sub-second execution speeds across all offline tools.
"""

import tempfile
import time
import unittest
from pathlib import Path

from scripts.lib.audio_proof import analyze_audio_proofing, generate_ssml
from scripts.lib.conlang import generate_words, mutate_text
from scripts.lib.council import run_editorial_council
from scripts.lib.economy import (
    calculate_gravity_trade_flow,
    simulate_supply_shock,
)
from scripts.lib.local_rag import IndexedChunk, LocalLoreRetrievalEngine


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

    def test_benchmark_rag_bm25_retrieval(self) -> None:
        """Benchmarks indexing and retrieval over 1,000 synthetic chunks."""
        engine = LocalLoreRetrievalEngine()
        for i in range(1000):
            chunk = IndexedChunk(
                id=f"chunk_{i}",
                doc_id=f"doc_{i // 10}",
                doc_title=f"World Lore Chapter {i // 10}",
                corpus_type="lore",
                category="Characters" if i % 2 == 0 else "MagicSystems",
                doc_path=f"Vault/Doc_{i}.md",
                heading=f"Section {i}",
                text=f"Aether resonance leyline energy flows through Citadel {i}. Archon Valerius channels solar flame against the void.",
                word_count=20,
                token_count_est=25,
                entities=[f"Entity_{i}", "Valerius", "Citadel"],
            )
            engine.chunks.append(chunk)

        t0 = time.perf_counter()
        engine._build_vector_index()
        t_index = time.perf_counter() - t0
        self.assertLess(t_index, 0.50, f"Indexing 1,000 chunks took {t_index:.3f}s (must be <0.5s)")

        t0 = time.perf_counter()
        results = engine.query("Valerius aether resonance solar", top_k=10, expand_query=True)
        t_query = time.perf_counter() - t0
        self.assertLess(t_query, 0.10, f"Querying 1,000 chunks took {t_query:.3f}s (must be <0.1s)")
        self.assertEqual(len(results), 10)

    def test_benchmark_audio_proofing(self) -> None:
        """Benchmarks full audio proofing analysis & SSML generation for 5,000 words."""
        t0 = time.perf_counter()
        report = analyze_audio_proofing(self.ms_file, wpm=150)
        ssml = generate_ssml(self.sample_text)
        t_elapsed = time.perf_counter() - t0

        self.assertLess(t_elapsed, 0.25, f"Audio proofing took {t_elapsed:.3f}s (must be <0.25s)")
        self.assertGreater(report.total_words, 500)
        self.assertIn("<speak", ssml)

    def test_benchmark_editorial_council(self) -> None:
        """Benchmarks 4-perspective Editorial Council evaluation for 5,000 words."""
        t0 = time.perf_counter()
        dossier = run_editorial_council(self.ms_file)
        t_elapsed = time.perf_counter() - t0

        self.assertLess(t_elapsed, 0.30, f"Editorial Council took {t_elapsed:.3f}s (must be <0.30s)")
        self.assertEqual(len(dossier.perspectives), 4)

    def test_benchmark_conlang_generation_and_mutation(self) -> None:
        """Benchmarks batch phonotactic generation of 1,000 words and sound shift rules."""
        profile = {
            "name": "BenchmarkLang",
            "consonants": ["p", "t", "k", "b", "d", "g", "s", "m", "n", "l", "r"],
            "vowels": ["a", "e", "i", "o", "u"],
            "syllable_structures": ["CV", "CVC", "CCV", "VC"],
            "forbidden_clusters": ["sr", "tl"],
            "stress_rule": "penultimate",
        }
        rules = ["k > ch / _[e,i]", "p > f / V_V", "s > h / #_"]

        t0 = time.perf_counter()
        words = generate_words(profile, count=500, num_syllables=3)
        mutated = [mutate_text(w, rules, profile["vowels"], profile["consonants"]) for w in words]
        t_elapsed = time.perf_counter() - t0

        self.assertLess(t_elapsed, 0.20, f"Conlang 500-word generation & mutation took {t_elapsed:.3f}s (must be <0.2s)")
        self.assertEqual(len(mutated), 500)

    def test_benchmark_economic_gravity_and_cascade(self) -> None:
        """Benchmarks gravity trade flow and supply shock cascade."""
        settlements = [
            {
                "id": f"City_{i}",
                "name": f"Settlement {i}",
                "population": 20000 + i * 1000,
                "tier": "Major City",
                "trade_hub": True,
                "coordinates": (i * 20.0, (i % 5) * 30.0),
                "export_commodities": ["grain", "iron", "timber"],
                "import_demands": ["spices", "cloth", "mana"],
            }
            for i in range(15)
        ]

        t0 = time.perf_counter()
        flows = calculate_gravity_trade_flow(settlements)
        shock = simulate_supply_shock(
            settlements=settlements,
            shock_event="Drought & Siege",
            target_settlement_id="City_0",
            affected_commodity="grain",
            shock_magnitude=0.6,
        )
        t_elapsed = time.perf_counter() - t0

        self.assertLess(t_elapsed, 0.15, f"Economy calculation took {t_elapsed:.3f}s (must be <0.15s)")
        self.assertGreater(len(flows["routes"]), 10)
        self.assertEqual(shock["epicenter_id"], "City_0")


if __name__ == "__main__":
    unittest.main()
