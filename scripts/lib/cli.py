#!/usr/bin/env python3
"""
Ars Arcanum Unified Python CLI Dispatcher (scripts/lib/cli.py)
=============================================================
Provides modular command parsing, alias routing, and delegation to core and craft engines.
"""

import difflib
import importlib
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger("arcanum.cli")

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

VERSION = "0.1.0"

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = SCRIPTS_DIR.parent if SCRIPTS_DIR.name == "scripts" else SCRIPTS_DIR
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


def print_banner():
    banner = f"""Ars Arcanum Unified CLI — v{VERSION}
Sovereign Authoring OS, Revision Tracker & Publishing Pipeline (Zero-Pip Stdlib)

Usage:
  arcanum <command> [arguments...]
  ars-arcanum <command> [arguments...]

🛡️  Sovereign Revision, Portfolio & Word Processing:
  compare <MS> [D_NEW] [D_OLD] Visual Redline changelog comparison between drafts (alias: diff, redline)
  revision-heatmap [MS]        Manuscript revision density & prose churn heatmap (alias: churn, heatmap)
  portfolio [DIR] [--html]     Multi-manuscript catalog dashboard & drafting velocity (alias: author-stats)
  theme-studio [opts]          Atmospheric visual presets & procedural typewriter audio studio (alias: themes, sound)
  word [MS]                    Open manuscript in Microsoft Word / LibreOffice (alias: writer)
  docx <build|sync|import|open> Manage Word .docx manuscript synchronization & comment extraction
  import <SOURCE> [options]    Import Scrivener, Word (.docx), or Markdown into sovereign vault
  new <type> <NAME> [opts]     Scaffold new project (type: manuscript | draft | world | universe | volume)
  draft <MS> [DRAFT_NAME]      Fork next manuscript draft version (alias: new draft, init-draft)

📚 Publishing & Compilation Pipeline:
  publish [MS] [options]       Compile to print PDF, EPUB, or DOCX (alias: export, compile)
  preflight [MS]               Pre-flight typesetting & compliance validator (Amazon KDP, IngramSpark)
  matter build [MS]            Generate modular front matter and back matter files (alias: frontmatter)
  codex <WORLD> [--html]       Compile static offline World Wiki encyclopedia (alias: wiki)
  omnibus <UNIVERSE> [--html]  Compile multi-volume series omnibus with unified TOC (alias: anthology)
  query [MS]                   Scaffold submission package: query letter, synopsis, tracker

🔒 Data Protection, Safety & Infrastructure:
  save [TARGET] [-m "note"]    Save an instant Git version milestone (alias: snapshot)
  backup <TARGET> [options]    Create a verified, standalone .tar.gz backup archive
  restore <ARCHIVE> [options]  Restore a project from a verified backup archive (with overwrite guards)
  doctor [options]             Run unified health & toolchain diagnostics (alias: check, diagnostics)
  config <show|set|get>        Manage global settings, Authorial Constitution & intent directives
  cache <scan|clear|purge>     Manage mtime-keyed fast performance cache
  fs [opts]                    Inspect atomic storage safety & lockfile status
  migrate <VAULT> [opts]       Safely migrate legacy folder schemas to current standards
  scope [TARGET] [opts]        Granular manuscript & lore scope targeting & diagnostic
  tool <list|enable|disable>   View and toggle sovereign core engines switchboard

📖 Master Craft References & External Tool Guides:
  doc [TOPIC]                  Display theoretical craft logic documentation & advisory guidance
  docs/guides/                 Comprehensive guides for 32 Obsidian plugins & external toolchain
                               (PolyGlot, Gramps, Wonderdraft, Celestia, Typst, Pandoc, Longform)

Global Options:
  -v, --version                Display Ars Arcanum version
  -h, --help                   Display this help menu
"""
    print(banner)


def dispatch_subcommand(module_name: str, argv: list[str]) -> int:
    """Dynamically load module and run its main() function."""
    try:
        mod = importlib.import_module(module_name)
        if hasattr(mod, "main"):
            old_argv = sys.argv
            sys.argv = [module_name, *argv]
            try:
                import inspect
                sig = inspect.signature(mod.main)
                res = mod.main(argv) if len(sig.parameters) > 0 else mod.main()
                return int(res) if res is not None and isinstance(res, (int, bool)) else 0
            finally:
                sys.argv = old_argv
        else:
            print(f"Error: Engine '{module_name}' does not expose main()", file=sys.stderr)
            return 1
    except SystemExit as se:
        return int(se.code) if se.code is not None and isinstance(se.code, int) else 0
    except Exception as e:
        print(f"Error executing '{module_name}': {e}", file=sys.stderr)
        return 1


