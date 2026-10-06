#!/usr/bin/env python3
"""
Unit and Integration Tests for Ars Arcanum Universal Resonance Mesh Engine
(tests/test_resonance.py)
================================================================================
Comprehensive test suite verifying:
- Universal Domain Pillar partitioning and Knowledge Mesh topology
- Deterministic Causal Cascade calculations across physics, economy, factions, tactics, and prose
- Multi-tiered Creative Spark and structural isomorphism synthesis
- Multi-hop conceptual bridge shortest-path graph traversals
- Cross-domain coherence and consistency auditing
- Standalone offline HTML visualizer with strict Content Security Policy
- Unified CLI dispatching (`arcanum resonance`, `cascade`, `spark`, `bridge`, `audit`)
- Studio Hub and Zen Studio cross-engine data integration
- Engine registry compliance, metadata invariants, and advisory resolution pathways
"""

import sys
import tempfile
import unittest
from pathlib import Path

# Add project scripts to path
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.resonance import (
    CSP_HEADER,
    CascadeReport,
    CreativeSpark,
    CrossDomainEdge,
    CrossDomainNode,
    DomainPillar,
    ResonanceMesh,
    STRUCTURAL_ISOMORPHISMS,
    main as resonance_main,
)
from lib.registry import get_engine
from lib.studio_hub import collect_studio_hub_data, generate_studio_hub_html
from lib.zen_studio import build_zen_studio_bundle
from lib.cli import main as cli_main


class TestResonanceMeshPrimitives(unittest.TestCase):
    """Test core graph primitives, pillars, and foundational mesh construction."""

    def setUp(self) -> None:
        self.mesh = ResonanceMesh()

    def test_pillar_definitions(self) -> None:
        pillars = list(DomainPillar)
        self.assertEqual(len(pillars), 5)
        self.assertIn(DomainPillar.COSMOLOGY_PHYSICS, pillars)
        self.assertIn(DomainPillar.SOCIETY_SYSTEMS, pillars)
        self.assertIn(DomainPillar.NARRATIVE_CHRONOLOGY, pillars)
        self.assertIn(DomainPillar.STYLISTICS_SENSES, pillars)
        self.assertIn(DomainPillar.AUTHORING_PRODUCTION, pillars)

    def test_foundational_mesh_nodes(self) -> None:
        # All 47 canonical domain engines should be initialized as domain nodes
        self.assertEqual(len(self.mesh.nodes), 47)
        self.assertIn("astrophysics", self.mesh.nodes)
        self.assertIn("climate", self.mesh.nodes)
        self.assertIn("economy", self.mesh.nodes)
        self.assertIn("factions", self.mesh.nodes)
        self.assertIn("magic_system", self.mesh.nodes)
        self.assertIn("conlang", self.mesh.nodes)
        self.assertIn("dramatis_personae", self.mesh.nodes)
        self.assertIn("manuscript_scaffold", self.mesh.nodes)
        self.assertIn("tips", self.mesh.nodes)
        self.assertIn("resonance", self.mesh.nodes)
        self.assertIn("vault_search", self.mesh.nodes)

    def test_foundational_mesh_edges(self) -> None:
        self.assertEqual(len(self.mesh.edges), 71)
        # Check specific cross-domain causal edges
        relations = [(e.source_id, e.target_id, e.relation) for e in self.mesh.edges]
        self.assertIn(("astrophysics", "climate", "causally_drives"), relations)
        self.assertIn(("ecology", "economy", "economically_impacts"), relations)
        self.assertIn(("factions", "tactical_sim", "manifests_in"), relations)
        self.assertIn(("world_doctor", "codex_export", "constrains"), relations)
        self.assertIn(("writing_sprint", "zen_studio", "manifests_in"), relations)
        self.assertIn(("manuscript_diff", "revision_heatmap", "causally_drives"), relations)
        self.assertIn(("portfolio", "studio_hub", "manifests_in"), relations)
        self.assertIn(("importer", "manuscript_scaffold", "causally_drives"), relations)
        self.assertIn(("docx_sync", "preflight", "constrains"), relations)
        self.assertIn(("diagnostics", "fs_utils", "constrains"), relations)
        self.assertIn(("frontmatter_builder", "continuity", "constrains"), relations)
        self.assertIn(("migrate", "world_doctor", "causally_drives"), relations)
        self.assertIn(("config", "studio_hub", "manifests_in"), relations)
        self.assertIn(("cache", "vault_search", "causally_drives"), relations)
        self.assertIn(("fs_utils", "corpus_export", "constrains"), relations)

    def test_zero_isolated_nodes_across_ecosystem(self) -> None:
        """Verifies that 100% of the 53 registered engines have degree >= 2 in the resonance mesh."""
        node_degrees: dict[str, int] = dict.fromkeys(self.mesh.nodes, 0)
        for e in self.mesh.edges:
            node_degrees[e.source_id] = node_degrees.get(e.source_id, 0) + 1
            node_degrees[e.target_id] = node_degrees.get(e.target_id, 0) + 1

        isolated = [k for k, v in node_degrees.items() if v == 0]
        self.assertEqual(isolated, [], f"Found isolated nodes in resonance mesh: {isolated}")

        low_degree = [k for k, v in node_degrees.items() if v < 2]
        self.assertEqual(low_degree, [], f"Found low connectivity nodes (degree < 2): {low_degree}")

    def test_node_and_edge_serialization(self) -> None:
        node = CrossDomainNode(
            id="test_node",
            label="Test Lore Node",
            pillar=DomainPillar.COSMOLOGY_PHYSICS,
            engine="astrophysics",
            node_type="custom_star",
            attributes={"mass": 1.2},
            tags=["binary", "sol"],
        )
        d = node.to_dict()
        self.assertEqual(d["id"], "test_node")
        self.assertEqual(d["pillar"], "cosmology_physics")
        self.assertEqual(d["attributes"]["mass"], 1.2)

        edge = CrossDomainEdge(
            source_id="test_node",
            target_id="climate",
            relation="causally_drives",
            strength=0.95,
            description="Star mass dictates insolation",
        )
        ed = edge.to_dict()
        self.assertEqual(ed["source_id"], "test_node")
        self.assertEqual(ed["relation"], "causally_drives")


