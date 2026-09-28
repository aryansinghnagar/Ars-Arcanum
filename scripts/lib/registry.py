#!/usr/bin/env python3
"""
Ars Arcanum Engine & Plugin Registry (scripts/lib/registry.py)
============================================================
Defines core vs craft engine classification, exhaustive metadata registry,
domain logic (physics, mathematics, linguistics, economics, narrative theory),
rationale ("why this way"), subfeature matrices, author extension guides with
concrete examples, dynamic plugin discovery, and capability introspection across
CLI and GUI surfaces.
"""

from __future__ import annotations

import difflib
import importlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EngineCategory(str, Enum):
    CORE = "core"
    CRAFT = "craft"
    UTILITY = "utility"


@dataclass
class AdvisoryResolution:
    """Creative resolution pathway for an advisory pattern."""
    mode: str  # "Hard Realism", "Speculative / Trope", "Creative Sovereignty"
    description: str


@dataclass
class EngineSpec:
    """Metadata specification for an Ars Arcanum engine / plugin module."""
    name: str
    category: EngineCategory
    title: str
    description: str
    module_name: str
    cli_command: str
    aliases: list[str] = field(default_factory=list)
    studio_tab: str | None = None
    default_enabled: bool = True
    enabled: bool = True
    logic_documentation: str = ""
    scientific_logic: str = ""
    why_this_way: str = ""
    worldbuilding_relevance: str = ""
    storytelling_relevance: str = ""
    writing_relevance: str = ""
    subfeatures: list[dict[str, str]] = field(default_factory=list)
    extension_guide: str = ""
    advisory_guidance: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.scientific_logic and self.logic_documentation:
            self.scientific_logic = self.logic_documentation
        elif not self.logic_documentation and self.scientific_logic:
            self.logic_documentation = self.scientific_logic


