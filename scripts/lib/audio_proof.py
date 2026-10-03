#!/usr/bin/env python3
"""
Ars Arcanum Sovereign Audio Proofing Engine
(scripts/lib/audio_proof.py)
================================================================================
Zero-dependency, offline audio proofing, SSML generation, and speech duration
estimation engine for speculative fiction authors.

Capabilities:
1. Speech Duration & Punctuation Pause Modeling:
   - Configurable Words-Per-Minute (default: 150 WPM).
   - Micro-pause adjustments for commas (150ms), em-dashes (300ms), ellipses (500ms),
     sentence terminators (400ms), paragraph breaks (500ms), and scene breaks (1500ms).
   - Dialogue vs. Narration density and estimated speaking times.
2. Scene-by-Scene SSML Synthesizer:
   - W3C SSML 1.0 standard compliant markup generation.
   - Distinct prosody wrapping for spoken dialogue vs narrative exposition.
   - Scene separator pause insertion.
3. Offline TTS Batch Orchestration & Chunking:
   - Smart chunking respecting paragraph/sentence boundaries (under target char limits).
   - CLI command generators for local neural TTS (Piper TTS) and formant TTS (eSpeak NG).
4. Standalone Offline Interactive HTML Proofing Dossier:
   - Strict offline Content Security Policy (default-src 'none').
   - Scene pacing timeline, phonetic collision warnings (alliteration / homophone hotspots),
     and sentence breathability metrics.

Zero external dependencies; 100% offline privacy.
"""

import argparse
import html
import json
import logging
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

try:
    from lib._bootstrap import atomic_write
except ImportError:
    from _bootstrap import atomic_write

logger = logging.getLogger("arcanum.audio_proof")


@dataclass
class AudioSceneTelemetry:
    scene_id: int
    title: str
    word_count: int
    char_count: int
    sentence_count: int
    dialogue_words: int
    narration_words: int
    dialogue_ratio: float
    estimated_duration_sec: float
    formatted_duration: str
    pause_time_sec: float
    longest_sentence_words: int
    breathability_score: float  # 0.0 - 100.0 (higher = easier to narrate)
    ssml_snippet: str
    text_content: str
    phonetic_flags: list[str] = field(default_factory=list)


@dataclass
class AudioProofReport:
    target_path: str
    total_words: int
    total_chars: int
    total_sentences: int
    total_dialogue_words: int
    total_narration_words: int
    overall_dialogue_ratio: float
    target_wpm: int
    total_duration_sec: float
    total_duration_formatted: str
    total_pause_sec: float
    average_sentence_length: float
    scenes: list[AudioSceneTelemetry] = field(default_factory=list)
    tts_chunks: list[dict[str, Any]] = field(default_factory=list)
    tts_commands: list[str] = field(default_factory=list)


def split_scenes(content: str) -> list[tuple[str, str]]:
    """
    Split markdown manuscript text into scenes based on headers or scene break markers.
    Returns list of (scene_title, scene_text).
    """
    lines = content.splitlines()
    scenes: list[tuple[str, str]] = []
    current_title = "Scene 1"
    current_lines: list[str] = []
    scene_counter = 1

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            if current_lines:
                text = "\n".join(current_lines).strip()
                if text:
                    scenes.append((current_title, text))
                current_lines = []
            header_text = re.sub(r"^#+\s*", "", stripped)
            current_title = header_text if header_text else f"Scene {scene_counter}"
            scene_counter += 1
        elif stripped in ("---", "***", "___", "* * *", "###"):
            if current_lines:
                text = "\n".join(current_lines).strip()
                if text:
                    scenes.append((current_title, text))
                current_lines = []
            current_title = f"Scene {scene_counter}"
            scene_counter += 1
        else:
            current_lines.append(line)

    if current_lines:
        text = "\n".join(current_lines).strip()
        if text:
            scenes.append((current_title, text))

    if not scenes and content.strip():
        scenes.append(("Scene 1", content.strip()))

    return scenes


