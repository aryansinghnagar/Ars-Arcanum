#!/usr/bin/env python3
"""
Ars Arcanum UI Visual Presets & Procedural Typewriter Sound Engine
(scripts/lib/ui_theme_engine.py)
=================================================================
Pure-Python & zero-asset Web Audio API synthesis engine delivering:
- 11 Distinct Atmospheric UI Visual Presets (CSS Token Palettes)
- 10 Realistic Procedural Typewriter & Keystroke Audio Models
- Zero-Asset Client-Side Synthesis (No WAV/MP3 files, zero external CDN)
- Strict Content Security Policy (default-src 'none') compliance
- Universal Theme & Sound Control Center Modal & Quick Switcher
"""

from __future__ import annotations

import json
from typing import Any

# ==============================================================================
# 1. VISUAL PRESET DEFINITIONS & CSS TOKEN MATRIX
# ==============================================================================

VISUAL_PRESETS: dict[str, dict[str, Any]] = {
    "sovereign-dark": {
        "id": "sovereign-dark",
        "name": "Sovereign Dark",
        "category": "core",
        "description": "Obsidian void, celestial cyan, and sovereign purple default.",
        "icon": "🌌",
        "tokens": {
            "--bg": "#090d16",
            "--bg-main": "#090d16",
            "--bg-primary": "#090d16",
            "--bg-body": "#090d16",
            "--surface": "#111827",
            "--surface-hover": "#1f2937",
            "--bg-panel": "#111827",
            "--bg-panel-sub": "#1f2937",
            "--bg-card": "#131d31",
            "--card-bg": "#131d31",
            "--card-border": "#1e2e4a",
            "--border": "#1e2e4a",
            "--border-sub": "#1f2937",
            "--border-color": "#1e2e4a",
            "--text": "#f8fafc",
            "--text-primary": "#f8fafc",
            "--text-main": "#f8fafc",
            "--text-muted": "#94a3b8",
            "--text-secondary": "#94a3b8",
            "--muted": "#94a3b8",
            "--accent": "#38bdf8",
            "--accent-primary": "#38bdf8",
            "--accent-blue": "#38bdf8",
            "--accent-cyan": "#06b6d4",
            "--accent-glow": "rgba(56, 189, 248, 0.25)",
            "--purple": "#c084fc",
            "--accent-purple": "#c084fc",
            "--green": "#10b981",
            "--accent-emerald": "#10b981",
            "--success": "#10b981",
            "--amber": "#f59e0b",
            "--accent-amber": "#f59e0b",
            "--warning": "#f59e0b",
            "--rose": "#f43f5e",
            "--accent-rose": "#f43f5e",
            "--danger": "#f43f5e",
            "--red": "#ef4444",
            "--shadow": "0 10px 25px -5px rgba(0, 0, 0, 0.5)",
            "--font-sans": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
            "--font-mono": "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace",
            "--font-serif": "'Georgia', 'EB Garamond', 'Times New Roman', serif",
        },
        "swatches": ["#090d16", "#111827", "#38bdf8", "#c084fc", "#10b981"],
    },
    "classic-light": {
        "id": "classic-light",
        "name": "Classic Light",
        "category": "core",
        "description": "Clean publishing manuscript, slate typography on crisp ivory.",
        "icon": "📄",
        "tokens": {
            "--bg": "#f8fafc",
            "--bg-main": "#f8fafc",
            "--bg-primary": "#f8fafc",
            "--bg-body": "#f8fafc",
            "--surface": "#ffffff",
            "--surface-hover": "#f1f5f9",
            "--bg-panel": "#ffffff",
            "--bg-panel-sub": "#f1f5f9",
            "--bg-card": "#ffffff",
            "--card-bg": "#ffffff",
            "--card-border": "#cbd5e1",
            "--border": "#cbd5e1",
            "--border-sub": "#e2e8f0",
            "--border-color": "#cbd5e1",
            "--text": "#0f172a",
            "--text-primary": "#0f172a",
            "--text-main": "#0f172a",
            "--text-muted": "#64748b",
            "--text-secondary": "#64748b",
            "--muted": "#64748b",
            "--accent": "#0284c7",
            "--accent-primary": "#0284c7",
            "--accent-blue": "#0284c7",
            "--accent-cyan": "#0891b2",
            "--accent-glow": "rgba(2, 132, 199, 0.15)",
            "--purple": "#9333ea",
            "--accent-purple": "#9333ea",
            "--green": "#059669",
            "--accent-emerald": "#059669",
            "--success": "#059669",
            "--amber": "#d97706",
            "--accent-amber": "#d97706",
            "--warning": "#d97706",
            "--rose": "#e11d48",
            "--accent-rose": "#e11d48",
            "--danger": "#e11d48",
            "--red": "#dc2626",
            "--shadow": "0 4px 6px -1px rgba(0, 0, 0, 0.08)",
            "--font-sans": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
            "--font-mono": "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace",
            "--font-serif": "'Georgia', 'EB Garamond', 'Times New Roman', serif",
        },
        "swatches": ["#f8fafc", "#ffffff", "#0284c7", "#9333ea", "#059669"],
    },
    "retro": {
        "id": "retro",
        "name": "Retro Amber CRT",
        "category": "vintage",
        "description": "1980s phosphor terminal, warm amber glow, and vintage monospace.",
        "icon": "📺",
        "tokens": {
            "--bg": "#120e06",
            "--bg-main": "#120e06",
            "--bg-primary": "#120e06",
            "--bg-body": "#120e06",
            "--surface": "#1c150a",
            "--surface-hover": "#291f0f",
            "--bg-panel": "#1c150a",
            "--bg-panel-sub": "#291f0f",
            "--bg-card": "#241b0c",
            "--card-bg": "#241b0c",
            "--card-border": "#423214",
            "--border": "#423214",
            "--border-sub": "#33260f",
            "--border-color": "#423214",
            "--text": "#fbbf24",
            "--text-primary": "#fbbf24",
            "--text-main": "#fbbf24",
            "--text-muted": "#b47818",
            "--text-secondary": "#b47818",
            "--muted": "#b47818",
            "--accent": "#f59e0b",
            "--accent-primary": "#f59e0b",
            "--accent-blue": "#fbbf24",
            "--accent-cyan": "#f59e0b",
            "--accent-glow": "rgba(245, 158, 11, 0.35)",
            "--purple": "#d97706",
            "--accent-purple": "#d97706",
            "--green": "#84cc16",
            "--accent-emerald": "#84cc16",
            "--success": "#84cc16",
            "--amber": "#fbbf24",
            "--accent-amber": "#fbbf24",
            "--warning": "#f59e0b",
            "--rose": "#ef4444",
            "--accent-rose": "#ef4444",
            "--danger": "#ef4444",
            "--red": "#dc2626",
            "--shadow": "0 8px 20px -4px rgba(0, 0, 0, 0.7)",
            "--font-sans": "'Courier New', Courier, monospace",
            "--font-mono": "'Courier New', Courier, monospace",
            "--font-serif": "'Courier New', Courier, monospace",
        },
        "swatches": ["#120e06", "#241b0c", "#fbbf24", "#f59e0b", "#84cc16"],
    },
    "futuristic": {
        "id": "futuristic",
        "name": "Futuristic HUD",
        "category": "scifi",
        "description": "High-altitude starship cockpit, electric neon cyan, and dark void.",
        "icon": "⚡",
        "tokens": {
            "--bg": "#030712",
            "--bg-main": "#030712",
            "--bg-primary": "#030712",
            "--bg-body": "#030712",
            "--surface": "#071226",
            "--surface-hover": "#0c1d3b",
            "--bg-panel": "#071226",
            "--bg-panel-sub": "#0c1d3b",
            "--bg-card": "#0b1933",
            "--card-bg": "#0b1933",
            "--card-border": "#163261",
            "--border": "#163261",
            "--border-sub": "#0f2347",
            "--border-color": "#163261",
            "--text": "#e0f2fe",
            "--text-primary": "#e0f2fe",
            "--text-main": "#e0f2fe",
            "--text-muted": "#5b84b1",
            "--text-secondary": "#5b84b1",
            "--muted": "#5b84b1",
            "--accent": "#00f0ff",
            "--accent-primary": "#00f0ff",
            "--accent-blue": "#00f0ff",
            "--accent-cyan": "#00f0ff",
            "--accent-glow": "rgba(0, 240, 255, 0.35)",
            "--purple": "#a855f7",
            "--accent-purple": "#a855f7",
            "--green": "#00ff9f",
            "--accent-emerald": "#00ff9f",
            "--success": "#00ff9f",
            "--amber": "#ffb800",
            "--accent-amber": "#ffb800",
            "--warning": "#ffb800",
            "--rose": "#ff0055",
            "--accent-rose": "#ff0055",
            "--danger": "#ff0055",
            "--red": "#ff0055",
            "--shadow": "0 10px 28px -5px rgba(0, 240, 255, 0.15)",
            "--font-sans": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
            "--font-mono": "ui-monospace, SFMono-Regular, monospace",
            "--font-serif": "'Inter', sans-serif",
        },
        "swatches": ["#030712", "#071226", "#00f0ff", "#a855f7", "#00ff9f"],
    },
    "retrofuturistic": {
        "id": "retrofuturistic",
        "name": "Retrofuturistic Synthwave",
        "category": "creative",
        "description": "1980s Outrun aesthetic, hot neon magenta, cyan grid, and deep violet.",
        "icon": "🌆",
        "tokens": {
            "--bg": "#13091f",
            "--bg-main": "#13091f",
            "--bg-primary": "#13091f",
            "--bg-body": "#13091f",
            "--surface": "#1f0d33",
            "--surface-hover": "#2f144d",
            "--bg-panel": "#1f0d33",
            "--bg-panel-sub": "#2f144d",
            "--bg-card": "#291145",
            "--card-bg": "#291145",
            "--card-border": "#581c87",
            "--border": "#581c87",
            "--border-sub": "#3b0764",
            "--border-color": "#581c87",
            "--text": "#fdf4ff",
            "--text-primary": "#fdf4ff",
            "--text-main": "#fdf4ff",
            "--text-muted": "#b080c9",
            "--text-secondary": "#b080c9",
            "--muted": "#b080c9",
            "--accent": "#ff2a85",
            "--accent-primary": "#ff2a85",
            "--accent-blue": "#00e5ff",
            "--accent-cyan": "#00e5ff",
            "--accent-glow": "rgba(255, 42, 133, 0.35)",
            "--purple": "#c084fc",
            "--accent-purple": "#c084fc",
            "--green": "#06ffd2",
            "--accent-emerald": "#06ffd2",
            "--success": "#06ffd2",
            "--amber": "#ffc400",
            "--accent-amber": "#ffc400",
            "--warning": "#ffc400",
            "--rose": "#ff3366",
            "--accent-rose": "#ff3366",
            "--danger": "#ff3366",
            "--red": "#ff0055",
            "--shadow": "0 10px 25px -5px rgba(255, 42, 133, 0.2)",
            "--font-sans": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
            "--font-mono": "ui-monospace, monospace",
            "--font-serif": "'Georgia', serif",
        },
        "swatches": ["#13091f", "#291145", "#ff2a85", "#00e5ff", "#06ffd2"],
    },
    "fantastical": {
        "id": "fantastical",
        "name": "Fantastical Grimoire",
        "category": "creative",
        "description": "Arcane illuminated manuscript, burnished gold, amethyst, and parchment.",
        "icon": "✨",
        "tokens": {
            "--bg": "#15101e",
            "--bg-main": "#15101e",
            "--bg-primary": "#15101e",
            "--bg-body": "#15101e",
            "--surface": "#1e162b",
            "--surface-hover": "#2d2140",
            "--bg-panel": "#1e162b",
            "--bg-panel-sub": "#2d2140",
            "--bg-card": "#281d3a",
            "--card-bg": "#281d3a",
            "--card-border": "#4c376f",
            "--border": "#4c376f",
            "--border-sub": "#382752",
            "--border-color": "#4c376f",
            "--text": "#fef3c7",
            "--text-primary": "#fef3c7",
            "--text-main": "#fef3c7",
            "--text-muted": "#a894c2",
            "--text-secondary": "#a894c2",
            "--muted": "#a894c2",
            "--accent": "#d97706",
            "--accent-primary": "#d97706",
            "--accent-blue": "#c084fc",
            "--accent-cyan": "#fbbf24",
            "--accent-glow": "rgba(217, 119, 6, 0.3)",
            "--purple": "#c084fc",
            "--accent-purple": "#c084fc",
            "--green": "#10b981",
            "--accent-emerald": "#10b981",
            "--success": "#10b981",
            "--amber": "#fbbf24",
            "--accent-amber": "#fbbf24",
            "--warning": "#fbbf24",
            "--rose": "#f43f5e",
            "--accent-rose": "#f43f5e",
            "--danger": "#f43f5e",
            "--red": "#ef4444",
            "--shadow": "0 10px 25px -5px rgba(0, 0, 0, 0.6)",
            "--font-sans": "'Georgia', 'EB Garamond', serif",
            "--font-mono": "ui-monospace, monospace",
            "--font-serif": "'Georgia', 'EB Garamond', 'Times New Roman', serif",
        },
        "swatches": ["#15101e", "#281d3a", "#d97706", "#c084fc", "#10b981"],
    },
    "grim": {
        "id": "grim",
        "name": "Grim Charcoal",
        "category": "dark",
        "description": "Weathered ash, desaturated iron, and dried crimson grimdark tone.",
        "icon": "⚔️",
        "tokens": {
            "--bg": "#0f0f11",
            "--bg-main": "#0f0f11",
            "--bg-primary": "#0f0f11",
            "--bg-body": "#0f0f11",
            "--surface": "#17171a",
            "--surface-hover": "#222227",
            "--bg-panel": "#17171a",
            "--bg-panel-sub": "#222227",
            "--bg-card": "#1f1f24",
            "--card-bg": "#1f1f24",
            "--card-border": "#383842",
            "--border": "#383842",
            "--border-sub": "#2c2c34",
            "--border-color": "#383842",
            "--text": "#d4d4d8",
            "--text-primary": "#d4d4d8",
            "--text-main": "#d4d4d8",
            "--text-muted": "#71717a",
            "--text-secondary": "#71717a",
            "--muted": "#71717a",
            "--accent": "#a1a1aa",
            "--accent-primary": "#a1a1aa",
            "--accent-blue": "#94a3b8",
            "--accent-cyan": "#71717a",
            "--accent-glow": "rgba(161, 161, 170, 0.2)",
            "--purple": "#7c3aed",
            "--accent-purple": "#7c3aed",
            "--green": "#4ade80",
            "--accent-emerald": "#4ade80",
            "--success": "#4ade80",
            "--amber": "#ca8a04",
            "--accent-amber": "#ca8a04",
            "--warning": "#ca8a04",
            "--rose": "#991b1b",
            "--accent-rose": "#991b1b",
            "--danger": "#991b1b",
            "--red": "#7f1d1d",
            "--shadow": "0 10px 25px -5px rgba(0, 0, 0, 0.7)",
            "--font-sans": "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
            "--font-mono": "ui-monospace, monospace",
            "--font-serif": "'Georgia', serif",
        },
        "swatches": ["#0f0f11", "#1f1f24", "#a1a1aa", "#991b1b", "#71717a"],
    },
    "edgy": {
        "id": "edgy",
        "name": "Edgy Cyber-Goth",
        "category": "dark",
        "description": "High-contrast pitch black, radioactive acid green, and razor crimson.",
        "icon": "⚡",
        "tokens": {
            "--bg": "#000000",
            "--bg-main": "#000000",
            "--bg-primary": "#000000",
            "--bg-body": "#000000",
            "--surface": "#0a0a0a",
            "--surface-hover": "#171717",
            "--bg-panel": "#0a0a0a",
            "--bg-panel-sub": "#171717",
            "--bg-card": "#141414",
            "--card-bg": "#141414",
            "--card-border": "#2e2e2e",
            "--border": "#2e2e2e",
            "--border-sub": "#222222",
            "--border-color": "#2e2e2e",
            "--text": "#ffffff",
            "--text-primary": "#ffffff",
            "--text-main": "#ffffff",
            "--text-muted": "#808080",
            "--text-secondary": "#808080",
            "--muted": "#808080",
            "--accent": "#22c55e",
            "--accent-primary": "#22c55e",
            "--accent-blue": "#00f0ff",
            "--accent-cyan": "#22c55e",
            "--accent-glow": "rgba(34, 197, 94, 0.4)",
            "--purple": "#a855f7",
            "--accent-purple": "#a855f7",
            "--green": "#22c55e",
            "--accent-emerald": "#22c55e",
            "--success": "#22c55e",
            "--amber": "#eab308",
            "--accent-amber": "#eab308",
            "--warning": "#eab308",
            "--rose": "#ff003c",
            "--accent-rose": "#ff003c",
            "--danger": "#ff003c",
            "--red": "#ff003c",
            "--shadow": "0 10px 30px -5px rgba(34, 197, 94, 0.2)",
            "--font-sans": "ui-monospace, SFMono-Regular, Menlo, Monaco, monospace",
            "--font-mono": "ui-monospace, SFMono-Regular, monospace",
            "--font-serif": "ui-monospace, monospace",
        },
        "swatches": ["#000000", "#141414", "#22c55e", "#ff003c", "#ffffff"],
    },
    "cozy": {
        "id": "cozy",
        "name": "Cozy Hearth & Matcha",
        "category": "warm",
        "description": "Autumnal terracotta, warm hazelnut wood, matcha green, and cream.",
        "icon": "☕",
        "tokens": {
            "--bg": "#1c1613",
            "--bg-main": "#1c1613",
            "--bg-primary": "#1c1613",
            "--bg-body": "#1c1613",
            "--surface": "#261f1a",
            "--surface-hover": "#362c26",
            "--bg-panel": "#261f1a",
            "--bg-panel-sub": "#362c26",
            "--bg-card": "#332a23",
            "--card-bg": "#332a23",
            "--card-border": "#524237",
            "--border": "#524237",
            "--border-sub": "#42352c",
            "--border-color": "#524237",
            "--text": "#fdebd0",
            "--text-primary": "#fdebd0",
            "--text-main": "#fdebd0",
            "--text-muted": "#ac9688",
            "--text-secondary": "#ac9688",
            "--muted": "#ac9688",
            "--accent": "#e09f67",
            "--accent-primary": "#e09f67",
            "--accent-blue": "#e09f67",
            "--accent-cyan": "#8cb369",
            "--accent-glow": "rgba(224, 159, 103, 0.25)",
            "--purple": "#b5838d",
            "--accent-purple": "#b5838d",
            "--green": "#8cb369",
            "--accent-emerald": "#8cb369",
            "--success": "#8cb369",
            "--amber": "#e7c169",
            "--accent-amber": "#e7c169",
            "--warning": "#e7c169",
            "--rose": "#d96b6b",
            "--accent-rose": "#d96b6b",
            "--danger": "#d96b6b",
            "--red": "#c94a4a",
            "--shadow": "0 8px 22px -4px rgba(0, 0, 0, 0.5)",
            "--font-sans": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
            "--font-mono": "ui-monospace, monospace",
            "--font-serif": "'Georgia', serif",
        },
        "swatches": ["#1c1613", "#332a23", "#e09f67", "#8cb369", "#fdebd0"],
    },
    "scifi": {
        "id": "scifi",
        "name": "Sci-Fi Telemetry",
        "category": "scifi",
        "description": "Deep cobalt orbital vessel instrumentation and starlight white.",
        "icon": "🛰️",
        "tokens": {
            "--bg": "#080e1e",
            "--bg-main": "#080e1e",
            "--bg-primary": "#080e1e",
            "--bg-body": "#080e1e",
            "--surface": "#0e1a38",
            "--surface-hover": "#152650",
            "--bg-panel": "#0e1a38",
            "--bg-panel-sub": "#152650",
            "--bg-card": "#13244d",
            "--card-bg": "#13244d",
            "--card-border": "#1d3d82",
            "--border": "#1d3d82",
            "--border-sub": "#152c5c",
            "--border-color": "#1d3d82",
            "--text": "#f0f6fc",
            "--text-primary": "#f0f6fc",
            "--text-main": "#f0f6fc",
            "--text-muted": "#6b8ec4",
            "--text-secondary": "#6b8ec4",
            "--muted": "#6b8ec4",
            "--accent": "#38bdf8",
            "--accent-primary": "#38bdf8",
            "--accent-blue": "#38bdf8",
            "--accent-cyan": "#38bdf8",
            "--accent-glow": "rgba(56, 189, 248, 0.3)",
            "--purple": "#818cf8",
            "--accent-purple": "#818cf8",
            "--green": "#34d399",
            "--accent-emerald": "#34d399",
            "--success": "#34d399",
            "--amber": "#fbbf24",
            "--accent-amber": "#fbbf24",
            "--warning": "#fbbf24",
            "--rose": "#f87171",
            "--accent-rose": "#f87171",
            "--danger": "#f87171",
            "--red": "#ef4444",
            "--shadow": "0 10px 26px -5px rgba(56, 189, 248, 0.15)",
            "--font-sans": "ui-monospace, SFMono-Regular, Menlo, Monaco, monospace",
            "--font-mono": "ui-monospace, SFMono-Regular, monospace",
            "--font-serif": "ui-monospace, monospace",
        },
        "swatches": ["#080e1e", "#13244d", "#38bdf8", "#818cf8", "#34d399"],
    },
    "horror": {
        "id": "horror",
        "name": "Cosmic Horror Void",
        "category": "dark",
        "description": "Abyssal necrotic void, bruised violet, and eerie spectral green.",
        "icon": "👁️",
        "tokens": {
            "--bg": "#0a060d",
            "--bg-main": "#0a060d",
            "--bg-primary": "#0a060d",
            "--bg-body": "#0a060d",
            "--surface": "#120a17",
            "--surface-hover": "#1d1026",
            "--bg-panel": "#120a17",
            "--bg-panel-sub": "#1d1026",
            "--bg-card": "#1c0e24",
            "--card-bg": "#1c0e24",
            "--card-border": "#3b1b4d",
            "--border": "#3b1b4d",
            "--border-sub": "#291336",
            "--border-color": "#3b1b4d",
            "--text": "#e2d9ec",
            "--text-primary": "#e2d9ec",
            "--text-main": "#e2d9ec",
            "--text-muted": "#8c77a1",
            "--text-secondary": "#8c77a1",
            "--muted": "#8c77a1",
            "--accent": "#a855f7",
            "--accent-primary": "#a855f7",
            "--accent-blue": "#c084fc",
            "--accent-cyan": "#10b981",
            "--accent-glow": "rgba(168, 85, 247, 0.35)",
            "--purple": "#c084fc",
            "--accent-purple": "#c084fc",
            "--green": "#10b981",
            "--accent-emerald": "#10b981",
            "--success": "#10b981",
            "--amber": "#d97706",
            "--accent-amber": "#d97706",
            "--warning": "#d97706",
            "--rose": "#881337",
            "--accent-rose": "#881337",
            "--danger": "#881337",
            "--red": "#7f1d1d",
            "--shadow": "0 10px 25px -5px rgba(168, 85, 247, 0.2)",
            "--font-sans": "'Georgia', serif",
            "--font-mono": "ui-monospace, monospace",
            "--font-serif": "'Georgia', 'Times New Roman', serif",
        },
        "swatches": ["#0a060d", "#1c0e24", "#a855f7", "#10b981", "#881337"],
    },
}

