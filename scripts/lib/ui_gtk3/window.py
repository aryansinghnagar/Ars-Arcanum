#!/usr/bin/env python3
"""
Ars Arcanum GTK 3 Main Window & Application Controller (scripts/lib/ui_gtk3/window.py)
====================================================================================
Modular desktop window coordinating 6 workflow studios, project selectors,
accelerator keymaps, and lifecycle event orchestration.
"""

import logging
import subprocess
import sys
import threading

from lib.ui_gtk3.common import (
    HAS_GTK,
    HOME_DIR,
    PROJECT_ROOT,
    DialogHelpersMixin,
    Gdk,
    GLib,
    Gtk,
    setup_styles,
    toggle_high_contrast,
)
from lib.ui_gtk3.dialogs import SpeculativeDialogsMixin
from lib.ui_gtk3.discovery import ArcanumDiscoveryMixin
from lib.ui_gtk3.studios.cosmos import CosmosStudioMixin
from lib.ui_gtk3.studios.diagnostics import DiagnosticsStudioMixin
from lib.ui_gtk3.studios.drafting import DraftingStudioMixin
from lib.ui_gtk3.studios.publishing import PublishingStudioMixin
from lib.ui_gtk3.studios.safety import SafetyStudioMixin
from lib.ui_gtk3.studios.speculative import SpeculativeStudioMixin
from lib.ui_gtk3.workers import WorkerMixin

try:
    from lib.tips import are_tips_enabled, get_tip_database
except ImportError:
    try:
        from tips import are_tips_enabled, get_tip_database
    except ImportError:
        def are_tips_enabled() -> bool:
            return True

        def get_tip_database():
            return None

logger = logging.getLogger("arcanum.ui_gtk3.window")


