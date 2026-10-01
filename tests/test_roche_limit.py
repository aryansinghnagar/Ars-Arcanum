#!/usr/bin/env python3
"""
Unit tests for Astrophysics Roche Limit Calculator
(scripts/lib/astrophysics.py: calc_roche_limit)
"""

import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.astrophysics import calc_roche_limit, roche_limit, calc_roche, EARTH_RADIUS


class TestRocheLimit(unittest.TestCase):

    def test_earth_moon_roche_limit_fluid_and_rigid(self):
        # Earth: radius ~ 6371000 m, density ~ 5515 kg/m3
        # Moon: density ~ 3344 kg/m3
        res = calc_roche_limit(
            planet_radius_m=EARTH_RADIUS,
            density_planet_kgm3=5515.0,
            density_moon_kgm3=3344.0,
        )

        self.assertIn("rigid_roche_limit_km", res)
        self.assertIn("fluid_roche_limit_km", res)
        self.assertIn("fluid_roche_limit_radii", res)
        self.assertIn("ring_formation_zone", res)

        # Rigid Roche Limit ~ 9497 km
        self.assertAlmostEqual(res["rigid_roche_limit_km"], 9497.0, delta=200.0)
        # Fluid Roche Limit ~ 18386 km
        self.assertAlmostEqual(res["fluid_roche_limit_km"], 18386.0, delta=300.0)
        self.assertGreater(res["fluid_roche_limit_km"], res["rigid_roche_limit_km"])

    def test_roche_limit_density_ratio(self):
        res = calc_roche_limit(planet_radius_m=70000000.0, density_ratio=1.33)
        self.assertGreater(res["fluid_roche_limit_km"], 70000.0)
        self.assertGreater(res["rigid_roche_limit_km"], 70000.0)

    def test_roche_limit_aliases(self):
        res1 = calc_roche_limit(planet_radius_m=6371000.0, density_planet_kgm3=5515.0, density_moon_kgm3=3344.0)
        res2 = roche_limit(planet_radius_m=6371000.0, density_planet_kgm3=5515.0, density_moon_kgm3=3344.0)
        res3 = calc_roche(planet_radius_m=6371000.0, density_planet_kgm3=5515.0, density_moon_kgm3=3344.0)
        self.assertEqual(res1["rigid_roche_limit_km"], res2["rigid_roche_limit_km"])
        self.assertEqual(res1["fluid_roche_limit_km"], res3["fluid_roche_limit_km"])

    def test_roche_limit_zero_validation(self):
        with self.assertRaises(ValueError):
            calc_roche_limit(planet_radius_m=0.0)
        with self.assertRaises(ValueError):
            calc_roche_limit(planet_radius_m=6000000.0, density_planet_kgm3=5000.0, density_moon_kgm3=0.0)


if __name__ == "__main__":
    unittest.main()
