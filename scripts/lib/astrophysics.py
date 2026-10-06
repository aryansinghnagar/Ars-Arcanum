#!/usr/bin/env python3
"""
Ars Arcanum Astrophysics & Relativistic Spaceflight Engine (scripts/lib/astrophysics.py)
=======================================================================================
Zero-dependency, offline astrophysics and relativistic trajectory calculator for
science-fiction worldbuilders and authors.

Capabilities:
1. Relativistic Brachistochrone (1g constant acceleration midpoint turnover) Trajectories:
   - Ship proper time (tau) vs coordinate observer time (t)
   - Midpoint turnover peak velocity (v_max / fraction of c)
   - Peak Lorentz factor (gamma)
   - Effective delta-v and relativistic rocket propellant mass ratios
2. Relativistic Kinematics & Time Dilation:
   - Lorentz factor gamma = 1 / sqrt(1 - (v/c)^2)
   - Coordinate time vs proper time dilation
   - Gravitational time dilation (Schwarzschild metric)
3. Orbital Transfers & Keplerian Mechanics:
   - Vis-viva circular and escape orbital velocities
   - Hohmann transfer delta-v and half-orbit transfer durations
   - Synodic period between planetary orbits
4. Light-Speed Communication & Signal Latencies:
   - One-way and round-trip communication delays across astronomical baselines
   - Built-in solar system and interstellar distance presets
5. Planetary Surface Gravity & Circumstellar Habitable Zone (HZ):
   - Surface gravity in m/s^2 and Earth-g equivalents
   - Escape velocities
   - Kopparapu conservative/optimistic habitable zone boundaries based on stellar luminosity

Outputs:
- Terminal ANSI formatted summary tables
- Machine-readable JSON (--json)
- Standalone interactive HTML report (--html <file>)
"""

import argparse
import json
import sys
from pathlib import Path

try:
    from lib.astrophysics_calc import (
        calc_brachistochrone,
        calc_comms_delay,
        calc_habitability_gravity,
        calc_orbital_transfer,
        calc_planetary_dossier,
        calc_roche_limit,
        calc_time_dilation,
    )
    from lib.astrophysics_data import (
        AU,
        BODY_PRESETS,
        C_SQ,
        DISTANCE_PRESETS,
        EARTH_MASS,
        EARTH_RADIUS,
        G0,
        LIGHT_YEAR,
        PARSEC,
        SECONDS_PER_DAY,
        SECONDS_PER_YEAR,
        SOLAR_LUMINOSITY,
        SOLAR_MASS,
        SOLAR_RADIUS,
        C,
        G,
        format_distance,
        format_duration,
        parse_acceleration,
        parse_distance,
    )
    from lib.astrophysics_template import (
        generate_astrophysics_html_report,
        generate_dossier_html_report,
        generate_dossier_markdown_report,
    )
    from lib.scope import (
        EngineScope,
        add_scope_arguments,
        parse_scope_args,
        resolve_world_path,
    )
except ImportError:
    try:
        from astrophysics_calc import (  # type: ignore[no-redef]
            calc_brachistochrone,
            calc_comms_delay,
            calc_habitability_gravity,
            calc_orbital_transfer,
            calc_planetary_dossier,
            calc_roche_limit,
            calc_time_dilation,
        )
        from astrophysics_data import (  # type: ignore[no-redef]
            AU,
            BODY_PRESETS,
            C_SQ,
            DISTANCE_PRESETS,
            EARTH_MASS,
            EARTH_RADIUS,
            G0,
            LIGHT_YEAR,
            PARSEC,
            SECONDS_PER_DAY,
            SECONDS_PER_YEAR,
            SOLAR_LUMINOSITY,
            SOLAR_MASS,
            SOLAR_RADIUS,
            C,
            G,
            format_distance,
            format_duration,
            parse_acceleration,
            parse_distance,
        )
        from astrophysics_template import (  # type: ignore[no-redef]
            generate_astrophysics_html_report,
            generate_dossier_html_report,
            generate_dossier_markdown_report,
        )
        from scope import (
            EngineScope,
            add_scope_arguments,
            parse_scope_args,
            resolve_world_path,
        )
    except ImportError:
        EngineScope = None  # type: ignore

        def add_scope_arguments(*args, **kwargs):  # type: ignore
            pass

        def parse_scope_args(*args, **kwargs):  # type: ignore
            return None

        def resolve_world_path(*args, **kwargs):  # type: ignore
            return None


