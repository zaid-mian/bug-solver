# --------------------------------------
#  This is the Abstract Interface for
#   Test operations
# --------------------------------------

from abc import ABC, abstractmethod
import os
from pathlib import Path

from .types import TestResult, TestOpStatus


class BaseTestRunner(ABC):
    @abstractmethod
    def run_tests(
        self, path: str | os.PathLike | Path = None, keyword: str = None
    ) -> TestResult:
        """Runs basic tests"""
        pass

    @abstractmethod
    def collect_tests(self, path: str | os.PathLike | Path = None) -> TestResult:
        """Collect existing tests"""
        pass

    @abstractmethod
    def run_test_command(
        self, args_str: str, timeout_seconds: float = 60.0
    ) -> TestResult:
        """Escape Hatch or fallback for pytest commands"""
        pass
