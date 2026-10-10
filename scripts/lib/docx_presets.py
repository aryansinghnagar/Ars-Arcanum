#!/usr/bin/env python3
"""
Ars Arcanum DOCX Presets & Typography Configuration Engine (scripts/lib/docx_presets.py)
=======================================================================================
Defines standard manuscript typography presets and custom overrides for .docx export.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("arcanum.docx_presets")

DOCX_PRESETS: dict[str, dict[str, Any]] = {
    "chicago-manual": {
        "name": "Chicago Manual of Style (CMOS)",
        "description": "Chicago Manual of Style (17th/18th ed.) author manuscript guidelines. Times New Roman 12pt, double-spaced, 1-inch margins, 0.5-inch indent, '#' scene breaks, running header (Surname / Short Title / Page #).",
        "font_family": "Times New Roman",
        "font_size_pt": 12.0,
        "line_spacing": 2.0,
        "margin_inches": 1.0,
        "first_line_indent_inches": 0.5,
        "scene_break_symbol": "#",
        "page_break_chapters": True,
        "include_header_slug": True,
    },
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
    },
}


PRESET_ALIASES: dict[str, str] = {
    "cmos": "chicago-manual",
    "chicago": "chicago-manual",
    "shunn": "standard-submission",
    "industry": "standard-submission",
    "modern": "modern-manuscript",
    "trade": "classic-trade",
    "classic": "classic-trade",
}


def _normalize_preset_name(preset_name: str) -> str:
    norm = preset_name.strip().lower().replace("_", "-")
    return PRESET_ALIASES.get(norm, norm)


def get_active_docx_preset_name() -> str:
    """Returns the name of the currently active DOCX preset."""
    try:
        from lib.config_store import load_config
    except ImportError:
        from config_store import load_config

    cfg = load_config()
    docx_cfg = cfg.get("docx_formatting", {})
    preset = _normalize_preset_name(docx_cfg.get("active_preset", "standard-submission"))
    if preset not in DOCX_PRESETS:
        preset = "standard-submission"
    return preset


def get_docx_config(preset_name: str | None = None) -> dict[str, Any]:
    """Returns the resolved DOCX formatting dictionary."""
    if preset_name:
        norm_name = _normalize_preset_name(preset_name)
        if norm_name in DOCX_PRESETS:
            return dict(DOCX_PRESETS[norm_name])

    try:
        from lib.config_store import load_config
    except ImportError:
        from config_store import load_config

    cfg = load_config()
    docx_cfg = cfg.get("docx_formatting", {})
    active = _normalize_preset_name(docx_cfg.get("active_preset", "standard-submission"))
    base = dict(DOCX_PRESETS.get(active, DOCX_PRESETS["standard-submission"]))
    base["active_preset"] = active
    # Merge custom overrides if custom preset or explicit overrides present
    if "custom_overrides" in docx_cfg and isinstance(docx_cfg["custom_overrides"], dict):
        base.update(docx_cfg["custom_overrides"])
    return base


def get_docx_preset_names() -> list[str]:
    """Returns the list of available DOCX preset keys."""
    return list(DOCX_PRESETS.keys())


def set_docx_preset(preset_name: str) -> bool:
    """Sets the active DOCX formatting preset."""
    norm_name = _normalize_preset_name(preset_name)
    if norm_name not in DOCX_PRESETS:
        logger.error("Unknown DOCX preset: %s", preset_name)
        return False

    try:
        from lib.config_store import load_config, save_config
    except ImportError:
        from config_store import load_config, save_config

    cfg = load_config()
    if "docx_formatting" not in cfg or not isinstance(cfg["docx_formatting"], dict):
        cfg["docx_formatting"] = {}
    cfg["docx_formatting"]["active_preset"] = norm_name
    return save_config(cfg)


def set_docx_option(key: str, val: Any) -> bool:
    """Sets a specific DOCX formatting option."""
    try:
        from lib.config_store import load_config, save_config
    except ImportError:
        from config_store import load_config, save_config

    cfg = load_config()
    if "docx_formatting" not in cfg or not isinstance(cfg["docx_formatting"], dict):
        cfg["docx_formatting"] = {}
    if "custom_overrides" not in cfg["docx_formatting"] or not isinstance(cfg["docx_formatting"]["custom_overrides"], dict):
        cfg["docx_formatting"]["custom_overrides"] = {}
    cfg["docx_formatting"]["custom_overrides"][key] = val
    cfg["docx_formatting"]["active_preset"] = "custom"
    return save_config(cfg)


def list_docx_presets() -> dict[str, dict[str, Any]]:
    """Returns all available DOCX presets."""
    return DOCX_PRESETS


__all__ = [
    "DOCX_PRESETS",
    "get_active_docx_preset_name",
    "get_docx_config",
    "get_docx_preset_names",
    "list_docx_presets",
    "set_docx_option",
    "set_docx_preset",
]
