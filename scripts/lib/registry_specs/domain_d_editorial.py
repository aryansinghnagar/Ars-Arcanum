#!/usr/bin/env python3
"""
Domain engine specification definitions for Ars Arcanum Registry.
"""
from __future__ import annotations

try:
    from lib.registry_base import EngineCategory, EngineSpec
except ImportError:
    from registry_base import EngineCategory, EngineSpec

ENGINES: dict[str, EngineSpec] = {

    # =========================================================================
    # DOMAIN D: CONTINUITY & EDITORIAL POLISH
    # =========================================================================

    "continuity": EngineSpec(
        name="continuity",
        category=EngineCategory.CRAFT,
        title="Semantic Continuity & Trait Linter",
        description="Local-first semantic narrative continuity analyzer cross-validating character traits across drafts",
        module_name="lib.continuity",
        cli_command="continuity",
        aliases=["continuity", "check-continuity", "traits"],
        studio_tab="Diagnostics",
        logic_documentation="Extracts character physical traits (eyes, hair, titles, status) from World Bible files and sentence-level manuscript scenes, detecting character trait drift, impossible contradictions, and inter-scene inconsistencies.",
        scientific_logic="""1. Semantic Entity-Trait Extraction Graph:
   Extracts canonical trait tuples $(E, T, V)$ from World Bible (e.g. $(\\text{Kaelen}, \\text{eye\\_color}, \\text{grey-blue})$).

2. Manuscript Surface Assertion Cross-Validation:
   NLP pattern sweeps extract asserted traits in scenes: $(\\text{Kaelen}, \\text{eye\\_color}, \\text{green})$.
   When asserted value $V_{\\text{scene}} \\ne V_{\\text{canon}}$, a continuity conflict is flagged with line citations.""",
        why_this_way="In 100,000+ word novels written over months, authors accidentally change eye color, handedness, or titles between chapters.",
        worldbuilding_relevance="Ensures character traits established in lore dossiers are maintained in prose.",
        storytelling_relevance="Catches accidental continuity discrepancies before publication.",
        writing_relevance="Provides clear advisory alerts with multiple creative resolution pathways.",
        subfeatures=[
            {"name": "Trait Inconsistency Auditor", "rule": "Cross-checks eye color, hair, scars, and handedness between lore and scenes.", "example": "arcanum continuity -w World/ -m Manuscript/"},
            {"name": "Inventory & Relic Tracker", "rule": "Audits weapon and gear retention across scenes.", "example": "arcanum continuity -w World/ -m Manuscript/ --gear"},
        ],
        extension_guide="""Run continuity checker:
```bash
arcanum continuity -w World/ -m Manuscript/
```""",
        advisory_guidance=[
            {"pattern": "Character eye color asserted as green in scene but blue in World Bible", "option_a": "Correct scene prose to match World Bible canonical blue eyes", "option_b": "Ground color shift in story (e.g. illusion, colored contact, magical flare)", "option_c": "Update World Bible dossier if the author intentionally changed character design"},
        ],
    ),

    "series_continuity": EngineSpec(
        name="series_continuity",
        category=EngineCategory.CRAFT,
        title="Series Continuity Ledger",
        description="Tracks recurring character traits, scars, eye color, and gear across multi-volume series",
        module_name="lib.series_continuity",
        cli_command="series",
        aliases=["series", "series-continuity", "ledger"],
        studio_tab="Worldbuilding",
        logic_documentation="Tracks character physical traits (handedness, scars, eye color), relic chains of custody, biological aging across timeskips, and geopolitical world-state changes across multi-book sagas.",
        scientific_logic="""1. Cross-Volume State Mutation Ledger:
   Tracks immutable historical facts across multi-book sagas:
   $$\\text{Volume 1 State } S_1 \\xrightarrow{\\text{Timeskip } \\Delta T} \\text{Volume 2 State } S_2 \\xrightarrow{} \\text{Volume 3 State } S_3$$
   Validates character biological aging ($A_2 = A_1 + \\Delta T$), relic custody handoffs, and scar permanence.""",
        why_this_way="Multi-volume series are vulnerable to retcons and forgotten character wounds across years of writing.",
        worldbuilding_relevance="Ensures multi-volume world lore remains coherent as empires rise and fall.",
        storytelling_relevance="Maintains character scars, trauma, and power progression across decades of story time.",
        writing_relevance="Prevents embarrassing retcons and continuity errors between Book 1 and Book 5.",
        subfeatures=[
            {"name": "Cross-Volume Trait Ledger", "rule": "Ensures character traits and physical scars carry over across books.", "example": "arcanum series --ledger-check"},
            {"name": "Timeskip Aging Validator", "rule": "Audits biological ages against world calendar timeskips.", "example": "arcanum series --aging-check"},
        ],
        extension_guide="""Define series-level invariants in `World/Series/series_ledger.yaml`:
```yaml
series_ledger:
  volumes: ["Book 1", "Book 2", "Book 3"]
  relics:
    - name: "Sunblade"
      custody:
        "Book 1": "King Alden (Lost in Chapter 14)"
        "Book 2": "Kaelen Voss (Found in Vault)"
```""",
        advisory_guidance=[
            {"pattern": "Character eye color or handedness changed between volumes", "option_a": "Revert to Book 1 canonical trait", "option_b": "Ground change in story event (e.g. magical scarring, injury, disguise)", "option_c": "Acknowledge and retain as an intentional character transformation"},
        ],
    ),

    "typography_cleaner": EngineSpec(
        name="typography_cleaner",
        category=EngineCategory.CORE,
        title="Typography Cleaner",
        description="Normalizes smart curly quotes, em-dashes, and typographical ellipses",
        module_name="lib.typography_cleaner",
        cli_command="polish typography",
        aliases=["clean-typography", "polish", "typography"],
        studio_tab="Editor",
        logic_documentation="Applies Chicago Manual of Style (CMOS) and Oxford typographical rules: converts straight quotes to curly quotes, double hyphens to em-dashes, and triple periods to true ellipses.",
        scientific_logic="""1. Chicago Manual of Style (CMOS 17th Ed) / Oxford Typography Rules:
   - Straight quotes `' '` and `" "` normalized to typographical curly quotes `‘ ’` and `“ ”` with opening/closing whitespace heuristics.
   - Double hyphens `--` converted to unspaced true em-dashes `—`.
   - Triple periods `...` converted to Unicode horizontal ellipsis `…`.
   - Dialogue punctuation: Dialogue tags properly lowercased after commas (`“Wait,” he said.` vs `“Wait!” He ran.`).""",
        why_this_way="Straight typewriter quotes and double hyphens look amateurish in published ebooks and print books. Automated typographical normalization elevates prose to professional literary standards.",
        worldbuilding_relevance="Handles in-universe punctuation rules (e.g. alien glottal stops vs quotation marks).",
        storytelling_relevance="Prevents jarring punctuation anomalies from pulling readers out of immersion.",
        writing_relevance="Gives prose a polished, traditionally published literary aesthetic in one click.",
        subfeatures=[
            {"name": "Smart Quotes Normalizer", "rule": "Converts straight quotes to typographical curly quotes with contraction handling.", "example": "arcanum polish typography Manuscript/01_Chapter.md"},
            {"name": "Dialogue Comma Splice Linter", "rule": "Audits dialogue tag capitalization and comma placement.", "example": "arcanum polish typography Manuscript/ --audit-dialogue"},
        ],
        extension_guide="""Clean typography across a manuscript:
```bash
arcanum polish typography Manuscript/
```""",
        advisory_guidance=[
            {"pattern": "Unconventional dialogue punctuation (e.g. em-dash quotes or guillemets)", "option_a": "Normalize to standard CMOS quotation marks", "option_b": "Preserve European / custom dialogue conventions", "option_c": "Apply selectively per character dialect"},
        ],
    ),

    "manuscript_diff": EngineSpec(
        name="manuscript_diff",
        category=EngineCategory.CORE,
        title="Draft Diff & Visual Redline",
        description="Comparative redline changelog and visual diffs between manuscript drafts",
        module_name="lib.manuscript_diff",
        cli_command="compare",
        aliases=["diff", "redline", "changelog", "manuscript-diff"],
        studio_tab="Editor",
        logic_documentation="Computes Myers semantic diff algorithms between draft iterations (Draft-01 vs Draft-02), isolating word additions, deletions, paragraph moves, and dialogue changes.",
        scientific_logic="""1. Myers Semantic Diff Algorithm:
   Computes shortest edit script $SES$ and Longest Common Subsequence ($LCS$) between two draft text streams.
   Distinguishes prose additions ($+$), deletions ($-$), paragraph position relocations, and dialogue word rewrites.""",
        why_this_way="Standard git line diffs are unreadable for prose because changing one word refits an entire paragraph. Word-level semantic visual redlines clearly show creative revisions.",
        worldbuilding_relevance="Tracks when specific lore terms or character names were altered across revisions.",
        storytelling_relevance="Highlights major scene cuts, restructured chapters, and dialogue tightenings.",
        writing_relevance="Generates side-by-side visual HTML redline views with word churn statistics.",
        subfeatures=[
            {"name": "Visual Redline HTML Exporter", "rule": "Generates side-by-side green/red comparison view.", "example": "arcanum compare Manuscript/Draft-01 Manuscript/Draft-02 --html dist/redline.html"},
            {"name": "Excised Prose Scraps Vault", "rule": "Automatically extracts cut prose chunks (>50 words) into a reusable Scraps vault.", "example": "arcanum compare Manuscript/ --extract-scraps"},
        ],
        extension_guide="""Compare two drafts from CLI:
```bash
arcanum compare Manuscript/Draft-01 Manuscript/Draft-02
```""",
        advisory_guidance=[
            {"pattern": "Large block cut detected (>500 words)", "option_a": "Archive excised prose in Scraps/ folder for recycling", "option_b": "Review scene pacing to ensure no dropped plot threads", "option_c": "Accept cut as intentional tightening"},
        ],
    ),

    "revision_heatmap": EngineSpec(
        name="revision_heatmap",
        category=EngineCategory.CRAFT,
        title="Manuscript Revision Density & Churn Heatmap",
        description="Snapshot-based revision churn analyzer flagging over-revised (REV-101) and pristine-draft (REV-102) chapters",
        module_name="lib.revision_heatmap",
        cli_command="revision-heatmap",
        aliases=["churn", "revision-density", "draft-churn", "heatmap"],
        studio_tab="Diagnostics",
        logic_documentation="Analyzes historical snapshot diffs to compute sentence-level word churn ratios, distinguishing structural rewrites from polish edits and flagging over-revised vs pristine chapters.",
        scientific_logic="""1. Word Churn Ratio & Revision Density Metric:
   $$\\text{Churn Ratio } R = \\frac{\\text{Words Added} + \\text{Words Deleted}}{\\text{Total Chapter Words}}$$
   - REV-101 (Over-revised / Perfectionist Trap): Churn $> 120\\%$ across 5+ drafts with minimal plot progression.
   - REV-102 (Pristine / Under-revised): Churn $< 5\\%$ despite major developmental restructuring in adjacent chapters.""",
        why_this_way="Authors often get stuck endlessly rewriting Chapter 1 without making progress on later chapters. Churn heatmaps provide objective data on where editing effort is truly needed.",
        worldbuilding_relevance="Shows which lore sections underwent the heaviest conceptual overhauls.",
        storytelling_relevance="Identifies 'problem chapters' that have been endlessly rewritten without progress.",
        writing_relevance="Helps authors step away from perfectionist over-editing and move forward.",
        subfeatures=[
            {"name": "Chapter Churn Density Matrix", "rule": "Computes historical modification intensity per chapter.", "example": "arcanum revision-heatmap Manuscript/ --html dist/churn.html"},
            {"name": "Perfectionist Trap Detector", "rule": "Flags chapters with churn >120% across drafts.", "example": "arcanum revision-heatmap Manuscript/ --flag-traps"},
        ],
        extension_guide="""Run revision heatmap diagnostic:
```bash
arcanum revision-heatmap Manuscript/
```""",
        advisory_guidance=[
            {"pattern": "Chapter flagged with excessive revision churn (>80% word replacement across 5+ drafts)", "option_a": "Perform fresh developmental outline review of the scene's core goal", "option_b": "Lock the chapter and proceed to drafting subsequent chapters", "option_c": "Accept high churn as necessary stylistic exploration"},
        ],
    ),
}

__all__ = ["ENGINES"]
