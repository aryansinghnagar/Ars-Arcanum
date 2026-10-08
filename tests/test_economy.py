#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Economy, Commodity PPP & Anachronism Matrix (scripts/lib/economy.py).
"""

import io
import tempfile
import unittest
from pathlib import Path
import sys
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.economy import (
    extract_economy_profiles,
    calculate_ppp_rates,
    audit_manuscript_prices,
    audit_technological_anachronisms,
    calc_trade_margin,
    generate_economy_html_report,
    resolve_world_dir,
    resolve_manuscript_dir,
    main,
)


class TestEconomyEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.world_dir = Path(self.temp_dir.name) / "World"
        self.ms_dir = Path(self.temp_dir.name) / "Manuscript"
        self.world_dir.mkdir(parents=True)
        self.ms_dir.mkdir(parents=True)
        (self.world_dir / "Economies").mkdir(parents=True)
        (self.ms_dir / "Book-01" / "01_Act_I").mkdir(parents=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_extract_economy_profiles_and_ppp(self):
        (self.world_dir / "Economies" / "Solar_Standard.md").write_text("""---
name: "Solar Standard Economy"
base_currency: "Solar Crown"
tech_era: "medieval"
currencies:
  - "Solar Crown: 1.0"
  - "Silver Sovereign: 0.1"
  - "Copper Bit: 0.01"
commodity_basket:
  - "loaf_of_bread: 2"
  - "pint_of_ale: 1"
  - "riding_horse: 500"
---
# Solar Standard Economy
""", encoding="utf-8")

        (self.world_dir / "Economies" / "Lunar_Dinar.md").write_text("""---
name: "Lunar Economy"
base_currency: "Lunar Dinar"
tech_era: "medieval"
currencies:
  - "Lunar Dinar: 1.0"
  - "Silver Dirham: 0.2"
commodity_basket:
  - "loaf_of_bread: 4"
  - "pint_of_ale: 2"
  - "riding_horse: 1000"
---
# Lunar Economy
""", encoding="utf-8")

        econs = extract_economy_profiles(self.world_dir)
        self.assertIn("Solar Standard Economy", econs)
        self.assertIn("Lunar Economy", econs)

        ppp = calculate_ppp_rates(econs)
        self.assertAlmostEqual(ppp["Solar Standard Economy"]["Lunar Economy"], 0.5, places=2)
        self.assertAlmostEqual(ppp["Lunar Economy"]["Solar Standard Economy"], 2.0, places=2)

    def test_extract_currency_denominations(self):
        (self.world_dir / "Economies" / "Merchant_Guild.md").write_text("""---
name: "Merchant Guild Economy"
base_currency: "Gold Ducat"
currencies:
  - "Gold Ducat: 1.0"
  - "Silver Florin: 0.1"
  - "Copper Groat: 0.01"
---
""", encoding="utf-8")
        econs = extract_economy_profiles(self.world_dir)
        self.assertIn("Merchant Guild Economy", econs)
        mg = econs["Merchant Guild Economy"]
        self.assertEqual(mg["currencies"]["Gold Ducat"], 1.0)
        self.assertEqual(mg["currencies"]["Silver Florin"], 0.1)
        self.assertEqual(mg["currencies"]["Copper Groat"], 0.01)

    def test_calculate_ppp_disjoint_baskets(self):
        (self.world_dir / "Economies" / "Econ_A.md").write_text("""---
name: "Economy A"
commodity_basket:
  - "silk: 50"
---
""", encoding="utf-8")
        (self.world_dir / "Economies" / "Econ_B.md").write_text("""---
name: "Economy B"
commodity_basket:
  - "ore: 100"
---
""", encoding="utf-8")
        econs = extract_economy_profiles(self.world_dir)
        ppp = calculate_ppp_rates(econs)
        self.assertIsNone(ppp["Economy A"]["Economy B"])

    def test_audit_manuscript_prices_anomalies_and_deflation(self):
        (self.world_dir / "Economies" / "Imperial.md").write_text("""---
