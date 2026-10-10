#!/usr/bin/env python3
"""
Unit Tests for Ars Arcanum UI Visual Presets & Procedural Sound Engine
(tests/test_ui_theme_engine.py)
======================================================================
Validates:
- 11 Visual Presets & Token Matrix completeness.
- 10 Procedural Acoustic Typewriter Models & Synthesis logic.
- Strict Content Security Policy (default-src 'none') and air-gapped isolation.
- Control Center Modal & Quick Switcher HTML markup.
- Standalone Theme & Sound Studio HTML generation and typing sandbox.
- Studio CLI entrypoint, argument parsing, and output generation.
- Config & Constitution persistence for visual, sound, and CRT preferences.
- Universal CLI routing & alias dispatch.
- Cross-template integration cohesion.
"""

from __future__ import annotations

import io
import os
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.config import (
    get_crt_fx_enabled,
    get_typewriter_sound_preset,
    get_ui_visual_preset,
    main as config_main,
    set_crt_fx_enabled,
    set_typewriter_sound_preset,
    set_ui_visual_preset,
)
from lib.constitution import DEFAULT_AUTHORIAL_POLICY
from lib.ui_theme_engine import (
    SOUND_PRESETS,
    VISUAL_PRESETS,
    get_theme_control_center_html,
    get_theme_engine_css,
    get_theme_engine_js,
)
from lib.ui_theme_studio import main as studio_main, render_theme_studio_html


class TestVisualPresets(unittest.TestCase):
    """Verifies all 11 UI visual presets and their CSS token dictionaries."""

    EXPECTED_PRESETS = {
        "sovereign-dark",
        "classic-light",
        "retro",
        "futuristic",
        "retrofuturistic",
        "fantastical",
        "grim",
        "edgy",
        "cozy",
        "scifi",
        "horror",
    }

    REQUIRED_TOKENS = {
        "--bg",
        "--bg-main",
        "--surface",
        "--surface-hover",
        "--bg-card",
        "--card-bg",
        "--card-border",
        "--border",
        "--text",
        "--text-muted",
        "--accent",
        "--accent-glow",
        "--purple",
        "--green",
        "--amber",
        "--rose",
        "--shadow",
    }

    def test_all_11_visual_presets_defined(self) -> None:
        self.assertEqual(
            set(VISUAL_PRESETS.keys()),
            self.EXPECTED_PRESETS,
            f"Missing or extra presets: {set(VISUAL_PRESETS.keys()) ^ self.EXPECTED_PRESETS}",
        )
        self.assertEqual(len(VISUAL_PRESETS), 11)

    def test_visual_preset_structure_and_tokens(self) -> None:
        for pid, pdata in VISUAL_PRESETS.items():
            self.assertEqual(pdata.get("id"), pid)
            self.assertTrue(pdata.get("name"), f"Preset {pid} missing name")
            self.assertTrue(pdata.get("category"), f"Preset {pid} missing category")
            self.assertTrue(pdata.get("description"), f"Preset {pid} missing description")
            self.assertTrue(pdata.get("icon"), f"Preset {pid} missing icon")

            tokens = pdata.get("tokens", {})
            self.assertIsInstance(tokens, dict, f"Preset {pid} tokens not a dict")
            for req_token in self.REQUIRED_TOKENS:
                self.assertIn(
                    req_token,
                    tokens,
                    f"Preset '{pid}' missing required CSS token '{req_token}'",
                )

            swatches = pdata.get("swatches", [])
            self.assertIsInstance(swatches, list)
            self.assertGreaterEqual(len(swatches), 3, f"Preset '{pid}' must have at least 3 swatches")
            for swatch in swatches:
                self.assertTrue(
                    swatch.startswith(("#", "rgb")),
                    f"Preset '{pid}' invalid swatch color: {swatch}",
                )


