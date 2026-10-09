# Testing Patterns

## Core Sections (Required)

### 1) Test Stack and Commands

- Primary test framework: Python `unittest` (CPython 3.10+ standard library)
- Assertion/mocking tools: `unittest.TestCase`, `unittest.mock.patch`, `unittest.mock.MagicMock`
- Commands:


```bash
# Run all automated unit and integration tests (404+ tests across 55 modules)
python -m unittest discover tests

# Run high-performance multi-core parallel test runner (~2.49s)
python scripts/test_parallel.py

# Run specific engine test suite
python -m unittest tests.test_scope
python -m unittest tests.test_registry
python -m unittest tests.test_word_counter
python -m unittest tests.test_writing_sprint
python -m unittest tests.test_revision_heatmap
python -m unittest tests.test_portfolio
python -m unittest tests.test_epistemic_safety
python -m unittest tests.test_data_access
python -m unittest tests.test_frontmatter
python -m unittest tests.test_docx_sync
python -m unittest tests.test_lockfile
python -m unittest tests.test_path_traversal_defense
python -m unittest tests.test_security_remediations
python -m unittest tests.test_backup_pure_python

# Run coverage report with threshold enforcement
coverage run -m unittest discover tests; coverage report --fail-under=80

# Run type safety verification (112 source files clean)
mypy --explicit-package-bases scripts tests
```

### 2) Test Layout

- Test file placement pattern: Dedicated `tests/` directory with `test_<module_name>.py` naming.
- Naming convention: Classes named `Test<FeatureName>`, test methods named `test_<specific_behavior>`.
- Setup files and fixtures: `tests/fixtures/` (`sample_universe`, `sample_manuscript`, `sample_world`).

### 3) Test Scope Matrix

| Scope | Covered? | Typical target | Notes |
|---|---|---|---|
| Unit | Yes | All 17 core domain engines, data access layer, YAML parser, and helper libraries | 100% engine coverage, pure standard library |
| Integration | Yes | CLI dispatcher, Pure-Python Backups & Restores, DOCX roundtrips, Snapshot milestones, Writing Sprint sessions | Verifies end-to-end data pipelines |
| Ecosystem Cohesion | Yes | CLI dispatch, alias routing, retirement doctrine guidance ([`tests/test_ecosystem_cohesion.py`](file:///tests/test_ecosystem_cohesion.py)) | Verifies seamless multi-engine interplay |
| Security / Invariants | Yes | [`tests/test_security_remediations.py`](file:///tests/test_security_remediations.py), [`tests/test_path_traversal_defense.py`](file:///tests/test_path_traversal_defense.py), [`tests/test_threat_model.py`](file:///tests/test_threat_model.py) | Validates regex sanitization, Windows device name defense, CSP, XML stream scanning, and restore directory protection |

### 4) Mocking and Isolation Strategy

- Main mocking approach: `tempfile.TemporaryDirectory()` for filesystem isolation; `unittest.mock.patch` for environment variables.
- Isolation guarantees: Every test runs in an ephemeral temporary directory, tearing down all generated files on exit.
- Common failure mode in tests: Unclosed file handles or relative path resolution errors (prevented via `_bootstrap.py` canonical path resolution and `try...finally` descriptor cleanup).

### 5) Coverage and Quality Signals

- Coverage tool + threshold: 80% aggregate coverage enforced in `pyproject.toml` (`fail_under = 80`); 0 test failures or errors permitted.
- Current reported coverage: 404+ tests collected across 55 test modules (404 passed, 0 failures) with 81%+ aggregate coverage in $\approx 2.49$ seconds via parallel runner (`scripts/test_parallel.py`).
- Known gaps/flaky areas: None. All tests are 100% deterministic and offline.

### 6) Evidence

- [`tests/test_data_access.py#L1-L60`](file:///tests/test_data_access.py#L1-L60)
- [`tests/test_frontmatter.py#L1-L80`](file:///tests/test_frontmatter.py#L1-L80)
- [`tests/test_docx_sync.py#L1-L100`](file:///tests/test_docx_sync.py#L1-L100)
- [`tests/test_registry.py#L1-L100`](file:///tests/test_registry.py#L1-L100)
- [`tests/test_revision_heatmap.py#L1-L100`](file:///tests/test_revision_heatmap.py#L1-L100)
- [`tests/test_portfolio.py#L1-L100`](file:///tests/test_portfolio.py#L1-L100)
- [`tests/test_lockfile.py#L1-L100`](file:///tests/test_lockfile.py#L1-L100)
- [`tests/test_path_traversal_defense.py#L1-L95`](file:///tests/test_path_traversal_defense.py#L1-L95)
- [`tests/test_backup_pure_python.py#L1-L100`](file:///tests/test_backup_pure_python.py#L1-L100)
- [`tests/test_type_safety.py#L1-L40`](file:///tests/test_type_safety.py#L1-L40)
- [`pyproject.toml#L35-L60`](file:///pyproject.toml#L35-L60)