# Canonical Engine Registry Definitions
_ENGINES: dict[str, EngineSpec] = {
    # =========================================================================
    # DOMAIN A: ASTROPHYSICS, CLIMATE, CARTOGRAPHY & CELESTIAL MECHANICS
    # =========================================================================
    "astrophysics": EngineSpec(
        name="astrophysics",
        category=EngineCategory.CRAFT,
        title="Astrophysics & Orbital Mechanics",
        description="Relativistic brachistochrone kinematics, Lorentz time dilation, Keplerian orbits, and tidal Roche limits",
        module_name="lib.astrophysics",
        cli_command="calc astro",
        aliases=["astrophysics", "astro", "orbital"],
        studio_tab="Worldbuilding",
        logic_documentation="Calculates relativistic kinematics (Brachistochrone 1g transit t = (2c/a) cosh^-1(1 + ad/2c^2)), Lorentz dilation gamma = 1/sqrt(1-v^2/c^2), Keplerian orbits T^2 = 4pi^2 a^3 / (GM), Hill spheres, and Roche tidal limits.",
        scientific_logic="""1. Relativistic Brachistochrone Kinematics:
   For constant proper acceleration $a$ with turnaround at midpoint over proper distance $d$:
   $$t_{\\text{ship}} = \\frac{2c}{a} \\cosh^{-1}\\left(1 + \\frac{ad}{2c^2}\\right), \\quad t_{\\text{coord}} = 2\\sqrt{\\left(\\frac{d}{2c}\\right)^2 + \\frac{d}{a}}$$
   Peak velocity at turnover: $v_{\\text{max}} = c \\tanh\\left(\\frac{a t_{\\text{ship}}}{2c}\\right)$.

2. Lorentz Time Dilation & Relativistic Doppler Shift:
   $$\\gamma = \\frac{1}{\\sqrt{1 - v^2/c^2}}, \\quad \\Delta t_{\\text{observer}} = \\gamma \\Delta t_{\\text{proper}}, \\quad f_{\\text{obs}} = f_{\\text{src}} \\sqrt{\\frac{1 - v/c}{1 + v/c}}$$

3. Keplerian Orbital Mechanics & Stellar Insolation:
   Kepler's Third Law for semi-major axis $a$ and stellar mass $M_*$:
   $$T^2 = \\frac{4\\pi^2 a^3}{G(M_* + m_p)} \\approx \\frac{a^3}{M_*} \\text{ (in AU, Solar Masses, Years)}$$
   Stellar flux at orbital radius $d$: $S = \\frac{L_*}{4\\pi d^2}$. Habitable zone: $d_{\\text{HZ}} = \\sqrt{L_* / S_{\\text{target}}}$.

4. Tidal Limits & Gravitational Sphere of Influence:
   - Rigid Roche Limit: $d_{\\text{Roche}} = R_M \\left(2 \\frac{\\rho_M}{\\rho_m}\\right)^{1/3}$
   - Fluid Roche Limit: $d_{\\text{fluid}} \\approx 2.44 R_M (\\rho_M / \\rho_m)^{1/3}$
   - Hill Sphere (stable moon envelope): $r_H \\approx a (1 - e) \\left(\\frac{m_p}{3 M_*}\\right)^{1/3}$""",
        why_this_way="Hard sci-fi and space opera narratives break suspension of disbelief when travel times, communication light-delays, and tidal disruptions violate general/special relativity or orbital mechanics. By computing exact closed-form kinematic integrals, authors gain unshakeable pacing rails: travel intervals become natural story chapters, light-lag creates dramatic communication tension, and time dilation provides visceral emotional stakes.",
        worldbuilding_relevance="Determines accurate planetary day lengths, orbital years, multi-moon tidal forces, ring formation boundaries, and star habitable zones.",
        storytelling_relevance="Enforces hard travel durations as natural narrative pacing rails; light-lag creates dramatic information latency; relativistic time dilation creates tragic generational disconnects between travelers and home worlds.",
        writing_relevance="Supplies visceral sensory cues: spin-gravity Coriolis disorientation, relativistic optical blueshift/redshift, and 1g acceleration deck weight.",
        subfeatures=[
            {"name": "Brachistochrone Transit", "rule": "Computes continuous-acceleration burn-and-flip trajectory duration and peak velocity.", "example": "arcanum calc astro transit --distance 4.3ly --accel 1.0g"},
            {"name": "Keplerian Ephemeris", "rule": "Computes orbital period, semi-major axis, and orbital velocity from stellar mass.", "example": "arcanum calc astro orbit --star-mass 1.2 --semi-major 1.4"},
            {"name": "Roche Limit & Rings", "rule": "Calculates planetary tidal disruption radius for rigid and fluid satellite bodies.", "example": "arcanum calc astro roche --planet-radius 6371 --density-ratio 1.2"},
            {"name": "Time Dilation Converter", "rule": "Translates ship proper time to planetary frame coordinate time given journey velocity profile.", "example": "arcanum calc astro dilation --velocity 0.95c --proper-years 2.0"},
        ],
        extension_guide="""Authors can specify custom cosmological constants in `world.yaml`:
```yaml
cosmology:
  primary_star:
    mass_sol: 1.15
    luminosity_sol: 1.42
    spectral_type: "F8V"
  planets:
    - name: "Aethelgard"
      semi_major_au: 1.18
      eccentricity: 0.034
      axial_tilt_deg: 18.5
      moons:
        - name: "Selene-Prime"
          mass_kg: 7.34e22
          orbital_radius_km: 384400
```
Programmatic Python API:
```python
from lib.astrophysics import calc_brachistochrone_transit, calc_roche_limit
res = calc_brachistochrone_transit(distance_meters=4.07e16, acceleration_ms2=9.81)
print(f"Ship proper time: {res.ship_days:.1f} days, Peak v: {res.v_max_c:.3f} c")
```""",
        advisory_guidance=[
            {"pattern": "Relativistic FTL transit velocity specified without warp bubble", "option_a": "Cap velocity at sub-light (<1.0 c) with Lorentz dilation", "option_b": "Ground with Alcubierre warp field or hyperspace corridor", "option_c": "Retain uninhibited FTL as intentional space opera convention"},
            {"pattern": "Moon orbiting inside planetary Roche limit", "option_a": "Move moon orbit outside Roche radius to prevent breakup", "option_b": "Transform shattered moon into a majestic planetary ring system", "option_c": "Ground stability via monolithic ancient construct or arcane anchor"},
        ],
    ),

    "climate": EngineSpec(
        name="climate",
        category=EngineCategory.CRAFT,
        title="Planetary Climate & Köppen Biomes",
        description="Solar insolation, atmospheric circulation cells, orographic rain shadows, and Köppen-Geiger biome classification",
        module_name="lib.climate",
        cli_command="calc climate",
        aliases=["climate", "biomes", "weather"],
        studio_tab="Worldbuilding",
        logic_documentation="Simulates Milankovitch orbital cycles (eccentricity, obliquity, precession), solar flux insolation S = L/(4pi d^2), atmospheric circulation cells (Hadley/Ferrel/Polar), Coriolis deflection, and orographic rain shadows.",
        scientific_logic="""1. Solar Constant & Stefan-Boltzmann Blackbody Equilibrium:
   $$S = 1361 \\times \\frac{L_*}{d^2} \\text{ (W/m}^2\\text{)}, \\quad T_{\\text{eq}} = \\left[\\frac{S (1 - A)}{4\\sigma}\\right]^{1/4}$$
   Effective surface temperature including greenhouse warming: $T_{\\text{surf}} = T_{\\text{eq}} + \\Delta T_{\\text{greenhouse}}$.

2. Atmospheric Circulation Cells & Coriolis Deflection:
   Circulation cell regime depends on Rossby number $Ro = \\frac{U}{2\\Omega L}$:
   - Slow Rotator ($P_{\\text{rot}} > 120\\text{h}$): 1-cell Hadley global circulation pole-to-equator.
   - Earth-like ($16\\text{h} \\le P_{\\text{rot}} \\le 48\\text{h}$): 3-cell regime (Hadley $0^\\circ\\text{--}30^\\circ$, Ferrel $30^\\circ\\text{--}60^\\circ$, Polar $60^\\circ\\text{--}90^\\circ$).
   - Rapid Rotator ($P_{\\text{rot}} < 16\\text{h}$): 5+ multiple banded jet circulation cells (Jovian regime).

3. Orographic Rain Shadow & Adiabatic Lapse Rates:
   - Dry Adiabatic Lapse Rate (DALR): $\\Gamma_d \\approx 9.8^\\circ\\text{C/km}$
   - Saturated Adiabatic Lapse Rate (MALR): $\\Gamma_m \\approx 5.0\\text{--}6.5^\\circ\\text{C/km}$
   - Leeward Foehn/Chinook compression heating: Leeward surface air is dramatically warmer and drier ($RH < 20\\%$).

4. Köppen-Geiger Mathematical Biome Partitioning:
   - Group A (Tropical): All months $T_{\\text{mean}} \\ge 18^\\circ\\text{C}$.
   - Group B (Arid/Semi-Arid): Annual precipitation $P_{\\text{ann}} < 20 \\times (T_{\\text{ann}} + 14)$.
   - Group C (Temperate): Coldest month $-3^\\circ\\text{C} < T_{\\text{min}} < 18^\\circ\\text{C}$, warmest $T_{\\text{max}} \\ge 10^\\circ\\text{C}$.
   - Group D (Continental): Coldest month $T_{\\text{min}} \\le -3^\\circ\\text{C}$, warmest $T_{\\text{max}} \\ge 10^\\circ\\text{C}$.
   - Group E (Polar): Warmest month $T_{\\text{max}} < 10^\\circ\\text{C}$ (ET Tundra, EF Ice Cap).""",
        why_this_way="Fictional worlds frequently suffer from 'biome soup'—arbitrary placing of deserts next to rainforests without physical mechanisms. By deriving biomes strictly from astronomical insolation, axial tilt, planetary spin rate, and mountain elevation barriers, world geography emerges with organic, undeniable physical coherence.",
        worldbuilding_relevance="Determines realistic placement of deserts, rainforests, tundra, and temperate zones based on axial tilt and mountains.",
        storytelling_relevance="Sets weather hazards, seasonal agricultural campaigns, and migration pressures driving story conflicts.",
        writing_relevance="Enriches atmospheric sensory details: monsoon humidity, freezing katabatic mountain winds, arid desert salt breezes.",
        subfeatures=[
            {"name": "Insolation & Habitability", "rule": "Calculates solar flux and blackbody surface temperature across latitudes.", "example": "arcanum climate --star-lum 1.0 --distance-au 1.05 --albedo 0.29"},
            {"name": "Circulation Cell Mapper", "rule": "Determines wind bands (Trade Winds, Westerlies, Polar Easterlies) from rotation period.", "example": "arcanum climate --rotation-hours 32.0"},
            {"name": "Orographic Rain Shadow", "rule": "Simulates adiabatic cloud rainout on windward slope and desertification on leeward side.", "example": "arcanum climate --mountain-elevation 4200 --base-precip 1200"},
            {"name": "Köppen Classifier", "rule": "Assigns formal Köppen 3-letter classification (e.g. Cfb, BWh, Dfc) to climate coordinates.", "example": "arcanum climate --base-temp 14.5 --base-precip 650"},
        ],
        extension_guide="""Define regional microclimates in `world.yaml`:
```yaml
climate:
  planetary_albedo: 0.31
  axial_tilt_deg: 24.2
  greenhouse_delta_k: 35.0
  regions:
    - name: "Great Valdian Basin"
      latitude_deg: 34.0
      elevation_m: 450
      windward_mountain_height_m: 3800
      wind_direction: "West"
```""",
        advisory_guidance=[
            {"pattern": "Coastal desert without cold ocean current or mountain rain shadow", "option_a": "Add offshore cold current or windward mountain range", "option_b": "Attribute aridity to ancient magical cataclysm or subterranean siphon", "option_c": "Retain as an exotic, wondrous geographical anomaly"},
        ],
    ),

    "calendar": EngineSpec(
        name="calendar",
        category=EngineCategory.CRAFT,
        title="Custom Planetary Calendars & Moons",
        description="Multi-moon synodic phase tracker, celestial conjunctions, Metonic cycles, and invariant calendar math",
        module_name="lib.calendar",
        cli_command="calendar",
        aliases=["calendars", "moons", "ephemeris"],
        studio_tab="Worldbuilding",
        logic_documentation="Models custom planetary calendars, multiple moon orbital phases, synodic conjunctions (syzygy), Metonic lunisolar cycle synchronization, and epoch offset conversions.",
        scientific_logic="""1. Synodic Lunar Period & Multi-Moon Conjunctions:
   Given planetary orbital period $P_{\\text{year}}$ and moon sidereal period $P_{\\text{sid}}$:
   $$\\frac{1}{P_{\\text{syn}}} = \\left| \\frac{1}{P_{\\text{sid}}} - \\frac{1}{P_{\\text{year}}} \\right|$$
   For two moons with synodic periods $P_1$ and $P_2$, joint syzygy conjunction occurs every:
   $$P_{\\text{conj}} = \\frac{P_1 \\cdot P_2}{|P_1 - P_2|}$$

2. Metonic Lunisolar Harmonization:
   Find integer ratio $m \\cdot P_{\\text{year}} \\approx n \\cdot P_{\\text{syn}}$ via continued fraction expansion of $P_{\\text{year}} / P_{\\text{syn}}$.

3. Invariant Astronomical Epoch Conversions:
   Transform arbitrary fictional dates $(Y, M, D, H)$ into absolute fractional Julian Astronomical Days (JAD) from epoch $T_0$:
   $$\\text{JAD}(t) = t_{\\text{epoch}} + (Y - Y_0) \\times D_{\\text{year}} + \\sum_{i=1}^{M-1} D_i + (D - 1) + \\frac{H}{24}$$""",
        why_this_way="Fictional stories with multiple moons or non-365 day years frequently create impossible lunar phases (e.g. full moons occurring twice in one week or eclipses without syzygy alignment). The calendar engine executes rigorous fractional epoch arithmetic, guaranteeing that celestial omens and festival cycles are mathematically immutable.",
        worldbuilding_relevance="Constructs bespoke calendar systems with unique week lengths, months, and festival days.",
        storytelling_relevance="Anchors prophecy countdowns and dramatic deadlines to rare celestial conjunctions.",
        writing_relevance="Provides in-universe date arithmetic and lunar phase lighting descriptions.",
        subfeatures=[
            {"name": "Synodic Lunar Phase Tracker", "rule": "Calculates illumination percentage (New, Crescent, Quarter, Gibbous, Full) for all moons.", "example": "arcanum calendar --date 1442-08-15 --phases"},
            {"name": "Multi-Moon Conjunction Auditor", "rule": "Forecasts rare triple/quadruple moon alignments and solar/lunar eclipses.", "example": "arcanum calendar --syzygy-scan 50years"},
            {"name": "Intercalary Leap Year Rule", "rule": "Applies custom leap-day/leap-month algorithms to keep seasons aligned.", "example": "arcanum calendar --validate-drift"},
        ],
        extension_guide="""Create a custom calendar definition in `World/Calendars/solar_calendar.yaml`:
```yaml
calendar:
  name: "Imperial Solar Calendar"
  year_length_days: 384.25
  day_length_hours: 26.0
  months:
    - name: "Primus"
      days: 32
    - name: "Secundus"
      days: 32
    - name: "Veris"
      days: 32
  leap_rule: "Every 4th year adds 1 day to Intercalary Feast"
  moons:
    - name: "Lunara"
      sidereal_days: 28.5
    - name: "Umbra"
      sidereal_days: 14.2
```""",
        advisory_guidance=[
            {"pattern": "Unequal seasonal lengths caused by orbital eccentricity", "option_a": "Calculate precise Keplerian seasonal lengths for calendar", "option_b": "Attribute seasonal harmony to divine orbital intervention", "option_c": "Use harsh long winters as a central cultural story pillar"},
        ],
    ),

    "ecology": EngineSpec(
        name="ecology",
        category=EngineCategory.CRAFT,
        title="Ecology & Food Web Simulator",
        description="Trophic energy pyramid validator, Lotka-Volterra predator-prey dynamics, and Kleiber metabolic scaling",
        module_name="lib.ecology",
        cli_command="ecology",
        aliases=["ecology", "foodweb", "bestiary"],
        studio_tab="Worldbuilding",
        logic_documentation="Applies Raymond Lindeman's 10% trophic transfer efficiency, Lotka-Volterra predator-prey differential models, Kleiber's metabolic scaling (P proportional to M^0.75), and Square-Cube skeletal limits on megafauna.",
        scientific_logic="""1. Lindeman Trophic Transfer Efficiency:
   Energy available at trophic level $n+1$:
   $$E_{n+1} = \\eta \\cdot E_n \\quad (\\eta \\approx 0.10 \\text{ to } 0.15)$$
   Biomass ratio between primary producers (Level 1), herbivores (Level 2), and apex predators (Level 3/4) must scale as $1000 : 100 : 10 : 1$.

2. Lotka-Volterra Predator-Prey Coupled Differential Equations:
   $$\\frac{dx}{dt} = \\alpha x - \\beta x y, \\quad \\frac{dy}{dt} = \\delta x y - \\gamma y$$
   Where $x$ = prey population, $y$ = predator population, $\\alpha$ = prey growth rate, $\\beta$ = predation rate, $\\gamma$ = predator mortality, $\\delta$ = conversion efficiency.

3. Kleiber's Law of Metabolic Scaling & Daily Forage Requirements:
   Basal metabolic rate $BMR$ scales with body mass $M$:
   $$BMR = B_0 M^{3/4} \\propto M^{0.75}$$
   A 5-tonne dragon requires $\\sim 5000^{0.75} \\approx 594$ times the daily caloric intake of a 1kg creature (not 5,000x).

4. Square-Cube Law & Megafauna Skeletal Limits:
   As body length $L$ scales by factor $k$:
   $$\\text{Mass } M \\propto k^3, \\quad \\text{Bone Cross-Sectional Area } A \\propto k^2, \\quad \\text{Skeletal Stress } \\sigma = \\frac{F}{A} \\propto k$$
   Terrestrial creatures exceeding 50 tonnes require aquatic buoyancy, hollow avian pneumatic bones, or arcane mass-reduction field effects.""",
        why_this_way="Fantasy worlds often populate dungeons and forests with thousands of giant apex monsters without sufficient prey biomass, creating ecological absurdity. The ecology engine guarantees that creature habitats, hunting ranges, and foraging demands respect physical energetics.",
        worldbuilding_relevance="Calculates sustainable predator densities, herbivore grazing lands, and monster biome capacities.",
        storytelling_relevance="Scarcity of game drives hunter-gatherer migrations, monster attacks, and territorial conflicts.",
        writing_relevance="Provides authentic sensory descriptions of flora, fauna behavior, and foraging yields.",
        subfeatures=[
            {"name": "Trophic Energy Pyramid", "rule": "Audits biomass ratios across producers, herbivores, carnivores, and apex predators.", "example": "arcanum ecology --biome temperate-forest --producers 100000kg"},
            {"name": "Kleiber Metabolic Sizer", "rule": "Calculates daily food/caloric consumption for giant mythical beasts.", "example": "arcanum ecology --beast-mass 8500kg --diet carnivore"},
            {"name": "Square-Cube Skeletal Stress", "rule": "Evaluates bone thickness and structural feasibility for colossal creatures.", "example": "arcanum ecology --creature-length 25m --terrestrial"},
        ],
        extension_guide="""Define creature ecology in `World/Bestiary/frost_wyrm.md`:
```yaml
---
name: "Frost Wyrm"
trophic_level: 4 # Apex Predator
adult_mass_kg: 3200
metabolism: "endothermic"
diet: "carnivorous"
territory_km2: 180
prey_species: ["Mountain Elk", "Highland Goat"]
skeletal_adaptation: "Pneumatic hollow carbon-lattice bone structure"
---
```""",
        advisory_guidance=[
            {"pattern": "Colossal apex predator biomass exceeds available herbivore prey", "option_a": "Scale down predator pack size or expand prey territory", "option_b": "Ground feeding via magical ambient energy or geothermal vents", "option_c": "Retain giant monster as a rare mythical creature"},
        ],
    ),

    "cartography": EngineSpec(
        name="cartography",
        category=EngineCategory.CRAFT,
        title="Offline Vector Cartography",
        description="Interactive SVG vector maps, Voronoi territorial influence polygons, Dijkstra travel pathfinding, and elevation contours",
        module_name="lib.cartography",
        cli_command="map",
        aliases=["cartography", "map", "vector-map"],
        studio_tab="Worldbuilding",
        logic_documentation="Generates and renders interactive SVG vector maps with Voronoi territorial influence polygons, Dijkstra shortest travel path calculation, contour elevation layering, and waypoint staging.",
        scientific_logic="""1. Voronoi Territorial Influence & Delaunay Dual:
   For a set of settlement seed points $P = \\{p_1, p_2, \\dots, p_n\\}$, the territorial cell $V(p_i)$ is:
   $$V(p_i) = \\{x \\in \\mathbb{R}^2 \\mid d(x, p_i) \\le d(x, p_j) \\; \\forall j \\ne i\\}$$
   Computes national borders, trade spheres of influence, and natural geographic border marches.

2. Dijkstra Shortest-Path & Friction-Surface Routing:
   Travel graph $G = (V, E)$ with edge weight $w(u, v) = d(u, v) \\times f_{\\text{terrain}}$, where $f_{\\text{terrain}}$ is the cost multiplier:
   - Paved Roman Road: $1.0$
   - Grassland / Plains: $1.4$
   - Dense Forest: $2.5$
   - Mountain Pass: $4.0$
   - Swampland / Marsh: $5.0$

3. Isoline Elevation Contouring & Hydrology Drainage:
   Generates elevation contours via Marching Squares algorithms. Rivers originate at high-elevation precipitation nodes ($E > 2000\\text{m}$) and follow downhill topological gradients $\\nabla E$, merging at confluences toward sea level ($E = 0$).""",
        why_this_way="Raster image maps cannot compute travel times, cannot dynamically toggle spoiler territories, and cannot scale crisply to print resolutions. Vector SVG maps combined with topological graph algorithms allow instant computation of travel routes and tactical chokepoints.",
        worldbuilding_relevance="Maps mountain ranges, river drainage basins, national borders, and trade road networks.",
        storytelling_relevance="Visualizes character journey routes, tactical chokepoints (mountain passes, river bridges), and military frontlines.",
        writing_relevance="Provides exact journey day estimates and landscape horizons during drafting.",
        subfeatures=[
            {"name": "Voronoi Realm Border Generator", "rule": "Computes organic national boundaries from castle and capital seat coordinates.", "example": "arcanum map --realm-borders"},
            {"name": "Dijkstra Journey Router", "rule": "Finds lowest-friction travel path across rivers, roads, and mountain passes.", "example": "arcanum map --route 'Riverwatch' 'Sunspire'"},
            {"name": "Hydrology Drainage Sweep", "rule": "Ensures rivers flow downhill without impossible uphill climbs or ungrounded bifurcations.", "example": "arcanum map --audit-rivers"},
        ],
        extension_guide="""Define waypoints and roads in `World/Map/map_data.yaml`:
```yaml
waypoints:
  - id: "wp_capital"
    name: "Aethelgard High Keep"
    coords: [450, 620]
    elevation_m: 350
    type: "city"
  - id: "wp_pass"
    name: "Dragon's Throat Pass"
    coords: [680, 410]
    elevation_m: 2400
    type: "mountain_pass"
roads:
  - from: "wp_capital"
    to: "wp_pass"
    type: "paved_highway"
    speed_factor: 1.0
```""",
        advisory_guidance=[
            {"pattern": "River bifurcates across flat plain away from coast", "option_a": "Merge rivers downstream following natural downhill gradient", "option_b": "Ground split via engineered royal canal locks or magical delta", "option_c": "Keep fantastical river split as a unique world feature"},
        ],
    ),

    "journey": EngineSpec(
        name="journey",
        category=EngineCategory.CRAFT,
        title="Travel & Logistics Calculator",
        description="Travel time, supply consumption, terrain difficulty, pack animal feed, and pacing logistics",
        module_name="lib.journey",
        cli_command="calc journey",
        aliases=["journey", "travel", "logistics"],
        studio_tab="Worldbuilding",
        logic_documentation="Calculates travel duration across terrain types (paved road, forest, mountain pass, swamp), pack animal feed ratios, high-altitude acclimatization, and wagon wheelwright repairs.",
        scientific_logic="""1. Tobler's Hiking Function & Terrain Velocity:
   Walking velocity $W$ as a function of slope angle $\\theta = \\frac{dh}{dx}$:
   $$W = 6 \\exp\\left(-3.5 \\left| \\frac{dh}{dx} + 0.05 \\right|\\right) \\text{ (km/h)}$$
   Base overland rates (8-hour march day):
   - Unencumbered Infantry on Paved Road: $32\\text{--}36\\text{ km/day}$
   - Loaded Wagon Train on Dirt Road: $18\\text{--}22\\text{ km/day}$
   - Cavalry / Light Couriers (with horse remounts): $60\\text{--}80\\text{ km/day}$

2. Logistics Consumption Ratios:
   - Human: $1.0\\text{ kg dry rations} + 3.0\\text{ liters water/day}$.
   - Pack Horse / Mule: $5.0\\text{ kg grain/hay} + 30\\text{ liters water/day}$.
   - Supply Limit Horizon: An army wagon carrying 500kg grain eaten by its own 2 draft horses reaches maximum radius of $\\sim 10\\text{ days}$ without local foraging.""",
        why_this_way="Fictional characters often teleport across continents in days, stripping the story of scale and logistical tension. Computing travel days and grain consumption grounds journeys in physical reality, creating natural story beats for campfire conversations, breakdowns, and exhaustion.",
        worldbuilding_relevance="Determines staging distance between coaching inns, royal relay post stations, and fortresses.",
        storytelling_relevance="Prevents travel teleportation; journey duration shapes character conversations and camping bonding scenes.",
        writing_relevance="Supplies realistic travel fatigue, blister care, foraging yields, and campfire sensory details.",
        subfeatures=[
            {"name": "March Duration Calculator", "rule": "Calculates march days given troop count, encumbrance, and terrain.", "example": "arcanum calc journey --distance-km 240 --terrain mountain --cavalry"},
            {"name": "Supply & Feed Burn Auditor", "rule": "Computes required grain wagons and water barrels for expeditions.", "example": "arcanum calc journey --party-size 12 --horses 8 --days 14"},
        ],
        extension_guide="""Run journey calculations via CLI:
```bash
arcanum calc journey --origin "Valdoria" --dest "Frostpeak" --distance 320 --mounts horse --terrain rough-hills
```""",
        advisory_guidance=[
            {"pattern": "Unrealistically fast foot travel speed (>50 km/day over rough mountains)", "option_a": "Increase travel duration to 4-5 days for realistic pacing", "option_b": "Ground travel speed via enchanted boots, post-horse relay, or magical draft", "option_c": "Retain accelerated travel for tight narrative velocity"},
        ],
    ),

    # =========================================================================
    # DOMAIN B: NARRATIVE ARCHITECTURE, DRAMATURGY & PACING
    # =========================================================================
    "structure": EngineSpec(
        name="structure",
        category=EngineCategory.CRAFT,
        title="Narrative Structure & Paradigms",
        description="Validates manuscript beats against Three-Act, Save the Cat, 8-Sequence, Hero's Journey, and Kishōtenketsu",
        module_name="lib.structure",
        cli_command="structure",
        aliases=["structure", "paradigms", "beats"],
        studio_tab="Craft",
        logic_documentation="Maps chapter word distributions against classical and modern storytelling frameworks: Three-Act Structure, Save the Cat, 8-Sequence Method, Hero's Journey, Fichtean Curve, and Kishōtenketsu (4-act twist without conflict).",
        scientific_logic="""1. Three-Act Structure (Aristotle / Syd Field):
   - Act I (Setup & Inciting Incident): $0\\%\\text{--}25\\%$
   - Act II-A (Rising Action & Pinch 1): $25\\%\\text{--}50\\%$
   - Midpoint Shift (Mirror Moment / Active Agency): $50\\%$
   - Act II-B (Crisis & All Hope Lost): $50\\%\\text{--}75\\%$
   - Act III (Climax & Resolution): $75\\%\\text{--}100\\%$

2. Save the Cat 15-Beat Architecture (Blake Snyder):
   - Opening Image ($1\\%$), Theme Stated ($5\\%$), Setup ($1\\%\\text{--}10\\%$)
   - Catalyst ($12\\%$), Debate ($12\\%\\text{--}25\\%$), Break into Two ($25\\%$)
   - B-Story ($28\\%$), Fun & Games ($25\\%\\text{--}50\\%$), Midpoint ($50\\%$)
   - Bad Guys Close In ($50\\%\\text{--}75\\%$), All is Lost ($75\\%$), Dark Night of Soul ($75\\%\\text{--}80\\%$)
   - Break into Three ($80\\%$), Finale ($80\\%\\text{--}99\\%$), Final Image ($100\\%$)

3. Kishōtenketsu (Traditional East Asian 4-Act Paradigm):
   - Ki (起 - Introduction): $0\\%\\text{--}25\\%$
   - Shō (承 - Development): $25\\%\\text{--}50\\%$
   - Ten (転 - The Unexpected Twist / Context Reframe without Western Conflict): $50\\%\\text{--}75\\%$
   - Ketsu (結 - Harmonization & Conclusion): $75\\%\\text{--}100\\%$""",
        why_this_way="Narrative pacing issues (the sagging middle, premature climax, rushed resolution) stem from unbalanced word allocations across structural beats. By mapping exact cumulative manuscript words against established dramatic paradigms, authors immediately see where their pacing drags or accelerates too quickly.",
        worldbuilding_relevance="Aligns world discovery milestones with character paradigm shifts.",
        storytelling_relevance="Diagnoses sluggish midpoints, premature climaxes, and rushed resolutions.",
        writing_relevance="Provides structural confidence during outlining and developmental editing.",
        subfeatures=[
            {"name": "Multi-Paradigm Beat Mapper", "rule": "Projects chapter word boundaries onto 3-Act, Save the Cat, 8-Sequence, and Kishōtenketsu models.", "example": "arcanum structure Manuscript/ --paradigm save-the-cat"},
            {"name": "Midpoint Harmony Check", "rule": "Audits whether pivotal status-quo shift occurs within 48%-52% of total word count.", "example": "arcanum structure Manuscript/ --midpoint-check"},
        ],
        extension_guide="""Configure custom story paradigms in `Manuscript/manuscript.yaml`:
```yaml
structure:
  target_words: 95000
  paradigm: "Three-Act"
  custom_milestones:
    inciting_incident: 12000
    midpoint_cataclysm: 47500
    climax_entry: 76000
```""",
        advisory_guidance=[
            {"pattern": "Midpoint transformation occurs at 68% instead of standard 50%", "option_a": "Rebalance chapter lengths toward symmetrical midpoint", "option_b": "Adopt asymmetrical 4-part Kishōtenketsu or Fichtean episodic pacing", "option_c": "Retain pacing as an intentional authorial tension curve"},
        ],
    ),

    "scene_mechanics": EngineSpec(
        name="scene_mechanics",
        category=EngineCategory.CRAFT,
        title="Scene Mechanics & Tension",
        description="Dwight Swain Motivation-Reaction Units (MRUs), Scene/Sequel cycles, in media res entries, and cliffhangers",
        module_name="lib.scene_mechanics",
        cli_command="tension",
        aliases=["scene", "swain", "mru"],
        studio_tab="Craft",
        logic_documentation="Audits Dwight Swain's Scene (Goal -> Conflict -> Disaster) and Sequel (Reaction -> Dilemma -> Decision) Motivation-Reaction Units (MRUs), in media res entries, and cliffhanger exits.",
        scientific_logic="""1. Dwight Swain Motivation-Reaction Units (MRUs):
   The micro-rhythm of dramatic prose follows neurological causality:
   $$\\text{External Motivation (Objective)} \\longrightarrow \\text{Somatic Reaction (Involuntary)} \\longrightarrow \\text{Visceral Action (Reflex)} \\longrightarrow \\text{Rational Speech / Choice}$$

2. Macro Scene-Sequel Alternation Cycle:
   - SCENE (Active Kinetic Pacing):
     $$\\text{Goal (Concrete, Immediate)} \\longrightarrow \\text{Conflict (Escalating Obstacles)} \\longrightarrow \\text{Disaster (The Hook: 'No, and furthermore' or 'Yes, but')}$$
   - SEQUEL (Reflective Emotional Pacing):
     $$\\text{Reaction (Visceral Emotional Processing)} \\longrightarrow \\text{Dilemma (No Good Options)} \\longrightarrow \\text{Decision (New Active Goal)}$$

3. In Media Res & Chapter Hook Index:
   Evaluates sentence 1-3 action density versus delayed backstory exposition.""",
        why_this_way="Scenes feel sluggish when authors reverse MRU order (e.g. having a character speak rationally before reacting physically to an explosion) or when scenes end in flat resolutions without new complications.",
        worldbuilding_relevance="Embeds world conflicts directly into immediate character stakes.",
        storytelling_relevance="Ensures every chapter advances plot and character transformation without dead weight.",
        writing_relevance="Eliminates 'talking heads in a void' and weak chapter endings.",
        subfeatures=[
            {"name": "MRU Sequence Validator", "rule": "Flags backwards reaction-before-stimulus constructions in intense action paragraphs.", "example": "arcanum tension Manuscript/01_Chapter.md --mru"},
            {"name": "Disaster Hook Classifier", "rule": "Audits scene exit endings for 'Yes, but' or 'No, and furthermore' tension.", "example": "arcanum tension Manuscript/ --hooks"},
        ],
        extension_guide="""Tag scene mechanics in chapter frontmatter:
```yaml
---
title: "The Siege of Dawn"
scene_type: "Scene" # or "Sequel"
goal: "Secure the courtyard gate mechanism before the battering ram breaks through"
conflict: "Iron gate chain is rusted solid; crossbow fire from upper battlements"
disaster: "Yes, the gate is locked, BUT the lever shears off in Kaelen's hand"
---
```""",
        advisory_guidance=[
            {"pattern": "Scene ends in clean triumph without new complication ('Yes, and')", "option_a": "Transform into Swain 'Yes, but' or 'No, and furthermore' disaster", "option_b": "Use victory to trigger higher external stakes from rival factions", "option_c": "Retain triumph as an earned moment of celebration"},
        ],
    ),

    "pacing": EngineSpec(
        name="pacing",
        category=EngineCategory.CRAFT,
        title="Pacing & Dialogue Rhythm",
        description="Dialogue-to-narrative density ratio, Gary Provost sentence length waveforms, and tension curve oscillations",
        module_name="lib.pacing",
        cli_command="pace",
        aliases=["pacing", "rhythm", "waveform"],
        studio_tab="Craft",
        logic_documentation="Analyzes prose mode distribution (Dialogue vs Action vs Monologue vs Exposition), Gary Provost sentence length waveforms, tension curve oscillations, and POV screen-time balance.",
        scientific_logic="""1. Gary Provost Sentence Rhythm Waveform:
   Sentence lengths must vary dynamically to produce musical prose:
   $$\\text{Variance } \\sigma^2 = \\frac{1}{N} \\sum_{i=1}^N (L_i - \\bar{L})^2$$
   Monotonous prose ($\\sigma < 3.5$ words) triggers reader fatigue. High-rhythm prose oscillates between 3-word punchy staccato and 25-word flowing lyrical sentences.

2. Prose Mode Quad-Distribution:
   Every paragraph is segmented into one of four modes:
   - Dialogue ($D$): Spoken speech with attributions.
   - Action / Kinetics ($A$): Physical movement and somatic reactions.
   - Interior Monologue ($M$): Character introspection and psychic perception.
   - Exposition / World Lore ($E$): Background history and environment context.
   Ideal action scenes maintain $A + D > 75\\%$; reflective sequels maintain $M > 50\\%$. Exposition $E > 30\\%$ in action scenes triggers pacing drag.""",
        why_this_way="Readers perceive a story as 'fast' or 'slow' not by word count, but by sentence rhythm variance and the ratio of dialogue/action to static exposition.",
        worldbuilding_relevance="Prevents lore dumps from stalling active narrative momentum.",
        storytelling_relevance="Balances fast-paced action sequences with reflective sequels and character bonding.",
        writing_relevance="Flags monotonous sentence structures and dialogue void syndrome.",
        subfeatures=[
            {"name": "Sentence Length Waveform", "rule": "Visualizes syllable and word count oscillation across paragraphs.", "example": "arcanum pace Manuscript/01_Chapter.md --waveform"},
            {"name": "Prose Mode Classifier", "rule": "Calculates percentage distribution of Dialogue vs Action vs Monologue vs Exposition.", "example": "arcanum pace Manuscript/ --modes"},
        ],
        extension_guide="""Run pacing analysis via CLI:
```bash
arcanum pace Manuscript/ --html dist/pacing_report.html
```""",
        advisory_guidance=[
            {"pattern": "Chapter dialogue density exceeds 80% without somatic action beats", "option_a": "Insert physical character actions, sensory environment cues, and pauses", "option_b": "Retain as a rapid-fire interrogation or tense courtroom debate", "option_c": "Keep stylized theatrical dialogue mode"},
        ],
    ),

    "plot_matrix": EngineSpec(
        name="plot_matrix",
        category=EngineCategory.CRAFT,
        title="Plot Grid & Subplot Matrix",
        description="Multi-threaded narrative grid tracking concurrent character arcs, mystery clues, and Chekhov's guns",
        module_name="lib.plot_matrix",
        cli_command="plot",
        aliases=["plot", "matrix", "subplots"],
        studio_tab="Craft",
        logic_documentation="Builds multi-track 2D plot spreadsheets tracking concurrent A-plots, B-plots, mystery clues, Chekhov's guns, Sanderson's Promise-Progress-Payoff (P3) cycles, and character co-occurrence collisions.",
        scientific_logic="""1. 2D Multi-Thread Plot Matrix:
   Rows represent Chapters $C_1, C_2, \\dots, C_n$; columns represent concurrent Narrative Threads $T_1, T_2, \\dots, T_m$ (Main A-Plot, Romance B-Plot, Political Intrigue C-Plot, Mystery Clues).

2. Chekhov's Gun Lifecycle State Machine:
   $$\\text{Introduced (Chapter } i) \\longrightarrow \\text{Primed / Referenced (Chapter } j) \\longrightarrow \\text{Discharged / Paid Off (Chapter } k)$$
   Flags unresolved guns ($k = \\text{None}$) and ungrounded climactic solutions ($i = k$, deus ex machina).

3. Sanderson Promise-Progress-Payoff (P3) Architecture:
   - Promise: Explicit early contract with reader establishing tone and stakes.
   - Progress: Measurable, perceptible milestones toward resolving the contract.
   - Payoff: Satisfying fulfillment or deliberate subversion of the promise.""",
        why_this_way="Complex multi-POV novels easily drop subplots or fail to pay off foreshadowed clues. A formal matrix ensures every introduced story element undergoes proper priming and payoff.",
        worldbuilding_relevance="Ensures world events (wars, celestial transits) align with character chapters.",
        storytelling_relevance="Tracks foreshadowing fulfillment and prevents forgotten subplots across chapters.",
        writing_relevance="Provides structural clarity across complex, multi-threaded epics.",
        subfeatures=[
            {"name": "Chekhov Gun Lifecycle Audit", "rule": "Tracks introduced artifacts and flags those with zero climactic payoff.", "example": "arcanum plot Manuscript/ --chekhov"},
            {"name": "Subplot Progression Grid", "rule": "Generates 2D chapter-by-thread visual matrix.", "example": "arcanum plot Manuscript/ --html dist/plot_matrix.html"},
        ],
        extension_guide="""Annotate plot threads in chapter frontmatter:
```yaml
---
title: "Whispers in the Crypt"
threads:
  a_plot: "Infiltrate royal vault"
  b_plot_romance: "Althea discovers Kaelen's exile mark"
chekhov_guns:
  - id: "obsidian_dagger"
    status: "introduced" # "primed" | "discharged"
    notes: "Found beneath the sarcophagus"
---
```""",
        advisory_guidance=[
            {"pattern": "Chekhov gun introduced in early chapter without payoff by climax", "option_a": "Integrate payoff during climactic resolution", "option_b": "Frame as an intentional mystery clue carried into sequel volume", "option_c": "Keep as atmospheric background lore element"},
        ],
    ),

    "branching_graph": EngineSpec(
        name="branching_graph",
        category=EngineCategory.CRAFT,
        title="Interactive Branching Narrative Graph",
        description="Topological choice DAG validator and multi-engine exporter (HTML Subway Map, Ink, Twine, Mermaid)",
        module_name="lib.branching_graph",
        cli_command="branch",
        aliases=["branching", "gamebook", "interactive-fiction", "branch-graph", "subway-map"],
        studio_tab="Editor",
        logic_documentation="Parses choice directives (@choice, @state), validates choice graph topology, detects dead-ends/unreachable nodes, and exports interactive narrative subway maps.",
        scientific_logic="""1. Choice Graph Directed Acyclic Graph (DAG) Topology:
   Graph $G = (V, E)$ where nodes $V$ are narrative scenes and directed edges $E$ are user choices `@choice: [Prompt] -> Target_Scene`.

2. State-Dependent Edge Evaluation:
   Edge $e = (u, v)$ is navigable if state condition $S \\models \\phi(e)$ holds. Directives `@state: var += delta` mutate the world state vector $S$.

3. Topological Path Invariants:
   - Dead-End Detection: $\\text{deg}^+(v) = 0$ where $v$ is not marked `@ending`.
   - Unreachable Node Sweep: Nodes where $\\text{deg}^-(v) = 0$ ($v \\ne v_{\\text{root}}$).
   - Inevitable Convergence Index: Degree of choice collapse back to canonical bottlenecks.""",
        why_this_way="Interactive fiction and gamebooks suffer from unnavigable orphan scenes or unintentional infinite loops without automated topological verification.",
        worldbuilding_relevance="Maps interactive choose-your-own-path gamebooks and branching historical events.",
        storytelling_relevance="Visualizes multi-POV storyline splits, divergences, and climax convergences.",
        writing_relevance="Ensures all branching narrative paths are satisfying and structurally balanced.",
        subfeatures=[
            {"name": "Topological Dead-End Detector", "rule": "Finds orphan scenes and choice branches with no exit or resolution.", "example": "arcanum branch Manuscript/ --validate"},
            {"name": "Subway Map HTML Exporter", "rule": "Compiles interactive SVG/HTML visual narrative subway diagram.", "example": "arcanum branch Manuscript/ --html dist/branching_map.html"},
            {"name": "Twine / Ink Transpiler", "rule": "Transpiles sovereign markdown choice directives into standard Twine Sugarcube and Inkle Ink formats.", "example": "arcanum branch Manuscript/ --export-ink dist/story.ink"},
        ],
        extension_guide="""Embed choice directives directly in markdown chapter prose:
```markdown
# Chapter 03: The Forked Path

You stand before the Iron Gate.

@state: courage += 1
@choice: [Force open the rusty gate] -> 04A_Dungeon_Vault
@choice: [Climb the ivy wall] -> 04B_Rooftop_Escape
```""",
        advisory_guidance=[
            {"pattern": "Dead-end branch node without resolution or choice exit", "option_a": "Add resolution epilogue or redirect choice to convergence node", "option_b": "Frame branch as an intentional tragic failure ending", "option_c": "Keep as work-in-progress draft stub"},
        ],
    ),

    "story_canvas": EngineSpec(
        name="story_canvas",
        category=EngineCategory.CRAFT,
        title="Visual Story Canvas & Corkboard",
        description="Visual drag-and-drop narrative corkboard with live structural harmony recalculation",
        module_name="lib.story_canvas",
        cli_command="canvas",
        aliases=["corkboard", "story-map", "story-canvas"],
        studio_tab="Editor",
        logic_documentation="Provides an offline visual corkboard where authors can drag and drop chapter index cards, reordering disk files bidirectionally, while calculating tension and structural beat distributions in real-time.",
        scientific_logic="""1. Bidirectional Disk File Graph Synchronization:
   Card ordering in the visual UI is backed by atomic renaming:
   $$\\text{UI Order } \\langle C_1, C_2, \\dots, C_n \\rangle \\longleftrightarrow \\text{Atomic POSIX renumbering on disk } 01\\_\\dots, 02\\_\\dots$$

2. Real-Time Structural Harmony Recalculation:
   As cards are dragged between Act columns, word counts and tension curves recompute instantly via standard deviation deltas from target beat percentages.""",
        why_this_way="Visual thinkers need a spatial corkboard to arrange scenes without breaking the disk file naming conventions of novelWriter and Obsidian.",
        worldbuilding_relevance="Pins location dossiers and artifact cards alongside relevant plot scenes.",
        storytelling_relevance="Enables intuitive visual restructuring of acts, sequences, and subplot pacing.",
        writing_relevance="Combines visual index cards with synopsis summaries for effortless chapter navigation.",
        subfeatures=[
            {"name": "Drag-and-Drop Corkboard", "rule": "Rearranges chapters and scenes across act columns with instant preview.", "example": "arcanum canvas Manuscript/ --html dist/canvas.html"},
            {"name": "Atomic Disk Renumberer", "rule": "Safely updates file names on disk to mirror corkboard arrangement.", "example": "arcanum canvas Manuscript/ --apply-order"},
        ],
        extension_guide="""Launch Story Canvas via CLI:
```bash
arcanum canvas Manuscript/
```""",
        advisory_guidance=[
            {"pattern": "Visual card reordering changes chapter narrative sequence on disk", "option_a": "Confirm atomic file renumbering on disk", "option_b": "Create virtual outline arrangement without touching disk files", "option_c": "Export new card order as an alternative draft outline"},
        ],
    ),

    "causality": EngineSpec(
        name="causality",
        category=EngineCategory.CRAFT,
        title="Causal Graph & Timeline Branches",
        description="Directed Acyclic Graph causality engine, timeline paradox detection, and multiverse trees",
        module_name="lib.causality",
        cli_command="causality",
        aliases=["causality", "causal", "time-travel", "paradox"],
        studio_tab="Worldbuilding",
        logic_documentation="Models narrative causality using Directed Acyclic Graphs (DAG), detects Closed Timelike Curves (CTC), evaluates Novikov self-consistency loops, and tracks multiverse timeline branch divergence.",
        scientific_logic="""1. Causal Directed Acyclic Graph (DAG) Structure:
   Events $E = \\{e_1, e_2, \\dots, e_n\\}$ with causal relation $e_i \\prec e_j$ (event $i$ is a necessary prerequisite for event $j$).

2. Closed Timelike Curve (CTC) & Paradox Detection:
   - Grandfather Paradox (Inconsistency Cycle): A causal edge directed into its own past light-cone that negates its own cause: $\\exists e_i \\prec \\dots \\prec e_j \\prec \\neg e_i$.
   - Novikov Self-Consistency Condition: A closed loop where total probability of the loop occurring is $P = 1.0$ (ontological loop / bootstrap paradox without contradiction).
   - Multiverse Branching (Many-Worlds): At divergence point $t_{\\text{fork}}$, create new branch world-line $W_2$ while preserving $W_1$ invariant.""",
        why_this_way="Time-travel and precognition narratives frequently collapse into unresolvable logical contradictions. The causality engine mathematically checks every causal link to guarantee temporal consistency.",
        worldbuilding_relevance="Establishes hard physical/metaphysical rules for time travel, prophecies, and precognition.",
        storytelling_relevance="Audits time-travel story logic, grandfather paradoxes, bootstrap paradoxes, and temporal loops.",
        writing_relevance="Helps authors keep track of causal ripples, memory echoes, and butterfly effects.",
        subfeatures=[
            {"name": "CTC Paradox Sweeper", "rule": "Scans historical timeline events for negative causal feedback loops.", "example": "arcanum causality World/ --audit-loops"},
            {"name": "Multiverse Branch Visualizer", "rule": "Exports branching timeline tree showing divergent worldlines.", "example": "arcanum causality World/ --html dist/causal_tree.html"},
        ],
        extension_guide="""Define causal events in `World/History/timeline_events.yaml`:
```yaml
events:
  - id: "assassination_king"
    date: "1442-03-12"
    prerequisites: ["palace_guard_bribe", "smuggled_nightshade"]
    consequences: ["succession_crisis", "martial_law"]
    temporal_branch: "prime"
```""",
        advisory_guidance=[
            {"pattern": "Ungrounded causal bootstrap paradox (information with no origin)", "option_a": "Provide origin event for the retrocausal information", "option_b": "Ground as a stable Novikov self-consistent ontological loop", "option_c": "Embrace the paradox as a deliberate cosmic mystery"},
        ],
    ),

    "timeline_sync": EngineSpec(
        name="timeline_sync",
        category=EngineCategory.CRAFT,
        title="Dual-Track Timeline Synchronizer",
        description="Chronological vs narrative sequence synchronizer with flashback and paradox detection",
        module_name="lib.timeline_sync",
        cli_command="timeline",
        aliases=["timeline-sync", "sync-timeline", "chronology"],
        studio_tab="Worldbuilding",
        logic_documentation="Synchronizes dual-track narrative sequence (reader's page order) against chronological in-universe dates, detecting impossible character bilocations, flashbacks, and timeline paradoxes.",
        scientific_logic="""1. Dual-Track Sequence Alignment:
   - Narrative Track (Discourse Time): Ordered sequence $\\langle 1, 2, \\dots, N \\rangle$ of chapters read by the audience.
   - Chronological Track (Story Time): In-universe absolute timestamp $T_{\\text{world}}(C_k)$.
   - Nonlinear Anachrony: Flashbacks (analepsis: $T(C_{k}) < T(C_{k-1})$) and Flash-forwards (prolepsis: $T(C_{k}) \\gg T(C_{k-1})$).

2. Bilocation & Invariant Spatial Velocity Check:
   If character $X$ appears in Chapter $A$ at location $L_A$ at time $t_A$, and in Chapter $B$ at location $L_B$ at time $t_B$:
   $$v_{\\text{required}} = \\frac{d(L_A, L_B)}{|t_B - t_A|} \\le v_{\\text{max\\_travel}}$$
   Flags impossible bilocations when required velocity exceeds realistic travel speed.""",
        why_this_way="Nonlinear storytelling (flashbacks, parallel storylines) easily creates unintentional continuity bugs where characters appear in two distant places at the same time.",
        worldbuilding_relevance="Builds thousands of years of historical annals aligned with in-universe calendar math.",
        storytelling_relevance="Manages nonlinear storytelling (flashbacks, parallel storylines, framing narratives).",
        writing_relevance="Ensures character biological ages, travel times, and seasons match narrative dates.",
        subfeatures=[
            {"name": "Bilocation Conflict Detector", "rule": "Flags characters present at two different locations on the same in-universe date.", "example": "arcanum timeline Manuscript/ --audit-bilocation"},
            {"name": "Anachrony Visualizer", "rule": "Renders dual-track Gantt chart linking story time to chapter reading order.", "example": "arcanum timeline Manuscript/ --html dist/timeline.html"},
        ],
        extension_guide="""Specify narrative and chronological times in chapter frontmatter:
```yaml
---
title: "The Battle of Ash Hollow"
chrono_date: "1442-09-14"
narrative_time: "Day 4 of the Campaign (Flashback)"
pov: "Commander Jennifer"
location: "Ash Hollow Fortress"
---
```""",
        advisory_guidance=[
            {"pattern": "Character appears in two distant locations on the same chronological date (bilocation)", "option_a": "Adjust chapter narrative date or introduce travel interval", "option_b": "Ground bilocation via magical teleportation, twin sibling, or astral projection", "option_c": "Retain as an intentional non-linear storytelling perspective"},
        ],
    ),

    "prophecy": EngineSpec(
        name="prophecy",
        category=EngineCategory.CRAFT,
        title="Prophecy Lifecycle Tracker",
        description="Tracks cryptic prophecy stanzas, interpretations, fulfillment conditions, and subversions",
        module_name="lib.prophecy",
        cli_command="prophecy",
        aliases=["prophecy", "oracle", "delphic"],
        studio_tab="Worldbuilding",
        logic_documentation="Tracks cryptic prophecy stanzas, Delphic ambiguities, fulfillment milestones, Oedipal paradoxes, and deliberate thematic subversions across manuscript chapters.",
        scientific_logic="""1. Prophecy Stanza & Delphic Clause Tree:
   A prophecy consists of stanzas $S_1, S_2, \\dots, S_n$, where each stanza contains one or more ambiguous clauses $C_{ij}$.
   Each clause maps to multiple competing In-World Interpretations $\\{I_1, I_2, \\dots\\}$ and one True Fulfillment Event $E^*$.

2. Oedipal Paradox (Self-Fulfilling Prophecy):
   Event $E^*$ is caused precisely by the antagonist's actions to prevent $E^*$: $\\text{Action}(\\neg E^*) \\Longrightarrow E^*$.

3. Fulfillment Typology:
   - Literal: Clause resolves in exact accordance with prophecy wording.
   - Metaphorical / Delphic: 'No man born of woman' resolved via C-section (Macbeth).
   - Subverted: Prophecy revealed as manufactured political propaganda.""",
        why_this_way="Prophecies become boring when they spoil the plot or feel like arbitrary author cheat codes. Tracking interpretations and subversions ensures foreshadowing feels earned and climactic.",
        worldbuilding_relevance="Grounds sacred religious scriptures, ancient oracle inscriptions, and mythological lore.",
        storytelling_relevance="Builds reader anticipation and dramatic irony through ambiguous prophecy clauses.",
        writing_relevance="Aids in crafting poetic, double-meaning prophetic verses and riddle stanzas.",
        subfeatures=[
            {"name": "Clause Fulfillment Matrix", "rule": "Tracks status (Unfulfilled, Primed, Fulfilled, Subverted) per stanza.", "example": "arcanum prophecy World/ --status"},
            {"name": "Delphic Ambiguity Analyzer", "rule": "Identifies double-meanings and homophones in poetic verses.", "example": "arcanum prophecy World/ --verses"},
        ],
        extension_guide="""Define prophecy manifests in `World/History/prophecy_of_the_sun.yaml`:
```yaml
prophecy:
  title: "The Prophecy of the Shattered Sun"
  source: "Oracle of Delphi-Prime"
  stanzas:
    - id: "stanza_1"
      verse: "When the black star bleeds upon the silver sea..."
      literal_interpretation: "Solar eclipse over the Silver Ocean"
      true_event_chapter: "Chapter_18"
      status: "fulfilled"
```""",
        advisory_guidance=[
            {"pattern": "Prophecy clause fulfilled too straightforwardly without thematic twist", "option_a": "Add Delphic double-meaning or ironic twist to fulfillment", "option_b": "Subvert the prophecy as a manufactured political fraud", "option_c": "Fulfill literally as a legendary validation of ancient truth"},
        ],
    ),

    "writing_sprint": EngineSpec(
        name="writing_sprint",
        category=EngineCategory.CORE,
        title="Sovereign Writing Sprint & Session Analytics",
        description="Sprint session timer, WPM velocity analytics, daily streak tracking, and offline HTML productivity dashboard",
        module_name="lib.writing_sprint",
        cli_command="sprint",
        aliases=["sprint", "pomodoro", "velocity"],
        studio_tab="Productivity",
        logic_documentation="Tracks focused writing sprint intervals, net new word counts, WPM typing velocity, daily streaks, time-of-day productivity heatmaps, and offline achievement quests.",
        scientific_logic="""1. Pomodoro Focus Interval & Velocity Analytics:
   $$\\text{Net Words} = W_{\\text{end}} - W_{\\text{start}}, \\quad \\text{WPM} = \\frac{\\text{Net Words}}{\\text{Sprint Duration (Minutes)}}$$

2. Time-of-Day Productivity Heatmap:
   Bivariate distribution of writing volume across hour of day $h \\in [0, 23]$ and day of week $d \\in [0, 6]$ to isolate author's peak cognitive flow windows.""",
        why_this_way="Authors struggle with writer's block when looking at a massive 100,000-word book. Short 15-25 minute sprints gamify drafting and build daily output momentum.",
        worldbuilding_relevance="Measures worldbuilding note generation velocity and research sprints.",
        storytelling_relevance="Assists writers in breaking through drafting blocks and hitting volume milestones.",
        writing_relevance="Builds consistent daily writing habits with motivating offline progress reports.",
        subfeatures=[
            {"name": "Sprint Interval Timer", "rule": "Runs 15/25/45-minute timed drafting sessions with net word telemetry.", "example": "arcanum sprint Manuscript/ --minutes 25"},
            {"name": "Productivity Heatmap", "rule": "Generates offline HTML report of writing velocity by hour and day.", "example": "arcanum sprint --history --html dist/sprint_dashboard.html"},
        ],
        extension_guide="""Start a writing sprint from CLI:
```bash
arcanum sprint Manuscript/ --minutes 20 --target-words 500
```""",
        advisory_guidance=[
            {"pattern": "Sprint target word count not reached during interval", "option_a": "Extend sprint timer by 5 minutes for completion", "option_b": "Log session words and celebrate net positive output", "option_c": "Reflect in session journal and take a restful break"},
        ],
    ),

    # =========================================================================
    # DOMAIN C: CHARACTERS, SOCIETY, CONLANGS, ECONOMY & COMBAT
    # =========================================================================
    "dramatis_personae": EngineSpec(
        name="dramatis_personae",
        category=EngineCategory.CRAFT,
        title="Multi-Volume Dramatis Personae & Universe Cast Matrix",
        description="Cross-volume character profile parser, manuscript POV/mention cross-referencer, lifecycle continuity, and phonetic collision detector",
        module_name="lib.dramatis_personae",
        cli_command="cast",
        aliases=["dramatis-personae", "dramatis", "cast", "characters-cast"],
        studio_tab="Worldbuilding",
        logic_documentation="Parses character dossiers, cross-references manuscript chapter POV screen-times, validates lifecycle states (Alive -> Missing -> Deceased -> Ascended), detects name phonetic collisions (e.g. Jon vs Joram), and exports HTML galleries.",
        scientific_logic="""1. Character Lifecycle State Machine:
   $$\\text{Active / Alive} \\longrightarrow \\text{Missing / Incarcerated} \\longrightarrow \\text{Deceased} \\longrightarrow \\text{Ascended / Legendary}$$
   Catches impossible retroactive mentions of deceased characters in present active scenes without flashback tags.

2. Phonetic Name Collision & Levenshtein Distance:
   For character names $N_1$ and $N_2$ appearing in the same chapter scene:
   $$\\text{Levenshtein}(N_1, N_2) \\le 2 \\quad \\lor \\quad \\text{Soundex}(N_1) = \\text{Soundex}(N_2)$$
   Flags confusingly similar character names (e.g. 'Kaelen' and 'Kaelin') that disorient readers.""",
        why_this_way="Epic fantasies with hundreds of characters frequently suffer from confusingly similar names and accidental continuity revivals of dead characters.",
        worldbuilding_relevance="Maintains comprehensive universe cast matrices across noble houses, factions, and orders.",
        storytelling_relevance="Audits character screen-time, relationship chord networks, and long-term POV absence.",
        writing_relevance="Prevents similar-sounding character names that confuse readers.",
        subfeatures=[
            {"name": "Phonetic Name Collision Auditor", "rule": "Flags similar names using Soundex, Metaphone, and Levenshtein metrics.", "example": "arcanum cast --audit-names"},
            {"name": "POV Screen-Time Balancer", "rule": "Calculates chapter word counts per character perspective.", "example": "arcanum cast Manuscript/ --screen-time"},
            {"name": "HTML Cast Gallery Exporter", "rule": "Exports standalone visual portrait cards with bio and affiliation tags.", "example": "arcanum cast World/ --html dist/cast_gallery.html"},
        ],
        extension_guide="""Define characters in `World/Characters/kaelen_voss.md`:
```yaml
---
name: "Kaelen Voss"
aliases: ["The Shadow Blade", "Kael"]
status: "Alive" # Alive | Missing | Deceased | Ascended
house: "House Voss"
faction: "Silent Hand"
pov: true
eye_color: "Grey-Blue"
handedness: "Right"
---
```""",
        advisory_guidance=[
            {"pattern": "Phonetically similar character names in same scene (e.g. 'Kaelen' and 'Kaelin')", "option_a": "Rename one character with distinct starting consonant", "option_b": "Establish in-universe naming tradition (e.g. cousins named after grandfather)", "option_c": "Retain names with clarifying nicknames / titles"},
        ],
    ),

    "voice": EngineSpec(
        name="voice",
        category=EngineCategory.CRAFT,
        title="Character Voice Profiler",
        description="Dialogue vocabulary uniqueness, sentence rhythm, verbal tics, and POV voice bleed detection",
        module_name="lib.voice",
        cli_command="audit voice",
        aliases=["voice", "idiolect", "stylometry"],
        studio_tab="Craft",
        logic_documentation="Analyzes character idiolects, lexical rarity scores, sentence length cadence, verbal tics, and conversational dominance to detect voice bleed across multiple POV characters.",
        scientific_logic="""1. Character Idiolect Stylometry & Lexical Rarity:
   Vocabulary uniqueness for character $C$ dialogue tokens $V_C$ against overall corpus $V_{\\text{corpus}}$:
   $$\\text{Uniqueness}(C) = \\frac{1}{|V_C|} \\sum_{w \\in V_C} -\\log_2 P_{\\text{corpus}}(w)$$

2. POV Voice Bleed Detection:
   Computes cosine similarity between token frequency vectors of POV character chapters:
   $$\\text{Similarity}(C_1, C_2) = \\frac{\\vec{v}_1 \\cdot \\vec{v}_2}{\\|\\vec{v}_1\\| \\|\\vec{v}_2\\|}$$
   Values $\\text{Similarity} > 0.88$ indicate severe voice bleed (characters sound identical).""",
        why_this_way="When all characters sound like the author, multi-POV stories lose immersion. Idiolect stylometry ensures a gruff dwarf warrior speaks with distinct sentence cadence and vocabulary compared to a court scholar.",
        worldbuilding_relevance="Reflects character social class, regional origins, and professional guilds through distinct dialogue registers.",
        storytelling_relevance="Ensures reader immediately knows who is speaking without relying on dialogue tags.",
        writing_relevance="Prevents all characters from sounding like the author.",
        subfeatures=[
            {"name": "Idiolect Uniqueness Scorer", "rule": "Measures lexical rarity and vocabulary signature per character.", "example": "arcanum audit voice Manuscript/ --characters"},
            {"name": "Voice Bleed Matrix", "rule": "Compares pairwise dialogue similarity between all POV protagonists.", "example": "arcanum audit voice Manuscript/ --bleed-check"},
        ],
        extension_guide="""Configure voice profiles in `World/Characters/jennifer.md`:
```yaml
voice_profile:
  formality: 0.85 # High formality, courtly
  sentence_cadence: "long-flowing"
  verbal_tics: ["Indeed", "Preposterous", "Furthermore"]
  forbidden_slang: ["gonna", "wanna", "ain't"]
```""",
        advisory_guidance=[
            {"pattern": "Two POV characters share nearly identical vocabulary and sentence cadence (voice bleed)", "option_a": "Diversify idiolects with unique verbal tics, catchphrases, and sentence lengths", "option_b": "Frame shared voice as cultural upbringing or shared military academy training", "option_c": "Retain consistent authorial voice across ensemble cast"},
        ],
    ),

    "conlang": EngineSpec(
        name="conlang",
        category=EngineCategory.CRAFT,
        title="Conlang Phonotactics & Lexicon",
        description="Phoneme inventory generator, sound-law shift simulator, Leipzig glossing, and constructed vocabulary builder",
        module_name="lib.conlang",
        cli_command="conlang",
        aliases=["conlang", "linguistics", "phonotactics"],
        studio_tab="Worldbuilding",
        logic_documentation="Generates phonotactic syllable structures (CV, CVC, CCV), enforces Sonority Sequencing, models historical sound-shift mutations (Grimm's Law), and parses Leipzig 3-line interlinear glosses.",
        scientific_logic="""1. Syllable Phonotactics & Sonority Sequencing Principle (SSP):
   Syllable template (e.g. $(C_1)(C_2)V(C_3)$). Sonority scale:
   $$\\text{Vowels (5)} > \\text{Glides (4)} > \\text{Liquids (3)} > \\text{Nasals (2)} > \\text{Fricatives (1)} > \\text{Stops (0)}$$
   Onsets must rise in sonority towards nucleus; codas must fall in sonority.

2. Neogrammarian Sound Shift Engine (Grimm's & Verner's Laws):
   Regular regex rewrite rules applied sequentially across ancestral proto-lexicon:
   - Proto-Germanic Grimm's Law: $p \\to f, t \\to \\theta, k \\to h$.
   - Intervocalic Lenition: $V[p, t, k]V \\to V[b, d, g]V$.

3. Leipzig 3-Line Interlinear Glossing Rules:
   - Line 1: Source language text (`Dó-m-un-a k-el-a`)
   - Line 2: Grammatical morpheme gloss (`house-LOC-DEF.SG walk-PST-3SG`)
   - Line 3: Free English translation (`'He walked in the house.'`)""",
        why_this_way="Randomly made-up fantasy words look like keyboard mash and lack cultural authenticity. The conlang engine ensures phonetic harmony, realistic sound shifts across centuries, and structured grammar.",
        worldbuilding_relevance="Creates distinct, culturally grounded naming conventions for characters, places, and relics.",
        storytelling_relevance="Brings linguistic diversity to life; language barriers and translation puzzles create story intrigue.",
        writing_relevance="Generates evocative names and authentic in-universe idioms with phonetic harmony.",
        subfeatures=[
            {"name": "Phonotactic Syllable Generator", "rule": "Generates natural-sounding words adhering to custom phoneme inventories.", "example": "arcanum conlang gen HighElven --count 20"},
            {"name": "Historical Sound Shift Simulator", "rule": "Mutates proto-language roots into modern daughter dialects.", "example": "arcanum conlang mut ProtoElven ModernElven --rules 'p>f, k>h'"},
            {"name": "Leipzig Gloss Parser", "rule": "Parses and validates 3-line interlinear linguistic glosses in lore notes.", "example": "arcanum conlang gloss 'Dó-m-un-a k-el-a'"},
        ],
        extension_guide="""Create a conlang specification in `World/Languages/valyrian.yaml`:
```yaml
conlang:
  name: "High Valyrian"
  phonemes:
    consonants: ["p", "t", "k", "b", "d", "g", "m", "n", "r", "l", "s", "z", "v"]
    vowels: ["a", "e", "i", "o", "u", "y"]
  syllable_template: "CVC"
  sound_shifts:
    - "k > h / _#"
    - "p > f / V_V"
```""",
        advisory_guidance=[
            {"pattern": "Word violates language phonotactic syllable template", "option_a": "Adjust spelling to match phonotactic inventory", "option_b": "Classify word as ancient loanword or foreign dialect term", "option_c": "Retain spelling as an authorial artistic flourish"},
        ],
    ),

    "genealogy": EngineSpec(
        name="genealogy",
        category=EngineCategory.CRAFT,
        title="Dynastic Lineage & Genealogy",
        description="Family tree compilation, succession rank calculator, Wright's inbreeding coefficient, and Mermaid diagrams",
        module_name="lib.genealogy",
        cli_command="genealogy",
        aliases=["genealogy", "lineage", "dynasty"],
        studio_tab="Worldbuilding",
        logic_documentation="Calculates Wright's inbreeding coefficient (F), evaluates succession laws (Salic, Primogeniture, Ultimogeniture, Tanistry, Gavelkind), resolves cadet branch cadency, and exports Mermaid family trees.",
        scientific_logic="""1. Wright's Inbreeding Coefficient $F$:
   $$F = \\sum \\left(\\frac{1}{2}\\right)^{n_1 + n_2 + 1} (1 + F_A)$$
   Where $n_1, n_2$ are generations from each parent back to common ancestor $A$, and $F_A$ is the inbreeding coefficient of ancestor $A$.

2. Succession Law Priority Evaluators:
   - Agnatic (Salic) Primogeniture: Strictly through eldest male lines.
   - Male-Preference Primogeniture: Daughters inherit only if no surviving sons exist.
   - Absolute Cognatic Primogeniture: Eldest child regardless of gender.
   - Ultimogeniture: Youngest child inherits.
   - Tanistry: Noble clan council elects most capable adult heir.
   - Gavelkind: Realm partitioned equally among all surviving heirs.""",
        why_this_way="Dynastic civil wars and succession crises are central to fantasy epics. Automatically computing inheritance claims and inbreeding coefficients prevents plot holes in royal genealogies.",
        worldbuilding_relevance="Builds noble lineages, royal marriage alliances, and inheritance claim hierarchies.",
        storytelling_relevance="Drives succession crises, bastard claims, civil wars, and ancestral destiny arcs.",
        writing_relevance="Keeps generational relationships, honorific titles, and family kinship accurate.",
        subfeatures=[
            {"name": "Succession Claim Roster", "rule": "Calculates claimant rankings under Salic, Cognatic, or Gavelkind laws.", "example": "arcanum genealogy --house 'Voss' --succession salic"},
            {"name": "Wright Inbreeding Calculator", "rule": "Computes coefficient of kinship F across noble marriages.", "example": "arcanum genealogy --inbreeding 'Kaelen' 'Lyra'"},
            {"name": "Mermaid Tree Exporter", "rule": "Compiles family trees into visual Mermaid flowchart markdown.", "example": "arcanum genealogy --house 'Voss' --mermaid"},
        ],
        extension_guide="""Link characters via frontmatter parentage tags:
```yaml
---
name: "Crown Prince Valerius"
house: "House Aethelgard"
father: "King Alden III"
mother: "Queen Eleanor"
birth_year: 1418
succession_status: "Primary Heir"
---
```""",
        advisory_guidance=[
            {"pattern": "Disputed succession claim between multiple primary heirs", "option_a": "Clarify legal succession law precedence", "option_b": "Use the disputed claim as the catalyst for dynastic civil war", "option_c": "Retain ambiguity as a central plot mystery"},
        ],
    ),

    "factions": EngineSpec(
        name="factions",
        category=EngineCategory.CRAFT,
        title="Geopolitical Factions & Diplomacy",
        description="Diplomatic relation matrices, tension paradox detection, alliance networks, and Lanchester square-law",
        module_name="lib.factions",
        cli_command="faction",
        aliases=["faction", "factions", "diplomacy"],
        studio_tab="Worldbuilding",
        logic_documentation="Evaluates balance-of-power coalitions, diplomatic tension paradoxes, espionage network infiltration, and Lanchester square-law military strength ratios.",
        scientific_logic="""1. Geopolitical Relation Affinity Matrix:
   Relation state $R(A, B) \\in \\{\\text{Allied (+2)}, \\text{Friendly (+1)}, \\text{Neutral (0)}, \\text{Suspicious (-1)}, \\text{Hostile (-2)}, \\text{Active War (-3)}\\}$.

2. Balance-of-Power Coalition Dynamics:
   If faction $X$ military power $P(X) > \\sum_{Y \\ne X} P(Y)$, smaller factions form balancing coalitions:
   $$\\text{Coalition Affinity } C(A, B) \\propto P(\\text{Hegemon}) - R(A, B)$$

3. Diplomatic Paradox Detection:
   Flags triangular intransitivities: $A$ allied with $B$, $B$ allied with $C$, but $A$ at war with $C$ (triggers diplomatic treaty crisis).""",
        why_this_way="Political intrigue narratives thrive on complex alliances, trade embargoes, and proxy conflicts.",
        worldbuilding_relevance="Structures geopolitical factions, noble houses, knightly orders, and shadow syndicates.",
        storytelling_relevance="Powers political intrigue, betrayal, treaty negotiations, and shifting war alliances.",
        writing_relevance="Informs court dialogue, diplomatic etiquette, and heraldic protocol.",
        subfeatures=[
            {"name": "Diplomatic Paradox Sweeper", "rule": "Finds conflicting treaty obligations and proxy war traps.", "example": "arcanum faction World/ --audit-treaties"},
            {"name": "Alliance Matrix Exporter", "rule": "Exports color-coded diplomatic relation matrix.", "example": "arcanum faction World/ --html dist/diplomacy.html"},
        ],
        extension_guide="""Define factions in `World/Factions/iron_covenant.yaml`:
```yaml
faction:
  name: "Iron Covenant"
  type: "Military Theocracy"
  power_index: 85
  relations:
    "Silver Guild": "Hostile"
    "Crown Coalition": "Allied"
    "Shadow Synod": "Active War"
```""",
        advisory_guidance=[
            {"pattern": "Faction simultaneously marked as active ally and at war", "option_a": "Update relationship to formal state of war or truce", "option_b": "Frame as a covert proxy conflict under public alliance", "option_c": "Retain as a fragile political double-game"},
        ],
    ),

    "economy": EngineSpec(
        name="economy",
        category=EngineCategory.CRAFT,
        title="Macroeconomics & Currencies",
        description="In-world fiat/specie exchange rates, Purchasing Power Parity (PPP), commodity baskets, and Gresham's Law",
        module_name="lib.economy",
        cli_command="economy",
        aliases=["economy", "currency", "prices"],
        studio_tab="Worldbuilding",
        logic_documentation="Models Gresham's Law (coinage debasement), Purchasing Power Parity (PPP) commodity price baskets, trade arbitrage margins, and fractional reserve promissory notes.",
        scientific_logic="""1. Gresham's Law & Coinage Debasement:
   When government debases coinage silver content from $\\text{Ag}_1$ to $\\text{Ag}_2 < \\text{Ag}_1$, bad money drives out good:
   $$\\text{Velocity}(\\text{Debased}) \\gg \\text{Velocity}(\\text{Pure}), \\quad \\text{Hoarding Rate } H \\propto (\\text{Ag}_1 - \\text{Ag}_2)$$

2. Purchasing Power Parity (PPP) & Commodity Basket Index:
   Price level $P$ derived from canonical basket (1 bushel wheat, 1 gallon ale, 1 wool cloak, 1 iron horseshoe):
   $$P_{\\text{region}} = \\sum_{i=1}^m w_i \\cdot p_i, \\quad \\text{Exchange Rate } E(A, B) = \\frac{P_A}{P_B}$$

3. Trade Route Arbitrage & Transport Costs:
   Commodity price gap between origin $O$ and market $M$: $\\Delta P = P_M - P_O - \\text{Carriage Cost} - \\text{Tariffs}$. Arbitrage occurs when $\\Delta P > 0$.""",
        why_this_way="Fantasy economies often feature runaway inflation or wildly unrealistic pricing (e.g. an inn room costing more than a warhorse). Grounding prices in agricultural labor and commodity baskets creates economic coherence.",
        worldbuilding_relevance="Establishes currency exchange rates, guild price-fixing, tax burdens, and black markets.",
        storytelling_relevance="Economic inequality, debt, tariffs, and contraband smuggling fuel plot stakes and character motivations.",
        writing_relevance="Provides realistic pricing for tavern meals, horse rentals, sword forging, and carriage fares.",
        subfeatures=[
            {"name": "Commodity Price Calculator", "rule": "Calculates realistic historical purchasing power and trade goods prices.", "example": "arcanum economy --price 'Warhorse' --region 'Borderlands'"},
            {"name": "Coinage Debasement Simulator", "rule": "Simulates inflation and coin clipping economic crises.", "example": "arcanum economy --debase 'Silver Crown' --silver-loss 25%"},
        ],
        extension_guide="""Define currencies and prices in `World/Economy/currencies.yaml`:
```yaml
currencies:
  - name: "Imperial Gold Sovereign"
    specie_mass_g: 8.5
    purity: 0.92 # 22k gold
    exchange_to_copper: 240
  - name: "Silver Mark"
    specie_mass_g: 12.0
    purity: 0.85
    exchange_to_copper: 20
commodity_basket:
  loaf_bread_copper: 1
  ale_flagon_copper: 2
  riding_horse_copper: 2400
```""",
        advisory_guidance=[
            {"pattern": "Extreme commodity price disparity across open border markets", "option_a": "Rebalance prices toward equilibrium considering carriage costs", "option_b": "Explain gap by wartime blockade, banditry, or guild monopolies", "option_c": "Retain disparity to emphasize regional isolation"},
        ],
    ),

    "tactical_sim": EngineSpec(
        name="tactical_sim",
        category=EngineCategory.CRAFT,
        title="Tactical Skirmish & Battle Simulator",
        description="Lanchester linear and square-law combat models, terrain modifiers, morale decay, and casualty simulation",
        module_name="lib.tactical_sim",
        cli_command="sim battle",
        aliases=["battle", "sim", "combat", "tactical"],
        studio_tab="Worldbuilding",
        logic_documentation="Simulates Lanchester linear and square-law combat dynamics, terrain modifiers (castle walls, dense forest, river crossings), unit morale rout thresholds, and blow-by-blow narrative choreography logs.",
        scientific_logic="""1. Lanchester Linear Law (Ancient Aimless / Melee Duels):
   $$\\frac{dx}{dt} = -\\beta y, \\quad \\frac{dy}{dt} = -\\alpha x \\quad \\Longrightarrow \\quad \\alpha(x_0^2 - x^2) = \\beta(y_0^2 - y^2)$$

2. Lanchester Square Law (Ranged Targeted Fire / Modern Arms):
   $$\\frac{dx}{dt} = -\\beta y, \\quad \\frac{dy}{dt} = -\\alpha x \\quad \\Longrightarrow \\quad \\alpha(x_0^2 - x^2) = \\beta(y_0^2 - y^2)$$
   Concentration of force scales quadratically: 2,000 archers defeating 1,000 archers retain $\\sqrt{2000^2 - 1000^2} \\approx 1,732$ survivors (only 268 casualties).

3. Morale Thresholds & Rout Mechanics:
   Units rout when casualties exceed discipline threshold (Militia $15\\%$, Veteran Infantry $35\\%$, Elite Guard $60\\%$), multiplying retreating casualties threefold due to rearguard collapse.""",
        why_this_way="Authors often depict heroic underdogs wiping out massive armies without explaining tactical terrain advantages or force multipliers.",
        worldbuilding_relevance="Determines realistic army sizes, siege durations, supply requirements, and military logistics.",
        storytelling_relevance="Choreographs dramatic duels and large-scale battle turning points with tactical realism.",
        writing_relevance="Supplies visceral combat beats: weapon reach advantages, shield bracing, fatigue, armor dents.",
        subfeatures=[
            {"name": "Lanchester Battle Resolver", "rule": "Simulates skirmishes and sieges with terrain and ranged multipliers.", "example": "arcanum sim battle --force-a 5000 --force-b 3000 --fortified"},
            {"name": "Choreography Beat Generator", "rule": "Produces narrative chronological log of cavalry flanking and rout moments.", "example": "arcanum sim battle --narrative-log"},
        ],
        extension_guide="""Run a battle simulation from CLI:
```bash
arcanum sim battle --force-a 1200 --force-b 800 --terrain mountain-pass --flank
```""",
        advisory_guidance=[
            {"pattern": "Small infantry militia defeats superior armored cavalry in open field without terrain advantage", "option_a": "Add terrain bottleneck (mud, pikes, trenches) to justify victory", "option_b": "Ground victory via surprise flanking, magical artillery, or cavalry panic", "option_c": "Retain outcome as heroic against-all-odds underdog victory"},
        ],
    ),

    "magic_system": EngineSpec(
        name="magic_system",
        category=EngineCategory.CRAFT,
        title="Magic System Constraints",
        description="Brandon Sanderson's Three Laws of Magic, mana conservation, sympathetic backlash, and caster fatigue tier validator",
        module_name="lib.magic_system",
        cli_command="magic-check",
        aliases=["magic-report", "magic", "arcana", "spells"],
        studio_tab="Worldbuilding",
        logic_documentation="Evaluates magic systems against Brandon Sanderson's Three Laws of Magic, tracks energy conservation, calculates sympathetic backlash, and monitors caster fatigue tier limits.",
        scientific_logic="""1. Brandon Sanderson's Three Laws of Magic:
   - First Law: An author's ability to solve problems with magic in a satisfying way is directly proportional to how well the reader understands said magic.
   - Second Law: Limitations > Powers (Weaknesses, costs, and failure modes create dramatically compelling conflict).
   - Third Law: Expand what you already have before you add something new (deep combinatorial extrapolation of existing magic axioms).

2. Thermodynamic Energy Conservation & Sympathetic Backlash:
   Magic cannot create energy from void; it transforms or transfers energy:
   $$\\Delta E_{\\text{spell}} = E_{\\text{source}} - \\text{Heat Dissipation Loss} - \\text{Backlash Strain}$$
   Casting kinetic energy requires thermal or chemical absorption; caster blood chills or veins burn as metabolic price.

3. Caster Fatigue Tier State Machine:
   $$\\text{Tier 1 (Effortless)} \\longrightarrow \\text{Tier 2 (Straining)} \\longrightarrow \\text{Tier 3 (Exhaustion / Epistaxis)} \\longrightarrow \\text{Tier 4 (Arcane Burnout / Coma)}$$""",
        why_this_way="Soft magic used to solve plot climaxes feels unearned and cheap. Hard magic with rigorous costs and limitations creates gripping puzzle-solving tension.",
        worldbuilding_relevance="Integrates arcane arts into society, military doctrine, education, and economy.",
        storytelling_relevance="Ensures magic creates satisfying problem-solving tension rather than unearned convenience.",
        writing_relevance="Provides visceral somatic magic details: burning blood, glowing glyphs, mana chills, spell exhaustion.",
        subfeatures=[
            {"name": "Sanderson Three Laws Auditor", "rule": "Checks whether magical solutions in climaxes were properly foreshadowed.", "example": "arcanum magic-check Manuscript/ --sanderson"},
            {"name": "Arcane Cost & Backlash Ledger", "rule": "Tracks spell energy accounting and somatic caster costs across scenes.", "example": "arcanum magic-report World/ --costs"},
        ],
        extension_guide="""Define magic axioms in `World/MagicSystems/blood_alchemy.yaml`:
```yaml
magic_system:
  name: "Blood Alchemy"
  type: "Hard Arcane"
  axioms:
    - "Transmutation requires equivalent mass in organic substrate"
    - "Caster experiences metabolic fever proportional to transformed mass"
  limitations:
    - "Cannot transmute noble metals (gold, silver)"
    - "Requires direct somatic skin contact"
  costs:
    fatigue_burn_rate: "Medium"
    backlash_risk: "High upon concentration loss"
```""",
        advisory_guidance=[
            {"pattern": "Spell cast without required reagent or exceeding caster tier", "option_a": "Enforce standard spell failure or severe magical backlash", "option_b": "Frame as a dangerous life-force sacrifice or divine breakthrough", "option_c": "Permit the surge as a pivotal dramatic miracle"},
        ],
    ),

    # =========================================================================
    # DOMAIN D: STYLISTICS, SENSORY IMMERSION & EDITORIAL POLISH
    # =========================================================================
    "stylistics": EngineSpec(
        name="stylistics",
        category=EngineCategory.CRAFT,
        title="Stylistics & Readability Audits",
        description="Flesch-Kincaid grade level, passive voice detector, nominalizations ('zombie nouns'), filter words, and echo words",
        module_name="lib.stylistics",
        cli_command="audit style",
        aliases=["stylistics", "style", "readability", "polish-style"],
        studio_tab="Craft",
        logic_documentation="Evaluates Flesch-Kincaid grade level, passive voice constructions, nominalizations ('zombie nouns'), filter words ('she heard', 'he saw'), echo word repetitions within sliding windows, and said-bookisms.",
        scientific_logic="""1. Flesch-Kincaid Grade Level & Reading Ease:
   $$\\text{FKGL} = 0.39 \\left(\\frac{\\text{total words}}{\\text{total sentences}}\\right) + 11.8 \\left(\\frac{\\text{total syllables}}{\\text{total words}}\\right) - 15.59$$
   $$\\text{FRE} = 206.835 - 1.015 \\left(\\frac{\\text{words}}{\\text{sentences}}\\right) - 84.6 \\left(\\frac{\\text{syllables}}{\\text{words}}\\right)$$
   Genre benchmarks: Epic Fantasy ($7.5\\text{--}9.5$), Thriller ($6.0\\text{--}7.5$), Literary Fiction ($9.0\\text{--}12.0$).

2. Nominalization ('Zombie Noun') Detection:
   Flags verbs smothered into abstract nouns (e.g. 'made an investigation into' $\to$ 'investigated'; 'reached an agreement' $\to$ 'agreed').

3. Filter Words & Psychic Distance Stripper:
   Flags sensory distance filters ('She saw the door open' $\to$ 'The door flew open'; 'He heard thunder roll' $\to$ 'Thunder rolled') to bring readers directly into character consciousness.

4. Sliding Window Echo Repetition:
   Detects non-trivial lexical words repeated within a $W$-word sliding window ($W = 150$ words).""",
        why_this_way="Passive voice, excessive filter words, and unintentional echo words dilute prose power and increase psychic distance between reader and character.",
        worldbuilding_relevance="Ensures fantasy prose maintains an appropriate, immersive reading level.",
        storytelling_relevance="Tightens narrative voice, accelerates reader velocity, and eliminates psychic distance.",
        writing_relevance="Provides actionable line-editing recommendations that elevate draft quality.",
        subfeatures=[
            {"name": "Flesch-Kincaid Readability Auditor", "rule": "Computes grade level, sentence syllable complexity, and reading ease.", "example": "arcanum audit style Manuscript/ --readability"},
            {"name": "Filter Word Stripper", "rule": "Flags sensory distance filters to establish deep POV immersion.", "example": "arcanum audit style Manuscript/ --filter-words"},
            {"name": "Sliding Window Echo Finder", "rule": "Highlights non-trivial word repetitions within 150-word passages.", "example": "arcanum audit style Manuscript/ --echoes"},
        ],
        extension_guide="""Run stylistics audit from CLI:
```bash
arcanum audit style Manuscript/ --html dist/stylistics_report.html
```""",
        advisory_guidance=[
            {"pattern": "High filter word density ('she realized', 'he noticed')", "option_a": "Strip filter words for direct psychic immersion", "option_b": "Retain filter words to emphasize deliberate detective observation", "option_c": "Preserve for distant narrator stylistic voice"},
        ],
    ),

    "senses": EngineSpec(
        name="senses",
        category=EngineCategory.CRAFT,
        title="Sensory Immersion Heatmap",
        description="Distribution of visual, auditory, olfactory, gustatory, tactile, kinesthetic, and interoceptive prose",
        module_name="lib.senses",
        cli_command="audit senses",
        aliases=["senses", "sensory", "immersion", "white-room"],
        studio_tab="Craft",
        logic_documentation="Scans prose across 8 sensory dimensions (Visual, Auditory, Olfactory, Gustatory, Tactile/Thermal, Kinesthetic/Proprioception, Equilibrium, Interoception) to prevent White Room Syndrome.",
        scientific_logic="""1. 8-Dimensional Sensory Palette Vector:
   Prose scanned across 8 somatic sensory channels:
   - Visual: Color, illumination, shadow, reflection, silhouette.
   - Auditory: Pitch, timbre, reverberation, murmur, clash, silence.
   - Olfactory: Ozone, sulfur, pine damp, decay, roasted grain.
   - Gustatory: Bitter copper, brine, sweet nectar, ash.
   - Tactile / Thermal: Grit, velvet, searing heat, freezing draft.
   - Kinesthetic / Proprioception: Muscle strain, weight, momentum.
   - Vestibular / Equilibrium: Vertigo, dizziness, weightlessness.
   - Interoception: Heart racing, hollow stomach, adrenaline surge.

2. White Room Syndrome Diagnostic Index:
   Scenes where $\\text{Visual} > 90\\%$ and other sensory dimensions $< 10\\%$ are flagged as sterile 'talking heads in a void'.""",
        why_this_way="Writers frequently rely 95% on visual descriptions, ignoring smell, touch, sound, and internal visceral sensations that anchor deep physical immersion.",
        worldbuilding_relevance="Gives each fantasy/sci-fi location a unique sensory signature (tavern smoke, dungeon damp, desert sulfur).",
        storytelling_relevance="Enhances immersion during climaxes by intensifying sensory density.",
        writing_relevance="Flags visual-only exposition and reminds writers to engage smell, sound, and physical touch.",
        subfeatures=[
            {"name": "8-Channel Sensory Scanner", "rule": "Measures sensory vocabulary density across all 8 biological modalities.", "example": "arcanum audit senses Manuscript/01_Chapter.md"},
            {"name": "White Room Syndrome Sweeper", "rule": "Flags sensory-starved scenes lacking auditory, olfactory, or tactile details.", "example": "arcanum audit senses Manuscript/ --white-room"},
        ],
        extension_guide="""Run sensory immersion audit from CLI:
```bash
arcanum audit senses Manuscript/ --html dist/sensory_heatmap.html
```""",
        advisory_guidance=[
            {"pattern": "Scene has zero auditory or olfactory sensory grounding", "option_a": "Add atmospheric background sounds and scent profiles", "option_b": "Frame sensory absence as character dissociation or sterile environment", "option_c": "Keep sparse sensory style for brisk action velocity"},
        ],
    ),

    "continuity": EngineSpec(
        name="continuity",
        category=EngineCategory.CRAFT,
        title="Semantic Continuity & Trait Linter",
        description="Local-first semantic narrative continuity analyzer cross-validating character traits across drafts",
        module_name="lib.continuity",
        cli_command="continuity",
        aliases=["continuity", "check-continuity", "traits"],
        studio_tab="Diagnostics",
        logic_documentation="Extracts character physical traits (eyes, hair, titles, status) from World Bible files and sentence-level manuscript scenes, detecting character trait drift, impossible contradictions, and inter-scene inconsistencies.",
        scientific_logic="""1. Semantic Entity-Trait Extraction Graph:
   Extracts canonical trait tuples $(E, T, V)$ from World Bible (e.g. $(\\text{Kaelen}, \\text{eye\\_color}, \\text{grey-blue})$).

2. Manuscript Surface Assertion Cross-Validation:
   NLP pattern sweeps extract asserted traits in scenes: $(\\text{Kaelen}, \\text{eye\\_color}, \\text{green})$.
   When asserted value $V_{\\text{scene}} \\ne V_{\\text{canon}}$, a continuity conflict is flagged with line citations.""",
        why_this_way="In 100,000+ word novels written over months, authors accidentally change eye color, handedness, or titles between chapters.",
        worldbuilding_relevance="Ensures character traits established in lore dossiers are maintained in prose.",
        storytelling_relevance="Catches accidental continuity discrepancies before publication.",
        writing_relevance="Provides clear advisory alerts with multiple creative resolution pathways.",
        subfeatures=[
            {"name": "Trait Inconsistency Auditor", "rule": "Cross-checks eye color, hair, scars, and handedness between lore and scenes.", "example": "arcanum continuity -w World/ -m Manuscript/"},
            {"name": "Inventory & Relic Tracker", "rule": "Audits weapon and gear retention across scenes.", "example": "arcanum continuity -w World/ -m Manuscript/ --gear"},
        ],
        extension_guide="""Run continuity checker:
```bash
arcanum continuity -w World/ -m Manuscript/
```""",
        advisory_guidance=[
            {"pattern": "Character eye color asserted as green in scene but blue in World Bible", "option_a": "Correct scene prose to match World Bible canonical blue eyes", "option_b": "Ground color shift in story (e.g. illusion, colored contact, magical flare)", "option_c": "Update World Bible dossier if the author intentionally changed character design"},
        ],
    ),

    "series_continuity": EngineSpec(
        name="series_continuity",
        category=EngineCategory.CRAFT,
        title="Series Continuity Ledger",
        description="Tracks recurring character traits, scars, eye color, and gear across multi-volume series",
        module_name="lib.series_continuity",
        cli_command="series",
        aliases=["series", "series-continuity", "ledger"],
        studio_tab="Worldbuilding",
        logic_documentation="Tracks character physical traits (handedness, scars, eye color), relic chains of custody, biological aging across timeskips, and geopolitical world-state changes across multi-book sagas.",
        scientific_logic="""1. Cross-Volume State Mutation Ledger:
   Tracks immutable historical facts across multi-book sagas:
   $$\\text{Volume 1 State } S_1 \\xrightarrow{\\text{Timeskip } \\Delta T} \\text{Volume 2 State } S_2 \\xrightarrow{} \\text{Volume 3 State } S_3$$
   Validates character biological aging ($A_2 = A_1 + \\Delta T$), relic custody handoffs, and scar permanence.""",
        why_this_way="Multi-volume series are vulnerable to retcons and forgotten character wounds across years of writing.",
        worldbuilding_relevance="Ensures multi-volume world lore remains coherent as empires rise and fall.",
        storytelling_relevance="Maintains character scars, trauma, and power progression across decades of story time.",
        writing_relevance="Prevents embarrassing retcons and continuity errors between Book 1 and Book 5.",
        subfeatures=[
            {"name": "Cross-Volume Trait Ledger", "rule": "Ensures character traits and physical scars carry over across books.", "example": "arcanum series --ledger-check"},
            {"name": "Timeskip Aging Validator", "rule": "Audits biological ages against world calendar timeskips.", "example": "arcanum series --aging-check"},
        ],
        extension_guide="""Define series-level invariants in `World/Series/series_ledger.yaml`:
```yaml
series_ledger:
  volumes: ["Book 1", "Book 2", "Book 3"]
  relics:
    - name: "Sunblade"
      custody:
        "Book 1": "King Alden (Lost in Chapter 14)"
        "Book 2": "Kaelen Voss (Found in Vault)"
```""",
        advisory_guidance=[
            {"pattern": "Character eye color or handedness changed between volumes", "option_a": "Revert to Book 1 canonical trait", "option_b": "Ground change in story event (e.g. magical scarring, injury, disguise)", "option_c": "Acknowledge and retain as an intentional character transformation"},
        ],
    ),

    "typography_cleaner": EngineSpec(
        name="typography_cleaner",
        category=EngineCategory.CORE,
        title="Typography Cleaner",
        description="Normalizes smart curly quotes, em-dashes, and typographical ellipses",
        module_name="lib.typography_cleaner",
        cli_command="polish typography",
        aliases=["clean-typography", "polish", "typography"],
        studio_tab="Editor",
        logic_documentation="Applies Chicago Manual of Style (CMOS) and Oxford typographical rules: converts straight quotes to curly quotes, double hyphens to em-dashes, and triple periods to true ellipses.",
        scientific_logic="""1. Chicago Manual of Style (CMOS 17th Ed) / Oxford Typography Rules:
   - Straight quotes `' '` and `" "` normalized to typographical curly quotes `‘ ’` and `“ ”` with opening/closing whitespace heuristics.
   - Double hyphens `--` converted to unspaced true em-dashes `—`.
   - Triple periods `...` converted to Unicode horizontal ellipsis `…`.
   - Dialogue punctuation: Dialogue tags properly lowercased after commas (`“Wait,” he said.` vs `“Wait!” He ran.`).""",
        why_this_way="Straight typewriter quotes and double hyphens look amateurish in published ebooks and print books. Automated typographical normalization elevates prose to professional literary standards.",
        worldbuilding_relevance="Handles in-universe punctuation rules (e.g. alien glottal stops vs quotation marks).",
        storytelling_relevance="Prevents jarring punctuation anomalies from pulling readers out of immersion.",
        writing_relevance="Gives prose a polished, traditionally published literary aesthetic in one click.",
        subfeatures=[
            {"name": "Smart Quotes Normalizer", "rule": "Converts straight quotes to typographical curly quotes with contraction handling.", "example": "arcanum polish typography Manuscript/01_Chapter.md"},
            {"name": "Dialogue Comma Splice Linter", "rule": "Audits dialogue tag capitalization and comma placement.", "example": "arcanum polish typography Manuscript/ --audit-dialogue"},
        ],
        extension_guide="""Clean typography across a manuscript:
```bash
arcanum polish typography Manuscript/
```""",
        advisory_guidance=[
            {"pattern": "Unconventional dialogue punctuation (e.g. em-dash quotes or guillemets)", "option_a": "Normalize to standard CMOS quotation marks", "option_b": "Preserve European / custom dialogue conventions", "option_c": "Apply selectively per character dialect"},
        ],
    ),

    "manuscript_diff": EngineSpec(
        name="manuscript_diff",
        category=EngineCategory.CORE,
        title="Draft Diff & Visual Redline",
        description="Comparative redline changelog and visual diffs between manuscript drafts",
        module_name="lib.manuscript_diff",
        cli_command="compare",
        aliases=["diff", "redline", "changelog", "manuscript-diff"],
        studio_tab="Editor",
        logic_documentation="Computes Myers semantic diff algorithms between draft iterations (Draft-01 vs Draft-02), isolating word additions, deletions, paragraph moves, and dialogue changes.",
        scientific_logic="""1. Myers Semantic Diff Algorithm:
   Computes shortest edit script $SES$ and Longest Common Subsequence ($LCS$) between two draft text streams.
   Distinguishes prose additions ($+$), deletions ($-$), paragraph position relocations, and dialogue word rewrites.""",
        why_this_way="Standard git line diffs are unreadable for prose because changing one word refits an entire paragraph. Word-level semantic visual redlines clearly show creative revisions.",
        worldbuilding_relevance="Tracks when specific lore terms or character names were altered across revisions.",
        storytelling_relevance="Highlights major scene cuts, restructured chapters, and dialogue tightenings.",
        writing_relevance="Generates side-by-side visual HTML redline views with word churn statistics.",
        subfeatures=[
            {"name": "Visual Redline HTML Exporter", "rule": "Generates side-by-side green/red comparison view.", "example": "arcanum compare Manuscript/Draft-01 Manuscript/Draft-02 --html dist/redline.html"},
            {"name": "Excised Prose Scraps Vault", "rule": "Automatically extracts cut prose chunks (>50 words) into a reusable Scraps vault.", "example": "arcanum compare Manuscript/ --extract-scraps"},
        ],
        extension_guide="""Compare two drafts from CLI:
```bash
arcanum compare Manuscript/Draft-01 Manuscript/Draft-02
```""",
        advisory_guidance=[
            {"pattern": "Large block cut detected (>500 words)", "option_a": "Archive excised prose in Scraps/ folder for recycling", "option_b": "Review scene pacing to ensure no dropped plot threads", "option_c": "Accept cut as intentional tightening"},
        ],
    ),

    "revision_heatmap": EngineSpec(
        name="revision_heatmap",
        category=EngineCategory.CRAFT,
        title="Manuscript Revision Density & Churn Heatmap",
        description="Snapshot-based revision churn analyzer flagging over-revised (REV-101) and pristine-draft (REV-102) chapters",
        module_name="lib.revision_heatmap",
        cli_command="revision-heatmap",
        aliases=["churn", "revision-density", "draft-churn", "heatmap"],
        studio_tab="Diagnostics",
        logic_documentation="Analyzes historical snapshot diffs to compute sentence-level word churn ratios, distinguishing structural rewrites from polish edits and flagging over-revised vs pristine chapters.",
        scientific_logic="""1. Word Churn Ratio & Revision Density Metric:
   $$\\text{Churn Ratio } R = \\frac{\\text{Words Added} + \\text{Words Deleted}}{\\text{Total Chapter Words}}$$
   - REV-101 (Over-revised / Perfectionist Trap): Churn $> 120\\%$ across 5+ drafts with minimal plot progression.
   - REV-102 (Pristine / Under-revised): Churn $< 5\\%$ despite major developmental restructuring in adjacent chapters.""",
        why_this_way="Authors often get stuck endlessly rewriting Chapter 1 without making progress on later chapters. Churn heatmaps provide objective data on where editing effort is truly needed.",
        worldbuilding_relevance="Shows which lore sections underwent the heaviest conceptual overhauls.",
        storytelling_relevance="Identifies 'problem chapters' that have been endlessly rewritten without progress.",
        writing_relevance="Helps authors step away from perfectionist over-editing and move forward.",
        subfeatures=[
            {"name": "Chapter Churn Density Matrix", "rule": "Computes historical modification intensity per chapter.", "example": "arcanum revision-heatmap Manuscript/ --html dist/churn.html"},
            {"name": "Perfectionist Trap Detector", "rule": "Flags chapters with churn >120% across drafts.", "example": "arcanum revision-heatmap Manuscript/ --flag-traps"},
        ],
        extension_guide="""Run revision heatmap diagnostic:
```bash
arcanum revision-heatmap Manuscript/
```""",
        advisory_guidance=[
            {"pattern": "Chapter flagged with excessive revision churn (>80% word replacement across 5+ drafts)", "option_a": "Perform fresh developmental outline review of the scene's core goal", "option_b": "Lock the chapter and proceed to drafting subsequent chapters", "option_c": "Accept high churn as necessary stylistic exploration"},
        ],
    ),

    # =========================================================================
    # DOMAIN E: STUDIOS, AUTHORING COCKPITS & AUDIO FOCUS
    # =========================================================================
    "studio_hub": EngineSpec(
        name="studio_hub",
        category=EngineCategory.CORE,
        title="Sovereign Studio Desktop Hub & Dashboard",
        description="Master unified desktop and web orchestrator dashboard unifying all 50 craft engines",
        module_name="lib.studio_hub",
        cli_command="hub",
        aliases=["dashboard", "studio-hub", "gui-web", "hub"],
        studio_tab="Tools",
        logic_documentation="Master local-first web and desktop orchestrator providing live manuscript telemetry, lore entity cards, structural harmony curves, timeline paradox audits, and craft engine matrix.",
        scientific_logic="""1. Local-First Orchestration Architecture:
   Zero-dependency Python HTTP/WebSocket server running on localhost ($127.0.0.1$) serving 100% offline single-page application with strict Content Security Policy:
   `default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:; connect-src 'self';`

2. Real-Time Telemetry Extractor:
   Scans workspace ASTs on modification, updating word count milestones, reading time (200 wpm), narration time (150 wpm), and timeline bilocation paradox counters.""",
        why_this_way="Authors need a central, beautiful command cockpit to inspect their universe, drafts, and craft engines without relying on cloud services.",
        worldbuilding_relevance="Central command cockpit unifying all 50 domain engines into an intuitive GUI.",
        storytelling_relevance="Displays real-time project metrics: words, reading hours, chapters, and paradoxes.",
        writing_relevance="Runs 100% offline with zero external network calls or cloud dependencies.",
        subfeatures=[
            {"name": "Craft Science Encyclopedia Viewer", "rule": "Searchable interactive browser drawer detailing mathematical/physical logic and examples for all 50 engines.", "example": "arcanum hub --tab guide"},
            {"name": "Live Telemetry Dashboard", "rule": "Displays real-time word counts, reading hours, and timeline health.", "example": "arcanum hub"},
        ],
        extension_guide="""Launch Studio Hub on custom port:
```bash
arcanum hub --port 8085
```""",
        advisory_guidance=[
            {"pattern": "Port 8080 already bound by another process", "option_a": "Automatically increment to next available port (e.g. 8081)", "option_b": "Export standalone static HTML dashboard file", "option_c": "Launch desktop GTK window instead of web hub"},
        ],
    ),

    "zen_studio": EngineSpec(
        name="zen_studio",
        category=EngineCategory.CORE,
        title="Zen Drafting Studio",
        description="Distraction-free typewriter drafting cockpit with in-situ lore drawer and beat tracker",
        module_name="lib.zen_studio",
        cli_command="studio",
        aliases=["zen", "zen-studio", "editor"],
        studio_tab="Editor",
        logic_documentation="Zero-dependency, single-file offline HTML5 typewriter drafting environment featuring dark/sepia/light themes, live reading/speech telemetry, in-situ world lore drawer, and LocalStorage autosave.",
        scientific_logic="""1. Typewriter Scroll & Focus Ergonomics:
   Maintains active typing line centered vertically in viewport (50% screen height), eliminating neck strain.

2. In-Situ Lore Split Drawer:
   Allows instant full-text search across World Bible dossiers without breaking drafting flow or switching windows.

3. Offline LocalStorage Autosave:
   Saves buffer on every keystroke to browser LocalStorage with 1-click Markdown download backup.""",
        why_this_way="Cluttered word processors with hundreds of toolbars distract authors from flow state drafting. Zen Studio strips away all distractions while keeping lore reference at your fingertips.",
        worldbuilding_relevance="Allows writers to search character dossiers and magic rules without breaking drafting flow.",
        storytelling_relevance="Provides live chapter word counts and reading time estimates while drafting.",
        writing_relevance="Delivers a distraction-free, pure typewriter focus environment with 100% offline privacy.",
        subfeatures=[
            {"name": "Typewriter Mode", "rule": "Keeps active line centered with distraction-free dark/sepia themes.", "example": "arcanum studio Manuscript/01_Chapter.md"},
            {"name": "In-Situ Lore Drawer", "rule": "Slide-out drawer displaying character and location infoboxes.", "example": "arcanum studio Manuscript/ -w World/"},
        ],
        extension_guide="""Launch Zen Studio from CLI:
```bash
arcanum studio Manuscript/ -w World/
```""",
        advisory_guidance=[
            {"pattern": "Drafting in Zen Studio with unsaved local buffer changes", "option_a": "Auto-save changes to browser LocalStorage and disk", "option_b": "Download standalone Markdown export file", "option_c": "Discard local buffer and restore canonical disk state"},
        ],
    ),

    "ambient": EngineSpec(
        name="ambient",
        category=EngineCategory.CRAFT,
        title="Ambient Focus & Binaural Beats",
        description="Local offline sound synthesis for deep writing focus (binaural beats, rain, fire, library)",
        module_name="lib.ambient",
        cli_command="ambient",
        aliases=["ambient", "binaural", "focus-sound"],
        studio_tab="Tools",
        logic_documentation="Synthesizes pure offline procedural soundscapes using Python standard library and Web Audio API: brown noise, pink noise, binaural alpha/theta waves, rain, fireplace, and quiet library ambiance.",
        scientific_logic="""1. Procedural Noise Synthesis:
   - Brown Noise: Integrated white noise with $1/f^2$ spectral power density (deep soothing rumble for concentration).
   - Pink Noise: $1/f$ power density (balanced acoustic masking).

2. Binaural Beats Neuromodulation:
   Plays carrier frequency $f_c = 220\\text{ Hz}$ in left ear and $f_c + \\Delta f$ in right ear:
   - Alpha Waves ($\\Delta f = 10\\text{ Hz}$): Relaxed cognitive alertness and flow state.
   - Theta Waves ($\\Delta f = 6\\text{ Hz}$): Deep creative visualization and associative ideation.
   - Gamma Waves ($\\Delta f = 40\\text{ Hz}$): High-intensity analytical problem solving.""",
        why_this_way="Streaming ambient audio from YouTube or Spotify leaks privacy and requires internet. Procedural Web Audio synthesis runs 100% offline with zero bandwidth.",
        worldbuilding_relevance="Creates deep auditory immersion matching the environment being drafted.",
        storytelling_relevance="Assists authors in entering deep flow states for focused writing sessions.",
        writing_relevance="100% offline audio generator requiring no internet or external media files.",
        subfeatures=[
            {"name": "Binaural Beat Synthesizer", "rule": "Generates real-time 40Hz Gamma and 10Hz Alpha waves for deep focus.", "example": "arcanum ambient --binaural alpha"},
            {"name": "Procedural Soundscapes", "rule": "Web Audio synthesis of rain on parchment, crackling hearth, and library.", "example": "arcanum ambient rain"},
        ],
        extension_guide="""Play ambient focus audio:
```bash
arcanum ambient library --volume 0.7
```""",
        advisory_guidance=[
            {"pattern": "Audio playback requested in headless terminal environment", "option_a": "Generate WAV audio file for external local media player", "option_b": "Launch Web Audio synthesis in browser Studio Hub", "option_c": "Display visual Pomodoro focus timer without sound"},
        ],
    ),

    "portfolio": EngineSpec(
        name="portfolio",
        category=EngineCategory.CRAFT,
        title="Portfolio & Drafting Velocity",
        description="Multi-manuscript word count tracker, sprint pacing, and catalog overview dashboard",
        module_name="lib.portfolio",
        cli_command="portfolio",
        aliases=["portfolio", "catalog", "series-overview"],
        studio_tab="Overview",
        logic_documentation="Aggregates multi-book catalog analytics, lifetime drafting velocity, release pipeline Gantt milestones, and writing streak heatmaps.",
        scientific_logic="""1. Portfolio Multi-Book Velocity Aggregator:
   Aggregates total output across all series volumes:
   $$\\text{Total Words} = \\sum_{i=1}^M W_i, \\quad \\text{Lifetime Velocity} = \\frac{\\text{Total Words}}{\\text{Days Elapsed}}$$
   Forecasts completion dates based on 30-day moving average velocity.""",
        why_this_way="Authors managing multi-book series or shared universes need high-altitude catalog visibility over release pipelines.",
        worldbuilding_relevance="Tracks master lore integration across multi-book shared universes.",
        storytelling_relevance="Monitors series-level narrative arcs and production schedules.",
        writing_relevance="Celebrates daily word count milestones and sustains creative momentum.",
        subfeatures=[
            {"name": "Catalog Analytics Overview", "rule": "Displays word count, chapter counts, and completion percentages for all manuscripts.", "example": "arcanum portfolio Manuscripts/"},
            {"name": "Drafting Velocity Forecast", "rule": "Projects series completion milestones based on 30-day moving average.", "example": "arcanum portfolio Manuscripts/ --forecast"},
        ],
        extension_guide="""Run portfolio analysis:
```bash
arcanum portfolio Manuscripts/ --html dist/portfolio.html
```""",
        advisory_guidance=[
            {"pattern": "Drafting velocity lull detected (>14 days inactive)", "option_a": "Schedule a 15-minute low-pressure writing sprint", "option_b": "Switch focus to worldbuilding lore or character sketches", "option_c": "Acknowledge planned creative rest period"},
        ],
    ),

    # =========================================================================
    # DOMAIN F: RETRIEVAL, INTELLIGENCE & PIPELINE INFRASTRUCTURE
    # =========================================================================
    "local_rag": EngineSpec(
        name="local_rag",
        category=EngineCategory.CORE,
        title="Sovereign Local Semantic Retrieval",
        description="Hybrid TF-IDF vector space and SQLite FTS5 lore query engine with Reciprocal Rank Fusion",
        module_name="lib.local_rag",
        cli_command="rag",
        aliases=["query-lore", "semantic-search", "lore-query", "rag"],
        studio_tab="Tools",
        logic_documentation="Zero-dependency hybrid TF-IDF vector space and SQLite FTS5 BM25 search engine with Reciprocal Rank Fusion (RRF), hierarchical parent-child chunking, and local LLM context synthesis.",
        scientific_logic="""1. Hybrid Vector-Lexical Search with Reciprocal Rank Fusion (RRF):
   Combines SQLite FTS5 BM25 full-text rank $R_{\\text{FTS5}}$ with TF-IDF cosine similarity rank $R_{\\text{TFIDF}}$:
   $$\\text{RRF Score}(d) = \\frac{1}{60 + R_{\\text{FTS5}}(d)} + \\frac{1}{60 + R_{\\text{TFIDF}}(d)}$$

2. Hierarchical Parent-Child Chunking:
   Documents indexed in small 200-word child chunks for precise retrieval, resolving to full 1000-word parent sections for LLM context synthesis.

3. 100% Offline Air-Gapped Operation:
   Executes entirely via standard library SQLite and pure Python math without external network calls or remote embeddings.""",
        why_this_way="Cloud AI search leaks unpublished world lore and manuscript IP. Local RAG guarantees 100% air-gapped privacy and instantaneous sub-10ms retrieval.",
        worldbuilding_relevance="Answers complex lore queries instantly across tens of thousands of vault notes.",
        storytelling_relevance="Synthesizes relevant character backgrounds, magic constraints, and history before drafting.",
        writing_relevance="Empowers in-situ research without leaving the drafting cockpit.",
        subfeatures=[
            {"name": "Hybrid RRF Query Engine", "rule": "Fuses BM25 exact matching with TF-IDF semantic relevance.", "example": "arcanum rag 'How does blood magic exhaustion work?'"},
            {"name": "Context Pack Builder", "rule": "Assembles structured context dossiers for local LLM completion.", "example": "arcanum rag --context 'Battle of Dawn'"},
        ],
        extension_guide="""Query lore from CLI:
```bash
arcanum rag "What are the weaknesses of Frost Wyrms?"
```""",
        advisory_guidance=[
            {"pattern": "Ambiguous search query returns multiple cross-domain entities", "option_a": "Apply domain category filter (e.g. Characters, Magic)", "option_b": "Use Reciprocal Rank Fusion to synthesize top matches", "option_c": "Display interactive search disambiguation list"},
        ],
    ),

    "corpus_export": EngineSpec(
        name="corpus_export",
        category=EngineCategory.CORE,
        title="Universal Structured Corpus & RAG Exporter",
        description="Structured JSONL, SQLite FTS5 database, markdown summary digest exporter, and bidirectional vault restore",
        module_name="lib.corpus_export",
        cli_command="corpus",
        aliases=["corpus-export", "export-corpus", "rag-export", "corpus-restore"],
        studio_tab="Tools",
        logic_documentation="Exports complete universe lore and manuscript vaults into structured JSONL datasets, SQLite FTS5 relational databases, fine-tuning formats (Alpaca, ShareGPT), and cryptographically verified ZIP archives with bidirectional restoration.",
        scientific_logic="""1. Fine-Tuning & RAG Dataset Synthesis:
   Transpiles lore notes and manuscript scenes into instruction-tuning datasets:
   - Alpaca format: `{"instruction": "...", "input": "...", "output": "..."}`
   - ShareGPT / ChatML format: `{"messages": [{"role": "system", "content": "..."}, ...]}`

2. Cryptographic Integrity Archive:
   Exports ZIP/tarball bundles with SHA-256 manifest digests, enabling 100% loss-less bidirectional restore.""",
        why_this_way="Writers need data sovereignty and freedom from proprietary lock-in. Corpus export allows feeding custom lore into local fine-tuned LLMs or migrating between tools.",
        worldbuilding_relevance="Backs up and structures massive worldbuilding vaults into machine-readable datasets.",
        storytelling_relevance="Enables structured data analysis of character appearances and scene interactions.",
        writing_relevance="Guarantees permanent data portability with zero vendor lock-in.",
        subfeatures=[
            {"name": "JSONL Dataset Exporter", "rule": "Exports lore into Alpaca and ShareGPT fine-tuning datasets.", "example": "arcanum corpus World/ -f alpaca -o dist/dataset.jsonl"},
            {"name": "Bidirectional Vault Restore", "rule": "Restores full folder structure and frontmatter from verified archives.", "example": "arcanum corpus restore backup_2026.zip"},
        ],
        extension_guide="""Export structured dataset:
```bash
arcanum corpus World/ -f jsonl -o dist/lore_corpus.jsonl
```""",
        advisory_guidance=[
            {"pattern": "Export target archive already exists", "option_a": "Overwrite existing archive with new SHA-256 timestamped build", "option_b": "Create incremental delta export file", "option_c": "Prompt user for custom export destination"},
        ],
    ),

    "importer": EngineSpec(
        name="importer",
        category=EngineCategory.CORE,
        title="Batch Manuscript & Vault Importer",
        description="Batch importer for Scrivener, Word (.docx), Google Docs, and unstructured Markdown trees",
        module_name="lib.importer",
        cli_command="import",
        aliases=["importer", "import-manuscript", "scrivener-import"],
        studio_tab="Tools",
        logic_documentation="Converts external Scrivener projects, Word (.docx) documents, Google Docs, and raw Markdown folders into sovereign Ars Arcanum manuscript vaults with manifest metadata and novelWriter project files.",
        scientific_logic="""1. OpenXML / Scrivener XML AST Extraction:
   Parses Scrivener binder XML (`project.scrivx`) and Word OpenXML DOM structures, reconstructing hierarchical chapter trees and preserving synopsis cards and annotations.""",
        why_this_way="Migrating out of closed writing platforms is tedious and error-prone. The importer auto-splits monolithic manuscripts into clean, numbered chapter files.",
        worldbuilding_relevance="Auto-seeds initial world dossiers from imported character and location names.",
        storytelling_relevance="Splits monolithic manuscript files into clean, ordered chapter structures.",
        writing_relevance="Provides seamless migration from proprietary writing apps to sovereign Ars Arcanum.",
        subfeatures=[
            {"name": "Scrivener Project Importer", "rule": "Converts .scriv bundles into Ars Arcanum vaults.", "example": "arcanum import MyNovel.scriv"},
            {"name": "Monolithic Docx Chapter Splitter", "rule": "Splits Word documents by Heading 1 and scene breaks.", "example": "arcanum import draft.docx --split-chapters"},
        ],
        extension_guide="""Import a manuscript:
```bash
arcanum import path/to/project.scriv
```""",
        advisory_guidance=[
            {"pattern": "Monolithic manuscript file without chapter break headers", "option_a": "Auto-split at common chapter patterns (# Chapter, Act, scene breaks)", "option_b": "Import as single continuous chapter file", "option_c": "Prompt user for custom chapter delimiter regex"},
        ],
    ),

    "docx_sync": EngineSpec(
        name="docx_sync",
        category=EngineCategory.CORE,
        title="DOCX Bidirectional Sync",
        description="Three-way content hash sync with conflict branching for Microsoft Word / LibreOffice",
        module_name="lib.docx_sync",
        cli_command="docx",
        aliases=["word", "writer", "docx-sync"],
        studio_tab="Editor",
        logic_documentation="Parses OpenXML ZIP/XML structures to bidirectionally synchronize Markdown manuscript chapters with Microsoft Word (.docx) documents, preserving formatting and comments.",
        scientific_logic="""1. Three-Way Content Hash Synchronization:
   Computes SHA-256 digests of Markdown source $H_{\\text{MD}}$, Word document $H_{\\text{DOCX}}$, and Base common ancestor $H_{\\text{BASE}}$.
   - If only MD changed: Recompiles DOCX.
   - If only DOCX changed: Updates MD while preserving frontmatter.
   - If both changed independently: Branches into conflict review file (`Chapter_01_conflict.docx`).""",
        why_this_way="Professional editors use Microsoft Word Track Changes. Three-way syncing allows authors to work with editors without losing their canonical Markdown repository.",
        worldbuilding_relevance="Allows non-technical collaborators to review world glossaries in Word.",
        storytelling_relevance="Enables round-trip editorial workflow with professional editors using Word Track Changes.",
        writing_relevance="Allows drafting in LibreOffice or Word while retaining Markdown canonical source of truth.",
        subfeatures=[
            {"name": "Bidirectional Markdown-DOCX Sync", "rule": "Synchronizes edits made in Word back into Markdown files.", "example": "arcanum docx sync Manuscript/"},
            {"name": "Conflict Branching", "rule": "Creates safe side-by-side conflict files on simultaneous edits.", "example": "arcanum docx build Manuscript/"},
        ],
        extension_guide="""Sync Word edits:
```bash
arcanum docx sync Manuscript/
```""",
        advisory_guidance=[
            {"pattern": "Simultaneous edit conflict in MD and DOCX", "option_a": "Branch into conflict file for manual side-by-side review", "option_b": "Prefer Markdown version as canonical source", "option_c": "Prefer DOCX version with Track Changes preserved"},
        ],
    ),

    "world_doctor": EngineSpec(
        name="world_doctor",
        category=EngineCategory.CORE,
        title="World Bible Doctor",
        description="Deep lore consistency, broken wikilink, orphan entity, and timeline chronology checker",
        module_name="lib.world_doctor",
        cli_command="world-doctor",
        aliases=["doctor-world", "lore-check", "world-doctor"],
        studio_tab="Diagnostics",
        logic_documentation="Performs comprehensive graph topology sweeps across World Bible notes, detecting dangling wikilinks, orphaned dossiers, fuzzy name spelling variants (e.g. Kaelen vs Kaelin), and chronological conflicts.",
        scientific_logic="""1. Graph Topology Integrity Sweep:
   Lore notes modeled as directed graph $G = (V, E)$ where edges are wikilinks `[[Target]]`.
   - Dangling Wikilinks: $e = (u, v) \\in E$ where $v \\notin V$.
   - Orphan Nodes: $\\text{deg}^+(v) + \\text{deg}^-(v) = 0$.
   - Fuzzy Spelling Variants: Levenshtein distance $\\le 2$ between entity names.""",
        why_this_way="World bibles with hundreds of interlinked markdown files accumulate broken links and misspelled character names over time.",
        worldbuilding_relevance="Maintains airtight world bible health across hundreds of interlinked lore notes.",
        storytelling_relevance="Prevents accidental continuity blunders and dropped worldbuilding concepts.",
        writing_relevance="Generates an offline HTML health report with 1-click suggested repairs.",
        subfeatures=[
            {"name": "Dangling Wikilink Sweeper", "rule": "Finds broken links to nonexistent lore files.", "example": "arcanum world-doctor World/"},
            {"name": "Fuzzy Name Variant Finder", "rule": "Detects accidental spelling variants (e.g. Althea vs Althaea).", "example": "arcanum world-doctor World/ --fuzzy"},
        ],
        extension_guide="""Run world bible health check:
```bash
arcanum world-doctor World/
```""",
        advisory_guidance=[
            {"pattern": "Fuzzy spelling variant detected (e.g. Althea / Althaea)", "option_a": "Unify all references to primary spelling", "option_b": "Register variant as legitimate in-universe dialect alias", "option_c": "Retain as intentional distinct entities"},
        ],
    ),

    "diagnostics": EngineSpec(
        name="diagnostics",
        category=EngineCategory.CORE,
        title="System Diagnostics & Diagnostics Report",
        description="Toolchain validation, environment health checks, and redacted bug triage bundles",
        module_name="lib.diagnostics",
        cli_command="doctor",
        aliases=["check", "doctor", "health"],
        studio_tab="Diagnostics",
        logic_documentation="Inspects system environment, verifies 100% offline air-gap isolation, checks external optional tools (Git, Typst, Pandoc), and validates atomic file permissions.",
        scientific_logic="""1. Toolchain & Offline Air-Gap Verification:
   Audits presence of standard CLI tools (git, python3, typst, pandoc) and verifies that no external network sockets are open during authoring operations.""",
        why_this_way="Ensures the sovereign environment is 100% operational and safe before embarking on major compile/export runs.",
        worldbuilding_relevance="Verifies storage capacity and integrity for large multimedia lore repositories.",
        storytelling_relevance="Validates compilation toolchains before initiating final book exports.",
        writing_relevance="Provides peace of mind with 100% offline privacy and health verifications.",
        subfeatures=[
            {"name": "Toolchain Probe", "rule": "Verifies availability of Git, Typst, Pandoc, and Python 3.10+.", "example": "arcanum doctor"},
            {"name": "Air-Gap Network Isolation Audit", "rule": "Verifies zero outbound network sockets or telemetry pings.", "example": "arcanum doctor --audit-airgap"},
        ],
        extension_guide="""Run system diagnostics:
```bash
arcanum doctor
```""",
        advisory_guidance=[
            {"pattern": "Optional compiler tool missing (e.g. Typst)", "option_a": "Use standard library Python/HTML fallback compiler", "option_b": "Install optional binary via system package manager", "option_c": "Export Markdown for manual external typesetting"},
        ],
    ),

    "config": EngineSpec(
        name="config",
        category=EngineCategory.CORE,
        title="Project Configuration",
        description="Global and local workspace configuration, paths, and preferences",
        module_name="lib.config",
        cli_command="config",
        studio_tab="Tools",
        logic_documentation="Manages JSON/YAML workspace configurations, environment overrides, and secure backup destinations using atomic file operations.",
        scientific_logic="""1. Hierarchical Configuration Cascading:
   Configuration loaded with strict override hierarchy:
   $$\\text{Default Invariants} \\longrightarrow \\text{Global } \\sim/.config/arcanum/ \\longrightarrow \\text{Local } .arcanum.yaml \\longrightarrow \\text{Environment Variables}$$""",
        why_this_way="Allows authors to customize fonts, word count targets, and backup paths per project while retaining sane global defaults.",
        worldbuilding_relevance="Stores default world vault paths, cosmological constants, and universe-level preferences.",
        storytelling_relevance="Configures target word count milestones, chapter formatting templates, and paradigm defaults.",
        writing_relevance="Customizes UI fonts, dark/sepia themes, and export directories.",
        subfeatures=[
            {"name": "Configuration Getter/Setter", "rule": "Gets and sets local/global preferences.", "example": "arcanum config set target_words 90000"},
            {"name": "Cascading Resolution Inspector", "rule": "Traces configuration values across defaults, global, and local scopes.", "example": "arcanum config trace target_words"},
        ],
        extension_guide="""Inspect configuration:
```bash
arcanum config get backup_dest
```""",
        advisory_guidance=[
            {"pattern": "Missing configuration key", "option_a": "Generate default configuration file", "option_b": "Inherit global environment variable", "option_c": "Use ephemeral in-memory fallback"},
        ],
    ),

    "cache": EngineSpec(
        name="cache",
        category=EngineCategory.CORE,
        title="Performance Cache",
        description="Fast mtime-keyed in-memory index for lore vaults and manuscripts",
        module_name="lib.cache",
        cli_command="cache",
        studio_tab="Tools",
        logic_documentation="Caches parsed markdown ASTs, word counts, and wikilink graphs using file modification timestamps (mtime) and SHA-256 digests for sub-millisecond query performance.",
        scientific_logic="""1. mtime-Keyed AST Caching:
   Caches parsed markdown frontmatter and word counts keyed by `(file_path, mtime, size)`. Only re-parses disk files when mtime changes, achieving sub-millisecond response across 10,000+ files.""",
        why_this_way="Re-parsing thousands of markdown files on every UI keystroke causes UI lag. Fast in-memory caching keeps typing fluid.",
        worldbuilding_relevance="Enables instantaneous searching across thousands of world lore entities without re-parsing disk files.",
        storytelling_relevance="Provides live, lag-free structural word counts and chapter analytics across multi-volume series.",
        writing_relevance="Maintains background typing speed without UI stuttering.",
        subfeatures=[
            {"name": "Cache Invalidation & Sweeper", "rule": "Clears and rebuilds mtime index.", "example": "arcanum cache clear"},
            {"name": "mtime AST Indexer", "rule": "Pre-computes markdown word counts and frontmatter hashes for fast lookup.", "example": "arcanum cache warm"},
        ],
        extension_guide="""Clear and rebuild cache:
```bash
arcanum cache scan
```""",
        advisory_guidance=[
            {"pattern": "Stale cache detected", "option_a": "Trigger automatic cache invalidation on next read", "option_b": "Run background asynchronous cache refresh", "option_c": "Bypass cache with direct disk read"},
        ],
    ),

    "manuscript_scaffold": EngineSpec(
        name="manuscript_scaffold",
        category=EngineCategory.CORE,
        title="Manuscript Structure Scaffolder",
        description="Pluggable manuscript directory scaffolding across 16 narrative structure presets and custom division layouts",
        module_name="lib.manuscript_scaffold",
        cli_command="scaffold",
        aliases=["scaffold", "presets", "structure-presets", "manuscript-scaffold"],
        studio_tab="Craft",
        logic_documentation="Generates numbered directory hierarchies and starter chapters across 16 structural paradigms (Classic Three-Act, Hero's Journey, Save the Cat, Story Circle, Kishōtenketsu, 7-Point, Fichtean Curve, 8-Sequence, Freytag's Pyramid, MICE Quotient, Romancing the Beat, Virgin's Promise, Snowflake, Parallel, Episodic, Nonlinear) and custom user-defined division lists with path traversal protection.",
        scientific_logic="""1. Narrative Paradigm Directory Scaffolding:
   Maps structural beats to physical filesystem directories with zero cloud dependencies:
   $$\\text{Preset } K \\longrightarrow \\langle 01\\_\\text{Div}_1, 02\\_\\text{Div}_2, \\dots, N\\_\\text{Div}_N \\rangle$$

2. Path Traversal & Identifier Validation:
   Enforces token regex `^[A-Za-z0-9_-]+$`, rejecting directory traversal tokens (`..`, `/`, `\\`).

3. Manifest Serialization & Upward Discovery:
   Serializes `schema_version: "1.1"` in `manuscript.yaml` with bidirectional paradigm links.""",
        why_this_way="Different storytelling traditions (Western 3-Act, Eastern Kishōtenketsu, Romance beat sheets, Multi-POV parallel tracks) require different folder structures matching the author's mental model.",
        worldbuilding_relevance="Enables structured scaffolding of companion volumes, parallel lore threads, and episodic world chronologies.",
        storytelling_relevance="Aligns the physical folder layout directly with the chosen narrative pacing framework.",
        writing_relevance="Provides clean, distraction-free starter chapters and atomic division creation.",
        subfeatures=[
            {"name": "16 Built-in Presets", "rule": "Supports Classic Three-Act, Hero's Journey, Save the Cat, Kishōtenketsu, and 12 other presets.", "example": "arcanum scaffold MyNovel/Book-01 --structure heros_journey"},
            {"name": "Custom Divisions", "rule": "Scaffolds arbitrary named division lists with regex validation.", "example": "arcanum scaffold MyNovel/Book-01 --structure custom --divisions 'Prologue,Part-I,Part-II,Epilogue'"},
            {"name": "Structure Preset Introspection", "rule": "Lists and inspects all registered presets and division descriptions.", "example": "arcanum scaffold list / arcanum scaffold info kishotenketsu"},
        ],
        extension_guide="""Scaffold a volume or query structure presets:
```bash
# List all 16 presets
arcanum scaffold list

# View details for a preset
arcanum scaffold info kishotenketsu

# Scaffold a volume with custom structure
arcanum scaffold Manuscripts/Novel/Book-01 --structure story_circle
```""",
        advisory_guidance=[
            {"pattern": "Manuscript structure does not match default Three-Act model", "option_a": "Select matching preset from 16 registered narrative frameworks", "option_b": "Define custom division labels via `--divisions`", "option_c": "Retain default Three-Act structure"},
        ],
    ),

    "fs_utils": EngineSpec(
        name="fs_utils",
        category=EngineCategory.CORE,
        title="Atomic File System",
        description="Crash-safe atomic writes and storage operations",
        module_name="lib.fs_utils",
        cli_command="fs",
        studio_tab="Tools",
        logic_documentation="Guarantees zero data loss using POSIX atomic writes (temp file -> flush -> fsync -> os.replace -> parent dir fsync) with cross-platform file locking.",
        scientific_logic="""1. POSIX Atomic Write Lifecycle:
   $$\\text{Write to } .tmp\\_PID \\longrightarrow \\text{flush()} \\longrightarrow \\text{os.fsync()} \\longrightarrow \\text{os.replace()} \\longrightarrow \\text{parent dir fsync()}$$
   Guarantees that a power cut or crash never leaves a corrupted half-written file on disk.""",
        why_this_way="Direct unbuffered writes corrupt creative drafts during unexpected crashes. Atomic replacement guarantees file integrity.",
        worldbuilding_relevance="Protects irreplaceable creative world lore against power cuts or sudden crashes.",
        storytelling_relevance="Safeguards manuscript drafts, version forks, and chapter re-orderings.",
        writing_relevance="Ensures every keystroke and autosave is durable on disk.",
        subfeatures=[
            {"name": "Atomic Write Engine", "rule": "Writes files safely via temporary files and fsync.", "example": "from lib._bootstrap import atomic_write; atomic_write('chap.md', content)"},
            {"name": "Cross-Platform File Lock (ArcanumLock)", "rule": "Prevents race conditions during background exports and backups.", "example": "from lib.lockfile import ArcanumLock; with ArcanumLock('export'): pass"},
        ],
        extension_guide="""Use in Python scripts:
```python
from lib._bootstrap import atomic_write
atomic_write("Manuscript/Chapter_01.md", "# Chapter 1\\n\\nProse...")
```""",
        advisory_guidance=[
            {"pattern": "File lock contention", "option_a": "Wait with exponential backoff", "option_b": "Create conflict branch file (e.g. Chapter_conflict_2026.md)", "option_c": "Prompt user for manual lock override"},
        ],
    ),

    "migrate": EngineSpec(
        name="migrate",
        category=EngineCategory.CORE,
        title="Vault Migration",
        description="Schema upgrade engine for migrating older lore vaults and projects",
        module_name="lib.migrate",
        cli_command="migrate",
        aliases=["upgrade", "migrate"],
        studio_tab="Tools",
        logic_documentation="Upgrades legacy Obsidian vaults, frontmatter schemas, and manuscript folders to current Ars Arcanum standards with zero data destruction.",
        scientific_logic="""1. Non-Destructive Schema Migration Pipeline:
   Upgrades legacy frontmatter formats and folder structures with automatic backup creation before applying schema transforms.""",
        why_this_way="Creative projects span years; software updates must never break or alter historical lore notes.",
        worldbuilding_relevance="Preserves historical world lore notes across multi-year writing projects.",
        storytelling_relevance="Updates legacy chapter header formats to modern novelWriter / Markdown standards.",
        writing_relevance="Enables seamless project modernization without manual file editing.",
        subfeatures=[
            {"name": "Vault Schema Upgrader", "rule": "Migrates legacy frontmatter YAML tags to current standard.", "example": "arcanum migrate World/"},
            {"name": "Pre-Migration Safety Snapshot", "rule": "Creates compressed rollback archive before applying changes.", "example": "arcanum migrate World/ --snapshot"},
        ],
        extension_guide="""Run vault migration:
```bash
arcanum migrate World/
```""",
        advisory_guidance=[
            {"pattern": "Unrecognized legacy frontmatter", "option_a": "Migrate to standard YAML frontmatter schema", "option_b": "Preserve unmapped keys under custom_attributes", "option_c": "Leave legacy file untouched in archival branch"},
        ],
    ),

    # =========================================================================
    # DOMAIN G: PUBLISHING, PREFLIGHT & TYPESETTING
    # =========================================================================
    "preflight": EngineSpec(
        name="preflight",
        category=EngineCategory.CORE,
        title="Typesetting Preflight Validator",
        description="Print-PDF compliance, image resolution, and trim size validation",
        module_name="lib.preflight",
        cli_command="preflight",
        aliases=["pre-flight", "prepress"],
        studio_tab="Publishing",
        logic_documentation="Validates print-on-demand requirements (Amazon KDP, IngramSpark), spine width calculation based on page count and paper thickness, bleed margins, font embedding, and image DPI.",
        scientific_logic="""1. Print-on-Demand (POD) Spine Width Formulation:
   Spine width $W_{\\text{spine}}$ based on page count $N$ and paper stock caliper (PPI - Pages Per Inch):
   $$W_{\\text{spine}} = \\frac{N}{\\text{PPI}} \\text{ (inches)} = \\frac{N}{2} \\times \\text{Caliper (mm)}$$
   - Cream 55lb (434 PPI): $W = N / 434$ inches
   - White 50lb (500 PPI): $W = N / 500$ inches

2. Signature Page Count & Bleed Bounds:
   Page counts must round up to multiples of 4 (or 6) for physical sheet binding. Cover bleeds require $+0.125\\text{ in}$ ($3.2\\text{ mm}$) margins on all outer edges.""",
        why_this_way="Amazon KDP and IngramSpark reject PDF uploads with incorrect spine widths or low-res images. Preflight validation catches these errors before submission.",
        worldbuilding_relevance="Verifies world map image resolutions for crisp 300+ DPI print reproduction.",
        storytelling_relevance="Calculates final physical book thickness, signature layouts, and spine text fitting.",
        writing_relevance="Catches widow/orphan lines, bad page breaks, and unlinked footnotes before print submission.",
        subfeatures=[
            {"name": "Spine Width Calculator", "rule": "Calculates spine width across KDP and IngramSpark paper types.", "example": "arcanum preflight Manuscript/ --pages 380 --paper cream-55"},
            {"name": "POD Signature Auditor", "rule": "Ensures page counts align to 4-page signatures.", "example": "arcanum preflight Manuscript/"},
        ],
        extension_guide="""Run preflight audit:
```bash
arcanum preflight Manuscript/
```""",
        advisory_guidance=[
            {"pattern": "Page count not multiple of 4/6 (POD signature)", "option_a": "Add blank backmatter note pages to round up", "option_b": "Adjust font leading / margins slightly", "option_c": "Proceed with printer automatic blank insertion"},
        ],
    ),

    "frontmatter_builder": EngineSpec(
        name="frontmatter_builder",
        category=EngineCategory.CORE,
        title="Frontmatter & Backmatter Builder",
        description="Generates copyright, dedication, epigraph, and biographical matter",
        module_name="lib.frontmatter_builder",
        cli_command="matter",
        aliases=["frontmatter", "backmatter", "matter-builder"],
        studio_tab="Publishing",
        logic_documentation="Scaffolds modular frontmatter (half-title, title page, copyright notice, dedication, epigraph, table of contents) and backmatter (about author, teaser chapters, discussion questions).",
        scientific_logic="""1. Standard Editorial Front/Back Matter Architecture:
   Scaffolds industry standard publishing sequences: Half-Title $\\to$ Title Page $\\to$ Copyright / CIP Legal Block $\\to$ Dedication $\\to$ Epigraph $\\to$ Table of Contents $\\to$ Body Chapters $\\to$ Acknowledgments $\\to$ About Author.""",
        why_this_way="Authors often forget required legal copyright notices, CIP data, and ISBN placeholders required for distribution.",
        worldbuilding_relevance="Injects in-universe historical quotes and epigraphs to enrich cosmological lore.",
        storytelling_relevance="Provides structural framing and thematic epigraphs that set chapter tone.",
        writing_relevance="Automates legal copyright notices, CIP data, and acknowledgments.",
        subfeatures=[
            {"name": "Publishing Matter Scaffolder", "rule": "Generates complete frontmatter and backmatter markdown files.", "example": "arcanum matter build Manuscript/"},
            {"name": "Frontmatter Normalizer", "rule": "Standardizes schema keys across legacy chapter files.", "example": "arcanum matter normalize Manuscript/"},
        ],
        extension_guide="""Build frontmatter files:
```bash
arcanum matter build Manuscript/
```""",
        advisory_guidance=[
            {"pattern": "Missing copyright year or ISBN", "option_a": "Scaffold default copyright with current year", "option_b": "Insert placeholder ISBN for proof review", "option_c": "Leave blank for public domain / draft distribution"},
        ],
    ),

    "concordance": EngineSpec(
        name="concordance",
        category=EngineCategory.CORE,
        title="Dramatis Personae & Glossary Generator",
        description="Compiles character indices and lore terms into publication-ready back-matter",
        module_name="lib.concordance",
        cli_command="concordance",
        aliases=["glossary", "concordance", "index"],
        studio_tab="Publishing",
        logic_documentation="Extracts lore entities from world dossiers, indexes their manuscript occurrences with chapter citations, and formats publication-ready Dramatis Personae and Glossary appendices.",
        scientific_logic="""1. Concordance Indexing & Chapter Occurrence Mapping:
   Extracts entity keywords from World Bible dossiers and maps every occurrence across manuscript chapters with exact page/chapter citations.""",
        why_this_way="Manual indexing of glossaries and character lists is tedious and prone to missing terms.",
        worldbuilding_relevance="Transforms complex world notes into accessible reader companion guides.",
        storytelling_relevance="Allows epic fantasy/sci-fi readers to look up houses, ranks, and foreign terms without spoilers.",
        writing_relevance="Automates tedious manual backmatter indexing with typographical formatting.",
        subfeatures=[
            {"name": "Glossary Compiler", "rule": "Generates alphabetized glossary with chapter occurrence citations.", "example": "arcanum concordance Manuscript/ -w World/"},
            {"name": "Dramatis Personae Indexer", "rule": "Builds character cast index with chapter appearance references.", "example": "arcanum concordance --cast Manuscript/"},
        ],
        extension_guide="""Generate glossary backmatter:
```bash
arcanum concordance Manuscript/ -w World/ -o Manuscript/04_Back_Matter/Glossary.md
```""",
        advisory_guidance=[
            {"pattern": "Term cited in lore but never mentioned in manuscript", "option_a": "Exclude unused term from book backmatter", "option_b": "Include in extended world codex only", "option_c": "Retain in backmatter for atmospheric worldbuilding"},
        ],
    ),

    "codex_export": EngineSpec(
        name="codex_export",
        category=EngineCategory.CRAFT,
        title="World Wiki Codex Export",
        description="Compiles world lore notes into a standalone, searchable offline HTML encyclopedia",
        module_name="lib.codex_export",
        cli_command="codex",
        aliases=["codex", "wiki", "export-codex"],
        studio_tab="Publishing",
        logic_documentation="Compiles World Bible markdown files into an ultra-fast, responsive, single-file offline HTML wiki with full-text search, spoiler sliders, and interactive relationship embeds.",
        scientific_logic="""1. Standalone Single-File Static Wiki Generator:
   Bundles all markdown dossiers into a self-contained offline HTML5 file with zero remote CDN dependencies, embedded SVG icons, instant JavaScript client-side search, and interactive spoiler disclosure sliders.""",
        why_this_way="Authors need a way to share companion world wikis with readers, editors, and tabletop RPG players without hosting servers.",
        worldbuilding_relevance="Creates an offline encyclopedia compendium for fans, beta readers, and tabletop GMs.",
        storytelling_relevance="Provides readers with an exploratory lore codex companion.",
        writing_relevance="Enables quick reference lookup of lore notes on tablets and secondary monitors.",
        subfeatures=[
            {"name": "Single-File HTML Wiki Exporter", "rule": "Compiles entire lore vault into a searchable standalone HTML file.", "example": "arcanum codex World/ --html dist/world_codex.html"},
            {"name": "Interactive Spoiler Slider", "rule": "Renders chronological secret reveals tailored to reader progress.", "example": "arcanum codex World/ --spoiler-protection"},
        ],
        extension_guide="""Export World Codex:
```bash
arcanum codex World/ --html dist/codex.html
```""",
        advisory_guidance=[
            {"pattern": "World notes contain major late-story spoiler revelations", "option_a": "Enable reader spoiler slider to hide late-book lore", "option_b": "Segment secrets into GM/Author-only codex section", "option_c": "Export full unredacted codex for author reference"},
        ],
    ),

    "omnibus": EngineSpec(
        name="omnibus",
        category=EngineCategory.CORE,
        title="Series Omnibus Compiler",
        description="Multi-volume master series compiler with unified Dramatis Personae and master timeline",
        module_name="lib.omnibus",
        cli_command="omnibus",
        aliases=["compile-omnibus", "series-omnibus", "omnibus"],
        studio_tab="Publishing",
        logic_documentation="Compiles multi-volume book series into deluxe single-volume omnibus editions with unified Dramatis Personae, master timeline appendices, and cross-volume continuity harmonization.",
        scientific_logic="""1. Multi-Volume Series Compilation Pipeline:
   Merges multiple manuscript volumes into a single master Typst or EPUB3 edition with unified frontmatter, interstitial 'Story So Far' recaps, and master series concordance.""",
        why_this_way="Creating omnibus box sets manually requires hours of error-prone copy-pasting and renumbering.",
        worldbuilding_relevance="Unifies lore glossaries across an entire trilogy or multi-book saga.",
        storytelling_relevance="Ensures smooth inter-book reading with 'The Story So Far' interstitial recaps.",
        writing_relevance="Formats deluxe Typst and EPUB3 box sets with persistent offline bookmarks.",
        subfeatures=[
            {"name": "Series Omnibus Builder", "rule": "Compiles multi-volume series into deluxe omnibus editions.", "example": "arcanum omnibus Universe/ --html dist/omnibus.html"},
            {"name": "Cross-Book Interstitial Recap Generator", "rule": "Synthesizes 'Story So Far' transitions between volumes.", "example": "arcanum omnibus Universe/ --generate-recaps"},
        ],
        extension_guide="""Compile series omnibus:
```bash
arcanum omnibus Universes/Eldoria/ --output dist/eldoria_trilogy.pdf
```""",
        advisory_guidance=[
            {"pattern": "Inconsistent term definitions across Book 1 and Book 3 in omnibus compilation", "option_a": "Harmonize to latest canonical definition in master glossary", "option_b": "Annotate term evolution as historical in-universe linguistic shift", "option_c": "Retain volume-specific glossaries in individual book sections"},
        ],
    ),

    "resonance": EngineSpec(
        name="resonance",
        category=EngineCategory.CORE,
        title="Universal Resonance Mesh & Cross-Domain Synthesizer",
        description="Deterministic cross-domain knowledge graph, causal cascade simulation, and creative spark bridges linking all 50 engines",
        module_name="lib.resonance",
        cli_command="resonance",
        aliases=["mesh", "cascade", "spark", "bridge", "ecosystem", "synergy"],
        studio_tab="Worldbuilding",
        logic_documentation="Unifies all 50 Ars Arcanum engines across 5 core domain pillars into a deterministic, bi-directional knowledge graph with multi-hop causal cascading and structural isomorphism generators.",
        scientific_logic="""1. Universal Domain Mesh Topology & Graph Invariants:
   Represents domain variables, entities, and craft rules as typed nodes in a bi-directional knowledge graph $G = (V, E)$ partitioned across 5 Domain Pillars:
   - Cosmology & Physics, Society & Systems, Narrative & Chronology, Stylistics & Senses, Authoring OS.
   Edge relations $r \\in \\{\\text{causally\\_drives}, \\text{constrains}, \\text{isomorphic\\_to}, \\text{manifests\\_in}, \\text{economically\\_impacts}, \\text{lexically\\_influences}, \\text{thematically\\_mirrors}, \\text{sensory\\_grounding\\_for}\\}$.

2. Deterministic Causal Cascade Dynamics:
   Forward-propagating deterministic simulation of parameter shifts:
   $$\\Delta \\text{Param}_0 \\xrightarrow{r_1} \\Delta \\text{Node}_1 \\xrightarrow{r_2} \\Delta \\text{Node}_2 \\dots \\xrightarrow{r_n} \\Delta \\text{Node}_n$$
   Evaluates physical, ecological, economic, diplomatic, and narrative scene tension delta vectors with calculated confidence scores.

3. Structural Isomorphism & Cross-Field Analogy Synthesis:
   Algorithmic mapping between disparate mathematical and conceptual systems (e.g. thermodynamic entropy $\\leftrightarrow$ institutional decay, trophic pyramids $\\leftrightarrow$ magic carrying capacity, hydrological flow $\\leftrightarrow$ monetary velocity).""",
        why_this_way="Narrative depth emerges when world systems, plot events, and character psychology are causally interdependent rather than isolated silos. By deterministically modeling cross-domain connections, authors can explore non-obvious creative sparks and guarantee that physical, economic, and magical changes ripple plausibly through their entire narrative universe.",
        worldbuilding_relevance="Enables holistic world design where planetary cosmology directly shapes climate, agriculture, currency stability, geopolitics, and cultural idioms.",
        storytelling_relevance="Generates multidisciplinary plot hooks and scene complications; guarantees that macro-world events create visceral micro-scene tension.",
        writing_relevance="Supplies concrete sensory palettes and linguistic metaphors grounded in the world's physical and cultural reality.",
        subfeatures=[
            {"name": "Knowledge Mesh Visualizer", "rule": "Generates interactive offline visual graph of all 50 engines and world entities.", "example": "arcanum resonance mesh --html dist/mesh.html"},
            {"name": "Deterministic Causal Cascade", "rule": "Simulates downstream repercussions of parameter changes across disparate fields.", "example": "arcanum resonance cascade astrophysics --param axial_tilt --val 38.5"},
            {"name": "Creative Spark Synthesizer", "rule": "Generates multidisciplinary analogies and plot premises connecting disparate domains.", "example": "arcanum resonance spark astrophysics conlang economy"},
            {"name": "Multi-Hop Conceptual Bridge", "rule": "Finds conceptual pathways connecting two arbitrary craft domains.", "example": "arcanum resonance bridge astrophysics voice"},
            {"name": "Cross-Domain Coherence Audit", "rule": "Validates mutual mathematical and narrative consistency across all engine files.", "example": "arcanum resonance audit"},
        ],
        extension_guide="""Simulate cross-domain parameter cascade:
```bash
arcanum resonance cascade magic_system --param magic_cost --val "high_backlash"
arcanum resonance spark ecology factions scene_mechanics --count 3
arcanum resonance mesh --html dist/knowledge_mesh.html
```""",
        advisory_guidance=[
            {"pattern": "Upstream physical change creates severe downstream economic/military contradiction in manuscript", "option_a": "Apply calculated downstream cascade changes across all lore files for hard realism", "option_b": "Isolate the change as an in-world supernatural anomaly or magical shielding effect", "option_c": "Retain divergence as an intentional surreal mystery or authorial creative choice"},
        ],
    ),

    "tips": EngineSpec(
        name="tips",
        category=EngineCategory.CORE,
        title="Dynamic Intelligent Tips & Knowledge Discovery",
        description="Metadata-rich non-obvious craft wisdom, mathematical insights, and workflow discovery engine across all 51 domain engines",
        module_name="lib.tips",
        cli_command="tip",
        aliases=["tips", "craft-tips", "advice", "hint", "hints", "help-tips"],
        studio_tab="Intelligent Tips",
        logic_documentation="Context-sensitive retrieval engine indexing 120+ masterclass tips across all 51 engines and 117 subfeatures with non-repeating cycle history and user display configuration.",
        scientific_logic="""1. Multidimensional Contextual Ranking & Token Scoring:
   Evaluates user focus vector $\\mathbf{u} = (\\text{engine}, \\text{subfeature}, \\text{keywords}, \\text{context})$ against indexed tip metadata $\\mathbf{t}_i$:
   $$\\text{Score}(\\mathbf{t}_i, \\mathbf{u}) = w_e \\cdot \\mathbb{I}(e_i = u_e) + w_{sf} \\cdot \\text{Sim}(sf_i, u_{sf}) + w_k \\cdot |\\text{Tags}_i \\cap \\text{Toks}(\\mathbf{u})| + w_d \\cdot \\text{DepthWeight}_i$$

2. History Set Differencing & Zero-Stall Rotation:
   Maintains LRU session history $H_s \\subset \\text{Tips}$. Selects from candidate pool $C = \\{\\mathbf{t} \\in \\text{Tips} \\setminus H_s \\mid \\text{Score}(\\mathbf{t}, \\mathbf{u}) \\ge \\theta \\}$, resetting $H_s \\leftarrow \\emptyset$ upon pool exhaustion to ensure continuous variety without immediate repetition.

3. Non-Intrusive Sovereign Presentation Rails:
   Supports zero-friction integration into CLI command banners, Studio Hub contextual banners, Zen Studio drawers, and desktop UI status bars with explicit user opt-out persistence.""",
        why_this_way="Complex creative operating systems contain hundreds of advanced mathematical and narrative features that authors may never discover. Ambient, non-intrusive tips delivered at the precise moment of relevant work bridge the gap between engine capabilities and authorial execution without cognitive overload.",
        worldbuilding_relevance="Surfaces deep scientific rules (e.g. Roche limits, orographic rain shadows, Gresham's law, linguistic vowel shifts) directly during lore creation.",
        storytelling_relevance="Highlights non-linear pacing formulas, dramaturgical scene questions, paradox classifications, and character idiolect metrics while plotting.",
        writing_relevance="Provides actionable prose polish advice, sensory saturation ratios, modal hedge detection, and typography normalization tips in-situ during drafting.",
        subfeatures=[
            {"name": "Contextual Relevance Filter", "rule": "Retrieves high-scoring craft tips matching active engine, subfeature, or draft context.", "example": "arcanum tip climate --subfeature 'Orographic Rain Shadow'"},
            {"name": "Non-Obvious Masterclass Database", "rule": "Curates 120+ deep craft and technical tips across all registered engines.", "example": "arcanum tip --depth masterclass"},
            {"name": "Zero-Stall History Cycling", "rule": "Guarantees fresh, non-repeating tips across repeated requests using history tracking.", "example": "arcanum tip --cycle"},
            {"name": "Sovereign Display Configuration", "rule": "Allows authors to enable, disable, or query tip status persistently.", "example": "arcanum tip --disable / arcanum tip --enable"},
            {"name": "Cross-Platform Ambient Presentation", "rule": "Delivers tips through CLI footers, Studio Hub badges, and Zen Studio drawers.", "example": "arcanum tip --format json"},
        ],
        extension_guide="""Query contextual tips via CLI or Python API:
```bash
# Get tip for active engine
arcanum tip astrophysics

# Get tip for specific subfeature
arcanum tip conlang --subfeature phonology

# Enable or disable tips display
arcanum tip --enable
arcanum tip --disable
arcanum tip --status
```""",
        advisory_guidance=[
            {"pattern": "Author prefers distraction-free interface without tip displays", "option_a": "Disable tips globally via `arcanum tip --disable` or Studio Hub Settings toggle", "option_b": "Restrict tip depth to masterclass-only via configuration", "option_c": "Keep tips enabled in CLI footers only"},
        ],
    ),
}


