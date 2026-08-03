# ------------------------------------------
#  Adapter Type: GitHub Client Operations
# ------------------------------------------

from enum import Enum
from dataclasses import dataclass
from typing import Any, Optional, Dict


class GitHubOpStatus(Enum):
    # --------------------------
    #  For Initialization
    # --------------------------
    INIT_GITHUB_CLIENT = "init_github_client"

    # errors
    REPO_NOT_FOUND = "repo_not_found"
    BAD_CREDENTIALS = "bad_credentials"
    API_ERROR = "api_error"

    # --------------------------
    #  For Get Issue
    # --------------------------
    RETRIEVED_ISSUE = "retrieved_issue"

    # errors
    ISSUE_NOT_FOUND = "issue_not_found"

    # --------------------------
    #  For Create Pull Request
    # --------------------------
    PR_MADE = "pr_made"

    # errors
    UNPROCESSABLE = "unprocessable"
    REPO_OR_BRANCH_NOT_FOUND = "repo_or_branch_not_found"

    # -------------------------
    #  For Post Issue Comment
    # -------------------------

    # General Exception
    GENERAL_EXCEPTION = "general_exception"


@dataclass
class GitHubClientResult:
    status = GitHubOpStatus

    # for get_issue
    issue_dict: Optional[Dict[str, Any]] = None

    raw_data: Any = None
    error_details: Optional[str] = None
