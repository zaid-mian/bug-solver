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

    # ...
    SUCCESS = "success"
    NO_MATCHES = "no_matches"
    DIRTY_WORKING_TREE = "dirty_working_tree"
    MERGE_CONFICT = "merge_conflict"

    UNKOWN_ERROR = "unknown_error"

    # ---------------------------------
    #  For subprocess call/run errors
    # ---------------------------------
    SUBPROCESS_ERROR = "subprocess_error"


@dataclass
class GitResult:
    status: GitOpStatus
    raw_data: Any = None
    error_details: Optional[str] = None