class TestSoundPresets(unittest.TestCase):
    """Verifies all 10 procedural typewriter acoustic models and metadata."""

    EXPECTED_SOUND_MODELS = {
        "remington_1890",
        "royal_1930",
        "selectric_1960",
        "smith_corona_1980",
        "cherry_blue",
        "thock",
        "cyber_terminal",
        "steampunk",
        "scribe_quill",
        "gothic_relic",
    }

    def test_all_10_sound_presets_defined(self) -> None:
        self.assertEqual(
            set(SOUND_PRESETS.keys()),
            self.EXPECTED_SOUND_MODELS,
            f"Missing or extra sound presets: {set(SOUND_PRESETS.keys()) ^ self.EXPECTED_SOUND_MODELS}",
        )
        self.assertEqual(len(SOUND_PRESETS), 10)

    def test_sound_preset_structure(self) -> None:
        for sid, sdata in SOUND_PRESETS.items():
            self.assertEqual(sdata.get("id"), sid)
            self.assertTrue(sdata.get("name"), f"Sound preset {sid} missing name")
            self.assertTrue(sdata.get("era"), f"Sound preset {sid} missing era")
            self.assertTrue(sdata.get("description"), f"Sound preset {sid} missing description")
            self.assertTrue(sdata.get("icon"), f"Sound preset {sid} missing icon")


class TestThemeEngineCss(unittest.TestCase):
    """Verifies CSS generator generates complete CSS variables, CRT effects, and modal styles."""

    def setUp(self) -> None:
        self.css = get_theme_engine_css()

    def test_css_is_valid_non_empty_string(self) -> None:
        self.assertIsInstance(self.css, str)
        self.assertGreater(len(self.css), 1000)

    def test_css_contains_all_11_preset_selectors(self) -> None:
        for pid in TestVisualPresets.EXPECTED_PRESETS:
            selector = f'[data-theme="{pid}"]'
            self.assertIn(
                selector,
                self.css,
                f"CSS output missing theme selector for '{pid}'",
            )

    def test_css_contains_crt_scanlines_overlay(self) -> None:
        self.assertIn(".crt-effect", self.css)
        self.assertIn(".crt-effect::before", self.css)
        self.assertIn(".crt-effect::after", self.css)
        self.assertIn("pointer-events: none;", self.css)

    def test_css_contains_modal_dialog_styles(self) -> None:
        self.assertIn(".arcanum-modal-overlay", self.css)
        self.assertIn(".arcanum-modal-dialog", self.css)
        self.assertIn(".arcanum-preset-grid", self.css)
        self.assertIn(".arcanum-sound-grid", self.css)
        self.assertIn(".arcanum-theme-launcher-btn", self.css)


