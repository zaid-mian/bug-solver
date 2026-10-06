"""Unit tests for the test-execution tool factory and the sandboxed adapter.

Builds a tiny throwaway pytest project in a tmp dir and runs the real
adapter against it — proving tests execute inside the target repo and
that the sanitizer actually blocks hostile input.
"""

import textwrap
from pathlib import Path

import pytest

from adapters.testing.SubprocessPytestManager import SubprocessPytestManager
from adapters.testing.types import TestOpStatus
from tools.testing_tools import testing_tools as make_testing_tools


@pytest.fixture()
def mini_repo(tmp_path: Path) -> Path:
    (tmp_path / "test_ok.py").write_text(
        textwrap.dedent(
            """\
            def test_ok():
                assert 1 + 1 == 2
            """
        )
    )
    (tmp_path / "test_bad.py").write_text(
        textwrap.dedent(
            """\
            def test_bad():
                assert 1 + 1 == 3
            """
        )
    )
    return tmp_path


def test_factory_exposes_three_tools(mini_repo):
    tools = make_testing_tools(SubprocessPytestManager(repo_path=mini_repo))
    assert sorted(t.name for t in tools) == [
        "collect_tests",
        "run_test_command",
        "run_tests",
    ]


def test_collect_finds_tests(mini_repo):
    adapter = SubprocessPytestManager(repo_path=mini_repo)
    result = adapter.collect_tests(paths=["."])
    assert result.status == TestOpStatus.ALL_COLLECTED_TESTS
    assert "test_ok" in str(result.raw_data)
    assert "test_bad" in str(result.raw_data)


def test_run_tests_reports_pass_and_fail(mini_repo):
    adapter = SubprocessPytestManager(repo_path=mini_repo)
    ok_result = adapter.run_tests(paths=["test_ok.py"])
    assert ok_result.status == TestOpStatus.ALL_TESTS_PASSED

    bad_result = adapter.run_tests(paths=["test_bad.py"])
    assert bad_result.status == TestOpStatus.SOME_TESTS_FAILED
    assert "test_bad" in str(bad_result.raw_data)


def test_run_test_command_sanitizes(mini_repo):
    adapter = SubprocessPytestManager(repo_path=mini_repo)
    blocked = adapter.run_test_command("test_ok.py; rm -rf /tmp/should-not-exist")
    assert blocked.status == TestOpStatus.USAGE_ERROR
    assert "Blocked" in (blocked.error_details or "")


def test_run_test_command_executes(mini_repo):
    adapter = SubprocessPytestManager(repo_path=mini_repo)
    result = adapter.run_test_command("test_ok.py -q")
    assert result.status == TestOpStatus.EXECUTED_FALLBACK_COMMAND
    assert "1 passed" in str(result.raw_data)
