---
fileClass: DeliberativeCouncil
fields:
  name:
    type: Input
  aliases:
    type: List
  type:
    type: Select
    options:
      values:
        - deliberative_council
  council_name:
    type: Input
  convening_body:
    type: File
    path: Factions
  location:
    type: File
    path: Locations
  date:
    type: Input
  fc-date:
    type: Input
  fc-calendar:
    type: Input
  fc-category:
    type: Input
  presiding_officer:
    type: File
    path: Characters
  voting_threshold_pct:
    type: Number
  deliberation_stakes:
    type: Input
  primary_factions_present:
    type: List
  central_dispute:
    type: Input
  thesis_faction:
    type: Input
  antithesis_faction:
    type: Input
  synthesis_outcome:
    type: Input
  binding_resolution:
    type: Input
  status:
    type: Select
    options:
      values:
        - Scheduled
        - In-Session
        - Deadlocked
        - Concluded
        - Dissolved
---
# DeliberativeCouncil FileClass Schema
Defines structured frontmatter fields and controlled input validation for council debates, parliamentary disputes, and narrative dialectics via Metadata Menu.
