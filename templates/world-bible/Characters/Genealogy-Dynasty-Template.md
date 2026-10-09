---
fileClass: GenealogyHouse
type: genealogy_house
name: "<% tp.file.title %>"
house_name: "House Valdoria"
tags:
  - world/genealogy
  - world/faction
seat_of_power: "[[Locations/Location-Template|High-Sanctuary]]"
founding_year: 840
fc-date: "0840-01-01"
fc-calendar: "Valdorian Solar-Lunar Standard"
fc-category: "Genealogy"
succession_law: "Agnatic-Cognatic Primogeniture"
current_head: "[[Characters/Character-Template|Lord-Alden-Valdoria]]"
heir_apparent: "[[Characters/Character-Template|Protagonist]]"
cadet_branches:
  - "House Valdoria-Ost"
  - "House Valdoria-Soren"
allied_houses:
  - "House Silverthorn"
  - "House Blackwood"
rival_houses:
  - "House Kaelen-Grip"
motto: "Steel in Silence, Light in Truth"
heraldry: "A silver falcon clutching a sapphire compass on an obsidian field"
---

# <% tp.file.title %> — Dynastic House & Lineage

> [!NOTE] ⚠️ EDUCATIONAL TEMPLATE (AI-GENERATED)
> **Notice**: This template was AI-generated for educational demonstration and craft guidance within the Ars Arcanum operating system. It is strictly non-commercial and provided solely to demonstrate system features, mechanical schemas, and engine capabilities. Authors should replace placeholder values with their original worldbuilding details.

<details>
<summary>💡 <b>Ars Arcanum Engine Guidance & Feature Breakdown (Click to Expand)</b></summary>

### Features Demonstrated in This Template:
- **Succession Claim Roster**: `genealogy` (`arcanum genealogy --succession 'House Valdoria'`) — Generates legitimate inheritance claim rankings under Agnatic/Cognatic Primogeniture, Tanistry, or Ultimogeniture.
- **Wright Inbreeding Calculator**: `genealogy` (`arcanum genealogy --inbreeding-check 'Lord-Alden-Valdoria'`) — Calculates Wright's coefficient of relationship and consanguinity to prevent accidental genetic contradictions.
- **Charted Roots & Canvas Roots Integration**: `charted-roots` — Automatically builds interactive visual family trees on Obsidian Canvas directly from note frontmatter.
- **Mermaid Pedigree Exporter**: `genealogy` (`arcanum genealogy --mermaid 'House Valdoria'`) — Renders automatic visual family tree diagrams and Ahnentafel ancestor numbers.

### How to Use for Your Projects:
1. Define the `succession_law` and list the primary dynastic line.
2. In each individual character note, set `parents: [...]`, `spouses: [...]`, and `house: "[[House-Name]]"`.
3. Open with **Charted Roots** or run `arcanum genealogy` to generate pedigree lineage charts.
</details>

---

## 1. Dynastic Lineage & Succession Order

```mermaid
graph TD
    A[Lord Vaelen Valdoria I <br/>*840–912*] --> B[Lord Corren Valdoria <br/>*908–975*]
    B --> C[Lord Alden Valdoria <br/>*Current Head*]
    B --> D[Lady Mirelle Valdoria <br/>*Cadet Founder*]
    C --> E[Protagonist / Heir Apparent <br/>*b. 1240*]
    C --> F[Lady Sorsha Valdoria <br/>*b. 1244*]
    D --> G[Baron Rayner of Ost <br/>*Cadet Heir*]
```

### Official Succession Queue:
1. **First Heir**: [[Characters/Character-Template|Protagonist]] (Eldest true-born child)
2. **Second Heir**: [[Characters/Character-Template|Lady-Sorsha-Valdoria]] (Second-born daughter)
3. **Third Heir**: [[Characters/Character-Template|Baron-Rayner-of-Ost]] (Cadet branch claim)

---

## 2. Dynastic Alliances, Marriages & Feuds

| House | Relationship | Strategic Treaty / Blood Covenant |
| :--- | :--- | :--- |
| **House Silverthorn** | Sworn Ally | Bound by the Treaty of the Three Spires (1180); mutual military defense pact. |
| **House Blackwood** | Neutral Trade Partner | Controls grain trade corridors through the Eastern March; non-aggression agreement. |
| **House Kaelen-Grip** | Bitter Blood Feud | Century-long dispute over the silver mines of Whispering Vale. |

---

## 3. Notable Historical Relics & Ancestral Assets
- **Ancestral Blade**: [[Artifacts/Artifact-Relic-Template|The-Silver-Verdict]] (Forged in 920 during the First Cataclysm).
- **Citadel & Fortifications**: [[Locations/Location-Template|High-Sanctuary]] — Imperial fortress built into the granite spires.
- **Primary Source of Wealth**: Aether-refining monopolies and toll rights along the Silver River.

---

## 4. Roster of Living Scions & House Members
```dataview
TABLE role as "Role", born as "Birth Year", title as "Title", current_location as "Location"
FROM #world/character
WHERE house = this.file.link OR contains(house, "Valdoria")
SORT born ASC
```