def extract_dialogue_and_narration(text: str) -> tuple[int, int]:
    """
    Count approximate words inside spoken quotes (dialogue) vs outside (narration).
    """
    dialogue_quotes = re.findall(r'["“][^"”]*["”]', text)
    dialogue_words = sum(len(q.split()) for q in dialogue_quotes)
    all_words = len(re.findall(r"\b\w+\b", text))
    narration_words = max(0, all_words - dialogue_words)
    return dialogue_words, narration_words


def check_phonetic_flags(text: str) -> list[str]:
    """
    Identifies potential tongue-twisters, excessive sibilance, or dense consonant clusters.
    """
    flags: list[str] = []
    words = re.findall(r"\b[a-zA-Z]+\b", text.lower())

    # 1. High Sibilance check (s, sh, z, ch clusters)
    sibilant_matches = len(re.findall(r"\b(s\w*|sh\w*|z\w*|ch\w*)\b", text.lower()))
    if len(words) > 30 and (sibilant_matches / len(words)) > 0.35:
        flags.append("High Sibilance Density: Frequent 's'/'sh'/'ch' sounds may cause microphone hiss.")

    # 2. 4+ word alliteration runs
    for i in range(len(words) - 3):
        w1, w2, w3, w4 = words[i], words[i + 1], words[i + 2], words[i + 3]
        if len(w1) > 2 and w1[0] == w2[0] == w3[0] == w4[0]:
            flags.append(f"Alliteration Hotspot: '{w1} {w2} {w3} {w4}' (Repeated '{w1[0]}' onset)")
            break

    # 3. Excessive sentence length (>45 words without comma/semicolon)
    sentences = re.split(r"[.!?]+", text)
    for s in sentences:
        s_words = len(s.split())
        if s_words > 45 and ("," not in s and ";" not in s and "—" not in s):
            flags.append(f"Breath Strain Warning: {s_words}-word clause without pause punctuation.")
            break

    return flags


def estimate_scene_duration(text: str, wpm: int = 150) -> tuple[float, float, int, float]:
    """
    Calculates estimated duration in seconds considering speech rate and punctuation pauses.
    Returns (duration_sec, pause_sec, max_sentence_len, breathability).
    """
    words = len(re.findall(r"\b\w+\b", text))
    if words == 0:
        return 0.0, 0.0, 0, 100.0

    # Base speech time: words / (wpm / 60)
    base_speech_sec = (words / max(1, wpm)) * 60.0

    # Punctuation pauses
    commas = len(re.findall(r"[,;:]", text))
    em_dashes = len(re.findall(r"(—|--)", text))
    ellipses = len(re.findall(r"(\.\.\.|…)", text))
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    sentence_count = len(sentences)
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    paragraph_count = len(paragraphs)

    pause_sec = (
        (commas * 0.15)
        + (em_dashes * 0.30)
        + (ellipses * 0.50)
        + (sentence_count * 0.40)
        + (paragraph_count * 0.50)
    )

    total_duration_sec = base_speech_sec + pause_sec

    # Sentence metrics & breathability
    sentence_lengths = [len(s.split()) for s in sentences] if sentences else [0]
    max_len = max(sentence_lengths) if sentence_lengths else 0
    avg_len = sum(sentence_lengths) / max(1, len(sentence_lengths)) if sentence_lengths else 0

    # Breathability: penalty for very long sentences and low pause punctuation
    penalty = 0.0
    if max_len > 35:
        penalty += min(35.0, (max_len - 35) * 1.5)
    if avg_len > 24:
        penalty += min(25.0, (avg_len - 24) * 2.0)

    breathability = max(10.0, min(100.0, 100.0 - penalty))

    return total_duration_sec, pause_sec, max_len, breathability


