#!/usr/bin/env python3
"""
Ars Arcanum Universal Structured Corpus & RAG Dataset Exporter
(scripts/lib/corpus_export.py)
================================================================================
Zero-dependency, offline structured corpus compilation engine transforming
Obsidian World Bibles, Cosmos Universes, and multi-volume manuscripts into
sanitized JSONL, SQLite database, and Markdown datasets for local LLM
fine-tuning, vector search embeddings, and archival analysis.

Capabilities:
1. Universal Vault & Manuscript Traversal:
   - Scans World Bibles (Characters, Locations, Factions, MagicSystems, History, etc.)
   - Scans Manuscript Chapters, Scenes, Drafts, and Front/Back Matter.
   - Extracts YAML frontmatter, inline @tags, Obsidian [[wikilinks]], and headings.
2. Semantic Chunking for Local RAG:
   - Configurable paragraph/heading-aware semantic chunking with token estimates.
   - Preserves parent document metadata, section headers, and entity link graphs per chunk.
3. Multi-Format Sovereign Exports:
   - JSON Lines (`documents.jsonl`, `chunks.jsonl`, `entities.jsonl`).
   - Relational SQLite 3 Database (`corpus.db`) with normalized schema and FTS5 full-text search.
   - Master Corpus Markdown Digest (`_corpus_summary.md`).

Zero external dependencies; 100% offline privacy.
"""

import argparse
import json
import logging
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

__all__ = [
    "CorpusChunk",
    "CorpusDocument",
    "CorpusEntity",
    "CorpusScanner",
    "export_jsonl",
    "export_markdown_summary",
    "export_sqlite",
    "main",
    "restore_corpus_from_jsonl",
    "restore_corpus_from_sqlite",
    "sanitize_id",
]

try:
    from lib._bootstrap import count_prose_words
    from lib.corpus_export_formatters import (
        export_jsonl,
        export_markdown_summary,
        export_sqlite,
        restore_corpus_from_jsonl,
        restore_corpus_from_sqlite,
    )
    from lib.frontmatter import parse_yaml_frontmatter
    from lib.scope import (
        EngineScope,
        add_scope_arguments,
        filter_manuscript_scope,
        filter_world_scope,
        parse_scope_args,
        resolve_manuscript_path,
        resolve_world_path,
    )
except ImportError:
    from _bootstrap import count_prose_words
    from corpus_export_formatters import (  # type: ignore[no-redef]
        export_jsonl,
        export_markdown_summary,
        export_sqlite,
        restore_corpus_from_jsonl,
        restore_corpus_from_sqlite,
    )
    from frontmatter import parse_yaml_frontmatter
    from scope import (  # type: ignore[no-redef]
        EngineScope,
        add_scope_arguments,
        filter_manuscript_scope,
        filter_world_scope,
        parse_scope_args,
        resolve_manuscript_path,
        resolve_world_path,
    )

logger = logging.getLogger("arcanum.corpus")

FRONTMATTER_REGEX = re.compile(r"^---\s*\r?\n(.*?)\r?\n---\s*(?:\r?\n|$)", re.DOTALL)
WIKILINK_REGEX = re.compile(r"\[\[([^\|\]]+)(?:\|([^\]]+))?\]\]")
TAG_REGEX = re.compile(r"@([a-zA-Z0-9_-]+):\s*([^\r\n]+)")
HEADING_REGEX = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)

LORE_TAXONOMIES = {
    "Characters", "Locations", "Factions", "Artifacts", "Bestiary",
    "Cosmology", "Languages", "MagicSystems", "Magic-Technology", "History",
    "Items", "Concepts", "Flora", "Fauna", "Religions", "Nations"
}


