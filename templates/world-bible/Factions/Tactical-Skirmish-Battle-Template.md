---
type: tactical_battle
name: "<% tp.file.title %>"
battle_name: "The Battle of the Silver Ridge"
tags:
  - world/tactics
  - world/history
location: "[[Locations/Location-Template|Whispering-Vale]]"
date: "1248-09-14"
weather: "Heavy Rain & Dense Fog"
terrain_type: "Narrow Montane Ridge & Choke Defile"
attacker_faction: "[[Factions/Faction-Template|Order-of-the-Silver-Dawn]]"
attacker_commander: "[[Characters/Character-Template|Protagonist]]"
attacker_infantry: 3500
attacker_cavalry: 600
attacker_archers: 1200
attacker_arcane_units: 150
attacker_initial_morale: 88
defender_faction: "[[Factions/Faction-Template|The-Shadow-Cabal-of-Ost]]"
defender_commander: "[[Characters/Character-Template|Lord-Kaelen]]"
defender_infantry: 4200
defender_cavalry: 200
defender_archers: 1800
defender_arcane_units: 300
defender_initial_morale: 74
lanchester_model: "Square-Law (Aimed Ranged Fire + Arcane)"
frontage_width_meters: 450
outcome: "Decisive Attacker Victory"
attacker_casualties: 420
defender_casualties: 2150
---

# <% tp.file.title %> — Tactical Skirmish & Battle Simulation

> [!NOTE] ⚠️ EDUCATIONAL TEMPLATE (AI-GENERATED)
> **Notice**: This template was AI-generated for educational demonstration and craft guidance within the Ars Arcanum operating system. It is strictly non-commercial and provided solely to demonstrate system features, mechanical schemas, and engine capabilities. Authors should replace placeholder values with their original worldbuilding details.

<details>
<summary>💡 <b>Ars Arcanum Engine Guidance & Feature Breakdown (Click to Expand)</b></summary>

### Features Demonstrated in This Template:
- **Lanchester Battle Resolver**: `tactical_sim` (`arcanum tactical battle --attacker FactionA --defender FactionB --terrain ridge`) — Solves differential Lanchester attrition equations ($dx/dt = -\beta y$, $dy/dt = -\alpha x$) modulated by terrain elevation multipliers, troop frontage, discipline, and weapon lethality.
- **Choreography Beat Generator**: `tactical_sim` (`arcanum tactical battle --choreography`) — Synthesizes dramatic squad-level turning points, heroic duels, and commander crisis decisions for high-tension chapter drafting.
- **Morale Breaking Points & Rout Cascades**: Tracks cohesion decay curves and shock breakpoints where retreating units trigger domino panic.

### How to Use for Your Projects:
1. Define unit numbers, commander traits, and tactical terrain modifiers.
2. Select the attrition model (`Square-Law` for aimed ranged/arcane fire, `Linear-Law` for un-aimed volleys or dense shield walls).
3. Use the Phase-by-Phase breakdown to write structured, logically unshakeable battle chapters.
</details>

---

## 1. Tactical Order of Battle & Unit Compositions

```
    [Attacker: Order of the Silver Dawn] (Total: 5,450 | Morale: 88%)
    ├── Center: 3,500 Silver-Pike Infantry (Dense Phalanx, Depth: 8 Ranks)
    ├── Wings: 1,200 Longbow Archers (Elevated Ridge Flanks)
    ├── Reserve / Shock: 600 Armored Cataphracts
    └── Arcane Battery: 150 Aether-Weavers (Kinetic Deflector Screens)

                      ⚔️  FRONTAGE: 450 METERS  ⚔️

    [Defender: Shadow Cabal of Ost] (Total: 6,500 | Morale: 74%)
    ├── Vanguard: 4,200 Mercenary Reavers (Loose Skirmish Line)
    ├── Rear: 1,800 Crossbowmen (Pavise Barricades)
    ├── Flank: 200 Light Raiders
    └── Arcane Core: 300 Shadow Cultists (Abyssal Hex Cannons)
```

---

## 2. Terrain & Environmental Multipliers
- **Ridge Choke-Point (450m Frontage)**: Limits defender's numerical advantage; prevents cavalry flanking maneuvers.
- **Elevation Superiority (+2.2x Defender Armor Bonus)**: The Order occupied the upper crest before dawn.
- **Dense Rain & Fog (-35% Crossbow Effective Range)**: Severely degraded Cabal crossbow volleys while Aether-Weaver kinetic shields absorbed indirect fire.

---

## 3. Phase-by-Phase Battle Chronicle

### Phase 1: Arcane Artillery Duel & Vanguard Advance (06:00 – 08:30)
- The Cabal initiated with abyssal hex barrages. The Order's 150 Aether-Weavers linked barriers, absorbing 82% of explosive shockwaves at the cost of somatic exhaustion in 20 weavers.
- Cabal mercenaries charged the slope into the rain; footing gave way on the slippery scree.

### Phase 2: The Pike Wall Collision & Midpoint Crisis (08:30 – 11:15)
- The pike wall held against the initial charge, inflicting 8:1 casualties through frontage compression.
- *Crisis Point*: Cabal shadow cultists detonated a corpse bomb on the left flank, creating a 30-meter breach. Commander [[Characters/Character-Template|Protagonist]] personally led the 600 Cataphract reserve to plug the gap.

### Phase 3: The Flank Encirclement & General Rout (11:15 – 13:00)
- Defender morale plummeted below the 40% breaking threshold following the death of their vanguard warlord.
- The Cabal rearguard collapsed into a disorganized panic down the narrow ravine.

---

## 4. Tactical Lessons & Story Repercussions
- **Casualty Disparity**: Order lost 420 soldiers (7.7%); Cabal lost 2,150 killed/captured (33.0%).
- **Strategic Impact**: Secures the northern pass for the remainder of Book 1 and captures the enemy battle-standard for the High Chapter vaults.
