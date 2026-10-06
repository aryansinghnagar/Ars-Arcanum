# Ars Arcanum Agent & Developer Governance Instructions

> **Canonical commands, verification gates, exit-code contracts, branching doctrines, and invariant rules for working on Ars Arcanum.**

---

## 1. Project Invariants (Non-Negotiable)

1. **Plain Text & Open Formats First**: All lore, character dossiers, outlines, and manuscript scenes are stored in standard Markdown (`.md`), YAML manifests (`.yaml`), or novelWriter XML (`.nwx`). Never introduce proprietary database formats or mandatory cloud dependencies.
2. **Separated Universe-Lore-Manuscript Architecture**:
   - Universes: `~/Universes/<UniverseName>/` (`universe.yaml` + Git repository).
   - World Lore Vaults: `~/Universes/<UniverseName>/<WorldName>/` (Pure Obsidian Vault + Git repository).
   - Prose Manuscripts: `~/Manuscripts/<ManuscriptName>/` (`manuscript.yaml` + `Book-*` acts + Git repository).
3. **Safe Path Handling & Quoting**: All shell scripts must quote variable expansions (`"$VAR"`) and handle whitespace/special characters safely. NUL-delimited streams (`find -print0`) are used for batch processing.
4. **Transactional Staging**: Directory creation, backup extraction, and file generation must stage in temporary directories (`mktemp -d`) with trap cleanups (`trap cleanup EXIT INT TERM`).
5. **Fail-Closed Security**: Verification and binary installations must fail closed (`TYPST_OK=0`) when digests or dependencies are unavailable.

---

## 2. Exit-Code Contract

All scripts and the CLI facade (`scripts/arcanum`) adhere strictly to this 4-value contract:

| Exit Code | Semantics | Description |
| :---: | :--- | :--- |
| `0` | **Success** | Operation completed cleanly without errors. |
| `1` | **Runtime / Diagnostic Failure** | Execution failed, or diagnostic check identified integrity issues (e.g. broken links, invalid schemas). |
| `2` | **Usage / Environment Error** | Bad arguments, unknown options, unresolvable paths, or unsupported OS. |
| `3` | **Nothing to Act On** | Clean working tree (no changes to snapshot), required argument missing in headless mode, or user aborted dialog. |

---

## 3. Canonical Commands & Quality Gate

Every proposed change MUST pass the full quality gate in this exact order before opening or merging a pull request:

```bash
# 1. Full Python Unit & Integration Test Suite (853 tests, 0 failures allowed)
python -m unittest discover tests

# 2. Strict Expanded Ruff Linter Pass (0 violations allowed)
ruff check .

# 3. Strict Mypy Static Type Checking across all source files (167 files clean)
mypy --config-file mypy.ini --explicit-package-bases scripts/lib tests

# 4. Canonical 7-Stage Integration Verification Harness
bash scripts/verify.sh
```

---

## 4. Subsystem, Discovery & Scoping Guidelines

- **Centralized Discovery & Scoping**: Never implement bespoke filesystem scanning or recursive disk crawling. Always utilize [`scripts/lib/scope.py`](file:///scripts/lib/scope.py) (`resolve_engine_scope`, `parse_scope_expression`, `parse_int_ranges`) and [`scripts/lib/worlds.sh`](file:///scripts/lib/worlds.sh) (`discover_universes`, `discover_worlds`, `discover_manuscripts`).
- **Granular Scoping Invariants**: All craft engines must bind standard scope CLI arguments (`add_scope_arguments(parser)`) and honor chapter ranges (`-c 1-5`, `ch01..ch05`), scene ranges (`--scene 1-3`), book filters (`-b`), and world scopes (`-w`) rather than scanning all files on disk.
- **Intelligent Context Defaults**: When no target is specified, engines must default to the active project configured in `config.json`, the current working directory, or a single discovered project before falling back to full-vault sweeps.
- **Headless Safety**: When writing or modifying test suites in `tests/`, always sandbox `$HOME` (`TEST_HOME=$(mktemp -d)`) and unset `$DISPLAY` / `$WAYLAND_DISPLAY` so tests run headlessly.
- **Python / Shell Boundary**: When executing Python helper commands from shell scripts, pass arguments via `sys.argv` or `stdin` — never interpolate shell variables into `python3 -c` code strings.
- **GTK Worker Threading**: In [`scripts/arcanum_app.py`](file:///scripts/arcanum_app.py), never execute long-running CLI tools or subprocesses on the GTK main UI thread. Always use `_start_worker(target_func)` with `GLib.idle_add` UI callbacks.

---

## 5. Modernization & Branching Governance

- **Branch Isolation**: Cut feature branches directly from trunk (`main`). Use descriptive naming (e.g. `feature/phase-1-packaging`).
- **No Stacked Branches (Hazard H7)**: Merge PRs to `main` before starting subsequent phases. Never build a new phase upon unmerged sibling branches.
- **Living Documentation (Hazard H8)**: When adding, renaming, or deprecating CLI flags or directory layouts, update `README.md`, `docs/AUTHOR_MANUAL.md`, `docs/codebase/`, and this file within the same commit/PR.
- **Regime-Aware Safety**: All subsystems are in the **Post-Testability ("Lit") Regime** at **Safety Rung L4**. Green CI on pull requests is mandatory before merging.
