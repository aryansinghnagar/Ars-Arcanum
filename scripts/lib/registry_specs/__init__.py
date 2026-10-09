#!/usr/bin/env python3
"""
Ars Arcanum Domain Engine Specifications Package (scripts/lib/registry_specs)
=============================================================================
Aggregates domain-specific EngineSpec definitions for the 14 retained core engines.
"""
from __future__ import annotations

from .domain_editorial import ENGINES as ENGINES_EDITORIAL
from .domain_infrastructure import ENGINES as ENGINES_INFRASTRUCTURE
from .domain_portfolio import ENGINES as ENGINES_PORTFOLIO
from .domain_publishing import ENGINES as ENGINES_PUBLISHING

ALL_ENGINES = {
    **ENGINES_EDITORIAL,
    **ENGINES_PORTFOLIO,
    **ENGINES_INFRASTRUCTURE,
    **ENGINES_PUBLISHING,
}

__all__ = ["ALL_ENGINES"]
