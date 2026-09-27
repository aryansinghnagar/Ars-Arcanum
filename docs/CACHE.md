# Ephemeral Cache Engine (`cache`)
> **Domain F: Retrieval & Infrastructure** | **CLI:** `arcanum cache`

---

## 1. Overview & Theoretical Rationale
The **Cache Engine** provides deterministic, content-addressable ephemeral caching for expensive parsing and validation operations (e.g. multi-chapter NLP scans, graph topological sorts, and vector tokenization).

---

## 2. Invariant Cache Invalidation Logic
A cached entry is validated against disk state using a strict compound key:
$$\text{Entry Valid} \iff (\text{mtime}_{\text{disk}} == \text{mtime}_{\text{cache}}) \land (\text{SHA256}_{\text{content}} == \text{Hash}_{\text{cache}})$$

If either the filesystem modification timestamp or the SHA-256 digest diverges, the entry is invalidated and re-evaluated atomically.

---

## 3. Subfeatures Matrix
- **SQLite Disk Storage**: Fast local key-value store in `.arcanum/cache.db`.
- **Automatic Migration Evacuation**: Clears stale indexes on schema upgrades.
- **Cache Health Telemetry**: Tracks hit/miss ratios and total disk occupancy.

---

## 4. CLI Usage Examples
```bash
# Display cache statistics and disk usage
arcanum cache --stats

# Invalidate and purge all cached index entries
arcanum cache --purge
```
