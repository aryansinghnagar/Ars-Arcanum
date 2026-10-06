#!/usr/bin/env python3
"""
Ars Arcanum Sovereign Zero-Dependency Local Vault Search & Lore Engine
(scripts/lib/vault_search.py)
================================================================================
Zero-dependency, 100% offline hybrid mathematical search engine powering natural
language lore queries, multi-volume continuity recall, and prompt synthesis
without external vector databases or neural networks.

Mathematical Core:
1. Vector Space Model (VSM):
   - Sub-linear Term Frequency: TF(t, d) = 1.0 + ln(count(t, d)) if count > 0 else 0
   - Smoothed Inverse Document Frequency: IDF(t) = ln(1.0 + (N - df(t) + 0.5) / (df(t) + 0.5)) + 1.0
   - L2-Normalized Cosine Similarity: CosSim(q, d) = (v_q . v_d) / (||v_q|| * ||v_d||)
2. Hybrid SQLite FTS5 & Entity Fusion:
   - Combines vector space cosine angle with exact FTS5 BM25 keyword relevance.
   - Boosts chunks with matching named entities, wikilinks, and section headers.
3. Injection-Safe Context Prompt Synthesizer:
   - Formats top-k retrieved lore chunks into structured reference blocks with
     strict provenance attribution, category tagging, and word/token estimates.

Zero external dependencies; 100% offline privacy.
"""

from __future__ import annotations

import argparse
import json
import logging
import math
import os
import re
import sqlite3
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    from lib._bootstrap import PROJECT_ROOT, atomic_write
    from lib.corpus_export import CorpusDocument, CorpusScanner
    from lib.scope import (
        EngineScope,
        add_scope_arguments,
        parse_scope_args,
        resolve_manuscript_path,
        resolve_universe_path,
        resolve_world_path,
    )
    from lib.vault_search_template import (
        format_markdown_report,
        generate_html_retrieval_viewer,
        synthesize_llm_context,
    )
except ImportError:
    try:
        from _bootstrap import PROJECT_ROOT, atomic_write
        from corpus_export import CorpusDocument, CorpusScanner
        from scope import (
            EngineScope,
            add_scope_arguments,
            parse_scope_args,
            resolve_manuscript_path,
            resolve_universe_path,
            resolve_world_path,
        )
        from vault_search_template import (  # type: ignore[no-redef]
            format_markdown_report,
            generate_html_retrieval_viewer,
            synthesize_llm_context,
        )
    except ImportError:
        PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

        def atomic_write(path: Path, content: str, encoding: str = "utf-8") -> None:
            import tempfile as _tf
            p = Path(path).resolve()
            p.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp = _tf.mkstemp(dir=p.parent, prefix=f".{p.name}.", suffix=".tmp")
            try:
                with os.fdopen(fd, "w", encoding=encoding, newline="") as f:
                    f.write(content)
                    f.flush()
                    os.fsync(f.fileno())
                os.replace(tmp, p)
            except BaseException:
                try:
                    Path(tmp).unlink(missing_ok=True)
                except OSError:
                    pass
                raise

        CorpusDocument = None  # type: ignore
        CorpusScanner = None  # type: ignore
        EngineScope = None  # type: ignore

        def add_scope_arguments(*args: Any, **kwargs: Any) -> None:  # type: ignore
            pass

        def parse_scope_args(*args: Any, **kwargs: Any) -> Any:  # type: ignore
            return None

        def resolve_manuscript_path(*args: Any, **kwargs: Any) -> Any:  # type: ignore
            return None

        def resolve_world_path(*args: Any, **kwargs: Any) -> Any:  # type: ignore
            return None

        def resolve_universe_path(*args: Any, **kwargs: Any) -> Any:  # type: ignore
            return None

logger = logging.getLogger("arcanum.vault_search")

# Standard English Stopwords (Curated for craft and narrative retrieval)
STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i",
    "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's",
    "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
    "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
    "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves",
    "then", "there", "there's", "these", "they", "they'd", "they'll", "they're",
    "they've", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves"
}

