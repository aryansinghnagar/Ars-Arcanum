# Series & Cross-Volume Continuity Verifier (`series_continuity`)
> **Domain D: Stylistics, Polish & Continuity** | **CLI:** `arcanum series-continuity`

---

## 1. Overview & Theoretical Rationale
In multi-volume fantasy and sci-fi series (e.g. trilogies, decalogies), world rules, character ages, and historical lore established in Book 1 frequently suffer from "lore drift" by Book 4.

The **Series Continuity Engine** verifies canonical consistency across all books within a shared universe.

---

## 2. Cross-Volume State Synchronization Logic
1. **Canonical World Bible Sync**: Evaluates whether individual book manuscripts alter immutable historical events or magical limitations without explicit retcons.
2. **Character Age & Timeline Drift**:
   $$\text{Age}(C, \text{Book } k) = \text{BirthYear}(C) + t_{\text{timeline}}(\text{Book } k)$$
3. **Deceased Entity Invariant**: Flags any appearance of deceased characters in subsequent volumes unless marked as flashbacks, visions, or resurrection events.

---

## 3. CLI Command Examples
```bash
# Verify series consistency across all books in the universe
arcanum series-continuity ./Universes/Aethelgard/

# Check cross-book entity attribute drift
arcanum series-continuity ./Universes/Aethelgard/ --entities
```
