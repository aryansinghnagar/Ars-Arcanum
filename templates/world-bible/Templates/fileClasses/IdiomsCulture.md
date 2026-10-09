---
fileClass: IdiomsCulture
fields:
  name:
    type: Input
  aliases:
    type: List
  type:
    type: Select
    options:
      values:
        - idioms_culture
  culture_group:
    type: Input
  associated_language:
    type: File
    path: Languages
  geographic_region:
    type: File
    path: Locations
  primary_metaphor_domains:
    type: List
  superstitious_oaths:
    type: List
  blasphemies_and_curses:
    type: List
  etymological_depth_rating:
    type: Select
    options:
      values:
        - Shallow
        - Moderate
        - Deep
---
# IdiomsCulture FileClass Schema
Defines structured frontmatter fields and controlled input validation for cultural idioms, speculative proverbs, and vernacular oaths via Metadata Menu.
