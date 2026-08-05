"""
src/tools/github_tools.py

Bridge layer exposing GitHub operations to the LLM.
Translates adapter responses/outcomes into Markdown response templates.
"""

# -----------------------------------------
#  Necessary Standard & LangChain Imports
# -----------------------------------------
import os
from pathlib import Path
from typing import List, Callable, Dict
from langchain_core.tools import tool, BaseTool

# -----------------------------------------
#  Abstract Interface & Result Types
# -----------------------------------------
from adapters.platform.base import BaseGitHubClient
from adapters.platform.types import GitHubClientResult, GitHubOpStatus

# -----------------------------------------
#  Helper / Prompt Engineering Utility
# -----------------------------------------
from utils.template_loader import load_response_tempate


# -----------------------------------------
#  Factory Function (Dependency Injection)
# -----------------------------------------
def github_tools(github_adapter: BaseGitHubClient) -> List[BaseTool]:
    """
    Factory that binds an adapter implementation to LangChain @tools decorators.
    Using parse_docstring to give more argument context to the LLM.
    Returns a list of tools to be bound to a LangGraph node(s).
    """

    # -----------------------------------------
    #  Tool 1: Get Issue Tool
    # -----------------------------------------
    @tool(parse_docstring=True)
    def get_issue(issue_number: int) -> str:
        """
        Retrieves the issue from GitHub that corresponds to issue_number.
        Returns issue information like title, body, state, and comments.

        Args:
            issue_number: The number for the issue that we are trying to get infromation about, in order to solve the bug/issue.
        """

        # Execute via abstract adapter
        result: GitHubClientResult = github_adapter.get_issue(issue_number=issue_number)

        # Then load the markdown response template
        template: str = load_response_tempate(
            skill="planner", tool_name="get_issues", section=result.status.value
        )

        # Format template placeholders with tool inputs and adapter results
        return template.format(
            issue_number=issue_number,
            issue_title=result.issue_dict["Issue Title"],
            issue_description=result.issue_dict["Issue Description"],
            issue_state=result.issue_dict["State"],
            issue_dict=result.issue_dict,
            comments=result.comments,
            raw_data=result.raw_data,
            error_details=result.error_details,
        )

    # --------------------------------------
    #  Tool 2: Create Pull Request Tool
    # --------------------------------------
    @tool(parse_docstring=True)
    def create_pull_request(
        title: str, body: str, head_branch: str, base_branch: str = "main"
    ) -> str:
        """
        Creates a PR/Pull Request with title, body, head_branch, and base_branch.

        Args:
            title: the title of the PR
            body: the body or description of the PR
            head_branch: The branch that has the fix
            base_branch: the default or main branch that the PR is merging into
        """

        # Execute via abstract adapter
        result: GitHubClientResult = github_adapter.create_pull_request(
            title=title, body=body, head_branch=head_branch, base_branch=base_branch
        )

        # Then load the markdown response template
        template: str = load_response_tempate(
            skill="pr_writer",
            tool_name="create_pull_request",
            section=result.status.value,
        )

        # Format template placeholders with tool inputs and adapter results
        return template.format(
            title=title,
            head_branch=head_branch,
            base_branch=base_branch,
            comments=result.comments,
            raw_data=result.raw_data,
            error_details=result.error_details,
        )

    # ----------------------------------------
    #  Tool 3: Get Default Branch Tool
    # ----------------------------------------
    @tool
    def get_default_branch() -> str:
        """
        Get the default or base branch.
        """

        # Execute via abstract adapter
        result: GitHubClientResult = github_adapter.get_default_branch()

        # Then load the markdown response template
        template: str = load_response_tempate(
            skill="pr_writer",
            tool_name="get_default_branch",
            section=result.status.value,
        )

        # Format template placeholders with tool inputs and adapter results
        return template.format(
            default_branch=result.default_branch,
            raw_data=result.raw_data,
            error_details=result.error_details,
        )

    # -------------------------------------
    #  Tool 4: For Post Issue Comment Tool
    # -------------------------------------
    @tool(parse_docstring=True)
    def post_issue_comment(issue_number: int, comment: str) -> str:
        """
        Post a comment onto the issue.

        Args:
            issue_number: The issue number
            comment: The comment that will be posted
        """

        # Execute via abstract adapter
        result: GitHubClientResult = github_adapter.post_issue_comment(
            issue_number=issue_number, comment=comment
        )

        # Then load the markdown response template
        template: str = load_response_tempate(
            skill="pr_writer",
            tool_name="post_issue_comment",
            section=result.status.value,
        )

        # Format template placeholders with tool inputs and adapter results
        return template.format(
            issue_number=issue_number,
            comment=comment,
            raw_data=result.raw_data,
            error_details=result.error_details,
        )

    return [get_issue, create_pull_request, get_default_branch, post_issue_comment]