__all__ = [
    "AU",
    "BODY_PRESETS",
    "C_SQ",
    "DISTANCE_PRESETS",
    "EARTH_MASS",
    "EARTH_RADIUS",
    "G0",
    "LIGHT_YEAR",
    "PARSEC",
    "SECONDS_PER_DAY",
    "SECONDS_PER_YEAR",
    "SOLAR_LUMINOSITY",
    "SOLAR_MASS",
    "SOLAR_RADIUS",
    "C",
    "G",
    "calc_brachistochrone",
    "calc_comms_delay",
    "calc_habitability_gravity",
    "calc_orbital_transfer",
    "calc_planetary_dossier",
    "calc_roche_limit",
    "calc_time_dilation",
    "format_distance",
    "format_duration",
    "generate_astrophysics_html_report",
    "generate_dossier_html_report",
    "generate_dossier_markdown_report",
    "main",
    "parse_acceleration",
    "parse_distance",
    "print_table",
]


# Canonical aliases
calc_roche_limits = calc_roche_limit
roche_limit = calc_roche_limit
calc_roche = calc_roche_limit
calc_brachistochrone_transit = calc_brachistochrone


# ==============================================================================
# CLI Entrypoint & Formatting
# ==============================================================================



def print_table(title: str, rows: list):
    """Prints a styled terminal table."""
    print(f"\n\033[1;36m=== {title} ===\033[0m")
    max_k = max(len(k) for k, _ in rows) + 2
    for k, v in rows:
        print(f"  \033[1m{k:<{max_k}}\033[0m: \033[32m{v}\033[0m")
    print()


