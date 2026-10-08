#!/usr/bin/env python3
"""
Ars Arcanum Configuration Engine (scripts/lib/config.py)
========================================================
Manages local user preferences and global configuration in standard XDG directories
(~/.config/ars-arcanum/config.json).

Provides programmatic API and CLI commands for managing:
- Secure external backup destinations
- Default trim sizes and export presets
- Active author profiles
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

try:
    import lib._bootstrap  # noqa: F401
except ImportError:
    import _bootstrap  # noqa: F401

logger = logging.getLogger("arcanum.config")

CONFIG_DIR_NAME = "ars-arcanum"
LEGACY_CONFIG_DIR_NAME = "arcanum"
CONFIG_FILE_NAME = "config.json"


def get_config_dir() -> Path:
    """Returns the XDG configuration directory for Ars Arcanum."""
    xdg_config_home = os.environ.get("XDG_CONFIG_HOME")
    base = Path(xdg_config_home) if xdg_config_home else Path.home() / ".config"
    return base / CONFIG_DIR_NAME


def get_config_file_path() -> Path:
    """Returns the primary configuration file path, checking legacy fallback if needed."""
    primary_dir = get_config_dir()
    primary_file = primary_dir / CONFIG_FILE_NAME
    if primary_file.is_file():
        return primary_file

    # Check legacy fallback
    legacy_dir = primary_dir.parent / LEGACY_CONFIG_DIR_NAME
    legacy_file = legacy_dir / CONFIG_FILE_NAME
    if legacy_file.is_file():
        return legacy_file

    return primary_file


def load_config() -> dict:
    """Loads configuration dictionary from disk."""
    config_path = get_config_file_path()
    if not config_path.is_file():
        return {}
    try:
        with open(config_path, encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
    except Exception as e:
        logger.warning("Failed to parse configuration file at %s: %s", config_path, e)
    return {}


def save_config(config_data: dict) -> bool:
    """Saves configuration dictionary to disk with restrictive 0o600 permissions."""
    config_path = get_config_file_path()
    try:
        try:
            from lib.fs_utils import atomic_write
        except ImportError:
            try:
                from fs_utils import atomic_write
            except ImportError:
                from lib._bootstrap import atomic_write
        data_str = json.dumps(config_data, indent=2, ensure_ascii=False) + "\n"
        atomic_write(config_path, data_str)
        try:
            os.chmod(config_path, 0o600)
        except OSError:
            pass
        return True
    except Exception as e:
        logger.error("Failed to write configuration file at %s: %s", config_path, e)
        return False


DOCX_PRESETS = {
    "standard-submission": {
        "name": "Standard Submission (Shunn / Industry)",
        "description": "William Shunn standard manuscript format. Times New Roman 12pt, double-spaced, 1-inch margins, 0.5-inch indent, '#' scene breaks.",
        "font_family": "Times New Roman",
        "font_size_pt": 12.0,
        "line_spacing": 2.0,
        "margin_inches": 1.0,
        "first_line_indent_inches": 0.5,
        "scene_break_symbol": "#",
        "page_break_chapters": True,
        "include_header_slug": True,
    },
    "modern-manuscript": {
        "name": "Modern Manuscript",
        "description": "Clean modern editorial layout. Georgia 11.5pt, 1.35 line spacing, 1-inch margins, 0.35-inch indent, '* * *' scene breaks.",
        "font_family": "Georgia",
        "font_size_pt": 11.5,
        "line_spacing": 1.35,
        "margin_inches": 1.0,
        "first_line_indent_inches": 0.35,
        "scene_break_symbol": "* * *",
        "page_break_chapters": True,
        "include_header_slug": True,
    },
    "classic-trade": {
        "name": "Classic Literary & Trade",
        "description": "Classic book proportions. EB Garamond 12pt, 1.5 line spacing, 1-inch margins, 0.5-inch indent.",
        "font_family": "EB Garamond",
        "font_size_pt": 12.0,
        "line_spacing": 1.5,
        "margin_inches": 1.0,
        "first_line_indent_inches": 0.5,
        "scene_break_symbol": "* * *",
        "page_break_chapters": True,
        "include_header_slug": False,
    },
    "custom": {
        "name": "Custom User Formatting",
        "description": "User-customized manuscript typography and spacing.",
        "font_family": "Times New Roman",
        "font_size_pt": 12.0,
        "line_spacing": 2.0,
        "margin_inches": 1.0,
        "first_line_indent_inches": 0.5,
        "scene_break_symbol": "#",
        "page_break_chapters": True,
        "include_header_slug": True,
    }
}


def get_backup_dest() -> str:
    """Returns configured external secure backup destination path or empty string."""
    cfg = load_config()
    dest = cfg.get("secure_backup_destination") or cfg.get("backup_destination") or ""
    return str(dest).strip()


get_backup_destination = get_backup_dest


def set_backup_dest(dest_path: str) -> bool:
    """Sets and persists the secure external backup destination."""
    cfg = load_config()
    clean_path = str(Path(dest_path).expanduser().resolve())
    cfg["secure_backup_destination"] = clean_path
    return save_config(cfg)


def clear_backup_dest() -> bool:
    """Clears the configured secure external backup destination."""
    cfg = load_config()
    cfg.pop("secure_backup_destination", None)
    cfg.pop("backup_destination", None)
    return save_config(cfg)


def get_active_docx_preset_name() -> str:
    """Returns the name of the currently active DOCX preset."""
    cfg = load_config()
    docx_cfg = cfg.get("docx_formatting", {})
    preset = docx_cfg.get("active_preset", "standard-submission")
    if preset not in DOCX_PRESETS:
        preset = "standard-submission"
    return preset


def get_docx_config() -> dict:
    """Returns the resolved DOCX formatting dictionary."""
    cfg = load_config()
    docx_cfg = cfg.get("docx_formatting", {})
    preset_name = docx_cfg.get("active_preset", "standard-submission")
    base = dict(DOCX_PRESETS.get(preset_name, DOCX_PRESETS["standard-submission"]))
    base["active_preset"] = preset_name
    # Merge custom overrides if custom preset or explicit overrides present
    if "custom_overrides" in docx_cfg and isinstance(docx_cfg["custom_overrides"], dict):
        base.update(docx_cfg["custom_overrides"])
    return base


def set_docx_preset(preset_name: str) -> bool:
    """Sets the active DOCX formatting preset."""
    if preset_name not in DOCX_PRESETS:
        logger.error("Unknown DOCX preset: %s", preset_name)
        return False
    cfg = load_config()
    if "docx_formatting" not in cfg or not isinstance(cfg["docx_formatting"], dict):
        cfg["docx_formatting"] = {}
    cfg["docx_formatting"]["active_preset"] = preset_name
    return save_config(cfg)


def set_docx_option(key: str, val) -> bool:
    """Sets a specific DOCX formatting option."""
    cfg = load_config()
    if "docx_formatting" not in cfg or not isinstance(cfg["docx_formatting"], dict):
        cfg["docx_formatting"] = {}
    if "custom_overrides" not in cfg["docx_formatting"] or not isinstance(cfg["docx_formatting"]["custom_overrides"], dict):
        cfg["docx_formatting"]["custom_overrides"] = {}
    cfg["docx_formatting"]["custom_overrides"][key] = val
    cfg["docx_formatting"]["active_preset"] = "custom"
    return save_config(cfg)


def list_docx_presets() -> dict:
    """Returns all available DOCX presets."""
    return DOCX_PRESETS


def get_tips_enabled() -> bool:
    """Returns True if dynamic contextual tips are enabled (default: True)."""
    cfg = load_config()
    return bool(cfg.get("tips_enabled", True))


def set_tips_enabled(enabled: bool) -> bool:
    """Sets and persists dynamic tips enabled state."""
    cfg = load_config()
    cfg["tips_enabled"] = bool(enabled)
    return save_config(cfg)


def toggle_tips() -> bool:
    """Toggles dynamic tips enabled state and returns new value."""
    current = get_tips_enabled()
    set_tips_enabled(not current)
    return not current


def get_active_manuscript_name() -> str:
    """Returns configured active manuscript name/path or empty string."""
    cfg = load_config()
    return str(cfg.get("active_manuscript") or "").strip()


def set_active_manuscript(name: str) -> bool:
    """Sets and persists the active manuscript name or path."""
    cfg = load_config()
    cfg["active_manuscript"] = str(name).strip()
    return save_config(cfg)


def clear_active_manuscript() -> bool:
    """Clears the active manuscript preference."""
    cfg = load_config()
    cfg.pop("active_manuscript", None)
    return save_config(cfg)


def get_active_world_name() -> str:
    """Returns configured active world name/path or empty string."""
    cfg = load_config()
    return str(cfg.get("active_world") or "").strip()


def set_active_world(name: str) -> bool:
    """Sets and persists the active world name or path."""
    cfg = load_config()
    cfg["active_world"] = str(name).strip()
    return save_config(cfg)


def clear_active_world() -> bool:
    """Clears the active world preference."""
    cfg = load_config()
    cfg.pop("active_world", None)
    return save_config(cfg)


def get_active_universe_name() -> str:
    """Returns configured active universe name/path or empty string."""
    cfg = load_config()
    return str(cfg.get("active_universe") or "").strip()


def set_active_universe(name: str) -> bool:
    """Sets and persists the active universe name or path."""
    cfg = load_config()
    cfg["active_universe"] = str(name).strip()
    return save_config(cfg)


def clear_active_universe() -> bool:
    """Clears the active universe preference."""
    cfg = load_config()
    cfg.pop("active_universe", None)
    return save_config(cfg)


def get_default_scope() -> dict[str, Any]:
    """Returns default scope settings dictionary."""
    cfg = load_config()
    scope = cfg.get("default_scope", {})
    return scope if isinstance(scope, dict) else {}


def set_default_scope(scope_data: dict[str, Any]) -> bool:
    """Sets and persists default scope dictionary."""
    cfg = load_config()
    cfg["default_scope"] = scope_data
    return save_config(cfg)


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
}


def _deep_merge_dict(target: dict[str, Any], source: dict[str, Any]) -> None:
    """Recursively merges source dict into target dict in-place."""
    for k, v in source.items():
        if isinstance(v, dict) and isinstance(target.get(k), dict):
            _deep_merge_dict(target[k], v)
        else:
            target[k] = v


def get_authorial_policy() -> dict[str, Any]:
    """Returns configured authorial policy settings dictionary."""
    cfg = load_config()
    pol = cfg.get("authorial_policy", {})
    import copy
    res = copy.deepcopy(DEFAULT_AUTHORIAL_POLICY)
    if isinstance(pol, dict):
        _deep_merge_dict(res, pol)
    return res


def set_authorial_policy(policy_data: dict[str, Any]) -> bool:
    """Sets and persists authorial policy dictionary."""
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
    res = dict(base)

    def _merge_dict(target: dict[str, Any], source: dict[str, Any]) -> None:
        for k, v in source.items():
            if isinstance(v, dict) and isinstance(target.get(k), dict):
                _merge_dict(target[k], v)
            else:
                target[k] = v

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
                        _merge_dict(res, w_data)
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
                        _merge_dict(res, m_data)
                except Exception as e:
                    logger.debug("Failed reading constitution at %s: %s", cand, e)

    return res


def is_rule_suppressed(rule_id: str, constitution: dict[str, Any] | None = None) -> bool:
    """Checks whether a diagnostic rule ID is suppressed by the active Authorial Constitution."""
    if constitution is None:
        constitution = get_authorial_policy()
    diag = constitution.get("diagnostics", {})
    suppressed = set()
    if isinstance(diag, dict):
        suppressed.update(str(r).upper().strip() for r in diag.get("suppressed_rules", []))
    suppressed.update(str(r).upper().strip() for r in constitution.get("suppressed_rules", []))
    return rule_id.upper().strip() in suppressed



def get_world_axioms(world_name: str | None = None) -> dict[str, Any]:
    """Returns world axioms dictionary for world or global default."""
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


def get_daily_flow_state() -> dict[str, Any]:
    """Returns the daily flow ritual and cursor state dictionary."""
    cfg = load_config()
    flow = cfg.get("daily_flow_state", {})
    if not isinstance(flow, dict):
        flow = {}
    return {
        "last_active_manuscript": flow.get("last_active_manuscript", ""),
        "last_active_file": flow.get("last_active_file", ""),
        "last_cursor_line": int(flow.get("last_cursor_line", 1)),
        "next_time_bridge": flow.get("next_time_bridge", ""),
        "active_workspace_phase": flow.get("active_workspace_phase", "drafting"),
        "fast_idea_scraps": list(flow.get("fast_idea_scraps", [])),
    }


def set_daily_flow_state(state_data: dict[str, Any]) -> bool:
    """Sets and persists the daily flow ritual state."""
    cfg = load_config()
    current = get_daily_flow_state()
    current.update(state_data)
    cfg["daily_flow_state"] = current
    return save_config(cfg)



def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ars Arcanum Configuration Tool")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # backup-dest subcommand
    bd_parser = subparsers.add_parser("backup-dest", help="Manage secure backup destination")
    bd_sub = bd_parser.add_subparsers(dest="action", required=True)

    bd_sub.add_parser("get", help="Print current secure backup destination")

    set_p = bd_sub.add_parser("set", help="Set secure backup destination")
    set_p.add_argument("path", help="Absolute or relative path to secure backup directory")

    bd_sub.add_parser("clear", help="Clear configured secure backup destination")

    # docx-preset subcommand
    preset_parser = subparsers.add_parser("docx-preset", help="Manage DOCX formatting presets")
    preset_parser.add_argument("preset", nargs="?", help="Preset name to activate (standard-submission, modern-manuscript, classic-trade, custom)")

    # docx-presets list subcommand
    subparsers.add_parser("docx-presets", help="List all available DOCX formatting presets")

    # docx-config subcommand
    dcfg_parser = subparsers.add_parser("docx-config", help="View or set DOCX formatting options")
    dcfg_parser.add_argument("key", nargs="?", help="Option key (e.g. font_family, font_size_pt, line_spacing, margin_inches)")
    dcfg_parser.add_argument("value", nargs="?", help="Option value")

    # tips subcommand
    tips_parser = subparsers.add_parser("tips", help="Manage dynamic tips display preference")
    tips_sub = tips_parser.add_subparsers(dest="action", required=False)
    tips_sub.add_parser("get", help="Get current tips enabled status")
    tips_sub.add_parser("enable", help="Enable dynamic tips display")
    tips_sub.add_parser("disable", help="Disable dynamic tips display")
    tips_sub.add_parser("toggle", help="Toggle dynamic tips display")
    set_tips_p = tips_sub.add_parser("set", help="Set tips enabled status (true/false)")
    set_tips_p.add_argument("state", help="true or false")

    # active-manuscript subcommand
    ams_parser = subparsers.add_parser("active-manuscript", help="Manage active manuscript default")
    ams_sub = ams_parser.add_subparsers(dest="action", required=False)
    ams_sub.add_parser("get", help="Get active manuscript")
    ams_set = ams_sub.add_parser("set", help="Set active manuscript")
    ams_set.add_argument("name", help="Manuscript name or directory")
    ams_sub.add_parser("clear", help="Clear active manuscript")

    # active-world subcommand
    aw_parser = subparsers.add_parser("active-world", help="Manage active world default")
    aw_sub = aw_parser.add_subparsers(dest="action", required=False)
    aw_sub.add_parser("get", help="Get active world")
    aw_set = aw_sub.add_parser("set", help="Set active world")
    aw_set.add_argument("name", help="World name or directory")
    aw_sub.add_parser("clear", help="Clear active world")

    # active-universe subcommand
    au_parser = subparsers.add_parser("active-universe", help="Manage active universe default")
    au_sub = au_parser.add_subparsers(dest="action", required=False)
    au_sub.add_parser("get", help="Get active universe")
    au_set = au_sub.add_parser("set", help="Set active universe")
    au_set.add_argument("name", help="Universe name or directory")
    au_sub.add_parser("clear", help="Clear active universe")

    args = parser.parse_args(argv)

    if args.subcommand == "backup-dest":
        if args.action == "get":
            dest = get_backup_dest()
            if dest:
                print(dest)
                sys.exit(0)
            else:
                sys.exit(1)
        elif args.action == "set":
            if set_backup_dest(args.path):
                print(f"[CONFIG] Secure backup destination set to: {get_backup_dest()}")
                sys.exit(0)
            else:
                print("[!] Error saving configuration.", file=sys.stderr)
                sys.exit(1)
        elif args.action == "clear":
            if clear_backup_dest():
                print("[CONFIG] Secure backup destination cleared.")
                sys.exit(0)
            else:
                print("[!] Error updating configuration.", file=sys.stderr)
                sys.exit(1)

    elif args.subcommand == "docx-preset":
        if args.preset:
            if set_docx_preset(args.preset):
                print(f"[CONFIG] Active DOCX preset set to: {args.preset}")
                sys.exit(0)
            else:
                print(f"[!] Error: Invalid preset '{args.preset}'. Available: {', '.join(DOCX_PRESETS.keys())}", file=sys.stderr)
                sys.exit(1)
        else:
            print(get_active_docx_preset_name())
            sys.exit(0)

    elif args.subcommand == "docx-presets":
        active = get_active_docx_preset_name()
        print("=== Ars Arcanum DOCX Formatting Presets ===")
        for pid, info in DOCX_PRESETS.items():
            mark = " (active)" if pid == active else ""
            print(f"- {pid}{mark}: {info['name']}")
            print(f"    Font: {info['font_family']} {info['font_size_pt']}pt | Spacing: {info['line_spacing']}x | Margins: {info['margin_inches']}\"")
            print(f"    Description: {info['description']}")
        sys.exit(0)

    elif args.subcommand == "docx-config":
        if args.key and args.value is not None:
            val = args.value
            # Type cast numbers
            try:
                val = float(val) if "." in val else int(val)
            except ValueError:
                if val.lower() == "true":
                    val = True
                elif val.lower() == "false":
                    val = False
            if set_docx_option(args.key, val):
                print(f"[CONFIG] DOCX option '{args.key}' set to: {val}")
                sys.exit(0)
            else:
                print("[!] Error updating DOCX option.", file=sys.stderr)
                sys.exit(1)
        elif args.key:
            cfg = get_docx_config()
            if args.key in cfg:
                print(cfg[args.key])
                sys.exit(0)
            else:
                print(f"[!] Key '{args.key}' not found in DOCX configuration.", file=sys.stderr)
                sys.exit(1)
        else:
            print(json.dumps(get_docx_config(), indent=2))
            sys.exit(0)

    elif args.subcommand == "tips":
        action = getattr(args, "action", None)
        if action == "enable" or (action == "set" and getattr(args, "state", "").lower() in ("true", "1", "yes", "on")):
            set_tips_enabled(True)
            print("[CONFIG] Dynamic tips display enabled.")
            return 0
        if action == "disable" or (action == "set" and getattr(args, "state", "").lower() in ("false", "0", "no", "off")):
            set_tips_enabled(False)
            print("[CONFIG] Dynamic tips display disabled.")
            return 0
        if action == "toggle":
            new_val = toggle_tips()
            print(f"[CONFIG] Dynamic tips display {'enabled' if new_val else 'disabled'}.")
            return 0
        # Default or "get"
        enabled = get_tips_enabled()
        print(f"tips_enabled: {enabled}")
        return 0

    elif args.subcommand == "active-manuscript":
        action = getattr(args, "action", None)
        if action == "set" and hasattr(args, "name"):
            set_active_manuscript(args.name)
            print(f"[CONFIG] Active manuscript set to: {args.name}")
            return 0
        if action == "clear":
            clear_active_manuscript()
            print("[CONFIG] Active manuscript cleared.")
            return 0
        val = get_active_manuscript_name()
        print(val or "None")
        return 0

    elif args.subcommand == "active-world":
        action = getattr(args, "action", None)
        if action == "set" and hasattr(args, "name"):
            set_active_world(args.name)
            print(f"[CONFIG] Active world set to: {args.name}")
            return 0
        if action == "clear":
            clear_active_world()
            print("[CONFIG] Active world cleared.")
            return 0
        val = get_active_world_name()
        print(val or "None")
        return 0

    elif args.subcommand == "active-universe":
        action = getattr(args, "action", None)
        if action == "set" and hasattr(args, "name"):
            set_active_universe(args.name)
            print(f"[CONFIG] Active universe set to: {args.name}")
            return 0
        if action == "clear":
            clear_active_universe()
            print("[CONFIG] Active universe cleared.")
            return 0
        val = get_active_universe_name()
        print(val or "None")
        return 0

    return 0



if __name__ == "__main__":
    sys.exit(main())
