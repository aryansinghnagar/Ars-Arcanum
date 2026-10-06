# Coding Conventions

## Core Sections (Required)

### 1) Naming Rules

| Item | Rule | Example | Evidence |
|------|------|---------|----------|
| Files | Lowercase snake_case | `astrophysics.py`, `test_resonance.py` | [`scripts/lib/`](file:///scripts/lib/), [`tests/`](file:///tests/) |
| Functions/methods | Lowercase snake_case with descriptive verbs | `simulate_cascade()`, `get_by_engine()` | [`scripts/lib/resonance.py`](file:///scripts/lib/resonance.py), [`scripts/lib/tips.py`](file:///scripts/lib/tips.py) |
| Types/interfaces/classes | PascalCase | `ResonanceMesh`, `TipDatabase`, `EngineSpec` | [`scripts/lib/registry.py`](file:///scripts/lib/registry.py), [`scripts/lib/registry_base.py`](file:///scripts/lib/registry_base.py), [`scripts/lib/tips.py`](file:///scripts/lib/tips.py) |
| Constants/Enums | UPPER_SNAKE_CASE | `TipPillar.COSMOLOGY_PHYSICS`, `WINDOWS_RESERVED_NAMES` | [`scripts/lib/tips.py`](file:///scripts/lib/tips.py), [`scripts/lib/_bootstrap.py`](file:///scripts/lib/_bootstrap.py) |

### 2) Formatting and Linting

- Formatter: Ruff (configured via `pyproject.toml`)
- Linter: Ruff (rule families: `E`, `F`, `B`, `S`, `UP`, `SIM`, `I`, `RUF`, `C901`)
- Most relevant enforced rules:
  1. `S108` / `S603`: Strict subprocess and path traversal security guards.
  2. `UP035` / `UP038`: Modern Python 3.10+ typing syntax (`list[str]`, `dict[str, Any]`, `X | Y`).
  3. `C901`: Cyclomatic complexity threshold $\le 20$ for core functions.
- Run commands:
  ```bash
  ruff check .
  mypy --explicit-package-bases scripts tests
  ```

### 3) Import and Module Conventions

- Import grouping/order: Standard library imports $\to$ third-party GUI (optional) $\to$ local internal imports (`lib._bootstrap`, `lib.registry_base`, `lib.registry_specs`, `lib.registry`).
- Alias vs relative import policy: Bootstrap fallback pattern `try: import lib.X; except ImportError: import X`.
- Public exports/barrel policy: Explicit `__all__` exported from `scripts/lib/registry.py`, `scripts/lib/registry_base.py`, and `scripts/lib/registry_specs/__init__.py`.
- Module size limit: Source files must not exceed 800 lines of code; large domains must be split into dedicated sub-packages.

### 4) Error and Logging Conventions

- Error strategy by layer: Explicit domain exception handling with user-facing diagnostic remediation (`world_doctor.py`, `diagnostics.py`).
- Concurrency errors: File lock exceptions caught with non-swallowed debug diagnostics via `logger.debug()`.
- Logging style and required context fields: Standard library `logging.getLogger("arcanum.<subsystem>")`.
- Sensitive-data redaction rules: SEC-02 credential redaction; zero API keys or external secrets committed (`.gitignore#L52-L63`).

### 5) Testing Conventions

- Test file naming/location rule: Co-located in `tests/test_<module_name>.py`.
- Mocking strategy norm: `unittest.mock.patch` with temporary directory isolation via `tempfile.TemporaryDirectory()`.
- Coverage expectation: 100% engine coverage across all 47 registered engines, 862 automated unit/integration tests with 0 failures permitted.

### 6) Evidence

- [`pyproject.toml#L1-L35`](file:///pyproject.toml#L1-L35)
- [`scripts/lib/registry_base.py#L1-L60`](file:///scripts/lib/registry_base.py#L1-L60)
- [`scripts/lib/registry.py#L1-L60`](file:///scripts/lib/registry.py#L1-L60)
- [`scripts/lib/_bootstrap.py#L75-L115`](file:///scripts/lib/_bootstrap.py#L75-L115)
- [`tests/test_tips.py#L1-L50`](file:///tests/test_tips.py#L1-L50)
- [`AGENTS.md#L1-L60`](file:///AGENTS.md#L1-L60)
