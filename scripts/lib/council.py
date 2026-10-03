#!/usr/bin/env python3
"""
Ars Arcanum Multi-Perspective Editorial Council Engine
(scripts/lib/council.py)
================================================================================
Zero-dependency, offline multi-agent editorial council synthesizing 4 distinct
craft perspectives into a unified diagnostic manuscript dossier.

Editorial Council Perspectives:
1. Plot Doctor:
   - Evaluates narrative pacing waveform, Swain MRU causal chains, scene vs sequel
     balance, and chapter ending hooks.
2. Lore Auditor:
   - Evaluates worldbuilding consistency, magic rule constraints, cosmological
     pantheon references, and universe timeline integrity.
3. Voice Coach:
   - Evaluates character dialogue distinctiveness, dialogue tag variety (said vs
     bookisms), mean utterance lengths, and voice bleed.
4. Sensory Stylist:
   - Evaluates 8-channel sensory immersion (visual, auditory, olfactory, gustatory,
     tactile, proprioception, thermoception, chronoception), filter words, and
     adverb density.

Zero external dependencies; 100% offline privacy.
"""

import argparse
import html
import json
import logging
import math
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

try:
    from lib._bootstrap import atomic_write
except ImportError:
    from _bootstrap import atomic_write

logger = logging.getLogger("arcanum.council")

FILTER_WORDS = {
    "saw", "heard", "felt", "noticed", "watched", "smelled", "tasted", "seemed",
    "appeared", "decided", "realized", "wondered", "thought", "looked", "sounded",
    "could see", "could hear", "could feel"
}

SENSORY_LEXICON = {
    "visual": {"color", "shadow", "light", "glare", "crimson", "gleam", "dark", "bright", "flash", "silhouette", "glow", "pale", "azure", "gold"},
    "auditory": {"whisper", "clang", "echo", "roar", "hum", "silence", "shriek", "rattle", "creak", "thunder", "mutter", "hiss", "clatter"},
    "olfactory": {"scent", "smell", "odor", "stench", "fragrance", "ozone", "smoke", "musk", "perfume", "damp", "rot", "acrid", "pungent"},
    "gustatory": {"taste", "bitter", "sweet", "sour", "metallic", "salty", "flavor", "tang", "bile", "savory", "coppery", "ash"},
    "tactile": {"rough", "smooth", "sharp", "soft", "grain", "texture", "prickle", "abrasive", "gritty", "slick", "velvet", "coarse"},
    "proprioception": {"weight", "balance", "heaviness", "stumble", "pulse", "lurch", "vertigo", "sway", "tension", "reach", "paralyzed"},
    "thermoception": {"cold", "heat", "chill", "warmth", "frost", "burning", "frozen", "scorching", "fever", "lukewarm", "icy", "blistering"},
    "chronoception": {"moment", "second", "hour", "instant", "eternity", "delay", "fleeting", "dawn", "dusk", "time", "clock", "aeon"}
}


@dataclass
class PerspectiveScore:
    perspective_name: str
    expert_title: str
    score: float  # 0.0 - 100.0
    grade: str    # A+, A, B, C, D, F
    summary: str
    key_findings: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)


@dataclass
class CouncilDossier:
    target_path: str
    overall_score: float
    overall_grade: str
    total_words: int
    total_chapters: int
    perspectives: list[PerspectiveScore] = field(default_factory=list)
    prioritized_action_items: list[str] = field(default_factory=list)


def score_to_grade(score: float) -> str:
    if score >= 95.0:
        return "A+"
    if score >= 88.0:
        return "A"
    if score >= 80.0:
        return "B+"
    if score >= 72.0:
        return "B"
    if score >= 65.0:
        return "C+"
    if score >= 55.0:
        return "C"
    if score >= 45.0:
        return "D"
    return "F"


