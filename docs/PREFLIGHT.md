# Publication Preflight Verification Harness (`preflight`)
> **Domain G: Publishing & Preflight** | **CLI:** `arcanum preflight` / `arcanum check`

---

## 1. Overview & Theoretical Rationale
The **Preflight Verification Harness** acts as the final quality gate before exporting a manuscript for typesetting, EPUB generation, or agent submission. It runs comprehensive, multi-stage checks across syntax, lore continuity, pacing, sensory immersion, and typographic integrity.

---

## 2. 7-Stage Preflight Quality Gates
1. **Stage 1 (Syntax & Frontmatter)**: Validates YAML frontmatter parsing and Markdown heading hierarchies.
2. **Stage 2 (Link & Anchor Integrity)**: Verifies that all internal chapter cross-references and wikilinks (`[[Lore Term]]`) resolve to valid entities.
3. **Stage 3 (Intra-Volume Continuity)**: Scans character attributes and timeline events for physical contradictions.
4. **Stage 4 (Pacing & Structural Harmony)**: Evaluates L1 paradigm harmony score against the selected narrative framework.
5. **Stage 5 (Sensory Palette Balance)**: Ensures chapters meet minimum non-visual sensory immersion thresholds.
6. **Stage 6 (Typography & Quotations)**: Verifies curly quote pairing and em-dash styling.
7. **Stage 7 (Export Readiness)**: Validates Typst/Pandoc build targets and asset dependencies.

---

## 3. CLI Command Examples
```bash
# Run full preflight verification suite
arcanum preflight 01_Manuscript/

# Output machine-readable JSON report for CI/CD pipelines
arcanum preflight 01_Manuscript/ --json
```
