---
fileClass: BranchingNode
fields:
  name:
    type: Input
  node_id:
    type: Input
  node_title:
    type: Input
  scene_type:
    type: Select
    options:
      values:
        - Choice_Node
        - Linear_Passage
        - Ending_Node
        - Death_Node
  parent_nodes:
    type: List
  state_requirements:
    type: List
  state_modifications:
    type: List
---
# BranchingNode FileClass Schema
Defines structured metadata fields for interactive branching narrative graphs and choice nodes.
