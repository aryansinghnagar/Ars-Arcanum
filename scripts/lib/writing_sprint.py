#!/usr/bin/env python3
"""
Ars Arcanum Writing Sprint & Cognitive Velocity Engine (scripts/lib/writing_sprint.py)
====================================================================================
Offline author productivity timer, session velocity analytics logger, and habit
consistency engine for speculative fiction authors.

Features:
- Stateful sprint lifecycle (start, stop, status, cancel, log, stats, report)
- Multi-source hybrid velocity derivation (.arcanum/sprint_log.jsonl, Obsidian Daily-Writing-Log, Git snapshots)
- Rolling 7d/30d velocity (WPM, WPH, daily words), daily streaks, time-of-day peak flow analysis
- Standalone HTML5 Velocity & Sprint Studio exporter (--html)
- Zero external dependencies; 100% offline Content Security Policy.
"""

from __future__ import annotations

import argparse
import datetime
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any

try:
    from lib._bootstrap import atomic_write, count_prose_words
    from lib.frontmatter import extract_frontmatter_and_body
    from lib.scope import resolve_manuscript_path
    from lib.velocity_template import render_velocity_html
except ImportError:
    from _bootstrap import atomic_write, count_prose_words
    from frontmatter import extract_frontmatter_and_body
    from scope import resolve_manuscript_path
    try:
        from velocity_template import render_velocity_html
    except ImportError:
        render_velocity_html = None  # type: ignore[assignment]

logger = logging.getLogger("arcanum.sprint")


def _get_arcanum_dir(ms_dir: Path) -> Path:
    """Returns the .arcanum hidden metadata directory for a manuscript or project."""
    arc_dir = ms_dir / ".arcanum"
    arc_dir.mkdir(parents=True, exist_ok=True)
    return arc_dir


def _get_state_file(ms_dir: Path) -> Path:
    """Returns the path to the active sprint state lock file."""
    return _get_arcanum_dir(ms_dir) / ".sprint_state.json"


def _get_log_file(ms_dir: Path) -> Path:
    """Returns the path to the historical sprint JSONL log file."""
    return _get_arcanum_dir(ms_dir) / "sprint_log.jsonl"


def _count_current_manuscript_words(ms_dir: Path, chapter_file: str | None = None) -> int:
    """Computes current total words in the manuscript or target chapter."""
    if chapter_file:
        target_path = Path(chapter_file)
        if not target_path.is_file():
            target_path = ms_dir / chapter_file
        if target_path.is_file():
            try:
                content = target_path.read_text(encoding="utf-8", errors="replace")
                return count_prose_words(content)
            except Exception:
                return 0

    # Count across all markdown files in manuscript
    total = 0
    for md_file in ms_dir.rglob("*.md"):
        if (
            not md_file.name.startswith((".", "_"))
            and "Backups" not in md_file.parts
            and ".arcanum" not in md_file.parts
        ):
            try:
                txt = md_file.read_text(encoding="utf-8", errors="replace")
                total += count_prose_words(txt)
            except Exception:
                pass
    return total


def start_sprint(
    target_dir: Path | str,
    target_words: int = 500,
    minutes: int = 25,
    chapter: str | None = None,
    interactive: bool = False,
    force: bool = False,
) -> dict[str, Any]:
    """Starts a new sprint session and writes state to .arcanum/.sprint_state.json."""
    ms_path = resolve_manuscript_path(target_dir) or Path(target_dir).resolve()
    if not ms_path.is_dir():
        raise FileNotFoundError(f"Manuscript directory not found: {target_dir}")

    state_file = _get_state_file(ms_path)
    if state_file.is_file() and not force:
        try:
            existing = json.loads(state_file.read_text(encoding="utf-8", errors="replace"))
            raise RuntimeError(
                f"An active sprint is already running (started at {existing.get('timestamp')}). "
                "Run 'arcanum sprint stop' to conclude it or 'arcanum sprint cancel' to abort."
            )
        except json.JSONDecodeError:
            pass  # Stale or corrupted file, proceed with overwrite

    initial_words = _count_current_manuscript_words(ms_path, chapter)
    session_id = f"sprint_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    timestamp_iso = datetime.datetime.now().isoformat()
    start_unix = time.time()

    state = {
        "session_id": session_id,
        "timestamp": timestamp_iso,
        "start_time_unix": start_unix,
        "target_words": int(target_words),
        "planned_duration_min": int(minutes),
        "manuscript_dir": str(ms_path),
        "chapter_target": chapter or "",
        "initial_word_count": initial_words,
    }

    atomic_write(state_file, json.dumps(state, indent=2))

    if interactive and hasattr(sys.stdout, "isatty") and sys.stdout.isatty():
        _run_interactive_tty_timer(ms_path, state)

    return {
        "status": "started",
        "session_id": session_id,
        "timestamp": timestamp_iso,
        "target_words": target_words,
        "duration_minutes": minutes,
        "initial_word_count": initial_words,
        "chapter": chapter or "Full Manuscript",
    }


