#!/usr/bin/env python3
"""
Ars Arcanum Economy Data & Technology Era Dictionaries
(scripts/lib/economy_data.py)
================================================================================
Foundational technological eras, distinguishing inventions/materials dictionary,
and text normalization primitives.
"""

from __future__ import annotations

import re

# Technological Eras in chronological sequence
TECH_ERAS: list[str] = [
    "stone_age",
    "bronze_age",
    "iron_age",
    "medieval",
    "renaissance",
    "industrial",
    "victorian",
    "modern_20th",
    "information_age",
    "interstellar",
]

ERA_ORDER: dict[str, int] = {era: idx for idx, era in enumerate(TECH_ERAS)}

# Anachronism dictionary: term -> earliest acceptable era
TECH_ERA_DICTIONARY: dict[str, str] = {
    # Bronze Age+ (Earliest Bronze Age)
    "bronze": "bronze_age",
    "chariot": "bronze_age",
    "papyrus": "bronze_age",
    "cuneiform": "bronze_age",

    # Iron Age+
    "iron sword": "iron_age",
    "steel sword": "iron_age",
    "parchment": "iron_age",
    "phalanx": "iron_age",
    "trireme": "iron_age",
    "aqueduct": "iron_age",

    # Medieval+
    "crossbow": "medieval",
    "chainmail": "medieval",
    "plate armor": "medieval",
    "trebuchet": "medieval",
    "windmill": "medieval",
    "feudal": "medieval",

    # Renaissance+
    "gunpowder": "renaissance",
    "musket": "renaissance",
    "arquebus": "renaissance",
    "cannon": "renaissance",
    "printing press": "renaissance",
    "telescope": "renaissance",
    "caravel": "renaissance",
    "galleon": "renaissance",
    "flintlock": "renaissance",

    # Industrial+
    "steam engine": "industrial",
    "locomotive": "industrial",
    "railroad": "industrial",
    "telegraph": "industrial",
    "dynamite": "industrial",
    "factory line": "industrial",
    "rifled barrel": "industrial",

    # Victorian / Early 20th+
    "electricity": "victorian",
    "lightbulb": "victorian",
    "phonograph": "victorian",
    "automobile": "victorian",
    "internal combustion": "victorian",
    "airship": "victorian",
    "zeppelin": "victorian",
    "zepplin": "victorian",
    "radio": "victorian",
    "telephone": "victorian",

    # Modern 20th+
    "radar": "modern_20th",
    "sonar": "modern_20th",
    "plastic": "modern_20th",
    "nylon": "modern_20th",
    "penicillin": "modern_20th",
    "antibiotic": "modern_20th",
    "jet aircraft": "modern_20th",
    "transistor": "modern_20th",
    "nuclear reactor": "modern_20th",
    "atomic bomb": "modern_20th",
    "satellite": "modern_20th",

    # Information Age+
    "microchip": "information_age",
    "silicon chip": "information_age",
    "internet": "information_age",
    "smartphone": "information_age",
    "gps": "information_age",
    "fiber optic": "information_age",
    "lithium battery": "information_age",

    # Interstellar / Far Future+
    "fusion drive": "interstellar",
    "warp drive": "interstellar",
    "hyperdrive": "interstellar",
    "antimatter": "interstellar",
    "blaster": "interstellar",
    "plasma cannon": "interstellar",
    "cybernetic implant": "interstellar",
    "forcefield": "interstellar",
}


def normalize_name(name: str) -> str:
    """Normalizes whitespace and casing for identifier and entity comparison."""
    return re.sub(r"[\s_-]+", " ", str(name).strip().lower())


# Temporal, idiomatic, and pronoun non-commodity exclusions for prose price parsing
TEMPORAL_PREPOSITION_EXCLUSIONS: set[str] = {
    "moment", "moments", "second", "seconds", "minute", "minutes", "hour", "hours",
    "day", "days", "week", "weeks", "month", "months", "year", "years", "decade", "decades",
    "century", "centuries", "while", "instant", "breath", "heartbeat", "heartbeats",
    "time", "times", "eternity", "period", "spell", "stretch", "season", "seasons",
    "night", "nights", "morning", "mornings", "afternoon", "evening",
    "long", "good", "certain", "sure", "life", "ever", "now", "then", "once", "nothing", "free",
    "example", "instance", "each", "everyone", "someone", "anyone", "all", "us", "them", "him", "her", "me", "you",
}


__all__ = [
    "ERA_ORDER",
    "TECH_ERAS",
    "TECH_ERA_DICTIONARY",
    "TEMPORAL_PREPOSITION_EXCLUSIONS",
    "normalize_name",
]

