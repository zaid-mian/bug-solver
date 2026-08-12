# -------------------------------------
#  Concrete Extension of
#  BaseTestRunner Abstract Class
# -------------------------------------

import os
import shlex
import subprocess
from pathlib import Path

from .base import BaseTestRunner
from .types import TestResult, TestOpStatus


class SubprocessPytestManager(BaseTestRunner):
    def run_tests(
        self, paths: list[str | os.PathLike | Path] = None, keyword: str = None
    ) -> TestResult:
        """Runs basic tests"""

        passed = []
        failed = []

        test_results = []
        for path in paths:
            try:
                if keyword == None:
                    test_result = subprocess.run(
                        ["pytest", path], capture_output=True, text=True, check=True
                    )
                else:
                    test_result = subprocess.run(
                        ["pytest", "-k", keyword],
                        capture_output=True,
                        text=True,
                        check=True,
                    )

                # otherwise the tests are successful, add to the list
                test_results.append(test_result)
                passed.append(path)
            except subprocess.CalledProcessError as e:
                if e.returncode == 1:
                    failed.append(path)
                elif e.returncode == 2:
                    return TestResult(
                        status=TestOpStatus.INTERRUPTED,
                        raw_data=e,
                        error_details=e.stderr,
                        passed=passed,
                        failed=failed,
                    )
                elif e.returncode == 3:
                    return TestResult(
                        status=TestOpStatus.INTERNAL_ERROR,
                        raw_data=e,
                        error_details=e.stderr,
                        passed=passed,
                        failed=failed,
                    )
                elif e.returncode == 4:
                    return TestResult(
                        status=TestOpStatus.USAGE_ERROR,
                        raw_data=e,
                        error_details=e.stderr,
                        passed=passed,
                        failed=failed,
                    )
                elif e.returncode == 5:
                    return TestResult(
                        status=TestOpStatus.NO_TESTS_FOUND,
                        raw_data=e,
                        error_details=e.stderr,
                        passed=passed,
                        failed=failed,
                    )

        if failed == []:
            return TestResult(
                status=TestOpStatus.ALL_TESTS_PASSED,
                raw_data=test_results,
                passed=passed,
            )

        return TestResult(
            status=TestOpStatus.SOME_TESTS_FAILED,
            raw_data=test_results,
            passed=passed,
            failed=failed,
        )

    def collect_tests(
        self, paths: list[str | os.PathLike | Path] = None, keyword: str = None
    ) -> TestResult:
        """Collect existing tests"""

        passed = []
        failed = []

        collected_results = []
        for path in paths:
            try:
                if keyword == None:
                    collect_test_result = subprocess.run(
                        ["pytest", "--co", path],
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                else:
                    collect_test_result = subprocess.run(
                        ["pytest", "--co", "-k", keyword],
                        capture_output=True,
                        text=True,
                        check=True,
                    )

                # otherwise the tests are successful, add to the list
                collected_results.append(collect_test_result)
                passed.append(path)
            except subprocess.CalledProcessError as e:
                if e.returncode == 1:
                    return TestResult(
                        status=TestOpStatus.COLLECTION_LEVEL_ERRORS,
                        raw_data=e,
                        passed=passed,
                        failed=failed,
                        error_details=e.stderr,
                    )
                elif e.returncode == 2:
                    return TestResult(
                        status=TestOpStatus.INTERRUPTED,
                        raw_data=e,
                        error_details=e.stderr,
                        passed=passed,
                        failed=failed,
                    )
                elif e.returncode == 5:
                    failed.append(failed)

        if failed == []:
            return TestResult(
                status=TestOpStatus.ALL_COLLECTED_TESTS,
                raw_data=collected_results,
                passed=passed,
            )
        elif passed == []:
            return TestResult(
                status=TestOpStatus.NO_TESTS_COLLECTED,
                raw_data=collected_results,
                failed=failed,
            )

        return TestResult(
            status=TestOpStatus.SOME_TESTS_FAILED,
            raw_data=collected_results,
            passed=passed,
            failed=failed,
        )

    def run_test_command(
        self, args_str: str, timeout_seconds: float = 60.0
    ) -> TestResult:
        """Escape Hatch or fallback for pytest commands"""
        """
        # First validate and tokenize
        is_safe, tokens, error_msg = sanitize_and_tokenize(args_str)
        if not is_safe:
            return GitResult(
                status=GitOpStatus.FORBIDDEN_ARGS,
                raw_data=tokens,
                error_details=error_msg,
            )
        """

        tokens = shlex.split(args_str)

        # Then build the executable array
        command = ["pytest"] + tokens

        try:
            fallback_result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=True,
            )

        except subprocess.TimeoutExpired:
            return TestResult(
                status=TestOpStatus.TIMEOUT,
                error_details=f"Command 'pytest {args_str}' timed out after {timeout_seconds} seconds.",
            )

        except subprocess.CalledProcessError as e:
            return TestResult(
                status=TestOpStatus.SUBPROCESS_ERROR, raw_data=e, error_details=e.stderr
            )

        return TestResult(
            status=TestOpStatus.EXECUTED_FALLBACK_COMMAND, raw_data=fallback_result
        )
