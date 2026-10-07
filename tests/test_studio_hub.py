#!/usr/bin/env python3
"""
Unit and Integration Tests for Ars Arcanum Sovereign Studio Desktop Hub
(tests/test_studio_hub.py)
================================================================================
Validates data aggregation, static HTML dashboard compilation, CSP compliance,
REST/JSON API request handlers, and CLI invocation.
"""

import http.client
import json
import socketserver
import tempfile
import threading
import time
import unittest
from pathlib import Path
from typing import Any

from scripts.lib.studio_hub import (
    HUB_VERSION,
    SovereignStudioHandler,
    analyze_structure_harmony,
    collect_studio_hub_data,
    export_static_studio_hub,
    extract_timeline_summary,
    generate_studio_hub_html,
    get_engine_catalog,
    main as studio_hub_main,
    scan_lore_entities,
    scan_manuscript_chapters,
)


class TestStudioHubEngine(unittest.TestCase):
    """Tests data scanning, telemetry metrics, and static HTML generation."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

        # Create sample World directory
        self.world_dir = self.root / "World"
        self.world_dir.mkdir(parents=True, exist_ok=True)
        (self.world_dir / "world.yaml").write_text("name: Eldoria\n", encoding="utf-8")

        chars_dir = self.world_dir / "Characters"
        chars_dir.mkdir(parents=True, exist_ok=True)
        (chars_dir / "Kaelen.md").write_text(
            "---\nname: Kaelen\ntags: [protagonist, mage]\naliases: [The Silver Blade]\n---\n"
            "# Kaelen\nA solitary spellblade wandering the shattered valleys.\n",
            encoding="utf-8",
        )

        magic_dir = self.world_dir / "Magic"
        magic_dir.mkdir(parents=True, exist_ok=True)
        (magic_dir / "RuneCasting.md").write_text(
            "---\nname: Rune Casting\ntags: [hard_magic, glyphs]\n---\n"
            "# Rune Casting\nMagic requires physical inscription into conductive silver.\n",
            encoding="utf-8",
        )

        # Create sample Manuscript directory
        self.ms_dir = self.root / "Manuscript"
        self.ms_dir.mkdir(parents=True, exist_ok=True)
        (self.ms_dir / "manuscript.yaml").write_text("title: The Silver Vale\n", encoding="utf-8")

        ch1_text = (
            "---\ntitle: The Awakening\npov: Kaelen\nstatus: Draft\nchrono_date: '1042-04-12'\ntime: Morning\n---\n"
            "# Chapter 1: The Awakening\n\n"
            "The dawn broke over the jagged spires of the Silver Vale. Kaelen drew his blade.\n"
            "@choice: [Investigate the rune vault] -> vault\n"
            "@choice: [Flee into the mist] -> mist\n"
        )
        (self.ms_dir / "01_Chapter_01.md").write_text(ch1_text, encoding="utf-8")

        ch2_text = (
            "---\ntitle: The Shattered Glyph\npov: Kaelen\nstatus: Revised\nchrono_date: '1042-04-12'\ntime: Noon\n---\n"
            "# Chapter 2: The Shattered Glyph\n\n"
            "Inside the vault, obsidian shards hummed with forbidden energy.\n"
            "@state: energy += 10\n"
        )
        (self.ms_dir / "02_Chapter_02.md").write_text(ch2_text, encoding="utf-8")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_get_engine_catalog(self):
        catalog = get_engine_catalog()
        self.assertTrue(len(catalog) >= 10)
        engine_ids = [e["id"] for e in catalog]
        self.assertIn("zen_studio", engine_ids)
        self.assertIn("corpus_export", engine_ids)
        self.assertIn("vault_search", engine_ids)
        self.assertIn("dramatis_personae", engine_ids)
        self.assertIn("causality", engine_ids)

    def test_scan_manuscript_chapters(self):
        chapters = scan_manuscript_chapters(self.ms_dir)
        self.assertEqual(len(chapters), 2)
        ch1 = chapters[0]
        self.assertEqual(ch1["title"], "The Awakening")
        self.assertEqual(ch1["pov"], "Kaelen")
        self.assertEqual(ch1["choices_count"], 2)
        self.assertTrue(ch1["words"] > 0)

        ch2 = chapters[1]
        self.assertEqual(ch2["title"], "The Shattered Glyph")
        self.assertEqual(ch2["states_count"], 1)

    def test_scan_lore_entities(self):
        entities = scan_lore_entities(self.world_dir)
        self.assertEqual(len(entities), 2)
        names = [e["name"] for e in entities]
        self.assertIn("Kaelen", names)
        self.assertIn("Rune Casting", names)

        kaelen = next(e for e in entities if e["name"] == "Kaelen")
        self.assertEqual(kaelen["category"], "Characters")
        self.assertIn("protagonist", kaelen["tags"])

    def test_analyze_structure_harmony(self):
        chapters = scan_manuscript_chapters(self.ms_dir)
        harmony = analyze_structure_harmony(chapters)
        self.assertEqual(harmony["total_chapters"], 2)
        self.assertTrue(harmony["total_words"] > 0)
        self.assertEqual(len(harmony["pacing_curve"]), 2)
        self.assertEqual(harmony["pacing_curve"][-1]["percentage"], 100.0)

    def test_extract_timeline_summary_and_paradox(self):
        events = extract_timeline_summary(self.world_dir, self.ms_dir)
        self.assertEqual(len(events), 2)
        # In our setup, ch1 and ch2 have same actor Kaelen and same chrono_date '1042-04-12'
        # which triggers the bilocation paradox check
        self.assertTrue(any(e["paradox"] for e in events))

    def test_collect_studio_hub_data(self):
        data = collect_studio_hub_data(self.root)
        self.assertEqual(data["version"], HUB_VERSION)
        self.assertEqual(data["metrics"]["total_chapters"], 2)
        self.assertEqual(data["metrics"]["total_lore_entities"], 2)
        self.assertIn("Characters", data["metrics"]["lore_breakdown"])
        self.assertIn("Magic Systems", data["metrics"]["lore_breakdown"])

    def test_generate_studio_hub_html_and_csp(self):
        data = collect_studio_hub_data(self.root)
        html = generate_studio_hub_html(data, api_mode=False)

        # Check Content Security Policy declaration
        self.assertIn("Content-Security-Policy", html)
        self.assertIn("default-src 'none'", html)
        self.assertIn("connect-src 'self'", html)

        # Check UI components
        self.assertIn("Ars Arcanum", html)
        self.assertIn("Sovereign Studio Hub", html)
        self.assertIn("The Awakening", html)
        self.assertIn("Kaelen", html)
        self.assertIn("Rune Casting", html)

    def test_export_static_studio_hub(self):
        out_file = self.root / "studio_hub.html"
        res = export_static_studio_hub(out_file, self.root)
        self.assertEqual(res, out_file)
        self.assertTrue(out_file.exists())
        content = out_file.read_text(encoding="utf-8")
        self.assertIn("Overview Dashboard", content)

    def test_cli_json_and_static_export(self):
        static_target = self.root / "cli_dashboard.html"
        code = studio_hub_main([str(self.root), "--export-static", str(static_target)])
        self.assertEqual(code, 0)
        self.assertTrue(static_target.exists())

        code_json = studio_hub_main([str(self.root), "--json"])
        self.assertEqual(code_json, 0)


class TestStudioHubServerAPI(unittest.TestCase):
    """Tests the embedded HTTP server and REST endpoints."""

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp_dir.name)

        world_dir = cls.root / "World"
        world_dir.mkdir(parents=True, exist_ok=True)
        (world_dir / "world.yaml").write_text("name: TestCosmos\n", encoding="utf-8")
        (world_dir / "Hero.md").write_text("---\nname: Hero\ntags: [fighter]\n---\n# Hero\n", encoding="utf-8")

        ms_dir = cls.root / "Manuscript"
        ms_dir.mkdir(parents=True, exist_ok=True)
        (ms_dir / "manuscript.yaml").write_text("title: TestStory\n", encoding="utf-8")
        (ms_dir / "01_Ch1.md").write_text("---\ntitle: Ch1\n---\n# Ch1\nStory text.\n", encoding="utf-8")

        cls.data = collect_studio_hub_data(cls.root)
        SovereignStudioHandler.data = cls.data
        SovereignStudioHandler.project_dir = cls.root

        socketserver.TCPServer.allow_reuse_address = True
        cls.httpd = socketserver.TCPServer(("127.0.0.1", 0), SovereignStudioHandler)
        cls.port = cls.httpd.server_address[1]

        cls.server_thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.server_thread.start()
        time.sleep(0.1)

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.temp_dir.cleanup()

    def _get(self, path: str) -> tuple[int, dict[str, str], bytes]:
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        conn.request("GET", path)
        resp = conn.getresponse()
        headers = dict(resp.getheaders())
        data = resp.read()
        conn.close()
        return resp.status, headers, data

    def _post_raw(self, path: str, body_bytes: bytes, headers: dict[str, str] | None = None) -> tuple[int, dict[str, str], bytes]:
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        h = headers or {"Content-Type": "application/json", "Content-Length": str(len(body_bytes))}
        conn.request("POST", path, body_bytes, h)
        resp = conn.getresponse()
        resp_headers = dict(resp.getheaders())
        data = resp.read()
        conn.close()
        return resp.status, resp_headers, data

    def _post_json(self, path: str, payload: dict[str, Any]) -> tuple[int, dict[str, str], dict[str, Any]]:
        body = json.dumps(payload).encode("utf-8")
        status, headers, data = self._post_raw(path, body)
        try:
            json_data = json.loads(data.decode("utf-8"))
        except Exception:
            json_data = {}
        return status, headers, json_data

    def test_head_request(self):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        conn.request("HEAD", "/")
        resp = conn.getresponse()
        headers = dict(resp.getheaders())
        conn.close()
        self.assertEqual(resp.status, 200)
        self.assertIn("text/html", headers.get("Content-Type", ""))

    def test_invalid_host_header(self):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        conn.request("GET", "/", headers={"Host": "malicious-site.com"})
        resp = conn.getresponse()
        resp.read()
        conn.close()
        self.assertEqual(resp.status, 403)

    def test_get_other_endpoints(self):
        # /index.html
        status, _, _ = self._get("/index.html")
        self.assertEqual(status, 200)

        # /api/timeline
        status, _, data = self._get("/api/timeline")
        self.assertEqual(status, 200)

        # /api/metrics
        status, _, data = self._get("/api/metrics")
        self.assertEqual(status, 200)

        # /api/docs and /api/engines
        status, _, _ = self._get("/api/docs")
        self.assertEqual(status, 200)
        status, _, _ = self._get("/api/engines")
        self.assertEqual(status, 200)

        # /api/resonance
        status, _, _ = self._get("/api/resonance")
        self.assertEqual(status, 200)

        # /api/tips
        status, _, _ = self._get("/api/tips?engine=astrophysics")
        self.assertEqual(status, 200)

        # /api/tips/all
        status, _, _ = self._get("/api/tips/all")
        self.assertEqual(status, 200)

        # /api/tips/status
        status, _, _ = self._get("/api/tips/status")
        self.assertEqual(status, 200)

        # /api/all
        status, _, data = self._get("/api/all")
        self.assertEqual(status, 200)
        json_data = json.loads(data.decode("utf-8"))
        self.assertIn("version", json_data)

        # 404
        status, _, _ = self._get("/api/unknown_route")
        self.assertEqual(status, 404)

    def test_post_payload_too_large(self):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        try:
            conn.request("POST", "/api/council", body=b"{}", headers={"Content-Length": "20000000"})
            resp = conn.getresponse()
            resp.read()
            self.assertEqual(resp.status, 413)
        except (ConnectionResetError, ConnectionAbortedError):
            pass
        finally:
            conn.close()

    def test_post_invalid_json(self):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        conn.request("POST", "/api/council", body=b"invalid json!!", headers={"Content-Length": "14"})
        resp = conn.getresponse()
        data = json.loads(resp.read().decode("utf-8"))
        conn.close()
        self.assertEqual(resp.status, 200)
        self.assertEqual(data["word_count"], 0)

    def test_post_tips_toggle_and_set(self):
        status, _, res = self._post_json("/api/tips/toggle", {})
        self.assertEqual(status, 200)
        self.assertEqual(res["status"], "success")

        status, _, res = self._post_json("/api/tips/set", {"enabled": True})
        self.assertEqual(status, 200)
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["enabled"])

    def test_post_branch(self):
        status, _, res = self._post_json("/api/branch", {"text": "Path @choice: [Left path] -> left\n@choice: [Right path] -> right"})
        self.assertEqual(status, 200)
        self.assertEqual(res["total_choices"], 2)

    def test_post_resonance_endpoints(self):
        # Cascade
        status, _, res = self._post_json("/api/resonance/cascade", {"node": "astrophysics", "param": "axial_tilt", "val": 30.0})
        self.assertEqual(status, 200)

        # Spark
        status, _, res = self._post_json("/api/resonance/spark", {"domains": ["astrophysics", "climate"], "count": 2})
        self.assertEqual(status, 200)
        self.assertIsInstance(res, list)

        # Bridge
        status, _, res = self._post_json("/api/resonance/bridge", {"domain_a": "astrophysics", "domain_b": "voice"})
        self.assertEqual(status, 200)

        # /api/chapter/save happy path
        save_payload = {
            "file": "Manuscript/03_Chapter_03.md",
            "content": "# Chapter 3\n\nThe cold wind howled across the high peaks.",
        }
        status, _, res = self._post_json("/api/chapter/save", save_payload)
        self.assertEqual(status, 200)
        self.assertEqual(res["status"], "success")
        self.assertIn("03_Chapter_03.md", res["path"])
        self.assertTrue((self.root / "Manuscript" / "03_Chapter_03.md").is_file())

        # /api/chapter/save path traversal rejection
        status, _, _ = self._post_json("/api/chapter/save", {"file": "../evil.md", "content": "attack"})
        self.assertEqual(status, 400)

        # /api/chapter/save non-markdown rejection
        status, _, _ = self._post_json("/api/chapter/save", {"file": "script.py", "content": "print('bad')"})
        self.assertEqual(status, 400)

        # /api/chapter/save missing payload
        status, _, _ = self._post_json("/api/chapter/save", {})
        self.assertEqual(status, 400)

        # 404 POST
        status, _, _ = self._post_json("/api/unknown_post", {})
        self.assertEqual(status, 404)


class TestStudioHubEdgeCases(unittest.TestCase):
    """Tests edge cases in scanning and server startup."""

    def test_scan_manuscript_edge_cases(self):
        self.assertEqual(scan_manuscript_chapters(None), [])
        self.assertEqual(scan_manuscript_chapters(Path("nonexistent_path_12345")), [])

        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            (p / ".hidden.md").write_text("hidden", encoding="utf-8")
            (p / "_draft.md").write_text("draft", encoding="utf-8")
            backup_dir = p / "Backups"
            backup_dir.mkdir()
            (backup_dir / "backup.md").write_text("backup", encoding="utf-8")
            (p / "empty.md").write_text("", encoding="utf-8")
            no_frontmatter = p / "no_fm.md"
            no_frontmatter.write_text("# Chapter Without Frontmatter\nSome content here.", encoding="utf-8")

            res = scan_manuscript_chapters(p)
            self.assertEqual(len(res), 1)
            self.assertEqual(res[0]["title"], "Chapter Without Frontmatter")

    def test_start_studio_hub_server(self):
        from unittest.mock import MagicMock, patch
        from scripts.lib.studio_hub import start_studio_hub_server

        with patch("http.server.ThreadingHTTPServer") as mock_server:
            instance = MagicMock()
            instance.server_address = ("127.0.0.1", 8080)
            instance.serve_forever.side_effect = KeyboardInterrupt
            mock_server.return_value.__enter__.return_value = instance

            with tempfile.TemporaryDirectory() as td:
                start_studio_hub_server(project_dir=Path(td), open_browser=True)
            self.assertTrue(instance.serve_forever.called)


if __name__ == "__main__":
    unittest.main()

