#!/usr/bin/env python3
"""
Ars Arcanum Resonance Mesh Domain Topology, Data Models & Structural Isomorphisms
(scripts/lib/resonance_data.py)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DomainPillar(str, Enum):
    COSMOLOGY_PHYSICS = "cosmology_physics"
    SOCIETY_SYSTEMS = "society_systems"
    NARRATIVE_CHRONOLOGY = "narrative_chronology"
    STYLISTICS_SENSES = "stylistics_senses"
    AUTHORING_PRODUCTION = "authoring_production"


@dataclass
class CrossDomainNode:
    id: str
    label: str
    pillar: DomainPillar
    engine: str
    node_type: str
    attributes: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    source_file: str | None = None
    summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "pillar": self.pillar.value,
            "engine": self.engine,
            "node_type": self.node_type,
            "attributes": self.attributes,
            "tags": self.tags,
            "source_file": self.source_file,
            "summary": self.summary,
        }


@dataclass
class CrossDomainEdge:
    source_id: str
    target_id: str
    relation: str  # e.g., 'causally_drives', 'constrains', 'isomorphic_to', 'manifests_in', 'lexically_influences', 'economically_impacts', 'thematically_mirrors', 'sensory_grounding_for'
    strength: float = 1.0  # 0.0 to 1.0
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation": self.relation,
            "strength": self.strength,
            "description": self.description,
            "metadata": self.metadata,
        }


@dataclass
class CascadeImpact:
    node_id: str
    field_name: str
    old_value: Any
    new_value: Any
    delta_description: str
    confidence: float
    pillar: DomainPillar
    engine: str
    advisory_action: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "field_name": self.field_name,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "delta_description": self.delta_description,
            "confidence": self.confidence,
            "pillar": self.pillar.value,
            "engine": self.engine,
            "advisory_action": self.advisory_action,
        }


@dataclass
class CascadeReport:
    origin_node_id: str
    origin_field: str
    origin_old_value: Any
    origin_new_value: Any
    impacts: list[CascadeImpact] = field(default_factory=list)
    summary: str = ""
    advisory_resolutions: list[dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "origin_node_id": self.origin_node_id,
            "origin_field": self.origin_field,
            "origin_old_value": self.origin_old_value,
            "origin_new_value": self.origin_new_value,
            "impact_count": len(self.impacts),
            "impacts": [i.to_dict() for i in self.impacts],
            "summary": self.summary,
            "advisory_resolutions": self.advisory_resolutions,
        }


@dataclass
class CreativeSpark:
    id: str
    title: str
    domains: list[str]
    pillars: list[str]
    core_analogy: str
    narrative_premise: str
    worldbuilding_hook: str
    scene_conflict: str
    sensory_palette: list[str]
    symbolic_mirror: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "domains": self.domains,
            "pillars": self.pillars,
            "core_analogy": self.core_analogy,
            "narrative_premise": self.narrative_premise,
            "worldbuilding_hook": self.worldbuilding_hook,
            "scene_conflict": self.scene_conflict,
            "sensory_palette": self.sensory_palette,
            "symbolic_mirror": self.symbolic_mirror,
        }


@dataclass
class CoherenceViolation:
    rule_id: str
    severity: str  # "error", "warning", "info"
    message: str
    nodes_involved: list[str]
    domain_engines: list[str]
    recommendation: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "message": self.message,
            "nodes_involved": self.nodes_involved,
            "domain_engines": self.domain_engines,
            "recommendation": self.recommendation,
        }


# =============================================================================
# Foundational Domains & Pillars (47 Canonical Domains)
# =============================================================================

FOUNDATIONAL_DOMAINS: list[tuple[str, str, str, str, str]] = [
    ("astrophysics", "Astrophysics & Spaceflight", "cosmology_physics", "astrophysics", "domain"),
    ("climate", "Planetary Climate & Biomes", "cosmology_physics", "climate", "domain"),
    ("cartography", "Vector Cartography & Geography", "cosmology_physics", "cartography", "domain"),
    ("calendar", "Planetary Calendars & Ephemeris", "cosmology_physics", "calendar", "domain"),
    ("ecology", "Ecology & Food Webs", "cosmology_physics", "ecology", "domain"),
    ("journey", "Travel Logistics & Attrition", "cosmology_physics", "journey", "domain"),
    ("cosmology", "Deific Pantheons & Theological Conflict", "cosmology_physics", "cosmology", "domain"),
    ("factions", "Geopolitical Factions & Diplomacy", "society_systems", "factions", "domain"),
    ("economy", "Macroeconomics & Currencies", "society_systems", "economy", "domain"),
    ("magic_system", "Magic System & Arcane Axioms", "society_systems", "magic_system", "domain"),
    ("conlang", "Conlang Phonotactics & Lexicon", "society_systems", "conlang", "domain"),
    ("genealogy", "Dynastic Lineage & Succession", "society_systems", "genealogy", "domain"),
    ("tactical_sim", "Tactical Skirmish & Battle Sim", "society_systems", "tactical_sim", "domain"),
    ("causality", "Causal DAG & Decisions", "narrative_chronology", "causality", "domain"),
    ("timeline_sync", "Dual-Track Timeline Sync", "narrative_chronology", "timeline_sync", "domain"),
    ("structure", "Story Paradigms & Acts", "narrative_chronology", "structure", "domain"),
    ("plot_matrix", "Plot Matrix & Subplots", "narrative_chronology", "plot_matrix", "domain"),
    ("prophecy", "Prophecy Lifecycle Tracker", "narrative_chronology", "prophecy", "domain"),
    ("dramatis_personae", "Dramatis Personae Matrix", "narrative_chronology", "dramatis_personae", "domain"),
    ("story_canvas", "Visual Story Canvas", "narrative_chronology", "story_canvas", "domain"),
    ("manuscript_scaffold", "Manuscript Structure Scaffolder", "narrative_chronology", "manuscript_scaffold", "domain"),
    ("continuity", "Semantic Continuity & Trait Linter", "stylistics_senses", "continuity", "domain"),
    ("series_continuity", "Series Continuity Ledger", "stylistics_senses", "series_continuity", "domain"),
    ("codex_export", "World Wiki Codex", "stylistics_senses", "codex_export", "domain"),
    ("typography_cleaner", "Typography Cleaner", "stylistics_senses", "typography_cleaner", "domain"),
    ("writing_sprint", "Writing Sprint Analytics", "authoring_production", "writing_sprint", "domain"),
    ("revision_heatmap", "Revision Churn Heatmap", "authoring_production", "revision_heatmap", "domain"),
    ("manuscript_diff", "Visual Draft Diff & Redline", "authoring_production", "manuscript_diff", "domain"),
    ("zen_studio", "Zen Drafting Studio", "authoring_production", "zen_studio", "domain"),
    ("ambient", "Ambient Soundscape Player", "authoring_production", "ambient", "domain"),
    ("portfolio", "Portfolio Velocity Tracker", "authoring_production", "portfolio", "domain"),
    ("studio_hub", "Studio Desktop Hub", "authoring_production", "studio_hub", "domain"),
    ("vault_search", "Local Vault Search & Lore Engine", "authoring_production", "vault_search", "domain"),
    ("corpus_export", "Universal Corpus Exporter", "authoring_production", "corpus_export", "domain"),
    ("importer", "Batch Manuscript Importer", "authoring_production", "importer", "domain"),
    ("docx_sync", "DOCX Bidirectional Sync", "authoring_production", "docx_sync", "domain"),
    ("world_doctor", "World Bible Doctor", "authoring_production", "world_doctor", "domain"),
    ("diagnostics", "System Diagnostics", "authoring_production", "diagnostics", "domain"),
    ("omnibus", "Series Omnibus Compiler", "authoring_production", "omnibus", "domain"),
    ("frontmatter_builder", "Frontmatter Builder", "authoring_production", "frontmatter_builder", "domain"),
    ("preflight", "Typesetting Preflight", "authoring_production", "preflight", "domain"),
    ("migrate", "Vault Migration", "authoring_production", "migrate", "domain"),
    ("config", "Project Configuration", "authoring_production", "config", "domain"),
    ("cache", "Performance Cache", "authoring_production", "cache", "domain"),
    ("fs_utils", "Atomic File System", "authoring_production", "fs_utils", "domain"),
    ("tips", "Dynamic Intelligent Tip Engine", "authoring_production", "tips", "domain"),
    ("resonance", "Resonance Mesh & Cross-Domain Synthesizer", "authoring_production", "resonance", "domain"),
]

# =============================================================================
# Foundational Cross-Domain Causal Edges
# =============================================================================

FOUNDATIONAL_EDGES: list[tuple[str, str, str, float, str]] = [
    ("astrophysics", "climate", "causally_drives", 0.95, "Stellar luminosity, orbital distance, and axial tilt determine planetary solar insolation and seasonal climate bands."),
    ("astrophysics", "calendar", "causally_drives", 0.95, "Orbital period and planetary rotation dictate solar year length, day length, and leap cycle rules."),
    ("astrophysics", "cosmology", "thematically_mirrors", 0.85, "Celestial mechanics and orbital alignments shape deific mythologies and astrological pantheons."),
    ("cosmology", "magic_system", "causally_drives", 0.90, "Divine domains, deific mandates, and holy taboos govern metaphysical spell limitations."),
    ("cosmology", "factions", "manifests_in", 0.90, "Theological dogmas, holy orders, and religious schisms drive factional alliances and inquisitions."),
    ("climate", "cartography", "manifests_in", 0.90, "Global atmospheric circulation and Köppen thermal zones define biome distribution on geographic maps."),
    ("climate", "ecology", "constrains", 0.90, "Precipitation and temperature extremes constrain primary biomass productivity and biome carrying capacities."),
    ("ecology", "economy", "economically_impacts", 0.85, "Flora and fauna resources define agricultural staple crops, livestock commodities, and trade goods."),
    ("economy", "factions", "causally_drives", 0.85, "Trade route wealth, resource scarcity, and currency stability drive faction alliances, tensions, and wars."),
    ("factions", "tactical_sim", "manifests_in", 0.90, "Diplomatic rivalries and territorial disputes trigger military engagements and strategic skirmishes."),
    ("cartography", "journey", "constrains", 0.90, "Geographic topography, elevation, and river barriers dictate travel routes, speeds, and caloric costs."),
    ("journey", "tactical_sim", "constrains", 0.85, "Army supply train logistics and terrain march rates determine military attrition and siege sustainability."),
    ("astrophysics", "magic_system", "thematically_mirrors", 0.75, "Celestial alignments and orbital nodes dictate arcane leylines and magical power fluctuations."),
    ("magic_system", "economy", "economically_impacts", 0.80, "Magical manufacturing, transmutation limits, and mana costs reshape labor value and commodity prices."),
    ("factions", "genealogy", "manifests_in", 0.85, "Noble houses and dynastic alliances cement geopolitical pacts and succession claims."),
    ("cartography", "conlang", "constrains", 0.75, "Geographic separation by oceans and mountains drives phonotactic drift and dialect divergence."),
    ("conlang", "factions", "lexically_influences", 0.80, "Cultural honorifics, titles, and linguistic idioms reflect faction caste structures and values."),
    ("factions", "dramatis_personae", "manifests_in", 0.90, "Faction loyalties, ranks, and ideologies shape character motivations and interpersonal dynamics."),
    ("genealogy", "dramatis_personae", "manifests_in", 0.90, "Bloodlines, inheritances, and family feuds define character backstories and rivalries."),
    ("dramatis_personae", "continuity", "constrains", 0.95, "Character physical traits, titles, and frontmatter metadata must remain consistent across all chapters."),
    ("causality", "timeline_sync", "causally_drives", 0.95, "Causal preconditions and consequence chains determine historical chronological event ordering."),
    ("timeline_sync", "structure", "constrains", 0.90, "Historical chronology provides the canvas for narrative story arcs (3-Act, 8-Sequence, Kishotenketsu)."),
    ("structure", "plot_matrix", "manifests_in", 0.90, "Master act milestones dictate subplot pacing, climax convergences, and midpoint twists."),
    ("plot_matrix", "story_canvas", "manifests_in", 0.90, "Subplot scene goals and chapter milestones map to visual story corkboard cards."),
    ("prophecy", "causality", "constrains", 0.85, "Prophetic constraints and metaphorical clauses create immutable causal anchor points in the timeline."),
    ("prophecy", "timeline_sync", "causally_drives", 0.90, "Prophetic fulfillment milestones anchor critical timestamp intervals in the timeline."),
    ("continuity", "series_continuity", "manifests_in", 0.90, "Book-level continuity facts aggregate into multi-volume series canon ledgers."),
    ("world_doctor", "continuity", "constrains", 0.95, "World Bible Doctor verifies wiki-link integrity and typed frontmatter references across the vault."),
    ("zen_studio", "vault_search", "thematically_mirrors", 0.85, "In-situ drafting leverages real-time local semantic vault search for instant lore lookup."),
    ("story_canvas", "structure", "manifests_in", 0.90, "Visual corkboard cards map directly to master act structures and chapter beats."),
    ("manuscript_scaffold", "structure", "manifests_in", 0.95, "Pre-seeds chapter and act divisions mapped to 16 canonical story structure paradigms."),
    ("manuscript_scaffold", "story_canvas", "manifests_in", 0.90, "Generates structural corkboard cards and narrative milestone columns from template divisions."),
    ("tips", "zen_studio", "sensory_grounding_for", 0.90, "Provides in-situ masterclass craft wisdom and non-obvious guidance in the drafting drawer."),
    ("tips", "studio_hub", "manifests_in", 0.90, "Surfaces non-intrusive contextual telemetry tips across the top status banner."),
    ("resonance", "world_doctor", "causally_drives", 0.95, "Synthesizes multi-domain cross-validation checks and causal ripple analyses."),
    ("resonance", "studio_hub", "manifests_in", 0.95, "Powers interactive 5-pillar resonance graph and simulation lab in the desktop hub."),
    ("corpus_export", "vault_search", "causally_drives", 0.95, "Exports structured JSONL and SQLite tables consumed by hybrid vault search retriever."),
    ("omnibus", "series_continuity", "constrains", 0.90, "Synthesizes cross-volume continuity ledgers into multi-book omnibus."),
    ("preflight", "typography_cleaner", "constrains", 0.90, "Ensures smart quotes, dashes, and ellipsis compliance before publishing."),
    ("calendar", "timeline_sync", "causally_drives", 0.95, "Translates planetary ephemeris into narrative and chronological timestamps."),
    ("world_doctor", "codex_export", "constrains", 0.95, "Doctor-validated wikilink topology compiles into static offline World Wiki encyclopedia."),
    ("codex_export", "dramatis_personae", "manifests_in", 0.85, "Codex export builds glossary indexes and cross-referenced character dossiers."),
    ("writing_sprint", "zen_studio", "manifests_in", 0.95, "Live sprint timer and word-per-minute telemetry stream directly into Zen Drafting Studio."),
    ("writing_sprint", "portfolio", "causally_drives", 0.90, "Daily sprint metrics and drafting velocity aggregate into author portfolio analytics."),
    ("manuscript_diff", "revision_heatmap", "causally_drives", 0.95, "Line-level redline diffs aggregate into chapter revision churn and density heatmaps."),
    ("revision_heatmap", "plot_matrix", "manifests_in", 0.85, "High-churn revision hot spots correlate with structural chapter restructurings."),
    ("docx_sync", "manuscript_diff", "manifests_in", 0.90, "Roundtrip DOCX synchronization changes produce visual redline diffs against markdown."),
    ("manuscript_diff", "zen_studio", "manifests_in", 0.85, "Draft comparison redlines display in-situ during drafting and revision sessions."),
    ("ambient", "zen_studio", "sensory_grounding_for", 0.90, "Atmospheric soundscapes play in background during distraction-free drafting."),
    ("ambient", "climate", "manifests_in", 0.85, "Atmospheric weather profiles and biome acoustic dynamics configure focus soundscapes."),
    ("portfolio", "studio_hub", "manifests_in", 0.95, "Portfolio velocity, word counts, and milestone completion render in desktop studio hub."),
    ("omnibus", "portfolio", "manifests_in", 0.90, "Series omnibus compilation updates multi-volume catalog status and publishing readiness."),
    ("importer", "manuscript_scaffold", "causally_drives", 0.90, "Batch imported Scrivener and Word files scaffold into standardized act/chapter layouts."),
    ("importer", "docx_sync", "manifests_in", 0.90, "Converts foreign documents into bi-directional syncable markdown manuscripts."),
    ("docx_sync", "preflight", "constrains", 0.90, "Editorial roundtrip Word documents are validated for style and typography compliance."),
    ("zen_studio", "docx_sync", "manifests_in", 0.85, "Zen studio drafts export cleanly to external editors via synchronized Word docx."),
    ("diagnostics", "fs_utils", "constrains", 0.95, "System diagnostics verify atomic write guarantees, lockfile safety, and disk storage."),
    ("diagnostics", "studio_hub", "manifests_in", 0.90, "Provides live health badges and toolchain diagnostic cards in desktop studio hub."),
    ("frontmatter_builder", "continuity", "constrains", 0.95, "Standardizes YAML metadata schemas for character trait and lore continuity linting."),
    ("frontmatter_builder", "world_doctor", "manifests_in", 0.90, "Builds schema-compliant frontmatter headers for world bible lore entries."),
    ("migrate", "world_doctor", "causally_drives", 0.95, "Migrates and repairs legacy obsidian vaults to standard schema verified by world doctor."),
    ("migrate", "corpus_export", "manifests_in", 0.90, "Upgrades project structure to enable universal structured corpus export and vault search."),
    ("config", "studio_hub", "manifests_in", 0.95, "Stores persistent studio preferences, theme settings, and engine configurations."),
    ("config", "tips", "constrains", 0.90, "Persistently configures ambient tip display frequency, pillars, and author preferences."),
    ("cache", "vault_search", "causally_drives", 0.95, "Caches token embeddings, term vectors, and FTS5 search indices for instant lookup."),
    ("cache", "fs_utils", "constrains", 0.90, "Accelerates mtime-keyed file change detection and atomic cache invalidation."),
    ("fs_utils", "corpus_export", "constrains", 0.95, "Guarantees crash-safe atomic writes for SQLite databases and JSONL export datasets."),
    ("fs_utils", "omnibus", "constrains", 0.90, "Provides atomic multi-volume compilation and directory synchronization."),
    ("typography_cleaner", "zen_studio", "manifests_in", 0.90, "Automated smart quote and punctuation formatting runs in-situ during Zen drafting."),
    ("conlang", "dramatis_personae", "lexically_influences", 0.85, "Phonotactic naming rules shape character names and aristocratic titles."),
    ("plot_matrix", "causality", "constrains", 0.90, "Subplot milestones and Chekhov guns enforce causal DAG constraints across chapters."),
]

# =============================================================================
# Cross-Domain Structural Analogy & Isomorphism Patterns
# =============================================================================

STRUCTURAL_ISOMORPHISMS: list[dict[str, Any]] = [
    {
        "id": "iso-thermo-politics",
        "title": "Thermodynamic Entropy & Geopolitical Institutional Decay",
        "domains": ["astrophysics", "factions", "economy"],
        "analogy": "Closed thermodynamic systems experience entropy increases; similarly, isolated political factions experience institutional inertia, rent-seeking, and bureaucratic friction unless renewed by external energy/trade influx.",
        "worldbuilding_hook": "An ancient empire's capital city is strictly sealed off to preserve purity, inadvertently starving its economic and magical energy reserves into systemic collapse.",
        "scene_conflict": "A reformer diplomat attempts to open trade borders with a rival guild against hardline traditionalists who view isolation as sacred virtue.",
        "sensory_palette": ["smell of dry parchment and stagnant oil", "clanging brass clocks losing calibration", "decaying tapestries in drafty stone corridors"],
        "symbolic_mirror": "A dwindling stellar furnace or dying lamp mirrors the ruler's deteriorating cognitive hold over the imperial provinces.",
    },
    {
        "id": "iso-ecology-magic-cost",
        "title": "Trophic Energy Pyramids & Arcane Resource Scarcity",
        "domains": ["ecology", "magic_system", "economy"],
        "analogy": "Only ~10% of biological energy transfers up trophic levels; similarly, high-tier magical feats consume exponentially more primary biomass/mana, creating an arcane carrying capacity limit on wizard populations.",
        "worldbuilding_hook": "Casting arch-sorcery requires consuming the caloric yield of an entire farming valley, making high wizards feared like apex apex predators by commoners.",
        "scene_conflict": "A village healer is confronted by royal battlemages requisitioning the harvest to fuel an impending border barrier spell.",
        "sensory_palette": ["shriveled wheat stalks crumbling to ash", "sweet ozone ozone scent of mana exhaustion", "hollow eyes of starving agrarian laborers"],
        "symbolic_mirror": "A starving pack of winter wolves encircling a fortress while inside the court squanders energy on frivolous light spells.",
    },
    {
        "id": "iso-tectonics-linguistics",
        "title": "Plate Tectonics & Conlang Dialect Divergence",
        "domains": ["cartography", "conlang", "genealogy"],
        "analogy": "Continental drift creates mountain cordilleras and impassable rifts; geographical isolation accelerates consonant shifts (Grimm's Law) and grammatical bifurcation among separated royal branches.",
        "worldbuilding_hook": "Two neighboring kingdoms that share common ancestral kings can no longer understand each other's legal decrees after a geological cataclysm severed the mountain pass 300 years ago.",
        "scene_conflict": "A royal herald's formal ultimatum is misconstrued as an insult due to a palatal shift in the verb conjugations of the northern dialect.",
        "sensory_palette": ["echoing vowel tones in granite valleys", "harsh guttural fricatives of mountain sentinels", "cracking sound of shifting scree underfoot"],
        "symbolic_mirror": "A deep jagged fissure running through a treaty courtyard reflecting the fractured lineage of two cousin monarchs.",
    },
    {
        "id": "iso-orbital-prophecy",
        "title": "Keplerian Orbital Resonance & Prophetic Cycles",
        "domains": ["astrophysics", "prophecy", "timeline_sync"],
        "analogy": "Celestial bodies in orbital resonance (e.g. 1:2:4 Laplace resonance) generate deterministic recurring alignments; ancient prophecies are celestial clockwork tracking mathematical recurrence of gravitational nodes.",
        "worldbuilding_hook": "The 'Doomsday Prophecy' is actually an astronomical calculation of when three moons align to induce massive seismic mantle plumes and mana surge tides.",
        "scene_conflict": "An astronomer-priest discovers the sacred eclipse alignment will occur three years earlier than the scripture dogma predicted, exposing the high temple's chronological fraud.",
        "sensory_palette": ["creaking armillary spheres of polished bronze", "violet glow along the horizon as twin moons converge", "sharp chill of sudden pre-dawn shadow"],
        "symbolic_mirror": "The converging paths of three estranged protagonists reflecting the inevitable alignment of three celestial bodies in the sky.",
    },
    {
        "id": "iso-immunology-espionage",
        "title": "Immune Response Cascades & Covert Intelligence Networks",
        "domains": ["ecology", "factions", "tactical_sim"],
        "analogy": "Innate vs adaptive immune responses mirror general palace guards vs sleeper cell assassins: antigen detection triggers cytokine storm inflammation just as border infiltration triggers nationwide martial law crackdowns.",
        "worldbuilding_hook": "The spymaster operates like an autoimmune disease—identifying harmless loyal citizens as foreign pathogens and systematically eliminating the kingdom's own vital administrative organs.",
        "scene_conflict": "A double agent must bypass biological quarantine sensors that also detect encrypted magical ink woven into skin pigments.",
        "sensory_palette": ["feverish sweat on cold stone flags", "bitter herbal teas masking poison antidotes", "muffled clatter of midnight arrest battalions"],
        "symbolic_mirror": "A character's infected wound throbbing with heat while the surrounding city erupts in riot and wildfire.",
    },
    {
        "id": "iso-hydrology-currency",
        "title": "Hydrological Basins & Monetary Velocity / Inflation",
        "domains": ["climate", "economy", "journey"],
        "analogy": "River basins direct water runoff from alpine headwaters to delta estuaries; monetary currency flows along trade rivers, where damming (hoarding) produces upstream stagnation and sudden downstream droughts.",
        "worldbuilding_hook": "A river fortress guild levies crippling tariffs on grain barges, causing monetary starvation in coastal cities and triggering hyperinflation of substitute barter currencies.",
        "scene_conflict": "A merchant captain must smuggle silver ingots down river rapids before the guild's price-fixing decree takes effect at sunrise.",
        "sensory_palette": ["sloshing river water against hull timbers", "heavy clink of debased copper coins in wet leather pouches", "smell of tar, marsh weeds, and rotten silt"],
        "symbolic_mirror": "A dry riverbed strewn with bleached pebbles mirroring the empty vaults and defaulted promises of the royal treasury.",
    },
    {
        "id": "iso-branching-multiverse",
        "title": "Quantum Many-Worlds Branching & Interactive Decision Trees",
        "domains": ["causality", "story_canvas", "plot_matrix"],
        "analogy": "Quantum state decoherence generates non-communicating parallel histories; narrative choice nodes create branching causal graphs where subtle moral choices diverge into vastly distinct world states.",
        "worldbuilding_hook": "An ancient temporal observatory allows travelers to peer into branching world-lines, revealing that a single assassinated ambassador caused the collapse of three empires in alternate branches.",
        "scene_conflict": "A protagonist must decide whether to collapse a divergent timeline branch that would erase a parallel version of their daughter to save the primary world.",
        "sensory_palette": ["humming crystal prism arrays splitting white light into ghost spectra", "hair standing on end from electrostatic temporal shearing", "faint echoes of unmade conversations in empty rooms"],
        "symbolic_mirror": "A shattered mirror where each shard reflects a slightly different expression of the same face.",
    },
    {
        "id": "iso-acoustic-immersion",
        "title": "Acoustic Resonance, Biome Weather & Ambient Cognitive Flow",
        "domains": ["ambient", "climate", "zen_studio"],
        "analogy": "Binaural frequency entrainment and acoustic soundscapes modulate cognitive focus states, just as planetary weather soundscapes ground narrative scene immersion in physical reality.",
        "worldbuilding_hook": "A monastic order uses resonant stone amphitheaters and cavern wind pipes to tune human emotional states and induce collective prophetic trance states.",
        "scene_conflict": "An infiltrator must navigate a temple whose acoustic dampening floors amplify the slightest heartbeat or weapon click.",
        "sensory_palette": ["deep subterranean drone vibrating through stone soles", "rhythmic patter of frozen sleet on canvas pavilions", "warm crackle of dry pine logs in a hearth"],
        "symbolic_mirror": "A single tuned tuning fork humming in harmony with an approaching thunderhead.",
    },
    {
        "id": "iso-scaffold-cathedral",
        "title": "Gothic Architectural Ribbing & Narrative Structural Paradigms",
        "domains": ["manuscript_scaffold", "structure", "story_canvas"],
        "analogy": "Flying buttresses and ribbed vaults distribute massive stone roof loads into balanced ground vectors; narrative act and division presets distribute reader emotional tension across deterministic milestone beats.",
        "worldbuilding_hook": "Cathedrals and grand administrative arches are built with proportional harmonic ratios that secretly encode the rise and fall of historical dynasties.",
        "scene_conflict": "An architect-turned-rebel discovers structural fault lines deliberately engineered into the royal basilica to collapse upon coronation day.",
        "sensory_palette": ["smell of damp lime mortar and freshly cut limestone", "soaring verticality of shadowed granite arches", "dust motes drifting through stained-glass rose windows"],
        "symbolic_mirror": "A towering stone arch holding immense weight through balanced counter-forces mirroring a fragile political alliance.",
    },
]


# =============================================================================
# Deterministic Cascade Impact Calculation Engine
# =============================================================================

def compute_cascade_impacts(
    origin_node_id: str,
    param_key: str,
    new_value: Any,
    old_value: Any,
    nodes: dict[str, CrossDomainNode],
    adjacency: dict[str, list[CrossDomainEdge]],
) -> list[CascadeImpact]:
    """Computes deterministic cascade impacts across physics, society, and narrative domains."""
    impacts: list[CascadeImpact] = []
    visited = {origin_node_id}
    param_norm = param_key.lower().replace("-", "_")

    # 1. Astrophysics / Cosmology Changes
    if param_norm in ["axial_tilt", "axial_tilt_deg", "obliquity"]:
        val_f = float(new_value)
        old_f = float(old_value) if old_value is not None else 23.4
        diff = val_f - old_f

        impacts.append(CascadeImpact(
            node_id="climate",
            field_name="seasonal_extremes",
            old_value="Moderate Seasons",
            new_value="Severe Continental Seasons" if val_f > 30 else ("Mild Uniform Climate" if val_f < 10 else "Earth-Normal Seasons"),
            delta_description=f"Axial tilt shift ({val_f:.1f}°) expands polar circle latitudes and intensifies summer/winter thermal contrasts.",
            confidence=0.98,
            pillar=DomainPillar.COSMOLOGY_PHYSICS,
            engine="climate",
            advisory_action="Recalculate Köppen temperature bands with `arcanum calc climate`.",
        ))
        impacts.append(CascadeImpact(
            node_id="ecology",
            field_name="crop_growing_season",
            old_value="240 days",
            new_value=f"{max(60, int(240 - abs(diff) * 6))} days",
            delta_description="High obliquity compresses agrarian planting windows into rapid spring surges followed by deep freezes.",
            confidence=0.92,
            pillar=DomainPillar.COSMOLOGY_PHYSICS,
            engine="ecology",
            advisory_action="Adjust famine vulnerability thresholds in agrarian biomes.",
        ))
        impacts.append(CascadeImpact(
            node_id="economy",
            field_name="grain_futures_volatility",
            old_value="Stable",
            new_value="High Price Volatility (+35% Seasonal Swing)",
            delta_description="Shorter agricultural harvest cycles force mercantile grain hoarding and spike commodity seasonal price fluctuations.",
            confidence=0.88,
            pillar=DomainPillar.SOCIETY_SYSTEMS,
            engine="economy",
            advisory_action="Update commodity basket volatility indices in `economy.yaml`.",
        ))
        impacts.append(CascadeImpact(
            node_id="tactical_sim",
            field_name="campaign_season_window",
            old_value="Late Spring to Autumn (6 months)",
            new_value="Strict Mid-Summer Window (2.5 months)",
            delta_description="Harsh winters and rapid autumn blizzards restrict military siege and campaign operations to narrow summer windows.",
            confidence=0.85,
            pillar=DomainPillar.SOCIETY_SYSTEMS,
            engine="tactical_sim",
            advisory_action="Add winter attrition modifiers to tactical battle scenarios.",
        ))
        impacts.append(CascadeImpact(
            node_id="scene_mechanics",
            field_name="ambient_scene_tension",
            old_value="Standard",
            new_value="Heightened Survival Urgency",
            delta_description="Prose sensory descriptions must emphasize looming seasonal shifts (gathering winter stores, race against frost).",
            confidence=0.80,
            pillar=DomainPillar.NARRATIVE_CHRONOLOGY,
            engine="scene_mechanics",
            advisory_action="Inject seasonal sensory cues into scene drafts in Zen Studio.",
        ))

    elif param_norm in ["stellar_mass", "star_mass", "luminosity", "semi_major_au"]:
        val_f = float(new_value)
        impacts.append(CascadeImpact(
            node_id="calendar",
            field_name="year_length_days",
            old_value="365.25 days",
            new_value=f"{round(365.25 * math.sqrt(val_f**3 if param_norm == 'semi_major_au' else 1.0), 1)} days",
            delta_description="Orbital mechanics directly alter the solar year length and calendar month divisions.",
            confidence=0.99,
            pillar=DomainPillar.COSMOLOGY_PHYSICS,
            engine="calendar",
            advisory_action="Sync calendar leap cycles with `arcanum calendar --sync`.",
        ))
        impacts.append(CascadeImpact(
            node_id="conlang",
            field_name="calendar_idioms",
            old_value="Standard Month Roots",
            new_value="Expanded Epagomenal Feast Days",
            delta_description="Longer solar years generate cultural intercalary festival periods that embed into common linguistic expressions.",
            confidence=0.75,
            pillar=DomainPillar.SOCIETY_SYSTEMS,
            engine="conlang",
            advisory_action="Generate calendar-derived idioms using `arcanum conlang`.",
        ))

    # 2. Magic System & Arcane Axiom Changes
    elif param_norm in ["magic_cost", "mana_source", "arcane_backlash", "magic_entropy"]:
        impacts.append(CascadeImpact(
            node_id="factions",
            field_name="mage_guild_monopoly",
            old_value="Decentralized Hedge Mages",
            new_value="Strict Cartel / State Regulation",
            delta_description="High magical backlash or costly mana requirements centralize arcane power into wealthy state-sponsored institutions.",
            confidence=0.91,
            pillar=DomainPillar.SOCIETY_SYSTEMS,
            engine="factions",
            advisory_action="Review faction power balance matrix in `arcanum faction`.",
        ))
        impacts.append(CascadeImpact(
            node_id="economy",
            field_name="labor_productivity_parity",
            old_value="Handicraft Guilds",
            new_value="Arcane Displacement of Manual Labor",
            delta_description="Magical energy alters economic purchasing power parity and displaces non-magical artisan wages.",
            confidence=0.86,
            pillar=DomainPillar.SOCIETY_SYSTEMS,
            engine="economy",
            advisory_action="Audit wage ratios across agrarian vs arcane sectors.",
        ))
        impacts.append(CascadeImpact(
            node_id="prophecy",
            field_name="magical_omen_validity",
            old_value="Symbolic Metaphor",
            new_value="Measurable Arcane Leyline Resonance",
            delta_description="Arcane entropy limits provide measurable criteria for validating authentic prophetic fulfillments.",
            confidence=0.82,
            pillar=DomainPillar.NARRATIVE_CHRONOLOGY,
            engine="prophecy",
            advisory_action="Verify prophecy clauses against magic laws with `arcanum prophecy`.",
        ))

    # 3. Macroeconomic / Currency Changes
    elif param_norm in ["currency_debasement", "inflation_rate", "trade_embargo"]:
        impacts.append(CascadeImpact(
            node_id="factions",
            field_name="revolt_risk_index",
            old_value="Low (0.15)",
            new_value="Critical (0.78) — Border Provinces Disaffected",
            delta_description="Debased specie erodes provincial troop pay, incentivizing mercenary defection and peasant revolt.",
            confidence=0.93,
            pillar=DomainPillar.SOCIETY_SYSTEMS,
            engine="factions",
            advisory_action="Check faction diplomatic paradoxes with `arcanum faction`.",
        ))
        impacts.append(CascadeImpact(
            node_id="tactical_sim",
            field_name="mercenary_morale_threshold",
            old_value="Reliable (Morale 80)",
            new_value="Brittle / Mutinous (Morale 40)",
            delta_description="Troops paid in debased currency suffer severe morale penalties and retreat early under tactical pressure.",
            confidence=0.89,
            pillar=DomainPillar.SOCIETY_SYSTEMS,
            engine="tactical_sim",
            advisory_action="Run simulated skirmish with reduced morale modifier.",
        ))
        impacts.append(CascadeImpact(
            node_id="voice",
            field_name="provincial_dialogue_slang",
            old_value="Courtly Formal",
            new_value="Subversive Gutter Slang & Smuggling Cant",
            delta_description="Economic desperation breeds underground barter dialects and anti-royalist cant.",
            confidence=0.78,
            pillar=DomainPillar.NARRATIVE_CHRONOLOGY,
            engine="voice",
            advisory_action="Audit dialogue authenticity in `arcanum audit voice`.",
        ))

    # Generic graph traversal fallback if no specific rule matched
    if not impacts:
        neighbors = adjacency.get(origin_node_id, [])
        for edge in neighbors:
            tgt = nodes.get(edge.target_id)
            if tgt and tgt.id not in visited:
                visited.add(tgt.id)
                impacts.append(CascadeImpact(
                    node_id=tgt.id,
                    field_name=f"downstream_influence_from_{param_norm}",
                    old_value="Default",
                    new_value=f"Adjusted via {edge.relation} (strength {edge.strength:.2f})",
                    delta_description=f"Direct relational influence from {origin_node_id} ({edge.description})",
                    confidence=edge.strength,
                    pillar=tgt.pillar,
                    engine=tgt.engine,
                    advisory_action=f"Inspect connected node `{tgt.label}` in {tgt.engine}.",
                ))

    return impacts
