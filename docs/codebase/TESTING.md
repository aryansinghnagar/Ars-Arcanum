# Testing Patterns

## Core Sections (Required)

### 1) Test Stack and Commands

- Primary test framework: Python `unittest` (CPython 3.10+ standard library)
- Assertion/mocking tools: `unittest.TestCase`, `unittest.mock.patch`, `unittest.mock.MagicMock`
- Commands:

```bash
# Run all automated unit and integration tests (952 tests)
python -m unittest discover tests

# Run specific engine test suite
python -m unittest tests.test_backup_pure_python
python -m unittest tests.test_roche_limit
python -m unittest tests.test_security_remediations
python -m unittest tests.test_scene_break_preservation
python -m unittest tests.test_economy_normalization
python -m unittest tests.test_ecosystem_cohesion
python -m unittest tests.test_resonance

# Run coverage report (86% coverage, fail_under = 85)
coverage run -m unittest discover tests; coverage report

# Run type safety verification
mypy --config-file mypy.ini scripts/lib/
```

### 2) Test Layout

- Test file placement pattern: Dedicated `tests/` directory with `test_<module_name>.py` naming.
- Naming convention: Classes named `Test<FeatureName>`, test methods named `test_<specific_behavior>`.
- Setup files and fixtures: `tests/fixtures/` (`sample_universe`, `sample_manuscript`, `sample_world`).

### 3) Test Scope Matrix

| Scope | Covered? | Typical target | Notes |
|-------|----------|----------------|-------|
| Unit | Yes | All 53 domain engines, lifecycle modules, and helper libraries | 100% engine coverage, pure standard library |
| Integration | Yes | CLI dispatcher, Studio Hub REST API, Zen Studio exports, Pure-Python Backups | Verifies end-to-end data pipelines |
| E2E | Yes | Grand Tour master lifecycle (`test_grand_tour_e2e.py`) | Tests full authoring lifecycle across all domains |
| Ecosystem Cohesion | Yes | CLI dispatch, alias routing, zero isolated mesh nodes (`test_ecosystem_cohesion.py`) | Verifies seamless multi-engine interplay |
| Security / Supply Chain | Yes | `test_security_remediations.py`, `test_path_traversal_defense.py`, `test_threat_model.py`, `test_supply_chain.py` | Validates regex sanitization, CSP, plugin hashes, XML stream scanning |

### 4) Mocking and Isolation Strategy

- Main mocking approach: `tempfile.TemporaryDirectory()` for filesystem isolation; `unittest.mock.patch` for environment variables.
- Isolation guarantees: Every test runs in an ephemeral temporary directory, tearing down all generated files on exit.
- Common failure mode in tests: Unclosed file handles or relative path resolution errors (prevented via `_bootstrap.py` canonical path resolution and `try...finally` descriptor cleanup).

### 5) Coverage and Quality Signals

- Coverage tool + threshold: 86% aggregate coverage with `fail_under = 85` enforced in `pyproject.toml`; 0 test failures or errors permitted.
- Current reported coverage: 952 tests passing (950 passed, 2 skipped, 0 failures) in $\approx 36$ seconds.
- Known gaps/flaky areas: None. All tests are deterministic and offline.

### 6) Evidence

- `tests/test_ecosystem_cohesion.py#L1-L180`
- `tests/test_resonance.py#L1-L150`
- `tests/test_tips.py#L1-L150`
- `tests/test_grand_tour_e2e.py#L1-L100`
- `tests/test_path_traversal_defense.py#L1-L80`
- `.github/workflows/ci.yml#L20-L45`
