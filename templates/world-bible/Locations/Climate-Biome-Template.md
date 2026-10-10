---
fileClass: ClimateBiome
type: climate_biome
name: "<% tp.file.title %>"
biome_name: "Highland Cloud Forest"
tags:
  - world/climate
  - world/location
koppen_code: "Cfb"
climate_group: "Temperate Marine / Highland"
latitude_deg: 38.5
elevation_m: 1450
annual_precip_mm: 1250
mean_annual_temp_c: 12.4
windward_mountain_height_m: 3200
wind_direction: "West-Southwest"
hadley_cell_regime: "Ferrel Cell (Westerlies)"
axial_tilt_deg: 23.5
insolation_wm2: 1310
---

# <% tp.file.title %> — Climate & Biome Specification

> [!NOTE] ⚠️ EDUCATIONAL TEMPLATE (AI-GENERATED)
> **Notice**: This template was AI-generated for educational demonstration and craft guidance within the Ars Arcanum operating system. It is strictly non-commercial and provided solely to demonstrate system features, mechanical schemas, and engine capabilities. Authors should replace placeholder values with their original worldbuilding details.

<details>
<summary>💡 <b>Ars Arcanum Engine Guidance & Feature Breakdown (Click to Expand)</b></summary>

### Features Demonstrated in This Template:
- **Insolation & Habitability**: `climate` (`arcanum climate --star-lum 1.0 --distance-au 1.05 --albedo 0.29`) — Calculates solar flux ($S = 1361 \times L_*/d^2 \text{ W/m}^2$) and blackbody surface equilibrium temperature ($T_{\text{eq}} = [S(1-A)/4\sigma]^{1/4}$) across latitudes and Milankovitch cycles.
- **Circulation Cell Mapper**: `climate` (`arcanum climate --rotation-hours 32.0`) — Maps Rossby number regimes and prevailing planetary wind bands (Trade Winds 0°–30°, Ferrel Westerlies 30°–60°, Polar Easterlies 60°–90°) from planetary rotation velocity.
- **Orographic Rain Shadow**: `climate` (`arcanum climate --mountain-elevation 3200 --base-precip 1250`) — Simulates adiabatic lapse rate cooling (DALR: 9.8°C/km) on windward ascent and compressed leeward Foehn heating (MALR: 5.5°C/km).
- **Köppen Classifier**: `climate` (`arcanum climate --base-temp 12.4 --base-precip 1250`) — Assigns formal Köppen 3-letter classification (e.g. `Cfb`, `BWh`, `Dfc`, `ET`) to climate coordinates.

### How to Use for Your Projects:
1. Define your world's `axial_tilt_deg` and the region's `latitude_deg`.
2. Input the elevation and surrounding mountain barrier heights to calculate realistic rain shadow deserts and lush windward river valleys.
3. Use the seasonal weather table to ground realistic travel weather and harvest campaigns in your manuscript.
</details>

---

## 1. Mathematical Biome & Temperature Profile

```
           Windward Slope                         Leeward Rain Shadow
           Moist Air (DALR/MALR)                  Dry Adiabatic Compression
               ☁️ 🌧️ 🌧️                             ☀️  (Foehn Heating)
              /                                         \
             /   [Highland Cloud Forest]                 \   [Arid Basin]
            /    Elev: 1,450m  Temp: 12.4°C               \  Elev: 400m  Temp: 24.1°C
           /     Precip: 1,250 mm/yr                       \ Precip: 210 mm/yr
    ______/                                                 \______
```

| Parameter | Windward Incline | Mountain Crest (3,200m) | Leeward Basin (400m) |
| :--- | :--- | :--- | :--- |
| **Biome Type** | Temperate Cloud Forest (`Cfb`) | Alpine Tundra (`ET`) | Semi-Arid Steppe (`BSk`) |
| **Annual Rainfall**| 1,250 mm | 1,800 mm (Snow/Ice) | 210 mm (Rain Shadow) |
| **Mean Summer High**| 21.0°C | 6.5°C | 34.0°C |
| **Mean Winter Low** | -2.5°C | -22.0°C | 2.0°C |

---

## 2. Seasonal Weather Dynamics & Narrative Hazards

### Spring (Month of Thaw)
- **Meteorological Profile**: Rapid snowmelt from the 3,200m crest generates flash floods in the lower gorges. Heavy morning advection fog blankets all roads below 1,000m until midday.
- **Story Hazard**: Mountain passes are blocked by mudslides; carriage travel is impossible without pack mules.

### Summer (The High Sun)
- **Meteorological Profile**: Steady southwesterly trade winds bring afternoon orographic thunderstorms between 14:00 and 17:00 daily.
- **Sensory Cues**: Electrified air, sweet smell of damp fir needles, boiling purple cloud formations hugging the granite spires.

### Autumn (The Frost Wind)
- **Meteorological Profile**: Crisp, clear days with sharp nocturnal radiation inversions. Freezing frost lines creep down from the peaks by the third week.
- **Story Hazard**: Early blizzards can trap traveling armies on the high ridges without winter rations.

### Winter (The Long Dark)
- **Meteorological Profile**: Persistent katabatic downdrafts rushing down from the glacier field; snowdrifts accumulate up to 4 meters along north-facing ramparts.

---

## 3. Exoplanetary & Planetary Climate Archetypes

| Preset Identifier | Planetary Archetype | Atmospheric Regime | Key Biome & Survival Zone |
| :--- | :--- | :--- | :--- |
| `preset-tidally-locked` | Tidally Locked Eyeball World | 1-Cell Day-to-Night circulation; perpetual substellar upwelling | Twilight Terminator Ring (`Cfb`/`Dfb` microclimates with perpetual gale winds) |
| `preset-runaway-greenhouse` | Super-Earth Greenhouse | Dense $\text{CO}_2/\text{H}_2\text{O}$ vapor blanket ($P_{\text{surf}} > 35\text{ atm}$, $T > 300^\circ\text{C}$) | Aerostat Cloud Cities at $z = 55\text{ km}$ ($P \sim 1\text{ atm}$, $T \sim 25^\circ\text{C}$) |
| `preset-snowball-cryo` | Glaciated Snowball World | High Bond albedo ($A > 0.65$), global sea ice ($z > 150\text{ m}$) | Sub-Glacial Hydrothermal Vents and volcanic rift ecosystems |

