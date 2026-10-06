#!/usr/bin/env python3
"""
Unit and Integration Tests for Ars Arcanum Local Vault Search Engine
(tests/test_vault_search.py)
"""

import io
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.lib.vault_search import (
    IndexedChunk,
    VaultSearchEngine,
    find_default_corpus_database,
    format_markdown_report,
    generate_html_retrieval_viewer,
    main as search_main,
    synthesize_llm_context,
    tokenize,
)


class TestLocalVaultSearch(unittest.TestCase):
    """Validates vector space retrieval, hybrid scoring, and context synthesis."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

        # Create sample markdown vault for testing
        self.vault_dir = self.root / "World_Vault"
        self.vault_dir.mkdir(parents=True, exist_ok=True)

        # Document 1: Character (Valerius)
        char_file = self.vault_dir / "Valerius.md"
        char_file.write_text(
            "---\n"
            "name: Archon Valerius\n"
            "type: Character\n"
            "category: Characters\n"
            "aliases: [The Dawnstrider]\n"
            "---\n"
            "# Archon Valerius\n\n"
            "Valerius is the High Archon of the Sunfire Citadel. He wields the legendary blade [[Dawnstrider]].\n"
            "During the Battle of the Crimson Rift, Valerius channeled radiant solar energy to seal the void.\n",
            encoding="utf-8",
        )

        # Document 2: Location (Sunfire Citadel)
        loc_file = self.vault_dir / "Sunfire_Citadel.md"
        loc_file.write_text(
            "---\n"
            "name: Sunfire Citadel\n"
            "type: Location\n"
            "category: Locations\n"
            "---\n"
            "# Sunfire Citadel\n\n"
            "The Sunfire Citadel is an ancient fortress constructed atop the Solar Spire.\n"
            "It houses the High Archon and the Council of Radiance. The citadel was besieged during the Void Incursion.\n",
            encoding="utf-8",
        )

        # Document 3: Magic System (Aether Resonance)
        magic_file = self.vault_dir / "Aether_Resonance.md"
        magic_file.write_text(
            "---\n"
            "name: Aether Resonance\n"
            "type: MagicSystem\n"
            "category: MagicSystems\n"
            "---\n"
            "# Aether Resonance\n\n"
            "Aether resonance requires harmonic alignment between the caster's soulstone and the atmospheric leylines.\n"
            "Overchanneling causes crystal calcification of the blood vessels.\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_tokenization_and_stopwords(self) -> None:
        """Verifies text tokenization, lowercase conversion, and stopword stripping."""
        text = "The High Archon wields Dawnstrider in the Sunfire Citadel!"
        tokens = tokenize(text, remove_stopwords=True)
        self.assertIn("high", tokens)
        self.assertIn("archon", tokens)
        self.assertIn("wields", tokens)
        self.assertIn("dawnstrider", tokens)
        self.assertIn("sunfire", tokens)
        self.assertIn("citadel", tokens)
        self.assertNotIn("the", tokens)
        self.assertNotIn("in", tokens)

    def test_in_memory_directory_indexing_and_query(self) -> None:
        """Verifies directory ingestion and cosine similarity vector retrieval."""
        engine = VaultSearchEngine()
        loaded = engine.load_from_directory(self.vault_dir)
        self.assertEqual(loaded, 3)
        self.assertEqual(engine.total_chunks, 3)

        results = engine.query("Dawnstrider Valerius", top_k=2)
        self.assertGreater(len(results), 0)
        top = results[0]
        self.assertEqual(top.chunk.doc_title, "Archon Valerius")
        self.assertIn("Dawnstrider", top.chunk.entities)
        self.assertGreater(top.score, 0.1)

    def test_sqlite_fts5_and_vector_hybrid_query(self) -> None:
        """Verifies querying an exported SQLite corpus database with hybrid FTS5."""
        db_path = self.root / "corpus.db"
        conn = sqlite3.connect(str(db_path))
        c = conn.cursor()

        c.execute("""
        CREATE TABLE documents (
            id TEXT PRIMARY KEY,
            corpus_type TEXT,
            category TEXT,
            title TEXT,
            path TEXT,
            word_count INTEGER,
            checksum TEXT,
            mtime REAL
        )
        """)

        c.execute("""
        CREATE TABLE chunks (
            id TEXT PRIMARY KEY,
            doc_id TEXT,
            chunk_index INTEGER,
            heading TEXT,
            text TEXT,
            word_count INTEGER,
            token_count_est INTEGER,
            entities_json TEXT
        )
        """)

        c.execute("""
        CREATE VIRTUAL TABLE chunks_fts USING fts5(
            id UNINDEXED,
            doc_id UNINDEXED,
            heading,
            text
        )
        """)

        doc1 = ("doc_valerius", "lore", "Characters", "Archon Valerius", "Characters/Valerius.md", 30, "chk1", 100.0)
        c.execute("INSERT INTO documents VALUES (?, ?, ?, ?, ?, ?, ?, ?)", doc1)

        chunk1 = (
            "doc_valerius_0",
            "doc_valerius",
            0,
            "Overview",
            "Valerius wields the legendary solar blade Dawnstrider in the Sunfire Citadel.",
            15,
            20,
            json.dumps(["Valerius", "Dawnstrider"]),
        )
        c.execute("INSERT INTO chunks VALUES (?, ?, ?, ?, ?, ?, ?, ?)", chunk1)
        c.execute("INSERT INTO chunks_fts VALUES (?, ?, ?, ?)", ("doc_valerius_0", "doc_valerius", "Overview", chunk1[4]))

        conn.commit()
        conn.close()

        engine = VaultSearchEngine()
        loaded = engine.load_from_sqlite(db_path)
        self.assertEqual(loaded, 1)

        results = engine.query("Dawnstrider", hybrid_fts=True)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].chunk.doc_title, "Archon Valerius")
        self.assertGreater(results[0].score_breakdown["cosine_similarity"], 0.0)
        self.assertGreater(results[0].score_breakdown["fts_score"], 0.0)

    def test_jsonl_dataset_loading(self) -> None:
        """Verifies ingestion of JSON Lines datasets."""
        chunks_file = self.root / "chunks.jsonl"
        docs_file = self.root / "documents.jsonl"

        with docs_file.open("w", encoding="utf-8") as f:
            f.write(json.dumps({"id": "d1", "title": "Citadel History", "corpus_type": "lore", "category": "Lore"}) + "\n")

        with chunks_file.open("w", encoding="utf-8") as f:
            f.write(json.dumps({
                "id": "c1",
                "doc_id": "d1",
                "heading": "Siege of Radiance",
                "text": "The Sunfire Citadel withstood forty days of siege by the shadow armies.",
                "word_count": 12,
                "token_count_est": 16,
                "entities": ["Sunfire Citadel"],
            }) + "\n")

        engine = VaultSearchEngine()
        loaded = engine.load_from_jsonl(chunks_file, docs_file)
        self.assertEqual(loaded, 1)

        res = engine.query("shadow armies siege")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].chunk.heading, "Siege of Radiance")

    def test_query_expansion_and_bm25_plus(self) -> None:
        """Verifies co-occurrence query expansion and BM25+ computation."""
        engine = VaultSearchEngine()
        engine.load_from_directory(self.vault_dir)

        tokens = ["valerius"]
        expanded = engine.expand_query(tokens, max_expansions=2)
        self.assertIn("valerius", expanded)

        # Check BM25+ scoring directly
        chunk = next(c for c in engine.chunks if "valerius" in c.text.lower())
        bm25_score = engine.compute_bm25_plus(["valerius"], chunk)
        self.assertGreater(bm25_score, 0.0)

    def test_context_and_report_synthesizers(self) -> None:
        """Verifies LLM prompt synthesis and Markdown/HTML generation."""
        engine = VaultSearchEngine()
        engine.load_from_directory(self.vault_dir)
        results = engine.query("Dawnstrider solar energy", top_k=2)

        prompt_ctx = synthesize_llm_context("Who is Valerius?", results)
        self.assertIn("<system_instructions>", prompt_ctx)
        self.assertIn("<canonical_lore_context>", prompt_ctx)
        self.assertIn("<user_query>", prompt_ctx)
        self.assertIn("Who is Valerius?", prompt_ctx)
        self.assertIn("Archon Valerius", prompt_ctx)

        empty_ctx = synthesize_llm_context("Unknown inquiry", [])
        self.assertIn("No canonical lore records matched the inquiry.", empty_ctx)

    def test_markdown_and_html_exporters(self) -> None:
        """Verifies Markdown and offline HTML export helpers."""
        chunk = IndexedChunk(
            id="test_1",
            doc_id="doc_1",
            doc_title="Archon Valerius",
            corpus_type="lore",
            category="Characters",
            doc_path="Characters/Valerius.md",
            heading="Solar Blade",
            text="Valerius forged Dawnstrider in the core of the star.",
            word_count=10,
            token_count_est=13,
            entities=["Valerius", "Dawnstrider"],
        )
        res = VaultSearchEngine()
        res.chunks = [chunk]
        res._build_vector_index()
        results = res.query("Dawnstrider")

        # Markdown
        md = format_markdown_report("Dawnstrider", results)
        self.assertIn("# Ars Arcanum Vault Search Report", md)
        self.assertIn("Archon Valerius", md)

        # HTML
        html_view = generate_html_retrieval_viewer("Dawnstrider", results)
        self.assertIn("<!DOCTYPE html>", html_view)
        self.assertIn("Content-Security-Policy", html_view)
        self.assertIn("default-src 'none'", html_view)
        self.assertIn("Archon Valerius", html_view)

    def test_cli_execution(self) -> None:
        """Verifies CLI execution with various output formats."""
        out_json = self.root / "result.json"
        code = search_main([
            "Valerius solar blade",
            "-t", str(self.vault_dir),
            "-f", "json",
            "-o", str(out_json),
        ])
        self.assertEqual(code, 0)
        self.assertTrue(out_json.is_file())

        with out_json.open("r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("query", data)
        self.assertIn("results", data)
        self.assertGreater(len(data["results"]), 0)

    def test_cli_stdout_and_errors(self) -> None:
        with patch("sys.stderr", new_callable=io.StringIO):
            code_no_q = search_main([])
            self.assertEqual(code_no_q, 2)

        with patch("sys.stderr", new_callable=io.StringIO) as mock_err:
            code_bad_t = search_main(["Valerius", "-t", str(self.root / "missing_dir")])
            self.assertEqual(code_bad_t, 1)
            self.assertIn("Target path", mock_err.getvalue())

        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            code_ctx = search_main(["Valerius", "-t", str(self.vault_dir), "-f", "context"])
            self.assertEqual(code_ctx, 0)
            self.assertIn("<canonical_lore_context>", mock_out.getvalue())

    def test_empty_vault_and_no_match_query(self) -> None:
        """Verifies handling of empty directory indexing and queries with 0 matches."""
        empty_dir = self.root / "Empty_Vault"
        empty_dir.mkdir(parents=True, exist_ok=True)

        engine = VaultSearchEngine()
        count = engine.load_from_directory(empty_dir)
        self.assertEqual(count, 0)
        self.assertEqual(engine.total_chunks, 0)

        results = engine.query("Nonexistent query about dragons")
        self.assertEqual(len(results), 0)

    def test_min_score_threshold_and_top_k(self) -> None:
        """Verifies top_k limiting and score bounds."""
        engine = VaultSearchEngine()
        engine.load_from_directory(self.vault_dir)

        top_1 = engine.query("Valerius citadel", top_k=1)
        self.assertEqual(len(top_1), 1)

        top_all = engine.query("Valerius citadel aether", top_k=10)
        self.assertLessEqual(len(top_all), 3)

    def test_tokenization_special_cases(self) -> None:
        """Verifies edge cases for tokenizer: empty strings, numbers, symbols."""
        self.assertEqual(tokenize(""), [])
        self.assertEqual(tokenize("   "), [])
        self.assertEqual(tokenize("123 4567 89"), [])
        self.assertEqual(tokenize("!@#$%^&*()"), [])
        toks = tokenize("knight-commander's sword", remove_stopwords=False)
        self.assertTrue(any("knight" in t for t in toks))

    def test_cli_markdown_and_html_output(self) -> None:
        """Verifies CLI execution producing markdown and HTML outputs."""
        out_md = self.root / "report.md"
        out_html = self.root / "report.html"

        code_md = search_main([
            "Aether leylines",
            "-t", str(self.vault_dir),
            "-f", "markdown",
            "-o", str(out_md),
        ])
        self.assertEqual(code_md, 0)
        self.assertTrue(out_md.is_file())
        self.assertIn("Aether Resonance", out_md.read_text(encoding="utf-8"))

        code_html = search_main([
            "Aether leylines",
            "-t", str(self.vault_dir),
            "-f", "html",
            "-o", str(out_html),
        ])
        self.assertEqual(code_html, 0)
        self.assertTrue(out_html.is_file())
        self.assertIn("Content-Security-Policy", out_html.read_text(encoding="utf-8"))

    def test_find_default_corpus_database(self) -> None:
        res = find_default_corpus_database()
        self.assertTrue(res is None or isinstance(res, Path))


if __name__ == "__main__":
    unittest.main()
