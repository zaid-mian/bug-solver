"""LangGraph single-node graph template.

Returns a predefined response. Replace logic and configuration as needed.
"""

from __future__ import annotations

from typing import Literal

from langgraph.graph import END, START, StateGraph

# -------------------
#  Import Constants
# -------------------
from constants import MAX_RETRIES, Status

from .nodes import coder, evaluator, planner, pr_writer, test_runner
from .state import State

'''
# -------------------
#  Context
# -------------------
class Context(TypedDict):
    """Context parameters for the agent.

    Set these when creating assistants OR when invoking the graph.
    See: https://langchain-ai.github.io/langgraph/cloud/how-tos/configuration_cloud/
    """

    my_configurable_param: str
'''


'''
async def call_model(state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
    """Process input and returns output.

    Can use runtime context to alter behavior.
    """
    return {
        "changeme": "output from call_model. "
        f"Configured with {(runtime.context or {}).get('my_configurable_param')}"
    }
'''


# ------------------------
#  Conditional Function
# ------------------------
def check_status(state: State) -> Literal[0, 1, 2]:
    """Route after the Evaluator node.

    0 -> PR Writer (fix verified), 1 -> Coder (try again),
    2 -> Planner (retries exhausted, re-plan from scratch).
    """
    if state["status"] == Status.SUCCESS:
        return 0
    if state.get("retry_count", 0) > MAX_RETRIES:
        return 2
    return 1


# -----------------------
#  Define the graph
# -----------------------
graph = StateGraph(State)

# -------------------------------
#  Add each node and their edges
# -------------------------------
# Add the planner node and make an edge from the START
graph.add_node("Planner", planner)
graph.add_edge(START, "Planner")

# Add the coder node and make an edge from the Planner
graph.add_node("Coder", coder)
graph.add_edge("Planner", "Coder")

# Add the Test runner node and make an edge from the Coder
graph.add_node("Test Runner", test_runner)
graph.add_edge("Coder", "Test Runner")

# Add the Evaluator node and make an edge from the Test Runner
graph.add_node("Evaluator", evaluator)
graph.add_edge("Test Runner", "Evaluator")

# Add the PR Writer node and make a conditional edge from Evaluator
# -------------------------------------------
#  If STATUS is SUCCESS then move to PR Writer,
#  or if retry_count is above default max.
#  Otherwise go back to Coder
# -------------------------------------------
graph.add_node("PR Writer", pr_writer)
graph.add_conditional_edges(
    "Evaluator", check_status, {0: "PR Writer", 1: "Coder", 2: "Planner"}
)
graph.add_edge("PR Writer", END)

# ---------------------
#  Compile the Graph
# ---------------------
app = graph.compile()