def _run_interactive_tty_timer(ms_path: Path, state: dict[str, Any]) -> None:
    """Runs a live countdown timer in interactive TTY mode."""
    duration_sec = state["planned_duration_min"] * 60
    start_time = state["start_time_unix"]
    target_words = state["target_words"]
    ch = state.get("chapter_target") or "Manuscript"

    print(f"\n🚀 Writing Sprint Started! Target: {target_words:,} words in {state['planned_duration_min']} min ({ch})")
    print("Press Ctrl+C at any time to finish or pause.\n")

    try:
        while True:
            elapsed = time.time() - start_time
            remaining = max(0, duration_sec - elapsed)
            rem_m = int(remaining // 60)
            rem_s = int(remaining % 60)
            pct = min(100.0, (elapsed / max(1, duration_sec)) * 100.0)

            # Live timer string with ANSI carriage return
            sys.stdout.write(f"\r⏱️  Time Remaining: \033[1;36m{rem_m:02d}:{rem_s:02d}\033[0m ({pct:4.1f}%) | Goal: {target_words}w   ")
            sys.stdout.flush()

            if remaining <= 0:
                print("\n\n🎉 Sprint Duration Complete! Time is up!")
                break
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\n\n⏸️ Sprint timer stopped by user.")


def status_sprint(target_dir: Path | str) -> dict[str, Any]:
    """Queries the currently active sprint session."""
    ms_path = resolve_manuscript_path(target_dir) or Path(target_dir).resolve()
    state_file = _get_state_file(ms_path)
    if not state_file.is_file():
        return {"status": "inactive", "message": "No active sprint session running."}

    try:
        state = json.loads(state_file.read_text(encoding="utf-8", errors="replace"))
    except Exception as e:
        return {"status": "error", "message": f"Corrupted sprint state file: {e}"}

    start_unix = state.get("start_time_unix", time.time())
    elapsed_min = round((time.time() - start_unix) / 60.0, 1)
    planned_min = state.get("planned_duration_min", 25)
    target_words = state.get("target_words", 500)
    init_words = state.get("initial_word_count", 0)
    ch = state.get("chapter_target") or None

    cur_words = _count_current_manuscript_words(ms_path, ch)
    delta_words = max(0, cur_words - init_words)
    wpm = round(delta_words / max(0.1, elapsed_min), 1)

    return {
        "status": "active",
        "session_id": state.get("session_id"),
        "started_at": state.get("timestamp"),
        "elapsed_minutes": elapsed_min,
        "planned_duration_min": planned_min,
        "target_words": target_words,
        "initial_words": init_words,
        "current_words": cur_words,
        "words_written": delta_words,
        "instantaneous_wpm": wpm,
        "chapter": ch or "Full Manuscript",
    }


def stop_sprint(
    target_dir: Path | str,
    manual_words: int | None = None,
) -> dict[str, Any]:
    """Concludes the active sprint session, logs record to sprint_log.jsonl, and removes state lock."""
    ms_path = resolve_manuscript_path(target_dir) or Path(target_dir).resolve()
    state_file = _get_state_file(ms_path)
    if not state_file.is_file():
        raise RuntimeError("No active sprint session found. Use 'arcanum sprint start' first.")

    try:
        state = json.loads(state_file.read_text(encoding="utf-8", errors="replace"))
    except Exception as e:
        state_file.unlink(missing_ok=True)
        raise RuntimeError(f"Corrupted sprint state file cleared: {e}") from e

    start_unix = state.get("start_time_unix", time.time())
    duration_min = round(max(0.1, (time.time() - start_unix) / 60.0), 2)
    target_words = state.get("target_words", 500)
    init_words = state.get("initial_word_count", 0)
    ch = state.get("chapter_target") or ""

    if manual_words is not None:
        words_written = int(manual_words)
    else:
        cur_words = _count_current_manuscript_words(ms_path, ch if ch else None)
        words_written = max(0, cur_words - init_words)

    wpm = round(words_written / duration_min, 2)
    wph = round(wpm * 60, 1)
    ratio = round(words_written / max(1, target_words), 3)

    record = {
        "session_id": state.get("session_id"),
        "timestamp": datetime.datetime.now().isoformat(),
        "duration_min": duration_min,
        "words_written": words_written,
        "wpm": wpm,
        "wph": wph,
        "target": target_words,
        "completion_ratio": ratio,
        "chapter": ch,
    }

    # Append to JSONL log
    log_file = _get_log_file(ms_path)
    record_line = json.dumps(record) + "\n"
    with log_file.open("a", encoding="utf-8") as f:
        f.write(record_line)

    # Clean up state lock file
    state_file.unlink(missing_ok=True)

    return {
        "status": "completed",
        "session_id": record["session_id"],
        "duration_minutes": duration_min,
        "words_written": words_written,
        "target_words": target_words,
        "wpm": wpm,
        "wph": wph,
        "completion_ratio": ratio,
        "completion_percentage": round(ratio * 100.0, 1),
        "chapter": ch or "Full Manuscript",
    }


def cancel_sprint(target_dir: Path | str) -> dict[str, Any]:
    """Aborts the active sprint session without saving to sprint_log.jsonl."""
    ms_path = resolve_manuscript_path(target_dir) or Path(target_dir).resolve()
    state_file = _get_state_file(ms_path)
    if state_file.is_file():
        state_file.unlink(missing_ok=True)
        return {"status": "cancelled", "message": "Active sprint session cancelled."}
    return {"status": "inactive", "message": "No active sprint session was running."}


def log_manual_sprint(
    target_dir: Path | str,
    words: int,
    minutes: float = 25.0,
    timestamp: str | None = None,
    target_words: int = 500,
    chapter: str = "",
) -> dict[str, Any]:
    """Manually records a completed writing session into .arcanum/sprint_log.jsonl."""
    ms_path = resolve_manuscript_path(target_dir) or Path(target_dir).resolve()
    if not ms_path.is_dir():
        raise FileNotFoundError(f"Manuscript directory not found: {target_dir}")

    ts = timestamp or datetime.datetime.now().isoformat()
    duration = max(0.1, float(minutes))
    wpm = round(words / duration, 2)
    wph = round(wpm * 60, 1)
    ratio = round(words / max(1, target_words), 3)
    session_id = f"manual_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"

    record = {
        "session_id": session_id,
        "timestamp": ts,
        "duration_min": duration,
        "words_written": int(words),
        "wpm": wpm,
        "wph": wph,
        "target": int(target_words),
        "completion_ratio": ratio,
        "chapter": chapter,
    }

    log_file = _get_log_file(ms_path)
    with log_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

    return {
        "status": "logged",
        "record": record,
    }


def get_velocity_metrics(target_dir: Path | str) -> dict[str, Any]:
    """
    Hybrid velocity engine aggregating drafting logs across:
    1. .arcanum/sprint_log.jsonl
    2. Obsidian Daily-Writing-Log markdown files
    3. Historical snapshot / git commit timestamp deltas
    """
    ms_path = resolve_manuscript_path(target_dir) or Path(target_dir).resolve()
    sprints: list[dict[str, Any]] = []

    # Source 1: .arcanum/sprint_log.jsonl
    log_file = _get_log_file(ms_path)
    if log_file.is_file():
        for line in log_file.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if line:
                try:
                    sprints.append(json.loads(line))
                except Exception:
                    pass

    # Source 2: Scan for Obsidian Daily-Writing-Log markdown notes
    seen_files: set[Path] = set()
    search_dirs = [ms_path]
    if ms_path.parent.is_dir() and ms_path.parent != ms_path:
        search_dirs.append(ms_path.parent)

    for s_dir in search_dirs:
        for f in s_dir.rglob("*.md"):
            real_f = f.resolve()
            if real_f in seen_files:
                continue
            seen_files.add(real_f)

            if real_f.is_file() and ("Writing-Log" in real_f.name or "WritingLog" in real_f.name):
                # Ignore unrendered templates in Templates/ folders
                if "Templates" in real_f.parts or "templates" in real_f.parts:
                    continue
                try:
                    content = real_f.read_text(encoding="utf-8", errors="replace")
                    fm, _ = extract_frontmatter_and_body(content)
                    if fm.get("fileClass") == "WritingLog" or fm.get("type") == "daily_writing_log":
                        date_raw = str(fm.get("date", ""))
                        if date_raw.startswith("<%") or not date_raw:
                            continue  # Skip unrendered templater placeholders
                        words_w = int(fm.get("words_written", 0))
                        time_m = float(fm.get("writing_time_minutes", 25.0))
                        wpm_val = float(fm.get("wpm_velocity", words_w / max(0.1, time_m)))
                        goal = int(fm.get("goal") or fm.get("dailyGoal") or fm.get("target_words_daily") or 1000)

                        sprints.append({
                            "session_id": f"obsidian_{real_f.stem}",
                            "timestamp": f"{date_raw}T12:00:00",
                            "duration_min": time_m,
                            "words_written": words_w,
                            "wpm": round(wpm_val, 2),
                            "wph": round(wpm_val * 60, 1),
                            "target": goal,
                            "completion_ratio": round(words_w / max(1, goal), 3),
                            "chapter": str(fm.get("scene_worked_on", "")),
                        })
                except Exception:
                    pass

    # Sort sprints chronologically
    sprints.sort(key=lambda x: str(x.get("timestamp", "")))

    total_sessions = len(sprints)
    total_words = sum(s.get("words_written", 0) for s in sprints)
    total_minutes = sum(s.get("duration_min", 0.0) for s in sprints)
    overall_wpm = round(total_words / max(0.1, total_minutes), 2) if total_minutes > 0 else 0.0

    # Rolling windows (7 days, 30 days)
    now = datetime.datetime.now()
    cutoff_7d = now - datetime.timedelta(days=7)
    cutoff_30d = now - datetime.timedelta(days=30)

    words_7d, min_7d = 0, 0.0
    words_30d, min_30d = 0, 0.0
    active_days: set[str] = set()
    tod_dist = {"Morning (6-12)": 0, "Afternoon (12-18)": 0, "Evening (18-24)": 0, "Night (0-6)": 0}

    for s in sprints:
        ts_str = str(s.get("timestamp", ""))
        try:
            ts_dt = datetime.datetime.fromisoformat(ts_str[:19])
        except (ValueError, TypeError):
            continue

        day_key = ts_dt.strftime("%Y-%m-%d")
        active_days.add(day_key)
        w = s.get("words_written", 0)
        m = s.get("duration_min", 0.0)

        # Time of day analysis
        hr = ts_dt.hour
        if 6 <= hr < 12:
            tod_dist["Morning (6-12)"] += w
        elif 12 <= hr < 18:
            tod_dist["Afternoon (12-18)"] += w
        elif 18 <= hr < 24:
            tod_dist["Evening (18-24)"] += w
        else:
            tod_dist["Night (0-6)"] += w

        if ts_dt >= cutoff_7d:
            words_7d += w
            min_7d += m
        if ts_dt >= cutoff_30d:
            words_30d += w
            min_30d += m

    rolling_7d_wpd = int(words_7d / 7) if total_sessions > 0 else 0
    rolling_7d_wpm = round(words_7d / max(0.1, min_7d), 2) if min_7d > 0 else 0.0
    rolling_30d_wpd = int(words_30d / 30) if total_sessions > 0 else 0
    rolling_30d_wpm = round(words_30d / max(0.1, min_30d), 2) if min_30d > 0 else 0.0

    # Habit streak calculation
    cur_streak = 0
    best_streak = 0
    sorted_days = sorted([datetime.date.fromisoformat(d) for d in active_days])

    if sorted_days:
        # Check current streak up to today or yesterday
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)

        check_day = today if today in sorted_days else (yesterday if yesterday in sorted_days else None)
        if check_day:
            temp_streak = 0
            curr_check = check_day
            day_set = set(sorted_days)
            while curr_check in day_set:
                temp_streak += 1
                curr_check -= datetime.timedelta(days=1)
            cur_streak = temp_streak

        # Longest consecutive streak
        temp_best = 1
        curr_run = 1
        for i in range(1, len(sorted_days)):
            if (sorted_days[i] - sorted_days[i - 1]).days == 1:
                curr_run += 1
                if curr_run > temp_best:
                    temp_best = curr_run
            else:
                curr_run = 1
        best_streak = temp_best if sorted_days else 0

    return {
        "total_sprint_sessions": total_sessions,
        "total_sprint_words": total_words,
        "total_sprint_minutes": round(total_minutes, 1),
        "overall_average_wpm": overall_wpm,
        "rolling_7d_daily_words": rolling_7d_wpd,
        "rolling_7d_wpm": rolling_7d_wpm,
        "rolling_30d_daily_words": rolling_30d_wpd,
        "rolling_30d_wpm": rolling_30d_wpm,
        "current_streak_days": cur_streak,
        "best_streak_days": best_streak,
        "time_of_day_distribution": tod_dist,
        "sprint_history": sprints,
    }


