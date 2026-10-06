#!/usr/bin/env python3
"""
Ars Arcanum Astrophysics Calculation Engine (scripts/lib/astrophysics_calc.py)
=============================================================================
Pure mathematical models for relativistic brachistochrone trajectories,
Lorentz kinematics, Keplerian orbital mechanics, communications latencies,
planetary habitability metrics, tidal Roche limits, and star system dossiers.
"""

from __future__ import annotations

import math
from typing import Any

try:
    from lib.astrophysics_data import (
        AU,
        BODY_PRESETS,
        C_SQ,
        EARTH_MASS,
        EARTH_RADIUS,
        G0,
        SECONDS_PER_DAY,
        SOLAR_LUMINOSITY,
        SOLAR_MASS,
        C,
        G,
        format_distance,
        format_duration,
    )
    from lib.climate import calc_atmospheric_circulation, calc_planetary_insolation
except ImportError:
    from astrophysics_data import (  # type: ignore[no-redef]
        AU,
        BODY_PRESETS,
        C_SQ,
        EARTH_MASS,
        EARTH_RADIUS,
        G0,
        SECONDS_PER_DAY,
        SOLAR_LUMINOSITY,
        SOLAR_MASS,
        C,
        G,
        format_distance,
        format_duration,
    )
    try:
        from climate import calc_atmospheric_circulation, calc_planetary_insolation  # type: ignore[no-redef]
    except ImportError:
        def calc_planetary_insolation(*args: Any, **kwargs: Any) -> dict[str, Any]:
            return {"surface_temp_c": 15.0, "liquid_water_habitable": True}

        def calc_atmospheric_circulation(*args: Any, **kwargs: Any) -> dict[str, Any]:
            return {}


def calc_brachistochrone(distance_m: float, acc_mps2: float = G0, exhaust_vel_mps: float | None = None) -> dict[str, Any]:
    """
    Calculates exact relativistic 1-turnover (accelerate to midpoint, decelerate to stop)
    continuous-thrust Brachistochrone spaceflight trajectory.
    """
    if distance_m <= 0:
        raise ValueError("Flight distance must be greater than zero.")
    if acc_mps2 <= 0:
        raise ValueError("Acceleration must be greater than zero.")

    a = acc_mps2
    d = distance_m
    half_d = d / 2.0

    # Relativistic parameter alpha = a * d_half / c^2
    alpha = (a * half_d) / C_SQ
    gamma_max = 1.0 + alpha

    # Peak velocity at turnover midpoint
    if gamma_max > 1.0:
        beta_max = math.sqrt(1.0 - 1.0 / (gamma_max * gamma_max))
        v_max = beta_max * C
    else:
        beta_max = 0.0
        v_max = 0.0

    # Ship Proper Time (tau): tau = 2 * (c / a) * acosh(1 + a*d / (2*c^2))
    tau_sec = 2.0 * (C / a) * math.acosh(gamma_max)

    # Coordinate / Observer Time (t): t = 2 * (c / a) * sqrt((1 + a*d / (2*c^2))^2 - 1)
    t_sec = 2.0 * (C / a) * math.sqrt(gamma_max * gamma_max - 1.0)

    # Time lag between observer and crew
    time_dilation_lag_sec = t_sec - tau_sec

    # Newtonian (classical) non-relativistic comparison
    t_newton_sec = 2.0 * math.sqrt(d / a)
    v_newton_mps = math.sqrt(a * d)

    # Effective total delta-v: 2 * c * atanh(v_max / c) = a * tau
    effective_deltav = a * tau_sec

    # Propellant mass ratio if exhaust velocity is specified
    mass_ratio = None
    if exhaust_vel_mps and exhaust_vel_mps > 0:
        mass_ratio = math.exp(effective_deltav / exhaust_vel_mps)

    # Photon rocket ideal mass ratio: sqrt((1 + beta_max)/(1 - beta_max)) for each leg
    photon_mass_ratio = ((1.0 + beta_max) / (1.0 - beta_max)) if beta_max < 1.0 else float("inf")

    return {
        "distance_m": d,
        "distance_formatted": format_distance(d),
        "acceleration_mps2": a,
        "acceleration_g": a / G0,
        "proper_time_sec": tau_sec,
        "proper_time_formatted": format_duration(tau_sec),
        "coordinate_time_sec": t_sec,
        "coordinate_time_formatted": format_duration(t_sec),
        "time_dilation_lag_sec": time_dilation_lag_sec,
        "time_dilation_lag_formatted": format_duration(time_dilation_lag_sec),
        "peak_velocity_mps": v_max,
        "peak_velocity_c_fraction": beta_max,
        "peak_gamma": gamma_max,
        "effective_deltav_mps": effective_deltav,
        "effective_deltav_kms": effective_deltav / 1000.0,
        "newtonian_time_sec": t_newton_sec,
        "newtonian_time_formatted": format_duration(t_newton_sec),
        "newtonian_peak_velocity_mps": v_newton_mps,
        "exhaust_velocity_mps": exhaust_vel_mps,
        "propellant_mass_ratio": mass_ratio,
        "photon_mass_ratio": photon_mass_ratio,
    }


