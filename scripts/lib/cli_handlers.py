#!/usr/bin/env python3
"""
Ars Arcanum Unified CLI Command Handlers & Dispatch Table (scripts/lib/cli_handlers.py)
======================================================================================
Defines specialized sub-command handlers, parameter normalization, advisory docs
redirection for retired engines, and the canonical dispatch routing table.
"""

from __future__ import annotations

import sys
from collections.abc import Callable


def _handle_new(dispatch_script_fn: Callable[[str, list[str]], int], rest: list[str]) -> int:
    """Handle 'arcanum new <type> <NAME>' sub-dispatch."""
    if not rest:
        print(
            "Usage: arcanum new <manuscript|draft|world|universe|volume> <NAME> [options]",
            file=sys.stderr,
        )
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
        return dispatch_script_fn(entry[0], [*entry[1], *sub_args])
    print(f"Unknown project type '{sub_type}'. Choose: manuscript, draft, world, universe, volume.", file=sys.stderr)
    return 2


def _handle_matter(dispatch_sub_fn: Callable[[str, list[str]], int], rest: list[str]) -> int:
    """Handle 'arcanum matter [build]' default sub-dispatch."""
    if rest and rest[0] == "build":
        return dispatch_sub_fn("lib.frontmatter_builder", rest)
    return dispatch_sub_fn("lib.frontmatter_builder", ["build", *rest])


def _handle_pruned(doc_name: str, alternative_tool: str = "") -> int:
    """Provides craft reference advisory message and points to plugins/docs."""
    alt_msg = f"Recommended Tool / Plugin: {alternative_tool}\n" if alternative_tool else ""
    print(
        f"🏛️  Ars Arcanum Craft Studio — Reference Doctrine ({doc_name.upper()})\n"
        f"----------------------------------------------------------------------\n"
        f"Note: The standalone '{doc_name.lower()}' engine has transitioned to our\n"
        f"Tool-First architecture, delegating to specialized offline tools & Obsidian plugins.\n\n"
        f"{alt_msg}"
        f"For theoretical foundations, formulas, rubrics, and workflows:\n"
        f"  • Read docs/{doc_name.upper()}.md\n"
        f"  • See docs/guides/EXTERNAL_TOOLS_AND_PLUGINS.md\n"
        f"  • Or run: arcanum doc {doc_name.lower()}"
    )
    return 0


def _handle_tool(rest: list[str]) -> int:
    """Handle 'arcanum tool <list|enable|disable|status>' sub-dispatch."""
    from lib.config import get_authorial_policy, get_disabled_engines, set_engine_enabled
    from lib.registry import list_engines

    if not rest or rest[0] in ("list", "ls"):
        disabled = set(get_disabled_engines())
        engines = list_engines()
        print(f"Ars Arcanum Tool Switchboard ({len(engines)} sovereign core engines):\n")
        print(f"{'Status':<12} {'Name':<24} {'Command':<18} {'Title'}")
        print("-" * 80)
        for eng in sorted(engines, key=lambda e: e.name):
            status = "❌ DISABLED" if eng.name in disabled else "✓ ENABLED"
            print(f"{status:<12} {eng.name:<24} {eng.cli_command:<18} {eng.title}")
        return 0

    sub = rest[0].lower()
    if sub == "enable":
        if len(rest) < 2:
            print("Usage: arcanum tool enable <ENGINE_NAME>", file=sys.stderr)
            return 2
        name = rest[1]
        set_engine_enabled(name, True)
        print(f"✓ Tool '{name}' is now ENABLED.")
        return 0

    if sub == "disable":
        if len(rest) < 2:
            print("Usage: arcanum tool disable <ENGINE_NAME>", file=sys.stderr)
            return 2
        name = rest[1]
        set_engine_enabled(name, False)
        print(f"✓ Tool '{name}' is now DISABLED in authorial policy.")
        return 0

    if sub in ("status", "policy"):
        pol = get_authorial_policy()
        print("🏛️ Ars Arcanum Authorial Sovereignty Policy:")
        for k, v in pol.items():
            print(f"  • {k}: {v}")
        return 0

    print(f"Unknown tool action '{sub}'. Choose: list, enable, disable, status.", file=sys.stderr)
    return 2


def _handle_doctor(dispatch_sub_fn: Callable[[str, list[str]], int], rest: list[str]) -> int:
    """Handle 'arcanum doctor' diagnostics dispatch."""
    return dispatch_sub_fn("lib.diagnostics", rest)


