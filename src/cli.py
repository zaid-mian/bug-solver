import os
import typer
from typing import Annotated, Optional
from pathlib import Path
from git import Repo, InvalidGitRepositoryError

from constants import Status
from agent.graph import app

# ----------------------
#  Example Commands
# ----------------------
'''
# Mode 1: Fetch issue from GitHub, fix locally, push & PR
bugsolver run 142 --auto-pr

# Mode 2: Fix a local bug described in prose or a file, local-only (no PR)
bugsolver run "Fix memory leak in parser" --local-only

# Mode 3: Dry-run mode (make code changes locally, but don't commit/push)
bugsolver run 142 --dry-run
'''

# -----------------------
#  Define the typer cli
# -----------------------
cli = typer.Typer(help="CLI tool for running LangGraph Bug Solver Agent")

# ---------------------------------
#  Function to Get Local Git Repo
# ---------------------------------
def get_repo_root() -> Path:
    """ Finds the root directory of the current local git repository """
    try:
        repo = Repo(".", search_parent_directories=True)
        return Path(repo.working_tree_dir)
    except InvalidGitRepositoryError:
        typer.echo("Error: Command not run inside a valid git repository.", err=True)
        raise typer.Exit(code=1)

# --------------------------------
#  Command Function to Run Agent
# --------------------------------
'''
Args:
    target: required argument of either issue number or local bug description
    repo_path: optional path of the local repository
    new_branch: optional boolean to either toggle the agent to create a new branch or not (use the current one the developer is on)
    auto_pr: optional boolean to either toggle the agent to PR or not
    local_only: optional boolean to either toggle the agent to push to git/github or not
'''
@cli.command()
def run(
    target: Annotated[
        str,
        typer.Argument(
            help="Issue number or local bug description."
        )
    ],

    repo_path: Annotated[
        Optional[Path],
        typer.Option("--path", "-p", help="Path to local repository.")
    ] = None, # standard default

    new_branch: Annotated[
        bool,
        typer.Option("--new-branch/--no-new-branch", help="To define if the Bug Solver Agent will create a new branch or use the one the developer/user is currently on.")
    ] = True,

    auto_pr: Annotated[
        bool,
        typer.Option("--pr/--no-pr", help="Automatically create a Pull Request on GitHub.")
    ] = True,

    local_only: Annotated[
        bool,
        typer.Option("--local-only", help="Keep changes local without pushing.")
    ] = False
):
    """ Run the Bug Solver Agent on a local repository or remote GitHub issue."""

    # 1: resolve target type
    if target.isdigit():
        resolved_issue_id: Optional[int] = int(target)

        # this is not necessarily true, since there is one in GitHub, but it will probably be read else where
        bug_description: Optional[str] = None
        is_remote_issue = True
    else:
        resolved_issue_id: Optional[int] = None
        bug_description: Optional[str] = target
        is_remote_issue = False

    # 2: resolve repository path
    target_repo_path = repo_path or get_repo_root()

    # 3: Git and GitHub Manager
    git_manager = SubprocessGitManager(repo_path=target_repo_path)

    github_token = os.environ.get("GITHUB_TOKEN")
    github_manager = PyGithubManager(token=github_token) if github_token else None

    # 4: Construct RunnableConfig (Execution Environment)
    config = {
        "configurable": {
            "git_manager": git_manager,
            "github_manager": github_manager,
            "execution_mode": {
                "auto_pr": auto_pr and not local_only,
                "new_branch": new_branch,
                "local_only": local_only,
                "is_remote_issue": resolved_issue_id is not None
            }
        }
    }

    # 5: Construct Initial Graph State
    initial_state = {
        "issue_id": resolved_issue_id,
        "issue_description": bug_description,
        "repo_path": str(target_repo_path),
        "status": Status.IN_PROGESS
    }

    # 6: Invoke the LangGraph Agent
    typer.echo(f"Starting Bug Solver Agent on repository: {target_repo_path}")
    result = app.invoke(initial_state, config=config)

    typer.echo(f"Workflow finished. Status {result.get('status')}")

if __name__ == "__main__":
    cli()
