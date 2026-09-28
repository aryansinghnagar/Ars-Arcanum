---
fileClass: AstrophysicsSystem
fields:
  name:
    type: Input
  system_name:
    type: Input
  primary_star_mass_sol:
    type: Number
  primary_star_luminosity_sol:
    type: Number
  spectral_type:
    type: Input
  planet_name:
    type: Input
  semi_major_axis_au:
    type: Number
  orbital_period_days:
    type: Number
  planetary_mass_earth:
    type: Number
  surface_gravity_g:
    type: Number
  axial_tilt_deg:
    type: Number
  day_length_hours:
    type: Number
  moons:
    type: List
---
# AstrophysicsSystem FileClass Schema
Defines structured frontmatter fields for planetary physics, stellar ephemeris, and orbital mechanics.
