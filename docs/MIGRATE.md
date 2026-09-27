# Schema & Directory Migration Engine (`migrate`)
> **Domain F: Retrieval & Infrastructure** | **CLI:** `arcanum migrate`

---

## 1. Overview & Theoretical Rationale
The **Migration Engine** safely updates project directory topologies and metadata schemas across major Ars Arcanum release versions ($v1.0.0 \to v2.0.0$) while guaranteeing zero loss of creative writing.

---

## 2. Invariant Migration Lifecycle
1. **Safety Pre-Flight**: Acquires `ArcanumLock` and creates a compressed snapshot archive (`.arcanum/snapshots/pre_migrate_<timestamp>.tar.gz`).
2. **Schema Transformation**: Deterministically walks all markdown files, converts legacy frontmatter keys, and restructures folder layouts.
3. **Post-Migration Verification**: Runs the full `preflight` suite. If any verification stage fails, the snapshot is automatically restored.

---

## 3. CLI Command Examples
```bash
# Preview proposed migration transformations without modifying files
arcanum migrate --dry-run

# Execute project migration to v2.0.0 schema
arcanum migrate --apply
```
