#!/usr/bin/env python3
"""
Ars Arcanum Corpus Exporter Formatters & Restore Utilities
(scripts/lib/corpus_export_formatters.py)
==========================================================
Serialization formats (JSONL, SQLite relational FTS5 schema, Markdown digest)
and bidirectional vault restoration routines for the Universal Corpus Exporter.
"""

from __future__ import annotations

import datetime
import html
import json
import logging
import sqlite3
from pathlib import Path
from typing import TYPE_CHECKING, Any

try:
    from lib._bootstrap import atomic_write
except ImportError:
    from _bootstrap import atomic_write

if TYPE_CHECKING:
    from lib.corpus_export import CorpusScanner
else:
    CorpusScanner = Any

logger = logging.getLogger("arcanum.corpus_export_formatters")


def export_jsonl(scanner: CorpusScanner, output_dir: Path) -> dict[str, Path]:
    """Exports dataset to documents.jsonl, chunks.jsonl, and entities.jsonl."""
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {}

    # 1. documents.jsonl
    docs_file = output_dir / "documents.jsonl"
    doc_lines = [json.dumps(d.to_dict(include_body=True, include_chunks=False)) for d in scanner.documents]
    atomic_write(docs_file, "\n".join(doc_lines) + "\n")
    paths["documents"] = docs_file

    # 2. chunks.jsonl
    chunks_file = output_dir / "chunks.jsonl"
    chunk_lines = []
    for d in scanner.documents:
        for c in d.chunks:
            chunk_dict = c.to_dict()
            chunk_dict["doc_title"] = d.title
            chunk_dict["doc_category"] = d.category
            chunk_dict["corpus_type"] = d.corpus_type
            chunk_lines.append(json.dumps(chunk_dict))
    atomic_write(chunks_file, "\n".join(chunk_lines) + "\n")
    paths["chunks"] = chunks_file

    # 3. entities.jsonl
    entities_file = output_dir / "entities.jsonl"
    unique_entities = {e.name: e for e in scanner.entities.values()}
    ent_lines = [json.dumps(e.to_dict()) for e in unique_entities.values()]
    atomic_write(entities_file, "\n".join(ent_lines) + "\n")
    paths["entities"] = entities_file

    return paths