# ==============================================================================
# 2. SOUND PRESET DEFINITIONS & ACOUSTIC MODELS
# ==============================================================================

SOUND_PRESETS: dict[str, dict[str, Any]] = {
    "remington_1890": {
        "id": "remington_1890",
        "name": "Remington Standard (1890)",
        "era": "1890s",
        "description": "Heavy cast-iron carriage impact, deep mechanical body, antique brass resonance.",
        "icon": "🏛️",
    },
    "royal_1930": {
        "id": "royal_1930",
        "name": "Royal Model P (1930)",
        "era": "1930s",
        "description": "Classic mechanical typewriter slug hit, snappy metal clack, distinct release.",
        "icon": "🖋️",
    },
    "selectric_1960": {
        "id": "selectric_1960",
        "name": "IBM Selectric (1960)",
        "era": "1960s",
        "description": "Electric typeball solenoid snap, motor hum pulse, rapid corporate keystroke.",
        "icon": "🖩",
    },
    "smith_corona_1980": {
        "id": "smith_corona_1980",
        "name": "Smith Corona (1980)",
        "era": "1980s",
        "description": "Electronic portable typewriter daisywheel strike, high-speed plastic snap.",
        "icon": "📟",
    },
    "cherry_blue": {
        "id": "cherry_blue",
        "name": "Cherry MX Blue",
        "era": "Modern",
        "description": "Tactile clicky mechanical keyboard, crisp leaf pop, light bottom-out thud.",
        "icon": "⌨️",
    },
    "thock": {
        "id": "thock",
        "name": "Custom Linear (Thock)",
        "era": "Modern",
        "description": "Lubed linear switches on brass plate, deep bass acoustic pop, muffled bottom-out.",
        "icon": "🧈",
    },
    "cyber_terminal": {
        "id": "cyber_terminal",
        "name": "Cyber Terminal",
        "era": "2080s",
        "description": "Retro-futuristic terminal reed relay, electronic frequency chirp, laser precision.",
        "icon": "⚡",
    },
    "steampunk": {
        "id": "steampunk",
        "name": "Steampunk Chronometer",
        "era": "Victorian",
        "description": "Brass clockwork escapement tick, miniature steam hiss, precision gear click.",
        "icon": "⚙️",
    },
    "scribe_quill": {
        "id": "scribe_quill",
        "name": "Scribe's Feather Quill",
        "era": "Medieval",
        "description": "Parchment surface friction scratch, ink flow stroke, delicate nib tap.",
        "icon": "🪶",
    },
    "gothic_relic": {
        "id": "gothic_relic",
        "name": "Gothic Chisel & Stone",
        "era": "Ancient",
        "description": "Stone tablet impact, heavy chisel thud, flint resonance ping.",
        "icon": "🗿",
    },
}


