#!/usr/bin/env python3
"""
Ars Arcanum Dynamic Intelligent Tip Engine & Metadata Database (scripts/lib/tips.py)
====================================================================================
Sovereign, offline, intelligent craft & technical tip retrieval system. Provides
curated, non-obvious, actionable craft wisdom, scientific principles, mathematical
insights, workflow synergies, and technical mastery hints across all 51 engines
and subfeatures in the Ars Arcanum operating system.

Non-intrusive display rails:
- Displays context-sensitive tips matching active engine, feature, subfeature,
  or creative activity (drafting, worldbuilding, revision, publishing, review).
- Prioritizes non-obvious masterclass depth over trivial or obvious advice.
- Intelligent ranking, tag matching, and non-repeating cycle history.
- Full user sovereignty: persistable enable/disable toggle via configuration, CLI,
  and GUI surfaces.
"""

from __future__ import annotations

import argparse
import difflib
import json
import logging
import random
import sys
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any

try:
    import lib._bootstrap  # noqa: F401
    from lib.config import load_config, save_config
except ImportError:
    import _bootstrap  # noqa: F401
    from config import load_config, save_config

logger = logging.getLogger("arcanum.tips")


class TipCategory(str, Enum):
    CRAFT = "craft"
    CORE = "core"
    UTILITY = "utility"


class TipPillar(str, Enum):
    COSMOLOGY_PHYSICS = "cosmology_physics"
    SOCIETY_SYSTEMS = "society_systems"
    NARRATIVE_CHRONOLOGY = "narrative_chronology"
    EDITORIAL_CRAFT = "editorial_craft"
    MANUSCRIPT_DRAFTING = "manuscript_drafting"
    SYSTEM_OPS = "system_ops"


class TipDepth(str, Enum):
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    MASTERCLASS = "masterclass"


@dataclass
class Tip:
    """Metadata-rich craft and technical tip specification."""

    id: str
    engine: str
    feature: str
    subfeature: str
    category: TipCategory
    pillar: TipPillar
    title: str
    content: str
    rationale: str
    example: str = ""
    tags: list[str] = field(default_factory=list)
    contexts: list[str] = field(default_factory=list)
    depth: TipDepth = TipDepth.ADVANCED
    weight: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        """Serializes tip to a plain dictionary."""
        d = asdict(self)
        d["category"] = self.category.value
        d["pillar"] = self.pillar.value
        d["depth"] = self.depth.value
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Tip:
        """Deserializes tip from dictionary."""
        return cls(
            id=data["id"],
            engine=data["engine"],
            feature=data.get("feature", data["engine"]),
            subfeature=data.get("subfeature", "general"),
            category=TipCategory(data.get("category", "craft")),
            pillar=TipPillar(data.get("pillar", "editorial_craft")),
            title=data["title"],
            content=data["content"],
            rationale=data.get("rationale", ""),
            example=data.get("example", ""),
            tags=list(data.get("tags", [])),
            contexts=list(data.get("contexts", ["cli", "studio"])),
            depth=TipDepth(data.get("depth", "advanced")),
            weight=float(data.get("weight", 1.0)),
        )


# =============================================================================
# EXHAUSTIVE CANONICAL TIP DATABASE (ALL 51 ENGINES + WORKFLOW CONTEXTS)
# =============================================================================

