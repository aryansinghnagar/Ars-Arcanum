# The 16 Canonical Narrative Paradigms & Structural Scaffolding Guide

> [!NOTE] ⚠️ EDUCATIONAL TEMPLATE (AI-GENERATED)
> **Notice**: This template was AI-generated for educational demonstration and craft guidance within the Ars Arcanum operating system. It is strictly non-commercial and provided solely to demonstrate system features, mechanical schemas, and engine capabilities. Authors should replace placeholder values with their original story structure plans.

<details>
<summary>💡 <b>Ars Arcanum Engine Guidance & Feature Breakdown (Click to Expand)</b></summary>

### Features Demonstrated in This Guide:
- **16 Built-in Presets**: `manuscript_scaffold` (`arcanum scaffold MyNovel/Book-01 --structure heros_journey`) — Scaffolds complete novel directory trees pre-seeded with act divisions and beat markers across 16 canonical frameworks.
- **Custom Divisions**: `manuscript_scaffold` (`arcanum scaffold MyNovel/Book-01 --structure custom --divisions 'Prologue,Part-I,Part-II,Epilogue'`) — Scaffolds arbitrary named division layouts with strict regex validation.
- **Structure Preset Introspection**: `manuscript_scaffold` (`arcanum scaffold list`, `arcanum scaffold info kishotenketsu`) — Inspects all registered structural presets and target percentage curves.
- **Multi-Paradigm Beat Mapper**: `structure` (`arcanum structure Manuscripts/Book-01 --paradigm three_act`) — Evaluates narrative milestone percentages (Hook at 1%, Inciting Incident at 12%, Climax at 90%) across any selected paradigm.
- **Midpoint Harmony Check**: `structure` (`arcanum structure Manuscripts/Book-01 --midpoint-check`) — Verifies that the active reversal occurs within the 48%–52% milestone envelope.

### How to Use for Your Projects:
1. Choose the narrative framework that best fits your story's genre, pacing, and philosophical theme.
2. Run `arcanum scaffold Manuscripts/MyNovel --preset <preset_key>` to scaffold the act/chapter folders.
3. Run `arcanum structure Manuscripts/MyNovel` anytime during drafting to check for structural sagging or pacing drag.
</details>

---

## 🏛️ Comprehensive Matrix of All 16 Built-in Paradigms

| Preset Key | Paradigm Name & Origin | Primary Focus & Genre Suitability | Core Division Blueprint |
| :--- | :--- | :--- | :--- |
| `three_act` | **Classic Three-Act Structure** (Aristotle / Syd Field) | Universal commercial fiction, thrillers, fantasy | `Act_I` (Setup) $\to$ `Act_II` (Confrontation) $\to$ `Act_III` (Resolution) |
| `heros_journey` | **The Hero's Journey (Monomyth)** (Campbell / Vogler) | Epic fantasy, mythic adventure, space opera | `Departure` $\to$ `Initiation` $\to$ `Return` |
| `save_the_cat` | **Save the Cat! Beat Sheet** (Blake Snyder) | Fast-paced commercial thrillers, screenplays | `Act_I-Setup` $\to$ `Act_II-Fun_and_Games` $\to$ `Act_III-Finale` |
| `story_circle` | **Dan Harmon Story Circle** (Harmon) | Episodic character growth, sci-fi, television | `Comfort_Zone` $\to$ `Unfamiliar_World` $\to$ `Return_Path` $\to$ `Transformation` |
| `kishotenketsu` | **Kishōtenketsu (起承転結)** (Classical East Asian) | Mystery, slice-of-life, contemplative fiction | `Ki-Intro` $\to$ `Sho-Dev` $\to$ `Ten-Twist` $\to$ `Ketsu-Reconciliation` |
| `seven_point` | **Seven-Point Story Structure** (Dan Wells) | High-stakes sci-fi, plotting from resolution | `Hook_and_Turn` $\to$ `Midpoint_and_Reversal` $\to$ `Resolution` |
| `fichtean_curve` | **The Fichtean Curve** | Rapid escalating crises, survival thrillers | `Rising_Crises` $\to$ `Climax_and_Resolution` |
| `eight_sequence` | **Eight-Sequence Method** (Frank Daniel) | Film adaptations, tightly paced novels | `Seq_A` through `Seq_H` (8 distinct 10-15k word mini-movies) |
| `freytags_pyramid`| **Freytag's Dramatic Pyramid** (Gustav Freytag) | Classic tragedy, historical drama | `Exposition` $\to$ `Rising_Action` $\to$ `Climax` $\to$ `Falling` $\to$ `Denouement` |
| `mice_quotient` | **MICE Quotient** (Orson Scott Card) | Sci-Fi, mysteries, world explorations | `Milieu` (Place) $\cdot$ `Idea` (Mystery) $\cdot$ `Character` (Identity) $\cdot$ `Event` (Status Quo) |
| `romancing_beat`| **Romancing the Beat** (Gwen Hayes) | Romance, romantic subplots, emotional arcs | `Phase_1-Setup` $\to$ `Phase_2-Falling_Fast` $\to$ `Phase_3-Retreat` $\to$ `Phase_4-Together` |
| `virgins_promise`| **The Virgin's Promise** (Kim Hudson) | Inward journey, creative awakening, self-fulfillment | `Dependent_World` $\to$ `Secret_World` $\to$ `Kingdom_Awakens` |
| `snowflake` | **Snowflake Method** (Randy Ingermanson) | Top-down fractal plotting and expanding | `One_Sentence` $\to$ `Paragraph` $\to$ `Character_Sheets` $\to$ `Scene_List` |
| `parallel_pov` | **Parallel / Multi-POV Matrix** | Epic multi-threaded fantasy (GRRM style) | `POV_Track_A` $\parallel$ `POV_Track_B` $\parallel$ `POV_Track_C` $\to$ `Convergence` |
| `episodic` | **Episodic / Picaresque** | Serial adventures, sword & sorcery, procedural | `Episode_01` through `Episode_N` (Self-contained arcs) |
| `nonlinear` | **Nonlinear / Fragmented** | Literary fiction, memory mysteries, time travel | `Braided_Timelines` $\cdot$ `Framing_Narrative` $\cdot$ `Flashback_Core` |

---

## 📐 Deep Dive: Kishōtenketsu (Conflict-Free Twist Dynamics)
Unlike Western conflict-driven models that rely on opposing antagonistic forces, Kishōtenketsu structures narrative tension around an unexpected contextual juxtaposition:

```
[起 Ki: Introduction] ───> [承 Shō: Expansion] ───> [転 Ten: The Unexpected Twist] ───> [結 Ketsu: Reconciliation]
Establish quiet archive    Describe daily copying    A stranger delivers an ancient       The archive is not a library,
and peaceful town life.    and scholar routines.     star-map from a sunken empire.       but a prison for the stars.
```
