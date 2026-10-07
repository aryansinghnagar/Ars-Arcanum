#!/usr/bin/env python3
"""
Ars Arcanum Sovereign Studio Desktop Hub & Telemetry Dashboard
(scripts/lib/studio_hub.py)
================================================================================
Master unified desktop & web-based interactive orchestrator dashboard unifying
all 50+ craft engines, Zen drafting studio, editorial council, local semantic
RAG, branching narrative DAG visualizer, fine-tuning synthesizer, omnibus
compiler, and synchronized audio overlays.

100% Offline Sovereign Operating System — Zero Pip Dependencies — Zero Remote CDNs.
"""

from __future__ import annotations

import argparse
import http.server
import json
import logging
import re
import sys
import threading
import time
import urllib.parse
import webbrowser
from pathlib import Path
from typing import Any

try:
    from lib._bootstrap import atomic_write, count_prose_words
    from lib.resonance import ResonanceMesh
    from lib.scope import (
        EngineScope,
        parse_number_ranges,
        parse_unified_scope_string,
    )
    from lib.studio_hub_data import (
        FRONTMATTER_REGEX,
        analyze_structure_harmony,
        collect_studio_hub_data,
        extract_timeline_summary,
        get_engine_catalog,
        scan_lore_entities,
        scan_manuscript_chapters,
    )
    from lib.tips import are_tips_enabled, get_tip_database, toggle_tips
except ImportError:
    from _bootstrap import atomic_write, count_prose_words
    from resonance import ResonanceMesh  # type: ignore[no-redef]
    from scope import (  # type: ignore[no-redef]
        EngineScope,
        parse_number_ranges,
        parse_unified_scope_string,
    )
    from studio_hub_data import (  # type: ignore[no-redef]
        FRONTMATTER_REGEX,
        analyze_structure_harmony,
        collect_studio_hub_data,
        extract_timeline_summary,
        get_engine_catalog,
        scan_lore_entities,
        scan_manuscript_chapters,
    )
    from tips import are_tips_enabled, get_tip_database, toggle_tips

logger = logging.getLogger("arcanum.studio_hub")

HUB_VERSION = "0.1.0"

__all__ = [
    "FRONTMATTER_REGEX",
    "HUB_VERSION",
    "SovereignStudioHandler",
    "analyze_structure_harmony",
    "collect_studio_hub_data",
    "export_static_studio_hub",
    "extract_timeline_summary",
    "generate_studio_hub_html",
    "get_engine_catalog",
    "main",
    "scan_lore_entities",
    "scan_manuscript_chapters",
    "start_studio_hub_server",
]




# -----------------------------------------------------------------------------
# Standalone HTML/CSS/JS Studio Hub Dashboard Generator
# -----------------------------------------------------------------------------


try:
    from lib.studio_hub_template import generate_studio_hub_html
except ImportError:
    from studio_hub_template import generate_studio_hub_html



# -----------------------------------------------------------------------------
# Embedded Sovereign HTTP Server & REST API Dispatcher
# -----------------------------------------------------------------------------


_engine_exec_lock = threading.Lock()


