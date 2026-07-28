# -------------------------------
#  Concrete Extension of
#  LocalGitRepo Abstract Class
# -------------------------------

import subprocess
from pathlib import Path

from base import BaseGitRepo
from security import sanitize_and_tokenize
from .types import GitResult, GitOpStatus


class SubprocessGitManager(BaseGitRepo):
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path

    def list_local_branches(self):
        try:
            result = subprocess.run(
                ["git", "branch", "--format=%(refname:short)"],
                capture_output=True,
                text=True,
                check=True,
            )
            return GitResult(
                status=GitOpStatus.LISTED_BRANCHES,
                raw_data=[
                    line.strip() for line in result.stdout.split("\n") if line.strip()
                ],
            )

        except subprocess.CalledProcessError as e:
            return GitResult(
                status=GitOpStatus.SUBPROCESS_ERROR, raw_data=e, error_details=e.stderr
            )

    def checkout_branch(self, branch_name: str, create_new: bool = True) -> GitResult:
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
            local_branches = self.list_local_branches().raw_data

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

                if branch_name == curr_branch.stdout.strip():
                    # no action needed then already on the correct branch
                    return GitResult(status=GitOpStatus.ALREADY_ON_BRANCH)

                else:
                    # else we just switch to the local branch
                    try:
                        subprocess.run(
                            ["git", "switch", branch_name],
                            capture_output=True,
                            text=True,
                            check=True,
                        )

                        return GitResult(
                            status=GitOpStatus.SWITCHED_TO_EXISTING,
                        )
                    except subprocess.CalledProcessError as e:
                        return GitResult(
                            status=GitOpStatus.SUBPROCESS_ERROR,
                            raw_data=e,
                            error_details=e.stderr,
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
                try:
                    subprocess.run(
                        ["git", "fetch", "--all"],
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

                # get the branches
                try:
                    all_branches = subprocess.run(
                        ["git", "branch", "-a"],
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

                # check if a branch with the same name exists remotely, if so then return to agent to get a new name
                if branch_name in all_branches.stdout.strip():
                    return GitResult(
                        status=GitOpStatus.BRANCH_EXISTS_REMOTELY,
                        raw_data=all_branches.stdout.strip(),
                        error_details=f"Branch '{branch_name}' exists outside the developer's local repo, should not use this branch or it's name.",
                    )

                else:
                    # then there are no branches with that name, and even though the new_branch variable was set to False we will create the new branch and switch to it
                    try:
                        subprocess.run(
                            ["git", "switch", "-c", branch_name],
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
            try:
                subprocess.run(
                    ["git", "fetch", "--all"],
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

            # get the branches
            try:
                all_branches = subprocess.run(
                    ["git", "branch", "-a"], capture_output=True, text=True, check=True
                )
            except subprocess.CalledProcessError as e:
                return GitResult(
                    status=GitOpStatus.SUBPROCESS_ERROR,
                    raw_data=e,
                    error_details=e.stderr,
                )

            if branch_name in all_branches.stdout.strip():
                return GitResult(
                    GitOpStatus.BRANCH_ALREADY_EXISTS,
                    raw_data=all_branches.stdout.strip(),
                    error_details=f"Branch '{branch_name}' already exists",
                )

            else:
                # then just create the branch
                try:
                    subprocess.run(
                        ["git", "switch", "-c", branch_name],
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

                return GitResult(
                    status=GitOpStatus.BRANCH_CREATED,
                )

    def apply_patch_or_commit(
        self, messages: str, files: list[str] = None
    ) -> GitResult:
        """Stages changes and creates a commit."""

        """ 
            We should already be on the correct branch (new or not),
            so we need commit the modified files.

            We could use git add . or git add -A,
            but it is safer to commit invidual files/changes - especially when making bug fixes            
        """

        # first stage the changes with git add
        # make the subprocess command with all files provided
        stage_command = ["git", "add"] + files

        try:
            subprocess.run(stage_command, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            # Check for the exit codes, to determine if the error is a git related error
            if e.returncode == 1 and ".gitignore" in e.stderr:
                # parse the e.stderr for the file(s) that are gitignored
                ignored_files = []
                file_flag = False
                for line in e.stderr.splitlines():
                    if line.endswith(":"):
                        file_flag = True

                    if line.startswith("hint"):
                        break

                    if file_flag:
                        ignored_files.append(line.replace("\n", ""))

                return GitResult(
                    status=GitOpStatus.GITIGNORE_ERROR,
                    raw_data=e,
                    error_details=e.stderr,
                    ignored_files=ignored_files,
                )
            elif e.returncode == 128 and "pathspec" in e.stderr:
                # this command only returns one unmatched file at a time, so we need to rerun it per file
                unmatched_files = []
                committed_files = []
                for file in files:
                    try:
                        subprocess.run(
                            ["git", "add", file],
                            capture_output=True,
                            text=True,
                            check=True,
                        )

                        committed_files.append(file)
                    except subprocess.CalledProcessError as e:
                        # parse the e.stderr for the file(s) that not matched
                        for line in e.stderr.splitlines():
                            parts = line.split("'")
                            unmatched_files.append(parts[1])

                return GitResult(
                    status=GitOpStatus.PATHSPEC_ERROR,
                    raw_data=e,
                    error_details=e.stderr,
                    unmatched_files=unmatched_files,
                    committed_files=committed_files,
                )

            elif (
                e.returncode == 128 or e.returncode == 1
            ) and "not a git repository" in e.stderr:
                return GitResult(
                    status=GitOpStatus.GITREPO_ERROR, raw_data=e, error_details=e.stderr
                )

            # otherwise give the simple subprocess error
            return GitResult(
                status=GitOpStatus.SUBPROCESS_ERROR,
                raw_data=e,
                error_details=e.stderr,
            )

        # check staging status
        git_result_status = self.git_status()

        if git_result_status.status != GitOpStatus.GIT_STATUS:
            return GitResult(
                status=GitOpStatus.FAILED_STATUS,
                raw_data=git_result_status.raw_data,
                error_details=git_result_status.error_details,
            )
        # else it should be clean and it continues to commit

        # next commit with a message
        try:
            commit_result = subprocess.run(
                ["git", "commit", "-m", messages],
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            if e.returncode == 1 and "empty commit message" in e.stderr:
                return GitResult(
                    status=GitOpStatus.MISSING_COMMIT_MESSAGE,
                    raw_data=e,
                    error_details=e.stderr,
                )
            if e.returncode == 1 and e.stderr == "":
                return GitResult(status=GitOpStatus.CLEAN_TREE, raw_data=e)
            elif (
                e.returncode == 128 or e.returncode == 1
            ) and "not a git repository" in e.stderr:
                return GitResult(
                    status=GitOpStatus.GITREPO_ERROR, raw_data=e, error_details=e.stderr
                )

            # otherwise give the simple subprocess error
            return GitResult(
                status=GitOpStatus.SUBPROCESS_ERROR,
                raw_data=e,
                error_details=e.stderr,
            )

        # okay then return the STAGED_AND_COMMITTED GitResult
        return GitResult(
            status=GitOpStatus.STAGED_AND_COMMITTED, raw_data=commit_result
        )

    def push(self, branch_name: str, remote: str = "origin") -> GitResult:
        """Pushes current branch to remote."""

        try:
            pushed_result = subprocess.run(
                ["git", "push", remote, branch_name],
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            # check for known git errors via return code and error response
            if e.returncode == 1 and "branch is behind" in e.stderr:
                return GitResult(
                    status=GitOpStatus.BEHIND_BRANCH, raw_data=e, error_details=e.stderr
                )
            elif e.returncode == 1 and "non-fast-forward" in e.stderr:
                return GitResult(
                    status=GitOpStatus.NON_FAST_FORWARD,
                    raw_data=e,
                    error_details=e.stderr,
                )
            elif (
                e.returncode == 128 or e.returncode == 1
            ) and "no upstream branch" in e.stderr:
                # then run the -u in the push command
                try:
                    pushed_result = subprocess.run(
                        ["git", "push", "-u", remote, branch_name],
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                except subprocess.CalledProcessError as e:
                    return GitResult(
                        status=GitOpStatus.FAILED_UPSTREAM_PUSH,
                        raw_data=e,
                        error_details=e.stderr,
                    )

                return GitResult(
                    status=GitOpStatus.UPSTREAM_BRANCH,
                    raw_data=pushed_result,
                    error_details=e.stderr,
                )

            elif e.returncode == 128 and (
                "repository not found" in e.stderr
                or "no configured push destination" in e.stderr
                or "does not appear to be a git repository" in e.stderr
            ):
                return GitResult(
                    status=GitOpStatus.REPOSITORY_NOT_FOUND,
                    raw_data=e,
                    error_details=e.stderr,
                )

            # otherwise give the simple subprocess error
            return GitResult(
                status=GitOpStatus.SUBPROCESS_ERROR,
                raw_data=e,
                error_details=e.stderr,
            )

        # okay then return the PUSHED_TO_REMOTE_BRANCH GitResult
        return GitResult(
            status=GitOpStatus.PUSHED_TO_REMOTE_BRANCH, raw_data=pushed_result
        )

    def pull(self, branch_name: str, remote: str = "origin") -> GitResult:
        """Pulls remote branch to current branch."""

        try:
            pull_result = subprocess.run(
                ["git", "pull", remote, branch_name],
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            if (e.returncode == 1 or e.returncode == 128) and (
                "conflict" in e.stderr or "CONFLICT" in e.stderr
            ):
                return GitResult(
                    status=GitOpStatus.MERGE_CONFICT, raw_data=e, error_details=e.stderr
                )
            elif (e.returncode == 1 or e.returncode == 128) and (
                "overwritten" in e.stderr or "local changes" in e.stderr
            ):
                return GitResult(
                    status=GitOpStatus.LOCAL_CHANGES_CONFLICT,
                    raw_data=e,
                    error_details=e.stderr,
                )
            elif (
                e.returncode == 128 or e.returncode == 1
            ) and "no tracking information" in e.stderr:
                return GitResult(
                    status=GitOpStatus.NO_UPSTREAM_SET,
                    raw_data=e,
                    error_details=e.stderr,
                )
            elif e.returncode == 128 and (
                "find remote ref" in e.stderr
                or " '{remote}' does not appear to be a git repository" in e.stderr
            ):
                return GitResult(
                    status=GitOpStatus.MISSING_BRANCH_OR_REFERENCE,
                    raw_data=e,
                    error_details=e.stderr,
                )

            # otherwise give the simple subprocess error
            return GitResult(
                status=GitOpStatus.SUBPROCESS_ERROR,
                raw_data=e,
                error_details=e.stderr,
            )

        # okay then return the PULLED_FROM_REMOTE_BRANCH GitResult
        return GitResult(
            status=GitOpStatus.PULLED_FROM_REMOTE_BRANCH, raw_data=pull_result
        )

    def search_repo_text(self, text_pattern: str) -> GitResult:
        """Performs semantic keyword, symbol, or error string searches"""

        try:
            grep_result = subprocess.run(
                ["git", "grep", "-i", "-n", text_pattern, "--", "src/**/*.py", "src/**/*.md"],
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            if e.returncode == 1 and e.stderr == "":
                return GitResult(
                    status=GitOpStatus.NO_MATCHES, raw_data=e, error_details=e.stderr
                )

            return GitResult(
                status=GitOpStatus.SUBPROCESS_ERROR, raw_data=e, error_details=e.stderr
            )

        return GitResult(status=GitOpStatus.FOUND_MATCHES, raw_data=grep_result)

    def git_status(self) -> GitResult:
        """Performs git status command to check staging and possible merging conflicts."""
        try:
            status_result = subprocess.run(
                ["git", "status"], capture_output=True, text=True, check=True
            )
        except subprocess.CalledProcessError as e:
            # check via return code
            if e.returncode == 1 and "unmerged paths" in e.stderr:
                return GitResult(
                    status=GitOpStatus.MERGE_CONFICT, raw_data=e, error_details=e.stderr
                )

            # otherwise give the simple subprocess error
            return GitResult(
                status=GitOpStatus.SUBPROCESS_ERROR,
                raw_data=e,
                error_details=e.stderr,
            )

        return GitResult(status=GitOpStatus.GIT_STATUS, raw_data=status_result)

    def run_git_command(
        self, args_str: str, timeout_seconds: float = 30.0
    ) -> GitResult:
        """This is a Fallback or Escape Hatch Tool in case the standard tools are not sufficient for complex Git conflicts or issues."""
        # First validate and tokenize
        is_safe, tokens, error_msg = sanitize_and_tokenize(args_str)
        if not is_safe:
            return GitResult(
                status=GitOpStatus.FORBIDDEN_ARGS,
                raw_data=tokens,
                error_details=error_msg,
            )

        # Then build the executable array
        command = ["git"] + tokens

        # Then execute without shell=True
        try:
            fallback_result = subprocess.run(
                command,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                shell=False,
                check=True,
            )

        except subprocess.TimeoutExpired:
            return GitResult(
                status=GitOpStatus.TIMEOUT,
                error_details=f"Command 'git {args_str}' timed out after {timeout_seconds} seconds.",
            )

        except subprocess.CalledProcessError as e:
            return GitResult(
                status=GitOpStatus.SUBPROCESS_ERROR, raw_data=e, error_details=e.stderr
            )

        return GitResult(
            status=GitOpStatus.EXECUTED_FALLBACK_COMMAND, raw_data=fallback_result
        )
