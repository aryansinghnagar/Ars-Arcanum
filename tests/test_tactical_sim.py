#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Dynamic Tactical Combat Simulator (scripts/lib/tactical_sim.py).
Validates:
- WOR-104: Fighter attributes, armor mitigation, initiative, and morale checks.
- Terrain modifiers (open field, castle walls, dense forest, dungeon corridor).
- Monte Carlo probability analysis and blow-by-blow narrative fight logs.
- MVP tracking, combatant type coverage, win rate arithmetic.
- High-level warfare scenario planning with Lanchester's Square Law analysis.
- Lanchester warfare reference guide generation.
- CLI execution and modes (sim, plan, guide).
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

from lib.tactical_sim import (
    simulate_single_battle,
    run_monte_carlo,
    plan_warfare_scenario,
    get_lanchester_warfare_guide,
    main,
    DEFAULT_SIDE1,
    DEFAULT_SIDE2,
    TERRAIN_MODIFIERS,
)


class TestTacticalSimulator(unittest.TestCase):

    def test_single_battle_simulation(self):
        """simulate_single_battle must return a valid result dict with winner in {0,1,2}."""
        battle = simulate_single_battle(DEFAULT_SIDE1, DEFAULT_SIDE2, terrain="open_field")
        self.assertIn(battle["winner"], (0, 1, 2))
        self.assertGreater(battle["rounds_lasted"], 0)
        self.assertGreater(len(battle["log"]), 3)
        self.assertIn("mvp", battle)

    def test_monte_carlo_probability(self):
        """run_monte_carlo must return runs count and non-negative win rates."""
        mc = run_monte_carlo(DEFAULT_SIDE1, DEFAULT_SIDE2, terrain="open_field", runs=20)
        self.assertEqual(mc["runs"], 20)
        self.assertGreaterEqual(mc["side1_win_rate"], 0.0)
        self.assertGreaterEqual(mc["side2_win_rate"], 0.0)
        self.assertGreater(mc["avg_rounds"], 0)

    def test_castle_walls_defense_advantage(self):
        """simulate_single_battle with castle_walls terrain must complete and return winner_name."""
        battle = simulate_single_battle(DEFAULT_SIDE1, DEFAULT_SIDE2, terrain="castle_walls")
        self.assertIsNotNone(battle["winner_name"])

    def test_simulate_returns_winner_key_valid(self):
        """Winner must be 0 (draw), 1 (Side 1 wins), or 2 (Side 2 wins)."""
        for terrain in ("open_field", "dense_forest", "dungeon_corridor"):
            battle = simulate_single_battle(DEFAULT_SIDE1, DEFAULT_SIDE2, terrain=terrain)
            self.assertIn(battle["winner"], (0, 1, 2))

    def test_terrain_modifiers_schema(self):
        """Each terrain modifier must have name, ranged_mod, def_bonus, and desc."""
        required = {"name", "ranged_mod", "def_bonus", "desc"}
        for mod in TERRAIN_MODIFIERS.values():
            self.assertTrue(required.issubset(mod.keys()))

    def test_monte_carlo_win_rates_sum_to_100(self):
        mc = run_monte_carlo(DEFAULT_SIDE1, DEFAULT_SIDE2, terrain="open_field", runs=50)
        total = mc["side1_win_rate"] + mc["side2_win_rate"] + mc["draw_rate"]
        self.assertAlmostEqual(total, 100.0, delta=0.2)

    def test_plan_warfare_scenario_attacker_decisive(self):
        att = {"name": "Grand Imperial Army", "troops": 10000, "tech_level": "advanced", "morale": 90, "supplies_days": 60}
        dfn = {"name": "Isolated Garrison", "troops": 1000, "tech_level": "medieval", "morale": 50}
        res = plan_warfare_scenario(att, dfn, terrain="open_field", season="summer")

        self.assertIn("Decisive Attacker Victory", res["predicted_outcome"])
        self.assertGreater(res["combat_power_ratio"], 2.0)
        self.assertEqual(len(res["story_beats"]), 4)
        self.assertIn("lanchester_analysis", res)

    def test_plan_warfare_scenario_frictions_and_defender_victory(self):
        att = {"name": "Starving Invaders", "troops": 1200, "supplies_days": 7}
        dfn = {"name": "Fortress Defenders", "troops": 2000, "morale": 80}
        res = plan_warfare_scenario(att, dfn, terrain="castle_walls", season="winter")

        self.assertTrue("Defender" in res["predicted_outcome"] or "Rout" in res["predicted_outcome"])

    def test_plan_warfare_scenario_stalemate_and_rout(self):
        # Stalemate
        att_equal = {"name": "Army A", "troops": 1000}
        dfn_equal = {"name": "Army B", "troops": 1000}
        res_equal = plan_warfare_scenario(att_equal, dfn_equal, terrain="open_field")
        self.assertIn("Stalemate", res_equal["predicted_outcome"])

        # Catastrophic Rout
        att_small = {"name": "Tiny Raiding Party", "troops": 100}
        dfn_huge = {"name": "Massive Host", "troops": 5000}
        res_rout = plan_warfare_scenario(att_small, dfn_huge, terrain="open_field")
        self.assertIn("Catastrophic Attacker Rout", res_rout["predicted_outcome"])

    def test_lanchester_warfare_guide(self):
        guide = get_lanchester_warfare_guide()
        self.assertIn("Lanchester's Linear Law", guide)
        self.assertIn("Lanchester's Square Law", guide)
        self.assertIn("Terrain & Tactical Asymmetry Multipliers", guide)

    def test_cli_main_guide_and_plan(self):
        # Guide
        with patch.object(sys, "argv", ["tactical_sim.py", "guide"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                main()
                self.assertIn("Lanchester's Laws", mock_stdout.getvalue())

        # Plan text
        with patch.object(sys, "argv", ["tactical_sim.py", "plan", "--attacker-troops", "3000", "--defender-troops", "1000"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                main()
                self.assertIn("Warfare Scenario Analysis", mock_stdout.getvalue())

        # Plan JSON
        with patch.object(sys, "argv", ["tactical_sim.py", "plan", "--json"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                main()
                data = json.loads(mock_stdout.getvalue())
                self.assertIn("predicted_outcome", data)

    def test_cli_main_sim(self):
        with tempfile.TemporaryDirectory() as td:
            s1_file = Path(td) / "s1.json"
            s2_file = Path(td) / "s2.json"
            s1_file.write_text(json.dumps(DEFAULT_SIDE1), encoding="utf-8")
            s2_file.write_text(json.dumps(DEFAULT_SIDE2), encoding="utf-8")

            # Single battle JSON
            with patch.object(sys, "argv", ["tactical_sim.py", "sim", "--side1", str(s1_file), "--side2", str(s2_file), "--json"]):
                with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                    main()
                    data = json.loads(mock_stdout.getvalue())
                    self.assertIn("winner_name", data)

            # Monte Carlo text
            with patch.object(sys, "argv", ["tactical_sim.py", "sim", "-n", "10"]):
                with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                    main()
                    self.assertIn("Monte Carlo Tactical Simulation", mock_stdout.getvalue())

            # Single battle text
            with patch.object(sys, "argv", ["tactical_sim.py", "sim"]):
                with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                    main()
                    self.assertIn("Tactical Skirmish Result", mock_stdout.getvalue())

    def test_cli_main_no_args(self):
        with patch.object(sys, "argv", ["tactical_sim.py"]), self.assertRaises(SystemExit):
            main()

    def test_deterministic_seed_repeatability(self):
        """Verify that giving an explicit seed reproduces identical battle trajectories and outcomes."""
        res1 = simulate_single_battle(DEFAULT_SIDE1, DEFAULT_SIDE2, terrain="open_field", seed=42)
        res2 = simulate_single_battle(DEFAULT_SIDE1, DEFAULT_SIDE2, terrain="open_field", seed=42)
        self.assertEqual(res1["winner"], res2["winner"])
        self.assertEqual(res1["rounds_lasted"], res2["rounds_lasted"])
        self.assertEqual(res1["log"], res2["log"])
        self.assertEqual(res1["mvp"], res2["mvp"])

        mc1 = run_monte_carlo(DEFAULT_SIDE1, DEFAULT_SIDE2, terrain="open_field", runs=20, seed=123)
        mc2 = run_monte_carlo(DEFAULT_SIDE1, DEFAULT_SIDE2, terrain="open_field", runs=20, seed=123)
        self.assertEqual(mc1["side1_win_rate"], mc2["side1_win_rate"])
        self.assertEqual(mc1["side2_win_rate"], mc2["side2_win_rate"])

    def test_presets_cli_and_simulation(self):
        """Verify that skirmish presets execute successfully and produce combat results."""
        from lib.tactical_sim import SKIRMISH_PRESETS

        for preset_name, p_data in SKIRMISH_PRESETS.items():
            self.assertIn("side1", p_data)
            self.assertIn("side2", p_data)
            self.assertIn("terrain", p_data)
            battle = simulate_single_battle(p_data["side1"], p_data["side2"], terrain=p_data["terrain"], seed=10)
            self.assertIn(battle["winner"], (0, 1, 2))

            # CLI with preset
            with patch.object(sys, "argv", ["tactical_sim.py", "sim", "--preset", preset_name, "--json"]):
                with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                    main()
                    data = json.loads(mock_stdout.getvalue())
                    self.assertIn("winner_name", data)

    def test_html_report_generation(self):
        """Verify HTML reports for both skirmish battles and warfare scenario planning."""
        from lib.tactical_sim import generate_tactical_sim_html_report

        with tempfile.TemporaryDirectory() as td:
            # 1. Skirmish HTML
            battle = simulate_single_battle(DEFAULT_SIDE1, DEFAULT_SIDE2, terrain="open_field")
            battle_html = Path(td) / "battle.html"
            generate_tactical_sim_html_report(battle, battle_html)
            self.assertTrue(battle_html.is_file())
            b_text = battle_html.read_text(encoding="utf-8")
            self.assertIn("default-src 'none'", b_text)
            self.assertIn("Skirmish Victory", b_text)

            # 2. Monte Carlo HTML
            mc = run_monte_carlo(DEFAULT_SIDE1, DEFAULT_SIDE2, terrain="open_field", runs=10)
            mc_html = Path(td) / "mc.html"
            generate_tactical_sim_html_report(mc, mc_html)
            self.assertTrue(mc_html.is_file())
            mc_text = mc_html.read_text(encoding="utf-8")
            self.assertIn("MONTE CARLO PROBABILITY DISTRIBUTION", mc_text)

            # 3. Plan HTML
            att = {"name": "Legion", "troops": 3000}
            dfn = {"name": "Rebels", "troops": 1000}
            plan = plan_warfare_scenario(att, dfn)
            plan_html = Path(td) / "plan.html"
            generate_tactical_sim_html_report(plan, plan_html)
            self.assertTrue(plan_html.is_file())
            p_text = plan_html.read_text(encoding="utf-8")
            self.assertIn("Warfare Scenario Analysis", p_text)


if __name__ == "__main__":
    unittest.main()


