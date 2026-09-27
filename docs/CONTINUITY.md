# Intra-Volume Continuity Verifier (`continuity`)
> **Domain D: Stylistics, Polish & Continuity** | **CLI:** `arcanum continuity`

---

## 1. Overview & Theoretical Rationale
The **Continuity Verifier** maintains an entity attribute state graph across manuscript chapters to catch physical, spatial, and biographical continuity errors within a single volume.

---

## 2. Mathematical State Verification Logic
For any entity $e$ with property $P$ evaluated at sequential scenes $S_1$ and $S_2$ ($t(S_1) < t(S_2)$):
$$P(e, S_2) \neq P(e, S_1) \implies \exists \text{ Explicit Event } E_k \text{ in } [S_1, S_2] \text{ modifying } P$$

If a property changes (e.g. eye color shifts from blue to green, or a character wields a shattered sword) without an intervening modification event, an inconsistency alert is raised.

---

## 3. Subfeatures Matrix
- **Physical Trait Tracker**: Verifies eye color, hair, scars, and dominant hand consistency.
- **Inventory & Weapon State**: Tracks items picked up, transferred, broken, or consumed.
- **Injury & Stamina Dynamics**: Flags unrealistic instant recovery from major physical trauma without healing time or magic intervention.

---

## 4. Extension & Annotation Guide
Authors can explicitly tag state modifications in prose or frontmatter:
```markdown
---
title: "Chapter 4: The Skirmish"
pov: "Valerius"
state_events:
  - entity: "Valerius"
    action: "lost_weapon"
    target: "Sunblade"
  - entity: "Valerius"
    action: "injured"
    detail: "left_shoulder_wound"
---
```

### CLI Command
```bash
arcanum continuity 01_Manuscript/ --strict
```
