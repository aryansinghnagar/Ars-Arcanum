"""Strict Typed Authorial Constitution & 3-Tier Policy Cascade (Phase 2B Refactor).

Upgrades `scripts/lib/constitution.py` by replacing untyped `dict[str, Any]` payloads with
frozen `@dataclass` schemas and adding explicit `!rule_id` negation support so child
constitutions (World or Manuscript level) can disable inherited diagnostic rules.

Repository Target: `scripts/lib/typed_constitution.py`
"""

from __future__ import annotations

import argparse
from collections.abc import Iterable
from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
import sys
from typing import Any

try:
    from lib.vault_index import parse_frontmatter
except ImportError:
    from vault_index import parse_frontmatter


@dataclass(frozen=True)
class CraftPolicyThresholds:
    """Quantitative thresholds for Subsystem 2 advisory diagnostics."""

    max_chapter_words: int = 6_500
    min_chapter_words: int = 1_200
    max_pov_drought_words: int = 25_000
    high_churn_ratio_threshold: float = 0.50
    min_scrap_extraction_words: int = 50


@dataclass(frozen=True)
class AuthorialConstitution:
    """Strictly typed representation of a resolved 3-tier Authorial Constitution."""

    scope_name: str
    sovereign_offline_only: bool = True
    allow_generative_ai: bool = False
    active_rules: frozenset[str] = field(
        default_factory=lambda: frozenset(
            {
                "REV-101",
                "REV-102",
                "REV-103",
                "REV-104",
                "EPI-201",
                "TIME-301",
                "CON-401",
                "LED-501",
            }
        )
    )
    banned_idioms: tuple[str, ...] = ()
    canonical_stages: tuple[str, ...] = (
        "Concept",
        "Pre-Draft Outline",
        "Drafting",
        "Pre-Revision Outline",
        "Revision",
        "Beta Review",
        "Proofing",
        "Querying",
        "Publishing",
    )
    thresholds: CraftPolicyThresholds = field(default_factory=CraftPolicyThresholds)

    def is_rule_enabled(self, rule_id: str) -> bool:
        """Return True if `rule_id` is active after resolving all `!RULE` negations."""
        return rule_id in self.active_rules

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["active_rules"] = sorted(self.active_rules)
        return payload


def merge_rule_lists_with_negation(
    base_rules: Iterable[str] | frozenset[str],
    override_directives: list[str] | tuple[str, ...],
) -> frozenset[str]:
    """Merge rule lists across constitution tiers while honoring `!RULE_ID` removal directives."""
    resolved = set(base_rules)
    for raw_item in override_directives:
        token = str(raw_item).strip()
        if not token:
            continue
        if token.startswith("!"):
            target = token[1:].strip()
            if target == "*":
                resolved.clear()
            else:
                resolved.discard(target)
        else:
            resolved.add(token)
    return frozenset(resolved)


def resolve_constitution_cascade(
    *,
    global_dict: dict[str, Any] | None = None,
    world_dict: dict[str, Any] | None = None,
    manuscript_dict: dict[str, Any] | None = None,
) -> AuthorialConstitution:
    """Resolve the 3-tier policy cascade (Global -> World -> Manuscript) into an `AuthorialConstitution`."""
    base = AuthorialConstitution(scope_name="Global")
    active_rules = set(base.active_rules)
    banned_idioms = set(base.banned_idioms)
    thresh_dict = asdict(base.thresholds)
    scope_name = base.scope_name
    sovereign_offline = base.sovereign_offline_only
    allow_ai = base.allow_generative_ai

    for tier_name, layer in (
        ("Global", global_dict),
        ("World", world_dict),
        ("Manuscript", manuscript_dict),
    ):
        if not layer:
            continue
        if layer.get("scope_name"):
            scope_name = str(layer["scope_name"])
        elif scope_name == base.scope_name:
            scope_name = tier_name
        if "sovereign_offline_only" in layer:
            sovereign_offline = bool(layer["sovereign_offline_only"])
        if "allow_generative_ai" in layer:
            allow_ai = bool(layer["allow_generative_ai"])

        if "rules" in layer and isinstance(layer["rules"], (list, tuple)):
            active_rules = set(
                merge_rule_lists_with_negation(active_rules, [str(x) for x in layer["rules"]])
            )
        if "banned_idioms" in layer and isinstance(layer["banned_idioms"], (list, tuple)):
            banned_idioms = set(
                merge_rule_lists_with_negation(banned_idioms, [str(x) for x in layer["banned_idioms"]])
            )
        if "thresholds" in layer and isinstance(layer["thresholds"], dict):
            for k, v in layer["thresholds"].items():
                if k in thresh_dict:
                    thresh_dict[k] = type(thresh_dict[k])(v)

    thresholds = CraftPolicyThresholds(
        max_chapter_words=int(thresh_dict["max_chapter_words"]),
        min_chapter_words=int(thresh_dict["min_chapter_words"]),
        max_pov_drought_words=int(thresh_dict["max_pov_drought_words"]),
        high_churn_ratio_threshold=float(thresh_dict["high_churn_ratio_threshold"]),
        min_scrap_extraction_words=int(thresh_dict["min_scrap_extraction_words"]),
    )

    return AuthorialConstitution(
        scope_name=scope_name,
        sovereign_offline_only=sovereign_offline,
        allow_generative_ai=allow_ai,
        active_rules=frozenset(active_rules),
        banned_idioms=tuple(sorted(banned_idioms)),
        thresholds=thresholds,
    )


def load_yaml_constitution_file(path: Path) -> dict[str, Any]:
    """Load a `constitution.yaml` file using the zero-dependency frontmatter parser."""
    if not path.exists():
        return {}
    raw = path.read_text(encoding="utf-8")
    wrapped = raw if raw.lstrip().startswith("---") else f"---\n{raw}\n---\n"
    parsed, _ = parse_frontmatter(wrapped)
    return parsed


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for `arcanum typed-constitution`."""
    parser = argparse.ArgumentParser(
        prog="arcanum typed-constitution",
        description="Resolve and inspect the 3-tier Authorial Constitution cascade.",
    )
    parser.add_argument("--global-config", type=Path, default=None, help="Global constitution.yaml path")
    parser.add_argument("--world-config", type=Path, default=None, help="World constitution.yaml path")
    parser.add_argument("--manuscript-config", type=Path, default=None, help="Manuscript constitution.yaml path")
    args = parser.parse_args(argv)

    g_dict = load_yaml_constitution_file(args.global_config) if args.global_config else None
    w_dict = load_yaml_constitution_file(args.world_config) if args.world_config else None
    m_dict = load_yaml_constitution_file(args.manuscript_config) if args.manuscript_config else None

    resolved = resolve_constitution_cascade(
        global_dict=g_dict,
        world_dict=w_dict,
        manuscript_dict=m_dict,
    )
    sys.stdout.write(json.dumps(resolved.to_dict(), indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
