import os
import time
from pathlib import Path
from typing import Annotated

import typer
from git import InvalidGitRepositoryError, Repo

from adapters.filesystem.base import BaseFileSystemTools
from adapters.filesystem.PATHLIBPythonManager import PATHLIBPythonManager
from adapters.git.base import BaseGitRepo
from adapters.git.SubprocessGitManager import SubprocessGitManager
from adapters.platform.PyGithubManager import PyGithubManager
from adapters.platform.types import GitHubOpStatus
from adapters.testing.SubprocessPytestManager import SubprocessPytestManager
from agent.graph import app
from constants import Status

# ----------------------
#  Example Commands
# ----------------------
"""
# Mode 1: Fetch issue from GitHub, fix locally, push & PR
bugsolver run 142 --auto-pr

# Mode 2: Fix a local bug described in prose or a file, local-only (no PR)
bugsolver run "Fix memory leak in parser" --local-only

# Mode 3: Dry-run mode (make code changes locally, but don't commit/push)
bugsolver run 142 --dry-run
"""

# -----------------------
#  Define the typer cli
# -----------------------
cli = typer.Typer(help="CLI tool for running LangGraph Bug Solver Agent")


# ---------------------------------
#  Function to Get Local Git Repo
# ---------------------------------
def get_repo_root() -> Path:
    """Finds the root directory of the current local git repository"""
    try:
        repo = Repo(".", search_parent_directories=True)
        return Path(repo.working_tree_dir)
    except InvalidGitRepositoryError:
        typer.echo("Error: Command not run inside a valid git repository.", err=True)
        raise typer.Exit(code=1)


# --------------------------------
#  Command Function to Run Agent
# --------------------------------
"""
Args:
    target: required argument of either issue number or local bug description
    repo_path: optional path of the local repository
    new_branch: optional boolean to either toggle the agent to create a new branch or not (use the current one the developer is on)
    auto_pr: optional boolean to either toggle the agent to PR or not
    local_only: optional boolean to either toggle the agent to push to git/github or not
"""


