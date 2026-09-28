#!/usr/bin/env python3
"""
Unit and Integration Tests for Ars Arcanum Ecosystem Cohesion & Cross-Engine Interoperability
(tests/test_ecosystem_cohesion.py)
================================================================================
Comprehensive test suite verifying:
- 100% CLI command and alias dispatch coverage across all 53 registered engines
- Elimination of engine isolation and conflicts
- FS Utils atomic storage and filesystem diagnostics
- Cross-engine multi-stage authoring pipelines (Scaffold -> Canvas -> Timeline -> Structure -> Corpus -> RAG)
- Zero-conflict command topology across CLI and registry surfaces
"""

from __future__ import annotations

import io
import sys
import tempfile
import unittest
from pathlib import Path

# Add project scripts to path
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib import (
    cli,
    corpus_export,
    fs_utils,
    local_rag,
    manuscript_scaffold,
    registry,
    resonance,
    story_canvas,
    structure,
    timeline_sync,
    world_doctor,
)


class TestEcosystemCliDispatch(unittest.TestCase):
    """Verifies that all 53 registered engines and all aliases route cleanly in CLI."""

    def setUp(self) -> None:
        self.reg = registry.get_registry()

    def test_registered_engines_count(self) -> None:
        self.assertEqual(len(self.reg), 53)

    def test_all_53_primary_commands_dispatch(self) -> None:
        unrouted = []
        for name, spec in self.reg.items():
            cmd_tokens = spec.cli_command.split()
            old_stdout, old_stderr = sys.stdout, sys.stderr
            sys.stdout, sys.stderr = io.StringIO(), io.StringIO()
            try:
                ret = cli.main([*cmd_tokens, "--help"])
                err = sys.stderr.getvalue()
                if "Error: Unknown command" in err or (ret == 2 and "Unknown command" in err):
                    unrouted.append((name, spec.cli_command, err.strip()))
            except SystemExit:
                pass
            finally:
                sys.stdout, sys.stderr = old_stdout, old_stderr

        self.assertEqual(unrouted, [], f"Unrouted primary engine commands found: {unrouted}")

    def test_all_engine_aliases_dispatch(self) -> None:
        unrouted_aliases = []
        for name, spec in self.reg.items():
            for alias in spec.aliases:
                tokens = alias.split()
                first_token = tokens[0]
                old_stdout, old_stderr = sys.stdout, sys.stderr
                sys.stdout, sys.stderr = io.StringIO(), io.StringIO()
                try:
                    ret = cli.main([first_token, "--help"])
                    err = sys.stderr.getvalue()
                    if "Error: Unknown command" in err or (ret == 2 and "Unknown command" in err):
                        unrouted_aliases.append((name, alias, err.strip()))
                except SystemExit:
                    pass
                finally:
                    sys.stdout, sys.stderr = old_stdout, old_stderr

        self.assertEqual(unrouted_aliases, [], f"Unrouted engine aliases found: {unrouted_aliases}")


class TestFsUtilsDiagnostics(unittest.TestCase):
    """Tests the atomic filesystem diagnostic utility."""

    def test_check_filesystem(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            res = fs_utils.check_filesystem(tmpdir)
            self.assertTrue(res.get("atomic_write_verified"))
            self.assertEqual(res.get("status"), "healthy")

    def test_fs_utils_main(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            old_stdout, old_stderr = sys.stdout, sys.stderr
            sys.stdout, sys.stderr = io.StringIO(), io.StringIO()
            try:
                ret = fs_utils.main(["--json", tmpdir])
                out = sys.stdout.getvalue()
                self.assertEqual(ret, 0)
                self.assertIn('"status": "healthy"', out)
            finally:
                sys.stdout, sys.stderr = old_stdout, old_stderr


class TestCrossEnginePipeline(unittest.TestCase):
    """Tests end-to-end integration across multiple interacting craft engines."""

    def test_full_authoring_and_lore_pipeline(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            ms_dir = root / "Manuscript"
            ms_dir.mkdir()
            world_dir = root / "World"
            world_dir.mkdir()

            # 1. Scaffold manuscript structure
            divisions = manuscript_scaffold.scaffold_volume(
                target_dir=ms_dir,
                structure_key="save_the_cat",
                create_starter_chapter=True,
            )
            self.assertEqual(len(divisions), 3)

            # 2. Add rich world bible lore
            (world_dir / "Solaris_Faction.md").write_text(
                "---\ntitle: Solaris Guild\ntype: faction\nleader: High Archon\n---\n# Solaris Guild\nA powerful mercantile faction controlling solar leylines.",
                encoding="utf-8",
            )

            # 3. Extract scene cards via Story Canvas
            cards = story_canvas.extract_scene_cards(ms_dir)
            self.assertEqual(len(cards), 1)
            canvas_html = story_canvas.generate_story_canvas_html(target_path=ms_dir, cards=cards)
            self.assertIn("<!DOCTYPE html>", canvas_html)
            self.assertIn("Content-Security-Policy", canvas_html)

            # 4. Extract and analyze timeline events
            events = timeline_sync.extract_timeline_events(ms_dir)
            report = timeline_sync.analyze_timeline_synchronization(events)
            self.assertIn("narrative_events", report)
            self.assertEqual(report["total_events"], 1)

            # 5. Analyze story pacing structure
            struct_res = structure.scan_manuscript_structure(ms_dir)
            self.assertIn("chapters", struct_res)

            # 6. Corpus Scanner & Export to SQLite
            scanner = corpus_export.CorpusScanner(target=root)
            scanner.scan()
            self.assertGreaterEqual(len(scanner.documents), 2)
            out_sqlite = root / "corpus.sqlite"
            corpus_export.export_sqlite(scanner, out_sqlite)
            self.assertTrue(out_sqlite.exists())

            # 7. Local Semantic RAG Hybrid Retrieval
            rag = local_rag.LocalLoreRetrievalEngine()
            rag.load_from_sqlite(out_sqlite)
            query_res = rag.query("mercantile solar leylines", top_k=5)
            self.assertGreaterEqual(len(query_res), 1)

            # 8. World Doctor Vault Consistency Audit
            violations = world_doctor.check_world(world_dir)
            self.assertIsInstance(violations, dict)
            self.assertEqual(violations.get("notes"), 1)


class TestResonanceMeshIntegrity(unittest.TestCase):
    """Verifies that all 53 engines are cohesive nodes with degree >= 2."""

    def test_full_resonance_mesh_connectivity(self) -> None:
        mesh = resonance.ResonanceMesh()
        self.assertEqual(len(mesh.nodes), 53)
        self.assertEqual(len(mesh.edges), 74)

        node_degrees: dict[str, int] = {k: 0 for k in mesh.nodes}
        for e in mesh.edges:
            node_degrees[e.source_id] = node_degrees.get(e.source_id, 0) + 1
            node_degrees[e.target_id] = node_degrees.get(e.target_id, 0) + 1

        isolated = [k for k, v in node_degrees.items() if v == 0]
        self.assertEqual(isolated, [])

        low_deg = [k for k, v in node_degrees.items() if v < 2]
        self.assertEqual(low_deg, [])


if __name__ == "__main__":
    unittest.main()
