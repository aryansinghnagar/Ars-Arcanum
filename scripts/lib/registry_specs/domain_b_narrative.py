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
    # DOMAIN B: NARRATIVE ARCHITECTURE, DRAMATURGY & PACING
    # =========================================================================
    "structure": EngineSpec(
        name="structure",
        category=EngineCategory.CRAFT,
        title="Narrative Structure & Paradigms",
        description="Validates manuscript beats against Three-Act, Save the Cat, 8-Sequence, Hero's Journey, and Kishōtenketsu",
        module_name="lib.structure",
        cli_command="structure",
        aliases=["structure", "paradigms", "beats"],
        studio_tab="Craft",
        logic_documentation="Maps chapter word distributions against classical and modern storytelling frameworks: Three-Act Structure, Save the Cat, 8-Sequence Method, Hero's Journey, Fichtean Curve, and Kishōtenketsu (4-act twist without conflict).",
        scientific_logic="""1. Three-Act Structure (Aristotle / Syd Field):
   - Act I (Setup & Inciting Incident): $0\\%\\text{--}25\\%$
   - Act II-A (Rising Action & Pinch 1): $25\\%\\text{--}50\\%$
   - Midpoint Shift (Mirror Moment / Active Agency): $50\\%$
   - Act II-B (Crisis & All Hope Lost): $50\\%\\text{--}75\\%$
   - Act III (Climax & Resolution): $75\\%\\text{--}100\\%$

2. Save the Cat 15-Beat Architecture (Blake Snyder):
   - Opening Image ($1\\%$), Theme Stated ($5\\%$), Setup ($1\\%\\text{--}10\\%$)
   - Catalyst ($12\\%$), Debate ($12\\%\\text{--}25\\%$), Break into Two ($25\\%$)
   - B-Story ($28\\%$), Fun & Games ($25\\%\\text{--}50\\%$), Midpoint ($50\\%$)
   - Bad Guys Close In ($50\\%\\text{--}75\\%$), All is Lost ($75\\%$), Dark Night of Soul ($75\\%\\text{--}80\\%$)
   - Break into Three ($80\\%$), Finale ($80\\%\\text{--}99\\%$), Final Image ($100\\%$)

3. Kishōtenketsu (Traditional East Asian 4-Act Paradigm):
   - Ki (起 - Introduction): $0\\%\\text{--}25\\%$
   - Shō (承 - Development): $25\\%\\text{--}50\\%$
   - Ten (転 - The Unexpected Twist / Context Reframe without Western Conflict): $50\\%\\text{--}75\\%$
   - Ketsu (結 - Harmonization & Conclusion): $75\\%\\text{--}100\\%$""",
        why_this_way="Narrative pacing issues (the sagging middle, premature climax, rushed resolution) stem from unbalanced word allocations across structural beats. By mapping exact cumulative manuscript words against established dramatic paradigms, authors immediately see where their pacing drags or accelerates too quickly.",
        worldbuilding_relevance="Aligns world discovery milestones with character paradigm shifts.",
        storytelling_relevance="Diagnoses sluggish midpoints, premature climaxes, and rushed resolutions.",
        writing_relevance="Provides structural confidence during outlining and developmental editing.",
        subfeatures=[
            {"name": "Multi-Paradigm Beat Mapper", "rule": "Projects chapter word boundaries onto 3-Act, Save the Cat, 8-Sequence, and Kishōtenketsu models.", "example": "arcanum structure Manuscript/ --paradigm save-the-cat"},
            {"name": "Midpoint Harmony Check", "rule": "Audits whether pivotal status-quo shift occurs within 48%-52% of total word count.", "example": "arcanum structure Manuscript/ --midpoint-check"},
        ],
        extension_guide="""Configure custom story paradigms in `Manuscript/manuscript.yaml`:
```yaml
structure:
  target_words: 95000
  paradigm: "Three-Act"
  custom_milestones:
    inciting_incident: 12000
    midpoint_cataclysm: 47500
    climax_entry: 76000
```""",
        advisory_guidance=[
            {"pattern": "Midpoint transformation occurs at 68% instead of standard 50%", "option_a": "Rebalance chapter lengths toward symmetrical midpoint", "option_b": "Adopt asymmetrical 4-part Kishōtenketsu or Fichtean episodic pacing", "option_c": "Retain pacing as an intentional authorial tension curve"},
        ],
    ),

    "plot_matrix": EngineSpec(
        name="plot_matrix",
        category=EngineCategory.CRAFT,
        title="Plot Grid & Subplot Matrix",
        description="Multi-threaded narrative grid tracking concurrent character arcs, mystery clues, and Chekhov's guns",
        module_name="lib.plot_matrix",
        cli_command="plot",
        aliases=["plot", "matrix", "subplots"],
        studio_tab="Craft",
        logic_documentation="Builds multi-track 2D plot spreadsheets tracking concurrent A-plots, B-plots, mystery clues, Chekhov's guns, Sanderson's Promise-Progress-Payoff (P3) cycles, and character co-occurrence collisions.",
        scientific_logic="""1. 2D Multi-Thread Plot Matrix:
   Rows represent Chapters $C_1, C_2, \\dots, C_n$; columns represent concurrent Narrative Threads $T_1, T_2, \\dots, T_m$ (Main A-Plot, Romance B-Plot, Political Intrigue C-Plot, Mystery Clues).

2. Chekhov's Gun Lifecycle State Machine:
   $$\\text{Introduced (Chapter } i) \\longrightarrow \\text{Primed / Referenced (Chapter } j) \\longrightarrow \\text{Discharged / Paid Off (Chapter } k)$$
   Flags unresolved guns ($k = \\text{None}$) and ungrounded climactic solutions ($i = k$, deus ex machina).

3. Sanderson Promise-Progress-Payoff (P3) Architecture:
   - Promise: Explicit early contract with reader establishing tone and stakes.
   - Progress: Measurable, perceptible milestones toward resolving the contract.
   - Payoff: Satisfying fulfillment or deliberate subversion of the promise.""",
        why_this_way="Complex multi-POV novels easily drop subplots or fail to pay off foreshadowed clues. A formal matrix ensures every introduced story element undergoes proper priming and payoff.",
        worldbuilding_relevance="Ensures world events (wars, celestial transits) align with character chapters.",
        storytelling_relevance="Tracks foreshadowing fulfillment and prevents forgotten subplots across chapters.",
        writing_relevance="Provides structural clarity across complex, multi-threaded epics.",
        subfeatures=[
            {"name": "Chekhov Gun Lifecycle Audit", "rule": "Tracks introduced artifacts and flags those with zero climactic payoff.", "example": "arcanum plot Manuscript/ --chekhov"},
            {"name": "Subplot Progression Grid", "rule": "Generates 2D chapter-by-thread visual matrix.", "example": "arcanum plot Manuscript/ --html dist/plot_matrix.html"},
        ],
        extension_guide="""Annotate plot threads in chapter frontmatter:
```yaml
---
title: "Whispers in the Crypt"
threads:
  a_plot: "Infiltrate royal vault"
  b_plot_romance: "Althea discovers Kaelen's exile mark"
chekhov_guns:
  - id: "obsidian_dagger"
    status: "introduced" # "primed" | "discharged"
    notes: "Found beneath the sarcophagus"
---
```""",
        advisory_guidance=[
            {"pattern": "Chekhov gun introduced in early chapter without payoff by climax", "option_a": "Integrate payoff during climactic resolution", "option_b": "Frame as an intentional mystery clue carried into sequel volume", "option_c": "Keep as atmospheric background lore element"},
        ],
    ),

    "story_canvas": EngineSpec(
        name="story_canvas",
        category=EngineCategory.CRAFT,
        title="Visual Story Canvas & Corkboard",
        description="Visual drag-and-drop narrative corkboard with live structural harmony recalculation",
        module_name="lib.story_canvas",
        cli_command="canvas",
        aliases=["corkboard", "story-map", "story-canvas"],
        studio_tab="Editor",
        logic_documentation="Provides an offline visual corkboard where authors can drag and drop chapter index cards, reordering disk files bidirectionally, while calculating tension and structural beat distributions in real-time.",
        scientific_logic="""1. Bidirectional Disk File Graph Synchronization:
   Card ordering in the visual UI is backed by atomic renaming:
   $$\\text{UI Order } \\langle C_1, C_2, \\dots, C_n \\rangle \\longleftrightarrow \\text{Atomic POSIX renumbering on disk } 01\\_\\dots, 02\\_\\dots$$

2. Real-Time Structural Harmony Recalculation:
   As cards are dragged between Act columns, word counts and tension curves recompute instantly via standard deviation deltas from target beat percentages.""",
        why_this_way="Visual thinkers need a spatial corkboard to arrange scenes without breaking the disk file naming conventions of novelWriter and Obsidian.",
        worldbuilding_relevance="Pins location dossiers and artifact cards alongside relevant plot scenes.",
        storytelling_relevance="Enables intuitive visual restructuring of acts, sequences, and subplot pacing.",
        writing_relevance="Combines visual index cards with synopsis summaries for effortless chapter navigation.",
        subfeatures=[
            {"name": "Drag-and-Drop Corkboard", "rule": "Rearranges chapters and scenes across act columns with instant preview.", "example": "arcanum canvas Manuscript/ --html dist/canvas.html"},
            {"name": "Atomic Disk Renumberer", "rule": "Safely updates file names on disk to mirror corkboard arrangement.", "example": "arcanum canvas Manuscript/ --apply-order"},
        ],
        extension_guide="""Launch Story Canvas via CLI:
```bash
arcanum canvas Manuscript/
```""",
        advisory_guidance=[
            {"pattern": "Visual card reordering changes chapter narrative sequence on disk", "option_a": "Confirm atomic file renumbering on disk", "option_b": "Create virtual outline arrangement without touching disk files", "option_c": "Export new card order as an alternative draft outline"},
        ],
    ),

    "causality": EngineSpec(
        name="causality",
        category=EngineCategory.CRAFT,
        title="Causal Graph & Timeline Branches",
        description="Directed Acyclic Graph causality engine, timeline paradox detection, and multiverse trees",
        module_name="lib.causality",
        cli_command="causality",
        aliases=["causality", "causal", "time-travel", "paradox"],
        studio_tab="Worldbuilding",
        logic_documentation="Models narrative causality using Directed Acyclic Graphs (DAG), detects Closed Timelike Curves (CTC), evaluates Novikov self-consistency loops, and tracks multiverse timeline branch divergence.",
        scientific_logic="""1. Causal Directed Acyclic Graph (DAG) Structure:
   Events $E = \\{e_1, e_2, \\dots, e_n\\}$ with causal relation $e_i \\prec e_j$ (event $i$ is a necessary prerequisite for event $j$).

2. Closed Timelike Curve (CTC) & Paradox Detection:
   - Grandfather Paradox (Inconsistency Cycle): A causal edge directed into its own past light-cone that negates its own cause: $\\exists e_i \\prec \\dots \\prec e_j \\prec \\neg e_i$.
   - Novikov Self-Consistency Condition: A closed loop where total probability of the loop occurring is $P = 1.0$ (ontological loop / bootstrap paradox without contradiction).
   - Multiverse Branching (Many-Worlds): At divergence point $t_{\\text{fork}}$, create new branch world-line $W_2$ while preserving $W_1$ invariant.""",
        why_this_way="Time-travel and precognition narratives frequently collapse into unresolvable logical contradictions. The causality engine mathematically checks every causal link to guarantee temporal consistency.",
        worldbuilding_relevance="Establishes hard physical/metaphysical rules for time travel, prophecies, and precognition.",
        storytelling_relevance="Audits time-travel story logic, grandfather paradoxes, bootstrap paradoxes, and temporal loops.",
        writing_relevance="Helps authors keep track of causal ripples, memory echoes, and butterfly effects.",
        subfeatures=[
            {"name": "CTC Paradox Sweeper", "rule": "Scans historical timeline events for negative causal feedback loops.", "example": "arcanum causality World/ --audit-loops"},
            {"name": "Multiverse Branch Visualizer", "rule": "Exports branching timeline tree showing divergent worldlines.", "example": "arcanum causality World/ --html dist/causal_tree.html"},
        ],
        extension_guide="""Define causal events in `World/History/timeline_events.yaml`:
```yaml
events:
  - id: "assassination_king"
    date: "1442-03-12"
    prerequisites: ["palace_guard_bribe", "smuggled_nightshade"]
    consequences: ["succession_crisis", "martial_law"]
    temporal_branch: "prime"
```""",
        advisory_guidance=[
            {"pattern": "Ungrounded causal bootstrap paradox (information with no origin)", "option_a": "Provide origin event for the retrocausal information", "option_b": "Ground as a stable Novikov self-consistent ontological loop", "option_c": "Embrace the paradox as a deliberate cosmic mystery"},
        ],
    ),

    "timeline_sync": EngineSpec(
        name="timeline_sync",
        category=EngineCategory.CRAFT,
        title="Dual-Track Timeline Synchronizer",
        description="Chronological vs narrative sequence synchronizer with flashback and paradox detection",
        module_name="lib.timeline_sync",
        cli_command="timeline",
        aliases=["timeline-sync", "sync-timeline", "chronology"],
        studio_tab="Worldbuilding",
        logic_documentation="Synchronizes dual-track narrative sequence (reader's page order) against chronological in-universe dates, detecting impossible character bilocations, flashbacks, and timeline paradoxes.",
        scientific_logic="""1. Dual-Track Sequence Alignment:
   - Narrative Track (Discourse Time): Ordered sequence $\\langle 1, 2, \\dots, N \\rangle$ of chapters read by the audience.
   - Chronological Track (Story Time): In-universe absolute timestamp $T_{\\text{world}}(C_k)$.
   - Nonlinear Anachrony: Flashbacks (analepsis: $T(C_{k}) < T(C_{k-1})$) and Flash-forwards (prolepsis: $T(C_{k}) \\gg T(C_{k-1})$).

2. Bilocation & Invariant Spatial Velocity Check:
   If character $X$ appears in Chapter $A$ at location $L_A$ at time $t_A$, and in Chapter $B$ at location $L_B$ at time $t_B$:
   $$v_{\\text{required}} = \\frac{d(L_A, L_B)}{|t_B - t_A|} \\le v_{\\text{max\\_travel}}$$
   Flags impossible bilocations when required velocity exceeds realistic travel speed.""",
        why_this_way="Nonlinear storytelling (flashbacks, parallel storylines) easily creates unintentional continuity bugs where characters appear in two distant places at the same time.",
        worldbuilding_relevance="Builds thousands of years of historical annals aligned with in-universe calendar math.",
        storytelling_relevance="Manages nonlinear storytelling (flashbacks, parallel storylines, framing narratives).",
        writing_relevance="Ensures character biological ages, travel times, and seasons match narrative dates.",
        subfeatures=[
            {"name": "Bilocation Conflict Detector", "rule": "Flags characters present at two different locations on the same in-universe date.", "example": "arcanum timeline Manuscript/ --audit-bilocation"},
            {"name": "Anachrony Visualizer", "rule": "Renders dual-track Gantt chart linking story time to chapter reading order.", "example": "arcanum timeline Manuscript/ --html dist/timeline.html"},
        ],
        extension_guide="""Specify narrative and chronological times in chapter frontmatter:
```yaml
---
title: "The Battle of Ash Hollow"
chrono_date: "1442-09-14"
narrative_time: "Day 4 of the Campaign (Flashback)"
pov: "Commander Jennifer"
location: "Ash Hollow Fortress"
---
```""",
        advisory_guidance=[
            {"pattern": "Character appears in two distant locations on the same chronological date (bilocation)", "option_a": "Adjust chapter narrative date or introduce travel interval", "option_b": "Ground bilocation via magical teleportation, twin sibling, or astral projection", "option_c": "Retain as an intentional non-linear storytelling perspective"},
        ],
    ),

    "prophecy": EngineSpec(
        name="prophecy",
        category=EngineCategory.CRAFT,
        title="Prophecy Lifecycle Tracker",
        description="Tracks cryptic prophecy stanzas, interpretations, fulfillment conditions, and subversions",
        module_name="lib.prophecy",
        cli_command="prophecy",
        aliases=["prophecy", "oracle", "delphic"],
        studio_tab="Worldbuilding",
        logic_documentation="Tracks cryptic prophecy stanzas, Delphic ambiguities, fulfillment milestones, Oedipal paradoxes, and deliberate thematic subversions across manuscript chapters.",
        scientific_logic="""1. Prophecy Stanza & Delphic Clause Tree:
   A prophecy consists of stanzas $S_1, S_2, \\dots, S_n$, where each stanza contains one or more ambiguous clauses $C_{ij}$.
   Each clause maps to multiple competing In-World Interpretations $\\{I_1, I_2, \\dots\\}$ and one True Fulfillment Event $E^*$.

2. Oedipal Paradox (Self-Fulfilling Prophecy):
   Event $E^*$ is caused precisely by the antagonist's actions to prevent $E^*$: $\\text{Action}(\\neg E^*) \\Longrightarrow E^*$.

3. Fulfillment Typology:
   - Literal: Clause resolves in exact accordance with prophecy wording.
   - Metaphorical / Delphic: 'No man born of woman' resolved via C-section (Macbeth).
   - Subverted: Prophecy revealed as manufactured political propaganda.""",
        why_this_way="Prophecies become boring when they spoil the plot or feel like arbitrary author cheat codes. Tracking interpretations and subversions ensures foreshadowing feels earned and climactic.",
        worldbuilding_relevance="Grounds sacred religious scriptures, ancient oracle inscriptions, and mythological lore.",
        storytelling_relevance="Builds reader anticipation and dramatic irony through ambiguous prophecy clauses.",
        writing_relevance="Aids in crafting poetic, double-meaning prophetic verses and riddle stanzas.",
        subfeatures=[
            {"name": "Clause Fulfillment Matrix", "rule": "Tracks status (Unfulfilled, Primed, Fulfilled, Subverted) per stanza.", "example": "arcanum prophecy World/ --status"},
            {"name": "Delphic Ambiguity Analyzer", "rule": "Identifies double-meanings and homophones in poetic verses.", "example": "arcanum prophecy World/ --verses"},
        ],
        extension_guide="""Define prophecy manifests in `World/History/prophecy_of_the_sun.yaml`:
```yaml
prophecy:
  title: "The Prophecy of the Shattered Sun"
  source: "Oracle of Delphi-Prime"
  stanzas:
    - id: "stanza_1"
      verse: "When the black star bleeds upon the silver sea..."
      literal_interpretation: "Solar eclipse over the Silver Ocean"
      true_event_chapter: "Chapter_18"
      status: "fulfilled"
```""",
        advisory_guidance=[
            {"pattern": "Prophecy clause fulfilled too straightforwardly without thematic twist", "option_a": "Add Delphic double-meaning or ironic twist to fulfillment", "option_b": "Subvert the prophecy as a manufactured political fraud", "option_c": "Fulfill literally as a legendary validation of ancient truth"},
        ],
    ),

    "writing_sprint": EngineSpec(
        name="writing_sprint",
        category=EngineCategory.CORE,
        title="Sovereign Writing Sprint & Session Analytics",
        description="Sprint session timer, WPM velocity analytics, daily streak tracking, and offline HTML productivity dashboard",
        module_name="lib.writing_sprint",
        cli_command="sprint",
        aliases=["sprint", "pomodoro", "velocity"],
        studio_tab="Productivity",
        logic_documentation="Tracks focused writing sprint intervals, net new word counts, WPM typing velocity, daily streaks, time-of-day productivity heatmaps, and offline achievement quests.",
        scientific_logic="""1. Pomodoro Focus Interval & Velocity Analytics:
   $$\\text{Net Words} = W_{\\text{end}} - W_{\\text{start}}, \\quad \\text{WPM} = \\frac{\\text{Net Words}}{\\text{Sprint Duration (Minutes)}}$$

2. Time-of-Day Productivity Heatmap:
   Bivariate distribution of writing volume across hour of day $h \\in [0, 23]$ and day of week $d \\in [0, 6]$ to isolate author's peak cognitive flow windows.""",
        why_this_way="Authors struggle with writer's block when looking at a massive 100,000-word book. Short 15-25 minute sprints gamify drafting and build daily output momentum.",
        worldbuilding_relevance="Measures worldbuilding note generation velocity and research sprints.",
        storytelling_relevance="Assists writers in breaking through drafting blocks and hitting volume milestones.",
        writing_relevance="Builds consistent daily writing habits with motivating offline progress reports.",
        subfeatures=[
            {"name": "Sprint Interval Timer", "rule": "Runs 15/25/45-minute timed drafting sessions with net word telemetry.", "example": "arcanum sprint Manuscript/ --minutes 25"},
            {"name": "Productivity Heatmap", "rule": "Generates offline HTML report of writing velocity by hour and day.", "example": "arcanum sprint --history --html dist/sprint_dashboard.html"},
        ],
        extension_guide="""Start a writing sprint from CLI:
```bash
arcanum sprint Manuscript/ --minutes 20 --target-words 500
```""",
        advisory_guidance=[
            {"pattern": "Sprint target word count not reached during interval", "option_a": "Extend sprint timer by 5 minutes for completion", "option_b": "Log session words and celebrate net positive output", "option_c": "Reflect in session journal and take a restful break"},
        ],
    ),
}

__all__ = ["ENGINES"]
