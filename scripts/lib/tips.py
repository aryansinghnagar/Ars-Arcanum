#!/usr/bin/env python3
"""
Ars Arcanum Dynamic Intelligent Tip Engine & Metadata Database (scripts/lib/tips.py)
====================================================================================
Sovereign, offline, intelligent craft & technical tip retrieval system. Provides
curated, non-obvious, actionable craft wisdom, scientific principles, mathematical
insights, workflow synergies, and technical mastery hints across all registered
engines and subfeatures in the Ars Arcanum operating system.

Non-intrusive display rails:
- Displays context-sensitive tips matching active engine, feature, subfeature,
  or creative activity (drafting, worldbuilding, revision, publishing, review).
- Prioritizes non-obvious masterclass depth over trivial or obvious advice.
- Intelligent ranking, tag matching, and non-repeating cycle history.
- Full user sovereignty: persistable enable/disable toggle via configuration, CLI,
  and GUI surfaces.
"""

from __future__ import annotations

import argparse
import difflib
import json
import logging
import random
import sys
import unicodedata
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any

try:
    import lib._bootstrap  # noqa: F401
    from lib.config import load_config, save_config
    from lib.tips_catalog import ALL_RAW_TIPS, ENGINE_ALIASES
except ImportError:
    import _bootstrap  # noqa: F401
    from config import load_config, save_config
    from tips_catalog import ALL_RAW_TIPS, ENGINE_ALIASES

logger = logging.getLogger("arcanum.tips")

# Canonical raw tips dataset re-exported for backwards compatibility
_RAW_TIPS: list[dict[str, Any]] = ALL_RAW_TIPS


class TipCategory(str, Enum):
    CRAFT = "craft"
    CORE = "core"
    UTILITY = "utility"


class TipPillar(str, Enum):
    COSMOLOGY_PHYSICS = "cosmology_physics"
    SOCIETY_SYSTEMS = "society_systems"
    NARRATIVE_CHRONOLOGY = "narrative_chronology"
    EDITORIAL_CRAFT = "editorial_craft"
    MANUSCRIPT_DRAFTING = "manuscript_drafting"
    SYSTEM_OPS = "system_ops"


class TipDepth(str, Enum):
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    MASTERCLASS = "masterclass"


@dataclass
class Tip:
    """Metadata-rich craft and technical tip specification."""

    id: str
    engine: str
    feature: str
    subfeature: str
    category: TipCategory
    pillar: TipPillar
    title: str
    content: str
    rationale: str
    example: str = ""
    tags: list[str] = field(default_factory=list)
    contexts: list[str] = field(default_factory=list)
    depth: TipDepth = TipDepth.ADVANCED
    weight: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        """Serializes tip to a plain dictionary."""
        d = asdict(self)
        d["category"] = self.category.value
        d["pillar"] = self.pillar.value
        d["depth"] = self.depth.value
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Tip:
        """Deserializes tip from dictionary."""
        return cls(
            id=data["id"],
            engine=data["engine"],
            feature=data.get("feature", data["engine"]),
            subfeature=data.get("subfeature", "general"),
            category=TipCategory(data.get("category", "craft")),
            pillar=TipPillar(data.get("pillar", "editorial_craft")),
            title=data["title"],
            content=data["content"],
            rationale=data.get("rationale", ""),
            example=data.get("example", ""),
            tags=list(data.get("tags", [])),
            contexts=list(data.get("contexts", ["cli", "studio"])),
            depth=TipDepth(data.get("depth", "advanced")),
            weight=float(data.get("weight", 1.0)),
        )


def _norm_str(s: str) -> str:
    n = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in n if c.isalnum())


def _toks_str(s: str) -> set[str]:
    n = unicodedata.normalize("NFD", s.lower())
    clean = "".join(c if c.isalnum() else " " for c in n)
    return {w for w in clean.split() if len(w) > 2}


# =============================================================================
# TIP DATABASE & RETRIEVAL ENGINE CLASS
# =============================================================================