class SovereignStudioHandler(http.server.BaseHTTPRequestHandler):
    """Zero-dependency HTTP request handler for local sovereign studio telemetry."""

    data: dict[str, Any] = {}
    project_dir: Path = Path.cwd()
    active_scope: EngineScope = EngineScope()

    def _validate_host(self) -> bool:
        host_header = self.headers.get("Host", "")
        host_name = host_header.split(":")[0].strip().lower()
        if host_name in ("localhost", "127.0.0.1", "::1", "[::1]", ""):
            return True
        self.send_error(403, "Forbidden: Invalid Host header")
        return False

    def _validate_origin(self) -> bool:
        origin = self.headers.get("Origin", "").strip()
        if not origin:
            return True
        if origin.lower() == "null":
            self.send_error(403, "Forbidden: Sandboxed null Origin rejected")
            return False
        try:
            parsed = urllib.parse.urlparse(origin)
            if parsed.scheme in ("http", "https") and parsed.hostname in ("localhost", "127.0.0.1", "::1", "[::1]"):
                return True
        except Exception:
            pass
        self.send_error(403, "Forbidden: Cross-origin request rejected")
        return False

    def do_HEAD(self) -> None:
        if not self._validate_host():
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()

    def do_GET(self) -> None:
        if not self._validate_host():
            return
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path in ("/", "/index.html"):
            html = generate_studio_hub_html(self.data, api_mode=True)
            encoded = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(encoded)
        elif path == "/api/status":
            self._send_json(self.data.get("system", {}))
        elif path == "/api/scope":
            self._send_json({
                "status": "success",
                "scope": {
                    "universe": self.active_scope.universe,
                    "world": self.active_scope.world,
                    "lore_categories": self.active_scope.lore_categories,
                    "series": self.active_scope.series,
                    "manuscript": self.active_scope.manuscript,
                    "book": self.active_scope.book,
                    "chapters": self.active_scope.chapters,
                    "scenes": self.active_scope.scenes,
                    "raw_filter": self.active_scope.raw_scope,
                    "raw_scope": self.active_scope.raw_scope,
                }
            })
        elif path == "/api/lore":
            self._send_json(self.data.get("lore_entities", []))
        elif path == "/api/chapters":
            self._send_json(self.data.get("chapters", []))
        elif path == "/api/timeline":
            self._send_json(self.data.get("timeline_events", []))
        elif path == "/api/metrics":
            self._send_json(self.data.get("metrics", {}))
        elif path in ("/api/docs", "/api/engines"):
            self._send_json(self.data.get("engine_catalog", []))
        elif path == "/api/resonance":
            self._send_json(self.data.get("resonance", {}))
        elif path == "/api/tips":
            query_params = urllib.parse.parse_qs(parsed.query)
            engine = query_params.get("engine", [None])[0]
            feature = query_params.get("feature", [None])[0]
            context = query_params.get("context", [None])[0]
            q = query_params.get("q", [None])[0] or query_params.get("query", [None])[0]
            tip = get_tip_database().get_contextual_tip(engine=engine, feature=feature, context=context, query=q)
            self._send_json(tip.to_dict() if tip else {})
        elif path == "/api/tips/all":
            self._send_json([t.to_dict() for t in get_tip_database().get_all()])
        elif path == "/api/tips/status":
            self._send_json({"enabled": are_tips_enabled(), "total_count": len(get_tip_database())})
        elif path == "/api/all":
            self._send_json(self.data)
        else:
            self.send_error(404, "Endpoint not found")

    def do_POST(self) -> None:
        if not self._validate_host() or not self._validate_origin():
            return
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        try:
            content_length = int(self.headers.get("Content-Length", 0))
        except (ValueError, TypeError):
            content_length = 0

        if content_length > 10 * 1024 * 1024:  # 10MB limit
            self.send_error(413, "Payload too large")
            return

        body_bytes = self.rfile.read(content_length)
        try:
            payload = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
        except Exception:
            payload = {}

        if path == "/api/query":
            self._handle_query(payload)
        elif path == "/api/tips/toggle":
            new_val = toggle_tips()
            self._send_json({"status": "success", "enabled": new_val})
        elif path == "/api/tips/set":
            val = bool(payload.get("enabled", True))
            from lib.tips import set_tips_enabled
            set_tips_enabled(val)
            self._send_json({"status": "success", "enabled": val})
        elif path == "/api/council":
            self._handle_council(payload)
        elif path == "/api/branch":
            text = payload.get("text", "")
            choices = re.findall(r"@choice:\s*\[([^\]]+)\]\s*->\s*(\S+)", text)
            self._send_json({"total_choices": len(choices), "choices": choices})
        elif path.startswith("/api/resonance/"):
            self._handle_resonance(path, payload)
        elif path == "/api/scope":
            self._handle_scope(payload)
        elif path == "/api/engine/run":
            self._handle_engine_run(payload)
        elif path == "/api/chapter/save":
            self._handle_chapter_save(payload)
        else:
            self.send_error(404, "Endpoint not found")

    def _handle_query(self, payload: dict[str, Any]) -> None:
        query = str(payload.get("query", "")).strip().lower()
        q_terms = [t for t in re.split(r"\W+", query) if len(t) >= 2]
        scored_matches = []
        for e in self.data.get("lore_entities", []):
            e_name = str(e.get("name", "")).lower()
            e_summary = str(e.get("summary", "")).lower()
            e_tags = [str(t).lower() for t in e.get("tags", [])]
            score = 0.0
            if query and query in e_name:
                score += 20.0
            if query and query in e_summary:
                score += 5.0
            for term in q_terms:
                if term in e_name:
                    score += 8.0
                if any(term in tag for tag in e_tags):
                    score += 4.0
                if term in e_summary:
                    score += 2.0
            if score > 0 or (not q_terms and query in e_name):
                entry = dict(e)
                entry["relevance_score"] = round(score, 2)
                scored_matches.append(entry)

        scored_matches.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        self._send_json({
            "query": query,
            "search_mode": "relevance_scored",
            "total_matches": len(scored_matches),
            "results": scored_matches,
        })

    def _handle_council(self, payload: dict[str, Any]) -> None:
        text = str(payload.get("text", "")).strip()
        words = text.split() if text else []
        word_count = len(words)
        sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
        sentence_lens = [len(s.split()) for s in sentences] if sentences else []

        # 1. Line Editor Critique
        if not text:
            line_critique = "Empty passage. Enter text to run stylistic cadence analysis."
        else:
            avg_len = sum(sentence_lens) / len(sentence_lens) if sentence_lens else 0
            run_ons = sum(1 for slen in sentence_lens if slen > 35)
            passive_matches = len(re.findall(r"\b(?:was|were|is|are|been|being)\s+[a-z]+ed\b", text, re.IGNORECASE))
            critique_notes = [f"Average sentence length: {avg_len:.1f} words across {len(sentences)} sentences."]
            if run_ons > 0:
                critique_notes.append(f"Flagged {run_ons} potentially unwieldy sentence(s) (>35 words).")
            if passive_matches > 0:
                critique_notes.append(f"Detected {passive_matches} passive voice construction(s).")
            if len(sentence_lens) > 3:
                variance = sum((slen - avg_len) ** 2 for slen in sentence_lens) / len(sentence_lens)
                if variance < 4.0:
                    critique_notes.append("Cadence alert: Sentence lengths are highly uniform; vary rhythm for dramatic tension.")
            line_critique = " ".join(critique_notes)

        # 2. Lore Arbiter Critique
        lore_entities = self.data.get("lore_entities", [])
        found_entities = []
        text_lower = text.lower()
        for ent in lore_entities:
            ename = str(ent.get("name", ""))
            if ename and ename.lower() in text_lower:
                found_entities.append(ename)
        lore_critique = f"Lore integrity verified: Identified {len(found_entities)} registered canon entities: {', '.join(found_entities[:5])}." if found_entities else "No registered World Bible entities detected in this excerpt."

        # 3. Story Architect Critique
        dialogue_quotes = len(re.findall(r'["“][^"”]+["”]', text))
        dialogue_words = sum(len(q.split()) for q in re.findall(r'["“]([^"”]+)["”]', text))
        dialogue_ratio = (dialogue_words / max(1, word_count)) * 100
        if word_count == 0:
            arch_critique = "No narrative draft supplied."
        elif dialogue_ratio > 60:
            arch_critique = f"Dialogue-heavy scene ({dialogue_ratio:.0f}% dialogue across {dialogue_quotes} turns). Ensure sensory anchoring and physical blocking."
        elif dialogue_ratio < 10 and word_count > 100:
            arch_critique = f"Exposition-dense passage ({dialogue_ratio:.0f}% dialogue). Consider interspersing character interaction or internal monologue."
        else:
            arch_critique = f"Balanced narrative structure ({dialogue_ratio:.0f}% dialogue, {word_count} total words)."

        # 4. Continuity Steward Critique
        date_matches = re.findall(r"\b(?:\d{4}-\d{2}-\d{2}|Act\s+[IVXLCDM\d]+|Chapter\s+\d+|Year\s+\d+)\b", text, re.IGNORECASE)
        tag_matches = re.findall(r"@(chrono|state|choice|price|prophecy):", text)
        steward_notes = []
        if date_matches:
            steward_notes.append(f"Temporal anchors detected: {', '.join(set(date_matches))}.")
        if tag_matches:
            steward_notes.append(f"Inline semantic metadata tags: {', '.join(set(tag_matches))}.")
        if not steward_notes:
            steward_notes.append("No explicit chronology tags or temporal markers in passage.")
        continuity_critique = " ".join(steward_notes)

        self._send_json({
            "status": "success",
            "word_count": word_count,
            "sentence_count": len(sentences),
            "critique": {
                "line_editor": line_critique,
                "lore_arbiter": lore_critique,
                "story_architect": arch_critique,
                "continuity_steward": continuity_critique,
            },
        })

    def _handle_resonance(self, path: str, payload: dict[str, Any]) -> None:
        mesh = ResonanceMesh(self.project_dir)
        if path == "/api/resonance/cascade":
            node = payload.get("node", "astrophysics")
            param = payload.get("param", "axial_tilt")
            val = payload.get("val", 38.5)
            report = mesh.simulate_cascade(origin_node_id=node, param_key=param, new_value=val)
            self._send_json(report.to_dict())
        elif path == "/api/resonance/spark":
            domains = payload.get("domains", [])
            count = payload.get("count", 3)
            sparks = mesh.generate_sparks(domains=domains, count=count)
            self._send_json([s.to_dict() for s in sparks])
        elif path == "/api/resonance/bridge":
            dom_a = payload.get("domain_a", "astrophysics")
            dom_b = payload.get("domain_b", "voice")
            steps = mesh.find_bridge(dom_a, dom_b)
            self._send_json(steps)
        else:
            self.send_error(404, "Endpoint not found")

    def _handle_scope(self, payload: dict[str, Any]) -> None:
        ch = parse_number_ranges(payload.get("chapters")) if payload.get("chapters") is not None else SovereignStudioHandler.active_scope.chapters
        sc = parse_number_ranges(payload.get("scenes")) if payload.get("scenes") is not None else SovereignStudioHandler.active_scope.scenes
        raw_f = payload.get("filter") or payload.get("raw_filter") or payload.get("raw_scope")
        if raw_f:
            parsed_sc = parse_unified_scope_string(str(raw_f))
            SovereignStudioHandler.active_scope = EngineScope.from_dict(parsed_sc)
        else:
            bk_val = payload.get("book") or payload.get("books")
            bks = [str(bk_val)] if bk_val and isinstance(bk_val, str) else (bk_val if isinstance(bk_val, list) else SovereignStudioHandler.active_scope.books)
            SovereignStudioHandler.active_scope = EngineScope(
                universe=payload.get("universe") or SovereignStudioHandler.active_scope.universe,
                world=payload.get("world") or SovereignStudioHandler.active_scope.world,
                lore_categories=payload.get("lore_categories") or SovereignStudioHandler.active_scope.lore_categories,
                series=payload.get("series") or SovereignStudioHandler.active_scope.series,
                manuscript=payload.get("manuscript") or SovereignStudioHandler.active_scope.manuscript,
                books=bks,
                chapters=ch,
                scenes=sc,
                raw_scope=str(raw_f or SovereignStudioHandler.active_scope.raw_scope),
            )
        self._send_json({
            "status": "success",
            "scope": SovereignStudioHandler.active_scope.to_dict()
        })

    def _handle_engine_run(self, payload: dict[str, Any]) -> None:
        eng_id = payload.get("engine", "")
        scope_dict = payload.get("scope", {})
        if scope_dict:
            bk_val = scope_dict.get("book") or scope_dict.get("books")
            bks = [str(bk_val)] if bk_val and isinstance(bk_val, str) else (bk_val if isinstance(bk_val, list) else SovereignStudioHandler.active_scope.books)
            engine_scope = EngineScope(
                universe=scope_dict.get("universe") or SovereignStudioHandler.active_scope.universe,
                world=scope_dict.get("world") or SovereignStudioHandler.active_scope.world,
                lore_categories=scope_dict.get("lore_categories") or SovereignStudioHandler.active_scope.lore_categories,
                series=scope_dict.get("series") or SovereignStudioHandler.active_scope.series,
                manuscript=scope_dict.get("manuscript") or SovereignStudioHandler.active_scope.manuscript,
                books=bks,
                chapters=parse_number_ranges(scope_dict.get("chapters")) if scope_dict.get("chapters") is not None else SovereignStudioHandler.active_scope.chapters,
                scenes=parse_number_ranges(scope_dict.get("scenes")) if scope_dict.get("scenes") is not None else SovereignStudioHandler.active_scope.scenes,
                raw_scope=str(scope_dict.get("raw_scope", SovereignStudioHandler.active_scope.raw_scope)),
            )
        else:
            engine_scope = SovereignStudioHandler.active_scope

        result = self._execute_scoped_engine(eng_id, engine_scope, payload.get("options", {}))
        self._send_json(result)

    def _handle_chapter_save(self, payload: dict[str, Any]) -> None:
        file_rel = payload.get("file") or payload.get("path") or payload.get("filename")
        content = payload.get("content")
        if not file_rel or content is None:
            self.send_error(400, "Bad Request: Missing 'file' or 'content' in payload")
            return

        # Path traversal sanitization
        file_str = str(file_rel).replace("\\", "/")
        if ".." in file_str or file_str.startswith(("/", "\\")):
            self.send_error(400, "Bad Request: Path traversal rejected")
            return

        target_path = (self.project_dir / file_str).resolve()
        # Ensure target_path is within project_dir
        try:
            target_path.relative_to(self.project_dir.resolve())
        except ValueError:
            self.send_error(403, "Forbidden: Target path outside project directory")
            return

        if not target_path.name.endswith(".md"):
            self.send_error(400, "Bad Request: Only markdown (.md) chapter files can be saved")
            return

        try:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            atomic_write(target_path, str(content))

            # Evict from DataAccessLayer LRU cache if active
            try:
                from lib.data_access import get_data_access
                dal = get_data_access()
                if dal:
                    dal.cache.evict(target_path)
            except Exception:
                pass

            words = count_prose_words(str(content))
            self._send_json({
                "status": "success",
                "path": str(target_path.relative_to(self.project_dir)).replace("\\", "/"),
                "words": words,
                "saved_at": time.time(),
            })
        except Exception as e:
            logger.error("Failed to save chapter %s: %s", target_path, e)
            self.send_error(500, f"Internal Server Error: {e}")

    def _execute_scoped_engine(self, engine_name: str, scope: EngineScope, options: dict[str, Any]) -> dict[str, Any]:
        """Executes an authorized craft engine synchronously with captured output and applied scope under lock."""
        import contextlib
        import io

        from lib.cli import dispatch_subcommand

        norm_name = engine_name.lower().strip()

        # Doctrine/advisory engines handled gracefully without module import failure
        advisory_engines = {
            "pacing": "PACING",
            "pace": "PACING",
            "scene_mechanics": "SCENE_MECHANICS",
            "scenes": "SCENE_MECHANICS",
            "tension": "SCENE_MECHANICS",
            "stylistics": "STYLISTICS",
            "style": "STYLISTICS",
            "voice": "VOICE",
            "senses": "SENSES",
            "sensory": "SENSES",
            "council": "COUNCIL",
        }
        if norm_name in advisory_engines:
            doc_target = advisory_engines[norm_name]
            msg = (
                f"Ars Arcanum Craft Studio — Reference Doctrine ({doc_target})\n"
                f"Note: Standalone heuristic '{norm_name}' has transitioned to deterministic "
                f"metadata and authoritative craft documentation.\n"
                f"To view the craft guide, run: arcanum doc {norm_name}"
            )
            return {
                "status": "success",
                "engine": engine_name,
                "exit_code": 0,
                "stdout": msg,
                "stderr": "",
                "combined_output": msg,
                "scope_applied": {
                    "manuscript": scope.manuscript,
                    "world": scope.world,
                    "chapters": scope.chapters,
                    "scenes": scope.scenes,
                    "book": scope.book,
                    "series": scope.series,
                },
            }

        # Strict Allowlist of craft engines executable via Studio Hub API
        allowed_engines = {
            "astrophysics": "lib.astrophysics",
            "astro": "lib.astrophysics",
            "magic": "lib.magic_system",
            "magic_system": "lib.magic_system",
            "genealogy": "lib.genealogy",
            "lineage": "lib.genealogy",
            "conlang": "lib.conlang",
            "calendar": "lib.calendar",
            "factions": "lib.factions",
            "faction": "lib.factions",
            "economy": "lib.economy",
            "ecology": "lib.ecology",
            "climate": "lib.climate",
            "journey": "lib.journey",
            "structure": "lib.structure",
            "plot": "lib.plot_matrix",
            "plot_matrix": "lib.plot_matrix",
            "canvas": "lib.story_canvas",
            "story_canvas": "lib.story_canvas",
            "timeline": "lib.timeline_sync",
            "timeline_sync": "lib.timeline_sync",
            "omnibus": "lib.omnibus",
            "corpus": "lib.corpus_export",
            "corpus_export": "lib.corpus_export",
            "search": "lib.vault_search",
            "vault_search": "lib.vault_search",
            "rag": "lib.vault_search",
            "doctor": "lib.diagnostics",
            "world_doctor": "lib.world_doctor",
            "sprint": "lib.writing_sprint",
            "writing_sprint": "lib.writing_sprint",
            "revision_heatmap": "lib.revision_heatmap",
            "typography": "lib.typography_cleaner",
            "typography_cleaner": "lib.typography_cleaner",
            "preflight": "lib.preflight",
            "zen_studio": "lib.zen_studio",
            "studio": "lib.zen_studio",
            "scope": "lib.scope",
            "causality": "lib.causality",
            "prophecy": "lib.prophecy",
            "resonance": "lib.resonance",
            "words": "lib.cache",
        }

        if norm_name not in allowed_engines:
            return {
                "status": "error",
                "engine": engine_name,
                "exit_code": 1,
                "stdout": "",
                "stderr": f"Error: Engine '{engine_name}' is not in the authorized engine allowlist.",
                "combined_output": f"Error: Engine '{engine_name}' is not in the authorized engine allowlist.",
                "scope_applied": {},
            }

        argv: list[str] = []
        if scope.manuscript:
            argv.extend(["--manuscript", str(scope.manuscript)])
        if scope.world:
            argv.extend(["--world", str(scope.world)])
        if scope.chapters:
            argv.extend(["--chapters", ",".join(str(c) for c in scope.chapters)])
        if scope.scenes:
            argv.extend(["--scenes", ",".join(str(s) for s in scope.scenes)])
        if scope.book:
            argv.extend(["--book", str(scope.book)])
        if scope.series:
            argv.extend(["--series", str(scope.series)])

        mod_name = allowed_engines[norm_name]
        buf_out = io.StringIO()
        buf_err = io.StringIO()
        exit_code = 0

        with _engine_exec_lock:
            try:
                with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
                    exit_code = dispatch_subcommand(mod_name, argv)
            except Exception as ex:
                buf_err.write(f"\nExecution error: {ex}")
                exit_code = 1

        out_text = buf_out.getvalue()
        err_text = buf_err.getvalue()

        return {
            "status": "success" if exit_code == 0 else "error",
            "engine": engine_name,
            "exit_code": exit_code,
            "stdout": out_text,
            "stderr": err_text,
            "combined_output": (out_text + "\n" + err_text).strip(),
            "scope_applied": {
                "manuscript": scope.manuscript,
                "world": scope.world,
                "chapters": scope.chapters,
                "scenes": scope.scenes,
                "book": scope.book,
                "series": scope.series,
            }
        }

    def _send_json(self, data: Any) -> None:
        payload = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format: str, *args: Any) -> None:
        # Suppress noisy standard request logging
        pass


