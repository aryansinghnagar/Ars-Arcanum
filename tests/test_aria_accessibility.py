#!/usr/bin/env python3
"""
Unit test suite for ARIA accessibility and assistive technology compliance
(tests/test_aria_accessibility.py).

Validates that all offline HTML templates and interactive studios provide:
- Semantic ARIA landmarks (role="main", role="banner", role="navigation", role="region", role="contentinfo")
- Tab accessibility (role="tablist", role="tab", role="tabpanel", aria-selected, aria-controls)
- Modal dialog accessibility (role="dialog", aria-modal="true", aria-labelledby / aria-label)
- Screen reader telemetry (aria-live="polite", aria-atomic="true")
- Accessible button and control labels (aria-label)
- Dyslexia-accessible typography configurations
"""

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SCRIPTS_LIB = REPO_ROOT / "scripts" / "lib"


class TestAriaAccessibilityCompliance(unittest.TestCase):
    """Verifies that generated HTML templates include necessary ARIA roles, landmarks, and attributes."""

    def test_zen_studio_aria_accessibility(self):
        zen_path = SCRIPTS_LIB / "zen_studio_template.py"
        self.assertTrue(zen_path.is_file(), f"Zen Studio template missing at {zen_path}")
        content = zen_path.read_text(encoding="utf-8")

        # 1. Semantic Landmarks
        self.assertIn('role="banner"', content, "Zen Studio missing role='banner' landmark")
        self.assertIn('role="main"', content, "Zen Studio missing role='main' landmark")
        self.assertIn('role="region"', content, "Zen Studio missing role='region' landmark")
        self.assertIn('role="contentinfo"', content, "Zen Studio missing role='contentinfo' landmark")

        # 2. Tab Navigation
        self.assertIn('role="tablist"', content, "Zen Studio missing role='tablist'")
        self.assertIn('role="tab"', content, "Zen Studio missing role='tab'")
        self.assertIn('role="tabpanel"', content, "Zen Studio missing role='tabpanel'")
        self.assertIn('aria-selected=', content, "Zen Studio missing aria-selected attribute on tabs")
        self.assertIn('aria-controls=', content, "Zen Studio missing aria-controls attribute on tabs")

        # 3. Live Regions & Feedback
        self.assertIn('aria-live="polite"', content, "Zen Studio missing aria-live='polite' region for dynamic updates")

        # 4. Modals & Dialogs
        self.assertIn('role="dialog"', content, "Zen Studio missing role='dialog' for modal windows")
        self.assertIn('aria-modal="true"', content, "Zen Studio missing aria-modal='true' on dialogs")

        # 5. Accessible Controls & Dyslexia Support
        self.assertIn('aria-label=', content, "Zen Studio missing aria-label attributes for icon buttons")
        self.assertIn('data-font="dyslexic"', content, "Zen Studio missing dyslexia-friendly font option")
        self.assertIn('OpenDyslexic', content, "Zen Studio missing OpenDyslexic font family")

    def test_studio_hub_aria_accessibility(self):
        hub_path = SCRIPTS_LIB / "studio_hub_template.py"
        self.assertTrue(hub_path.is_file(), f"Studio Hub template missing at {hub_path}")
        content = hub_path.read_text(encoding="utf-8")

        # 1. Semantic Navigation & Tabs
        self.assertIn('role="navigation"', content, "Studio Hub missing role='navigation'")
        self.assertIn('role="tablist"', content, "Studio Hub missing role='tablist'")
        self.assertIn('role="tab"', content, "Studio Hub missing role='tab'")
        self.assertIn('role="tabpanel"', content, "Studio Hub missing role='tabpanel'")
        self.assertIn('aria-selected=', content, "Studio Hub missing aria-selected attribute on tabs")

        # 2. Modal Accessibility
        self.assertIn('role="dialog"', content, "Studio Hub missing role='dialog' on execution modal")
        self.assertIn('aria-modal="true"', content, "Studio Hub missing aria-modal='true' on execution modal")

        # 3. Live Console Feedback
        self.assertIn('aria-live="polite"', content, "Studio Hub missing aria-live='polite' for live command execution")

        # 4. Accessible Form Controls
        self.assertIn('aria-label=', content, "Studio Hub missing aria-label on interactive inputs/buttons")

    def test_story_canvas_aria_accessibility(self):
        canvas_path = SCRIPTS_LIB / "story_canvas_template.py"
        self.assertTrue(canvas_path.is_file(), f"Story Canvas template missing at {canvas_path}")
        content = canvas_path.read_text(encoding="utf-8")

        # 1. Semantic Landmarks & Main
        self.assertIn('role="banner"', content, "Story Canvas missing role='banner'")
        self.assertIn('role="main"', content, "Story Canvas missing role='main'")
        self.assertIn('role="toolbar"', content, "Story Canvas missing role='toolbar'")
        self.assertIn('role="region"', content, "Story Canvas missing role='region'")

        # 2. Modal Accessibility & Keyboard Trap/Dismiss
        self.assertIn('role="dialog"', content, "Story Canvas missing role='dialog' for paradigm guide")
        self.assertIn('aria-modal="true"', content, "Story Canvas missing aria-modal='true' on paradigm modal")
        self.assertIn('aria-labelledby=', content, "Story Canvas missing aria-labelledby on paradigm modal")
        self.assertIn('Escape', content, "Story Canvas missing keyboard Escape dismissal handler")

        # 3. Live Craft Tips
        self.assertIn('aria-live="polite"', content, "Story Canvas missing aria-live='polite' on tip bar")


if __name__ == "__main__":
    unittest.main()
