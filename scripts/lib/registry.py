#!/usr/bin/env python3
"""
Ars Arcanum Engine & Plugin Registry (scripts/lib/registry.py)
============================================================
Defines core vs craft engine classification, dynamic plugin discovery,
engine metadata introspection, educational logic documentation, and capability
catalog across CLI and GUI surfaces.
"""

from __future__ import annotations

import difflib
import importlib
import importlib.util
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger("arcanum.registry")

# Re-export base classes and utilities for seamless backward-compatibility
try:
    from lib.registry_base import (
        AdvisoryResolution,
        BaseCraftEngine,
        EngineCategory,
        EngineSpec,
    )
except ImportError:
    from registry_base import (
        AdvisoryResolution,
        BaseCraftEngine,
        EngineCategory,
        EngineSpec,
    )

try:
    from lib.registry_specs import ALL_ENGINES
except ImportError:
    from registry_specs import ALL_ENGINES

# Canonical Global Engine Registry (initialized from modular domain specifications)
_ENGINES: dict[str, EngineSpec] = dict(ALL_ENGINES)

# -----------------------------------------------------------------------------
# Public Query & Discovery Functions
# -----------------------------------------------------------------------------

def register_user_engine(spec: EngineSpec) -> None:
    """Register or override an engine specification dynamically."""
    _ENGINES[spec.name] = spec


def load_user_plugin(file_path: Path | str) -> EngineSpec | None:
    """Loads a custom Python engine plugin file and registers its specification."""
    p = Path(file_path).resolve()
    if not p.is_file() or p.suffix != ".py" or p.name.startswith((".", "_")):
        return None

    module_name = f"arcanum_plugin_{p.stem}"
    try:
        spec = importlib.util.spec_from_file_location(module_name, str(p))
        if spec is None or spec.loader is None:
            return None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        # Check for BaseCraftEngine subclass instance or class
        for attr_name in dir(mod):
            attr = getattr(mod, attr_name)
            if isinstance(attr, type) and issubclass(attr, BaseCraftEngine) and attr is not BaseCraftEngine:
                engine_instance = attr()
                engine_spec = engine_instance.get_spec()
                register_user_engine(engine_spec)
                return engine_spec
            if isinstance(attr, EngineSpec):
                register_user_engine(attr)
                return attr

        if hasattr(mod, "register_engine"):
            res = mod.register_engine()
            if isinstance(res, EngineSpec):
                register_user_engine(res)
                return res
    except Exception as e:
        logger.warning(f"Failed to load dynamic plugin from '{p}': {e}")
    return None


def discover_user_plugins(extra_dirs: list[Path | str] | None = None) -> list[EngineSpec]:
    """Discovers and registers custom craft engines located in user config or universe plugin directories."""
    discovered: list[EngineSpec] = []
    search_dirs: list[Path] = []

    # 1. ~/.config/ars-arcanum/engines/
    home_dir = Path.home()
    user_config_plugins = home_dir / ".config" / "ars-arcanum" / "engines"
    if user_config_plugins.is_dir():
        search_dirs.append(user_config_plugins)

    # 2. ~/Universes/*/.plugins/
    universes_dir = home_dir / "Universes"
    if universes_dir.is_dir():
        for u in universes_dir.iterdir():
            if u.is_dir():
                u_plugins = u / ".plugins"
                if u_plugins.is_dir():
                    search_dirs.append(u_plugins)

    # 3. Extra directories
    if extra_dirs:
        for d in extra_dirs:
            p = Path(d).resolve()
            if p.is_dir():
                search_dirs.append(p)

    for sdir in search_dirs:
        for py_file in sorted(sdir.glob("*.py")):
            if not py_file.name.startswith((".", "_")):
                spec = load_user_plugin(py_file)
                if spec:
                    discovered.append(spec)

    return discovered


# Canonical alias for dynamic plugin discovery
discover_craft_plugins = discover_user_plugins


