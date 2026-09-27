# Visual Story Canvas & Corkboard Engine (`story_canvas`)
> **Domain B: Narrative Architecture** | **CLI:** `arcanum story-canvas` / `arcanum canvas`

---

## 1. Overview & Theoretical Rationale
The **Story Canvas Engine** generates a standalone, zero-dependency, interactive visual corkboard and timeline arranger. It empowers authors to drag, drop, reorder, and visually balance manuscript scenes across canonical narrative paradigms.

---

## 2. Mathematical Harmony & Pacing Feedback
As scenes are dragged across Act columns and beat milestones, the client-side JavaScript dynamically recalculates the **Structural Harmony Metric**:
$$\text{Harmony Score} = \max\left(0, \min\left(100, 100 \times \left(1 - \frac{1}{2}\sum_{b} |\text{ActualPct}_b - \text{TargetPct}_b|\right)\right)\right)$$

---

## 3. Subfeatures Matrix
- **9 Paradigm Swimlanes**: Three-Act, Save the Cat!, 8-Sequence, Dan Harmon Story Circle, Hero's Journey, Freytag's Pyramid, Seven-Point, Kishōtenketsu, and Fichtean Curve.
- **POV & Plot Thread Filters**: Instant visual highlighting of specific character arcs and subplots.
- **One-Click Manifest Export**: Exports the updated chapter order directly as an actionable JSON manifest.
- **Strict Content Security Policy**: 100% offline, zero remote CDN scripts.

---

## 4. CLI Command Examples
```bash
# Generate standalone HTML story canvas for manuscript
arcanum story-canvas 01_Manuscript/ --paradigm eight_sequence

# Export extracted scene cards as JSON
arcanum story-canvas 01_Manuscript/ --json
```