# -----------------------------------------------------------------------------
# Public Query & Discovery Functions
# -----------------------------------------------------------------------------

def get_registry() -> dict[str, EngineSpec]:
    """Return the global engine dictionary."""
    return _ENGINES


def get_engine(name: str) -> EngineSpec | None:
    """Retrieve an engine specification by name, command, or alias."""
    name_clean = name.lower().strip()
    name_underscored = name_clean.replace("-", "_").replace(" ", "_")
    name_hyphenated = name_clean.replace("_", "-").replace(" ", "-")

    if name_clean in _ENGINES:
        return _ENGINES[name_clean]
    if name_underscored in _ENGINES:
        return _ENGINES[name_underscored]

    for spec in _ENGINES.values():
        all_names = {
            spec.name.lower(),
            spec.name.lower().replace("_", "-"),
            spec.cli_command.lower(),
            spec.cli_command.lower().replace(" ", "-"),
            spec.cli_command.lower().replace(" ", "_"),
        }
        for a in spec.aliases:
            all_names.add(a.lower())
            all_names.add(a.lower().replace("_", "-"))
            all_names.add(a.lower().replace("-", "_"))
        if name_clean in all_names or name_underscored in all_names or name_hyphenated in all_names:
            return spec

    for spec in _ENGINES.values():
        if spec.cli_command.lower().startswith(name_clean + " ") or spec.cli_command.lower().endswith(" " + name_clean):
            return spec
    return None