class TipDatabase:
    """Intelligent retrieval and ranking engine for Ars Arcanum craft tips."""

    def __init__(self, raw_tips: list[dict[str, Any]] | None = None) -> None:
        raw = raw_tips if raw_tips is not None else _RAW_TIPS
        self._tips: list[Tip] = [Tip.from_dict(t) for t in raw]
        self._by_id: dict[str, Tip] = {t.id: t for t in self._tips}
        self._by_engine: dict[str, list[Tip]] = {}
        self._by_category: dict[str, list[Tip]] = {}
        self._by_pillar: dict[str, list[Tip]] = {}
        self._by_context: dict[str, list[Tip]] = {}

        for t in self._tips:
            eng = t.engine.lower().strip()
            self._by_engine.setdefault(eng, []).append(t)
            cat = t.category.value
            self._by_category.setdefault(cat, []).append(t)
            pil = t.pillar.value
            self._by_pillar.setdefault(pil, []).append(t)
            for ctx in t.contexts:
                self._by_context.setdefault(ctx.lower().strip(), []).append(t)

        self._history_seen: set[str] = set()

    def __len__(self) -> int:
        return len(self._tips)

    def resolve_engine(self, name_or_alias: str) -> str | None:
        """Resolves an engine name, alias, or command string to canonical engine name."""
        if not name_or_alias:
            return None
        clean = name_or_alias.lower().strip().replace(" ", "-").replace("_", "-")
        if clean in self._by_engine:
            return clean
        clean_under = clean.replace("-", "_")
        if clean_under in self._by_engine:
            return clean_under
        if clean in ENGINE_ALIASES:
            return ENGINE_ALIASES[clean]
        if clean_under in ENGINE_ALIASES:
            return ENGINE_ALIASES[clean_under]
        # Check close matches
        all_canonical = list(self._by_engine.keys())
        matches = difflib.get_close_matches(clean, all_canonical, n=1, cutoff=0.6)
        if matches:
            return matches[0]
        alias_matches = difflib.get_close_matches(clean, list(ENGINE_ALIASES.keys()), n=1, cutoff=0.6)
        if alias_matches:
            return ENGINE_ALIASES[alias_matches[0]]
        return None

    def get_all(self) -> list[Tip]:
        """Returns all registered tips."""
        return list(self._tips)

    def get_by_id(self, tip_id: str) -> Tip | None:
        """Looks up a tip by exact unique ID."""
        return self._by_id.get(tip_id.strip())

    def get_by_engine(self, engine: str, subfeature: str | None = None) -> list[Tip]:
        """Returns all tips associated with an engine, optionally filtered by subfeature."""
        canonical = self.resolve_engine(engine)
        clean_eng = canonical if canonical else engine.lower().strip()
        tips = self._by_engine.get(clean_eng, [])
        if not tips:
            for k, v in self._by_engine.items():
                if clean_eng in k or k in clean_eng:
                    tips = v
                    break

        if not tips:
            return []

        if not subfeature or not subfeature.strip():
            return list(tips)

        # Multi-criteria subfeature relevance scoring
        q_norm = _norm_str(subfeature)
        q_toks = _toks_str(subfeature)
        scored: list[tuple[float, Tip]] = []

        for t in tips:
            score = 0.0
            t_sub_norm = _norm_str(t.subfeature)
            t_feat_norm = _norm_str(t.feature)
            t_title_norm = _norm_str(t.title)

            if q_norm == t_sub_norm:
                score += 50.0
            elif q_norm == t_feat_norm:
                score += 40.0
            elif q_norm and (q_norm in t_sub_norm or t_sub_norm in q_norm):
                score += 30.0
            elif q_norm and (q_norm in t_feat_norm or t_feat_norm in q_norm):
                score += 25.0

            for tag in t.tags:
                tag_norm = _norm_str(tag)
                if tag_norm == q_norm:
                    score += 35.0
                elif tag_norm and (tag_norm in q_norm or q_norm in tag_norm):
                    score += 20.0

            searchable_toks = _toks_str(f"{t.subfeature} {t.feature} {t.title} {' '.join(t.tags)}")
            overlap = len(q_toks & searchable_toks)
            score += overlap * 6.0

            if q_norm and q_norm in t_title_norm:
                score += 15.0

            if score > 0.0:
                scored.append((score * t.weight, t))

        if scored:
            scored.sort(key=lambda x: x[0], reverse=True)
            top_score = scored[0][0]
            if top_score >= 30.0:
                return [t for s, t in scored if s >= 0.5 * top_score]
            return [t for _, t in scored]

        return list(tips)

    def get_by_context(self, context: str) -> list[Tip]:
        """Returns tips relevant to a workflow context (e.g. drafting, worldbuilding, review)."""
        clean_ctx = context.lower().strip()
        return list(self._by_context.get(clean_ctx, []))

    def search(self, query: str, limit: int = 10) -> list[Tip]:
        """Searches tips across title, content, rationale, tags, and subfeature names."""
        if not query or not query.strip():
            return self._tips[:limit]

        terms = [t.lower() for t in query.strip().split() if len(t) > 1]
        if not terms:
            terms = [query.lower().strip()]

        scored: list[tuple[float, Tip]] = []
        for t in self._tips:
            score = 0.0
            searchable_text = f"{t.title} {t.content} {t.rationale} {t.engine} {t.feature} {t.subfeature} {' '.join(t.tags)}".lower()

            # Exact phrase bonus
            if query.lower() in searchable_text:
                score += 12.0

            # Individual term matches
            for term in terms:
                if term in t.title.lower():
                    score += 5.0
                if term in t.tags:
                    score += 4.0
                if term in t.engine.lower():
                    score += 4.0
                if term in t.subfeature.lower():
                    score += 3.0
                if term in t.content.lower():
                    score += 2.0
                if term in t.rationale.lower():
                    score += 1.0

            if score > 0.0:
                scored.append((score * t.weight, t))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [t for _, t in scored[:limit]]

    def get_contextual_tip(
        self,
        engine: str | None = None,
        feature: str | None = None,
        subfeature: str | None = None,
        context: str | None = None,
        query: str | None = None,
        exclude_seen: bool = True,
    ) -> Tip | None:
        """Intelligently retrieves the best-matching, non-obvious tip for current user context."""
        candidates: list[Tip] = []

        # 1. Targeted engine + subfeature query
        if engine:
            candidates = self.get_by_engine(engine, subfeature or feature)

        # 2. Query search if engine didn't yield exact match or freeform query given
        if not candidates and query:
            candidates = self.search(query, limit=15)

        # 3. Contextual fallback (e.g. drafting, worldbuilding)
        if not candidates and context:
            candidates = self.get_by_context(context)

        # 4. Universal fallback
        if not candidates:
            candidates = list(self._tips)

        # Filter out seen if requested and we have un-seen remaining
        if exclude_seen and len(candidates) > 1:
            unseen = [t for t in candidates if t.id not in self._history_seen]
            if unseen:
                candidates = unseen
            else:
                # Reset history for this set if exhausted
                candidate_ids = {t.id for t in candidates}
                self._history_seen.difference_update(candidate_ids)

        if not candidates:
            return None

        # Weighted selection among top candidates
        weights = [t.weight for t in candidates]
        chosen = random.choices(candidates, weights=weights, k=1)[0]
        self._history_seen.add(chosen.id)
        return chosen

    def get_engines(self) -> list[str]:
        """Returns sorted list of all unique engines represented in tips database."""
        return sorted(self._by_engine.keys())

    def get_categories(self) -> list[str]:
        """Returns list of unique categories."""
        return [c.value for c in TipCategory]

    def get_pillars(self) -> list[str]:
        """Returns list of unique pillars."""
        return [p.value for p in TipPillar]