TOKEN_PATTERN = re.compile(r"\b[a-zA-Z0-9_\-']+\b")


def tokenize(text: str, remove_stopwords: bool = True) -> list[str]:
    """Extract normalized alphanumeric tokens from text."""
    if not text:
        return []
    tokens = [m.group(0).lower().strip("-_'") for m in TOKEN_PATTERN.finditer(text)]
    tokens = [t for t in tokens if len(t) > 1 and not t.isdigit()]
    if remove_stopwords:
        tokens = [t for t in tokens if t not in STOPWORDS]
    return tokens


@dataclass
class IndexedChunk:
    """Represents an in-memory or database chunk prepared for vector scoring."""
    id: str
    doc_id: str
    doc_title: str
    corpus_type: str
    category: str
    doc_path: str
    heading: str
    text: str
    word_count: int
    token_count_est: int
    entities: list[str] = field(default_factory=list)
    term_counts: dict[str, int] = field(default_factory=dict)
    vector_norm: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "doc_id": self.doc_id,
            "doc_title": self.doc_title,
            "corpus_type": self.corpus_type,
            "category": self.category,
            "doc_path": self.doc_path,
            "heading": self.heading,
            "text": self.text,
            "word_count": self.word_count,
            "token_count_est": self.token_count_est,
            "entities": self.entities,
        }


@dataclass
class RetrievalResult:
    """Represents a scored and attributed retrieval result."""
    chunk: IndexedChunk
    score: float
    score_breakdown: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk.id,
            "doc_id": self.chunk.doc_id,
            "doc_title": self.chunk.doc_title,
            "corpus_type": self.chunk.corpus_type,
            "category": self.chunk.category,
            "doc_path": self.chunk.doc_path,
            "heading": self.chunk.heading,
            "text": self.chunk.text,
            "word_count": self.chunk.word_count,
            "token_count_est": self.chunk.token_count_est,
            "entities": self.chunk.entities,
            "score": round(self.score, 4),
            "score_breakdown": {k: round(v, 4) for k, v in self.score_breakdown.items()},
        }


