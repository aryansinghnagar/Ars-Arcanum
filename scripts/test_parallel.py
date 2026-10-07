#!/usr/bin/env python3
"""
Ars Arcanum High-Performance Parallel Test Harness
(scripts/test_parallel.py)
================================================================================
Zero-dependency, multi-process test runner utilizing Python's ProcessPoolExecutor
to execute the comprehensive test suite across available CPU cores concurrently.

Capabilities:
1. Dynamic Test Module Discovery:
   - Discovers all `tests/test_*.py` test modules.
2. Multi-Core Process Pool Execution:
   - Distributes test files across `os.cpu_count()` worker processes.
   - Captures stdout/stderr per test process to avoid interleaved terminal noise.
3. Summary & Failure Diagnostics:
   - Real-time progress indicators.
   - Comprehensive failure diffs, timing metrics, and exit code propagation.

Zero external dependencies; 100% standard library Python.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import io
import os
import sys
import time
import unittest
from pathlib import Path

# UTF-8 stream re-encoding for cross-platform Windows CLI safety
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Add project root to sys.path
SCRIPTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPTS_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


def _run_single_test_module(module_name: str) -> dict:
    """Worker task that runs a single test module in an isolated process."""
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    start_t = time.time()
    stream = io.StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=1)
    loader = unittest.defaultTestLoader

    try:
        suite = loader.loadTestsFromName(module_name)
        result = runner.run(suite)
        duration = time.time() - start_t

        return {
            "module": module_name,
            "tests_run": result.testsRun,
            "was_successful": result.wasSuccessful(),
            "failures": len(result.failures),
            "errors": len(result.errors),
            "skipped": len(result.skipped),
            "output": stream.getvalue(),
            "failure_details": [f"{t!s}:\n{tb}" for t, tb in (result.failures + result.errors)],
            "duration": duration,
        }
    except Exception as e:
        duration = time.time() - start_t
        return {
            "module": module_name,
            "tests_run": 0,
            "was_successful": False,
            "failures": 0,
            "errors": 1,
            "skipped": 0,
            "output": f"Exception loading {module_name}: {e}\n",
            "failure_details": [f"{module_name}: {e}"],
            "duration": duration,
        }


def run_parallel_tests(
    test_dir: Path | None = None,
    workers: int | None = None,
    filter_pattern: str | None = None,
) -> int:
    """Discovers and executes all tests concurrently using ProcessPoolExecutor."""
    tests_path = (test_dir or PROJECT_ROOT / "tests").resolve()
    if not tests_path.is_dir():
        print(f"Error: Test directory not found: {tests_path}", file=sys.stderr)
        return 1

    # Discover test files
    test_files = sorted(tests_path.glob("test_*.py"))
    if filter_pattern:
        test_files = [f for f in test_files if filter_pattern.lower() in f.stem.lower()]

    if not test_files:
        print(f"No test files found in {tests_path}")
        return 0

    module_names = [f"tests.{f.stem}" for f in test_files]
    num_workers = workers or max(1, min(16, (os.cpu_count() or 4)))

    print("=== Ars Arcanum Sovereign Test Runner ===")
    print(f"Discovered {len(module_names)} test modules across {num_workers} parallel worker processes.\n")

    overall_start = time.time()
    results = []
    failed_results = []

    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
        future_to_mod = {executor.submit(_run_single_test_module, mod): mod for mod in module_names}

        for future in concurrent.futures.as_completed(future_to_mod):
            mod_name = future_to_mod[future]
            try:
                res = future.result()
                results.append(res)
                if not res["was_successful"]:
                    failed_results.append(res)
                    print(f"  [FAIL] {res['module']} ({res['duration']:.2f}s) - {res['failures']} fail, {res['errors']} err")
                else:
                    print(f"  [PASS] {res['module']} ({res['tests_run']} tests, {res['duration']:.2f}s)")
            except Exception as e:
                print(f"  [FAIL] {mod_name} - Process execution error: {e}", file=sys.stderr)
                failed_results.append({"module": mod_name, "failure_details": [str(e)]})

    total_time = time.time() - overall_start
    total_tests = sum(r.get("tests_run", 0) for r in results)
    total_failures = sum(r.get("failures", 0) for r in results)
    total_errors = sum(r.get("errors", 0) for r in results)
    total_skipped = sum(r.get("skipped", 0) for r in results)

    print("\n" + "=" * 60)
    if failed_results:
        print(f"FAILURES DETECTED ({len(failed_results)} module(s)):")
        for fr in failed_results:
            print(f"\n--- Failure Details: {fr['module']} ---")
            for detail in fr.get("failure_details", []):
                print(detail)
        print("=" * 60)
        print(f"FAILED (failures={total_failures}, errors={total_errors}) in {total_time:.2f}s")
        print(f"Ran {total_tests} tests across {len(results)} modules (skipped={total_skipped}).")
        return 1

    print(f"OK (skipped={total_skipped})")
    print(f"Ran {total_tests} tests in {total_time:.2f}s across {len(results)} modules with {num_workers} processes.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ars Arcanum High-Performance Parallel Test Harness")
    parser.add_argument("-w", "--workers", type=int, default=None, help="Number of worker processes (default: CPU count)")
    parser.add_argument("-k", "--filter", help="Filter test module names by substring")
    parser.add_argument("-d", "--test-dir", help="Path to tests directory")
    args = parser.parse_args(argv)

    t_dir = Path(args.test_dir) if args.test_dir else None
    return run_parallel_tests(test_dir=t_dir, workers=args.workers, filter_pattern=args.filter)


if __name__ == "__main__":
    sys.exit(main())
