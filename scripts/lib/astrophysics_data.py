#!/usr/bin/env python3
"""
Ars Arcanum Astrophysics Data & Constants (scripts/lib/astrophysics_data.py)
===========================================================================
Astronomical constants, standard solar system body presets, interstellar distance
presets, and unit parsing/formatting routines for speculative spaceflight models.
"""

from __future__ import annotations

import re
from typing import Any

# --- Physical & Astronomical Constants (SI Units) ---
C = 299792458.0                          # Speed of light in vacuum (m/s)
C_SQ = C * C                             # c^2 (m^2/s^2)
G = 6.67430e-11                          # Gravitational constant (m^3 kg^-1 s^-2)
G0 = 9.80665                             # Standard Earth surface gravity (m/s^2, 1g)
AU = 149597870700.0                      # Astronomical Unit (meters)
LIGHT_YEAR = 9460730472580800.0          # 1 Light Year (meters)
PARSEC = 30856775814913700.0             # 1 Parsec (meters)
SOLAR_MASS = 1.98847e30                  # Solar Mass M_sun (kg)
EARTH_MASS = 5.9722e24                   # Earth Mass M_earth (kg)
EARTH_RADIUS = 6371000.0                 # Earth volumetric mean radius (meters)
SOLAR_LUMINOSITY = 3.828e26              # Solar Luminosity L_sun (Watts)
SOLAR_RADIUS = 6.957e8                   # Solar Radius R_sun (meters)
SECONDS_PER_DAY = 86400.0
SECONDS_PER_YEAR = 31557600.0            # Julian year (365.25 days)

# --- Standard Distance Presets (meters) ---
DISTANCE_PRESETS: dict[str, float] = {
    "earth-moon": 384400000.0,
    "earth-mars-min": 54600000000.0,
    "earth-mars-avg": 225000000000.0,
    "earth-mars-max": 401000000000.0,
    "earth-jupiter-min": 588000000000.0,
    "earth-jupiter-avg": 778500000000.0,
    "earth-jupiter-max": 968000000000.0,
    "earth-saturn": 1433000000000.0,
    "earth-neptune": 4500000000000.0,
    "earth-pluto": 5900000000000.0,
    "kuiper-belt-inner": 30.0 * AU,
    "oort-cloud-inner": 2000.0 * AU,
    "proxima-centauri": 4.2465 * LIGHT_YEAR,
    "alpha-centauri": 4.37 * LIGHT_YEAR,
    "sirius": 8.611 * LIGHT_YEAR,
    "vega": 25.04 * LIGHT_YEAR,
    "trappist-1": 39.46 * LIGHT_YEAR,
    "galactic-center": 26000.0 * LIGHT_YEAR,
    "andromeda": 2537000.0 * LIGHT_YEAR,
}

# --- Standard Body Presets ---
BODY_PRESETS: dict[str, dict[str, Any]] = {
    "sun": {"mass": SOLAR_MASS, "radius": SOLAR_RADIUS, "name": "Sun"},
    "mercury": {"mass": 3.3011e23, "radius": 2439700.0, "semi_major_au": 0.3871, "name": "Mercury"},
    "venus": {"mass": 4.8675e24, "radius": 6051800.0, "semi_major_au": 0.7233, "name": "Venus"},
    "earth": {"mass": EARTH_MASS, "radius": EARTH_RADIUS, "semi_major_au": 1.0, "name": "Earth"},
    "moon": {"mass": 7.342e22, "radius": 1737400.0, "name": "Moon"},
    "mars": {"mass": 6.4171e23, "radius": 3389500.0, "semi_major_au": 1.5237, "name": "Mars"},
    "jupiter": {"mass": 1.8982e27, "radius": 69911000.0, "semi_major_au": 5.2044, "name": "Jupiter"},
    "saturn": {"mass": 5.6834e26, "radius": 58232000.0, "semi_major_au": 9.5826, "name": "Saturn"},
    "uranus": {"mass": 8.6810e25, "radius": 25362000.0, "semi_major_au": 19.2184, "name": "Uranus"},
    "neptune": {"mass": 1.02413e26, "radius": 24622000.0, "semi_major_au": 30.1104, "name": "Neptune"},
}


