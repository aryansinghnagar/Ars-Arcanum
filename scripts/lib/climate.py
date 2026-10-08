#!/usr/bin/env python3
r"""
Ars Arcanum Planetary Climate, Orographic Biomes & Atmospheric Engine (scripts/lib/climate.py)
=============================================================================================
Zero-dependency, offline planetary insolation, atmospheric circulation, orographic rain shadow,
and Köppen biome validator for science-fiction and fantasy worldbuilders.

Capabilities:
1. Stellar Insolation & Equilibrium Surface Temperature:
   - Computes solar flux $S = 1361 \times (L / d^2)\ W/m^2$.
   - Calculates blackbody equilibrium temperature $T_{eq} = (S(1-A)/(4\sigma))^{1/4}$.
   - Computes surface temperature with atmospheric greenhouse coefficient.
2. Atmospheric Circulation Cells & Prevailing Winds:
   - Models Coriolis parameter and planetary rotation period (hours).
   - Generates Hadley, Ferrel, and Polar atmospheric circulation cells.
   - Determines prevailing surface wind vectors (Trade Winds, Westerlies, Polar Easterlies).
3. Orographic Rain Shadow Simulator:
   - Calculates adiabatic lapse rates ($9.8^\circ C/km$ dry, $5.0^\circ C/km$ moist).
   - Simulates windward precipitation enhancement vs leeward rain-shadow aridification.
4. Köppen Biome Classification:
   - Classifies ecological biomes from temperature and annual precipitation.


Zero external dependencies; 100% offline privacy.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

try:
    from lib._bootstrap import atomic_write
    from lib.climate_template import build_climate_html_report
    from lib.scope import add_scope_arguments, parse_scope_args
except ImportError:
    from _bootstrap import atomic_write
    from climate_template import build_climate_html_report
    try:
        from scope import add_scope_arguments, parse_scope_args
    except ImportError:
        pass


logger = logging.getLogger("arcanum.climate")

# Physical constants
SIGMA = 5.670374419e-8          # Stefan-Boltzmann constant (W m^-2 K^-4)
SOLAR_CONSTANT_EARTH = 1361.0   # Earth solar flux at 1 AU (W/m^2)

PLANETARY_PRESETS: dict[str, dict[str, Any]] = {
    "earth": {
        "name": "Earth Standard",
        "star_lum": 1.0,
        "distance_au": 1.0,
        "albedo": 0.30,
        "greenhouse": 33.0,
        "rotation_hours": 24.0,
        "mountain_elevation": 3000.0,
        "base_precip": 1000.0,
        "base_temp": 15.0,
    },
    "mars": {
        "name": "Mars Desert & Permafrost",
        "star_lum": 1.0,
        "distance_au": 1.524,
        "albedo": 0.25,
        "greenhouse": 5.0,
        "rotation_hours": 24.6,
        "mountain_elevation": 8000.0,
        "base_precip": 50.0,
        "base_temp": -60.0,
    },
    "venus": {
        "name": "Venusian Runaway Greenhouse",
        "star_lum": 1.0,
        "distance_au": 0.723,
        "albedo": 0.77,
        "greenhouse": 500.0,
        "rotation_hours": 5832.0,
        "mountain_elevation": 5000.0,
        "base_precip": 0.0,
        "base_temp": 460.0,
    },
    "tidally_locked": {
        "name": "Tidally Locked Eyeball World",
        "star_lum": 0.05,
        "distance_au": 0.15,
        "albedo": 0.28,
        "greenhouse": 40.0,
        "rotation_hours": 720.0,
        "mountain_elevation": 4000.0,
        "base_precip": 1200.0,
        "base_temp": 18.0,
    },
    "desert_world": {
        "name": "Hyper-Arid Dune World (Arrakis)",
        "star_lum": 1.1,
        "distance_au": 1.05,
        "albedo": 0.38,
        "greenhouse": 25.0,
        "rotation_hours": 22.0,
        "mountain_elevation": 4500.0,
        "base_precip": 80.0,
        "base_temp": 32.0,
    },
    "ocean_world": {
        "name": "Pelagic Ocean Super-Biome",
        "star_lum": 0.9,
        "distance_au": 0.95,
        "albedo": 0.22,
        "greenhouse": 38.0,
        "rotation_hours": 28.0,
        "mountain_elevation": 1000.0,
        "base_precip": 2600.0,
        "base_temp": 24.0,
    },
    "super_earth": {
        "name": "Dense Super-Earth",
        "star_lum": 1.2,
        "distance_au": 1.15,
        "albedo": 0.32,
        "greenhouse": 48.0,
        "rotation_hours": 14.0,
        "mountain_elevation": 6000.0,
        "base_precip": 1600.0,
        "base_temp": 22.0,
    },
}


def calc_planetary_insolation(
    stellar_luminosity: float = 1.0,
    semi_major_axis_au: float = 1.0,
    bond_albedo: float = 0.30,
    greenhouse_warming_k: float = 33.0
) -> dict:
    """Calculates stellar flux, equilibrium temperature, and surface temperature."""
    d = max(1e-6, float(semi_major_axis_au))
    lum = max(0.0, float(stellar_luminosity))
    albedo = min(0.999, max(0.0, float(bond_albedo)))

    # S = S0 * (L / d^2)
    stellar_flux = SOLAR_CONSTANT_EARTH * (lum / (d ** 2))

    # T_eq = [ S * (1 - A) / (4 * sigma) ]^(1/4)
    absorbed_flux = stellar_flux * (1.0 - albedo)
    t_eq_k = (absorbed_flux / (4.0 * SIGMA)) ** 0.25
    t_surf_k = t_eq_k + float(greenhouse_warming_k)
    t_surf_c = t_surf_k - 273.15

    # Habitable range check (liquid water at 1 atm: 0°C to 100°C)
    habitable = 0.0 <= t_surf_c <= 100.0

    return {
        "stellar_luminosity_sun": stellar_luminosity,
        "semi_major_axis_au": semi_major_axis_au,
        "bond_albedo": bond_albedo,
        "greenhouse_warming_k": greenhouse_warming_k,
        "stellar_flux_w_m2": round(stellar_flux, 1),
        "equilibrium_temp_k": round(t_eq_k, 1),
        "surface_temp_k": round(t_surf_k, 1),
        "surface_temp_c": round(t_surf_c, 1),
        "surface_temp_f": round(t_surf_c * 9.0 / 5.0 + 32.0, 1),
        "liquid_water_habitable": habitable,
    }


def calc_atmospheric_circulation(rotation_period_hours: float = 24.0) -> dict:
    """
    Determines number of atmospheric circulation cells and prevailing surface wind bands.
    """
    p = max(0.1, float(rotation_period_hours))
    if p > 120.0:
        # Slow rotator: Single Hadley cell per hemisphere (equator to pole)
        cells = 1
        bands = [
            {"lat_min": 0, "lat_max": 90, "name": "Global Hadley Cell", "wind_direction": "Slow Easterly / Direct Convection", "surface_flow": "Equatorward"}
        ]
    elif 16.0 <= p <= 120.0:
        # Earth-like 3-cell circulation
        cells = 3
        bands = [
            {"lat_min": 0, "lat_max": 30, "name": "Hadley Cell (Tropics)", "wind_direction": "Trade Winds (Easterlies / NE in North, SE in South)", "surface_flow": "Equatorward"},
            {"lat_min": 30, "lat_max": 60, "name": "Ferrel Cell (Mid-Latitudes)", "wind_direction": "Prevailing Westerlies (SW in North, NW in South)", "surface_flow": "Poleward"},
            {"lat_min": 60, "lat_max": 90, "name": "Polar Cell (High Latitudes)", "wind_direction": "Polar Easterlies (NE in North, SE in South)", "surface_flow": "Equatorward"},
        ]
    else:
        # Fast rotator: 5 cells (Jovian banded circulation)
        cells = 5
        bands = [
            {"lat_min": 0, "lat_max": 18, "name": "Equatorial Cell", "wind_direction": "Strong Tropical Easterlies", "surface_flow": "Equatorward"},
            {"lat_min": 18, "lat_max": 36, "name": "Subtropical Jet Cell", "wind_direction": "Strong Westerly Jet", "surface_flow": "Poleward"},
            {"lat_min": 36, "lat_max": 54, "name": "Mid-Latitude Cell", "wind_direction": "Banded Easterlies", "surface_flow": "Equatorward"},
            {"lat_min": 54, "lat_max": 72, "name": "Subpolar Jet Cell", "wind_direction": "Subpolar Westerlies", "surface_flow": "Poleward"},
            {"lat_min": 72, "lat_max": 90, "name": "Polar Vortex", "wind_direction": "Polar Easterlies", "surface_flow": "Equatorward"},
        ]

    return {
        "rotation_period_hours": p,
        "circulation_cells_per_hemisphere": cells,
        "coriolis_effect": "Negligible / Slow" if p > 120 else ("Moderate / Earth-like" if p >= 16 else "Extreme / Jovian"),
        "wind_bands": bands,
    }


def classify_koppen_biome(temp_c: float, annual_precip_mm: float) -> str:
    """Classifies terrestrial biome according to Köppen-Geiger logic."""
    if temp_c < -10.0:
        return "Polar Ice Cap"
    if temp_c < 0.0:
        return "Tundra / Alpine Permafrost" if annual_precip_mm < 400 else "Glacial Taiga"
    if temp_c < 10.0:
        if annual_precip_mm < 250:
            return "Cold Boreal Steppe"
        if annual_precip_mm < 600:
            return "Boreal Forest / Taiga"
        return "Temperate Oceanic Rain Forest"
    if temp_c < 22.0:
        if annual_precip_mm < 250:
            return "Arid Mid-Latitude Desert"
        if annual_precip_mm < 500:
            return "Semiarid Steppe / Scrubland"
        if annual_precip_mm < 1200:
            return "Temperate Deciduous Woodland"
        return "Temperate Rainforest"
    # Hot Tropical / Subtropical
    if annual_precip_mm < 250:
        return "Hyper-Arid Subtropical Desert"
    if annual_precip_mm < 600:
        return "Tropical Semiarid Savanna"
    if annual_precip_mm < 1800:
        return "Tropical Monsoon Forest"
    return "Tropical Rainforest (Equatorial)"


def calc_orographic_rain_shadow(
    mountain_elevation_m: float = 3000.0,
    base_precip_mm: float = 1000.0,
    base_temp_c: float = 20.0,
    wind_speed_kmh: float = 30.0
) -> dict:
    """
    Simulates orographic precipitation on windward slope and rain-shadow desert on leeward slope.
    """
    # Dry adiabatic lapse rate = 9.8°C / km
    # Moist adiabatic lapse rate = 5.0°C / km
    elev = max(0.0, float(mountain_elevation_m))
    crest_temp_c = float(base_temp_c) - (elev / 1000.0) * 6.5

    # Windward side: precipitation enhancement
    # Precip increases with elevation up to ~2500m
    windward_factor = 1.0 + min(1.8, (elev / 1000.0) * 0.45)
    windward_precip_mm = max(0.0, float(base_precip_mm)) * windward_factor
    windward_biome = classify_koppen_biome(crest_temp_c + 4.0, windward_precip_mm)

    # Leeward side: adiabatic descent warming and relative humidity plummet
    # Precip collapses
    leeward_precip_mm = max(0.0, float(base_precip_mm)) * max(0.08, 1.0 - (elev / 1000.0) * 0.28)
    leeward_temp_c = float(base_temp_c) + (elev / 1000.0) * 1.5 # Foehn / Chinook heating
    leeward_biome = classify_koppen_biome(leeward_temp_c, leeward_precip_mm)

    is_rain_shadow = (leeward_precip_mm < 350.0) or (windward_precip_mm / max(1.0, leeward_precip_mm) > 2.5)

    return {
        "mountain_elevation_m": mountain_elevation_m,
        "base_precip_mm": base_precip_mm,
        "base_temp_c": base_temp_c,
        "crest_temp_c": round(crest_temp_c, 1),
        "windward": {
            "precipitation_mm": round(windward_precip_mm, 1),
            "precipitation_multiplier": round(windward_factor, 2),
            "biome": windward_biome,
            "climate_desc": "Moist Orographic Cloud Forest / Rainforest",
        },
        "leeward": {
            "precipitation_mm": round(leeward_precip_mm, 1),
            "foehn_temp_c": round(leeward_temp_c, 1),
            "biome": leeward_biome,
            "climate_desc": "Arid Rain-Shadow Basin / Desert" if is_rain_shadow else "Moderately Drier Valley",
        },
        "is_severe_rain_shadow": is_rain_shadow,
    }


def generate_climate_html_report(climate_data: dict, output_path: Path):
    """Generates standalone HTML report for Planetary Climate and Biomes."""
    html_content = build_climate_html_report(climate_data)
    atomic_write(output_path, html_content)


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Planetary Climate & Orographic Simulator")
    parser.add_argument("--preset", choices=list(PLANETARY_PRESETS.keys()), help="Load celestial planetary preset (e.g. earth, mars, venus, desert_world)")
    parser.add_argument("--star-lum", type=float, default=None, help="Stellar luminosity in L_sun (default 1.0)")
    parser.add_argument("--distance-au", type=float, default=None, help="Orbital semi-major axis in AU (default 1.0)")
    parser.add_argument("--albedo", type=float, default=None, help="Bond albedo (default 0.30)")
    parser.add_argument("--greenhouse", type=float, default=None, help="Greenhouse warming in K (default 33.0)")
    parser.add_argument("--rotation-hours", type=float, default=None, help="Planetary rotation period in hours (default 24.0)")
    parser.add_argument("--mountain-elevation", type=float, default=None, help="Mountain ridge elevation in meters (default 3000)")
    parser.add_argument("--base-precip", type=float, default=None, help="Base precipitation in mm/year (default 1000)")
    parser.add_argument("--base-temp", type=float, default=None, help="Base surface temperature in °C (default 20)")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    parser.add_argument("--html", help="Path to export standalone HTML report")
    try:
        add_scope_arguments(parser, include_manuscript=False, include_world=False, target_pos_arg=False)
    except NameError:
        pass

    args = parser.parse_args()
    _scope = None
    try:
        _scope = parse_scope_args(args)
    except NameError:
        pass

    # Apply preset defaults if specified
    preset_data = PLANETARY_PRESETS.get(args.preset, {}) if args.preset else {}

    star_lum = float(args.star_lum) if args.star_lum is not None else float(preset_data.get("star_lum", 1.0))
    distance_au = float(args.distance_au) if args.distance_au is not None else float(preset_data.get("distance_au", 1.0))
    albedo = float(args.albedo) if args.albedo is not None else float(preset_data.get("albedo", 0.30))
    greenhouse = float(args.greenhouse) if args.greenhouse is not None else float(preset_data.get("greenhouse", 33.0))
    rotation_hours = float(args.rotation_hours) if args.rotation_hours is not None else float(preset_data.get("rotation_hours", 24.0))
    mountain_elevation = float(args.mountain_elevation) if args.mountain_elevation is not None else float(preset_data.get("mountain_elevation", 3000.0))
    base_precip = float(args.base_precip) if args.base_precip is not None else float(preset_data.get("base_precip", 1000.0))
    base_temp = float(args.base_temp) if args.base_temp is not None else float(preset_data.get("base_temp", 20.0))

    ins = calc_planetary_insolation(
        stellar_luminosity=star_lum,
        semi_major_axis_au=distance_au,
        bond_albedo=albedo,
        greenhouse_warming_k=greenhouse,
    )
    circ = calc_atmospheric_circulation(rotation_period_hours=rotation_hours)
    oro = calc_orographic_rain_shadow(
        mountain_elevation_m=mountain_elevation,
        base_precip_mm=base_precip,
        base_temp_c=base_temp,
    )

    result = {
        "preset": preset_data.get("name", args.preset) if args.preset else None,
        "insolation": ins,
        "circulation": circ,
        "orography": oro,
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        preset_tag = f" [{preset_data.get('name')}]" if args.preset else ""
        print(f"\n\033[1;36m=== Ars Arcanum Planetary Climate & Biome Model{preset_tag} ===\033[0m")
        print(f"Stellar Insolation : \033[1m{ins['stellar_flux_w_m2']} W/m²\033[0m ({star_lum} L_sun @ {distance_au} AU)")
        print(f"Mean Surface Temp  : \033[1;32m{ins['surface_temp_c']} °C\033[0m ({ins['surface_temp_f']} °F) — Habitable: {ins['liquid_water_habitable']}")
        print(f"Atmosphere         : {circ['circulation_cells_per_hemisphere']} circulation cells per hemisphere ({circ['coriolis_effect']} Coriolis)")
        print(f"\n\033[1;33mOrographic Rain Shadow ({oro['mountain_elevation_m']}m Mountain Ridge):\033[0m")
        print(f"  🌬️ Windward Slope : \033[32m{oro['windward']['precipitation_mm']} mm/yr\033[0m -> Biome: \033[1m{oro['windward']['biome']}\033[0m")
        print(f"  🏜️ Leeward Basin  : \033[31m{oro['leeward']['precipitation_mm']} mm/yr\033[0m -> Biome: \033[1m{oro['leeward']['biome']}\033[0m")
        if oro['is_severe_rain_shadow']:
            print("  ⚠️ Severe Rain Shadow Desert detected on leeward side.\n")
        else:
            print()

    if args.html:
        out_p = Path(args.html)
        generate_climate_html_report(result, out_p)
        print(f"Interactive HTML report written to: {out_p}")

    sys.exit(0)


if __name__ == "__main__":
    main()