# ==============================================================================
# 3. CSS STRING GENERATOR
# ==============================================================================

def get_theme_engine_css() -> str:
    """Generates the comprehensive CSS string defining all 11 visual presets, CRT effects, and modal UI."""
    css_rules: list[str] = []

    # Default :root rules (sovereign-dark)
    default_tokens = VISUAL_PRESETS["sovereign-dark"]["tokens"]
    root_props = "\n".join(f"    {k}: {v};" for k, v in default_tokens.items())
    css_rules.append(f""":root {{
{root_props}
}}""")

    # Theme-specific selectors for [data-theme="id"], body[data-theme="id"], and html[data-theme="id"]
    for pid, pdata in VISUAL_PRESETS.items():
        props = "\n".join(f"    {k}: {v};" for k, v in pdata["tokens"].items())
        css_rules.append(f"""[data-theme="{pid}"], html[data-theme="{pid}"], body[data-theme="{pid}"] {{
{props}
}}""")

    # CRT Scanline & Phosphor Overlay Styles
    css_rules.append("""
/* CRT Scanline & Phosphor Glow Mode */
.crt-effect {
    position: relative;
}
.crt-effect::before {
    content: " ";
    display: block;
    position: fixed;
    top: 0; left: 0; bottom: 0; right: 0;
    background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.28) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.03), rgba(0, 255, 0, 0.01), rgba(0, 0, 255, 0.03));
    z-index: 99998;
    background-size: 100% 3px, 6px 100%;
    pointer-events: none;
    opacity: 0.85;
}
.crt-effect::after {
    content: " ";
    display: block;
    position: fixed;
    top: 0; left: 0; bottom: 0; right: 0;
    background: radial-gradient(circle at center, transparent 60%, rgba(0, 0, 0, 0.65) 100%);
    z-index: 99999;
    pointer-events: none;
}

/* Theme Launcher Quick Button */
.arcanum-theme-launcher-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: var(--surface);
    color: var(--text);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.45rem 0.85rem;
    font-size: 0.825rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    user-select: none;
}
.arcanum-theme-launcher-btn:hover {
    background: var(--surface-hover);
    border-color: var(--accent);
    color: var(--accent);
    box-shadow: 0 0 10px var(--accent-glow);
}

/* Theme & Sound Studio Control Center Modal */
.arcanum-modal-overlay {
    display: none;
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0, 0, 0, 0.75);
    backdrop-filter: blur(6px);
    z-index: 100000;
    align-items: center;
    justify-content: center;
    padding: 1.5rem;
    box-sizing: border-box;
}
.arcanum-modal-overlay.active {
    display: flex;
}
.arcanum-modal-dialog {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 16px;
    width: 100%;
    max-width: 860px;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.75), 0 0 25px var(--accent-glow);
    overflow: hidden;
    color: var(--text);
}
.arcanum-modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.25rem 1.5rem;
    border-bottom: 1px solid var(--border);
    background: var(--surface);
}
.arcanum-modal-header h2 {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 800;
    display: flex;
    align-items: center;
    gap: 0.6rem;
    color: var(--text);
}
.arcanum-modal-close-btn {
    background: transparent;
    border: none;
    color: var(--text-muted);
    font-size: 1.35rem;
    cursor: pointer;
    padding: 0.2rem 0.5rem;
    border-radius: 6px;
    line-height: 1;
}
.arcanum-modal-close-btn:hover {
    color: var(--rose);
    background: var(--surface-hover);
}
.arcanum-modal-nav {
    display: flex;
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 0 1.5rem;
    gap: 0.5rem;
}
.arcanum-tab-btn {
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    padding: 0.75rem 1rem;
    color: var(--text-muted);
    font-weight: 600;
    font-size: 0.875rem;
    cursor: pointer;
    transition: all 0.2s;
}
.arcanum-tab-btn.active {
    color: var(--accent);
    border-bottom-color: var(--accent);
}
.arcanum-modal-body {
    padding: 1.5rem;
    overflow-y: auto;
    flex: 1;
}
.arcanum-tab-content {
    display: none;
}
.arcanum-tab-content.active {
    display: block;
}

/* Preset Cards Grid */
.arcanum-preset-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 1rem;
}
.arcanum-preset-card {
    background: var(--surface);
    border: 2px solid var(--border);
    border-radius: 12px;
    padding: 1rem;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.arcanum-preset-card:hover {
    border-color: var(--accent);
    transform: translateY(-2px);
    box-shadow: 0 6px 15px rgba(0,0,0,0.3);
}
.arcanum-preset-card.active {
    border-color: var(--accent);
    background: var(--bg-card);
    box-shadow: 0 0 15px var(--accent-glow);
}
.arcanum-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
}
.arcanum-card-title {
    font-weight: 700;
    font-size: 0.95rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}
.arcanum-swatch-row {
    display: flex;
    gap: 4px;
    margin: 0.6rem 0;
}
.arcanum-swatch-dot {
    width: 14px;
    height: 14px;
    border-radius: 50%;
    border: 1px solid rgba(255,255,255,0.15);
}
.arcanum-card-desc {
    font-size: 0.775rem;
    color: var(--text-muted);
    line-height: 1.4;
}

/* Sound Engine Controls */
.arcanum-sound-controls {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 1.25rem;
}
.arcanum-control-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    flex-wrap: wrap;
    gap: 0.75rem;
}
.arcanum-control-row:last-child {
    margin-bottom: 0;
}
.arcanum-sound-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
    gap: 0.85rem;
}
.arcanum-sound-card {
    background: var(--surface);
    border: 2px solid var(--border);
    border-radius: 10px;
    padding: 0.85rem;
    cursor: pointer;
    transition: all 0.2s;
}
.arcanum-sound-card:hover {
    border-color: var(--accent);
}
.arcanum-sound-card.active {
    border-color: var(--accent);
    background: var(--bg-card);
    box-shadow: 0 0 12px var(--accent-glow);
}
.arcanum-sound-title {
    font-weight: 700;
    font-size: 0.875rem;
    margin-bottom: 0.25rem;
    display: flex;
    align-items: center;
    gap: 0.35rem;
}
.arcanum-sound-era {
    font-size: 0.7rem;
    color: var(--accent);
    text-transform: uppercase;
    font-weight: 700;
}
.arcanum-sound-desc {
    font-size: 0.75rem;
    color: var(--text-muted);
    line-height: 1.35;
}
.arcanum-test-keys {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin-top: 1rem;
}
.arcanum-key-btn {
    background: var(--bg-panel-sub);
    color: var(--text);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 0.4rem 0.85rem;
    font-size: 0.8rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s;
}
.arcanum-key-btn:hover {
    background: var(--accent);
    color: var(--bg);
    border-color: var(--accent);
}
.arcanum-key-btn:active {
    transform: scale(0.95);
}
""")

    return "\n\n".join(css_rules)