def calc_time_dilation(
    v_mps: float | None = None,
    beta: float | None = None,
    gamma: float | None = None,
    grav_mass_kg: float | None = None,
    grav_radius_m: float | None = None,
) -> dict[str, Any]:
    """Calculates special and general relativistic time dilation."""
    res: dict[str, Any] = {}
    if beta is not None:
        v_mps = beta * C
    elif v_mps is not None:
        beta = v_mps / C
    elif gamma is not None:
        if gamma < 1.0:
            raise ValueError("Lorentz factor gamma must be >= 1.0")
        beta = math.sqrt(1.0 - 1.0 / (gamma * gamma))
        v_mps = beta * C
    else:
        v_mps = 0.0
        beta = 0.0

    if beta >= 1.0:
        raise ValueError("Velocity cannot equal or exceed the speed of light c")

    kin_gamma = 1.0 / math.sqrt(1.0 - beta * beta)
    tau_per_day = SECONDS_PER_DAY / kin_gamma
    lag_per_day = SECONDS_PER_DAY - tau_per_day

    res["kinematic"] = {
        "velocity_mps": v_mps,
        "velocity_kms": v_mps / 1000.0,
        "beta": beta,
        "gamma": kin_gamma,
        "crew_time_ratio": 1.0 / kin_gamma,
        "proper_seconds_per_observer_day": tau_per_day,
        "proper_per_observer_day_formatted": format_duration(tau_per_day),
        "lag_per_observer_day_formatted": format_duration(lag_per_day),
    }

    if grav_mass_kg and grav_radius_m:
        r_schwarzschild = (2.0 * G * grav_mass_kg) / C_SQ
        grav_factor = 0.0 if grav_radius_m <= r_schwarzschild else math.sqrt(1.0 - r_schwarzschild / grav_radius_m)
        res["gravitational"] = {
            "mass_kg": grav_mass_kg,
            "radius_m": grav_radius_m,
            "schwarzschild_radius_m": r_schwarzschild,
            "gravitational_dilation_factor": grav_factor,
            "time_rate_vs_infinity": grav_factor,
        }

    return res


def calc_orbital_transfer(
    primary_body: str = "sun",
    r1_m: float | None = None,
    r2_m: float | None = None,
    primary_mass_kg: float | None = None,
) -> dict[str, Any]:
    """Calculates Keplerian Hohmann orbital transfer delta-v and durations."""
    if r1_m is None:
        r1_m = AU
    if r2_m is None:
        r2_m = 1.524 * AU
    if r1_m <= 0 or r2_m <= 0:
        raise ValueError("Orbital radii r1 and r2 must be greater than zero.")
    m_primary = primary_mass_kg
    body_name = primary_body.capitalize()
    if primary_body.lower() in BODY_PRESETS:
        preset = BODY_PRESETS[primary_body.lower()]
        m_primary = preset["mass"]
        body_name = preset["name"]
    elif not m_primary:
        m_primary = SOLAR_MASS
        body_name = "Sun (Standard)"

    if m_primary <= 0:
        raise ValueError("Primary body mass must be greater than zero.")

    mu = G * m_primary

    # Circular orbit velocities
    v1 = math.sqrt(mu / r1_m)
    v2 = math.sqrt(mu / r2_m)

    # Orbital periods
    t1_sec = 2.0 * math.pi * math.sqrt((r1_m ** 3) / mu)
    t2_sec = 2.0 * math.pi * math.sqrt((r2_m ** 3) / mu)

    # Transfer ellipse semi-major axis
    a_trans = (r1_m + r2_m) / 2.0
    transfer_time_sec = math.pi * math.sqrt((a_trans ** 3) / mu)

    # Delta-v burns
    v_trans_1 = math.sqrt(mu * (2.0 / r1_m - 1.0 / a_trans))
    v_trans_2 = math.sqrt(mu * (2.0 / r2_m - 1.0 / a_trans))

    dv1 = abs(v_trans_1 - v1)
    dv2 = abs(v2 - v_trans_2)
    dv_total = dv1 + dv2

    # Synodic period between orbits
    synodic_sec = None
    if abs(t1_sec - t2_sec) > 1e-3:
        synodic_sec = 1.0 / abs(1.0 / t1_sec - 1.0 / t2_sec)

    return {
        "primary_body": body_name,
        "primary_mass_kg": m_primary,
        "r1_m": r1_m,
        "r1_formatted": format_distance(r1_m),
        "r2_m": r2_m,
        "r2_formatted": format_distance(r2_m),
        "v1_mps": v1,
        "v1_kms": v1 / 1000.0,
        "v2_mps": v2,
        "v2_kms": v2 / 1000.0,
        "period_r1_formatted": format_duration(t1_sec),
        "period_r2_formatted": format_duration(t2_sec),
        "transfer_duration_sec": transfer_time_sec,
        "transfer_duration_formatted": format_duration(transfer_time_sec),
        "delta_v1_mps": dv1,
        "delta_v1_kms": dv1 / 1000.0,
        "delta_v2_mps": dv2,
        "delta_v2_kms": dv2 / 1000.0,
        "delta_v_total_mps": dv_total,
        "delta_v_total_kms": dv_total / 1000.0,
        "synodic_period_formatted": format_duration(synodic_sec) if synodic_sec else "N/A",
    }


