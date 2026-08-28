# ---------------------------------
#  Adapter Type: Test operations
# ---------------------------------

import os
from enum import Enum
from dataclasses import dataclass
from typing import Any, Optional, Dict
from pathlib import Path


class TestOpStatus(Enum):
    # ---------------------
    #  For run_tests
    # ---------------------
    ALL_TESTS_PASSED = "all_tests_passed"

    # errors
    SOME_TESTS_FAILED = "some_tests_failed"  # exit 1: ran but some failed
    NO_TESTS_FOUND = "no_tests_found"  # exit 5
    INTERRUPTED = "interrupted"  # exit 2
    INTERNAL_ERROR = "internal_error"  # exit 3
    USAGE_ERROR = "usage_error"  # exit 4: bad args

    # ---------------------
    #  For collect_tests
    # ---------------------
    ALL_COLLECTED_TESTS = "all_collected_tests"  # collect-only success

    # errors
    COLLECTION_LEVEL_ERRORS = "collection_level_errors"  # code 1
    SOME_TESTS_NOT_COLLECTED = "some_tests_not_collected"
    NO_TESTS_COLLECTED = "no_tests_collected"  # code 5

    # -----------------------
    #  For run_test_command
    # -----------------------
    EXECUTED_FALLBACK_COMMAND = "executed_fallback_command"

    # errors
    TIMEOUT = "timeout"

    # -----------------------------
    #  General/Subprocess Errors
    # -----------------------------
    SUBPROCESS_ERROR = "subprocess_error"


@dataclass
class TestResult:
    status: TestOpStatus
    raw_data: Any = None
    passed: Optional[list[str | os.PathLike | Path]] = None
    failed: Optional[list[str | os.PathLike | Path]] = None
    error_details: Optional[str] = None
