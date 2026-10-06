"""
src/tools/testing_tools.py

Bridge layer exposing test operations to the LLM.
Translates adapter responses/outcomes into plain-text tool results.
"""

from typing import List
from langchain_core.tools import tool, BaseTool

from adapters.testing.base import BaseTestRunner
from adapters.testing.types import TestOpStatus


def _format(result) -> str:
    """Render a TestResult as readable text for the model."""
    lines = [f"status: {result.status.value}"]
    if result.passed:
        lines.append(f"passed: {result.passed}")
    if result.failed:
        lines.append(f"failed: {result.failed}")
    if result.error_details:
        lines.append(f"details: {result.error_details}")
    if result.raw_data:
        output = str(result.raw_data)
        # keep full tracebacks for failures, but cap pathological output
        if len(output) > 12000:
            output = output[:6000] + "\n...[truncated]...\n" + output[-6000:]
        lines.append(f"output:\n{output}")
    return "\n".join(lines)


def testing_tools(test_adapter: BaseTestRunner) -> List[BaseTool]:
    """
    Factory that binds a test-runner adapter to LangChain @tool decorators.
    Returns a list of tools to be bound to the Test Runner node.
    """

    @tool(parse_docstring=True)
    def run_tests(paths: List[str] = None, keyword: str = "") -> str:
        """
        Run pytest over the given test paths and return the full results.

        Args:
            paths: Test files or directories to run, e.g. ["tests/test_api.py"].
                Defaults to the whole repository when omitted.
            keyword: Optional -k expression to select tests, e.g. "test_login".
        """
        result = test_adapter.run_tests(
            paths=paths, keyword=keyword or None, timeout_seconds=300.0
        )
        return _format(result)

    @tool(parse_docstring=True)
    def collect_tests(paths: List[str] = None) -> str:
        """
        Collect (do not run) tests and return the collection report.
        Use this to discover what tests exist before running them.

        Args:
            paths: Test files or directories to collect from.
                Defaults to the whole repository when omitted.
        """
        result = test_adapter.collect_tests(paths=paths, timeout_seconds=120.0)
        return _format(result)

    @tool(parse_docstring=True)
    def run_test_command(args_str: str, timeout_seconds: float = 120.0) -> str:
        """
        Run an arbitrary pytest command: `pytest <args_str>`.

        The argument string is sanitized first: shell metacharacters and
        interactive flags (e.g. --pdb) are rejected, and the command always
        runs inside the target repository with a timeout.

        Args:
            args_str: Arguments for pytest, e.g. "tests/ -x -q" or
                "tests/test_api.py::test_login -v".
            timeout_seconds: Kill the run after this many seconds.
        """
        result = test_adapter.run_test_command(
            args_str=args_str, timeout_seconds=timeout_seconds
        )
        return _format(result)

    return [run_tests, collect_tests, run_test_command]