class TestCausalCascadeEngine(unittest.TestCase):
    """Test deterministic multi-hop simulation cascade across disparate fields."""

    def setUp(self) -> None:
        self.mesh = ResonanceMesh()

    def test_astrophysics_axial_tilt_cascade(self) -> None:
        report = self.mesh.simulate_cascade(
            origin_node_id="astrophysics",
            param_key="axial_tilt",
            new_value=38.5,
            old_value=23.4,
        )
        self.assertIsInstance(report, CascadeReport)
        self.assertEqual(report.origin_node_id, "astrophysics")
        self.assertGreaterEqual(len(report.impacts), 4)

        impact_nodes = {i.node_id: i for i in report.impacts}
        self.assertIn("climate", impact_nodes)
        self.assertIn("ecology", impact_nodes)
        self.assertIn("economy", impact_nodes)
        self.assertIn("tactical_sim", impact_nodes)
        self.assertIn("scene_mechanics", impact_nodes)

        # Check that climate seasonal extremes are flagged
        self.assertIn("Severe Continental Seasons", impact_nodes["climate"].new_value)
        # Check advisory resolutions
        self.assertEqual(len(report.advisory_resolutions), 3)
        modes = [a["mode"] for a in report.advisory_resolutions]
        self.assertIn("Hard Realism", modes)
        self.assertIn("Speculative / Trope", modes)
        self.assertIn("Creative Sovereignty", modes)

    def test_magic_system_cost_cascade(self) -> None:
        report = self.mesh.simulate_cascade(
            origin_node_id="magic_system",
            param_key="magic_cost",
            new_value="high_backlash",
        )
        impact_nodes = {i.node_id: i for i in report.impacts}
        self.assertIn("factions", impact_nodes)
        self.assertIn("economy", impact_nodes)
        self.assertIn("prophecy", impact_nodes)

    def test_macroeconomic_debasement_cascade(self) -> None:
        report = self.mesh.simulate_cascade(
            origin_node_id="economy",
            param_key="currency_debasement",
            new_value=0.65,
        )
        impact_nodes = {i.node_id: i for i in report.impacts}
        self.assertIn("factions", impact_nodes)
        self.assertIn("tactical_sim", impact_nodes)
        self.assertIn("voice", impact_nodes)
        self.assertIn("Subversive", impact_nodes["voice"].new_value)

    def test_stellar_mass_cascade(self) -> None:
        report = self.mesh.simulate_cascade(
            origin_node_id="astrophysics",
            param_key="stellar_mass",
            new_value=1.4,
        )
        impact_nodes = {i.node_id: i for i in report.impacts}
        self.assertIn("calendar", impact_nodes)
        self.assertIn("conlang", impact_nodes)

    def test_fallback_graph_traversal_cascade(self) -> None:
        # Test cascade on custom node with no hardcoded rule
        custom_node = CrossDomainNode(
            id="custom_leyline",
            label="Ancient Leyline Hub",
            pillar=DomainPillar.SOCIETY_SYSTEMS,
            engine="magic_system",
            node_type="leyline_hub",
        )
        self.mesh.add_node(custom_node)
        self.mesh.add_edge(CrossDomainEdge(
            source_id="custom_leyline",
            target_id="factions",
            relation="contested_territory",
            strength=0.88,
            description="Factions fight for control of the leyline hub",
        ))

        report = self.mesh.simulate_cascade(
            origin_node_id="custom_leyline",
            param_key="mana_saturation",
            new_value="overflow",
        )
        self.assertGreaterEqual(len(report.impacts), 1)
        self.assertEqual(report.impacts[0].node_id, "factions")


