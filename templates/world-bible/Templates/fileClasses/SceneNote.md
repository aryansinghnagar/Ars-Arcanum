---
fileClass: SceneNote
fields:
  name:
    type: Input
  book:
    type: Input
  chapter:
    type: Input
  pov_character:
    type: File
    path: Characters
  location:
    type: File
    path: Locations
  narrative_day:
    type: Input
  scene_type:
    type: Select
    options:
      values:
        - Scene
        - Sequel
  target_word_count:
    type: Number
  status:
    type: Select
    options:
      values:
        - Outline
        - Draft
        - Revised
        - Polish
        - Final
  pacing_intensity:
    type: Number
---
# SceneNote FileClass Schema
Defines structured frontmatter fields for Dwight Swain Scene & Sequel planning and pacing intensity.
