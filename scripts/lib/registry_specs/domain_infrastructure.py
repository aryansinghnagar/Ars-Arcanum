#!/usr/bin/env python3
"""
Domain Infrastructure Specifications for Ars Arcanum Registry.
"""
from __future__ import annotations

try:
    from lib.registry_base import EngineCategory, EngineSpec
except ImportError:
    from registry_base import EngineCategory, EngineSpec

ENGINES: dict[str, EngineSpec] = {
    "docx_sync": EngineSpec(
        name="docx_sync",
        category=EngineCategory.CORE,
        title="DOCX Bidirectional Sync",
        description="Two-way sync between Word .docx documents and Markdown with comment preservation",
        module_name="lib.docx_sync",
        cli_command="sync-docx",
        aliases=["docx", "sync", "docx-sync", "word-sync"],
        studio_tab="Editor",
        logic_documentation="Parses Word OpenXML AST structures to bidirectional synchronizer Markdown source, extracting margins comments into companion JSON sidecars and preserving in-situ scene directives.",
        scientific_logic="""1. OpenXML Bidirectional AST Translation:
   Converts Word paragraphs, styling, and comment anchors to Markdown while ignoring `<w:del>` tracked deletions and preserving mid-document `@scene:` directives.""",
        why_this_way="Many authors, editors, and beta readers work in Microsoft Word. Bidirectional sync provides seamless interoperability without losing metadata.",
        worldbuilding_relevance="Allows non-technical collaborators to edit lore or prose in standard word processors.",
        storytelling_relevance="Keeps scene-level metadata and margin critique notes anchored to exact prose paragraphs.",
        writing_relevance="Enables editing on mobile/tablets with Word and syncing back cleanly to Markdown.",
        subfeatures=[
            {"name": "Export to Word DOCX", "rule": "Exports markdown chapters into formatted DOCX manuscripts.", "example": "arcanum docx export Manuscript/01_Chapter.md"},
            {"name": "Import from Word DOCX", "rule": "Imports edited DOCX files and updates Markdown source.", "example": "arcanum docx import Manuscript/01_Chapter.docx"},
        ],
        extension_guide="""Sync Word file with Markdown:
```bash
arcanum docx sync Manuscript/
```""",
        advisory_guidance=[
            {"pattern": "Conflict detected between disk Markdown and imported DOCX", "option_a": "Create timestamped backup before merging", "option_b": "Inspect visual diff in redline view", "option_c": "Overwrite with imported DOCX content"},
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
        storytelling_relevance="Splits large monolithic documents into clean, manageable scene and chapter files.",
        writing_relevance="Eliminates the friction of migrating existing books into Ars Arcanum.",
        subfeatures=[
            {"name": "Scrivener Project Importer", "rule": "Extracts chapters and notes from .scriv binder files.", "example": "arcanum import scrivener ~/MyBook.scriv"},
            {"name": "Monolithic DOCX Splitter", "rule": "Splits single .docx novel file by Heading 1 chapter breaks.", "example": "arcanum import docx ~/Novel.docx -m Manuscript/"},
        ],
        extension_guide="""Import external manuscript:
```bash
arcanum import docx ~/MyDraft.docx -m ~/Manuscripts/MyBook/
```""",
        advisory_guidance=[
            {"pattern": "Monolithic document has no Heading 1 tags", "option_a": "Split chapters using regex pattern 'Chapter [0-9]+'", "option_b": "Import as single continuous chapter file", "option_c": "Prompt author for custom chapter separator string"},
        ],
    ),

    "diagnostics": EngineSpec(
        name="diagnostics",
        category=EngineCategory.CORE,
        title="System Diagnostics & Diagnostics Report",
        description="System verification and sanity checks (Python, pandoc, typst, git)",
        module_name="lib.diagnostics",
        cli_command="doctor",
        aliases=["doctor", "diagnostics", "check-env", "sanity-check", "status"],
        studio_tab="Diagnostics",
        logic_documentation="Probes the local operating system, verifying Python runtime version, standard library features, external publishing tools (Pandoc, Typst, Git, Ruff), directory permissions, and disk health.",
        scientific_logic="""1. Comprehensive System Health Probe:
   Executes sub-millisecond environment introspection, verifying runtime dependencies, directory write permissions, and compilation toolchain availability.""",
        why_this_way="Authors need instant feedback on whether their local system is properly configured for publishing and typesetting without technical troubleshooting.",
        worldbuilding_relevance="Ensures environment integrity before generating large static codices.",
        storytelling_relevance="Confirms system tools are ready for compilation.",
        writing_relevance="Provides 1-click health status of all required publishing tools.",
        subfeatures=[
            {"name": "Toolchain Probe", "rule": "Verifies availability of Python, Git, Pandoc, Typst, and Ruff.", "example": "arcanum doctor"},
            {"name": "JSON Diagnostics Report", "rule": "Emits machine-readable system diagnostic status.", "example": "arcanum doctor --json"},
        ],
        extension_guide="""Run system health check:
```bash
arcanum doctor
```""",
        advisory_guidance=[
            {"pattern": "Typst binary missing from PATH", "option_a": "Install Typst CLI via setup script", "option_b": "Use Pandoc fallback for PDF rendering", "option_c": "Export clean Markdown for external typesetting"},
        ],
    ),

    "config": EngineSpec(
        name="config",
        category=EngineCategory.CORE,
        title="Project Configuration",
        description="Manages configuration, user overrides, and workspace paths",
        module_name="lib.config",
        cli_command="config",
        aliases=["config", "settings", "constitution"],
        studio_tab="Diagnostics",
        logic_documentation="Loads and resolves layered platform configurations, merging global user preferences, project-level Authorial Constitutions, intent suppressions, and diagnostic severity thresholds.",
        scientific_logic="""1. Layered Hierarchical Configuration Model:
   Resolves configuration across system $\\to$ user global (`~/.config/ars-arcanum/config.json`) $\\to$ universe $\\to$ manuscript `constitution.yaml` with explicit intent overriding.""",
        why_this_way="Authors need full control over diagnostic rules, formatting defaults, and custom paths without hardcoded assumptions.",
        worldbuilding_relevance="Stores world-level axioms and rule suppressions.",
        storytelling_relevance="Maintains authorial intent directives across projects.",
        writing_relevance="Provides flexible, human-readable configuration files.",
        subfeatures=[
            {"name": "Config Viewer", "rule": "Displays active merged configuration settings.", "example": "arcanum config show"},
            {"name": "Constitution Editor", "rule": "Sets authorial rule suppressions and intent flags.", "example": "arcanum config set style.passive_voice allow"},
        ],
        extension_guide="""View active configuration:
```bash
arcanum config show
```""",
        advisory_guidance=[
            {"pattern": "Custom config key unrecognized", "option_a": "Validate against configuration schema", "option_b": "Preserve custom key in user metadata dictionary", "option_c": "Reset to default recommended configuration"},
        ],
    ),

    "cache": EngineSpec(
        name="cache",
        category=EngineCategory.CORE,
        title="Performance Cache",
        description="Accelerates repeat validation and parsing via modification-time indexing",
        module_name="lib.cache",
        cli_command="cache",
        aliases=["cache", "clear-cache", "purge-cache"],
        studio_tab="Diagnostics",
        logic_documentation="Maintains a thread-safe disk and in-memory cache keyed on file modification times (`mtime`) and file sizes, accelerating repeat queries, AST parsing, and cross-engine validation scans.",
        scientific_logic="""1. Mtime & Size Keyed AST Memoization:
   Caches serialized document ASTs and metadata dictionaries, bypassing disk I/O when filesystem `(mtime, size)` tuples are unchanged.""",
        why_this_way="Massive multi-book vaults with thousands of files require instant sub-second response times across all CLI and compilation operations.",
        worldbuilding_relevance="Accelerates repeated scans across large world bibles.",
        storytelling_relevance="Provides instantaneous chapter statistics without lag.",
        writing_relevance="Ensures fast, responsive CLI and compilation performance.",
        subfeatures=[
            {"name": "Cache Stats", "rule": "Displays cache hit ratios and disk footprint.", "example": "arcanum cache status"},
            {"name": "Cache Purge", "rule": "Clears all cached AST entries safely.", "example": "arcanum cache purge"},
        ],
        extension_guide="""Purge cache:
```bash
arcanum cache purge
```""",
        advisory_guidance=[
            {"pattern": "Cache size exceeds threshold", "option_a": "Automatically evict oldest LRU entries", "option_b": "Purge cache completely", "option_c": "Increase cache storage allocation in config"},
        ],
    ),

    "fs_utils": EngineSpec(
        name="fs_utils",
        category=EngineCategory.CORE,
        title="Atomic File System",
        description="Guarantees zero-data-loss atomic writes, path traversal defense, and cross-platform file locking",
        module_name="lib.fs_utils",
        cli_command="fs",
        aliases=["fs", "storage", "atomic-write", "locks"],
        studio_tab="Diagnostics",
        logic_documentation="Provides atomic POSIX/Windows file writes (`atomic_write`), directory recursion, filename token sanitization, and path-traversal / reserved-device defense across all disk operations.",
        scientific_logic="""1. Atomic Replace & Cross-Platform Concurrency:
   Writes to temporary file in target directory $\\to$ `flush()` $\\to$ `os.fsync()` $\\to$ `os.replace()` $\\to$ parent directory sync. Concurrency controlled via `fcntl.flock` on POSIX and `msvcrt.locking` on Windows.""",
        why_this_way="Power outages, sudden crashes, or concurrent processes must never corrupt an author's irreplaceable creative manuscript or lore database.",
        worldbuilding_relevance="Protects entire world vaults from disk write corruption.",
        storytelling_relevance="Guarantees every manuscript save is 100% atomic and safe.",
        writing_relevance="Provides total peace of mind for creative intellectual property.",
        subfeatures=[
            {"name": "Atomic Writer", "rule": "Executes fail-safe atomic writes to disk.", "example": "lib.fs_utils.atomic_write(path, content)"},
            {"name": "Lockfile Guard", "rule": "Acquires cross-platform ArcanumLock for critical operations.", "example": "with ArcanumLock(path): ..."},
        ],
        extension_guide="""Use atomic file writing in Python scripts:
```python
from lib.fs_utils import atomic_write
atomic_write("Chapter.md", "# Chapter 1\\nContent...")
```""",
        advisory_guidance=[
            {"pattern": "Target file locked by another process", "option_a": "Wait and retry acquisition with exponential backoff", "option_b": "Emit diagnostic warning and abort operation safely", "option_c": "Bypass lock with explicit force flag if stale"},
        ],
    ),

    "migrate": EngineSpec(
        name="migrate",
        category=EngineCategory.CORE,
        title="Vault Migration",
        description="Migrates legacy vault folder structures and frontmatter schemas to current standards",
        module_name="lib.migrate",
        cli_command="migrate",
        aliases=["migrate", "upgrade-vault", "schema-migrate"],
        studio_tab="Diagnostics",
        logic_documentation="Migrates legacy directory structures, frontmatter schemas, and deprecated configuration fields to the latest v0.1.0 specifications safely and non-destructively.",
        scientific_logic="""1. Deterministic Non-Destructive Schema Evolution:
   Validates vault health before migration, creates an atomic backup snapshot, and applies schema transformations with zero loss of custom metadata fields.""",
        why_this_way="As the authoring platform evolves, existing repositories must upgrade seamlessly without requiring manual file renaming or frontmatter editing.",
        worldbuilding_relevance="Upgrades legacy world bibles to standard Obsidian-compatible templates.",
        storytelling_relevance="Ensures manuscript directories align with modern compilation tools.",
        writing_relevance="Automates schema maintenance across large archives.",
        subfeatures=[
            {"name": "Vault Schema Migration", "rule": "Upgrades folder hierarchy and metadata schemas.", "example": "arcanum migrate ~/Worlds/Eldoria"},
            {"name": "Dry-Run Validator", "rule": "Previews all proposed changes before writing to disk.", "example": "arcanum migrate ~/Worlds/Eldoria --dry-run"},
        ],
        extension_guide="""Migrate vault schema:
```bash
arcanum migrate ~/Worlds/MyWorld/
```""",
        advisory_guidance=[
            {"pattern": "Unrecognized legacy frontmatter keys encountered", "option_a": "Preserve unrecognized keys in custom metadata block", "option_b": "Map to nearest standard schema key", "option_c": "Prompt user for manual field mapping"},
        ],
    ),
}

__all__ = ["ENGINES"]
