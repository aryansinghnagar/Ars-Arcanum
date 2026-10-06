#!/usr/bin/env python3
"""
Ars Arcanum GTK3 Project Discovery & State Synchronization Mixin
(scripts/lib/ui_gtk3/discovery.py)
================================================================
Vault discovery, manuscript chapter telemetry, git history tracking,
toolchain verification badges, and draft selector refresh routines.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any

from .common import (
    HAS_GTK,
    MANUSCRIPTS_DIR,
    UNIVERSES_DIR,
    WORLDS_DIR,
    GLib,
    _cached_which,
    logger,
)


class ArcanumDiscoveryMixin:
    """Discovery and state synchronization methods for ArcanumApp window."""

    # Dynamic attributes injected by ArcanumApp / GTK widgets
    discovered_universes: list[str]
    discovered_worlds: list[tuple[str, str, str]]
    discovered_manuscripts: list[tuple[str, str, str]]
    current_universe: str | None
    current_world_path: str | None
    current_manuscript_path: str | None
    _world_lore_counts: dict[tuple[str, float], dict[str, int]]
    _git_history_cache: dict[tuple[str, float], list[str]]

    combo_universe: Any
    combo_world: Any
    combo_manuscript: Any

    def _async_refresh_all_discovery(self) -> None:
        """Run full discovery off the GTK main thread."""
        discovered_universes: list[str] = []
        if UNIVERSES_DIR.is_dir():
            for p in sorted(UNIVERSES_DIR.iterdir()):
                if p.is_dir() and not p.name.startswith("."):
                    discovered_universes.append(p.name)

        first_universe = discovered_universes[0] if discovered_universes else "Default-Universe"
        discovered_worlds: list[tuple[str, str, str]] = []
        u_dir = UNIVERSES_DIR / first_universe
        if u_dir.is_dir():
            for w in sorted(u_dir.iterdir()):
                if w.is_dir() and not w.name.startswith(".") and w.name not in ("Worlds", ".git"):
                    discovered_worlds.append((w.name, str(w), f"[{first_universe}] {w.name}"))
            u_worlds = u_dir / "Worlds"
            if u_worlds.is_dir():
                for w in sorted(u_worlds.iterdir()):
                    if w.is_dir() and not w.name.startswith("."):
                        discovered_worlds.append((w.name, str(w), f"[{first_universe}] {w.name}"))
        if WORLDS_DIR.is_dir():
            for w in sorted(WORLDS_DIR.iterdir()):
                if w.is_dir() and not w.name.startswith("."):
                    discovered_worlds.append((w.name, str(w), f"[Legacy] {w.name}"))

        discovered_manuscripts: list[tuple[str, str, str]] = []
        if MANUSCRIPTS_DIR.is_dir():
            for m in sorted(MANUSCRIPTS_DIR.iterdir()):
                if m.is_dir() and not m.name.startswith("."):
                    discovered_manuscripts.append((m.name, str(m), m.name))

        for tool in ("git", "pandoc", "typst", "python3"):
            _cached_which(tool)

        def _apply():
            self.discovered_universes = discovered_universes
            self.combo_universe.remove_all()
            if not discovered_universes:
                self.combo_universe.append("Default-Universe", "Default-Universe")
                self.current_universe = "Default-Universe"
            else:
                for name in discovered_universes:
                    self.combo_universe.append(name, name)
                if not self.current_universe or self.current_universe not in discovered_universes:
                    self.current_universe = discovered_universes[0]
                self.combo_universe.set_active_id(self.current_universe)

            self.discovered_worlds = discovered_worlds
            self.combo_world.remove_all()
            for _wname, wpath, label in discovered_worlds:
                self.combo_world.append(wpath, label)
            if discovered_worlds:
                self.combo_world.set_active(0)
                self.current_world_path = discovered_worlds[0][1]
            else:
                self.current_world_path = None

            self.discovered_manuscripts = discovered_manuscripts
            self.combo_manuscript.remove_all()
            for _mname, mpath, label in discovered_manuscripts:
                self.combo_manuscript.append(mpath, label)
            if discovered_manuscripts:
                self.combo_manuscript.set_active(0)
                self.current_manuscript_path = discovered_manuscripts[0][1]
            else:
                self.current_manuscript_path = None

            self.update_active_world_display()
            self.update_active_manuscript_display()
            self.update_toolchain_badges()
            self.check_first_run_wizard()

        if HAS_GTK and GLib is not None:
            GLib.idle_add(_apply)

    def refresh_all_discovery(self):
        """Synchronous discovery — used by explicit refresh button."""
        self.refresh_universes()
        self.refresh_worlds_for_universe()
        self.refresh_manuscripts()
        self.update_active_world_display()
        self.update_active_manuscript_display()
        self.update_toolchain_badges()

    def refresh_universes(self):
        self.discovered_universes = []
        self.combo_universe.remove_all()

        if UNIVERSES_DIR.is_dir():
            for p in sorted(UNIVERSES_DIR.iterdir()):
                if p.is_dir() and not p.name.startswith("."):
                    self.discovered_universes.append(p.name)
                    self.combo_universe.append(p.name, p.name)

        if not self.discovered_universes:
            self.combo_universe.append("Default-Universe", "Default-Universe")
            self.current_universe = "Default-Universe"
        else:
            if not self.current_universe or self.current_universe not in self.discovered_universes:
                self.current_universe = self.discovered_universes[0]
            self.combo_universe.set_active_id(self.current_universe)

    def refresh_worlds_for_universe(self):
        self.combo_world.remove_all()
        self.discovered_worlds = []

        if self.current_universe:
            u_dir = UNIVERSES_DIR / self.current_universe
            if u_dir.is_dir():
                for w in sorted(u_dir.iterdir()):
                    if w.is_dir() and not w.name.startswith(".") and w.name not in ("Worlds", ".git"):
                        self.discovered_worlds.append((w.name, str(w), f"[{self.current_universe}] {w.name}"))
                u_worlds = u_dir / "Worlds"
                if u_worlds.is_dir():
                    for w in sorted(u_worlds.iterdir()):
                        if w.is_dir() and not w.name.startswith("."):
                            self.discovered_worlds.append((w.name, str(w), f"[{self.current_universe}] {w.name}"))

        if WORLDS_DIR.is_dir():
            for w in sorted(WORLDS_DIR.iterdir()):
                if w.is_dir() and not w.name.startswith("."):
                    self.discovered_worlds.append((w.name, str(w), f"[Legacy] {w.name}"))

        for _wname, wpath, label in self.discovered_worlds:
            self.combo_world.append(wpath, label)

        if self.discovered_worlds:
            self.combo_world.set_active(0)
            self.current_world_path = self.discovered_worlds[0][1]
        else:
            self.current_world_path = None

    def refresh_manuscripts(self):
        self.combo_manuscript.remove_all()
        self.discovered_manuscripts = []

        if MANUSCRIPTS_DIR.is_dir():
            for m in sorted(MANUSCRIPTS_DIR.iterdir()):
                if m.is_dir() and not m.name.startswith("."):
                    self.discovered_manuscripts.append((m.name, str(m), m.name))

        for _mname, mpath, label in self.discovered_manuscripts:
            self.combo_manuscript.append(mpath, label)

        if self.discovered_manuscripts:
            self.combo_manuscript.set_active(0)
            self.current_manuscript_path = self.discovered_manuscripts[0][1]
        else:
            self.current_manuscript_path = None

    def on_universe_changed(self, combo):
        active_id = combo.get_active_id()
        if active_id and active_id != self.current_universe:
            self.current_universe = active_id
            self.refresh_worlds_for_universe()
            self.update_active_world_display()

    def on_world_changed(self, combo):
        active_id = combo.get_active_id()
        if active_id:
            self.current_world_path = active_id
            self.update_active_world_display()

    def on_manuscript_changed(self, combo):
        active_id = combo.get_active_id()
        if active_id:
            self.current_manuscript_path = active_id
            self.update_active_manuscript_display()

    def update_active_world_display(self):
        if self.current_world_path and Path(self.current_world_path).is_dir():
            wpath = Path(self.current_world_path)
            wname = wpath.name
            if hasattr(self, "lbl_cosmos_heading"):
                self.lbl_cosmos_heading.set_markup(f"<span size='large' weight='bold'>World Lore Vault: {wname}</span>")
                self.lbl_cosmos_path.set_text(str(wpath))
                self.lbl_lore_stats.set_text("Counting lore entities…")
            self.set_status(f"Active World: {wname}")

            def _count_lore():
                try:
                    vault_mtime = wpath.stat().st_mtime
                except OSError:
                    vault_mtime = 0.0
                cache_key = (str(wpath), vault_mtime)
                if cache_key in self._world_lore_counts:
                    counts = self._world_lore_counts[cache_key]
                else:
                    counts = {}
                    for folder in ("Characters", "Locations", "Factions", "Magic-Technology",
                                   "Bestiary", "Artifacts", "Cosmology", "History", "Languages"):
                        fdir = wpath / folder
                        if not fdir.is_dir() and (wpath / "00-World-Bible" / folder).is_dir():
                            fdir = wpath / "00-World-Bible" / folder
                        if fdir.is_dir():
                            c = len([f for f in fdir.rglob("*.md")
                                     if not f.name.startswith(".") and "Template" not in f.name])
                            counts[folder] = c
                        else:
                            counts[folder] = 0
                    self._world_lore_counts[cache_key] = counts

                stats_str = "  •  ".join([f"<b>{k}</b>: {v}" for k, v in counts.items()])
                if HAS_GTK and GLib is not None and hasattr(self, "lbl_lore_stats"):
                    GLib.idle_add(
                        self.lbl_lore_stats.set_markup,
                        f"<b>Registered Lore Entities:</b>\n{stats_str}"
                    )

            self._start_worker(_count_lore)
        else:
            if hasattr(self, "lbl_cosmos_heading"):
                self.lbl_cosmos_heading.set_markup("<span size='large' weight='bold'>No World Lore Selected</span>")
                self.lbl_cosmos_path.set_text("Create a new world lore vault to begin worldbuilding.")
                self.lbl_lore_stats.set_text("No world lore vault active.")

    def update_active_manuscript_display(self):
        if self.current_manuscript_path and Path(self.current_manuscript_path).is_dir():
            mpath = Path(self.current_manuscript_path)
            mname = mpath.name
            if hasattr(self, "entry_pub_title"):
                self.entry_pub_title.set_text(mname)
            self.refresh_volume_options()
            self.refresh_draft_selectors()
            self.refresh_manuscript_analytics()
            self.refresh_snapshot_history()
            self.update_secure_dest_display()
            self.set_status(f"Active Manuscript: {mname}")
        else:
            if hasattr(self, "card_total_words") and hasattr(self.card_total_words, "val_label"):
                self.card_total_words.val_label.set_text("0")
                self.card_chapters.val_label.set_text("0")
            if hasattr(self, "manuscript_store"):
                self.manuscript_store.clear()
            self.refresh_draft_selectors()
            self.update_secure_dest_display()

    def refresh_volume_options(self):
        if not hasattr(self, "combo_pub_volume") or self.combo_pub_volume is None:
            return
        self.combo_pub_volume.remove_all()
        target = self.current_manuscript_path or self.current_world_path
        if not target:
            return
        tpath = Path(target)
        ms_dir = tpath / "01-Manuscript" if (tpath / "01-Manuscript").is_dir() else tpath
        books = []
        if ms_dir.is_dir():
            for b in sorted(ms_dir.glob("Book-*")):
                if b.is_dir():
                    books.append(b.name)

        if books:
            for b in books:
                self.combo_pub_volume.append(b, f"Volume: {b}")
            if len(books) > 1:
                self.combo_pub_volume.append("all", "All Volumes (Omnibus)")
            self.combo_pub_volume.set_active(0)
        else:
            self.combo_pub_volume.append("Book-01", "Volume: Book-01")
            self.combo_pub_volume.set_active(0)

    def refresh_manuscript_analytics(self):
        if not hasattr(self, "manuscript_store"):
            return
        self.manuscript_store.clear()
        target = self.current_manuscript_path or self.current_world_path
        if not target:
            return

        if hasattr(self, "card_total_words") and hasattr(self.card_total_words, "val_label"):
            self.card_total_words.val_label.set_text("…")
            self.card_chapters.val_label.set_text("…")
        if HAS_GTK and GLib is not None:
            GLib.idle_add(self._show_progress)

        try:
            from lib.cache import count_words as _canonical_count
        except Exception:
            _FM = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

            def _canonical_count(text: str) -> int:
                clean = _FM.sub("", text)
                clean = re.sub(r"```.*?```", "", clean, flags=re.DOTALL)
                kept = [ln for ln in clean.splitlines()
                        if ln.strip() and not (ln.strip().startswith("@") and re.match(r"^@[A-Za-z0-9_-]+:", ln.strip())) and not ln.strip().startswith("%")]
                return len(re.findall(r"\b\w+\b", "\n".join(kept), flags=re.UNICODE))

        tpath = Path(target)
        ms_dir = tpath / "01-Manuscript" if (tpath / "01-Manuscript").is_dir() else tpath

        def _worker():
            rows: list[tuple] = []
            total_words = 0
            total_chapters = 0

            if ms_dir.is_dir():
                for book_dir in sorted(ms_dir.glob("Book-*")):
                    if not book_dir.is_dir():
                        continue
                    book_words = 0
                    book_key = book_dir.name
                    rows.append(("book", None, book_key, book_dir.name, "Volume", 0, str(book_dir)))

                    draft_dirs = sorted([d for d in book_dir.glob("Draft-*") if d.is_dir()])
                    if draft_dirs:
                        for draft_dir in draft_dirs:
                            d_words = 0
                            d_key = f"{book_key}/{draft_dir.name}"
                            rows.append(("draft", book_key, d_key, draft_dir.name, "Draft Version", 0, str(draft_dir)))
                            for sub in sorted(draft_dir.iterdir()):
                                if sub.is_dir() and not sub.name.startswith("."):
                                    act_words = 0
                                    a_key = f"{d_key}/{sub.name}"
                                    rows.append(("act", d_key, a_key, sub.name, "Act / Section", 0, str(sub)))
                                    for ch_file in sorted(sub.glob("*.md")):
                                        if ch_file.is_file() and not ch_file.name.startswith("."):
                                            try:
                                                content = ch_file.read_text(encoding="utf-8", errors="replace")
                                                wc = _canonical_count(content)
                                                act_words += wc
                                                total_chapters += 1
                                                rows.append(("ch", a_key, None, ch_file.name, "Scene / Chapter", wc, str(ch_file)))
                                            except Exception as ex:
                                                logger.warning("Error counting %s: %s", ch_file, ex)
                                    for i, r in enumerate(rows):
                                        if r[2] == a_key:
                                            rows[i] = (r[0], r[1], r[2], r[3], r[4], act_words, r[6])
                                    d_words += act_words
                            for i, r in enumerate(rows):
                                if r[2] == d_key:
                                    rows[i] = (r[0], r[1], r[2], r[3], r[4], d_words, r[6])
                            book_words += d_words
                    else:
                        for act_dir in sorted(book_dir.iterdir()):
                            if act_dir.is_dir() and not act_dir.name.startswith(".") and act_dir.name != "Outlines":
                                act_words = 0
                                a_key = f"{book_key}/{act_dir.name}"
                                rows.append(("act", book_key, a_key, act_dir.name, "Act / Section", 0, str(act_dir)))
                                for ch_file in sorted(act_dir.glob("*.md")):
                                    if ch_file.is_file() and not ch_file.name.startswith("."):
                                        try:
                                            content = ch_file.read_text(encoding="utf-8", errors="replace")
                                            wc = _canonical_count(content)
                                            act_words += wc
                                            total_chapters += 1
                                            rows.append(("ch", a_key, None, ch_file.name, "Scene / Chapter", wc, str(ch_file)))
                                        except Exception as ex:
                                            logger.warning("Error counting %s: %s", ch_file, ex)
                                for i, r in enumerate(rows):
                                    if r[2] == a_key:
                                        rows[i] = (r[0], r[1], r[2], r[3], r[4], act_words, r[6])
                                book_words += act_words
                    for i, r in enumerate(rows):
                        if r[2] == book_key:
                            rows[i] = (r[0], r[1], r[2], r[3], r[4], book_words, r[6])
                    total_words += book_words

            def _apply():
                self.manuscript_store.clear()
                iter_map: dict[str, object] = {}
                for _level, parent_key, key, item, type_, wc, filepath in rows:
                    parent_iter = iter_map.get(parent_key) if parent_key else None
                    wc_str = f"{wc:,} words" if wc else ""
                    it = self.manuscript_store.append(parent_iter, [item, type_, wc_str, filepath])
                    if key:
                        iter_map[key] = it
                if hasattr(self, "card_total_words") and hasattr(self.card_total_words, "val_label"):
                    self.card_total_words.val_label.set_text(f"{total_words:,}")
                    self.card_chapters.val_label.set_text(str(total_chapters))
                if hasattr(self, "manuscript_tree"):
                    self.manuscript_tree.expand_all()
                self._hide_progress()

            if HAS_GTK and GLib is not None:
                GLib.idle_add(_apply)

        self._start_worker(_worker)

    def refresh_snapshot_history(self):
        if not hasattr(self, "history_store"):
            return
        self.history_store.clear()
        target = self.current_manuscript_path or self.current_world_path
        if not target:
            return
        wpath = Path(target)
        git_dir = wpath / ".git"
        if not git_dir.is_dir():
            return

        head_file = git_dir / "HEAD"
        try:
            head_mtime = head_file.stat().st_mtime if head_file.exists() else 0.0
        except OSError:
            head_mtime = 0.0
        cache_key = (str(wpath), head_mtime)

        if cache_key in self._git_history_cache:
            lines = self._git_history_cache[cache_key]
        else:
            try:
                res = subprocess.run(
                    ["git", "-C", str(wpath), "log", "-n", "15",
                     "--pretty=format:%h|%ad|%s", "--date=short"],
                    capture_output=True, text=True, check=True, timeout=15
                )
                lines = res.stdout.splitlines()
                self._git_history_cache[cache_key] = lines
            except Exception as e:
                logger.debug("Could not fetch git history: %s", e)
                lines = []

        for line in lines:
            parts = line.split("|", 2)
            if len(parts) == 3:
                self.history_store.append([parts[0], parts[1], parts[2]])

    def update_toolchain_badges(self):
        if not hasattr(self, "lbl_tool_git"):
            return
        tools = [
            ("git", self.lbl_tool_git),
            ("pandoc", self.lbl_tool_pandoc),
            ("typst", self.lbl_tool_typst),
            ("python3", self.lbl_tool_python),
        ]
        for cmd, badge in tools:
            path = _cached_which(cmd)
            if path:
                badge.status_label.set_markup("<span color='#2e7d32'><b>✓ Installed</b></span>")
            else:
                badge.status_label.set_markup("<span color='#d32f2f'><b>✗ Missing</b></span>")

    def refresh_draft_selectors(self):
        if not hasattr(self, "combo_draft_vol") or self.combo_draft_vol is None:
            return

        target = self.current_manuscript_path
        if not target or not Path(target).is_dir():
            self.combo_draft_vol.remove_all()
            self.combo_draft_list.remove_all()
            self.combo_diff_a.remove_all()
            self.combo_diff_b.remove_all()
            return

        tpath = Path(target)
        cur_vol = self.combo_draft_vol.get_active_id()
        self.combo_draft_vol.remove_all()
        volumes = [b.name for b in sorted(tpath.glob("Book-*")) if b.is_dir()]
        if not volumes:
            volumes = ["Book-01"]
        for v in volumes:
            self.combo_draft_vol.append(v, v)

        if cur_vol and cur_vol in volumes:
            self.combo_draft_vol.set_active_id(cur_vol)
        else:
            self.combo_draft_vol.set_active(0)

        active_vol = self.combo_draft_vol.get_active_id() or "Book-01"
        book_dir = tpath / active_vol

        drafts = []
        if book_dir.is_dir():
            for d in sorted(book_dir.glob("Draft-*")):
                if d.is_dir():
                    drafts.append(d.name)
        if not drafts and book_dir.is_dir():
            has_divisions = any(d.is_dir() and bool(re.match(r"^\d{2}_", d.name)) for d in book_dir.iterdir())
            if has_divisions or (book_dir / "01_Act_I").is_dir():
                drafts = ["Draft-01 (Baseline)"]

        self.combo_draft_list.remove_all()
        self.combo_diff_a.remove_all()
        self.combo_diff_b.remove_all()

        for d in drafts:
            self.combo_draft_list.append(d, d)
            self.combo_diff_a.append(d, d)
            self.combo_diff_b.append(d, d)

        if drafts:
            self.combo_draft_list.set_active(len(drafts) - 1)
            self.combo_diff_b.set_active(len(drafts) - 1)
            self.combo_diff_a.set_active(0)


__all__ = ["ArcanumDiscoveryMixin"]