class TestCreativeSparkSynthesizer(unittest.TestCase):
    """Test multidisciplinary creative spark generation and structural analogies."""

    def setUp(self) -> None:
        self.mesh = ResonanceMesh()

    def test_isomorphisms_exist(self) -> None:
        self.assertGreaterEqual(len(STRUCTURAL_ISOMORPHISMS), 6)
        for iso in STRUCTURAL_ISOMORPHISMS:
            self.assertIn("id", iso)
            self.assertIn("title", iso)
            self.assertIn("domains", iso)
            self.assertIn("analogy", iso)
            self.assertIn("worldbuilding_hook", iso)
            self.assertIn("scene_conflict", iso)
            self.assertIn("sensory_palette", iso)

    def test_generate_sparks_all(self) -> None:
        sparks = self.mesh.generate_sparks(count=4)
        self.assertEqual(len(sparks), 4)
        for s in sparks:
            self.assertIsInstance(s, CreativeSpark)
            self.assertTrue(s.title)
            self.assertTrue(s.core_analogy)
            self.assertTrue(s.worldbuilding_hook)
            self.assertTrue(s.scene_conflict)
            self.assertGreaterEqual(len(s.sensory_palette), 1)

    def test_generate_sparks_filtered_domains(self) -> None:
        sparks = self.mesh.generate_sparks(domains=["astrophysics", "economy"], count=2)
        self.assertGreaterEqual(len(sparks), 1)
        # Should match thermo-politics or orbital-prophecy
        matched_domains = set()
        for s in sparks:
            matched_domains.update(s.domains)
        self.assertTrue(any(d in matched_domains for d in ["astrophysics", "economy"]))

    def test_conceptual_bridge_shortest_path(self) -> None:
        # Find bridge from astrophysics to conlang
        steps = self.mesh.find_bridge("astrophysics", "conlang")
        self.assertGreaterEqual(len(steps), 2)
        # First step starts from astrophysics
        self.assertIn("astrophysics", steps[0]["from_domain"].lower())
        # Final step reaches conlang
        self.assertIn("conlang", steps[-1]["to_domain"].lower())


class TestVaultAndManuscriptScanner(unittest.TestCase):
    """Test indexing of actual markdown files in World vaults and Manuscripts."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.world_dir = self.root / "World"
        self.ms_dir = self.root / "Manuscript"
        self.world_dir.mkdir()
        self.ms_dir.mkdir()

        # Create dummy world lore note
        (self.world_dir / "Aethelgard.md").write_text(
            """---
name: Aethelgard
type: planet
category: Cosmology
tags: [habitable, terrestrial]
---
# Aethelgard
A rocky terrestrial world orbiting [[Sol-Invictus]]. Home to [[House-Valerius]].
""",
            encoding="utf-8",
        )

        # Create dummy chapter
        (self.ms_dir / "01_Chapter.md").write_text(
            """---