def format_stats_table(vel: dict[str, Any], title: str = "Manuscript") -> str:
    """Formats velocity statistics into an ANSI terminal report."""
    lines = []
    lines.append(f"⚡  {title} — Drafting Velocity & Sprint Telemetry")
    lines.append("═" * 70)
    lines.append(f"  Total Sprints:    {vel.get('total_sprint_sessions', 0):>6} sessions")
    lines.append(f"  Sprint Words:     {vel.get('total_sprint_words', 0):>6,} words ({vel.get('total_sprint_minutes', 0):.0f} active minutes)")
    lines.append(f"  All-Time Velocity: {vel.get('overall_average_wpm', 0):>5.1f} WPM ({vel.get('overall_average_wpm', 0)*60:>6.0f} WPH)")
    lines.append("─" * 70)
    lines.append(f"  7-Day Rolling:    {vel.get('rolling_7d_daily_words', 0):>6,} words/day ({vel.get('rolling_7d_wpm', 0):.1f} WPM)")
    lines.append(f"  30-Day Rolling:   {vel.get('rolling_30d_daily_words', 0):>6,} words/day ({vel.get('rolling_30d_wpm', 0):.1f} WPM)")
    lines.append(f"  Daily Streak:     {vel.get('current_streak_days', 0):>6} days (Best: {vel.get('best_streak_days', 0)} days)")
    lines.append("═" * 70)

    # Time of day flow
    tod = vel.get("time_of_day_distribution", {})
    if any(tod.values()):
        lines.append("\n🌅  Drafting Velocity by Time of Day:")
        tot_tod = max(1, sum(tod.values()))
        for k, v in tod.items():
            pct = (v / tot_tod) * 100.0
            lines.append(f"  • {k:<20} {v:>7,} words ({pct:5.1f}%)")

    # Recent sprints
    history = vel.get("sprint_history", [])
    if history:
        lines.append("\n📋  Recent Sprints (Last 5):")
        lines.append(f"{'Date/Time':<18} {'Target':<14} {'Min':>6} {'Words':>8} {'WPM':>8} {'Ratio':>8}")
        lines.append("─" * 70)
        for s in reversed(history[-5:]):
            ts = str(s.get("timestamp", ""))[:16].replace("T", " ")
            ch = str(s.get("chapter", ""))[:12] or "General"
            dur = s.get("duration_min", 0.0)
            w = s.get("words_written", 0)
            wpm = s.get("wpm", 0.0)
            rat = s.get("completion_ratio", 0.0) * 100.0
            lines.append(f"{ts:<18} {ch:<14} {dur:>6.1f} {w:>8,} {wpm:>8.1f} {rat:>7.0f}%")

    return "\n".join(lines)