@dataclass
class CorpusChunk:
    id: str
    doc_id: str
    chunk_index: int
    heading: str
    text: str
    word_count: int
    token_count_est: int
    entities: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CorpusEntity:
    id: str
    name: str
    entity_type: str
    doc_id: str | None
    aliases: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    outgoing_references: list[str] = field(default_factory=list)
    mention_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CorpusDocument:
    id: str
    corpus_type: str  # "lore", "manuscript", "meta"
    category: str     # "Characters", "Locations", "Chapter", "Universe", etc.
    title: str
    path: str
    word_count: int
    token_count_est: int
    frontmatter: dict[str, Any] = field(default_factory=dict)
    tags: dict[str, list[str]] = field(default_factory=dict)
    entities_referenced: list[str] = field(default_factory=list)
    body: str = ""
    chunks: list[CorpusChunk] = field(default_factory=list)

    def to_dict(self, include_body: bool = True, include_chunks: bool = True) -> dict[str, Any]:
        d: dict[str, Any] = {
            "id": self.id,
            "corpus_type": self.corpus_type,
            "category": self.category,
            "title": self.title,
            "path": self.path,
            "word_count": self.word_count,
            "token_count_est": self.token_count_est,
            "frontmatter": self.frontmatter,
            "tags": self.tags,
            "entities_referenced": self.entities_referenced,
        }
        if include_body:
            d["body"] = self.body
        if include_chunks:
            d["chunks"] = [c.to_dict() for c in self.chunks]
        return d


def sanitize_id(raw_str: str) -> str:
    """Converts a path or name into a safe, normalized identifier string."""
    clean = raw_str.replace("\\", "/").strip().lower()
    clean = re.sub(r"[^\w\-/.]", "_", clean)
    clean = re.sub(r"_+", "_", clean)
    return clean.strip("_")


def extract_wikilinks(text: str) -> list[str]:
    """Extracts unique targets from Obsidian wikilinks [[Target]] or [[Target|Label]]."""
    targets: list[str] = []
    for match in WIKILINK_REGEX.finditer(text):
        target = match.group(1).strip()
        if target and target not in targets:
            targets.append(target)
    return targets


def extract_inline_tags(text: str) -> dict[str, list[str]]:
    """Extracts key-value tags like @pov: Aeloria or @location: High-Sanctuary."""
    tags: dict[str, list[str]] = {}
    for match in TAG_REGEX.finditer(text):
        key = match.group(1).lower().strip()
        val = match.group(2).strip()
        if val:
            tags.setdefault(key, []).append(val)
    return tags


def chunk_document(
    doc_id: str,
    body: str,
    target_chunk_words: int = 250,
) -> list[CorpusChunk]:
    """
    Splits document body into heading- and paragraph-aware semantic chunks.
    Preserves heading context and extracts per-chunk entity wikilinks.
    """
    paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()]
    if not paragraphs:
        return []

    chunks: list[CorpusChunk] = []
    current_heading = "General"
    current_chunk_paras: list[str] = []
    current_chunk_words = 0
    chunk_idx = 1

    def flush_chunk():
        nonlocal chunk_idx, current_chunk_paras, current_chunk_words
        if not current_chunk_paras:
            return
        chunk_text = "\n\n".join(current_chunk_paras).strip()
        word_cnt = count_prose_words(chunk_text)
        token_est = round(word_cnt * 1.33)
        chunk_entities = extract_wikilinks(chunk_text)

        chunks.append(CorpusChunk(
            id=f"{doc_id}#chunk_{chunk_idx:03d}",
            doc_id=doc_id,
            chunk_index=chunk_idx,
            heading=current_heading,
            text=chunk_text,
            word_count=word_cnt,
            token_count_est=token_est,
            entities=chunk_entities,
        ))
        chunk_idx += 1
        current_chunk_paras = []
        current_chunk_words = 0

    for para in paragraphs:
        # Check if paragraph is or starts with a heading
        h_match = re.match(r"^(#{1,6})\s+([^\r\n]+)", para)
        if h_match:
            # If we already have accumulated chunk content, flush before starting new section
            if current_chunk_paras:
                flush_chunk()
            current_heading = h_match.group(2).strip()

        para_words = count_prose_words(para)
        if current_chunk_words + para_words > target_chunk_words and current_chunk_paras:
            flush_chunk()

        current_chunk_paras.append(para)
        current_chunk_words += para_words

    flush_chunk()
    return chunks