# ==============================================================================
# 4. JAVASCRIPT STRING GENERATOR (PROCEDURAL WEB AUDIO SYNTHESIS)
# ==============================================================================

def get_theme_engine_js() -> str:
    """
    Generates the pure client-side JavaScript engine string:
    - TypewriterAudioEngine with 10 procedural synthesis models
    - ArcanumThemeEngine with localStorage persistence
    - Keyboard typing hooks and modal controls
    """
    presets_json = json.dumps(VISUAL_PRESETS, indent=2)
    sounds_json = json.dumps(SOUND_PRESETS, indent=2)

    return f"""
// Ars Arcanum Procedural Typewriter Sound Engine & UI Theme Controller
// 100% Offline & Zero External Assets (Web Audio API Synthesized)
(function() {{
  'use strict';

  const PRESETS = {presets_json};
  const SOUND_MODELS = {sounds_json};

  // ==========================================================================
  // 1. PROCEDURAL WEB AUDIO TYPEWRITER SYNTHESIS
  // ==========================================================================
  class TypewriterAudioEngine {{
    constructor() {{
      this.ctx = null;
      this.noiseBuffer = null;
      this.currentModel = localStorage.getItem('arcanum_sound_preset') || 'remington_1890';
      this.volume = parseFloat(localStorage.getItem('arcanum_sound_volume') || '0.75');
      this.isMuted = localStorage.getItem('arcanum_sound_muted') === 'true';
    }}

    _initContext() {{
      if (!this.ctx) {{
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        if (AudioCtx) {{
          this.ctx = new AudioCtx();
          this._buildNoiseBuffer();
        }}
      }}
      if (this.ctx && this.ctx.state === 'suspended') {{
        this.ctx.resume();
      }}
    }}

    _buildNoiseBuffer() {{
      if (!this.ctx) return;
      const bufferSize = Math.floor(this.ctx.sampleRate * 0.2); // 200ms white noise
      this.noiseBuffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
      const data = this.noiseBuffer.getChannelData(0);
      for (let i = 0; i < bufferSize; i++) {{
        data[i] = Math.random() * 2 - 1;
      }}
    }}

    setVolume(val) {{
      this.volume = Math.max(0, Math.min(1, parseFloat(val)));
      localStorage.setItem('arcanum_sound_volume', this.volume.toString());
    }}

    setMuted(muted) {{
      this.isMuted = Boolean(muted);
      localStorage.setItem('arcanum_sound_muted', this.isMuted.toString());
    }}

    setModel(modelId) {{
      if (SOUND_MODELS[modelId]) {{
        this.currentModel = modelId;
        localStorage.setItem('arcanum_sound_preset', modelId);
      }}
    }}

    play(keyName) {{
      if (this.isMuted || this.volume <= 0.001) return;
      if (!keyName) return;

      const key = keyName.toLowerCase();
      // Ignore modifier and non-character navigation keys to prevent double/phantom strikes
      const ignoredKeys = new Set([
        'shift', 'control', 'alt', 'meta', 'capslock', 'escape',
        'arrowleft', 'arrowright', 'arrowup', 'arrowdown',
        'home', 'end', 'pageup', 'pagedown', 'insert',
        'pause', 'scrolllock', 'numlock', 'contextmenu', 'tab',
        'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12'
      ]);
      if (ignoredKeys.has(key)) return;

      this._initContext();
      if (!this.ctx) return;

      const now = this.ctx.currentTime;
      const pitchVar = 1.0 + (Math.random() * 0.08 - 0.04); // +/- 4% pitch variance
      const gainVar = (0.9 + Math.random() * 0.2) * this.volume; // +/- 10% gain variance

      if (key === ' ' || key === 'space' || key === 'spacebar') {{
        this._playSpace(now, pitchVar * 0.85, gainVar * 1.1);
      }} else if (key === 'enter' || key === 'return') {{
        this._playEnter(now, pitchVar, gainVar);
      }} else if (key === 'backspace' || key === 'delete') {{
        this._playBackspace(now, pitchVar, gainVar);
      }} else {{
        this._playModelStrike(this.currentModel, now, pitchVar, gainVar);
      }}
    }}

    _createNoiseSource() {{
      if (!this.noiseBuffer || !this.ctx) return null;
      const src = this.ctx.createBufferSource();
      src.buffer = this.noiseBuffer;
      return src;
    }}

    _playModelStrike(model, t, pitch, gain) {{
      const ctx = this.ctx;
      switch (model) {{
        case 'remington_1890': {{
          // Heavy cast iron impact + antique low body + micro ping
          const osc = ctx.createOscillator();
          const oscGain = ctx.createGain();
          osc.type = 'triangle';
          osc.frequency.setValueAtTime(140 * pitch, t);
          osc.frequency.exponentialRampToValueAtTime(65 * pitch, t + 0.045);
          oscGain.gain.setValueAtTime(0.4 * gain, t);
          oscGain.gain.exponentialRampToValueAtTime(0.0001, t + 0.045);
          osc.connect(oscGain);
          oscGain.connect(ctx.destination);
          osc.start(t);
          osc.stop(t + 0.05);

          const noise = this._createNoiseSource();
          if (noise) {{
            const filter = ctx.createBiquadFilter();
            filter.type = 'bandpass';
            filter.frequency.setValueAtTime(950 * pitch, t);
            filter.Q.setValueAtTime(3.5, t);
            const nGain = ctx.createGain();
            nGain.gain.setValueAtTime(0.55 * gain, t);
            nGain.gain.exponentialRampToValueAtTime(0.0001, t + 0.03);
            noise.connect(filter);
            filter.connect(nGain);
            nGain.connect(ctx.destination);
            noise.start(t);
            noise.stop(t + 0.035);
          }}
          break;
        }}

        case 'royal_1930': {{
          // Classic crisp metal slug hit + snappy release
          const noise = this._createNoiseSource();
          if (noise) {{
            const filter = ctx.createBiquadFilter();
            filter.type = 'bandpass';
            filter.frequency.setValueAtTime(1800 * pitch, t);
            filter.Q.setValueAtTime(4.5, t);
            const nGain = ctx.createGain();
            nGain.gain.setValueAtTime(0.6 * gain, t);
            nGain.gain.exponentialRampToValueAtTime(0.0001, t + 0.022);
            noise.connect(filter);
            filter.connect(nGain);
            nGain.connect(ctx.destination);
            noise.start(t);
            noise.stop(t + 0.025);
          }}

          const osc = ctx.createOscillator();
          const oscGain = ctx.createGain();
          osc.type = 'sine';
          osc.frequency.setValueAtTime(440 * pitch, t);
          osc.frequency.exponentialRampToValueAtTime(180 * pitch, t + 0.025);
          oscGain.gain.setValueAtTime(0.3 * gain, t);
          oscGain.gain.exponentialRampToValueAtTime(0.0001, t + 0.025);
          osc.connect(oscGain);
          oscGain.connect(ctx.destination);
          osc.start(t);
          osc.stop(t + 0.03);
          break;
        }}

        case 'selectric_1960': {{
          // Electric typeball solenoid snap + motor pulse
          const osc = ctx.createOscillator();
          const oscGain = ctx.createGain();
          osc.type = 'square';
          osc.frequency.setValueAtTime(520 * pitch, t);
          osc.frequency.exponentialRampToValueAtTime(210 * pitch, t + 0.018);
          oscGain.gain.setValueAtTime(0.25 * gain, t);
          oscGain.gain.exponentialRampToValueAtTime(0.0001, t + 0.018);
          osc.connect(oscGain);
          oscGain.connect(ctx.destination);
          osc.start(t);
          osc.stop(t + 0.02);

          const noise = this._createNoiseSource();
          if (noise) {{
            const filter = ctx.createBiquadFilter();
            filter.type = 'bandpass';
            filter.frequency.setValueAtTime(1300 * pitch, t);
            filter.Q.setValueAtTime(3.0, t);
            const nGain = ctx.createGain();
            nGain.gain.setValueAtTime(0.45 * gain, t);
            nGain.gain.exponentialRampToValueAtTime(0.0001, t + 0.016);
            noise.connect(filter);
            filter.connect(nGain);
            nGain.connect(ctx.destination);
            noise.start(t);
            noise.stop(t + 0.02);
          }}
          break;
        }}

        case 'smith_corona_1980': {{
          // Electronic daisywheel snap + high-speed hammer
          const noise = this._createNoiseSource();
          if (noise) {{
            const filter = ctx.createBiquadFilter();
            filter.type = 'highpass';
            filter.frequency.setValueAtTime(2600 * pitch, t);
            const nGain = ctx.createGain();
            nGain.gain.setValueAtTime(0.5 * gain, t);
            nGain.gain.exponentialRampToValueAtTime(0.0001, t + 0.014);
            noise.connect(filter);
            filter.connect(nGain);
            nGain.connect(ctx.destination);
            noise.start(t);
            noise.stop(t + 0.018);
          }}
          break;
        }}

        case 'cherry_blue': {{
          // Tactile leaf pop + bottom-out thud + spring ring
          const clickOsc = ctx.createOscillator();
          const clickGain = ctx.createGain();
          clickOsc.type = 'sine';
          clickOsc.frequency.setValueAtTime(3400 * pitch, t);
          clickOsc.frequency.exponentialRampToValueAtTime(1600 * pitch, t + 0.01);
          clickGain.gain.setValueAtTime(0.4 * gain, t);
          clickGain.gain.exponentialRampToValueAtTime(0.0001, t + 0.01);
          clickOsc.connect(clickGain);
          clickGain.connect(ctx.destination);
          clickOsc.start(t);
          clickOsc.stop(t + 0.012);

          const thudOsc = ctx.createOscillator();
          const thudGain = ctx.createGain();
          thudOsc.type = 'triangle';
          thudOsc.frequency.setValueAtTime(260 * pitch, t + 0.004);
          thudOsc.frequency.exponentialRampToValueAtTime(90 * pitch, t + 0.03);
          thudGain.gain.setValueAtTime(0.35 * gain, t + 0.004);
          thudGain.gain.exponentialRampToValueAtTime(0.0001, t + 0.03);
          thudOsc.connect(thudGain);
          thudGain.connect(ctx.destination);
          thudOsc.start(t + 0.004);
          thudOsc.stop(t + 0.035);
          break;
        }}

        case 'thock': {{
          // Lubed linear switch: deep bass pop, zero high click
          const osc = ctx.createOscillator();
          const oscGain = ctx.createGain();
          osc.type = 'sine';
          osc.frequency.setValueAtTime(165 * pitch, t);
          osc.frequency.exponentialRampToValueAtTime(80 * pitch, t + 0.04);
          oscGain.gain.setValueAtTime(0.65 * gain, t);
          oscGain.gain.exponentialRampToValueAtTime(0.0001, t + 0.04);
          osc.connect(oscGain);
          oscGain.connect(ctx.destination);
          osc.start(t);
          osc.stop(t + 0.045);

          const noise = this._createNoiseSource();
          if (noise) {{
            const filter = ctx.createBiquadFilter();
            filter.type = 'lowpass';
            filter.frequency.setValueAtTime(550 * pitch, t);
            const nGain = ctx.createGain();
            nGain.gain.setValueAtTime(0.3 * gain, t);
            nGain.gain.exponentialRampToValueAtTime(0.0001, t + 0.025);
            noise.connect(filter);
            filter.connect(nGain);
            nGain.connect(ctx.destination);
            noise.start(t);
            noise.stop(t + 0.03);
          }}
          break;
        }}

        case 'cyber_terminal': {{
          // Magnetic reed relay tick + electronic chirp
          const osc1 = ctx.createOscillator();
          const osc2 = ctx.createOscillator();
          const chirpGain = ctx.createGain();
          osc1.type = 'sine';
          osc2.type = 'triangle';
          osc1.frequency.setValueAtTime(1200 * pitch, t);
          osc2.frequency.setValueAtTime(1800 * pitch, t);
          chirpGain.gain.setValueAtTime(0.25 * gain, t);
          chirpGain.gain.exponentialRampToValueAtTime(0.0001, t + 0.015);
          osc1.connect(chirpGain);
          osc2.connect(chirpGain);
          chirpGain.connect(ctx.destination);
          osc1.start(t);
          osc2.start(t);
          osc1.stop(t + 0.018);
          osc2.stop(t + 0.018);
          break;
        }}

        case 'steampunk': {{
          // Clockwork escapement tick + steam puff
          const tickOsc = ctx.createOscillator();
          const tickGain = ctx.createGain();
          tickOsc.type = 'sine';
          tickOsc.frequency.setValueAtTime(2200 * pitch, t);
          tickGain.gain.setValueAtTime(0.3 * gain, t);
          tickGain.gain.exponentialRampToValueAtTime(0.0001, t + 0.01);
          tickOsc.connect(tickGain);
          tickGain.connect(ctx.destination);
          tickOsc.start(t);
          tickOsc.stop(t + 0.012);

          const noise = this._createNoiseSource();
          if (noise) {{
            const filter = ctx.createBiquadFilter();
            filter.type = 'highpass';
            filter.frequency.setValueAtTime(3200 * pitch, t);
            const nGain = ctx.createGain();
            nGain.gain.setValueAtTime(0.2 * gain, t);
            nGain.gain.exponentialRampToValueAtTime(0.0001, t + 0.04);
            noise.connect(filter);
            filter.connect(nGain);
            nGain.connect(ctx.destination);
            noise.start(t);
            noise.stop(t + 0.045);
          }}
          break;
        }}

        case 'scribe_quill': {{
          // Parchment paper scratch friction + soft nib tap
          const noise = this._createNoiseSource();
          if (noise) {{
            const filter = ctx.createBiquadFilter();
            filter.type = 'bandpass';
            filter.frequency.setValueAtTime(2100 * pitch, t);
            filter.Q.setValueAtTime(2.0, t);
            const nGain = ctx.createGain();
            nGain.gain.setValueAtTime(0.05 * gain, t);
            nGain.gain.linearRampToValueAtTime(0.4 * gain, t + 0.02);
            nGain.gain.exponentialRampToValueAtTime(0.0001, t + 0.07);
            noise.connect(filter);
            filter.connect(nGain);
            nGain.connect(ctx.destination);
            noise.start(t);
            noise.stop(t + 0.075);
          }}
          break;
        }}

        case 'gothic_relic': {{
          // Stone chisel impact + flint ping
          const osc = ctx.createOscillator();
          const oscGain = ctx.createGain();
          osc.type = 'triangle';
          osc.frequency.setValueAtTime(110 * pitch, t);
          osc.frequency.exponentialRampToValueAtTime(45 * pitch, t + 0.06);
          oscGain.gain.setValueAtTime(0.55 * gain, t);
          oscGain.gain.exponentialRampToValueAtTime(0.0001, t + 0.06);
          osc.connect(oscGain);
          oscGain.connect(ctx.destination);
          osc.start(t);
          osc.stop(t + 0.065);

          const pingOsc = ctx.createOscillator();
          const pingGain = ctx.createGain();
          pingOsc.type = 'sine';
          pingOsc.frequency.setValueAtTime(2800 * pitch, t);
          pingGain.gain.setValueAtTime(0.2 * gain, t);
          pingGain.gain.exponentialRampToValueAtTime(0.0001, t + 0.035);
          pingOsc.connect(pingGain);
          pingGain.connect(ctx.destination);
          pingOsc.start(t);
          pingOsc.stop(t + 0.04);
          break;
        }}

        default:
          this._playModelStrike('remington_1890', t, pitch, gain);
      }}
    }}

    _playSpace(t, pitch, gain) {{
      const ctx = this.ctx;
      const osc = ctx.createOscillator();
      const oscGain = ctx.createGain();
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(115 * pitch, t);
      osc.frequency.exponentialRampToValueAtTime(45 * pitch, t + 0.06);
      oscGain.gain.setValueAtTime(0.6 * gain, t);
      oscGain.gain.exponentialRampToValueAtTime(0.0001, t + 0.06);
      osc.connect(oscGain);
      oscGain.connect(ctx.destination);
      osc.start(t);
      osc.stop(t + 0.065);
    }}

    _playEnter(t, pitch, gain) {{
      const ctx = this.ctx;
      // 1. Carriage slide friction
      const noise = this._createNoiseSource();
      if (noise) {{
        const filter = ctx.createBiquadFilter();
        filter.type = 'bandpass';
        filter.frequency.setValueAtTime(1400 * pitch, t);
        const nGain = ctx.createGain();
        nGain.gain.setValueAtTime(0.3 * gain, t);
        nGain.gain.exponentialRampToValueAtTime(0.0001, t + 0.09);
        noise.connect(filter);
        filter.connect(nGain);
        nGain.connect(ctx.destination);
        noise.start(t);
        noise.stop(t + 0.095);
      }}

      // 2. Brass Carriage Bell Ping
      const bellTime = t + 0.07;
      const bell1 = ctx.createOscillator();
      const bell2 = ctx.createOscillator();
      const bellGain = ctx.createGain();
      bell1.type = 'sine';
      bell2.type = 'sine';
      bell1.frequency.setValueAtTime(1760 * pitch, bellTime); // A6
      bell2.frequency.setValueAtTime(3520 * pitch, bellTime); // A7
      bellGain.gain.setValueAtTime(0.45 * gain, bellTime);
      bellGain.gain.exponentialRampToValueAtTime(0.0001, bellTime + 0.65);
      bell1.connect(bellGain);
      bell2.connect(bellGain);
      bellGain.connect(ctx.destination);
      bell1.start(bellTime);
      bell2.start(bellTime);
      bell1.stop(bellTime + 0.7);
      bell2.stop(bellTime + 0.7);
    }}

    _playBackspace(t, pitch, gain) {{
      const ctx = this.ctx;
      // Ratchet clack: double-click
      for (const offset of [0, 0.016]) {{
        const osc = ctx.createOscillator();
        const oscGain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(2400 * pitch, t + offset);
        oscGain.gain.setValueAtTime(0.35 * gain, t + offset);
        oscGain.gain.exponentialRampToValueAtTime(0.0001, t + offset + 0.012);
        osc.connect(oscGain);
        oscGain.connect(ctx.destination);
        osc.start(t + offset);
        osc.stop(t + offset + 0.015);
      }}
    }}
  }}

  // ==========================================================================
  // 2. ARCANUM THEME & STUDIO MANAGER
  // ==========================================================================
  const audio = new TypewriterAudioEngine();

  const ArcanumThemeEngine = {{
    audio: audio,
    presets: PRESETS,
    soundModels: SOUND_MODELS,

    init() {{
      // Load stored theme or default
      const savedTheme = localStorage.getItem('arcanum_theme_preset') || 'sovereign-dark';
      this.setTheme(savedTheme, false);

      // Load stored CRT mode
      const savedCrt = localStorage.getItem('arcanum_crt_fx') === 'true';
      this.setCrtEffect(savedCrt, false);

      // Bind global keyboard shortcut: Ctrl+Shift+T opens studio modal
      document.addEventListener('keydown', (e) => {{
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && (e.key === 'T' || e.key === 't')) {{
          e.preventDefault();
          this.toggleModal();
        }}
      }});

      // Auto-attach typewriter sounds to inputs and drafting areas
      this.autoAttachTypewriter();
    }},

    setTheme(themeId, persist = true) {{
      if (!PRESETS[themeId]) return;
      document.documentElement.setAttribute('data-theme', themeId);
      document.body.setAttribute('data-theme', themeId);
      if (persist) {{
        localStorage.setItem('arcanum_theme_preset', themeId);
      }}
      // Update UI active states in modal
      document.querySelectorAll('.arcanum-preset-card').forEach(card => {{
        if (card.getAttribute('data-preset-id') === themeId) {{
          card.classList.add('active');
        }} else {{
          card.classList.remove('active');
        }}
      }});
    }},

    setCrtEffect(enabled, persist = true) {{
      const isEnabled = Boolean(enabled);
      if (isEnabled) {{
        document.body.classList.add('crt-effect');
      }} else {{
        document.body.classList.remove('crt-effect');
      }}
      if (persist) {{
        localStorage.setItem('arcanum_crt_fx', isEnabled.toString());
      }}
      const toggle = document.getElementById('arcanumCrtToggle');
      if (toggle) toggle.checked = isEnabled;
    }},

    toggleModal() {{
      const modal = document.getElementById('arcanumThemeModal');
      if (!modal) return;
      modal.classList.toggle('active');
      if (modal.classList.contains('active')) {{
        this.syncModalControls();
      }}
    }},

    closeModal() {{
      const modal = document.getElementById('arcanumThemeModal');
      if (modal) modal.classList.remove('active');
    }},

    switchTab(tabId) {{
      document.querySelectorAll('.arcanum-tab-btn').forEach(btn => {{
        btn.classList.toggle('active', btn.getAttribute('data-tab') === tabId);
      }});
      document.querySelectorAll('.arcanum-tab-content').forEach(content => {{
        content.classList.toggle('active', content.id === 'tab-' + tabId);
      }});
    }},

    syncModalControls() {{
      const currentTheme = localStorage.getItem('arcanum_theme_preset') || 'sovereign-dark';
      this.setTheme(currentTheme, false);

      const currentSound = audio.currentModel;
      document.querySelectorAll('.arcanum-sound-card').forEach(card => {{
        card.classList.toggle('active', card.getAttribute('data-sound-id') === currentSound);
      }});

      const volSlider = document.getElementById('arcanumVolSlider');
      if (volSlider) {{
        volSlider.value = Math.round(audio.volume * 100);
        const volVal = document.getElementById('arcanumVolVal');
        if (volVal) volVal.innerText = volSlider.value + '%';
      }}

      const muteBtn = document.getElementById('arcanumMuteBtn');
      if (muteBtn) {{
        muteBtn.innerText = audio.isMuted ? '🔇 Unmute' : '🔊 Mute';
      }}

      const crtToggle = document.getElementById('arcanumCrtToggle');
      if (crtToggle) {{
        crtToggle.checked = document.body.classList.contains('crt-effect');
      }}
    }},

    attachTypewriter(element) {{
      if (!element) return;
      element.addEventListener('keydown', (e) => {{
        audio.play(e.key);
      }});
    }},

    autoAttachTypewriter() {{
      const targets = document.querySelectorAll('textarea, input[type="text"], input[type="search"], input[type="number"], .typewriter-target, [contenteditable="true"]');
      targets.forEach(t => this.attachTypewriter(t));
    }}
  }};

  // Expose global controller
  window.ArcanumThemeEngine = ArcanumThemeEngine;
  window.ArcanumAudio = audio;

  // Auto initialize on DOM ready
  if (document.readyState === 'loading') {{
    document.addEventListener('DOMContentLoaded', () => ArcanumThemeEngine.init());
  }} else {{
    ArcanumThemeEngine.init();
  }}
}})();
"""


