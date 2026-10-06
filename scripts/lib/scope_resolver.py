#!/usr/bin/env python3
"""
Ars Arcanum Scope & Context Resolver (scripts/lib/scope_resolver.py)
===================================================================
Active context resolution and path discovery for manuscripts, worlds, and universes.
"""

from __future__ import annotations

from pathlib import Path

try:
    from lib.scope_models import EngineScope
except ImportError:
    from scope_models import EngineScope  # type: ignore[no-redef]


def get_active_manuscript() -> Path | None:
    """
    Resolves the active manuscript using intelligent context precedence:
    1. Config setting ('active_manuscript') in config.json
    2. Current working directory (if inside a manuscript or has manuscript.yaml)
    3. Exactly one manuscript in ~/Manuscripts
    4. Most recently modified manuscript in ~/Manuscripts
    """
    try:
        from lib.config import load_config
        cfg = load_config()
        active_name = cfg.get("active_manuscript")
        if active_name:
            p = resolve_manuscript_path(active_name)
            if p and p.is_dir():
                return p
    except Exception:
        pass

    # Check cwd
    cwd = Path.cwd()
    if (cwd / "manuscript.yaml").is_file():
        return cwd
    for parent in [cwd, *cwd.parents]:
        if (parent / "manuscript.yaml").is_file():
            return parent
        if parent.parent.name == "Manuscripts" and parent.is_dir():
            return parent

    # Check ~/Manuscripts
    home = Path.home()
    mss = sorted((home / "Manuscripts").glob("*"), key=lambda p: str(p))
    mss = [p for p in mss if p.is_dir() and not p.name.startswith(".")]
    if len(mss) == 1:
        return mss[0]
    if len(mss) > 1:
        mss_sorted = sorted(mss, key=lambda p: p.stat().st_mtime, reverse=True)
        return mss_sorted[0]

    return None


def get_active_world() -> Path | None:
    """
    Resolves the active World Bible using intelligent context precedence:
    1. Config setting ('active_world') in config.json
    2. Current working directory (if inside a world or has world.yaml)
    3. Exactly one world in ~/Universes/*/* or ~/Worlds/*
    4. Most recently modified world vault
    """
    try:
        from lib.config import load_config
        cfg = load_config()
        active_name = cfg.get("active_world")
        if active_name:
            p = resolve_world_path(active_name)
            if p and p.is_dir():
                return p
    except Exception:
        pass

    # Check cwd
    cwd = Path.cwd()
    if (cwd / "world.yaml").is_file():
        return cwd
    for parent in [cwd, *cwd.parents]:
        if (parent / "world.yaml").is_file():
            return parent

    # Check ~/Universes/*/*
    home = Path.home()
    univ_worlds = sorted((home / "Universes").glob("*/*"), key=lambda p: str(p))
    univ_worlds = [p for p in univ_worlds if p.is_dir() and p.name not in ("Worlds", ".git") and not p.name.startswith(".")]
    if len(univ_worlds) == 1:
        return univ_worlds[0]

    # Check ~/Worlds/*
    legacy_worlds = sorted((home / "Worlds").glob("*"), key=lambda p: str(p))
    legacy_worlds = [p for p in legacy_worlds if p.is_dir() and not p.name.startswith(".")]
    if len(legacy_worlds) == 1:
        return legacy_worlds[0]

    all_worlds = univ_worlds + legacy_worlds
    if all_worlds:
        all_sorted = sorted(all_worlds, key=lambda p: p.stat().st_mtime, reverse=True)
        return all_sorted[0]

    return None


def get_active_universe() -> Path | None:
    """Resolves active universe directory."""
    try:
        from lib.config import load_config
        cfg = load_config()
        active_name = cfg.get("active_universe")
        if active_name:
            p = resolve_universe_path(active_name)
            if p and p.is_dir():
                return p
    except Exception:
        pass

    home = Path.home()
    universes = sorted((home / "Universes").glob("*"), key=lambda p: str(p))
    universes = [p for p in universes if p.is_dir() and not p.name.startswith(".")]
    if universes:
        return sorted(universes, key=lambda p: p.stat().st_mtime, reverse=True)[0]
    return None