def process_markdown_file(
    file_path: Path,
    root_path: Path,
    target_chunk_words: int = 250,
) -> CorpusDocument:
    """Parses a single Markdown document into a structured CorpusDocument with chunks."""
    content = file_path.read_text(encoding="utf-8", errors="replace")
    frontmatter = parse_yaml_frontmatter(content)
    body = FRONTMATTER_REGEX.sub("", content).strip()

    rel_path = str(file_path.relative_to(root_path)).replace("\\", "/")
    doc_id = sanitize_id(rel_path.removesuffix(".md"))

    # Determine corpus type & category
    path_parts = file_path.parts
    corpus_type = "lore"
    category = "General"

    if "Manuscripts" in path_parts or "draft" in file_path.name.lower() or "chapter" in file_path.name.lower():
        corpus_type = "manuscript"
        category = "Manuscript"
        for part in path_parts:
            if part.startswith(("Book-", "Volume-")):
                category = part
                break
    elif file_path.name in ("Universe-Index.md", "World-Bible-Index.md", "README.md", "SUMMARY.md"):
        corpus_type = "meta"
        category = "Index"
    else:
        # Check taxonomy folder
        for part in path_parts:
            if part in LORE_TAXONOMIES:
                category = part
                corpus_type = "lore"
                break
        else:
            if "type" in frontmatter:
                category = str(frontmatter["type"]).title()

    # Extract Title
    h1_match = re.search(r"^#\s+(.+)$", body, flags=re.MULTILINE)
    title = str(
        frontmatter.get("name")
        or frontmatter.get("title")
        or (h1_match.group(1).strip() if h1_match else file_path.stem.replace("-", " ").replace("_", " ").title())
    )

    # Extract tags & wikilinks
    tags = extract_inline_tags(body)
    if "aliases" in frontmatter and isinstance(frontmatter["aliases"], list):
        tags["aliases"] = [str(a) for a in frontmatter["aliases"]]
    if "tags" in frontmatter:
        raw_tags = frontmatter["tags"]
        if isinstance(raw_tags, list):
            tags["tags"] = [str(t) for t in raw_tags]
        elif isinstance(raw_tags, str):
            tags["tags"] = [raw_tags]

    entities_referenced = extract_wikilinks(body)
    # Also include wikilinks from frontmatter values
    for v in frontmatter.values():
        if isinstance(v, str):
            for link in extract_wikilinks(v):
                if link not in entities_referenced:
                    entities_referenced.append(link)

    word_count = count_prose_words(body)
    token_count_est = round(word_count * 1.33)

    chunks = chunk_document(doc_id, body, target_chunk_words=target_chunk_words)

    return CorpusDocument(
        id=doc_id,
        corpus_type=corpus_type,
        category=category,
        title=title,
        path=rel_path,
        word_count=word_count,
        token_count_est=token_count_est,
        frontmatter=frontmatter,
        tags=tags,
        entities_referenced=entities_referenced,
        body=body,
        chunks=chunks,
    )


