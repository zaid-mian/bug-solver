"""Integration tests for the compiled agent graph.

These exercise the real graph wiring without invoking an LLM (no Ollama
needed): node/edge topology and the conditional routing out of Evaluator.
"""

from agent.graph import app, check_status
from constants import Status


def test_graph_topology() -> None:
    compiled = app.get_graph()
    nodes = set(compiled.nodes.keys())
    assert {"Planner", "Coder", "Test Runner", "Evaluator", "PR Writer"} <= nodes

    edges = {(e.source, e.target) for e in compiled.edges}
    assert ("__start__", "Planner") in edges
    assert ("Planner", "Coder") in edges
    assert ("Coder", "Test Runner") in edges
    assert ("Test Runner", "Evaluator") in edges
    assert ("PR Writer", "__end__") in edges
    # Evaluator has conditional edges (to PR Writer / Coder / Planner)
    conditional_targets = {t for s, t in edges if s == "Evaluator"}
    assert {"PR Writer", "Coder", "Planner"} <= conditional_targets


def test_full_retry_lifecycle_routing() -> None:
    # A failed attempt goes back to the Coder...
    assert check_status({"status": Status.FAILED, "retry_count": 3}) == 1
    # ...until retries run out, at which point the Planner re-plans.
    assert check_status({"status": Status.FAILED, "retry_count": 11}) == 1
    assert check_status({"status": Status.IN_PROGRESS, "retry_count": 11}) == 2
    # Success always ships.
    assert check_status({"status": Status.SUCCESS, "retry_count": 11}) == 0