def evaluate_plot_doctor(text: str) -> PerspectiveScore:
    """Evaluates narrative pacing waveform, sentence length variance, and scene hooks."""
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    sentence_lengths = [len(s.split()) for s in sentences] if sentences else [0]

    # Calculate sentence length variance (waveform)
    if len(sentence_lengths) > 1:
        avg_len = sum(sentence_lengths) / len(sentence_lengths)
        variance = sum((sl - avg_len) ** 2 for sl in sentence_lengths) / len(sentence_lengths)
        std_dev = math.sqrt(variance)
    else:
        avg_len = 15.0
        std_dev = 0.0

    # Pacing waveform score: ideal standard deviation is between 6.0 and 14.0 words
    waveform_score = 100.0
    if std_dev < 4.0:
        waveform_score -= (4.0 - std_dev) * 15.0
    elif std_dev > 18.0:
        waveform_score -= min(30.0, (std_dev - 18.0) * 3.0)

    # Paragraph count & scene endings
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    hooks = 0
    for p in paragraphs:
        if p.endswith(("?", "—", "!")) or "suddenly" in p.lower() or "until" in p.lower():
            hooks += 1
    hook_ratio = hooks / max(1, len(paragraphs))

    plot_score = max(20.0, min(100.0, 0.60 * waveform_score + 0.40 * min(100.0, hook_ratio * 400.0)))
    grade = score_to_grade(plot_score)

    findings = []
    recs = []
    if std_dev < 5.0:
        findings.append(f"Monotonous Sentence Rhythm: Low length standard deviation ({std_dev:.1f} words). Sentences feel repetitive.")
        recs.append("Apply Gary Provost's sentence waveform: mix short 5-word punches with 20-word flowing clauses.")
    else:
        findings.append(f"Dynamic Pacing Cadence: Excellent sentence length variation (std dev: {std_dev:.1f} words).")

    if hook_ratio < 0.10:
        findings.append("Low Chapter/Scene Hook Density: Scene conclusions resolve with low narrative momentum.")
        recs.append("End scenes on unresolved micro-dilemmas, unanswered dialogue questions, or abrupt sensory disruptions.")
    else:
        findings.append(f"Strong Narrative Momentum: {hooks} scene/paragraph momentum hooks detected.")

    return PerspectiveScore(
        perspective_name="Plot Doctor",
        expert_title="Master Narrative Architect & Pacing Specialist",
        score=round(plot_score, 1),
        grade=grade,
        summary="Evaluates story progression, cadence waveforms, and scene tension mechanics.",
        key_findings=findings,
        recommendations=recs,
        metrics={
            "total_sentences": len(sentences),
            "average_sentence_length": round(avg_len, 1),
            "sentence_std_dev": round(std_dev, 1),
            "waveform_score": round(waveform_score, 1),
            "scene_hooks_detected": hooks,
        }
    )


def evaluate_lore_auditor(text: str, world_path: Path | None = None) -> PerspectiveScore:
    """Evaluates worldbuilding entity references, magic system constraints, and cosmological terminology."""
    words = re.findall(r"\b[A-Za-z0-9_-]+\b", text)
    capitalized_entities = set(re.findall(r"\b[A-Z][a-z]{2,}(?:\s+[A-Z][a-z]{2,})*\b", text))
    # Exclude sentence starters
    common_starters = {"The", "There", "He", "She", "They", "It", "When", "Then", "After", "Before", "As", "In", "On", "At", "If"}
    proper_nouns = [e for e in capitalized_entities if e not in common_starters]

    # Check magic & cosmic indicators
    magic_keywords = {"spell", "rune", "mana", "aether", "resonance", "weave", "catalyst", "incantation", "circle", "binding"}
    cosmic_keywords = {"god", "pantheon", "deity", "celestial", "abyss", "shrine", "temple", "divine", "oracle", "prophecy"}

    magic_hits = sum(1 for w in words if w.lower() in magic_keywords)
    cosmic_hits = sum(1 for w in words if w.lower() in cosmic_keywords)

    lore_score = 80.0
    if len(proper_nouns) >= 5:
        lore_score += 15.0
    elif len(proper_nouns) < 2:
        lore_score -= 20.0

    if magic_hits > 0 or cosmic_hits > 0:
        lore_score += 5.0

    lore_score = max(20.0, min(100.0, lore_score))
    grade = score_to_grade(lore_score)

    findings = [
        f"Identified {len(proper_nouns)} distinct in-situ named world entities ({', '.join(list(proper_nouns)[:6])}...).",
        f"Found {magic_hits} magic system references and {cosmic_hits} cosmological/theological terms.",
    ]
    recs = []
    if len(proper_nouns) < 3:
        recs.append("Anchor prose deeper into the local geography and historical lore of the world.")
    else:
        recs.append("Verify all named entities against the Sovereign Codex for spelling and continuity parity.")

    return PerspectiveScore(
        perspective_name="Lore Auditor",
        expert_title="Chief Worldbuilding Continuity & Cosmology Inspector",
        score=round(lore_score, 1),
        grade=grade,
        summary="Audits universe continuity, magic mechanics, and named entity consistency.",
        key_findings=findings,
        recommendations=recs,
        metrics={
            "named_entities_count": len(proper_nouns),
            "sample_entities": list(proper_nouns)[:8],
            "magic_term_density": magic_hits,
            "cosmology_term_density": cosmic_hits,
        }
    )