class CorpusScanner:
    """Scans a target directory or file and compiles all documents, chunks, and entities."""

    def __init__(
        self,
        target: Path,
        target_chunk_words: int = 250,
        include_drafts: bool = True,
        scope: EngineScope | None = None,
    ):
        self.target = target.resolve()
        self.target_chunk_words = target_chunk_words
        self.include_drafts = include_drafts
        self.scope = scope
        self.documents: list[CorpusDocument] = []
        self.entities: dict[str, CorpusEntity] = {}
        self.relationships: list[dict[str, str]] = []

    def scan(self) -> None:
        """Executes full repository discovery and entity resolution."""
        files: list[Path] = []
        if self.target.is_file() and self.target.suffix.lower() == ".md":
            files.append(self.target)
            root_path = self.target.parent
        else:
            root_path = self.target
            if self.scope and self.scope.is_scoped():
                if self.scope.books or self.scope.chapters or self.scope.scenes:
                    scoped_chapters, _, _ = filter_manuscript_scope(self.target, self.scope)
                    files = [c.file_path for c in scoped_chapters]
                elif self.scope.lore_categories:
                    scoped_lore = filter_world_scope(self.target, self.scope)
                    files = [item.file_path for item in scoped_lore]
                else:
                    for p in sorted(self.target.rglob("*.md")):
                        if p.name.startswith((".", "_")) or "Backups" in p.parts or ".git" in p.parts or "node_modules" in p.parts:
                            continue
                        if not self.include_drafts and "Back_Matter" in p.parts:
                            continue
                        files.append(p)
            else:
                for p in sorted(self.target.rglob("*.md")):
                    if p.name.startswith((".", "_")):
                        continue
                    if "Backups" in p.parts or ".git" in p.parts or "node_modules" in p.parts:
                        continue
                    if not self.include_drafts and "Back_Matter" in p.parts:
                        continue
                    files.append(p)

        self.documents = [
            process_markdown_file(f, root_path, target_chunk_words=self.target_chunk_words)
            for f in files
        ]

        self._build_entity_graph()

    def _build_entity_graph(self) -> None:
        """Discovers declared entities and builds cross-document references."""
        # 1. Register declared entities from documents
        for doc in self.documents:
            # Lore documents or documents with explicit name/type define an entity
            is_entity_doc = (
                doc.corpus_type == "lore"
                or "type" in doc.frontmatter
                or doc.category in LORE_TAXONOMIES
            )
            if is_entity_doc:
                ent_name = str(doc.frontmatter.get("name", doc.title))
                ent_type = str(doc.frontmatter.get("type", doc.category)).lower()
                aliases = [str(a) for a in doc.frontmatter.get("aliases", []) if isinstance(a, str)]

                ent = CorpusEntity(
                    id=sanitize_id(ent_name),
                    name=ent_name,
                    entity_type=ent_type,
                    doc_id=doc.id,
                    aliases=aliases,
                    metadata=doc.frontmatter,
                    outgoing_references=list(doc.entities_referenced),
                    mention_count=0,
                )
                self.entities[ent_name] = ent
                # Map aliases too
                for a in aliases:
                    if a not in self.entities:
                        self.entities[a] = ent

                # Extract explicit frontmatter relationships
                for rel_key, rel_val in doc.frontmatter.items():
                    if isinstance(rel_val, str) and rel_val.startswith("[[") and rel_val.endswith("]]"):
                        target_ent = rel_val.strip("[]").split("|")[0].strip()
                        self.relationships.append({
                            "source": ent_name,
                            "target": target_ent,
                            "relation": rel_key,
                            "doc_id": doc.id,
                        })

        # 2. Count mentions and incoming links across all documents
        for doc in self.documents:
            for ref in doc.entities_referenced:
                if ref in self.entities:
                    self.entities[ref].mention_count += 1
                else:
                    # Discover implicit entity referenced by wikilink
                    self.entities[ref] = CorpusEntity(
                        id=sanitize_id(ref),
                        name=ref,
                        entity_type="inferred",
                        doc_id=None,
                        mention_count=1,
                    )

    def total_words(self) -> int:
        return sum(d.word_count for d in self.documents)

    def total_chunks(self) -> int:
        return sum(len(d.chunks) for d in self.documents)


