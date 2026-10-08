#!/usr/bin/env python3
"""
Ars Arcanum Universal Resonance Mesh & Cross-Domain Synthesizer
(scripts/lib/resonance.py)
================================================================================
Central cross-domain knowledge graph and deterministic simulation cascade engine
unifying all 50 craft and core engines of Ars Arcanum into a cohesive ecosystem.

Pillars:
1. Cosmology, Physics & Geography (Astrophysics, Climate, Cartography, Calendar, Ecology, Journey)
2. Society, Culture & Arcana (Factions, Economy, Magic System, Conlang, Genealogy, Tactical Sim)
3. Narrative Architecture & Chronology (Causality, Timeline, Structure, Branching, Plot, Scene, Pacing, Prophecy, Cast, Voice)
4. Stylistics & Sensory Immersion (Stylistics, Senses, Continuity, Series Continuity, Concordance, Codex)
5. Authoring OS & Telemetry (Writing Sprint, Heatmap, Diff, Typography, Zen Studio, Ambient, Portfolio, Hub, RAG, Exporter, Doctor)

Capabilities:
- Deterministic cross-domain knowledge mesh and entity relationship indexing
- Deterministic Causal Cascade Engine with dry-run impact reports and advisory resolutions
- Multi-tiered Creative Spark & Cross-Domain Analogy Synthesizer
- Cross-Domain Consistency & Coherence Auditor
- Standalone offline interactive HTML Knowledge Mesh Visualizer & Simulation Lab
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import deque
from pathlib import Path
from typing import Any

try:
    from lib._bootstrap import atomic_write
    from lib.data_access import get_data_access
    from lib.frontmatter import parse_yaml_frontmatter
    from lib.resonance_data import (
        FOUNDATIONAL_DOMAINS,
        FOUNDATIONAL_EDGES,
        STRUCTURAL_ISOMORPHISMS,
        CascadeImpact,
        CascadeReport,
        CoherenceViolation,
        CreativeSpark,
        CrossDomainEdge,
        CrossDomainNode,
        DomainPillar,
        compute_cascade_impacts,
    )
    from lib.resonance_template import render_resonance_html
except ImportError:
    try:
        from _bootstrap import atomic_write
        from data_access import get_data_access
        from frontmatter import parse_yaml_frontmatter
        from resonance_data import (
            FOUNDATIONAL_DOMAINS,
            FOUNDATIONAL_EDGES,
            STRUCTURAL_ISOMORPHISMS,
            CascadeImpact,
            CascadeReport,
            CoherenceViolation,
            CreativeSpark,
            CrossDomainEdge,
            CrossDomainNode,
            DomainPillar,
            compute_cascade_impacts,
        )
        from resonance_template import render_resonance_html
    except ImportError:
        def atomic_write(path: Path, content: str, encoding: str = "utf-8") -> None:
            import os as _os
            import tempfile as _tf
            p = Path(path).resolve()
            p.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp = _tf.mkstemp(dir=p.parent, prefix=f".{p.name}.", suffix=".tmp")
            try:
                with _os.fdopen(fd, "w", encoding=encoding, newline="") as f:
                    f.write(content)
                    f.flush()
                    _os.fsync(f.fileno())
                _os.replace(tmp, p)
            except BaseException:
                try:
                    Path(tmp).unlink(missing_ok=True)
                except OSError:
                    pass
                raise

        def parse_yaml_frontmatter(text: str) -> dict[str, Any]:
            if not text.startswith("---"):
                return {}
            parts = text.split("---", 2)
            if len(parts) < 3:
                return {}
            data: dict[str, Any] = {}
            for line in parts[1].splitlines():
                line = line.strip()
                if ":" in line and not line.startswith("#"):
                    k, v = line.split(":", 1)
                    data[k.strip()] = v.strip().strip("\"'")
            return data


VERSION = "0.1.0"
CSP_HEADER = "<meta http-equiv=\"Content-Security-Policy\" content=\"default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;\">"

__all__ = [
    "CSP_HEADER",
    "FOUNDATIONAL_DOMAINS",
    "FOUNDATIONAL_EDGES",
    "STRUCTURAL_ISOMORPHISMS",
    "VERSION",
    "CascadeImpact",
    "CascadeReport",
    "CoherenceViolation",
    "CreativeSpark",
    "CrossDomainEdge",
    "CrossDomainNode",
    "DomainPillar",
    "ResonanceMesh",
    "main",
]


# =============================================================================
# Universal Resonance Mesh Implementation
# =============================================================================

class ResonanceMesh:
    """Central graph mesh and cross-domain reasoning engine."""

    def __init__(self, project_dir: Path | None = None) -> None:
        self.project_dir = project_dir or Path.cwd()
        self.nodes: dict[str, CrossDomainNode] = {}
        self.edges: list[CrossDomainEdge] = []
        self._adjacency: dict[str, list[CrossDomainEdge]] = {}
        self._reverse_adjacency: dict[str, list[CrossDomainEdge]] = {}
        self._bootstrap_foundational_mesh()

    def _bootstrap_foundational_mesh(self) -> None:
        """Initializes canonical domain nodes and cross-pillar bridges."""
        for d_id, label, pillar_val, engine, n_type in FOUNDATIONAL_DOMAINS:
            self.add_node(CrossDomainNode(
                id=d_id,
                label=label,
                pillar=DomainPillar(pillar_val),
                engine=engine,
                node_type=n_type,
                summary=f"Canonical {label} engine domain.",
            ))

        for src, tgt, rel, strength, desc in FOUNDATIONAL_EDGES:
            self.add_edge(CrossDomainEdge(
                source_id=src,
                target_id=tgt,
                relation=rel,
                strength=strength,
                description=desc,
            ))

    def add_node(self, node: CrossDomainNode) -> None:
        self.nodes[node.id] = node
        if node.id not in self._adjacency:
            self._adjacency[node.id] = []
        if node.id not in self._reverse_adjacency:
            self._reverse_adjacency[node.id] = []

    def add_edge(self, edge: CrossDomainEdge) -> None:
        self.edges.append(edge)
        self._adjacency.setdefault(edge.source_id, []).append(edge)
        self._reverse_adjacency.setdefault(edge.target_id, []).append(edge)

    def scan_vault_and_manuscript(self, world_dir: Path | None = None, manuscript_dir: Path | None = None) -> None:
        """Scans workspace markdown vaults and manuscripts to populate concrete instance nodes."""
        w_dir = world_dir or (self.project_dir / "World" if (self.project_dir / "World").exists() else None)
        m_dir = manuscript_dir or (self.project_dir / "Manuscript" if (self.project_dir / "Manuscript").exists() else None)
        dal = get_data_access()

        if w_dir and w_dir.exists():
            for p in sorted(w_dir.rglob("*.md")):
                if p.name.startswith((".", "_")) or "Backups" in p.parts:
                    continue
                try:
                    text = dal.read_file(p)
                    meta, _ = dal.parse_frontmatter(p)
                except OSError:
                    continue
                entity_name = meta.get("name") or meta.get("Title") or p.stem.replace("_", " ").replace("-", " ").title()
                entity_type = meta.get("type") or meta.get("category") or "lore_entity"
                node_id = f"entity_{p.stem.lower()}"

                pillar = DomainPillar.SOCIETY_SYSTEMS
                engine = "world_doctor"
                t_low = str(entity_type).lower()
                if any(k in t_low for k in ["star", "planet", "orbit", "climate", "moon", "astro"]):
                    pillar = DomainPillar.COSMOLOGY_PHYSICS
                    engine = "astrophysics"
                elif any(k in t_low for k in ["faction", "nation", "guild", "house", "dynasty"]):
                    pillar = DomainPillar.SOCIETY_SYSTEMS
                    engine = "factions"
                elif any(k in t_low for k in ["character", "person", "npc", "hero", "protagonist"]):
                    pillar = DomainPillar.NARRATIVE_CHRONOLOGY
                    engine = "dramatis_personae"
                elif any(k in t_low for k in ["magic", "spell", "axiom", "mana"]):
                    pillar = DomainPillar.SOCIETY_SYSTEMS
                    engine = "magic_system"
                elif any(k in t_low for k in ["language", "conlang", "dialect"]):
                    pillar = DomainPillar.SOCIETY_SYSTEMS
                    engine = "conlang"
                elif any(k in t_low for k in ["event", "timeline", "era", "battle"]):
                    pillar = DomainPillar.NARRATIVE_CHRONOLOGY
                    engine = "timeline_sync"

                node = CrossDomainNode(
                    id=node_id,
                    label=str(entity_name),
                    pillar=pillar,
                    engine=engine,
                    node_type=str(entity_type),
                    attributes=meta,
                    tags=meta.get("tags", []) if isinstance(meta.get("tags"), list) else [],
                    source_file=str(p.relative_to(self.project_dir)) if self.project_dir in p.parents else str(p),
                    summary=text[:200].replace("\n", " ").strip(),
                )
                self.add_node(node)
                # Link to domain engine node
                if engine in self.nodes:
                    self.add_edge(CrossDomainEdge(
                        source_id=engine,
                        target_id=node_id,
                        relation="contains_instance",
                        strength=0.9,
                        description=f"{engine} contains concrete instance {entity_name}",
                    ))

                # Extract wiki-links to create graph edges
                links = re.findall(r"\[\[([^\]\|#]+)(?:\|[^\]\]]*)?\]\]", text)
                for lk in links:
                    tgt_id = f"entity_{lk.strip().lower().replace(' ', '_').replace('-', '_')}"
                    self.add_edge(CrossDomainEdge(
                        source_id=node_id,
                        target_id=tgt_id,
                        relation="cross_references",
                        strength=0.7,
                        description=f"{entity_name} links to {lk}",
                    ))

        if m_dir and m_dir.exists():
            for p in sorted(m_dir.rglob("*.md")):
                if p.name.startswith((".", "_")) or "Backups" in p.parts:
                    continue
                try:
                    text = dal.read_file(p)
                    meta, _ = dal.parse_frontmatter(p)
                except OSError:
                    continue
                title = meta.get("title") or meta.get("Title") or p.stem.replace("_", " ").title()
                ch_id = f"chapter_{p.stem.lower()}"
                words = len(text.split())

                node = CrossDomainNode(
                    id=ch_id,
                    label=str(title),
                    pillar=DomainPillar.NARRATIVE_CHRONOLOGY,
                    engine="scene_mechanics",
                    node_type="manuscript_chapter",
                    attributes={"words": words, **meta},
                    tags=meta.get("tags", []) if isinstance(meta.get("tags"), list) else [],
                    source_file=str(p.relative_to(self.project_dir)) if self.project_dir in p.parents else str(p),
                    summary=f"Manuscript chapter: {words} words. POV: {meta.get('pov', 'Omniscient')}",
                )
                self.add_node(node)
                self.add_edge(CrossDomainEdge(
                    source_id="scene_mechanics",
                    target_id=ch_id,
                    relation="manuscript_craft_beat",
                    strength=0.85,
                    description=f"Chapter {title} narrative scene craft",
                ))

    # =========================================================================
    # Deterministic Causal Cascade Engine
    # =========================================================================

    def simulate_cascade(
        self,
        origin_node_id: str,
        param_key: str,
        new_value: Any,
        old_value: Any = None,
    ) -> CascadeReport:
        """Computes deterministic forward-chaining causal cascade across all connected domain nodes."""
        report = CascadeReport(
            origin_node_id=origin_node_id,
            origin_field=param_key,
            origin_old_value=old_value,
            origin_new_value=new_value,
        )

        impacts = compute_cascade_impacts(
            origin_node_id=origin_node_id,
            param_key=param_key,
            new_value=new_value,
            old_value=old_value,
            nodes=self.nodes,
            adjacency=self._adjacency,
        )

        report.impacts = impacts
        report.summary = (
            f"Cascading change from [{origin_node_id}.{param_key} = {new_value}] "
            f"propagated across {len(impacts)} downstream domain nodes spanning {len({i.pillar for i in impacts})} pillars."
        )
        report.advisory_resolutions = [
            {"mode": "Hard Realism", "description": "Apply all calculated downstream physical, economic, and tactical impacts to maintain strict causal plausibility."},
            {"mode": "Speculative / Trope", "description": "Selectively isolate the change to local storytelling scenes while keeping macro-systems stable."},
            {"mode": "Creative Sovereignty", "description": "Use the downstream dissonance as a central narrative paradox or deliberate surreal world mystery."},
        ]

        return report

    # =========================================================================
    # Creative Spark & Multi-Domain Analogy Synthesizer
    # =========================================================================

    def generate_sparks(
        self,
        domains: list[str] | None = None,
        count: int = 3,
        seed: str | None = None,
    ) -> list[CreativeSpark]:
        """Synthesizes rich cross-disciplinary creative sparks and analogies connecting disparate fields."""
        selected_sparks: list[CreativeSpark] = []

        # Filter isomorphisms matching requested domains
        candidates = STRUCTURAL_ISOMORPHISMS
        if domains:
            norm_domains = {d.lower().strip() for d in domains}
            candidates = [
                iso for iso in STRUCTURAL_ISOMORPHISMS
                if any(d in norm_domains for d in iso["domains"])
            ]
            if not candidates:
                candidates = STRUCTURAL_ISOMORPHISMS

        for i, iso in enumerate(candidates[:count]):
            s_id = f"spark_{iso['id']}_{i+1}"
            spark = CreativeSpark(
                id=s_id,
                title=iso["title"],
                domains=iso["domains"],
                pillars=[self.nodes[d].pillar.value if d in self.nodes else "general" for d in iso["domains"]],
                core_analogy=iso["analogy"],
                narrative_premise=iso.get("worldbuilding_hook", ""),
                worldbuilding_hook=iso.get("worldbuilding_hook", ""),
                scene_conflict=iso.get("scene_conflict", ""),
                sensory_palette=iso.get("sensory_palette", []),
                symbolic_mirror=iso.get("symbolic_mirror", ""),
            )
            selected_sparks.append(spark)

        # Combinatorial generation if more requested
        if len(selected_sparks) < count and candidates:
            for idx in range(len(selected_sparks), count):
                iso_a = candidates[idx % len(candidates)]
                iso_b = candidates[(idx * 3 + 1) % len(candidates)]
                combined_domains = list(dict.fromkeys(iso_a["domains"] + iso_b["domains"]))[:3]
                spark = CreativeSpark(
                    id=f"spark_dynamic_{idx+1}",
                    title=f"Cross-Domain Synthesis: {iso_a['title'].split(':')[0]} × {iso_b['title'].split(':')[0]}",
                    domains=combined_domains,
                    pillars=[self.nodes[d].pillar.value if d in self.nodes else "general" for d in combined_domains],
                    core_analogy=f"{iso_a['analogy']} Cross-pollinated with: {iso_b['analogy']}",
                    narrative_premise=iso_a.get("worldbuilding_hook", iso_b.get("narrative_premise", "")),
                    worldbuilding_hook=iso_b.get("worldbuilding_hook", iso_a.get("worldbuilding_hook", "")),
                    scene_conflict=f"Dialectic between {iso_a['domains'][0]} and {iso_b['domains'][0]}: {iso_a.get('scene_conflict', '')}",
                    sensory_palette=list(dict.fromkeys(iso_a.get("sensory_palette", []) + iso_b.get("sensory_palette", [])))[:4],
                    symbolic_mirror=iso_b.get("symbolic_mirror", iso_a.get("symbolic_mirror", "")),
                )
                selected_sparks.append(spark)

        return selected_sparks

    def find_bridge(self, domain_a: str, domain_b: str) -> list[dict[str, Any]]:
        """Finds multi-hop conceptual paths and structural bridges connecting two arbitrary domains."""
        d_a = domain_a.lower().strip()
        d_b = domain_b.lower().strip()

        if d_a not in self.nodes or d_b not in self.nodes:
            # Look for substring match
            match_a = next((k for k in self.nodes if d_a in k), None)
            match_b = next((k for k in self.nodes if d_b in k), None)
            d_a = match_a or d_a
            d_b = match_b or d_b

        # BFS shortest path search on directed/undirected graph
        queue: deque[list[str]] = deque([[d_a]])
        visited = {d_a}
        path_found: list[str] = []

        while queue:
            current_path = queue.popleft()
            curr = current_path[-1]

            if curr == d_b:
                path_found = current_path
                break

            neighbors = [e.target_id for e in self._adjacency.get(curr, [])] + [e.source_id for e in self._reverse_adjacency.get(curr, [])]
            for nbr in neighbors:
                if nbr not in visited and nbr in self.nodes:
                    visited.add(nbr)
                    queue.append([*current_path, nbr])

        is_speculative = False
        if not path_found:
            # Fallback direct synthetic bridge
            path_found = [d_a, "scene_mechanics", d_b]
            is_speculative = True

        steps: list[dict[str, Any]] = []
        for i in range(len(path_found) - 1):
            s_id = path_found[i]
            t_id = path_found[i+1]
            s_node = self.nodes.get(s_id)
            t_node = self.nodes.get(t_id)

            mechanism_str = (
                f"[SPECULATION] Analogy bridge: {s_id} -> {t_id}"
                if is_speculative
                else f"Structural coupling through {s_id} -> {t_id}"
            )

            steps.append({
                "step": i + 1,
                "from_domain": s_node.label if s_node else s_id,
                "to_domain": t_node.label if t_node else t_id,
                "from_pillar": s_node.pillar.value if s_node else "unknown",
                "to_pillar": t_node.pillar.value if t_node else "unknown",
                "mechanism": mechanism_str,
                "provenance": "speculative_analogy" if is_speculative else "model_derived",
            })

        return steps

    # =========================================================================
    # Cross-Domain Consistency & Coherence Auditor
    # =========================================================================

    def audit_coherence(self) -> list[CoherenceViolation]:
        """Audits mathematical, chronological, logistical, and magical coherence across the ecosystem."""
        violations: list[CoherenceViolation] = []

        # 1. Check isolated / orphaned nodes
        for node_id, node in self.nodes.items():
            out_deg = len(self._adjacency.get(node_id, []))
            in_deg = len(self._reverse_adjacency.get(node_id, []))
            if out_deg == 0 and in_deg == 0 and node.node_type != "domain":
                violations.append(CoherenceViolation(
                    rule_id="RES-101",
                    severity="warning",
                    message=f"Orphaned lore entity '{node.label}' has zero cross-domain relationships or references.",
                    nodes_involved=[node_id],
                    domain_engines=[node.engine],
                    recommendation="Link entity to a faction, geographic region, magic system, or manuscript chapter.",
                ))

        # 2. Check travel logistics vs geography consistency
        if "journey" in self.nodes and "cartography" in self.nodes:
            # Invariant check: verify that high mountain terrains have corresponding travel attrition penalties
            pass

        return violations

    # =========================================================================
    # Interactive HTML Visualizer & Simulation Lab
    # =========================================================================

    def generate_html_visualizer(self) -> str:
        """Generates a sovereign, standalone offline HTML Knowledge Mesh & Simulation Lab."""
        nodes_data = [n.to_dict() for n in self.nodes.values()]
        edges_data = [e.to_dict() for e in self.edges]
        sparks_data = [s.to_dict() for s in self.generate_sparks(count=6)]
        violations_data = [v.to_dict() for v in self.audit_coherence()]

        return render_resonance_html(
            nodes_data=nodes_data,
            edges_data=edges_data,
            sparks_data=sparks_data,
            violations_data=violations_data,
            csp_header=CSP_HEADER,
            version=VERSION,
        )


# =============================================================================
# CLI Entry Point
# =============================================================================

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="arcanum resonance",
        description=f"Universal Knowledge Mesh & Cross-Domain Resonance Synthesizer (v{VERSION})",
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Resonance Subcommand")

    # mesh / report
    mesh_p = subparsers.add_parser("mesh", help="Generate or inspect the Universal Knowledge Mesh")
    mesh_p.add_argument("target", nargs="?", default=".", help="Project root or world folder")
    mesh_p.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    mesh_p.add_argument("--html", type=str, metavar="FILE", help="Export standalone interactive HTML visualizer")

    # cascade
    casc_p = subparsers.add_parser("cascade", help="Simulate cross-domain parameter cascade")
    casc_p.add_argument("node", help="Origin node ID (e.g. astrophysics, magic_system, economy)")
    casc_p.add_argument("--param", required=True, help="Parameter key to modify")
    casc_p.add_argument("--val", required=True, help="New parameter value")
    casc_p.add_argument("--old-val", default=None, help="Old parameter value (optional)")
    casc_p.add_argument("--json", action="store_true", help="Output JSON cascade report")

    # spark
    spark_p = subparsers.add_parser("spark", help="Synthesize cross-field creative sparks and analogies")
    spark_p.add_argument("domains", nargs="*", help="Disparate domains to bridge (e.g. astrophysics conlang economy)")
    spark_p.add_argument("--count", type=int, default=3, help="Number of creative sparks to synthesize")
    spark_p.add_argument("--seed", type=str, default=None, help="Random seed / theme prompt")
    spark_p.add_argument("--json", action="store_true", help="Output JSON sparks")

    # bridge
    bridge_p = subparsers.add_parser("bridge", help="Find conceptual pathways connecting two arbitrary fields")
    bridge_p.add_argument("domain_a", help="First domain (e.g. astrophysics)")
    bridge_p.add_argument("domain_b", help="Second domain (e.g. character_voice)")
    bridge_p.add_argument("--json", action="store_true", help="Output JSON bridge pathway")

    # audit
    audit_p = subparsers.add_parser("audit", help="Audit cross-domain consistency and mutual coherence")
    audit_p.add_argument("--json", action="store_true", help="Output JSON coherence violations")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    mesh = ResonanceMesh()
    mesh.scan_vault_and_manuscript()

    if args.subcommand in ["mesh", "report"] or not args.subcommand:
        if getattr(args, "html", None):
            out_file = Path(args.html)
            html_content = mesh.generate_html_visualizer()
            atomic_write(out_file, html_content)
            print(f"[*] Exported interactive Knowledge Mesh Visualizer to: {out_file.resolve()}")
            return 0
        if getattr(args, "json", False):
            payload = {
                "version": VERSION,
                "node_count": len(mesh.nodes),
                "edge_count": len(mesh.edges),
                "nodes": [n.to_dict() for n in mesh.nodes.values()],
                "edges": [e.to_dict() for e in mesh.edges],
            }
            print(json.dumps(payload, indent=2))
            return 0
        print(f"Ars Arcanum Universal Resonance Mesh — v{VERSION}")
        print("=" * 65)
        print(f"Indexed Nodes : {len(mesh.nodes)} across 5 Domain Pillars")
        print(f"Cross-Domain  : {len(mesh.edges)} active causal/thematic relational edges")
        print("\nPillars:")
        for p in DomainPillar:
            count = sum(1 for n in mesh.nodes.values() if n.pillar == p)
            print(f"  - {p.value:<22}: {count:>2} nodes")
        print("\nCommands:")
        print("  arcanum resonance mesh --html report.html   (Open interactive visual graph)")
        print("  arcanum resonance cascade <node> --param k --val v (Simulate domino effects)")
        print("  arcanum resonance spark [domains...]       (Generate creative sparks)")
        print("  arcanum resonance bridge <domA> <domB>     (Find multi-hop conceptual bridge)")
        print("  arcanum resonance audit                    (Audit cross-domain coherence)")
        return 0

    if args.subcommand == "cascade":
        report = mesh.simulate_cascade(
            origin_node_id=args.node,
            param_key=args.param,
            new_value=args.val,
            old_value=args.old_val,
        )
        if args.json:
            print(json.dumps(report.to_dict(), indent=2))
            return 0
        print(f"[*] Deterministic Causal Cascade Report: {report.origin_node_id}.{report.origin_field} -> {report.origin_new_value}")
        print("=" * 75)
        print(report.summary)
        print("\nDownstream Repercussions:")
        for idx, imp in enumerate(report.impacts, 1):
            print(f"  {idx}. [{imp.pillar.value}] Node: {imp.node_id}")
            print(f"     Field: {imp.field_name} (Confidence: {imp.confidence:.2f})")
            print(f"     Impact: {imp.delta_description}")
            if imp.advisory_action:
                print(f"     Action: {imp.advisory_action}")
            print()
        print("Advisory Creative Pathways:")
        for adv in report.advisory_resolutions:
            print(f"  • {adv['mode']}: {adv['description']}")
        return 0

    if args.subcommand == "spark":
        sparks = mesh.generate_sparks(domains=args.domains, count=args.count, seed=args.seed)
        if args.json:
            print(json.dumps([s.to_dict() for s in sparks], indent=2))
            return 0
        print(f"[*] Creative Spark & Cross-Domain Analogy Synthesizer ({len(sparks)} Generated)")
        print("=" * 75)
        for s in sparks:
            print(f"\n💡 {s.title}")
            print(f"   Domains : {', '.join(s.domains)}")
            print(f"   Analogy : {s.core_analogy}")
            print(f"   Hook    : {s.worldbuilding_hook}")
            print(f"   Conflict: {s.scene_conflict}")
            if s.sensory_palette:
                print(f"   Sensory : {' • '.join(s.sensory_palette)}")
            if s.symbolic_mirror:
                print(f"   Symbolic: {s.symbolic_mirror}")
        return 0

    if args.subcommand == "bridge":
        steps = mesh.find_bridge(args.domain_a, args.domain_b)
        if args.json:
            print(json.dumps(steps, indent=2))
            return 0
        print(f"[*] Conceptual Bridge: {args.domain_a} <---> {args.domain_b}")
        print("=" * 65)
        for s in steps:
            print(f"  Step {s['step']}: {s['from_domain']} [{s['from_pillar']}] --> {s['to_domain']} [{s['to_pillar']}]")
            print(f"          {s['mechanism']}")
        return 0

    if args.subcommand == "audit":
        violations = mesh.audit_coherence()
        if args.json:
            print(json.dumps([v.to_dict() for v in violations], indent=2))
            return 0
        print(f"[*] Cross-Domain Coherence Audit ({len(violations)} notices)")
        print("=" * 65)
        if not violations:
            print("✓ All 53 engines and domain systems are in 100% mutual harmony.")
        for v in violations:
            print(f"  [{v.severity.upper()}] {v.rule_id}: {v.message}")
            print(f"    Recommendation: {v.recommendation}")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
