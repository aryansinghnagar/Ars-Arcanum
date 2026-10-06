#!/usr/bin/env python3
"""
Ars Arcanum Domain Engine Specifications Package (scripts/lib/registry_specs)
=============================================================================
Aggregates domain-specific EngineSpec definitions across all 7 architectural domains.
"""
from __future__ import annotations

from .domain_a_science import ENGINES as ENGINES_A
from .domain_b_narrative import ENGINES as ENGINES_B
from .domain_c_society import ENGINES as ENGINES_C
from .domain_d_editorial import ENGINES as ENGINES_D
from .domain_e_studios import ENGINES as ENGINES_E
from .domain_f_retrieval import ENGINES as ENGINES_F
from .domain_g_publishing import ENGINES as ENGINES_G

ALL_ENGINES = {
    **ENGINES_A,
    **ENGINES_B,
    **ENGINES_C,
    **ENGINES_D,
    **ENGINES_E,
    **ENGINES_F,
    **ENGINES_G,
}

__all__ = ["ALL_ENGINES"]