# Global default database instance
_GLOBAL_DB: TipDatabase | None = None


def get_tip_database() -> TipDatabase:
    """Returns the global shared TipDatabase singleton instance."""
    global _GLOBAL_DB
    if _GLOBAL_DB is None:
        _GLOBAL_DB = TipDatabase()
    return _GLOBAL_DB


# =============================================================================
# USER PREFERENCE & CONFIGURATION INTEGRATION
# =============================================================================


def are_tips_enabled() -> bool:
    """Checks if dynamic tips are enabled in user configuration (default: True)."""
    try:
        cfg = load_config()
        return bool(cfg.get("tips_enabled", True))
    except Exception as e:
        logger.debug("Failed reading tips_enabled config: %s", e)
        return True


def set_tips_enabled(enabled: bool) -> bool:
    """Persists user tips preference to configuration (~/.config/ars-arcanum/config.json)."""
    try:
        cfg = load_config()
        cfg["tips_enabled"] = bool(enabled)
        return save_config(cfg)
    except Exception as e:
        logger.error("Failed saving tips_enabled config: %s", e)
        return False


def toggle_tips() -> bool:
    """Toggles dynamic tips enabled state and returns the new state."""
    new_state = not are_tips_enabled()
    set_tips_enabled(new_state)
    return new_state


# =============================================================================
# FORMATTING & PRESENTATION HELPERS
# =============================================================================


def format_cli_tip(tip: Tip, verbose: bool = False) -> str:
    """Formats a tip cleanly for command-line presentation."""
    border = "─" * 78
    lines = [
        border,
        f"💡 \033[1;33mARS ARCANUM CRAFT WISDOM\033[0m: \033[1m{tip.title}\033[0m",
        f"   [\033[36m{tip.engine.upper()}\033[0m • \033[35m{tip.subfeature}\033[0m • \033[32m{tip.depth.value.capitalize()}\033[0m]",
        "",
        f"   {tip.content}",
    ]
    if verbose and tip.rationale:
        lines.append(f"\n   ⚙️  \033[2mRationale:\033[0m {tip.rationale}")
    if tip.example:
        lines.append(f"\n   ⚡ \033[2mExample:\033[0m {tip.example}")
    lines.append(border)
    return "\n".join(lines)


