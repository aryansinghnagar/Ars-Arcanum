# Contributing to Ars Arcanum

Thank you for considering a contribution. Ars Arcanum is an open-source,
audit-verified project with strict quality gates and a standardized exit-code
contract. This guide is deliberately short and practical.

## Ground rules

- **Target platforms**: Linux (Mint, Ubuntu, Debian, Fedora, Arch), Windows 10/11, and macOS. Everything
  must degrade gracefully and safely, not crash.
- **Design invariants** live in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and
  [docs/ROADMAP.md](docs/ROADMAP.md) — read both before changing scripts. In
  particular: atomic file writes, cross-platform file locking (`ArcanumLock`), the exit-code contract below, and "safe handling of arbitrary
  filenames and Windows device names" are non-negotiable.
- **Architecture history** is recorded as ADRs in
  [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).
  If your change reverses or extends a recorded decision, add a new ADR rather
  than editing an old one.
- **No secrets, no personal paths**: never hardcode usernames, absolute home
  paths, or credentials. Standalone-world detection must stay structural
  (path prefix), not identity-based.

### Exit-code contract (N-01)

Scripts and CLI dispatchers exit `0` on success and non-zero otherwise, with four documented
meanings. Each script's header comment remains the authoritative per-script
contract; when you add a script, document its codes there and keep them
within this table:

| Code | Meaning |
| :--- | :--- |
| `0` | success |
| `1` | runtime or diagnostic failure — the operation ran and failed, or reported findings |
| `2` | usage or environment error — bad option, unknown world, ambiguous world selection, missing dependency |
| `3` | nothing to act on — required argument absent with no GUI/TTY fallback, or the user aborted an interactive selection |

## Development setup

```bash
# Clone the repository
git clone https://github.com/aryansinghnagar/Ars-Arcanum.git
cd Ars-Arcanum

# Install package in editable mode
pip install -e .

# Dry-run Linux desktop setup (optional)
bash scripts/setup_arcanum.sh --dry-run
```

You do not need the full desktop toolchain to iterate: the test suites sandbox
`HOME` and unset `DISPLAY`, so they run headlessly with just standard Python 3.10+ installed.

## Before you submit — the quality gate

Every change must pass all of these quality gates:

```bash
# 1. Full Python Unit & Integration Test Suite (855 tests, 0 failures allowed)
python -m unittest discover tests

# 2. Strict Expanded Ruff Linter Pass (0 violations allowed)
ruff check .

# 3. Strict Mypy Static Type Checking (0 errors)
mypy --explicit-package-bases scripts tests

# 4. Coverage Threshold Enforcement (fail_under = 80)
coverage run -m unittest discover tests; coverage report --fail-under=80

# 5. Shell syntax & 7-stage integration verification harness (POSIX)
bash scripts/verify.sh
```

`verify.sh` is the project's core quality gate on POSIX platforms — it must be able to *fail*
(it fails closed by design; if you find a stage that cannot fail, that is a
bug worth reporting). When adding new scripts, wire them into the harness's
stage 1 and the CI lint lists.

New shell code should pass `shellcheck -S warning`. When crossing the shell/Python boundary, pass
data via **stdin or argv** — never interpolate values into `python3 -c`
source strings.

## Commit style

Conventional commits, atomic scopes — e.g. `fix(export): ...`,
`feat(concordance): ...`, `ci: ...`, `docs(meta): ...`. Reference the
affected component in parentheses and explain *why* in the body, not just
*what*.

## Submitting

1. Fork, branch from `main`.
2. Make your change; run the full quality gate above.
3. Open a pull request against `main` describing the motivation, the change,
   and the verification output (a pasted `ALL-CHECKS-PASS` goes a long way).

## Reporting bugs and security issues

- Ordinary bugs: GitHub issues with reproduction steps.
- **Security vulnerabilities**: follow the private-disclosure process in
  [SECURITY.md](SECURITY.md) or [docs/GOVERNANCE.md](docs/GOVERNANCE.md) — please do not open public issues for
  undisclosed vulnerabilities.