def main():
    parser = argparse.ArgumentParser(description="Ars Arcanum Astrophysics & Relativistic Flight Engine")
    subparsers = parser.add_subparsers(dest="subcommand", help="Astrophysics subcommands")

    # 1. Transit / Brachistochrone
    p_transit = subparsers.add_parser("transit", help="Calculate relativistic Brachistochrone trajectory")
    p_transit.add_argument("distance", help="Distance (e.g. 'alpha-centauri', '1.5 AU', '4.2 ly', '54 mkm')")
    p_transit.add_argument("-a", "--accel", default="1g", help="Constant acceleration (default: '1g', or '9.81 m/s^2')")
    p_transit.add_argument("--ve", default=None, help="Exhaust velocity in m/s for rocket propellant mass ratio calculation")
    p_transit.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    p_transit.add_argument("--html", help="Path to export interactive HTML report")
    add_scope_arguments(p_transit, include_manuscript=False, include_world=True, target_pos_arg=False)

    # 2. Time Dilation
    p_td = subparsers.add_parser("time-dilation", help="Calculate relativistic velocity and gravitational time dilation")
    p_td.add_argument("-v", "--velocity", help="Velocity (e.g. '0.99c', '200000 km/s', '10000000 m/s')")
    p_td.add_argument("--beta", type=float, help="Velocity as fraction of light speed (0.0 to 0.99999)")
    p_td.add_argument("--gamma", type=float, help="Lorentz factor gamma (>= 1.0)")
    p_td.add_argument("--mass", type=float, help="Primary body mass (kg) for gravitational dilation")
    p_td.add_argument("--radius", type=float, help="Orbital/surface radius (meters) for gravitational dilation")
    p_td.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    add_scope_arguments(p_td, include_manuscript=False, include_world=True, target_pos_arg=False)

    # 3. Orbit / Hohmann Transfer
    p_orbit = subparsers.add_parser("orbit", help="Calculate Keplerian orbital mechanics and Hohmann transfers")
    p_orbit.add_argument("--primary", default="sun", help="Primary body ('sun', 'earth', 'jupiter', etc.)")
    p_orbit.add_argument("--r1", required=True, help="Initial orbit radius (e.g. '1.0 AU', '7000 km')")
    p_orbit.add_argument("--r2", required=True, help="Target orbit radius (e.g. '1.52 AU', '42164 km')")
    p_orbit.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    add_scope_arguments(p_orbit, include_manuscript=False, include_world=True, target_pos_arg=False)

    # 4. Comms Latency
    p_comms = subparsers.add_parser("comms", help="Calculate light-speed communication delays")
    p_comms.add_argument("distance", help="Baseline distance (e.g. 'earth-mars-avg', '5.2 AU', '4.3 ly')")
    p_comms.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    add_scope_arguments(p_comms, include_manuscript=False, include_world=True, target_pos_arg=False)

    # 5. Habitability & Surface Gravity
    p_hab = subparsers.add_parser("habitability", help="Calculate planetary surface gravity & habitable zone boundaries")
    p_hab.add_argument("--mass", default="1.0", help="Planet mass in Earth masses (e.g. '1.0', or '5.97e24 kg')")
    p_hab.add_argument("--radius", default="1.0", help="Planet radius in Earth radii (e.g. '1.0', or '6371 km')")
    p_hab.add_argument("--star-lum", default="1.0", help="Host star luminosity relative to Sun (default: 1.0)")
    p_hab.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    add_scope_arguments(p_hab, include_manuscript=False, include_world=True, target_pos_arg=False)

    # 6. Roche Limit & Ring Formation
    p_roche = subparsers.add_parser("roche", help="Calculate planetary tidal Roche limits and ring boundaries")
    p_roche.add_argument("--planet-radius", default="6371km", help="Primary body radius (e.g. '6371km', '1.0 Earth', or '70000km')")
    p_roche.add_argument("--density-planet", type=float, default=5515.0, help="Primary body density in kg/m^3 (default: 5515 Earth)")
    p_roche.add_argument("--density-moon", type=float, default=3344.0, help="Satellite density in kg/m^3 (default: 3344 Moon)")
    p_roche.add_argument("--density-ratio", type=float, default=None, help="Direct density ratio (rho_M / rho_m)")
    p_roche.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    p_roche.add_argument("--html", help="Path to export interactive HTML report")
    add_scope_arguments(p_roche, include_manuscript=False, include_world=True, target_pos_arg=False)

    p_dossier = subparsers.add_parser("dossier", help="Generate comprehensive Star System Dossier for non-standard planets")
    p_dossier.add_argument("--mass", default="1.0", help="Planet mass in Earth masses")
    p_dossier.add_argument("--radius", default="1.0", help="Planet radius in Earth radii")
    p_dossier.add_argument("--star-lum", default="1.0", help="Host star luminosity relative to Sun")
    p_dossier.add_argument("--distance-au", default="1.0", help="Orbital semi-major axis in AU")
    p_dossier.add_argument("--type", default="standard", choices=["standard", "tidally-locked", "gas-giant-exomoon", "brown-dwarf-world", "circumbinary", "hycean"], help="Non-standard planetary configuration")
    p_dossier.add_argument("--html", help="Path to export interactive HTML report")
    p_dossier.add_argument("--md", help="Path to export Markdown report")
    p_dossier.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    add_scope_arguments(p_dossier, include_manuscript=False, include_world=True, target_pos_arg=False)

    args = parser.parse_args()

    if not args.subcommand:
        parser.print_help()
        sys.exit(0)

    try:
        if args.subcommand == "transit":
            d_m = parse_distance(args.distance)
            a_mps2 = parse_acceleration(args.accel)
            ve = float(args.ve) if args.ve else None
            res = calc_brachistochrone(d_m, a_mps2, ve)

            if args.json:
                print(json.dumps(res, indent=2))
            else:
                newt_note = res["newtonian_time_formatted"]
                if res.get("newtonian_peak_velocity_mps", 0) > 299792458:
                    newt_c = res["newtonian_peak_velocity_mps"] / 299792458.0
                    newt_note += f" (Unphysical: peak v = {newt_c:.2f}c)"
                table = [
                    ("Mission Distance", f"{res['distance_formatted']} ({res['distance_m']:,.0f} m)"),
                    ("Constant Acceleration", f"{res['acceleration_g']:.3f} g ({res['acceleration_mps2']:.2f} m/s²)"),
                    ("Ship Proper Time (Crew)", res["proper_time_formatted"]),
                    ("Coordinate Time (Observer)", res["coordinate_time_formatted"]),
                    ("Time Dilation Difference", res["time_dilation_lag_formatted"]),
                    ("Peak Velocity (Turnover)", f"{res['peak_velocity_c_fraction'] * 100:.3f}% c ({res['peak_velocity_mps']/1000:,.1f} km/s)"),
                    ("Peak Lorentz Factor (γ)", f"{res['peak_gamma']:.4f}"),
                    ("Effective Total Delta-V", f"{res['effective_deltav_kms']:,.1f} km/s"),
                    ("Classical Newtonian Time", newt_note),
                ]
                if res["propellant_mass_ratio"]:
                    table.append(("Required Fuel Mass Ratio (m0/mf)", f"{res['propellant_mass_ratio']:.2e}"))
                print_table("Relativistic Brachistochrone Trajectory", table)

            if args.html:
                out_p = Path(args.html)
                generate_astrophysics_html_report(f"Brachistochrone Flight ({args.distance})", {"Trajectory Metrics": res}, out_p)
                print(f"Interactive HTML report written to: {out_p}")


        elif args.subcommand == "dossier":
            m_str = str(args.mass).strip().lower()
            m_kg = float(m_str[:-2]) if m_str.endswith("kg") else float(m_str) * EARTH_MASS

            r_str = str(args.radius).strip().lower()
            if r_str.endswith("km"):
                r_m = float(r_str[:-2]) * 1000.0
            elif r_str.endswith("m"):
                r_m = float(r_str[:-1])
            else:
                r_m = float(r_str) * EARTH_RADIUS

            l_star = float(args.star_lum) * SOLAR_LUMINOSITY
            d_au = float(args.distance_au)

            res = calc_planetary_dossier(
                mass_kg=m_kg, radius_m=r_m, star_luminosity_watts=l_star,
                semi_major_axis_au=d_au, planet_type=args.type
            )

            if args.json:
                print(json.dumps(res, indent=2))
            else:
                table = [
                    ("Configuration Type", res["planet_type"]),
                    ("Surface Gravity", f"{res['habitability_metrics']['surface_gravity_g']:.3f} g"),
                    ("Surface Temp (Equilibrium)", f"{res['climate_insolation']['surface_temp_c']:.1f} °C"),
                    ("Habitable (Liquid Water)", str(res['climate_insolation']['liquid_water_habitable'])),
                ]
                print_table("Star System Dossier Overview", table)
                if res['scientific_plausibility_warnings']:
                    print("\033[1;33mPlausibility & Drift Warnings:\033[0m")
                    for w in res['scientific_plausibility_warnings']:
                        print(f"  - {w}")
                    print()

            if args.html:
                out_p = Path(args.html)
                generate_dossier_html_report(f"Dossier ({args.type})", res, out_p)
                print(f"HTML Dossier exported to {out_p}")
            if args.md:
                out_p = Path(args.md)
                generate_dossier_markdown_report(f"Dossier ({args.type})", res, out_p)
                print(f"Markdown Dossier exported to {out_p}")

        elif args.subcommand == "time-dilation":
            beta_val = args.beta
            v_val = None
            if args.velocity:
                v_str = args.velocity.strip().lower()
                if v_str.endswith("c"):
                    beta_val = float(v_str[:-1])
                elif v_str.endswith("km/s"):
                    v_val = float(v_str[:-4]) * 1000.0
                elif v_str.endswith("m/s"):
                    v_val = float(v_str[:-3])
                else:
                    v_val = float(v_str)

            res = calc_time_dilation(
                v_mps=v_val,
                beta=beta_val,
                gamma=args.gamma,
                grav_mass_kg=args.mass,
                grav_radius_m=args.radius
            )

            if args.json:
                print(json.dumps(res, indent=2))
            else:
                kin = res["kinematic"]
                table = [
                    ("Velocity", f"{kin['velocity_kms']:,.2f} km/s ({kin['beta']*100:.4f}% c)"),
                    ("Lorentz Factor (γ)", f"{kin['gamma']:.6f}"),
                    ("Ship Time per 1 Earth Day", kin["proper_per_observer_day_formatted"]),
                    ("Time Dilation Lag per Day", kin["lag_per_observer_day_formatted"]),
                ]
                if "gravitational" in res:
                    g_info = res["gravitational"]
                    table.extend([
                        ("Gravitational Dilation Factor", f"{g_info['gravitational_dilation_factor']:.6f}"),
                        ("Schwarzschild Radius", f"{g_info['schwarzschild_radius_m']:,.2f} m"),
                    ])
                print_table("Relativistic Time Dilation", table)

        elif args.subcommand == "orbit":
            r1_m = parse_distance(args.r1)
            r2_m = parse_distance(args.r2)
            res = calc_orbital_transfer(primary_body=args.primary, r1_m=r1_m, r2_m=r2_m)

            if args.json:
                print(json.dumps(res, indent=2))
            else:
                table = [
                    ("Primary Celestial Body", res["primary_body"]),
                    ("Initial Orbit Radius (R1)", f"{res['r1_formatted']} (v={res['v1_kms']:.2f} km/s, T={res['period_r1_formatted']})"),
                    ("Target Orbit Radius (R2)", f"{res['r2_formatted']} (v={res['v2_kms']:.2f} km/s, T={res['period_r2_formatted']})"),
                    ("Transfer Transit Duration", res["transfer_duration_formatted"]),
                    ("Burn 1 Injection Δv", f"{res['delta_v1_kms']:.3f} km/s"),
                    ("Burn 2 Circularization Δv", f"{res['delta_v2_kms']:.3f} km/s"),
                    ("Total Transfer Budget Δv", f"{res['delta_v_total_kms']:.3f} km/s"),
                    ("Synodic Launch Window Period", res["synodic_period_formatted"]),
                ]
                print_table("Hohmann Orbital Transfer", table)

        elif args.subcommand == "comms":
            d_m = parse_distance(args.distance)
            res = calc_comms_delay(d_m)
            if args.json:
                print(json.dumps(res, indent=2))
            else:
                table = [
                    ("Baseline Distance", res["distance_formatted"]),
                    ("One-Way Signal Delay", res["one_way_formatted"]),
                    ("Round-Trip Ping Latency (RTT)", res["round_trip_formatted"]),
                ]
                print_table("Electromagnetic Communication Delay", table)

        elif args.subcommand == "habitability":
            # parse mass
            m_str = str(args.mass).strip().lower()
            m_kg = float(m_str[:-2]) if m_str.endswith("kg") else float(m_str) * EARTH_MASS

            # parse radius
            r_str = str(args.radius).strip().lower()
            if r_str.endswith("km"):
                r_m = float(r_str[:-2]) * 1000.0
            elif r_str.endswith("m"):
                r_m = float(r_str[:-1])
            else:
                r_m = float(r_str) * EARTH_RADIUS

            l_star = float(args.star_lum) * SOLAR_LUMINOSITY
            res = calc_habitability_gravity(m_kg, r_m, l_star)

            if args.json:
                print(json.dumps(res, indent=2))
            else:
                hz = res["habitable_zone_conservative"]
                table = [
                    ("Surface Gravity", f"{res['surface_gravity_g']:.3f} g ({res['surface_gravity_mps2']:.2f} m/s²)"),
                    ("Escape Velocity", f"{res['escape_velocity_kms']:.2f} km/s"),
                    ("Planet Mass", f"{res['mass_earth_ratio']:.2f} M_Earth"),
                    ("Planet Radius", f"{res['radius_earth_ratio']:.2f} R_Earth"),
                    ("Conservative Habitable Zone", f"{hz['inner_au']:.2f} AU – {hz['outer_au']:.2f} AU"),
                ]
                print_table("Planetary Habitability & Gravity Analysis", table)

        elif args.subcommand == "roche":
            # parse radius
            r_str = str(args.planet_radius).strip().lower()
            if r_str.endswith("km"):
                r_m = float(r_str[:-2]) * 1000.0
            elif r_str.endswith("m"):
                r_m = float(r_str[:-1])
            elif "earth" in r_str:
                r_m = float(r_str.replace("earth", "").strip() or "1.0") * EARTH_RADIUS
            elif "jupiter" in r_str:
                r_m = float(r_str.replace("jupiter", "").strip() or "1.0") * 71492000.0
            else:
                r_m = float(r_str) * 1000.0 if float(r_str) < 1000000 else float(r_str)

            res = calc_roche_limit(
                planet_radius_m=r_m,
                density_planet_kgm3=float(args.density_planet),
                density_moon_kgm3=float(args.density_moon),
                density_ratio=float(args.density_ratio) if args.density_ratio is not None else None,
            )

            if args.json:
                print(json.dumps(res, indent=2))
            else:
                table = [
                    ("Primary Body Radius", f"{res['planet_radius_km']:,.1f} km"),
                    ("Density Ratio (ρ_planet / ρ_moon)", f"{res['density_ratio']:.4f}"),
                    ("Rigid Roche Limit", f"{res['rigid_roche_limit_km']:,.1f} km ({res['rigid_roche_limit_radii']:.2f} R_planet)"),
                    ("Fluid Roche Limit", f"{res['fluid_roche_limit_km']:,.1f} km ({res['fluid_roche_limit_radii']:.2f} R_planet)"),
                    ("Stable Ring Formation Zone", f"{res['ring_formation_zone']['inner_km']:,.1f} km – {res['ring_formation_zone']['outer_km']:,.1f} km"),
                ]
                print_table("Planetary Tidal Roche Limits & Ring Boundaries", table)

            if getattr(args, "html", None):
                out_p = Path(args.html)
                generate_astrophysics_html_report(f"Roche Limits ({res['planet_radius_km']} km body)", {"Tidal Boundaries": res}, out_p)

    except Exception as e:
        print(f"\033[31mError: {e}\033[0m", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