def dispatch_script(script_name: str, argv: list[str]) -> int:
    """Dispatches a standalone script (Python or Bash)."""
    script_path = SCRIPTS_DIR / script_name
    if not script_path.is_file():
        script_path = PROJECT_ROOT / "scripts" / script_name
    if not script_path.is_file():
        print(f"Error: Script '{script_name}' not found.", file=sys.stderr)
        return 1

    if script_name.endswith(".py"):
        cmd = [sys.executable, str(script_path), *argv]
    else:
        # Bash script: find working bash executable on Windows or POSIX
        bash_exe = None
        if sys.platform == "win32":
            for c in [
                r"C:\Program Files\Git\bin\bash.exe",
                r"C:\Program Files\Git\usr\bin\bash.exe",
                r"C:\Program Files (x86)\Git\bin\bash.exe",
                shutil.which("bash"),
            ]:
                if c and os.path.isfile(c):
                    bash_exe = c
                    break
        bash_cmd = bash_exe or shutil.which("bash") or "bash"
        cmd = [bash_cmd, script_path.as_posix(), *argv]

    try:
        proc = subprocess.run(cmd)
        return proc.returncode
    except Exception as e:
        print(f"Error running '{script_name}': {e}", file=sys.stderr)
        return 1


def handle_engines_command(argv: list[str]) -> int:
    from lib.registry import EngineCategory, list_engines
    category = None
    if "--core" in argv:
        category = EngineCategory.CORE
    elif "--craft" in argv:
        category = EngineCategory.CRAFT

    engines = list_engines(category=category)
    print(f"Ars Arcanum Registered Plugins & Engines ({len(engines)} total):\n")
    print(f"{'Category':<10} {'Name':<22} {'Command':<18} {'Title / Description'}")
    print("-" * 80)
    for eng in sorted(engines, key=lambda e: (e.category.value, e.name)):
        cat_badge = f"[{eng.category.value.upper()}]"
        print(f"{cat_badge:<10} {eng.name:<22} {eng.cli_command:<18} {eng.title}")
    return 0


def handle_doc_command(argv: list[str]) -> int:
    import json

    from lib.registry import (
        format_engine_doc,
        format_unified_bibliography,
        get_all_engine_docs,
        get_engine,
        get_engine_docs,
        list_engines,
        search_engine_docs,
    )

    if not argv or argv[0] in ("--all", "-a", "all"):
        docs = get_all_engine_docs()
        print(f"🏛️  Ars Arcanum Author Craft Guide & Advisory Matrix ({len(docs)} Engines Available)\n")
        print("To view deep craft logic, scientific foundations, and advisory guidance for an engine, run:")
        print("  arcanum doc <ENGINE> [--math|--theory|--sources|--why|--examples|--subfeatures|--json]\n")
        print("To view the complete cross-engine master bibliography, run:")
        print("  arcanum doc bibliography [--craft|--core|--utility|--markdown|--json]\n")
        print(f"{'Command':<20} {'Category':<12} {'Engine Title':<32} {'Relevance Summary'}")
        print("=" * 95)
        for d in sorted(docs, key=lambda x: (x['category'], x['name'])):
            rel_summary = d['worldbuilding_relevance'][:40] + "..." if len(d['worldbuilding_relevance']) > 40 else d['worldbuilding_relevance']
            print(f"arcanum {d['cli_command']:<12} [{d['category'].upper():<10}] {d['title']:<32} {rel_summary}")
        return 0

    # Flag parsing
    mode = "full"
    is_json = False
    is_markdown = False
    cat_filter: str | None = None
    search_query = None
    cleaned_args: list[str] = []

    idx = 0
    while idx < len(argv):
        arg = argv[idx]
        if arg in ("--math", "--physics", "--logic"):
            mode = "math"
        elif arg in ("--sources", "--references", "--citations", "--bibliography", "--bib", "--theory", "--papers", "--reading"):
            mode = "sources"
        elif arg in ("--why", "--rationale"):
            mode = "why"
        elif arg in ("--examples", "--extension", "--how-to", "--guide"):
            mode = "examples"
        elif arg in ("--subfeatures", "--features"):
            mode = "subfeatures"
        elif arg in ("--advisory", "--resolution"):
            mode = "advisory"
        elif arg in ("--json", "-j"):
            is_json = True
        elif arg in ("--markdown", "--md"):
            is_markdown = True
        elif arg in ("--craft",):
            cat_filter = "craft"
        elif arg in ("--core",):
            cat_filter = "core"
        elif arg in ("--utility",):
            cat_filter = "utility"
        elif arg in ("--category", "-c"):
            if idx + 1 < len(argv):
                cat_filter = argv[idx + 1]
                idx += 1
        elif arg in ("--search", "-s", "--find"):
            if idx + 1 < len(argv):
                search_query = argv[idx + 1]
                idx += 1
            else:
                search_query = ""
        else:
            cleaned_args.append(arg)
        idx += 1

    if search_query is not None:
        results = search_engine_docs(search_query)
        if is_json:
            print(json.dumps([get_engine_docs(r.name) for r in results], indent=2))
            return 0
        print(f"🔍 Search results for '{search_query}' ({len(results)} matches):\n")
        for r in results:
            print(f" • [{r.category.value.upper()}] arcanum {r.cli_command:<14} {r.title}")
            desc_snip = r.description[:75] + "..." if len(r.description) > 75 else r.description
            print(f"   {desc_snip}\n")
        return 0

    target_full = " ".join(cleaned_args).strip().lower()

    # Consolidated Master Bibliography handler
    if target_full in ("bib", "bibliography", "citations", "sources", "references", "master-bibliography", "master_bibliography") or (not cleaned_args and mode == "sources"):
        fmt = "json" if is_json else ("markdown" if is_markdown else "text")
        print(format_unified_bibliography(category=cat_filter, format_type=fmt))
        return 0

    if not cleaned_args:
        docs = get_all_engine_docs()
        if is_json:
            print(json.dumps(docs, indent=2))
            return 0
        return handle_doc_command(["--all"])

    spec = get_engine(target_full)
    if not spec and len(cleaned_args) > 1:
        spec = get_engine(cleaned_args[0].strip().lower())

    if not spec:
        variants = {target_full, target_full.replace("-", "_"), target_full.replace("_", "-")}
        candidate_paths = []
        for v in variants:
            candidate_paths.extend([
                PROJECT_ROOT / "docs" / f"{v.upper()}.md",
                PROJECT_ROOT / "docs" / f"{v.lower()}.md",
                PROJECT_ROOT / "docs" / f"{v}.md",
                PROJECT_ROOT / "docs" / "guides" / f"{v.upper()}.md",
                PROJECT_ROOT / "docs" / "guides" / f"{v}.md",
            ])
        for candidate in candidate_paths:
            if candidate.is_file():
                content = candidate.read_text(encoding="utf-8", errors="replace")
                if is_json:
                    print(json.dumps({"name": target_full, "file": str(candidate), "content": content}, indent=2))
                    return 0
                print(f"📖 Ars Arcanum Craft Documentation: {candidate.name}\n" + "=" * 70 + "\n")
                print(content)
                return 0

        from difflib import get_close_matches
        all_names = [e.name for e in list_engines()] + [e.cli_command for e in list_engines()]
        for e in list_engines():
            all_names.extend(e.aliases)
            all_names.append(e.name.replace("_", "-"))
        matches = get_close_matches(target_full, all_names, n=1, cutoff=0.5)
        if not matches and len(cleaned_args) > 1:
            matches = get_close_matches(cleaned_args[0], all_names, n=1, cutoff=0.5)

        if matches:
            print(f"Error: No documentation found for engine: '{target_full}'. Did you mean 'arcanum doc {matches[0]}'?", file=sys.stderr)
        else:
            print(f"Error: No documentation found for engine: '{target_full}'. Run 'arcanum doc' to list all engines.", file=sys.stderr)
        return 1

    if is_json:
        doc_dict = get_engine_docs(spec.name)
        print(json.dumps(doc_dict, indent=2))
        return 0

    print(format_engine_doc(spec, mode=mode))
    return 0



