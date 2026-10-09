#!/usr/bin/env python3
"""
Ars Arcanum Configuration Storage Engine (scripts/lib/config_store.py)
======================================================================
Manages low-level configuration file resolution and atomic disk I/O in standard
XDG directories (~/.config/ars-arcanum/config.json).
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger("arcanum.config_store")

CONFIG_DIR_NAME = "ars-arcanum"
LEGACY_CONFIG_DIR_NAME = "arcanum"
CONFIG_FILE_NAME = "config.json"


def get_config_dir() -> Path:
    """Returns the XDG configuration directory for Ars Arcanum."""
    custom = os.environ.get("ARCANUM_CONFIG_DIR")
    if custom:
        return Path(custom).resolve()
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


get_config_path = get_config_file_path


def load_config() -> dict[str, Any]:
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


def save_config(config_data: dict[str, Any]) -> bool:
    """Saves configuration dictionary to disk with restrictive 0o600 permissions."""
    config_path = get_config_file_path()
    try:
        try:
            from lib.fs_utils import atomic_write
        except ImportError:
            try:
                from fs_utils import atomic_write
            except ImportError:
                from lib._bootstrap import atomic_write  # type: ignore[no-redef]
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


__all__ = [
    "CONFIG_DIR_NAME",
    "CONFIG_FILE_NAME",
    "LEGACY_CONFIG_DIR_NAME",
    "clear_backup_dest",
    "get_backup_dest",
    "get_backup_destination",
    "get_config_dir",
    "get_config_file_path",
    "get_config_path",
    "get_tips_enabled",
    "load_config",
    "save_config",
    "set_backup_dest",
    "set_tips_enabled",
    "toggle_tips",
]
