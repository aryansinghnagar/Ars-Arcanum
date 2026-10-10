#!/usr/bin/env python3
"""
Domain Portfolio & Drafting Velocity Specifications for Ars Arcanum Registry.
"""
from __future__ import annotations

try:
    from lib.registry_base import EngineCategory, EngineSpec
except ImportError:
    from registry_base import EngineCategory, EngineSpec

ENGINES: dict[str, EngineSpec] = {
    "portfolio": EngineSpec(
        name="portfolio",
        category=EngineCategory.CORE,
        title="Portfolio & Catalog Analytics",
        description="Comprehensive overview of all universes, volumes, word counts, and drafting velocity",
        module_name="lib.portfolio",
        cli_command="portfolio",
        aliases=["portfolio", "series-overview", "author-stats", "catalog"],
        studio_tab="Dashboard",
        logic_documentation="Aggregates multi-series universe statistics: lifetime word counts, active draft stages, daily drafting velocity, and deadline projections across all local repositories.",
        scientific_logic="""1. Aggregated Multi-Project Metric Rollup:
   Scans all discovered universe manifests and manuscript chapters:
   $$W_{\\text{total}} = \\sum_{i=1}^U \\sum_{j=1}^{V_i} W_{ij}, \\quad \\text{Velocity } V_{\\text{daily}} = \\frac{\\Delta W}{\\Delta t}$$
   Projects estimated completion dates based on historical 7-day rolling velocity.""",
        why_this_way="Professional authors managing multiple series need a unified high-altitude portfolio view of their productivity and deadlines without cloud SaaS trackers.",
        worldbuilding_relevance="Summarizes total lore volume across interconnected universes.",
        storytelling_relevance="Tracks milestone completion across simultaneous novel projects.",
        writing_relevance="Provides daily word velocity metrics and deadline projections.",
        subfeatures=[
            {"name": "Multi-Universe Word Counter", "rule": "Aggregates words across all local manuscripts and lore vaults.", "example": "arcanum portfolio"},
            {"name": "Drafting Velocity Projector", "rule": "Calculates daily pace and estimated book completion date.", "example": "arcanum portfolio --velocity 1000"},
        ],
        extension_guide="""View portfolio overview:
```bash
arcanum portfolio
```""",
        advisory_guidance=[
            {"pattern": "Drafting velocity drops below target threshold", "option_a": "Adjust deadline schedule to accommodate realistic pacing", "option_b": "Schedule dedicated writing sprints", "option_c": "Accept variance during developmental plotting phase"},
        ],
    ),

    "word_counter": EngineSpec(
        name="word_counter",
        category=EngineCategory.CORE,
        title="Unicode Prose Word Count & Manuscript Telemetry",
        description="Accurate prose tokenization, POV distribution, dialogue ratios, reading times, and HTML Velocity Studio",
        module_name="lib.word_counter",
        cli_command="words",
        aliases=["wordcount", "count", "report", "words"],
        studio_tab="Editor",
        logic_documentation="Parses manuscript chapters, strips YAML frontmatter, code blocks, CriticMarkup, and NovelCrafter tags, calculating accurate prose words, dialogue vs narrative balance, CJK ideographs, reading time (~225 WPM), and audiobook narration duration (~150 WPM).",
        scientific_logic="""1. Prose Boundary Tokenization & Dialogue Extraction:
   $$W_{\\text{total}} = |\\{ w \\in \\text{Prose} \\mid w \\in \\mathcal{U}_{\\text{words}} \\}|$$
   $$\\text{Dialogue Ratio } \\delta = \\frac{W_{\\text{dialogue}}}{W_{\\text{total}}} \\times 100\\%$$
   Reading duration $T_{\\text{read}} = \\frac{W_{\\text{total}}}{225\\text{ WPM}}$, Audiobook duration $T_{\\text{audio}} = \\frac{W_{\\text{total}}}{9000\\text{ WPH}}$.""",
        why_this_way="Accurate prose counts separate pure story words from markdown metadata and CriticMarkup track-changes, while dialogue balance gives objective insight into scene dramatization.",
        worldbuilding_relevance="Measures lore entry word volume and category distributions.",
        storytelling_relevance="Tracks chapter pacing symmetry, POV character share, and dialogue dramatization.",
        writing_relevance="Delivers instant word progress against volume milestones and estimated print pages.",
        subfeatures=[
            {"name": "POV Share Breakdown", "rule": "Groups words by character POV tags.", "example": "arcanum words --pov"},
            {"name": "Dialogue vs Narrative Ratio", "rule": "Computes percentage of spoken dialogue vs descriptive prose.", "example": "arcanum words --dialogue"},
            {"name": "Interactive Velocity Studio", "rule": "Exports standalone offline HTML dashboard.", "example": "arcanum words --html dist/velocity.html"},
        ],
        extension_guide="""Run manuscript word count:
```bash
arcanum words Manuscript/
```""",
        advisory_guidance=[
            {"pattern": "Dialogue ratio drops below 15% in major action chapter", "option_a": "Dramatize exposition through character dialogue", "option_b": "Preserve high narrative density for internal monologue", "option_c": "Add brief character reactions"},
        ],
    ),

    "writing_sprint": EngineSpec(
        name="writing_sprint",
        category=EngineCategory.CORE,
        title="Writing Sprint & Cognitive Velocity Engine",
        description="Stateful Pomodoro sprint timer, rolling WPM velocity logger, habit streaks, and HTML studio",
        module_name="lib.writing_sprint",
        cli_command="sprint",
        aliases=["writing-sprint", "sprint", "velocity"],
        studio_tab="Editor",
        logic_documentation="Tracks focused drafting sessions via atomic state locks, computes real-time words-per-minute (WPM) and target completion ratio, records session history in .arcanum/sprint_log.jsonl, and calculates rolling 7d/30d velocity curves and habit streaks.",
        scientific_logic="""1. Session Velocity & Completion Ratio:
   $$\\bar{V}_{\\text{wpm}} = \\frac{\\Delta W}{\\Delta T}, \\quad \\rho = \\frac{\\Delta W}{W_{\\text{target}}}$$
2. Ultradian Rhythm & Sprint Rest Cycles:
   Enforces focused 25-50 min generative bursts detaching draft generation from critical evaluation.""",
        why_this_way="Sprints silence the inner editor and build daily drafting momentum. Local JSONL storage preserves 100% offline privacy without SaaS lock-in.",
        worldbuilding_relevance="Encourages focused lore brainstorming bursts.",
        storytelling_relevance="Helps authors push through raw first drafts without perfectionist stalling.",
        writing_relevance="Provides empirical drafting velocity data and daily streak accountability.",
        subfeatures=[
            {"name": "Interactive TTY Countdown", "rule": "Live ANSI countdown with real-time goal meters.", "example": "arcanum sprint start --target 500 --minutes 25"},
            {"name": "Automated Word Delta Logging", "rule": "Computes net words added from manuscript diffs upon session completion.", "example": "arcanum sprint stop"},
            {"name": "Velocity & Streak Analytics", "rule": "Calculates rolling 7d pace, habit streaks, and peak flow hours.", "example": "arcanum sprint stats"},
        ],
        extension_guide="""Start a writing sprint:
```bash
arcanum sprint start --target 500 --minutes 25
```""",
        advisory_guidance=[
            {"pattern": "Drafting velocity stalls (<10 WPM) during active sprint", "option_a": "Pause sprint and outline scene conflict in lore vault", "option_b": "Switch to freewriting / fast-drafting mode", "option_c": "Take a 5-minute cognitive rest break"},
        ],
    ),
}

__all__ = ["ENGINES"]