class ArcanumApp(
    Gtk.Window,
    WorkerMixin,
    DialogHelpersMixin,
    ArcanumDiscoveryMixin,
    CosmosStudioMixin,
    DraftingStudioMixin,
    SpeculativeStudioMixin,
    PublishingStudioMixin,
    SafetyStudioMixin,
    DiagnosticsStudioMixin,
    SpeculativeDialogsMixin,
):
    """Main Ars Arcanum GTK 3 desktop application window."""

    def __init__(self, active_tab: str | None = None):
        if HAS_GTK and hasattr(Gtk.Window, "__init__"):
            super().__init__(title="Ars Arcanum — Sovereign Author & Worldbuilder Studio")
            self.set_default_size(1080, 740)
            if hasattr(Gtk, "WindowPosition"):
                self.set_position(Gtk.WindowPosition.CENTER)

        # Apply basic modern styling
        self.setup_styles()

        self.current_universe = None
        self.current_world_path = None
        self.current_manuscript_path = None
        self.current_selected_scene_file = None

        self.discovered_universes: list[str] = []
        self.discovered_worlds: list[tuple[str, str, str]] = []
        self.discovered_manuscripts: list[tuple[str, str, str]] = []

        self.combo_draft_vol = None
        self.combo_draft_list = None
        self.combo_diff_a = None
        self.combo_diff_b = None
        self.lbl_secure_dest = None
        self.entry_scope_ch = None
        self.entry_scope_sc = None

        self._world_lore_counts: dict = {}
        self._dialog_cache: dict = {}
        self._git_history_cache: dict = {}
        self._pulse_timer_id = None
        self._first_run_wizard_shown = False
        self._high_contrast_active = False

        if not HAS_GTK:
            return

        # Main vertical container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(main_box)

        # Header Bar
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.props.title = "Ars Arcanum"
        header.props.subtitle = "Sovereign Writing & Worldbuilding Studio"
        self.set_titlebar(header)

        # Quick Snapshot button in HeaderBar
        snap_btn = Gtk.Button(label="📷 Quick Snapshot")
        if hasattr(snap_btn, "get_style_context"):
            snap_btn.get_style_context().add_class("suggested-action")
        snap_btn.set_tooltip_text("Record a 1-click Git version milestone (Ctrl+S)")
        snap_btn.connect("clicked", self.on_quick_snapshot_clicked)
        header.pack_end(snap_btn)

        # Accessibility High-Contrast Toggle Button
        contrast_btn = Gtk.Button(label="👁️ High Contrast")
        contrast_btn.set_tooltip_text("Toggle high-contrast accessibility theme (Ctrl+H)")
        contrast_btn.connect("clicked", self.on_toggle_high_contrast_clicked)
        header.pack_end(contrast_btn)

        # Manual / Help button
        help_btn = Gtk.Button(label="📖 Field Manual")
        help_btn.set_tooltip_text("Open the Ars Arcanum Author's Field Manual (F1)")
        help_btn.connect("clicked", self.on_open_manual_clicked)
        header.pack_end(help_btn)

        # Top Project Selector Bar
        selector_bar = self.create_selector_bar()
        main_box.pack_start(selector_bar, False, False, 0)

        # 6-Studio Workspace Notebook
        self.notebook = Gtk.Notebook()
        self.notebook.set_tab_pos(Gtk.PositionType.TOP)
        main_box.pack_start(self.notebook, True, True, 0)

        # Create the 6 primary workflow studios
        self.tab_cosmos = self.create_cosmos_tab()
        self.tab_manuscript = self.create_manuscript_tab()
        self.tab_speculative = self.create_speculative_tab()
        self.tab_publishing = self.create_publishing_tab()
        self.tab_safety = self.create_safety_tab()
        self.tab_doctor = self.create_doctor_tab()

        self.notebook.append_page(self.tab_cosmos, Gtk.Label(label="🪐 Cosmos & Worlds"))
        self.notebook.append_page(self.tab_manuscript, Gtk.Label(label="✍️ Manuscripts & Drafting"))
        self.notebook.append_page(self.tab_speculative, Gtk.Label(label="🔮 Speculative Studio"))
        self.notebook.append_page(self.tab_publishing, Gtk.Label(label="📚 Publishing & Exports"))
        self.notebook.append_page(self.tab_safety, Gtk.Label(label="🔒 Snapshots & Backups"))
        self.notebook.append_page(self.tab_doctor, Gtk.Label(label="🩺 Diagnostics & Doctor"))
        self.notebook.connect("switch-page", self._on_notebook_switch_page)

        if active_tab:
            tab_clean = active_tab.lower().strip()
            tab_map = {
                "cosmos": 0, "universe": 0, "universes": 0, "world": 0, "worlds": 0,
                "drafting": 1, "manuscript": 1, "manuscripts": 1, "novel": 1, "writing": 1, "write": 1,
                "comparator": 1, "diff": 1, "compare": 1, "redline": 1,
                "worldbuilding": 2, "speculative": 2, "engines": 2, "lore": 2, "magic": 2,
                "publishing": 3, "typesetting": 3, "export": 3, "publish": 3,
                "safety": 4, "backups": 4, "snapshots": 4, "backup": 4, "snapshot": 4, "git": 4,
                "doctor": 5, "diagnostics": 5, "health": 5, "check": 5
            }
            if tab_clean in tab_map:
                self.notebook.set_current_page(tab_map[tab_clean])

        # Bottom bar with status + pulse progress bar for long ops
        bottom_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.statusbar = Gtk.Statusbar()
        self.status_context = self.statusbar.get_context_id("main")
        bottom_bar.pack_start(self.statusbar, True, True, 0)

        self._progress_bar = Gtk.ProgressBar()
        self._progress_bar.set_pulse_step(0.05)
        self._progress_bar.set_no_show_all(True)
        bottom_bar.pack_start(self._progress_bar, False, False, 0)
        main_box.pack_start(bottom_bar, False, False, 0)

        # Setup keyboard accelerators
        self.setup_accelerators()

        # Run discovery off GTK main thread so startup is instant
        self._start_worker(self._async_refresh_all_discovery)
        self.check_first_run()

    def setup_styles(self, high_contrast: bool = False):
        setup_styles(high_contrast=high_contrast)

    def setup_accelerators(self):
        """Installs standard keyboard shortcuts (Ctrl+N, Ctrl+S, Ctrl+E, Ctrl+B, F1, Ctrl+H, Ctrl+R)."""
        if not HAS_GTK or Gdk is None:
            return
        accel_group = Gtk.AccelGroup()
        self.add_accel_group(accel_group)

        # Helper to bind key combinations
        def _add_accel(key_val, mod_mask, callback):
            accel_group.connect(key_val, mod_mask, Gtk.AccelFlags.VISIBLE, lambda *args: callback(None))

        # Ctrl+N -> New Manuscript
        _add_accel(Gdk.KEY_n, Gdk.ModifierType.CONTROL_MASK, self.on_new_manuscript_clicked)
        # Ctrl+S -> Quick Snapshot
        _add_accel(Gdk.KEY_s, Gdk.ModifierType.CONTROL_MASK, self.on_quick_snapshot_clicked)
        # Ctrl+E -> Compile Book
        _add_accel(Gdk.KEY_e, Gdk.ModifierType.CONTROL_MASK, self.on_compile_clicked)
        # Ctrl+B -> Standalone Backup
        _add_accel(Gdk.KEY_b, Gdk.ModifierType.CONTROL_MASK, self.on_create_backup_clicked)
        # F1 -> Author's Field Manual
        _add_accel(Gdk.KEY_F1, Gdk.ModifierType(0), self.on_open_manual_clicked)
        # Ctrl+H -> High Contrast Mode Toggle
        _add_accel(Gdk.KEY_h, Gdk.ModifierType.CONTROL_MASK, self.on_toggle_high_contrast_clicked)
        # Ctrl+R -> Refresh Discovery
        _add_accel(Gdk.KEY_r, Gdk.ModifierType.CONTROL_MASK, lambda b: self.refresh_all_discovery())

    def on_toggle_high_contrast_clicked(self, btn=None):
        new_state = toggle_high_contrast()
        self._high_contrast_active = new_state
        self.set_status(f"High Contrast Mode {'Enabled' if new_state else 'Disabled'}")

    def set_status(self, message):
        if not hasattr(self, "statusbar") or self.statusbar is None:
            return
        self.statusbar.pop(self.status_context)
        self.statusbar.push(self.status_context, message)

    def _on_notebook_switch_page(self, notebook, page, page_num: int):
        """Displays a non-intrusive contextual craft wisdom tip in statusbar when navigating studios."""
        try:
            if not are_tips_enabled():
                return
            db = get_tip_database()
            if not db:
                return
            context_map = {
                0: ("cosmos", "cartography"),
                1: ("drafting", "structure"),
                2: ("worldbuilding", "magic_system"),
                3: ("publishing", "codex_export"),
                4: ("safety", "fs_utils"),
                5: ("diagnostics", "world_doctor"),
            }
            ctx, eng = context_map.get(page_num, ("drafting", "structure"))
            tip = db.get_contextual_tip(engine=eng, context=ctx)
            if tip:
                self.set_status(f"💡 [{tip.engine.upper()}]: {tip.title} — {tip.content}")
        except Exception as e:
            logger.debug("Failed displaying contextual status tip: %s", e)

    def create_selector_bar(self):
        bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        bar.set_border_width(8)
        bar.get_style_context().add_class("card-box")

        # 1. Universe Selector
        lbl_uni = Gtk.Label(label="<b>Universe:</b>", use_markup=True)
        bar.pack_start(lbl_uni, False, False, 0)

        self.combo_universe = Gtk.ComboBoxText()
        self.combo_universe.connect("changed", self.on_universe_changed)
        bar.pack_start(self.combo_universe, False, False, 0)

        btn_new_uni = Gtk.Button(label="+ Universe")
        btn_new_uni.connect("clicked", self.on_new_universe_clicked)
        bar.pack_start(btn_new_uni, False, False, 0)

        bar.pack_start(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL), False, False, 4)

        # 2. World Lore Vault Selector
        lbl_world = Gtk.Label(label="<b>World Lore:</b>", use_markup=True)
        bar.pack_start(lbl_world, False, False, 0)

        self.combo_world = Gtk.ComboBoxText()
        self.combo_world.connect("changed", self.on_world_changed)
        bar.pack_start(self.combo_world, True, True, 0)

        btn_new_world = Gtk.Button(label="+ World")
        btn_new_world.connect("clicked", self.on_new_world_clicked)
        bar.pack_start(btn_new_world, False, False, 0)

        bar.pack_start(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL), False, False, 4)

        # 3. Manuscript Project Selector
        lbl_ms = Gtk.Label(label="<b>Manuscript:</b>", use_markup=True)
        bar.pack_start(lbl_ms, False, False, 0)

        self.combo_manuscript = Gtk.ComboBoxText()
        self.combo_manuscript.connect("changed", self.on_manuscript_changed)
        bar.pack_start(self.combo_manuscript, True, True, 0)

        btn_new_ms = Gtk.Button(label="+ Manuscript")
        btn_new_ms.get_style_context().add_class("suggested-action")
        btn_new_ms.connect("clicked", self.on_new_manuscript_clicked)
        bar.pack_start(btn_new_ms, False, False, 0)

        bar.pack_start(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL), False, False, 4)

        # 4. Scope Targeting (Chapters & Scenes)
        lbl_scope_ch = Gtk.Label(label="<b>Ch:</b>", use_markup=True)
        bar.pack_start(lbl_scope_ch, False, False, 0)

        self.entry_scope_ch = Gtk.Entry()
        self.entry_scope_ch.set_placeholder_text("1-5, 8")
        self.entry_scope_ch.set_width_chars(7)
        self.entry_scope_ch.set_tooltip_text("Filter target chapters: e.g. 1-5, 8, 10-12 or ch01..ch05")
        bar.pack_start(self.entry_scope_ch, False, False, 0)

        lbl_scope_sc = Gtk.Label(label="<b>Sc:</b>", use_markup=True)
        bar.pack_start(lbl_scope_sc, False, False, 0)

        self.entry_scope_sc = Gtk.Entry()
        self.entry_scope_sc.set_placeholder_text("1-3")
        self.entry_scope_sc.set_width_chars(5)
        self.entry_scope_sc.set_tooltip_text("Filter target scenes within chapters: e.g. 1-4 or sc01..sc03")
        bar.pack_start(self.entry_scope_sc, False, False, 0)

        btn_refresh = Gtk.Button(label="🔄")
        btn_refresh.set_tooltip_text("Refresh discovered universes, worlds, and manuscripts (Ctrl+R)")
        btn_refresh.connect("clicked", lambda b: self.refresh_all_discovery())
        bar.pack_start(btn_refresh, False, False, 0)

        return bar

    def get_current_scope_args(self) -> list[str]:
        """Returns active scope CLI arguments based on selector bar state."""
        args: list[str] = []
        if hasattr(self, "entry_scope_ch") and self.entry_scope_ch:
            ch = self.entry_scope_ch.get_text().strip()
            if ch:
                args.extend(["--chapters", ch])
        if hasattr(self, "entry_scope_sc") and self.entry_scope_sc:
            sc = self.entry_scope_sc.get_text().strip()
            if sc:
                args.extend(["--scenes", sc])
        return args

    def check_first_run(self):
        flag_file = HOME_DIR / ".config" / "arcanum" / "first_run_done"
        if not flag_file.is_file() and not self.discovered_worlds and not self.discovered_manuscripts and HAS_GTK and GLib is not None:
            GLib.idle_add(self.show_welcome_dialog, flag_file)

    def check_first_run_wizard(self):
        if getattr(self, "_first_run_wizard_shown", False):
            return
        self._first_run_wizard_shown = True
        has_projects = bool(self.discovered_worlds or self.discovered_manuscripts)
        if not has_projects and HAS_GTK:
            dialog = Gtk.Dialog(title="Welcome to Ars Arcanum", parent=self, flags=0)
            dialog.set_default_size(520, 320)
            box = dialog.get_content_area()
            box.set_border_width(16)
            box.set_spacing(12)

            lbl_title = Gtk.Label()
            lbl_title.set_markup("<span size='large' weight='bold'>Welcome to Ars Arcanum Studio!</span>")
            lbl_title.set_xalign(0)
            box.pack_start(lbl_title, False, False, 0)

            lbl_desc = Gtk.Label(label="Ars Arcanum is your sovereign writing, worldbuilding, and publishing platform.\nHow would you like to begin?")
            lbl_desc.set_xalign(0)
            lbl_desc.set_line_wrap(True)
            box.pack_start(lbl_desc, False, False, 0)

            btn_demo = Gtk.Button(label="✨  Generate Sample Cosmos (Recommended)\nExplore a pre-configured fantasy cosmos with lore, characters & starter chapters")
            btn_demo.get_style_context().add_class("suggested-action")
            btn_demo.connect("clicked", lambda b: (dialog.response(Gtk.ResponseType.YES), dialog.destroy(), self.on_generate_demo_clicked(None)))
            box.pack_start(btn_demo, False, False, 4)

            btn_new = Gtk.Button(label="➕  Create Fresh Project\nStart a new blank Universe, World Lore Vault, or Manuscript")
            btn_new.connect("clicked", lambda b: (dialog.response(Gtk.ResponseType.OK), dialog.destroy(), self.on_new_universe_clicked(None)))
            box.pack_start(btn_new, False, False, 4)

            btn_skip = Gtk.Button(label="Skip / Explore Interface")
            btn_skip.connect("clicked", lambda b: (dialog.response(Gtk.ResponseType.CANCEL), dialog.destroy()))
            box.pack_start(btn_skip, False, False, 4)

            dialog.show_all()

    def show_welcome_dialog(self, flag_file=None):
        if not HAS_GTK:
            return
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Welcome to Ars Arcanum!"
        )
        dialog.format_secondary_text(
            "Ars Arcanum is your private, local-first writing and worldbuilding studio.\n\n"
            "• Tab 1 (Universes & Worlds): Manage Obsidian World Lore Vaults directly.\n"
            "• Tab 2 (Manuscripts & Drafting): Organize scenes and inspect/write @pov, @char, @location, @thread, and @status tags visually.\n"
            "• Tab 3 (Publishing & Exports): Compile trade-quality print PDFs, EPUBs, and DOCX submission manuscripts.\n"
            "• Click '📖 Field Manual' (F1) in the top right anytime for complete guides.\n\n"
            "Happy Writing!"
        )
        dialog.run()
        dialog.destroy()
        if flag_file:
            try:
                flag_file.parent.mkdir(parents=True, exist_ok=True)
                flag_file.write_text("done\n", encoding="utf-8")
            except Exception:
                pass

    def on_open_manual_clicked(self, btn=None):
        manual_path = PROJECT_ROOT / "docs" / "AUTHOR_MANUAL.md"
        if manual_path.is_file():
            self._launch_detached(["xdg-open", str(manual_path)])
        else:
            self.show_error("Author's Field Manual not found.")

    def show_error(self, message):
        if not HAS_GTK:
            print(f"[Error] {message}", file=sys.stderr)
            return
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.OK,
            text=message
        )
        dialog.run()
        dialog.destroy()

    @staticmethod
    def _stream_process_to_log(proc, buffer_obj, append_fn, chunk_lines=50):
        buf = []
        try:
            for line in proc.stdout or []:
                buf.append(line)
                if len(buf) >= chunk_lines:
                    if HAS_GTK and GLib is not None:
                        GLib.idle_add(append_fn, buffer_obj, "".join(buf))
                    buf = []
        finally:
            if buf and HAS_GTK and GLib is not None:
                GLib.idle_add(append_fn, buffer_obj, "".join(buf))

    @staticmethod
    def _launch_detached(argv):
        try:
            proc = subprocess.Popen(
                list(argv),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                start_new_session=True,
            )
        except Exception as e:
            logger.warning("Failed to launch %s: %s", argv, e)
            return None

        def _reap():
            try:
                rc = proc.wait(timeout=30)
                if rc != 0:
                    logger.warning("Launcher %s exited with code %s", argv, rc)
            except Exception as e:
                logger.warning("Launcher %s wait failed: %s", argv, e)

        threading.Thread(target=_reap, daemon=True).start()
        return proc

    def _run_async_command(self, cmd, success_msg, callback=None, timeout=120):
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            if HAS_GTK and GLib is not None:
                GLib.idle_add(self.set_status, "Error: command timed out.")
            return
        if HAS_GTK and GLib is not None:
            if res.returncode == 0:
                GLib.idle_add(self.set_status, success_msg)
            else:
                GLib.idle_add(self.set_status, f"Error: {res.stderr.strip() or 'Command failed'}")
            if callback:
                GLib.idle_add(callback)


# Compatibility alias
ScriptoriumApp = ArcanumApp


def run_gtk3_app(active_tab: str | None = None):
    """Entry point for launching the GTK 3 desktop application."""
    if not HAS_GTK:
        return False
    app = ArcanumApp(active_tab=active_tab)
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()
    return True


def main():
    """Main CLI entry point for standalone GTK 3 execution."""
    if not HAS_GTK:
        print("[!] PyGObject / GTK 3 is not installed in the current Python environment.", file=sys.stderr)
        print("[i] Falling back to Zenity desktop control dashboard...", file=sys.stderr)
        sys.exit(2)

    run_gtk3_app()


if __name__ == "__main__":
    main()
