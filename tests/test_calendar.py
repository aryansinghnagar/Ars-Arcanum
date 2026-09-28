#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Custom Planetary Calendars & Multi-Moon Phase Engine (scripts/lib/calendar.py).
Covers calendar spec loading, date arithmetic, absolute day conversions, multi-moon synodic phases,
syzygy/conjunction detection, terminal grid rendering, HTML export, and CLI commands.
"""

import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.calendar import (
    absolute_day_to_date,
    date_to_absolute_day,
    detect_celestial_events,
    generate_calendar_html_report,
    get_moon_phase,
    load_calendar_spec,
    render_month_terminal_grid,
    format_date,
    main
)


class TestCalendarEngine(unittest.TestCase):

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.world_dir = Path(self.temp_dir.name) / "World"
        self.cosmology_dir = self.world_dir / "Cosmology"
        self.cosmology_dir.mkdir(parents=True)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_load_calendar_spec(self) -> None:
        """load_calendar_spec parses days, hours, months, weekdays, and moon definitions."""
        (self.cosmology_dir / "Pantheon.md").write_text("""---
name: "Solar Pantheon"
type: cosmology
days_per_year: 400
hours_per_day: 28
months:
  - "Dawn"
  - "Sunhigh"
  - "Dusk"
  - "Nightfall"
weekdays:
  - "Moonday"
  - "Fireday"
  - "Waterday"
  - "Earthday"
  - "Starday"
eras:
  - name: "Age of Sun"
    short: "AS"
    offset: 0
    format: "{weekday}, {day} {month}, Year {year} {era}"
moons:
  - name: "Selene"
    period: 25.0
    offset: 0.0