def export_sqlite(scanner: CorpusScanner, db_path: Path) -> Path:
    """Exports structured SQLite database with relational schema and full-text search."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Schema creation
    cursor.executescript("""
    CREATE TABLE corpus_meta (
        corpus_name TEXT PRIMARY KEY,
        exported_at TEXT,
        total_docs INTEGER,
        total_words INTEGER,
        total_chunks INTEGER,
        total_entities INTEGER,
        version TEXT
    );

    CREATE TABLE documents (
        id TEXT PRIMARY KEY,
        corpus_type TEXT,
        category TEXT,
        title TEXT,
        path TEXT,
        word_count INTEGER,
        token_count_est INTEGER,
        frontmatter_json TEXT,
        body TEXT
    );

    CREATE TABLE chunks (
        id TEXT PRIMARY KEY,
        doc_id TEXT,
        chunk_index INTEGER,
        heading TEXT,
        text TEXT,
        word_count INTEGER,
        token_count_est INTEGER,
        entities_json TEXT,
        FOREIGN KEY(doc_id) REFERENCES documents(id)
    );

    CREATE TABLE entities (
        id TEXT PRIMARY KEY,
        name TEXT UNIQUE,
        entity_type TEXT,
        doc_id TEXT,
        aliases_json TEXT,
        mention_count INTEGER,
        metadata_json TEXT
    );

    CREATE TABLE entity_mentions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entity_name TEXT,
        source_doc_id TEXT,
        chunk_id TEXT,
        mention_type TEXT
    );

    CREATE TABLE relationships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_entity TEXT,
        target_entity TEXT,
        relation_type TEXT,
        doc_id TEXT
    );

    CREATE INDEX idx_docs_type ON documents(corpus_type);
    CREATE INDEX idx_docs_category ON documents(category);
    CREATE INDEX idx_chunks_doc ON chunks(doc_id);
    CREATE INDEX idx_entities_type ON entities(entity_type);
    CREATE INDEX idx_rel_source ON relationships(source_entity);
    CREATE INDEX idx_rel_target ON relationships(target_entity);
    """)

    # Try creating FTS5 virtual tables
    try:
        cursor.executescript("""
        CREATE VIRTUAL TABLE documents_fts USING fts5(
            id UNINDEXED,
            title,
            body
        );
        CREATE VIRTUAL TABLE chunks_fts USING fts5(
            id UNINDEXED,
            heading,
            text
        );
        """)
        has_fts5 = True
    except Exception as e:
        logger.warning("SQLite FTS5 virtual tables could not be created: %s", e)
        has_fts5 = False

    # Insert metadata
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    unique_entities = {e.name: e for e in scanner.entities.values()}

    cursor.execute("""
    INSERT INTO corpus_meta (corpus_name, exported_at, total_docs, total_words, total_chunks, total_entities, version)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        scanner.target.name,
        now_iso,
        len(scanner.documents),
        scanner.total_words(),
        scanner.total_chunks(),
        len(unique_entities),
        "2.0.0",
    ))

    # Insert documents & chunks
    for doc in scanner.documents:
        cursor.execute("""
        INSERT INTO documents (id, corpus_type, category, title, path, word_count, token_count_est, frontmatter_json, body)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            doc.id,
            doc.corpus_type,
            doc.category,
            doc.title,
            doc.path,
            doc.word_count,
            doc.token_count_est,
            json.dumps(doc.frontmatter),
            doc.body,
        ))

        if has_fts5:
            cursor.execute("INSERT INTO documents_fts (id, title, body) VALUES (?, ?, ?)", (doc.id, doc.title, doc.body))

        for c in doc.chunks:
            cursor.execute("""
            INSERT INTO chunks (id, doc_id, chunk_index, heading, text, word_count, token_count_est, entities_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                c.id,
                c.doc_id,
                c.chunk_index,
                c.heading,
                c.text,
                c.word_count,
                c.token_count_est,
                json.dumps(c.entities),
            ))

            if has_fts5:
                cursor.execute("INSERT INTO chunks_fts (id, heading, text) VALUES (?, ?, ?)", (c.id, c.heading, c.text))

            # Record chunk mentions
            for ent_ref in c.entities:
                cursor.execute("""
                INSERT INTO entity_mentions (entity_name, source_doc_id, chunk_id, mention_type)
                VALUES (?, ?, ?, ?)
                """, (ent_ref, doc.id, c.id, "wikilink"))

    # Insert entities
    for ent in unique_entities.values():
        cursor.execute("""
        INSERT OR REPLACE INTO entities (id, name, entity_type, doc_id, aliases_json, mention_count, metadata_json)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            ent.id,
            ent.name,
            ent.entity_type,
            ent.doc_id,
            json.dumps(ent.aliases),
            ent.mention_count,
            json.dumps(ent.metadata),
        ))

    # Insert relationships
    for rel in scanner.relationships:
        cursor.execute("""
        INSERT INTO relationships (source_entity, target_entity, relation_type, doc_id)
        VALUES (?, ?, ?, ?)
        """, (rel["source"], rel["target"], rel["relation"], rel["doc_id"]))

    conn.commit()
    conn.close()
    return db_path


def export_markdown_summary(scanner: CorpusScanner, output_file: Path) -> Path:
    """Generates an executive Markdown corpus digest and data catalog."""
    now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    unique_entities = {e.name: e for e in scanner.entities.values()}

    # Categorize documents
    lore_docs = [d for d in scanner.documents if d.corpus_type == "lore"]
    manuscript_docs = [d for d in scanner.documents if d.corpus_type == "manuscript"]
    meta_docs = [d for d in scanner.documents if d.corpus_type == "meta"]

    top_entities = sorted(unique_entities.values(), key=lambda e: e.mention_count, reverse=True)[:15]

    lines = [
        f"# Corpus Summary Digest: {scanner.target.name}",
        "",
        f"> **Generated**: {now_str}  ",
        f"> **Target**: `{scanner.target}`  ",
        f"> **Total Documents**: {len(scanner.documents)} | **Total Words**: {scanner.total_words():,} | **Semantic Chunks**: {scanner.total_chunks():,} | **Entities**: {len(unique_entities):,}",
        "",
        "---",
        "",
        "## 1. Corpus Metrics Overview",
        "",
        "| Dimension | Count | Total Words | Est. Tokens (~1.33x) |",
        "| :--- | :--- | :--- | :--- |",
        f"| **World Bible & Lore** | {len(lore_docs)} | {sum(d.word_count for d in lore_docs):,} | {sum(d.token_count_est for d in lore_docs):,} |",
        f"| **Manuscripts & Chapters** | {len(manuscript_docs)} | {sum(d.word_count for d in manuscript_docs):,} | {sum(d.token_count_est for d in manuscript_docs):,} |",
        f"| **Meta & Indexes** | {len(meta_docs)} | {sum(d.word_count for d in meta_docs):,} | {sum(d.token_count_est for d in meta_docs):,} |",
        f"| **Total Unified Corpus** | **{len(scanner.documents)}** | **{scanner.total_words():,}** | **{round(scanner.total_words() * 1.33):,}** |",
        "",
        "---",
        "",
        "## 2. Most Frequently Mentioned Entities",
        "",
        "| Entity Name | Type | Mentions | Defined In | Aliases |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]

    for ent in top_entities:
        doc_str = f"`{ent.doc_id}`" if ent.doc_id else "*Inferred*"
        alias_str = ", ".join(ent.aliases) if ent.aliases else "—"
        lines.append(f"| **{html.escape(ent.name)}** | `{ent.entity_type}` | {ent.mention_count} | {doc_str} | {alias_str} |")

    lines.extend([
        "",
        "---",
        "",
        "## 3. Document Catalog",
        "",
        "| Path | Type | Category | Words | Chunks | Links |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |",
    ])

    for d in scanner.documents:
        lines.append(f"| `{d.path}` | `{d.corpus_type}` | {d.category} | {d.word_count:,} | {len(d.chunks)} | {len(d.entities_referenced)} |")

    lines.append("")
    atomic_write(output_file, "\n".join(lines))
    return output_file


def _validate_safe_restore_path(target_dir: Path, rel_path_str: str) -> Path:
    """Validates that a relative path from an archive does not escape target_dir."""
    clean_rel = Path(rel_path_str.replace("\\", "/"))
    if clean_rel.is_absolute() or ".." in clean_rel.parts:
        raise ValueError(f"Path traversal detected in corpus dataset: '{rel_path_str}'")
    out_file = (target_dir / clean_rel).resolve()
    target_resolved = target_dir.resolve()
    try:
        out_file.relative_to(target_resolved)
    except ValueError:
        raise ValueError(f"Target file path '{out_file}' escapes target directory '{target_resolved}'") from None
    return out_file


def restore_corpus_from_jsonl(source_path: Path, target_dir: Path) -> None:
    """Restores corpus documents from a documents.jsonl file."""
    target_dir.mkdir(parents=True, exist_ok=True)
    with open(source_path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            doc = json.loads(line)
            content_parts = []
            if doc.get("frontmatter"):
                content_parts.append("---")
                for k, v in doc["frontmatter"].items():
                    if isinstance(v, list):
                        content_parts.append(f"{k}:")
                        for item in v:
                            content_parts.append(f"  - {json.dumps(item) if isinstance(item, str) else item}")
                    else:
                        content_parts.append(f"{k}: {json.dumps(v) if isinstance(v, str) else v}")
                content_parts.append("---")
            if doc.get("body"):
                content_parts.append(doc["body"])

            content = "\n".join(content_parts)
            out_file = _validate_safe_restore_path(target_dir, doc["path"])
            out_file.parent.mkdir(parents=True, exist_ok=True)
            atomic_write(out_file, content)


def restore_corpus_from_sqlite(source_path: Path, target_dir: Path) -> None:
    """Restores corpus documents from a corpus.db SQLite file."""
    target_dir.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(source_path))
    cursor = conn.cursor()
    cursor.execute("SELECT path, frontmatter_json, body FROM documents")
    for row in cursor.fetchall():
        path_str, fm_json, body = row
        out_file = _validate_safe_restore_path(target_dir, path_str)
        out_file.parent.mkdir(parents=True, exist_ok=True)

        fm = json.loads(fm_json) if fm_json else {}
        content_parts = []
        if fm:
            content_parts.append("---")
            for k, v in fm.items():
                if isinstance(v, list):
                    content_parts.append(f"{k}:")
                    for item in v:
                        content_parts.append(f"  - {json.dumps(item) if isinstance(item, str) else item}")
                else:
                    content_parts.append(f"{k}: {json.dumps(v) if isinstance(v, str) else v}")
            content_parts.append("---")

        if body:
            content_parts.append(body)

        content = "\n".join(content_parts)
        atomic_write(out_file, content)
    conn.close()


__all__ = [
    "export_jsonl",
    "export_markdown_summary",
    "export_sqlite",
    "restore_corpus_from_jsonl",
    "restore_corpus_from_sqlite",
]