# The canonical dispatch table — single source of truth for all command routing.
DISPATCH_TABLE: dict[str, tuple[str, ...]] = {
    # --- Switchboard & System Management ---
    "tool": ("handler", "tool"), "tools": ("handler", "tool"),
    "switchboard": ("handler", "tool"), "plugins": ("handler", "tool"),
    "doc": ("handler", "doc"), "docs": ("handler", "doc"), "explain": ("handler", "doc"),
    "guide": ("handler", "doc"), "craft-docs": ("handler", "doc"),
    "new": ("handler", "new"), "create": ("handler", "new"),

    # --- Retained Core Engines: Revision & Editorial ---
    "compare": ("module", "lib.manuscript_diff"), "diff": ("module", "lib.manuscript_diff"),
    "redline": ("module", "lib.manuscript_diff"), "changelog": ("module", "lib.manuscript_diff"),
    "manuscript-diff": ("module", "lib.manuscript_diff"),
    "revision-heatmap": ("module", "lib.revision_heatmap"), "churn": ("module", "lib.revision_heatmap"),
    "revision-density": ("module", "lib.revision_heatmap"), "draft-churn": ("module", "lib.revision_heatmap"),
    "heatmap": ("module", "lib.revision_heatmap"),

    # --- Retained Core Engines: Portfolio & Word Processing ---
    "portfolio": ("module", "lib.portfolio"), "catalog": ("module", "lib.portfolio"),
    "series-overview": ("module", "lib.portfolio"), "author-stats": ("module", "lib.portfolio"),
    "docx": ("module", "lib.docx_sync"), "docx-sync": ("module", "lib.docx_sync"),
    "sync-docx": ("module", "lib.docx_sync"),
    "word": ("module", "lib.docx_sync", "open"), "writer": ("module", "lib.docx_sync", "open"),
    "word-processor": ("module", "lib.docx_sync", "open"),
    "import": ("module", "lib.importer"), "importer": ("module", "lib.importer"),
    "import-manuscript": ("module", "lib.importer"), "scrivener-import": ("module", "lib.importer"),

    # --- Retained Core Engines: Publishing Pipeline ---
    "preflight": ("module", "lib.preflight"), "pre-flight": ("module", "lib.preflight"),
    "prepress": ("module", "lib.preflight"),
    "matter": ("handler", "matter"), "frontmatter": ("handler", "matter"),
    "backmatter": ("handler", "matter"), "matter-builder": ("handler", "matter"),
    "codex": ("module", "lib.codex_export"), "wiki": ("module", "lib.codex_export"),
    "export-codex": ("module", "lib.codex_export"),
    "omnibus": ("module", "lib.omnibus"), "compile-omnibus": ("module", "lib.omnibus"),
    "series-omnibus": ("module", "lib.omnibus"),

    # --- Retained Core Engines: Infrastructure & Safety ---
    "save": ("module", "lib.snapshot"), "snapshot": ("module", "lib.snapshot"),
    "snap": ("module", "lib.snapshot"), "commit": ("module", "lib.snapshot"),
    "backup": ("module", "lib.backup"), "backup-world": ("module", "lib.backup"),
    "restore": ("module", "lib.restore"), "restore-world": ("module", "lib.restore"),
    "fs": ("module", "lib.fs_utils"), "fs-utils": ("module", "lib.fs_utils"),
    "atomic-storage": ("module", "lib.fs_utils"), "atomic-fs": ("module", "lib.fs_utils"),
    "config": ("module", "lib.config"), "settings": ("module", "lib.config"),
    "preferences": ("module", "lib.config"), "constitution": ("module", "lib.config"),
    "cache": ("module", "lib.cache"), "cache-engine": ("module", "lib.cache"),
    "cache-clear": ("module", "lib.cache", "clear"), "cache-scan": ("module", "lib.cache", "scan"),
    "migrate": ("module", "lib.migrate"), "upgrade": ("module", "lib.migrate"),
    "doctor": ("handler", "doctor"), "check": ("handler", "doctor"),
    "diagnostics": ("handler", "doctor"), "health": ("handler", "doctor"), "status": ("handler", "doctor"),
    "audit": ("handler", "doctor"),
    "scope": ("module", "lib.scope"), "target-scope": ("module", "lib.scope"),
    "engine-scope": ("module", "lib.scope"),

    # --- Script Shell Entry Points ---
    "draft": ("script", "arcanum", "draft"), "drafts": ("script", "arcanum", "draft"),
    "publish": ("script", "arcanum", "export"), "export": ("script", "arcanum", "export"),
    "compile": ("script", "arcanum", "export"),
    "universe": ("script", "arcanum", "universe"), "cosmos": ("script", "arcanum", "universe"),
    "world": ("script", "arcanum", "world"), "init-world": ("script", "arcanum", "world"),
    "manuscript": ("script", "arcanum", "manuscript"), "novel": ("script", "arcanum", "manuscript"),
    "volume": ("script", "arcanum", "add-volume"), "add-volume": ("script", "arcanum", "add-volume"),
    "words": ("script", "arcanum", "words"), "wordcount": ("script", "arcanum", "words"),
    "query": ("script", "init_query.py"), "synopsis": ("script", "init_query.py"),
    "verify": ("script", "verify.sh"), "test": ("script", "verify.sh"),
    "setup": ("script", "setup_arcanum.sh"),
    "engines": ("handler", "engines"),

    # --- Retired Engines Handled Gracefully via Craft Doctrine Guidance ---
    "astro": ("handler", "pruned_astro"), "astrophysics": ("handler", "pruned_astro"),
    "orbital": ("handler", "pruned_astro"), "calc": ("handler", "pruned_astro"),
    "climate": ("handler", "pruned_climate"), "weather": ("handler", "pruned_climate"),
    "biomes": ("handler", "pruned_climate"),
    "calendar": ("handler", "pruned_calendar"), "calendars": ("handler", "pruned_calendar"),
    "moons": ("handler", "pruned_calendar"), "ephemeris": ("handler", "pruned_calendar"),
    "ecology": ("handler", "pruned_ecology"), "foodweb": ("handler", "pruned_ecology"),
    "bestiary": ("handler", "pruned_ecology"),
    "map": ("handler", "pruned_cartography"), "cartography": ("handler", "pruned_cartography"),
    "journey": ("handler", "pruned_journey"), "travel": ("handler", "pruned_journey"),
    "expedition": ("handler", "pruned_journey"),
    "cosmology": ("handler", "pruned_cosmology"), "pantheon": ("handler", "pruned_cosmology"),
    "theology": ("handler", "pruned_cosmology"), "heresy": ("handler", "pruned_cosmology"),
    "structure": ("handler", "pruned_structure"), "beats": ("handler", "pruned_structure"),
    "paradigm": ("handler", "pruned_structure"), "paradigms": ("handler", "pruned_structure"),
    "scaffold": ("handler", "pruned_structure"), "manuscript-scaffold": ("handler", "pruned_structure"),
    "plot": ("handler", "pruned_plot"), "plot-matrix": ("handler", "pruned_plot"),
    "subplot": ("handler", "pruned_plot"), "matrix": ("handler", "pruned_plot"),
    "canvas": ("handler", "pruned_canvas"), "corkboard": ("handler", "pruned_canvas"),
    "story-canvas": ("handler", "pruned_canvas"),
    "causality": ("handler", "pruned_causality"), "causal": ("handler", "pruned_causality"),
    "time-travel": ("handler", "pruned_causality"), "paradox": ("handler", "pruned_causality"),
    "timeline": ("handler", "pruned_timeline"), "timeline-sync": ("handler", "pruned_timeline"),
    "prophecy": ("handler", "pruned_prophecy"), "oracle": ("handler", "pruned_prophecy"),
    "sprint": ("handler", "pruned_sprint"), "writing-sprint": ("handler", "pruned_sprint"),
    "dramatis_personae": ("handler", "pruned_cast"), "cast": ("handler", "pruned_cast"),
    "dramatis": ("handler", "pruned_cast"),
    "conlang": ("handler", "pruned_conlang"), "lexicon": ("handler", "pruned_conlang"),
    "linguistics": ("handler", "pruned_conlang"), "phonotactics": ("handler", "pruned_conlang"),
    "genealogy": ("handler", "pruned_genealogy"), "lineage": ("handler", "pruned_genealogy"),
    "dynasty": ("handler", "pruned_genealogy"),
    "faction": ("handler", "pruned_faction"), "factions": ("handler", "pruned_faction"),
    "economy": ("handler", "pruned_economy"), "currencies": ("handler", "pruned_economy"),
    "sim": ("handler", "pruned_tactical"), "tactical-sim": ("handler", "pruned_tactical"),
    "battle": ("handler", "pruned_tactical"), "combat": ("handler", "pruned_tactical"),
    "magic": ("handler", "pruned_magic"), "magic-check": ("handler", "pruned_magic"),
    "continuity": ("handler", "pruned_continuity"), "check-continuity": ("handler", "pruned_continuity"),
    "series": ("handler", "pruned_series"), "series-continuity": ("handler", "pruned_series"),
    "ledger": ("handler", "pruned_series"),
    "polish": ("handler", "pruned_typography"), "clean-typography": ("handler", "pruned_typography"),
    "typography": ("handler", "pruned_typography"),
    "hub": ("handler", "pruned_hub"), "studio-hub": ("handler", "pruned_hub"), "dashboard": ("handler", "pruned_hub"),
    "studio": ("handler", "pruned_zen"), "zen": ("handler", "pruned_zen"), "zen-studio": ("handler", "pruned_zen"),
    "ambient": ("handler", "pruned_ambient"), "binaural": ("handler", "pruned_ambient"),
    "search": ("handler", "pruned_search"), "vault-search": ("handler", "pruned_search"), "rag": ("handler", "pruned_search"),
    "corpus": ("handler", "pruned_corpus"), "corpus-export": ("handler", "pruned_corpus"),
    "world-doctor": ("handler", "pruned_doctor"), "doctor-world": ("handler", "pruned_doctor"),
    "resonance": ("handler", "pruned_resonance"), "mesh": ("handler", "pruned_resonance"),
    "tip": ("handler", "pruned_tips"), "tips": ("handler", "pruned_tips"), "craft-tip": ("handler", "pruned_tips"),
    "branch": ("handler", "pruned_branch"), "branching": ("handler", "pruned_branch"),
    "pace": ("handler", "pruned_pacing"), "pacing": ("handler", "pruned_pacing"),
    "tension": ("handler", "pruned_scene_mechanics"), "scene": ("handler", "pruned_scene_mechanics"),
    "senses": ("handler", "pruned_senses"), "sensory": ("handler", "pruned_senses"),
    "voice": ("handler", "pruned_voice"), "style": ("handler", "pruned_stylistics"),
    "concordance": ("handler", "pruned_concordance"), "council": ("handler", "pruned_council"),
    "audio-proof": ("handler", "pruned_audio_proof"), "package": ("handler", "pruned_package"),
}


