---
fileClass: JourneyRoute
fields:
  name:
    type: Input
  route_name:
    type: Input
  origin_node:
    type: File
    path: Locations
  destination_node:
    type: File
    path: Locations
  total_distance_km:
    type: Number
  elevation_gain_m:
    type: Number
  elevation_loss_m:
    type: Number
  terrain_friction_index:
    type: Number
  standard_march_days:
    type: Number
  daily_ration_kg_per_person:
    type: Number
  daily_water_liters_per_person:
    type: Number
---
# JourneyRoute FileClass Schema
Defines structured frontmatter fields for travel logistics, terrain friction, and marching rations.