class TestThemeEngineJs(unittest.TestCase):
    """Verifies client-side Web Audio API synthesis engine and modal controller."""

    def setUp(self) -> None:
        self.js = get_theme_engine_js()

    def test_js_is_valid_non_empty_string(self) -> None:
        self.assertIsInstance(self.js, str)
        self.assertGreater(len(self.js), 5000)

    def test_js_contains_typewriter_audio_engine(self) -> None:
        self.assertIn("class TypewriterAudioEngine", self.js)
        self.assertIn("window.ArcanumAudio", self.js)
        self.assertIn("window.ArcanumThemeEngine", self.js)

    def test_js_contains_all_10_sound_model_synthesis_cases(self) -> None:
        models = [
            "remington_1890",
            "royal_1930",
            "selectric_1960",
            "smith_corona_1980",
            "cherry_blue",
            "thock",
            "cyber_terminal",
            "steampunk",
            "scribe_quill",
            "gothic_relic",
        ]
        for m in models:
            self.assertIn(f"case '{m}':", self.js, f"JS engine missing synthesis case for: {m}")

    def test_js_contains_acoustic_nuances_and_special_keys(self) -> None:
        # Spacebar, Enter bell, Backspace ratchet methods
        self.assertIn("_playSpace", self.js)
        self.assertIn("_playEnter", self.js)
        self.assertIn("_playBackspace", self.js)
        # Pitch and gain variation
        self.assertIn("pitchVar", self.js)
        self.assertIn("gainVar", self.js)

    def test_js_contains_modifier_and_navigation_key_filtering(self) -> None:
        # Verifies non-character modifier/navigation keys (Shift, Control, Alt, Arrows) are filtered
        self.assertIn("ignoredKeys", self.js)
        self.assertIn("shift", self.js)
        self.assertIn("control", self.js)
        self.assertIn("arrowleft", self.js)
        self.assertIn("ignoredKeys.has(key)", self.js)

    def test_js_contains_local_storage_persistence(self) -> None:
        keys = [
            "arcanum_theme_preset",
            "arcanum_sound_preset",
            "arcanum_sound_volume",
            "arcanum_sound_muted",
            "arcanum_crt_fx",
        ]
        for k in keys:
            self.assertIn(k, self.js, f"JS engine missing localStorage key: {k}")

    def test_js_has_zero_remote_urls_or_network_dependencies(self) -> None:
        """Enforces 100% offline air-gapped guarantee: zero http:// or https://."""
        http_matches = re.findall(r"https?://[^\s\"']+", self.js)
        self.assertEqual(
            http_matches,
            [],
            f"JS contains remote network URLs: {http_matches}",
        )


class TestThemeControlCenterHtml(unittest.TestCase):
    """Verifies the Theme & Sound Control Center Modal markup."""

    def setUp(self) -> None:
        self.html = get_theme_control_center_html()

    def test_markup_contains_launcher_button_and_modal(self) -> None:
        self.assertIn('id="arcanumThemeLauncher"', self.html)
        self.assertIn('id="arcanumThemeModal"', self.html)
        self.assertIn('id="tab-visuals"', self.html)
        self.assertIn('id="tab-audio"', self.html)

    def test_markup_contains_all_11_preset_cards(self) -> None:
        for pid in TestVisualPresets.EXPECTED_PRESETS:
            self.assertIn(f'data-preset-id="{pid}"', self.html)

    def test_markup_contains_all_10_sound_cards(self) -> None:
        for sid in TestSoundPresets.EXPECTED_SOUND_MODELS:
            self.assertIn(f'data-sound-id="{sid}"', self.html)

    def test_markup_contains_controls_and_test_pads(self) -> None:
        self.assertIn('id="arcanumVolSlider"', self.html)
        self.assertIn('id="arcanumMuteBtn"', self.html)
        self.assertIn('id="arcanumCrtToggle"', self.html)
        self.assertIn("Acoustic Test Pads:", self.html)


