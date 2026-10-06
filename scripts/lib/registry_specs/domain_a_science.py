#!/usr/bin/env python3
"""
Domain engine specification definitions for Ars Arcanum Registry.
"""
from __future__ import annotations

try:
    from lib.registry_base import EngineCategory, EngineSpec
except ImportError:
    from registry_base import EngineCategory, EngineSpec

ENGINES: dict[str, EngineSpec] = {
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
}

__all__ = ["ENGINES"]
