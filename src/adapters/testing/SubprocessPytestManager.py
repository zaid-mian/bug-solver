# -------------------------------------
#  Concrete Extension of
#  BaseTestRunner Abstract Class
# -------------------------------------

import os
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

    def collect_tests(self, path: str | os.PathLike | Path = None) -> TestResult:
        """Collect existing tests"""
        pass

    def run_test_command(
        self, args_str: str, timeout_seconds: float = 60.0
    ) -> TestResult:
        """Escape Hatch or fallback for pytest commands"""
        pass