_RAW_TIPS: list[dict[str, Any]] = [
    # -------------------------------------------------------------------------
    # DOMAIN 1: ASTROPHYSICS & ORBITAL MECHANICS
    # -------------------------------------------------------------------------
    {
        "id": "tip_astro_brachistochrone_turnaround",
        "engine": "astrophysics",
        "feature": "brachistochrone",
        "subfeature": "turnaround_flip",
        "category": "craft",
        "pillar": "cosmology_physics",
        "title": "Brachistochrone Midpoint Turnover as Pacing Pivot",
        "content": "In 1g constant-acceleration transits, peak coordinate velocity occurs at the exact midpoint turnover, where the ship rotates 180 degrees. Use the brief 60-second zero-g transition between acceleration and deceleration as a high-tension psychological scene pivot.",
        "rationale": "Physics dictates acceleration gravity drops to zero during the RCS turnover maneuver, creating visceral somatic disorientation and sensory contrast in hard sci-fi scenes.",
        "example": "arcanum calc astro transit --distance 4.3ly --accel 1.0g",
        "tags": ["brachistochrone", "relativistic", "transit", "kinematics", "zero-g", "pacing"],
        "contexts": ["worldbuilding", "cli", "drafting", "studio"],
        "depth": "masterclass",
        "weight": 1.2,
    },
    {
        "id": "tip_astro_light_lag_dramatic_latency",
        "engine": "astrophysics",
        "feature": "time_dilation",
        "subfeature": "light_lag",
        "category": "craft",
        "pillar": "cosmology_physics",
        "title": "Light-Lag Latency as Asymmetric Dramatic Information",
        "content": "Electromagnetic signals take ~8.3 minutes per AU. When battles or political coups occur at Saturn (~9.5 AU), Earth receives the news 79 minutes later. Structure subplot tension around one faction acting on outdated intelligence.",
        "rationale": "Relativistic light-delay eliminates instantaneous omniscience, turning communication latency into an organic narrative engine.",
        "example": "arcanum calc astro comms --distance 9.5au",
        "tags": ["light-lag", "astrophysics", "information-asymmetry", "tension", "space-opera"],
        "contexts": ["worldbuilding", "plot", "cli"],
        "depth": "advanced",
        "weight": 1.1,
    },
    {
        "id": "tip_astro_roche_limit_shattered_moons",
        "engine": "astrophysics",
        "feature": "roche_limit",
        "subfeature": "tidal_rings",
        "category": "craft",
        "pillar": "cosmology_physics",
        "title": "Roche Limit Breaches: Ring Systems over Cataclysm Clichés",
        "content": "A moon orbiting inside its planet's fluid Roche limit (d_fluid ≈ 2.44 R (ρ_M/ρ_m)^(1/3)) is torn apart by tidal differential forces into a majestic ring system rather than colliding whole. Use ancient orbital decay to explain ring genesis.",
        "rationale": "Tidal gradient forces exceed self-gravitation, guaranteeing pulverized debris fields rather than single impact events.",
        "example": "arcanum calc astro roche --planet-radius 6371 --density-ratio 1.2",
        "tags": ["roche-limit", "tides", "rings", "astrophysics", "worldbuilding"],
        "contexts": ["worldbuilding", "cli", "studio"],
        "depth": "advanced",
        "weight": 1.0,
    },
    {
        "id": "tip_astro_red_dwarf_tidal_locking",
        "engine": "astrophysics",
        "feature": "keplerian",
        "subfeature": "habitable_zone",
        "category": "craft",
        "pillar": "cosmology_physics",
        "title": "Red Dwarf Habitable Zones and Permanent Twilight Terminators",
        "content": "Planets in the habitable zone of M-dwarf stars must orbit very close (0.05–0.2 AU), causing rapid tidal locking. Confine civilization to the narrow perpetual-twilight 'terminator ring' where supersonic global winds circulate between baked and frozen hemispheres.",
        "rationale": "Gravitational tidal torque scales as 1/r^6, forcing synchronous rotation within tens of millions of years in close orbits.",
        "example": "arcanum calc astro orbit --star-mass 0.25 --semi-major 0.12",
        "tags": ["tidal-locking", "red-dwarf", "habitable-zone", "climate", "worldbuilding"],
        "contexts": ["worldbuilding", "cli"],
        "depth": "masterclass",
        "weight": 1.2,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 2: PLANETARY CLIMATE & KÖPPEN BIOMES
    # -------------------------------------------------------------------------
    {
        "id": "tip_climate_orographic_foehn_winds",
        "engine": "climate",
        "feature": "rain_shadow",
        "subfeature": "foehn_effect",
        "category": "craft",
        "pillar": "cosmology_physics",
        "title": "Leeward Foehn Heating: Psychological Irritability in Rain Shadows",
        "content": "Air ascending a mountain cools at the moist lapse rate (5°C/km), precipitating its moisture. As it descends the leeward side dry, it warms at the dry lapse rate (9.8°C/km), creating scorching, desiccating Foehn/Chinook winds known historically to heighten human irritability and wildfire risks.",
        "rationale": "Thermodynamics dictates leeward air is dramatically hotter and drier than windward air at identical elevations.",
        "example": "arcanum calc climate --mountain-elevation 3500 --base-precip 1200",
        "tags": ["climate", "rain-shadow", "foehn-winds", "biomes", "sensory"],
        "contexts": ["worldbuilding", "drafting", "cli"],
        "depth": "masterclass",
        "weight": 1.1,
    },
    {
        "id": "tip_climate_rossby_cells_rotation",
        "engine": "climate",
        "feature": "circulation_cells",
        "subfeature": "coriolis",
        "category": "craft",
        "pillar": "cosmology_physics",
        "title": "Planetary Spin Rate Dictates Wind Bands and Maritime Trade Routes",
        "content": "Planets with slow rotations (>60 hours) form a single Hadley circulation cell per hemisphere (equator to pole winds). Rapid rotators (<16 hours) fragment into 5+ narrow wind bands. Base your Age-of-Sail maritime navigation and trade routes strictly on these Coriolis wind rails.",
        "rationale": "The Rossby number Ro = U / (2Ω L) controls whether Coriolis deflection partitions atmospheric circulation into multiple convective belts.",
        "example": "arcanum calc climate --rotation-hours 14.0",
        "tags": ["climate", "coriolis", "wind-bands", "trade-routes", "worldbuilding"],
        "contexts": ["worldbuilding", "cli"],
        "depth": "advanced",
        "weight": 1.0,
    },
    {
        "id": "tip_climate_milankovitch_glacial_cycles",
        "engine": "climate",
        "feature": "insolation",
        "subfeature": "milankovitch",
        "category": "craft",
        "pillar": "cosmology_physics",
        "title": "Orbital Eccentricity as Multi-Generational Migration Catalyst",
        "content": "High orbital eccentricity (e > 0.08) causes severe disparities between perihelion and aphelion seasons. Over centuries, axial precession cycles can turn lush savannahs into barren salt flats, naturally driving barbarian migrations and dynastic collapses.",
        "rationale": "Milankovitch orbital forcing modulates total annual insolation distribution, providing grand-scale causal foundations for historical lore.",
        "example": "arcanum calc climate --eccentricity 0.09 --axial-tilt 26.5",
        "tags": ["milankovitch", "climate", "migration", "history", "worldbuilding"],
        "contexts": ["worldbuilding", "cli"],
        "depth": "masterclass",
        "weight": 1.0,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 3: CUSTOM PLANETARY CALENDARS & MOONS
    # -------------------------------------------------------------------------
    {
        "id": "tip_calendar_synodic_syzygy_tides",
        "engine": "calendar",
        "feature": "lunar_phases",
        "subfeature": "syzygy",
        "category": "craft",
        "pillar": "cosmology_physics",
        "title": "Multi-Moon Syzygy: King Tides as Tactical Fortress Breaches",
        "content": "When two or more moons align in syzygy (conjunction or opposition), their gravitational vectors sum linearly, creating monstrous 'King Tides'. Time an amphibious fortress assault to this mathematically calculated celestial conjunction.",
        "rationale": "Tidal forces are additive during syzygy (F_total = F_1 + F_2), producing predictable extreme high and low tides.",
        "example": "arcanum calendar --syzygy-scan 20years",
        "tags": ["calendar", "moons", "syzygy", "tides", "siege", "tactics"],
        "contexts": ["worldbuilding", "tactics", "cli"],
        "depth": "advanced",
        "weight": 1.1,
    },
    {
        "id": "tip_calendar_metonic_intercalation",
        "engine": "calendar",
        "feature": "intercalary",
        "subfeature": "metonic",
        "category": "craft",
        "pillar": "society_systems",
        "title": "Lunisolar Drift and Priestly Power over Intercalary Leap Months",
        "content": "Lunisolar calendars require periodic intercalary leap months (e.g. 7 leap months every 19 years) to prevent harvest festivals from drifting into winter. Give the high priesthood sole legal authority to declare leap months to create bureaucratic corruption and tax manipulation.",
        "rationale": "Continued fraction expansion of the year-to-lunar-month ratio yields exact mathematical synchronization intervals.",
        "example": "arcanum calendar --validate-drift",
        "tags": ["calendar", "intercalation", "metonic", "priesthood", "politics"],
        "contexts": ["worldbuilding", "cli"],
        "depth": "intermediate",
        "weight": 1.0,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 4: ECOLOGY & FOOD WEBS
    # -------------------------------------------------------------------------
    {
        "id": "tip_ecology_lindeman_trophic_pyramid",
        "engine": "ecology",
        "feature": "trophic_pyramid",
        "subfeature": "energy_transfer",
        "category": "craft",
        "pillar": "cosmology_physics",
        "title": "Lindeman's 10% Rule: Why Apex Monster Populations Must Be Tiny",
        "content": "Only ~10% of metabolic energy transfers from one trophic level to the next. A 10,000-ton dragon population requires 100,000 tons of herbivores, supported by 1,000,000 tons of plant biomass. Make apex predators rare solitary hermits or territorial wanderers.",
        "rationale": "Thermodynamic trophic dissipation strictly caps top-carnivore biomass, preventing biologically impossible monster hordes.",
        "example": "arcanum ecology --trophic-audit",
        "tags": ["ecology", "trophic-pyramid", "monsters", "dragons", "worldbuilding"],
        "contexts": ["worldbuilding", "cli"],
        "depth": "advanced",
        "weight": 1.1,
    },
    {
        "id": "tip_ecology_kleiber_metabolic_scaling",
        "engine": "ecology",
        "feature": "metabolic_scaling",
        "subfeature": "kleiber",
        "category": "craft",
        "pillar": "cosmology_physics",
        "title": "Kleiber's Law: Giant Megafauna Have Slow Hearts and Long Lives",
        "content": "Basal metabolic rate scales with body mass as M^0.75. Giant creatures consume fewer calories per gram of tissue, breathe slower, and have much longer lifespans and gestation periods than smaller beasts. Reflect this in their ponderous speech and reproductive rarity.",
        "rationale": "Fractal cardiovascular transport networks impose a 3/4-power allometric scaling constraint across all biological organisms.",
        "example": "arcanum ecology --scale-mass 15000",
        "tags": ["kleiber", "allometry", "megafauna", "biology", "worldbuilding"],
        "contexts": ["worldbuilding", "cli"],
        "depth": "masterclass",
        "weight": 1.0,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 5: CARTOGRAPHY & GEODESICS
    # -------------------------------------------------------------------------
    {
        "id": "tip_cartography_river_confluence_invariant",
        "engine": "cartography",
        "feature": "rivers",
        "subfeature": "topography",
        "category": "craft",
        "pillar": "cosmology_physics",
        "title": "The River Confluence Invariant: Rivers Merge, Never Split",
        "content": "Under natural topography, tributaries merge downstream into larger rivers; they never bifurcate or split, with the sole exception of low-gradient sediment-choked delta estuaries near sea level. If an inland river splits in your lore, justify it with artificial canals or magical warding.",
        "rationale": "Water seeks the lowest local gravitational potential; erosion deepens a single primary channel over geological time.",
        "example": "arcanum map --validate-hydro",
        "tags": ["cartography", "rivers", "geology", "worldbuilding", "topography"],
        "contexts": ["worldbuilding", "cli"],
        "depth": "intermediate",
        "weight": 1.0,
    },
    {
        "id": "tip_cartography_great_circle_polar_routes",
        "engine": "cartography",
        "feature": "geodesics",
        "subfeature": "great_circle",
        "category": "craft",
        "pillar": "cosmology_physics",
        "title": "Great Circle Navigation: Why Shortest Routes Look Curved on Maps",
        "content": "On spherical worlds, the shortest path between two points is a Great Circle geodesic, not a straight line on a flat map. Ships and airships traveling between distant northern ports will arc through frigid arctic latitudes to save days of transit.",
        "rationale": "Spherical geometry minimizes arc length along great circles, exposing voyagers to unexpected polar storms.",
        "example": "arcanum map --geodesic-dist --from 45N,10W --to 48N,140E",
        "tags": ["cartography", "geodesics", "great-circle", "navigation", "travel"],
        "contexts": ["worldbuilding", "cli"],
        "depth": "advanced",
        "weight": 1.0,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 6: JOURNEY & LOGISTICS
    # -------------------------------------------------------------------------
    {
        "id": "tip_journey_caloric_decay_marching",
        "engine": "journey",
        "feature": "logistics",
        "subfeature": "caloric_debt",
        "category": "craft",
        "pillar": "society_systems",
        "title": "The 150 km Supply Wall: Why Armies Cannot March Indefinitely",
        "content": "Pack horses consume a portion of the grain they carry each day. Beyond ~150–200 km from a supply depot, a wagon train consumes 100% of its own cargo just to sustain the draft animals. Ground military campaigns along navigable rivers or captured granaries.",
        "rationale": "Logistical payload decreases exponentially with distance traveled without external forage or depot staging.",
        "example": "arcanum calc journey --distance 320km --terrain mountain --pack-animals 50",
        "tags": ["logistics", "supply-lines", "military", "journey", "realism"],
        "contexts": ["worldbuilding", "tactics", "cli"],
        "depth": "masterclass",
        "weight": 1.1,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 7: NARRATIVE STRUCTURE & PARADIGMS
    # -------------------------------------------------------------------------
    {
        "id": "tip_structure_kishotenketsu_twist",
        "engine": "structure",
        "feature": "paradigms",
        "subfeature": "kishotenketsu",
        "category": "craft",
        "pillar": "narrative_chronology",
        "title": "Kishōtenketsu (Ten): Structural Subversion Without Conflict",
        "content": "In Kishōtenketsu, the 3rd phase (Ten / The Twist) does not escalate binary protagonist-antagonist conflict. Instead, it introduces an apparently unrelated perspective, motif, or scene that recontextualizes the first two phases (Ki and Shō) into a profound philosophical synthesis (Ketsu).",
        "rationale": "Provides non-Western narrative rhythm for contemplative, mystery, or philosophical subplots.",
        "example": "arcanum structure --paradigm kishotenketsu",
        "tags": ["kishotenketsu", "structure", "paradigms", "non-western", "craft"],
        "contexts": ["drafting", "structure", "cli"],
        "depth": "masterclass",
        "weight": 1.2,
    },
    {
        "id": "tip_structure_8sequence_midpoint_mirror",
        "engine": "structure",
        "feature": "8sequence",
        "subfeature": "midpoint",
        "category": "craft",
        "pillar": "narrative_chronology",
        "title": "Sequence 4 Midpoint Mirror: From Reactive Survival to Proactive Attack",
        "content": "In the 8-Sequence framework, Sequence 4 terminates at the exact Midpoint (50% mark). This beat must transform the protagonist from reactive survival (fleeing or defending) to proactive attack (initiating a deliberate counter-strategy based on a devastating revelation).",
        "rationale": "Prevents the notorious Act II sag by fundamentally shifting the dramatic polarity of the story.",
        "example": "arcanum structure --paradigm 8-sequence",
        "tags": ["structure", "8-sequence", "midpoint", "pacing", "craft"],
        "contexts": ["drafting", "structure", "cli", "canvas"],
        "depth": "advanced",
        "weight": 1.1,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 8: SCENE MECHANICS & TENSION
    # -------------------------------------------------------------------------
    {
        "id": "tip_scene_mru_sensory_sequence",
        "engine": "scene_mechanics",
        "feature": "mru",
        "subfeature": "swain_units",
        "category": "craft",
        "pillar": "editorial_craft",
        "title": "Motivation-Reaction Unit Strict Order: Stimulus Before Speech",
        "content": "Always format dramatic reactions in strict physiological order: (1) External Sensory Stimulus -> (2) Involuntary Reflex (gasp/flinch) -> (3) Visceral Emotion -> (4) Conscious Thought -> (5) Rational Action/Speech. Placing speech before the reflex breaks reader immersion.",
        "rationale": "Neurobiology processes sensory input through the amygdala before the prefrontal cortex can formulate verbal syntax.",
        "example": "arcanum audit scenes",
        "tags": ["scene-mechanics", "mru", "swain", "immersion", "prose-craft"],
        "contexts": ["drafting", "revision", "cli", "zen"],
        "depth": "masterclass",
        "weight": 1.2,
    },
    {
        "id": "tip_scene_sequel_dilemma_structure",
        "engine": "scene_mechanics",
        "feature": "sequels",
        "subfeature": "dilemma",
        "category": "craft",
        "pillar": "editorial_craft",
        "title": "The Sequel Triple-Step: Emotion -> Dilemma -> Decision",
        "content": "Following a scene Disaster, never jump straight into the next action beat. Insert a 'Sequel' containing: (1) Emotional processing of defeat, (2) Intellectual analysis of a lose-lose dilemma, and (3) A desperate choice that initiates the next Scene Goal.",
        "rationale": "Gives the reader psychological digestion time and makes subsequent character actions feel motivated rather than arbitrary.",
        "example": "arcanum pace --tension",
        "tags": ["scene-mechanics", "sequel", "dilemma", "pacing", "craft"],
        "contexts": ["drafting", "structure", "cli"],
        "depth": "advanced",
        "weight": 1.0,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 9: PACING & DIALOGUE RHYTHM
    # -------------------------------------------------------------------------
    {
        "id": "tip_pacing_syllabic_churn_dopamine",
        "engine": "pacing",
        "feature": "rhythm",
        "subfeature": "sentence_variance",
        "category": "craft",
        "pillar": "editorial_craft",
        "title": "Sentence Length Standard Deviation: The Secret to Page-Turning Prose",
        "content": "High prose readability relies on sentence length variance (S_L > 8.0). Alternating a punchy 4-word sentence with a lyrical 28-word compound clause prevents cognitive hypnosis and keeps the reader's mental cadence engaged.",
        "rationale": "Monotonous sentence lengths (all 12–15 words) produce acoustic fatigue regardless of the scene's emotional stakes.",
        "example": "arcanum pace --pov",
        "tags": ["pacing", "sentence-length", "rhythm", "stylistics", "craft"],
        "contexts": ["drafting", "revision", "cli", "zen"],
        "depth": "advanced",
        "weight": 1.1,
    },
    {
        "id": "tip_pacing_action_tactile_anchors",
        "engine": "pacing",
        "feature": "action_pacing",
        "subfeature": "tactile_anchor",
        "category": "craft",
        "pillar": "editorial_craft",
        "title": "Action Scene Tactile Micro-Anchors Prevent Blur Fatigue",
        "content": "If a fast-paced combat or chase scene feels breathless and confusing, insert a 1-sentence tactile micro-anchor every 300 words: the smell of hot iron, grit between teeth, or a throbbing split knuckle. This restores physical spatial grounding.",
        "rationale": "Cognitive overload during fast-paced prose requires periodic somatic grounding to maintain spatial orientation.",
        "example": "arcanum senses",
        "tags": ["pacing", "action", "sensory", "grounding", "combat"],
        "contexts": ["drafting", "revision", "cli", "zen"],
        "depth": "masterclass",
        "weight": 1.0,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 10: PLOT MATRIX & SUBPLOTS
    # -------------------------------------------------------------------------
    {
        "id": "tip_plot_subplot_thematic_inversion",
        "engine": "plot_matrix",
        "feature": "subplots",
        "subfeature": "thematic_inversion",
        "category": "craft",
        "pillar": "narrative_chronology",
        "title": "Thematic Inversion: Secondary Plots Must Test the Core Argument",
        "content": "If your primary plot argues that 'loyalty overcomes tyranny', create a subplot where loyalty to a corrupt mentor produces disastrous betrayal. Subplots should challenge and stress-test the story's core thesis rather than merely echo it.",
        "rationale": "Dialectical narrative tension requires the story to present the strongest possible counter-argument to its own theme.",
        "example": "arcanum plot --matrix",
        "tags": ["plot-matrix", "subplots", "theme", "narrative", "craft"],
        "contexts": ["drafting", "canvas", "cli"],
        "depth": "masterclass",
        "weight": 1.1,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 11: BRANCHING NARRATIVE GRAPH
    # -------------------------------------------------------------------------
    {
        "id": "tip_branching_state_variable_fallbacks",
        "engine": "branching_graph",
        "feature": "state_variables",
        "subfeature": "dead_ends",
        "category": "craft",
        "pillar": "narrative_chronology",
        "title": "Gamebook State Variables: Eliminate Invisible Soft-Locks",
        "content": "When branching choices depend on inventory state (e.g. @state: has_key == true), always provide an alternative narrative failure pathway (e.g. pick lock with high risk, or kick down door making noise) rather than an unexplained dead-end barrier.",
        "rationale": "Soft-locks destroy player agency; meaningful failure branches enrich interactive world reactivity.",
        "example": "arcanum branch --validate",
        "tags": ["branching", "gamebook", "interactive-fiction", "dag", "state"],
        "contexts": ["drafting", "cli", "studio"],
        "depth": "advanced",
        "weight": 1.0,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 12: STORY CANVAS & CORKBOARD
    # -------------------------------------------------------------------------
    {
        "id": "tip_canvas_swimlane_pov_balance",
        "engine": "story_canvas",
        "feature": "swimlanes",
        "subfeature": "pov_isolation",
        "category": "craft",
        "pillar": "narrative_chronology",
        "title": "Swimlane POV Isolation: Spotting Narrative Abandonment",
        "content": "Use the Story Canvas swimlane filter to isolate a single POV character across the timeline. If a primary character vanishes for more than 4 consecutive chapters in Act II, readers lose emotional empathy with their personal stakes.",
        "rationale": "Visual spatial sorting instantly reveals pacing deserts that remain hidden in linear text files.",
        "example": "arcanum canvas --html",
        "tags": ["story-canvas", "corkboard", "pov", "swimlanes", "structure"],
        "contexts": ["canvas", "studio", "cli"],
        "depth": "intermediate",
        "weight": 1.0,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 13: CAUSALITY & TIMELINES
    # -------------------------------------------------------------------------
    {
        "id": "tip_causality_novikov_self_consistency",
        "engine": "causality",
        "feature": "time_travel",
        "subfeature": "novikov",
        "category": "craft",
        "pillar": "narrative_chronology",
        "title": "Novikov Self-Consistency: Attempts to Stop Fate Create Fate",
        "content": "In closed timelike loops, any action taken by a time traveler to prevent an event must mathematically turn out to be the exact historical trigger that caused that event to occur in the first place.",
        "rationale": "The Novikov self-consistency principle dictates that the probability of a paradox-inducing quantum fluctuation is zero.",
        "example": "arcanum causality --ctc-check",
        "tags": ["causality", "time-travel", "novikov", "paradox", "timeline"],
        "contexts": ["worldbuilding", "plot", "cli"],
        "depth": "masterclass",
        "weight": 1.2,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 14: TIMELINE SYNC
    # -------------------------------------------------------------------------
    {
        "id": "tip_timeline_dual_track_anachrony",
        "engine": "timeline_sync",
        "feature": "dual_track",
        "subfeature": "anachrony",
        "category": "craft",
        "pillar": "narrative_chronology",
        "title": "Dual-Track Timelines: Decouple In-Universe Time from Reading Order",
        "content": "Always separate chronological timeline dates (JAD/Julian Days) from narrative exposure order (Chapter 1, 2, 3). This allows non-linear storytelling (in medias res, flashbacks) while preventing accidental chronological paradoxes.",
        "rationale": "Enforces strict mathematical causality under the hood while granting complete artistic freedom over structural exposition.",
        "example": "arcanum timeline --sync",
        "tags": ["timeline-sync", "chronology", "anachrony", "flashbacks", "structure"],
        "contexts": ["worldbuilding", "drafting", "cli"],
        "depth": "advanced",
        "weight": 1.0,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 15: PROPHECY & ORACLES
    # -------------------------------------------------------------------------
    {
        "id": "tip_prophecy_syntactic_ambiguity",
        "engine": "prophecy",
        "feature": "prophecy_tracker",
        "subfeature": "ambiguity",
        "category": "craft",
        "pillar": "narrative_chronology",
        "title": "Oracular Syntactic Ambiguity: The Delphi Double-Meaning",
        "content": "Never write a prophecy that is literally transparent. Structure clauses with deliberate grammatical ambiguity (e.g. 'A great empire will fall' — referring to the inquirer's own kingdom) so fulfillment is shocking yet retroactively obvious.",
        "rationale": "Historical and mythological prophecies gain dramatic potency through subversion of dogmatic expectations.",
        "example": "arcanum prophecy --audit",
        "tags": ["prophecy", "oracles", "foreshadowing", "dramatic-irony", "lore"],
        "contexts": ["worldbuilding", "plot", "cli"],
        "depth": "advanced",
        "weight": 1.1,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 16: WRITING SPRINT & SESSION ANALYTICS
    # -------------------------------------------------------------------------
    {
        "id": "tip_sprint_peak_burst_management",
        "engine": "writing_sprint",
        "feature": "sprint_timer",
        "subfeature": "velocity",
        "category": "core",
        "pillar": "manuscript_drafting",
        "title": "Sprint Flow Velocity: Protect the 14-Minute Peak Burst",
        "content": "Typing velocity telemetry shows peak cognitive flow typically occurs between minutes 11 and 18 of a 25-minute sprint. Never stop to look up a name or fact during this window; type '[TODO: name]' and keep typing to preserve momentum.",
        "rationale": "Context switching during flow states incurs a 10–15 minute cognitive penalty to re-enter deep drafting rhythm.",
        "example": "arcanum sprint --target 500 --time 25",
        "tags": ["sprint", "flow-state", "productivity", "drafting", "wpm"],
        "contexts": ["drafting", "zen", "cli"],
        "depth": "intermediate",
        "weight": 1.1,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 17: DRAMATIS PERSONAE & CAST MATRIX
    # -------------------------------------------------------------------------
    {
        "id": "tip_cast_triadic_relationship_valence",
        "engine": "dramatis_personae",
        "feature": "cast_matrix",
        "subfeature": "valence",
        "category": "craft",
        "pillar": "society_systems",
        "title": "Triadic Relationship Valence: No Two Characters Share Neutral Ties",
        "content": "In a core ensemble, every character must have a distinct valence (affinity, rivalry, debt, ideological clash) with every other member. If characters B and C interact with A but have no relationship with each other, scenes with all three feel stiff.",
        "rationale": "Network theory shows triadic closure generates organic drama and conversational cross-talk.",
        "example": "arcanum cast --matrix",
        "tags": ["dramatis-personae", "cast", "relationships", "ensemble", "character"],
        "contexts": ["worldbuilding", "drafting", "cli"],
        "depth": "advanced",
        "weight": 1.0,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 18: CHARACTER VOICE PROFILER
    # -------------------------------------------------------------------------
    {
        "id": "tip_voice_syntactic_fingerprinting",
        "engine": "voice",
        "feature": "voice_profiler",
        "subfeature": "syntax_bleed",
        "category": "craft",
        "pillar": "editorial_craft",
        "title": "Voice Differentiation: Focus on Clause Structure, Not Quirks",
        "content": "Avoid relying on catchphrases or phonetic accents to differentiate character voices. Instead, vary syntactic clause complexity: high-status or analytical characters speak in hypotaxis (subordinate clauses), while direct action characters use parataxis (short coordinate clauses).",
        "rationale": "Syntactic rhythm creates authentic, sustainable character voice without annoying the reader with exaggerated phonetics.",
        "example": "arcanum audit voice",
        "tags": ["voice", "syntax", "dialogue", "stylistics", "character"],
        "contexts": ["drafting", "revision", "cli", "zen"],
        "depth": "masterclass",
        "weight": 1.2,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 19: CONLANG PHONOTACTICS & LEXICON
    # -------------------------------------------------------------------------
    {
        "id": "tip_conlang_archaic_liturgy_retention",
        "engine": "conlang",
        "feature": "sound_laws",
        "subfeature": "liturgy_retention",
        "category": "craft",
        "pillar": "society_systems",
        "title": "Grimm's Law Sound Shifts: Archaic Liturgies Resist Mutation",
        "content": "When simulating centuries of sound-law shifts (e.g. stop consonant softening p->f, t->th, k->h), preserve unmutated archaic phonemes in religious prayers, legal oaths, and ancient place names. This instantly signals deep historical antiquity.",
        "rationale": "Sacred texts and legal inscriptions are historically frozen by scribal orthodoxy, resisting colloquial phonotactic drift.",
        "example": "arcanum conlang mut High-Valdian --centuries 4",
        "tags": ["conlang", "linguistics", "grimms-law", "worldbuilding", "history"],
        "contexts": ["worldbuilding", "cli"],
        "depth": "masterclass",
        "weight": 1.1,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 20: DYNASTIC LINEAGE & GENEALOGY
    # -------------------------------------------------------------------------
    {
        "id": "tip_genealogy_consanguinity_inbreeding",
        "engine": "genealogy",
        "feature": "succession",
        "subfeature": "inbreeding_coefficient",
        "category": "craft",
        "pillar": "society_systems",
        "title": "Consanguinity Math: Realistic Justification for Hereditary Quirks",
        "content": "Before designing royal hereditary defects, calculate Wright's Inbreeding Coefficient (F). First-cousin marriages across 3+ consecutive generations raise F > 0.0625, mathematically guaranteeing the expression of rare recessive traits.",
        "rationale": "Pedigree collapse in closed aristocracies follows deterministic population genetics.",
        "example": "arcanum genealogy House-Aethel --inbreeding",
        "tags": ["genealogy", "succession", "genetics", "dynasty", "worldbuilding"],
        "contexts": ["worldbuilding", "cli"],
        "depth": "advanced",
        "weight": 1.0,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 21: GEOPOLITICAL FACTIONS & DIPLOMACY
    # -------------------------------------------------------------------------
    {
        "id": "tip_factions_triangular_hegemony_balance",
        "engine": "factions",
        "feature": "diplomacy_matrix",
        "subfeature": "triangular_balance",
        "category": "craft",
        "pillar": "society_systems",
        "title": "Three-Faction Hegemony: The Two Weaker Always Unite",
        "content": "In any three-power political system, if Faction A grows stronger than B and C individually, game theory dictates that B and C will form an uneasy defensive alliance, despite intense mutual hatred. Use this to force rival protagonists into joint operations.",
        "rationale": "Balance-of-power realism dictates survival supersedes historical animosity.",
        "example": "arcanum faction --html",
        "tags": ["factions", "diplomacy", "politics", "game-theory", "worldbuilding"],
        "contexts": ["worldbuilding", "cli"],
        "depth": "advanced",
        "weight": 1.0,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 22: MACROECONOMICS & CURRENCIES
    # -------------------------------------------------------------------------
    {
        "id": "tip_economy_greshams_law_coin_debasement",
        "engine": "economy",
        "feature": "currencies",
        "subfeature": "greshams_law",
        "category": "craft",
        "pillar": "society_systems",
        "title": "Gresham's Law: Debased Coins Drive Pure Gold into Secret Vaults",
        "content": "When a ruler debases silver coins by 20% to fund a war, citizens hoard the old pure silver coins or melt them into bullion. In markets, shopkeepers will refuse coins by count and demand balance scales to weigh actual metal content.",
        "rationale": "Bad money drives out good under legal tender price controls; merchants adapt with empirical weight verification.",
        "example": "arcanum economy --trade",
        "tags": ["economy", "currencies", "greshams-law", "worldbuilding", "realism"],
        "contexts": ["worldbuilding", "cli"],
        "depth": "masterclass",
        "weight": 1.1,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 23: TACTICAL BATTLE SIMULATOR
    # -------------------------------------------------------------------------
    {
        "id": "tip_tactical_lanchester_square_choke_points",
        "engine": "tactical_sim",
        "feature": "battle_sim",
        "subfeature": "lanchester",
        "category": "craft",
        "pillar": "society_systems",
        "title": "Lanchester's Square Law: Why Small Forces Must Create Choke Points",
        "content": "For ranged combat where units can focus fire, force power scales as N^2. An army of 1,000 archers defeats 500 archers with only ~134 casualties. Small forces can only win by forcing the battle into narrow defiles where Lanchester's Linear Law applies.",
        "rationale": "Lanchester differential combat equations demonstrate why open-field engagements are suicidal for outnumbered forces.",
        "example": "arcanum sim battle --force-a 1000 --force-b 500 --terrain gorge",
        "tags": ["tactics", "lanchester", "battle", "military", "strategy"],
        "contexts": ["worldbuilding", "tactics", "cli"],
        "depth": "masterclass",
        "weight": 1.2,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 24: HARD MAGIC SYSTEM CONSTRAINTS
    # -------------------------------------------------------------------------
    {
        "id": "tip_magic_sanderson_second_law_costs",
        "engine": "magic_system",
        "feature": "arcane_constraints",
        "subfeature": "metabolic_cost",
        "category": "craft",
        "pillar": "cosmology_physics",
        "title": "Sanderson's Second Law: Limitations Drive Drama, Not Powers",
        "content": "An author's ability to solve problems with magic is directly proportional to how well the reader understands the costs and limitations. Tie spellcasting to irreversible metabolic strain (e.g. hypothermia or acute caloric depletion) to give non-magical characters tactical leverage.",
        "rationale": "Unlimited magic destroys narrative tension; strict thermodynamic or physical constraints create high-stakes problem-solving.",
        "example": "arcanum magic-check",
        "tags": ["magic", "sanderson", "constraints", "worldbuilding", "tension"],
        "contexts": ["worldbuilding", "drafting", "cli"],
        "depth": "masterclass",
        "weight": 1.2,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 25: STYLISTICS & READABILITY AUDITS
    # -------------------------------------------------------------------------
    {
        "id": "tip_stylistics_said_bookisms_vs_action_beats",
        "engine": "stylistics",
        "feature": "dialogue_tags",
        "subfeature": "action_beats",
        "category": "craft",
        "pillar": "editorial_craft",
        "title": "Replace 'Said-Bookisms' with Physical Action Beats",
        "content": "Avoid exotic dialogue tags like 'he sneered', 'she hissed', or 'he expounded'. The word 'said' is invisible to the brain. Even better: replace the tag with an active character gesture that conveys subtext and mood.",
        "rationale": "Intrusive dialogue tags draw attention to the author rather than the dialogue; action beats anchor spatial blocking.",
        "example": "arcanum audit dialogue",
        "tags": ["stylistics", "dialogue", "said-bookisms", "action-beats", "prose-craft"],
        "contexts": ["drafting", "revision", "cli", "zen"],
        "depth": "intermediate",
        "weight": 1.0,
    },
    {
        "id": "tip_stylistics_echo_radar_proximity",
        "engine": "stylistics",
        "feature": "echoes",
        "subfeature": "word_repetition",
        "category": "craft",
        "pillar": "editorial_craft",
        "title": "Word Echo Radar: Catching Unconscious Repetitions within 150 Words",
        "content": "The human brain unconsciously reuses evocative words within 100–150 words (e.g. using 'labyrinthine' twice on the same page). Run the Stylistics Echo scan to detect duplicate content words before sending to beta readers.",
        "rationale": "Lexical echo proximity dulls the sensory impact of distinctive descriptive vocabulary.",
        "example": "arcanum audit echoes",
        "tags": ["stylistics", "echoes", "repetition", "polishing", "revision"],
        "contexts": ["revision", "cli", "zen"],
        "depth": "intermediate",
        "weight": 1.0,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 26: SENSORY IMMERSION HEATMAP
    # -------------------------------------------------------------------------
    {
        "id": "tip_senses_white_room_multi_sensory",
        "engine": "senses",
        "feature": "sensory_radar",
        "subfeature": "white_room",
        "category": "craft",
        "pillar": "editorial_craft",
        "title": "Defeating White Room Syndrome: The 2-Non-Visual Sense Rule",
        "content": "When characters talk in an empty-feeling space ('White Room Syndrome'), it is usually because >80% of sensory details are purely visual. Ensure every major scene opening includes at least two non-visual senses: olfactory, thermal, tactile, or acoustic.",
        "rationale": "Olfactory and acoustic inputs process through deep limbic memory structures, triggering involuntary somatic immersion in readers.",
        "example": "arcanum audit senses",
        "tags": ["senses", "white-room", "immersion", "sensory", "prose-craft"],
        "contexts": ["drafting", "revision", "cli", "zen"],
        "depth": "masterclass",
        "weight": 1.1,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 27: SEMANTIC CONTINUITY & TRAIT LINTER
    # -------------------------------------------------------------------------
    {
        "id": "tip_continuity_semantic_trait_drift",
        "engine": "continuity",
        "feature": "trait_linter",
        "subfeature": "attribute_drift",
        "category": "craft",
        "pillar": "editorial_craft",
        "title": "Automated Trait Drift Detection Across Long Drafts",
        "content": "In 100,000+ word manuscripts, minor character traits (eye color, wounded arm, ring hand) frequently invert between Chapter 4 and Chapter 28. Run the semantic continuity linter to cross-reference text mentions against the World Bible entity dossiers.",
        "rationale": "Eliminates embarrassing developmental inconsistencies before editorial submission.",
        "example": "arcanum continuity -w World -m Manuscript",
        "tags": ["continuity", "traits", "linter", "characters", "quality"],
        "contexts": ["revision", "review", "cli"],
        "depth": "intermediate",
        "weight": 1.0,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 28: SERIES CONTINUITY LEDGER
    # -------------------------------------------------------------------------
    {
        "id": "tip_series_canon_ledger_world_state",
        "engine": "series_continuity",
        "feature": "series_ledger",
        "subfeature": "world_mutations",
        "category": "craft",
        "pillar": "society_systems",
        "title": "Series Canon Ledger: Permanent World-State Mutations",
        "content": "When drafting Book 3 of a series, track permanent world mutations (e.g. destroyed fortress gates, assassinated guildmasters, bankrupt banks) in the Series Continuity Ledger so background lore never accidentally reverts to the Book 1 baseline.",
        "rationale": "Ensures multi-volume universe progression remains cumulative and cohesive.",
        "example": "arcanum series --html",
        "tags": ["series-continuity", "canon", "universe", "multi-book", "worldbuilding"],
        "contexts": ["worldbuilding", "review", "cli"],
        "depth": "advanced",
        "weight": 1.0,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 29: TYPOGRAPHY CLEANER
    # -------------------------------------------------------------------------
    {
        "id": "tip_typography_shunn_em_dash_standards",
        "engine": "typography_cleaner",
        "feature": "clean_typography",
        "subfeature": "shunn_rules",
        "category": "utility",
        "pillar": "editorial_craft",
        "title": "William Shunn Em-Dash Standard: No Surrounding Spaces",
        "content": "In traditional publishing and standard manuscript format, em-dashes must connect words directly without surrounding spaces (word—word). Spaced hyphens (word - word) or spaced em-dashes (word — word) trigger automated pre-screening rejections at traditional presses.",
        "rationale": "Enforces strict typesetting compliance with Chicago Manual of Style and William Shunn industry norms.",
        "example": "arcanum polish typography Manuscript/",
        "tags": ["typography", "shunn", "em-dash", "typesetting", "publishing"],
        "contexts": ["export", "publishing", "cli"],
        "depth": "intermediate",
        "weight": 1.0,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 30: MANUSCRIPT DIFF & VISUAL REDLINE
    # -------------------------------------------------------------------------
    {
        "id": "tip_diff_semantic_churn_reorganization",
        "engine": "manuscript_diff",
        "feature": "redline_diff",
        "subfeature": "structural_shift",
        "category": "core",
        "pillar": "editorial_craft",
        "title": "Visual Redline Diff: Distinguishing Polish from Rewrites",
        "content": "Use the visual redline comparator to verify revision depth. A chapter showing small dispersed yellow patches is undergoing surface line polish; a chapter with solid green/red blocks indicates structural developmental surgery.",
        "rationale": "Word-level LCS diffing provides clear visual feedback on whether a revision addressed structural flaws or merely swapped synonyms.",
        "example": "arcanum compare Manuscript Draft-02 Draft-01",
        "tags": ["diff", "redline", "revision", "drafting", "editorial"],
        "contexts": ["revision", "review", "cli"],
        "depth": "intermediate",
        "weight": 1.0,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 31: REVISION HEATMAP & EDIT DENSITY
    # -------------------------------------------------------------------------
    {
        "id": "tip_heatmap_churn_danger_zones",
        "engine": "revision_heatmap",
        "feature": "revision_density",
        "subfeature": "hotspots",
        "category": "craft",
        "pillar": "editorial_craft",
        "title": "Revision Density Hotspots: The Danger of Over-Editing Middle Chapters",
        "content": "Chapters with >65% edit churn across multiple revisions indicate structural confusion rather than prose issues. Stop tweaking sentences in hot chapters—open the Story Canvas and verify the scene's core Goal, Conflict, and Disaster.",
        "rationale": "Excessive prose churn is usually a symptom of a weak underlying dramatic spine.",
        "example": "arcanum revision-heatmap Manuscript",
        "tags": ["revision-heatmap", "churn", "density", "editing", "pacing"],
        "contexts": ["revision", "review", "cli"],
        "depth": "advanced",
        "weight": 1.1,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 32: SOVEREIGN STUDIO HUB
    # -------------------------------------------------------------------------
    {
        "id": "tip_hub_dual_monitor_telemetry",
        "engine": "studio_hub",
        "feature": "web_cockpit",
        "subfeature": "multi_monitor",
        "category": "core",
        "pillar": "system_ops",
        "title": "Studio Hub: Multi-Monitor Worldbuilding Cockpit",
        "content": "Launch the Studio Hub (arcanum hub --port 8080) on your secondary monitor while drafting in Zen Studio or Obsidian on your primary display. The hub provides live wordcount telemetry, entity dossiers, and cross-domain resonance without window switching.",
        "rationale": "100% offline local HTTP server architecture keeps your unpublished intellectual property completely private.",
        "example": "arcanum hub",
        "tags": ["studio-hub", "dashboard", "telemetry", "offline", "workflow"],
        "contexts": ["studio", "cli"],
        "depth": "intermediate",
        "weight": 1.0,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 33: ZEN DRAFTING STUDIO
    # -------------------------------------------------------------------------
    {
        "id": "tip_zen_typewriter_scroll_ergonomics",
        "engine": "zen_studio",
        "feature": "zen_editor",
        "subfeature": "typewriter_mode",
        "category": "core",
        "pillar": "manuscript_drafting",
        "title": "Typewriter Mode: Ergonomic Focus for Prolonged Drafting",
        "content": "In Zen Studio, enable Typewriter Mode to lock your active line to the vertical center of your monitor. This prevents neck strain from looking down at the bottom of the screen and keeps your mental focus anchored directly on the cursor.",
        "rationale": "Ergonomic gaze alignment reduces physical eye and neck fatigue during 2+ hour writing sessions.",
        "example": "arcanum studio Manuscript/",
        "tags": ["zen-studio", "typewriter", "drafting", "focus", "ergonomics"],
        "contexts": ["zen", "drafting", "cli"],
        "depth": "intermediate",
        "weight": 1.0,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 34: AMBIENT FOCUS SOUNDSCAPES
    # -------------------------------------------------------------------------
    {
        "id": "tip_ambient_binaural_frequency_tuning",
        "engine": "ambient",
        "feature": "binaural_generator",
        "subfeature": "gamma_vs_alpha",
        "category": "utility",
        "pillar": "manuscript_drafting",
        "title": "Binaural Focus: 40 Hz Gamma for Complex Plotting, 10 Hz Alpha for Drafting",
        "content": "Use the built-in offline audio synthesizer (arcanum ambient) to generate 40 Hz Gamma waves for complex timeline and causal logic, or 10 Hz Alpha waves for relaxed, fluid creative drafting flow.",
        "rationale": "Pure algorithmic audio generation executes locally with zero external sample downloads or network dependencies.",
        "example": "arcanum ambient --profile gamma-40hz",
        "tags": ["ambient", "binaural", "focus", "soundscapes", "audio"],
        "contexts": ["drafting", "zen", "cli"],
        "depth": "intermediate",
        "weight": 1.0,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 35: PORTFOLIO & DRAFTING VELOCITY
    # -------------------------------------------------------------------------
    {
        "id": "tip_portfolio_velocity_projection",
        "engine": "portfolio",
        "feature": "drafting_velocity",
        "subfeature": "projection",
        "category": "utility",
        "pillar": "system_ops",
        "title": "Drafting Velocity: Rolling 30-Day Completion Projections",
        "content": "The portfolio engine tracks your rolling 30-day words-per-day average, calculating mathematically grounded completion dates for all active manuscripts rather than relying on wishful thinking.",
        "rationale": "Empirical pacing analytics help authors commit to realistic publishing deadlines without burnout.",
        "example": "arcanum portfolio --html",
        "tags": ["portfolio", "velocity", "analytics", "milestones", "projects"],
        "contexts": ["review", "cli"],
        "depth": "intermediate",
        "weight": 1.0,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 36: LOCAL SEMANTIC RAG RETRIEVER
    # -------------------------------------------------------------------------
    {
        "id": "tip_rag_hybrid_entity_boost",
        "engine": "local_rag",
        "feature": "semantic_search",
        "subfeature": "hybrid_scoring",
        "category": "core",
        "pillar": "system_ops",
        "title": "Zero-Pip Local RAG: Hybrid TF-IDF + FTS5 Entity Boosting",
        "content": "When querying your world bible using 'arcanum rag <query>', the engine combines statistical BM25/TF-IDF term weighting with SQLite FTS5 exact entity token matches. Enclose proper nouns in quotes to prioritize specific character dossiers.",
        "rationale": "Hybrid semantic retrieval delivers sub-second lore context without needing bloated 10GB neural model downloads.",
        "example": "arcanum rag \"Archon Valerius\" bloodline",
        "tags": ["local-rag", "semantic-search", "sqlite-fts5", "tf-idf", "lore-retrieval"],
        "contexts": ["drafting", "worldbuilding", "cli"],
        "depth": "advanced",
        "weight": 1.1,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 37: CORPUS EXPORT & RAG EXPORTER
    # -------------------------------------------------------------------------
    {
        "id": "tip_corpus_jsonl_fine_tuning_export",
        "engine": "corpus_export",
        "feature": "jsonl_export",
        "subfeature": "structured_datasets",
        "category": "utility",
        "pillar": "system_ops",
        "title": "Corpus Export: Clean Structured Datasets for Offline LLMs",
        "content": "Export your entire universe into structured JSONL or SQLite (arcanum corpus --format jsonl) with clean frontmatter extraction and section chunking, ideal for training or prompting local offline language models.",
        "rationale": "Standardized schema export protects your creative data from proprietary lock-in.",
        "example": "arcanum corpus Universe/ --format jsonl -o dataset.jsonl",
        "tags": ["corpus-export", "jsonl", "rag", "sqlite", "interoperability"],
        "contexts": ["export", "cli"],
        "depth": "advanced",
        "weight": 1.0,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 38: VAULT IMPORTER
    # -------------------------------------------------------------------------
    {
        "id": "tip_importer_scrivener_frontmatter_preservation",
        "engine": "importer",
        "feature": "batch_import",
        "subfeature": "scrivener",
        "category": "utility",
        "pillar": "system_ops",
        "title": "Scrivener Import: Automatic Frontmatter and Tag Preservation",
        "content": "Importing a Scrivener project (.scriv) automatically translates Scrivener synopses, POV character assignments, and binder folder hierarchies into valid Ars Arcanum YAML frontmatter headers.",
        "rationale": "Seamlessly migrates years of legacy writing into a sovereign, plain-text Markdown architecture.",
        "example": "arcanum import ~/Novel.scriv --target Manuscripts/MyNovel",
        "tags": ["importer", "scrivener", "migration", "markdown", "vault"],
        "contexts": ["cli"],
        "depth": "intermediate",
        "weight": 1.0,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 39: DOCX BIDIRECTIONAL SYNC
    # -------------------------------------------------------------------------
    {
        "id": "tip_docx_preset_shunn_submission",
        "engine": "docx_sync",
        "feature": "shunn_presets",
        "subfeature": "word_sync",
        "category": "core",
        "pillar": "editorial_craft",
        "title": "DOCX Presets: One-Click William Shunn Submission Formatting",
        "content": "Switch formatting presets instantly using 'arcanum docx-preset standard-submission'. The engine automatically sets Times New Roman 12pt, double spacing, 1-inch margins, 0.5-inch indents, and '#' scene break symbols.",
        "rationale": "Guarantees 100% compliance with traditional agent and publisher submission standards without manual Microsoft Word fiddling.",
        "example": "arcanum docx sync Manuscript/ --open",
        "tags": ["docx-sync", "word", "shunn", "presets", "publishing"],
        "contexts": ["export", "publishing", "cli"],
        "depth": "intermediate",
        "weight": 1.1,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 40: WORLD BIBLE DOCTOR
    # -------------------------------------------------------------------------
    {
        "id": "tip_world_doctor_orphaned_entities",
        "engine": "world_doctor",
        "feature": "integrity_scan",
        "subfeature": "orphaned_lore",
        "category": "utility",
        "pillar": "society_systems",
        "title": "World Doctor: Cleaning Orphaned Entities and Dead Wikilinks",
        "content": "Run 'arcanum world-doctor <World>' to discover orphaned lore files that have zero inbound references from characters, factions, or manuscript chapters, as well as dead Obsidian [[wikilinks]].",
        "rationale": "Maintains a pristine, tightly interconnected lore graph without sprawling disconnected clutter.",
        "example": "arcanum world-doctor Worlds/Aethelgard",
        "tags": ["world-doctor", "integrity", "wikilinks", "diagnostics", "lore"],
        "contexts": ["worldbuilding", "review", "cli"],
        "depth": "intermediate",
        "weight": 1.0,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 41: SYSTEM DIAGNOSTICS
    # -------------------------------------------------------------------------
    {
        "id": "tip_diagnostics_health_suite",
        "engine": "diagnostics",
        "feature": "system_diagnostics",
        "subfeature": "toolchain_check",
        "category": "utility",
        "pillar": "system_ops",
        "title": "System Diagnostics: 100% Offline Toolchain Verification",
        "content": "Run 'arcanum doctor' to audit your environment: verifies Python standard library modules, POSIX atomic file locking, Git milestone availability, and system font rendering in under 1 second.",
        "rationale": "Guarantees fail-safe operational readiness across Windows, Linux, and macOS environments.",
        "example": "arcanum doctor",
        "tags": ["diagnostics", "doctor", "health", "system", "toolchain"],
        "contexts": ["cli"],
        "depth": "intermediate",
        "weight": 1.0,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 42: CONFIG & PREFERENCES
    # -------------------------------------------------------------------------
    {
        "id": "tip_config_secure_0600_permissions",
        "engine": "config",
        "feature": "user_preferences",
        "subfeature": "security_permissions",
        "category": "utility",
        "pillar": "system_ops",
        "title": "Secure Permissions: 0600 File Privacy in ~/.config/ars-arcanum/",
        "content": "All Ars Arcanum configuration files are saved with restrictive 0600 permissions (read/write only by the author). Use 'arcanum config tips disable' if you ever want a zero-advice, minimalist distraction-free environment.",
        "rationale": "Protects author metadata and backup destinations from unauthorized multi-user access.",
        "example": "arcanum config tips disable",
        "tags": ["config", "security", "permissions", "preferences", "privacy"],
        "contexts": ["cli"],
        "depth": "intermediate",
        "weight": 1.0,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 43: PERFORMANCE CACHE
    # -------------------------------------------------------------------------
    {
        "id": "tip_cache_mtime_keyed_instant_wordcounts",
        "engine": "cache",
        "feature": "mtime_cache",
        "subfeature": "sub_millisecond",
        "category": "utility",
        "pillar": "system_ops",
        "title": "Performance Cache: Sub-Millisecond Analytics via MTime Hashing",
        "content": "The Ars Arcanum cache engine keys chapter wordcounts, frontmatter, and AST tokens to file modification times (mtime). Only modified chapters are re-parsed, enabling instant CLI telemetry even on 500,000-word epics.",
        "rationale": "Eliminates disk I/O bottlenecks during frequent command-line queries and drafting autosaves.",
        "example": "arcanum cache scan",
        "tags": ["cache", "performance", "mtime", "speed", "analytics"],
        "contexts": ["cli"],
        "depth": "advanced",
        "weight": 1.0,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 44: ATOMIC FILE SYSTEM UTILITIES
    # -------------------------------------------------------------------------
    {
        "id": "tip_fs_atomic_write_crash_protection",
        "engine": "fs_utils",
        "feature": "atomic_io",
        "subfeature": "crash_defense",
        "category": "core",
        "pillar": "system_ops",
        "title": "Atomic Write Invariant: Zero Manuscript Corruption on Power Loss",
        "content": "Every file write in Ars Arcanum writes to a temporary sibling file, flushes buffers, calls os.fsync, and replaces the target atomically via os.replace. Even a sudden power outage or system crash will never leave a corrupted half-written chapter.",
        "rationale": "Guarantees ACID-like durability invariants for all unpublished author drafts.",
        "example": "from lib._bootstrap import atomic_write; atomic_write(path, text)",
        "tags": ["atomic-write", "file-safety", "crash-protection", "fsync", "data-integrity"],
        "contexts": ["system", "cli"],
        "depth": "masterclass",
        "weight": 1.2,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 45: VAULT MIGRATION ENGINE
    # -------------------------------------------------------------------------
    {
        "id": "tip_migrate_dry_run_safety_snapshot",
        "engine": "migrate",
        "feature": "schema_migration",
        "subfeature": "dry_run",
        "category": "utility",
        "pillar": "system_ops",
        "title": "Vault Migration: Mandatory Safety Snapshots Before Schema Upgrades",
        "content": "When upgrading vault schemas across major Ars Arcanum versions, always test with 'arcanum migrate --dry-run' first. Actual migrations automatically create a verified .tar.gz snapshot before touching a single file.",
        "rationale": "Ensures complete reversibility and peace of mind during repository architecture updates.",
        "example": "arcanum migrate --dry-run",
        "tags": ["migrate", "schema", "snapshot", "backup", "safety"],
        "contexts": ["cli"],
        "depth": "intermediate",
        "weight": 1.0,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 46: PREFLIGHT TYPESETTING VALIDATOR
    # -------------------------------------------------------------------------
    {
        "id": "tip_preflight_orphan_widow_suppression",
        "engine": "preflight",
        "feature": "typesetting_compliance",
        "subfeature": "orphan_widow",
        "category": "utility",
        "pillar": "editorial_craft",
        "title": "Preflight Validator: Catching Orphan/Widow Lines and Gutter Clashes",
        "content": "Run 'arcanum preflight Manuscript/' before generating final print PDFs. The preflight engine checks for orphan/widow headings, unclosed quotation pairs, trailing scene breaks, and inside gutter margin allowances.",
        "rationale": "Prevents costly re-print fees by catching structural layout errors before submission to IngramSpark or KDP.",
        "example": "arcanum preflight Manuscript/",
        "tags": ["preflight", "typesetting", "pdf", "print", "publishing"],
        "contexts": ["export", "publishing", "cli"],
        "depth": "advanced",
        "weight": 1.1,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 47: FRONTMATTER & BACKMATTER BUILDER
    # -------------------------------------------------------------------------
    {
        "id": "tip_frontmatter_in_universe_epigraphs",
        "engine": "frontmatter_builder",
        "feature": "modular_matter",
        "subfeature": "epigraphs",
        "category": "craft",
        "pillar": "editorial_craft",
        "title": "Dynamic Epigraphs: In-Universe Historical Excerpts",
        "content": "Use the Frontmatter Builder to automatically generate copyright pages, dedication layouts, and chapter epigraphs pulled directly from your in-universe World Bible religious scriptures and academic histories.",
        "rationale": "Elevates book production quality and enriches lore immersion from the very first page.",
        "example": "arcanum matter build Manuscript/",
        "tags": ["frontmatter", "backmatter", "epigraphs", "publishing", "formatting"],
        "contexts": ["publishing", "export", "cli"],
        "depth": "intermediate",
        "weight": 1.0,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 48: CONCORDANCE & GLOSSARY GENERATOR
    # -------------------------------------------------------------------------
    {
        "id": "tip_concordance_back_matter_glossary",
        "engine": "concordance",
        "feature": "glossary_generator",
        "subfeature": "term_occurrences",
        "category": "craft",
        "pillar": "editorial_craft",
        "title": "Concordance: Automated Pronunciation & Term Glossary",
        "content": "Run 'arcanum concordance <Manuscript>' to scan all in-text mentions of fantasy terms and characters, generating an alphabetical Dramatis Personae and Glossary appendix with exact chapter citations.",
        "rationale": "Saves hours of manual back-matter compiling while ensuring 100% spelling parity.",
        "example": "arcanum concordance Manuscript/ -b",
        "tags": ["concordance", "glossary", "backmatter", "dramatis-personae", "publishing"],
        "contexts": ["publishing", "export", "cli"],
        "depth": "intermediate",
        "weight": 1.0,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 49: WORLD WIKI CODEX EXPORT
    # -------------------------------------------------------------------------
    {
        "id": "tip_codex_selective_spoiler_filtering",
        "engine": "codex_export",
        "feature": "wiki_export",
        "subfeature": "spoiler_tags",
        "category": "utility",
        "pillar": "society_systems",
        "title": "Codex Export: Generating Offline Reader Wikis Without Spoilers",
        "content": "Compile your Obsidian world vault into a standalone offline HTML wiki (arcanum codex <World>). Add '@spoiler: true' in frontmatter to redact secret plot revelations when sharing the wiki with beta readers.",
        "rationale": "Generates beautiful, self-contained offline reference wikis for fans and editors without leaking climax twists.",
        "example": "arcanum codex Worlds/Aethelgard --html",
        "tags": ["codex", "wiki", "export", "spoilers", "offline"],
        "contexts": ["worldbuilding", "export", "cli"],
        "depth": "advanced",
        "weight": 1.1,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 50: SERIES OMNIBUS COMPILER
    # -------------------------------------------------------------------------
    {
        "id": "tip_omnibus_unified_chronological_sequence",
        "engine": "omnibus",
        "feature": "omnibus_compiler",
        "subfeature": "chronological_merge",
        "category": "utility",
        "pillar": "narrative_chronology",
        "title": "Series Omnibus: Compiling Multi-Book Chronological Cuts",
        "content": "The Omnibus Compiler can merge multiple separate volumes (Book 1, Book 2, Book 3) into a single master publication or re-order scenes across books into a seamless chronological master cut with shared appendices.",
        "rationale": "Automates multi-volume compilation with unified page numbering and cross-volume dramatis personae.",
        "example": "arcanum omnibus Universes/Cosmos --html",
        "tags": ["omnibus", "series", "compilation", "publishing", "multi-volume"],
        "contexts": ["publishing", "export", "cli"],
        "depth": "advanced",
        "weight": 1.1,
    },

    # -------------------------------------------------------------------------
    # DOMAIN 51: UNIVERSAL RESONANCE MESH & CROSS-DOMAIN SYNTHESIZER
    # -------------------------------------------------------------------------
    {
        "id": "tip_resonance_cross_domain_creative_sparks",
        "engine": "resonance",
        "feature": "creative_sparks",
        "subfeature": "domain_bridges",
        "category": "craft",
        "pillar": "cosmology_physics",
        "title": "Resonance Mesh: Finding Analogies Between Disparate Craft Domains",
        "content": "Run 'arcanum resonance spark' to generate structural analogies connecting unrelated fields (e.g. Plate Tectonics + Conlang Dialect Shifts, or Immunology + Espionage Networks). Use these bridges to design world systems that feel organically interconnected.",
        "rationale": "Cross-domain isomorphism transforms standard speculative tropes into deeply cohesive world architectures.",
        "example": "arcanum resonance spark",
        "tags": ["resonance", "sparks", "isomorphism", "cross-domain", "creativity"],
        "contexts": ["worldbuilding", "drafting", "cli", "studio"],
        "depth": "masterclass",
        "weight": 1.3,
    },
    {
        "id": "tip_resonance_causal_cascade_simulation",
        "engine": "resonance",
        "feature": "causal_cascade",
        "subfeature": "parameter_ripple",
        "category": "craft",
        "pillar": "cosmology_physics",
        "title": "Causal Cascades: Simulating How 1 Physical Change Alters Society",
        "content": "Use 'arcanum resonance cascade' to trace the ripple effects of a single environmental tweak (e.g. doubling planetary axial tilt). The mesh calculates how extreme seasons cascade into agricultural nomadism, solar worship religions, and bimetallic grain futures.",
        "rationale": "Forces worldbuilding elements into strict causal dependency chains rather than isolated aesthetic choices.",
        "example": "arcanum resonance cascade --node climate --param axial_tilt --val 38.5",
        "tags": ["resonance", "cascade", "causality", "worldbuilding", "simulation"],
        "contexts": ["worldbuilding", "cli"],
        "depth": "masterclass",
        "weight": 1.2,
    },
    {
        'id': 'tip_ecology_square_cube_scaling',
        'engine': 'ecology',
        'feature': 'Square-Cube Skeletal Stress',
        'subfeature': 'skeletal_stress',
        'category': 'craft',
        'pillar': 'cosmology_physics',
        'title': 'Galilean Square-Cube Limit: Grounding Titan Monsters',
        'content': 'Body mass scales with volume (r^3) while bone cross-sectional strength scales only with area (r^2). Biological land animals exceeding 20 tonnes require pillar-like columnar limbs, hollow pneumatic bones, or arcane buoyancy anchors to avoid spontaneous bone collapse.',
        'rationale': 'Applies mathematical scaling laws to maintain biological plausibility for fantasy beasts and alien megafauna.',
        'example': 'arcanum ecology --scale-mass 25000',
        'tags': ['ecology', 'square-cube', 'megafauna', 'biology', 'scaling'],
        'contexts': ['worldbuilding', 'cli'],
        'depth': 'masterclass',
        'weight': 1.1,
    },
    {
        'id': 'tip_cartography_voronoi_physical_barriers',
        'engine': 'cartography',
        'feature': 'Voronoi Realm Border Generator',
        'subfeature': 'voronoi_borders',
        'category': 'craft',
        'pillar': 'society_systems',
        'title': 'Voronoi Political Borders Warped by Mountain Ridges',
        'content': 'Mathematical Voronoi diagrams partition territory equidistant between fortress capitals. In realistic geography, these straight Voronoi lines must be warped and snapped to mountain cordilleras and impassable rivers, creating natural frontier buffers.',
        'rationale': 'Blends computational territorial partitioning with physical topographic constraints.',
        'example': 'arcanum map --voronoi-realms',
        'tags': ['cartography', 'voronoi', 'borders', 'politics', 'geography'],
        'contexts': ['worldbuilding', 'cli'],
        'depth': 'advanced',
        'weight': 1.0,
    },
    {
        'id': 'tip_cartography_dijkstra_friction_weights',
        'engine': 'cartography',
        'feature': 'Dijkstra Journey Router',
        'subfeature': 'dijkstra_routing',
        'category': 'craft',
        'pillar': 'society_systems',
        'title': 'Terrain Friction Weights in Trade Route Modeling',
        'content': 'When routing trade caravans using Dijkstra graphs, assign high friction multipliers to swamps (5x) and mountain passes (8x) relative to paved post roads (1x) or downstream river barges (0.3x). This explains why historical cities grew along river valleys.',
        'rationale': 'Accurate friction modeling produces historically realistic settlement patterns and strategic choke points.',
        'example': 'arcanum map --route --from Capital --to Port',
        'tags': ['cartography', 'dijkstra', 'trade-routes', 'geography', 'routing'],
        'contexts': ['worldbuilding', 'cli'],
        'depth': 'advanced',
        'weight': 1.0,
    },
    {
        'id': 'tip_journey_feed_burn_wagons',
        'engine': 'journey',
        'feature': 'Supply & Feed Burn Auditor',
        'subfeature': 'feed_burn',
        'category': 'craft',
        'pillar': 'society_systems',
        'title': 'Winter Feed Bulk: Why Hay Halves Military Baggage Trains',
        'content': 'In winter expeditions when pasture forage is dead, draft oxen require dry hay which takes up 3x the volume of dense grain. This cuts effective weapon and food transport capacity in half, forcing winter sieges to rely on nearby naval supply or face rapid starvation.',
        'rationale': 'Calculates volumetric cargo density and draft animal consumption rates under adverse seasonal conditions.',
        'example': 'arcanum calc journey --season winter --wagons 40',
        'tags': ['journey', 'logistics', 'winter', 'siege', 'military'],
        'contexts': ['worldbuilding', 'tactics', 'cli'],
        'depth': 'masterclass',
        'weight': 1.1,
    },
    {
        'id': 'tip_structure_midpoint_harmony_act2',
        'engine': 'structure',
        'feature': 'Midpoint Harmony Check',
        'subfeature': 'act2_volume',
        'category': 'craft',
        'pillar': 'narrative_chronology',
        'title': 'Act II Volume Harmony: Maintaining 50% Narrative Mass',
        'content': 'In 3-Act and Hero Journey paradigms, Act II should constitute between 48% and 54% of total manuscript wordcount. If Act II exceeds 60%, the story suffers from repetitive obstacle padding; if under 40%, the protagonist fails to earn their internal transformation.',
        'rationale': 'Monitors structural mass distribution across narrative acts to prevent pacing distortion.',
        'example': 'arcanum structure --harmony-check',
        'tags': ['structure', 'act2', 'harmony', 'proportions', 'editing'],
        'contexts': ['structure', 'review', 'cli', 'canvas'],
        'depth': 'advanced',
        'weight': 1.0,
    },
    {
        'id': 'tip_scene_disaster_hook_types',
        'engine': 'scene_mechanics',
        'feature': 'Disaster Hook Classifier',
        'subfeature': 'disaster_hooks',
        'category': 'craft',
        'pillar': 'editorial_craft',
        'title': 'The 4 Canonical Chapter-Ending Disaster Hooks',
        'content': 'End every scene with one of 4 decisive disaster hooks: (1) Goal denied completely, (2) Goal achieved with devastating secondary cost (Yes, but...), (3) Unforeseen third-party complication, or (4) Moral dilemma that invalidates the original goal.',
        'rationale': 'Ensures every scene propels the narrative forward by denying easy resolutions.',
        'example': 'arcanum audit scenes',
        'tags': ['scene-mechanics', 'disaster', 'cliffhanger', 'pacing', 'craft'],
        'contexts': ['drafting', 'revision', 'cli', 'zen'],
        'depth': 'advanced',
        'weight': 1.1,
    },
    {
        'id': 'tip_pacing_prose_mode_switching',
        'engine': 'pacing',
        'feature': 'Prose Mode Classifier',
        'subfeature': 'mode_switching',
        'category': 'craft',
        'pillar': 'editorial_craft',
        'title': 'The 5 Narrative Modes: Alternating Reading Speed Every 1,500 Words',
        'content': 'The 5 modes (Dialogue, Action, Description, Exposition, Internal Monologue) govern reading tempo. Fast modes (Dialogue/Action) burn reader energy; slow modes (Description/Exposition) allow contemplation. Alternate fast and slow modes every 1,000–1,500 words.',
        'rationale': 'Prevents emotional numbness during prolonged action and boredom during worldbuilding exposition.',
        'example': 'arcanum pace --html',
        'tags': ['pacing', 'prose-modes', 'tempo', 'dialogue', 'exposition'],
        'contexts': ['drafting', 'revision', 'cli', 'zen'],
        'depth': 'masterclass',
        'weight': 1.1,
    },
    {
        'id': 'tip_plot_chekhov_three_phase_lifecycle',
        'engine': 'plot_matrix',
        'feature': 'Chekhov Gun Lifecycle Audit',
        'subfeature': 'chekhov_guns',
        'category': 'craft',
        'pillar': 'narrative_chronology',
        'title': 'Chekhov Gun 3-Phase Lifecycle: Setup, Misdirection, Climax',
        'content': 'Every planted clue or magical relic must pass through 3 phases: (1) Casual, non-dramatic introduction in Act I, (2) False or partial discharge at the Midpoint to divert suspicion, and (3) Decisive, non-obvious payoff in the Climax.',
        'rationale': 'Audits plot elements to ensure foreshadowed items satisfy readers without being predictable.',
        'example': 'arcanum plot --chekhov-scan',
        'tags': ['plot-matrix', 'chekhov-gun', 'foreshadowing', 'climax', 'craft'],
        'contexts': ['plot', 'drafting', 'cli'],
        'depth': 'advanced',
        'weight': 1.1,
    },
    {
        'id': 'tip_branching_topological_cycle_state_mutation',
        'engine': 'branching_graph',
        'feature': 'Topological Dead-End Detector',
        'subfeature': 'cycle_mutation',
        'category': 'craft',
        'pillar': 'narrative_chronology',
        'title': 'Interactive DAG Cycles: Require State Flag Mutation on Return',
        'content': 'In branching interactive fiction, if a choice loops the reader back to an earlier hub location, ensure the traversal mutates at least one state flag (@state: searched_desk = true). Otherwise, the loop creates an inescapable soft-lock trap.',
        'rationale': 'Topological sorting of story DAGs identifies infinite cyclic loops and unreachable leaf nodes.',
        'example': 'arcanum branch --validate',
        'tags': ['branching', 'dag', 'gamebook', 'interactive-fiction', 'logic'],
        'contexts': ['drafting', 'cli'],
        'depth': 'advanced',
        'weight': 1.0,
    },
    {
        'id': 'tip_branching_twine_ink_transpiler_state',
        'engine': 'branching_graph',
        'feature': 'Twine / Ink Transpiler',
        'subfeature': 'transpiler',
        'category': 'utility',
        'pillar': 'system_ops',
        'title': 'Twine & Ink Transpilation: Preserving @choice and @state Syntax',
        'content': 'Draft interactive branching gamebooks in plain Markdown with @choice: [Label] -> target and @state: flags. Export directly to Twine Harlowe/SugarCube HTML or Inkle Ink scripts with full variable logic intact.',
        'rationale': 'Allows distraction-free drafting in standard Markdown while supporting standard game engines.',
        'example': 'arcanum branch --export-ink story.ink',
        'tags': ['branching', 'twine', 'ink', 'transpiler', 'export'],
        'contexts': ['export', 'cli'],
        'depth': 'intermediate',
        'weight': 1.0,
    },
    {
        'id': 'tip_canvas_atomic_disk_renumbering',
        'engine': 'story_canvas',
        'feature': 'Atomic Disk Renumberer',
        'subfeature': 'disk_renumber',
        'category': 'core',
        'pillar': 'system_ops',
        'title': 'Atomic Canvas Renumbering: Reorder Chapters Without Broken Git History',
        'content': 'When dragging scene cards on the visual corkboard to rearrange chapter sequences, the atomic disk renumberer updates filename numeric prefixes (01_, 02_) and frontmatter sequence tags using two-pass temporary staging to prevent git diff collision.',
        'rationale': 'Preserves clean revision history and file atomicity when restructuring large manuscripts.',
        'example': 'arcanum canvas --sync-disk',
        'tags': ['story-canvas', 'renumbering', 'git', 'atomic-write', 'organization'],
        'contexts': ['canvas', 'cli'],
        'depth': 'advanced',
        'weight': 1.0,
    },
    {
        'id': 'tip_causality_multiverse_bifurcation_entropy',
        'engine': 'causality',
        'feature': 'Multiverse Branch Visualizer',
        'subfeature': 'bifurcation_entropy',
        'category': 'craft',
        'pillar': 'narrative_chronology',
        'title': 'Multiverse Bifurcation: Track Divergence Entropy from Anchor Nodes',
        'content': 'In alternate history and parallel timeline stories, every divergent branch must originate from an explicit historical bifurcation event. Track divergence entropy over time: small initial differences compound into radical cultural divergence over generations.',
        'rationale': 'Provides rigorous mathematical DAG rails for multiverse worldbuilding.',
        'example': 'arcanum causality --multiverse-tree',
        'tags': ['causality', 'multiverse', 'bifurcation', 'alternate-history', 'timeline'],
        'contexts': ['worldbuilding', 'plot', 'cli'],
        'depth': 'masterclass',
        'weight': 1.1,
    },
    {
        'id': 'tip_timeline_bilocation_conflict_sweeper',
        'engine': 'timeline_sync',
        'feature': 'Bilocation Conflict Detector',
        'subfeature': 'bilocation_check',
        'category': 'craft',
        'pillar': 'narrative_chronology',
        'title': 'The Bilocation Auditor: Catching Impossible Character Teleportation',
        'content': 'In multi-POV epics, the bilocation detector cross-references character scene timestamps against the cartography journey distance matrix. It flags when a character appears at Fortress B on Day 14 after being seen at Coastal City A on Day 12 without sufficient travel time.',
        'rationale': 'Automates spatial-temporal validation to eliminate glaring logistical plot holes.',
        'example': 'arcanum timeline --audit-bilocation',
        'tags': ['timeline-sync', 'bilocation', 'continuity', 'travel-time', 'logistics'],
        'contexts': ['review', 'worldbuilding', 'cli'],
        'depth': 'advanced',
        'weight': 1.1,
    },
    {
        'id': 'tip_prophecy_delphic_three_interpretations',
        'engine': 'prophecy',
        'feature': 'Delphic Ambiguity Analyzer',
        'subfeature': 'adversarial_interpretations',
        'category': 'craft',
        'pillar': 'narrative_chronology',
        'title': 'Delphic Stress-Testing: Evaluating 3 Adversarial Interpretations',
        'content': 'Before finalizing an in-universe prophecy, run the Delphic analyzer to test 3 distinct readings: (1) The Dogmatic/Orthodox belief of the priesthood, (2) The Protagonist literal hope, and (3) The True Arcane Resolution that subverts both.',
        'rationale': 'Guarantees that prophetic fulfillment produces genuine revelation rather than predictable melodrama.',
        'example': 'arcanum prophecy --delphic-test',
        'tags': ['prophecy', 'delphi', 'ambiguity', 'climax', 'lore'],
        'contexts': ['worldbuilding', 'plot', 'cli'],
        'depth': 'masterclass',
        'weight': 1.2,
    },
    {
        'id': 'tip_sprint_circadian_velocity_alignment',
        'engine': 'writing_sprint',
        'feature': 'Productivity Heatmap',
        'subfeature': 'circadian_velocity',
        'category': 'core',
        'pillar': 'manuscript_drafting',
        'title': 'Circadian Velocity: Matching Drafting to Biological Peak Hours',
        'content': 'Your writing sprint telemetry generates a 24-hour circadian productivity heatmap. Schedule raw first-draft drafting during your highest-WPM biological window (e.g. 06:30–08:30) and reserve low-velocity afternoon hours for worldbuilding lore entries.',
        'rationale': 'Aligns cognitively demanding creative output with personal circadian dopamine rhythms.',
        'example': 'arcanum sprint --heatmap',
        'tags': ['sprint', 'circadian', 'productivity', 'analytics', 'drafting'],
        'contexts': ['drafting', 'zen', 'cli'],
        'depth': 'intermediate',
        'weight': 1.0,
    },
    {
        'id': 'tip_dramatis_phonetic_name_collision_auditor',
        'engine': 'dramatis_personae',
        'feature': 'Phonetic Name Collision Auditor',
        'subfeature': 'phonetic_collision',
        'category': 'craft',
        'pillar': 'editorial_craft',
        'title': 'Phonetic Collision Linter: Eliminating Same-Initial Character Confusion',
        'content': 'Readers subconsciously confuse characters who share the same first initial and syllable count (e.g. Kenneth, Kristin, Kathryn). The phonetic collision auditor scans your cast and flags shared phonotactic envelopes.',
        'rationale': 'Reduces cognitive friction in ensemble casts by ensuring distinctive character acoustic profiles.',
        'example': 'arcanum cast --audit-phonetics',
        'tags': ['dramatis-personae', 'names', 'phonetics', 'clarity', 'cast'],
        'contexts': ['worldbuilding', 'review', 'cli'],
        'depth': 'intermediate',
        'weight': 1.0,
    },
    {
        'id': 'tip_dramatis_pov_screentime_balancer',
        'engine': 'dramatis_personae',
        'feature': 'POV Screen-Time Balancer',
        'subfeature': 'screentime_balance',
        'category': 'craft',
        'pillar': 'narrative_chronology',
        'title': 'POV Wordcount Quotas: Preventing Secondary Characters from Hijacking the Book',
        'content': 'In multi-POV epics, track the exact percentage of total words allocated to each viewpoint character. If a secondary comic-relief POV exceeds 25% of total volume, the main emotional arc loses dramatic focus.',
        'rationale': 'Monitors POV screen-time balance across volume chapters to maintain thematic cohesion.',
        'example': 'arcanum words --pov',
        'tags': ['dramatis-personae', 'pov', 'screentime', 'balance', 'pacing'],
        'contexts': ['review', 'structure', 'cli'],
        'depth': 'intermediate',
        'weight': 1.0,
    },
    {
        'id': 'tip_voice_sensory_focus_bias',
        'engine': 'voice',
        'feature': 'Idiolect Uniqueness Scorer',
        'subfeature': 'sensory_focus_bias',
        'category': 'craft',
        'pillar': 'editorial_craft',
        'title': 'Viewpoint Sensory Bias: Characters Notice What They Care About',
        'content': 'Differentiate POV voices by assigning each character a distinct sensory lens: a blacksmith POV notices metal alloys, heat gradients, and joint stress; a courtier POV notices fabric weaves, perfumes, and nervous micro-expressions.',
        'rationale': 'Sensory selection reinforces character professional background without requiring explicit exposition.',
        'example': 'arcanum audit voice',
        'tags': ['voice', 'sensory', 'viewpoint', 'characterization', 'prose-craft'],
        'contexts': ['drafting', 'revision', 'cli', 'zen'],
        'depth': 'masterclass',
        'weight': 1.2,
    },
    {
        'id': 'tip_voice_voice_bleed_rare_metaphors',
        'engine': 'voice',
        'feature': 'Voice Bleed Matrix',
        'subfeature': 'metaphor_bleed',
        'category': 'craft',
        'pillar': 'editorial_craft',
        'title': 'Metaphor Bleed Linter: Never Let Two Characters Share Rare Idioms',
        'content': 'The voice bleed matrix flags when two different viewpoint characters employ identical rare metaphors or idiomatic expressions. Unique figurative language must belong strictly to one cultural or individual idiolect.',
        'rationale': 'Preserves the psychological illusion of distinct consciousnesses across POV transitions.',
        'example': 'arcanum audit voice --bleed',
        'tags': ['voice', 'voice-bleed', 'metaphors', 'dialogue', 'stylistics'],
        'contexts': ['revision', 'review', 'cli'],
        'depth': 'masterclass',
        'weight': 1.1,
    },
    {
        'id': 'tip_conlang_leipzig_gloss_parser',
        'engine': 'conlang',
        'feature': 'Leipzig Gloss Parser',
        'subfeature': 'leipzig_glossing',
        'category': 'craft',
        'pillar': 'society_systems',
        'title': '3-Line Leipzig Glossing: Grammatical Rigor for In-Universe Inscriptions',
        'content': 'Format fictional language runes and ancient prophecies using standard 3-line Leipzig Glossing (Original Text -> Morpheme-by-Morpheme Tags -> Idiomatic English). This guarantees grammatical consistency across all world lore volumes.',
        'rationale': 'Enforces linguistic authenticity and eliminates arbitrary fantasy gibberish.',
        'example': 'arcanum conlang lex High-Valdian --gloss',
        'tags': ['conlang', 'leipzig', 'linguistics', 'grammar', 'inscriptions'],
        'contexts': ['worldbuilding', 'cli'],
        'depth': 'advanced',
        'weight': 1.0,
    },
    {
        'id': 'tip_conlang_phonotactic_syllable_templates',
        'engine': 'conlang',
        'feature': 'Phonotactic Syllable Generator',
        'subfeature': 'syllable_templates',
        'category': 'craft',
        'pillar': 'society_systems',
        'title': 'Sonority Hierarchy Templates: Generating Cohesive Fantasy Place Names',
        'content': 'Define exact maximal syllable templates (e.g. (C)V(N)) and sonority sequencing rules for each culture. Generating place names from these rules guarantees all cities in Kingdom A sound culturally unified without sounding like random vowel soup.',
        'rationale': 'Sonority sequencing governs human articulatory ease, creating organic linguistic identity.',
        'example': 'arcanum conlang gen Elven --count 50',
        'tags': ['conlang', 'phonotactics', 'syllables', 'place-names', 'naming'],
        'contexts': ['worldbuilding', 'cli'],
        'depth': 'advanced',
        'weight': 1.0,
    },
    {
        'id': 'tip_genealogy_succession_claim_roster_conflicts',
        'engine': 'genealogy',
        'feature': 'Succession Claim Roster',
        'subfeature': 'succession_claims',
        'category': 'craft',
        'pillar': 'society_systems',
        'title': 'Succession Law Clashes: Generating Organic Dynastic Civil Wars',
        'content': 'Model succession crises by pitting competing legal doctrines against each other: Salic Law (strictly agnatic male line) vs Proximity of Blood (daughter of elder son vs living younger uncle). The legal ambiguity creates compelling, multi-faceted civil wars.',
        'rationale': 'Historical dynastic wars erupted from legitimate competing legal claims rather than simple villainous greed.',
        'example': 'arcanum lineage House-Valerius',
        'tags': ['genealogy', 'succession', 'civil-war', 'dynasty', 'politics'],
        'contexts': ['worldbuilding', 'cli'],
        'depth': 'masterclass',
        'weight': 1.1,
    },
    {
        'id': 'tip_factions_diplomatic_paradox_cascades',
        'engine': 'factions',
        'feature': 'Diplomatic Paradox Sweeper',
        'subfeature': 'diplomatic_paradoxes',
        'category': 'craft',
        'pillar': 'society_systems',
        'title': 'Diplomatic Paradox Sweeper: WWI-Style Incompatible Treaty Cascades',
        'content': 'Run the diplomatic paradox sweeper to find treaty contradictions (e.g. Faction A has mutual defense pacts with both B and C; when B attacks C, A is legally bound to declare war on both). Use this to trap moral leaders in no-win geopolitical crises.',
        'rationale': 'Complex alliance webs produce explosive, deterministic geopolitical escalations.',
        'example': 'arcanum faction --audit-treaties',
        'tags': ['factions', 'treaties', 'diplomacy', 'geopolitics', 'alliances'],
        'contexts': ['worldbuilding', 'cli'],
        'depth': 'masterclass',
        'weight': 1.1,
    },
    {
        'id': 'tip_economy_coinage_debasement_simulator',
        'engine': 'economy',
        'feature': 'Coinage Debasement Simulator',
        'subfeature': 'coin_debasement',
        'category': 'craft',
        'pillar': 'society_systems',
        'title': 'Coinage Debasement Simulator: Mercenary Mutinies and Black Markets',
        'content': 'Simulate how royal coin clipping and copper dilution triggers wage protests from foreign mercenaries who refuse debased payment, forcing the crown to offer land grants or surrender strategic castles as collateral.',
        'rationale': 'Monetary debasement connects macroeconomic fiscal distress directly to military crisis.',
        'example': 'arcanum economy --debase-sim',
        'tags': ['economy', 'debasement', 'mercenaries', 'money', 'worldbuilding'],
        'contexts': ['worldbuilding', 'cli'],
        'depth': 'advanced',
        'weight': 1.0,
    },
    {
        'id': 'tip_tactical_fencing_tempo_beats',
        'engine': 'tactical_sim',
        'feature': 'Choreography Beat Generator',
        'subfeature': 'fencing_tempo',
        'category': 'craft',
        'pillar': 'editorial_craft',
        'title': 'Historical Duel Choreography: Vor, Nach, and Indes Tempos',
        'content': 'Ground sword duels in German Liechtenauer fencing concepts: Vor (Before/Attacking), Nach (After/Defending/Parrying), and Indes (Instantly taking the bind during contact). Every strike should shift tactical initiative rather than trading meaningless blows.',
        'rationale': 'Authentic martial tempo structures duels with logical cause-and-effect combat tension.',
        'example': 'arcanum sim battle --duel',
        'tags': ['tactical-sim', 'fencing', 'choreography', 'combat', 'duels'],
        'contexts': ['drafting', 'revision', 'cli'],
        'depth': 'masterclass',
        'weight': 1.1,
    },
    {
        'id': 'tip_magic_arcane_cost_backlash_ledger',
        'engine': 'magic_system',
        'feature': 'Arcane Cost & Backlash Ledger',
        'subfeature': 'arcane_backlash',
        'category': 'craft',
        'pillar': 'cosmology_physics',
        'title': 'Arcane Backlash Ledger: Mana Waste Heat and Environmental Trauma',
        'content': 'Enforce the first law of arcane thermodynamics: dissipated spell energy cannot vanish. Failed or interrupted spells must release their stored potential into the immediate environment as localized heat waves, sensory flash-blindness, or structural crystallization.',
        'rationale': 'Converts spell failure from a simple fizzle into an active, dangerous narrative complication.',
        'example': 'arcanum magic-check',
        'tags': ['magic', 'backlash', 'thermodynamics', 'costs', 'worldbuilding'],
        'contexts': ['worldbuilding', 'drafting', 'cli'],
        'depth': 'masterclass',
        'weight': 1.1,
    },
    {
        'id': 'tip_stylistics_filter_word_stripping',
        'engine': 'stylistics',
        'feature': 'Filter Word Stripper',
        'subfeature': 'filter_words',
        'category': 'craft',
        'pillar': 'editorial_craft',
        'title': 'Filter Word Stripper: Collapsing Psychic Distance in Deep POV',
        'content': "Strip sensory filter verbs (she saw, he heard, she felt, he realized, she noticed). Instead of 'She heard the thunder rumble across the valley', write 'Thunder rumbled across the valley'. This places the reader directly inside the character's perception.",
        'rationale': 'Filter words insert an unnecessary cognitive layer between reader and story events.',
        'example': 'arcanum audit prose --filter-words',
        'tags': ['stylistics', 'filter-words', 'deep-pov', 'prose-craft', 'immersion'],
        'contexts': ['drafting', 'revision', 'cli', 'zen'],
        'depth': 'advanced',
        'weight': 1.1,
    },
    {
        'id': 'tip_stylistics_flesch_kincaid_readability_tuning',
        'engine': 'stylistics',
        'feature': 'Flesch-Kincaid Readability Auditor',
        'subfeature': 'flesch_kincaid',
        'category': 'craft',
        'pillar': 'editorial_craft',
        'title': 'Calibrating Flesch-Kincaid Grade Levels to Narrative Intensity',
        'content': 'High-octane action scenes should target Grade 4–6 Flesch-Kincaid reading levels (short words, immediate verbs), while contemplative lore or courtly diplomacy comfortably sits at Grade 9–11. Sudden jumps in grade level flag pacing turbulence.',
        'rationale': 'Measures cognitive processing load across manuscript chapters to maintain appropriate tension.',
        'example': 'arcanum audit rhythm',
        'tags': ['stylistics', 'flesch-kincaid', 'readability', 'rhythm', 'editing'],
        'contexts': ['revision', 'review', 'cli'],
        'depth': 'intermediate',
        'weight': 1.0,
    },
    {
        'id': 'tip_senses_8channel_sensory_scanner',
        'engine': 'senses',
        'feature': '8-Channel Sensory Scanner',
        'subfeature': '8_channel_scan',
        'category': 'craft',
        'pillar': 'editorial_craft',
        'title': '8-Channel Sensory Scanner: Thermal, Vestibular, and Proprioceptive Cues',
        'content': 'Beyond sight and sound, scan for the lesser-used sensory channels: Vestibular (balance, dizziness, falling sensation), Thermal (radiant hearth heat, icy drafts), and Proprioceptive (muscle fatigue, weight of heavy cloaks). These create visceral physical realism.',
        'rationale': "Vestibular and proprioceptive sensations activate somatic empathy in the reader's sensorimotor cortex.",
        'example': 'arcanum audit senses',
        'tags': ['senses', '8-channel', 'proprioception', 'thermal', 'immersion'],
        'contexts': ['drafting', 'revision', 'cli', 'zen'],
        'depth': 'masterclass',
        'weight': 1.2,
    },
    {
        'id': 'tip_continuity_inventory_relic_tracker',
        'engine': 'continuity',
        'feature': 'Inventory & Relic Tracker',
        'subfeature': 'inventory_relics',
        'category': 'craft',
        'pillar': 'editorial_craft',
        'title': 'Relic & Inventory Tracker: Catching Lost Weapons and Impossible Keys',
        'content': 'The inventory continuity engine tracks carried keys, weapons, maps, and artifacts across scene transitions. It flags when a character draws a dagger that was confiscated by town guards two chapters earlier.',
        'rationale': 'Prevents jarring continuity lapses that break reader trust in plot mechanics.',
        'example': 'arcanum continuity --inventory',
        'tags': ['continuity', 'inventory', 'relics', 'weapons', 'props'],
        'contexts': ['review', 'revision', 'cli'],
        'depth': 'intermediate',
        'weight': 1.0,
    },
    {
        'id': 'tip_series_timeskip_aging_validator',
        'engine': 'series_continuity',
        'feature': 'Timeskip Aging Validator',
        'subfeature': 'timeskip_aging',
        'category': 'craft',
        'pillar': 'narrative_chronology',
        'title': 'Timeskip Aging Validator: Maintaining Multi-Year Canon Coherence',
        'content': 'When advancing the timeline by 5, 10, or 20 years between volumes, the timeskip validator computes correct character ages, verifies pregnancy timelines, and checks that mentor figures exhibit appropriate signs of physical aging.',
        'rationale': 'Maintains airtight chronological consistency across multi-volume series.',
        'example': 'arcanum series --timeskip 10',
        'tags': ['series-continuity', 'timeskip', 'aging', 'canon', 'chronology'],
        'contexts': ['worldbuilding', 'review', 'cli'],
        'depth': 'advanced',
        'weight': 1.0,
    },
    {
        'id': 'tip_typography_dialogue_comma_splice_linter',
        'engine': 'typography_cleaner',
        'feature': 'Dialogue Comma Splice Linter',
        'subfeature': 'dialogue_punctuation',
        'category': 'utility',
        'pillar': 'editorial_craft',
        'title': 'Dialogue Punctuation: Speech Tags Use Commas, Action Beats Use Periods',
        'content': "Ensure dialogue punctuation adheres to professional publishing standards: Speech tags use internal commas ('No,' he said.), whereas physical action beats require periods ('No.' He drew his blade.). The typography cleaner automatically audits these.",
        'rationale': 'Enforces Chicago Manual of Style dialogue punctuation rules before final typesetting.',
        'example': 'arcanum polish typography Manuscript/',
        'tags': ['typography', 'dialogue', 'punctuation', 'editing', 'publishing'],
        'contexts': ['export', 'publishing', 'cli'],
        'depth': 'intermediate',
        'weight': 1.0,
    },
    {
        'id': 'tip_diff_excised_prose_scraps_vault',
        'engine': 'manuscript_diff',
        'feature': 'Excised Prose Scraps Vault',
        'subfeature': 'scraps_vault',
        'category': 'core',
        'pillar': 'editorial_craft',
        'title': 'Excised Scraps Vault: Never Lose High-Quality Cut Paragraphs',
        'content': 'When cutting bloated scenes during developmental edits, the redline diff engine automatically archives excised blocks into `_scraps/`. You can salvage beautiful descriptive imagery or world lore snippets for later books without feeling guilty about ruthless pruning.',
        'rationale': 'Removes psychological hesitation during developmental cutting by guaranteeing safety of excised prose.',
        'example': 'arcanum compare Manuscript Draft-02 Draft-01 --save-scraps',
        'tags': ['diff', 'scraps', 'editing', 'pruning', 'preservation'],
        'contexts': ['revision', 'review', 'cli'],
        'depth': 'intermediate',
        'weight': 1.0,
    },
    {
        'id': 'tip_heatmap_perfectionist_trap_detector',
        'engine': 'revision_heatmap',
        'feature': 'Perfectionist Trap Detector',
        'subfeature': 'perfectionist_trap',
        'category': 'craft',
        'pillar': 'manuscript_drafting',
        'title': 'Perfectionist Trap Detector: Breaking the Chapter 1 Polish Loop',
        'content': 'The revision heatmap alerts authors when Chapter 1 has undergone >15 revision cycles while middle chapters remain unwritten. It gently nudges you to freeze early chapters and focus drafting energy forward on Act II and Act III.',
        'rationale': 'Prevents the common writer pitfall of endlessly polishing opening scenes at the expense of finishing the draft.',
        'example': 'arcanum revision-heatmap Manuscript',
        'tags': ['revision-heatmap', 'perfectionism', 'drafting', 'momentum', 'productivity'],
        'contexts': ['drafting', 'revision', 'cli'],
        'depth': 'intermediate',
        'weight': 1.1,
    },
    {
        'id': 'tip_hub_craft_science_encyclopedia_viewer',
        'engine': 'studio_hub',
        'feature': 'Craft Science Encyclopedia Viewer',
        'subfeature': 'science_encyclopedia',
        'category': 'core',
        'pillar': 'system_ops',
        'title': 'In-Situ Craft Science Encyclopedia: Instant Formula Lookups',
        'content': 'Open the Craft Science tab in Studio Hub to review closed-form formulas (Lorentz gamma, Köppen climate thresholds, Lanchester differential combat) without leaving your offline drafting environment.',
        'rationale': 'Provides authoritative mathematical and physical reference within a sovereign, zero-telemetry studio.',
        'example': 'arcanum hub',
        'tags': ['studio-hub', 'encyclopedia', 'formulas', 'reference', 'offline'],
        'contexts': ['studio', 'worldbuilding', 'cli'],
        'depth': 'intermediate',
        'weight': 1.0,
    },
    {
        'id': 'tip_ambient_procedural_soundscapes_infinite',
        'engine': 'ambient',
        'feature': 'Procedural Soundscapes',
        'subfeature': 'procedural_audio',
        'category': 'utility',
        'pillar': 'manuscript_drafting',
        'title': 'Procedural Audio Synthesis: Infinite Non-Repeating Focus Loops',
        'content': 'Unlike looped MP3 files that fatigue the ear with repeating sound artifacts every 30 seconds, Ars Arcanum ambient audio generates organic pink noise, rain droplet timing, and low tavern murmur procedurally in real-time math.',
        'rationale': 'Procedural audio eliminates repetitive auditory triggers that break deep concentration.',
        'example': 'arcanum ambient generate tavern',
        'tags': ['ambient', 'procedural-audio', 'soundscape', 'focus', 'flow-state'],
        'contexts': ['drafting', 'zen', 'cli'],
        'depth': 'advanced',
        'weight': 1.0,
    },
    {
        'id': 'tip_portfolio_catalog_milestone_aggregation',
        'engine': 'portfolio',
        'feature': 'Catalog Analytics Overview',
        'subfeature': 'milestone_aggregation',
        'category': 'utility',
        'pillar': 'system_ops',
        'title': 'Portfolio Catalog: Multi-Volume Series Progress at a Glance',
        'content': 'The portfolio engine aggregates active draft status, total series wordcounts, and editorial milestone readiness across all manuscripts in your ~/Manuscripts/ directory into a single unified dashboard.',
        'rationale': 'Gives prolific series authors executive oversight across multiple simultaneous writing projects.',
        'example': 'arcanum portfolio --html',
        'tags': ['portfolio', 'catalog', 'dashboard', 'milestones', 'series'],
        'contexts': ['review', 'cli'],
        'depth': 'intermediate',
        'weight': 1.0,
    },
    {
        'id': 'tip_local_rag_context_pack_injection',
        'engine': 'local_rag',
        'feature': 'Context Pack Builder',
        'subfeature': 'context_packs',
        'category': 'core',
        'pillar': 'system_ops',
        'title': 'Context Pack Builder: Scene-Specific Lore Injection',
        'content': "Before drafting a high-stakes confrontation, generate a targeted Context Pack (arcanum rag --pack 'High Temple Siege'). It pulls relevant character rivalries, weapon specs, and architectural layout notes into a compact drafting cheat-sheet.",
        'rationale': 'Synthesizes relevant lore into immediate working memory for high-density drafting sessions.',
        'example': "arcanum rag --pack 'Treaty of Vald'",
        'tags': ['local-rag', 'context-pack', 'drafting', 'lore-retrieval', 'cheat-sheet'],
        'contexts': ['drafting', 'zen', 'cli'],
        'depth': 'advanced',
        'weight': 1.1,
    },
    {
        'id': 'tip_corpus_bidirectional_vault_restore',
        'engine': 'corpus_export',
        'feature': 'Bidirectional Vault Restore',
        'subfeature': 'vault_restore',
        'category': 'utility',
        'pillar': 'system_ops',
        'title': 'Corpus Vault Restore: Full Project Recovery from a Single JSONL Archive',
        'content': "In disaster recovery scenarios, use 'arcanum corpus-restore <dataset.jsonl>' to instantly reconstruct your entire folder hierarchy, Markdown files, and YAML frontmatter with 100% fidelity.",
        'rationale': 'Ensures disaster recovery resilience without relying on cloud sync services.',
        'example': 'arcanum corpus-restore backup_corpus.jsonl --target ~/RestoredVault',
        'tags': ['corpus-export', 'restore', 'backup', 'disaster-recovery', 'safety'],
        'contexts': ['cli'],
        'depth': 'advanced',
        'weight': 1.0,
    },
    {
        'id': 'tip_importer_monolithic_docx_chapter_splitting',
        'engine': 'importer',
        'feature': 'Monolithic Docx Chapter Splitter',
        'subfeature': 'docx_splitter',
        'category': 'utility',
        'pillar': 'system_ops',
        'title': 'Monolithic Word Import: Auto-Splitting by Heading Styles',
        'content': "Importing a massive 150,000-word single-file Word document automatically detects 'Heading 1' and 'Heading 2' paragraph styles, splitting them into neatly numbered individual chapter files with extracted titles.",
        'rationale': 'Eliminates tedious manual copy-pasting when migrating large manuscripts from traditional word processors.',
        'example': 'arcanum import EpicNovel.docx --split-headings',
        'tags': ['importer', 'docx', 'splitting', 'migration', 'word'],
        'contexts': ['cli'],
        'depth': 'intermediate',
        'weight': 1.0,
    },
    {
        'id': 'tip_docx_conflict_branching_non_destructive',
        'engine': 'docx_sync',
        'feature': 'Conflict Branching',
        'subfeature': 'conflict_branches',
        'category': 'core',
        'pillar': 'system_ops',
        'title': 'DOCX Non-Destructive Conflict Branches: Zero Overwrite Risk',
        'content': 'If a manuscript chapter was edited in Obsidian and simultaneously modified by an editor in Microsoft Word, docx_sync detects the timestamp collision and creates a `.conflict.md` branch rather than overwriting either version.',
        'rationale': 'Upholds the Ars Arcanum zero-data-loss invariant across external editor roundtrips.',
        'example': 'arcanum docx sync Manuscript/',
        'tags': ['docx-sync', 'conflict-resolution', 'safety', 'word', 'collaboration'],
        'contexts': ['export', 'publishing', 'cli'],
        'depth': 'advanced',
        'weight': 1.0,
    },
    {
        'id': 'tip_world_doctor_fuzzy_name_variant_finder',
        'engine': 'world_doctor',
        'feature': 'Fuzzy Name Variant Finder',
        'subfeature': 'fuzzy_name_variants',
        'category': 'utility',
        'pillar': 'society_systems',
        'title': 'Fuzzy Name Variant Finder: Catching Inadvertent Spelling Mutations',
        'content': "The World Doctor uses Levenshtein distance matching across all lore files to detect accidental name variations (e.g. 'Aeliana' vs 'Aelyana' vs 'Aelliana') created over months of worldbuilding.",
        'rationale': 'Maintains rigorous orthographic consistency across sprawling fantasy epics.',
        'example': 'arcanum world-doctor Worlds/Cosmos --fuzzy-names',
        'tags': ['world-doctor', 'spelling', 'names', 'levenshtein', 'consistency'],
        'contexts': ['worldbuilding', 'review', 'cli'],
        'depth': 'intermediate',
        'weight': 1.0,
    },
    {
        'id': 'tip_diagnostics_air_gap_isolation_audit',
        'engine': 'diagnostics',
        'feature': 'Air-Gap Network Isolation Audit',
        'subfeature': 'air_gap_audit',
        'category': 'utility',
        'pillar': 'system_ops',
        'title': 'Air-Gap Network Audit: Verifying 100% Offline Data Privacy',
        'content': 'Run the diagnostic air-gap audit to verify that all generated HTML files, static wikis, and local HTTP endpoints contain zero remote script tags, CDN stylesheets, or outbound telemetry requests.',
        'rationale': 'Guarantees absolute intellectual property privacy for unreleased creative manuscripts.',
        'example': 'arcanum doctor --air-gap',
        'tags': ['diagnostics', 'air-gap', 'privacy', 'offline', 'security'],
        'contexts': ['cli'],
        'depth': 'intermediate',
        'weight': 1.0,
    },
    {
        'id': 'tip_config_cascading_resolution_hierarchy',
        'engine': 'config',
        'feature': 'Cascading Resolution Inspector',
        'subfeature': 'cascading_config',
        'category': 'utility',
        'pillar': 'system_ops',
        'title': 'Cascading Preferences: Frontmatter Overrides Project Overrides Global',
        'content': 'Configuration settings resolve in strict cascading order: Chapter Frontmatter YAML > Project world.yaml/manuscript.yaml > Global ~/.config/ars-arcanum/config.json. You can set global dark mode while customizing specific project export trim sizes.',
        'rationale': 'Provides granular configuration control without duplicating settings across files.',
        'example': 'arcanum config',
        'tags': ['config', 'cascading', 'hierarchy', 'preferences', 'yaml'],
        'contexts': ['cli'],
        'depth': 'intermediate',
        'weight': 1.0,
    },
    {
        'id': 'tip_cache_ast_indexer_mtime_preindexing',
        'engine': 'cache',
        'feature': 'mtime AST Indexer',
        'subfeature': 'ast_indexing',
        'category': 'utility',
        'pillar': 'system_ops',
        'title': 'MTime AST Indexer: Sub-5ms Query Speeds Across 1,000,000 Words',
        'content': 'The performance cache pre-indexes chapter Markdown syntax trees, heading maps, and @tag directives into an mtime-keyed binary cache, allowing full-universe searches to execute in under 5 milliseconds.',
        'rationale': 'Eliminates repetitive file parsing, keeping CLI and GUI interactions instantaneous.',
        'example': 'arcanum cache scan',
        'tags': ['cache', 'ast', 'indexing', 'performance', 'speed'],
        'contexts': ['cli'],
        'depth': 'advanced',
        'weight': 1.0,
    },
    {
        'id': 'tip_fs_cross_platform_arcanum_lock',
        'engine': 'fs_utils',
        'feature': 'Cross-Platform File Lock (ArcanumLock)',
        'subfeature': 'arcanum_lock',
        'category': 'core',
        'pillar': 'system_ops',
        'title': 'Cross-Platform ArcanumLock: Concurrency Safety Across OS Platforms',
        'content': 'The ArcanumLock context manager uses fcntl.flock on POSIX and msvcrt.locking on Windows. Concurrency-sensitive operations (backups, exports, migrations) acquire exclusive file locks to prevent multi-process race conditions.',
        'rationale': 'Guarantees robust multi-process safety across all major operating systems.',
        'example': 'from lib.lockfile import ArcanumLock; with ArcanumLock(path): ...',
        'tags': ['fs-utils', 'locking', 'concurrency', 'file-safety', 'cross-platform'],
        'contexts': ['system', 'cli'],
        'depth': 'masterclass',
        'weight': 1.2,
    },
    {
        'id': 'tip_preflight_spine_width_paper_density_math',
        'engine': 'preflight',
        'feature': 'Spine Width Calculator',
        'subfeature': 'spine_width_math',
        'category': 'utility',
        'pillar': 'editorial_craft',
        'title': 'Spine Width Calculation: Page Count and Paper Density Formulas',
        'content': 'Print book spine thickness is calculated by: Spine (mm) = (Page Count / 2) * (Caliper in mm). 50lb white paper has a PPI of ~512 (0.0496mm/leaf), while 60lb cream paper has a PPI of ~434 (0.0585mm/leaf). Preflight audits cover dimensions before PDF compilation.',
        'rationale': 'Eliminates spine text misalignment on paperback and hardcover book jackets.',
        'example': 'arcanum preflight Manuscript/ --spine-check',
        'tags': ['preflight', 'spine-width', 'paper-weight', 'typesetting', 'publishing'],
        'contexts': ['export', 'publishing', 'cli'],
        'depth': 'advanced',
        'weight': 1.1,
    },
    {
        'id': 'tip_preflight_pod_signature_auditor',
        'engine': 'preflight',
        'feature': 'POD Signature Auditor',
        'subfeature': 'signature_alignment',
        'category': 'utility',
        'pillar': 'editorial_craft',
        'title': 'POD Signature Auditor: Eliminating Unwanted Trailing Blank Pages',
        'content': 'Traditional offset and print-on-demand presses print in 4-page, 8-page, or 16-page signatures. If your final page count is 321 pages, a 16-page press will insert 15 blank pages at the end of your book. Preflight alerts you to tighten formatting to reach an even multiple of 4 or 8.',
        'rationale': 'Optimizes print signature economics and prevents awkward blank page clusters.',
        'example': 'arcanum preflight Manuscript/ --signatures',
        'tags': ['preflight', 'signatures', 'pod', 'print', 'publishing'],
        'contexts': ['export', 'publishing', 'cli'],
        'depth': 'advanced',
        'weight': 1.1,
    },
    {
        'id': 'tip_frontmatter_schema_normalizer_keys',
        'engine': 'frontmatter_builder',
        'feature': 'Frontmatter Normalizer',
        'subfeature': 'schema_normalization',
        'category': 'craft',
        'pillar': 'editorial_craft',
        'title': 'Frontmatter Normalizer: Standardizing Inconsistent YAML Headers',
        'content': 'The frontmatter normalizer standardizes disparate metadata keys (e.g. converting legacy POV:, Character:, pov: to canonical lowercase pov:) across all chapters in a manuscript with atomic write safety.',
        'rationale': 'Maintains schema hygiene and prevents parsing errors in downstream craft engines.',
        'example': 'arcanum matter build Manuscript/ --normalize',
        'tags': ['frontmatter', 'yaml', 'schema', 'normalization', 'consistency'],
        'contexts': ['publishing', 'export', 'cli'],
        'depth': 'intermediate',
        'weight': 1.0,
    },
    {
        'id': 'tip_concordance_chronological_first_appearance',
        'engine': 'concordance',
        'feature': 'Dramatis Personae Indexer',
        'subfeature': 'first_appearance_indexing',
        'category': 'craft',
        'pillar': 'editorial_craft',
        'title': 'First-Appearance Cast Indexing: Chronological Character Introduction Lists',
        'content': 'The concordance engine can generate a Dramatis Personae sorted strictly by chapter of first appearance, complete with initial alias and page number, making multi-volume fantasy cast lists easy for readers to reference.',
        'rationale': 'Automates complex back-matter compilation from AST manuscript scans.',
        'example': 'arcanum concordance Manuscript/ --first-appearance',
        'tags': ['concordance', 'dramatis-personae', 'cast', 'first-appearance', 'backmatter'],
        'contexts': ['publishing', 'export', 'cli'],
        'depth': 'intermediate',
        'weight': 1.0,
    },
    {
        'id': 'tip_codex_interactive_spoiler_slider_progress',
        'engine': 'codex_export',
        'feature': 'Interactive Spoiler Slider',
        'subfeature': 'spoiler_slider',
        'category': 'utility',
        'pillar': 'society_systems',
        'title': 'Codex Spoiler Slider: Reader-Controlled Lore Disclosure',
        'content': 'When exporting your World Bible to offline HTML codex, the interactive spoiler slider allows readers to set their current reading progress (e.g. Chapter 12). Lore entries, character allegiances, and secret identities reveal dynamically without spoiling future chapters.',
        'rationale': 'Enables safe sharing of rich world lore wikis with beta readers and book clubs.',
        'example': 'arcanum codex Worlds/Aethelgard --html --with-spoiler-slider',
        'tags': ['codex', 'wiki', 'spoiler-slider', 'beta-readers', 'worldbuilding'],
        'contexts': ['worldbuilding', 'export', 'cli'],
        'depth': 'advanced',
        'weight': 1.1,
    },
    {
        'id': 'tip_omnibus_interstitial_recap_generator',
        'engine': 'omnibus',
        'feature': 'Cross-Book Interstitial Recap Generator',
        'subfeature': 'interstitial_recaps',
        'category': 'utility',
        'pillar': 'narrative_chronology',
        'title': "Interstitial Recaps: Automated 'Story So Far' Summaries Between Books",
        'content': "When compiling multi-volume series into an omnibus edition, the omnibus engine extracts chapter plot tags and climax consequences to scaffold concise 'The Story So Far' recap interstitials between books.",
        'rationale': 'Enhances reader orientation across lengthy multi-volume reading experiences.',
        'example': 'arcanum omnibus Universes/Cosmos --with-recaps',
        'tags': ['omnibus', 'recaps', 'series', 'compilation', 'publishing'],
        'contexts': ['publishing', 'export', 'cli'],
        'depth': 'advanced',
        'weight': 1.0,
    },
    {
        'id': 'tip_resonance_knowledge_mesh_visualizer_graph',
        'engine': 'resonance',
        'feature': 'Knowledge Mesh Visualizer',
        'subfeature': 'mesh_visualization',
        'category': 'craft',
        'pillar': 'cosmology_physics',
        'title': 'Knowledge Mesh: Visualizing High-Dimensional Cross-Domain Synergies',
        'content': 'The Universal Resonance Mesh connects all 51 engines into an interconnected knowledge graph. Visualizing the mesh reveals how astrophysics orbits dictate calendar festivals, which dictate agricultural harvest cycles, which govern military campaign timing.',
        'rationale': 'Exposes emergent systemic relationships across seemingly isolated worldbuilding domains.',
        'example': 'arcanum resonance mesh',
        'tags': ['resonance', 'knowledge-mesh', 'graph', 'synergy', 'worldbuilding'],
        'contexts': ['worldbuilding', 'studio', 'cli'],
        'depth': 'masterclass',
        'weight': 1.3,
    },
    {
        'id': 'tip_resonance_cross_domain_coherence_auditor',
        'engine': 'resonance',
        'feature': 'Cross-Domain Coherence Audit',
        'subfeature': 'cross_domain_audit',
        'category': 'craft',
        'pillar': 'cosmology_physics',
        'title': 'Cross-Domain Coherence Audit: Detecting Inter-System Contradictions',
        'content': "Run 'arcanum resonance audit' to scan your entire world lore vault for cross-domain contradictions (e.g. an equatorial low-elevation city described as having arctic blizzards without orographic rain shadows or magic system anchors).",
        'rationale': 'Provides holistic automated consistency checks across the entire worldbuilding ecosystem.',
        'example': 'arcanum resonance audit',
        'tags': ['resonance', 'coherence', 'audit', 'contradictions', 'consistency', 'cross-domain-coherence-audit'],
        'contexts': ['worldbuilding', 'review', 'cli'],
        'depth': 'masterclass',
        'weight': 1.2,
    },
    {
        'id': 'tip_climate_koppen_classification_ecotones',
        'engine': 'climate',
        'feature': 'Köppen Classifier',
        'subfeature': 'koppen_classifier',
        'category': 'craft',
        'pillar': 'cosmology_physics',
        'title': 'Köppen Climate Boundaries: Biome Ecotones as Natural Frontiers',
        'content': 'Use Köppen temperature and precipitation thresholds (e.g. Cs Mediterranean dry-summer vs Cw monsoonal winter-dry) to establish organic cultural frontiers and agricultural zones. Civilizations rarely wage offensive campaigns across sharply divergent climate envelopes.',
        'rationale': 'Köppen boundaries (hottest month > 10°C for arboriculture, coldest month > -3°C for temperate frost resistance) dictate draft animal survival, logistics, and harvest rhythms.',
        'example': 'arcanum calc climate --koppen-classify',
        'tags': ['climate', 'koppen', 'koppen-classifier', 'biomes', 'ecotones', 'agriculture', 'borders'],
        'contexts': ['worldbuilding', 'cli', 'studio'],
        'depth': 'masterclass',
        'weight': 1.1,
    },
    {
        'id': 'tip_cartography_hydrology_drainage_gradient',
        'engine': 'cartography',
        'feature': 'Hydrology Drainage Sweep',
        'subfeature': 'hydrology_drainage_sweep',
        'category': 'craft',
        'pillar': 'cosmology_physics',
        'title': 'Hydrology Drainage: Rivers Converge Downhill and Never Bifurcate',
        'content': 'Water strictly follows the steepest topological descent gradient. Rivers continuously coalesce into larger trunk waterways; they never split downstream except in flat sediment-choked ocean deltas. Inland lakes without ocean outlets become hyper-saline dead seas.',
        'rationale': 'Gravitational potential minimization dictates dendritic drainage networks, preventing geologically impossible river bifurcations.',
        'example': 'arcanum map Worlds/Aethelgard --audit-drainage',
        'tags': ['cartography', 'hydrology', 'drainage', 'rivers', 'endorheic', 'topography', 'hydrology-drainage-sweep'],
        'contexts': ['worldbuilding', 'cli', 'studio'],
        'depth': 'advanced',
        'weight': 1.1,
    },
    {
        'id': 'tip_structure_multi_paradigm_beat_mapping',
        'engine': 'structure',
        'feature': 'Multi-Paradigm Beat Mapper',
        'subfeature': 'multi_paradigm_beat_mapper',
        'category': 'craft',
        'pillar': 'editorial_craft',
        'title': 'Multi-Paradigm Beat Mapping: Cross-Validating Narrative Momentum',
        'content': 'Cross-validate your chapter progression across 9 structural paradigms (Three-Act, Hero\'s Journey, Dan Harmon Story Circle, Kishōtenketsu, Fichtean Curve, Save the Cat). A beat that functions as the Midpoint Shift in Three-Act should align with the Ten (Twist) in Kishōtenketsu.',
        'rationale': 'Comparative paradigm analysis exposes hidden pacing dead-zones that single-framework outlines obscure.',
        'example': 'arcanum audit structure Manuscript/ --paradigm harmonize',
        'tags': ['structure', 'beats', 'paradigm', 'harmonize', 'kishotenketsu', 'midpoint', 'multi-paradigm-beat-mapper'],
        'contexts': ['drafting', 'review', 'cli', 'studio'],
        'depth': 'masterclass',
        'weight': 1.2,
    },
    {
        'id': 'tip_plot_matrix_subplot_progression_grid',
        'engine': 'plot_matrix',
        'feature': 'Subplot Progression Grid',
        'subfeature': 'subplot_progression_grid',
        'category': 'craft',
        'pillar': 'editorial_craft',
        'title': 'Subplot Progression Grid: Alternating Primary and Secondary Stakes',
        'content': 'Map subplots onto a progression matrix ensuring no chapter advances the main external plot without also triggering a shift in at least one internal or romantic subplot. When the main quest stalls, secondary subplots must accelerate to preserve narrative forward momentum.',
        'rationale': 'Multi-threaded narrative density maintains reader engagement during necessary external plot transitions.',
        'example': 'arcanum plot Manuscript/ --subplots',
        'tags': ['plot-matrix', 'subplots', 'braiding', 'pacing', 'character-arc', 'subplot-progression-grid'],
        'contexts': ['drafting', 'review', 'cli', 'studio'],
        'depth': 'advanced',
        'weight': 1.1,
    },
    {
        'id': 'tip_prophecy_clause_fulfillment_matrix',
        'engine': 'prophecy',
        'feature': 'Clause Fulfillment Matrix',
        'subfeature': 'clause_fulfillment_matrix',
        'category': 'craft',
        'pillar': 'narrative_chronology',
        'title': 'Clause Fulfillment Matrix: Deconstructing Oracles into Atomic Conditions',
        'content': 'Deconstruct Delphic prophecies into a boolean matrix of atomic clauses with distinct fulfiller IDs and condition triggers. Have antagonists fulfill prerequisite clauses in unexpected literal ways while believing they are actively averting them.',
        'rationale': 'Atomic condition decomposition prevents narrative plotholes and generates genuine dramatic irony rather than arbitrary authorial contrivance.',
        'example': 'arcanum prophecy Worlds/Aethelgard --matrix',
        'tags': ['prophecy', 'clause-fulfillment', 'delphic', 'dramatic-irony', 'conditions', 'clause-fulfillment-matrix'],
        'contexts': ['worldbuilding', 'plot', 'cli'],
        'depth': 'masterclass',
        'weight': 1.2,
    },
    {
        'id': 'tip_genealogy_mermaid_tree_export',
        'engine': 'genealogy',
        'feature': 'Mermaid Tree Exporter',
        'subfeature': 'mermaid_tree_exporter',
        'category': 'craft',
        'pillar': 'society_systems',
        'title': 'Mermaid Lineage Trees: Visualizing Dynastic Loops and Morganatic Branches',
        'content': 'Compile royal family trees directly into Mermaid flowcharts (`graph TD`) to visually detect incestuous consolidation loops, disputed cadet branches, and morganatic succession crises in your world codex without external graphics software.',
        'rationale': 'Graph-theoretic lineage representation converts complex tabular genealogies into instant visual pedigree charts with 100% offline rendering.',
        'example': 'arcanum genealogy HouseValerius --mermaid',
        'tags': ['genealogy', 'mermaid', 'pedigree', 'lineage', 'dynasty', 'succession', 'mermaid-tree-exporter'],
        'contexts': ['worldbuilding', 'cli', 'studio'],
        'depth': 'advanced',
        'weight': 1.1,
    },
    {
        'id': 'tip_economy_commodity_price_distance_friction',
        'engine': 'economy',
        'feature': 'Commodity Price Calculator',
        'subfeature': 'commodity_price_calculator',
        'category': 'craft',
        'pillar': 'society_systems',
        'title': 'Commodity Pricing: Distance Friction and Inelastic Food Staples',
        'content': 'Grain and salt possess strictly inelastic demand; transporting them by overland ox cart adds ~0.5% cost per mile, making long-distance overland grain trade unprofitable compared to coastal shipping. Use localized grain price shocks to motivate mercenary desertions and border skirmishes.',
        'rationale': 'Caloric transport friction governs pre-industrial macroeconomic boundaries and realistic trade logistics.',
        'example': 'arcanum economy Worlds/Aethelgard --commodity grain --distance 120',
        'tags': ['economy', 'commodity-prices', 'freight', 'trade', 'logistics', 'inflation', 'commodity-price-calculator'],
        'contexts': ['worldbuilding', 'cli'],
        'depth': 'masterclass',
        'weight': 1.1,
    },
    {
        'id': 'tip_typography_smart_quotes_and_primes',
        'engine': 'typography_cleaner',
        'feature': 'Smart Quotes Normalizer',
        'subfeature': 'smart_quotes_normalizer',
        'category': 'craft',
        'pillar': 'editorial_craft',
        'title': 'Smart Quotes vs Primes: Handling Leading Dialogue Elisions and Measurements',
        'content': 'Never let automated typographers turn leading-elision apostrophes (e.g. ’em, ’round, ’cause) into opening single quotes (‘). Use the smart quotes normalizer to preserve right curly apostrophes (U+2019) in contractions and straight primes (′/″) for coordinates and heights.',
        'rationale': 'Standard automated typography algorithms misinterpret leading apostrophes as opening quotes, violating publishing industry typesetting rules.',
        'example': 'arcanum audit quotes Manuscript/ --normalize',
        'tags': ['typography', 'smart-quotes', 'primes', 'typesetting', 'shunn', 'elision', 'smart-quotes-normalizer'],
        'contexts': ['publishing', 'review', 'cli'],
        'depth': 'advanced',
        'weight': 1.0,
    },
    {
        'id': 'tip_zen_studio_in_situ_lore_drawer_retrieval',
        'engine': 'zen_studio',
        'feature': 'In-Situ Lore Drawer',
        'subfeature': 'in_situ_lore_drawer',
        'category': 'utility',
        'pillar': 'manuscript_drafting',
        'title': 'In-Situ Lore Drawer: Zero-Distraction Entity Verification While Drafting',
        'content': 'Use Zen Studio\'s slide-out lore drawer (`📜 Lore Vault`) to instantly search character eye colors, weapon weights, and world rules directly beside your editor without opening external browser windows or breaking flow state.',
        'rationale': 'Eliminates context-switching cognitive penalty during high-velocity prose drafting sprints.',
        'example': 'arcanum zen Manuscript/ --lore Worlds/Aethelgard',
        'tags': ['zen-studio', 'lore-drawer', 'in-situ', 'drafting', 'flow-state', 'in-situ-lore-drawer'],
        'contexts': ['drafting', 'studio'],
        'depth': 'intermediate',
        'weight': 1.1,
    },
    {
        'id': 'tip_migrate_vault_schema_upgrader_ast',
        'engine': 'migrate',
        'feature': 'Vault Schema Upgrader',
        'subfeature': 'vault_schema_upgrader',
        'category': 'core',
        'pillar': 'system_ops',
        'title': 'Vault Schema Upgrader: Safe AST-Level Migration of Legacy Frontmatter',
        'content': 'When upgrading world lore repositories to new Ars Arcanum schema specifications, the schema upgrader parses frontmatter AST trees without touching prose body text or destroying custom markdown formatting.',
        'rationale': 'AST-level transformation guarantees byte-accurate preservation of prose while standardizing deprecated metadata tags.',
        'example': 'arcanum migrate Worlds/Aethelgard --schema v2.0',
        'tags': ['migrate', 'schema-upgrader', 'ast', 'frontmatter', 'vault', 'vault-schema-upgrader'],
        'contexts': ['safety', 'cli'],
        'depth': 'advanced',
        'weight': 1.0,
    },
    {
        'id': 'tip_resonance_multi_hop_conceptual_bridge',
        'engine': 'resonance',
        'feature': 'Multi-Hop Conceptual Bridge',
        'subfeature': 'multi_hop_conceptual_bridge',
        'category': 'craft',
        'pillar': 'cosmology_physics',
        'title': 'Multi-Hop Conceptual Bridge: Connecting Astrophysics to Character Voice',
        'content': 'Use multi-hop resonance bridging (`arcanum resonance bridge astrophysics voice`) to discover surprising thematic connective chains: orbital eccentricity -> severe seasonal starvation -> cultural idioms of hoarding -> characters speaking with sharp culinary metaphors.',
        'rationale': 'Breadth-first search over the 51-engine knowledge mesh uncovers deep causal chains linking physical world parameters to intimate character dialogue.',
        'example': 'arcanum resonance bridge astrophysics voice',
        'tags': ['resonance', 'conceptual-bridge', 'multi-hop', 'synergy', 'theme', 'voice', 'multi-hop-conceptual-bridge'],
        'contexts': ['worldbuilding', 'drafting', 'cli'],
        'depth': 'masterclass',
        'weight': 1.2,
    },
    {
        'id': 'tip_tips_contextual_relevance_filter',
        'engine': 'tips',
        'feature': 'Contextual Relevance Filter',
        'subfeature': 'contextual_relevance_filter',
        'category': 'core',
        'pillar': 'editorial_craft',
        'title': 'Contextual Tip Targeting: Pinpoint Specific Engine & Subfeature Craft Guidance',
        'content': 'Target tip retrieval directly to your current creative task (`arcanum tip <engine> --subfeature "<subfeature>"`) to surface deep mathematical formulas, narrative edge cases, and workflow shortcuts tailored precisely to the file or chapter you are editing.',
        'rationale': 'Multi-criteria token scoring matches exact craft domains, eliminating irrelevant generalities and surfacing actionable domain wisdom.',
        'example': 'arcanum tip pacing --subfeature "Fitts Tension Curves"',
        'tags': ['tips', 'contextual-filter', 'subfeature', 'workflow', 'discovery', 'contextual-relevance-filter'],
        'contexts': ['cli', 'drafting', 'worldbuilding'],
        'depth': 'advanced',
        'weight': 1.1,
    },
    {
        'id': 'tip_tips_non_obvious_masterclass_database',
        'engine': 'tips',
        'feature': 'Non-Obvious Masterclass Database',
        'subfeature': 'non_obvious_masterclass_database',
        'category': 'craft',
        'pillar': 'editorial_craft',
        'title': 'Masterclass Depth Filter: Surfacing Non-Obvious Narrative Mechanics',
        'content': 'Use `arcanum tip --depth masterclass` to bypass beginner advice and exclusively explore high-altitude dramaturgical principles, astrophysics orbital invariants, and macroeconomic monetary models.',
        'rationale': 'Filters database queries to the highest tier of craft rigor and structural depth.',
        'example': 'arcanum tip --depth masterclass',
        'tags': ['tips', 'masterclass', 'depth', 'craft', 'rigor', 'non-obvious-masterclass-database'],
        'contexts': ['cli', 'worldbuilding', 'review'],
        'depth': 'masterclass',
        'weight': 1.2,
    },
    {
        'id': 'tip_tips_zero_stall_history_cycling',
        'engine': 'tips',
        'feature': 'Zero-Stall History Cycling',
        'subfeature': 'zero_stall_history_cycling',
        'category': 'core',
        'pillar': 'system_ops',
        'title': 'Zero-Stall History Cycling: Continuous Novel Insights Without Repetition',
        'content': 'The tip retrieval engine tracks session history via set differencing. Repeated queries or draft drawer rolls cycle through distinct craft hints before automatically refreshing the pool once exhausted.',
        'rationale': 'Guarantees variety across long writing sessions and eliminates tip fatigue.',
        'example': 'arcanum tip --cycle',
        'tags': ['tips', 'history-cycling', 'rotation', 'lru', 'zero-stall-history-cycling'],
        'contexts': ['cli', 'studio', 'drafting'],
        'depth': 'intermediate',
        'weight': 1.0,
    },
    {
        'id': 'tip_tips_sovereign_display_configuration',
        'engine': 'tips',
        'feature': 'Sovereign Display Configuration',
        'subfeature': 'sovereign_display_configuration',
        'category': 'utility',
        'pillar': 'system_ops',
        'title': 'Sovereign Tip Control: Distraction-Free Toggle & Preference Persistence',
        'content': 'Toggle ambient tips on or off at will using `arcanum tip --disable` or `arcanum tip --enable`. Your preference is persistently recorded in `config.json` without touching project lore or manuscript files.',
        'rationale': 'Upholds absolute authorial sovereignty and customizable workflow ergonomics.',
        'example': 'arcanum tip --disable && arcanum tip --status',
        'tags': ['tips', 'config', 'sovereignty', 'toggle', 'preferences', 'sovereign-display-configuration'],
        'contexts': ['cli', 'system', 'preferences'],
        'depth': 'intermediate',
        'weight': 1.0,
    },
    {
        'id': 'tip_tips_cross_platform_ambient_presentation',
        'engine': 'tips',
        'feature': 'Cross-Platform Ambient Presentation',
        'subfeature': 'cross_platform_ambient_presentation',
        'category': 'utility',
        'pillar': 'manuscript_drafting',
        'title': 'Ambient Multi-Surface Presentation: Tips in CLI, Studio Hub & Zen Studio',
        'content': 'Tips are non-intrusively embedded across all surfaces: CLI terminal execution footers, Studio Hub top banner badges, and Zen Studio slide-out craft wisdom drawers.',
        'rationale': 'Delivers insights ambiently at the moment of action across both terminal and GUI workflows without blocking UI interactions.',
        'example': 'arcanum zen Manuscript/ --lore Worlds/Aethelgard',
        'tags': ['tips', 'ambient-presentation', 'studio-hub', 'zen-studio', 'cli', 'cross-platform-ambient-presentation'],
        'contexts': ['studio', 'drafting', 'cli'],
        'depth': 'intermediate',
        'weight': 1.0,
    },
]


# =============================================================================
# ENGINE ALIAS MAP
# =============================================================================

ENGINE_ALIASES: dict[str, str] = {
    "astro": "astrophysics",
    "astrophysics": "astrophysics",
    "orbital": "astrophysics",
    "orbits": "astrophysics",
    "transit": "astrophysics",
    "brachistochrone": "astrophysics",
    "climate": "climate",
    "biomes": "climate",
    "weather": "climate",
    "koppen": "climate",
    "calendar": "calendar",
    "calendars": "calendar",
    "lunar": "calendar",
    "moons": "calendar",
    "ecology": "ecology",
    "trophic": "ecology",
    "foodweb": "ecology",
    "bestiary": "ecology",
    "creatures": "ecology",
    "map": "cartography",
    "maps": "cartography",
    "cartography": "cartography",
    "voronoi": "cartography",
    "hydrology": "cartography",
    "journey": "journey",
    "travel": "journey",
    "march": "journey",
    "logistics": "journey",
    "structure": "structure",
    "paradigm": "structure",
    "beats": "structure",
    "story-circle": "structure",
    "scene": "scene_mechanics",
    "scenes": "scene_mechanics",
    "scene-mechanics": "scene_mechanics",
    "scene_mechanics": "scene_mechanics",
    "mru": "scene_mechanics",
    "pacing": "pacing",
    "rhythm": "pacing",
    "waveform": "pacing",
    "plot": "plot_matrix",
    "plots": "plot_matrix",
    "plot-matrix": "plot_matrix",
    "plot_matrix": "plot_matrix",
    "chekhov": "plot_matrix",
    "graph": "branching_graph",
    "branching": "branching_graph",
    "branching-graph": "branching_graph",
    "branching_graph": "branching_graph",
    "dag": "branching_graph",
    "subway": "branching_graph",
    "canvas": "story_canvas",
    "story-canvas": "story_canvas",
    "story_canvas": "story_canvas",
    "corkboard": "story_canvas",
    "causality": "causality",
    "paradox": "causality",
    "time-travel": "causality",
    "timeline": "timeline_sync",
    "timeline-sync": "timeline_sync",
    "timeline_sync": "timeline_sync",
    "anachrony": "timeline_sync",
    "bilocation": "timeline_sync",
    "prophecy": "prophecy",
    "oracle": "prophecy",
    "oracles": "prophecy",
    "sprint": "writing_sprint",
    "writing-sprint": "writing_sprint",
    "writing_sprint": "writing_sprint",
    "wpm": "writing_sprint",
    "cast": "dramatis_personae",
    "dramatis": "dramatis_personae",
    "dramatis-personae": "dramatis_personae",
    "dramatis_personae": "dramatis_personae",
    "characters": "dramatis_personae",
    "character": "dramatis_personae",
    "voice": "voice",
    "idiolect": "voice",
    "dialogue-voice": "voice",
    "conlang": "conlang",
    "linguistics": "conlang",
    "language": "conlang",
    "phonology": "conlang",
    "genealogy": "genealogy",
    "lineage": "genealogy",
    "dynasty": "genealogy",
    "succession": "genealogy",
    "pedigree": "genealogy",
    "faction": "factions",
    "factions": "factions",
    "diplomacy": "factions",
    "alliances": "factions",
    "economy": "economy",
    "currency": "economy",
    "money": "economy",
    "commodities": "economy",
    "sim": "tactical_sim",
    "battle": "tactical_sim",
    "tactical": "tactical_sim",
    "tactical-sim": "tactical_sim",
    "tactical_sim": "tactical_sim",
    "combat": "tactical_sim",
    "magic": "magic_system",
    "magic-system": "magic_system",
    "magic_system": "magic_system",
    "arcane": "magic_system",
    "spells": "magic_system",
    "stylistics": "stylistics",
    "style": "stylistics",
    "readability": "stylistics",
    "echoes": "stylistics",
    "senses": "senses",
    "sensory": "senses",
    "atmosphere": "senses",
    "continuity": "continuity",
    "consistency": "continuity",
    "series": "series_continuity",
    "series-continuity": "series_continuity",
    "series_continuity": "series_continuity",
    "typography": "typography_cleaner",
    "typography-cleaner": "typography_cleaner",
    "typography_cleaner": "typography_cleaner",
    "quotes": "typography_cleaner",
    "smartquotes": "typography_cleaner",
    "diff": "manuscript_diff",
    "manuscript-diff": "manuscript_diff",
    "manuscript_diff": "manuscript_diff",
    "redline": "manuscript_diff",
    "heatmap": "revision_heatmap",
    "revision-heatmap": "revision_heatmap",
    "revision_heatmap": "revision_heatmap",
    "churn": "revision_heatmap",
    "hub": "studio_hub",
    "studio-hub": "studio_hub",
    "studio_hub": "studio_hub",
    "studio": "studio_hub",
    "zen": "zen_studio",
    "zen-studio": "zen_studio",
    "zen_studio": "zen_studio",
    "ambient": "ambient",
    "audio": "ambient",
    "soundscape": "ambient",
    "binaural": "ambient",
    "portfolio": "portfolio",
    "catalog": "portfolio",
    "analytics": "portfolio",
    "rag": "local_rag",
    "local-rag": "local_rag",
    "local_rag": "local_rag",
    "semantic": "local_rag",
    "fts5": "local_rag",
    "corpus": "corpus_export",
    "corpus-export": "corpus_export",
    "corpus_export": "corpus_export",
    "export-corpus": "corpus_export",
    "import": "importer",
    "importer": "importer",
    "scrivener": "importer",
    "docx": "docx_sync",
    "docx-sync": "docx_sync",
    "docx_sync": "docx_sync",
    "word": "docx_sync",
    "world-doctor": "world_doctor",
    "world_doctor": "world_doctor",
    "doctor-world": "world_doctor",
    "doctor": "diagnostics",
    "diagnostics": "diagnostics",
    "health": "diagnostics",
    "config": "config",
    "preferences": "config",
    "settings": "config",
    "cache": "cache",
    "mtime": "cache",
    "fs": "fs_utils",
    "fs-utils": "fs_utils",
    "fs_utils": "fs_utils",
    "atomic": "fs_utils",
    "migrate": "migrate",
    "migration": "migrate",
    "upgrade": "migrate",
    "preflight": "preflight",
    "pre-flight": "preflight",
    "prepress": "preflight",
    "matter": "frontmatter_builder",
    "frontmatter": "frontmatter_builder",
    "frontmatter-builder": "frontmatter_builder",
    "frontmatter_builder": "frontmatter_builder",
    "concordance": "concordance",
    "glossary": "concordance",
    "index": "concordance",
    "codex": "codex_export",
    "codex-export": "codex_export",
    "codex_export": "codex_export",
    "wiki": "codex_export",
    "omnibus": "omnibus",
    "series-omnibus": "omnibus",
    "resonance": "resonance",
    "mesh": "resonance",
    "cascade": "resonance",
    "spark": "resonance",
    "bridge": "resonance",
    "synergy": "resonance",
    "tip": "tips",
    "tips": "tips",
    "craft-tips": "tips",
    "advice": "tips",
    "hint": "tips",
    "hints": "tips",
    "wisdom": "tips",
}


def _norm_str(s: str) -> str:
    import unicodedata
    n = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in n if c.isalnum())


def _toks_str(s: str) -> set[str]:
    import unicodedata
    n = unicodedata.normalize("NFD", s.lower())
    clean = "".join(c if c.isalnum() else " " for c in n)
    return {w for w in clean.split() if len(w) > 2}


# =============================================================================
# TIP DATABASE & RETRIEVAL ENGINE CLASS
# =============================================================================


class TipDatabase:
    """Intelligent retrieval and ranking engine for Ars Arcanum craft tips."""

    def __init__(self, raw_tips: list[dict[str, Any]] | None = None) -> None:
        raw = raw_tips if raw_tips is not None else _RAW_TIPS
        self._tips: list[Tip] = [Tip.from_dict(t) for t in raw]
        self._by_id: dict[str, Tip] = {t.id: t for t in self._tips}
        self._by_engine: dict[str, list[Tip]] = {}
        self._by_category: dict[str, list[Tip]] = {}
        self._by_pillar: dict[str, list[Tip]] = {}
        self._by_context: dict[str, list[Tip]] = {}

        for t in self._tips:
            eng = t.engine.lower().strip()
            self._by_engine.setdefault(eng, []).append(t)
            cat = t.category.value
            self._by_category.setdefault(cat, []).append(t)
            pil = t.pillar.value
            self._by_pillar.setdefault(pil, []).append(t)
            for ctx in t.contexts:
                self._by_context.setdefault(ctx.lower().strip(), []).append(t)

        self._history_seen: set[str] = set()

    def __len__(self) -> int:
        return len(self._tips)

    def resolve_engine(self, name_or_alias: str) -> str | None:
        """Resolves an engine name, alias, or command string to canonical engine name."""
        if not name_or_alias:
            return None
        clean = name_or_alias.lower().strip().replace(" ", "-").replace("_", "-")
        if clean in self._by_engine:
            return clean
        clean_under = clean.replace("-", "_")
        if clean_under in self._by_engine:
            return clean_under
        if clean in ENGINE_ALIASES:
            return ENGINE_ALIASES[clean]
        if clean_under in ENGINE_ALIASES:
            return ENGINE_ALIASES[clean_under]
        # Check close matches
        all_canonical = list(self._by_engine.keys())
        matches = difflib.get_close_matches(clean, all_canonical, n=1, cutoff=0.6)
        if matches:
            return matches[0]
        alias_matches = difflib.get_close_matches(clean, list(ENGINE_ALIASES.keys()), n=1, cutoff=0.6)
        if alias_matches:
            return ENGINE_ALIASES[alias_matches[0]]
        return None

    def get_all(self) -> list[Tip]:
        """Returns all registered tips."""
        return list(self._tips)

    def get_by_id(self, tip_id: str) -> Tip | None:
        """Looks up a tip by exact unique ID."""
        return self._by_id.get(tip_id.strip())

    def get_by_engine(self, engine: str, subfeature: str | None = None) -> list[Tip]:
        """Returns all tips associated with an engine, optionally filtered by subfeature."""
        canonical = self.resolve_engine(engine)
        clean_eng = canonical if canonical else engine.lower().strip()
        tips = self._by_engine.get(clean_eng, [])
        if not tips:
            for k, v in self._by_engine.items():
                if clean_eng in k or k in clean_eng:
                    tips = v
                    break

        if not tips:
            return []

        if not subfeature or not subfeature.strip():
            return list(tips)

        # Multi-criteria subfeature relevance scoring
        q_norm = _norm_str(subfeature)
        q_toks = _toks_str(subfeature)
        scored: list[tuple[float, Tip]] = []

        for t in tips:
            score = 0.0
            t_sub_norm = _norm_str(t.subfeature)
            t_feat_norm = _norm_str(t.feature)
            t_title_norm = _norm_str(t.title)

            if q_norm == t_sub_norm:
                score += 50.0
            elif q_norm == t_feat_norm:
                score += 40.0
            elif q_norm and (q_norm in t_sub_norm or t_sub_norm in q_norm):
                score += 30.0
            elif q_norm and (q_norm in t_feat_norm or t_feat_norm in q_norm):
                score += 25.0

            for tag in t.tags:
                tag_norm = _norm_str(tag)
                if tag_norm == q_norm:
                    score += 35.0
                elif tag_norm and (tag_norm in q_norm or q_norm in tag_norm):
                    score += 20.0

            searchable_toks = _toks_str(f"{t.subfeature} {t.feature} {t.title} {' '.join(t.tags)}")
            overlap = len(q_toks & searchable_toks)
            score += overlap * 6.0

            if q_norm and q_norm in t_title_norm:
                score += 15.0

            if score > 0.0:
                scored.append((score * t.weight, t))

        if scored:
            scored.sort(key=lambda x: x[0], reverse=True)
            top_score = scored[0][0]
            if top_score >= 30.0:
                return [t for s, t in scored if s >= 0.5 * top_score]
            return [t for _, t in scored]

        return list(tips)

    def get_by_context(self, context: str) -> list[Tip]:
        """Returns tips relevant to a workflow context (e.g. drafting, worldbuilding, review)."""
        clean_ctx = context.lower().strip()
        return list(self._by_context.get(clean_ctx, []))

    def search(self, query: str, limit: int = 10) -> list[Tip]:
        """Searches tips across title, content, rationale, tags, and subfeature names."""
        if not query or not query.strip():
            return self._tips[:limit]

        terms = [t.lower() for t in query.strip().split() if len(t) > 1]
        if not terms:
            terms = [query.lower().strip()]

        scored: list[tuple[float, Tip]] = []
        for t in self._tips:
            score = 0.0
            searchable_text = f"{t.title} {t.content} {t.rationale} {t.engine} {t.feature} {t.subfeature} {' '.join(t.tags)}".lower()

            # Exact phrase bonus
            if query.lower() in searchable_text:
                score += 12.0

            # Individual term matches
            for term in terms:
                if term in t.title.lower():
                    score += 5.0
                if term in t.tags:
                    score += 4.0
                if term in t.engine.lower():
                    score += 4.0
                if term in t.subfeature.lower():
                    score += 3.0
                if term in t.content.lower():
                    score += 2.0
                if term in t.rationale.lower():
                    score += 1.0

            if score > 0.0:
                scored.append((score * t.weight, t))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [t for _, t in scored[:limit]]

    def get_contextual_tip(
        self,
        engine: str | None = None,
        feature: str | None = None,
        subfeature: str | None = None,
        context: str | None = None,
        query: str | None = None,
        exclude_seen: bool = True,
    ) -> Tip | None:
        """Intelligently retrieves the best-matching, non-obvious tip for current user context."""
        candidates: list[Tip] = []

        # 1. Targeted engine + subfeature query
        if engine:
            candidates = self.get_by_engine(engine, subfeature or feature)

        # 2. Query search if engine didn't yield exact match or freeform query given
        if not candidates and query:
            candidates = self.search(query, limit=15)

        # 3. Contextual fallback (e.g. drafting, worldbuilding)
        if not candidates and context:
            candidates = self.get_by_context(context)

        # 4. Universal fallback
        if not candidates:
            candidates = list(self._tips)

        # Filter out seen if requested and we have un-seen remaining
        if exclude_seen and len(candidates) > 1:
            unseen = [t for t in candidates if t.id not in self._history_seen]
            if unseen:
                candidates = unseen
            else:
                # Reset history for this set if exhausted
                candidate_ids = {t.id for t in candidates}
                self._history_seen.difference_update(candidate_ids)

        if not candidates:
            return None

        # Weighted selection among top candidates
        weights = [t.weight for t in candidates]
        chosen = random.choices(candidates, weights=weights, k=1)[0]
        self._history_seen.add(chosen.id)
        return chosen

    def get_engines(self) -> list[str]:
        """Returns sorted list of all unique engines represented in tips database."""
        return sorted(self._by_engine.keys())

    def get_categories(self) -> list[str]:
        """Returns list of unique categories."""
        return [c.value for c in TipCategory]

    def get_pillars(self) -> list[str]:
        """Returns list of unique pillars."""
        return [p.value for p in TipPillar]


# Global default database instance
_GLOBAL_DB: TipDatabase | None = None


def get_tip_database() -> TipDatabase:
    """Returns the global shared TipDatabase singleton instance."""
    global _GLOBAL_DB
    if _GLOBAL_DB is None:
        _GLOBAL_DB = TipDatabase()
    return _GLOBAL_DB


# =============================================================================
# USER PREFERENCE & CONFIGURATION INTEGRATION
# =============================================================================


def are_tips_enabled() -> bool:
    """Checks if dynamic tips are enabled in user configuration (default: True)."""
    try:
        cfg = load_config()
        return bool(cfg.get("tips_enabled", True))
    except Exception as e:
        logger.debug("Failed reading tips_enabled config: %s", e)
        return True


def set_tips_enabled(enabled: bool) -> bool:
    """Persists user tips preference to configuration (~/.config/ars-arcanum/config.json)."""
    try:
        cfg = load_config()
        cfg["tips_enabled"] = bool(enabled)
        return save_config(cfg)
    except Exception as e:
        logger.error("Failed saving tips_enabled config: %s", e)
        return False


def toggle_tips() -> bool:
    """Toggles dynamic tips enabled state and returns the new state."""
    new_state = not are_tips_enabled()
    set_tips_enabled(new_state)
    return new_state


# =============================================================================
# FORMATTING & PRESENTATION HELPERS
# =============================================================================


def format_cli_tip(tip: Tip, verbose: bool = False) -> str:
    """Formats a tip cleanly for command-line presentation."""
    border = "─" * 78
    lines = [
        border,
        f"💡 \033[1;33mARS ARCANUM CRAFT WISDOM\033[0m: \033[1m{tip.title}\033[0m",
        f"   [\033[36m{tip.engine.upper()}\033[0m • \033[35m{tip.subfeature}\033[0m • \033[32m{tip.depth.value.capitalize()}\033[0m]",
        "",
        f"   {tip.content}",
    ]
    if verbose and tip.rationale:
        lines.append(f"\n   ⚙️  \033[2mRationale:\033[0m {tip.rationale}")
    if tip.example:
        lines.append(f"\n   ⚡ \033[2mExample:\033[0m {tip.example}")
    lines.append(border)
    return "\n".join(lines)


def format_short_tip(tip: Tip) -> str:
    """Formats a 1-line compact tip for statusbars and minimal footers."""
    return f"💡 [{tip.engine.upper()} / {tip.subfeature}]: {tip.title} — {tip.content}"


# =============================================================================
# CLI DISPATCHER & MAIN ENTRYPOINT
# =============================================================================


def main(argv: list[str] | None = None) -> int:
    """CLI handler for 'arcanum tip' and standalone tips management."""
    parser = argparse.ArgumentParser(
        description="Ars Arcanum Dynamic Craft Tip & Wisdom Engine"
    )
    parser.add_argument(
        "query_pos",
        nargs="?",
        default="",
        help="Optional search query or engine name",
    )
    parser.add_argument(
        "--engine",
        "-e",
        help="Target engine name (e.g. astrophysics, climate, pacing, conlang)",
    )
    parser.add_argument(
        "--feature",
        "-f",
        help="Specific subfeature or capability",
    )
    parser.add_argument(
        "--context",
        "-c",
        help="Workflow context (drafting, worldbuilding, review, publishing, export)",
    )
    parser.add_argument(
        "--query",
        "-q",
        help="Search query across tip database",
    )
    parser.add_argument(
        "--all",
        "-a",
        action="store_true",
        help="List all tips matching filters",
    )
    parser.add_argument(
        "--json",
        "-j",
        action="store_true",
        help="Output raw JSON format",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed scientific/structural rationale",
    )
    parser.add_argument(
        "--enable",
        action="store_true",
        help="Enable dynamic tip display in user configuration",
    )
    parser.add_argument(
        "--disable",
        action="store_true",
        help="Disable dynamic tip display in user configuration",
    )
    parser.add_argument(
        "--toggle",
        action="store_true",
        help="Toggle dynamic tip display enabled state",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show whether tips are enabled in config",
    )
    parser.add_argument(
        "--list-engines",
        action="store_true",
        help="List all engines with registered tips",
    )

    args = parser.parse_args(argv)
    db = get_tip_database()

    # Preference modification subcommands
    if args.enable:
        set_tips_enabled(True)
        print("✓ Dynamic tips enabled in configuration (~/.config/ars-arcanum/config.json).")
        return 0

    if args.disable:
        set_tips_enabled(False)
        print("✓ Dynamic tips disabled in configuration (~/.config/ars-arcanum/config.json).")
        return 0

    if args.toggle:
        state = toggle_tips()
        print(f"✓ Dynamic tips are now {'ENABLED' if state else 'DISABLED'}.")
        return 0

    if args.status:
        state = are_tips_enabled()
        print(f"Dynamic tips: {'ENABLED' if state else 'DISABLED'} (Total Tips in DB: {len(db)})")
        return 0

    if args.list_engines:
        engines = db.get_engines()
        print(f"Ars Arcanum Tip Engine Coverage ({len(engines)} engines, {len(db)} total tips):\n")
        for eng in engines:
            tips = db.get_by_engine(eng)
            print(f"  • {eng:<22} ({len(tips)} tips)")
        return 0

    # Determine query / engine
    engine_name = args.engine
    query_text = args.query or args.query_pos

    if not engine_name and query_text:
        # Check if query matches an engine name or alias
        resolved = db.resolve_engine(query_text)
        if resolved:
            engine_name = resolved
            query_text = ""

    if args.all:
        if engine_name:
            results = db.get_by_engine(engine_name, args.feature)
        elif query_text:
            results = db.search(query_text, limit=100)
        elif args.context:
            results = db.get_by_context(args.context)
        else:
            results = db.get_all()

        if args.json:
            print(json.dumps([t.to_dict() for t in results], indent=2))
            return 0

        print(f"=== Ars Arcanum Craft Wisdom ({len(results)} matching tips) ===\n")
        for t in results:
            print(format_cli_tip(t, verbose=args.verbose))
            print()
        return 0

    # Single tip retrieval
    tip = db.get_contextual_tip(
        engine=engine_name,
        feature=args.feature,
        context=args.context,
        query=query_text,
    )

    if not tip:
        if args.json:
            print(json.dumps({"error": "No matching tip found."}))
        else:
            print("No matching craft tip found. Run 'arcanum tip --all' to browse tips.", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(tip.to_dict(), indent=2))
    else:
        print(format_cli_tip(tip, verbose=args.verbose))

    return 0


if __name__ == "__main__":
    sys.exit(main())

