#!/usr/bin/env python3
"""
Domain engine specification definitions for Ars Arcanum Registry.
"""
from __future__ import annotations

try:
    from lib.registry_base import EngineCategory, EngineSpec
except ImportError:
    from registry_base import EngineCategory, EngineSpec

ENGINES: dict[str, EngineSpec] = {

    # =========================================================================
    # DOMAIN F: RETRIEVAL, INTELLIGENCE & PIPELINE INFRASTRUCTURE
    # =========================================================================
    "vault_search": EngineSpec(
        name="vault_search",
        category=EngineCategory.CORE,
        title="Sovereign Local Vault Search & Lore Engine",
        description="Hybrid TF-IDF vector space and SQLite FTS5 lore query engine with Reciprocal Rank Fusion",
        module_name="lib.vault_search",
        cli_command="search",
        aliases=["search", "vault-search", "rag", "query-lore", "recall"],
        studio_tab="Tools",
        logic_documentation="Zero-dependency hybrid TF-IDF vector space and SQLite FTS5 BM25 search engine with Reciprocal Rank Fusion (RRF), hierarchical parent-child chunking, and local LLM context synthesis.",
        scientific_logic="""1. Hybrid Vector-Lexical Search with Reciprocal Rank Fusion (RRF):
   Combines SQLite FTS5 BM25 full-text rank $R_{\\text{FTS5}}$ with TF-IDF cosine similarity rank $R_{\\text{TFIDF}}$:
   $$\\text{RRF Score}(d) = \\frac{1}{60 + R_{\\text{FTS5}}(d)} + \\frac{1}{60 + R_{\\text{TFIDF}}(d)}$$

2. Hierarchical Parent-Child Chunking:
   Documents indexed in small 200-word child chunks for precise retrieval, resolving to full 1000-word parent sections for LLM context synthesis.

3. 100% Offline Air-Gapped Operation:
   Executes entirely via standard library SQLite and pure Python math without external network calls or remote embeddings.""",
        why_this_way="Cloud AI search leaks unpublished world lore and manuscript IP. Local vault search guarantees 100% air-gapped privacy and instantaneous sub-10ms retrieval.",
        worldbuilding_relevance="Answers complex lore queries instantly across tens of thousands of vault notes.",
        storytelling_relevance="Synthesizes relevant character backgrounds, magic constraints, and history before drafting.",
        writing_relevance="Empowers in-situ research without leaving the drafting cockpit.",
        subfeatures=[
            {"name": "Hybrid RRF Query Engine", "rule": "Fuses BM25 exact matching with TF-IDF semantic relevance.", "example": "arcanum search 'How does blood magic exhaustion work?'"},
            {"name": "Context Pack Builder", "rule": "Assembles structured context dossiers for local LLM completion.", "example": "arcanum search --context 'Battle of Dawn'"},
        ],
        extension_guide="""Query lore from CLI:
```bash
arcanum search "What are the weaknesses of Frost Wyrms?"
```""",
        advisory_guidance=[
            {"pattern": "Ambiguous search query returns multiple cross-domain entities", "option_a": "Apply domain category filter (e.g. Characters, Magic)", "option_b": "Use Reciprocal Rank Fusion to synthesize top matches", "option_c": "Display interactive search disambiguation list"},
        ],
    ),

    "corpus_export": EngineSpec(
        name="corpus_export",
        category=EngineCategory.CORE,
        title="Universal Structured Corpus & RAG Exporter",
        description="Structured JSONL, SQLite FTS5 database, markdown summary digest exporter, and bidirectional vault restore",
        module_name="lib.corpus_export",
        cli_command="corpus",
        aliases=["corpus-export", "export-corpus", "rag-export", "corpus-restore"],
        studio_tab="Tools",
        logic_documentation="Exports complete universe lore and manuscript vaults into structured JSONL datasets, SQLite FTS5 relational databases, fine-tuning formats (Alpaca, ShareGPT), and cryptographically verified ZIP archives with bidirectional restoration.",
        scientific_logic="""1. Fine-Tuning & RAG Dataset Synthesis:
   Transpiles lore notes and manuscript scenes into instruction-tuning datasets:
   - Alpaca format: `{"instruction": "...", "input": "...", "output": "..."}`
   - ShareGPT / ChatML format: `{"messages": [{"role": "system", "content": "..."}, ...]}`

2. Cryptographic Integrity Archive:
   Exports ZIP/tarball bundles with SHA-256 manifest digests, enabling 100% loss-less bidirectional restore.""",
        why_this_way="Writers need data sovereignty and freedom from proprietary lock-in. Corpus export allows feeding custom lore into local fine-tuned LLMs or migrating between tools.",
        worldbuilding_relevance="Backs up and structures massive worldbuilding vaults into machine-readable datasets.",
        storytelling_relevance="Enables structured data analysis of character appearances and scene interactions.",
        writing_relevance="Guarantees permanent data portability with zero vendor lock-in.",
        subfeatures=[
            {"name": "JSONL Dataset Exporter", "rule": "Exports lore into Alpaca and ShareGPT fine-tuning datasets.", "example": "arcanum corpus World/ -f alpaca -o dist/dataset.jsonl"},
            {"name": "Bidirectional Vault Restore", "rule": "Restores full folder structure and frontmatter from verified archives.", "example": "arcanum corpus restore backup_2026.zip"},
        ],
        extension_guide="""Export structured dataset:
```bash
arcanum corpus World/ -f jsonl -o dist/lore_corpus.jsonl
```""",
        advisory_guidance=[
            {"pattern": "Export target archive already exists", "option_a": "Overwrite existing archive with new SHA-256 timestamped build", "option_b": "Create incremental delta export file", "option_c": "Prompt user for custom export destination"},
        ],
    ),

    "importer": EngineSpec(
        name="importer",
        category=EngineCategory.CORE,
        title="Batch Manuscript & Vault Importer",
        description="Batch importer for Scrivener, Word (.docx), Google Docs, and unstructured Markdown trees",
        module_name="lib.importer",
        cli_command="import",
        aliases=["importer", "import-manuscript", "scrivener-import"],
        studio_tab="Tools",
        logic_documentation="Converts external Scrivener projects, Word (.docx) documents, Google Docs, and raw Markdown folders into sovereign Ars Arcanum manuscript vaults with manifest metadata and novelWriter project files.",
        scientific_logic="""1. OpenXML / Scrivener XML AST Extraction:
   Parses Scrivener binder XML (`project.scrivx`) and Word OpenXML DOM structures, reconstructing hierarchical chapter trees and preserving synopsis cards and annotations.""",
        why_this_way="Migrating out of closed writing platforms is tedious and error-prone. The importer auto-splits monolithic manuscripts into clean, numbered chapter files.",
        worldbuilding_relevance="Auto-seeds initial world dossiers from imported character and location names.",
        storytelling_relevance="Splits monolithic manuscript files into clean, ordered chapter structures.",
        writing_relevance="Provides seamless migration from proprietary writing apps to sovereign Ars Arcanum.",
        subfeatures=[
            {"name": "Scrivener Project Importer", "rule": "Converts .scriv bundles into Ars Arcanum vaults.", "example": "arcanum import MyNovel.scriv"},
            {"name": "Monolithic Docx Chapter Splitter", "rule": "Splits Word documents by Heading 1 and scene breaks.", "example": "arcanum import draft.docx --split-chapters"},
        ],
        extension_guide="""Import a manuscript:
```bash
arcanum import path/to/project.scriv
```""",
        advisory_guidance=[
            {"pattern": "Monolithic manuscript file without chapter break headers", "option_a": "Auto-split at common chapter patterns (# Chapter, Act, scene breaks)", "option_b": "Import as single continuous chapter file", "option_c": "Prompt user for custom chapter delimiter regex"},
        ],
    ),

    "docx_sync": EngineSpec(
        name="docx_sync",
        category=EngineCategory.CORE,
        title="DOCX Bidirectional Sync",
        description="Three-way content hash sync with conflict branching for Microsoft Word / LibreOffice",
        module_name="lib.docx_sync",
        cli_command="docx",
        aliases=["word", "writer", "docx-sync"],
        studio_tab="Editor",
        logic_documentation="Parses OpenXML ZIP/XML structures to bidirectionally synchronize Markdown manuscript chapters with Microsoft Word (.docx) documents, preserving formatting and comments.",
        scientific_logic="""1. Three-Way Content Hash Synchronization:
   Computes SHA-256 digests of Markdown source $H_{\\text{MD}}$, Word document $H_{\\text{DOCX}}$, and Base common ancestor $H_{\\text{BASE}}$.
   - If only MD changed: Recompiles DOCX.
   - If only DOCX changed: Updates MD while preserving frontmatter.
   - If both changed independently: Branches into conflict review file (`Chapter_01_conflict.docx`).""",
        why_this_way="Professional editors use Microsoft Word Track Changes. Three-way syncing allows authors to work with editors without losing their canonical Markdown repository.",
        worldbuilding_relevance="Allows non-technical collaborators to review world glossaries in Word.",
        storytelling_relevance="Enables round-trip editorial workflow with professional editors using Word Track Changes.",
        writing_relevance="Allows drafting in LibreOffice or Word while retaining Markdown canonical source of truth.",
        subfeatures=[
            {"name": "Bidirectional Markdown-DOCX Sync", "rule": "Synchronizes edits made in Word back into Markdown files.", "example": "arcanum docx sync Manuscript/"},
            {"name": "Conflict Branching", "rule": "Creates safe side-by-side conflict files on simultaneous edits.", "example": "arcanum docx build Manuscript/"},
        ],
        extension_guide="""Sync Word edits:
```bash
arcanum docx sync Manuscript/
```""",
        advisory_guidance=[
            {"pattern": "Simultaneous edit conflict in MD and DOCX", "option_a": "Branch into conflict file for manual side-by-side review", "option_b": "Prefer Markdown version as canonical source", "option_c": "Prefer DOCX version with Track Changes preserved"},
        ],
    ),

    "world_doctor": EngineSpec(
        name="world_doctor",
        category=EngineCategory.CORE,
        title="World Bible Doctor",
        description="Deep lore consistency, broken wikilink, orphan entity, and timeline chronology checker",
        module_name="lib.world_doctor",
        cli_command="world-doctor",
        aliases=["doctor-world", "lore-check", "world-doctor"],
        studio_tab="Diagnostics",
        logic_documentation="Performs comprehensive graph topology sweeps across World Bible notes, detecting dangling wikilinks, orphaned dossiers, fuzzy name spelling variants (e.g. Kaelen vs Kaelin), and chronological conflicts.",
        scientific_logic="""1. Graph Topology Integrity Sweep:
   Lore notes modeled as directed graph $G = (V, E)$ where edges are wikilinks `[[Target]]`.
   - Dangling Wikilinks: $e = (u, v) \\in E$ where $v \\notin V$.
   - Orphan Nodes: $\\text{deg}^+(v) + \\text{deg}^-(v) = 0$.
   - Fuzzy Spelling Variants: Levenshtein distance $\\le 2$ between entity names.""",
        why_this_way="World bibles with hundreds of interlinked markdown files accumulate broken links and misspelled character names over time.",
        worldbuilding_relevance="Maintains airtight world bible health across hundreds of interlinked lore notes.",
        storytelling_relevance="Prevents accidental continuity blunders and dropped worldbuilding concepts.",
        writing_relevance="Generates an offline HTML health report with 1-click suggested repairs.",
        subfeatures=[
            {"name": "Dangling Wikilink Sweeper", "rule": "Finds broken links to nonexistent lore files.", "example": "arcanum world-doctor World/"},
            {"name": "Fuzzy Name Variant Finder", "rule": "Detects accidental spelling variants (e.g. Althea vs Althaea).", "example": "arcanum world-doctor World/ --fuzzy"},
        ],
        extension_guide="""Run world bible health check:
```bash
arcanum world-doctor World/
```""",
        advisory_guidance=[
            {"pattern": "Fuzzy spelling variant detected (e.g. Althea / Althaea)", "option_a": "Unify all references to primary spelling", "option_b": "Register variant as legitimate in-universe dialect alias", "option_c": "Retain as intentional distinct entities"},
        ],
    ),

    "diagnostics": EngineSpec(
        name="diagnostics",
        category=EngineCategory.CORE,
        title="System Diagnostics & Diagnostics Report",
        description="Toolchain validation, environment health checks, and redacted bug triage bundles",
        module_name="lib.diagnostics",
        cli_command="doctor",
        aliases=["check", "doctor", "health"],
        studio_tab="Diagnostics",
        logic_documentation="Inspects system environment, verifies 100% offline air-gap isolation, checks external optional tools (Git, Typst, Pandoc), and validates atomic file permissions.",
        scientific_logic="""1. Toolchain & Offline Air-Gap Verification:
   Audits presence of standard CLI tools (git, python3, typst, pandoc) and verifies that no external network sockets are open during authoring operations.""",
        why_this_way="Ensures the sovereign environment is 100% operational and safe before embarking on major compile/export runs.",
        worldbuilding_relevance="Verifies storage capacity and integrity for large multimedia lore repositories.",
        storytelling_relevance="Validates compilation toolchains before initiating final book exports.",
        writing_relevance="Provides peace of mind with 100% offline privacy and health verifications.",
        subfeatures=[
            {"name": "Toolchain Probe", "rule": "Verifies availability of Git, Typst, Pandoc, and Python 3.10+.", "example": "arcanum doctor"},
            {"name": "Air-Gap Network Isolation Audit", "rule": "Verifies zero outbound network sockets or telemetry pings.", "example": "arcanum doctor --audit-airgap"},
        ],
        extension_guide="""Run system diagnostics:
```bash
arcanum doctor
```""",
        advisory_guidance=[
            {"pattern": "Optional compiler tool missing (e.g. Typst)", "option_a": "Use standard library Python/HTML fallback compiler", "option_b": "Install optional binary via system package manager", "option_c": "Export Markdown for manual external typesetting"},
        ],
    ),

    "config": EngineSpec(
        name="config",
        category=EngineCategory.CORE,
        title="Project Configuration",
        description="Global and local workspace configuration, paths, and preferences",
        module_name="lib.config",
        cli_command="config",
        studio_tab="Tools",
        logic_documentation="Manages JSON/YAML workspace configurations, environment overrides, and secure backup destinations using atomic file operations.",
        scientific_logic="""1. Hierarchical Configuration Cascading:
   Configuration loaded with strict override hierarchy:
   $$\\text{Default Invariants} \\longrightarrow \\text{Global } \\sim/.config/arcanum/ \\longrightarrow \\text{Local } .arcanum.yaml \\longrightarrow \\text{Environment Variables}$$""",
        why_this_way="Allows authors to customize fonts, word count targets, and backup paths per project while retaining sane global defaults.",
        worldbuilding_relevance="Stores default world vault paths, cosmological constants, and universe-level preferences.",
        storytelling_relevance="Configures target word count milestones, chapter formatting templates, and paradigm defaults.",
        writing_relevance="Customizes UI fonts, dark/sepia themes, and export directories.",
        subfeatures=[
            {"name": "Configuration Getter/Setter", "rule": "Gets and sets local/global preferences.", "example": "arcanum config set target_words 90000"},
            {"name": "Cascading Resolution Inspector", "rule": "Traces configuration values across defaults, global, and local scopes.", "example": "arcanum config trace target_words"},
        ],
        extension_guide="""Inspect configuration:
```bash
arcanum config get backup_dest
```""",
        advisory_guidance=[
            {"pattern": "Missing configuration key", "option_a": "Generate default configuration file", "option_b": "Inherit global environment variable", "option_c": "Use ephemeral in-memory fallback"},
        ],
    ),

    "cache": EngineSpec(
        name="cache",
        category=EngineCategory.CORE,
        title="Performance Cache",
        description="Fast mtime-keyed in-memory index for lore vaults and manuscripts",
        module_name="lib.cache",
        cli_command="cache",
        studio_tab="Tools",
        logic_documentation="Caches parsed markdown ASTs, word counts, and wikilink graphs using file modification timestamps (mtime) and SHA-256 digests for sub-millisecond query performance.",
        scientific_logic="""1. mtime-Keyed AST Caching:
   Caches parsed markdown frontmatter and word counts keyed by `(file_path, mtime, size)`. Only re-parses disk files when mtime changes, achieving sub-millisecond response across 10,000+ files.""",
        why_this_way="Re-parsing thousands of markdown files on every UI keystroke causes UI lag. Fast in-memory caching keeps typing fluid.",
        worldbuilding_relevance="Enables instantaneous searching across thousands of world lore entities without re-parsing disk files.",
        storytelling_relevance="Provides live, lag-free structural word counts and chapter analytics across multi-volume series.",
        writing_relevance="Maintains background typing speed without UI stuttering.",
        subfeatures=[
            {"name": "Cache Invalidation & Sweeper", "rule": "Clears and rebuilds mtime index.", "example": "arcanum cache clear"},
            {"name": "mtime AST Indexer", "rule": "Pre-computes markdown word counts and frontmatter hashes for fast lookup.", "example": "arcanum cache warm"},
        ],
        extension_guide="""Clear and rebuild cache:
```bash
arcanum cache scan
```""",
        advisory_guidance=[
            {"pattern": "Stale cache detected", "option_a": "Trigger automatic cache invalidation on next read", "option_b": "Run background asynchronous cache refresh", "option_c": "Bypass cache with direct disk read"},
        ],
    ),

    "manuscript_scaffold": EngineSpec(
        name="manuscript_scaffold",
        category=EngineCategory.CORE,
        title="Manuscript Structure Scaffolder",
        description="Pluggable manuscript directory scaffolding across 16 narrative structure presets and custom division layouts",
        module_name="lib.manuscript_scaffold",
        cli_command="scaffold",
        aliases=["scaffold", "presets", "structure-presets", "manuscript-scaffold"],
        studio_tab="Craft",
        logic_documentation="Generates numbered directory hierarchies and starter chapters across 16 structural paradigms (Classic Three-Act, Hero's Journey, Save the Cat, Story Circle, Kishōtenketsu, 7-Point, Fichtean Curve, 8-Sequence, Freytag's Pyramid, MICE Quotient, Romancing the Beat, Virgin's Promise, Snowflake, Parallel, Episodic, Nonlinear) and custom user-defined division lists with path traversal protection.",
        scientific_logic="""1. Narrative Paradigm Directory Scaffolding:
   Maps structural beats to physical filesystem directories with zero cloud dependencies:
   $$\\text{Preset } K \\longrightarrow \\langle 01\\_\\text{Div}_1, 02\\_\\text{Div}_2, \\dots, N\\_\\text{Div}_N \\rangle$$

2. Path Traversal & Identifier Validation:
   Enforces token regex `^[A-Za-z0-9_-]+$`, rejecting directory traversal tokens (`..`, `/`, `\\`).

3. Manifest Serialization & Upward Discovery:
   Serializes `schema_version: "1.1"` in `manuscript.yaml` with bidirectional paradigm links.""",
        why_this_way="Different storytelling traditions (Western 3-Act, Eastern Kishōtenketsu, Romance beat sheets, Multi-POV parallel tracks) require different folder structures matching the author's mental model.",
        worldbuilding_relevance="Enables structured scaffolding of companion volumes, parallel lore threads, and episodic world chronologies.",
        storytelling_relevance="Aligns the physical folder layout directly with the chosen narrative pacing framework.",
        writing_relevance="Provides clean, distraction-free starter chapters and atomic division creation.",
        subfeatures=[
            {"name": "16 Built-in Presets", "rule": "Supports Classic Three-Act, Hero's Journey, Save the Cat, Kishōtenketsu, and 12 other presets.", "example": "arcanum scaffold MyNovel/Book-01 --structure heros_journey"},
            {"name": "Custom Divisions", "rule": "Scaffolds arbitrary named division lists with regex validation.", "example": "arcanum scaffold MyNovel/Book-01 --structure custom --divisions 'Prologue,Part-I,Part-II,Epilogue'"},
            {"name": "Structure Preset Introspection", "rule": "Lists and inspects all registered presets and division descriptions.", "example": "arcanum scaffold list / arcanum scaffold info kishotenketsu"},
        ],
        extension_guide="""Scaffold a volume or query structure presets:
```bash
# List all 16 presets
arcanum scaffold list

# View details for a preset
arcanum scaffold info kishotenketsu

# Scaffold a volume with custom structure
arcanum scaffold Manuscripts/Novel/Book-01 --structure story_circle
```""",
        advisory_guidance=[
            {"pattern": "Manuscript structure does not match default Three-Act model", "option_a": "Select matching preset from 16 registered narrative frameworks", "option_b": "Define custom division labels via `--divisions`", "option_c": "Retain default Three-Act structure"},
        ],
    ),

    "fs_utils": EngineSpec(
        name="fs_utils",
        category=EngineCategory.CORE,
        title="Atomic File System",
        description="Crash-safe atomic writes and storage operations",
        module_name="lib.fs_utils",
        cli_command="fs",
        studio_tab="Tools",
        logic_documentation="Guarantees zero data loss using POSIX atomic writes (temp file -> flush -> fsync -> os.replace -> parent dir fsync) with cross-platform file locking.",
        scientific_logic="""1. POSIX Atomic Write Lifecycle:
   $$\\text{Write to } .tmp\\_PID \\longrightarrow \\text{flush()} \\longrightarrow \\text{os.fsync()} \\longrightarrow \\text{os.replace()} \\longrightarrow \\text{parent dir fsync()}$$
   Guarantees that a power cut or crash never leaves a corrupted half-written file on disk.""",
        why_this_way="Direct unbuffered writes corrupt creative drafts during unexpected crashes. Atomic replacement guarantees file integrity.",
        worldbuilding_relevance="Protects irreplaceable creative world lore against power cuts or sudden crashes.",
        storytelling_relevance="Safeguards manuscript drafts, version forks, and chapter re-orderings.",
        writing_relevance="Ensures every keystroke and autosave is durable on disk.",
        subfeatures=[
            {"name": "Atomic Write Engine", "rule": "Writes files safely via temporary files and fsync.", "example": "from lib._bootstrap import atomic_write; atomic_write('chap.md', content)"},
            {"name": "Cross-Platform File Lock (ArcanumLock)", "rule": "Prevents race conditions during background exports and backups.", "example": "from lib.lockfile import ArcanumLock; with ArcanumLock('export'): pass"},
        ],
        extension_guide="""Use in Python scripts:
```python
from lib._bootstrap import atomic_write
atomic_write("Manuscript/Chapter_01.md", "# Chapter 1\\n\\nProse...")
```""",
        advisory_guidance=[
            {"pattern": "File lock contention", "option_a": "Wait with exponential backoff", "option_b": "Create conflict branch file (e.g. Chapter_conflict_2026.md)", "option_c": "Prompt user for manual lock override"},
        ],
    ),

    "migrate": EngineSpec(
        name="migrate",
        category=EngineCategory.CORE,
        title="Vault Migration",
        description="Schema upgrade engine for migrating older lore vaults and projects",
        module_name="lib.migrate",
        cli_command="migrate",
        aliases=["upgrade", "migrate"],
        studio_tab="Tools",
        logic_documentation="Upgrades legacy Obsidian vaults, frontmatter schemas, and manuscript folders to current Ars Arcanum standards with zero data destruction.",
        scientific_logic="""1. Non-Destructive Schema Migration Pipeline:
   Upgrades legacy frontmatter formats and folder structures with automatic backup creation before applying schema transforms.""",
        why_this_way="Creative projects span years; software updates must never break or alter historical lore notes.",
        worldbuilding_relevance="Preserves historical world lore notes across multi-year writing projects.",
        storytelling_relevance="Updates legacy chapter header formats to modern novelWriter / Markdown standards.",
        writing_relevance="Enables seamless project modernization without manual file editing.",
        subfeatures=[
            {"name": "Vault Schema Upgrader", "rule": "Migrates legacy frontmatter YAML tags to current standard.", "example": "arcanum migrate World/"},
            {"name": "Pre-Migration Safety Snapshot", "rule": "Creates compressed rollback archive before applying changes.", "example": "arcanum migrate World/ --snapshot"},
        ],
        extension_guide="""Run vault migration:
```bash
arcanum migrate World/
```""",
        advisory_guidance=[
            {"pattern": "Unrecognized legacy frontmatter", "option_a": "Migrate to standard YAML frontmatter schema", "option_b": "Preserve unmapped keys under custom_attributes", "option_c": "Leave legacy file untouched in archival branch"},
        ],
    ),
}

__all__ = ["ENGINES"]
