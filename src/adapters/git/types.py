# -------------------------------------
#  Adapter Type: Local Git Operations
# -------------------------------------

from enum import Enum
from dataclasses import dataclass
from typing import Any, Optional


class GitOpStatus(Enum):
    # ---------------------------
    #  For checkout_branch
    # ---------------------------
    # we do not need to create a new branch
    SWITCHED_TO_EXISTING = "switched_to_existing"
    ALREADY_ON_BRANCH = "already_on_branch"
    BRANCH_EXISTS_REMOTELY = "branch_exists_remotely"

    # we need to create a new branch, so cannot accept an existing branch
    BRANCH_ALREADY_EXISTS = "branch_already_exists"

    # For general branch creation and switch
    BRANCH_CREATED = "branch_created"

    # ---------------------------
    #  For apply_patch_or_commit
    # ---------------------------
    STAGED_AND_COMMITTED = "staged_and_committed"

    # errors
    GITIGNORE_ERROR = "gitignore_error"
    PATHSPEC_ERROR = "pathspec_error"
    GITREPO_ERROR = "gitrepo_error"
    CLEAN_TREE = "clean_tree"
    MISSING_COMMIT_MESSAGE = "missing_commit_message"
    FAILED_STATUS = "failed_status"

    # -----------------------------
    #  For push (to remote branch)
    # -----------------------------
    PUSHED_TO_REMOTE_BRANCH = "pushed_to_remote_branch"

    # errors
    BEHIND_BRANCH = "behind_branch"
    NON_FAST_FORWARD = "non_fast_forward"
    UPSTREAM_BRANCH = "upstream_branch"
    FAILED_UPSTREAM_PUSH = "failed_upstream_push"
    REPOSITORY_NOT_FOUND = "repository_not_found"

    # -------------------------------
    #  For pull (from remote branch)
    # -------------------------------
    PULLED_FROM_REMOTE_BRANCH = "pulled_from_remote_branch"

    # errors
    MERGE_CONFICT = "merge_conflict"
    LOCAL_CHANGES_CONFLICT = "local_changes_conflict"
    NO_UPSTREAM_SET = "no_upstream_set"
    MISSING_BRANCH_OR_REFERENCE = "missing_branch_or_reference"

    # ...
    NO_MATCHES = "no_matches"
    DIRTY_WORKING_TREE = "dirty_working_tree"

    # ------------------------
    #  For Git Status
    # ------------------------
    GIT_STATUS = "git_status"

    # ---------------------------------------------------
    #  For the Escape Hatch Tool/Fallback Command Tool
    # ---------------------------------------------------
    EXECUTED_FALLBACK_COMMAND = "executed_fallback_command"

    # errors
    FORBIDDEN_ARGS = "forbidden_args"
    TIMEOUT = "timeout"

    # ---------------------------------
    #  For subprocess call/run errors
    # ---------------------------------
    # this equivalent to the unhandled or unkown errors
    SUBPROCESS_ERROR = "subprocess_error"


@dataclass
class GitResult:
    status: GitOpStatus
    raw_data: Any = None
    error_details: Optional[str] = None
