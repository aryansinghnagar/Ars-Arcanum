#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Astrophysics & Relativistic Flight Engine (scripts/lib/astrophysics.py).
Covers Brachistochrone trajectories, Lorentz factors, time dilation, Hohmann transfers, comms latencies,
planetary habitability / surface gravity calculations, and CLI subcommands.
"""

import io
import json
import tempfile
import unittest
from pathlib import Path
import sys
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.astrophysics import (
    G0, AU, LIGHT_YEAR, PARSEC, EARTH_MASS, EARTH_RADIUS, SOLAR_LUMINOSITY, parse_distance, parse_acceleration, format_duration, format_distance,
    calc_brachistochrone, calc_time_dilation, calc_orbital_transfer,
    calc_comms_delay, calc_habitability_gravity, generate_astrophysics_html_report,
    generate_dossier_html_report, generate_dossier_markdown_report,
    calc_planetary_dossier, main, print_table
)


class TestAstrophysicsEngine(unittest.TestCase):

    def test_parse_distance(self):
        self.assertAlmostEqual(parse_distance("1.0 AU"), AU, places=1)
        self.assertAlmostEqual(parse_distance("2 astronomical units"), 2 * AU, places=1)
        self.assertAlmostEqual(parse_distance("4.2 ly"), 4.2 * LIGHT_YEAR, places=1)
        self.assertAlmostEqual(parse_distance("3 light-years"), 3 * LIGHT_YEAR, places=1)
        self.assertAlmostEqual(parse_distance("1000 km"), 1000000.0)
        self.assertAlmostEqual(parse_distance("5 kilometers"), 5000.0)
        self.assertAlmostEqual(parse_distance("earth-moon"), 384400000.0)
        self.assertAlmostEqual(parse_distance("alpha-centauri"), 4.37 * LIGHT_YEAR, places=1)
        self.assertAlmostEqual(parse_distance("54 mkm"), 54e9)
        self.assertAlmostEqual(parse_distance("54 million-km"), 54e9)
        self.assertAlmostEqual(parse_distance("54 million kilometers"), 54e9)
        self.assertAlmostEqual(parse_distance("2.5 bkm"), 2.5e12)
        self.assertAlmostEqual(parse_distance("2.5 billion-km"), 2.5e12)
        self.assertAlmostEqual(parse_distance("2.5 billion kilometers"), 2.5e12)
        self.assertAlmostEqual(parse_distance("10 kpc"), 10.0 * 1e3 * PARSEC)
        self.assertAlmostEqual(parse_distance("2 kiloparsecs"), 2.0 * 1e3 * PARSEC)
        self.assertAlmostEqual(parse_distance("5 mpc"), 5.0 * 1e6 * PARSEC)
        self.assertAlmostEqual(parse_distance("1 megaparsec"), 1.0 * 1e6 * PARSEC)
        self.assertAlmostEqual(parse_distance("1 parsec"), PARSEC)
        self.assertAlmostEqual(parse_distance("2 pc"), 2 * PARSEC)
        self.assertAlmostEqual(parse_distance("500 meters"), 500.0)
        self.assertAlmostEqual(parse_distance("123.45"), 123.45)

    def test_parse_acceleration(self):
        self.assertAlmostEqual(parse_acceleration("1g"), G0, places=3)
        self.assertAlmostEqual(parse_acceleration("g"), G0, places=3)
        self.assertAlmostEqual(parse_acceleration("2g"), 2.0 * G0, places=3)
        self.assertAlmostEqual(parse_acceleration("9.81 m/s^2"), 9.81, places=2)
        self.assertAlmostEqual(parse_acceleration("5.0 m/s2"), 5.0, places=2)
        self.assertAlmostEqual(parse_acceleration("15.5"), 15.5, places=2)

    def test_format_duration(self):
        self.assertEqual(format_duration(-5.0), "0s")
        self.assertIn("seconds", format_duration(45.0))
        self.assertIn("minutes", format_duration(300.0))
        self.assertIn("hours", format_duration(7200.0))
        self.assertIn("days", format_duration(86400.0 * 5))
        self.assertIn("years", format_duration(86400.0 * 365.25 * 3.5))

    def test_format_distance(self):
        self.assertIn("kpc", format_distance(PARSEC * 2000.0))
        self.assertIn("ly", format_distance(LIGHT_YEAR * 4.2))
        self.assertIn("AU", format_distance(AU * 1.5))
        self.assertIn("km", format_distance(50000000.0))
        self.assertIn("m", format_distance(500.0))

    def test_brachistochrone_relativistic_sublight(self):
        d = 225e9
        res = calc_brachistochrone(d, acc_mps2=G0)
        self.assertGreater(res["proper_time_sec"], 0)
        self.assertGreater(res["coordinate_time_sec"], 0)
        self.assertAlmostEqual(res["peak_gamma"], 1.0, places=3)
        self.assertAlmostEqual(res["proper_time_sec"], res["coordinate_time_sec"], delta=10.0)

    def test_brachistochrone_interstellar_relativistic(self):
        d = 4.37 * LIGHT_YEAR
        res = calc_brachistochrone(d, acc_mps2=G0, exhaust_vel_mps=3e7)
        proper_years = res["proper_time_sec"] / (86400.0 * 365.25)
        coord_years = res["coordinate_time_sec"] / (86400.0 * 365.25)
        self.assertGreater(coord_years, proper_years)
        self.assertGreater(res["peak_velocity_c_fraction"], 0.90)
        self.assertGreater(res["peak_gamma"], 2.0)
        self.assertIsNotNone(res["propellant_mass_ratio"])

    def test_time_dilation_kinematic(self):
        res = calc_time_dilation(beta=0.866)
        kin = res["kinematic"]
        self.assertAlmostEqual(kin["gamma"], 2.0, places=1)
        self.assertAlmostEqual(kin["crew_time_ratio"], 0.5, places=1)
        self.assertAlmostEqual(kin["proper_seconds_per_observer_day"], 43200.0, delta=100.0)

    def test_time_dilation_variants(self):
        res_v = calc_time_dilation(v_mps=100000000.0)
        self.assertIn("kinematic", res_v)
        res_gamma = calc_time_dilation(gamma=2.5)
        self.assertAlmostEqual(res_gamma["kinematic"]["gamma"], 2.5)

    def test_time_dilation_gravitational(self):
        res = calc_time_dilation(beta=0.0, grav_mass_kg=EARTH_MASS, grav_radius_m=EARTH_RADIUS)
        self.assertIn("gravitational", res)
        g_info = res["gravitational"]
        self.assertAlmostEqual(g_info["gravitational_dilation_factor"], 1.0, places=5)
        self.assertGreater(g_info["schwarzschild_radius_m"], 0.0)

    def test_hohmann_orbital_transfer(self):
        r1 = 1.0 * AU
        r2 = 1.524 * AU
        res = calc_orbital_transfer(primary_body="sun", r1_m=r1, r2_m=r2)
        self.assertAlmostEqual(res["v1_kms"], 29.78, delta=0.5)
        transfer_days = res["transfer_duration_sec"] / 86400.0
        self.assertAlmostEqual(transfer_days, 258.8, delta=10.0)
        self.assertAlmostEqual(res["delta_v_total_kms"], 5.59, delta=0.5)

    def test_comms_delay(self):
        res = calc_comms_delay(384400000.0)
        self.assertAlmostEqual(res["one_way_seconds"], 1.282, places=2)
        self.assertAlmostEqual(res["round_trip_seconds"], 2.564, places=2)

    def test_habitability_gravity(self):
        res = calc_habitability_gravity(EARTH_MASS, EARTH_RADIUS)
        self.assertAlmostEqual(res["surface_gravity_g"], 1.0, places=2)
        self.assertAlmostEqual(res["escape_velocity_kms"], 11.18, delta=0.1)
        hz = res["habitable_zone_conservative"]
        self.assertAlmostEqual(hz["inner_au"], 0.95, delta=0.05)
        self.assertAlmostEqual(hz["outer_au"], 1.37, delta=0.05)

    def test_html_and_markdown_report_generation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_file = Path(tmp_dir) / "astro_report.html"
            sample_data = {"Mission Metrics": calc_brachistochrone(AU * 2.0)}
            generate_astrophysics_html_report("Test Flight", sample_data, out_file)
            self.assertTrue(out_file.is_file())
            content = out_file.read_text(encoding="utf-8")
            self.assertIn("Test Flight", content)
            self.assertIn("Ars Arcanum Relativistic & Astrophysics Engine", content)

            dossier = calc_planetary_dossier(
                mass_kg=EARTH_MASS, radius_m=EARTH_RADIUS,
                star_luminosity_watts=SOLAR_LUMINOSITY, semi_major_axis_au=1.0,
                planet_type="eyeball-world"
            )
            dossier_html = Path(tmp_dir) / "dossier.html"
            generate_dossier_html_report("Eyeball Dossier", dossier, dossier_html)
            self.assertTrue(dossier_html.is_file())

            dossier_md = Path(tmp_dir) / "dossier.md"
            generate_dossier_markdown_report("Eyeball Dossier", dossier, dossier_md)
            self.assertTrue(dossier_md.is_file())

    def test_planetary_dossier_types(self):
        types_to_test = ["tidally-locked", "eyeball-world", "greenhouse-runaway", "super-earth", "custom"]
        for pt in types_to_test:
            dossier = calc_planetary_dossier(
                mass_kg=EARTH_MASS * (3.0 if pt == "super-earth" else 1.0),
                radius_m=EARTH_RADIUS * (1.5 if pt == "super-earth" else 1.0),
                star_luminosity_watts=SOLAR_LUMINOSITY,
                semi_major_axis_au=0.2 if pt == "greenhouse-runaway" else 1.0,
                planet_type=pt
            )
            self.assertEqual(dossier["planet_type"], pt)
            self.assertIn("habitability_metrics", dossier)
            self.assertIn("scientific_plausibility_warnings", dossier)

    def test_boundary_validation_clamps(self):
        with self.assertRaises(ValueError):
            calc_brachistochrone(0.0)
        with self.assertRaises(ValueError):
            calc_brachistochrone(1000.0, acc_mps2=-1.0)
        with self.assertRaises(ValueError):
            calc_orbital_transfer(r1_m=-1.0)
        with self.assertRaises(ValueError):
            calc_comms_delay(-100.0)
        with self.assertRaises(ValueError):
            calc_habitability_gravity(EARTH_MASS, radius_m=0.0)
        with self.assertRaises(ValueError):
            calc_habitability_gravity(EARTH_MASS, EARTH_RADIUS, star_luminosity_watts=-10.0)
        with self.assertRaises(ValueError):
            calc_time_dilation(v_mps=3e9)
        with self.assertRaises(ValueError):
            calc_time_dilation(beta=1.5)
        with self.assertRaises(ValueError):
            calc_time_dilation(gamma=0.5)

    def test_print_table(self):
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            print_table("Test Header", [("Key 1", "Value 1"), ("Key 2", "Value 2")])
            output = mock_out.getvalue()
            self.assertIn("Test Header", output)
            self.assertIn("Key 1", output)

    def test_cli_subcommands(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            html_p = Path(tmp_dir) / "report.html"
            md_p = Path(tmp_dir) / "report.md"

            # transit json
            with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
                with patch("sys.argv", ["astrophysics.py", "transit", "1.0 AU", "--json"]):
                    main()
                    data = json.loads(mock_out.getvalue())
                    self.assertIn("peak_gamma", data)

            # transit table & html
            with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
                with patch("sys.argv", ["astrophysics.py", "transit", "alpha-centauri", "--accel", "1g", "--ve", "30000000", "--html", str(html_p)]):
                    main()
                    self.assertIn("Relativistic Brachistochrone Trajectory", mock_out.getvalue())
                    self.assertTrue(html_p.is_file())

            # dossier json
            with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
                with patch("sys.argv", ["astrophysics.py", "dossier", "--mass", "1.0", "--radius", "6371km", "--type", "tidally-locked", "--json"]):
                    main()
                    data = json.loads(mock_out.getvalue())
                    self.assertEqual(data["planet_type"], "tidally-locked")

            # dossier table + html + md
            with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
                with patch("sys.argv", ["astrophysics.py", "dossier", "--mass", "5.972e24kg", "--radius", "6371000m", "--type", "circumbinary", "--html", str(html_p), "--md", str(md_p)]):
                    main()
                    self.assertIn("Star System Dossier Overview", mock_out.getvalue())
                    self.assertTrue(md_p.is_file())

            # time-dilation json & table
            with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
                with patch("sys.argv", ["astrophysics.py", "time-dilation", "--beta", "0.8", "--json"]):
                    main()
                    data = json.loads(mock_out.getvalue())
                    self.assertIn("kinematic", data)

            with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
                with patch("sys.argv", ["astrophysics.py", "time-dilation", "--velocity", "0.5c", "--mass", str(EARTH_MASS), "--radius", str(EARTH_RADIUS)]):
                    main()
                    self.assertIn("Relativistic Time Dilation", mock_out.getvalue())

            with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
                with patch("sys.argv", ["astrophysics.py", "time-dilation", "--velocity", "1000km/s"]):
                    main()
                    self.assertIn("Relativistic Time Dilation", mock_out.getvalue())

            with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
                with patch("sys.argv", ["astrophysics.py", "time-dilation", "--velocity", "5000m/s"]):
                    main()
                    self.assertIn("Relativistic Time Dilation", mock_out.getvalue())

            # orbit json & table
            with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
                with patch("sys.argv", ["astrophysics.py", "orbit", "--r1", "1.0 AU", "--r2", "1.524 AU", "--json"]):
                    main()
                    data = json.loads(mock_out.getvalue())
                    self.assertIn("delta_v_total_kms", data)

            with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
                with patch("sys.argv", ["astrophysics.py", "orbit", "--r1", "1.0 AU", "--r2", "1.524 AU"]):
                    main()
                    self.assertIn("Hohmann Orbital Transfer", mock_out.getvalue())

            # comms json & table
            with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
                with patch("sys.argv", ["astrophysics.py", "comms", "earth-mars-avg", "--json"]):
                    main()
                    data = json.loads(mock_out.getvalue())
                    self.assertIn("one_way_seconds", data)

            with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
                with patch("sys.argv", ["astrophysics.py", "comms", "1.0 AU"]):
                    main()
                    self.assertIn("Electromagnetic Communication Delay", mock_out.getvalue())

            # habitability json & table
            with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
                with patch("sys.argv", ["astrophysics.py", "habitability", "--mass", "1.0", "--radius", "1.0", "--json"]):
                    main()
                    data = json.loads(mock_out.getvalue())
                    self.assertIn("surface_gravity_g", data)

            with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
                with patch("sys.argv", ["astrophysics.py", "habitability", "--mass", "5.972e24kg", "--radius", "6371km"]):
                    main()
                    self.assertIn("Planetary Habitability & Gravity Analysis", mock_out.getvalue())

            # error handling in CLI
            with patch("sys.stderr", new_callable=io.StringIO) as mock_err:
                with patch("sys.argv", ["astrophysics.py", "transit", "-500m"]):
                    with self.assertRaises(SystemExit) as cm:
                        main()
                    self.assertEqual(cm.exception.code, 1)
                    self.assertIn("Error:", mock_err.getvalue())

            # no subcommand
            with patch("sys.argv", ["astrophysics.py"]):
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