def get_registry() -> dict[str, EngineSpec]:
    """Return the global engine dictionary."""
    return _ENGINES


def get_engine(name: str) -> EngineSpec | None:
    """Retrieve an engine specification by name, command, or alias."""
    name_clean = name.lower().strip()
    name_underscored = name_clean.replace("-", "_").replace(" ", "_")
    name_hyphenated = name_clean.replace("_", "-").replace(" ", "-")

    if name_clean in _ENGINES:
        return _ENGINES[name_clean]
    if name_underscored in _ENGINES:
        return _ENGINES[name_underscored]

    for spec in _ENGINES.values():
        all_names = {
            spec.name.lower(),
            spec.name.lower().replace("_", "-"),
            spec.cli_command.lower(),
            spec.cli_command.lower().replace(" ", "-"),
            spec.cli_command.lower().replace(" ", "_"),
        }
        for a in spec.aliases:
            all_names.add(a.lower())
            all_names.add(a.lower().replace("_", "-"))
            all_names.add(a.lower().replace("-", "_"))
        if name_clean in all_names or name_underscored in all_names or name_hyphenated in all_names:
            return spec

    for spec in _ENGINES.values():
        if spec.cli_command.lower().startswith(name_clean + " ") or spec.cli_command.lower().endswith(" " + name_clean):
            return spec
    return None


def list_engines(category: EngineCategory | None = None, enabled_only: bool = True) -> list[EngineSpec]:
    """List engine specifications matching optional category and enabled filter."""
    res = []
    for spec in _ENGINES.values():
        if category is not None and spec.category != category:
            continue
        if enabled_only and not spec.enabled:
            continue
        res.append(spec)
    return res


def get_core_engines(enabled_only: bool = True) -> list[EngineSpec]:
    """Return all core platform engines."""
    return list_engines(category=EngineCategory.CORE, enabled_only=enabled_only)


def get_craft_engines(enabled_only: bool = True) -> list[EngineSpec]:
    """Return all craft & specialized worldbuilding engines."""
    return list_engines(category=EngineCategory.CRAFT, enabled_only=enabled_only)


def is_engine_enabled(name: str) -> bool:
    """Check if an engine is enabled."""
    spec = get_engine(name)
    return spec.enabled if spec else False


def enable_engine(name: str) -> bool:
    """Enable a specific engine."""
    spec = get_engine(name)
    if spec:
        spec.enabled = True
        return True
    return False


def disable_engine(name: str) -> bool:
    """Disable a specific engine."""
    spec = get_engine(name)
    if spec:
        spec.enabled = False
        return True
    return False


def load_engine_module(name: str) -> Any:
    """Dynamically import and return the engine's Python module."""
    spec = get_engine(name)
    if not spec:
        raise ValueError(f"Unknown engine: '{name}'")
    return importlib.import_module(spec.module_name)


def search_engine_docs(query: str) -> list[EngineSpec]:
    """Fuzzy and substring search across all engine specifications."""
    q = query.lower().strip()
    if not q:
        return list(_ENGINES.values())

    results: list[EngineSpec] = []
    for spec in _ENGINES.values():
        searchable_text = f"{spec.name} {spec.title} {spec.description} {spec.scientific_logic} {spec.why_this_way} {spec.extension_guide} {' '.join(spec.aliases)}".lower()
        if q in searchable_text:
            results.append(spec)

    if not results:
        # Try fuzzy match on engine names and titles
        all_names = {s.name: s for s in _ENGINES.values()}
        matches = difflib.get_close_matches(q, list(all_names.keys()), n=5, cutoff=0.4)
        results = [all_names[m] for m in matches]

    return results


