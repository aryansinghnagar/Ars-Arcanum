#!/usr/bin/env python3
"""
Ars Arcanum Unified CLI Command Handlers & Dispatch Table (scripts/lib/cli_handlers.py)
======================================================================================
Defines specialized sub-command handlers, parameter normalization, advisory docs
redirection, and the canonical dispatch routing table.
"""

from __future__ import annotations

import os
import sys
from collections.abc import Callable


def _handle_new(dispatch_script_fn: Callable[[str, list[str]], int], rest: list[str]) -> int:
    """Handle 'arcanum new <type> <NAME>' sub-dispatch."""
    if not rest:
        print(
            "Usage: arcanum new <manuscript|draft|world|universe|volume> <NAME> "
            "[--structure STRUCTURE] [--divisions DIVISIONS] [options]",
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


def _handle_polish(dispatch_sub_fn: Callable[[str, list[str]], int], rest: list[str]) -> int:
    """Handle 'arcanum polish [typography]' sub-dispatch."""
    if rest and rest[0] == "typography":
        return dispatch_sub_fn("lib.typography_cleaner", rest[1:])
    return dispatch_sub_fn("lib.typography_cleaner", rest)


def _handle_ambient(dispatch_sub_fn: Callable[[str, list[str]], int], rest: list[str]) -> int:
    """Handle 'arcanum ambient [generate]' default sub-dispatch."""
    if rest and rest[0] == "generate":
        return dispatch_sub_fn("lib.ambient", rest)
    return dispatch_sub_fn("lib.ambient", ["generate", *rest])


def _handle_resonance(dispatch_sub_fn: Callable[[str, list[str]], int], cmd: str, rest: list[str]) -> int:
    """Handle 'arcanum resonance|mesh|cascade|spark|bridge' sub-dispatch."""
    if cmd in ("mesh", "cascade", "spark", "bridge"):
        return dispatch_sub_fn("lib.resonance", [cmd, *rest])
    return dispatch_sub_fn("lib.resonance", rest)


def _handle_sim(dispatch_sub_fn: Callable[[str, list[str]], int], rest: list[str]) -> int:
    """Handle 'arcanum sim [battle]' sub-dispatch."""
    if rest and rest[0] == "battle":
        return dispatch_sub_fn("lib.tactical_sim", ["sim", *rest[1:]])
    return dispatch_sub_fn("lib.tactical_sim", rest)


def _handle_magic(dispatch_sub_fn: Callable[[str, list[str]], int], rest: list[str]) -> int:
    """Handle 'arcanum magic|magic-check' with default 'check' sub-action."""
    if rest and rest[0] in ("check", "report"):
        return dispatch_sub_fn("lib.magic_system", rest)
    return dispatch_sub_fn("lib.magic_system", ["check", *rest])


def _handle_conlang(dispatch_sub_fn: Callable[[str, list[str]], int], cmd: str, rest: list[str]) -> int:
    """Handle 'arcanum conlang|family-tree|grammar|declension|conjugate|semantic-shift' sub-dispatch."""
    if cmd in ("family-tree", "grammar", "declension", "conjugate", "semantic-shift", "lexicon", "mutate", "generate"):
        return dispatch_sub_fn("lib.conlang", [cmd, *rest])
    return dispatch_sub_fn("lib.conlang", rest)


def _handle_calc(dispatch_sub_fn: Callable[[str, list[str]], int], rest: list[str]) -> int:
    """Handle 'arcanum calc <subcommand>' sub-dispatch."""
    if not rest:
        print(
            "Usage: arcanum calc <transit|time-dilation|orbit|comms|habitability|system-dossier|journey|battle|logistics|climate|trade> [args...]",
            file=sys.stderr,
        )
        return 2
    sub = rest[0].lower()
    sub_args = rest[1:]
    if sub in ("transit", "time-dilation", "orbit", "comms", "habitability", "astro", "astrophysics", "system-dossier", "dossier"):
        if sub in ("astro", "astrophysics"):
            return dispatch_sub_fn("lib.astrophysics", sub_args)
        return dispatch_sub_fn("lib.astrophysics", [sub, *sub_args])
    if sub in ("journey", "expedition", "travel"):
        return dispatch_sub_fn("lib.journey", sub_args)
    if sub in ("battle", "sim", "tactical", "combat"):
        return dispatch_sub_fn("lib.tactical_sim", ["sim", *sub_args])
    if sub in ("logistics", "supply"):
        return dispatch_sub_fn("lib.factions", ["logistics", *sub_args])
    if sub in ("climate", "weather", "insolation", "biomes"):
        return dispatch_sub_fn("lib.climate", sub_args)
    if sub in ("trade", "arbitrage", "ppp"):
        return dispatch_sub_fn("lib.economy", ["trade", *sub_args])
    print(f"Unknown calc mode '{sub}'. Choose: transit, time-dilation, orbit, comms, habitability, system-dossier, journey, battle, logistics, climate, trade.", file=sys.stderr)
    return 2


def _handle_pruned(doc_name: str, args: list[str]) -> int:
    """Provides craft reference advisory message and optional doc redirection."""
    print(
        f"Ars Arcanum Craft Studio — Reference Doctrine ({doc_name.upper()})\n"
        f"Note: The standalone regex/heuristic '{doc_name.lower()}' engine has transitioned\n"
        f"to deterministic metadata and authoritative craft documentation.\n\n"
        f"For theoretical foundations, formulas, and rubrics, see docs/{doc_name.upper()}.md\n"
        f"or run: arcanum doc {doc_name.lower()}"
    )
    return 0


def _handle_audit(dispatch_sub_fn: Callable[[str, list[str]], int], rest: list[str]) -> int:
    """Handle 'arcanum audit <subcommand>' sub-dispatch."""
    if not rest:
        return dispatch_sub_fn("lib.diagnostics", ["audit"])
    sub = rest[0].lower()
    sub_args = rest[1:]
    _pruned_audit = {
        "dialogue": "STYLISTICS",
        "tags": "STYLISTICS",
        "said-bookisms": "STYLISTICS",
        "echoes": "STYLISTICS",
        "echo": "STYLISTICS",
        "repetition": "STYLISTICS",
        "rhythm": "PACING",
        "readability": "STYLISTICS",
        "prose": "STYLISTICS",
        "style": "STYLISTICS",
        "stylistics": "STYLISTICS",
        "voice": "VOICE",
        "voice-bleed": "VOICE",
        "scenes": "SCENE_MECHANICS",
        "scene": "SCENE_MECHANICS",
        "mru": "SCENE_MECHANICS",
        "idioms": "STYLISTICS",
        "idiom": "STYLISTICS",
        "eponyms": "STYLISTICS",
        "senses": "SENSES",
        "sensory": "SENSES",
        "palette": "SENSES",
    }
    if sub in _pruned_audit:
        return _handle_pruned(_pruned_audit[sub], sub_args)
    if sub in ("structure", "paradigm"):
        return dispatch_sub_fn("lib.structure", sub_args)
    if sub in ("tech", "technology", "anachronisms"):
        return dispatch_sub_fn("lib.economy", ["tech", *sub_args])
    return dispatch_sub_fn("lib.diagnostics", rest)


def _handle_tool(rest: list[str]) -> int:
    """Handle 'arcanum tool <list|enable|disable|status>' sub-dispatch."""
    from lib.config import get_authorial_policy, get_disabled_engines, set_engine_enabled
    from lib.registry import list_engines

    if not rest or rest[0] in ("list", "ls"):
        disabled = set(get_disabled_engines())
        engines = list_engines()
        print(f"Ars Arcanum Tool Switchboard ({len(engines)} total tools):\n")
        print(f"{'Status':<12} {'Name':<22} {'Command':<18} {'Title'}")
        print("-" * 75)
        for eng in sorted(engines, key=lambda e: e.name):
            status = "❌ DISABLED" if eng.name in disabled else "✓ ENABLED"
            print(f"{status:<12} {eng.name:<22} {eng.cli_command:<18} {eng.title}")
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
    """Handle 'arcanum doctor' with world-doctor path detection."""
    if rest and not rest[0].startswith("-") and os.path.isdir(rest[0]):
        return dispatch_sub_fn("lib.world_doctor", rest)
    return dispatch_sub_fn("lib.diagnostics", rest)


# The canonical dispatch table — single source of truth for all command routing.
# Format: alias -> (dispatch_type, target, [optional_prefix_args])
DISPATCH_TABLE: dict[str, tuple[str, ...]] = {
    "tool": ("handler", "tool"), "tools": ("handler", "tool"),
    "switchboard": ("handler", "tool"), "plugins": ("handler", "tool"),
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
    "search": ("module", "lib.vault_search"), "vault-search": ("module", "lib.vault_search"),
    "rag": ("module", "lib.vault_search"), "query-lore": ("module", "lib.vault_search"),
    "semantic-search": ("module", "lib.vault_search"), "lore-query": ("module", "lib.vault_search"),
    "recall": ("module", "lib.vault_search"),
    "branch": ("handler", "pruned_branch"), "branching": ("handler", "pruned_branch"),
    "gamebook": ("handler", "pruned_branch"), "interactive-fiction": ("handler", "pruned_branch"),
    "branch-graph": ("handler", "pruned_branch"), "subway-map": ("handler", "pruned_branch"),
    "hub": ("module", "lib.studio_hub"), "dashboard": ("module", "lib.studio_hub"),
    "gui-web": ("module", "lib.studio_hub"), "studio-hub": ("module", "lib.studio_hub"),
    "causality": ("module", "lib.causality"), "causal": ("module", "lib.causality"),
    "time-travel": ("module", "lib.causality"), "ctc": ("module", "lib.causality"),
    "multiverse": ("module", "lib.causality"), "paradox": ("module", "lib.causality"),
    "prophecy": ("module", "lib.prophecy"), "prophecies": ("module", "lib.prophecy"),
    "oracle": ("module", "lib.prophecy"), "delphic": ("module", "lib.prophecy"),
    "arcane-inscription": ("module", "lib.prophecy"), "prophecy-matrix": ("module", "lib.prophecy"),
    "senses": ("handler", "pruned_senses"), "sensory": ("handler", "pruned_senses"),
    "immersion": ("handler", "pruned_senses"), "white-room": ("handler", "pruned_senses"),
    "palette": ("handler", "pruned_senses"),
    "sprint": ("module", "lib.writing_sprint"), "writing-sprint": ("module", "lib.writing_sprint"),
    "pomodoro": ("module", "lib.writing_sprint"), "session": ("module", "lib.writing_sprint"),
    "velocity": ("module", "lib.writing_sprint"),
    "revision-heatmap": ("module", "lib.revision_heatmap"), "churn": ("module", "lib.revision_heatmap"),
    "revision-density": ("module", "lib.revision_heatmap"), "draft-churn": ("module", "lib.revision_heatmap"),
    "heatmap": ("module", "lib.revision_heatmap"),
    "words": ("script", "arcanum", "words"), "wordcount": ("script", "arcanum", "words"),
    "report": ("script", "arcanum", "words"), "count": ("script", "arcanum", "words"),
    "stats": ("script", "arcanum", "words"),
    "pace": ("handler", "pruned_pacing"), "pacing": ("handler", "pruned_pacing"),
    "rhythm": ("handler", "pruned_pacing"), "waveform": ("handler", "pruned_pacing"),
    "tension": ("handler", "pruned_scene_mechanics"), "tension-arc": ("handler", "pruned_scene_mechanics"),
    "scene": ("handler", "pruned_scene_mechanics"), "scenes": ("handler", "pruned_scene_mechanics"),
    "swain": ("handler", "pruned_scene_mechanics"), "mru": ("handler", "pruned_scene_mechanics"),
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
    "package": ("handler", "pruned_package"), "dist": ("handler", "pruned_package"),
    "bundle": ("handler", "pruned_package"),
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
    "concordance": ("handler", "concordance"), "glossary": ("handler", "concordance"),
    "index": ("handler", "concordance"),
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
    "council": ("handler", "pruned_council"), "editorial-council": ("handler", "pruned_council"),
    "dossier": ("handler", "pruned_council"), "council-audit": ("handler", "pruned_council"),
    "audio-proof": ("handler", "pruned_audio_proof"), "tts-proof": ("handler", "pruned_audio_proof"),
    "speech-proof": ("handler", "pruned_audio_proof"), "audio-export": ("handler", "pruned_audio_proof"),
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
    "voice": ("handler", "pruned_voice"), "voice-bleed": ("handler", "pruned_voice"),
    "idiolect": ("handler", "pruned_voice"), "stylometry": ("handler", "pruned_voice"),
    "style": ("handler", "pruned_stylistics"), "stylistics": ("handler", "pruned_stylistics"),
    "polish-style": ("handler", "pruned_stylistics"), "readability": ("handler", "pruned_stylistics"),
    "audit": ("handler", "audit"),
    "scope": ("module", "lib.scope"), "target-scope": ("module", "lib.scope"),
    "engine-scope": ("module", "lib.scope"),
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
        "polish": lambda rest: _handle_polish(dispatch_sub_fn, rest),
        "ambient": lambda rest: _handle_ambient(dispatch_sub_fn, rest),
        "sim": lambda rest: _handle_sim(dispatch_sub_fn, rest),
        "magic": lambda rest: _handle_magic(dispatch_sub_fn, rest),
        "calc": lambda rest: _handle_calc(dispatch_sub_fn, rest),
        "audit": lambda rest: _handle_audit(dispatch_sub_fn, rest),
        "doctor": lambda rest: _handle_doctor(dispatch_sub_fn, rest),
        "engines": handle_engines_fn,
        "resonance": lambda cmd, rest: _handle_resonance(dispatch_sub_fn, cmd, rest),
        "conlang": lambda cmd, rest: _handle_conlang(dispatch_sub_fn, cmd, rest),
        "pruned_branch": lambda args: _handle_pruned("BRANCHING_GRAPH", args),
        "pruned_pacing": lambda args: _handle_pruned("PACING", args),
        "pruned_scene_mechanics": lambda args: _handle_pruned("SCENE_MECHANICS", args),
        "pruned_senses": lambda args: _handle_pruned("SENSES", args),
        "pruned_voice": lambda args: _handle_pruned("VOICE", args),
        "pruned_stylistics": lambda args: _handle_pruned("STYLISTICS", args),
        "concordance": lambda args: _handle_pruned("CONCORDANCE", args),
        "pruned_council": lambda args: _handle_pruned("COUNCIL", args),
        "pruned_audio_proof": lambda args: _handle_pruned("AUDIO_PROOF", args),
        "pruned_package": lambda args: _handle_pruned("PACKAGING", args),
    }


__all__ = [
    "DISPATCH_TABLE",
    "_handle_audit",
    "_handle_calc",
    "_handle_conlang",
    "_handle_doctor",
    "_handle_magic",
    "_handle_new",
    "_handle_pruned",
    "_handle_resonance",
    "_handle_sim",
    "_handle_tool",
    "build_handlers_map",
]
