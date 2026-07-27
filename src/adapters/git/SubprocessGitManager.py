# -------------------------------
#  Concrete Extension of
#  LocalGitRepo Abstract Class
# -------------------------------

import subprocess

from .base import BaseGitRepo
from .types import GitResult, GitOpStatus


class SubprocessGitManager(BaseGitRepo):
    def list_local_branches(self):
        try:
            result = subprocess.run(
                ["git", "branch", "--format=%(refname:short)"],
                capture_output=True,
                text=True,
                check=True,
            )
            return [line.strip() for line in result.stdout.split("\n") if line.strip()]

        except subprocess.CalledProcessError as e:
            return (
                f"Git command failed with exit code {e.returncode}"
                f"Error details: {e.stderr}"
            )

    def checkout_branch(self, branch_name: str, create_new: bool = True) -> str:
        """Switches or creates a new branch."""
        # first check if we are creating a new branch
        """
            if not then we need to check if the branch name matches the current branch,
                to determine if we need to switch or not, or if there is a contradiction then create a new branch

            else if we are creating a new branch we need to check if the branch name already exists or now,
                if so prompt for new name
                else create the new branch
        """
        if not create_new:
            # get all branches on local git
            local_branches = self.list_local_branches()

            # first check if it exists at all
            if branch_name in local_branches:
                # get current branch
                curr_branch = ""
                try:
                    curr_branch = subprocess.run(
                        ["git", "branch", "--show-current"],
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                except subprocess.CalledProcessError as e:
                    return GitResult(
                        status=GitOpStatus.SUBPROCESS_ERROR,
                        raw_data=e,
                        error_details=e.stderr,
                    )

                if branch_name == curr_branch:
                    # no action needed then already on the correct branch
                    return GitResult(status=GitOpStatus.ALREADY_ON_BRANCH)

                else:
                    # else we just switch to the local branch
                    switch_result = subprocess.run(
                        ["git", "switch", branch_name], capture_output=True, text=True
                    )

                    return GitResult(
                        status=GitOpStatus.SWITCHED_TO_EXISTING,
                    )

            else:
                """
                else then local developer has never contributed to the branch with the name branch_name
                but there may be a branch with such a name already that someone else has created, so check for that first
                        *** we will never add to another dev's branch
                    if so then we need to get another branch name
                else we just create the branch locally
                """

                # first check for the remote branches and their names
                subprocess.run(
                    ["git", "fetch", "--all"], capture_output=True, text=True
                )

                # get the branches
                all_branches = subprocess.run(
                    ["git", "branch", "-a"], capture_output=True, text=True
                )

                # check if a branch with the same name exists remotely, if so then return to agent to get a new name
                if branch_name in all_branches:
                    return GitResult(
                        status=GitOpStatus.BRANCH_EXISTS_REMOTELY,
                        raw_data=all_branches,
                        error_details="Branch '{branch_name}' exists outside the developer's local repo, should not use this branch or it's name.",
                    )

                else:
                    # then there are no branches with that name, and even though the new_branch variable was set to False we will create the new branch and switch to it
                    subprocess.run(
                        ["git", "switch", "-c", branch_name],
                        capture_output=True,
                        text=True,
                    )

                    return GitResult(
                        status=GitOpStatus.BRANCH_CREATED,
                    )
        else:
            """
            Otherwise if we are supposed to create a new branch
                first check if that branch already exists,
                    if so then we need another branch name
                if it doesn't then just create the branch
            """

            # get all branches
            subprocess.run(["git", "fetch", "--all"], capture_output=True, text=True)

            # get the branches
            all_branches = subprocess.run(
                ["git", "branch", "-a"], capture_output=True, text=True
            )

            if branch_name in all_branches:
                return GitResult(
                    GitOpStatus.BRANCH_ALREADY_EXISTS,
                    raw_data=all_branches,
                    error_details="Branch '{branch_name}' already exists",
                )

            else:
                # then just create the branch
                subprocess.run(
                    ["git", "switch", "-c", branch_name],
                    capture_output=True,
                    text=True,
                )

                return GitResult(
                    status=GitOpStatus.BRANCH_CREATED,
                )

    def apply_patch_or_commit(self, messages: str, files: list[str] = None) -> str:
        """Stages changes and creates a commit."""
        return "Placeholder"

    def push(self, branch_name: str, remote: str = "origin") -> str:
        """Pushes current branch to remote."""
        return "Placeholder"

    def search_repo_text(self, text_pattern: str) -> str:
        """Performs semantic keyword, symbol, or error string searches"""
        return "Placeholder"