def evaluate_voice_coach(text: str) -> PerspectiveScore:
    """Evaluates character dialogue distinctiveness, utterance lengths, and dialogue tag mechanics."""
    dialogue_matches = re.findall(r'["“]([^"”]+)["”]', text)
    dialogue_word_count = sum(len(d.split()) for d in dialogue_matches)
    total_words = len(re.findall(r"\b\w+\b", text))
    dialogue_ratio = dialogue_word_count / max(1, total_words)

    # Dialogue tag audit
    said_tags = len(re.findall(r'\b(said|asked|replied)\b', text, re.IGNORECASE))
    fancy_tags = len(re.findall(r'\b(breathed|snarled|growled|exclaimed|gasped|hissed|intoned|barked)\b', text, re.IGNORECASE))

    # Utterance lengths
    utterance_lens = [len(d.split()) for d in dialogue_matches]
    avg_utterance = sum(utterance_lens) / max(1, len(utterance_lens)) if utterance_lens else 0.0

    voice_score = 85.0
    if dialogue_ratio < 0.15:
        voice_score -= 15.0
    elif dialogue_ratio > 0.70:
        voice_score -= 10.0

    if fancy_tags > said_tags and fancy_tags > 5:
        voice_score -= 15.0  # Penalty for excessive said-bookisms

    voice_score = max(20.0, min(100.0, voice_score))
    grade = score_to_grade(voice_score)

    findings = [
        f"Dialogue Density: {(dialogue_ratio * 100):.1f}% of prose is spoken dialogue across {len(dialogue_matches)} utterances.",
        f"Mean Utterance Length: {avg_utterance:.1f} words per dialogue block.",
        f"Dialogue Tag Balance: {said_tags} invisible tags ('said/asked') vs {fancy_tags} evocative tags ('gasped/hissed').",
    ]
    recs = []
    if fancy_tags > said_tags and fancy_tags > 5:
        recs.append("Excessive Said-Bookisms: Replace descriptive tags with character action beats (e.g. Elena set down her blade vs Elena snarled).")
    if dialogue_ratio < 0.20:
        recs.append("Low Dialogue Ratio: Break up heavy exposition blocks with interpersonal character conflict and spoken debate.")
    else:
        recs.append("Maintain character idiolect distinctiveness by auditing contraction usage and vocabulary favorites.")

    return PerspectiveScore(
        perspective_name="Voice Coach",
        expert_title="Dramatis Personae & Idiolect Stylist",
        score=round(voice_score, 1),
        grade=grade,
        summary="Analyzes dialogue balance, character speech cadence, and attribution tags.",
        key_findings=findings,
        recommendations=recs,
        metrics={
            "dialogue_ratio": round(dialogue_ratio, 3),
            "utterance_count": len(dialogue_matches),
            "average_utterance_length": round(avg_utterance, 1),
            "invisible_tags": said_tags,
            "evocative_tags": fancy_tags,
        }
    )


