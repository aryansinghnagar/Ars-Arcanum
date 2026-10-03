#!/usr/bin/env python3
"""
Ars Arcanum Unified Python CLI Dispatcher (scripts/lib/cli.py)
=============================================================
Provides modular command parsing, alias routing, and delegation to core and craft engines.
"""

import difflib
import importlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

VERSION = "4.3.0"

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = SCRIPTS_DIR.parent if SCRIPTS_DIR.name == "scripts" else SCRIPTS_DIR
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


def print_banner():
    banner = f"""Ars Arcanum Unified CLI — v{VERSION}
An intuitive, fail-safe Linux writing and worldbuilding studio.

Usage:
  arcanum <command> [arguments...]
  ars-arcanum <command> [arguments...]

✍️  Core Authoring & Editorial Craft:
  hub [TARGET] [--port PORT]   Launch Sovereign Studio Desktop Hub & Telemetry Dashboard
  write [TARGET]               Open writing workspace in novelWriter or Obsidian (alias: open)
  studio [MS] [-w WORLD]       Standalone offline Zen drafting studio & in-situ lore drawer
  word [MS]                    Open manuscript in Microsoft Word / LibreOffice (alias: writer)
  docx <build|sync|import|open> Manage Word .docx manuscript synchronization
  import <SOURCE> [options]    Import Scrivener, Word (.docx), or Markdown into sovereign vault
  new <type> <NAME> [opts]     Scaffold new project (type: manuscript | draft | world | universe | volume)
  draft <MS> [DRAFT_NAME]      Fork next manuscript draft version (alias: new draft, init-draft)
  compare <MS> [D_NEW] [D_OLD] Visual Redline changelog comparison between drafts (alias: diff, redline)
  save [TARGET] [-m "note"]    Save an instant Git version milestone (alias: snapshot)
  publish [MS] [options]       Compile to print PDF, EPUB, or DOCX (alias: export, compile)
  preflight [MS]               Pre-flight typesetting & compliance validator (PUB-101)
  matter build [MS]            Generate modular front matter and back matter files (PUB-103)
  query [MS]                   Scaffold submission package: query letter, synopsis, tracker (PUB-106)
  polish typography [TARGET]   Normalize smart curly quotes, em-dashes, and ellipses (PRO-104)
  rag <QUERY> [opts]           Sovereign local semantic retrieval & LLM context synthesis (alias: query-lore)
  branch <TARGET> [opts]       Multi-POV narrative thread & convergence subway map (PLT-103)
  words [MS] [--md|--json|--pov] Show live word counts and chapter analytics (alias: report, count)
  pace [MS] [--pov|--html]     Analyze dialogue/action density & prose rhythm
  tension [MS] [--html]        Model chapter tension curve & narrative arcs
  plot [MS] [--html|--matrix]  Multi-track plot grid & subplot pacing matrix (PLT-101)
  structure [MS] [-p PARADIGM] Story paradigm enforcer: 3-Act, 8-Sequence, Kishotenketsu (PLT-102)
  scaffold [TARGET] [options]  Pluggable manuscript structure scaffolder across 16 presets (alias: presets)
  canvas [MS] [--html|--json]  Interactive visual story canvas & corkboard drag-and-drop
  timeline [MS|WORLD] [--html] Dual-track chronological vs narrative timeline synchronizer
  omnibus <UNIVERSE> [--html]  Compile multi-volume series omnibus with unified lore
  corpus <TARGET> [-f FORMAT]  Universal structured JSONL, SQLite & RAG dataset exporter
  ambient [PROFILE]            Focus soundscape loop player (PLT-106)
  portfolio [DIR] [--html]     Multi-manuscript catalog dashboard & drafting velocity (OPS-103)
  package [MS] [-t TARGET]     Multi-platform release packager: Reader, Submission, ARC (OPS-101)
  sprint [MS]                  Sovereign writing sprint timer & productivity analytics
  revision-heatmap [MS]        Manuscript revision density & churn heatmap
  resonance [CMD] [opts]       Universal Knowledge Mesh, Causal Cascade & Creative Spark bridges
  tip [opts]                   Dynamic non-obvious craft advice & engine wisdom (aliases: tips, hint)
  doc [ENGINE]                 Display educational craft logic documentation & advisory resolution guide (alias: guide, explain)

🪐 Universe, World Lore & Series Continuity:
  universe [NAME] [--list]     Create or list narrative universes in ~/Universes/
  world <NAME> [-u UNIVERSE]   Scaffold an Obsidian World Lore Vault
  cast [UNIVERSE] [--html|--md] Multi-volume Dramatis Personae & Universe Cast Matrix (alias: dramatis-personae)
  map <WORLD> [--html|--svg]   Interactive offline vector cartography & map editor (WOR-101)
  codex <WORLD> [--html]       Compile static offline World Wiki encyclopedia (WOR-102)
  series [TARGET] [--html]     Multi-book series continuity & character trait ledger (WOR-103)
  sim battle [options]         High-level tactical battle scenario planner (WOR-104)
  concordance <TARGET> [-b]    Generate Dramatis Personae & Glossary back-matter
  continuity [-w W -m MS]      Analyze character traits & narrative consistency (alias: check-continuity)
  faction [WORLD] [--html]     Geopolitical relationship matrix & diplomatic paradoxes
  economy [WORLD] [-m MS]      Macroeconomic currencies, commodity baskets & PPP rates
  causality [WORLD] [MS]       Multi-paradigm causal DAGs & time-travel validator
  ecology [WORLD] [--html]     Trophic energy pyramids (10% rule) & bestiary food-web
  magic-check [-w W -m MS]     Verify hard magic system constraints & axioms (advisory)
  magic-report [-w W]          Export comprehensive arcane constraint report
  prophecy [WORLD] [-m MS]     Prophecy lifecycle clauses & fulfillment verification
  genealogy <House|Char>       Compile dynastic lineage trees & Mermaid flowcharts
  lineage <House>              Display succession rank roster & claimants
  conlang <gen|mut|lex> <Lang> Conlang phonotactics, sound-law shift & lexicon
  calendar [WORLD] [--phases]  Multi-calendar/multi-era invariant chronology & arithmetic
  calc <subcommand>            Astrophysics, climate, battle, logistics & journey calculator
  audit <subcommand>           Prose audits: dialogue, echoes, voice, scenes, structure, tech, idioms, senses

🔒 Data Protection & Safety:
  backup <TARGET> [options]    Create a verified, standalone .tar.gz backup archive
  backup-dest <get|set|clear>  Configure secure secondary backup destination (alias: config backup-dest)
  restore <ARCHIVE> [options]  Restore a project from a verified backup archive

🩺 System Health & Tools:
  doctor [options]             Run unified health & toolchain diagnostics (alias: check)
  world-doctor <WORLD> [opts]  Run deep World Bible lore consistency checks
  cache <scan|wordcounts|clear> Manage mtime-keyed fast performance cache
  gui [--tab TAB]              Launch desktop Control Center (aliases: app, control-center)
  menu                         Launch interactive numbered terminal dashboard (alias: interactive)
  verify                       Run canonical 7-stage test harness
  setup [--dry-run]            Install core packages, typography fonts, and launchers
  uninstall [--dry-run]        Revert desktop launchers and system components

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
        print("  arcanum doc <ENGINE> [--math|--why|--examples|--subfeatures|--json]\n")
        print(f"{'Command':<20} {'Category':<12} {'Engine Title':<32} {'Relevance Summary'}")
        print("=" * 95)
        for d in sorted(docs, key=lambda x: (x['category'], x['name'])):
            rel_summary = d['worldbuilding_relevance'][:40] + "..." if len(d['worldbuilding_relevance']) > 40 else d['worldbuilding_relevance']
            print(f"arcanum {d['cli_command']:<12} [{d['category'].upper():<10}] {d['title']:<32} {rel_summary}")
        return 0

    # Flag parsing
    mode = "full"
    is_json = False
    search_query = None
    cleaned_args: list[str] = []

    idx = 0
    while idx < len(argv):
        arg = argv[idx]
        if arg in ("--math", "--theory", "--physics", "--logic"):
            mode = "math"
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

    if not cleaned_args:
        docs = get_all_engine_docs()
        if is_json:
            print(json.dumps(docs, indent=2))
            return 0
        return handle_doc_command(["--all"])

    target_full = " ".join(cleaned_args).strip().lower()
    spec = get_engine(target_full)
    if not spec and len(cleaned_args) > 1:
        spec = get_engine(cleaned_args[0].strip().lower())

    if not spec:
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



# ---------------------------------------------------------------------------
# Dispatch Table: Single source of truth for all CLI command routing.
# ---------------------------------------------------------------------------
# Each key is a command alias. The value is either:
#   ("module", "lib.module_name")         — dispatch_subcommand(module, rest)
#   ("module", "lib.module_name", [...])  — dispatch_subcommand(module, [..., *rest])
#   ("script", "script_name")             — dispatch_script(script, rest)
#   ("script", "script_name", [...])      — dispatch_script(script, [..., *rest])
#   ("handler", callable)                 — callable(rest)
# ---------------------------------------------------------------------------

def _handle_new(rest: list[str]) -> int:
    """Handle 'arcanum new <type> <NAME>' sub-dispatch."""
    if not rest:
        print("Usage: arcanum new <manuscript|draft|world|universe|volume> <NAME> [--structure STRUCTURE] [--divisions DIVISIONS] [options]", file=sys.stderr)
        return 2
    sub_type = rest[0].lower()
    sub_args = rest[1:]
    _new_dispatch: dict[str, tuple[str, list[str]]] = {
        "manuscript": ("arcanum", ["new", "manuscript"]),
        "novel": ("arcanum", ["new", "manuscript"]),
        "book": ("arcanum", ["new", "manuscript"]),
        "draft": ("arcanum", ["draft"]),
        "revision": ("arcanum", ["draft"]),
        "world": ("arcanum", ["new", "world"]),
        "lore": ("arcanum", ["new", "world"]),
        "vault": ("arcanum", ["new", "world"]),
        "universe": ("arcanum", ["new", "universe"]),
        "cosmos": ("arcanum", ["new", "universe"]),
        "volume": ("arcanum", ["add-volume"]),
        "book-volume": ("arcanum", ["add-volume"]),
    }
    entry = _new_dispatch.get(sub_type)
    if entry:
        return dispatch_script(entry[0], [*entry[1], *sub_args])
    print(f"Unknown project type '{sub_type}'. Choose: manuscript, draft, world, universe, volume.", file=sys.stderr)
    return 2


def _handle_matter(rest: list[str]) -> int:
    """Handle 'arcanum matter [build]' default sub-dispatch."""
    if rest and rest[0] == "build":
        return dispatch_subcommand("lib.frontmatter_builder", rest)
    return dispatch_subcommand("lib.frontmatter_builder", ["build", *rest])


def _handle_polish(rest: list[str]) -> int:
    """Handle 'arcanum polish [typography]' sub-dispatch."""
    if rest and rest[0] == "typography":
        return dispatch_subcommand("lib.typography_cleaner", rest[1:])
    return dispatch_subcommand("lib.typography_cleaner", rest)


def _handle_ambient(rest: list[str]) -> int:
    """Handle 'arcanum ambient [generate]' default sub-dispatch."""
    if rest and rest[0] == "generate":
        return dispatch_subcommand("lib.ambient", rest)
    return dispatch_subcommand("lib.ambient", ["generate", *rest])


def _handle_resonance(cmd: str, rest: list[str]) -> int:
    """Handle 'arcanum resonance|mesh|cascade|spark|bridge' sub-dispatch."""
    if cmd in ("mesh", "cascade", "spark", "bridge"):
        return dispatch_subcommand("lib.resonance", [cmd, *rest])
    return dispatch_subcommand("lib.resonance", rest)


def _handle_sim(rest: list[str]) -> int:
    """Handle 'arcanum sim [battle]' sub-dispatch."""
    if rest and rest[0] == "battle":
        return dispatch_subcommand("lib.tactical_sim", ["sim", *rest[1:]])
    return dispatch_subcommand("lib.tactical_sim", rest)


def _handle_magic(rest: list[str]) -> int:
    """Handle 'arcanum magic|magic-check' with default 'check' sub-action."""
    if rest and rest[0] in ("check", "report"):
        return dispatch_subcommand("lib.magic_system", rest)
    return dispatch_subcommand("lib.magic_system", ["check", *rest])


def _handle_conlang(cmd: str, rest: list[str]) -> int:
    """Handle 'arcanum conlang|family-tree|grammar|declension|conjugate|semantic-shift' sub-dispatch."""
    if cmd in ("family-tree", "grammar", "declension", "conjugate", "semantic-shift", "lexicon", "mutate", "generate"):
        return dispatch_subcommand("lib.conlang", [cmd, *rest])
    return dispatch_subcommand("lib.conlang", rest)


def _handle_calc(rest: list[str]) -> int:
    """Handle 'arcanum calc <subcommand>' sub-dispatch."""
    if not rest:
        print("Usage: arcanum calc <transit|time-dilation|orbit|comms|habitability|system-dossier|journey|battle|logistics|climate|trade> [args...]", file=sys.stderr)
        return 2
    sub = rest[0].lower()
    sub_args = rest[1:]
    if sub in ("transit", "time-dilation", "orbit", "comms", "habitability", "astro", "astrophysics", "system-dossier", "dossier"):
        if sub in ("astro", "astrophysics"):
            return dispatch_subcommand("lib.astrophysics", sub_args)
        return dispatch_subcommand("lib.astrophysics", [sub, *sub_args])
    if sub in ("journey", "expedition", "travel"):
        return dispatch_subcommand("lib.journey", sub_args)
    if sub in ("battle", "sim", "tactical", "combat"):
        return dispatch_subcommand("lib.tactical_sim", ["sim", *sub_args])
    if sub in ("logistics", "supply"):
        return dispatch_subcommand("lib.factions", ["logistics", *sub_args])
    if sub in ("climate", "weather", "insolation", "biomes"):
        return dispatch_subcommand("lib.climate", sub_args)
    if sub in ("trade", "arbitrage", "ppp"):
        return dispatch_subcommand("lib.economy", ["trade", *sub_args])
    print(f"Unknown calc mode '{sub}'. Choose: transit, time-dilation, orbit, comms, habitability, system-dossier, journey, battle, logistics, climate, trade.", file=sys.stderr)
    return 2


def _handle_audit(rest: list[str]) -> int:
    """Handle 'arcanum audit <subcommand>' sub-dispatch."""
    if not rest:
        return dispatch_script("arcanum_doctor.sh", [])
    sub = rest[0].lower()
    sub_args = rest[1:]
    _audit_dispatch: dict[str, tuple[str, list[str]]] = {
        "dialogue": ("lib.stylistics", ["dialogue"]),
        "tags": ("lib.stylistics", ["dialogue"]),
        "said-bookisms": ("lib.stylistics", ["dialogue"]),
        "echoes": ("lib.stylistics", ["echoes"]),
        "echo": ("lib.stylistics", ["echoes"]),
        "repetition": ("lib.stylistics", ["echoes"]),
        "rhythm": ("lib.stylistics", ["rhythm"]),
        "readability": ("lib.stylistics", ["rhythm"]),
        "prose": ("lib.stylistics", ["scan"]),
        "style": ("lib.stylistics", ["scan"]),
        "stylistics": ("lib.stylistics", ["scan"]),
        "voice": ("lib.voice", []),
        "voice-bleed": ("lib.voice", []),
        "scenes": ("lib.scene_mechanics", []),
        "scene": ("lib.scene_mechanics", []),
        "mru": ("lib.scene_mechanics", []),
        "structure": ("lib.structure", []),
        "paradigm": ("lib.structure", []),
        "idioms": ("lib.stylistics", ["idiom"]),
        "idiom": ("lib.stylistics", ["idiom"]),
        "eponyms": ("lib.stylistics", ["idiom"]),
        "senses": ("lib.senses", []),
        "sensory": ("lib.senses", []),
        "palette": ("lib.senses", []),
        "tech": ("lib.economy", ["tech"]),
        "technology": ("lib.economy", ["tech"]),
        "anachronisms": ("lib.economy", ["tech"]),
    }
    entry = _audit_dispatch.get(sub)
    if entry:
        return dispatch_subcommand(entry[0], [*entry[1], *sub_args])
    return dispatch_subcommand("lib.diagnostics", rest)


def _handle_pace(rest: list[str]) -> int:
    """Handle 'arcanum pace' with default sub-action prefix."""
    if rest and rest[0] in ("pace", "tension", "pov"):
        return dispatch_subcommand("lib.pacing", rest)
    return dispatch_subcommand("lib.pacing", ["pace", *rest])


def _handle_doctor(rest: list[str]) -> int:
    """Handle 'arcanum doctor' with world-doctor path detection."""
    if rest and not rest[0].startswith("-") and os.path.isdir(rest[0]):
        return dispatch_subcommand("lib.world_doctor", rest)
    return dispatch_subcommand("lib.diagnostics", rest)


# The canonical dispatch table — single source of truth for all command routing.
# Format: alias -> (dispatch_type, target, [optional_prefix_args])
_DISPATCH_TABLE: dict[str, tuple[str, ...]] = {
    # --- Core Authoring & Editorial Craft ---
    "doc": ("handler", "doc"), "docs": ("handler", "doc"), "explain": ("handler", "doc"),
    "guide": ("handler", "doc"), "craft-docs": ("handler", "doc"),
    "import": ("module", "lib.importer"), "importer": ("module", "lib.importer"),
    "import-manuscript": ("module", "lib.importer"), "scrivener-import": ("module", "lib.importer"),
    "write": ("script", "lib/ui_controller.py"), "open": ("script", "lib/ui_controller.py"),
    "word": ("module", "lib.docx_sync", "open"), "writer": ("module", "lib.docx_sync", "open"),
    "word-processor": ("module", "lib.docx_sync", "open"),
    "docx": ("module", "lib.docx_sync"), "docx-sync": ("module", "lib.docx_sync"),
    "sync-docx": ("module", "lib.docx_sync"),
    "new": ("handler", "new"), "create": ("handler", "new"),
    "draft": ("script", "arcanum", "draft"), "drafts": ("script", "arcanum", "draft"),
    "init-draft": ("script", "arcanum", "draft"), "new-draft": ("script", "arcanum", "draft"),
    "revision": ("script", "arcanum", "draft"),
    "compare": ("module", "lib.manuscript_diff"), "diff": ("module", "lib.manuscript_diff"),
    "redline": ("module", "lib.manuscript_diff"), "changelog": ("module", "lib.manuscript_diff"),
    "manuscript-diff": ("module", "lib.manuscript_diff"),
    "save": ("module", "lib.snapshot"), "snapshot": ("module", "lib.snapshot"),
    "snap": ("module", "lib.snapshot"), "commit": ("module", "lib.snapshot"),
    "publish": ("script", "arcanum", "export"), "export": ("script", "arcanum", "export"),
    "compile": ("script", "arcanum", "export"),
    "preflight": ("module", "lib.preflight"), "pre-flight": ("module", "lib.preflight"),
    "prepress": ("module", "lib.preflight"),
    "matter": ("handler", "matter"), "frontmatter": ("handler", "matter"),
    "backmatter": ("handler", "matter"), "matter-builder": ("handler", "matter"),
    "query": ("script", "init_query.py"), "synopsis": ("script", "init_query.py"),
    "agent": ("script", "init_query.py"),
    "polish": ("handler", "polish"), "clean-typography": ("handler", "polish"),
    "typography": ("handler", "polish"),
    "studio": ("module", "lib.zen_studio"), "zen": ("module", "lib.zen_studio"),
    "zen-studio": ("module", "lib.zen_studio"), "editor": ("module", "lib.zen_studio"),
    "corpus": ("module", "lib.corpus_export"), "corpus-export": ("module", "lib.corpus_export"),
    "export-corpus": ("module", "lib.corpus_export"), "rag-export": ("module", "lib.corpus_export"),
    "corpus-restore": ("module", "lib.corpus_export"),
    "rag": ("module", "lib.local_rag"), "query-lore": ("module", "lib.local_rag"),
    "semantic-search": ("module", "lib.local_rag"), "lore-query": ("module", "lib.local_rag"),
    "branch": ("module", "lib.branching_graph"), "branching": ("module", "lib.branching_graph"),
    "gamebook": ("module", "lib.branching_graph"), "interactive-fiction": ("module", "lib.branching_graph"),
    "branch-graph": ("module", "lib.branching_graph"), "subway-map": ("module", "lib.branching_graph"),
    "hub": ("module", "lib.studio_hub"), "dashboard": ("module", "lib.studio_hub"),
    "gui-web": ("module", "lib.studio_hub"), "studio-hub": ("module", "lib.studio_hub"),
    "causality": ("module", "lib.causality"), "causal": ("module", "lib.causality"),
    "time-travel": ("module", "lib.causality"), "ctc": ("module", "lib.causality"),
    "multiverse": ("module", "lib.causality"), "paradox": ("module", "lib.causality"),
    "prophecy": ("module", "lib.prophecy"), "prophecies": ("module", "lib.prophecy"),
    "oracle": ("module", "lib.prophecy"), "delphic": ("module", "lib.prophecy"),
    "arcane-inscription": ("module", "lib.prophecy"), "prophecy-matrix": ("module", "lib.prophecy"),
    "senses": ("module", "lib.senses"), "sensory": ("module", "lib.senses"),
    "immersion": ("module", "lib.senses"), "white-room": ("module", "lib.senses"),
    "palette": ("module", "lib.senses"),
    "sprint": ("module", "lib.writing_sprint"), "writing-sprint": ("module", "lib.writing_sprint"),
    "pomodoro": ("module", "lib.writing_sprint"), "session": ("module", "lib.writing_sprint"),
    "velocity": ("module", "lib.writing_sprint"),
    "revision-heatmap": ("module", "lib.revision_heatmap"), "churn": ("module", "lib.revision_heatmap"),
    "revision-density": ("module", "lib.revision_heatmap"), "draft-churn": ("module", "lib.revision_heatmap"),
    "heatmap": ("module", "lib.revision_heatmap"),
    "words": ("script", "arcanum", "words"), "wordcount": ("script", "arcanum", "words"),
    "report": ("script", "arcanum", "words"), "count": ("script", "arcanum", "words"),
    "stats": ("script", "arcanum", "words"),
    "pace": ("handler", "pace"), "pacing": ("handler", "pace"),
    "rhythm": ("handler", "pace"), "waveform": ("handler", "pace"),
    "tension": ("module", "lib.scene_mechanics"), "tension-arc": ("module", "lib.scene_mechanics"),
    "scene": ("module", "lib.scene_mechanics"), "scenes": ("module", "lib.scene_mechanics"),
    "swain": ("module", "lib.scene_mechanics"), "mru": ("module", "lib.scene_mechanics"),
    "plot": ("module", "lib.plot_matrix"), "plot-matrix": ("module", "lib.plot_matrix"),
    "subplot": ("module", "lib.plot_matrix"), "subplots": ("module", "lib.plot_matrix"),
    "matrix": ("module", "lib.plot_matrix"),
    "structure": ("module", "lib.structure"), "beats": ("module", "lib.structure"),
    "paradigm": ("module", "lib.structure"), "paradigms": ("module", "lib.structure"),
    "scaffold": ("module", "lib.manuscript_scaffold"), "scaffold-volume": ("module", "lib.manuscript_scaffold"),
    "manuscript-scaffold": ("module", "lib.manuscript_scaffold"),
    "structure-presets": ("module", "lib.manuscript_scaffold"), "presets": ("module", "lib.manuscript_scaffold"),
    "canvas": ("module", "lib.story_canvas"), "corkboard": ("module", "lib.story_canvas"),
    "story-map": ("module", "lib.story_canvas"), "story-canvas": ("module", "lib.story_canvas"),
    "timeline": ("module", "lib.timeline_sync"), "timeline-sync": ("module", "lib.timeline_sync"),
    "sync-timeline": ("module", "lib.timeline_sync"), "chronology": ("module", "lib.timeline_sync"),
    "omnibus": ("module", "lib.omnibus"), "compile-omnibus": ("module", "lib.omnibus"),
    "series-omnibus": ("module", "lib.omnibus"),
    "ambient": ("handler", "ambient"), "soundscape": ("handler", "ambient"),
    "noise": ("handler", "ambient"), "focus": ("handler", "ambient"),
    "binaural": ("handler", "ambient"), "focus-sound": ("handler", "ambient"),
    "portfolio": ("module", "lib.portfolio"), "catalog": ("module", "lib.portfolio"),
    "series-overview": ("module", "lib.portfolio"),
    "package": ("script", "package_distribution.py"), "dist": ("script", "package_distribution.py"),
    "bundle": ("script", "package_distribution.py"),
    "resonance": ("handler", "resonance"), "mesh": ("handler", "resonance"),
    "cascade": ("handler", "resonance"), "spark": ("handler", "resonance"),
    "bridge": ("handler", "resonance"), "ecosystem": ("handler", "resonance"),
    "synergy": ("handler", "resonance"),
    "tip": ("module", "lib.tips"), "tips": ("module", "lib.tips"),
    "craft-tip": ("module", "lib.tips"), "wisdom": ("module", "lib.tips"),
    "hint": ("module", "lib.tips"), "hints": ("module", "lib.tips"),
    "craft-tips": ("module", "lib.tips"), "advice": ("module", "lib.tips"),
    "help-tips": ("module", "lib.tips"),
    # --- Universe, World Lore & Series Continuity ---
    "universe": ("script", "arcanum", "universe"), "init-universe": ("script", "arcanum", "universe"),
    "cosmos": ("script", "arcanum", "universe"),
    "world": ("script", "arcanum", "world"), "init-world": ("script", "arcanum", "world"),
    "manuscript": ("script", "arcanum", "manuscript"), "init-manuscript": ("script", "arcanum", "manuscript"),
    "novel": ("script", "arcanum", "manuscript"),
    "volume": ("script", "arcanum", "add-volume"), "add-volume": ("script", "arcanum", "add-volume"),
    "add-book": ("script", "arcanum", "add-volume"), "new-book": ("script", "arcanum", "add-volume"),
    "map": ("module", "lib.cartography"), "cartography": ("module", "lib.cartography"),
    "vector-map": ("module", "lib.cartography"),
    "codex": ("module", "lib.codex_export"), "wiki": ("module", "lib.codex_export"),
    "export-codex": ("module", "lib.codex_export"),
    "series": ("module", "lib.series_continuity"), "series-continuity": ("module", "lib.series_continuity"),
    "ledger": ("module", "lib.series_continuity"),
    "sim": ("handler", "sim"), "tactical-sim": ("handler", "sim"),
    "battle": ("handler", "sim"), "combat": ("handler", "sim"), "tactical": ("handler", "sim"),
    "cast": ("module", "lib.dramatis_personae"), "dramatis-personae": ("module", "lib.dramatis_personae"),
    "dramatis": ("module", "lib.dramatis_personae"), "characters-cast": ("module", "lib.dramatis_personae"),
    "concordance": ("module", "lib.concordance"), "glossary": ("module", "lib.concordance"),
    "index": ("module", "lib.concordance"),
    "continuity": ("module", "lib.continuity"), "check-continuity": ("module", "lib.continuity"),
    "traits": ("module", "lib.continuity"),
    "faction": ("module", "lib.factions"), "factions": ("module", "lib.factions"),
    "diplomacy": ("module", "lib.factions"),
    "economy": ("module", "lib.economy"), "currencies": ("module", "lib.economy"),
    "currency": ("module", "lib.economy"), "prices": ("module", "lib.economy"),
    "ecology": ("module", "lib.ecology"), "foodweb": ("module", "lib.ecology"),
    "bestiary": ("module", "lib.ecology"),
    "magic": ("handler", "magic"), "magic-check": ("handler", "magic"),
    "magic-report": ("handler", "magic"),
    "arcana": ("handler", "magic"), "spells": ("handler", "magic"),
    "council": ("module", "lib.council"), "editorial-council": ("module", "lib.council"),
    "dossier": ("module", "lib.council"), "council-audit": ("module", "lib.council"),
    "audio-proof": ("module", "lib.audio_proof"), "tts-proof": ("module", "lib.audio_proof"),
    "speech-proof": ("module", "lib.audio_proof"), "audio-export": ("module", "lib.audio_proof"),
    "cosmology": ("module", "lib.cosmology"), "pantheon": ("module", "lib.cosmology"),
    "theology": ("module", "lib.cosmology"), "heresy": ("module", "lib.cosmology"),
    "deities": ("module", "lib.cosmology"),
    "genealogy": ("module", "lib.genealogy"),
    "lineage": ("module", "lib.genealogy", "lineage"), "dynasty": ("module", "lib.genealogy", "lineage"),
    "conlang": ("handler", "conlang"), "lexicon": ("handler", "conlang"),
    "linguistics": ("handler", "conlang"), "phonotactics": ("handler", "conlang"),
    "family-tree": ("handler", "conlang"), "grammar": ("handler", "conlang"),
    "declension": ("handler", "conlang"), "conjugate": ("handler", "conlang"),
    "semantic-shift": ("handler", "conlang"),
    "calendar": ("module", "lib.calendar"), "calendars": ("module", "lib.calendar"),
    "moons": ("module", "lib.calendar"), "ephemeris": ("module", "lib.calendar"),
    "calc": ("handler", "calc"), "calculator": ("handler", "calc"),
    "astro": ("module", "lib.astrophysics"), "astrophysics": ("module", "lib.astrophysics"),
    "orbital": ("module", "lib.astrophysics"),
    "climate": ("module", "lib.climate"), "weather": ("module", "lib.climate"),
    "biomes": ("module", "lib.climate"), "insolation": ("module", "lib.climate"),
    "journey": ("module", "lib.journey"), "travel": ("module", "lib.journey"),
    "expedition": ("module", "lib.journey"), "logistics": ("module", "lib.journey"),
    "voice": ("module", "lib.voice"), "voice-bleed": ("module", "lib.voice"),
    "idiolect": ("module", "lib.voice"), "stylometry": ("module", "lib.voice"),
    "style": ("module", "lib.stylistics", "scan"), "stylistics": ("module", "lib.stylistics", "scan"),
    "polish-style": ("module", "lib.stylistics", "scan"), "readability": ("module", "lib.stylistics", "scan"),
    "audit": ("handler", "audit"),
    # --- Data Protection & Safety ---
    "backup": ("module", "lib.backup"), "backup-world": ("module", "lib.backup"),
    "backup-dest": ("module", "lib.config", "backup-dest"),
    "backup-destination": ("module", "lib.config", "backup-dest"),
    "config": ("module", "lib.config"), "settings": ("module", "lib.config"),
    "preferences": ("module", "lib.config"),
    "restore": ("module", "lib.restore"), "restore-world": ("module", "lib.restore"),
    "fs": ("module", "lib.fs_utils"), "fs-utils": ("module", "lib.fs_utils"),
    "atomic-storage": ("module", "lib.fs_utils"), "atomic-fs": ("module", "lib.fs_utils"),
    # --- System Health & Diagnostics ---
    "doctor": ("handler", "doctor"), "check": ("handler", "doctor"),
    "diagnostics": ("handler", "doctor"), "health": ("handler", "doctor"),
    "world-doctor": ("module", "lib.world_doctor"), "doctor-world": ("module", "lib.world_doctor"),
    "lore-check": ("module", "lib.world_doctor"),
    "cache": ("module", "lib.cache"), "cache-engine": ("module", "lib.cache"),
    "cache-clear": ("module", "lib.cache", "clear"),
    "cache-scan": ("module", "lib.cache", "scan"),
    "migrate": ("module", "lib.migrate"), "upgrade": ("module", "lib.migrate"),
    "engines": ("handler", "engines"),
    "gui": ("script", "arcanum_app.py"), "control-center": ("script", "arcanum_app.py"),
    "app": ("script", "arcanum_app.py"), "ui": ("script", "arcanum_app.py"),
    "menu": ("script", "arcanum", "menu"), "interactive": ("script", "arcanum", "menu"),
    "dashboard-cli": ("script", "arcanum", "menu"),
    "verify": ("script", "verify.sh"), "test": ("script", "verify.sh"),
    "tests": ("script", "verify.sh"),
    "setup": ("script", "setup_arcanum.sh"),
    "uninstall": ("script", "arcanum", "uninstall"), "remove": ("script", "arcanum", "uninstall"),
}

# Handler dispatch map for commands requiring custom logic
_HANDLERS: dict[str, object] = {
    "doc": handle_doc_command,
    "new": _handle_new,
    "matter": _handle_matter,
    "polish": _handle_polish,
    "ambient": _handle_ambient,
    "sim": _handle_sim,
    "magic": _handle_magic,
    "calc": _handle_calc,
    "audit": _handle_audit,
    "pace": _handle_pace,
    "doctor": _handle_doctor,
    "engines": handle_engines_command,
    "resonance": _handle_resonance,
    "conlang": _handle_conlang,
}


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

    entry = _DISPATCH_TABLE.get(cmd)
    if entry is None:
        # Unknown command — fuzzy match against the dispatch table keys
        matches = difflib.get_close_matches(cmd, _DISPATCH_TABLE.keys(), n=1, cutoff=0.55)
        if matches:
            print(f"Error: Unknown command '{cmd}'. Did you mean '{matches[0]}'?", file=sys.stderr)
        else:
            print(f"Error: Unknown command '{cmd}'.", file=sys.stderr)
        print("Run 'arcanum --help' for available commands and examples.", file=sys.stderr)
        return 2

    dispatch_type = entry[0]

    if dispatch_type == "handler":
        handler_key = entry[1]
        handler_fn = _HANDLERS[handler_key]  # type: ignore[index]
        # Handlers that need the original cmd for sub-dispatch (resonance, conlang)
        if handler_key in ("resonance", "conlang"):
            return handler_fn(cmd, rest)  # type: ignore[operator]
        return handler_fn(rest)  # type: ignore[operator]

    if dispatch_type == "module":
        module_name = entry[1]
        if len(entry) > 2:
            # Has a prefix argument to prepend
            prefix = entry[2]
            return dispatch_subcommand(module_name, [prefix, *rest])  # type: ignore[arg-type]
        return dispatch_subcommand(module_name, rest)  # type: ignore[arg-type]

    if dispatch_type == "script":
        script_name = entry[1]
        if len(entry) > 2:
            prefix = entry[2]
            return dispatch_script(script_name, [prefix, *rest])  # type: ignore[arg-type]
        return dispatch_script(script_name, rest)  # type: ignore[arg-type]

    # Should never reach here
    print(f"Error: Unknown command '{cmd}'.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
