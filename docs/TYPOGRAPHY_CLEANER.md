# Typography Cleaner & Microtypography Normalizer (`typography_cleaner`)
> **Domain D: Stylistics, Polish & Continuity** | **CLI:** `arcanum typography-cleaner`

---

## 1. Overview & Theoretical Rationale
Publishing-grade typesetting requires rigorous typographic hygiene that standard word processors often fail to maintain.

The **Typography Cleaner Engine** executes a deterministic, idempotent regex pipeline that converts ASCII punctuation into publishing-standard Unicode microtypography.

---

## 2. Typographic Rules & Replacements
- **Curly Dialogue Quotes**: Replaces straight `"` and `'` with contextual opening/closing curly quotes (`“` `”`, `‘` `’`).
- **Em-Dashes**: Replaces double hyphens `--` with true em-dashes `—`.
- **En-Dashes**: Replaces hyphens in numeric ranges (`1914-1918`, `pp. 45-60`) with en-dashes `–`.
- **Ellipses**: Replaces three periods `...` with Unicode ellipsis `…`.
- **Non-Breaking Spaces**: Inserts non-breaking spaces before units of measure and em-dashes to prevent orphan line wraps.

---

## 3. CLI Command Examples
```bash
# Normalize typography across all manuscript files
arcanum typography-cleaner 01_Manuscript/ --apply

# Preview proposed typographic fixes without writing to disk
arcanum typography-cleaner 01_Manuscript/Chapter_01.md --dry-run
```
