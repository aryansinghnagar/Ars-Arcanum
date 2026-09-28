---
fileClass: EcologyFoodWeb
fields:
  name:
    type: Input
  ecosystem_name:
    type: Input
  biome_region:
    type: File
    path: Locations
  trophic_efficiency_pct:
    type: Number
  keystone_species:
    type: File
    path: Bestiary
  apex_predator:
    type: File
    path: Bestiary
  carrying_capacity_k_total:
    type: Number
---
# EcologyFoodWeb FileClass Schema
Defines structured frontmatter fields for trophic webs, keystone species, and biomass carrying capacities.