def calc_comms_delay(distance_m: float) -> dict[str, Any]:
    """Calculates electromagnetic signal propagation latencies."""
    if distance_m < 0:
        raise ValueError("Comms distance cannot be negative.")
    one_way_sec = distance_m / C
    rtt_sec = 2.0 * one_way_sec
    return {
        "distance_m": distance_m,
        "distance_formatted": format_distance(distance_m),
        "one_way_seconds": one_way_sec,
        "one_way_formatted": format_duration(one_way_sec),
        "round_trip_seconds": rtt_sec,
        "round_trip_formatted": format_duration(rtt_sec),
    }


def calc_habitability_gravity(
    mass_kg: float,
    radius_m: float,
    star_luminosity_watts: float = SOLAR_LUMINOSITY,
) -> dict[str, Any]:
    """Calculates planetary surface gravity, escape velocity, and stellar habitable zone."""
    if radius_m <= 0:
        raise ValueError("Planetary radius must be greater than zero.")
    if mass_kg < 0:
        raise ValueError("Planetary mass cannot be negative.")
    if star_luminosity_watts < 0:
        raise ValueError("Stellar luminosity cannot be negative.")

    g_surf = (G * mass_kg) / (radius_m * radius_m)
    g_ratio = g_surf / G0
    v_esc = math.sqrt((2.0 * G * mass_kg) / radius_m)

    l_rel = star_luminosity_watts / SOLAR_LUMINOSITY
    hz_inner_au = math.sqrt(l_rel) * 0.95
    hz_outer_au = math.sqrt(l_rel) * 1.37
    hz_optimistic_inner_au = math.sqrt(l_rel) * 0.75
    hz_optimistic_outer_au = math.sqrt(l_rel) * 1.77

    return {
        "mass_kg": mass_kg,
        "mass_earth_ratio": mass_kg / EARTH_MASS,
        "radius_m": radius_m,
        "radius_earth_ratio": radius_m / EARTH_RADIUS,
        "surface_gravity_mps2": g_surf,
        "surface_gravity_g": g_ratio,
        "escape_velocity_mps": v_esc,
        "escape_velocity_kms": v_esc / 1000.0,
        "stellar_luminosity_rel_sun": l_rel,
        "habitable_zone_conservative": {
            "inner_au": hz_inner_au,
            "outer_au": hz_outer_au,
            "inner_m": hz_inner_au * AU,
            "outer_m": hz_outer_au * AU,
        },
        "habitable_zone_optimistic": {
            "inner_au": hz_optimistic_inner_au,
            "outer_au": hz_optimistic_outer_au,
        }
    }


