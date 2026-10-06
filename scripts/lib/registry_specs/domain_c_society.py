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
    # DOMAIN C: CHARACTERS, SOCIETY, CONLANGS, ECONOMY & COMBAT
    # =========================================================================
    "dramatis_personae": EngineSpec(
        name="dramatis_personae",
        category=EngineCategory.CRAFT,
        title="Multi-Volume Dramatis Personae & Universe Cast Matrix",
        description="Cross-volume character profile parser, manuscript POV/mention cross-referencer, lifecycle continuity, and phonetic collision detector",
        module_name="lib.dramatis_personae",
        cli_command="cast",
        aliases=["dramatis-personae", "dramatis", "cast", "characters-cast"],
        studio_tab="Worldbuilding",
        logic_documentation="Parses character dossiers, cross-references manuscript chapter POV screen-times, validates lifecycle states (Alive -> Missing -> Deceased -> Ascended), detects name phonetic collisions (e.g. Jon vs Joram), and exports HTML galleries.",
        scientific_logic="""1. Character Lifecycle State Machine:
   $$\\text{Active / Alive} \\longrightarrow \\text{Missing / Incarcerated} \\longrightarrow \\text{Deceased} \\longrightarrow \\text{Ascended / Legendary}$$
   Catches impossible retroactive mentions of deceased characters in present active scenes without flashback tags.

2. Phonetic Name Collision & Levenshtein Distance:
   For character names $N_1$ and $N_2$ appearing in the same chapter scene:
   $$\\text{Levenshtein}(N_1, N_2) \\le 2 \\quad \\lor \\quad \\text{Soundex}(N_1) = \\text{Soundex}(N_2)$$
   Flags confusingly similar character names (e.g. 'Kaelen' and 'Kaelin') that disorient readers.""",
        why_this_way="Epic fantasies with hundreds of characters frequently suffer from confusingly similar names and accidental continuity revivals of dead characters.",
        worldbuilding_relevance="Maintains comprehensive universe cast matrices across noble houses, factions, and orders.",
        storytelling_relevance="Audits character screen-time, relationship chord networks, and long-term POV absence.",
        writing_relevance="Prevents similar-sounding character names that confuse readers.",
        subfeatures=[
            {"name": "Phonetic Name Collision Auditor", "rule": "Flags similar names using Soundex, Metaphone, and Levenshtein metrics.", "example": "arcanum cast --audit-names"},
            {"name": "POV Screen-Time Balancer", "rule": "Calculates chapter word counts per character perspective.", "example": "arcanum cast Manuscript/ --screen-time"},
            {"name": "HTML Cast Gallery Exporter", "rule": "Exports standalone visual portrait cards with bio and affiliation tags.", "example": "arcanum cast World/ --html dist/cast_gallery.html"},
        ],
        extension_guide="""Define characters in `World/Characters/kaelen_voss.md`:
```yaml
---
name: "Kaelen Voss"
aliases: ["The Shadow Blade", "Kael"]
status: "Alive" # Alive | Missing | Deceased | Ascended
house: "House Voss"
faction: "Silent Hand"
pov: true
eye_color: "Grey-Blue"
handedness: "Right"
---
```""",
        advisory_guidance=[
            {"pattern": "Phonetically similar character names in same scene (e.g. 'Kaelen' and 'Kaelin')", "option_a": "Rename one character with distinct starting consonant", "option_b": "Establish in-universe naming tradition (e.g. cousins named after grandfather)", "option_c": "Retain names with clarifying nicknames / titles"},
        ],
    ),


    "conlang": EngineSpec(
        name="conlang",
        category=EngineCategory.CRAFT,
        title="Conlang Phonotactics & Lexicon",
        description="Phoneme inventory generator, sound-law shift simulator, Leipzig glossing, and constructed vocabulary builder",
        module_name="lib.conlang",
        cli_command="conlang",
        aliases=["conlang", "linguistics", "phonotactics"],
        studio_tab="Worldbuilding",
        logic_documentation="Generates phonotactic syllable structures (CV, CVC, CCV), enforces Sonority Sequencing, models historical sound-shift mutations (Grimm's Law), and parses Leipzig 3-line interlinear glosses.",
        scientific_logic="""1. Syllable Phonotactics & Sonority Sequencing Principle (SSP):
   Syllable template (e.g. $(C_1)(C_2)V(C_3)$). Sonority scale:
   $$\\text{Vowels (5)} > \\text{Glides (4)} > \\text{Liquids (3)} > \\text{Nasals (2)} > \\text{Fricatives (1)} > \\text{Stops (0)}$$
   Onsets must rise in sonority towards nucleus; codas must fall in sonority.

2. Neogrammarian Sound Shift Engine (Grimm's & Verner's Laws):
   Regular regex rewrite rules applied sequentially across ancestral proto-lexicon:
   - Proto-Germanic Grimm's Law: $p \\to f, t \\to \\theta, k \\to h$.
   - Intervocalic Lenition: $V[p, t, k]V \\to V[b, d, g]V$.

3. Leipzig 3-Line Interlinear Glossing Rules:
   - Line 1: Source language text (`Dó-m-un-a k-el-a`)
   - Line 2: Grammatical morpheme gloss (`house-LOC-DEF.SG walk-PST-3SG`)
   - Line 3: Free English translation (`'He walked in the house.'`)""",
        why_this_way="Randomly made-up fantasy words look like keyboard mash and lack cultural authenticity. The conlang engine ensures phonetic harmony, realistic sound shifts across centuries, and structured grammar.",
        worldbuilding_relevance="Creates distinct, culturally grounded naming conventions for characters, places, and relics.",
        storytelling_relevance="Brings linguistic diversity to life; language barriers and translation puzzles create story intrigue.",
        writing_relevance="Generates evocative names and authentic in-universe idioms with phonetic harmony.",
        subfeatures=[
            {"name": "Phonotactic Syllable Generator", "rule": "Generates natural-sounding words adhering to custom phoneme inventories.", "example": "arcanum conlang gen HighElven --count 20"},
            {"name": "Historical Sound Shift Simulator", "rule": "Mutates proto-language roots into modern daughter dialects.", "example": "arcanum conlang mut ProtoElven ModernElven --rules 'p>f, k>h'"},
            {"name": "Leipzig Gloss Parser", "rule": "Parses and validates 3-line interlinear linguistic glosses in lore notes.", "example": "arcanum conlang gloss 'Dó-m-un-a k-el-a'"},
        ],
        extension_guide="""Create a conlang specification in `World/Languages/valyrian.yaml`:
```yaml
conlang:
  name: "High Valyrian"
  phonemes:
    consonants: ["p", "t", "k", "b", "d", "g", "m", "n", "r", "l", "s", "z", "v"]
    vowels: ["a", "e", "i", "o", "u", "y"]
  syllable_template: "CVC"
  sound_shifts:
    - "k > h / _#"
    - "p > f / V_V"
```""",
        advisory_guidance=[
            {"pattern": "Word violates language phonotactic syllable template", "option_a": "Adjust spelling to match phonotactic inventory", "option_b": "Classify word as ancient loanword or foreign dialect term", "option_c": "Retain spelling as an authorial artistic flourish"},
        ],
    ),

    "genealogy": EngineSpec(
        name="genealogy",
        category=EngineCategory.CRAFT,
        title="Dynastic Lineage & Genealogy",
        description="Family tree compilation, succession rank calculator, Wright's inbreeding coefficient, and Mermaid diagrams",
        module_name="lib.genealogy",
        cli_command="genealogy",
        aliases=["genealogy", "lineage", "dynasty"],
        studio_tab="Worldbuilding",
        logic_documentation="Calculates Wright's inbreeding coefficient (F), evaluates succession laws (Salic, Primogeniture, Ultimogeniture, Tanistry, Gavelkind), resolves cadet branch cadency, and exports Mermaid family trees.",
        scientific_logic="""1. Wright's Inbreeding Coefficient $F$:
   $$F = \\sum \\left(\\frac{1}{2}\\right)^{n_1 + n_2 + 1} (1 + F_A)$$
   Where $n_1, n_2$ are generations from each parent back to common ancestor $A$, and $F_A$ is the inbreeding coefficient of ancestor $A$.

2. Succession Law Priority Evaluators:
   - Agnatic (Salic) Primogeniture: Strictly through eldest male lines.
   - Male-Preference Primogeniture: Daughters inherit only if no surviving sons exist.
   - Absolute Cognatic Primogeniture: Eldest child regardless of gender.
   - Ultimogeniture: Youngest child inherits.
   - Tanistry: Noble clan council elects most capable adult heir.
   - Gavelkind: Realm partitioned equally among all surviving heirs.""",
        why_this_way="Dynastic civil wars and succession crises are central to fantasy epics. Automatically computing inheritance claims and inbreeding coefficients prevents plot holes in royal genealogies.",
        worldbuilding_relevance="Builds noble lineages, royal marriage alliances, and inheritance claim hierarchies.",
        storytelling_relevance="Drives succession crises, bastard claims, civil wars, and ancestral destiny arcs.",
        writing_relevance="Keeps generational relationships, honorific titles, and family kinship accurate.",
        subfeatures=[
            {"name": "Succession Claim Roster", "rule": "Calculates claimant rankings under Salic, Cognatic, or Gavelkind laws.", "example": "arcanum genealogy --house 'Voss' --succession salic"},
            {"name": "Wright Inbreeding Calculator", "rule": "Computes coefficient of kinship F across noble marriages.", "example": "arcanum genealogy --inbreeding 'Kaelen' 'Lyra'"},
            {"name": "Mermaid Tree Exporter", "rule": "Compiles family trees into visual Mermaid flowchart markdown.", "example": "arcanum genealogy --house 'Voss' --mermaid"},
        ],
        extension_guide="""Link characters via frontmatter parentage tags:
```yaml
---
name: "Crown Prince Valerius"
house: "House Aethelgard"
father: "King Alden III"
mother: "Queen Eleanor"
birth_year: 1418
succession_status: "Primary Heir"
---
```""",
        advisory_guidance=[
            {"pattern": "Disputed succession claim between multiple primary heirs", "option_a": "Clarify legal succession law precedence", "option_b": "Use the disputed claim as the catalyst for dynastic civil war", "option_c": "Retain ambiguity as a central plot mystery"},
        ],
    ),

    "factions": EngineSpec(
        name="factions",
        category=EngineCategory.CRAFT,
        title="Geopolitical Factions & Diplomacy",
        description="Diplomatic relation matrices, tension paradox detection, alliance networks, and Lanchester square-law",
        module_name="lib.factions",
        cli_command="faction",
        aliases=["faction", "factions", "diplomacy"],
        studio_tab="Worldbuilding",
        logic_documentation="Evaluates balance-of-power coalitions, diplomatic tension paradoxes, espionage network infiltration, and Lanchester square-law military strength ratios.",
        scientific_logic="""1. Geopolitical Relation Affinity Matrix:
   Relation state $R(A, B) \\in \\{\\text{Allied (+2)}, \\text{Friendly (+1)}, \\text{Neutral (0)}, \\text{Suspicious (-1)}, \\text{Hostile (-2)}, \\text{Active War (-3)}\\}$.

2. Balance-of-Power Coalition Dynamics:
   If faction $X$ military power $P(X) > \\sum_{Y \\ne X} P(Y)$, smaller factions form balancing coalitions:
   $$\\text{Coalition Affinity } C(A, B) \\propto P(\\text{Hegemon}) - R(A, B)$$

3. Diplomatic Paradox Detection:
   Flags triangular intransitivities: $A$ allied with $B$, $B$ allied with $C$, but $A$ at war with $C$ (triggers diplomatic treaty crisis).""",
        why_this_way="Political intrigue narratives thrive on complex alliances, trade embargoes, and proxy conflicts.",
        worldbuilding_relevance="Structures geopolitical factions, noble houses, knightly orders, and shadow syndicates.",
        storytelling_relevance="Powers political intrigue, betrayal, treaty negotiations, and shifting war alliances.",
        writing_relevance="Informs court dialogue, diplomatic etiquette, and heraldic protocol.",
        subfeatures=[
            {"name": "Diplomatic Paradox Sweeper", "rule": "Finds conflicting treaty obligations and proxy war traps.", "example": "arcanum faction World/ --audit-treaties"},
            {"name": "Alliance Matrix Exporter", "rule": "Exports color-coded diplomatic relation matrix.", "example": "arcanum faction World/ --html dist/diplomacy.html"},
        ],
        extension_guide="""Define factions in `World/Factions/iron_covenant.yaml`:
```yaml
faction:
  name: "Iron Covenant"
  type: "Military Theocracy"
  power_index: 85
  relations:
    "Silver Guild": "Hostile"
    "Crown Coalition": "Allied"
    "Shadow Synod": "Active War"
```""",
        advisory_guidance=[
            {"pattern": "Faction simultaneously marked as active ally and at war", "option_a": "Update relationship to formal state of war or truce", "option_b": "Frame as a covert proxy conflict under public alliance", "option_c": "Retain as a fragile political double-game"},
        ],
    ),

    "economy": EngineSpec(
        name="economy",
        category=EngineCategory.CRAFT,
        title="Macroeconomics & Currencies",
        description="In-world fiat/specie exchange rates, Purchasing Power Parity (PPP), commodity baskets, and Gresham's Law",
        module_name="lib.economy",
        cli_command="economy",
        aliases=["economy", "currency", "prices"],
        studio_tab="Worldbuilding",
        logic_documentation="Models Gresham's Law (coinage debasement), Purchasing Power Parity (PPP) commodity price baskets, trade arbitrage margins, and fractional reserve promissory notes.",
        scientific_logic="""1. Gresham's Law & Coinage Debasement:
   When government debases coinage silver content from $\\text{Ag}_1$ to $\\text{Ag}_2 < \\text{Ag}_1$, bad money drives out good:
   $$\\text{Velocity}(\\text{Debased}) \\gg \\text{Velocity}(\\text{Pure}), \\quad \\text{Hoarding Rate } H \\propto (\\text{Ag}_1 - \\text{Ag}_2)$$

2. Purchasing Power Parity (PPP) & Commodity Basket Index:
   Price level $P$ derived from canonical basket (1 bushel wheat, 1 gallon ale, 1 wool cloak, 1 iron horseshoe):
   $$P_{\\text{region}} = \\sum_{i=1}^m w_i \\cdot p_i, \\quad \\text{Exchange Rate } E(A, B) = \\frac{P_A}{P_B}$$

3. Trade Route Arbitrage & Transport Costs:
   Commodity price gap between origin $O$ and market $M$: $\\Delta P = P_M - P_O - \\text{Carriage Cost} - \\text{Tariffs}$. Arbitrage occurs when $\\Delta P > 0$.""",
        why_this_way="Fantasy economies often feature runaway inflation or wildly unrealistic pricing (e.g. an inn room costing more than a warhorse). Grounding prices in agricultural labor and commodity baskets creates economic coherence.",
        worldbuilding_relevance="Establishes currency exchange rates, guild price-fixing, tax burdens, and black markets.",
        storytelling_relevance="Economic inequality, debt, tariffs, and contraband smuggling fuel plot stakes and character motivations.",
        writing_relevance="Provides realistic pricing for tavern meals, horse rentals, sword forging, and carriage fares.",
        subfeatures=[
            {"name": "Commodity Price Calculator", "rule": "Calculates realistic historical purchasing power and trade goods prices.", "example": "arcanum economy --price 'Warhorse' --region 'Borderlands'"},
            {"name": "Coinage Debasement Simulator", "rule": "Simulates inflation and coin clipping economic crises.", "example": "arcanum economy --debase 'Silver Crown' --silver-loss 25%"},
        ],
        extension_guide="""Define currencies and prices in `World/Economy/currencies.yaml`:
```yaml
currencies:
  - name: "Imperial Gold Sovereign"
    specie_mass_g: 8.5
    purity: 0.92 # 22k gold
    exchange_to_copper: 240
  - name: "Silver Mark"
    specie_mass_g: 12.0
    purity: 0.85
    exchange_to_copper: 20
commodity_basket:
  loaf_bread_copper: 1
  ale_flagon_copper: 2
  riding_horse_copper: 2400
```""",
        advisory_guidance=[
            {"pattern": "Extreme commodity price disparity across open border markets", "option_a": "Rebalance prices toward equilibrium considering carriage costs", "option_b": "Explain gap by wartime blockade, banditry, or guild monopolies", "option_c": "Retain disparity to emphasize regional isolation"},
        ],
    ),

    "tactical_sim": EngineSpec(
        name="tactical_sim",
        category=EngineCategory.CRAFT,
        title="Tactical Skirmish & Battle Simulator",
        description="Lanchester linear and square-law combat models, terrain modifiers, morale decay, and casualty simulation",
        module_name="lib.tactical_sim",
        cli_command="sim battle",
        aliases=["battle", "sim", "combat", "tactical"],
        studio_tab="Worldbuilding",
        logic_documentation="Simulates Lanchester linear and square-law combat dynamics, terrain modifiers (castle walls, dense forest, river crossings), unit morale rout thresholds, and blow-by-blow narrative choreography logs.",
        scientific_logic="""1. Lanchester Linear Law (Ancient Aimless / Melee Duels):
   $$\\frac{dx}{dt} = -\\beta y, \\quad \\frac{dy}{dt} = -\\alpha x \\quad \\Longrightarrow \\quad \\alpha(x_0^2 - x^2) = \\beta(y_0^2 - y^2)$$

2. Lanchester Square Law (Ranged Targeted Fire / Modern Arms):
   $$\\frac{dx}{dt} = -\\beta y, \\quad \\frac{dy}{dt} = -\\alpha x \\quad \\Longrightarrow \\quad \\alpha(x_0^2 - x^2) = \\beta(y_0^2 - y^2)$$
   Concentration of force scales quadratically: 2,000 archers defeating 1,000 archers retain $\\sqrt{2000^2 - 1000^2} \\approx 1,732$ survivors (only 268 casualties).

3. Morale Thresholds & Rout Mechanics:
   Units rout when casualties exceed discipline threshold (Militia $15\\%$, Veteran Infantry $35\\%$, Elite Guard $60\\%$), multiplying retreating casualties threefold due to rearguard collapse.""",
        why_this_way="Authors often depict heroic underdogs wiping out massive armies without explaining tactical terrain advantages or force multipliers.",
        worldbuilding_relevance="Determines realistic army sizes, siege durations, supply requirements, and military logistics.",
        storytelling_relevance="Choreographs dramatic duels and large-scale battle turning points with tactical realism.",
        writing_relevance="Supplies visceral combat beats: weapon reach advantages, shield bracing, fatigue, armor dents.",
        subfeatures=[
            {"name": "Lanchester Battle Resolver", "rule": "Simulates skirmishes and sieges with terrain and ranged multipliers.", "example": "arcanum sim battle --force-a 5000 --force-b 3000 --fortified"},
            {"name": "Choreography Beat Generator", "rule": "Produces narrative chronological log of cavalry flanking and rout moments.", "example": "arcanum sim battle --narrative-log"},
        ],
        extension_guide="""Run a battle simulation from CLI:
```bash
arcanum sim battle --force-a 1200 --force-b 800 --terrain mountain-pass --flank
```""",
        advisory_guidance=[
            {"pattern": "Small infantry militia defeats superior armored cavalry in open field without terrain advantage", "option_a": "Add terrain bottleneck (mud, pikes, trenches) to justify victory", "option_b": "Ground victory via surprise flanking, magical artillery, or cavalry panic", "option_c": "Retain outcome as heroic against-all-odds underdog victory"},
        ],
    ),

    "magic_system": EngineSpec(
        name="magic_system",
        category=EngineCategory.CRAFT,
        title="Magic System Constraints",
        description="Brandon Sanderson's Three Laws of Magic, mana conservation, sympathetic backlash, and caster fatigue tier validator",
        module_name="lib.magic_system",
        cli_command="magic-check",
        aliases=["magic-report", "magic", "arcana", "spells"],
        studio_tab="Worldbuilding",
        logic_documentation="Evaluates magic systems against Brandon Sanderson's Three Laws of Magic, tracks energy conservation, calculates sympathetic backlash, and monitors caster fatigue tier limits.",
        scientific_logic="""1. Brandon Sanderson's Three Laws of Magic:
   - First Law: An author's ability to solve problems with magic in a satisfying way is directly proportional to how well the reader understands said magic.
   - Second Law: Limitations > Powers (Weaknesses, costs, and failure modes create dramatically compelling conflict).
   - Third Law: Expand what you already have before you add something new (deep combinatorial extrapolation of existing magic axioms).

2. Thermodynamic Energy Conservation & Sympathetic Backlash:
   Magic cannot create energy from void; it transforms or transfers energy:
   $$\\Delta E_{\\text{spell}} = E_{\\text{source}} - \\text{Heat Dissipation Loss} - \\text{Backlash Strain}$$
   Casting kinetic energy requires thermal or chemical absorption; caster blood chills or veins burn as metabolic price.

3. Caster Fatigue Tier State Machine:
   $$\\text{Tier 1 (Effortless)} \\longrightarrow \\text{Tier 2 (Straining)} \\longrightarrow \\text{Tier 3 (Exhaustion / Epistaxis)} \\longrightarrow \\text{Tier 4 (Arcane Burnout / Coma)}$$""",
        why_this_way="Soft magic used to solve plot climaxes feels unearned and cheap. Hard magic with rigorous costs and limitations creates gripping puzzle-solving tension.",
        worldbuilding_relevance="Integrates arcane arts into society, military doctrine, education, and economy.",
        storytelling_relevance="Ensures magic creates satisfying problem-solving tension rather than unearned convenience.",
        writing_relevance="Provides visceral somatic magic details: burning blood, glowing glyphs, mana chills, spell exhaustion.",
        subfeatures=[
            {"name": "Sanderson Three Laws Auditor", "rule": "Checks whether magical solutions in climaxes were properly foreshadowed.", "example": "arcanum magic-check Manuscript/ --sanderson"},
            {"name": "Arcane Cost & Backlash Ledger", "rule": "Tracks spell energy accounting and somatic caster costs across scenes.", "example": "arcanum magic-report World/ --costs"},
        ],
        extension_guide="""Define magic axioms in `World/MagicSystems/blood_alchemy.yaml`:
```yaml
magic_system:
  name: "Blood Alchemy"
  type: "Hard Arcane"
  axioms:
    - "Transmutation requires equivalent mass in organic substrate"
    - "Caster experiences metabolic fever proportional to transformed mass"
  limitations:
    - "Cannot transmute noble metals (gold, silver)"
    - "Requires direct somatic skin contact"
  costs:
    fatigue_burn_rate: "Medium"
    backlash_risk: "High upon concentration loss"
```""",
        advisory_guidance=[
            {"pattern": "Spell cast without required reagent or exceeding caster tier", "option_a": "Enforce standard spell failure or severe magical backlash", "option_b": "Frame as a dangerous life-force sacrifice or divine breakthrough", "option_c": "Permit the surge as a pivotal dramatic miracle"},
        ],
    ),
}

__all__ = ["ENGINES"]