class VaultSearchEngine:
    """
    Offline Vector Space & Hybrid Semantic Search Engine for Ars Arcanum.
    Ingests from SQLite corpus.db, JSONL datasets, or scans Markdown directories.
    """

    def __init__(self) -> None:
        self.chunks: list[IndexedChunk] = []
        self.doc_term_freqs: dict[str, int] = {}  # term -> count of chunks containing term
        self.idf_cache: dict[str, float] = {}
        self.sqlite_db_path: Path | None = None
        self._is_indexed: bool = False
        self.avg_doc_len: float = 150.0

    @property
    def total_chunks(self) -> int:
        return len(self.chunks)

    def load_from_sqlite(self, db_path: Path | str) -> int:
        """Loads and indexes chunks and documents from a corpus.db SQLite database."""
        path = Path(db_path).resolve()
        if not path.is_file():
            raise FileNotFoundError(f"Corpus database not found at '{path}'")

        self.sqlite_db_path = path
        conn = sqlite3.connect(str(path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = """
        SELECT
            c.id AS chunk_id,
            c.doc_id,
            c.chunk_index,
            c.heading,
            c.text,
            c.word_count,
            c.token_count_est,
            c.entities_json,
            d.corpus_type,
            d.category,
            d.title AS doc_title,
            d.path AS doc_path
        FROM chunks c
        JOIN documents d ON c.doc_id = d.id
        ORDER BY d.id, c.chunk_index
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        self.chunks = []

        for r in rows:
            entities = []
            if r["entities_json"]:
                try:
                    entities = json.loads(r["entities_json"])
                except Exception:
                    entities = []

            chunk = IndexedChunk(
                id=str(r["chunk_id"]),
                doc_id=str(r["doc_id"]),
                doc_title=str(r["doc_title"] or ""),
                corpus_type=str(r["corpus_type"] or "lore"),
                category=str(r["category"] or "General"),
                doc_path=str(r["doc_path"] or ""),
                heading=str(r["heading"] or ""),
                text=str(r["text"] or ""),
                word_count=int(r["word_count"] or 0),
                token_count_est=int(r["token_count_est"] or 0),
                entities=entities,
            )
            self.chunks.append(chunk)

        conn.close()
        self._build_vector_index()
        return len(self.chunks)

    def load_from_jsonl(self, chunks_jsonl: Path | str, docs_jsonl: Path | str | None = None) -> int:
        """Loads and indexes chunks from JSON Lines files."""
        c_path = Path(chunks_jsonl).resolve()
        if not c_path.is_file():
            raise FileNotFoundError(f"Chunks JSONL file not found at '{c_path}'")

        docs_map: dict[str, dict[str, Any]] = {}
        if docs_jsonl:
            d_path = Path(docs_jsonl).resolve()
            if d_path.is_file():
                with d_path.open("r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            d = json.loads(line)
                            docs_map[d.get("id", "")] = d

        self.chunks = []
        with c_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                c = json.loads(line)
                doc_id = c.get("doc_id", "")
                doc_meta = docs_map.get(doc_id, {})

                chunk = IndexedChunk(
                    id=str(c.get("id", "")),
                    doc_id=doc_id,
                    doc_title=str(doc_meta.get("title", doc_id)),
                    corpus_type=str(doc_meta.get("corpus_type", "lore")),
                    category=str(doc_meta.get("category", "General")),
                    doc_path=str(doc_meta.get("path", "")),
                    heading=str(c.get("heading", "")),
                    text=str(c.get("text", "")),
                    word_count=int(c.get("word_count", 0)),
                    token_count_est=int(c.get("token_count_est", 0)),
                    entities=list(c.get("entities", [])),
                )
                self.chunks.append(chunk)

        self._build_vector_index()
        return len(self.chunks)

    def load_from_directory(
        self,
        target_dir: Path | str,
        target_chunk_words: int = 250,
        scope: EngineScope | None = None,
    ) -> int:
        """Scans a directory of Markdown files in-memory using CorpusScanner."""
        if CorpusScanner is None:
            raise RuntimeError("CorpusScanner module is required to scan directory directly.")

        scanner = CorpusScanner(Path(target_dir), target_chunk_words=target_chunk_words, scope=scope)
        scanner.scan()

        self.chunks = []
        for doc in scanner.documents:
            for c in doc.chunks:
                chunk = IndexedChunk(
                    id=c.id,
                    doc_id=doc.id,
                    doc_title=doc.title,
                    corpus_type=doc.corpus_type,
                    category=doc.category,
                    doc_path=doc.path,
                    heading=c.heading,
                    text=c.text,
                    word_count=c.word_count,
                    token_count_est=c.token_count_est,
                    entities=list(c.entities),
                )
                self.chunks.append(chunk)

        self._build_vector_index()
        return len(self.chunks)

    def _build_vector_index(self) -> None:
        """Builds term frequency counters and IDF values for all loaded chunks."""
        self.doc_term_freqs = {}
        self.idf_cache = {}

        # 1. Compute term counts per chunk
        for chunk in self.chunks:
            full_text = f"{chunk.heading} {chunk.heading} {' '.join(chunk.entities)} {chunk.text}"
            tokens = tokenize(full_text)
            term_counts: dict[str, int] = {}
            for t in tokens:
                term_counts[t] = term_counts.get(t, 0) + 1
            chunk.term_counts = term_counts

            for t in term_counts:
                self.doc_term_freqs[t] = self.doc_term_freqs.get(t, 0) + 1

        n_chunks = len(self.chunks)
        if n_chunks == 0:
            self._is_indexed = True
            return

        # 2. Compute IDF per vocabulary term
        for term, df in self.doc_term_freqs.items():
            self.idf_cache[term] = math.log(1.0 + (n_chunks - df + 0.5) / (df + 0.5)) + 1.0

        # 3. Compute L2 vector norms for each chunk
        total_words = 0
        for chunk in self.chunks:
            norm_sq = 0.0
            doc_len = chunk.word_count if chunk.word_count > 0 else sum(chunk.term_counts.values())
            total_words += max(1, doc_len)
            for term, count in chunk.term_counts.items():
                idf = self.idf_cache.get(term, 1.0)
                w_tf = 1.0 + math.log(count)
                w = w_tf * idf
                norm_sq += w * w
            chunk.vector_norm = math.sqrt(norm_sq) if norm_sq > 0.0 else 1.0

        self.avg_doc_len = total_words / max(1, n_chunks)
        self._is_indexed = True

    def compute_bm25_plus(
        self,
        query_tokens: list[str],
        chunk: IndexedChunk,
        k1: float = 1.5,
        b: float = 0.75,
        delta: float = 0.5,
    ) -> float:
        """Calculates BM25+ relevance score for a document chunk given query tokens."""
        doc_len = max(1, chunk.word_count or sum(chunk.term_counts.values()))
        avg_len = getattr(self, "avg_doc_len", 150.0) or 150.0
        len_norm = 1.0 - b + b * (doc_len / avg_len)

        score = 0.0
        for q in query_tokens:
            tf = chunk.term_counts.get(q, 0)
            if tf > 0:
                idf = self.idf_cache.get(q, 1.0)
                tf_component = ((tf * (k1 + 1.0)) / (tf + k1 * len_norm)) + delta
                score += idf * tf_component
        return score

    def expand_query(self, query_tokens: list[str], max_expansions: int = 3) -> list[str]:
        """Deterministically expands query tokens using corpus co-occurrence analysis."""
        if not query_tokens or not self.chunks:
            return query_tokens

        query_set = set(query_tokens)
        co_occurrence: dict[str, int] = {}

        for chunk in self.chunks:
            if any(q in chunk.term_counts for q in query_set):
                for term, cnt in chunk.term_counts.items():
                    if term not in query_set and term not in STOPWORDS and len(term) > 2:
                        co_occurrence[term] = co_occurrence.get(term, 0) + cnt

        if not co_occurrence:
            return query_tokens

        candidates = sorted(
            co_occurrence.items(),
            key=lambda item: item[1] * self.idf_cache.get(item[0], 1.0),
            reverse=True,
        )
        expanded_terms = [t for t, _ in candidates[:max_expansions]]
        return list(query_tokens) + expanded_terms

    def query(
        self,
        query_text: str,
        top_k: int = 5,
        min_score: float = 0.05,
        category: str | None = None,
        corpus_type: str | None = None,
        hybrid_fts: bool = True,
        expand_query: bool = False,
    ) -> list[RetrievalResult]:
        """Executes hybrid semantic vector + BM25+ + exact keyword search."""
        if not self._is_indexed or not self.chunks:
            return []

        q_tokens = tokenize(query_text)
        if not q_tokens:
            return []

        effective_tokens = self.expand_query(q_tokens) if expand_query else q_tokens

        # 1. Compute query vector
        q_term_counts: dict[str, int] = {}
        for t in effective_tokens:
            q_term_counts[t] = q_term_counts.get(t, 0) + 1

        q_weights: dict[str, float] = {}
        q_norm_sq = 0.0
        for t, count in q_term_counts.items():
            idf = self.idf_cache.get(t, math.log(1.0 + len(self.chunks)) + 1.0)
            w = (1.0 + math.log(count)) * idf
            q_weights[t] = w
            q_norm_sq += w * w

        q_norm = math.sqrt(q_norm_sq) if q_norm_sq > 0.0 else 1.0

        # 2. SQLite FTS5 exact score collection
        fts_scores: dict[str, float] = {}
        if hybrid_fts and self.sqlite_db_path and self.sqlite_db_path.is_file():
            try:
                conn = sqlite3.connect(str(self.sqlite_db_path))
                cursor = conn.cursor()
                fts_terms = [re.sub(r"[^a-zA-Z0-9_-]", "", t) for t in effective_tokens if len(t) > 1]
                if fts_terms:
                    fts_query = " OR ".join(f"{t}*" for t in fts_terms)
                    cursor.execute(
                        "SELECT id, bm25(chunks_fts) AS rank_score FROM chunks_fts WHERE chunks_fts MATCH ? LIMIT 100",
                        (fts_query,)
                    )
                    for r in cursor.fetchall():
                        raw_rank = float(r[1])
                        norm_fts = 1.0 / (1.0 + abs(raw_rank))
                        fts_scores[str(r[0])] = norm_fts
                conn.close()
            except Exception as e:
                logger.debug(f"SQLite FTS5 hybrid query fallback: {e}")

        # 3. Score all chunks
        results: list[RetrievalResult] = []
        raw_query_lower = query_text.lower()

        def _normalize_cat(c: str) -> str:
            return c.lower().rstrip("s").replace("-", "").replace("_", "").strip()

        max_bm25 = 1.0
        raw_bm25_scores = {}
        for chunk in self.chunks:
            bm25_val = self.compute_bm25_plus(effective_tokens, chunk)
            raw_bm25_scores[chunk.id] = bm25_val
            if bm25_val > max_bm25:
                max_bm25 = bm25_val

        for chunk in self.chunks:
            if category and _normalize_cat(chunk.category) != _normalize_cat(category):
                continue
            if corpus_type and chunk.corpus_type.lower() != corpus_type.lower():
                continue

            # A. Vector Cosine Similarity
            dot_product = 0.0
            for t, qw in q_weights.items():
                if t in chunk.term_counts:
                    cw = (1.0 + math.log(chunk.term_counts[t])) * self.idf_cache.get(t, 1.0)
                    dot_product += qw * cw

            cosine_sim = dot_product / (q_norm * chunk.vector_norm) if (q_norm * chunk.vector_norm) > 0.0 else 0.0

            # B. Normalized BM25+ Score
            bm25_norm = raw_bm25_scores.get(chunk.id, 0.0) / max_bm25 if max_bm25 > 0 else 0.0

            # C. Entity & Heading Boosts
            entity_boost = 0.0
            for ent in chunk.entities:
                if ent.lower() in raw_query_lower:
                    entity_boost += 0.20

            heading_boost = 0.0
            if chunk.heading and any(t in chunk.heading.lower() for t in effective_tokens):
                heading_boost += 0.15

            title_boost = 0.0
            if chunk.doc_title and any(t in chunk.doc_title.lower() for t in effective_tokens):
                title_boost += 0.10

            # D. FTS5 Score Fusion
            fts_score = fts_scores.get(chunk.id, 0.0)

            combined_score = (
                (0.45 * cosine_sim)
                + (0.30 * bm25_norm)
                + (0.10 * fts_score)
                + min(0.15, entity_boost + heading_boost + title_boost)
            )

            final_score = max(0.0, min(1.0, combined_score))

            if final_score >= min_score:
                breakdown = {
                    "cosine_similarity": cosine_sim,
                    "bm25_plus": bm25_norm,
                    "fts_score": fts_score,
                    "entity_boost": entity_boost,
                    "heading_boost": heading_boost,
                    "title_boost": title_boost,
                    "combined_score": final_score,
                }
                results.append(RetrievalResult(chunk=chunk, score=final_score, score_breakdown=breakdown))

        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]


# Backward-compatible alias
LocalLoreRetrievalEngine = VaultSearchEngine


__all__ = [
    "STOPWORDS",
    "TOKEN_PATTERN",
    "IndexedChunk",
    "LocalLoreRetrievalEngine",
    "RetrievalResult",
    "VaultSearchEngine",
    "find_default_corpus_database",
    "format_markdown_report",
    "generate_html_retrieval_viewer",
    "main",
    "synthesize_llm_context",
    "tokenize",
]



def find_default_corpus_database() -> Path | None:
    """Searches workspace for default corpus.db SQLite database."""
    candidates = [
        PROJECT_ROOT / "dist" / "corpus.db",
        PROJECT_ROOT / "dist" / "corpus" / "corpus.db",
        PROJECT_ROOT / "corpus.db",
        Path.cwd() / "dist" / "corpus.db",
        Path.cwd() / "corpus.db",
    ]
    for c in candidates:
        if c.is_file():
            return c.resolve()
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="arcanum search",
        description="Sovereign Zero-Dependency Local Vault Search & Lore Engine",
    )
    parser.add_argument("query", nargs="*", help="Natural language query or lore question")
    parser.add_argument("-d", "--db", help="Path to corpus.db SQLite database")
    parser.add_argument("-t", "--target", help="Path to Markdown world vault or manuscript directory")
    parser.add_argument("-j", "--jsonl", help="Path to chunks.jsonl dataset file")
    parser.add_argument("-k", "--top-k", type=int, default=5, help="Number of chunks to retrieve (default: 5)")
    parser.add_argument("-m", "--min-score", type=float, default=0.05, help="Minimum relevance score threshold (default: 0.05)")
    parser.add_argument("-c", "--category", help="Filter chunks by category (e.g. Characters, Locations)")
    parser.add_argument("--type", dest="corpus_type", help="Filter by corpus type (lore, manuscript, meta)")
    parser.add_argument(
        "-f", "--format",
        choices=["context", "markdown", "json", "html"],
        default="context",
        help="Output format (default: context)",
    )
    parser.add_argument("-o", "--output", help="Save output to file instead of stdout")
    parser.add_argument("--instructions", help="Custom system instructions for LLM context")
    add_scope_arguments(parser, include_manuscript=True, include_world=True, target_pos_arg=False)

    args = parser.parse_args(argv)

    query_str = " ".join(args.query).strip()
    if not query_str:
        parser.print_help()
        return 2

    scope = parse_scope_args(args)
    if scope and getattr(args, "category", None) and not scope.lore_categories:
        scope.lore_categories = [args.category]

    engine = VaultSearchEngine()

    if args.db:
        db_path = Path(args.db).resolve()
        if not db_path.is_file():
            print(f"Error: Database '{db_path}' not found.", file=sys.stderr)
            return 1
        engine.load_from_sqlite(db_path)
    elif args.jsonl:
        jsonl_path = Path(args.jsonl).resolve()
        if not jsonl_path.is_file():
            print(f"Error: JSONL file '{jsonl_path}' not found.", file=sys.stderr)
            return 1
        engine.load_from_jsonl(jsonl_path)
    elif args.target:
        target_path = Path(args.target).resolve()
        if not target_path.exists():
            print(f"Error: Target path '{target_path}' not found.", file=sys.stderr)
            return 1
        engine.load_from_directory(target_path, scope=scope)
    elif scope and (scope.world or scope.manuscript or scope.universe):
        resolved_p = (
            resolve_world_path(scope=scope)
            or resolve_manuscript_path(scope=scope)
            or resolve_universe_path(scope=scope)
        )
        if resolved_p and resolved_p.is_dir():
            engine.load_from_directory(resolved_p, scope=scope)
        else:
            default_db = find_default_corpus_database()
            if default_db:
                engine.load_from_sqlite(default_db)
            else:
                engine.load_from_directory(Path.cwd(), scope=scope)
    else:
        default_db = find_default_corpus_database()
        if default_db:
            engine.load_from_sqlite(default_db)
        else:
            engine.load_from_directory(Path.cwd(), scope=scope)

    if engine.total_chunks == 0:
        print("Warning: No lore chunks found in specified source.", file=sys.stderr)

    results = engine.query(
        query_text=query_str,
        top_k=args.top_k,
        min_score=args.min_score,
        category=args.category,
        corpus_type=args.corpus_type,
    )

    output_text = ""
    if args.format == "context":
        output_text = synthesize_llm_context(query_str, results, system_instructions=args.instructions)
    elif args.format == "markdown":
        output_text = format_markdown_report(query_str, results)
    elif args.format == "json":
        payload = {
            "query": query_str,
            "total_chunks_indexed": engine.total_chunks,
            "results_count": len(results),
            "results": [r.to_dict() for r in results],
        }
        output_text = json.dumps(payload, indent=2, ensure_ascii=False)
    elif args.format == "html":
        output_text = generate_html_retrieval_viewer(query_str, results)

    if args.output:
        out_path = Path(args.output).resolve()
        atomic_write(out_path, output_text)
        print(f"Search report saved to: {out_path}")
    else:
        print(output_text)

    return 0


if __name__ == "__main__":
    sys.exit(main())
