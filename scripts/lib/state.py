#!/usr/bin/env python3
"""
Ars Arcanum Workspace & Author Flow State Manager (scripts/lib/state.py)
========================================================================
Manages active manuscript, world, universe defaults, target scoping preferences,
and author daily flow state / cursor tracking.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("arcanum.state")


def get_active_manuscript_name() -> str:
    """Returns configured active manuscript name/path or empty string."""
    try:
        from lib.config_store import load_config
    except ImportError:
        from config_store import load_config

    cfg = load_config()
    return str(cfg.get("active_manuscript") or "").strip()


def set_active_manuscript(name: str) -> bool:
    """Sets and persists the active manuscript name or path."""
    try:
        from lib.config_store import load_config, save_config
    except ImportError:
        from config_store import load_config, save_config

    cfg = load_config()
    cfg["active_manuscript"] = str(name).strip()
    return save_config(cfg)


def clear_active_manuscript() -> bool:
    """Clears the active manuscript preference."""
    try:
        from lib.config_store import load_config, save_config
    except ImportError:
        from config_store import load_config, save_config

    cfg = load_config()
    cfg.pop("active_manuscript", None)
    return save_config(cfg)


def get_active_world_name() -> str:
    """Returns configured active world name/path or empty string."""
    try:
        from lib.config_store import load_config
    except ImportError:
        from config_store import load_config

    cfg = load_config()
    return str(cfg.get("active_world") or "").strip()


def set_active_world(name: str) -> bool:
    """Sets and persists the active world name or path."""
    try:
        from lib.config_store import load_config, save_config
    except ImportError:
        from config_store import load_config, save_config

    cfg = load_config()
    cfg["active_world"] = str(name).strip()
    return save_config(cfg)


def clear_active_world() -> bool:
    """Clears the active world preference."""
    try:
        from lib.config_store import load_config, save_config
    except ImportError:
        from config_store import load_config, save_config

    cfg = load_config()
    cfg.pop("active_world", None)
    return save_config(cfg)


def get_active_universe_name() -> str:
    """Returns configured active universe name/path or empty string."""
    try:
        from lib.config_store import load_config
    except ImportError:
        from config_store import load_config

    cfg = load_config()
    return str(cfg.get("active_universe") or "").strip()


def set_active_universe(name: str) -> bool:
    """Sets and persists the active universe name or path."""
    try:
        from lib.config_store import load_config, save_config
    except ImportError:
        from config_store import load_config, save_config

    cfg = load_config()
    cfg["active_universe"] = str(name).strip()
    return save_config(cfg)


def clear_active_universe() -> bool:
    """Clears the active universe preference."""
    try:
        from lib.config_store import load_config, save_config
    except ImportError:
        from config_store import load_config, save_config

    cfg = load_config()
    cfg.pop("active_universe", None)
    return save_config(cfg)


def get_default_scope() -> dict[str, Any]:
    """Returns default scope settings dictionary."""
    try:
        from lib.config_store import load_config
    except ImportError:
        from config_store import load_config

    cfg = load_config()
    scope = cfg.get("default_scope", {})
    return scope if isinstance(scope, dict) else {}


def set_default_scope(scope_data: dict[str, Any]) -> bool:
    """Sets and persists default scope dictionary."""
    try:
        from lib.config_store import load_config, save_config
    except ImportError:
        from config_store import load_config, save_config

    cfg = load_config()
    cfg["default_scope"] = scope_data
    return save_config(cfg)


def get_daily_flow_state() -> dict[str, Any]:
    """Returns the daily flow ritual and cursor state dictionary."""
    try:
        from lib.config_store import load_config
    except ImportError:
        from config_store import load_config

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
    try:
        from lib.config_store import load_config, save_config
    except ImportError:
        from config_store import load_config, save_config

    cfg = load_config()
    current = get_daily_flow_state()
    current.update(state_data)
    cfg["daily_flow_state"] = current
    return save_config(cfg)


get_active_manuscript = get_active_manuscript_name
get_active_world = get_active_world_name
get_active_universe = get_active_universe_name


__all__ = [
    "clear_active_manuscript",
    "clear_active_universe",
    "clear_active_world",
    "get_active_manuscript",
    "get_active_manuscript_name",
    "get_active_universe",
    "get_active_universe_name",
    "get_active_world",
    "get_active_world_name",
    "get_daily_flow_state",
    "get_default_scope",
    "set_active_manuscript",
    "set_active_universe",
    "set_active_world",
    "set_daily_flow_state",
    "set_default_scope",
]
