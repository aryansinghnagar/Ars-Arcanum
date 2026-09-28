# Print Typesetting, Preflight Validation & Spine Width Specification

> [!NOTE] ⚠️ EDUCATIONAL TEMPLATE (AI-GENERATED)
> **Notice**: This template was AI-generated for educational demonstration and craft guidance within the Ars Arcanum operating system. It is strictly non-commercial and provided solely to demonstrate system features, mechanical schemas, and engine capabilities. Authors should replace placeholder values with their original publication specifications.

<details>
<summary>💡 <b>Ars Arcanum Engine Guidance & Feature Breakdown (Click to Expand)</b></summary>

### Features Demonstrated in This Specification:
- **Spine Width Calculator**: `preflight` (`arcanum preflight Manuscripts/Book-01 --pages 380 --paper cream-55`) — Calculates exact spine thickness across KDP and IngramSpark paper types ($T_s = \text{Pages} / \text{PPI}$) to prevent spine wrap misalignment.
- **POD Signature Auditor**: `preflight` (`arcanum preflight Manuscripts/Book-01`) — Ensures final page counts align to 4-page and 16-page press signatures, avoiding unwanted blank trailing leaves.
- **Typst Book Template Engine**: `typst` (`templates/typst/book_template.typ`) — Reusable, high-performance, offline typesetting layout engine.

### How to Use for Your Projects:
1. Select your target trim size (e.g. 5.5" × 8.5" or 6" × 9" Royal Hardcover).
2. Calculate your exact spine width before commissioning cover artwork.
3. Run `arcanum preflight` before uploading final interior PDFs to distributors.
</details>

---

## 📏 Trim Size & Spine Width Calculation Matrix

```
[Total Manuscript Word Count: ~95,000 Words]
  └── Formatted Interior Page Count: 384 Pages (Divisible by 4-Page Signature)
```

| Paper Stock Type | Paper Color | Pages Per Inch (PPI) | Formula for Spine Thickness ($T_s$) | 384-Page Spine Width |
| :--- | :--- | :--- | :--- | :--- |
| **KDP Standard Cream** | 55# Cream | `434 PPI` | $T_s = \text{Pages} / 434$ | **0.885 inches (22.5 mm)** |
| **KDP Standard White** | 50# White | `490 PPI` | $T_s = \text{Pages} / 490$ | **0.784 inches (19.9 mm)** |
| **IngramSpark Groundwood**| 50# Cream | `444 PPI` | $T_s = \text{Pages} / 444$ | **0.865 inches (22.0 mm)** |
| **IngramSpark Premium Color**| 70# White| `357 PPI` | $T_s = \text{Pages} / 357$ | **1.076 inches (27.3 mm)** |

---

## 📐 Preflight Margin & Gutter Invariants (5.5" × 8.5" Standard)

```
       ┌─────────────────────────────┐
       │     Top Margin: 0.75 in     │
       │  ┌───────────────────────┐  │
       │  │                       │  │
Outer  │  │                       │  │ Gutter / Inner
Margin │  │   Body Text Area      │  │ Margin:
0.625" │  │   (Min 10.5pt Typst)  │  │ 0.875 in (Accounts for spine glue)
       │  │                       │  │
       │  └───────────────────────┘  │
       │    Bottom Margin: 0.75 in   │
       └─────────────────────────────┘
```

---

## 🛡️ Preflight Checklist Before Press Submission
- [x] All chapter title pages start on a **recto** (right-hand / odd-numbered) page.
- [x] Running headers and page folios suppressed on blank verso pages.
- [x] Total page count is a multiple of 4 (zero orphan blank pages).
- [x] All embedded chapter header ornament graphics are vector SVGs or 300+ DPI bitmaps.
- [x] Font licenses validated for offline commercial embedding.
