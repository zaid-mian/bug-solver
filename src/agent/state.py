"""Shared agent state schema.

Lives in its own module so both the graph definition (agent/graph.py) and
the node implementations (agent/nodes.py) can import it without creating
a circular import.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated

from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
from typing_extensions import TypedDict

from constants import Status


class State(TypedDict):
    """Input state for the agent."""

    # The issue id, if there is one
    issue_id: int | None

    # The bug report, issue description, or error stack trace
    issue_description: str

    # The repository name and path
    repo_name: str

    repo_path: str | os.PathLike | Path

    # Paths and code snippets from repo
    relevant_files: list[str]

    # The plan
    fix_plan: str | None

    # Generated code fix/diff
    patch_code: str | None

    # Log/errors from running tests
    test_output: str | None

    # Integer tracking iteration cycles, to prevent infinite loops
    retry_count: int

    # Status
    status: Status

    # message history
    messages: Annotated[list[BaseMessage], add_messages]
