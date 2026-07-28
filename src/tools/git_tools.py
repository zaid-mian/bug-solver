"""
src/tools/git_tools.py

Bridge layer exposing Git operations to the LLM.
Translates adapter responses/outcomes into Markdown response templates.
"""

# -----------------------------------------
#  Necessary Standard & LangChain Imports
# -----------------------------------------
from typing import List, Callable
from langchain_core.tools import tool, BaseTool

# -----------------------------------------
#  Abstract Interface & Result Types
# -----------------------------------------
from adapters.git.base import BaseGitRepo
from adapters.git.types import GitResult, GitOpStatus

# -----------------------------------------
#  Helper / Prompt Engineering Utility
# -----------------------------------------
from utils.template_loader import load_response_tempate


# -----------------------------------------
#  Factory Function (Dependency Injection)
# -----------------------------------------
def git_tools(git_adapter: BaseGitRepo) -> List[BaseTool]:
    """
    Factory that binds an adapter implementation to LangChain @tools decorators.
    Using parse_docstring to give more argument context to the LLM.
    Returns a list of tools to be bound to a LangGraph node.
    """

    # -------------------------------------------------------
    #  Tools 1 and 2: Local Branch List and Branch Checkout
    # -------------------------------------------------------
    @tool
    def list_local_branches() -> str:
        """
        Retrieves all the branches on the developer's local repository.
        Use to get an idea of current branches, features implemented, bugs fixed, and available branch names.
        """

        # Execute via abstract adapter
        result: GitResult = git_adapter.list_local_branches()

        # Then load the markdown response template
        template: str = load_response_tempate(
            skill="planner", tool_name="local_branches", section=result.status.value
        )

        # Format template placeholders with tool inputs and adapter results
        return template.format(
            local_branches=result.raw_data,
            raw_data=result.raw_data,
            error_details=result.error_details,
        )

    @tool(parse_docstring=True)
    def checkout_branch(branch_name: str, create_new: bool = False) -> str:
        """
        Switches working directory to specified branch or creates a new one.

        Args:
            branch_name: Target branch name (e.g., 'fix/issue-123')
            create_new: Set to True if creating a new branch
        """

        # Execute via abstract adapter
        result: GitResult = git_adapter.checkout_branch(
            branch_name=branch_name, create_new=create_new
        )

        # Then load the markdown response template
        template: str = load_response_tempate(
            skill="planner", tool_name="branch_checkout", section=result.status.value
        )

        # Format template placeholders with tool inputs and adapter results
        return template.format(
            branch_name=branch_name,
            all_branches=result.raw_data,
            existing_branches=result.raw_data,
            raw_data=result.raw_data,
            error_details=result.error_details,
        )

    # ----------------------------------------
    #  Tool 3: Patch Staging and Commit Tool
    # ----------------------------------------
    @tool(parse_docstring=True)
    def stage_patch_and_commit(messages: str, files: list[str] = None) -> str:
        """
        Stages files (git add) that were modified to address the problem, then commits those staged changes to local branch.

        Args:
            messages: A message for the commit (e.g. 'git commit -m "Some relevant and detailed message')
            files: List of file names or file paths, depending on the working directory
        """

        # Execute via abstract adapter
        result: GitResult = git_adapter.apply_patch_or_commit(
            messages=messages, files=files
        )

        # Then load the markdown response template
        template: str = load_response_tempate(
            skill="planner", tool_name="commit", section=result.status.value
        )

        # Format template placeholders with tool inputs and adapter results
        return template.format(
            messages=messages,
            files=files,
            commit_result=result.raw_data,
            ignored_files=result.ignored_files,
            unmatched_files=result.unmatched_files,
            committed_files=result.committed_files,
            raw_data=result.raw_data,
            error_details=result.error_details,
        )

    # -----------------------------------------
    #  Tool 4: Push to Remote Branch
    # -----------------------------------------
    @tool(parse_docstring=True)
    def push(branch_name: str, remote: str = "origin") -> str:
        """
        Pushes current branch to remote branch.

        Args:
            branch_name: Target branch name (e.g., 'fix/issue-123')
            remote: The label for the target remote GitHub repository
        """

        # Execute via abstract adapter
        result: GitResult = git_adapter.push(branch_name=branch_name, remote=remote)

        # Then load the markdown response template
        template: str = load_response_tempate(
            skill="planner", tool_name="push", section=result.status.value
        )

        # Format template placeholders with tool inputs and adapter results
        return template.format(
            branch_name=branch_name,
            remote=remote,
            raw_data=result.raw_data,
            error_details=result.error_details,
        )

    # -----------------------------------------
    #  Tool 5: Pull from Remote Branch
    # -----------------------------------------
    @tool(parse_docstring=True)
    def pull(branch_name: str, remote: str = "origin") -> str:
        """
        Pulls from remote branch

        Args:
            branch_name: Target branch name (e.g., 'fix/issue-123')
            remote: The label for the target remote GitHub repository
        """

        # Execute via abstract adapter
        result: GitResult = git_adapter.pull(branch_name=branch_name, remote=remote)

        # Then load the markdown response template
        template: str = load_response_tempate(
            skill="planner", tool_name="pull", section=result.status.value
        )

        # Format template placeholders with tool inputs and adapter results
        return template.format(
            branch_name=branch_name,
            remote=remote,
            raw_data=result.raw_data,
            error_details=result.error_details,
        )