def get_engine_docs(name: str) -> dict[str, Any] | None:
    """Retrieve structured educational documentation and advisory guidance for an engine."""
    spec = get_engine(name)
    if not spec:
        return None
    return {
        "name": spec.name,
        "title": spec.title,
        "category": spec.category.value,
        "studio_tab": spec.studio_tab or "",
        "cli_command": spec.cli_command,
        "aliases": spec.aliases,
        "description": spec.description,
        "logic_documentation": spec.logic_documentation,
        "scientific_logic": spec.scientific_logic,
        "why_this_way": spec.why_this_way,
        "worldbuilding_relevance": spec.worldbuilding_relevance,
        "storytelling_relevance": spec.storytelling_relevance,
        "writing_relevance": spec.writing_relevance,
        "subfeatures": spec.subfeatures,
        "extension_guide": spec.extension_guide,
        "advisory_guidance": spec.advisory_guidance,
        "theory_references": spec.theory_references,
    }


def get_all_engine_docs() -> list[dict[str, Any]]:
    """Retrieve structured educational documentation for all registered engines."""
    return [
        {
            "name": spec.name,
            "title": spec.title,
            "category": spec.category.value,
            "studio_tab": spec.studio_tab or "",
            "cli_command": spec.cli_command,
            "aliases": spec.aliases,
            "description": spec.description,
            "logic_documentation": spec.logic_documentation,
            "scientific_logic": spec.scientific_logic,
            "why_this_way": spec.why_this_way,
            "worldbuilding_relevance": spec.worldbuilding_relevance,
            "storytelling_relevance": spec.storytelling_relevance,
            "writing_relevance": spec.writing_relevance,
            "subfeatures": spec.subfeatures,
            "extension_guide": spec.extension_guide,
            "advisory_guidance": spec.advisory_guidance,
            "theory_references": spec.theory_references,
        }
        for spec in _ENGINES.values()
    ]