name: "Imperial Economy"
base_currency: "Gold Crown"
currencies:
  - "Gold Crown: 1.0"
commodity_basket:
  - "loaf_of_bread: 100"
---
""", encoding="utf-8")

        (self.ms_dir / "Book-01" / "01_Act_I" / "01_Chapter.md").write_text("""# Chapter 1
@price: 5000 Gold Crown for loaf_of_bread
@price: 1 Gold Crown for loaf_of_bread
""", encoding="utf-8")

        econs = extract_economy_profiles(self.world_dir)
        findings = audit_manuscript_prices(self.ms_dir, econs)

        ids = [f["id"] for f in findings]
        self.assertIn("ECO-101", ids)
        self.assertEqual(len(findings), 2)

    def test_audit_unregistered_currency_eco102(self):
        (self.world_dir / "Economies" / "Imperial.md").write_text("""---
name: "Imperial Economy"
base_currency: "Gold Crown"
currencies:
  - "Gold Crown: 1.0"
---
""", encoding="utf-8")

        (self.ms_dir / "Book-01" / "01_Act_I" / "01_Chapter.md").write_text("""# Chapter 1
He also paid with 50 Galactico credits for wine.
""", encoding="utf-8")

        econs = extract_economy_profiles(self.world_dir)
        findings = audit_manuscript_prices(self.ms_dir, econs)

        ids = [f["id"] for f in findings]
        self.assertIn("ECO-102", ids)

    def test_audit_temporal_preposition_exclusion(self):
        """Verify temporal prepositional idioms like 'coins for a moment' do not trigger false anomalies."""
        (self.world_dir / "Economies" / "Imperial.md").write_text("""---
name: "Imperial Economy"
base_currency: "Gold Crown"
currencies:
  - "Gold Crown: 1.0"
---
""", encoding="utf-8")

        (self.ms_dir / "Book-01" / "01_Act_I" / "01_Chapter.md").write_text("""# Chapter 1
He stared at the 5 gold coins for a moment before turning away.
She counted 10 silver coins for an hour in the quiet tower.
""", encoding="utf-8")

        econs = extract_economy_profiles(self.world_dir)
        findings = audit_manuscript_prices(self.ms_dir, econs)
        self.assertEqual(len(findings), 0)

    def test_audit_technological_anachronisms(self):
        (self.ms_dir / "Book-01" / "01_Act_I" / "01_Scene.md").write_text("""# Scene
The knight polished his plate armor and checked the radar screen before wrapping his food in plastic.
""", encoding="utf-8")

        findings = audit_technological_anachronisms(self.ms_dir, baseline_era="medieval")
        terms = [f["term"] for f in findings]
        self.assertIn("radar", terms)
        self.assertIn("plastic", terms)
        self.assertNotIn("plate armor", terms)

        # Custom whitelist
        findings_wl = audit_technological_anachronisms(self.ms_dir, baseline_era="medieval", custom_whitelist=["radar", "plastic"])
        self.assertEqual(len(findings_wl), 0)

    def test_calc_trade_margin(self):
        res = calc_trade_margin(
            buy_price_per_ton=100.0,
            sell_price_per_ton=300.0,
            cargo_tons=50.0,
            distance_km_or_ly=100.0,
            transit_cost_per_ton_unit=0.5,
            tariff_pct=0.05
        )
        self.assertTrue(res["is_profitable"])
        self.assertGreater(res["net_profit"], 0)

    def test_generate_economy_html_report(self):
        (self.world_dir / "Economies" / "Econ.md").write_text("""---