# ==============================================================================
# 5. CONTROL CENTER MODAL HTML GENERATOR
# ==============================================================================

def get_theme_control_center_html() -> str:
    """Generates the self-contained HTML markup for the Theme & Sound Control Center Modal and Trigger."""
    # Build Visual Preset Cards
    preset_cards = []
    for pid, pdata in VISUAL_PRESETS.items():
        swatches_html = "".join(
            f'<span class="arcanum-swatch-dot" style="background:{s};"></span>'
            for s in pdata.get("swatches", [])
        )
        card = f"""
        <div class="arcanum-preset-card" data-preset-id="{pid}" onclick="ArcanumThemeEngine.setTheme('{pid}')">
            <div class="arcanum-card-header">
                <div class="arcanum-card-title">{pdata.get('icon', '🎨')} {pdata.get('name', pid)}</div>
                <span style="font-size:0.7rem; color:var(--accent); text-transform:uppercase; font-weight:700;">{pdata.get('category', 'core')}</span>
            </div>
            <div class="arcanum-swatch-row">{swatches_html}</div>
            <div class="arcanum-card-desc">{pdata.get('description', '')}</div>
        </div>
        """
        preset_cards.append(card)

    # Build Sound Preset Cards
    sound_cards = []
    for sid, sdata in SOUND_PRESETS.items():
        card = f"""
        <div class="arcanum-sound-card" data-sound-id="{sid}" onclick="ArcanumAudio.setModel('{sid}'); ArcanumAudio.play('a'); ArcanumThemeEngine.syncModalControls();">
            <div class="arcanum-sound-title">{sdata.get('icon', '⌨️')} {sdata.get('name', sid)}</div>
            <div class="arcanum-sound-era">{sdata.get('era', 'Classic')}</div>
            <div class="arcanum-sound-desc">{sdata.get('description', '')}</div>
        </div>
        """
        sound_cards.append(card)

    return f"""
<!-- Ars Arcanum Theme & Sound Control Center Trigger -->
<button id="arcanumThemeLauncher" class="arcanum-theme-launcher-btn" onclick="ArcanumThemeEngine.toggleModal()" title="Theme & Sound Studio (Ctrl+Shift+T)">
    🎨 🎛️ <span>Theme &amp; Audio</span>
</button>

<!-- Ars Arcanum Theme & Sound Control Center Modal -->
<div id="arcanumThemeModal" class="arcanum-modal-overlay" onclick="if(event.target===this) ArcanumThemeEngine.closeModal()">
    <div class="arcanum-modal-dialog">
        <div class="arcanum-modal-header">
            <h2>🎨 🎛️ Theme &amp; Sound Control Center</h2>
            <button class="arcanum-modal-close-btn" onclick="ArcanumThemeEngine.closeModal()" title="Close">&times;</button>
        </div>

        <nav class="arcanum-modal-nav">
            <button class="arcanum-tab-btn active" data-tab="visuals" onclick="ArcanumThemeEngine.switchTab('visuals')">🎨 Visual Presets (11)</button>
            <button class="arcanum-tab-btn" data-tab="audio" onclick="ArcanumThemeEngine.switchTab('audio')">🔊 Typewriter Audio (10)</button>
        </nav>

        <div class="arcanum-modal-body">
            <!-- Tab 1: Visual Presets -->
            <div id="tab-visuals" class="arcanum-tab-content active">
                <div class="arcanum-preset-grid">
                    {"".join(preset_cards)}
                </div>
            </div>

            <!-- Tab 2: Typewriter Sound Engine -->
            <div id="tab-audio" class="arcanum-tab-content">
                <div class="arcanum-sound-controls">
                    <div class="arcanum-control-row">
                        <div style="display:flex; align-items:center; gap:0.75rem;">
                            <label style="font-weight:700; font-size:0.875rem;">Master Volume:</label>
                            <input type="range" id="arcanumVolSlider" min="0" max="100" value="75" style="accent-color:var(--accent); cursor:pointer;" oninput="ArcanumAudio.setVolume(this.value/100); document.getElementById('arcanumVolVal').innerText=this.value+'%';">
                            <span id="arcanumVolVal" style="font-weight:700; font-size:0.85rem; color:var(--accent); min-width:40px;">75%</span>
                        </div>
                        <div style="display:flex; gap:0.5rem; align-items:center;">
                            <button id="arcanumMuteBtn" class="arcanum-key-btn" onclick="ArcanumAudio.setMuted(!ArcanumAudio.isMuted); this.innerText=ArcanumAudio.isMuted?'🔇 Unmute':'🔊 Mute';">🔊 Mute</button>
                            <label style="display:flex; align-items:center; gap:0.4rem; font-size:0.85rem; font-weight:600; cursor:pointer;">
                                <input type="checkbox" id="arcanumCrtToggle" onchange="ArcanumThemeEngine.setCrtEffect(this.checked)" style="accent-color:var(--accent);">
                                📺 CRT Scanlines
                            </label>
                        </div>
                    </div>

                    <div style="margin-top:0.75rem;">
                        <span style="font-size:0.75rem; text-transform:uppercase; color:var(--text-muted); font-weight:700;">Acoustic Test Pads:</span>
                        <div class="arcanum-test-keys">
                            <button class="arcanum-key-btn" onclick="ArcanumAudio.play('a')">Key Strike (A)</button>
                            <button class="arcanum-key-btn" onclick="ArcanumAudio.play(' ')">Spacebar (Thud)</button>
                            <button class="arcanum-key-btn" onclick="ArcanumAudio.play('enter')">Enter (Bell 🔔)</button>
                            <button class="arcanum-key-btn" onclick="ArcanumAudio.play('backspace')">Backspace (Ratchet)</button>
                        </div>
                    </div>
                </div>

                <div class="arcanum-sound-grid">
                    {"".join(sound_cards)}
                </div>
            </div>
        </div>
    </div>
</div>
"""


__all__ = [
    "SOUND_PRESETS",
    "VISUAL_PRESETS",
    "get_theme_control_center_html",
    "get_theme_engine_css",
    "get_theme_engine_js",
]