def format_engine_doc(spec_or_name: EngineSpec | str, mode: str = "full") -> str:
    """Formats an engine's educational documentation for terminal CLI display.
    Modes: 'full', 'math' / 'theory', 'sources' / 'references', 'why', 'examples', 'subfeatures', 'advisory'
    """
    if isinstance(spec_or_name, str):
        engine_obj = get_engine(spec_or_name)
        if not engine_obj:
            return f"No documentation available for engine: '{spec_or_name}'"
        spec = engine_obj
    else:
        spec = spec_or_name

    mode_clean = mode.lower().strip()

    if mode_clean in ("math", "theory", "physics", "logic"):
        return f"""══════════════════════════════════════════════════════════════════════════════
 📐 {spec.title.upper()} — SCIENTIFIC / MATHEMATICAL / NARRATIVE LOGIC
 Command: 'arcanum {spec.cli_command}'
══════════════════════════════════════════════════════════════════════════════

{spec.scientific_logic or spec.logic_documentation}
"""

    if mode_clean in ("sources", "references", "citations", "bibliography", "papers", "reading"):
        lines = [
            "══════════════════════════════════════════════════════════════════════════════",
            f" 📚 {spec.title.upper()} — THEORETICAL FOUNDATIONS & REFERENCE SOURCES",
            f" Command: 'arcanum {spec.cli_command}'",
            "══════════════════════════════════════════════════════════════════════════════\n",
        ]
        if spec.theory_references:
            for idx, src in enumerate(spec.theory_references, 1):
                lines.append(f"[{idx}] {src.get('title', 'Reference')}")
                if src.get("citation"):
                    lines.append(f"    • Citation: {src.get('citation')}")
                if src.get("url"):
                    lines.append(f"    • Link:     {src.get('url')}")
                if src.get("description"):
                    lines.append(f"    • Context:  {src.get('description')}\n")
                else:
                    lines.append("")
        else:
            lines.append("   (No external theory references indexed for this engine.)")
        return "\n".join(lines)

    if mode_clean in ("why", "rationale"):
        return f"""══════════════════════════════════════════════════════════════════════════════
 💡 {spec.title.upper()} — ARCHITECTURAL & CREATIVE RATIONALE ('WHY THIS WAY')
 Command: 'arcanum {spec.cli_command}'
══════════════════════════════════════════════════════════════════════════════

{spec.why_this_way or 'Provides deterministic mathematical and physical grounding for world lore.'}
"""

    if mode_clean in ("examples", "extension", "how-to", "guide"):
        return f"""══════════════════════════════════════════════════════════════════════════════
 🛠️ {spec.title.upper()} — AUTHOR EXTENSION GUIDE & PRACTICAL EXAMPLES
 Command: 'arcanum {spec.cli_command}'
══════════════════════════════════════════════════════════════════════════════

{spec.extension_guide or 'Configure parameters in YAML manifests or CLI invocation.'}
"""

    if mode_clean in ("subfeatures", "features"):
        lines = [
            "══════════════════════════════════════════════════════════════════════════════",
            f" ⚡ {spec.title.upper()} — SUBFEATURES MATRIX",
            f" Command: 'arcanum {spec.cli_command}'",
            "══════════════════════════════════════════════════════════════════════════════\n",
        ]
        if spec.subfeatures:
            for idx, sf in enumerate(spec.subfeatures, 1):
                lines.append(f"[{idx}] {sf.get('name', 'Subfeature')}")
                lines.append(f"    • Rule/Logic: {sf.get('rule', '')}")
                lines.append(f"    • Example:    {sf.get('example', '')}\n")
        else:
            lines.append("   (Subfeatures operate under the unified engine CLI command.)")
        return "\n".join(lines)

    if mode_clean in ("advisory", "resolution", "resolutions", "guidance", "choices"):
        lines = [
            "══════════════════════════════════════════════════════════════════════════════",
            f" 💡 {spec.title.upper()} — CREATIVE ADVISORY RESOLUTION PATHWAYS",
            f" Command: 'arcanum {spec.cli_command}'",
            "══════════════════════════════════════════════════════════════════════════════\n",
            "(The system never forces conformity. All checks provide multiple creative choices:)\n",
        ]
        if spec.advisory_guidance:
            for idx, adv in enumerate(spec.advisory_guidance, 1):
                lines.append(f"[{idx}] Pattern: {adv.get('pattern', 'Unconventional Choice')}")
                lines.append(f"    • Option A (Hard Realism): {adv.get('option_a', 'Standard convention')}")
                lines.append(f"    • Option B (Speculative Trope): {adv.get('option_b', 'In-world arcane/sci-fi grounding')}")
                lines.append(f"    • Option C (Author Sovereignty): {adv.get('option_c', 'Authorial creative freedom')}\n")
        else:
            lines.append("   (No specific advisory overrides registered for this engine.)")
        return "\n".join(lines)

    # Default 'full' mode
    doc = [
        "══════════════════════════════════════════════════════════════════════════════",
        f" 🏛️  ARS ARCANUM CRAFT ENGINE: {spec.title.upper()}",
        f"     Category: [{spec.category.value.upper()}]  •  Command: 'arcanum {spec.cli_command}'",
        "══════════════════════════════════════════════════════════════════════════════",
        "\n📖 Overview:",
        f"   {spec.description}",
        "\n⚙️ Engine Logic & Scientific / Structural Foundations:",
        f"   {spec.scientific_logic or spec.logic_documentation}",
        "\n💡 Why It Works This Way (Rationale):",
        f"   {spec.why_this_way or 'Provides deterministic mathematical and physical grounding for world lore.'}",
        "\n🌍 Worldbuilding Relevance:",
        f"   {spec.worldbuilding_relevance}",
        "\n📐 Storytelling & Narrative Architecture Relevance:",
        f"   {spec.storytelling_relevance}",
        "\n✍️ Prose Writing & Editorial Relevance:",
        f"   {spec.writing_relevance}",
    ]

    if spec.subfeatures:
        doc.append("\n⚡ Key Subfeatures & Capabilities:")
        for idx, sf in enumerate(spec.subfeatures, 1):
            doc.append(f"   [{idx}] {sf.get('name', 'Subfeature')}: {sf.get('rule', '')}")
            if sf.get('example'):
                doc.append(f"       Example: {sf.get('example')}")

    if spec.extension_guide:
        doc.append("\n🛠️ How to Build Upon & Extend This Logic (Examples):")
        doc.append("   " + "\n   ".join(spec.extension_guide.split("\n")))

    if spec.advisory_guidance:
        doc.append("\n💡 Advisory Mechanics & Creative Freedom Resolution Pathways:")
        doc.append("   (The system never forces conformity. All checks provide multiple creative choices:)")
        for idx, adv in enumerate(spec.advisory_guidance, 1):
            doc.append(f"\n   [{idx}] Pattern: {adv.get('pattern', 'Unconventional Choice')}")
            doc.append(f"       • Option A (Hard Realism): {adv.get('option_a', 'Standard convention')}")
            doc.append(f"       • Option B (Speculative Trope): {adv.get('option_b', 'In-world arcane/sci-fi grounding')}")
            doc.append(f"       • Option C (Author Sovereignty): {adv.get('option_c', 'Authorial creative freedom')}")

    if spec.theory_references:
        doc.append("\n📚 Theoretical Foundations & Reference Sources:")
        for idx, src in enumerate(spec.theory_references, 1):
            doc.append(f"\n   [{idx}] {src.get('title', 'Reference')}: {src.get('citation', '')}")
            if src.get('url'):
                doc.append(f"       Link: {src.get('url')}")
            if src.get('description'):
                doc.append(f"       Context: {src.get('description')}")

    doc.append("\n══════════════════════════════════════════════════════════════════════════════\n")
    return "\n".join(doc)


