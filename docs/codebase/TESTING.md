# Testing Patterns

## Core Sections (Required)

### 1) Test Stack and Commands

- Primary test framework: Python `unittest` (CPython 3.10+ standard library)
- Assertion/mocking tools: `unittest.TestCase`, `unittest.mock.patch`, `unittest.mock.MagicMock`
- Commands:

```bash
# Run all automated unit and integration tests (960 tests)
python -m unittest discover tests

# Run high-performance multi-core parallel test runner (~20s)
python scripts/test_parallel.py

# Run specific engine test suite
python -m unittest tests.test_scope
python -m unittest tests.test_registry
python -m unittest tests.test_resonance
python -m unittest tests.test_economy
python -m unittest tests.test_climate
python -m unittest tests.test_tactical_sim
python -m unittest tests.test_epistemic_safety
python -m unittest tests.test_data_access
python -m unittest tests.test_frontmatter
python -m unittest tests.test_docx_sync
python -m unittest tests.test_structure
python -m unittest tests.test_studio_hub
python -m unittest tests.test_lockfile
python -m unittest tests.test_path_traversal_defense
python -m unittest tests.test_aria_accessibility
python -m unittest tests.test_vault_search
python -m unittest tests.test_astrophysics
python -m unittest tests.test_security_remediations
python -m unittest tests.test_backup_pure_python

# Run coverage report with threshold enforcement
coverage run -m unittest discover tests; coverage report --fail-under=80

# Run type safety verification (217 source files clean)
mypy --explicit-package-bases scripts tests
```

### 2) Test Layout

- Test file placement pattern: Dedicated `tests/` directory with `test_<module_name>.py` naming.
- Naming convention: Classes named `Test<FeatureName>`, test methods named `test_<specific_behavior>`.
- Setup files and fixtures: `tests/fixtures/` (`sample_universe`, `sample_manuscript`, `sample_world`).

### 3) Test Scope Matrix

| Scope | Covered? | Typical target | Notes |
|---|---|---|---|
| Unit | Yes | All 47 domain engines, data access layer, recursive YAML parser, and helper libraries | 100% engine coverage, pure standard library |
| Integration | Yes | CLI dispatcher, Studio Hub REST API (chapter save), Zen Studio exports, Pure-Python Backups & Restores | Verifies end-to-end data pipelines |
| E2E | Yes | Grand Tour master lifecycle ([`tests/test_grand_tour_e2e.py`](file:///tests/test_grand_tour_e2e.py)) | Tests full authoring lifecycle across all deterministic domains |
| Accessibility & ARIA | Yes | [`tests/test_aria_accessibility.py`](file:///tests/test_aria_accessibility.py), [`tests/test_wcag_contrast.py`](file:///tests/test_wcag_contrast.py) | Asserts semantic ARIA landmarks, tab panels, modals, and WCAG AA contrast |
| Ecosystem Cohesion | Yes | CLI dispatch, alias routing, zero isolated mesh nodes ([`tests/test_ecosystem_cohesion.py`](file:///tests/test_ecosystem_cohesion.py)) | Verifies seamless multi-engine interplay |
| Security / Invariants | Yes | [`tests/test_security_remediations.py`](file:///tests/test_security_remediations.py), [`tests/test_path_traversal_defense.py`](file:///tests/test_path_traversal_defense.py), [`tests/test_threat_model.py`](file:///tests/test_threat_model.py) | Validates regex sanitization, Windows device name defense, CSP, XML stream scanning, and restore directory protection |

### 4) Mocking and Isolation Strategy

- Main mocking approach: `tempfile.TemporaryDirectory()` for filesystem isolation; `unittest.mock.patch` for environment variables.
- Isolation guarantees: Every test runs in an ephemeral temporary directory, tearing down all generated files on exit.
- Common failure mode in tests: Unclosed file handles or relative path resolution errors (prevented via `_bootstrap.py` canonical path resolution and `try...finally` descriptor cleanup).

### 5) Coverage and Quality Signals

- Coverage tool + threshold: 80% aggregate coverage enforced in `pyproject.toml` (`fail_under = 80`); 0 test failures or errors permitted.
- Current reported coverage: 960 tests collected (958 passed, 2 skipped on Windows, 0 failures) with 80%+ aggregate coverage in $\approx 20$ seconds via parallel runner (`scripts/test_parallel.py`).
- Known gaps/flaky areas: None. All tests are 100% deterministic and offline.

### 6) Evidence

- [`tests/test_data_access.py#L1-L60`](file:///tests/test_data_access.py#L1-L60)
- [`tests/test_frontmatter.py#L1-L80`](file:///tests/test_frontmatter.py#L1-L80)
- [`tests/test_docx_sync.py#L1-L100`](file:///tests/test_docx_sync.py#L1-L100)
- [`tests/test_structure.py#L1-L100`](file:///tests/test_structure.py#L1-L100)
- [`tests/test_studio_hub.py#L1-L80`](file:///tests/test_studio_hub.py#L1-L80)
- [`tests/test_registry.py#L1-L100`](file:///tests/test_registry.py#L1-L100)
- [`tests/test_resonance.py#L1-L100`](file:///tests/test_resonance.py#L1-L100)
- [`tests/test_economy.py#L1-L100`](file:///tests/test_economy.py#L1-L100)
- [`tests/test_lockfile.py#L1-L100`](file:///tests/test_lockfile.py#L1-L100)
- [`tests/test_path_traversal_defense.py#L1-L95`](file:///tests/test_path_traversal_defense.py#L1-L95)
- [`tests/test_backup_pure_python.py#L1-L100`](file:///tests/test_backup_pure_python.py#L1-L100)
- [`tests/test_grand_tour_e2e.py#L1-L100`](file:///tests/test_grand_tour_e2e.py#L1-L100)
- [`tests/test_type_safety.py#L1-L40`](file:///tests/test_type_safety.py#L1-L40)
- [`pyproject.toml#L35-L60`](file:///pyproject.toml#L35-L60)