name: "Barter Economy"
---
""", encoding="utf-8")
        econs = extract_economy_profiles(self.world_dir)
        html_out = Path(self.temp_dir.name) / "economy.html"
        findings = [{"severity": "WARNING", "id": "ECO-101", "message": "Test Finding", "file": "ch1.md", "line": 5}]
        generate_economy_html_report({"world": "TestWorld", "economies": econs, "findings": findings}, html_out)
        self.assertTrue(html_out.is_file())
        content = html_out.read_text(encoding="utf-8")
        self.assertIn("Content-Security-Policy", content)
        self.assertIn("Test Finding", content)

    def test_resolve_world_and_manuscript_dir(self):
        self.assertEqual(resolve_world_dir(str(self.world_dir)), str(self.world_dir.resolve()))
        self.assertEqual(resolve_manuscript_dir(str(self.ms_dir)), str(self.ms_dir.resolve()))

    def test_extract_economy_with_world_yaml_and_dict_basket(self):
        (self.world_dir / "world.yaml").write_text("dummy", encoding="utf-8")
        with patch("lib.economy.parse_yaml_frontmatter", return_value={"economy": {"base_currency": "Imperial Credit", "currencies": {"Imperial Credit": 1.0}}}):
            econs = extract_economy_profiles(self.world_dir)
            self.assertIn("Global", econs)
            self.assertEqual(econs["Global"]["base_currency"], "Imperial Credit")

    def test_prose_price_discrepancy(self):
        (self.world_dir / "Economies" / "Standard.md").write_text("""---
name: "Standard"
base_currency: "Gold Coins"
currencies:
  - "Gold Coins: 1.0"
commodity_basket:
  - "apple: 1"
---
""", encoding="utf-8")
        (self.ms_dir / "Book-01" / "01_Act_I" / "02_Prose.md").write_text("""# Scene
He paid 100 gold coins for the apple.
""", encoding="utf-8")
        econs = extract_economy_profiles(self.world_dir)
        findings = audit_manuscript_prices(self.ms_dir, econs)
        ids = [f["id"] for f in findings]
        self.assertIn("ECO-101", ids)

    def test_calc_trade_margin_unprofitable(self):
        res = calc_trade_margin(
            buy_price_per_ton=500.0,
            sell_price_per_ton=400.0,
            cargo_tons=10.0,
            distance_km_or_ly=1000.0,
            transit_cost_per_ton_unit=2.0,
            tariff_pct=0.1
        )
        self.assertFalse(res["is_profitable"])
        self.assertLess(res["net_profit"], 0)

    def test_cli_human_readable_check_report_tech_trade(self):
        # 1. check with findings & human readable
        (self.world_dir / "Economies" / "Standard.md").write_text("""---
name: "Standard"
base_currency: "Gold Coin"
currencies:
  - "Gold Coin: 1.0"
commodity_basket:
  - "apple: 1"
---
""", encoding="utf-8")
        (self.ms_dir / "Book-01" / "01_Act_I" / "01_Test.md").write_text("@price: 5000 Gold Coin for apple\n", encoding="utf-8")

        html_target = Path(self.temp_dir.name) / "out.html"
        with patch.object(sys, "argv", ["economy.py", "check", str(self.world_dir), str(self.ms_dir), "--html", str(html_target)]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 0)
                self.assertIn("Price Inflation", mock_stdout.getvalue())
                self.assertTrue(html_target.exists())

        # Test --strict mode exits with code 1 when findings exist
        with patch.object(sys, "argv", ["economy.py", "check", str(self.world_dir), str(self.ms_dir), "--strict"]):
            with patch("sys.stdout", new_callable=io.StringIO):
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 1)

        # 2. tech mode human readable with findings
        with patch.object(sys, "argv", ["economy.py", "tech", str(self.ms_dir), "-w", str(self.world_dir), "--era", "medieval"]):
            with patch("sys.stdout", new_callable=io.StringIO):
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 0)

        # 3. trade mode human readable
        with patch.object(sys, "argv", ["economy.py", "trade", "--buy", "100", "--sell", "200", "--distance", "50"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 0)
                self.assertIn("Trade Route Profitability Analysis", mock_stdout.getvalue())

    def test_cli_json_modes(self):
        (self.world_dir / "Economies" / "Standard.md").write_text("""---
