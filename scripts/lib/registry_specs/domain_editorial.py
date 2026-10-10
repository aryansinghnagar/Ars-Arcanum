#!/usr/bin/env python3
"""
Domain Editorial & Revision Specifications for Ars Arcanum Registry.
"""
from __future__ import annotations

try:
    from lib.registry_base import EngineCategory, EngineSpec
except ImportError:
    from registry_base import EngineCategory, EngineSpec

ENGINES: dict[str, EngineSpec] = {
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
        description="Word-level revision churn analyzer and interactive studio dashboard flagging perfectionist loops, cuts, and dialogue/prose skew across draft lineages",
        module_name="lib.revision_heatmap",
        cli_command="revision-heatmap",
        aliases=["churn", "revision-density", "draft-churn", "heatmap"],
        studio_tab="Diagnostics",
        logic_documentation="Analyzes historical snapshot diffs, draft lineages, and folder pairs to compute word-level churn ratios, separating dialogue from narrative exposition and evaluating 6 diagnostic craft rules (REV-101 through REV-106).",
        scientific_logic="""1. Word Churn Ratio & Revision Density Metric:
   $$\\text{Churn Ratio } R = \\frac{W_{\\text{added}} + W_{\\text{deleted}}}{\\max(W_{\\text{current}}, W_{\\text{baseline}}, 1)}$$
2. Dialogue vs Narrative Exposition Segmentation:
   Categorizes rewrites into spoken dialogue vs narrative prose to identify voice polishing vs structural rewrites.
3. 6-Tier Diagnostic Telemetry:
   - REV-101: Perfectionist High Churn ($R > 3.0 \\times R_{\\text{avg}}$ or $R \\ge 1.20$)
   - REV-102: Pristine Draft ($W_{\\text{churn}} == 0 \\land W > 50$)
   - REV-103: Heavy Narrative Cut ($W_{\\text{del}} \\ge 40\\%$)
   - REV-104: Major Chapter Expansion ($W_{\\text{add}} \\ge 50\\%$)
   - REV-105: Dialogue vs Narration Imbalance ($>75\\%$ dialogue or $>90\\%$ prose churn)
   - REV-106: Front-Loading Churn Anomaly (Opening chapters 1-3 over-churned vs rest of book)""",
        why_this_way="Authors often get trapped in perfectionist loops rewriting Chapter 1 without progressing on later chapters. Interactive churn heatmaps with dialogue breakdowns provide objective telemetry on editing churn.",
        worldbuilding_relevance="Shows which lore sections underwent the heaviest conceptual overhauls.",
        storytelling_relevance="Identifies problem chapters, major scene excisions, and dialogue restructuring hotspots across drafts.",
        writing_relevance="Helps authors step away from perfectionist over-editing, review narrative cuts, and balance manuscript pacing.",
        subfeatures=[
            {"name": "Interactive Studio Dashboard", "rule": "Generates standalone offline CSP-compliant HTML5 heatmap with sorting, filters, and theme toggle.", "example": "arcanum revision-heatmap Manuscript/ --html dist/heatmap.html --open"},
            {"name": "Dialogue vs Prose Split", "rule": "Measures spoken character dialogue churn separately from narrative exposition.", "example": "arcanum revision-heatmap Draft-02 Draft-01"},
            {"name": "6-Tier Telemetry Suite", "rule": "Flags REV-101 to REV-106 with craft advisory guidance.", "example": "arcanum revision-heatmap --threshold 2.5"},
        ],
        extension_guide="""Run interactive revision heatmap studio:
```bash
arcanum revision-heatmap Manuscript/ --html heatmap.html --open
arcanum revision-heatmap Manuscript/Draft-02 Manuscript/Draft-01
```""",
        advisory_guidance=[
            {"pattern": "REV-101: High Revision Density (>3x average or >120% churn)", "option_a": "Perform fresh developmental outline review of the scene's core goal", "option_b": "Lock the chapter and proceed to drafting subsequent chapters", "option_c": "Accept high churn as necessary stylistic exploration"},
            {"pattern": "REV-103: Heavy Narrative Cut (>40% baseline deleted)", "option_a": "Verify no unresolved plot threads or dropped character introductions", "option_b": "Archive cut prose chunks in a Scraps/ folder for future recycling", "option_c": "Accept cut as intentional tightening"},
            {"pattern": "REV-105: Dialogue vs Narration Imbalance (>75% dialogue churn)", "option_a": "Review narrative blocking and sensory details to ensure they match updated character dialogue", "option_b": "Accept as targeted dialogue voice polish pass", "option_c": "Examine if unspoken subtext should replace direct speech"},
        ],
    ),

    "draft_manager": EngineSpec(
        name="draft_manager",
        category=EngineCategory.CORE,
        title="Manuscript Draft & Revision Lineage Manager",
        description="Full-lifecycle draft versioning, granular chapter scoping, milestone tracking, immutability locking, and offline visual dashboard",
        module_name="lib.draft_manager",
        cli_command="draft",
        aliases=["drafts", "versioning", "draft-manager"],
        studio_tab="Editor",
        logic_documentation="Manages linear and experimental draft branching, selective chapter importing, active draft manifest switching, and draft freeze/locking with standalone HTML lineage DAG visualizations.",
        scientific_logic="""1. Draft Lineage Directed Acyclic Graph (DAG):
   Models revision history as a tree graph $G = (V, E)$ where vertices $V$ represent discrete draft snapshots (Draft-01, Draft-02, Draft-02-alt) and directed edges $E$ record parentage $(v_{\\text{parent}}, v_{\\text{child}})$.
2. Granular Chapter Set Inclusion & Exclusion:
   $$C_{\\text{new}} = (C_{\\text{source}} \\cap I) \\setminus X$$
   where $I$ is the inclusion range and $X$ is the exclusion range.""",
        why_this_way="Writers need seamless, risk-free revision branching to explore alternate endings or conduct developmental edits without corrupting current drafts.",
        worldbuilding_relevance="Enables parallel lore testing across alternate novel drafts.",
        storytelling_relevance="Allows writers to safely fork developmental edits and track milestone progression (Alpha, Beta, ARC, Line-Edit, Proof).",
        writing_relevance="Offers visual lineage graphs, active draft indicators, and immutability locks on frozen drafts.",
        subfeatures=[
            {"name": "Visual Lineage DAG Exporter", "rule": "Renders standalone offline HTML visual lineage tree and hero dashboard.", "example": "arcanum draft --html dist/drafts.html"},
            {"name": "Granular Chapter Slicing", "rule": "Forks drafts with selective chapter ranges.", "example": "arcanum draft fork Draft-02 --source Draft-01 --chapters 1-5,8 --exclude 4"},
            {"name": "Draft Immutability Lock", "rule": "Safeguards finalized/archived drafts against accidental edits.", "example": "arcanum draft lock Draft-01 --notes 'Initial Alpha complete'"},
        ],
        extension_guide="""Manage drafts from CLI:
```bash
arcanum draft tree
arcanum draft fork Draft-02 --milestone Beta
arcanum draft switch Draft-02
arcanum draft lock Draft-01
arcanum draft --html dist/drafts_dashboard.html
```""",
        advisory_guidance=[
            {"pattern": "Multiple active workstreams detected without designated active draft", "option_a": "Activate the most recent revision with 'arcanum draft switch'", "option_b": "Lock legacy drafts with 'arcanum draft lock'", "option_c": "Maintain parallel branch for alternate narrative paths"},
        ],
    ),
}

__all__ = ["ENGINES"]