def format_stats_markdown(vel: dict[str, Any], title: str = "Manuscript") -> str:
    """Formats velocity statistics as GitHub Markdown."""
    lines = []
    lines.append(f"# {title} — Drafting Velocity & Sprint Telemetry\n")
    lines.append(f"- **Total Sprint Sessions**: {vel.get('total_sprint_sessions', 0)}")
    lines.append(f"- **Sprint Words Written**: {vel.get('total_sprint_words', 0):,} words")
    lines.append(f"- **All-Time Average Velocity**: {vel.get('overall_average_wpm', 0):.1f} WPM")
    lines.append(f"- **7-Day Rolling Pace**: {vel.get('rolling_7d_daily_words', 0):,} words/day")
    lines.append(f"- **Active Habit Streak**: {vel.get('current_streak_days', 0)} consecutive days (Best: {vel.get('best_streak_days', 0)} days)\n")

    history = vel.get("sprint_history", [])
    if history:
        lines.append("## Recent Sprint Sessions\n")
        lines.append("| Date/Time | Target Chapter | Duration (min) | Words | WPM | Target Completion |")
        lines.append("| :--- | :--- | ---: | ---: | ---: | ---: |")
        for s in reversed(history[-10:]):
            ts = str(s.get("timestamp", ""))[:16].replace("T", " ")
            ch = str(s.get("chapter", "")) or "General"
            lines.append(f"| {ts} | {ch} | {s.get('duration_min', 0):.1f} | {s.get('words_written', 0):,} | {s.get('wpm', 0):.1f} | {s.get('completion_ratio', 0)*100:.0f}% |")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ars Arcanum Writing Sprint & Cognitive Velocity Engine")
    subparsers = parser.add_subparsers(dest="command", help="Sprint sub-command")

    # start
    p_start = subparsers.add_parser("start", help="Start a new writing sprint session")
    p_start.add_argument("manuscript", nargs="?", default=".", help="Manuscript directory")
    p_start.add_argument("--target", "-t", type=int, default=500, help="Target word count (default: 500)")
    p_start.add_argument("--minutes", "-m", type=int, default=25, help="Sprint duration in minutes (default: 25)")
    p_start.add_argument("--chapter", "-c", help="Specific chapter filename target")
    p_start.add_argument("--no-interactive", "-n", action="store_true", help="Start in non-interactive background mode")
    p_start.add_argument("--force", "-f", action="store_true", help="Force start and overwrite stale sprint state")
    p_start.add_argument("--json", action="store_true", help="Output JSON results")

    # stop
    p_stop = subparsers.add_parser("stop", help="Stop the active sprint session and record words")
    p_stop.add_argument("manuscript", nargs="?", default=".", help="Manuscript directory")
    p_stop.add_argument("--words", "-w", type=int, help="Manual words written override (default: auto-computed)")
    p_stop.add_argument("--json", action="store_true", help="Output JSON results")

    # status
    p_stat = subparsers.add_parser("status", help="Query active sprint session status")
    p_stat.add_argument("manuscript", nargs="?", default=".", help="Manuscript directory")
    p_stat.add_argument("--json", action="store_true", help="Output JSON results")

    # cancel / abort
    p_cancel = subparsers.add_parser("cancel", help="Cancel and abort active sprint session without saving")
    p_cancel.add_argument("manuscript", nargs="?", default=".", help="Manuscript directory")
    p_cancel.add_argument("--json", action="store_true", help="Output JSON results")

    # log
    p_log = subparsers.add_parser("log", help="Manually log a completed sprint session")
    p_log.add_argument("manuscript", nargs="?", default=".", help="Manuscript directory")
    p_log.add_argument("--words", "-w", type=int, required=True, help="Words written")
    p_log.add_argument("--minutes", "-m", type=float, default=25.0, help="Duration in minutes (default: 25)")
    p_log.add_argument("--target", "-t", type=int, default=500, help="Target word goal")
    p_log.add_argument("--chapter", "-c", default="", help="Chapter name")
    p_log.add_argument("--json", action="store_true", help="Output JSON results")

    # stats / history
    p_hist = subparsers.add_parser("stats", help="Display drafting velocity and sprint history statistics")
    p_hist.add_argument("manuscript", nargs="?", default=".", help="Manuscript directory")
    p_hist.add_argument("--json", action="store_true", help="Output JSON results")
    p_hist.add_argument("--md", action="store_true", help="Output Markdown report")
    p_hist.add_argument("--html", help="Generate standalone offline HTML5 Velocity Studio")
    p_hist.add_argument("--open", action="store_true", help="Open generated HTML5 Velocity Studio in default browser")

    # report
    p_rep = subparsers.add_parser("report", help="Generate standalone HTML5 Velocity & Sprint Studio")
    p_rep.add_argument("manuscript", nargs="?", default=".", help="Manuscript directory")
    p_rep.add_argument("--html", "-o", default="dist/velocity_studio.html", help="Output HTML file path")
    p_rep.add_argument("--open", action="store_true", help="Open generated HTML5 Velocity Studio in default browser")
    p_rep.add_argument("--json", action="store_true", help="Output JSON results")

    args = parser.parse_args(argv)

    cmd = args.command or "status"
    ms_dir = getattr(args, "manuscript", ".")

    try:
        if cmd == "start":
            res = start_sprint(
                ms_dir,
                target_words=args.target,
                minutes=args.minutes,
                chapter=args.chapter,
                interactive=not args.no_interactive,
                force=args.force,
            )
            if args.json:
                print(json.dumps(res, indent=2))
            else:
                print(f"🚀 Sprint session started: {res['session_id']} (Goal: {res['target_words']}w in {res['duration_minutes']}m)")
            return 0

        if cmd == "stop":
            res = stop_sprint(ms_dir, manual_words=args.words)
            if args.json:
                print(json.dumps(res, indent=2))
            else:
                print(f"🎉 Sprint Finished! Words: {res['words_written']:,} in {res['duration_minutes']}m ({res['wpm']:.1f} WPM, {res['completion_percentage']}% of goal)")
            return 0

        if cmd == "status":
            res = status_sprint(ms_dir)
            if args.json:
                print(json.dumps(res, indent=2))
            else:
                if res["status"] == "active":
                    print(f"⏱️  Active Sprint: {res['session_id']} | Elapsed: {res['elapsed_minutes']}m / {res['planned_duration_min']}m | Written: {res['words_written']}w ({res['instantaneous_wpm']} WPM)")
                else:
                    print("No active sprint session running. Run 'arcanum sprint start' to begin.")
            return 0

        if cmd == "cancel":
            res = cancel_sprint(ms_dir)
            if args.json:
                print(json.dumps(res, indent=2))
            else:
                print(res["message"])
            return 0

        if cmd == "log":
            res = log_manual_sprint(
                ms_dir,
                words=args.words,
                minutes=args.minutes,
                target_words=args.target,
                chapter=args.chapter,
            )
            if args.json:
                print(json.dumps(res, indent=2))
            else:
                print(f"✓ Sprint logged: {args.words:,} words in {args.minutes} min ({res['record']['wpm']} WPM)")
            return 0

        if cmd in ("stats", "report"):
            vel = get_velocity_metrics(ms_dir)
            html_out = getattr(args, "html", None)
            open_browser = getattr(args, "open", False)
            if not html_out and open_browser:
                html_out = "dist/velocity_studio.html"

            if html_out and render_velocity_html:
                # Import word counter data for rich studio
                try:
                    from lib.word_counter import analyze_manuscript_words
                    w_data = analyze_manuscript_words(ms_dir)
                except Exception:
                    w_data = {"title": "Manuscript", "total_words": vel.get("total_sprint_words", 0)}
                render_velocity_html(w_data, vel, html_out)
                print(f"✓ Standalone Velocity Studio written to: {html_out}")
                if open_browser:
                    import webbrowser
                    try:
                        webbrowser.open(Path(html_out).resolve().as_uri())
                    except Exception as exc:
                        print(f"Warning: Could not open browser: {exc}", file=sys.stderr)
                return 0

            if getattr(args, "json", False):
                print(json.dumps(vel, indent=2))
            elif getattr(args, "md", False):
                print(format_stats_markdown(vel))
            else:
                print(format_stats_table(vel))
            return 0

        parser.print_help()
        return 0

    except Exception as e:
        if getattr(args, "json", False):
            print(json.dumps({"status": "error", "error": str(e)}, indent=2))
        else:
            print(f"Error: {e}", file=sys.stderr)
        return 1


__all__ = [
    "cancel_sprint",
    "format_stats_markdown",
    "format_stats_table",
    "get_velocity_metrics",
    "log_manual_sprint",
    "main",
    "start_sprint",
    "status_sprint",
    "stop_sprint",
]

if __name__ == "__main__":
    sys.exit(main())