class TestThemeStudio(unittest.TestCase):
    """Verifies standalone Theme & Typewriter Sound Studio HTML generation."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.work_dir = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_render_theme_studio_html_content_and_csp(self) -> None:
        html = render_theme_studio_html()
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("Ars Arcanum — Theme &amp; Typewriter Sound Studio", html)
        self.assertIn(
            "default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;",
            html,
        )
        self.assertIn('id="typingSandbox"', html)
        self.assertIn('id="statWpm"', html)
        self.assertIn('id="statKeys"', html)
        self.assertIn('id="statWords"', html)
        self.assertIn('id="presetGallery"', html)
        self.assertIn('id="soundGallery"', html)

        # Zero remote URLs
        http_matches = re.findall(r"https?://[^\s\"'<>]+", html)
        self.assertEqual(http_matches, [], f"Studio HTML contains remote URLs: {http_matches}")

    def test_render_theme_studio_html_to_file(self) -> None:
        out_file = self.work_dir / "custom_studio.html"
        res_path = render_theme_studio_html(output_path=out_file)
        self.assertTrue(out_file.exists())
        self.assertEqual(Path(res_path).resolve(), out_file.resolve())
        content = out_file.read_text(encoding="utf-8")
        self.assertIn("<!DOCTYPE html>", content)
        self.assertIn("default-src 'none'", content)


class TestThemeStudioCli(unittest.TestCase):
    """Verifies CLI entrypoint for ui_theme_studio.py."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.work_dir = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_cli_help(self) -> None:
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            with self.assertRaises(SystemExit) as cm:
                studio_main(["--help"])
            self.assertEqual(cm.exception.code, 0)
            self.assertIn("arcanum theme-studio", mock_out.getvalue())

    def test_cli_export_html_custom_path(self) -> None:
        out_target = str(self.work_dir / "my_theme_studio.html")
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            rc = studio_main(["--html", out_target])
            self.assertEqual(rc, 0)
            self.assertIn("Ars Arcanum Theme & Sound Studio generated", mock_out.getvalue())
            self.assertTrue(Path(out_target).exists())

    def test_cli_with_preset_and_sound_flags(self) -> None:
        out_target = str(self.work_dir / "preset_studio.html")
        with patch("sys.stdout", new_callable=io.StringIO):
            rc = studio_main(["-p", "retrofuturistic", "-s", "steampunk", "-o", out_target])
            self.assertEqual(rc, 0)
            self.assertTrue(Path(out_target).exists())

    def test_cli_open_flag(self) -> None:
        with patch("webbrowser.open") as mock_open:
            with patch("sys.stdout", new_callable=io.StringIO):
                rc = studio_main(["--open"])
                self.assertEqual(rc, 0)
                mock_open.assert_called_once()

    def test_cli_rejects_invalid_preset(self) -> None:
        with patch("sys.stderr", new_callable=io.StringIO):
            with self.assertRaises(SystemExit) as cm:
                studio_main(["-p", "non_existent_preset_xyz"])
            self.assertNotEqual(cm.exception.code, 0)

    def test_cli_default_invocation(self) -> None:
        cwd_target = Path("theme_studio.html")
        try:
            with patch("sys.stdout", new_callable=io.StringIO):
                rc = studio_main([])
                self.assertEqual(rc, 0)
                self.assertTrue(cwd_target.exists())
        finally:
            if cwd_target.exists():
                cwd_target.unlink()


