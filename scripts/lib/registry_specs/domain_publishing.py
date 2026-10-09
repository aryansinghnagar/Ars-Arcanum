#!/usr/bin/env python3
"""
Domain Publishing & Preflight Specifications for Ars Arcanum Registry.
"""
from __future__ import annotations

try:
    from lib.registry_base import EngineCategory, EngineSpec
except ImportError:
    from registry_base import EngineCategory, EngineSpec

ENGINES: dict[str, EngineSpec] = {
    "preflight": EngineSpec(
        name="preflight",
        category=EngineCategory.CORE,
        title="Typesetting Preflight Validator",
        description="Print-PDF compliance, image resolution, and trim size validation",
        module_name="lib.preflight",
        cli_command="preflight",
        aliases=["pre-flight", "prepress"],
        studio_tab="Publishing",
        logic_documentation="Validates print-on-demand requirements (Amazon KDP, IngramSpark), spine width calculation based on page count and paper thickness, bleed margins, font embedding, and image DPI.",
        scientific_logic="""1. Print-on-Demand (POD) Spine Width Formulation:
   Spine width $W_{\\text{spine}}$ based on page count $N$ and paper stock caliper (PPI - Pages Per Inch):
   $$W_{\\text{spine}} = \\frac{N}{\\text{PPI}} \\text{ (inches)} = \\frac{N}{2} \\times \\text{Caliper (mm)}$$
   - Cream 55lb (434 PPI): $W = N / 434$ inches
   - White 50lb (500 PPI): $W = N / 500$ inches

2. Signature Page Count & Bleed Bounds:
   Page counts must round up to multiples of 4 (or 6) for physical sheet binding. Cover bleeds require $+0.125\\text{ in}$ ($3.2\\text{ mm}$) margins on all outer edges.""",
        why_this_way="Amazon KDP and IngramSpark reject PDF uploads with incorrect spine widths or low-res images. Preflight validation catches these errors before submission.",
        worldbuilding_relevance="Verifies world map image resolutions for crisp 300+ DPI print reproduction.",
        storytelling_relevance="Calculates final physical book thickness, signature layouts, and spine text fitting.",
        writing_relevance="Catches widow/orphan lines, bad page breaks, and unlinked footnotes before print submission.",
        subfeatures=[
            {"name": "Spine Width Calculator", "rule": "Calculates spine width across KDP and IngramSpark paper types.", "example": "arcanum preflight Manuscript/ --pages 380 --paper cream-55"},
            {"name": "POD Signature Auditor", "rule": "Ensures page counts align to 4-page signatures.", "example": "arcanum preflight Manuscript/"},
        ],
        extension_guide="""Run preflight audit:
```bash
arcanum preflight Manuscript/
```""",
        advisory_guidance=[
            {"pattern": "Page count not multiple of 4/6 (POD signature)", "option_a": "Add blank backmatter note pages to round up", "option_b": "Adjust font leading / margins slightly", "option_c": "Proceed with printer automatic blank insertion"},
        ],
    ),

    "frontmatter_builder": EngineSpec(
        name="frontmatter_builder",
        category=EngineCategory.CORE,
        title="Frontmatter & Backmatter Builder",
        description="Generates copyright, dedication, epigraph, and biographical matter",
        module_name="lib.frontmatter_builder",
        cli_command="matter",
        aliases=["frontmatter", "backmatter", "matter-builder"],
        studio_tab="Publishing",
        logic_documentation="Scaffolds modular frontmatter (half-title, title page, copyright notice, dedication, epigraph, table of contents) and backmatter (about author, teaser chapters, discussion questions).",
        scientific_logic="""1. Standard Editorial Front/Back Matter Architecture:
   Scaffolds industry standard publishing sequences: Half-Title $\\to$ Title Page $\\to$ Copyright / CIP Legal Block $\\to$ Dedication $\\to$ Epigraph $\\to$ Table of Contents $\\to$ Body Chapters $\\to$ Acknowledgments $\\to$ About Author.""",
        why_this_way="Authors often forget required legal copyright notices, CIP data, and ISBN placeholders required for distribution.",
        worldbuilding_relevance="Injects in-universe historical quotes and epigraphs to enrich cosmological lore.",
        storytelling_relevance="Provides structural framing and thematic epigraphs that set chapter tone.",
        writing_relevance="Automates legal copyright notices, CIP data, and acknowledgments.",
        subfeatures=[
            {"name": "Publishing Matter Scaffolder", "rule": "Generates complete frontmatter and backmatter markdown files.", "example": "arcanum matter build Manuscript/"},
            {"name": "Frontmatter Normalizer", "rule": "Standardizes schema keys across legacy chapter files.", "example": "arcanum matter normalize Manuscript/"},
        ],
        extension_guide="""Build frontmatter files:
```bash
arcanum matter build Manuscript/
```""",
        advisory_guidance=[
            {"pattern": "Missing copyright year or ISBN", "option_a": "Scaffold default copyright with current year", "option_b": "Insert placeholder ISBN for proof review", "option_c": "Leave blank for public domain / draft distribution"},
        ],
    ),

    "codex_export": EngineSpec(
        name="codex_export",
        category=EngineCategory.CRAFT,
        title="World Wiki Codex Export",
        description="Compiles world lore notes into a standalone, searchable offline HTML encyclopedia",
        module_name="lib.codex_export",
        cli_command="codex",
        aliases=["codex", "wiki", "export-codex"],
        studio_tab="Publishing",
        logic_documentation="Compiles World Bible markdown files into an ultra-fast, responsive, single-file offline HTML wiki with full-text search, spoiler sliders, and interactive relationship embeds.",
        scientific_logic="""1. Standalone Single-File Static Wiki Generator:
   Bundles all markdown dossiers into a self-contained offline HTML5 file with zero remote CDN dependencies, embedded SVG icons, instant JavaScript client-side search, and interactive spoiler disclosure sliders.""",
        why_this_way="Authors need a way to share companion world wikis with readers, editors, and tabletop RPG players without hosting servers.",
        worldbuilding_relevance="Creates an offline encyclopedia compendium for fans, beta readers, and tabletop GMs.",
        storytelling_relevance="Provides readers with an exploratory lore codex companion.",
        writing_relevance="Enables quick reference lookup of lore notes on tablets and secondary monitors.",
        subfeatures=[
            {"name": "Single-File HTML Wiki Exporter", "rule": "Compiles entire lore vault into a searchable standalone HTML file.", "example": "arcanum codex World/ --html dist/world_codex.html"},
            {"name": "Interactive Spoiler Slider", "rule": "Renders chronological secret reveals tailored to reader progress.", "example": "arcanum codex World/ --spoiler-protection"},
        ],
        extension_guide="""Export static codex:
```bash
arcanum codex World/ -o dist/codex.html
```""",
        advisory_guidance=[
            {"pattern": "Broken wiki link detected during codex compilation", "option_a": "Render link as unlinked text placeholder", "option_b": "Create placeholder stub note in export", "option_c": "Fail compilation in strict mode"},
        ],
    ),

    "omnibus": EngineSpec(
        name="omnibus",
        category=EngineCategory.CORE,
        title="Series Omnibus Compiler",
        description="Compiles multiple book volumes into a unified anthology with volume dividers and unified TOC",
        module_name="lib.omnibus",
        cli_command="omnibus",
        aliases=["omnibus", "anthology", "series-bundle"],
        studio_tab="Publishing",
        logic_documentation="Merges multiple manuscript volumes into a single omnibus edition, standardizing frontmatter, generating multi-volume tables of contents, injecting volume title dividers, and compiling to print-ready PDF and EPUB.",
        scientific_logic="""1. Multi-Volume AST Concatenator & Signature Normalizer:
   Re-indexes chapter sequences ($1..N$), standardizes heading hierarchy, handles volume-level frontmatter, and formats unified multi-book tables of contents.""",
        why_this_way="Publishing complete trilogies or boxed sets requires tedious manual merging and TOC reformatting. The omnibus compiler automates this in one command.",
        worldbuilding_relevance="Bundles complete universe sagas with unified appendices and glossaries.",
        storytelling_relevance="Compiles multi-arc trilogies into cohesive epic anthologies.",
        writing_relevance="Automates anthology compilation for Amazon KDP and IngramSpark distribution.",
        subfeatures=[
            {"name": "Series Omnibus Builder", "rule": "Compiles all volumes in a manuscript directory into one book.", "example": "arcanum omnibus Manuscript/ --pdf dist/Trilogy.pdf"},
            {"name": "Volume Divider Scaffolder", "rule": "Injects full-page volume divider sheets between books.", "example": "arcanum omnibus Manuscript/ --dividers"},
        ],
        extension_guide="""Build omnibus anthology:
```bash
arcanum omnibus Manuscript/ -o dist/Omnibus.pdf
```""",
        advisory_guidance=[
            {"pattern": "Volume numbers out of chronological sequence", "option_a": "Reorder volumes based on manifest configuration", "option_b": "Preserve folder alphabetical sorting", "option_c": "Prompt user for custom volume order"},
        ],
    ),
}

__all__ = ["ENGINES"]
