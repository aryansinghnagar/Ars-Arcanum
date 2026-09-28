---
fileClass: TimelineBranch
fields:
  name:
    type: Input
  branch_id:
    type: Input
  divergence_node:
    type: File
    path: History
  divergence_year:
    type: Number
  parent_timeline:
    type: Input
  paradox_index:
    type: Number
  divergence_catalyst:
    type: Input
  reconciliation_pathway:
    type: Input
---
# TimelineBranch FileClass Schema
Defines structured frontmatter fields for causal multiverse graphs, divergence nodes, and paradox indices.
