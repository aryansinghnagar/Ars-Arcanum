#!/usr/bin/env python3
"""
Unit tests for Ars Arcanum Causal DAG & Time-Travel Consistency Validator (scripts/lib/causality.py).
"""

import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib.causality import (
    extract_causal_nodes,
    audit_causality,
    generate_causality_mermaid,
    generate_causality_html_report,
    normalize_id,
    resolve_world_dir,
    resolve_manuscript_dir,
    main
)


class TestCausalityEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.world_dir = Path(self.temp_dir.name) / "World"
        self.ms_dir = Path(self.temp_dir.name) / "Manuscript"
        self.world_dir.mkdir(parents=True)
        (self.world_dir / "History").mkdir(parents=True)
        self.ms_dir.mkdir(parents=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _write(self, base_dir: Path, rel_path: str, content: str) -> Path:
        target = base_dir / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return target

    def test_normalize_id(self):
        self.assertEqual(normalize_id("Event_One #1"), "event-one-1")

    def test_extract_clean_linear_events(self):
        """Two events with no causal loops -> events_dict has exactly 2 entries."""
        self._write(
            self.ms_dir,
            "scene-alpha.md",
            "---\nname: Alpha\ntimeline: prime\n---\n\nProse for alpha.\n",
        )
        self._write(
            self.ms_dir,
            "scene-beta.md",
            "---\nname: Beta\ntimeline: prime\n---\n\nProse for beta.\n",
        )

        events, _timelines = extract_causal_nodes(self.world_dir, self.ms_dir)

        self.assertEqual(len(events), 2)
        ids = set(events.keys())
        self.assertIn("scene-alpha", ids)
        self.assertIn("scene-beta", ids)

    def test_causal_origins_extracted(self):
        """@causal-origin tag populates the causal_origins list."""
        self._write(
            self.ms_dir,
            "scene-child.md",
            "@timeline: prime\n@causal-origin: scene-parent\n",
        )
        self._write(self.ms_dir, "scene-parent.md", "@timeline: prime\n")

        events, _timelines = extract_causal_nodes(self.world_dir, self.ms_dir)

        self.assertIn("scene-child", events)
        self.assertIn("scene-parent", events["scene-child"]["causal_origins"])

    def test_causes_extracted(self):
        """@causes tag populates the causes list."""
        self._write(
            self.ms_dir,
            "scene-trigger.md",
            "@timeline: prime\n@causes: scene-result\n",
        )
        self._write(self.ms_dir, "scene-result.md", "@timeline: prime\n")

        events, _timelines = extract_causal_nodes(self.world_dir, self.ms_dir)

        self.assertIn("scene-trigger", events)
        self.assertIn("scene-result", events["scene-trigger"]["causes"])

    def test_extract_tag_directives_and_branch_from(self):
        self._write(
            self.world_dir / "History",
            "branch-event.md",
            """---
name: Branch Divergence
timeline: alternate-1
start_year: 1050
---
@branch-from: prime@1045
@causes: alt-consequence
@event: Custom Divergence
@paradox-type: branching
""",
        )
        events, timelines = extract_causal_nodes(self.world_dir, self.ms_dir)
        self.assertIn("custom-divergence", events)
        self.assertIn("alternate-1", timelines)

    def test_extract_skip_front_matter_and_hidden(self):
        self._write(self.ms_dir, ".hidden.md", "@timeline: prime\n")
        self._write(self.ms_dir, "Front_Matter/title.md", "@timeline: prime\n")
        events, _ = extract_causal_nodes(self.world_dir, self.ms_dir)
        self.assertNotIn(".hidden", events)
        self.assertNotIn("title", events)

    def test_unregistered_bootstrap_cau102(self):
        """Mutual causation without paradox_type -> CAU-102 (unregistered bootstrap)."""
        self._write(
            self.ms_dir,
            "scene-a.md",
            "---\ncauses: [scene-b]\n---\n\n@timeline: prime\n",
        )
        self._write(
            self.ms_dir,
            "scene-b.md",
            "---\ncauses: [scene-a]\n---\n\n@timeline: prime\n",
        )

        events, timelines = extract_causal_nodes(self.world_dir, self.ms_dir)
        findings = audit_causality(events, timelines)

        codes = [f["id"] for f in findings]
        self.assertIn("CAU-102", codes)

    def test_grandfather_paradox_cau101(self):
        """Cycle with paradox_type=grandfather -> CAU-101."""
        self._write(
            self.ms_dir,
            "event-gramps.md",
            "---\ncauses: [event-killer]\nparadox_type: grandfather\n---\n\n@timeline: prime\n",
        )
        self._write(
            self.ms_dir,
            "event-killer.md",
            "---\ncauses: [event-gramps]\nparadox_type: grandfather\n---\n\n@timeline: prime\n",
        )

        events, timelines = extract_causal_nodes(self.world_dir, self.ms_dir)
        findings = audit_causality(events, timelines)

        codes = [f["id"] for f in findings]
        self.assertIn("CAU-101", codes)

    def test_novikov_violation_cau103(self):
        """Cycle with paradox_type=novikov-violation -> CAU-103."""
        self._write(
            self.ms_dir,
            "event-nova.md",
            "---\ncauses: [event-anti]\nparadox_type: novikov-violation\n---\n\n@timeline: prime\n",
        )
        self._write(
            self.ms_dir,
            "event-anti.md",
            "---\ncauses: [event-nova]\nparadox_type: novikov-violation\n---\n\n@timeline: prime\n",
        )

        events, timelines = extract_causal_nodes(self.world_dir, self.ms_dir)
        findings = audit_causality(events, timelines)

        codes = [f["id"] for f in findings]
        self.assertIn("CAU-103", codes)

    def test_intentional_bootstrap_no_violation(self):
        """Cycle tagged paradox_type=bootstrap is self-consistent -> no CAU-101/102/103."""
        self._write(
            self.ms_dir,
            "event-loop-x.md",
            "---\ncauses: [event-loop-y]\nparadox_type: bootstrap\n---\n\n@timeline: prime\n",
        )
        self._write(
            self.ms_dir,
            "event-loop-y.md",
            "---\ncauses: [event-loop-x]\nparadox_type: bootstrap\n---\n\n@timeline: prime\n",
        )

        events, timelines = extract_causal_nodes(self.world_dir, self.ms_dir)
        findings = audit_causality(events, timelines)

        violation_codes = {"CAU-101", "CAU-102", "CAU-103"}
        raised = {f["id"] for f in findings}
        self.assertTrue(
            raised.isdisjoint(violation_codes),
            f"Unexpected violation codes for intentional bootstrap: {raised & violation_codes}",
        )

    def test_orphan_timeline_cau104(self):
        events = {"scene-1": {"id": "scene-1", "timeline": "prime", "time_coord": "", "causal_origins": [], "causes": [], "paradox_type": ""}}
        timelines = {
            "prime": {"id": "prime", "events": ["scene-1"]},
            "orphan-timeline": {"id": "orphan-timeline", "events": []}
        }
        findings = audit_causality(events, timelines)
        self.assertTrue(any(f["id"] == "CAU-104" for f in findings))

    def test_dangling_causal_origin_cau105(self):
        """Event referencing a nonexistent causal origin -> CAU-105."""
        self._write(
            self.ms_dir,
            "scene-orphan.md",
            "@timeline: prime\n@causal-origin: ghost-event-xyz\n",
        )

        events, timelines = extract_causal_nodes(self.world_dir, self.ms_dir)
        findings = audit_causality(events, timelines)

        codes = [f["id"] for f in findings]
        self.assertIn("CAU-105", codes)

    def test_temporal_inversion_cau106(self):
        """Cause occurring chronologically after effect without time-travel -> CAU-106."""
        self._write(
            self.ms_dir,
            "scene-late-cause.md",
            "@timeline: prime\n@time: 300\n@causes: scene-early-effect\n",
        )
        self._write(
            self.ms_dir,
            "scene-early-effect.md",
            "@timeline: prime\n@time: 100\n",
        )

        events, timelines = extract_causal_nodes(self.world_dir, self.ms_dir)
        findings = audit_causality(events, timelines)

        codes = [f["id"] for f in findings]
        self.assertIn("CAU-106", codes)

    def test_dynamic_butterfly_cau201(self):
        self._write(self.ms_dir, "event-1.md", "---\ncauses: [event-2]\nparadox_type: dynamic\n---\n@timeline: prime\n")
        self._write(self.ms_dir, "event-2.md", "---\ncauses: [event-1]\nparadox_type: dynamic\n---\n@timeline: prime\n")
        events, timelines = extract_causal_nodes(self.world_dir, self.ms_dir)
        findings = audit_causality(events, timelines)
        self.assertTrue(any(f["id"] == "CAU-201" for f in findings))

    def test_other_paradox_types(self):
        # groundhog loop
        self._write(self.ms_dir, "g1.md", "---\ncauses: [g2]\nparadox_type: groundhog\n---\n@timeline: prime\n")
        self._write(self.ms_dir, "g2.md", "---\ncauses: [g1]\nparadox_type: groundhog\n---\n@timeline: prime\n")
        # multiverse
        self._write(self.ms_dir, "m1.md", "---\ncauses: [m2]\nparadox_type: multiverse\n---\n@timeline: prime\n")
        self._write(self.ms_dir, "m2.md", "---\ncauses: [m1]\nparadox_type: multiverse\n---\n@timeline: prime\n")
        # relativistic
        self._write(self.ms_dir, "r1.md", "---\ncauses: [r2]\nparadox_type: relativistic\n---\n@timeline: prime\n")
        self._write(self.ms_dir, "r2.md", "---\ncauses: [r1]\nparadox_type: relativistic\n---\n@timeline: prime\n")

        events, timelines = extract_causal_nodes(self.world_dir, self.ms_dir)
        findings = audit_causality(events, timelines)
        self.assertTrue(any(f["id"] == "CAU-202" for f in findings))

    def test_resolvers(self):
        w_res = resolve_world_dir(str(self.world_dir))
        self.assertEqual(Path(w_res).resolve(), self.world_dir.resolve())
        m_res = resolve_manuscript_dir(str(self.ms_dir))
        self.assertEqual(Path(m_res).resolve(), self.ms_dir.resolve())
        self.assertEqual(resolve_manuscript_dir("nonexistent_path_12345"), "")

    def test_generate_causality_mermaid(self):
        """generate_causality_mermaid returns a string with 'graph TD' and 'mermaid'."""
        self._write(self.ms_dir, "scene-x.md", "@timeline: prime\n")
        self._write(
            self.ms_dir,
            "scene-y.md",
            "@timeline: prime\n@causes: scene-x\n",
        )

        events, timelines = extract_causal_nodes(self.world_dir, self.ms_dir)
        output = generate_causality_mermaid(events, timelines)

        self.assertIsInstance(output, str)
        self.assertIn("mermaid", output)
        self.assertIn("graph TD", output)

    def test_generate_causality_html_report(self):
        """HTML report is written, has CSP header, and contains 'Causal DAG'."""
        self._write(self.ms_dir, "scene-p.md", "@timeline: prime\n")
        self._write(
            self.ms_dir,
            "scene-q.md",
            "@timeline: prime\n@causes: scene-p\n",
        )

        events, timelines = extract_causal_nodes(self.world_dir, self.ms_dir)
        findings = audit_causality(events, timelines)

        report_path = Path(self.temp_dir.name) / "causality_report.html"
        audit_data = {
            "events": events,
            "timelines": timelines,
            "findings": findings,
            "world": "TestWorld",
        }
        generate_causality_html_report(audit_data, report_path)

        self.assertTrue(report_path.exists(), "HTML report file was not created")
        html = report_path.read_text(encoding="utf-8")
        self.assertIn("Content-Security-Policy", html)
        self.assertIn("Causal DAG", html)

    def test_clean_world_zero_findings(self):
        """Linear chain A->B->C with no cycles -> 0 audit findings."""
        self._write(self.ms_dir, "event-aaa.md", "@timeline: prime\n")
        self._write(
            self.ms_dir,
            "event-bbb.md",
            "@timeline: prime\n@causal-origin: event-aaa\n",
        )
        self._write(
            self.ms_dir,
            "event-ccc.md",
            "@timeline: prime\n@causal-origin: event-bbb\n",
        )

        events, timelines = extract_causal_nodes(self.world_dir, self.ms_dir)
        findings = audit_causality(events, timelines)

        self.assertEqual(len(findings), 0)

    def test_cli_subcommands(self):
        self._write(self.ms_dir, "scene-1.md", "---\nname: Start\n---\n@timeline: prime\n")
        self._write(self.ms_dir, "scene-2.md", "---\nname: Middle\n---\n@timeline: prime\n@causal-origin: scene-1\n")

        html_p = Path(self.temp_dir.name) / "c_report.html"
        note_p = Path(self.temp_dir.name) / "c_note.md"

        # 1. branch command
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            with patch("sys.argv", ["causality.py", "branch", "Dark Timeline", "--from-timeline", "prime", "--at-coord", "Year 500"]):
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 0)
                self.assertIn("dark-timeline", mock_out.getvalue())

        # 2. check command with clean DAG (exit 0)
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            with patch("sys.argv", ["causality.py", "check", "-w", str(self.world_dir), "-m", str(self.ms_dir), "--html", str(html_p), "--write-note", str(note_p)]):
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 0)
                self.assertIn("Causal DAG is acyclic and self-consistent", mock_out.getvalue())
                self.assertTrue(html_p.is_file())
                self.assertTrue(note_p.is_file())

        # 3. check json
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            with patch("sys.argv", ["causality.py", "dag", "-w", str(self.world_dir), "-m", str(self.ms_dir), "--json"]):
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 0)
                data = json.loads(mock_out.getvalue())
                self.assertEqual(data["events_count"], 2)

        # 4. check with finding -> exit 1
        self._write(self.ms_dir, "bad-loop.md", "@timeline: prime\n@causal-origin: non-existent\n")
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            with patch("sys.argv", ["causality.py", "-w", str(self.world_dir), "-m", str(self.ms_dir)]):
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 1)
                self.assertIn("CAU-105", mock_out.getvalue())

        # 5. missing targets error -> exit 2
        with patch("sys.stderr", new_callable=io.StringIO), patch("sys.argv", ["causality.py", "check"]):
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 2)


    def test_deliberate_and_surreal_cycle_bypass(self):
        """Cycles tagged with @intent: deliberate or @modality: surreal are recognized as artistic choices and bypassed."""
        self._write(
            self.ms_dir,
            "dream-loop-a.md",
            "---\nintent: deliberate\n---\n@timeline: prime\n@causal-origin: dream-loop-b\n",
        )
        self._write(
            self.ms_dir,
            "dream-loop-b.md",
            "@timeline: prime\n@causal-origin: dream-loop-a\n",
        )

        events, timelines = extract_causal_nodes(self.world_dir, self.ms_dir)
        findings = audit_causality(events, timelines)
        self.assertEqual(len(findings), 0, "Deliberate paradoxical cycle should be bypassed without error")

        # Test inline directive @modality: surreal
        self._write(
            self.ms_dir,
            "mythic-a.md",
            "@timeline: myth\n@modality: surreal\n@causal-origin: mythic-b\n",
        )
        self._write(
            self.ms_dir,
            "mythic-b.md",
            "@timeline: myth\n@causal-origin: mythic-a\n",
        )

        events2, timelines2 = extract_causal_nodes(self.world_dir, self.ms_dir)
        findings2 = audit_causality(events2, timelines2)
        self.assertEqual(len(findings2), 0, "Surreal modality cycle should be bypassed without error")


if __name__ == "__main__":
    unittest.main()