def format_seconds(seconds: float) -> str:
    """Format total seconds into MM:SS or HH:MM:SS."""
    total_sec = round(seconds)
    hours = total_sec // 3600
    minutes = (total_sec % 3600) // 60
    secs = total_sec % 60
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def generate_ssml(
    text: str,
    dialogue_pitch: str = "+5%",
    dialogue_rate: str = "medium",
    narration_pitch: str = "default",
    narration_rate: str = "medium",
    include_xml_header: bool = True,
) -> str:
    """
    Converts plain/markdown text into well-formed W3C SSML 1.0.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    ssml_body_parts: list[str] = []

    for p in paragraphs:
        # Check for scene break marker
        if p in ("---", "***", "___", "* * *"):
            ssml_body_parts.append('<break time="1500ms"/>')
            continue

        # Process paragraph line by line / quote by quote
        p_clean = html.escape(p)
        # Replace em-dashes and ellipses with SSML breaks
        p_clean = re.sub(r"(—|--)", ' <break time="300ms"/> ', p_clean)
        p_clean = re.sub(r"(\.\.\.|…)", ' <break time="500ms"/> ', p_clean)

        # Wrap dialogue in prosody
        def prosody_repl(match: re.Match[str]) -> str:
            quote_text = match.group(1)
            return f'<prosody pitch="{dialogue_pitch}" rate="{dialogue_rate}">{quote_text}</prosody>'

        p_prosody = re.sub(r'&quot;(.*?)&quot;', prosody_repl, p_clean)
        p_prosody = re.sub(r'“([^”]+)”', prosody_repl, p_prosody)

        p_wrapped = f'<p><prosody pitch="{narration_pitch}" rate="{narration_rate}">{p_prosody}</prosody></p><break time="500ms"/>'
        ssml_body_parts.append(p_wrapped)

    inner_ssml = "\n  ".join(ssml_body_parts)
    if include_xml_header:
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
  {inner_ssml}
</speak>"""
    return inner_ssml


