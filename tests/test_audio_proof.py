#!/usr/bin/env python3
"""
Unit and Integration Tests for Ars Arcanum Sovereign Audio Proofing Engine
(tests/test_audio_proof.py)
================================================================================
"""

import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.lib.audio_proof import (
    analyze_audio_proofing,
    check_phonetic_flags,
    chunk_for_tts,
    estimate_scene_duration,
    extract_dialogue_and_narration,
    format_seconds,
    generate_ssml,
    generate_tts_commands,
    main as audio_proof_main,
    render_audio_proof_html,
    split_scenes,
)


class TestAudioProofEngine(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

        self.sample_manuscript = self.root / "chapter_01.md"
        self.sample_manuscript.write_text(
            """# Chapter 1: The Solar Gate

The obsidian gates stood tall against the raging storm. Thunder cracked across the iron peaks.

"We cannot hold this passage," Elena shouted, gripping her runic spear. "Fall back to the citadel!"

Marcus shook his head. "If the gate falls, the entire valley burns."

---

# Chapter 2: The Crimson Breach

Silent shadows slipped through the subterranean fissures. Seven sinister serpents slithered south.

"Are you ready?" asked Marcus in a low whisper.

"I was born ready," Elena replied with a grim smile.
""",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_split_scenes(self) -> None:
        """Verifies scene splitting across headers and markdown horizontal rules."""
        text = self.sample_manuscript.read_text(encoding="utf-8")
        scenes = split_scenes(text)
        self.assertGreaterEqual(len(scenes), 2)
        self.assertIn("Chapter 1: The Solar Gate", scenes[0][0])
        self.assertIn("obsidian gates", scenes[0][1])

    def test_extract_dialogue_and_narration(self) -> None:
        """Verifies accurate extraction of spoken dialogue vs narration words."""
        text = 'Elena shouted, "Fall back to the citadel!" She raised her glowing shield.'
        d_words, n_words = extract_dialogue_and_narration(text)
        self.assertEqual(d_words, 5)  # "Fall back to the citadel!"
        self.assertGreater(n_words, 5)

    def test_check_phonetic_flags(self) -> None:
        """Detects sibilance / alliteration hotspots in prose."""
        text = "Seven sinister serpents slithered south seeking silent sanctuaries."
        flags = check_phonetic_flags(text)
        self.assertTrue(any("Alliteration" in f or "Sibilance" in f for f in flags))

    def test_estimate_scene_duration(self) -> None:
        """Verifies duration calculation including pause additions."""
        text = "Dawn broke over the high towers. The cold wind blew through the pines."
        dur_sec, pause_sec, _max_sent, breath = estimate_scene_duration(text, wpm=150)
        self.assertGreater(dur_sec, 0.0)
        self.assertGreater(pause_sec, 0.0)
        self.assertGreater(breath, 50.0)

    def test_format_seconds(self) -> None:
        """Verifies MM:SS and HH:MM:SS string formatting."""
        self.assertEqual(format_seconds(65), "01:05")
        self.assertEqual(format_seconds(3665), "01:01:05")

    def test_generate_ssml(self) -> None:
        """Verifies valid W3C SSML 1.0 markup generation."""
        text = 'He paused. "Listen closely." The wind died.'
        ssml = generate_ssml(text, dialogue_pitch="+10%", dialogue_rate="fast")
        self.assertIn("<speak", ssml)
        self.assertIn('<prosody pitch="+10%" rate="fast">Listen closely.</prosody>', ssml)
        self.assertIn("</speak>", ssml)

    def test_chunk_for_tts(self) -> None:
        """Verifies text chunking without breaking paragraphs."""
        text = ("Paragraph one.\n\n" * 50) + ("Paragraph two.\n\n" * 50)
        chunks = chunk_for_tts(text, max_chars=400)
        self.assertGreater(len(chunks), 1)
        for c in chunks:
            self.assertLessEqual(c["char_count"], 450)

    def test_generate_tts_commands(self) -> None:
        """Verifies CLI batch command generation for piper and espeak-ng."""
        chunks = [{"chunk_id": 1, "text": "Hello world"}]
        p_cmds = generate_tts_commands(chunks, engine="piper")
        e_cmds = generate_tts_commands(chunks, engine="espeak")

        self.assertIn("piper", p_cmds[0])
        self.assertIn("chunk_001.wav", p_cmds[0])
        self.assertIn("espeak-ng", e_cmds[0])

    def test_analyze_audio_proofing(self) -> None:
        """Performs full end-to-end manuscript audio analysis."""
        report = analyze_audio_proofing(self.sample_manuscript, wpm=150)
        self.assertGreater(report.total_words, 20)
        self.assertGreater(report.total_duration_sec, 0.0)
        self.assertGreater(report.overall_dialogue_ratio, 0.0)
        self.assertGreaterEqual(len(report.scenes), 2)

    def test_render_audio_proof_html(self) -> None:
        """Generates offline HTML report with strict Content Security Policy."""
        report = analyze_audio_proofing(self.sample_manuscript, wpm=150)
        out_html = self.root / "audio_proof.html"
        render_audio_proof_html(report, out_html)

        self.assertTrue(out_html.is_file())
        content = out_html.read_text(encoding="utf-8")
        self.assertIn("Content-Security-Policy", content)
        self.assertIn("default-src 'none'", content)
        self.assertIn("Audio Proofing", content)

    def test_cli_execution(self) -> None:
        """Verifies CLI execution options (--json, --ssml)."""
        # JSON mode
        with patch("sys.argv", ["audio_proof.py", str(self.sample_manuscript), "--json"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                audio_proof_main()
                data = json.loads(mock_stdout.getvalue())
                self.assertIn("total_words", data)
                self.assertIn("scenes", data)

        # SSML mode
        with patch("sys.argv", ["audio_proof.py", str(self.sample_manuscript), "--ssml"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                audio_proof_main()
                self.assertIn("<speak", mock_stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