try:
    from lib.cli_handlers import DISPATCH_TABLE, build_handlers_map
except ImportError:
    from cli_handlers import DISPATCH_TABLE, build_handlers_map

# Canonical alias for backward compatibility
_DISPATCH_TABLE = DISPATCH_TABLE


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    if not argv or argv[0] in ("-h", "--help", "help"):
        print_banner()
        return 0

    if argv[0] in ("-v", "--version", "version"):
        print(f"Ars Arcanum v{VERSION}")
        return 0

    cmd = argv[0].lower().strip()
    rest = argv[1:]

    handlers = build_handlers_map(
        dispatch_sub_fn=dispatch_subcommand,
        dispatch_script_fn=dispatch_script,
        handle_doc_fn=handle_doc_command,
        handle_engines_fn=handle_engines_command,
    )

    entry = DISPATCH_TABLE.get(cmd)
    if entry is None:
        # Check dynamic registry for user plugins or extended engines
        try:
            from lib.registry import discover_user_plugins, get_engine
            discover_user_plugins()
            dyn_spec = get_engine(cmd)
            if dyn_spec is not None and dyn_spec.module_name:
                return dispatch_subcommand(dyn_spec.module_name, rest)
        except Exception as e:
            logger.debug("Dynamic registry lookup failed for '%s': %s", cmd, e)

        # Unknown command — fuzzy match against the dispatch table keys
        matches = difflib.get_close_matches(cmd, DISPATCH_TABLE.keys(), n=1, cutoff=0.55)
        if matches:
            print(f"Error: Unknown command '{cmd}'. Did you mean '{matches[0]}'?", file=sys.stderr)
        else:
            print(f"Error: Unknown command '{cmd}'.", file=sys.stderr)
        print("Run 'arcanum --help' for available commands and examples.", file=sys.stderr)
        return 2

    dispatch_type = entry[0]

    if dispatch_type == "handler":
        handler_key = entry[1]
        handler_fn = handlers[handler_key]
        return handler_fn(rest)

    if dispatch_type == "module":
        module_name = entry[1]
        if len(entry) > 2:
            prefix = entry[2]
            return dispatch_subcommand(module_name, [prefix, *rest])
        return dispatch_subcommand(module_name, rest)

    if dispatch_type == "script":
        script_name = entry[1]
        if len(entry) > 2:
            prefix = entry[2]
            return dispatch_script(script_name, [prefix, *rest])
        return dispatch_script(script_name, rest)

    print(f"Error: Unknown command '{cmd}'.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())