---
""", encoding="utf-8")

        spec = load_calendar_spec(self.world_dir)
        self.assertEqual(spec["days_per_year"], 400)
        self.assertEqual(spec["hours_per_day"], 28)
        self.assertEqual(len(spec["months"]), 4)
        self.assertEqual(len(spec["weekdays"]), 5)
        self.assertEqual(spec["moons"][0]["name"], "Selene")
        self.assertEqual(len(spec["eras"]), 1)

    def test_load_calendar_spec_fallback_defaults(self) -> None:
        """load_calendar_spec provides defaults when cosmology notes are absent."""
        empty_world = Path(self.temp_dir.name) / "EmptyWorld"
        empty_world.mkdir(parents=True)
        spec = load_calendar_spec(empty_world)
        self.assertEqual(spec["days_per_year"], 365)
        self.assertEqual(spec["hours_per_day"], 24)
        self.assertEqual(len(spec["months"]), 12)
        self.assertEqual(len(spec["weekdays"]), 7)

    def test_format_date_with_and_without_eras(self) -> None:
        cal_spec = {
            "world": "TestWorld",
            "days_per_year": 360,
            "months": [{"name": "Janus", "days": 30}],
            "weekdays": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
            "eras": [
                {"name": "First Era", "short": "1E", "offset": 100, "format": "{weekday}, {day} {month}, Year {year} {era}"},
                {"name": "Mythic Era", "short": "ME", "offset": 0, "format": "{weekday}, {day} {month}, Year {year} {era}"}
            ]
        }
        res_mythic = format_date(50, 0, 15, cal_spec)
        self.assertIn("ME", res_mythic)
        self.assertIn("Janus", res_mythic)

        res_first = format_date(150, 0, 10, cal_spec)
        self.assertIn("1E", res_first)
        self.assertIn("Year 50", res_first)

        # No eras
        cal_no_era = {
            "world": "TestWorld",
            "days_per_year": 360,
            "months": [{"name": "Janus", "days": 30}],
            "weekdays": ["Mon", "Tue"],
            "eras": []
        }
        res_no_era = format_date(5, 0, 1, cal_no_era)
        self.assertIn("Janus", res_no_era)

    def test_date_conversions_roundtrip_day1(self) -> None:
        """Day 1 of Year 1 maps to absolute day 0 and inverts back cleanly."""
        cal_spec = {
            "world": "TestWorld",
            "days_per_year": 360,
            "months": [{"name": f"M{i+1}", "days": 30} for i in range(12)],
            "weekdays": ["D1", "D2", "D3", "D4", "D5", "D6"],
            "moons": [],
        }
        abs1 = date_to_absolute_day(1, 0, 1, cal_spec)
        self.assertEqual(abs1, 0)
        y, m, d, dow = absolute_day_to_date(abs1, cal_spec)
        self.assertEqual((y, m, d, dow), (1, 0, 1, 0))

    def test_date_conversions_roundtrip_multiyear(self) -> None:
        """Multi-year dates convert to continuous absolute day count and round-trip."""
        cal_spec = {
            "world": "TestWorld",
            "days_per_year": 360,
            "months": [{"name": f"M{i+1}", "days": 30} for i in range(12)],
            "weekdays": ["D1", "D2", "D3", "D4", "D5", "D6"],
            "moons": [],
        }
        abs_val = date_to_absolute_day(3, 3, 15, cal_spec)
        self.assertEqual(abs_val, 824)
        y, m, d, dow = absolute_day_to_date(abs_val, cal_spec)
        self.assertEqual((y, m, d), (3, 3, 15))
        self.assertEqual(dow, 824 % 6)

    def test_date_advancing_with_offset(self) -> None:
        """Adding day offsets correctly rolls over months and years."""
        cal_spec = {
            "world": "TestWorld",
            "days_per_year": 360,
            "months": [{"name": "M1", "days": 30}, {"name": "M2", "days": 30}],
            "weekdays": ["D1", "D2", "D3", "D4", "D5"],
            "moons": [],
        }
        abs_day = date_to_absolute_day(1, 0, 1, cal_spec) + 35
        y, m_idx, d, _dow = absolute_day_to_date(abs_day, cal_spec)
        self.assertEqual((y, m_idx, d), (1, 1, 6))

    def test_moon_phases_all_bands(self) -> None:
        moon = {"name": "Lumina", "period": 100.0, "offset": 0.0}
        # cycle_pos mapping:
        # 0.0 -> New Moon
        # 0.10 -> Waxing Crescent
        # 0.25 -> First Quarter
        # 0.35 -> Waxing Gibbous
        # 0.50 -> Full Moon
        # 0.60 -> Waning Gibbous
        # 0.75 -> Third Quarter
        # 0.90 -> Waning Crescent
        self.assertEqual(get_moon_phase(0, moon)["phase_name"], "New Moon")
        self.assertEqual(get_moon_phase(10, moon)["phase_name"], "Waxing Crescent")
        self.assertEqual(get_moon_phase(25, moon)["phase_name"], "First Quarter")
        self.assertEqual(get_moon_phase(35, moon)["phase_name"], "Waxing Gibbous")
        self.assertEqual(get_moon_phase(50, moon)["phase_name"], "Full Moon")
        self.assertEqual(get_moon_phase(60, moon)["phase_name"], "Waning Gibbous")
        self.assertEqual(get_moon_phase(75, moon)["phase_name"], "Third Quarter")
        self.assertEqual(get_moon_phase(90, moon)["phase_name"], "Waning Crescent")

    def test_syzygy_conjunction_detection_grand_and_dark(self) -> None:
        """detect_celestial_events identifies simultaneous Full Moons (Grand Conjunction) and New Moons (Dark Convergence)."""
        moons = [
            {"name": "MoonA", "period": 20.0, "offset": 0.0},
            {"name": "MoonB", "period": 40.0, "offset": 0.0},
        ]
        events10 = detect_celestial_events(10, moons)
        self.assertEqual(len(events10), 0)

        events40 = detect_celestial_events(40, moons)
        self.assertEqual(len(events40), 1)
        self.assertIn("Dark Convergence", events40[0])

        events_full = detect_celestial_events(10, [{"name": "M1", "period": 20.0, "offset": 0.0}, {"name": "M2", "period": 20.0, "offset": 0.0}])
        self.assertEqual(len(events_full), 1)
        self.assertIn("Grand Conjunction", events_full[0])

    def test_render_month_terminal_grid_layout(self) -> None:
        cal_spec = {
            "world": "Eldoria",
            "days_per_year": 365,
            "months": [{"name": "Primis", "days": 30}],
            "weekdays": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            "moons": [{"name": "Lumina", "period": 28.0, "offset": 0.0}],
        }
        grid = render_month_terminal_grid(1, 0, cal_spec)
        self.assertIn("Primis 1", grid)
        self.assertIn("Mon", grid)
        self.assertIn("30", grid)

    def test_html_report_generation_and_csp(self) -> None:
        cal_spec = {
            "world": "Eldoria",
            "days_per_year": 365,
            "hours_per_day": 24,
            "months": [{"name": "Solaris", "days": 30}],
            "weekdays": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            "moons": [{"name": "Lumina", "period": 28.0, "offset": 0.0}],
        }
        out_html = self.world_dir / "calendar.html"
        generate_calendar_html_report(1, 0, cal_spec, out_html)
        self.assertTrue(out_html.is_file())
        content = out_html.read_text(encoding="utf-8")
        self.assertIn("Planetary Calendar", content)
        self.assertIn("Solaris 1", content)
        self.assertIn("Content-Security-Policy", content)
        self.assertIn("default-src 'none'", content)

    def test_cli_commands(self) -> None:
        (self.cosmology_dir / "Cosmo.md").write_text("""---
name: "Aetheria Cosmo"
type: cosmology
days_per_year: 360
hours_per_day: 24
months:
  - "Month1"
  - "Month2"
weekdays:
  - "DayA"
  - "DayB"
moons:
  - name: "Luna"
    period: 30.0
    offset: 0.0
---
""", encoding="utf-8")

        html_out = Path(self.temp_dir.name) / "cal_cli.html"

        # 1. json output
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            with patch("sys.argv", ["calendar.py", str(self.world_dir), "-y", "2", "-m", "1", "-d", "5", "--json"]):
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 0)
                data = json.loads(mock_out.getvalue())
                self.assertEqual(data["year"], 2)
                self.assertEqual(data["day"], 5)

        # 2. terminal output + html
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            with patch("sys.argv", ["calendar.py", "-w", str(self.world_dir), "--advance", "10", "--html", str(html_out)]):
                main()
                self.assertIn("Ars Arcanum Planetary Calendar", mock_out.getvalue())
                self.assertTrue(html_out.is_file())

        # 3. invalid world -> exit 2
        with patch("sys.stderr", new_callable=io.StringIO):
            with patch("sys.argv", ["calendar.py", "-w", str(Path(self.temp_dir.name) / "nonexistent")]):
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