class TestThemeConfigAndGovernance(unittest.TestCase):
    """Verifies configuration persistence and Authorial Constitution defaults."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.work_dir = Path(self.temp_dir.name)
        self.env_patch = patch.dict(os.environ, {"XDG_CONFIG_HOME": str(self.work_dir)})
        self.env_patch.start()

    def tearDown(self) -> None:
        self.env_patch.stop()
        self.temp_dir.cleanup()

    def test_constitution_defaults_contain_theme_and_sound_keys(self) -> None:
        self.assertEqual(DEFAULT_AUTHORIAL_POLICY.get("ui_visual_preset"), "sovereign-dark")
        self.assertEqual(DEFAULT_AUTHORIAL_POLICY.get("typewriter_sound_preset"), "remington_1890")
        self.assertEqual(DEFAULT_AUTHORIAL_POLICY.get("crt_fx_enabled"), False)

    def test_get_set_ui_visual_preset(self) -> None:
        self.assertEqual(get_ui_visual_preset(), "sovereign-dark")
        success = set_ui_visual_preset("fantastical")
        self.assertTrue(success)
        self.assertEqual(get_ui_visual_preset(), "fantastical")

    def test_get_set_typewriter_sound_preset(self) -> None:
        self.assertEqual(get_typewriter_sound_preset(), "remington_1890")
        success = set_typewriter_sound_preset("cherry_blue")
        self.assertTrue(success)
        self.assertEqual(get_typewriter_sound_preset(), "cherry_blue")

    def test_get_set_crt_fx_enabled(self) -> None:
        self.assertFalse(get_crt_fx_enabled())
        success = set_crt_fx_enabled(True)
        self.assertTrue(success)
        self.assertTrue(get_crt_fx_enabled())
        set_crt_fx_enabled(False)
        self.assertFalse(get_crt_fx_enabled())

    def test_config_cli_theme_subcommands(self) -> None:
        # Get default theme
        with patch.object(sys, "argv", ["config.py", "theme"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
                rc = config_main()
                self.assertEqual(rc, 0)
                self.assertIn("sovereign-dark", mock_out.getvalue())

        # Set theme
        with patch.object(sys, "argv", ["config.py", "theme", "scifi"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
                rc = config_main()
                self.assertEqual(rc, 0)
                self.assertIn("Active UI visual preset set to: scifi", mock_out.getvalue())
                self.assertEqual(get_ui_visual_preset(), "scifi")

        # Set sound preset
        with patch.object(sys, "argv", ["config.py", "sound-preset", "royal_1930"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
                rc = config_main()
                self.assertEqual(rc, 0)
                self.assertIn("Active typewriter sound preset set to: royal_1930", mock_out.getvalue())
                self.assertEqual(get_typewriter_sound_preset(), "royal_1930")

        # Set CRT fx
        with patch.object(sys, "argv", ["config.py", "crt-fx", "enable"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
                rc = config_main()
                self.assertEqual(rc, 0)
                self.assertIn("CRT scanline effect enabled", mock_out.getvalue())
                self.assertTrue(get_crt_fx_enabled())


class TestCliDispatcherRouting(unittest.TestCase):
    """Verifies that unified CLI routes theme and typewriter subcommands to ui_theme_studio."""

    def test_cli_aliases_route_to_theme_studio(self) -> None:
        from lib.cli import main as cli_main

        aliases = [
            "theme-studio",
            "theme",
            "themes",
            "visuals",
            "presets",
            "sound",
            "typewriter",
            "sound-studio",
            "audio-studio",
        ]

        for alias in aliases:
            with patch("lib.cli.dispatch_subcommand", return_value=0) as mock_dispatch:
                rc = cli_main([alias, "--help"])
                self.assertEqual(rc, 0, f"Alias '{alias}' failed CLI dispatch")
                mock_dispatch.assert_called_once_with("lib.ui_theme_studio", ["--help"])

    def test_cli_doc_theme_studio(self) -> None:
        from lib.cli import handle_doc_command
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            rc = handle_doc_command(["theme-studio"])
            self.assertEqual(rc, 0)
            self.assertIn("UI Visual Presets & Procedural Typewriter Sound Studio", mock_out.getvalue())
            self.assertIn("arcanum theme-studio", mock_out.getvalue())


class TestTemplateIntegrationCohesion(unittest.TestCase):
    """Verifies that all interactive HTML visualizers integrate the Theme & Sound Engine."""

    TEMPLATES_TO_CHECK = [
        "velocity_template.py",
        "portfolio_template.py",
        "docx_sync_template.py",
        "manuscript_diff_template.py",
        "draft_manager_template.py",
        "revision_heatmap_template.py",
        "codex_export_template.py",
    ]

    def test_all_templates_reference_theme_engine(self) -> None:
        lib_dir = REPO_ROOT / "scripts" / "lib"
        for tname in self.TEMPLATES_TO_CHECK:
            tfile = lib_dir / tname
            self.assertTrue(tfile.exists(), f"Template file {tname} does not exist")
            content = tfile.read_text(encoding="utf-8")
            self.assertIn(
                "ui_theme_engine",
                content,
                f"Template '{tname}' does not import or reference ui_theme_engine",
            )
            has_controls = (
                "control_center_html" in content
                or "get_theme_control_center_html" in content
                or "ArcanumThemeEngine" in content
                or "arcanumThemeLauncher" in content
            )
            self.assertTrue(
                has_controls,
                f"Template '{tname}' does not render theme control center HTML or invoke ArcanumThemeEngine",
            )


if __name__ == "__main__":
    unittest.main()
