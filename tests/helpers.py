#!/usr/bin/env python3
"""
Ars Arcanum Test Fixture Helpers (tests/helpers.py)
===================================================
Shared test fixture generator utilities supporting pluggable structure presets.
"""

from collections.abc import Sequence
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

from lib._bootstrap import atomic_write


def scaffold_volume_simple(
    vol_dir: Path,
    structure_key: str = "three_act",
    custom_divisions: list[str] | None = None,
) -> list[Path]:
    """Helper to create division directories."""
    if custom_divisions:
        div_names = custom_divisions
    elif structure_key == "three_act":
        div_names = ["01_Act_I", "02_Act_II", "03_Act_III"]
    elif structure_key == "five_act":
        div_names = ["01_Exposition", "02_Rising_Action", "03_Climax", "04_Falling_Action", "05_Denouement"]
    else:
        div_names = ["01_Chapters"]

    div_dirs = []
    for d_name in div_names:
        d_path = vol_dir / d_name
        d_path.mkdir(parents=True, exist_ok=True)
        div_dirs.append(d_path)
    return div_dirs


def create_test_volume(
    ms_dir: Path,
    vol_name: str = "Book-01",
    structure: str = "three_act",
    custom_divisions: list[str] | None = None,
    chapters_per_division: int = 1,
    words_per_chapter: int = 100,
) -> Path:
    """Create a volume inside a manuscript with the specified structure."""
    vol_dir = ms_dir / vol_name
    vol_dir.mkdir(parents=True, exist_ok=True)
    (vol_dir / "04_Back_Matter").mkdir(exist_ok=True)

    div_dirs = scaffold_volume_simple(
        vol_dir,
        structure_key=structure,
        custom_divisions=custom_divisions,
    )

    for div_dir in div_dirs:
        for ch in range(1, chapters_per_division + 1):
            ch_file = div_dir / f"{ch:02d}_Chapter_{ch:02d}.md"
            words = ("word " * words_per_chapter).strip()
            content = f"# Chapter {ch}\n\n{words}\n"
            atomic_write(ch_file, content)

    return vol_dir


def create_test_manuscript(
    root: Path,
    name: str = "Test-Novel",
    structure: str = "three_act",
    custom_divisions: list[str] | None = None,
    volumes: Sequence[str] = ("Book-01",),
    chapters_per_division: int = 1,
    words_per_chapter: int = 100,
    author: str = "Test Author",
    universe: str = "Default-Universe",
    world: str = "",
) -> Path:
    """Create a test manuscript directory with the given structure."""
    ms_dir = root / name
    ms_dir.mkdir(parents=True, exist_ok=True)
    (ms_dir / "03-Art").mkdir(exist_ok=True)
    (ms_dir / "04-Publishing").mkdir(exist_ok=True)
    (ms_dir / "05-Backups").mkdir(exist_ok=True)

    manifest_lines = [
        "---",
        f"title: \"{name}\"",
        f"author: \"{author}\"",
        f"universe: \"{universe}\"",
        f"world: \"{world}\"",
        f"structure: \"{structure}\"",
        "language: \"en\"",
        "---",
    ]
    if custom_divisions:
        manifest_lines.append("custom_divisions:")
        for div in custom_divisions:
            manifest_lines.append(f"  - \"{div}\"")

    atomic_write(ms_dir / "manuscript.yaml", "\n".join(manifest_lines) + "\n")

    for vol in volumes:
        create_test_volume(
            ms_dir=ms_dir,
            vol_name=vol,
            structure=structure,
            custom_divisions=custom_divisions,
            chapters_per_division=chapters_per_division,
            words_per_chapter=words_per_chapter,
        )

    return ms_dir