def parse_distance(val_str: str) -> float:
    """Parses human string representation of distance to meters."""
    s = val_str.strip().lower()
    if s in DISTANCE_PRESETS:
        return DISTANCE_PRESETS[s]

    # Check suffixes (longest / multi-word first)
    if s.endswith(("million-km", "million km", "mkm", "million kilometers", "million kilometer")):
        num_str = re.split(r"(?:million[-\s]?km|mkm|million[-\s]?kilometer[s]?)", s)[0].strip()
        return float(num_str) * 1e9
    if s.endswith(("billion-km", "billion km", "bkm", "billion kilometers", "billion kilometer")):
        num_str = re.split(r"(?:billion[-\s]?km|bkm|billion[-\s]?kilometer[s]?)", s)[0].strip()
        return float(num_str) * 1e12
    if s.endswith(("kpc", "kiloparsec", "kiloparsecs")):
        num_str = re.split(r"(?:kpc|kiloparsec[s]?)", s)[0].strip()
        return float(num_str) * 1e3 * PARSEC
    if s.endswith(("mpc", "megaparsec", "megaparsecs")):
        num_str = re.split(r"(?:mpc|megaparsec[s]?)", s)[0].strip()
        return float(num_str) * 1e6 * PARSEC
    if s.endswith(("parsec", "parsecs", "pc")):
        num_str = re.split(r"(?:parsec[s]?|pc)", s)[0].strip()
        return float(num_str) * PARSEC
    if s.endswith(("light-years", "light-year", "lightyear", "lightyears", "ly")):
        num_str = re.split(r"(?:light[-\s]?year[s]?|ly)", s)[0].strip()
        return float(num_str) * LIGHT_YEAR
    if s.endswith(("astronomical unit", "astronomical units", "au")):
        num_str = re.split(r"(?:astronomical\s+unit[s]?|au)", s)[0].strip()
        return float(num_str) * AU
    if s.endswith(("kilometer", "kilometers", "km")):
        num_str = re.split(r"(?:kilometer[s]?|km)", s)[0].strip()
        return float(num_str) * 1000.0
    if s.endswith(("meter", "meters", "m")):
        num_str = re.split(r"(?:meter[s]?|m)", s)[0].strip()
        return float(num_str)

    return float(s)


def parse_acceleration(val_str: str) -> float:
    """Parses acceleration string to m/s^2."""
    s = val_str.strip().lower()
    if s.endswith("g"):
        num = float(s[:-1].strip() or "1")
        return num * G0
    if s.endswith(("m/s^2", "m/s2")):
        return float(s.split("m/s")[0].strip())
    return float(s)


def format_duration(seconds: float) -> str:
    """Formats seconds into human readable duration string (years, days, hours, mins, secs)."""
    if seconds < 0:
        return "0s"
    if seconds < 60:
        return f"{seconds:.2f} seconds"
    if seconds < 3600:
        mins = seconds / 60.0
        return f"{mins:.2f} minutes ({int(seconds // 60)}m {int(seconds % 60)}s)"
    if seconds < SECONDS_PER_DAY:
        hours = seconds / 3600.0
        m = int((seconds % 3600) // 60)
        return f"{hours:.2f} hours ({int(hours)}h {m}m)"
    if seconds < SECONDS_PER_YEAR:
        days = seconds / SECONDS_PER_DAY
        h = int((seconds % SECONDS_PER_DAY) // 3600)
        return f"{days:.2f} days ({int(days)}d {h}h)"

    years = seconds / SECONDS_PER_YEAR
    rem_days = (seconds % SECONDS_PER_YEAR) / SECONDS_PER_DAY
    return f"{years:.3f} years ({int(years)}y {int(rem_days)}d)"


def format_distance(meters: float) -> str:
    """Formats meters into most intuitive astronomical unit."""
    if meters >= PARSEC * 1000.0:
        return f"{meters / (PARSEC * 1000.0):.2f} kpc ({meters / LIGHT_YEAR:.1f} ly)"
    if meters >= LIGHT_YEAR * 0.1:
        return f"{meters / LIGHT_YEAR:.3f} ly ({meters / PARSEC:.3f} pc)"
    if meters >= AU * 0.1:
        return f"{meters / AU:.3f} AU ({meters / 1e9:.2f} million km)"
    if meters >= 1e6:
        return f"{meters / 1000.0:,.0f} km ({meters / AU:.4f} AU)"
    return f"{meters:,.1f} m"
