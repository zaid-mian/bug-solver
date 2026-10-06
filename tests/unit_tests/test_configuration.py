from langgraph.pregel import Pregel

from agent.graph import app, check_status
from constants import Status


def test_graph_compiles_to_pregel() -> None:
    assert isinstance(app, Pregel)


def test_graph_has_all_five_nodes() -> None:
    nodes = set(app.get_graph().nodes.keys())
    assert {"Planner", "Coder", "Test Runner", "Evaluator", "PR Writer"} <= nodes


def test_router_wiring() -> None:
    # SUCCESS -> PR Writer (0), FAILED -> Coder (1)
    assert check_status({"status": Status.SUCCESS, "retry_count": 0}) == 0
    assert check_status({"status": Status.FAILED, "retry_count": 0}) == 1