def get_engine_tips(engine_name: str) -> list[dict[str, Any]]:
    """Returns all metadata-rich craft and technical tips for a specific engine."""
    try:
        from lib.tips import get_tip_database
    except ImportError:
        try:
            from tips import get_tip_database
        except ImportError:
            return []
    db = get_tip_database()
    tips = db.get_by_engine(engine_name)
    return [t.to_dict() for t in tips]


def get_engine_catalog() -> list[dict[str, Any]]:
    """Returns the comprehensive craft engine catalog and capabilities as a list of dicts."""
    docs = get_all_engine_docs()
    return [
        {
            "id": d["name"],
            "name": d["title"],
            "category": d["category"].capitalize(),
            "studio_tab": d.get("studio_tab", ""),
            "cli": f"arcanum {d['cli_command']}",
            "desc": d["description"],
            "logic_documentation": d.get("logic_documentation", ""),
            "scientific_logic": d.get("scientific_logic", d.get("logic_documentation", "")),
            "why_this_way": d.get("why_this_way", ""),
            "worldbuilding_relevance": d.get("worldbuilding_relevance", ""),
            "storytelling_relevance": d.get("storytelling_relevance", ""),
            "writing_relevance": d.get("writing_relevance", ""),
            "subfeatures": d.get("subfeatures", []),
            "extension_guide": d.get("extension_guide", ""),
            "advisory_guidance": d.get("advisory_guidance", []),
            "theory_references": d.get("theory_references", []),
            "tips": get_engine_tips(d["name"]),
        }
        for d in docs
    ]


__all__ = [
    "AdvisoryResolution",
    "BaseCraftEngine",
    "EngineCategory",
    "EngineSpec",
    "disable_engine",
    "discover_craft_plugins",
    "discover_user_plugins",
    "enable_engine",
    "format_engine_doc",
    "get_all_engine_docs",
    "get_core_engines",
    "get_craft_engines",
    "get_engine",
    "get_engine_catalog",
    "get_engine_docs",
    "get_engine_tips",
    "get_registry",
    "is_engine_enabled",
    "list_engines",
    "load_engine_module",
    "load_user_plugin",
    "register_user_engine",
    "search_engine_docs",
]