def list_engines(category: EngineCategory | None = None, enabled_only: bool = True) -> list[EngineSpec]:
    """List engine specifications matching optional category and enabled filter."""
    res = []
    for spec in _ENGINES.values():
        if category is not None and spec.category != category:
            continue
        if enabled_only and not spec.enabled:
            continue
        res.append(spec)
    return res


def get_core_engines(enabled_only: bool = True) -> list[EngineSpec]:
    """Return all core platform engines."""
    return list_engines(category=EngineCategory.CORE, enabled_only=enabled_only)


def get_craft_engines(enabled_only: bool = True) -> list[EngineSpec]:
    """Return all craft & specialized worldbuilding engines."""
    return list_engines(category=EngineCategory.CRAFT, enabled_only=enabled_only)


def is_engine_enabled(name: str) -> bool:
    """Check if an engine is enabled."""
    spec = get_engine(name)
    return spec.enabled if spec else False


def enable_engine(name: str) -> bool:
    """Enable a specific engine."""
    spec = get_engine(name)
    if spec:
        spec.enabled = True
        return True
    return False


def disable_engine(name: str) -> bool:
    """Disable a specific engine."""
    spec = get_engine(name)
    if spec:
        spec.enabled = False
        return True
    return False


def load_engine_module(name: str) -> Any:
    """Dynamically import and return the engine's Python module."""
    spec = get_engine(name)
    if not spec:
        raise ValueError(f"Unknown engine: '{name}'")
    return importlib.import_module(spec.module_name)


