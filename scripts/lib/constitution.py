#!/usr/bin/env python3
"""
Ars Arcanum Authorial Constitution & Governance Engine (scripts/lib/constitution.py)
==================================================================================
Manages the Authorial Constitution, hierarchical multi-layer policy merging
(Global -> World -> Manuscript), diagnostic rule suppression, and engine switchboard.
"""

from __future__ import annotations

import copy
import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger("arcanum.constitution")

DEFAULT_AUTHORIAL_POLICY: dict[str, Any] = {
    "default_mode": "observational",
    "dry_run_default": True,
    "suggestion_mode_only": True,
    "framework_free_default": False,
    "whitelisted_terms": [],
    "disabled_engines": [],
    "active_tradition": "unconstrained",
    "canon": {
        "authority": "author",
        "narrator_reliability": "reliable",  # "reliable" | "unreliable"
        "allow_unresolved_mysteries": True,
    },
    "style": {
        "passive_voice": "observe",  # "observe" | "allow"
        "repetition": "observe",     # "observe" | "allow"
        "filter_verbs": "observe",   # "observe" | "allow"
    },
    "structure": {
        "framework": "none",
        "score_enabled": False,
        "mode": "descriptive",       # "descriptive" | "reference" | "opt_in"
    },
    "magic": {
        "modality": "unconstrained", # "mythic" | "soft" | "rationalist" | "unconstrained"
        "enforce_thermodynamics": False,
        "causal_accountability": "optional",
    },
    "continuity": {
        "timeline": "flexible",
        "preserve_poetic_variation": True,
        "allow_figurative_language": True,
    },
    "naming": {
        "collision_heuristics": "advisory",
        "whitelisted_pairs": [],
    },
    "diagnostics": {
        "default_severity": "advisory",
        "suppressed_rules": [],
    },
    "ui_visual_preset": "sovereign-dark",
    "typewriter_sound_preset": "remington_1890",
    "crt_fx_enabled": False,
}


def _deep_merge_dict(target: dict[str, Any], source: dict[str, Any]) -> None:
    """Recursively merges source dict into target dict in-place, extending lists without duplicates."""
    for k, v in source.items():
        if isinstance(v, dict) and isinstance(target.get(k), dict):
            _deep_merge_dict(target[k], v)
        elif isinstance(v, list) and isinstance(target.get(k), list):
            for item in v:
                if item not in target[k]:
                    target[k].append(copy.deepcopy(item) if isinstance(item, (dict, list)) else item)
        elif isinstance(v, (dict, list)):
            target[k] = copy.deepcopy(v)
        else:
            target[k] = v


def get_authorial_policy() -> dict[str, Any]:
    """Returns configured authorial policy settings dictionary."""
    try:
        from lib.config_store import load_config
    except ImportError:
        from config_store import load_config

    cfg = load_config()
    pol = cfg.get("authorial_policy", {})
    res = copy.deepcopy(DEFAULT_AUTHORIAL_POLICY)
    if isinstance(pol, dict):
        _deep_merge_dict(res, pol)
    return res


def set_authorial_policy(policy_data: dict[str, Any]) -> bool:
    """Sets and persists authorial policy dictionary."""
    try:
        from lib.config_store import load_config, save_config
    except ImportError:
        from config_store import load_config, save_config

    cfg = load_config()
    current = get_authorial_policy()
    current.update(policy_data)
    cfg["authorial_policy"] = current
    return save_config(cfg)


def get_authorial_constitution(
    world_path: str | Path | None = None,
    manuscript_path: str | Path | None = None,
) -> dict[str, Any]:
    """Returns the resolved Authorial Constitution merging global policy with local vault/manuscript declarations."""
    base = get_authorial_policy()
    res = copy.deepcopy(base)

    # Check world-level config or constitution
    if world_path:
        w_dir = Path(world_path)
        for cand in [w_dir / "constitution.json", w_dir / "constitution.yaml", w_dir / "world_config.json"]:
            if cand.is_file():
                try:
                    if cand.suffix == ".json":
                        with open(cand, encoding="utf-8") as f:
                            w_data = json.load(f)
                    else:
                        try:
                            from lib.frontmatter import parse_yaml_document
                            w_data = parse_yaml_document(cand.read_text(encoding="utf-8"))
                        except ImportError:
                            from frontmatter import parse_yaml_document
                            w_data = parse_yaml_document(cand.read_text(encoding="utf-8"))
                    if isinstance(w_data, dict):
                        _deep_merge_dict(res, w_data)
                except Exception as e:
                    logger.debug("Failed reading constitution at %s: %s", cand, e)

    # Check manuscript-level config or constitution
    if manuscript_path:
        m_dir = Path(manuscript_path)
        for cand in [m_dir / "constitution.json", m_dir / "constitution.yaml", m_dir / "manuscript_config.json"]:
            if cand.is_file():
                try:
                    if cand.suffix == ".json":
                        with open(cand, encoding="utf-8") as f:
                            m_data = json.load(f)
                    else:
                        try:
                            from lib.frontmatter import parse_yaml_document
                            m_data = parse_yaml_document(cand.read_text(encoding="utf-8"))
                        except ImportError:
                            from frontmatter import parse_yaml_document
                            m_data = parse_yaml_document(cand.read_text(encoding="utf-8"))
                    if isinstance(m_data, dict):
                        _deep_merge_dict(res, m_data)
                except Exception as e:
                    logger.debug("Failed reading constitution at %s: %s", cand, e)

    return res


