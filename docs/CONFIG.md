# Universal Configuration Engine (`config`)
> **Domain F: Retrieval & Infrastructure** | **CLI:** `arcanum config`

---

## 1. Overview & Theoretical Rationale
The **Configuration Engine** implements a deterministic, multi-tiered cascading configuration model. It ensures authors have fine-grained control over validation strictness, sensory thresholds, and formatting preferences across global, universe, and volume scopes.

---

## 2. Cascading Resolution Hierarchy
Configuration parameters resolve in order of increasing specificity:
$$\text{Resolved Config} = \text{Defaults} \oplus \text{Global Config} (\sim/.arcanum/config.yaml) \oplus \text{Universe Config} \oplus \text{Book Config} \oplus \text{CLI Flags}$$

---

## 3. Configuration Keys
| Key | Type | Default | Description |
|---|---|---|---|
| `pacing.target_words_per_scene` | `int` | `2500` | Target word count per scene card |
| `sensory.min_channels_per_scene` | `int` | `3` | Minimum non-visual sensory channels required |
| `typst.page_size` | `string` | `"6x9in"` | Publication trim size |
| `autosave.interval_sec` | `int` | `60` | Zen Studio local persistence frequency |

---

## 4. CLI Usage Examples
```bash
# View active configuration settings
arcanum config --list

# Set custom parameter
arcanum config set sensory.min_channels_per_scene 4
```