def chunk_for_tts(text: str, max_chars: int = 3500) -> list[dict[str, Any]]:
    """
    Splits text into chunks under max_chars without breaking mid-sentence or mid-paragraph.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[dict[str, Any]] = []
    current_chunk_paragraphs: list[str] = []
    current_char_count = 0
    chunk_index = 1

    for p in paragraphs:
        p_len = len(p)
        if current_char_count + p_len > max_chars and current_chunk_paragraphs:
            chunk_text = "\n\n".join(current_chunk_paragraphs)
            chunks.append({
                "chunk_id": chunk_index,
                "text": chunk_text,
                "char_count": len(chunk_text),
                "word_count": len(re.findall(r"\b\w+\b", chunk_text)),
            })
            chunk_index += 1
            current_chunk_paragraphs = [p]
            current_char_count = p_len
        else:
            current_chunk_paragraphs.append(p)
            current_char_count += p_len + 2

    if current_chunk_paragraphs:
        chunk_text = "\n\n".join(current_chunk_paragraphs)
        chunks.append({
            "chunk_id": chunk_index,
            "text": chunk_text,
            "char_count": len(chunk_text),
            "word_count": len(re.findall(r"\b\w+\b", chunk_text)),
        })

    return chunks


def generate_tts_commands(
    chunks: list[dict[str, Any]],
    engine: str = "piper",
    model_or_voice: str = "en_US-lessac-medium",
    output_dir: str = "audio_chunks",
) -> list[str]:
    """
    Generates batch terminal execution commands for Piper or eSpeak NG.
    """
    commands: list[str] = []
    for c in chunks:
        cid = c["chunk_id"]
        in_file = f"{output_dir}/chunk_{cid:03d}.txt"
        out_wav = f"{output_dir}/chunk_{cid:03d}.wav"

        if engine.lower() == "piper":
            cmd = f"piper --model {model_or_voice} --input_file {in_file} --output_file {out_wav}"
        else:  # espeak-ng default
            cmd = f"espeak-ng -f {in_file} -w {out_wav} -v {model_or_voice} -s 150"
        commands.append(cmd)

    return commands


def analyze_audio_proofing(target_path: Path, wpm: int = 150) -> AudioProofReport:
    """
    Performs full manuscript audio proofing analysis.
    """
    if target_path.is_file():
        content = target_path.read_text(encoding="utf-8", errors="replace")
    elif target_path.is_dir():
        # Combine all markdown chapters in sorted order
        md_files = sorted(target_path.glob("*.md"))
        parts = []
        for f in md_files:
            parts.append(f.read_text(encoding="utf-8", errors="replace"))
        content = "\n\n---\n\n".join(parts) if parts else ""
    else:
        content = ""

    raw_scenes = split_scenes(content)
    scene_telemetries: list[AudioSceneTelemetry] = []

    total_words = 0
    total_chars = 0
    total_sentences = 0
    total_dialogue_words = 0
    total_narration_words = 0
    total_duration_sec = 0.0
    total_pause_sec = 0.0
    all_sentence_lens: list[int] = []

    for idx, (title, s_text) in enumerate(raw_scenes, start=1):
        words = len(re.findall(r"\b\w+\b", s_text))
        chars = len(s_text)
        s_count = len([s for s in re.split(r"[.!?]+", s_text) if s.strip()])
        d_words, n_words = extract_dialogue_and_narration(s_text)
        d_ratio = round((d_words / words) if words > 0 else 0.0, 3)

        dur_sec, pause_sec, max_sent, breath = estimate_scene_duration(s_text, wpm=wpm)
        phonetic = check_phonetic_flags(s_text)
        ssml_snip = generate_ssml(s_text[:400] + ("..." if len(s_text) > 400 else ""))

        telemetry = AudioSceneTelemetry(
            scene_id=idx,
            title=title,
            word_count=words,
            char_count=chars,
            sentence_count=s_count,
            dialogue_words=d_words,
            narration_words=n_words,
            dialogue_ratio=d_ratio,
            estimated_duration_sec=dur_sec,
            formatted_duration=format_seconds(dur_sec),
            pause_time_sec=pause_sec,
            longest_sentence_words=max_sent,
            breathability_score=round(breath, 1),
            ssml_snippet=ssml_snip,
            text_content=s_text,
            phonetic_flags=phonetic,
        )
        scene_telemetries.append(telemetry)

        total_words += words
        total_chars += chars
        total_sentences += s_count
        total_dialogue_words += d_words
        total_narration_words += n_words
        total_duration_sec += dur_sec
        total_pause_sec += pause_sec

        sentences = [len(s.split()) for s in re.split(r"[.!?]+", s_text) if s.strip()]
        all_sentence_lens.extend(sentences)

    overall_d_ratio = round((total_dialogue_words / total_words) if total_words > 0 else 0.0, 3)
    avg_sent_len = round(sum(all_sentence_lens) / max(1, len(all_sentence_lens)), 1)

    chunks = chunk_for_tts(content)
    commands = generate_tts_commands(chunks, engine="piper")

    return AudioProofReport(
        target_path=str(target_path),
        total_words=total_words,
        total_chars=total_chars,
        total_sentences=total_sentences,
        total_dialogue_words=total_dialogue_words,
        total_narration_words=total_narration_words,
        overall_dialogue_ratio=overall_d_ratio,
        target_wpm=wpm,
        total_duration_sec=total_duration_sec,
        total_duration_formatted=format_seconds(total_duration_sec),
        total_pause_sec=round(total_pause_sec, 1),
        average_sentence_length=avg_sent_len,
        scenes=scene_telemetries,
        tts_chunks=chunks,
        tts_commands=commands,
    )


def render_audio_proof_html(report: AudioProofReport, output_path: Path) -> Path:
    """
    Renders a standalone interactive HTML audio proofing dossier.
    """
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:; media-src data: blob:;">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ars Arcanum — Audio Proofing & Speech Dossier</title>
<style>
  :root {{
    --bg: #090d16; --panel: #131b2e; --border: #23304d;
    --text: #f1f5f9; --muted: #94a3b8; --accent: #38bdf8; --gold: #fbbf24;
    --emerald: #10b981; --rose: #f43f5e;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    font-family: system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--text);
    margin: 0; padding: 1.5rem; line-height: 1.5;
  }}
  .container {{ max-width: 1200px; margin: 0 auto; }}
  header {{
    background: var(--panel); border: 1px solid var(--border); border-radius: 12px;
    padding: 1.5rem 2rem; margin-bottom: 1.5rem; display: flex; justify-content: space-between;
    align-items: center; flex-wrap: wrap; gap: 1rem;
  }}
  h1 {{ margin: 0; font-size: 1.6rem; color: var(--accent); }}
  .kpi-grid {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem;
    margin-bottom: 1.5rem;
  }}
  .kpi-card {{
    background: var(--panel); border: 1px solid var(--border); border-radius: 8px;
    padding: 1rem 1.25rem;
  }}
  .kpi-title {{ font-size: 0.75rem; text-transform: uppercase; color: var(--muted); font-weight: 600; }}
  .kpi-val {{ font-size: 1.5rem; font-weight: 700; color: var(--gold); margin-top: 0.25rem; }}
  .scene-card {{
    background: var(--panel); border: 1px solid var(--border); border-radius: 8px;
    padding: 1.25rem; margin-bottom: 1rem;
  }}
  .scene-header {{
    display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;
    border-bottom: 1px solid var(--border); padding-bottom: 0.5rem;
  }}
  .tag {{
    display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem;
    font-weight: 600; background: rgba(56, 189, 248, 0.15); color: var(--accent);
  }}
  .tag-warn {{ background: rgba(244, 63, 94, 0.15); color: var(--rose); }}
  .tag-good {{ background: rgba(16, 185, 129, 0.15); color: var(--emerald); }}
  pre {{
    background: #060911; border: 1px solid var(--border); border-radius: 6px;
    padding: 0.75rem; overflow-x: auto; font-size: 0.82rem; color: #cbd5e1;
  }}
  .flag-list {{ list-style: none; padding: 0; margin: 0.5rem 0 0 0; }}
  .flag-list li {{
    padding: 0.35rem 0.6rem; background: rgba(244, 63, 94, 0.1); border-left: 3px solid var(--rose);
    font-size: 0.82rem; margin-bottom: 0.3rem; border-radius: 0 4px 4px 0;
  }}
</style>
</head>
<body>
<div class="container">
  <header>
    <div>
      <h1>🎙️ Ars Arcanum Audio Proofing & Speech Dossier</h1>
      <div style="color:var(--muted);font-size:0.875rem;margin-top:0.25rem;">
        Target: <code style="color:var(--gold);">{html.escape(report.target_path)}</code> | Speed: {report.target_wpm} WPM
      </div>
    </div>
  </header>

  <div class="kpi-grid">
    <div class="kpi-card">
      <div class="kpi-title">Total Speech Duration</div>
      <div class="kpi-val">{report.total_duration_formatted}</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-title">Total Words</div>
      <div class="kpi-val">{report.total_words:,}</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-title">Dialogue Ratio</div>
      <div class="kpi-val">{(report.overall_dialogue_ratio * 100):.1f}%</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-title">Avg Sentence Length</div>
      <div class="kpi-val">{report.average_sentence_length} words</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-title">Pause Time Allocated</div>
      <div class="kpi-val">{report.total_pause_sec}s</div>
    </div>
  </div>

  <h2 style="color:var(--accent);font-size:1.25rem;margin-top:2rem;">📋 Scene-by-Scene Audio Breakdown ({len(report.scenes)} scenes)</h2>
  <div id="sceneContainer">
"""

    for s in report.scenes:
        breath_class = "tag-good" if s.breathability_score >= 80 else ("tag-warn" if s.breathability_score < 60 else "")
        flags_html = "".join(f"<li>⚠️ {html.escape(f)}</li>" for f in s.phonetic_flags)
        if not flags_html:
            flags_html = '<li style="background:rgba(16,185,129,0.1);border-color:var(--emerald);color:var(--emerald);">✓ Clean narration cadence; no phonetic collision flags.</li>'

        html_content += f"""
    <div class="scene-card">
      <div class="scene-header">
        <div>
          <strong style="color:var(--gold);font-size:1.05rem;">{html.escape(s.title)}</strong>
          <span style="color:var(--muted);font-size:0.8rem;margin-left:0.5rem;">({s.word_count} words • {s.sentence_count} sentences)</span>
        </div>
        <div>
          <span class="tag">⏱️ {s.formatted_duration}</span>
          <span class="tag {breath_class}">Breathability: {s.breathability_score}/100</span>
          <span class="tag">💬 {(s.dialogue_ratio * 100):.0f}% dialogue</span>
        </div>
      </div>
      <div>
        <ul class="flag-list">
          {flags_html}
        </ul>
      </div>
      <details style="margin-top:0.75rem;">
        <summary style="font-size:0.82rem;color:var(--accent);cursor:pointer;">View W3C SSML Markup</summary>
        <pre><code>{html.escape(s.ssml_snippet)}</code></pre>
      </details>
    </div>
"""

    html_content += f"""
  </div>

  <h2 style="color:var(--accent);font-size:1.25rem;margin-top:2rem;">⚡ Neural TTS Batch Commands ({len(report.tts_chunks)} Chunks)</h2>
  <div class="scene-card">
    <p style="font-size:0.85rem;color:var(--muted);margin-top:0;">Run these commands offline with <code>piper</code> or <code>espeak-ng</code> to synthesize audio proof files:</p>
    <pre><code>"""

    for cmd in report.tts_commands:
        html_content += f"{html.escape(cmd)}\n"

    html_content += """</code></pre>
  </div>
</div>
</body>
</html>
"""
    atomic_write(output_path, html_content)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Ars Arcanum Sovereign Audio Proofing Engine")
    parser.add_argument("target", help="Path to manuscript file or directory")
    parser.add_argument("--wpm", type=int, default=150, help="Target narration words per minute (default: 150)")
    parser.add_argument("--ssml", action="store_true", help="Print full SSML output to stdout")
    parser.add_argument("--html", help="Generate interactive HTML audio proofing dossier at output path")
    parser.add_argument("--json", action="store_true", help="Output telemetry report as JSON to stdout")
    parser.add_argument("--chunks-dir", help="Directory to output text chunks for TTS batch processing")
    args = parser.parse_args()

    target_path = Path(args.target)
    if not target_path.exists():
        print(f"Error: Target path does not exist: {target_path}", file=sys.stderr)
        sys.exit(1)

    report = analyze_audio_proofing(target_path, wpm=args.wpm)

    if args.chunks_dir:
        chunk_dir = Path(args.chunks_dir)
        chunk_dir.mkdir(parents=True, exist_ok=True)
        for c in report.tts_chunks:
            c_file = chunk_dir / f"chunk_{c['chunk_id']:03d}.txt"
            atomic_write(c_file, c["text"])
        print(f"Wrote {len(report.tts_chunks)} TTS chunks to {chunk_dir}")

    if args.html:
        out_html = Path(args.html)
        render_audio_proof_html(report, out_html)
        print(f"Audio proofing HTML report generated: {out_html}")

    if args.ssml:
        if target_path.is_file():
            text = target_path.read_text(encoding="utf-8", errors="replace")
        else:
            text = "\n\n".join(f.read_text(encoding="utf-8", errors="replace") for f in sorted(target_path.glob("*.md")))
        print(generate_ssml(text))
        return

    if args.json:
        print(json.dumps(asdict(report), indent=2))
        return

    # Default human-readable output
    print("=" * 75)
    print("  🎙️  Ars Arcanum Sovereign Audio Proofing & Speech Engine")
    print("=" * 75)
    print(f"Target Manuscript:       {report.target_path}")
    print(f"Total Words:             {report.total_words:,} words ({report.total_chars:,} chars)")
    print(f"Narration Speed:         {report.target_wpm} WPM")
    print(f"Estimated Duration:      {report.total_duration_formatted} ({report.total_duration_sec:.1f}s)")
    print(f"Pause Allocation:        {report.total_pause_sec:.1f}s ({round(report.total_pause_sec / max(1.0, report.total_duration_sec) * 100, 1)}% of time)")
    print(f"Dialogue / Narration:    {(report.overall_dialogue_ratio * 100):.1f}% Dialogue | {((1 - report.overall_dialogue_ratio) * 100):.1f}% Narration")
    print(f"Avg Sentence Length:     {report.average_sentence_length} words")
    print(f"Identified Scenes:       {len(report.scenes)}")
    print("-" * 75)
    print("Scene Breakdown:")
    for s in report.scenes[:10]:
        flag_str = f" | ⚠️ {len(s.phonetic_flags)} flags" if s.phonetic_flags else ""
        print(f" • [{s.formatted_duration}] {s.title:<30} {s.word_count:>5}w (Breathability: {s.breathability_score}/100{flag_str})")
    if len(report.scenes) > 10:
        print(f"   ... and {len(report.scenes) - 10} more scenes.")
    print("=" * 75)


if __name__ == "__main__":
    main()