name: "Standard"
base_currency: "Gold Coin"
tech_era: "industrial"
currencies:
  - "Gold Coin: 1.0"
commodity_basket:
  - "apple: 1"
---
""", encoding="utf-8")
        (self.ms_dir / "Book-01" / "01_Act_I" / "01_Test.md").write_text("@price: 5000 Gold Coin for apple\nHe checked the smartphone in his pocket.\n", encoding="utf-8")

        # 1. report --json
        with patch.object(sys, "argv", ["economy.py", "report", str(self.world_dir), str(self.ms_dir), "--json"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 0)
                import json
                res = json.loads(mock_stdout.getvalue())
                self.assertEqual(res["world"], self.world_dir.name)
                self.assertGreater(len(res["findings"]), 0)

        # 2. tech --json
        with patch.object(sys, "argv", ["economy.py", "tech", str(self.ms_dir), "-w", str(self.world_dir), "--json"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 0)
                res = json.loads(mock_stdout.getvalue())
                self.assertIn("findings", res)

        # 3. trade --json
        with patch.object(sys, "argv", ["economy.py", "trade", "--buy", "100", "--sell", "200", "--distance", "50", "--json"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 0)
                res = json.loads(mock_stdout.getvalue())
                self.assertTrue(res["is_profitable"])

    def test_cli_default_command_and_discovery(self):
        (self.world_dir / "Economies" / "Standard.md").write_text("""---
name: "Standard"
base_currency: "Gold Coin"
---
""", encoding="utf-8")
        temp_home = Path(self.temp_dir.name) / "home"
        (temp_home / "Universes" / "Cosmos" / "Aethelgard").mkdir(parents=True)
        (temp_home / "Manuscripts" / "Novel").mkdir(parents=True)

        with patch("pathlib.Path.home", return_value=temp_home):
            # Resolve universe
            res_w = resolve_world_dir("Aethelgard")
            self.assertTrue(res_w.endswith("Aethelgard"))
            # Resolve manuscript
            res_m = resolve_manuscript_dir("Novel")
            self.assertTrue(res_m.endswith("Novel"))
            # Auto fallback world
            res_single = resolve_world_dir(None)
            self.assertTrue(res_single.endswith("Aethelgard"))

            # Multiple worlds error in resolve_world_dir
            (temp_home / "Universes" / "Cosmos" / "Valendor").mkdir(parents=True)
            with patch("sys.stderr", new_callable=io.StringIO):
                with self.assertRaises(SystemExit) as cm:
                    resolve_world_dir(None)
                self.assertEqual(cm.exception.code, 2)

    def test_edge_cases_in_parsing(self):
        # Malformed list currencies & string commodity baskets
        (self.world_dir / "Economies" / "Weird.md").write_text("""---
name: "Weird Economy"
currencies:
  - "InvalidCurrency"
  - "BadValue: not_a_number"
commodity_basket:
  - "BreadWithoutPrice"
  - "Water: invalid_num"
---
""", encoding="utf-8")
        econs = extract_economy_profiles(self.world_dir)
        self.assertIn("Weird Economy", econs)
        w = econs["Weird Economy"]
        self.assertEqual(w["currencies"]["InvalidCurrency"], 1.0)
        self.assertEqual(w["currencies"]["BadValue"], 1.0)
        self.assertEqual(w["commodity_basket"]["Water"], 1.0)

    def test_clean_tech_and_check_runs(self):
        # Clean tech audit without findings
        (self.ms_dir / "Book-01" / "01_Act_I" / "01_Clean.md").write_text("# Scene 1\nThe knight rode on his horse across the stone bridge.\n", encoding="utf-8")
        with patch.object(sys, "argv", ["economy.py", "tech", str(self.ms_dir), "--era", "medieval"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 0)
                self.assertIn("[OK] No out-of-era technological terms", mock_stdout.getvalue())

        # Clean check audit without findings
        (self.world_dir / "Economies" / "Solar.md").write_text("""---
