# Dynamic Craft Engine Plugin Architecture (PLUGINS)
> **Engineering Specification & Plugin Authoring Manual** | Release v0.1.0 | Extensibility Layer

---

## 1. Executive Summary & Plugin Architecture

Ars Arcanum ships with 47 built-in craft and core domain engines covering astrophysics, ecology, conlangs, economy, causality, tactical combat, and manuscript diffing. However, worldbuilding systems often feature idiosyncratic rules (e.g. specialized alchemical combustion tables, unique faster-than-light warp physics, or clan succession rites).

The **Dynamic Plugin System** ([`scripts/lib/registry.py`](file:///scripts/lib/registry.py), [`scripts/lib/registry_base.py`](file:///scripts/lib/registry_base.py)) enables speculative fiction authors and engineers to build custom, 100% offline, zero-pip Python craft engines that seamlessly integrate into the unified CLI, Studio Hub, Zen Studio, and GTK3 Desktop GUI.

---

## 2. Dynamic Discovery Search Paths

When initialized, Ars Arcanum automatically discovers custom plugin modules across three standard directory tiers:

1. **User Global Config Directory**: `~/.config/ars-arcanum/engines/*.py`
2. **Narrative Universe Directory**: `~/Universes/<UNIVERSE>/plugins/*.py`
3. **Repository Development Directory**: `configs/plugins/<PLUGIN_NAME>/plugin.py`

Any `.py` file found in these directories that implements the `BaseCraftEngine` class or exports an `EngineSpec` is loaded dynamically via `importlib.util.spec_from_file_location` and registered into the global engine catalog.

---

## 3. Authoring a Custom Craft Engine Plugin

To create a new craft engine plugin, inherit from `BaseCraftEngine` in [`scripts/lib/registry_base.py`](file:///scripts/lib/registry_base.py):

```python
#!/usr/bin/env python3
"""
Custom Alchemy Reaction Simulator Plugin (alchemy_engine.py)
Save to: ~/.config/ars-arcanum/engines/alchemy_engine.py
"""

from scripts.lib.registry_base import BaseCraftEngine, EngineCategory, EngineSpec

class AlchemyEngine(BaseCraftEngine):
    name = "alchemy"
    category = EngineCategory.CRAFT
    title = "Sovereign Alchemy & Transmutation Simulator"
    description = "Models stoichiometric energy balance, elemental affinities, and rebound risks."
    cli_command = "arcanum craft alchemy"
    aliases = ["alchemy", "transmute", "elements"]
    studio_tab = "Worldbuilding"
    
    scientific_logic = """
    Calculates thermodynamic enthalpy balance for arcane reactions. Reagents must balance
    in primary elemental humors (Sulfur, Mercury, Salt) or trigger destructive energy discharge.
    """
    
    why_this_way = "Prevents soft worldbuilding 'free magic' plot holes by enforcing conservation of arcane mass."
    worldbuilding_relevance = "Defines industrial economies based on potion manufacturing and transmutation limits."
    storytelling_relevance = "Supplies hard constraints and failure consequences during critical high-stakes scenes."
    
    subfeatures = [
        {"name": "Reagent Balancing", "desc": "Validates 3-element stoichiometric ratios"},
        {"name": "Backlash Risk", "desc": "Calculates percentage chance of toxic atmospheric fallout"},
    ]

    def run(self, args: list[str]) -> int:
        print("🧪 Simulating arcane transmutation...")
        # Custom simulation logic here...
        return 0

# Optional explicit factory hook
def register_engine() -> EngineSpec:
    return AlchemyEngine().get_spec()
```

---

## 4. Hook Lifecycle & CLI / GUI Integration

Once discovered:
1. **Unified CLI**: Automatically routes `arcanum alchemy [opts]` and `arcanum craft alchemy [opts]` to your plugin.
2. **Help & Discovery**: Displays in `arcanum --help` and `arcanum doc alchemy`.
3. **Studio Hub & Zen Studio**: Appears in the craft engines drawer and can be audited from the Scope Cockpit.
4. **Desktop GUI**: Generates a dedicated tab under the GTK3 / Libadwaita window with interactive inputs.

---

## 5. Plugin Security & Sandboxing Invariants

In accordance with the Ars Arcanum Operating Manifesto:
- **Zero Cloud Invariant**: Custom plugins must never make outbound network requests or load remote CDN assets.
- **Atomic File Safety**: If writing files, plugins must import and use `atomic_write()` from `scripts.lib._bootstrap`.
- **Path Traversal Defense**: All target path arguments must be sanitized against path traversal (`..`) and Windows device names.

---

## 6. Sample Reference Plugins

The repository provides production-ready reference plugins in [`configs/plugins/`](file:///configs/plugins/):
- [`configs/plugins/magic_system_audit/plugin.py`](file:///configs/plugins/magic_system_audit/plugin.py): Arcane rule consistency and resource exhaustion auditor.
- [`configs/plugins/speculative_naming/plugin.py`](file:///configs/plugins/speculative_naming/plugin.py): Conlang phoneme generator and cultural naming checker.