def format_short_tip(tip: Tip) -> str:
    """Formats a 1-line compact tip for statusbars and minimal footers."""
    return f"💡 [{tip.engine.upper()} / {tip.subfeature}]: {tip.title} — {tip.content}"


# =============================================================================
# CLI DISPATCHER & MAIN ENTRYPOINT
# =============================================================================


def main(argv: list[str] | None = None) -> int:
    """CLI handler for 'arcanum tip' and standalone tips management."""
    parser = argparse.ArgumentParser(
        description="Ars Arcanum Dynamic Craft Tip & Wisdom Engine"
    )
    parser.add_argument(
        "query_pos",
        nargs="?",
        default="",
        help="Optional search query or engine name",
    )
    parser.add_argument(
        "--engine",
        "-e",
        help="Target engine name (e.g. astrophysics, climate, pacing, conlang)",
    )
    parser.add_argument(
        "--feature",
        "-f",
        help="Specific subfeature or capability",
    )
    parser.add_argument(
        "--context",
        "-c",
        help="Workflow context (drafting, worldbuilding, review, publishing, export)",
    )
    parser.add_argument(
        "--query",
        "-q",
        help="Search query across tip database",
    )
    parser.add_argument(
        "--all",
        "-a",
        action="store_true",
        help="List all tips matching filters",
    )
    parser.add_argument(
        "--json",
        "-j",
        action="store_true",
        help="Output raw JSON format",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed scientific/structural rationale",
    )
    parser.add_argument(
        "--enable",
        action="store_true",
        help="Enable dynamic tip display in user configuration",
    )
    parser.add_argument(
        "--disable",
        action="store_true",
        help="Disable dynamic tip display in user configuration",
    )
    parser.add_argument(
        "--toggle",
        action="store_true",
        help="Toggle dynamic tip display enabled state",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show whether tips are enabled in config",
    )
    parser.add_argument(
        "--list-engines",
        action="store_true",
        help="List all engines with registered tips",
    )

    args = parser.parse_args(argv)
    db = get_tip_database()

    # Preference modification subcommands
    if args.enable:
        set_tips_enabled(True)
        print("✓ Dynamic tips enabled in configuration (~/.config/ars-arcanum/config.json).")
        return 0

    if args.disable:
        set_tips_enabled(False)
        print("✓ Dynamic tips disabled in configuration (~/.config/ars-arcanum/config.json).")
        return 0

    if args.toggle:
        state = toggle_tips()
        print(f"✓ Dynamic tips are now {'ENABLED' if state else 'DISABLED'}.")
        return 0

    if args.status:
        state = are_tips_enabled()
        print(f"Dynamic tips: {'ENABLED' if state else 'DISABLED'} (Total Tips in DB: {len(db)})")
        return 0

    if args.list_engines:
        engines = db.get_engines()
        print(f"Ars Arcanum Tip Engine Coverage ({len(engines)} engines, {len(db)} total tips):\n")
        for eng in engines:
            tips = db.get_by_engine(eng)
            print(f"  • {eng:<22} ({len(tips)} tips)")
        return 0

    # Determine query / engine
    engine_name = args.engine
    query_text = args.query or args.query_pos

    if not engine_name and query_text:
        # Check if query matches an engine name or alias
        resolved = db.resolve_engine(query_text)
        if resolved:
            engine_name = resolved
            query_text = ""

    if args.all:
        if engine_name:
            results = db.get_by_engine(engine_name, args.feature)
        elif query_text:
            results = db.search(query_text, limit=100)
        elif args.context:
            results = db.get_by_context(args.context)
        else:
            results = db.get_all()

        if args.json:
            print(json.dumps([t.to_dict() for t in results], indent=2))
            return 0

        print(f"=== Ars Arcanum Craft Wisdom ({len(results)} matching tips) ===\n")
        for t in results:
            print(format_cli_tip(t, verbose=args.verbose))
            print()
        return 0

    # Single tip retrieval
    tip = db.get_contextual_tip(
        engine=engine_name,
        feature=args.feature,
        context=args.context,
        query=query_text,
    )

    if not tip:
        if args.json:
            print(json.dumps({"error": "No matching tip found."}))
        else:
            print("No matching craft tip found. Run 'arcanum tip --all' to browse tips.", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(tip.to_dict(), indent=2))
    else:
        print(format_cli_tip(tip, verbose=args.verbose))

    return 0


if __name__ == "__main__":
    sys.exit(main())
