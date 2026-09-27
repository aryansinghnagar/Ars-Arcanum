# Manuscript Semantic Diff Engine (`manuscript_diff`)
> **Domain D: Stylistics, Polish & Continuity** | **CLI:** `arcanum diff`

---

## 1. Overview & Theoretical Rationale
Standard code difference tools (e.g. `diff`, `git diff`) operate on newline boundaries. In prose manuscripts, inserting a single adjective shifts line wraps across an entire paragraph, producing unreadable diff noise.

The **Manuscript Diff Engine** operates on paragraph and word token boundaries, providing fine-grained semantic insights into prose revisions.

---

## 2. Mathematical Alignment & Word Edit Distance
1. **Paragraph Alignment**: Matches paragraphs between Draft A and Draft B using longest common subsequence (LCS) on normalized paragraph vectors.
2. **Word-Level Levenshtein Diff**: Within aligned paragraphs, calculates exact word insertions, deletions, and replacements.
3. **Telemetry Metrics**: Computes net word churn, expansion percentage, and deletion velocity.

---

## 3. CLI Command Examples
```bash
# Compare two chapter drafts
arcanum diff 01_Manuscript/Chapter_01_Draft1.md 01_Manuscript/Chapter_01_Draft2.md

# Compare current working tree against a Git snapshot
arcanum diff --snapshot snap_v1.2.0
```