def build_handlers_map(
    dispatch_sub_fn: Callable[[str, list[str]], int],
    dispatch_script_fn: Callable[[str, list[str]], int],
    handle_doc_fn: Callable[[list[str]], int],
    handle_engines_fn: Callable[[list[str]], int],
) -> dict[str, Callable[..., int]]:
    """Builds the runtime handler mapping with injected dispatch callbacks."""
    return {
        "tool": _handle_tool,
        "doc": handle_doc_fn,
        "new": lambda rest: _handle_new(dispatch_script_fn, rest),
        "matter": lambda rest: _handle_matter(dispatch_sub_fn, rest),
        "doctor": lambda rest: _handle_doctor(dispatch_sub_fn, rest),
        "engines": handle_engines_fn,
        "pruned_astro": lambda args: _handle_pruned("ASTROPHYSICS", "Celestia / StarGen / SpinCalc"),
        "pruned_climate": lambda args: _handle_pruned("CLIMATE", "Azgaar's Fantasy Map Generator"),
        "pruned_calendar": lambda args: _handle_pruned("CALENDAR", "Obsidian Calendarium / Aprils Timelines"),
        "pruned_ecology": lambda args: _handle_pruned("ECOLOGY", "Obsidian Canvas"),
        "pruned_cartography": lambda args: _handle_pruned("CARTOGRAPHY", "Wonderdraft / Obsidian Leaflet"),
        "pruned_journey": lambda args: _handle_pruned("JOURNEY", "Obsidian Leaflet / Wonderdraft"),
        "pruned_cosmology": lambda args: _handle_pruned("COSMOLOGY", "Obsidian Graph View / Dataview"),
        "pruned_structure": lambda args: _handle_pruned("STRUCTURE", "Longform / Noveler / StoryLine"),
        "pruned_plot": lambda args: _handle_pruned("PLOT_MATRIX", "Noveler / StoryLine / Canvas"),
        "pruned_canvas": lambda args: _handle_pruned("STORY_CANVAS", "Obsidian Canvas / StoryLine"),
        "pruned_causality": lambda args: _handle_pruned("CAUSALITY", "Aprils Automatic Timelines / Calendarium"),
        "pruned_timeline": lambda args: _handle_pruned("TIMELINE_SYNC", "Aprils Automatic Timelines / Calendarium"),
        "pruned_prophecy": lambda args: _handle_pruned("PROPHECY", "Obsidian Dataview / Tags"),
        "pruned_sprint": lambda args: _handle_pruned("WRITING_SPRINT", "Writing Goals / Novel Word Count"),
        "pruned_cast": lambda args: _handle_pruned("DRAMATIS_PERSONAE", "Canvas Roots / Dataview"),
        "pruned_conlang": lambda args: _handle_pruned("CONLANG", "PolyGlot / Condict / Rootweave / LanguageForge"),
        "pruned_genealogy": lambda args: _handle_pruned("GENEALOGY", "Gramps / Canvas Roots / StoryLine"),
        "pruned_faction": lambda args: _handle_pruned("FACTIONS", "Obsidian Dataview / Canvas"),
        "pruned_economy": lambda args: _handle_pruned("ECONOMY", "Obsidian Dossiers / Spreadsheets"),
        "pruned_tactical": lambda args: _handle_pruned("TACTICAL_SIM", "Tabletop / Wargame Rules"),
        "pruned_magic": lambda args: _handle_pruned("MAGIC_SYSTEM", "Rootweave / Dataview"),
        "pruned_continuity": lambda args: _handle_pruned("CONTINUITY", "Global Search and Replace / Vale"),
        "pruned_series": lambda args: _handle_pruned("SERIES_CONTINUITY", "Obsidian Dataview / Tag Wrangler"),
        "pruned_typography": lambda args: _handle_pruned("TYPOGRAPHY", "Obsidian Smart Typography / FormatForge / Typst"),
        "pruned_hub": lambda args: _handle_pruned("STUDIO_HUB", "Obsidian Workspace"),
        "pruned_zen": lambda args: _handle_pruned("ZEN_STUDIO", "Obsidian Typewriter Mode / FocusWriter"),
        "pruned_ambient": lambda args: _handle_pruned("AMBIENT", "External Focus Audio Players"),
        "pruned_search": lambda args: _handle_pruned("VAULT_SEARCH", "Obsidian Native Search / Dataview"),
        "pruned_corpus": lambda args: _handle_pruned("CORPUS_EXPORT", "Structured Data Exporters"),
        "pruned_doctor": lambda args: _handle_pruned("WORLD_DOCTOR", "Obsidian Search / Tag Wrangler"),
        "pruned_resonance": lambda args: _handle_pruned("RESONANCE", "Obsidian Graph View"),
        "pruned_tips": lambda args: _handle_pruned("TIPS", "Master Craft Reference Manuals"),
        "pruned_branch": lambda args: _handle_pruned("BRANCHING_GRAPH", "Obsidian Canvas / StoryLine"),
        "pruned_pacing": lambda args: _handle_pruned("PACING", "Sentence Rhythm / Write Good / Readability Score"),
        "pruned_scene_mechanics": lambda args: _handle_pruned("SCENE_MECHANICS", "Obsidian Scene Notes / Longform"),
        "pruned_senses": lambda args: _handle_pruned("SENSES", "Master Sensory Palette Reference"),
        "pruned_voice": lambda args: _handle_pruned("VOICE", "Character Voice Dossiers"),
        "pruned_stylistics": lambda args: _handle_pruned("STYLISTICS", "Vale / LanguageTool / FormatForge"),
        "pruned_concordance": lambda args: _handle_pruned("CONCORDANCE", "Obsidian Indexing"),
        "pruned_council": lambda args: _handle_pruned("COUNCIL", "Editorial Feedback Frameworks"),
        "pruned_audio_proof": lambda args: _handle_pruned("AUDIO_PROOF", "Piper TTS / Calibre"),
        "pruned_package": lambda args: _handle_pruned("PACKAGING", "Calibre / Typst CLI"),
    }


__all__ = [
    "DISPATCH_TABLE",
    "_handle_doctor",
    "_handle_matter",
    "_handle_new",
    "_handle_pruned",
    "_handle_tool",
    "build_handlers_map",
]