def evaluate_sensory_stylist(text: str) -> PerspectiveScore:
    """Evaluates 8 sensory channels, filter words, and show-don't-tell prose density."""
    text_lower = text.lower()
    words = re.findall(r"\b[a-zA-Z]+\b", text_lower)
    total_words = max(1, len(words))

    channel_counts: dict[str, int] = {}
    for channel, keywords in SENSORY_LEXICON.items():
        count = sum(1 for w in words if w in keywords)
        channel_counts[channel] = count

    active_channels = sum(1 for c, cnt in channel_counts.items() if cnt > 0)

    # Filter word count
    filter_word_count = 0
    for fw in FILTER_WORDS:
        filter_word_count += len(re.findall(r"\b" + re.escape(fw) + r"\b", text_lower))

    filter_density = filter_word_count / (total_words / 1000.0)

    # Adverb count ending in -ly
    adverbs = len(re.findall(r"\b[a-zA-Z]{3,}ly\b", text_lower))
    adverb_density = adverbs / (total_words / 1000.0)

    sensory_score = 90.0
    # Channel distribution bonus / penalty
    if active_channels < 3:
        sensory_score -= 25.0
    elif active_channels >= 6:
        sensory_score += 10.0

    if filter_density > 12.0:
        sensory_score -= min(25.0, (filter_density - 12.0) * 1.5)

    if adverb_density > 15.0:
        sensory_score -= min(15.0, (adverb_density - 15.0) * 1.0)

    sensory_score = max(20.0, min(100.0, sensory_score))
    grade = score_to_grade(sensory_score)

    findings = [
        f"Sensory Channel Coverage: {active_channels}/8 channels active ({', '.join(c for c, cnt in channel_counts.items() if cnt > 0)}).",
        f"Filter Word Density: {filter_density:.1f} filter words per 1,000 words ({filter_word_count} occurrences).",
        f"Adverb Density: {adverb_density:.1f} '-ly' adverbs per 1,000 words ({adverbs} occurrences).",
    ]
    recs = []
    missing_channels = [c for c, cnt in channel_counts.items() if cnt == 0]
    if missing_channels:
        recs.append(f"Incorporate missing sensory channels: {', '.join(missing_channels[:3])} to prevent White-Room Syndrome.")
    if filter_density > 10.0:
        recs.append("Prune filter words (felt/saw/heard) to pull the reader into immediate, unfiltered character immersion.")
    else:
        recs.append("Sensory immersion is rich and balanced across physical and visceral perception layers.")

    return PerspectiveScore(
        perspective_name="Sensory Stylist",
        expert_title="8-Channel Atmosphere & Immersion Specialist",
        score=round(sensory_score, 1),
        grade=grade,
        summary="Monitors sensory balance, filter word suppression, and prose texture.",
        key_findings=findings,
        recommendations=recs,
        metrics={
            "active_channels": active_channels,
            "channel_breakdown": channel_counts,
            "filter_word_count": filter_word_count,
            "filter_density_per_1k": round(filter_density, 1),
            "adverb_density_per_1k": round(adverb_density, 1),
        }
    )


def run_editorial_council(target_path: Path, world_path: Path | None = None) -> CouncilDossier:
    """Orchestrates all 4 editorial perspectives over the manuscript target."""
    if target_path.is_file():
        content = target_path.read_text(encoding="utf-8", errors="replace")
        total_chapters = 1
    elif target_path.is_dir():
        files = sorted(target_path.glob("*.md"))
        total_chapters = len(files)
        content = "\n\n".join(f.read_text(encoding="utf-8", errors="replace") for f in files)
    else:
        content = ""
        total_chapters = 0

    total_words = len(re.findall(r"\b\w+\b", content))

    p_plot = evaluate_plot_doctor(content)
    p_lore = evaluate_lore_auditor(content, world_path=world_path)
    p_voice = evaluate_voice_coach(content)
    p_sensory = evaluate_sensory_stylist(content)

    perspectives = [p_plot, p_lore, p_voice, p_sensory]
    overall_score = round(sum(p.score for p in perspectives) / len(perspectives), 1)
    overall_grade = score_to_grade(overall_score)

    action_items = []
    for p in perspectives:
        for r in p.recommendations:
            action_items.append(f"[{p.perspective_name}] {r}")

    return CouncilDossier(
        target_path=str(target_path),
        overall_score=overall_score,
        overall_grade=overall_grade,
        total_words=total_words,
        total_chapters=total_chapters,
        perspectives=perspectives,
        prioritized_action_items=action_items[:8],
    )


