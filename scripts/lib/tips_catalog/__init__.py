#!/usr/bin/env python3
"""
Ars Arcanum Modular Tips Catalog Package
"""

from __future__ import annotations

from typing import Any

try:
    from lib.tips_catalog.aliases import ENGINE_ALIASES
    from lib.tips_catalog.domain_cosmology import COSMOLOGY_PHYSICS_TIPS
    from lib.tips_catalog.domain_drafting import MANUSCRIPT_DRAFTING_TIPS
    from lib.tips_catalog.domain_editorial import EDITORIAL_CRAFT_TIPS
    from lib.tips_catalog.domain_narrative import NARRATIVE_CHRONOLOGY_TIPS
    from lib.tips_catalog.domain_society import SOCIETY_SYSTEMS_TIPS
    from lib.tips_catalog.domain_system import SYSTEM_OPS_TIPS
except ImportError:
    from tips_catalog.aliases import ENGINE_ALIASES
    from tips_catalog.domain_cosmology import COSMOLOGY_PHYSICS_TIPS
    from tips_catalog.domain_drafting import MANUSCRIPT_DRAFTING_TIPS
    from tips_catalog.domain_editorial import EDITORIAL_CRAFT_TIPS
    from tips_catalog.domain_narrative import NARRATIVE_CHRONOLOGY_TIPS
    from tips_catalog.domain_society import SOCIETY_SYSTEMS_TIPS
    from tips_catalog.domain_system import SYSTEM_OPS_TIPS

ALL_RAW_TIPS: list[dict[str, Any]] = (
    COSMOLOGY_PHYSICS_TIPS
    + SOCIETY_SYSTEMS_TIPS
    + NARRATIVE_CHRONOLOGY_TIPS
    + EDITORIAL_CRAFT_TIPS
    + MANUSCRIPT_DRAFTING_TIPS
    + SYSTEM_OPS_TIPS
)

__all__ = [
    "ALL_RAW_TIPS",
    "COSMOLOGY_PHYSICS_TIPS",
    "EDITORIAL_CRAFT_TIPS",
    "ENGINE_ALIASES",
    "MANUSCRIPT_DRAFTING_TIPS",
    "NARRATIVE_CHRONOLOGY_TIPS",
    "SOCIETY_SYSTEMS_TIPS",
    "SYSTEM_OPS_TIPS",
]