def deep_merge_constitution(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Returns a new dictionary with override merged recursively into base."""
    res = copy.deepcopy(base)
    _deep_merge_dict(res, override)
    return res


def load_authorial_constitution(project_dir: Path | str | None = None) -> dict[str, Any]:
    """Loads and resolves the Authorial Constitution for a specific project directory or global policy."""
    if not project_dir:
        return get_authorial_policy()
    return get_authorial_constitution(world_path=project_dir, manuscript_path=project_dir)


def get_suppressed_rules(project_dir: Path | str | None = None) -> list[str]:
    """Returns the list of all suppressed diagnostic rules."""
    c = load_authorial_constitution(project_dir) if project_dir else get_authorial_policy()
    suppressed: set[str] = set()
    diag = c.get("diagnostics", {})
    if isinstance(diag, dict):
        suppressed.update(str(r).upper().strip() for r in diag.get("suppressed_rules", []))
    suppressed.update(str(r).upper().strip() for r in c.get("suppressed_rules", []))
    return sorted(suppressed)


def is_rule_suppressed(rule_id: str, constitution: dict[str, Any] | Path | str | None = None) -> bool:
    """Checks whether a diagnostic rule ID is suppressed by the active Authorial Constitution."""
    if constitution is None:
        c_dict = get_authorial_policy()
    elif isinstance(constitution, (str, Path)):
        c_dict = load_authorial_constitution(constitution)
    else:
        c_dict = constitution

    diag = c_dict.get("diagnostics", {})
    suppressed = set()
    if isinstance(diag, dict):
        suppressed.update(str(r).upper().strip() for r in diag.get("suppressed_rules", []))
    suppressed.update(str(r).upper().strip() for r in c_dict.get("suppressed_rules", []))
    return rule_id.upper().strip() in suppressed


def get_world_axioms(world_name: str | None = None) -> dict[str, Any]:
    """Returns world axioms dictionary for world or global default."""
    try:
        from lib.config_store import load_config
    except ImportError:
        from config_store import load_config

    cfg = load_config()
    axioms = cfg.get("world_axioms", {})
    if not isinstance(axioms, dict):
        axioms = {}
    if world_name and world_name in axioms and isinstance(axioms[world_name], dict):
        return axioms[world_name]
    return axioms.get("default", {
        "magic_modality": "unconstrained",
        "epistemic_truth_default": "cultural_belief",
        "allow_anachronisms": True,
        "shared_universes": [],
        "custom_categories": [],
    })


def set_world_axioms(world_name: str, axioms_data: dict[str, Any]) -> bool:
    """Sets and persists world axioms for a specific world or default."""
    try:
        from lib.config_store import load_config, save_config
    except ImportError:
        from config_store import load_config, save_config

    cfg = load_config()
    if "world_axioms" not in cfg or not isinstance(cfg["world_axioms"], dict):
        cfg["world_axioms"] = {}
    cfg["world_axioms"][world_name] = axioms_data
    return save_config(cfg)


def get_disabled_engines() -> list[str]:
    """Returns list of disabled engine names."""
    pol = get_authorial_policy()
    return list(pol.get("disabled_engines", []))


def is_engine_enabled(engine_name: str) -> bool:
    """Checks if a specific engine is currently enabled."""
    disabled = get_disabled_engines()
    return engine_name.lower().strip() not in [d.lower().strip() for d in disabled]


def set_engine_enabled(engine_name: str, enabled: bool) -> bool:
    """Enables or disables an engine in authorial policy."""
    pol = get_authorial_policy()
    disabled = {d.lower().strip() for d in pol.get("disabled_engines", [])}
    clean_name = engine_name.lower().strip()
    if enabled:
        disabled.discard(clean_name)
    else:
        disabled.add(clean_name)
    pol["disabled_engines"] = sorted(disabled)
    return set_authorial_policy(pol)


__all__ = [
    "DEFAULT_AUTHORIAL_POLICY",
    "_deep_merge_dict",
    "deep_merge_constitution",
    "get_authorial_constitution",
    "get_authorial_policy",
    "get_disabled_engines",
    "get_suppressed_rules",
    "get_world_axioms",
    "is_engine_enabled",
    "is_rule_suppressed",
    "load_authorial_constitution",
    "set_authorial_policy",
    "set_engine_enabled",
    "set_world_axioms",
]