def export_static_studio_hub(target_file: Path, project_dir: Path | None = None) -> Path:
    """Compiles and writes a standalone static HTML Studio Hub file."""
    data = collect_studio_hub_data(project_dir)
    html_content = generate_studio_hub_html(data, api_mode=False)
    atomic_write(target_file, html_content)
    return target_file


def start_studio_hub_server(
    project_dir: Path | None = None,
    host: str = "127.0.0.1",
    port: int = 8080,
    open_browser: bool = True,
) -> None:
    """Starts the embedded zero-dependency local sovereign HTTP server."""
    root = project_dir or Path.cwd()
    data = collect_studio_hub_data(root)

    SovereignStudioHandler.data = data
    SovereignStudioHandler.project_dir = root

    http.server.ThreadingHTTPServer.allow_reuse_address = True
    with http.server.ThreadingHTTPServer((host, port), SovereignStudioHandler) as httpd:
        actual_port = httpd.server_address[1]
        url = f"http://{host}:{actual_port}/"
        print(f"⚡ Ars Arcanum Sovereign Studio Hub v{HUB_VERSION} active at: {url}")
        print("🛡️ 100% Offline Privacy — Zero Telemetry. Press Ctrl+C to stop.")

        if open_browser:
            def _launch_browser() -> None:
                time.sleep(0.3)
                webbrowser.open(url)

            threading.Thread(target=_launch_browser, daemon=True).start()

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down Sovereign Studio Hub.")


def main(argv: list[str] | None = None) -> int:
    """CLI dispatcher for the Sovereign Studio Desktop Hub."""
    parser = argparse.ArgumentParser(
        description="Ars Arcanum Sovereign Studio Desktop Hub & Telemetry Dashboard"
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=".",
        help="Path to Manuscript or World directory (default: current directory)",
    )
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=8080,
        help="Local server port (default: 8080)",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Server host address (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not automatically launch web browser",
    )
    parser.add_argument(
        "--export-static",
        metavar="FILE",
        help="Export standalone static offline HTML dashboard and exit",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw telemetry JSON to stdout and exit",
    )

    args = parser.parse_args(argv)
    target_path = Path(args.target).resolve()

    if args.json:
        data = collect_studio_hub_data(target_path)
        print(json.dumps(data, indent=2))
        return 0

    if args.export_static:
        out_file = Path(args.export_static).resolve()
        export_static_studio_hub(out_file, target_path)
        print(f"✓ Standalone Studio Hub static dashboard exported to: {out_file}")
        return 0

    start_studio_hub_server(
        project_dir=target_path,
        host=args.host,
        port=args.port,
        open_browser=not args.no_browser,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())


