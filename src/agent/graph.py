"""LangGraph single-node graph template.

Returns a predefined response. Replace logic and configuration as needed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, TypedDict, List, Optional, Literal
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.runtime import Runtime

# -------------------
#  Import Constants
# -------------------
from constants import MAX_RETRIES, Status

# -------------------
#  Context
# -------------------
class Context(TypedDict):
    """Context parameters for the agent.

    Set these when creating assistants OR when invoking the graph.
    See: https://langchain-ai.github.io/langgraph/cloud/how-tos/configuration_cloud/
    """

    my_configurable_param: str

# -------------------
#  State Class
# -------------------
@dataclass
class State(TypedDict):
    """Input state for the agent.

    Defines the initial structure of incoming data.
    See: https://langchain-ai.github.io/langgraph/concepts/low_level/#state
    """

    # The bug report or error stack trace
    issue_description: str

    # Paths and code snippets from repo
    relevant_files: List[str]

    # The plan
    fix_plan: Optional[str]

    # Generated code fix/diff
    patch_code: Optional[str]

    # Log/errors from running tests
    test_output: Optional[str]

    # Integer tracking iteration cycles, to prevent infinite loops
    retry_count: int

    # Status
    status: Status

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
#  Planner Node Function
# ------------------------
async def planner(state: State, runtime: Runtime[Context]):
    return ("Placeholder")

# ----------------------
#  Coder Node Function
# ----------------------
async def coder(state: State, runtime: Runtime[Context]):
    return ("Placeholder")

# ----------------------------
#  Test Runner Node Function
# ----------------------------
async def test_runner(state: State, runtime: Runtime[Context]):
    return ("Placeholder")

# ---------------------------
#  Coder Evaluator Function
# ---------------------------
async def evaluator(state: State, runtime: Runtime[Context]):
    return ("Placeholder")

# ---------------------------
#  Coder PR Writer Function
# ---------------------------
async def pr_writer(state: State, runtime: Runtime[Context]):
    return ("Placeholder")

# ------------------------
#  Conditional Function
# ------------------------
def check_status(state: State) -> Literal[0, 1, 2]:
    if Status.FAILED in state['status']:
        return 1
    elif Status.SUCCESS in state['status']:
        return 0

    # IN PROGRESS
    if state['retry_count'] > MAX_RETRIES:
        return 2

# -----------------------
#  Define the graph
# -----------------------
graph = StateGraph(State, context_schema=Context)

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
    "Evaluator",
    check_status,
    {
        0: "PR Writer",
        1: "Coder",
        2: "Planner"
    }
)
graph.add_edge("PR Writer", END)

# ---------------------
#  Compile the Graph
# ---------------------
graph = graph.compile()
