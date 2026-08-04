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
    #  For Get Default Branch
    # -------------------------
    RETRIEVED_DEFAULT = "retrieved_default"

    # -------------------------
    #  For Post Issue Comment
    # -------------------------
    COMMENT_MADE = "comment_made"

    # General Exception
    GENERAL_EXCEPTION = "general_exception"


@dataclass
class GitHubClientResult:
    status = GitHubOpStatus

    # for get_issue
    issue_dict: Optional[Dict[str, Any]] = None
    comments: Optional[list[Any]] = None

    # for get_default_branch
    default_branch: Optional[str] = None

    raw_data: Any = None
    error_details: Optional[str] = None