def resolve_manuscript_path(
    target_str: str | Path | None = None,
    scope: EngineScope | None = None,
) -> Path | None:
    """Resolves manuscript path or name to absolute Path."""
    if not target_str and scope and scope.manuscript:
        target_str = scope.manuscript

    if not target_str:
        return get_active_manuscript()

    p = Path(target_str).expanduser().resolve()
    if p.is_dir():
        return p

    home = Path.home()
    target_clean = str(target_str).strip().lower()

    # Search in ~/Manuscripts
    for m_dir in sorted((home / "Manuscripts").glob("*")):
        if m_dir.is_dir() and m_dir.name.lower() == target_clean:
            return m_dir

    # Search in cwd
    p_cwd = Path.cwd() / target_str
    if p_cwd.is_dir():
        return p_cwd

    # Fuzzy match
    for m_dir in sorted((home / "Manuscripts").glob("*")):
        if m_dir.is_dir() and target_clean in m_dir.name.lower():
            return m_dir

    return None


def resolve_world_path(
    target_str: str | Path | None = None,
    scope: EngineScope | None = None,
) -> Path | None:
    """Resolves world path or name to absolute Path."""
    if not target_str and scope and scope.world:
        target_str = scope.world

    if not target_str:
        return get_active_world()

    p = Path(target_str).expanduser().resolve()
    if p.is_dir():
        return p

    home = Path.home()
    target_clean = str(target_str).strip().lower()

    # Search in ~/Universes/*/*
    for w_dir in sorted((home / "Universes").glob("*/*")):
        if w_dir.is_dir() and w_dir.name.lower() == target_clean:
            return w_dir

    # Search in ~/Worlds/*
    for w_dir in sorted((home / "Worlds").glob("*")):
        if w_dir.is_dir() and w_dir.name.lower() == target_clean:
            return w_dir

    # Search in cwd
    p_cwd = Path.cwd() / target_str
    if p_cwd.is_dir():
        return p_cwd

    # Fuzzy match
    for w_dir in sorted((home / "Universes").glob("*/*")):
        if w_dir.is_dir() and target_clean in w_dir.name.lower():
            return w_dir

    return None


def resolve_universe_path(
    target_str: str | Path | None = None,
    scope: EngineScope | None = None,
) -> Path | None:
    """Resolves universe path or name to absolute Path."""
    if not target_str and scope and scope.universe:
        target_str = scope.universe

    if not target_str:
        return get_active_universe()

    p = Path(target_str).expanduser().resolve()
    if p.is_dir():
        return p

    home = Path.home()
    target_clean = str(target_str).strip().lower()

    for u_dir in sorted((home / "Universes").glob("*")):
        if u_dir.is_dir() and u_dir.name.lower() == target_clean:
            return u_dir

    return None


def resolve_manuscript_dir(
    target_str: str | Path | None = None,
    scope: EngineScope | None = None,
) -> str:
    """Resolves manuscript target string or path to directory string path or empty string."""
    p = resolve_manuscript_path(target_str, scope=scope)
    return str(p) if p and p.is_dir() else ""


def resolve_world_dir(
    target_str: str | Path | None = None,
    scope: EngineScope | None = None,
) -> str:
    """Resolves world target string or path to directory string path or empty string."""
    p = resolve_world_path(target_str, scope=scope)
    return str(p) if p and p.is_dir() else ""


def resolve_universe_dir(
    target_str: str | Path | None = None,
    scope: EngineScope | None = None,
) -> str:
    """Resolves universe target string or path to directory string path or empty string."""
    p = resolve_universe_path(target_str, scope=scope)
    return str(p) if p and p.is_dir() else ""