name: "Solar Standard Economy"
base_currency: "Solar Crown"
tech_era: "medieval"
currencies:
  - "Solar Crown: 1.0"
commodity_basket:
  - "apple: 2"
---
""", encoding="utf-8")
        with patch.object(sys, "argv", ["economy.py", "check", str(self.world_dir), str(self.ms_dir)]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 0)
                self.assertIn("[OK] Economic models and manuscript prices are internally consistent", mock_stdout.getvalue())

    def test_audit_functions_none_or_empty_dirs(self):
        self.assertEqual(audit_manuscript_prices(None, {}), [])
        self.assertEqual(audit_technological_anachronisms(None), [])

    def test_gravity_trade_flow_and_supply_shock(self):
        from lib.economy import (
            extract_settlement_network,
            calculate_gravity_trade_flow,
            simulate_supply_shock,
        )

        settlements = extract_settlement_network(self.world_dir)
        self.assertGreaterEqual(len(settlements), 2)

        flows = calculate_gravity_trade_flow(settlements)
        self.assertIn("routes", flows)
        self.assertGreater(len(flows["routes"]), 0)

        shock = simulate_supply_shock(settlements, "Blockade", "Solaria", "grain", shock_magnitude=0.6)
        self.assertIn("market_impacts", shock)
        self.assertEqual(shock["commodity"], "grain")

        # Test CLI trade-flow and supply-shock modes
        with patch.object(sys, "argv", ["economy.py", "trade-flow", str(self.world_dir)]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 0)
                self.assertIn("Economic Gravity Model", mock_stdout.getvalue())

        with patch.object(sys, "argv", ["economy.py", "supply-shock", str(self.world_dir), "-e", "Blockade", "-s", "Sun Citadel", "-c", "iron", "-m", "0.5"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 0)
                self.assertIn("Supply Shock", mock_stdout.getvalue())


    def test_deliberate_price_and_anachronism_bypass(self):
        """Files or lines tagged with @intent: deliberate or @anachronism: allow are bypassed during economic/tech audits."""
        # 1. Price audit with deliberate markup
        (self.world_dir / "Economies" / "Solar.md").write_text("""---
name: "Solar Standard Economy"
base_currency: "Solar Crown"
commodity_basket:
  - "loaf_of_bread: 2"
---
""", encoding="utf-8")
        econs = extract_economy_profiles(self.world_dir)

        # Deliberate frontmatter
        ch_delib = self.ms_dir / "Book-01" / "01_Act_I" / "delib_price.md"
        ch_delib.write_text("""---
intent: deliberate
---
He bought a rare cursed loaf for 500.0 Solar Crown.
""", encoding="utf-8")

        # Inline deliberate tag
        ch_inline = self.ms_dir / "Book-01" / "01_Act_I" / "inline_price.md"
        ch_inline.write_text("""# Chapter
He paid 999.0 Solar Crown for the forbidden talisman. <!-- @intent: deliberate -->
""", encoding="utf-8")

        findings = audit_manuscript_prices(self.ms_dir, econs)
        self.assertEqual(len(findings), 0, "Deliberate price anomalies should be bypassed")

        # 2. Anachronism audit with deliberate flag
        ch_tech = self.ms_dir / "Book-01" / "01_Act_I" / "tech_anachronism.md"
        ch_tech.write_text("""---
tech_era: "medieval"
intent: deliberate
---
He used an advanced steam engine to power the drawbridge.
""", encoding="utf-8")

        tech_findings = audit_technological_anachronisms(self.ms_dir)
        self.assertEqual(len(tech_findings), 0, "Deliberate tech anachronisms should be bypassed")


if __name__ == "__main__":
    unittest.main()


