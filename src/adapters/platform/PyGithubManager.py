# -------------------------------------
#  Concrete Extension of
#  BaseGitHubClient Abstract Class
# -------------------------------------

from github import Auth, Github, GithubException

from .base import BaseGitHubClient
from .types import GitHubClientResult, GitHubOpStatus


class PyGithubManager(BaseGitHubClient):
    def __init__(self, token: str, repo_name: str):
        self.token = token
        self.repo_name = repo_name
        self.status = GitHubOpStatus.INIT_GITHUB_CLIENT
        self.error_details = None
        self.raw_data = None
        self.repo = None

        try:
            auth = Auth.Token(self.token) if self.token else None
            self.github = Github(auth=auth) if auth else Github()
            self.repo = self.github.get_repo(self.repo_name)
            self.raw_data = f"Initialized GitHub Client for {self.repo_name}"
        except GithubException as e:
            self.raw_data = e
            if e.status == 404:
                self.status = GitHubOpStatus.REPO_NOT_FOUND
                self.error_details = f"Error: Repository {self.repo_name} not found."
            elif e.status == 401:
                self.status = GitHubOpStatus.BAD_CREDENTIALS
                self.error_details = "Error: Bad credentials or invalid token."
            else:
                self.status = GitHubOpStatus.API_ERROR
                self.error_details = f"GitHub API Error [{e.status}]"
        except Exception as e:
            self.status = GitHubOpStatus.GENERAL_EXCEPTION
            self.error_details = f"An unexpected error occurred: {e}"

    def get_issue(self, issue_number: int) -> GitHubClientResult:
        """Fetches issue title, description, and comments."""

        if self.repo is None:
            return GitHubClientResult(
                status=self.status,
                error_details=self.error_details or "GitHub client not initialized",
            )

        try:
            issue = self.repo.get_issue(number=issue_number)

            comments = []
            for comment in issue.get_comments():
                comments.append(comment)

        except GithubException as e:
            # handle specific HTTP error status codes
            if e.status == 404:
                return GitHubClientResult(
                    status=GitHubOpStatus.ISSUE_NOT_FOUND,
                    raw_data=e,
                    error_details=f"Error: Issue {issue_number} not found.",
                )
            else:
                return GitHubClientResult(
                    status=GitHubOpStatus.API_ERROR,
                    raw_data=e,
                    error_details=f"GitHub API Error [{e.status}: {getattr(e, 'data', str(e))}]",
                )

        except Exception as e:
            # Handle general connection/network errors
            return GitHubClientResult(
                status=GitHubOpStatus.GENERAL_EXCEPTION,
                raw_data=e,
                error_details=f"An unexpected error occurred: {e}",
            )

        return GitHubClientResult(
            status=GitHubOpStatus.RETRIEVED_ISSUE,
            issue_dict={
                "Issue Number": issue_number,
                "Issue Title": issue.title,
                "Issue Description": issue.body,
                "State": issue.state,
            },
            comments=comments,
            raw_data=issue,
        )

    def create_pull_request(
        self, title: str, body: str, head_branch: str, base_branch: str = "main"
    ) -> GitHubClientResult:
        """Opens a Pull Request and returns the PR URL."""

        try:
            pr = self.repo.create_pull(
                title=title, body=body, head=head_branch, base=base_branch
            )

        except GithubException as e:
            if e.status == 422:
                return GitHubClientResult(
                    status=GitHubOpStatus.UNPROCESSABLE,
                    raw_data=e,
                    error_details=e.data["errors"],
                )

            elif e.status == 404:
                return GitHubClientResult(
                    status=GitHubOpStatus.REPO_OR_BRANCH_NOT_FOUND,
                    raw_data=e,
                    error_details=e.data["errors"],
                )

            else:
                return GitHubClientResult(
                    status=GitHubOpStatus.GENERAL_EXCEPTION,
                    raw_data=e,
                    error_details=e.data["errors"],
                )

        return GitHubClientResult(status=GitHubOpStatus.PR_MADE, raw_data=pr)

    def get_default_branch(self) -> GitHubClientResult:
        """Prevents PR creation tools from failing on repos using non-standard target branches."""

        try:
            default_branch = self.repo.default_branch

        except GithubException as e:
            return GitHubClientResult(
                status=GitHubOpStatus.API_ERROR,
                raw_data=e,
                error_details=e.data["errors"],
            )

        except Exception as e:
            return GitHubClientResult(
                status=GitHubOpStatus.GENERAL_EXCEPTION,
                raw_data=e,
                error_details=f"An unexpected error occurred: {str(e)}",
            )

        return GitHubClientResult(
            status=GitHubOpStatus.RETRIEVED_DEFAULT, default_branch=default_branch
        )

    def post_issue_comment(self, issue_number: int, comment: str) -> GitHubClientResult:
        """Updates issue progress."""

        try:
            issue = self.repo.get_issue(number=issue_number)

            # create the comment
            comment = issue.create_comment(comment)

        except GithubException as e:
            return GitHubClientResult(
                status=GitHubOpStatus.API_ERROR,
                raw_data=e,
                error_details=e.data["errors"],
            )

        except Exception as e:
            return GitHubClientResult(
                status=GitHubOpStatus.GENERAL_EXCEPTION,
                raw_data=e,
                error_details=f"An unexpected error occurred: {str(e)}",
            )

        return GitHubClientResult(
            status=GitHubOpStatus.COMMENT_MADE,
        )