def calc_roche_limit(
    planet_radius_m: float,
    density_planet_kgm3: float = 5515.0,
    density_moon_kgm3: float = 3344.0,
    density_ratio: float | None = None,
) -> dict[str, Any]:
    """Calculates rigid and fluid Roche tidal disruption limits and ring formation zones."""
    if planet_radius_m <= 0:
        raise ValueError("Planetary radius must be greater than zero.")

    if density_ratio is not None and density_ratio > 0:
        ratio = float(density_ratio)
    else:
        if density_planet_kgm3 <= 0 or density_moon_kgm3 <= 0:
            raise ValueError("Densities must be greater than zero.")
        ratio = density_planet_kgm3 / density_moon_kgm3

    c_root = ratio ** (1.0 / 3.0)
    d_rigid_m = planet_radius_m * (2.0 ** (1.0 / 3.0)) * c_root
    d_fluid_m = 2.44 * planet_radius_m * c_root

    return {
        "planet_radius_m": planet_radius_m,
        "planet_radius_km": planet_radius_m / 1000.0,
        "density_ratio": round(ratio, 4),
        "rigid_roche_limit_m": d_rigid_m,
        "rigid_roche_limit_km": d_rigid_m / 1000.0,
        "rigid_roche_limit_radii": round(d_rigid_m / planet_radius_m, 3),
        "fluid_roche_limit_m": d_fluid_m,
        "fluid_roche_limit_km": d_fluid_m / 1000.0,
        "fluid_roche_limit_radii": round(d_fluid_m / planet_radius_m, 3),
        "ring_formation_zone": {
            "inner_km": round(planet_radius_m / 1000.0, 1),
            "outer_km": round(d_fluid_m / 1000.0, 1),
        },
    }


# Canonical aliases
calc_roche_limits = calc_roche_limit
roche_limit = calc_roche_limit
calc_roche = calc_roche_limit
calc_brachistochrone_transit = calc_brachistochrone


def calc_planetary_dossier(
    mass_kg: float,
    radius_m: float,
    star_luminosity_watts: float,
    semi_major_axis_au: float,
    planet_type: str = "standard",
    albedo: float = 0.30,
    greenhouse_k: float = 33.0,
    rotation_hours: float = 24.0,
) -> dict[str, Any]:
    """Calculates comprehensive planetary habitability, insolation, circulation, and warnings."""
    hab = calc_habitability_gravity(mass_kg, radius_m, star_luminosity_watts)

    climate_ins = calc_planetary_insolation(
        stellar_luminosity=star_luminosity_watts / SOLAR_LUMINOSITY,
        semi_major_axis_au=semi_major_axis_au,
        bond_albedo=albedo,
        greenhouse_warming_k=greenhouse_k
    )

    if planet_type == "tidally-locked":
        l_solar = max(1e-6, star_luminosity_watts / SOLAR_LUMINOSITY)
        star_mass_solar = max(0.08, l_solar ** (1.0 / 3.5))
        rotation_hours = math.sqrt((semi_major_axis_au ** 3) / star_mass_solar) * 365.25 * 24.0

    climate_circ = calc_atmospheric_circulation(rotation_period_hours=rotation_hours)

    warnings: list[str] = []

    g_ratio = hab["surface_gravity_g"]
    if g_ratio > 3.0:
        warnings.append("High surface gravity: Biological structures would need to be exceptionally squat and robust. Atmosphere will be highly compressed.")
    elif g_ratio < 0.3:
        warnings.append("Low surface gravity: May struggle to retain a dense atmosphere over geological timecales.")

    if planet_type == "tidally-locked":
        warnings.append("Tidally locked: Permanent dayside and nightside. Expected 'eyeball' world configuration with habitable terminator zone if atmosphere transfers heat.")
    elif planet_type == "gas-giant-exomoon":
        warnings.append("Exomoon: Significant tidal heating expected. Day/night cycle dominated by orbit around primary. Watch for eclipses and intense radiation belts.")
    elif planet_type == "brown-dwarf-world":
        warnings.append("Brown dwarf system: Minimal visible light, dominated by infrared. Photosynthesis would require specialized pigments. Small habitable zone.")
    elif planet_type == "circumbinary":
        warnings.append("Circumbinary (P/S-type): Orbital stability is complex. Insolation will vary significantly over the orbit, leading to extreme seasons.")
    elif planet_type == "hycean":
        warnings.append("Hycean: Global ocean with hydrogen-rich atmosphere. High pressures at ocean floor. Biosignatures may differ from Earth-like worlds.")

    if not climate_ins.get("liquid_water_habitable", False):
        warnings.append(f"Temperature Drift: Equilibrium surface temp is {climate_ins.get('surface_temp_c', 0.0)} °C, outside standard liquid water range.")

    return {
        "planet_type": planet_type,
        "habitability_metrics": hab,
        "climate_insolation": climate_ins,
        "climate_circulation": climate_circ,
        "scientific_plausibility_warnings": warnings
    }
