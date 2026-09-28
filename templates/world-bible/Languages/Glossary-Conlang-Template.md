---
type: language
name: "<% tp.file.title %>"
aliases:
  - "Valdorian High Runic"
  - "Old Scriptorian"
tags:
  - world/language
  - status/active
language_family: "Proto-Valdorian"
spoken_by: "[[Factions/Faction-Template|Order-of-the-Silver-Dawn]], Monastic Scribes of [[Locations/Location-Template|High-Sanctuary]]"
status: Liturgical
writing_system: "Linear Silver Runic Script"
consonants: [p, t, k, b, d, g, s, z, m, n, l, r, v, f, th, sh]
vowels: [a, e, i, o, u, ae, au]
syllable_structures: ["CV", "CVC", "CCV", "V", "VC"]
forbidden_clusters: ["pw", "tl", "sr", "kp", "bn"]
sonority_hierarchy: "Vowels > Glides (w, j) > Liquids (l, r) > Nasals (m, n) > Fricatives (f, v, s, z) > Stops (p, t, k, b, d, g)"
stress_rule: "penultimate" # initial, penultimate, ultimate
sound_changes:
  - "p > f / V_V (Intervocalic lenition)"
  - "k > ch / _[e,i] (Palatalization before front vowels)"
  - "m > n / _# (Word-final nasal neutralization)"
---

# <% tp.file.title %> — Conlang Phonology & Lexicon

> [!NOTE] ⚠️ EDUCATIONAL TEMPLATE (AI-GENERATED)
> **Notice**: This template was AI-generated for educational demonstration and craft guidance within the Ars Arcanum operating system. It is strictly non-commercial and provided solely to demonstrate system features, mechanical schemas, and engine capabilities. Authors should replace placeholder values with their original worldbuilding details.

<details>
<summary>💡 <b>Ars Arcanum Engine Guidance & Feature Breakdown (Click to Expand)</b></summary>

### Features Demonstrated in This Template:
- **Phonotactic Syllable Generator**: `conlang` (`arcanum conlang generate --template CVC --count 20`) — Enforces sonority sequencing hierarchies and filters illegal consonant clusters.
- **Historical Sound Shift Simulator**: `conlang` (`arcanum conlang mutate --rules "p>f/V_V"`) — Simulates diachronic sound shifts (Grimm's / Verner's law style mutations) across daughter languages.
- **Leipzig Gloss Parser**: `conlang` (`arcanum conlang gloss "val-aen ther-a"`) — Standardizes interlinear morphological morpheme annotations and grammatical case markers.
- **Glossary Compiler & Dramatis Personae Indexer**: `concordance` (`arcanum concordance Manuscripts/Book-01 -w World-Bible/`) — Compiles alphabetized in-world glossaries with chapter citations into publication backmatter.

### How to Use for Your Projects:
1. Define your language's consonant and vowel inventories, syllable templates, and forbidden consonant clusters.
2. Specify historical `sound_changes` to evolve ancient liturgical root words into modern vernacular slang.
3. Populate the Lexicon Table—terms defined here automatically link into your manuscript glossary.
</details>

> *"Valaen thera sil-moran — Through silver and silence, the truth endures."*

---

## 1. Phonology, Phonotactics & Sonority Rules
- **Syllable Canonical Formula**: $(\text{C}_1)(\text{C}_2)\text{V}(\text{C}_3)$ where $\text{C}_1$ must have lower sonority than $\text{C}_2$.
- **Phonetic Aesthetics**: Crisp, dental stops ($t, d, k$) and flowing liquids ($l, r$) giving a crystalline, rhythmic resonance.
- **Stress Rule**: Stress falls strictly on the penultimate (second-to-last) syllable (e.g. *Val-**DO**-ri-a*, *A-**E**-ther*).

---

## 2. Diachronic Sound Shift Mutations (Old High Valen $\to$ Modern Vernacular)

```mermaid
graph LR
    P[Proto-Root: *Pator*] -->|p > f lenition| M[Modern: *Fathor* (Father)]
    K[Proto-Root: *Kirke*] -->|k > ch palatalization| N[Modern: *Chirche* (Conduit)]
    G[Proto-Root: *Geldam*] -->|Final Nasal Shift| O[Modern: *Geldan* (Silver Coin)]
```

---

## 3. Essential Lexicon & Vocabulary Matrix

| Conlang Term | Part of Speech | Pronunciation (IPA) | English Definition | Cultural & Story Connotation |
| :--- | :--- | :--- | :--- | :--- |
| **Vael** | Noun / Root | /ˈvaɪl/ | Pure Aether / Breath | The divine spark animating conscious minds. |
| **Theron** | Noun | /ˈθɛ.rɒn/ | Guardian of the Seal | High military-scholastic title within the Order. |
| **Kaelis** | Adjective | /ˈkeɪ.lɪs/ | Shattered / Disgraced | Applied to houses stripped of their ancestral banners. |
| **Sil-moran** | Noun (Compound)| /sɪl.ˈmɔː.ræn/ | Silver Vigil | The silent night watch before a major military offensive. |
| **Aethelgard** | Proper Noun | /ˈeɪ.θəl.ɡɑːrd/ | High Mountain Bastion | The sovereign world-continent. |

---

## 4. Morphological Affixes & Compounding Grammar
- **Prefix `Sil-`**: Denotes purity, metal, or divine protection (*Sil-dran* = Shield of Light).
- **Suffix `-val`**: Indicates mastery or active agency (*Weave-val* = Weaver/Sorcerer).
- **Suffix `-aen`**: Plural collective or sacred community (*Valdoria-aen* = The people of Valdoria).

---

## 5. Common Proverbs & Dialogue Curses
- **Ceremonial Greeting**: *"Vaelen vos thera"* (*May the breath of light guide your path*).
- **Battle Rallying Cry**: *"In ferro veritas, in aether salus"* (*In iron truth, in aether salvation*).
- **Highland Curse**: *"Kaelis-mor!"* (*May your hearth grow cold and hollow*).