__all__ = [
    "FRONTMATTER_REGEX",
    "HEADING_REGEX",
    "LORE_TAXONOMIES",
    "TAG_REGEX",
    "WIKILINK_REGEX",
    "CorpusChunk",
    "CorpusDocument",
    "CorpusEntity",
    "CorpusScanner",
    "chunk_document",
    "export_jsonl",
    "export_markdown_summary",
    "export_sqlite",
    "extract_inline_tags",
    "extract_wikilinks",
    "main",
    "process_markdown_file",
    "restore_corpus_from_jsonl",
    "restore_corpus_from_sqlite",
    "sanitize_id",
]


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Universal Structured Corpus & RAG Dataset Exporter")
    subparsers = parser.add_subparsers(dest="subcommand", help="Corpus subcommands (export, restore)")

    # export command
    p_export = subparsers.add_parser("export", help="Export corpus to JSONL, SQLite, or Markdown")
    p_export.add_argument("target", nargs="?", help="Universe, World Bible, Manuscript directory or Markdown file")
    p_export.add_argument("--format", "-f", choices=["jsonl", "sqlite", "summary", "both", "all"], default="both", help="Export format (default: both)")
    p_export.add_argument("--output", "-o", help="Output directory or database file path")
    p_export.add_argument("--chunk-size", type=int, default=250, help="Target semantic chunk word size (default: 250)")
    p_export.add_argument("--json", action="store_true", help="Print export summary JSON to stdout")
    p_export.add_argument("--dry-run", action="store_true", help="Scan and report metrics without writing files")
    add_scope_arguments(p_export, include_manuscript=False, include_world=False, target_pos_arg=False)

    # restore command
    p_restore = subparsers.add_parser("restore", help="Restore corpus from JSONL or SQLite")
    p_restore.add_argument("source", help="Source file (documents.jsonl or corpus.db)")
    p_restore.add_argument("target", help="Target directory to restore into")

    raw_args = sys.argv[1:]
    if raw_args and raw_args[0] not in ("export", "restore", "-h", "--help"):
        # Fallback for legacy arcanum corpus <target> invocation
        raw_args = ["export", *raw_args]

    args = parser.parse_args(raw_args)

    if getattr(args, "subcommand", None) == "restore":
        print(f"Restoring from {args.source} to {args.target}...")
        source_path = Path(args.source)
        target_dir = Path(args.target)
        if not source_path.exists():
            print(f"Error: Source file does not exist: {source_path}", file=sys.stderr)
            sys.exit(1)
        if source_path.suffix.lower() == ".db":
            restore_corpus_from_sqlite(source_path, target_dir)
        elif source_path.suffix.lower() == ".jsonl":
            restore_corpus_from_jsonl(source_path, target_dir)
        else:
            print("Error: Source file must be a .db or .jsonl file", file=sys.stderr)
            sys.exit(1)
        print("Restore complete.")
        sys.exit(0)

    scope = parse_scope_args(args)
    raw_target = getattr(args, "target", None) or scope.universe or scope.world or scope.manuscript
    resolved_target = str(resolve_world_path(raw_target, scope=scope) or resolve_manuscript_path(raw_target, scope=scope) or raw_target) if raw_target else ""

    target_path = Path(resolved_target) if resolved_target else Path("")
    if not target_path.exists():
        print(f"Error: Target path does not exist: {target_path}", file=sys.stderr)
        sys.exit(1)

    scanner = CorpusScanner(target_path, target_chunk_words=args.chunk_size, scope=scope)
    scanner.scan()

    if args.dry_run or args.json:
        report = {
            "target": str(target_path),
            "total_documents": len(scanner.documents),
            "total_words": scanner.total_words(),
            "total_chunks": scanner.total_chunks(),
            "total_entities": len({e.name: e for e in scanner.entities.values()}),
            "categories": sorted({d.category for d in scanner.documents}),
        }
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(f"Corpus Dry Run: {len(scanner.documents)} docs | {scanner.total_words():,} words | {scanner.total_chunks():,} chunks | {report['total_entities']} entities")
        return

    # Determine default output directory
    out_path = Path(args.output) if args.output else Path("dist") / "corpus" / target_path.stem

    fmt = args.format.lower()

    generated_files: list[str] = []

    if fmt in ("jsonl", "both", "all"):
        jsonl_paths = export_jsonl(scanner, out_path)
        generated_files.extend([str(p) for p in jsonl_paths.values()])

    if fmt in ("sqlite", "both", "all"):
        db_file = out_path if out_path.suffix == ".db" else out_path / f"{sanitize_id(target_path.stem)}.db"
        export_sqlite(scanner, db_file)
        generated_files.append(str(db_file))

    if fmt in ("summary", "both", "all"):
        summary_file = out_path / "_corpus_summary.md"
        export_markdown_summary(scanner, summary_file)
        generated_files.append(str(summary_file))

    print("=" * 75)
    print("  🏛️  Ars Arcanum Universal Corpus Exporter — v2.0.0")
    print("=" * 75)
    print(f"Target:          {target_path}")
    print(f"Total Documents: {len(scanner.documents)}")
    print(f"Total Words:     {scanner.total_words():,}")
    print(f"Total Chunks:    {scanner.total_chunks():,}")
    print(f"Total Entities:  {len({e.name: e for e in scanner.entities.values()}):,}")
    print(f"Output Path:     {out_path}")
    print("-" * 75)
    print("Generated Artifacts:")
    for f in generated_files:
        print(f"  • {f}")
    print("=" * 75)


if __name__ == "__main__":
    main()