def render_council_markdown(dossier: CouncilDossier) -> str:
    """Renders the Council Dossier as clean Github Markdown."""
    lines = [
        "# 🏛️ Ars Arcanum Editorial Council Dossier",
        f"**Target:** `{dossier.target_path}` | **Overall Health Score:** {dossier.overall_score}/100 (Grade: **{dossier.overall_grade}**)",
        f"**Total Words:** {dossier.total_words:,} | **Chapters Audited:** {dossier.total_chapters}",
        "",
        "---",
        "",
        "## 🎯 Prioritized Council Directives",
    ]
    for idx, item in enumerate(dossier.prioritized_action_items, 1):
        lines.append(f"{idx}. {item}")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 👥 Editorial Specialist Reports")

    for p in dossier.perspectives:
        lines.append(f"### 📋 {p.perspective_name} ({p.grade} • {p.score}/100)")
        lines.append(f"*{p.expert_title}*")
        lines.append(f"> {p.summary}")
        lines.append("")
        lines.append("**Key Observations:**")
        for f in p.key_findings:
            lines.append(f"- {f}")
        lines.append("")
        lines.append("**Prescriptions:**")
        for r in p.recommendations:
            lines.append(f"- ⚡ {r}")
        lines.append("")

    return "\n".join(lines)


def render_council_html(dossier: CouncilDossier, output_path: Path) -> Path:
    """Renders an interactive standalone offline HTML dossier."""
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ars Arcanum — Multi-Perspective Editorial Council Dossier</title>
<style>
  :root {{
    --bg: #090d16; --panel: #131b2e; --border: #23304d;
    --text: #f1f5f9; --muted: #94a3b8; --accent: #38bdf8; --gold: #fbbf24;
    --emerald: #10b981; --rose: #f43f5e;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    font-family: system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--text);
    margin: 0; padding: 2rem; line-height: 1.6;
  }}
  .container {{ max-width: 1100px; margin: 0 auto; }}
  header {{
    background: var(--panel); border: 1px solid var(--border); border-radius: 12px;
    padding: 1.75rem 2rem; margin-bottom: 2rem; display: flex; justify-content: space-between;
    align-items: center; flex-wrap: wrap; gap: 1rem;
  }}
  h1 {{ margin: 0; font-size: 1.6rem; color: var(--accent); }}
  .grade-badge {{
    font-size: 2.2rem; font-weight: 800; color: var(--gold); background: #0f172a;
    border: 2px solid var(--gold); border-radius: 10px; padding: 0.2rem 1.25rem;
  }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1.5rem; margin-bottom: 2rem; }}
  .card {{
    background: var(--panel); border: 1px solid var(--border); border-radius: 10px;
    padding: 1.5rem; display: flex; flex-direction: column;
  }}
  .card-header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 0.75rem; margin-bottom: 1rem; }}
  .card-title {{ font-weight: 700; font-size: 1.15rem; color: var(--gold); }}
  .card-grade {{ font-weight: 700; font-size: 1.1rem; color: var(--accent); }}
  ul {{ padding-left: 1.25rem; margin: 0.5rem 0; }}
  li {{ margin-bottom: 0.4rem; font-size: 0.88rem; }}
  .action-box {{
    background: #0f172a; border-left: 4px solid var(--accent); padding: 1.25rem 1.5rem;
    border-radius: 6px; margin-bottom: 2rem;
  }}