def search_engine_docs(query: str) -> list[EngineSpec]:
    """Fuzzy and substring search across all engine specifications."""
    q = query.lower().strip()
    if not q:
        return list(_ENGINES.values())

    results: list[EngineSpec] = []
    for spec in _ENGINES.values():
        searchable_text = f"{spec.name} {spec.title} {spec.description} {spec.scientific_logic} {spec.why_this_way} {spec.extension_guide} {' '.join(spec.aliases)}".lower()
        if q in searchable_text:
            results.append(spec)

    if not results:
        # Try fuzzy match on engine names and titles
        all_names = {s.name: s for s in _ENGINES.values()}
        matches = difflib.get_close_matches(q, list(all_names.keys()), n=5, cutoff=0.4)
        results = [all_names[m] for m in matches]

    return results


def get_engine_docs(name: str) -> dict[str, Any] | None:
    """Retrieve structured educational documentation and advisory guidance for an engine."""
    spec = get_engine(name)
    if not spec:
        return None
    return {
        "name": spec.name,
        "title": spec.title,
        "category": spec.category.value,
        "studio_tab": spec.studio_tab or "",
        "cli_command": spec.cli_command,
        "aliases": spec.aliases,
        "description": spec.description,
        "logic_documentation": spec.logic_documentation,
        "scientific_logic": spec.scientific_logic,
        "why_this_way": spec.why_this_way,
        "worldbuilding_relevance": spec.worldbuilding_relevance,
        "storytelling_relevance": spec.storytelling_relevance,
        "writing_relevance": spec.writing_relevance,
        "subfeatures": spec.subfeatures,
        "extension_guide": spec.extension_guide,
        "advisory_guidance": spec.advisory_guidance,
    }


