#!/usr/bin/env python3
"""
Domain Portfolio Specifications for Ars Arcanum Registry.
"""
from __future__ import annotations

try:
    from lib.registry_base import EngineCategory, EngineSpec
except ImportError:
    from registry_base import EngineCategory, EngineSpec

ENGINES: dict[str, EngineSpec] = {
    "portfolio": EngineSpec(
        name="portfolio",
        category=EngineCategory.CORE,
        title="Portfolio & Drafting Velocity",
        description="Comprehensive overview of all universes, volumes, word counts, and drafting velocity",
        module_name="lib.portfolio",
        cli_command="portfolio",
        aliases=["portfolio", "series-overview", "author-stats"],
        studio_tab="Dashboard",
        logic_documentation="Aggregates multi-series universe statistics: lifetime word counts, active draft stages, daily drafting velocity, and deadline projections across all local repositories.",
        scientific_logic="""1. Aggregated Multi-Project Metric Rollup:
   Scans all discovered universe manifests and manuscript chapters:
   $$W_{\\text{total}} = \\sum_{i=1}^U \\sum_{j=1}^{V_i} W_{ij}, \\quad \\text{Velocity } V_{\\text{daily}} = \\frac{\\Delta W}{\\Delta t}$$
   Projects estimated completion dates based on historical 7-day rolling velocity.""",
        why_this_way="Professional authors managing multiple series need a unified high-altitude portfolio view of their productivity and deadlines without cloud SaaS trackers.",
        worldbuilding_relevance="Summarizes total lore volume across interconnected universes.",
        storytelling_relevance="Tracks milestone completion across simultaneous novel projects.",
        writing_relevance="Provides daily word velocity metrics and deadline projections.",
        subfeatures=[
            {"name": "Multi-Universe Word Counter", "rule": "Aggregates words across all local manuscripts and lore vaults.", "example": "arcanum portfolio"},
            {"name": "Drafting Velocity Projector", "rule": "Calculates daily pace and estimated book completion date.", "example": "arcanum portfolio --velocity"},
        ],
        extension_guide="""View portfolio overview:
```bash
arcanum portfolio
```""",
        advisory_guidance=[
            {"pattern": "Drafting velocity drops below target threshold", "option_a": "Adjust deadline schedule to accommodate realistic pacing", "option_b": "Schedule dedicated writing sprints", "option_c": "Accept variance during developmental plotting phase"},
        ],
    ),
}

__all__ = ["ENGINES"]