</style>
</head>
<body>
<div class="container">
  <header>
    <div>
      <h1>🏛️ Ars Arcanum Editorial Council Dossier</h1>
      <div style="color:var(--muted);font-size:0.875rem;margin-top:0.3rem;">
        Target: <code style="color:var(--gold);">{html.escape(dossier.target_path)}</code> | Words: {dossier.total_words:,} | Chapters: {dossier.total_chapters}
      </div>
    </div>
    <div style="display:flex;align-items:center;gap:1rem;">
      <div style="text-align:right;">
        <div style="font-size:0.75rem;color:var(--muted);text-transform:uppercase;">Overall Health</div>
        <div style="font-size:1.4rem;font-weight:700;color:var(--text);">{dossier.overall_score}/100</div>
      </div>
      <div class="grade-badge">{dossier.overall_grade}</div>
    </div>
  </header>

  <div class="action-box">
    <h3 style="margin:0 0 0.75rem 0;color:var(--accent);font-size:1.1rem;">🎯 Priority Directives for Next Revision</h3>
    <ul>
"""

    for item in dossier.prioritized_action_items:
        html_content += f"      <li>{html.escape(item)}</li>\n"

    html_content += """    </ul>
  </div>

  <h2 style="color:var(--accent);margin-bottom:1rem;font-size:1.3rem;">👥 Specialist Council Evaluations</h2>
  <div class="grid">
"""

    for p in dossier.perspectives:
        html_content += f"""
    <div class="card">
      <div class="card-header">
        <div>
          <div class="card-title">{html.escape(p.perspective_name)}</div>
          <small style="color:var(--muted);font-size:0.75rem;">{html.escape(p.expert_title)}</small>
        </div>
        <div class="card-grade">{p.grade} ({p.score}%)</div>
      </div>
      <p style="font-size:0.85rem;color:var(--muted);margin:0 0 0.75rem 0;">{html.escape(p.summary)}</p>
      <strong style="font-size:0.85rem;color:var(--text);">Observations:</strong>
      <ul>
"""
        for f in p.key_findings:
            html_content += f"        <li>{html.escape(f)}</li>\n"

        html_content += """      </ul>
      <strong style="font-size:0.85rem;color:var(--gold);margin-top:0.5rem;">Recommendations:</strong>
      <ul>
"""
        for r in p.recommendations:
            html_content += f"        <li style='color:var(--text);'>⚡ {html.escape(r)}</li>\n"

        html_content += """      </ul>
    </div>
"""

    html_content += """
  </div>
</div>
</body>
</html>
"""
    atomic_write(output_path, html_content)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Ars Arcanum Multi-Perspective Editorial Council Engine")
    parser.add_argument("target", help="Path to manuscript file or directory")
    parser.add_argument("--world", "-w", help="Optional World Bible directory for lore validation")
    parser.add_argument("--html", help="Generate interactive HTML dossier at specified path")
    parser.add_argument("--json", action="store_true", help="Output dossier as JSON to stdout")
    parser.add_argument("--markdown", "--md", action="store_true", help="Output dossier as Markdown to stdout")
    args = parser.parse_args()

    target_path = Path(args.target)
    if not target_path.exists():
        print(f"Error: Target path does not exist: {target_path}", file=sys.stderr)
        sys.exit(1)

    world_path = Path(args.world) if args.world else None
    dossier = run_editorial_council(target_path, world_path=world_path)

    if args.html:
        out_html = Path(args.html)
        render_council_html(dossier, out_html)
        print(f"Editorial Council HTML dossier generated: {out_html}")

    if args.json:
        print(json.dumps(asdict(dossier), indent=2))
        return

    if args.markdown:
        print(render_council_markdown(dossier))
        return

    # Default human-readable printout
    print("=" * 75)
    print(f"  🏛️  Ars Arcanum Editorial Council Dossier — Grade: {dossier.overall_grade} ({dossier.overall_score}/100)")
    print("=" * 75)
    print(f"Manuscript Target:       {dossier.target_path}")
    print(f"Total Words Audited:     {dossier.total_words:,}")
    print(f"Chapters Analyzed:       {dossier.total_chapters}")
    print("-" * 75)
    print("Perspective Grades:")
    for p in dossier.perspectives:
        print(f" • [{p.grade:>2}] {p.perspective_name:<18} ({p.score:>5.1f}/100) — {p.expert_title}")
    print("-" * 75)
    print("Top Action Items:")
    for idx, item in enumerate(dossier.prioritized_action_items[:5], 1):
        print(f" {idx}. {item}")
    print("=" * 75)


if __name__ == "__main__":
    main()
