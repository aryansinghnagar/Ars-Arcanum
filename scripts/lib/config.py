#!/usr/bin/env python3
"""
Ars Arcanum Configuration Engine Facade (scripts/lib/config.py)
==============================================================
Provides high-level programmatic API and CLI commands for managing:
- User preferences & XDG persistence (via lib.config_store)
- Standard DOCX formatting presets & typography (via lib.docx_presets)
- Active workspace targets & flow state (via lib.state)
- Authorial Constitution & governance policies (via lib.constitution)
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from typing import Any

try:
    from lib.config_store import (
        CONFIG_DIR_NAME,
        CONFIG_FILE_NAME,
        LEGACY_CONFIG_DIR_NAME,
        clear_backup_dest,
        get_backup_dest,
        get_backup_destination,
        get_config_dir,
        get_config_file_path,
        get_config_path,
        get_tips_enabled,
        load_config,
        save_config,
        set_backup_dest,
        set_tips_enabled,
        toggle_tips,
    )
    from lib.constitution import (
        DEFAULT_AUTHORIAL_POLICY,
        _deep_merge_dict,
        deep_merge_constitution,
        get_authorial_constitution,
        get_authorial_policy,
        get_disabled_engines,
        get_suppressed_rules,
        get_world_axioms,
        is_engine_enabled,
        is_rule_suppressed,
        load_authorial_constitution,
        set_authorial_policy,
        set_engine_enabled,
        set_world_axioms,
    )
    from lib.docx_presets import (
        DOCX_PRESETS,
        get_active_docx_preset_name,
        get_docx_config,
        get_docx_preset_names,
        list_docx_presets,
        set_docx_option,
        set_docx_preset,
    )
    from lib.state import (
        clear_active_manuscript,
        clear_active_universe,
        clear_active_world,
        get_active_manuscript_name,
        get_active_universe_name,
        get_active_world_name,
        get_daily_flow_state,
        get_default_scope,
        set_active_manuscript,
        set_active_universe,
        set_active_world,
        set_daily_flow_state,
        set_default_scope,
    )
except ImportError:
    from config_store import (  # type: ignore[no-redef]
        CONFIG_DIR_NAME,
        CONFIG_FILE_NAME,
        LEGACY_CONFIG_DIR_NAME,
        clear_backup_dest,
        get_backup_dest,
        get_backup_destination,
        get_config_dir,
        get_config_file_path,
        get_config_path,
        get_tips_enabled,
        load_config,
        save_config,
        set_backup_dest,
        set_tips_enabled,
        toggle_tips,
    )
    from constitution import (  # type: ignore[no-redef]
        DEFAULT_AUTHORIAL_POLICY,
        _deep_merge_dict,
        deep_merge_constitution,
        get_authorial_constitution,
        get_authorial_policy,
        get_disabled_engines,
        get_suppressed_rules,
        get_world_axioms,
        is_engine_enabled,
        is_rule_suppressed,
        load_authorial_constitution,
        set_authorial_policy,
        set_engine_enabled,
        set_world_axioms,
    )
    from docx_presets import (  # type: ignore[no-redef]
        DOCX_PRESETS,
        get_active_docx_preset_name,
        get_docx_config,
        get_docx_preset_names,
        list_docx_presets,
        set_docx_option,
        set_docx_preset,
    )
    from state import (  # type: ignore[no-redef]
        clear_active_manuscript,
        clear_active_universe,
        clear_active_world,
        get_active_manuscript_name,
        get_active_universe_name,
        get_active_world_name,
        get_daily_flow_state,
        get_default_scope,
        set_active_manuscript,
        set_active_universe,
        set_active_world,
        set_daily_flow_state,
        set_default_scope,
    )

logger = logging.getLogger("arcanum.config")


def get_ui_visual_preset() -> str:
    """Returns active UI visual preset name (default: sovereign-dark)."""
    cfg = load_config()
    return str(cfg.get("ui_visual_preset") or "sovereign-dark").strip()


def set_ui_visual_preset(preset: str) -> bool:
    """Sets and persists the active UI visual preset."""
    cfg = load_config()
    cfg["ui_visual_preset"] = preset.strip().lower()
    return save_config(cfg)


def get_typewriter_sound_preset() -> str:
    """Returns active typewriter procedural audio preset model (default: remington_1890)."""
    cfg = load_config()
    return str(cfg.get("typewriter_sound_preset") or "remington_1890").strip()


def set_typewriter_sound_preset(preset: str) -> bool:
    """Sets and persists the active typewriter procedural audio model."""
    cfg = load_config()
    cfg["typewriter_sound_preset"] = preset.strip().lower()
    return save_config(cfg)


def get_crt_fx_enabled() -> bool:
    """Returns whether CRT scanline mode is globally enabled."""
    cfg = load_config()
    return bool(cfg.get("crt_fx_enabled", False))


def set_crt_fx_enabled(enabled: bool) -> bool:
    """Sets and persists the CRT scanline effect preference."""
    cfg = load_config()
    cfg["crt_fx_enabled"] = bool(enabled)
    return save_config(cfg)


def _handle_backup_dest_cli(args: argparse.Namespace) -> int:
    if args.action == "get":
        dest = get_backup_dest()
        if dest:
            print(dest)
            return 0
        return 1
    if args.action == "set":
        if set_backup_dest(args.path):
            print(f"[CONFIG] Secure backup destination set to: {get_backup_dest()}")
            return 0
        print("[!] Error saving configuration.", file=sys.stderr)
        return 1
    if args.action == "clear":
        if clear_backup_dest():
            print("[CONFIG] Secure backup destination cleared.")
            return 0
        print("[!] Error updating configuration.", file=sys.stderr)
        return 1
    return 0


def _handle_docx_cli(args: argparse.Namespace) -> int:
    if args.subcommand == "docx-preset":
        if args.preset:
            if set_docx_preset(args.preset):
                print(f"[CONFIG] Active DOCX preset set to: {args.preset}")
                return 0
            print(
                f"[!] Error: Invalid preset '{args.preset}'. Available: {', '.join(DOCX_PRESETS.keys())}",
                file=sys.stderr,
            )
            return 1
        print(get_active_docx_preset_name())
        return 0

    if args.subcommand == "docx-presets":
        active = get_active_docx_preset_name()
        print("=== Ars Arcanum DOCX Formatting Presets ===")
        for pid, info in DOCX_PRESETS.items():
            mark = " (active)" if pid == active else ""
            print(f"- {pid}{mark}: {info['name']}")
            print(
                f"    Font: {info['font_family']} {info['font_size_pt']}pt | Spacing: {info['line_spacing']}x | Margins: {info['margin_inches']}\""
            )
            print(f"    Description: {info['description']}")
        return 0

    if args.subcommand == "docx-config":
        if args.key and args.value is not None:
            val: Any = args.value
            try:
                val = float(val) if "." in val else int(val)
            except ValueError:
                if str(val).lower() == "true":
                    val = True
                elif str(val).lower() == "false":
                    val = False
            if set_docx_option(args.key, val):
                print(f"[CONFIG] DOCX option '{args.key}' set to: {val}")
                return 0
            print("[!] Error updating DOCX option.", file=sys.stderr)
            return 1
        if args.key:
            cfg = get_docx_config()
            if args.key in cfg:
                print(cfg[args.key])
                return 0
            print(f"[!] Key '{args.key}' not found in DOCX configuration.", file=sys.stderr)
            return 1
        print(json.dumps(get_docx_config(), indent=2))
        return 0
    return 0


def _handle_tips_cli(args: argparse.Namespace) -> int:
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
    enabled = get_tips_enabled()
    print(f"tips_enabled: {enabled}")
    return 0


def _handle_state_cli(args: argparse.Namespace) -> int:
    action = getattr(args, "action", None)
    if args.subcommand == "active-manuscript":
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

    if args.subcommand == "active-world":
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

    if args.subcommand == "active-universe":
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


def _handle_theme_cli(args: argparse.Namespace) -> int:
    if args.subcommand == "theme":
        if args.preset:
            if set_ui_visual_preset(args.preset):
                print(f"[CONFIG] Active UI visual preset set to: {args.preset}")
                return 0
            print("[!] Error saving UI preset.", file=sys.stderr)
            return 1
        print(get_ui_visual_preset())
        return 0

    if args.subcommand == "sound-preset":
        if args.preset:
            if set_typewriter_sound_preset(args.preset):
                print(f"[CONFIG] Active typewriter sound preset set to: {args.preset}")
                return 0
            print("[!] Error saving sound preset.", file=sys.stderr)
            return 1
        print(get_typewriter_sound_preset())
        return 0

    if args.subcommand == "crt-fx":
        action = getattr(args, "action", None)
        if action == "enable":
            set_crt_fx_enabled(True)
            print("[CONFIG] CRT scanline effect enabled.")
            return 0
        if action == "disable":
            set_crt_fx_enabled(False)
            print("[CONFIG] CRT scanline effect disabled.")
            return 0
        val = get_crt_fx_enabled()
        print(f"crt_fx_enabled: {val}")
        return 0
    return 0


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

    # docx subcommands
    preset_parser = subparsers.add_parser("docx-preset", help="Manage DOCX formatting presets")
    preset_parser.add_argument(
        "preset",
        nargs="?",
        help="Preset name to activate (standard-submission, modern-manuscript, classic-trade, custom)",
    )
    subparsers.add_parser("docx-presets", help="List all available DOCX formatting presets")
    dcfg_parser = subparsers.add_parser("docx-config", help="View or set DOCX formatting options")
    dcfg_parser.add_argument(
        "key",
        nargs="?",
        help="Option key (e.g. font_family, font_size_pt, line_spacing, margin_inches)",
    )
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

    # state subcommands
    ams_parser = subparsers.add_parser("active-manuscript", help="Manage active manuscript default")
    ams_sub = ams_parser.add_subparsers(dest="action", required=False)
    ams_sub.add_parser("get", help="Get active manuscript")
    ams_set = ams_sub.add_parser("set", help="Set active manuscript")
    ams_set.add_argument("name", help="Manuscript name or directory")
    ams_sub.add_parser("clear", help="Clear active manuscript")

    aw_parser = subparsers.add_parser("active-world", help="Manage active world default")
    aw_sub = aw_parser.add_subparsers(dest="action", required=False)
    aw_sub.add_parser("get", help="Get active world")
    aw_set = aw_sub.add_parser("set", help="Set active world")
    aw_set.add_argument("name", help="World name or directory")
    aw_sub.add_parser("clear", help="Clear active world")

    au_parser = subparsers.add_parser("active-universe", help="Manage active universe default")
    au_sub = au_parser.add_subparsers(dest="action", required=False)
    au_sub.add_parser("get", help="Get active universe")
    au_set = au_sub.add_parser("set", help="Set active universe")
    au_set.add_argument("name", help="Universe name or directory")
    au_sub.add_parser("clear", help="Clear active universe")

    # theme subcommands
    theme_parser = subparsers.add_parser("theme", help="Manage UI visual preset")
    theme_parser.add_argument("preset", nargs="?", help="Preset name to activate")

    sound_parser = subparsers.add_parser("sound-preset", help="Manage typewriter audio model preset")
    sound_parser.add_argument("preset", nargs="?", help="Acoustic sound model to activate")

    crt_parser = subparsers.add_parser("crt-fx", help="Manage CRT scanline effect preference")
    crt_sub = crt_parser.add_subparsers(dest="action", required=False)
    crt_sub.add_parser("get", help="Get CRT scanline preference")
    crt_sub.add_parser("enable", help="Enable CRT scanlines")
    crt_sub.add_parser("disable", help="Disable CRT scanlines")

    args = parser.parse_args(argv)

    if args.subcommand == "backup-dest":
        return _handle_backup_dest_cli(args)
    if args.subcommand in ("docx-preset", "docx-presets", "docx-config"):
        return _handle_docx_cli(args)
    if args.subcommand == "tips":
        return _handle_tips_cli(args)
    if args.subcommand in ("active-manuscript", "active-world", "active-universe"):
        return _handle_state_cli(args)
    if args.subcommand in ("theme", "sound-preset", "crt-fx"):
        return _handle_theme_cli(args)

    return 0


__all__ = [
    "CONFIG_DIR_NAME",
    "CONFIG_FILE_NAME",
    "DEFAULT_AUTHORIAL_POLICY",
    "DOCX_PRESETS",
    "LEGACY_CONFIG_DIR_NAME",
    "_deep_merge_dict",
    "clear_active_manuscript",
    "clear_active_universe",
    "clear_active_world",
    "clear_backup_dest",
    "deep_merge_constitution",
    "get_active_docx_preset_name",
    "get_active_manuscript_name",
    "get_active_universe_name",
    "get_active_world_name",
    "get_authorial_constitution",
    "get_authorial_policy",
    "get_backup_dest",
    "get_backup_destination",
    "get_config_dir",
    "get_config_file_path",
    "get_config_path",
    "get_crt_fx_enabled",
    "get_daily_flow_state",
    "get_default_scope",
    "get_disabled_engines",
    "get_docx_config",
    "get_docx_preset_names",
    "get_suppressed_rules",
    "get_tips_enabled",
    "get_typewriter_sound_preset",
    "get_ui_visual_preset",
    "get_world_axioms",
    "is_engine_enabled",
    "is_rule_suppressed",
    "list_docx_presets",
    "load_authorial_constitution",
    "load_config",
    "main",
    "save_config",
    "set_active_manuscript",
    "set_active_universe",
    "set_active_world",
    "set_authorial_policy",
    "set_backup_dest",
    "set_crt_fx_enabled",
    "set_daily_flow_state",
    "set_default_scope",
    "set_docx_option",
    "set_docx_preset",
    "set_engine_enabled",
    "set_tips_enabled",
    "set_typewriter_sound_preset",
    "set_ui_visual_preset",
    "set_world_axioms",
    "toggle_tips",
]

if __name__ == "__main__":
    sys.exit(main())
