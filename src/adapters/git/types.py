# -------------------------------------
#  Adapter Type: Local Git Operations
# -------------------------------------

from enum import Enum
from dataclasses import dataclass
from typing import Any, Optional


class GitOpStatus(Enum):
    # For checkout_branch
    # we do not need to create a new branch
    SWITCHED_TO_EXISTING = "switched_to_existing"
    ALREADY_ON_BRANCH = "already_on_branch"
    BRANCH_EXISTS_REMOTELY = "branch_exists_remotely"

    # we need to create a new branch, so cannot accept an existing branch
    BRANCH_ALREADY_EXISTS = "branch_already_exists"

    # For general branch creation and switch
    BRANCH_CREATED = "branch_created"

    # ...
    SUCCESS = "success"
    NO_MATCHES = "no_matches"
    DIRTY_WORKING_TREE = "dirty_working_tree"
    MERGE_CONFICT = "merge_conflict"
    UNKOWN_ERROR = "unknown_error"

    # for subprocess call/run errors
    SUBPROCESS_ERROR = "subprocess_error"


@dataclass
class GitResult:
    status: GitOpStatus
    raw_data: Any = None
    error_details: Optional[str] = None