@cli.command()
def run(
    target: Annotated[
        str, typer.Argument(help="Issue number or local bug description.")
    ],
    repo_name: Annotated[
        str | None,
        typer.Option(
            "--name",
            "-n",
            help="The GitHub repository as owner/repo (needed for issue mode and PRs).",
        ),
    ] = None,
    repo_path: Annotated[
        Path | None, typer.Option("--path", "-p", help="Path to local repository.")
    ] = None,  # standard default
    new_branch: Annotated[
        bool,
        typer.Option(
            "--new-branch/--no-new-branch",
            help="To define if the Bug Solver Agent will create a new branch or use the one the developer/user is currently on.",
        ),
    ] = True,
    auto_pr: Annotated[
        bool,
        typer.Option(
            "--pr/--no-pr", help="Automatically create a Pull Request on GitHub."
        ),
    ] = True,
    local_only: Annotated[
        bool, typer.Option("--local-only", help="Keep changes local without pushing.")
    ] = False,
    provider: Annotated[
        str | None,
        typer.Option(
            "--provider",
            help="LLM provider: ollama (default), anthropic, openai, groq, openrouter.",
        ),
    ] = None,
    model: Annotated[
        str | None,
        typer.Option(
            "--model",
            "-m",
            help="Model name (e.g. qwen2.5-coder:7b, claude-3-5-sonnet-latest, gpt-4o).",
        ),
    ] = None,
):
    """Run the Bug Solver Agent on a local repository or remote GitHub issue."""

    # 1: resolve target type
    if target.isdigit():
        resolved_issue_id: int | None = int(target)
        bug_description: str | None = None
    else:
        resolved_issue_id: int | None = None
        bug_description: str | None = target

    # 2: resolve repository path
    target_repo_path = repo_path or get_repo_root()

    # 3: Git, Workspace/Filesystem, and GitHub Manager
    git_manager: BaseGitRepo = SubprocessGitManager(repo_path=target_repo_path)

    workspace_manager: BaseFileSystemTools = PATHLIBPythonManager(root=target_repo_path)

    github_token = os.environ.get("GITHUB_TOKEN")
    github_manager = (
        PyGithubManager(token=github_token, repo_name=repo_name)
        if github_token and repo_name
        else None
    )

    # check if the initialization of the GitHub client failed was a success
    if github_manager is not None and github_manager.status != GitHubOpStatus.INIT_GITHUB_CLIENT:
        # then raise an error message
        typer.echo(
            (
                f"The initialization of the GitHub Client Manager failed: [{github_manager.status}: {github_manager.error_details}]",
                f"Raw data: {github_manager.raw_data}"
                f"Make sure the repository name is owner/repo as in GitHub."
                f"Make sure to have the valid credentials/",
            ),
            err=True,
        )

    # 3b: test runner adapter (scoped to the target repo so test commands
    # can never escape into the agent's own working directory)
    test_manager = SubprocessPytestManager(repo_path=target_repo_path)

    # 3c: put the agent on a dedicated fix branch so the target repo's
    # current branch is never polluted
    branch_name: str | None = None
    if new_branch and not local_only:
        branch_name = f"bugsolver/fix-{resolved_issue_id or 'local'}-{int(time.time())}"
        branch_result = git_manager.checkout_branch(branch_name, create_new=True)
        typer.echo(f"Created fix branch: {branch_name} ({branch_result.status})")

    # 3d: the LLM: defaults to local Ollama, or uses Anthropic / OpenAI / Groq / OpenRouter
    from utils.model_factory import get_model
    from utils.ui import (
        print_banner,
        print_node_result,
        print_node_start,
        print_summary_card,
    )

    llm = get_model(provider=provider, model_name=model)

    # 4: Construct RunnableConfig (Execution Environment)
    config = {
        "configurable": {
            "model": llm,
            "adapters": {
                "git_manager": git_manager,
                "workspace_manager": workspace_manager,
                "github_manager": github_manager,
                "test_manager": test_manager,
            },
            "execution_mode": {
                "auto_pr": auto_pr and not local_only,
                "new_branch": new_branch,
                "local_only": local_only,
                "is_remote_issue": resolved_issue_id is not None,
            },
        }
    }

    # 5: Construct Initial Graph State
    initial_state = {
        "issue_id": resolved_issue_id,
        "issue_description": bug_description,
        "repo_name": repo_name,
        "repo_path": str(target_repo_path),
        "status": Status.IN_PROGRESS,
        # the non-optional states with empty values
        "relevant_files": [],
        "retry_count": 0,
        "messages": [],
    }

    # 6: Stream the LangGraph Agent with Rich UI
    import asyncio

    mode_str = "Local (No Push/PR)" if local_only else ("Auto PR" if auto_pr else "Branch Only")
    print_banner(
        repo_path=target_repo_path,
        provider=provider,
        model=model,
        mode=mode_str,
    )

    async def _stream_workflow():
        final_state: dict = dict(initial_state)
        nodes_executed: list[str] = []
        step_idx = 1

        async for chunk in app.astream(initial_state, config=config):
            for node_name, state_update in chunk.items():
                nodes_executed.append(node_name)
                final_state.update(state_update)

                print_node_start(node_name, step_num=step_idx, total_steps=5)

                diff_snippet = None
                if node_name == "Coder":
                    try:
                        status_res = git_manager.git_status()
                        if status_res and status_res.raw_data:
                            diff_snippet = str(status_res.raw_data)
                    except Exception:
                        pass

                print_node_result(node_name, state_update, diff_snippet=diff_snippet)
                step_idx += 1

        return final_state, nodes_executed

    try:
        final_state, nodes_executed = asyncio.run(_stream_workflow())
        final_status = final_state.get("status", "COMPLETED")
    except Exception as e:
        final_status = f"FAILED ({e})"
        nodes_executed = []
        final_state = {}

    print_summary_card(
        repo_path=str(target_repo_path),
        task_desc=bug_description or f"GitHub Issue #{resolved_issue_id}",
        final_status=str(final_status),
        nodes_executed=nodes_executed,
        retries=final_state.get("retry_count", 0),
        branch_name=branch_name,
        pr_url=final_state.get("pr_url"),
    )


if __name__ == "__main__":
    cli()