def get_all_engine_docs() -> list[dict[str, Any]]:
    """Retrieve structured educational documentation for all registered engines."""
    return [
        {
            "name": spec.name,
            "title": spec.title,
            "category": spec.category.value,
            "studio_tab": spec.studio_tab or "",
            "cli_command": spec.cli_command,
            "aliases": spec.aliases,
            "description": spec.description,
            "logic_documentation": spec.logic_documentation,
            "scientific_logic": spec.scientific_logic,
            "why_this_way": spec.why_this_way,
            "worldbuilding_relevance": spec.worldbuilding_relevance,
            "storytelling_relevance": spec.storytelling_relevance,
            "writing_relevance": spec.writing_relevance,
            "subfeatures": spec.subfeatures,
            "extension_guide": spec.extension_guide,
            "advisory_guidance": spec.advisory_guidance,
        }
        for spec in _ENGINES.values()
    ]


def format_engine_doc(spec_or_name: EngineSpec | str, mode: str = "full") -> str:
    """Formats an engine's educational documentation for terminal CLI display.
    Modes: 'full', 'math' / 'theory', 'why', 'examples', 'subfeatures', 'advisory'
    """
    if isinstance(spec_or_name, str):
        engine_obj = get_engine(spec_or_name)
        if not engine_obj:
            return f"No documentation available for engine: '{spec_or_name}'"
        spec = engine_obj
    else:
        spec = spec_or_name

    mode_clean = mode.lower().strip()

    if mode_clean in ("math", "theory", "physics", "logic"):
        return f"""══════════════════════════════════════════════════════════════════════════════
 📐 {spec.title.upper()} — SCIENTIFIC / MATHEMATICAL / NARRATIVE LOGIC
 Command: 'arcanum {spec.cli_command}'
══════════════════════════════════════════════════════════════════════════════

{spec.scientific_logic or spec.logic_documentation}
"""

    if mode_clean in ("why", "rationale"):
        return f"""══════════════════════════════════════════════════════════════════════════════
 💡 {spec.title.upper()} — ARCHITECTURAL & CREATIVE RATIONALE ('WHY THIS WAY')
 Command: 'arcanum {spec.cli_command}'
══════════════════════════════════════════════════════════════════════════════

{spec.why_this_way or 'Provides deterministic mathematical and physical grounding for world lore.'}
"""

    if mode_clean in ("examples", "extension", "how-to", "guide"):
        return f"""══════════════════════════════════════════════════════════════════════════════
 🛠️ {spec.title.upper()} — AUTHOR EXTENSION GUIDE & PRACTICAL EXAMPLES
 Command: 'arcanum {spec.cli_command}'
══════════════════════════════════════════════════════════════════════════════

{spec.extension_guide or 'Configure parameters in YAML manifests or CLI invocation.'}
"""

    if mode_clean in ("subfeatures", "features"):
        lines = [
            "══════════════════════════════════════════════════════════════════════════════",
            f" ⚡ {spec.title.upper()} — SUBFEATURES MATRIX",
            f" Command: 'arcanum {spec.cli_command}'",
            "══════════════════════════════════════════════════════════════════════════════\n",
        ]
        if spec.subfeatures:
            for idx, sf in enumerate(spec.subfeatures, 1):
                lines.append(f"[{idx}] {sf.get('name', 'Subfeature')}")
                lines.append(f"    • Rule/Logic: {sf.get('rule', '')}")
                lines.append(f"    • Example:    {sf.get('example', '')}\n")
        else:
            lines.append("   (Subfeatures operate under the unified engine CLI command.)")
        return "\n".join(lines)

    if mode_clean in ("advisory", "resolution", "resolutions", "guidance", "choices"):
        lines = [
            "══════════════════════════════════════════════════════════════════════════════",
            f" 💡 {spec.title.upper()} — CREATIVE ADVISORY RESOLUTION PATHWAYS",
            f" Command: 'arcanum {spec.cli_command}'",
            "══════════════════════════════════════════════════════════════════════════════\n",
            "(The system never forces conformity. All checks provide multiple creative choices:)\n",
        ]
        if spec.advisory_guidance:
            for idx, adv in enumerate(spec.advisory_guidance, 1):
                lines.append(f"[{idx}] Pattern: {adv.get('pattern', 'Unconventional Choice')}")
                lines.append(f"    • Option A (Hard Realism): {adv.get('option_a', 'Standard convention')}")
                lines.append(f"    • Option B (Speculative Trope): {adv.get('option_b', 'In-world arcane/sci-fi grounding')}")
                lines.append(f"    • Option C (Author Sovereignty): {adv.get('option_c', 'Authorial creative freedom')}\n")
        else:
            lines.append("   (No specific advisory overrides registered for this engine.)")
        return "\n".join(lines)

    # Default 'full' mode
    doc = [
        "══════════════════════════════════════════════════════════════════════════════",
        f" 🏛️  ARS ARCANUM CRAFT ENGINE: {spec.title.upper()}",
        f"     Category: [{spec.category.value.upper()}]  •  Command: 'arcanum {spec.cli_command}'",
        "══════════════════════════════════════════════════════════════════════════════",
        "\n📖 Overview:",
        f"   {spec.description}",
        "\n⚙️ Engine Logic & Scientific / Structural Foundations:",
        f"   {spec.scientific_logic or spec.logic_documentation}",
        "\n💡 Why It Works This Way (Rationale):",
        f"   {spec.why_this_way or 'Provides deterministic mathematical and physical grounding for world lore.'}",
        "\n🌍 Worldbuilding Relevance:",
        f"   {spec.worldbuilding_relevance}",
        "\n📐 Storytelling & Narrative Architecture Relevance:",
        f"   {spec.storytelling_relevance}",
        "\n✍️ Prose Writing & Editorial Relevance:",
        f"   {spec.writing_relevance}",
    ]

    if spec.subfeatures:
        doc.append("\n⚡ Key Subfeatures & Capabilities:")
        for idx, sf in enumerate(spec.subfeatures, 1):
            doc.append(f"   [{idx}] {sf.get('name', 'Subfeature')}: {sf.get('rule', '')}")
            if sf.get('example'):
                doc.append(f"       Example: {sf.get('example')}")

    if spec.extension_guide:
        doc.append("\n🛠️ How to Build Upon & Extend This Logic (Examples):")
        doc.append("   " + "\n   ".join(spec.extension_guide.split("\n")))

    if spec.advisory_guidance:
        doc.append("\n💡 Advisory Mechanics & Creative Freedom Resolution Pathways:")
        doc.append("   (The system never forces conformity. All checks provide multiple creative choices:)")
        for idx, adv in enumerate(spec.advisory_guidance, 1):
            doc.append(f"\n   [{idx}] Pattern: {adv.get('pattern', 'Unconventional Choice')}")
            doc.append(f"       • Option A (Hard Realism): {adv.get('option_a', 'Standard convention')}")
            doc.append(f"       • Option B (Speculative Trope): {adv.get('option_b', 'In-world arcane/sci-fi grounding')}")
            doc.append(f"       • Option C (Author Sovereignty): {adv.get('option_c', 'Authorial creative freedom')}")

    doc.append("\n══════════════════════════════════════════════════════════════════════════════\n")
    return "\n".join(doc)


