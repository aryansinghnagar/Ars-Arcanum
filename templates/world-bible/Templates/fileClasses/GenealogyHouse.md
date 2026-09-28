---
fileClass: GenealogyHouse
fields:
  name:
    type: Input
  house_name:
    type: Input
  seat_of_power:
    type: File
    path: Locations
  founding_year:
    type: Number
  succession_law:
    type: Input
  current_head:
    type: File
    path: Characters
  heir_apparent:
    type: File
    path: Characters
  cadet_branches:
    type: List
  allied_houses:
    type: List
  motto:
    type: Input
---
# GenealogyHouse FileClass Schema
Defines structured frontmatter fields for dynastic houses, succession rules, and lineage graphs.
