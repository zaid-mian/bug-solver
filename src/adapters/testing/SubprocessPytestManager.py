# -------------------------------------
#  Concrete Extension of
#  BaseTestRunner Abstract Class
# -------------------------------------
#
#  Runs pytest inside the *target* repository (cwd-scoped), with every
#  subprocess call going through a sanitizer first: no shell, no
#  metacharacters, no interactive flags. The agent can run tests but
#  can never escape into arbitrary shell execution.

import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

from .base import BaseTestRunner
from .types import TestResult, TestOpStatus

# Invoke pytest via the current interpreter so the adapter works inside
# virtualenvs and containers regardless of PATH.
_PYTEST = [sys.executable, "-m", "pytest"]

# Characters that only make sense for shell interpretation. The subprocess
# calls below always use shell=False, but we reject them anyway so a
# compromised/misbehaving model cannot smuggle shell syntax through.
_SHELL_METACHARS = set(";&|$`<>(){}!\\")

# pytest flags that would hang or escape the sandbox
_BLOCKED_FLAGS = {"--pdb", "--pdbcls", "--trace"}


def sanitize_pytest_args(args_str: str) -> Tuple[bool, List[str], str]:
    """Validate an argument string for `pytest <args>`.

    Returns (is_safe, tokens, error_reason). Safe means: tokenizes cleanly,
    contains no shell metacharacters, and contains no blocked flags.
    """
    if not args_str or not args_str.strip():
        return False, [], "No pytest arguments provided."

    for ch in args_str:
        if ch in _SHELL_METACHARS:
            return (
                False,
                [],
                f"Shell metacharacter {ch!r} is not allowed in test commands.",
            )

    try:
        tokens = shlex.split(args_str)
    except ValueError as e:
        return False, [], f"Invalid shell syntax or unclosed quote: {e}."

    if not tokens:
        return False, [], "No pytest arguments provided."

    for token in tokens:
        if token in _BLOCKED_FLAGS:
            return False, [], f"pytest flag {token!r} is prohibited (interactive)."

    return True, tokens, ""


class SubprocessPytestManager(BaseTestRunner):
    def __init__(self, repo_path: str | os.PathLike | Path | None = None):
        # All test commands run with cwd set to the target repository, so
        # the agent can never accidentally run tests against its own code.
        self.repo_path = Path(repo_path) if repo_path else None

    def _run(self, cmd: List[str], timeout: float) -> subprocess.CompletedProcess:
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=self.repo_path,
            check=False,
        )

    def run_tests(
        self,
        paths: list[str | os.PathLike | Path] = None,
        keyword: str = None,
        timeout_seconds: float = 300.0,
    ) -> TestResult:
        """Runs pytest over the given paths (defaults to the repo root)."""

        targets = [str(p) for p in paths] if paths else ["."]
        passed, failed = [], []
        outputs = []

        for target in targets:
            cmd = _PYTEST + [target, "-v", "--tb=short"]
            if keyword:
                cmd += ["-k", keyword]
            try:
                result = self._run(cmd, timeout_seconds)
            except subprocess.TimeoutExpired:
                return TestResult(
                    status=TestOpStatus.TIMEOUT,
                    error_details=f"pytest {target} timed out after {timeout_seconds}s.",
                    passed=passed,
                    failed=failed,
                )
            outputs.append(result.stdout + result.stderr)
            if result.returncode == 0:
                passed.append(target)
            elif result.returncode == 1:
                failed.append(target)
            elif result.returncode == 2:
                return TestResult(
                    status=TestOpStatus.INTERRUPTED,
                    error_details=result.stderr,
                    passed=passed,
                    failed=failed,
                )
            elif result.returncode == 5:
                return TestResult(
                    status=TestOpStatus.NO_TESTS_FOUND,
                    error_details=result.stderr or "No tests found.",
                    passed=passed,
                    failed=failed,
                )
            else:
                return TestResult(
                    status=TestOpStatus.INTERNAL_ERROR,
                    error_details=result.stderr,
                    passed=passed,
                    failed=failed,
                )

        if not failed:
            return TestResult(
                status=TestOpStatus.ALL_TESTS_PASSED,
                raw_data="\n".join(outputs),
                passed=passed,
            )
        return TestResult(
            status=TestOpStatus.SOME_TESTS_FAILED,
            raw_data="\n".join(outputs),
            passed=passed,
            failed=failed,
        )

    def collect_tests(
        self,
        paths: list[str | os.PathLike | Path] = None,
        keyword: str = None,
        timeout_seconds: float = 120.0,
    ) -> TestResult:
        """Collect (do not run) tests, returning the collection report."""

        targets = [str(p) for p in paths] if paths else ["."]
        outputs = []
        for target in targets:
            cmd = _PYTEST + ["--collect-only", "-q", target]
            if keyword:
                cmd += ["-k", keyword]
            try:
                result = self._run(cmd, timeout_seconds)
            except subprocess.TimeoutExpired:
                return TestResult(
                    status=TestOpStatus.TIMEOUT,
                    error_details=f"Collection timed out after {timeout_seconds}s.",
                )
            outputs.append(result.stdout + result.stderr)
            if result.returncode == 5:
                return TestResult(
                    status=TestOpStatus.NO_TESTS_COLLECTED,
                    error_details=result.stderr or "No tests collected.",
                )
            if result.returncode not in (0, 1):
                return TestResult(
                    status=TestOpStatus.COLLECTION_LEVEL_ERRORS,
                    error_details=result.stderr,
                )

        return TestResult(
            status=TestOpStatus.ALL_COLLECTED_TESTS,
            raw_data="\n".join(outputs),
        )

    def run_test_command(
        self, args_str: str, timeout_seconds: float = 120.0
    ) -> TestResult:
        """Escape hatch: run `pytest <args_str>` after sanitization."""

        is_safe, tokens, error_msg = sanitize_pytest_args(args_str)
        if not is_safe:
            return TestResult(
                status=TestOpStatus.USAGE_ERROR,
                error_details=f"Blocked test command: {error_msg}",
            )

        try:
            result = self._run(_PYTEST + tokens, timeout_seconds)
        except subprocess.TimeoutExpired:
            return TestResult(
                status=TestOpStatus.TIMEOUT,
                error_details=(
                    f"Command 'pytest {args_str}' timed out "
                    f"after {timeout_seconds} seconds."
                ),
            )

        return TestResult(
            status=TestOpStatus.EXECUTED_FALLBACK_COMMAND,
            raw_data=(result.stdout + result.stderr),
            error_details=f"exit code: {result.returncode}",
        )
