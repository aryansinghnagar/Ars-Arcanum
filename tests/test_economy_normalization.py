#!/usr/bin/env python3
"""
Unit tests for Economy Currency Denominations & PPP Normalization (CRAFT-02)
(scripts/lib/economy.py)
"""

import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.economy import (
    extract_economy_profiles,
    audit_manuscript_prices,
)


class TestEconomyNormalization(unittest.TestCase):

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

    def test_multi_currency_denomination_normalization(self):
        # Economy 1: Solar Crown is base. 1 Copper Bit = 0.01 Solar Crown. Bread is 2 Solar Crowns (= 200 Copper Bits).
        (self.world_dir / "Economies" / "Solar.md").write_text("""---
name: "Solar Standard Economy"
base_currency: "Solar Crown"
currencies:
  - "Solar Crown: 1.0"
  - "Silver Sovereign: 0.1"
  - "Copper Bit: 0.01"
commodity_basket:
  - "loaf_of_bread: 2.0"
---
""", encoding="utf-8")

        # Economy 2: Lunar Dinar is base. Bread is 4 Lunar Dinars.
        (self.world_dir / "Economies" / "Lunar.md").write_text("""---
name: "Lunar Economy"
base_currency: "Lunar Dinar"
currencies:
  - "Lunar Dinar: 1.0"
  - "Silver Dirham: 0.2"
commodity_basket:
  - "loaf_of_bread: 4.0"
---
""", encoding="utf-8")

        # Scene with fair price in Copper Bits: 200 Copper Bits for loaf_of_bread (= 2 Solar Crowns, ratio 1.0x -> Fair, no anomaly)
        # Scene with anomalous price: 10000 Copper Bits for loaf_of_bread (= 100 Solar Crowns, ratio 50x -> Inflation anomaly!)
        (self.ms_dir / "Book-01" / "01_Act_I" / "scene.md").write_text("""# Scene 1
@price: 200 Copper Bit for loaf_of_bread
@price: 10000 Copper Bit for loaf_of_bread
""", encoding="utf-8")

        econs = extract_economy_profiles(self.world_dir)
        findings = audit_manuscript_prices(self.ms_dir, econs)

        # There should be exactly 1 finding for the 10000 Copper Bit price, NOT for the fair 200 Copper Bit price
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["id"], "ECO-101")
        self.assertIn("Severe Price Inflation Anomaly", findings[0]["message"])
        self.assertIn("10000.0 Copper Bit", findings[0]["message"])

    def test_ppp_cross_rate_basket_resolution(self):
        # Economy A defines wheat and bread
        (self.world_dir / "Economies" / "KingdomA.md").write_text("""---
name: "Kingdom A"
base_currency: "Crown"
currencies:
  - "Crown: 1.0"
commodity_basket:
  - "wheat: 10.0"
  - "bread: 2.0"
---
""", encoding="utf-8")

        # Economy B only defines bread (ratio 4.0 Dinar vs 2.0 Crown -> 1 Dinar = 0.5 Crown) and uses Dinar
        (self.world_dir / "Economies" / "KingdomB.md").write_text("""---
name: "Kingdom B"
base_currency: "Dinar"
currencies:
  - "Dinar: 1.0"
commodity_basket:
  - "bread: 4.0"
---
""", encoding="utf-8")

        # In Kingdom B, wheat is priced at 20 Dinar (= 10 Crowns via PPP 0.5x -> Fair, ratio 1.0x)
        # In Kingdom B, wheat priced at 1000 Dinar (= 500 Crowns -> Inflation anomaly)
        (self.ms_dir / "Book-01" / "01_Act_I" / "market.md").write_text("""# Market
@price: 20 Dinar for wheat
@price: 1000 Dinar for wheat
""", encoding="utf-8")

        econs = extract_economy_profiles(self.world_dir)
        findings = audit_manuscript_prices(self.ms_dir, econs)

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["id"], "ECO-101")
        self.assertIn("1000.0 Dinar", findings[0]["message"])


if __name__ == "__main__":
    unittest.main()
