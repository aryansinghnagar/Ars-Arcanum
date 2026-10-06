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
    # DOMAIN G: PUBLISHING, PREFLIGHT & TYPESETTING
    # =========================================================================
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
        extension_guide="""Export World Codex:
```bash
arcanum codex World/ --html dist/codex.html
```""",
        advisory_guidance=[
            {"pattern": "World notes contain major late-story spoiler revelations", "option_a": "Enable reader spoiler slider to hide late-book lore", "option_b": "Segment secrets into GM/Author-only codex section", "option_c": "Export full unredacted codex for author reference"},
        ],
    ),

    "omnibus": EngineSpec(
        name="omnibus",
        category=EngineCategory.CORE,
        title="Series Omnibus Compiler",
        description="Multi-volume master series compiler with unified Dramatis Personae and master timeline",
        module_name="lib.omnibus",
        cli_command="omnibus",
        aliases=["compile-omnibus", "series-omnibus", "omnibus"],
        studio_tab="Publishing",
        logic_documentation="Compiles multi-volume book series into deluxe single-volume omnibus editions with unified Dramatis Personae, master timeline appendices, and cross-volume continuity harmonization.",
        scientific_logic="""1. Multi-Volume Series Compilation Pipeline:
   Merges multiple manuscript volumes into a single master Typst or EPUB3 edition with unified frontmatter, interstitial 'Story So Far' recaps, and master series concordance.""",
        why_this_way="Creating omnibus box sets manually requires hours of error-prone copy-pasting and renumbering.",
        worldbuilding_relevance="Unifies lore glossaries across an entire trilogy or multi-book saga.",
        storytelling_relevance="Ensures smooth inter-book reading with 'The Story So Far' interstitial recaps.",
        writing_relevance="Formats deluxe Typst and EPUB3 box sets with persistent offline bookmarks.",
        subfeatures=[
            {"name": "Series Omnibus Builder", "rule": "Compiles multi-volume series into deluxe omnibus editions.", "example": "arcanum omnibus Universe/ --html dist/omnibus.html"},
            {"name": "Cross-Book Interstitial Recap Generator", "rule": "Synthesizes 'Story So Far' transitions between volumes.", "example": "arcanum omnibus Universe/ --generate-recaps"},
        ],
        extension_guide="""Compile series omnibus:
```bash
arcanum omnibus Universes/Eldoria/ --output dist/eldoria_trilogy.pdf
```""",
        advisory_guidance=[
            {"pattern": "Inconsistent term definitions across Book 1 and Book 3 in omnibus compilation", "option_a": "Harmonize to latest canonical definition in master glossary", "option_b": "Annotate term evolution as historical in-universe linguistic shift", "option_c": "Retain volume-specific glossaries in individual book sections"},
        ],
    ),

    "resonance": EngineSpec(
        name="resonance",
        category=EngineCategory.CORE,
        title="Universal Resonance Mesh & Cross-Domain Synthesizer",
        description="Deterministic cross-domain knowledge graph, causal cascade simulation, and creative spark bridges linking all 50 engines",
        module_name="lib.resonance",
        cli_command="resonance",
        aliases=["mesh", "cascade", "spark", "bridge", "ecosystem", "synergy"],
        studio_tab="Worldbuilding",
        logic_documentation="Unifies all 50 Ars Arcanum engines across 5 core domain pillars into a deterministic, bi-directional knowledge graph with multi-hop causal cascading and structural isomorphism generators.",
        scientific_logic="""1. Universal Domain Mesh Topology & Graph Invariants:
   Represents domain variables, entities, and craft rules as typed nodes in a bi-directional knowledge graph $G = (V, E)$ partitioned across 5 Domain Pillars:
   - Cosmology & Physics, Society & Systems, Narrative & Chronology, Stylistics & Senses, Authoring OS.
   Edge relations $r \\in \\{\\text{causally\\_drives}, \\text{constrains}, \\text{isomorphic\\_to}, \\text{manifests\\_in}, \\text{economically\\_impacts}, \\text{lexically\\_influences}, \\text{thematically\\_mirrors}, \\text{sensory\\_grounding\\_for}\\}$.

2. Deterministic Causal Cascade Dynamics:
   Forward-propagating deterministic simulation of parameter shifts:
   $$\\Delta \\text{Param}_0 \\xrightarrow{r_1} \\Delta \\text{Node}_1 \\xrightarrow{r_2} \\Delta \\text{Node}_2 \\dots \\xrightarrow{r_n} \\Delta \\text{Node}_n$$
   Evaluates physical, ecological, economic, diplomatic, and narrative scene tension delta vectors with calculated confidence scores.

3. Structural Isomorphism & Cross-Field Analogy Synthesis:
   Algorithmic mapping between disparate mathematical and conceptual systems (e.g. thermodynamic entropy $\\leftrightarrow$ institutional decay, trophic pyramids $\\leftrightarrow$ magic carrying capacity, hydrological flow $\\leftrightarrow$ monetary velocity).""",
        why_this_way="Narrative depth emerges when world systems, plot events, and character psychology are causally interdependent rather than isolated silos. By deterministically modeling cross-domain connections, authors can explore non-obvious creative sparks and guarantee that physical, economic, and magical changes ripple plausibly through their entire narrative universe.",
        worldbuilding_relevance="Enables holistic world design where planetary cosmology directly shapes climate, agriculture, currency stability, geopolitics, and cultural idioms.",
        storytelling_relevance="Generates multidisciplinary plot hooks and scene complications; guarantees that macro-world events create visceral micro-scene tension.",
        writing_relevance="Supplies concrete sensory palettes and linguistic metaphors grounded in the world's physical and cultural reality.",
        subfeatures=[
            {"name": "Knowledge Mesh Visualizer", "rule": "Generates interactive offline visual graph of all 50 engines and world entities.", "example": "arcanum resonance mesh --html dist/mesh.html"},
            {"name": "Deterministic Causal Cascade", "rule": "Simulates downstream repercussions of parameter changes across disparate fields.", "example": "arcanum resonance cascade astrophysics --param axial_tilt --val 38.5"},
            {"name": "Creative Spark Synthesizer", "rule": "Generates multidisciplinary analogies and plot premises connecting disparate domains.", "example": "arcanum resonance spark astrophysics conlang economy"},
            {"name": "Multi-Hop Conceptual Bridge", "rule": "Finds conceptual pathways connecting two arbitrary craft domains.", "example": "arcanum resonance bridge astrophysics voice"},
            {"name": "Cross-Domain Coherence Audit", "rule": "Validates mutual mathematical and narrative consistency across all engine files.", "example": "arcanum resonance audit"},
        ],
        extension_guide="""Simulate cross-domain parameter cascade:
```bash
arcanum resonance cascade magic_system --param magic_cost --val "high_backlash"
arcanum resonance spark ecology factions scene_mechanics --count 3
arcanum resonance mesh --html dist/knowledge_mesh.html
```""",
        advisory_guidance=[
            {"pattern": "Upstream physical change creates severe downstream economic/military contradiction in manuscript", "option_a": "Apply calculated downstream cascade changes across all lore files for hard realism", "option_b": "Isolate the change as an in-world supernatural anomaly or magical shielding effect", "option_c": "Retain divergence as an intentional surreal mystery or authorial creative choice"},
        ],
    ),

    "tips": EngineSpec(
        name="tips",
        category=EngineCategory.CORE,
        title="Dynamic Intelligent Tips & Knowledge Discovery",
        description="Metadata-rich non-obvious craft wisdom, mathematical insights, and workflow discovery engine across all 51 domain engines",
        module_name="lib.tips",
        cli_command="tip",
        aliases=["tips", "craft-tips", "advice", "hint", "hints", "help-tips"],
        studio_tab="Intelligent Tips",
        logic_documentation="Context-sensitive retrieval engine indexing 120+ masterclass tips across all 51 engines and 117 subfeatures with non-repeating cycle history and user display configuration.",
        scientific_logic="""1. Multidimensional Contextual Ranking & Token Scoring:
   Evaluates user focus vector $\\mathbf{u} = (\\text{engine}, \\text{subfeature}, \\text{keywords}, \\text{context})$ against indexed tip metadata $\\mathbf{t}_i$:
   $$\\text{Score}(\\mathbf{t}_i, \\mathbf{u}) = w_e \\cdot \\mathbb{I}(e_i = u_e) + w_{sf} \\cdot \\text{Sim}(sf_i, u_{sf}) + w_k \\cdot |\\text{Tags}_i \\cap \\text{Toks}(\\mathbf{u})| + w_d \\cdot \\text{DepthWeight}_i$$

2. History Set Differencing & Zero-Stall Rotation:
   Maintains LRU session history $H_s \\subset \\text{Tips}$. Selects from candidate pool $C = \\{\\mathbf{t} \\in \\text{Tips} \\setminus H_s \\mid \\text{Score}(\\mathbf{t}, \\mathbf{u}) \\ge \\theta \\}$, resetting $H_s \\leftarrow \\emptyset$ upon pool exhaustion to ensure continuous variety without immediate repetition.

3. Non-Intrusive Sovereign Presentation Rails:
   Supports zero-friction integration into CLI command banners, Studio Hub contextual banners, Zen Studio drawers, and desktop UI status bars with explicit user opt-out persistence.""",
        why_this_way="Complex creative operating systems contain hundreds of advanced mathematical and narrative features that authors may never discover. Ambient, non-intrusive tips delivered at the precise moment of relevant work bridge the gap between engine capabilities and authorial execution without cognitive overload.",
        worldbuilding_relevance="Surfaces deep scientific rules (e.g. Roche limits, orographic rain shadows, Gresham's law, linguistic vowel shifts) directly during lore creation.",
        storytelling_relevance="Highlights non-linear pacing formulas, dramaturgical scene questions, paradox classifications, and character idiolect metrics while plotting.",
        writing_relevance="Provides actionable prose polish advice, sensory saturation ratios, modal hedge detection, and typography normalization tips in-situ during drafting.",
        subfeatures=[
            {"name": "Contextual Relevance Filter", "rule": "Retrieves high-scoring craft tips matching active engine, subfeature, or draft context.", "example": "arcanum tip climate --subfeature 'Orographic Rain Shadow'"},
            {"name": "Non-Obvious Masterclass Database", "rule": "Curates 120+ deep craft and technical tips across all registered engines.", "example": "arcanum tip --depth masterclass"},
            {"name": "Zero-Stall History Cycling", "rule": "Guarantees fresh, non-repeating tips across repeated requests using history tracking.", "example": "arcanum tip --cycle"},
            {"name": "Sovereign Display Configuration", "rule": "Allows authors to enable, disable, or query tip status persistently.", "example": "arcanum tip --disable / arcanum tip --enable"},
            {"name": "Cross-Platform Ambient Presentation", "rule": "Delivers tips through CLI footers, Studio Hub badges, and Zen Studio drawers.", "example": "arcanum tip --format json"},
        ],
        extension_guide="""Query contextual tips via CLI or Python API:
```bash
# Get tip for active engine
arcanum tip astrophysics

# Get tip for specific subfeature
arcanum tip conlang --subfeature phonology

# Enable or disable tips display
arcanum tip --enable
arcanum tip --disable
arcanum tip --status
```""",
        advisory_guidance=[
            {"pattern": "Author prefers distraction-free interface without tip displays", "option_a": "Disable tips globally via `arcanum tip --disable` or Studio Hub Settings toggle", "option_b": "Restrict tip depth to masterclass-only via configuration", "option_c": "Keep tips enabled in CLI footers only"},
        ],
    ),


    "cosmology": EngineSpec(
        name="cosmology",
        category=EngineCategory.CRAFT,
        title="Deific Pantheon Conflict & Theological Heresy Engine",
        description="Divine domain overlap validator, ritual catalyst auditor, and theological schism / heresy detector",
        module_name="lib.cosmology",
        cli_command="cosmology",
        aliases=["pantheon", "deities", "theology", "heresy"],
        studio_tab="Worldbuilding",
        scientific_logic="""Models theological structures and supernatural authority through formal domain matrices:
1. Divine Domain Hegemony & Overlap:
   Identifies conflicting domain claims (e.g. rival war deities) without hierarchy or territorial boundary treaties.
2. Ritual Catalyst Consistency:
   Validates sacrifice/catalyst prerequisites against world magical and ecological laws.
3. Theological Schisms & Doctrinal Contradictions:
   Detects incompatible religious dogmas between allied factions and divine mandates.
4. Divine Energy Accounting:
   Ensures miracle intervention scales proportionally with worship footprint and prayer density.""",
        why_this_way="Pantheons and religious orders often suffer from accidental domain redundancy or arbitrary miracle power without underlying theological logic. Explicit matrix checks provide rich geopolitical and mythological conflict hooks.",
        worldbuilding_relevance="Constructs believable deific hierarchies, holy orders, religious wars, and sacred taboos.",
        storytelling_relevance="Supplies organic faction conflicts based on holy schisms and competing divine prophecies.",
        writing_relevance="Informs oath formulas, temple architecture descriptions, and priest liturgical dialogue.",
        subfeatures=[
            {"name": "Domain Overlap Conflict Audit", "rule": "Identifies contested deific portfolios across pantheons.", "example": "arcanum cosmology pantheon Worlds/Eldoria"},
            {"name": "Theological Heresy Detector", "rule": "Scans faction dogmas for religious contradictions.", "example": "arcanum cosmology heresy Worlds/Eldoria"},
            {"name": "Ritual Catalyst Validation", "rule": "Verifies sacrifice/relic requirements for divine invocations.", "example": "arcanum cosmology check Worlds/Eldoria"},
        ],
        extension_guide="""Run cosmology checks:
```bash
arcanum cosmology check Worlds/Eldoria --json
```""",
        advisory_guidance=[
            {"pattern": "Overlapping storm domains between two gods", "option_a": "Establish distinct aspects (e.g. oceanic tempest vs desert lightning)", "option_b": "Frame overlap as the mythological origin of an eternal divine war", "option_c": "Unify deities as two regional names for the same cosmic entity"},
        ],
    ),
}

__all__ = ["ENGINES"]