title: The Frost Awakening
pov: Kaelen
status: Draft
---
# Chapter 1: The Frost Awakening
The cold wind bit through the wool cloak as Kaelen gazed at [[Aethelgard]].
""",
            encoding="utf-8",
        )

        self.mesh = ResonanceMesh(self.root)
        self.mesh.scan_vault_and_manuscript(self.world_dir, self.ms_dir)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_scanned_nodes_populated(self) -> None:
        self.assertIn("entity_aethelgard", self.mesh.nodes)
        self.assertIn("chapter_01_chapter", self.mesh.nodes)

        aethel_node = self.mesh.nodes["entity_aethelgard"]
        self.assertEqual(aethel_node.label, "Aethelgard")
        self.assertEqual(aethel_node.pillar, DomainPillar.COSMOLOGY_PHYSICS)
        self.assertEqual(aethel_node.engine, "astrophysics")

        chap_node = self.mesh.nodes["chapter_01_chapter"]
        self.assertEqual(chap_node.label, "The Frost Awakening")
        self.assertEqual(chap_node.pillar, DomainPillar.NARRATIVE_CHRONOLOGY)

    def test_scanned_wikilink_edges(self) -> None:
        # Aethelgard should link to Sol-Invictus and House-Valerius
        out_edges = [e.target_id for e in self.mesh._adjacency.get("entity_aethelgard", [])]
        self.assertIn("entity_sol_invictus", out_edges)
        self.assertIn("entity_house_valerius", out_edges)


class TestCoherenceAuditor(unittest.TestCase):
    """Test consistency and mutual coherence auditing across engines."""

    def setUp(self) -> None:
        self.mesh = ResonanceMesh()

    def test_coherence_audit_clean_defaults(self) -> None:
        violations = self.mesh.audit_coherence()
        # Default domain engines are interconnected so no orphaned domain engines
        domain_violations = [v for v in violations if v.rule_id == "RES-101" and self.mesh.nodes[v.nodes_involved[0]].node_type == "domain"]
        self.assertEqual(len(domain_violations), 0)

    def test_orphaned_custom_node_audit(self) -> None:
        orphan = CrossDomainNode(
            id="entity_lonely_character",
            label="Forgotten NPC",
            pillar=DomainPillar.NARRATIVE_CHRONOLOGY,
            engine="dramatis_personae",
            node_type="character",
        )
        self.mesh.add_node(orphan)
        violations = self.mesh.audit_coherence()
        orphan_viols = [v for v in violations if "entity_lonely_character" in v.nodes_involved]
        self.assertEqual(len(orphan_viols), 1)
        self.assertEqual(orphan_viols[0].rule_id, "RES-101")


class TestHTMLVisualizerExport(unittest.TestCase):
    """Test standalone offline interactive HTML Knowledge Mesh Visualizer."""

    def setUp(self) -> None:
        self.mesh = ResonanceMesh()
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_html_generation_and_csp(self) -> None:
        html_str = self.mesh.generate_html_visualizer()
        self.assertIn("<!DOCTYPE html>", html_str)
        self.assertIn(CSP_HEADER, html_str)
        self.assertIn("Universal Knowledge & Resonance Mesh", html_str)
        self.assertIn("Causal Cascade Sandbox", html_str)
        self.assertIn("Creative Spark Lab", html_str)
        self.assertIn("Coherence Audit", html_str)
        # Ensure zero remote CDNs or scripts
        self.assertNotIn("https://cdn", html_str)
        self.assertNotIn("http://cdn", html_str)
        self.assertNotIn("unpkg.com", html_str)

    def test_cli_html_export(self) -> None:
        out_file = Path(self.temp_dir.name) / "mesh_test.html"
        ret = resonance_main(["mesh", "--html", str(out_file)])
        self.assertEqual(ret, 0)
        self.assertTrue(out_file.exists())
        self.assertGreater(out_file.stat().st_size, 5000)


class TestCLIRoutingAndIntegration(unittest.TestCase):
    """Test unified CLI commands for resonance mesh, cascade, spark, bridge, and audit."""

    def test_cli_mesh_summary(self) -> None:
        ret = cli_main(["resonance", "mesh"])
        self.assertEqual(ret, 0)

    def test_cli_cascade(self) -> None:
        ret = cli_main(["cascade", "astrophysics", "--param", "axial_tilt", "--val", "35.0"])
        self.assertEqual(ret, 0)

    def test_cli_spark(self) -> None:
        ret = cli_main(["spark", "astrophysics", "conlang", "--count", "2"])
        self.assertEqual(ret, 0)

    def test_cli_bridge(self) -> None:
        ret = cli_main(["bridge", "astrophysics", "voice"])
        self.assertEqual(ret, 0)

    def test_cli_doc_resonance(self) -> None:
        ret = cli_main(["doc", "resonance"])
        self.assertEqual(ret, 0)


class TestStudioHubAndZenStudioResonance(unittest.TestCase):
    """Test telemetry integration in Studio Hub and Zen Studio."""

    def test_studio_hub_telemetry_contains_resonance(self) -> None:
        data = collect_studio_hub_data()
        self.assertIn("resonance", data)
        self.assertIn("resonance_nodes_count", data["metrics"])
        self.assertIn("resonance_edges_count", data["metrics"])
        self.assertGreaterEqual(data["metrics"]["resonance_nodes_count"], 47)
        self.assertGreaterEqual(len(data["resonance"]["sparks"]), 1)

    def test_studio_hub_html_contains_resonance_tab(self) -> None:
        data = collect_studio_hub_data()
        html_out = generate_studio_hub_html(data)
        self.assertIn("tab-resonance", html_out)
        self.assertIn("Universal Mesh Nodes", html_out)
        self.assertIn("Deterministic Causal Cascade Sandbox", html_out)
        self.assertIn("Creative Spark & Cross-Domain Analogy Lab", html_out)
        self.assertIn("renderHubCascadeSandbox", html_out)

    def test_zen_studio_bundle_contains_sparks(self) -> None:
        temp_dir = tempfile.TemporaryDirectory()
        try:
            target_html = Path(temp_dir.name) / "zen.html"
            build_zen_studio_bundle(Path("scripts/lib"), output_path=target_html)
            content = target_html.read_text(encoding="utf-8")
            self.assertIn("tabBtnSparks", content)
            self.assertIn("💡 Sparks", content)
            self.assertIn("sparks = [", content)
        finally:
            temp_dir.cleanup()


class TestEngineRegistryCompliance(unittest.TestCase):
    """Test registry invariants for resonance spec."""

    def test_resonance_registered(self) -> None:
        spec = get_engine("resonance")
        self.assertIsNotNone(spec)
        assert spec is not None
        self.assertEqual(spec.name, "resonance")
        self.assertEqual(spec.cli_command, "resonance")
        self.assertGreaterEqual(len(spec.subfeatures), 4)
        self.assertTrue(spec.logic_documentation)
        self.assertTrue(spec.scientific_logic)
        self.assertTrue(spec.why_this_way)
        self.assertTrue(spec.worldbuilding_relevance)
        self.assertTrue(spec.storytelling_relevance)
        self.assertTrue(spec.writing_relevance)
        self.assertGreaterEqual(len(spec.advisory_guidance), 1)

class TestResonanceCliAndAdvanced(unittest.TestCase):
    """Test CLI JSON options, audit commands, dynamic sparks, and fallback bridge."""

    def setUp(self) -> None:
        self.mesh = ResonanceMesh()

    def test_dynamic_sparks_and_bridge_fallback(self) -> None:
        # Requesting more sparks than hardcoded (e.g. 15) triggers dynamic spark generation
        sparks = self.mesh.generate_sparks(count=15)
        self.assertEqual(len(sparks), 15)
        self.assertTrue(any("dynamic" in s.id for s in sparks))

        # Fallback bridge when domains are completely disconnected or fake
        mesh = ResonanceMesh()
        mesh.nodes.clear()
        mesh.edges.clear()
        mesh._adjacency.clear()
        mesh._reverse_adjacency.clear()
        node_a = CrossDomainNode("alpha", "Alpha", DomainPillar.COSMOLOGY_PHYSICS, "astrophysics", "domain")
        node_b = CrossDomainNode("beta", "Beta", DomainPillar.SOCIETY_SYSTEMS, "economy", "domain")
        mesh.add_node(node_a)
        mesh.add_node(node_b)
        steps = mesh.find_bridge("alpha", "beta")
        self.assertGreaterEqual(len(steps), 1)

    def test_resonance_cli_json_and_audit(self) -> None:
        # mesh --json
        self.assertEqual(resonance_main(["mesh", "--json"]), 0)
        # cascade --json
        self.assertEqual(resonance_main(["cascade", "astrophysics", "--param", "axial_tilt", "--val", "30", "--json"]), 0)
        # spark --json
        self.assertEqual(resonance_main(["spark", "--json"]), 0)
        # bridge --json
        self.assertEqual(resonance_main(["bridge", "astrophysics", "voice", "--json"]), 0)
        # audit --json and audit human readable
        self.assertEqual(resonance_main(["audit", "--json"]), 0)
        self.assertEqual(resonance_main(["audit"]), 0)


if __name__ == "__main__":
    unittest.main()