def get_engine_tips(engine_name: str) -> list[dict[str, Any]]:
    """Returns all metadata-rich craft and technical tips for a specific engine."""
    try:
        from lib.tips import get_tip_database
    except ImportError:
        try:
            from tips import get_tip_database
        except ImportError:
            return []
    db = get_tip_database()
    tips = db.get_by_engine(engine_name)
    return [t.to_dict() for t in tips]


def get_engine_catalog() -> list[dict[str, Any]]:
    """Returns the comprehensive craft engine catalog and capabilities as a list of dicts."""
    docs = get_all_engine_docs()
    return [
        {
            "id": d["name"],
            "name": d["title"],
            "category": d["category"].capitalize(),
            "studio_tab": d.get("studio_tab", ""),
            "cli": f"arcanum {d['cli_command']}",
            "desc": d["description"],
            "logic_documentation": d.get("logic_documentation", ""),
            "scientific_logic": d.get("scientific_logic", d.get("logic_documentation", "")),
            "why_this_way": d.get("why_this_way", ""),
            "worldbuilding_relevance": d.get("worldbuilding_relevance", ""),
            "storytelling_relevance": d.get("storytelling_relevance", ""),
            "writing_relevance": d.get("writing_relevance", ""),
            "subfeatures": d.get("subfeatures", []),
            "extension_guide": d.get("extension_guide", ""),
            "advisory_guidance": d.get("advisory_guidance", []),
            "tips": get_engine_tips(d["name"]),
        }
        for d in docs
    ]

