---
fileClass: TacticalBattle
fields:
  name:
    type: Input
  battle_name:
    type: Input
  location:
    type: File
    path: Locations
  date:
    type: Input
  terrain_type:
    type: Input
  attacker_faction:
    type: File
    path: Factions
  attacker_commander:
    type: File
    path: Characters
  attacker_infantry:
    type: Number
  attacker_cavalry:
    type: Number
  defender_faction:
    type: File
    path: Factions
  defender_commander:
    type: File
    path: Characters
  defender_infantry:
    type: Number
  defender_cavalry:
    type: Number
  lanchester_model:
    type: Input
  frontage_width_meters:
    type: Number
  outcome:
    type: Input
---
# TacticalBattle FileClass Schema
Defines structured frontmatter fields for tactical battle simulations and Lanchester attrition dynamics.
